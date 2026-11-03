"""Bohrungen der Staatlichen Geologischen Dienste rund um das Projekt (docs/23 §2.2, Phase P2).

Abgefragt wird nur auf Klick (D88): die Anfrage sendet die Lage des Projekts an den Dienst des Landes. Welche Dienste
es gibt, steht mit Beleg in dienste.json. Zwei Arten:
  wfs-kopf        Kopfdaten (Lage, GOK, Endteufe, Datum) und das Schichtenverzeichnis als Grafik (Berlin, Brandenburg)
  wfs-boreholeml  BoreholeML mit den freigegebenen Schichtdaten (NRW, Baden-Wuerttemberg) - nur diese lassen sich
                  ins Projekt uebernehmen und modellieren (boreholeml.importieren, Herkunft markiert)
Doppelte: dieselbe Bohrung im Gutachten und beim Land (Name oder Abstand) - zugleich eine Gegenprobe von Lage und GOK.
"""
from __future__ import annotations

import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from . import boreholeml

DIENSTE: list[dict] = json.loads(Path(__file__).with_name("dienste.json").read_text(encoding="utf-8"))["dienste"]
RADIUS_STANDARD, RADIUS_MAX = 250.0, 2000.0     # m um die Mitte des Projekts
ANZAHL_MAX = 200                                # Bohrungen je Dienst und Abfrage
ZEIT_KOPF, ZEIT_BML = 30, 120                   # s; der BoreholeML-Dienst von NRW braucht fuer grosse Flaechen lange
DOPPELT_ABSTAND = 3.0                           # m: naeher = dieselbe Bohrung (auch ohne gleichen Namen)
NAME_ABSTAND = 50.0                             # m: gleicher Name zaehlt nur so nah als dieselbe Bohrung
KONFIDENZ_ARCHIV = 0.5                          # Schichten aus der Datenbank eines Landes: nicht gegen ein PDF geprueft
AGENT = "GroundTwin (+https://github.com/martinpazmino/GroundTwin)"
VERSUCHE = 3                                    # Verbindungsabbrueche (Brandenburg: 2 von 3 an manchen Tagen)
_UTM = {25831: (31, 0.0), 25832: (32, 0.0), 25833: (33, 0.0), 4647: (32, 32_000_000.0), 5650: (33, 33_000_000.0)}
_NORMAL = {31: 25831, 32: 25832, 33: 25833}


class DienstFehler(Exception):
    """Ein Dienst antwortet nicht oder mit einer Fehlermeldung (betrifft nur diesen Dienst)."""


# ---------------------------------------------------------------- Lage
def utm_normal(x: float, y: float, epsg: int) -> tuple[float, float, int]:
    """ETRS89/UTM ohne Zonenkennung im Rechtswert (4647 -> 25832, 5650 -> 25833)."""
    if int(epsg) not in _UTM:
        raise ValueError(f"EPSG:{epsg} – für die Abfrage der Länder ETRS89/UTM nötig (25832/25833)")
    zone, abzug = _UTM[int(epsg)]
    return float(x) - abzug, float(y), _NORMAL[zone]


def utm_zu_geo(e: float, n: float, zone: int) -> tuple[float, float]:
    """UTM (GRS80, Nordhalbkugel) -> (Laenge, Breite) in Grad; Reihen nach Snyder (USGS 1987), Fehler << 1 m."""
    a, f, k0 = 6378137.0, 1 / 298.257222101, 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    m = n / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu) + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32)
            * math.sin(4 * mu) + 151 * e1 ** 3 / 96 * math.sin(6 * mu) + 1097 * e1 ** 4 / 512 * math.sin(8 * mu))
    s, c, t = math.sin(phi1), math.cos(phi1), math.tan(phi1)
    n1 = a / math.sqrt(1 - e2 * s * s)
    t1, c1 = t * t, ep2 * c * c
    r1 = a * (1 - e2) / (1 - e2 * s * s) ** 1.5
    d = (e - 500000.0) / (n1 * k0)
    breite = phi1 - (n1 * t / r1) * (d ** 2 / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1 ** 2 - 9 * ep2) * d ** 4 / 24
                                     + (61 + 90 * t1 + 298 * c1 + 45 * t1 ** 2 - 252 * ep2 - 3 * c1 ** 2) * d ** 6 / 720)
    laenge = (d - (1 + 2 * t1 + c1) * d ** 3 / 6
              + (5 - 2 * c1 + 28 * t1 - 3 * c1 ** 2 + 8 * ep2 + 24 * t1 ** 2) * d ** 5 / 120) / c
    return zone * 6 - 183 + math.degrees(laenge), math.degrees(breite)


BOHRDIENSTE = ("wfs-kopf", "wfs-boreholeml")


def dienste_am_ort(x: float, y: float, epsg: int, arten: tuple[str, ...] = BOHRDIENSTE) -> list[dict]:
    """Dienste der Arten, deren Gebiet die Mitte des Projekts enthaelt (an Landesgrenzen auch mehrere)."""
    x, y, epsg = utm_normal(x, y, epsg)
    lon, lat = utm_zu_geo(x, y, {25831: 31, 25832: 32, 25833: 33}[epsg])
    return [d for d in DIENSTE if d["art"] in arten and d["gebiet_wgs84"][0] <= lon <= d["gebiet_wgs84"][2]
            and d["gebiet_wgs84"][1] <= lat <= d["gebiet_wgs84"][3]]


def dienst(dienst_id: str) -> dict:
    for d in DIENSTE:
        if d["id"] == dienst_id:
            return d
    raise ValueError(f"unbekannter Dienst {dienst_id}")


def namensnennung(d: dict, heute: date | None = None) -> str:
    return d["namensnennung"].replace("{jahr}", str((heute or date.today()).year))


# ---------------------------------------------------------------- Abruf
def _holen(url: str, zeit: float) -> bytes:
    anfrage = urllib.request.Request(url, headers={"User-Agent": AGENT})
    for versuch in range(1, VERSUCHE + 1):
        try:
            with urllib.request.urlopen(anfrage, timeout=zeit) as antwort:
                return antwort.read()
        except TimeoutError:
            raise DienstFehler(f"keine Antwort in {zeit:g} s") from None
        except urllib.error.HTTPError as err:
            raise DienstFehler(f"HTTP {err.code}") from None
        except (urllib.error.URLError, OSError) as err:
            if isinstance(getattr(err, "reason", None), TimeoutError):   # Zeitueberschreitung beim Verbinden: nicht neu
                raise DienstFehler(f"keine Antwort in {zeit:g} s") from None
            if versuch < VERSUCHE:                         # Verbindung abgebrochen (z. B. reset by peer): kurz warten, neu
                time.sleep(versuch)
                continue
            raise DienstFehler(f"nicht erreichbar ({getattr(err, 'reason', err)})") from None
    raise AssertionError("unerreichbar")


def _url(d: dict, **parameter) -> str:
    werte = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature", **parameter}
    return d["url"] + "?" + urllib.parse.urlencode(werte, safe=":,")


def abfragen(x: float, y: float, epsg: int, radius: float = RADIUS_STANDARD, holer=None) -> dict:
    """Bohrungen der Laender im Umkreis: {mitte, epsg, radius, dienste, treffer [...], fehler [...], quellen [...]}."""
    holer = holer or _holen
    radius = min(max(float(radius), 10.0), RADIUS_MAX)
    x, y, epsg = utm_normal(x, y, epsg)
    am_ort = dienste_am_ort(x, y, epsg)
    treffer, fehler = [], []
    bbox = f"{x - radius:.1f},{y - radius:.1f},{x + radius:.1f},{y + radius:.1f},urn:ogc:def:crs:EPSG::{epsg}"
    for d in am_ort:
        if epsg not in d["systeme"]:
            fehler.append({"dienst": d["id"], "fehler": f"Dienst ohne EPSG:{epsg}"})
            continue
        for typ in d["typen"]:
            kopf = d["art"] == "wfs-kopf"
            parameter = {"TYPENAMES": typ, "BBOX": bbox, "COUNT": ANZAHL_MAX}
            if kopf:
                parameter["SRSNAME"] = f"urn:ogc:def:crs:EPSG::{epsg}"
            try:
                daten = holer(_url(d, **parameter), ZEIT_KOPF if kopf else ZEIT_BML)
                treffer += _kopfdaten(d, typ, daten) if kopf else _boreholeml_kopf(d, daten)
            except (DienstFehler, ValueError) as err:
                fehler.append({"dienst": d["id"], "fehler": str(err)[:300]})
    for t in treffer:
        t["abstand"] = round(math.hypot(t["x"] - x, t["y"] - y), 1) if t["x"] is not None else None
    treffer = sorted((t for t in treffer if t["abstand"] is not None and t["abstand"] <= radius),
                     key=lambda t: t["abstand"])
    return {"mitte": [round(x, 2), round(y, 2)], "epsg": epsg, "radius": radius,
            "zeit": datetime.now().strftime("%Y-%m-%d %H:%M"), "dienste": [d["id"] for d in am_ort],
            "treffer": treffer, "fehler": fehler,
            "quellen": [{"dienst": d["id"], "titel": d["titel"], "land": d["land"], "lizenz": d["lizenz"],
                         "namensnennung": namensnennung(d), "beleg": d["beleg"]} for d in am_ort]}


def _lokal(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _wurzel(daten: bytes, d: dict) -> ET.Element:
    try:
        w = ET.fromstring(daten)
    except ET.ParseError as err:
        raise DienstFehler(f"Antwort ist kein XML ({err})") from None
    if _lokal(w) == "ExceptionReport":
        text = " ".join(t.strip() for t in w.itertext() if t.strip())
        raise DienstFehler(f"Fehlermeldung des Dienstes: {text[:200]}")
    return w


def _zahl(text: str | None) -> float | None:
    try:
        return float(str(text).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _kopfdaten(d: dict, typ: str, daten: bytes) -> list[dict]:
    """WFS-Antwort mit Kopfdaten (Felder nach dienste.json) -> Treffer; Lage aus der Geometrie (angefragtes System)."""
    w = _wurzel(daten, d)
    f = d["felder"]
    out = []
    for mitglied in (el for el in w if _lokal(el) in ("member", "featureMember")):
        if not len(mitglied):
            continue
        merkmal = mitglied[0]
        werte = {_lokal(c): (c.text or "").strip() for c in merkmal}
        pos = next((p.text for p in merkmal.iter() if _lokal(p) == "pos" and p.text), None)
        xy = [float(v) for v in pos.split()[:2]] if pos else [_zahl(werte.get(f["x"])), _zahl(werte.get(f["y"]))]
        profil = werte.get(f.get("profil", "")) or None
        out.append({"dienst": d["id"], "id": werte.get(f["id"]) or merkmal.get(f"{{{boreholeml.GML}}}id", ""),
                    "name": werte.get(f["name"]) or werte.get(f["id"]) or "?", "x": xy[0], "y": xy[1],
                    "gok": _zahl(werte.get(f["gok"])), "teufe": _zahl(werte.get(f["teufe"])),
                    "datum": (werte.get(f.get("datum", "")) or "")[:10] or None,
                    "schichten": "grafik" if profil else "keine", "profil": profil, "schichten_n": None})
    return out


def _boreholeml_kopf(d: dict, daten: bytes) -> list[dict]:
    """BoreholeML-Antwort -> Treffer mit Zahl der Schichten und ob sie Petrographie tragen."""
    _wurzel(daten, d)
    try:
        doc = boreholeml.importieren(daten, d["id"])
    except ValueError as err:
        if "keine BoreholeML-Bohrung" in str(err):
            return []                                       # leere FeatureCollection: keine Bohrung im Umkreis
        raise
    out = []
    for b in doc["boreholes"]:
        schichten = b.get("layers") or []
        mit_petro = any(ly.get("soil_class") for ly in schichten)
        out.append({"dienst": d["id"], "id": b.get("fremd_id") or b["code"], "name": b["code"],
                    "x": b.get("x"), "y": b.get("y"), "gok": b.get("gok_nhn"), "teufe": b.get("end_depth"),
                    "datum": None, "profil": None, "schichten_n": len(schichten),
                    "schichten": "boreholeml" if mit_petro else ("ohne Petrographie" if schichten else "keine")})
    return out


def holen(dienst_id: str, ids: list[str], holer=None, heute: date | None = None) -> dict:
    """Ausgewaehlte Bohrungen eines BoreholeML-Dienstes mit Schichtdaten -> Dokument im kanonischen JSON (Herkunft)."""
    d = dienst(dienst_id)
    if d["art"] == "wfs-kopf":
        raise ValueError(f"{d['titel']}: nur Kopfdaten, das Schichtenverzeichnis als Grafik – nicht ins Modell übernehmbar")
    if d["art"] != "wfs-boreholeml":
        raise ValueError(f"{d['titel']}: kein Dienst für Bohrdaten")
    ids = [i for i in dict.fromkeys(ids) if i]
    if not ids:
        raise ValueError("keine Bohrung gewählt")
    daten = (holer or _holen)(_url(d, TYPENAMES=d["typen"][0], RESOURCEID=",".join(ids)), ZEIT_BML)
    _wurzel(daten, d)
    doc = boreholeml.importieren(daten, f"{d['titel']} ({d['land']})")
    heute = heute or date.today()
    for b in doc["boreholes"]:
        b.update(herkunft="SGD", quelle=d["id"], lizenz=d["lizenz"], namensnennung=namensnennung(d, heute),
                 abgerufen=heute.isoformat(), coord_source=f"SGD {d['land']}",
                 code=f"{d['id']}-{b['code']}")            # Kurzname mit Land: "14" gibt es auch im Gutachten
        b["issues"] = [f"aus {d['titel']} ({d['land']}), ID {b.get('fremd_id') or b['code']}, {d['lizenz']}, abgerufen "
                       f"{heute.strftime('%d.%m.%Y')} – nicht aus dem Gutachten"] + list(b.get("issues") or [])[1:]
        for ly in b.get("layers") or []:                      # Archivdaten: feste, niedrige Konfidenz (docs/23 §2.3)
            if ly.get("confidence") is None:
                ly["confidence"] = KONFIDENZ_ARCHIV
    fehlen = set(ids) - {b.get("fremd_id") for b in doc["boreholes"]}
    if fehlen:
        doc["fehlen"] = sorted(fehlen)
    return doc


# ---------------------------------------------------------------- Gutachten und Land: dieselbe Bohrung?
def _name(text: str | None) -> str:
    return re.sub(r"[\s_./-]", "", str(text or "")).lower().lstrip("0")


def doppelte(treffer: list[dict], bohrungen: list[dict]) -> dict:
    """Markiert Treffer, die eine Bohrung des Gutachtens sind (Name gleich und < 50 m, oder < 3 m), mit der Abweichung
    von Lage und GOK. bohrungen: {id, code, x, y, gok}. Rueckgabe: Gegenprobe {anzahl, lage_max, gok_max}."""
    mit_lage = [b for b in bohrungen if b.get("x") is not None and b.get("y") is not None]
    gegen = []
    for t in treffer:
        bester = None
        for b in mit_lage:
            abstand = math.hypot(b["x"] - t["x"], b["y"] - t["y"])
            gleich = _name(b["code"]) and _name(b["code"]) == _name(t["name"])
            if (gleich and abstand <= NAME_ABSTAND) or abstand <= DOPPELT_ABSTAND:
                if bester is None or abstand < bester[1]:
                    bester = (b, abstand)
        if bester:
            b, abstand = bester
            dgok = None if b.get("gok") is None or t.get("gok") is None else round(float(b["gok"]) - float(t["gok"]), 2)
            t.update(gutachten=b["code"], gutachten_id=b["id"], abweichung_lage=round(abstand, 2), abweichung_gok=dgok)
            gegen.append((abstand, dgok))
    return {"anzahl": len(gegen),
            "lage_max": round(max(a for a, _ in gegen), 2) if gegen else None,
            "gok_max": round(max(abs(g) for _, g in gegen if g is not None), 2) if any(g is not None for _, g in gegen) else None}
