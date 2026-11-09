"""Register der Dienste der Laender (dienste.json): laden, pruefen, ordnen, speichern - fuer die App und das Werkzeug
„Dienste der Länder“ (docs/21 §4.8, D98).

Arten: angebunden sind wfs-kopf, wfs-boreholeml und wms-kopf (Bohrungen; wms-kopf nur als Hinweis), wcs-dgm (Gelaende)
und lod2-kacheln (Gebaeude); portal-bohrungen, portal-dgm und portal-gebaeude sind nur Links. Status:
"geprueft" (mit Datum, gegen den echten Dienst getestet) oder "ungeprueft" (eingetragen, nicht getestet) - nie still.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

from . import laender, netz, utm
from .netz import DienstFehler

STANDARD = Path(__file__).with_name("dienste.json")
# GEO_AGENT_DIENSTE: das Register an einem anderen Ort (Container: /data, Pruefungen: eine Kopie); fehlt die Datei
# dort, beginnt sie als Kopie des Registers aus dem Repo
DATEI = Path(os.environ.get("GEO_AGENT_DIENSTE") or STANDARD)
# Art -> (Thema, angebunden)
ARTEN = {"wfs-kopf": ("bohrungen", True), "wfs-boreholeml": ("bohrungen", True), "wms-kopf": ("bohrungen", True),
         "wcs-dgm": ("dgm", True), "lod2-kacheln": ("gebaeude", True), "portal-bohrungen": ("bohrungen", False),
         "portal-dgm": ("dgm", False), "portal-gebaeude": ("gebaeude", False)}
THEMEN = {"bohrungen": "Bohrungen", "dgm": "Gelände (DGM)", "gebaeude": "Gebäude (LoD2)"}
PFLICHT = ("id", "land", "art", "titel", "anbieter", "url")
PFLICHT_JE_ART = {"wfs-kopf": ("typen", "systeme", "felder"), "wfs-boreholeml": ("typen", "systeme"),
                  "wms-kopf": ("typen", "systeme", "felder", "wms_version", "info_format"),
                  "wcs-dgm": ("coverage", "achsen", "system", "raster_m"), "lod2-kacheln": ("system", "format", "kachel_km")}
FELDER_KOPF = ("id", "name", "x", "y", "gok", "teufe", "datum", "profil", "punkt", "punkt_epsg", "hat_schichten")
REIHENFOLGE = ("id", "land", "laender", "art", "status", "geprueft", "aktiv", "titel", "anbieter", "url", "hinweis",
               "typen", "systeme", "felder", "wms_version", "info_format", "schichten", "coverage", "achsen", "system",
               "raster_m", "format", "kachel_km", "gebiet_wgs84", "gebiet_beleg", "lizenz", "lizenz_url", "namensnennung",
               "beleg")
ZEIT_PRUEFEN = 15


def _pfad(pfad: Path | None) -> Path:
    ziel = Path(pfad or DATEI)
    if not ziel.exists() and ziel != STANDARD:
        ziel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(STANDARD, ziel)
    return ziel


def laden(pfad: Path | None = None) -> dict:
    return json.loads(_pfad(pfad).read_text(encoding="utf-8"))


def version(pfad: Path | None = None) -> str:
    """Stand der Datei (Aenderungszeit): wer speichert, muss den Stand kennen, den er gelesen hat."""
    return str(_pfad(pfad).stat().st_mtime_ns)


def thema(d: dict) -> str:
    return ARTEN.get(d.get("art", ""), ("", False))[0]


def angebunden(d: dict) -> bool:
    """Fragt die App den Dienst selbst ab (sonst nur ein Link)? Abgeschaltete Eintraege nie."""
    return ARTEN.get(d.get("art", ""), ("", False))[1] and d.get("aktiv", True) is not False


def ordnen(d: dict) -> dict:
    """Feste Reihenfolge der Schluessel (stabile Unterschiede in git); unbekannte Schluessel bleiben, hinten."""
    return {**{k: d[k] for k in REIHENFOLGE if k in d}, **{k: v for k, v in d.items() if k not in REIHENFOLGE}}


def ergaenzen(d: dict) -> dict:
    """Fehlende Angaben, die sich ableiten lassen: Laender aus dem Land, Gebiet aus den Laendergrenzen, Status."""
    d = dict(d)
    if not d.get("laender") and d.get("land") in laender.LAENDER:
        d["laender"] = [d["land"]]
    elif not d.get("laender") and d.get("land") == "Deutschland":
        d["laender"] = list(laender.LAENDER)                 # bundesweit (z. B. die Bohrpunktkarte der BGR)
    if not d.get("gebiet_wgs84") and d.get("laender"):
        gebiete = [g for g in (laender.gebiet(name) for name in d["laender"]) if g]
        if gebiete:
            d["gebiet_wgs84"] = [min(g[0] for g in gebiete), min(g[1] for g in gebiete),
                                 max(g[2] for g in gebiete), max(g[3] for g in gebiete)]
    d.setdefault("status", "ungeprueft")
    return d


def fehler(daten: dict) -> list[str]:
    """Was am Register nicht stimmt (leer = in Ordnung); prueft jeden Eintrag und die Eindeutigkeit der Kennungen."""
    out: list[str] = []
    gesehen: set[str] = set()
    for i, d in enumerate(daten.get("dienste") or []):
        wo = f"Eintrag {i + 1} ({d.get('id') or '?'})"
        for k in PFLICHT:
            if not str(d.get(k) or "").strip():
                out.append(f"{wo}: „{k}“ fehlt")
        kennung = str(d.get("id") or "")
        if kennung and not re.fullmatch(r"[A-Z0-9][A-Z0-9-]{0,31}", kennung):
            out.append(f"{wo}: Kennung nur aus Großbuchstaben, Ziffern und „-“ (z. B. BY-DGM1)")
        if kennung in gesehen:
            out.append(f"{wo}: Kennung doppelt")
        gesehen.add(kennung)
        art = d.get("art")
        if art not in ARTEN:
            out.append(f"{wo}: Art „{art}“ unbekannt ({', '.join(ARTEN)})")
            continue
        for k in PFLICHT_JE_ART.get(art, ()):
            if d.get(k) in (None, "", [], {}):
                out.append(f"{wo}: für {art} fehlt „{k}“")
        url = str(d.get("url") or "")
        if url and not re.match(r"https?://[^\s/]+", url):
            out.append(f"{wo}: Adresse muss mit https:// (oder http://) beginnen")
        if art == "lod2-kacheln" and ("{e}" not in url or "{n}" not in url):
            out.append(f"{wo}: Kachel-Adresse braucht {{e}} und {{n}} (Kilometer Ost/Nord)")
        for name in d.get("laender") or []:
            if name not in laender.LAENDER:
                out.append(f"{wo}: Land „{name}“ unbekannt")
        g = d.get("gebiet_wgs84")
        if g is not None and not (isinstance(g, list) and len(g) == 4 and all(isinstance(v, (int, float)) for v in g)
                                  and g[0] < g[2] and g[1] < g[3]):
            out.append(f"{wo}: Gebiet als [Länge min, Breite min, Länge max, Breite max]")
        if d.get("status", "ungeprueft") not in ("geprueft", "ungeprueft"):
            out.append(f"{wo}: Status „geprueft“ oder „ungeprueft“")
        if d.get("geprueft"):
            try:
                date.fromisoformat(str(d["geprueft"]))
            except ValueError:
                out.append(f"{wo}: Prüfdatum als JJJJ-MM-TT")
        for k in ("systeme",):
            if k in d and not all(isinstance(v, int) for v in d[k] or []):
                out.append(f"{wo}: „{k}“ als Liste von EPSG-Nummern")
        if "felder" in d and (not isinstance(d["felder"], dict) or any(k not in FELDER_KOPF for k in d["felder"])):
            out.append(f"{wo}: „felder“ nur mit {', '.join(FELDER_KOPF)}")
    return out


def speichern(daten: dict, pfad: Path | None = None) -> dict:
    """Register pruefen, ergaenzen, ordnen (Land, Thema, Kennung) und atomar schreiben. ValueError bei Fehlern."""
    pfad = _pfad(pfad)
    dienste = [ordnen(ergaenzen(d)) for d in daten.get("dienste") or []]
    neu = {**{k: v for k, v in daten.items() if k != "dienste"}, "dienste": dienste}
    probleme = fehler(neu)
    if probleme:
        raise ValueError("; ".join(probleme[:8]) + (f" (und {len(probleme) - 8} weitere)" if len(probleme) > 8 else ""))
    rang = {name: i for i, name in enumerate(laender.LAENDER)}
    themen = list(THEMEN)
    neu["dienste"] = sorted(dienste, key=lambda d: (rang.get((d.get("laender") or [""])[0], -1) if d.get("land")
                                                    != "Deutschland" else -1,
                                                    themen.index(thema(d)) if thema(d) in themen else 9, d["id"]))
    neu["stand"] = date.today().isoformat()
    text = json.dumps(neu, ensure_ascii=False, indent=1) + "\n"
    zwischen = pfad.with_suffix(".tmp")
    try:
        zwischen.write_text(text, encoding="utf-8")
        zwischen.replace(pfad)
    except OSError as err:
        raise ValueError(f"Register nicht schreibbar ({pfad.name}: {err.strerror or err})") from None
    return neu


# ---------------------------------------------------------------- Pruefen gegen den echten Dienst (Werkzeug)
def _abfrage(url: str, werte: dict) -> str:
    return url + ("&" if "?" in url else "?") + urlencode(werte)


def _namen(xml: bytes, element: str) -> list[str]:
    try:
        wurzel = ET.fromstring(xml)
    except ET.ParseError as err:
        raise DienstFehler(f"Antwort ist kein XML ({err})") from None
    return [(e.text or "").strip() for e in wurzel.iter() if e.tag.split("}")[-1] == element and (e.text or "").strip()]


def pruefen_live(d: dict, holer=None, ansehen=None) -> dict:
    """Den Dienst einmal ansprechen: WFS/WCS-Capabilities (sind die eingetragenen Typen/Coverages da?), eine Kachel in
    der Mitte des Gebiets und eine Portalseite nur angesehen (die ersten 2 KB). Rueckgabe {ok, meldung, dauer_ms,
    gefunden}."""
    holer = holer or netz.holen
    ansehen = ansehen or netz.erreichbar
    d = ergaenzen(d)
    art = d.get("art")
    beginn = time.monotonic()
    gefunden: list[str] = []
    try:
        if art in ("wfs-kopf", "wfs-boreholeml", "wms-kopf"):
            kuerzel = "WMS" if art == "wms-kopf" else "WFS"
            gefunden = _namen(holer(_abfrage(d["url"], {"SERVICE": kuerzel, "REQUEST": "GetCapabilities"}), ZEIT_PRUEFEN),
                              "Name")
            fehlen = [t for t in d.get("typen") or [] if t not in gefunden]
            ok, meldung = not fehlen, (f"{kuerzel} erreichbar, {len(gefunden)} Objektarten" if not fehlen
                                      else f"{kuerzel} erreichbar, aber ohne {', '.join(fehlen)}")
        elif art == "wcs-dgm":
            gefunden = _namen(holer(_abfrage(d["url"], {"SERVICE": "WCS", "VERSION": "2.0.1",
                                                        "REQUEST": "GetCapabilities"}), ZEIT_PRUEFEN), "CoverageId")
            ok = d.get("coverage") in gefunden
            meldung = (f"WCS erreichbar, Coverage {d.get('coverage')} vorhanden" if ok
                       else f"WCS erreichbar, aber ohne Coverage {d.get('coverage')}")
        elif art == "lod2-kacheln":
            g = d.get("gebiet_wgs84") or [10.0, 50.0, 10.1, 50.1]
            zone = utm.zone(int(d.get("system") or 25832))
            x, y = (float(v) for v in utm.von_geo((g[0] + g[2]) / 2, (g[1] + g[3]) / 2, zone))
            km = int(d.get("kachel_km") or 1)
            e, n = int(x // 1000) // km * km, int(y // 1000) // km * km
            status, _ = ansehen(d["url"].format(e=e, n=n), ZEIT_PRUEFEN)
            ok, meldung = True, f"Kachel {e}/{n} in der Mitte des Gebiets vorhanden (HTTP {status})"
        else:
            status, _ = ansehen(d["url"], ZEIT_PRUEFEN)
            ok, meldung = True, f"Seite erreichbar (HTTP {status})"
    except DienstFehler as err:
        ok, meldung = False, str(err)
    return {"ok": ok, "meldung": meldung, "dauer_ms": round((time.monotonic() - beginn) * 1000),
            "gefunden": gefunden[:40]}
