"""Bohrungen ueber WMS-GetFeatureInfo als automatischer Hinweis mit Kopfdaten (docs/26 §2 Option b, §3).

Fuer Laender ohne offenen BoreholeML-WFS liefert OGC WMS-GetFeatureInfo die Kopfdaten (Lage, GOK, Endteufe, Datum,
Hinweis auf vorhandenes Schichtenverzeichnis oder Link zum Bohrprofil-PDF), ohne Gesamtdatenbanken herunterzuladen.
Unterstuetzt werden die beiden im Live-Test (docs/26 §1) nachgewiesenen Antwortformate:
  1. ESRI FeatureInfoResponse (text/xml): BGR Geoviewer Bohrungen Deutschland (GBL, Layer 0 „Einzelbohrungen Info“)
     fuer 13 Laender (BY, SN, NI, SH, ST, TH, MV, HB, HH, BE, BB, BW, NW).
  2. OGC GML FeatureCollection (application/vnd.ogc.gml): u. a. Geologischer Dienst fuer Bremen (wms_bohrdatenbank,
     CC BY) inklusive direktem Link zum Bohrprofil-PDF (bohrprofil_pdf_url).

Unverhandelbar (AGENTS.md Regel 4 & 5):
  - Niemals Schichten erfinden: WMS-GetFeatureInfo liefert nur Kopfdaten (`layers: []`, `schichten: "keine" | "grafik" | "portal"`).
  - Herkunft, Lizenz, Namensnennung und Abrufdatum bleiben an jedem Treffer und jeder Bohrung erhalten.
"""
from __future__ import annotations

import math
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date, datetime

from . import bohrdaten, laender
from .netz import DienstFehler
from .utm import utm_normal

# GetFeatureInfo liefert nur, was unter dem abgefragten Pixel (plus wenigen Pixeln Toleranz des Servers) liegt. Mit
# 101 x 101 Pixeln fand der BGR-WMS nur Bohrungen bis ~40 m um die Mitte, eine bekannte Bohrung 150 m daneben fehlte
# (Radius 500 m, 2026-11-07). 5 x 5 Pixel: das Mittelpixel mit Toleranz deckt den ganzen Umkreis (29-31 Treffer,
# die bekannte dabei); 3 x 3 lieferte nichts. Genau gefiltert wird danach nach dem Abstand.
BILD_BREITE = 5                                 # ungerade Pixelzahl: das Mittelpixel liegt auf (x, y)
BILD_MITTE = 2
TREFFER_MAX = 50                                # FEATURE_COUNT je WMS-GetFeatureInfo-Abruf

_PUNKT_RE = re.compile(r"POINT\s*\(\s*([+-]?\d+(?:[.,]\d+)?)\s+([+-]?\d+(?:[.,]\d+)?)", re.IGNORECASE)

# Gepruefte WMS-Kopf-Dienste (Live-Tests in docs/26 §1); spaeter nach Freigabe in dienste.json uebernehmbar
WMS_DIENSTE: list[dict] = [
    {
        "id": "hb-bohrungen-wms",
        "land": "Bremen",
        "laender": ["Bremen"],
        "art": "wms-kopf",
        "titel": "GDfB Bremen – Bohrdatenbank (WMS-GetFeatureInfo)",
        "url": "https://geodienste.bremen.de/wms_bohrdatenbank",
        "wms_version": "1.1.1",
        "info_format": "application/vnd.ogc.gml",
        "typen": ["Bohrpunkte_Bremen"],
        "systeme": [25832],
        "gebiet_wgs84": [8.48, 53.01, 8.99, 53.61],
        "felder": {
            "id": "akbez",
            "name": "shortname",
            "x": "x_4647",
            "y": "y_4647",
            "punkt_epsg": 4647,
            "gok": "hoehe_bohransatz",
            "teufe": "endtiefe",
            "datum": "bohrung_bis",
            "profil": "bohrprofil_pdf_url",
        },
        "lizenz": "CC BY 4.0",
        "namensnennung": "© Freie Hansestadt Bremen, GeoInformation Bremen / Geologischer Dienst für Bremen ({jahr})",
        "beleg": "https://geodienste.bremen.de/wms_bohrdatenbank?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetCapabilities",
        "status": "geprueft",
    },
    {
        "id": "de-bgr-gbl-wms",
        "land": "Deutschland",
        "laender": [
            "Bayern",
            "Sachsen",
            "Niedersachsen",
            "Schleswig-Holstein",
            "Sachsen-Anhalt",
            "Thüringen",
            "Mecklenburg-Vorpommern",
            "Bremen",
            "Hamburg",
            "Berlin",
            "Brandenburg",
            "Baden-Württemberg",
            "Nordrhein-Westfalen",
        ],
        "art": "wms-kopf",
        "titel": "BGR – Geoviewer Bohrungen Deutschland (GBL WMS-GetFeatureInfo)",
        "url": "https://services.bgr.de/wms/geologie/gbl/",
        "wms_version": "1.3.0",
        "info_format": "text/xml",
        "typen": ["0"],
        "systeme": [25832],
        "gebiet_wgs84": [5.86, 47.27, 15.04, 55.06],
        "felder": {
            "id": "gml_ID",
            "name": "shortName",
            "punkt": "point",
            "punkt_epsg": 25832,
            "gok": "surfaceLevel",
            "teufe": "totalLength",
            "datum": "drillingDate",
            "profil": "boreholeWebLink",
            "hat_schichten": "layerData",
        },
        "lizenz": "BGR-Nutzungsbedingungen (Darstellungsdienst)",
        "namensnennung": "© BGR Hannover und Staatliche Geologische Dienste der Bundesländer ({jahr})",
        "beleg": "https://services.bgr.de/wms/geologie/gbl/?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities",
        "status": "geprueft",
    },
]


def _lokal(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _zahl(text: str | None) -> float | None:
    if text is None:
        return None
    bereinigt = str(text).strip()
    if not bereinigt or bereinigt.lower() in ("null", "none", "nan", "-"):
        return None
    try:
        return float(bereinigt.replace(",", "."))
    except ValueError:
        return None


def _text(text: str | None) -> str | None:
    if text is None:
        return None
    bereinigt = str(text).strip()
    if not bereinigt or bereinigt.lower() in ("null", "none", "-"):
        return None
    return bereinigt


def _datum_iso(text: str | None) -> str | None:
    wert = _text(text)
    if not wert:
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}", wert):
        return wert[:10]
    m = re.match(r"^(\d{2})\.(\d{2})\.(\d{4})$", wert)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return wert[:10]


def _punkt_wkt(wkt: str | None) -> tuple[float | None, float | None]:
    if not wkt:
        return None, None
    m = _PUNKT_RE.search(wkt)
    if not m:
        return None, None
    return _zahl(m.group(1)), _zahl(m.group(2))


def _url_wms(d: dict, typ: str, x: float, y: float, epsg: int, radius: float) -> str:
    """Baut die OGC WMS-GetFeatureInfo-URL fuer Version 1.3.0 (CRS, I, J) oder 1.1.1 (SRS, X, Y)."""
    version = d.get("wms_version", "1.3.0")
    bbox = f"{x - radius:.1f},{y - radius:.1f},{x + radius:.1f},{y + radius:.1f}"
    parameter: dict[str, str | int] = {
        "SERVICE": "WMS",
        "VERSION": version,
        "REQUEST": "GetFeatureInfo",
        "LAYERS": typ,
        "QUERY_LAYERS": typ,
        "BBOX": bbox,
        "WIDTH": BILD_BREITE,
        "HEIGHT": BILD_BREITE,
        "INFO_FORMAT": d.get("info_format", "text/xml"),
        "FEATURE_COUNT": TREFFER_MAX,
    }
    if version.startswith("1.3"):
        parameter["CRS"] = f"EPSG:{epsg}"
        parameter["I"] = BILD_MITTE
        parameter["J"] = BILD_MITTE
    else:
        parameter["SRS"] = f"EPSG:{epsg}"
        parameter["X"] = BILD_MITTE
        parameter["Y"] = BILD_MITTE
    basis = d["url"].rstrip("?&")
    trenner = "&" if "?" in basis else "?"
    return basis + trenner + urllib.parse.urlencode(parameter, safe=":,/")


def _wurzel_wms(daten: bytes) -> ET.Element:
    try:
        w = ET.fromstring(daten)
    except ET.ParseError as err:
        raise DienstFehler(f"WMS-Antwort ist kein gueltiges XML ({err})") from None
    if _lokal(w) in ("ServiceExceptionReport", "ExceptionReport"):
        text = " ".join(t.strip() for t in w.itertext() if t.strip())
        raise DienstFehler(f"Fehlermeldung des WMS-Dienstes: {text[:200]}")
    return w


def _koordinaten_normalisieren(rx: float | None, ry: float | None, quell_epsg: int, ziel_epsg: int) -> tuple[float | None, float | None]:
    if rx is None or ry is None:
        return None, None
    nx, ny, nepsg = utm_normal(rx, ry, quell_epsg)
    if nepsg != ziel_epsg:
        lon, lat = bohrdaten.utm_zu_geo(nx, ny, {25831: 31, 25832: 32, 25833: 33}[nepsg])
        from . import utm
        nx, ny = utm.von_geo(lon, lat, {25831: 31, 25832: 32, 25833: 33}[ziel_epsg])
    return round(float(nx), 2), round(float(ny), 2)


def _aus_esri_fields(d: dict, w: ET.Element, ziel_epsg: int, heute: date) -> list[dict]:
    """Liest <FIELDS .../> aus einer ESRI WMS FeatureInfoResponse (z. B. BGR GBL WMS Layer 0)."""
    f = d["felder"]
    quell_epsg = int(f.get("punkt_epsg", ziel_epsg))
    out: list[dict] = []
    for el in w.iter():
        if _lokal(el) != "FIELDS":
            continue
        attr = el.attrib
        rohx, rohy = _punkt_wkt(attr.get(f.get("punkt", "point")))
        x, y = _koordinaten_normalisieren(rohx, rohy, quell_epsg, ziel_epsg)
        bohr_id = _text(attr.get(f["id"])) or _text(attr.get("OBJECTID")) or ""
        name = _text(attr.get(f["name"])) or bohr_id or "?"
        profil = _text(attr.get(f.get("profil", "")))
        hat_schichten = _text(attr.get(f.get("hat_schichten", ""))) == "1"
        schichten_status = "grafik" if profil else ("portal" if hat_schichten else "keine")
        out.append({
            "dienst": d["id"],
            "id": bohr_id,
            "name": name,
            "x": x,
            "y": y,
            "gok": _zahl(attr.get(f["gok"])),
            "teufe": _zahl(attr.get(f["teufe"])),
            "datum": _datum_iso(attr.get(f.get("datum", ""))),
            "schichten": schichten_status,
            "profil": profil,
            "schichten_n": None,
            "herkunft": {
                "quelle": "SGD",
                "methode": "WMS-GetFeatureInfo",
                "dienst": d["id"],
                "land": d["land"],
                "sgd": _text(attr.get("SGD")) or d["land"],
                "lizenz": d["lizenz"],
                "namensnennung": bohrdaten.namensnennung(d, heute),
                "abgerufen": heute.isoformat(),
            },
        })
    return out


def _aus_gml_features(d: dict, w: ET.Element, ziel_epsg: int, heute: date) -> list[dict]:
    """Liest <gml:featureMember> / <member> aus einer OGC GML WMS-GetFeatureInfo-Antwort (z. B. Bremen WMS)."""
    f = d["felder"]
    quell_epsg = int(f.get("punkt_epsg", ziel_epsg))
    out: list[dict] = []
    for mitglied in (el for el in w if _lokal(el) in ("featureMember", "member")):
        if not len(mitglied):
            continue
        merkmal = mitglied[0]
        werte = {_lokal(c): (c.text or "").strip() for c in merkmal}
        pos = next((p.text for p in merkmal.iter() if _lokal(p) == "pos" and p.text), None)
        if pos:
            teile = pos.split()
            rohx, rohy = (_zahl(teile[0]), _zahl(teile[1])) if len(teile) >= 2 else (None, None)
        else:
            rohx, rohy = _zahl(werte.get(f.get("x", ""))), _zahl(werte.get(f.get("y", "")))
        epsg_wert = int(_zahl(werte.get("ksys")) or quell_epsg)
        if f.get("x") == "x_4647":
            epsg_wert = 4647
        x, y = _koordinaten_normalisieren(rohx, rohy, epsg_wert, ziel_epsg)
        bohr_id = _text(werte.get(f["id"])) or _text(merkmal.get("fid")) or ""
        name = _text(werte.get(f["name"])) or bohr_id or "?"
        profil = _text(werte.get(f.get("profil", "")))
        out.append({
            "dienst": d["id"],
            "id": bohr_id,
            "name": name,
            "x": x,
            "y": y,
            "gok": _zahl(werte.get(f["gok"])),
            "teufe": _zahl(werte.get(f["teufe"])),
            "datum": _datum_iso(werte.get(f.get("datum", ""))),
            "schichten": "grafik" if profil else "keine",
            "profil": profil,
            "schichten_n": None,
            "herkunft": {
                "quelle": "SGD",
                "methode": "WMS-GetFeatureInfo",
                "dienst": d["id"],
                "land": d["land"],
                "lizenz": d["lizenz"],
                "namensnennung": bohrdaten.namensnennung(d, heute),
                "abgerufen": heute.isoformat(),
            },
        })
    return out


def wms_kopfdaten(d: dict, daten: bytes, epsg: int = 25832, heute: date | None = None) -> list[dict]:
    """Parst eine WMS-GetFeatureInfo-Antwort (ESRI FeatureInfoResponse oder OGC GML FeatureCollection) in Treffer."""
    heute = heute or date.today()
    w = _wurzel_wms(daten)
    if _lokal(w) == "FeatureInfoResponse" or any(_lokal(el) == "FIELDS" for el in w.iter()):
        return _aus_esri_fields(d, w, epsg, heute)
    return _aus_gml_features(d, w, epsg, heute)


def dienste_wms_am_ort(x: float, y: float, epsg: int, radius: float = 0.0,
                       dienste: list[dict] | None = None) -> list[dict]:
    """Waehlt passende WMS-Kopf-Dienste am Punkt (Landesdienste vor bundesweitem BGR-GBL-Dienst)."""
    kandidaten = dienste if dienste is not None else WMS_DIENSTE
    x, y, epsg = utm_normal(x, y, epsg)
    lon, lat = bohrdaten.utm_zu_geo(x, y, {25831: 31, 25832: 32, 25833: 33}[epsg])
    am_punkt = laender.laender_um(x, y, epsg, radius)
    out: list[dict] = []
    for d in kandidaten:
        if d.get("art") != "wms-kopf" or d.get("aktiv", True) is False:
            continue
        if am_punkt and d.get("laender"):
            if any(land in d["laender"] for land in am_punkt):
                out.append(d)
        elif (g := d.get("gebiet_wgs84")) and g[0] <= lon <= g[2] and g[1] <= lat <= g[3]:
            out.append(d)
    rang = {land: i for i, land in enumerate(am_punkt)}
    return sorted(out, key=lambda d: (d.get("land") == "Deutschland",
                                      min((rang[land] for land in d.get("laender") or [] if land in rang), default=0)))


def abfragen_wms(x: float, y: float, epsg: int, radius: float = bohrdaten.RADIUS_STANDARD,
                 dienste: list[dict] | None = None, holer=None, heute: date | None = None) -> dict:
    """Fragt WMS-GetFeatureInfo-Dienste im Umkreis ab und liefert dieselbe Struktur wie bohrdaten.abfragen()."""
    holer = holer or bohrdaten._holen
    heute = heute or date.today()
    radius = min(max(float(radius), 10.0), bohrdaten.RADIUS_MAX)
    x, y, epsg = utm_normal(x, y, epsg)
    am_ort = dienste_wms_am_ort(x, y, epsg, radius=radius, dienste=dienste)
    treffer: list[dict] = []
    fehler: list[dict] = []
    gesehen: set[tuple[str, str]] = set()
    unvollstaendig: list[str] = []

    for d in am_ort:
        Abfrage_epsg = epsg if epsg in d["systeme"] else d["systeme"][0]
        ax, ay = _koordinaten_normalisieren(x, y, epsg, Abfrage_epsg)
        if ax is None or ay is None:
            continue
        for typ in d["typen"]:
            url = _url_wms(d, typ, ax, ay, Abfrage_epsg, radius)
            try:
                daten = holer(url, bohrdaten.ZEIT_KOPF)
                roh = wms_kopfdaten(d, daten, epsg=epsg, heute=heute)
                if len(roh) >= TREFFER_MAX:                     # Grenze des Servers erreicht: Liste unvollstaendig
                    unvollstaendig.append(d["id"])
                for t in roh:
                    schluessel = (t["dienst"], t["id"])
                    if schluessel not in gesehen:
                        gesehen.add(schluessel)
                        treffer.append(t)
            except (DienstFehler, ValueError) as err:
                fehler.append({"dienst": d["id"], "fehler": str(err)[:300]})

    for t in treffer:
        t["abstand"] = round(math.hypot(t["x"] - x, t["y"] - y), 1) if t["x"] is not None and t["y"] is not None else None
    treffer = sorted((t for t in treffer if t["abstand"] is not None and t["abstand"] <= radius),
                     key=lambda t: t["abstand"])
    return {
        "mitte": [round(x, 2), round(y, 2)],
        "epsg": epsg,
        "radius": radius,
        "zeit": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dienste": [d["id"] for d in am_ort],
        "treffer": treffer,
        "fehler": fehler,
        "unvollstaendig": sorted(set(unvollstaendig)),   # markiert, nie still gekappt: Radius verkleinern
        "portale": [],
        "quellen": [
            {
                "dienst": d["id"],
                "titel": d["titel"],
                "land": d["land"],
                "lizenz": d["lizenz"],
                "namensnennung": bohrdaten.namensnennung(d, heute),
                "beleg": d["beleg"],
            }
            for d in am_ort
        ],
    }


def zu_bohrungen(treffer: list[dict], dienste: list[dict] | None = None, heute: date | None = None) -> dict:
    """Ueberfuehrt WMS-Kopftreffer in das kanonische Bohrung-Dokument (wie bohrdaten.py, aber `layers: []`,
    da WMS-GetFeatureInfo keine Schichten liefert; niemals Schichten erfinden!)."""
    heute = heute or date.today()
    register_map = {d["id"]: d for d in (dienste if dienste is not None else WMS_DIENSTE)}
    bohrungen_liste: list[dict] = []
    for t in treffer:
        d = register_map.get(t["dienst"], {
            "id": t.get("dienst", "wms"),
            "titel": t.get("dienst", "WMS"),
            "land": (t.get("herkunft") or {}).get("land", "Deutschland"),
            "lizenz": (t.get("herkunft") or {}).get("lizenz", "unbekannt"),
            "namensnennung": (t.get("herkunft") or {}).get("namensnennung", ""),
        })
        fremd_id = t.get("id") or t.get("name") or "?"
        hinweis = (
            f"aus {d['titel']} ({d['land']}), ID {fremd_id}, {d['lizenz']}, "
            f"abgerufen {heute.strftime('%d.%m.%Y')} – WMS-GetFeatureInfo liefert nur Kopfdaten "
            f"(Hinweis auf vorhandene Bohrung, kein Schichtenverzeichnis)"
        )
        if t.get("profil"):
            hinweis += f"; Bohrprofil-Link: {t['profil']}"
        bohrungen_liste.append({
            "code": f"{d['id']}-{t.get('name') or fremd_id}",
            "fremd_id": fremd_id,
            "x": t.get("x"),
            "y": t.get("y"),
            "epsg": 25832,
            "gok_nhn": t.get("gok"),
            "end_depth": t.get("teufe"),
            "layers": [],                                       # unverhandelbar: keine erfundenen Schichten
            "herkunft": "SGD",
            "quelle": d["id"],
            "lizenz": d["lizenz"],
            "namensnennung": bohrdaten.namensnennung(d, heute),
            "abgerufen": heute.isoformat(),
            "coord_source": f"SGD {d['land']} (WMS-GetFeatureInfo)",
            "profil_url": t.get("profil"),
            "issues": [hinweis],
        })
    return {"boreholes": bohrungen_liste}
