"""Wissenskatalog von GroundTwin Analysis (A2, D108, docs/29 §3): Eintraege, Groessen, Pruefung und Planer.

Ein Eintrag (Regel, Korrelation, Spanne, Analyse) nennt Eingaben, Ausgaben, Gueltigkeit, Unsicherheit und Quelle. Die
Abhaengigkeiten werden aus Ein- und Ausgaben berechnet, nie von Hand gezeichnet. Der Katalog rechnet nichts selbst:
``implementierung`` verweist auf den bestehenden Code (Verhalten unveraendert). Dieses Paket importiert keinen anderen
Bereich (reine Daten und Logik).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

HIER = Path(__file__).resolve().parent
ID_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")
ARTEN = ("rule", "correlation", "empirical_range", "analysis", "requirement")
AUTORITAET = ("standard", "correlation", "empirical", "guideline", "expert", "research")
PFLICHT = ("id", "version", "kind", "authority", "source", "inputs", "outputs", "validity", "uncertainty",
           "when_missing", "tests")


@lru_cache(maxsize=1)
def groessen() -> dict[str, dict]:
    return json.loads((HIER / "groessen.json").read_text(encoding="utf-8"))["groessen"]


@lru_cache(maxsize=1)
def katalog() -> dict[str, dict]:
    """Alle Eintraege nach id (eine Datei je Eintrag in katalog/)."""
    out = {}
    for f in sorted((HIER / "katalog").glob("*.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        out[e["id"]] = e
    return out


def _eingaben(e: dict) -> tuple[list[str], list[str]]:
    return list(e["inputs"].get("required") or []), list(e["inputs"].get("optional") or [])


def pruefen(eintraege: dict[str, dict] | None = None, bekannte: dict | None = None) -> list[str]:
    """Struktur, bekannte Groessen, eindeutige Erzeuger, keine Zyklen; leer = in Ordnung."""
    eintraege = katalog() if eintraege is None else eintraege
    bekannte = groessen() if bekannte is None else bekannte
    fehler: list[str] = []
    erzeuger: dict[str, str] = {}
    for k, e in eintraege.items():
        wo = f"{k}:"
        for f in PFLICHT:
            if f not in e:
                fehler.append(f"{wo} '{f}' fehlt")
        if not ID_RE.match(e.get("id", "")) or e.get("id") != k:
            fehler.append(f"{wo} id ungueltig")
        if e.get("kind") not in ARTEN or e.get("authority") not in AUTORITAET:
            fehler.append(f"{wo} kind/authority unbekannt")
        if not str((e.get("source") or {}).get("citation") or "").strip():
            fehler.append(f"{wo} ohne Quelle")
        req, opt = _eingaben(e)
        for g in req + opt + list(e.get("outputs") or []):
            if g not in bekannte:
                fehler.append(f"{wo} Groesse {g} nicht in groessen.json")
        for g in req + opt:
            if e.get("when_missing", {}).get(g, "block") not in ("block", "assume", "skip"):
                fehler.append(f"{wo} when_missing fuer {g} unbekannt")
        if not req and not opt:
            fehler.append(f"{wo} ohne Eingaben")
        for g in e.get("outputs") or []:
            if bekannte.get(g, {}).get("eingabe"):
                fehler.append(f"{wo} gibt {g} aus, das nur ein Mensch setzt")
            if g in erzeuger and erzeuger[g] != k:
                fehler.append(f"{wo} {g} wird schon von {erzeuger[g]} erzeugt")
            erzeuger[g] = k
    # Zyklen im Abhaengigkeitsgraph (Eintrag -> Eintrag ueber Groessen)
    kanten = abhaengigkeiten(eintraege)
    farbe: dict[str, int] = {}

    def besuch(k: str, pfad: list[str]):
        farbe[k] = 1
        for n in kanten.get(k, ()):
            if farbe.get(n) == 1:
                fehler.append("Zyklus: " + " -> ".join(pfad + [k, n]))
            elif not farbe.get(n):
                besuch(n, pfad + [k])
        farbe[k] = 2

    for k in eintraege:
        if not farbe.get(k):
            besuch(k, [])
    return fehler


def abhaengigkeiten(eintraege: dict[str, dict] | None = None) -> dict[str, set[str]]:
    """Kante a -> b, wenn eine Ausgabe von a eine Eingabe von b ist (aus den Signaturen berechnet)."""
    eintraege = katalog() if eintraege is None else eintraege
    erzeugt: dict[str, set[str]] = {}
    for k, e in eintraege.items():
        for g in e.get("outputs") or []:
            erzeugt.setdefault(g, set()).add(k)
    out: dict[str, set[str]] = {k: set() for k in eintraege}
    for k, e in eintraege.items():
        req, opt = _eingaben(e)
        for g in req + opt:
            for q in erzeugt.get(g, ()):
                if q != k:
                    out[q].add(k)
    return out


def planen(verfuegbar: set[str] | list[str], eintraege: dict[str, dict] | None = None,
           angenommen_im_projekt: set[str] | None = None) -> dict:
    """Was ein Projekt mit diesen Groessen rechnen kann (A2-Planer, Grundlage der Readiness-Sicht A3).

    Je Eintrag: ``moeglich`` (alle Pflichteingaben da), ``hinweisend`` (laeuft mit angenommenen oder ohne optionale
    Eingaben) oder ``blockiert`` (mit den fehlenden Eingaben). Je fehlender Grundgroesse: was sie liefert und was sie
    freischalten wuerde (direkt und ueber abgeleitete Groessen).

    ``angenommen_im_projekt``: Groessen, die das Projekt hat, aber (zum Teil) nur als Annahme (#35: kein Feinkorn
    genannt → Klasse < 5 %). Ein Eintrag, der sie benutzt, ist hoechstens ``hinweisend`` und nennt sie."""
    eintraege = katalog() if eintraege is None else eintraege
    im_projekt = set(angenommen_im_projekt or ())
    unbekannt = sorted(g for g in set(verfuegbar) if g not in groessen())
    da = _abschluss(set(verfuegbar), eintraege)        # 1. alles Ableitbare (Fixpunkt)
    status: dict[str, dict] = {}
    for k, e in eintraege.items():                     # 2. Status je Eintrag mit dem vollen Stand
        req, opt = _eingaben(e)
        wm = e.get("when_missing") or {}
        fehlt = [g for g in req if g not in da]
        angenommen = [g for g in fehlt if wm.get(g) == "assume"]
        blockiert = [g for g in fehlt if g not in angenommen]
        angenommen += [g for g in req + opt if g in im_projekt and g in da and g not in angenommen]
        opt_da = [g for g in opt if g in da]
        if blockiert or (not req and not opt_da):
            status[k] = {"status": "blockiert", "fehlt": blockiert or [g for g in opt if g not in da]}
            continue
        ohne = [g for g in opt if g not in da]
        status[k] = {"status": "hinweisend" if angenommen or (not req and ohne) else "moeglich",
                     "angenommen": angenommen, "ohne": ohne,
                     "abdeckung": f"{len(opt_da)}/{len(opt)}" if not req else None}
    # was eine fehlende Grundgroesse freischalten wuerde
    erzeugbar = {g for e in eintraege.values() for g in e["outputs"]}
    def braucht(s_: dict) -> list[str]:                # fehlt (blockiert), angenommen oder ohne (hinweisend)
        return s_.get("fehlt", []) + s_.get("angenommen", []) + s_.get("ohne", [])
    fehlend = sorted({g for s_ in status.values() for g in braucht(s_)})
    grund = [g for g in fehlend if g not in erzeugbar]
    freischalten = {}
    for g in grund:
        mit = planen_still(set(verfuegbar) | {g}, eintraege)
        vorher = {k for k, s in status.items() if s["status"] != "blockiert"}
        freischalten[g] = {"liefert": groessen()[g].get("liefert", ""), "eingabe": bool(groessen()[g].get("eingabe")),
                           "schaltet_frei": sorted(mit - vorher),          # allein, ohne weitere Groessen
                           "benoetigt_fuer": sorted(k for k, s_ in status.items() if g in braucht(s_))}
    benutzt = {g for e in eintraege.values() for g in _eingaben(e)[0] + _eingaben(e)[1]}
    return {"verfuegbar": sorted(set(verfuegbar)), "unbekannt": unbekannt, "eintraege": status,
            "fehlende_grundgroessen": freischalten,
            "ungenutzt": sorted(g for g in set(verfuegbar) if g not in benutzt)}   # vorhanden, aber kein Eintrag (A4)


def _abschluss(verfuegbar: set[str], eintraege: dict[str, dict]) -> set[str]:
    """Verfuegbare Groessen plus alles, was die rechenbaren Eintraege daraus ableiten."""
    da = set(verfuegbar)
    while True:
        neu = set()
        for e in eintraege.values():
            req, opt = _eingaben(e)
            wm = e.get("when_missing") or {}
            if all(g in da or wm.get(g) == "assume" for g in req) and (req or any(g in da for g in opt)):
                neu |= set(e["outputs"]) - da
        if not neu:
            return da
        da |= neu


def planen_still(verfuegbar: set[str], eintraege: dict[str, dict]) -> set[str]:
    """Nur die Menge der rechenbaren Eintraege (fuer 'was wuerde X freischalten')."""
    da, gehen = set(verfuegbar), set()
    geaendert = True
    while geaendert:
        geaendert = False
        for k, e in eintraege.items():
            if k in gehen:
                continue
            req, opt = _eingaben(e)
            wm = e.get("when_missing") or {}
            if all(g in da or wm.get(g) == "assume" for g in req) and (req or any(g in da for g in opt)):
                gehen.add(k)
                if set(e["outputs"]) - da:
                    da |= set(e["outputs"])
                geaendert = True
    return gehen


def protokoll(eintrag_id: str, eingaben: list[str], agsi_id: str, groesse: str, quellen: list[str],
              unsicherheit: dict | None = None, gueltig: bool | None = None) -> dict:
    """Ergebnis-Datensatz eines abgeleiteten Werts im Format des Manifests (A1, manifest.schema.json): Wertart aus dem
    Eintrag, Katalog-id + Version, Eingangs-ids (PROV 'used'); ausserhalb der Gueltigkeit ein Hinweis."""
    e = katalog()[eintrag_id]
    w = {"agsi_id": agsi_id, "groesse": groesse, "kind": e.get("value_kind_of_outputs", "derived"),
         "herkunft": {"quellen": list(quellen), "katalog": {"id": e["id"], "version": e["version"]},
                      "eingaben": list(eingaben), "methode": e.get("title", e["id"])}}
    if unsicherheit or gueltig is False:
        w["unsicherheit"] = dict(unsicherheit or {})
        if gueltig is False:
            w["unsicherheit"]["hinweis"] = "ausserhalb der Gueltigkeit des Eintrags"
    return w


def verfuegbar_aus_dokumenten(docs: list[dict], homogenbereiche: dict | None = None) -> set[str]:
    """Grundgroessen eines Projekts aus der Extraktion (kanonisches JSON): was das Gutachten liefert."""
    da: set[str] = set()
    for d in docs:
        for b in d.get("boreholes") or []:
            if b.get("layers"):
                da.add("bohrung.schichten")
                if any((s.get("description_raw") or s.get("description") or s.get("beschreibung")) for s in b["layers"]):
                    da.add("boden.beschreibung")
            if b.get("x") is not None or b.get("coordinates") or b.get("location"):
                da.add("bohrung.lage")
            if b.get("gok_nhn") is not None or b.get("gok") is not None:
                da.add("bohrung.gok")
            gw = b.get("groundwater") or []
            if gw:
                da.add("grundwasser.staende")
                if any(g.get("kind") not in (None, "", "unbestimmt", "gemessen") for g in gw if isinstance(g, dict)):
                    da.add("grundwasser.art")
        proben = d.get("labor") or []
        if proben:
            da.add("labor.messwerte")
        schluessel = {k for p in proben for k in (p.get("werte") or {})}
        for k, g in (("wassergehalt", "labor.wassergehalt"), ("fliessgrenze", "labor.fliessgrenze"),
                     ("ausrollgrenze", "labor.ausrollgrenze"), ("kf", "labor.kf")):
            if k in schluessel:
                da.add(g)
        if {"ton", "schluff"} <= schluessel:
            da.add("labor.korngroesse")
        for s in d.get("sondierungen") or []:
            art = str(s.get("art") or "").upper()
            if s.get("werte"):
                da.add("sondierung.cpt_qc" if art.startswith("CPT") else "sondierung.dph_n10")
    if homogenbereiche:
        da.add("hb.zuordnung")
    return da
