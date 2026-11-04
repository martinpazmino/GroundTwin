"""Arbeitsplatz der Baugrundmodell-App: Projekte auf der Platte, Extraktion als Hintergrundauftrag, Modell-Cache,
Unterlagen und Seitenbilder. Ohne Web-Rahmen testbar; server/api.py macht daraus die HTTP-Schnittstelle.

Ablage unter ARBEIT (ui/pipeline.py, mit GEO_AGENT_ARBEIT festlegbar):
  projekte/<signatur>/docs.json      Extraktion (kanonisches JSON je Dokument, unveraendert)
  projekte/<signatur>/projekt.json   Projektstand (Korrekturen, Lage, Pruefung) - ui/projekt.py
  web/modelle/<schluessel>.ifc       Modell fuer den Viewer (Name = Schluessel der Eingaben)
  web/unterlagen/<sha>_<seite>.png   Lageplan/Laengsschnitt als Bild
  web/seiten/<sha>_<seite>.png       Seiten des Gutachtens (Quelle einer Schicht zeigen)
  projekte/<signatur>/dgm.npy        Gelaendemodell aus den Dateien des Nutzers (Kopf in projekt.json, docs/23)
  projekte/<signatur>/sgd.json       letzte Abfrage der Bohrungen der Laender (Treffer, Gegenprobe, Quellen)
  projekte/<signatur>/fremd.json     uebernommene Bohrungen der Laender: weiteres Dokument hinter docs.json (die
                                     Signatur bleibt die der Gutachten; die Kennungen "Dokument:Bohrung" bleiben fest)
  projekte/<signatur>/gebaeude.json  LoD2-Gebaeude der Laender um das Projekt (Kopf in projekt.json, docs/23 P4)
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import threading
import traceback
import uuid
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

from ui import pipeline as pl
from ui import projekt as pj

_GEODATEN = str(Path(__file__).resolve().parents[1] / "services" / "geodaten")
if _GEODATEN not in sys.path:
    sys.path.insert(0, _GEODATEN)
from geodaten import bohrdaten, boreholeml, dgm_dienst, gelaende, geoldg, quasigeoid, tiles3d, utm  # noqa: E402
from geodaten import gebaeude as lod2  # noqa: E402

BEISPIELE = {
    "berlin": ("Berlin V-67b-VE – echte Daten, georeferenziert (7 Bohrungen)", "berlin_v67b.json"),
    "talheim": ("Talheim – echte Daten ohne Koordinaten (Reihe)", "talheim.json"),
    "demo": ("Demo – synthetisch, 12 Bohrungen mit Linse", "demo_synthetisch.json"),
    "trasse": ("Trasse – synthetisch, 6 km, 51 Bohrungen", "trasse_synthetisch.json"),
    "pdf": ("Synthetisches Bohrprofil-PDF (ganzer Ablauf mit Extraktion)", "synthetisch_bohrprofil.pdf"),
}
# Standort ohne Gutachten (docs/21 §4.7): je ein Ort, an dem die Dienste der Laender zeigen, was sie liefern (gegen
# die echten Dienste geprueft, 250 m Umkreis): NRW mit Schichtdaten, Baden-Wuerttemberg oft ohne Petrographie, Berlin
# nur Kopfdaten (Gelaende und Gebaeude ja, ein Schichtenmodell nein)
STANDORT_BEISPIELE = {
    "standort_dortmund": ("Standort Dortmund (NRW) – Vorerkundung aus 24 Bohrungen mit Schichtdaten",
                          393507.0, 5708058.0, 25832, "Beispiel Dortmund"),
    "standort_karlsruhe": ("Standort Karlsruhe (Baden-Württemberg) – Schichtdaten oft ohne Petrographie",
                           456391.0, 5428394.0, 25832, "Beispiel Karlsruhe"),
    "standort_berlin": ("Standort Berlin-Friedrichshain – nur Kopfdaten: Gelände und Gebäude, kein Schichtenmodell",
                        394800.0, 5818400.0, 25833, "Beispiel Berlin"),
}
MODELLE_IM_SPEICHER = 6
DGM_IM_SPEICHER = 2


def extraktion_aus_json(daten: bytes) -> list[dict]:
    """Kanonisches JSON der Extraktion (ein Dokument oder eine Liste) - geprueft, nicht veraendert."""
    try:
        obj = json.loads(daten.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as err:
        raise ValueError("weder PDF noch JSON der Extraktion") from err
    docs = obj if isinstance(obj, list) else [obj]
    if not docs or not all(isinstance(d, dict) and isinstance(d.get("boreholes"), list) and "file" in (d.get("document") or {})
                           for d in docs):
        raise ValueError("JSON ist keine Extraktion (document, boreholes)")
    return docs


def _ist_xml(daten: bytes) -> bool:
    return daten.lstrip(b"\xef\xbb\xbf \t\r\n")[:1] == b"<"


def signatur(docs: list[dict]) -> str:
    return hashlib.sha256(json.dumps(docs, sort_keys=True).encode()).hexdigest()[:12]


def _mit_bericht(xml: bytes, bericht: dict) -> bytes:
    """Bericht des BoreholeML-Exports als Kommentar hinter die XML-Deklaration (wer die Datei oeffnet, sieht ihn)."""
    zeilen = [f"GroundTwin: {len(bericht['exportiert'])} Bohrungen exportiert ({', '.join(bericht['exportiert'])})."]
    if bericht["ausgelassen"]:
        zeilen.append("Ausgelassen: " + "; ".join(f"{a['code']} ({a['grund']})" for a in bericht["ausgelassen"]) + ".")
    zeilen += bericht["hinweise"]
    kommentar = "\n".join("  " + z.replace("--", "- -") for z in zeilen)
    kopf, _, rest = xml.partition(b"?>")
    return kopf + b"?>\n<!--\n" + kommentar.encode("utf-8") + b"\n-->" + rest


def json_schreiben(pfad: Path, obj) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pfad.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    tmp.replace(pfad)                                     # nie halb geschriebene Dateien


@dataclass
class Auftrag:
    """Extraktion eines oder mehrerer PDFs im Hintergrund (Fortschritt je Seite)."""
    id: str
    dateien: list[str]
    stand: dict = field(default_factory=lambda: {"datei": "", "nr": 0, "dateien": 0, "seite": 0, "seiten": 0, "klasse": ""})
    fertig: bool = False
    fehler: list[str] = field(default_factory=list)
    projekt: str | None = None

    def als_dict(self) -> dict:
        return {"id": self.id, "dateien": self.dateien, "stand": self.stand, "fertig": self.fertig,
                "fehler": self.fehler, "projekt": self.projekt}


@dataclass
class Modellstand:
    schluessel: str
    modell: object | None
    bericht: dict | None
    vorb: pj.Vorbereitung
    fehler: str = ""


class Arbeitsplatz:
    def __init__(self, arbeit: Path | None = None):
        self.arbeit = Path(arbeit) if arbeit else pl.ARBEIT
        pl.ARBEIT = self.arbeit                           # Extraktion und Ablage im selben Ordner
        self.web = self.arbeit / "web"
        for unter in ("modelle", "unterlagen", "seiten"):
            (self.web / unter).mkdir(parents=True, exist_ok=True)
        self._projekte: dict[str, tuple[list[dict], pj.Projekt]] = {}
        self._sperren: dict[str, threading.RLock] = {}
        self._sperre = threading.Lock()
        self._extraktion = threading.Lock()               # der Extraktor ist nicht fuer parallele Laeufe gebaut
        self._auftraege: dict[str, Auftrag] = {}
        self._modelle: OrderedDict[str, tuple[object, dict]] = OrderedDict()
        self._dgm: OrderedDict[tuple, gelaende.Raster] = OrderedDict()
        self._dgm_sperre = threading.Lock()              # Cache wird von mehreren Projekten (Threads) benutzt

    # ------------------------------------------------------------ Projekte
    def ordner(self, sig: str) -> Path:
        if not sig.isalnum():
            raise KeyError(sig)
        return self.arbeit / "projekte" / sig

    def sperre(self, sig: str) -> threading.RLock:
        with self._sperre:
            return self._sperren.setdefault(sig, threading.RLock())

    def anlegen(self, docs: list[dict]) -> str:
        """Projekt zu diesen Dokumenten oeffnen; gibt es schon einen gespeicherten Stand, gilt er weiter."""
        sig = signatur(docs)
        ordner = self.ordner(sig)
        if not (ordner / "docs.json").exists():
            json_schreiben(ordner / "docs.json", docs)
        if sig not in self._projekte:
            p = None
            alt = self.arbeit / "projekte" / f"{sig}.json"           # Stand aus der Streamlit-App v2 (gleiche Signatur)
            for datei in (ordner / "projekt.json", alt):
                if p is None and datei.exists():
                    try:
                        p = pj.laden(json.loads(datei.read_text(encoding="utf-8")))
                    except (ValueError, TypeError, KeyError):
                        p = None                          # kaputter Stand: neu beginnen
            if p is not None and not p.name:
                p.name = pj.neues_projekt(docs, sig).name
            docs = self._mit_fremd(sig, docs)
            self._projekte[sig] = (docs, p or pj.neues_projekt(docs, sig))
            self.sichern(sig)
        return sig

    def laden(self, sig: str) -> tuple[list[dict], pj.Projekt]:
        if sig not in self._projekte:
            ordner = self.ordner(sig)
            if not (ordner / "docs.json").exists():
                raise KeyError(sig)
            docs = self._mit_fremd(sig, json.loads((ordner / "docs.json").read_text(encoding="utf-8")))
            p = pj.laden(json.loads((ordner / "projekt.json").read_text(encoding="utf-8"))) \
                if (ordner / "projekt.json").exists() else pj.neues_projekt(docs, sig)
            self._projekte[sig] = (docs, p)
        return self._projekte[sig]

    def _mit_fremd(self, sig: str, docs: list[dict]) -> list[dict]:
        """Gutachten + uebernommene Bohrungen der Laender (immer als letztes Dokument)."""
        datei = self.ordner(sig) / "fremd.json"
        return docs + [json.loads(datei.read_text(encoding="utf-8"))] if datei.exists() else docs

    def sichern(self, sig: str) -> None:
        _, p = self._projekte[sig]
        json_schreiben(self.ordner(sig) / "projekt.json", pj.speichern(p))

    def zuruecksetzen(self, sig: str) -> None:
        """Alle Korrekturen, Lagen, Pruefhaken und Eincheckungen verwerfen."""
        with self.sperre(sig):
            self.laden(sig)
            for datei in ("fremd.json", "sgd.json", "dgm.npy", "gebaeude.json"):   # Uebernommenes und Abfragen gehoeren dazu
                (self.ordner(sig) / datei).unlink(missing_ok=True)
            docs = json.loads((self.ordner(sig) / "docs.json").read_text(encoding="utf-8"))
            name = self._projekte[sig][1].name
            p = pj.neues_projekt(docs, sig)
            p.name = name or p.name                          # der Name ist keine Korrektur
            if pj.standort_von(docs):                         # Standort: weiter mit den Diensten im Schritt Lage
                p.schritt = "lage"
            self._projekte[sig] = (docs, p)
            self.sichern(sig)

    def loeschen(self, sig: str) -> None:
        with self.sperre(sig):
            self._projekte.pop(sig, None)
            shutil.rmtree(self.ordner(sig), ignore_errors=True)

    # ------------------------------------------------------------ Standort (ohne Gutachten, docs/23 §2.3, P5)
    @staticmethod
    def _in_deutschland(x: float, y: float, epsg: int) -> None:
        """ETRS89/UTM 32 oder 33 und im Rechteck um Deutschland (5,5-15,5 Grad Ost, 47,2-55,1 Grad Nord); die Bereiche
        der UTM-Werte allein gelten in jeder Zone (ein Punkt in Paris hatte in Zone 31 passende Zahlen)."""
        xn, yn, normal = bohrdaten.utm_normal(float(x), float(y), int(epsg))     # ValueError ausser ETRS89/UTM
        laenge, breite = (float(v) for v in utm.zu_geo(xn, yn, utm.zone(normal)))
        if utm.zone(normal) not in (32, 33) or not (5.5 <= laenge <= 15.5 and 47.2 <= breite <= 55.1):
            raise ValueError(f"Rechtswert {x:.0f} / Hochwert {y:.0f} liegen nicht in Deutschland (EPSG:{epsg})")

    def standort_punkt(self, laenge: float, breite: float, epsg: int | None = None) -> dict:
        """Klick in die Karte (Laenge/Breite, WGS84 ~ ETRS89 auf rund 1 m) -> ETRS89/UTM fuer den Standort: Zone nach der
        Laenge (32 westlich von 12 Grad, sonst 33) oder wie gewaehlt; dazu, was die Dienste der Laender dort liefern."""
        zone = utm.zone(epsg) if epsg else utm.zone_fuer(laenge)
        x, y = (float(v) for v in utm.von_geo(laenge, breite, zone))
        ziel = int(epsg) if epsg else 25800 + zone
        x += utm.versatz(25800 + zone, ziel) or 0.0                              # 4647/5650: mit Zonenkennung
        self._in_deutschland(x, y, ziel)
        return {"x": round(x, 1), "y": round(y, 1), "epsg": ziel, "laenge": round(float(laenge), 6),
                "breite": round(float(breite), 6), "dienste": bohrdaten.am_ort(x, y, ziel)}

    def standort_anlegen(self, x: float, y: float, epsg: int, name: str = "") -> tuple[str, bool]:
        """Projekt an einem Punkt (ETRS89/UTM): Bohrungen, DGM und Gebaeude kommen von den Diensten der Laender.
        Gibt es den Standort schon, wird er nur geoeffnet (Name und Schritt bleiben). Rueckgabe (Signatur, vorhanden)."""
        self._in_deutschland(x, y, epsg)
        punkt = {"x": round(float(x), 2), "y": round(float(y), 2), "epsg": int(epsg)}
        kennung = hashlib.sha256(json.dumps(punkt, sort_keys=True).encode()).hexdigest()
        docs = [{"document": {"file": f"Standort {punkt['x']:.0f} / {punkt['y']:.0f} (EPSG:{epsg})", "sha256": kennung,
                              "parser_version": "standort", "pages": None, "standort": punkt},
                 "boreholes": [], "soundings": {}}]
        vorhanden = (self.ordner(signatur(docs)) / "projekt.json").exists()
        sig = self.anlegen(docs)
        if vorhanden:
            return sig, True
        with self.sperre(sig):
            _, p = self.laden(sig)
            if name.strip():
                p.name = name.strip()[:120]
            p.lage_modus = pj.LAGE_KOORDINATEN
            p.schritt = "lage"
            self.sichern(sig)
        return sig, False

    def _standort_uebernehmen(self, von: str, nach: str) -> None:
        """Gutachten zu einem Standort: Bohrungen der Laender (mit Pruefstand), Abfrage, DGM und Gebaeude uebernehmen.

        Die Fremdbohrungen bleiben ein eigenes Dokument hinter dem Gutachten; ihre Kennungen wandern von "n_von:k"
        nach "n_nach:k". Die Gegenprobe rechnet gegen die Bohrungen des Gutachtens neu (ohne Netz).
        """
        with self.sperre(von):
            _, pv = self.laden(von)
            n_von = len(self._gutachten(von))
        quelle, ziel = self.ordner(von), self.ordner(nach)
        with self.sperre(nach):
            for datei in ("fremd.json", "sgd.json", "dgm.npy", "gebaeude.json"):
                if (quelle / datei).exists() and not (ziel / datei).exists():
                    shutil.copy2(quelle / datei, ziel / datei)
            self._projekte.pop(nach, None)                   # neu laden: fremd.json gehoert jetzt dazu
            docs, p = self.laden(nach)
            n_nach = len(self._gutachten(nach))
            p.dgm = p.dgm or copy.deepcopy(pv.dgm)          # tief: _ins_system aendert Listen darin (Ausdehnung)
            p.gebaeude = p.gebaeude or copy.deepcopy(pv.gebaeude)
            alt, neu = f"{n_von}:", f"{n_nach}:"
            for quelle_d, ziel_d in ((pv.bohrung, p.bohrung), (pv.schicht, p.schicht)):
                for k, o in quelle_d.items():
                    if k.startswith(alt):
                        ziel_d.setdefault(neu + k[len(alt):], dict(o))
            epsgs = Counter(int(b["crs_epsg"]) for d in docs[:n_nach] for b in d["boreholes"]
                            if b.get("x") is not None and b.get("crs_epsg"))
            if epsgs:                                        # Gutachten mit Zonenkennung, Standort ohne (oder umgekehrt)
                docs = self._ins_system(nach, docs, n_nach, p, epsgs.most_common(1)[0][0])
            sgd = ziel / "sgd.json"
            if sgd.exists():
                erg = json.loads(sgd.read_text(encoding="utf-8"))
                eigene = [b for b in pj.gelaende_eingabe(docs, p) if not str(b["id"]).startswith(neu)]
                erg["gegenprobe"] = self._gegenprobe(erg, eigene)
                json_schreiben(sgd, erg)
            p.lage_modus = pj.LAGE_KOORDINATEN
            p.version += 1
            self.sichern(nach)

    def _ins_system(self, sig: str, docs: list[dict], n_gutachten: int, p: pj.Projekt, ziel: int) -> list[dict]:
        """Bohrungen der Laender, DGM und Gebaeude eines Projekts ins System ziel derselben UTM-Zone umschreiben
        (Zonenkennung hinzu oder weg, docs/16 S17); eine andere Zone bleibt, wie sie ist (die Pruefungen markieren)."""
        if len(docs) > n_gutachten:
            fremd = docs[n_gutachten]
            for b in fremd["boreholes"]:
                v = utm.versatz(b.get("crs_epsg"), ziel)
                if v:
                    b["x"], b["crs_epsg"] = float(b["x"]) + v, ziel
            json_schreiben(self.ordner(sig) / "fremd.json", fremd)
        for kopf in (p.dgm, p.gebaeude):
            v = utm.versatz((kopf or {}).get("epsg"), ziel)
            if not v:
                continue
            kopf["epsg"] = ziel
            kopf["stand"] = hashlib.sha256(f"{kopf.get('stand')}:{ziel}".encode()).hexdigest()[:12]
            for k in ("x0",):
                if k in kopf:
                    kopf[k] += v
            for kasten in (kopf.get("ausdehnung"), (kopf.get("quelle") or {}).get("ausschnitt")):
                if kasten:
                    kasten[0] += v
                    kasten[2] += v
            if kopf is p.gebaeude and (self.ordner(sig) / "gebaeude.json").exists():
                daten = json.loads((self.ordner(sig) / "gebaeude.json").read_text(encoding="utf-8"))
                for g in daten["gebaeude"]:
                    for f in g["flaechen"]:
                        for ring in [f["ring"], *f.get("loecher", [])]:
                            for punkt in ring:
                                punkt[0] += v
                daten["epsg"] = ziel
                json_schreiben(self.ordner(sig) / "gebaeude.json", daten)
        return docs

    @staticmethod
    def _gegenprobe(erg: dict, eigene: list[dict]) -> dict:
        """Gegenprobe im System der Abfrage: Bohrungen des Gutachtens mit Zonenkennung (4647) gegen Treffer ohne."""
        gleich = []
        for b in eigene:
            v = utm.versatz(b["epsg"], erg["epsg"]) if b.get("epsg") else 0.0
            if v is not None:
                gleich.append({**b, "x": b["x"] + v if b.get("x") is not None else None})
        return bohrdaten.doppelte(erg["treffer"], gleich)

    def _system(self, docs: list[dict], p: pj.Projekt) -> int | None:
        """EPSG des Projekts (Standort, sonst das haeufigste der Bohrungen, sonst der kalibrierte Plan) oder None."""
        try:
            return int(pj.projekt_mitte(docs, p)[2])
        except (ValueError, TypeError):
            return None

    def liste(self) -> list[dict]:
        """Zuletzt bearbeitete Projekte (neueste zuerst)."""
        out = []
        for ordner in (self.arbeit / "projekte").glob("*/projekt.json"):
            try:
                d = json.loads(ordner.read_text(encoding="utf-8"))
                docs = json.loads((ordner.parent / "docs.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            try:                                          # uebernommene Bohrungen der Laender zaehlen mit
                fremd = len(json.loads((ordner.parent / "fremd.json").read_text(encoding="utf-8"))["boreholes"])
            except (OSError, ValueError, KeyError):
                fremd = 0
            n = sum(len(x["boreholes"]) for x in docs) + fremd
            gep = sum(1 for o in d.get("bohrung", {}).values() if o.get("geprueft"))
            out.append({"signatur": ordner.parent.name, "name": d.get("name") or ordner.parent.name,
                        "dokumente": [x["document"]["file"] for x in docs], "bohrungen": n, "fremd": fremd, "geprueft": gep,
                        "eincheckungen": len(d.get("eincheckungen") or []), "geaendert": d.get("geaendert") or "",
                        "schritt": d.get("schritt") or "bohrungen", "standort": pj.standort_von(docs) is not None})
        return sorted(out, key=lambda x: x["geaendert"], reverse=True)

    # ------------------------------------------------------------ Aenderungen
    def aendern(self, sig: str, ops: list[dict]) -> list[str]:
        """Aenderungen der Reihe nach; bei einem Fehler bleibt der Stand vor diesem Aufruf (alles oder nichts)."""
        with self.sperre(sig):
            docs, p = self.laden(sig)
            sicherung = pj.speichern(p)
            meldungen = []
            try:
                for op in ops:
                    if op.get("op") == "gok_aus_dgm":            # Werte rechnet der Server aus dem DGM
                        op = {**op, "werte": self._gok_vorschlaege(sig, docs, p, op.get("ids"))}
                    m = pj.aendern(docs, p, op)
                    if m:
                        meldungen.append(m)
            except (ValueError, KeyError, TypeError, IndexError) as fehler:
                self._projekte[sig] = (docs, pj.laden(sicherung))
                raise ValueError(str(fehler).strip("'\"")) from fehler
            self.sichern(sig)
            return meldungen

    # ------------------------------------------------------------ Zustand fuer die Oberflaeche
    def vorbereitung(self, docs: list[dict], p: pj.Projekt) -> tuple[pj.Vorbereitung, tuple[float, float], str]:
        vorb = pj.modell_eingabe(docs, p)
        ursprung = pj.ursprung(p, vorb, pj.standort_von(docs))
        return vorb, ursprung, self._schluessel(vorb, p, ursprung)

    def _schluessel(self, vorb: pj.Vorbereitung, p: pj.Projekt, ursprung) -> str:
        """Schluessel der Modell-Eingaben (ohne Pruefhaken: Haken setzen rechnet nicht neu)."""
        e = pj.einstellungen(p)
        eingabe = {"docs": pl.ohne_pruefvermerke(vorb.docs), "vorgabe": p.vorgabe, "methode": e.methode,
                   "puffer": e.puffer, "raster": e.raster, "basis": e.basis, "ursprung": list(ursprung),
                   "dgm": p.dgm.get("stand") if self._mit_dgm(p) else None}
        return hashlib.sha256(json.dumps(eingabe, sort_keys=True).encode()).hexdigest()[:16]

    def zustand(self, sig: str) -> dict:
        with self.sperre(sig):
            docs, p = self.laden(sig)
            vorb, ursprung, schluessel = self.vorbereitung(docs, p)
            gecacht = self._modelle.get(schluessel)
            bericht = gecacht[1] if gecacht else None
            epsgs = Counter(b.get("crs_epsg") for d in vorb.docs for b in d["boreholes"] if b.get("crs_epsg"))
            u = dict(p.unterlage) if p.unterlage else None
            kal_epsg = ((u or {}).get("kalibrierung") or {}).get("epsg")      # Plan kalibriert, noch keine Bohrung gesetzt
            standort = pj.standort_von(docs)
            if u:
                u["url"] = f"/dateien/unterlagen/{Path(u['datei']).name}"
                u.pop("datei", None)
                u.pop("pdf", None)
            letzter = p.eincheckungen[-1] if p.eincheckungen else None
            return {
                "signatur": sig, "name": p.name, "version": p.version, "schritt": p.schritt,
                "dokumente": [{"index": i, "datei": d["document"]["file"], "seiten": d["document"].get("pages"),
                               "pdf": pl.pdf_pfad(d["document"]) is not None} for i, d in enumerate(docs)],
                "lage_modus": p.lage_modus, "erzeugt": p.erzeugt, "auto": p.auto,
                "standort": {**standort, "dienste": bohrdaten.am_ort(standort["x"], standort["y"], standort["epsg"])}
                if standort else None, "reifegrad": pj.reifegrad(docs, p),
                "durchmesser": p.durchmesser, "durchmesser_auto": pj.durchmesser_auto(vorb),
                "ueberhoehung": p.ueberhoehung, "einstellungen": p.einstellungen,
                "unterlage": u, "reihe": pj.reihe_liste(docs, p), "reihe_standard": p.reihe["standard"],
                "vorgabe": p.vorgabe, "eincheckungen": p.eincheckungen,
                "pruefstand": pj.pruefstand(docs, p),
                "eingecheckt": pj.stand_text(letzter) if letzter else None,
                "seit_einchecken_geaendert": pj.seit_einchecken_geaendert(docs, p, schluessel),
                "bohrungen": pj.bohrungen_liste(docs, p),
                "klassen": pj.klassen_liste(),
                "hinweise": vorb.hinweise, "nicht_im_modell": vorb.nicht_im_modell,
                "modell": {"schluessel": schluessel, "aktuell": gecacht is not None,
                           "ifc": f"/dateien/modelle/{self._ifc_name(schluessel, docs, p)}"
                           if gecacht and (self.web / "modelle" / self._ifc_name(schluessel, docs, p)).exists() else None},
                "punkte": p.punkte,
                "gelaende": self._gelaende(sig, docs, p),
                "gebaeude": self._gebaeude_kopf(p, epsgs.most_common(1)[0][0] if epsgs else None),   # LoD2 (Kopf)
                "sgd": self._sgd(sig, docs),
                "geoldg": self._geoldg(docs, p, vorb, standort),
                "viewer": {"bohrungen": pj.viewer_bohrungen(docs, p, vorb, bericht), "ursprung": list(ursprung),
                           "epsg": epsgs.most_common(1)[0][0] if epsgs else kal_epsg or (standort or {}).get("epsg"),
                           "modus": p.lage_modus,
                           "punkte": p.punkte},
            }

    def bohrung(self, sig: str, bid: str) -> dict:
        with self.sperre(sig):
            docs, p = self.laden(sig)
            zeile = next((z for z in pj.bohrungen_liste(docs, p) if z["id"] == bid), None)
            if zeile is None:
                raise KeyError(bid)
            return {"bohrung": zeile, "schichten": pj.schichten_liste(docs, p, bid)}

    # ------------------------------------------------------------ Modell
    def _ifc_name(self, schluessel: str, docs: list[dict], p: pj.Projekt) -> str:
        """IFC fuer den Viewer: Geometrie-Schluessel + Durchmesser und Gebaeude (gehoeren zum IFC, nicht zur Geometrie)."""
        dm = json.dumps([p.durchmesser, pj.durchmesser_je_code(docs, p), (p.gebaeude or {}).get("stand")], sort_keys=True)
        return f"{schluessel}_{hashlib.sha256(dm.encode()).hexdigest()[:6]}.ifc"

    def modell(self, sig: str) -> dict:
        """Modell rechnen (oder aus dem Speicher) und das IFC fuer den Viewer ablegen."""
        with self.sperre(sig):
            docs, p = self.laden(sig)
            vorb, ursprung, schluessel = self.vorbereitung(docs, p)
            if not p.erzeugt:
                p.erzeugt = True
                self.sichern(sig)
            fehler = ""
            if schluessel not in self._modelle:
                if not vorb.lage and not any(True for _ in pj.bohrungen(docs)):
                    fehler = ("noch keine Bohrung – im Schritt Lage die Bohrungen der Länder abfragen und übernehmen "
                              "(Schichtdaten bisher NRW und Baden-Württemberg)" if pj.standort_von(docs)
                              else "keine Bohrung im Projekt")
                elif not vorb.lage:
                    fehler = "keine Bohrung mit Lage – im Schritt Lage setzen oder 'Reihe' wählen"
                else:
                    e = pj.einstellungen(p)
                    try:
                        m = pl.modell_bauen(vorb.docs, p.vorgabe, e.methode, e.puffer, e.raster, e.basis, ursprung,
                                            *self._dgm_fuer_modell(sig, p))
                        self._modelle[schluessel] = (m, pl.bericht(m))
                        while len(self._modelle) > MODELLE_IM_SPEICHER:
                            self._modelle.popitem(last=False)
                    except ValueError as err:
                        fehler = str(err)
            if fehler:
                return {"schluessel": schluessel, "fehler": fehler, "bericht": None, "ifc": None,
                        "hinweise": vorb.hinweise, "nicht_im_modell": vorb.nicht_im_modell}
            self._modelle.move_to_end(schluessel)
            m, bericht = self._modelle[schluessel]
            name = self._ifc_name(schluessel, docs, p)
            ziel = self.web / "modelle" / name
            if not ziel.exists():
                ziel.write_bytes(pl.ifc_bytes(m, vorb.docs, durchmesser=p.durchmesser,
                                              durchmesser_je=pj.durchmesser_je_code(docs, p),
                                              **self._gebaeude_fuer_ifc(sig, p, m)))
                alte = sorted((self.web / "modelle").glob("*.ifc"), key=lambda f: f.stat().st_mtime)[:-20]
                for f in alte:
                    f.unlink(missing_ok=True)
            return {"schluessel": schluessel, "fehler": "", "bericht": bericht, "ifc": f"/dateien/modelle/{name}",
                    "hinweise": list(dict.fromkeys(vorb.hinweise + bericht["hinweise"])),
                    "nicht_im_modell": vorb.nicht_im_modell + bericht["ausgeschlossen"]}

    def einchecken(self, sig: str, kommentar: str) -> dict:
        with self.sperre(sig):
            docs, p = self.laden(sig)
            _, _, schluessel = self.vorbereitung(docs, p)
            eintrag = pj.einchecken(docs, p, schluessel if schluessel in self._modelle else None, kommentar)
            self.sichern(sig)
            return eintrag

    def export(self, sig: str, art: str, organisation: str = "") -> tuple[bytes, str, str]:
        """(Inhalt, Dateiname, Medientyp) fuer den Download; organisation nur fuer BoreholeML."""
        if art == "3dtiles":
            return self._export_3dtiles(sig)
        if art == "geoldg":
            return self._export_geoldg(sig, organisation)
        with self.sperre(sig):
            docs, p = self.laden(sig)
            stamm = p.name or "baugrundmodell"
            vorb, _, schluessel = self.vorbereitung(docs, p)
            if art == "extraktion":
                return pl.json_bytes(docs if len(docs) > 1 else docs[0]), f"{stamm}_extraktion.json", "application/json"
            if art == "eingabe":
                return pl.json_bytes(vorb.docs), f"{stamm}_modell_eingabe.json", "application/json"
            if art == "projekt":
                return pl.json_bytes(pj.speichern(p)), f"{stamm}_projekt.json", "application/json"
            if art == "boreholeml":                     # nur gepruefte Bohrungen mit UTM und GOK (docs/23 §2.1)
                inhalt, bericht = boreholeml.exportieren(
                    vorb.docs, projekt=p.name, organisation=organisation, sig=sig,
                    dgm_zelle=(p.dgm or {}).get("dx"))
                return _mit_bericht(inhalt, bericht), f"{stamm}_boreholeml.xml", "application/xml"
        erg = self.modell(sig)
        if erg["fehler"]:
            raise ValueError(erg["fehler"])
        with self.sperre(sig):
            m, bericht = self._modelle[erg["schluessel"]]
            if art == "bericht":
                return pl.json_bytes(bericht), f"{stamm}_bericht.json", "application/json"
            if art == "einheiten":
                return pl.json_bytes(bericht["vorlage_einheiten"]), f"{stamm}_einheiten.json", "application/json"
            if art == "ifc":
                letzter = p.eincheckungen[-1] if p.eincheckungen else None
                inhalt = pl.ifc_bytes(m, vorb.docs, pruefstand=pj.stand_text(letzter) if letzter else "nicht eingecheckt",
                                      durchmesser=p.durchmesser, durchmesser_je=pj.durchmesser_je_code(docs, p),
                                      **self._gebaeude_fuer_ifc(sig, p, m))
                return inhalt, f"{stamm}.ifc", "application/x-step"
        raise KeyError(art)

    def _export_3dtiles(self, sig: str, holer=None) -> tuple[bytes, str, str]:
        """Baugrundmodell als 3D Tiles 1.1 (Cesium, D87): ellipsoidische Hoehen mit dem Quasigeoid GCG2016."""
        with self.sperre(sig):
            docs, p = self.laden(sig)
            if p.lage_modus != pj.LAGE_KOORDINATEN:
                raise ValueError("3D Tiles nur mit Lage nach Koordinaten (ETRS89/UTM)")
        geoid = quasigeoid.laden(self.arbeit / "cache", holer=holer)      # Netz nur beim ersten Mal, ohne Sperre
        ifc, _, _ = self.export(sig, "ifc")
        with self.sperre(sig):
            docs, p = self.laden(sig)
            m, bericht = self._modelle[self.vorbereitung(docs, p)[2]]
            try:
                utm.zone(m.epsg)
            except (ValueError, TypeError):
                raise ValueError(f"3D Tiles nur mit ETRS89/UTM (25832/25833, mit Zonenkennung 4647/5650), nicht "
                                 f"EPSG:{m.epsg}") from None
            info = {"projekt": p.name, "reifegrad": bericht.get("reifegrad"), "namensnennung": self._quellen(docs, p)}
            stamm = p.name or "baugrundmodell"
        inhalt, _ = tiles3d.exportieren(ifc, int(m.epsg), geoid, info)
        return inhalt, f"{stamm}_3dtiles.zip", "application/zip"

    @staticmethod
    def _geoldg(docs: list[dict], p: pj.Projekt, vorb: pj.Vorbereitung, standort: dict | None) -> dict:
        """Pruefliste nach GeolDG (docs/21 §5.3): eigene Bohrungen im Modell mit ihren wirksamen Werten, Fristen."""
        sondierungen = sum(len(d.get("soundings") or {}) for d in docs)
        return geoldg.pruefen([b for d in vorb.docs for b in d["boreholes"]], p.geoldg,
                              reihe=p.lage_modus == pj.LAGE_REIHE, sondierungen=sondierungen, standort=bool(standort))

    def _export_geoldg(self, sig: str, organisation: str = "") -> tuple[bytes, str, str]:
        """Paket fuer den Geologischen Dienst: Fachdaten (BoreholeML), Bewertungsdaten (IFC, Pruefbericht,
        Modelldokumentation) und die Pruefliste je Bohrung. Was nicht geht, steht mit Grund im LIESMICH."""
        with self.sperre(sig):
            docs, p = self.laden(sig)
            name, stamm = p.name, geoldg.dateiname(p.name or "baugrundmodell")
            u = self._geoldg(docs, p, self.vorbereitung(docs, p)[0], pj.standort_von(docs))
        if not u["bohrungen"]:                          # nur Bohrungen der Laender: liegen dem Land schon vor
            raise ValueError("keine eigene Bohrung im Projekt – nichts an den Geologischen Dienst zu übermitteln "
                             "(Bohrungen der Länder liegen dem Land vor)")
        dateien: dict[str, bytes] = {}
        fehlt: list[str] = []
        try:
            dateien[f"fachdaten_GeolDG_9/{stamm}_boreholeml.xml"] = self.export(sig, "boreholeml", organisation)[0]
        except ValueError:
            gruende = Counter(e["boreholeml"] for e in u["bohrungen"] if e["boreholeml"])
            fehlt.append("BoreholeML (Fachdaten): keine exportierbare Bohrung ("
                         + ", ".join(f"{n} × {g}" for g, n in gruende.most_common()) + "; je Bohrung in pruefliste.csv)")
        try:
            ifc = self.export(sig, "ifc")[0]
        except ValueError as err:
            fehlt.append(f"Baugrundmodell (Bewertungsdaten): {err}")
        else:
            with self.sperre(sig):
                docs, p = self.laden(sig)
                _, bericht = self._modelle[self.vorbereitung(docs, p)[2]]
                letzter = p.eincheckungen[-1] if p.eincheckungen else None
                doku = geoldg.modelldokumentation(bericht, name, pj.stand_text(letzter) if letzter else "nicht eingecheckt",
                                                  self._quellen(docs, p))
            dateien[f"bewertungsdaten_GeolDG_10/{stamm}.ifc"] = ifc
            dateien[f"bewertungsdaten_GeolDG_10/{stamm}_pruefbericht.json"] = pl.json_bytes(bericht)
            dateien["bewertungsdaten_GeolDG_10/modelldokumentation.txt"] = doku.encode("utf-8")
        fehlt.append("das Gutachten selbst (PDF; Bewertungsdaten nach § 10 Abs. 2 Satz 1 Nr. 1) – liegt Ihnen vor")
        return geoldg.paket(u, name, dateien, fehlt), f"{p.name or 'baugrundmodell'}_geoldg.zip", "application/zip"

    @staticmethod
    def _quellen(docs: list[dict], p: pj.Projekt) -> list[str]:
        """Namensnennungen der Daten der Laender im Modell (DGM, Gebaeude, Bohrungen) fuer Exporte."""
        quellen = []
        if p.dgm:
            q = p.dgm.get("quelle") or {}
            quellen.append(q.get("namensnennung") or f"DGM: {p.dgm.get('name') or 'eigene Datei'}")
        for d in ((p.gebaeude or {}).get("quelle") or {}).get("dienste", []):
            quellen.append(d.get("namensnennung") or d.get("titel", ""))
        quellen += [b["namensnennung"] for d in docs for b in d["boreholes"] if b.get("namensnennung")]
        return list(dict.fromkeys(q for q in quellen if q))

    # ------------------------------------------------------------ Unterlage (Lageplan / Laengsschnitt)
    def unterlage_setzen(self, sig: str, name: str, daten: bytes | None, art: str, seite: int) -> None:
        """Neues PDF (daten) oder nur andere Seite/Ansicht der vorhandenen Unterlage (daten=None)."""
        if art not in ("plan", "schnitt"):
            raise ValueError("Ansicht: plan oder schnitt")
        with self.sperre(sig):
            docs, p = self.laden(sig)
            alt = p.unterlage or {}
            if daten is None:
                if not alt.get("pdf"):
                    raise ValueError("keine Unterlage")
                daten = Path(alt["pdf"]).read_bytes()
                name = alt["name"]
            sha = hashlib.sha256(daten).hexdigest()[:16]
            pdf = self.arbeit / "unterlagen" / f"{sha}.pdf"
            pdf.parent.mkdir(parents=True, exist_ok=True)
            if not pdf.exists():
                pdf.write_bytes(daten)
            bild = pl.unterlage_rendern(daten, seite)
            seite = min(max(0, int(seite)), bild["seiten"] - 1)
            png = self.web / "unterlagen" / f"{sha}_{seite}.png"
            png.write_bytes(bild["png"])
            gleich = (alt.get("sha"), alt.get("seite"), alt.get("art")) == (sha, seite, art)
            p.unterlage = {"sha": sha, "seite": seite, "seiten": bild["seiten"], "art": art, "name": name,
                           "datei": str(png), "pdf": str(pdf), "breite": bild["breite"], "hoehe": bild["hoehe"],
                           "mm_pro_px": bild["mm_pro_px"], "kalibrierung": alt.get("kalibrierung") if gleich else None}
            p.lage_modus = pj.LAGE_KOORDINATEN if art == "plan" else pj.LAGE_REIHE
            p.unterlage_zaehler += 1
            p.version += 1
            self.sichern(sig)

    def unterlage_entfernen(self, sig: str) -> None:
        with self.sperre(sig):
            _, p = self.laden(sig)
            p.unterlage = None
            p.version += 1
            self.sichern(sig)

    # ------------------------------------------------------------ Gelaende (DGM aus Dateien des Nutzers, docs/23)
    def dgm_setzen(self, sig: str, dateien: list[tuple[str, bytes]], epsg: int | None) -> None:
        """DGM-Kachel(n) lesen, zusammenfuegen und im Projektordner ablegen; ersetzt ein vorhandenes DGM."""
        raster = gelaende.dateien_lesen(dateien, epsg)
        namen = [n for n, _ in dateien]
        self._dgm_ablegen(sig, raster, namen[0] if len(namen) == 1 else f"{len(namen)} Dateien", namen)

    def dgm_abrufen(self, sig: str, rand: float | None = None, holer=None) -> None:
        """DGM des Ausschnitts um die Bohrungen vom Dienst des Landes (nur auf Klick); ersetzt ein vorhandenes DGM."""
        with self.sperre(sig):
            docs, p = self.laden(sig)
            punkte, epsg = pj.projekt_punkte(docs, p)
        box = dgm_dienst.ausschnitt(punkte, dgm_dienst.RAND_STANDARD if rand is None else rand)
        raster, quelle = dgm_dienst.abrufen(*box, epsg, holer=holer)          # Netz: ohne Sperre
        self._dgm_ablegen(sig, raster, f"{quelle['titel']} ({quelle['land']})", [], quelle)

    def _dgm_ablegen(self, sig: str, raster: gelaende.Raster, name: str, dateien: list[str],
                     quelle: dict | None = None) -> None:
        with self.sperre(sig):
            _, p = self.laden(sig)
            ziel = self.ordner(sig) / "dgm.npy"
            kopf = gelaende.speichern(raster, ziel)
            p.dgm = {**kopf, "name": name, "dateien": dateien, "datei": ziel.name, "geladen": pj.jetzt(),
                     "quelle": quelle,                     # Dienst des Landes: Lizenz, Namensnennung, Zeit
                     "stand": hashlib.sha256(raster.z.tobytes() + json.dumps(kopf, sort_keys=True).encode())
                     .hexdigest()[:12]}                    # Inhalt und Georeferenz (gleiche Datei, anderes EPSG)
            p.version += 1
            self.sichern(sig)

    def dgm_entfernen(self, sig: str) -> None:
        """DGM aus dem Projekt nehmen; uebernommene GOK bleiben (Quelle DGM, in der Tabelle aenderbar)."""
        with self.sperre(sig):
            _, p = self.laden(sig)
            p.dgm = None
            (self.ordner(sig) / "dgm.npy").unlink(missing_ok=True)
            p.version += 1
            self.sichern(sig)

    def _raster(self, sig: str, p: pj.Projekt) -> gelaende.Raster | None:
        if not p.dgm:
            return None
        pfad = self.ordner(sig) / p.dgm.get("datei", "dgm.npy")
        if not pfad.exists():
            return None
        schluessel = (str(pfad), p.dgm.get("stand"))
        with self._dgm_sperre:
            if schluessel not in self._dgm:
                self._dgm[schluessel] = gelaende.laden(pfad, p.dgm)
                while len(self._dgm) > DGM_IM_SPEICHER:
                    self._dgm.popitem(last=False)
            self._dgm.move_to_end(schluessel)
            return self._dgm[schluessel]

    # ------------------------------------------------------------ Gebaeude der Laender (LoD2, docs/23 P4, nur auf Klick)
    def gebaeude_abrufen(self, sig: str, rand: float | None = None, holer=None) -> None:
        """LoD2-Gebaeude im Ausschnitt um die Bohrungen aus den Kacheln der Laender; ersetzt vorhandene."""
        with self.sperre(sig):
            docs, p = self.laden(sig)
            punkte, epsg = pj.projekt_punkte(docs, p)
        box = lod2.ausschnitt(punkte, lod2.RAND_STANDARD if rand is None else rand)
        liste, quelle = lod2.abrufen(*box, epsg, holer=holer)                 # Netz: ohne Sperre
        if not liste:
            raise ValueError("keine LoD2-Gebäude im Ausschnitt"
                             + (f" (keine Kachel: {', '.join(quelle['ohne_kachel'])})" if quelle["ohne_kachel"] else ""))
        daten = {"epsg": epsg, "quelle": quelle, "gebaeude": liste}
        with self.sperre(sig):
            _, p = self.laden(sig)
            json_schreiben(self.ordner(sig) / "gebaeude.json", daten)
            p.gebaeude = {"anzahl": len(liste), "flaechen": sum(len(b["flaechen"]) for b in liste), "epsg": epsg,
                          "quelle": quelle, "geladen": pj.jetzt(),
                          "stand": hashlib.sha256(json.dumps(daten, sort_keys=True).encode()).hexdigest()[:12]}
            p.version += 1
            self.sichern(sig)

    def gebaeude_entfernen(self, sig: str) -> None:
        with self.sperre(sig):
            _, p = self.laden(sig)
            p.gebaeude = None
            (self.ordner(sig) / "gebaeude.json").unlink(missing_ok=True)
            p.version += 1
            self.sichern(sig)

    @staticmethod
    def _gebaeude_kopf(p: pj.Projekt, system: int | None) -> dict | None:
        """Kopf der Gebaeude fuer die Oberflaeche; in einem anderen System als die Bohrungen kommen sie nicht ins IFC -
        das wird gesagt, nicht still weggelassen."""
        if not p.gebaeude:
            return None
        kopf = dict(p.gebaeude)
        if system and kopf.get("epsg") and int(kopf["epsg"]) != int(system):
            kopf["hinweis"] = (f"Gebäude in EPSG:{kopf['epsg']}, die Bohrungen in EPSG:{system} – sie kommen nicht ins "
                               "Modell; neu abrufen")
        return kopf

    def _gebaeude_fuer_ifc(self, sig: str, p: pj.Projekt, m) -> dict:
        """Gebaeude und Angaben je Dienst fuer ifc_schreiben (nur im System des Modells)."""
        pfad = self.ordner(sig) / "gebaeude.json"
        if not p.gebaeude or not pfad.exists() or p.gebaeude.get("epsg") != m.epsg:
            return {}
        daten = json.loads(pfad.read_text(encoding="utf-8"))
        q = daten["quelle"]
        return {"gebaeude": daten["gebaeude"],
                "gebaeude_info": {"Abgerufen": q["abgerufen"], "Hinweis": "Bestand aus dem LoD2 des Landes (Umgebung)",
                                  "dienste": {d["dienst"]: {"Quelle": f"{d['titel']} ({d['land']})", "Anbieter": d["anbieter"],
                                                            "Lizenz": d["lizenz"], "Namensnennung": d["namensnennung"]}
                                              for d in q["dienste"]}}}

    @staticmethod
    def _mit_dgm(p: pj.Projekt) -> bool:
        """Oberkante des Modells aus dem DGM: DGM geladen, Lage nach Koordinaten, Einstellung an."""
        return bool(p.dgm) and p.lage_modus == pj.LAGE_KOORDINATEN and pj.einstellungen(p).gelaende_dgm

    def _dgm_fuer_modell(self, sig: str, p: pj.Projekt) -> tuple:
        """(Raster, Angaben) fuer den Modellierer oder (None, None)."""
        raster = self._raster(sig, p) if self._mit_dgm(p) else None
        if raster is None:
            return None, None
        return raster, {"name": p.dgm.get("name"), "raster_m": p.dgm.get("dx"), "quelle_dienst": p.dgm.get("quelle")}

    def _gelaende(self, sig: str, docs: list[dict], p: pj.Projekt) -> dict | None:
        """Kopf des DGM und Vergleich GOK - DGM fuer die Oberflaeche (None ohne DGM)."""
        if not p.dgm:
            return None
        kopf = {k: v for k, v in p.dgm.items() if k != "datei"}
        raster = self._raster(sig, p)
        if raster is None:
            return {"info": kopf, "pruefung": None, "fehler": "DGM-Datei fehlt im Projektordner – bitte neu laden"}
        if p.lage_modus != pj.LAGE_KOORDINATEN:
            return {"info": kopf, "pruefung": None, "fehler": "Vergleich nur mit Lage nach Koordinaten"}
        return {"info": kopf, "pruefung": gelaende.gok_pruefen(raster, pj.gelaende_eingabe(docs, p)), "fehler": ""}

    def _gok_vorschlaege(self, sig: str, docs: list[dict], p: pj.Projekt, ids: list[str] | None) -> dict[str, float]:
        raster = self._raster(sig, p)
        if raster is None:
            raise ValueError("kein DGM geladen")
        return gelaende.gok_vorschlaege(raster, pj.gelaende_eingabe(docs, p), ids)

    # ------------------------------------------------------------ Bohrungen der Laender (docs/23 §2.2, nur auf Klick)
    def sgd_abfragen(self, sig: str, radius: float | None = None, holer=None) -> dict:
        """Dienste der Laender um die Mitte des Projekts abfragen; Treffer mit Gegenprobe gegen das Gutachten."""
        with self.sperre(sig):
            docs, p = self.laden(sig)
            x, y, epsg = pj.projekt_mitte(docs, p)
        erg = bohrdaten.abfragen(x, y, epsg, radius or bohrdaten.RADIUS_STANDARD, holer=holer)   # Netz: ohne Sperre
        with self.sperre(sig):
            docs, p = self.laden(sig)
            eigene = [b for b in pj.gelaende_eingabe(docs, p) if not str(b["id"]).startswith(f"{len(self._gutachten(sig))}:")]
            erg["gegenprobe"] = self._gegenprobe(erg, eigene)
            json_schreiben(self.ordner(sig) / "sgd.json", erg)
            p.version += 1
            self.sichern(sig)
            return erg

    def sgd_uebernehmen(self, sig: str, auswahl: list[dict], holer=None) -> str:
        """Gewaehlte Bohrungen (BoreholeML mit Schichtdaten) als weiteres Dokument ins Projekt; Herkunft markiert."""
        je_dienst: dict[str, list[str]] = {}
        for a in auswahl:
            je_dienst.setdefault(str(a.get("dienst")), []).append(str(a.get("id")))
        geholt = [bohrdaten.holen(d, ids, holer=holer) for d, ids in je_dienst.items()]   # Netz: ohne Sperre
        with self.sperre(sig):
            docs, p = self.laden(sig)
            gutachten = self._gutachten(sig)
            fremd = docs[len(gutachten)] if len(docs) > len(gutachten) else {
                "document": {"file": "Bohrungen der Länder (SGD)", "sha256": "", "parser_version": "sgd", "pages": None},
                "boreholes": [], "soundings": {}}
            schon = {(b.get("quelle"), b.get("fremd_id")) for b in fremd["boreholes"]}
            neu = [b for doc in geholt for b in doc["boreholes"] if (b.get("quelle"), b.get("fremd_id")) not in schon]
            if not neu:
                raise ValueError("diese Bohrungen sind schon im Projekt")
            system = self._system(docs, p)               # die Dienste liefern ohne Zonenkennung, das Projekt evtl. mit
            for b in neu:
                v = utm.versatz(b.get("crs_epsg"), system) if system else None
                if v:
                    b["x"], b["crs_epsg"] = float(b["x"]) + v, system
            fremd["boreholes"] += neu
            json_schreiben(self.ordner(sig) / "fremd.json", fremd)
            self._projekte[sig] = (gutachten + [fremd], p)
            p.version += 1
            self.sichern(sig)
            fehlen = [i for doc in geholt for i in doc.get("fehlen", [])]
            return (f"{len(neu)} Bohrungen der Länder übernommen ({', '.join(b['code'] for b in neu[:6])}"
                    f"{' …' if len(neu) > 6 else ''})" + (f"; nicht geliefert: {', '.join(fehlen)}" if fehlen else ""))

    def sgd_verwerfen(self, sig: str) -> None:
        """Die letzte Abfrage vergessen (uebernommene Bohrungen bleiben; entfernen wie jede Bohrung)."""
        with self.sperre(sig):
            _, p = self.laden(sig)
            (self.ordner(sig) / "sgd.json").unlink(missing_ok=True)
            p.version += 1
            self.sichern(sig)

    def _gutachten(self, sig: str) -> list[dict]:
        return json.loads((self.ordner(sig) / "docs.json").read_text(encoding="utf-8"))

    def _sgd(self, sig: str, docs: list[dict]) -> dict | None:
        datei = self.ordner(sig) / "sgd.json"
        if not datei.exists():
            return None
        erg = json.loads(datei.read_text(encoding="utf-8"))
        n = len(self._gutachten(sig))
        drin = {(b.get("quelle"), b.get("fremd_id")) for d in docs[n:] for b in d["boreholes"]}
        for t in erg["treffer"]:
            t["uebernommen"] = (t["dienst"], t["id"]) in drin
            t["uebernehmbar"] = t["schichten"] == "boreholeml" and not t.get("gutachten") and not t["uebernommen"]
        return erg

    # ------------------------------------------------------------ Seiten des Gutachtens (Quelle einer Schicht)
    def seite(self, sig: str, dokument: int, seite: int) -> dict:
        docs, _ = self.laden(sig)
        if not 0 <= dokument < len(docs):
            raise KeyError(dokument)
        pfad = pl.pdf_pfad(docs[dokument]["document"])
        if pfad is None:
            raise KeyError("PDF nicht abgelegt (Beispiel ohne PDF)")
        import pymupdf
        sha = docs[dokument]["document"]["sha256"][:16]
        ziel = self.web / "seiten" / f"{sha}_{seite}.png"
        with pymupdf.open(pfad) as pdf:
            if not 0 <= seite < pdf.page_count:
                raise KeyError(seite)
            r = pdf[seite].rect
            skala = min(2400 / max(r.width, r.height), 200 / 72)
            if not ziel.exists():
                pdf[seite].get_pixmap(matrix=pymupdf.Matrix(skala, skala), alpha=False).save(str(ziel))
        return {"url": f"/dateien/seiten/{ziel.name}", "px_je_pt": skala, "breite_pt": r.width, "hoehe_pt": r.height,
                "seite": seite, "seiten": docs[dokument]["document"].get("pages")}

    # ------------------------------------------------------------ Extraktion im Hintergrund
    def extrahieren(self, dateien: list[tuple[str, bytes]], ocr: bool, standort: str | None = None) -> Auftrag:
        """standort: Signatur eines Standort-Projekts, dessen Bohrungen der Laender, DGM und Gebaeude mitkommen."""
        if standort:
            self.laden(standort)                                 # KeyError, wenn es das Projekt nicht gibt
        a = Auftrag(uuid.uuid4().hex[:12], [n for n, _ in dateien])
        self._auftraege[a.id] = a
        threading.Thread(target=self._extrahieren, args=(a, dateien, ocr, standort), daemon=True).start()
        return a

    def _extrahieren(self, a: Auftrag, dateien: list[tuple[str, bytes]], ocr: bool, standort: str | None = None) -> None:
        docs = []
        with self._extraktion:
            for nr, (name, daten) in enumerate(dateien, start=1):
                a.stand.update(datei=name, nr=nr, dateien=len(dateien), seite=0, seiten=0, klasse="")
                if not daten.startswith(b"%PDF-"):              # Extraktion als JSON oder Bohrungen als BoreholeML
                    try:
                        docs += [boreholeml.importieren(daten, name)] if _ist_xml(daten) else extraktion_aus_json(daten)
                    except ValueError as err:
                        a.fehler.append(f"{name}: {err}")
                    continue

                def melden(seite: int, seiten: int, klasse: str) -> None:
                    a.stand.update(seite=seite, seiten=seiten, klasse=klasse)
                try:
                    docs.append(pl.pdf_extrahieren(name, daten, ocr, melden))
                except Exception as err:                  # ein kaputtes PDF stoppt die anderen nicht
                    a.fehler.append(f"{name}: {type(err).__name__}: {err}")
                    traceback.print_exc()
        if docs and any(d["boreholes"] for d in docs):
            a.projekt = self.anlegen(docs)
            if standort:
                try:
                    self._standort_uebernehmen(standort, a.projekt)
                except Exception as err:                       # das Gutachten-Projekt bleibt in jedem Fall
                    a.fehler.append(f"Standort nicht übernommen: {type(err).__name__}: {err}")
                    traceback.print_exc()
        elif docs:
            a.fehler.append("In den Dokumenten wurde keine Bohrung erkannt. Ist eine Seite mit Bohrprofilen dabei? "
                            "Bei Scans OCR einschalten.")
        a.fertig = True

    def auftrag(self, aid: str) -> Auftrag:
        return self._auftraege[aid]

    def beispiel(self, schluessel: str, ocr: bool = False) -> dict:
        """Beispiel oeffnen: JSON direkt als Projekt, das PDF ueber die Extraktion (Auftrag), ein Standort als Projekt am
        Punkt (im Schritt Lage; schon angelegt: wie zuletzt)."""
        if schluessel in STANDORT_BEISPIELE:
            _, x, y, epsg, name = STANDORT_BEISPIELE[schluessel]
            sig, vorhanden = self.standort_anlegen(x, y, epsg, name)
            with self.sperre(sig):
                return {"projekt": sig, "schritt": self.laden(sig)[1].schritt if vorhanden else "lage"}
        _, datei = BEISPIELE[schluessel]
        pfad = pl.BEISPIELE / datei
        if pfad.suffix == ".pdf":
            return {"auftrag": self.extrahieren([(pfad.name, pfad.read_bytes())], ocr).id}
        return {"projekt": self.anlegen([json.loads(pfad.read_text(encoding="utf-8"))])}
