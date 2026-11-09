"""Bohrdaten aus vom Nutzer heruntergeladenen oder vom Landesamt gelieferten Dateien (docs/26 §2 und §3, Option c).
Unterstuetzte Formate (jeweils auch einzeln in einem .zip-Archiv):
  - .xml (BoreholeML 3.0–3.2): ueber boreholeml.importieren
  - .gml (INSPIRE ge:Borehole): nur Kopfdaten, layers: []
  - .gpkg (GeoPackage): ueber sqlite3 (mode=ro) aus temporaerer Datei, Tabelle aus gpkg_contents, Punkt aus
    GeoPackage-Blob oder zugeordneten Spalten
  - .csv: Trenner ; oder ,, Dezimalkomma, UTF-8 oder cp1252, nur mit ausdruecklicher Zuordnung
  - .rar: wird mit klarer Meldung abgelehnt (keine neue Abhaengigkeit)
Unverhandelbar (AGENTS.md):
  - Niemals Schichten erfinden: ohne Schichtdaten bleibt layers: [] mit Hinweis in issues.
  - soil_class nur ueber boreholeml.bodenart_aus aus erkannten Codes, sonst None.
  - Jede Schicht bekommt confidence = bohrdaten.KONFIDENZ_ARCHIV (0.5).
  - Zeile ohne Lage, Lage ausserhalb Deutschlands (laender.land_am_punkt), doppelte id oder nicht zuordenbare Zahl
    kommen mit Zeile und Grund in abgelehnt, werden nie still ausgelassen.
  - Luecken, Ueberlappungen oder von >= bis werden in issues markiert, nicht repariert.
  - Nur Koordinatensysteme, die utm_normal kennt; alles andere ValueError mit dem EPSG im Text.
"""
from __future__ import annotations
import csv
import hashlib
import io
import math
import re
import sqlite3
import struct
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from pathlib import Path
from . import bohrdaten, boreholeml, laender, utm
from .utm import utm_normal
MAX_ENTPACKT = 200 * 1024 * 1024                # 200 MB Grenze beim Entpacken aus ZIP (Schutz vor Zip-Bomben)
ENDUNGEN = (".xml", ".gml", ".gpkg", ".csv")
_DOCTYPE_RE = re.compile(rb"<!\s*(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)
_EPSG_ENDE_RE = re.compile(r"(\d+)\s*$")
_VORSCHLAG_KANDIDATEN: dict[str, tuple[str, ...]] = {
    "id": ("id", "bo_ident", "bohr_id", "bohrung_id", "schluessel", "gml_id", "ident", "akbez", "bid", "fid"),
    "name": ("name", "longname", "langname", "bohrname", "bohrung", "bezeichnung", "shortname", "kurzname", "code"),
    "x": ("x", "rw", "rechtswert", "easting", "ostwert", "xcoord", "x_utm", "x_4647", "rechts"),
    "y": ("y", "hw", "hochwert", "northing", "nordwert", "ycoord", "y_utm", "y_4647", "hoch"),
    "epsg": ("epsg", "crs", "crs_epsg", "srs", "srid", "ksys"),
    "gok": ("gok", "gok_nhn", "gok_m_nhn", "gok_m_nn", "zcoordb", "ansatzhoehe", "hoehe_bohransatz", "surfacelevel", "ansatz", "hoehe"),
    "teufe": ("teufe", "endteufe", "endteufe_m", "endtiefe", "end_depth", "zcoorde", "totallength", "boreholelength", "tiefe", "laenge"),
    "datum": ("datum", "bohrdatum", "bohrende", "bohrung_bis", "bohrung_von", "drillingdate", "yrfromname", "yfromname", "jahr", "date"),
    "von": ("von", "top_depth", "tiefe_von", "from", "schicht_von", "oberkante", "ok"),
    "bis": ("bis", "bottom_depth", "tiefe_bis", "to", "schicht_bis", "unterkante", "uk"),
    "petrographie": ("petrographie", "petro", "rockname", "rock_name", "rockcode", "rock_code", "sep3", "bodenart_code", "hauptbodenart", "symbol"),
    "beschreibung": ("beschreibung", "description_raw", "descriptivetext", "rocknametext", "schichtbeschreibung", "benennung", "text"),
}
_ZUORDNUNG_FELDER = tuple(_VORSCHLAG_KANDIDATEN)


def _lokal(el: ET.Element) -> str:
    _, _, name = el.tag.rpartition("}")
    return name


def _kind(el: ET.Element, name: str) -> ET.Element | None:
    return next((c for c in el if _lokal(c) == name), None)


def _textwert(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return " ".join(t.strip() for t in el.itertext() if t.strip())


def _ist_nil(el: ET.Element | None) -> bool:
    if el is None:
        return True
    return el.get(f"{{{boreholeml.XSI}}}nil", "").lower() == "true"


def _quote_ident(name: str) -> str:
    """Quotet einen aus der Datei gelesenen SQL-Tabellen- oder Spaltennamen."""
    return '"' + str(name).replace('"', '""') + '"'


def _leerer_wert(wert: object) -> bool:
    if wert is None:
        return True
    text = str(wert).strip()
    return not text or text.lower() in ("null", "none", "nan", "-")


def _zahl_strikt(wert: object) -> tuple[float | None, bool]:
    """Parst eine Zahl (auch mit Dezimalkomma). Rueckgabe: (wert, ok). Leere Werte sind (None, True)."""
    if _leerer_wert(wert):
        return None, True
    if isinstance(wert, (int, float)) and not isinstance(wert, bool):
        v = float(wert)
        return (v, True) if math.isfinite(v) else (None, False)
    text = str(wert).strip().replace(",", ".")
    try:
        v = float(text)
    except ValueError:
        return None, False
    return (v, True) if math.isfinite(v) else (None, False)


def _datum_text(wert: object) -> str | None:
    if _leerer_wert(wert):
        return None
    text = str(wert).strip()
    m = re.match(r"^(\d{2})\.(\d{2})\.(\d{4})$", text)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return text[:10]


def _epsg_normal_pruefen(epsg: object) -> int:
    """Prueft das EPSG gegen utm_normal (hebt 5554..5556 vorher auf 25831..25833); sonst ValueError mit EPSG."""
    if _leerer_wert(epsg):
        raise ValueError("Kein Koordinatensystem (EPSG) angegeben")
    text = str(epsg).strip()
    m = _EPSG_ENDE_RE.search(text)
    if not m:
        raise ValueError(f"EPSG:{text} – ungültige EPSG-Angabe")
    code = int(m.group(1))
    code = boreholeml.HORIZONTAL.get(code, code)
    utm_normal(0.0, 0.0, code)
    return code


def _entpacken_einzeln(daten: bytes, name: str, max_groesse: int | None = None) -> tuple[bytes, str]:
    """Entpackt eine einzelne unterstuetzte Datei aus einem .zip; lehnt .rar und zu grosse Archive ab."""
    grenze = MAX_ENTPACKT if max_groesse is None else max_groesse
    klein = name.lower()
    if klein.endswith(".rar") or daten[:6] == b"Rar!\x1a\x07":
        raise ValueError(f"{name}: RAR-Archiv (.rar) wird nicht unterstützt – bitte vorher entpacken")
    if klein.endswith(".zip") or daten[:4] == b"PK\x03\x04":
        try:
            archiv = zipfile.ZipFile(io.BytesIO(daten))
        except zipfile.BadZipFile as err:
            raise ValueError(f"{name}: ZIP-Archiv nicht lesbar ({err})") from None
        kandidaten: list[zipfile.ZipInfo] = []
        for eintrag in archiv.infolist():
            if eintrag.is_dir():
                continue
            eklein = eintrag.filename.lower()
            basis = Path(eintrag.filename).name
            if "__macosx/" in eklein or basis.startswith("._"):
                continue
            if eklein.endswith(".rar"):
                raise ValueError(f"{name}: RAR-Archiv ({eintrag.filename}) im ZIP wird nicht unterstützt")
            if eklein.endswith(ENDUNGEN):
                kandidaten.append(eintrag)
        if not kandidaten:
            raise ValueError(f"{name}: keine unterstützte Bohrdaten-Datei (.xml, .gml, .gpkg, .csv) im ZIP")
        if len(kandidaten) > 1:
            raise ValueError(f"{name}: mehrere Bohrdaten-Dateien im ZIP – nur eine Datei je Archiv erlaubt")
        ziel = kandidaten[0]
        if ziel.file_size > grenze:
            raise ValueError(f"{ziel.filename}: Datei im ZIP zu groß ({ziel.file_size} Bytes > {grenze} Bytes)")
        with archiv.open(ziel) as quelle:
            inhalt = quelle.read(grenze + 1)
        if len(inhalt) > grenze:
            raise ValueError(f"{ziel.filename}: entpackte Datei überschreitet Größengrenze ({grenze} Bytes)")
        return inhalt, Path(ziel.filename).name
    return daten, name


def _xml_sicher_wurzel(daten: bytes, name: str) -> ET.Element:
    if _DOCTYPE_RE.search(daten):
        raise ValueError(f"{name}: unsicheres XML – DOCTYPE/ENTITY wird abgelehnt")
    try:
        wurzel = ET.fromstring(daten)
    except ET.ParseError as err:
        raise ValueError(f"{name}: kein lesbares XML ({err})") from None
    if _lokal(wurzel) in ("ExceptionReport", "ServiceExceptionReport"):
        raise ValueError(f"{name}: Fehlermeldung des Dienstes – {_textwert(wurzel)[:240]}")
    return wurzel


def _format_erkennen(daten: bytes, name: str) -> str:
    klein = name.lower()
    if klein.endswith(".rar") or daten[:6] == b"Rar!\x1a\x07":
        raise ValueError(f"{name}: RAR-Archiv (.rar) wird nicht unterstützt")
    if klein.endswith(".gpkg") or daten[:16] == b"SQLite format 3\x00":
        return "gpkg"
    if klein.endswith(".csv"):
        return "csv"
    if klein.endswith((".xml", ".gml")):
        wurzel = _xml_sicher_wurzel(daten, name)
        if any("boreholeml" in el.tag for el in wurzel.iter()):
            return "boreholeml"
        if any(_lokal(el) == "Borehole" for el in wurzel.iter()):
            return "inspire-gml"
        return "boreholeml" if klein.endswith(".xml") else "inspire-gml"
    raise ValueError(f"{name}: nicht unterstütztes Dateiformat (erlaubt: .xml, .gml, .gpkg, .csv, .zip)")


def _spalten_vorschlagen(
    spalten: list[str],
    geom_spalte: str | None = None,
    epsg: int | None = None,
    tabelle: str | None = None,
) -> dict:
    norm_map: dict[str, str] = {}
    for s in spalten:
        if s == geom_spalte:
            continue
        schluessel = s.strip().lower().replace("-", "_").replace(" ", "_")
        norm_map.setdefault(schluessel, s)
    vorschlag: dict[str, str | int] = {}
    if tabelle:
        vorschlag["tabelle"] = tabelle
    for feld, kandidaten in _VORSCHLAG_KANDIDATEN.items():
        for k in kandidaten:
            if k in norm_map:
                vorschlag[feld] = norm_map[k]
                break
    if "epsg" not in vorschlag and epsg is not None:
        vorschlag["epsg"] = epsg
    return vorschlag


# ---------------------------------------------------------------- GeoPackage-Hilfen
def _gpkg_punkt(blob: bytes | None) -> tuple[float | None, float | None, int | None]:
    """Liest (x, y, srs_id) aus einem OGC GeoPackage-Binary-Header + WKB-Point (oder reinem WKB-Point)."""
    if not blob or not isinstance(blob, (bytes, bytearray, memoryview)):
        return None, None, None
    b = bytes(blob)
    srs_id: int | None = None
    if len(b) >= 8 and b[:2] == b"GP":
        flags = b[3]
        if (flags >> 4) & 0x01:                     # Empty-Geometry-Flag
            return None, None, None
        h_endian = "<" if (flags & 0x01) else ">"
        srs_id = struct.unpack(h_endian + "i", b[4:8])[0]
        env_code = (flags >> 1) & 0x07
        env_bytes = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}.get(env_code)
        if env_bytes is None or len(b) < 8 + env_bytes + 21:
            return None, None, srs_id
        wkb = b[8 + env_bytes:]
    elif len(b) >= 21 and b[0] in (0, 1):
        wkb = b
    else:
        return None, None, None
    w_endian = "<" if wkb[0] == 1 else ">"
    wkb_typ = struct.unpack(w_endian + "I", wkb[1:5])[0]
    basis_typ = (wkb_typ & 0xFF) if (wkb_typ & 0xFF) <= 7 else (wkb_typ % 1000)
    if basis_typ != 1:
        return None, None, srs_id
    x, y = struct.unpack(w_endian + "dd", wkb[5:21])
    if not math.isfinite(x) or not math.isfinite(y):
        return None, None, srs_id
    return float(x), float(y), srs_id


def _epsg_aus_wkt(definition: str | None) -> int | None:
    """Erkennt ETRS89/UTM (25831..25833, 4647, 5650) aus der WKT-Definition in gpkg_spatial_ref_sys, wenn das
    Landesamt (wie MV in bohrdaten_dl.gpkg) eine interne srs_id=100000 statt des EPSG-Codes eingetragen hat."""
    if not definition:
        return None
    wkt = definition.upper()
    if "ETRS" not in wkt or "TRANSVERSE_MERCATOR" not in wkt:
        return None
    m_cm = re.search(r'PARAMETER\s*\[\s*"CENTRAL_MERIDIAN"\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\]', wkt)
    m_fe = re.search(r'PARAMETER\s*\[\s*"FALSE_EASTING"\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\]', wkt)
    if not m_cm or not m_fe:
        return None
    cm = round(float(m_cm.group(1)))
    fe = round(float(m_fe.group(1)))
    bekannt = {
        (3, 500_000): 25831,
        (9, 500_000): 25832,
        (9, 32_500_000): 4647,
        (15, 500_000): 25833,
        (15, 33_500_000): 5650,
    }
    return bekannt.get((cm, fe))


def _gpkg_srs_aufloesen(cur: sqlite3.Cursor, srs_id: int | None) -> int | None:
    if srs_id is None:
        return None
    code = int(srs_id)
    if code in utm._UTM or code in boreholeml.HORIZONTAL:
        return boreholeml.HORIZONTAL.get(code, code)
    try:
        zeile = cur.execute(
            "SELECT organization, organization_coordsys_id, definition FROM gpkg_spatial_ref_sys WHERE srs_id = ?",
            (code,),
        ).fetchone()
    except sqlite3.Error:
        zeile = None
    if zeile:
        org, org_id, wkt = zeile
        if org_id is not None:
            org_code = int(org_id)
            if isinstance(org, str) and org.upper() == "EPSG":
                return boreholeml.HORIZONTAL.get(org_code, org_code)
        aus_wkt = _epsg_aus_wkt(wkt)
        if aus_wkt is not None:
            return aus_wkt
    return code


def _gpkg_oeffnen_ro(daten: bytes, name: str):
    """Schreibt die GeoPackage-Bytes in eine temporaere Datei und oeffnet sie mit sqlite3 im Modus mode=ro."""
    if len(daten) < 16 or daten[:16] != b"SQLite format 3\x00":
        raise ValueError(f"{name}: keine gültige GeoPackage-/SQLite-Datei")
    tmp = tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False)
    pfad = Path(tmp.name)
    try:
        tmp.write(daten)
    finally:
        tmp.close()
    uri = f"file:{pfad.as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    return con, pfad


def _gpkg_metadaten(cur: sqlite3.Cursor, name: str, wunsch_tabelle: str | None = None) -> tuple[list[str], str, list[str], str | None, str | None, int | None]:
    try:
        eintraege = cur.execute("SELECT table_name, data_type, srs_id FROM gpkg_contents").fetchall()
    except sqlite3.Error as err:
        raise ValueError(f"{name}: gpkg_contents fehlt oder ist unlesbar ({err})") from None
    if not eintraege:
        raise ValueError(f"{name}: gpkg_contents enthält keine Tabellen")
    tabellen = [str(r[0]) for r in eintraege if r[0]]
    features = [str(r[0]) for r in eintraege if str(r[1] or "").lower() == "features" and r[0]]
    srs_map = {str(r[0]): r[2] for r in eintraege if r[0]}
    if wunsch_tabelle:
        if wunsch_tabelle not in tabellen:
            raise ValueError(f"{name}: Tabelle {wunsch_tabelle!r} nicht in gpkg_contents ({tabellen})")
        tabelle = next(t for t in tabellen if t == wunsch_tabelle)
    else:
        tabelle = features[0] if features else tabellen[0]
    info = cur.execute(f"PRAGMA table_info({_quote_ident(tabelle)})").fetchall()
    if not info:
        raise ValueError(f"{name}: Tabelle {tabelle!r} hat keine Spalten")
    spalten = [str(r[1]) for r in info]
    pk_spalte = next((str(r[1]) for r in info if r[5]), None)
    geom_spalte: str | None = None
    geom_srs: int | None = srs_map.get(tabelle)
    try:
        gzeile = cur.execute(
            "SELECT column_name, srs_id FROM gpkg_geometry_columns WHERE table_name = ?",
            (tabelle,),
        ).fetchone()
    except sqlite3.Error:
        gzeile = None
    if gzeile and gzeile[0] in spalten:
        geom_spalte = next(s for s in spalten if s == gzeile[0])
        if gzeile[1] is not None:
            geom_srs = gzeile[1]
    else:
        geom_spalte = next(
            (str(r[1]) for r in info if str(r[2] or "").upper() in ("POINT", "GEOMETRY", "BLOB")),
            None,
        )
    epsg = _gpkg_srs_aufloesen(cur, geom_srs)
    return tabellen, tabelle, spalten, geom_spalte, pk_spalte, epsg


# ---------------------------------------------------------------- CSV-Hilfen
def _csv_dekodieren(daten: bytes, name: str) -> tuple[str, str]:
    if b"\x00" in daten:
        raise ValueError(f"{name}: Datei enthält Binärdaten (NUL-Bytes) statt CSV-Text")
    try:
        return daten.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        try:
            return daten.decode("cp1252"), "cp1252"
        except UnicodeDecodeError as err:
            raise ValueError(f"{name}: Textkodierung weder UTF-8 noch cp1252 ({err})") from None


def _csv_trenner(text: str) -> str:
    erste = next((z for z in text.splitlines() if z.strip()), "")
    return "," if erste.count(",") > erste.count(";") else ";"


# ---------------------------------------------------------------- Vorschlag
def felder_vorschlagen(daten: bytes, name: str) -> dict:
    """Spalten bzw. Tabellen der Datei und ein unverbindlicher Vorschlag fuer die Zuordnung (`vorschlag`).
    `lesen` wendet diesen Vorschlag niemals stillschweigend an."""
    inhalt, inner_name = _entpacken_einzeln(daten, name)
    fmt = _format_erkennen(inhalt, inner_name)
    if fmt == "gpkg":
        con, pfad = _gpkg_oeffnen_ro(inhalt, inner_name)
        try:
            cur = con.cursor()
            tabellen, tabelle, spalten, geom_spalte, _, epsg = _gpkg_metadaten(cur, inner_name)
        finally:
            con.close()
            pfad.unlink(missing_ok=True)
        vorschlag = _spalten_vorschlagen(spalten, geom_spalte=geom_spalte, epsg=epsg, tabelle=tabelle)
        return {
            "datei": inner_name,
            "format": "gpkg",
            "tabellen": tabellen,
            "tabelle": tabelle,
            "spalten": spalten,
            "geometrie_spalte": geom_spalte,
            "epsg": epsg,
            "trenner": None,
            "kodierung": None,
            "vorschlag": vorschlag,
        }
    if fmt == "csv":
        text, kodierung = _csv_dekodieren(inhalt, inner_name)
        trenner = _csv_trenner(text)
        leser = csv.reader(io.StringIO(text), delimiter=trenner)
        kopf = next(([s.strip() for s in z] for z in leser if any(s.strip() for s in z)), [])
        if not kopf:
            raise ValueError(f"{inner_name}: CSV-Datei ist leer oder hat keine Kopfzeile")
        vorschlag = _spalten_vorschlagen(kopf)
        return {
            "datei": inner_name,
            "format": "csv",
            "tabellen": [],
            "tabelle": None,
            "spalten": kopf,
            "geometrie_spalte": None,
            "epsg": None,
            "trenner": trenner,
            "kodierung": kodierung,
            "vorschlag": vorschlag,
        }
    wurzel = _xml_sicher_wurzel(inhalt, inner_name)
    srs = next((el.get("srsName") for el in wurzel.iter() if el.get("srsName")), None)
    m = _EPSG_ENDE_RE.search(srs or "")
    epsg = boreholeml.HORIZONTAL.get(int(m.group(1)), int(m.group(1))) if m else None
    return {
        "datei": inner_name,
        "format": fmt,
        "tabellen": [],
        "tabelle": None,
        "spalten": [],
        "geometrie_spalte": None,
        "epsg": epsg,
        "trenner": None,
        "kodierung": None,
        "vorschlag": {"epsg": epsg} if epsg is not None else {},
    }


# ---------------------------------------------------------------- Herkunft & Schichtpruefung
def _quelle_daten(quelle: dict | None, name: str, heute: date) -> tuple[str, str, str, str, str, str, bool]:
    q = quelle or {}
    kennung = str(q.get("kennung") or "DATEI").strip()
    titel = str(q.get("titel") or name).strip()
    land = str(q.get("land") or "").strip()
    lizenz_roh = str(q.get("lizenz") or "").strip()
    lizenz_fehlt = not lizenz_roh or lizenz_roh.lower() == "unbekannt"
    lizenz = "unbekannt" if lizenz_fehlt else lizenz_roh
    nennung = str(q.get("namensnennung") or "").replace("{jahr}", str(heute.year)).strip()
    url = str(q.get("url") or "").strip()
    return kennung, titel, land, lizenz, nennung, url, lizenz_fehlt


def _schichten_markieren(schichten: list[dict], hinweise: list[str]) -> None:
    """Prueft Schichten auf von >= bis, Luecken und Ueberlappungen (nur markieren in issues, nie reparieren!)
    und setzt confidence = KONFIDENZ_ARCHIV."""
    vorher_bis: float | None = None
    for ly in schichten:
        ly["confidence"] = bohrdaten.KONFIDENZ_ARCHIV
        ly.setdefault("issues", [])
        von, bis = float(ly["top_depth"]), float(ly["bottom_depth"])
        if von < 0:
            meldung = f"Schicht {von:g}–{bis:g} m: negative Tiefe"
            ly["issues"].append(meldung)
            hinweise.append(meldung)
        if von >= bis:
            meldung = f"Schicht {von:g}–{bis:g} m: ungültige Tiefenlage (von >= bis)"
            ly["issues"].append(meldung)
            hinweise.append(meldung)
        if vorher_bis is not None:
            if von > vorher_bis + 1e-6:
                meldung = f"Lücke im Schichtenverzeichnis zwischen {vorher_bis:g} m und {von:g} m"
                ly["issues"].append(meldung)
                hinweise.append(meldung)
            elif von < vorher_bis - 1e-6:
                meldung = f"Überlappung im Schichtenverzeichnis bei {von:g} m (vorherige Schicht bis {vorher_bis:g} m)"
                ly["issues"].append(meldung)
                hinweise.append(meldung)
        vorher_bis = bis


def _schicht_bauen(von: float, bis: float, petro: str | None, beschreibung: str | None, methode: str) -> dict:
    petro_code = (petro or "").strip() or None
    klasse, hinweis = boreholeml.bodenart_aus(petro_code, None)
    text = (beschreibung or "").strip()
    return {
        "top_depth": von,
        "bottom_depth": bis,
        "description_raw": text,
        "soil_class": klasse,
        "hatch_class": None,
        "confidence": bohrdaten.KONFIDENZ_ARCHIV,
        "label_confirmed": None,
        "issues": [hinweis] if hinweis else [],
        "rock_code": petro_code,
        "provenance": [{"page": None, "method": methode}],
    }


def _bohrung_abschliessen(
    b: dict,
    quelle_info: tuple[str, str, str, str, str, str, bool],
    heute: date,
    datei_name: str,
) -> dict:
    kennung, titel, land, lizenz, nennung, url, lizenz_fehlt = quelle_info
    fremd_id = str(b.get("fremd_id") or b.get("code") or "?").strip()
    kurzname = str(b.get("name") or b.get("code") or fremd_id).strip()
    praefix = f"{kennung}-"
    code = kurzname if kurzname.startswith(praefix) else f"{kennung}-{kurzname}"
    vorhandene_issues = list(b.get("issues") or [])
    if vorhandene_issues and vorhandene_issues[0].startswith("aus ") and "nicht aus dem Gutachten" in vorhandene_issues[0]:
        vorhandene_issues = vorhandene_issues[1:]
    schichten = b.get("layers") or []
    _schichten_markieren(schichten, vorhandene_issues)
    if not schichten:
        if not any("ohne Schichtdaten" in h or "nur Kopfdaten" in h for h in vorhandene_issues):
            vorhandene_issues.append("ohne Schichtdaten (nur Kopfdaten in der Datei)")
    elif all(ly.get("soil_class") is None for ly in schichten):
        if not any("ohne Petrographie" in h or "unklassifiziert" in h for h in vorhandene_issues):
            vorhandene_issues.append("Schichten ohne Petrographie (unklassifiziert)")
    if lizenz_fehlt:
        vorhandene_issues.append("Lizenz in der Quelle fehlt (als unbekannt markiert)")
    erster_hinweis = (
        f"aus {titel}{f' ({land})' if land else ''}, ID {fremd_id}, {lizenz}, "
        f"abgerufen {heute.strftime('%d.%m.%Y')} – nicht aus dem Gutachten"
    )
    b.update(
        code=code,
        name=kurzname,
        kind="Bohrung",
        fremd_id=fremd_id,
        herkunft="SGD",
        quelle=kennung,
        lizenz=lizenz,
        namensnennung=nennung,
        abgerufen=heute.isoformat(),
        url=url or None,
        coord_source=f"SGD {land}".strip(),
        layers=schichten,
        issues=[erster_hinweis] + vorhandene_issues,
    )
    b.setdefault("groundwater", [])
    b.setdefault("groundwater_status", "")
    b.setdefault("checks", {})
    b.setdefault("provenance", [{"page": None, "bbox": None, "method": f"Datei ({datei_name})"}])
    return b


def _lage_pruefen(
    rohx: float | None,
    rohy: float | None,
    epsg: int,
    punkt_land: dict[tuple[float, float], str | None],
) -> tuple[float | None, float | None, int | None, str | None]:
    """Normalisiert (rohx, rohy, epsg) ueber utm_normal und prueft laender.land_am_punkt."""
    if rohx is None or rohy is None:
        return None, None, None, "ohne Lage"
    nx, ny, nepsg = utm_normal(rohx, rohy, epsg)
    schluessel = (round(nx, 3), round(ny, 3))
    if schluessel not in punkt_land:
        lon, lat = utm.zu_geo(nx, ny, utm.zone(nepsg))
        punkt_land[schluessel] = laender.land_am_punkt(float(lon), float(lat))
    if not punkt_land[schluessel]:
        return None, None, None, "Lage außerhalb Deutschlands"
    return nx, ny, nepsg, None


def _zuordnung_bereinigen(zuordnung: dict | None) -> dict | None:
    if zuordnung is None:
        return None
    if not isinstance(zuordnung, dict):
        raise ValueError("zuordnung muss ein Dictionary sein")
    if isinstance(zuordnung.get("vorschlag"), dict):
        basis = dict(zuordnung["vorschlag"])
        for k in ("tabelle", "epsg"):
            if k in zuordnung and k not in basis and zuordnung[k] is not None:
                basis[k] = zuordnung[k]
        return basis
    return dict(zuordnung)


# ---------------------------------------------------------------- Format-Leser
def _lesen_boreholeml(
    daten: bytes,
    inner_name: str,
    quelle_info: tuple[str, str, str, str, str, str, bool],
    heute: date,
) -> tuple[list[dict], list[dict]]:
    _xml_sicher_wurzel(daten, inner_name)
    roh = boreholeml.importieren(daten, inner_name)
    bohrungen: list[dict] = []
    abgelehnt: list[dict] = []
    gesehene_ids: set[str] = set()
    punkt_land: dict[tuple[float, float], str | None] = {}
    for zeile_nr, b in enumerate(roh.get("boreholes") or [], start=1):
        fremd_id = str(b.get("fremd_id", "")).strip()
        if not fremd_id:
            abgelehnt.append({"zeile": zeile_nr, "grund": "fehlende ID"})
            continue
        if fremd_id in gesehene_ids:
            abgelehnt.append({"zeile": zeile_nr, "grund": f"doppelte id: {fremd_id}"})
            continue
        gesehene_ids.add(fremd_id)
        epsg = _epsg_normal_pruefen(b.get("crs_epsg"))
        nx, ny, nepsg, grund = _lage_pruefen(b.get("x"), b.get("y"), epsg, punkt_land)
        if grund:
            abgelehnt.append({"zeile": zeile_nr, "grund": grund})
            continue
        schichten = b.get("layers") or []
        if any(ly.get("top_depth") is None or ly.get("bottom_depth") is None for ly in schichten):
            abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in Schichttiefe"})
            continue
        b["x"], b["y"], b["crs_epsg"] = nx, ny, nepsg
        b["fremd_id"] = fremd_id
        b["name"] = b.get("code") or fremd_id
        bohrungen.append(_bohrung_abschliessen(b, quelle_info, heute, inner_name))
    return bohrungen, abgelehnt


def _lesen_inspire_gml(
    daten: bytes,
    inner_name: str,
    quelle_info: tuple[str, str, str, str, str, str, bool],
    heute: date,
) -> tuple[list[dict], list[dict]]:
    wurzel = _xml_sicher_wurzel(daten, inner_name)
    rahmen_srs = next((el.get("srsName") for el in wurzel.iter() if _lokal(el) == "Envelope" and el.get("srsName")), None)
    if rahmen_srs:
        _epsg_normal_pruefen(rahmen_srs)
    merkmale = [el for el in wurzel.iter() if _lokal(el) == "Borehole" and "boreholeml" not in el.tag]
    if not merkmale:
        raise ValueError(f"{inner_name}: keine INSPIRE-Bohrung (ge:Borehole) gefunden")
    bohrungen: list[dict] = []
    abgelehnt: list[dict] = []
    gesehene_ids: set[str] = set()
    punkt_land: dict[tuple[float, float], str | None] = {}
    for zeile_nr, bh in enumerate(merkmale, start=1):
        local_id = next((_textwert(el) for el in bh.iter() if _lokal(el) == "localId" and _textwert(el)), "")
        gml_ident = _textwert(_kind(bh, "identifier"))
        gml_id = bh.get(f"{{{boreholeml.GML}}}id") or bh.get("id") or ""
        fremd_id = (local_id or gml_ident or gml_id).strip()
        if not fremd_id:
            abgelehnt.append({"zeile": zeile_nr, "grund": "fehlende ID"})
            continue
        if fremd_id in gesehene_ids:
            abgelehnt.append({"zeile": zeile_nr, "grund": f"doppelte id: {fremd_id}"})
            continue
        gesehene_ids.add(fremd_id)
        kurzname = _textwert(_kind(bh, "name")) or fremd_id
        punkt = next((el for el in bh.iter() if _lokal(el) == "Point"), None)
        pos_text = _textwert(_kind(punkt, "pos")) if punkt is not None else ""
        if not pos_text:
            abgelehnt.append({"zeile": zeile_nr, "grund": "ohne Lage"})
            continue
        srs = (punkt.get("srsName") if punkt is not None else None) or rahmen_srs
        epsg = _epsg_normal_pruefen(srs)
        teile = pos_text.split()
        if len(teile) < 2:
            abgelehnt.append({"zeile": zeile_nr, "grund": "ohne Lage"})
            continue
        rohx, ok_x = _zahl_strikt(teile[0])
        rohy, ok_y = _zahl_strikt(teile[1])
        if not ok_x or not ok_y:
            abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in Koordinaten"})
            continue
        nx, ny, nepsg, grund = _lage_pruefen(rohx, rohy, epsg, punkt_land)
        if grund:
            abgelehnt.append({"zeile": zeile_nr, "grund": grund})
            continue
        gok: float | None = None
        el_elev = _kind(bh, "elevation")
        if el_elev is not None and not _ist_nil(el_elev) and _textwert(el_elev):
            gok, ok_gok = _zahl_strikt(_textwert(el_elev))
            if not ok_gok:
                abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in elevation"})
                continue
        teufe: float | None = None
        el_len = _kind(bh, "boreholeLength")
        if el_len is not None and not _ist_nil(el_len):
            val_el = next((el for el in el_len.iter() if _lokal(el) == "value" and _textwert(el)), None)
            roh_len = _textwert(val_el) if val_el is not None else _textwert(el_len)
            if not roh_len:
                roh_len = el_len.get("{http://www.w3.org/1999/xlink}href") or ""
            if roh_len:
                teufe, ok_teufe = _zahl_strikt(roh_len)
                if not ok_teufe or (teufe is not None and teufe < 0):
                    abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in boreholeLength"})
                    continue
        b = {
            "code": kurzname,
            "name": kurzname,
            "fremd_id": fremd_id,
            "kind": "Bohrung",
            "x": nx,
            "y": ny,
            "crs_epsg": nepsg,
            "gok_nhn": gok,
            "gok_source": "SGD" if gok is not None else None,
            "end_depth": teufe if (teufe is not None and teufe > 0) else None,
            "layers": [],
            "issues": ["ohne Schichtdaten (INSPIRE ge:Borehole enthält nur Kopfdaten)"],
        }
        bohrungen.append(_bohrung_abschliessen(b, quelle_info, heute, inner_name))
    return bohrungen, abgelehnt


def _tabellen_zeilen_verarbeiten(
    zeilen_iter,
    spalten_index: dict[str, int],
    z_map: dict[str, str],
    festes_epsg: int | None,
    geom_idx: int | None,
    cur_gpkg: sqlite3.Cursor | None,
    quelle_info: tuple[str, str, str, str, str, str, bool],
    heute: date,
    inner_name: str,
    start_zeile: int = 1,
) -> tuple[list[dict], list[dict]]:
    hat_schichten = "von" in z_map or "bis" in z_map
    if hat_schichten and ("von" not in z_map or "bis" not in z_map):
        raise ValueError(f"{inner_name}: für Schichten im Langformat müssen sowohl 'von' als auch 'bis' zugeordnet sein")
    kandidaten: list[tuple[int, dict]] = []
    bohrungen_nach_id: dict[str, dict] = {}
    gesehene_ids: set[str] = set()
    abgelehnt: list[dict] = []
    def zelle(zeile: tuple | list, feld: str) -> object:
        sp = z_map.get(feld)
        if not sp:
            return None
        idx = spalten_index[sp]
        return zeile[idx] if idx < len(zeile) else None
    for zeile_nr, zeile in enumerate(zeilen_iter, start=start_zeile):
        roh_id = zelle(zeile, "id")
        if _leerer_wert(roh_id):
            abgelehnt.append({"zeile": zeile_nr, "grund": "fehlende ID"})
            continue
        fremd_id = str(roh_id).strip()
        if not hat_schichten and fremd_id in gesehene_ids:
            abgelehnt.append({"zeile": zeile_nr, "grund": f"doppelte id: {fremd_id}"})
            continue
        if "epsg" in z_map:
            roh_epsg = zelle(zeile, "epsg")
            epsg_wert, ok_epsg = _zahl_strikt(roh_epsg)
            if not ok_epsg or epsg_wert is None:
                abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in epsg"})
                gesehene_ids.add(fremd_id)
                continue
            zeilen_epsg = _epsg_normal_pruefen(int(epsg_wert))
        else:
            zeilen_epsg = festes_epsg
        rohx = rohy = None
        if "x" in z_map and "y" in z_map:
            rohx, ok_x = _zahl_strikt(zelle(zeile, "x"))
            rohy, ok_y = _zahl_strikt(zelle(zeile, "y"))
            if not ok_x or not ok_y:
                abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in Koordinaten (x/y)"})
                gesehene_ids.add(fremd_id)
                continue
        if (rohx is None or rohy is None) and geom_idx is not None and geom_idx < len(zeile):
            gx, gy, blob_srs = _gpkg_punkt(zeile[geom_idx])
            rohx, rohy = gx, gy
            if zeilen_epsg is None and blob_srs is not None and cur_gpkg is not None:
                aufgeloest = _gpkg_srs_aufloesen(cur_gpkg, blob_srs)
                if aufgeloest is not None:
                    zeilen_epsg = _epsg_normal_pruefen(aufgeloest)
        if zeilen_epsg is None:
            raise ValueError(f"{inner_name}: kein Koordinatensystem (EPSG) angegeben")
        gok, ok_gok = _zahl_strikt(zelle(zeile, "gok"))
        teufe, ok_teufe = _zahl_strikt(zelle(zeile, "teufe"))
        if not ok_gok:
            abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in gok"})
            gesehene_ids.add(fremd_id)
            continue
        if not ok_teufe or (teufe is not None and teufe < 0):
            abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in teufe"})
            gesehene_ids.add(fremd_id)
            continue
        schicht: dict | None = None
        if hat_schichten:
            von, ok_von = _zahl_strikt(zelle(zeile, "von"))
            bis, ok_bis = _zahl_strikt(zelle(zeile, "bis"))
            if not ok_von or not ok_bis or von is None or bis is None:
                abgelehnt.append({"zeile": zeile_nr, "grund": "nicht zuordenbare Zahl in Schichttiefe (von/bis)"})
                continue
            petro_roh = zelle(zeile, "petrographie")
            beschr_roh = zelle(zeile, "beschreibung")
            schicht = _schicht_bauen(
                von,
                bis,
                None if _leerer_wert(petro_roh) else str(petro_roh),
                None if _leerer_wert(beschr_roh) else str(beschr_roh),
                f"Datei ({inner_name})",
            )
        if rohx is None or rohy is None:
            abgelehnt.append({"zeile": zeile_nr, "grund": "ohne Lage"})
            if not hat_schichten:
                gesehene_ids.add(fremd_id)
            continue
        nx, ny, nepsg = utm_normal(rohx, rohy, zeilen_epsg)
        if hat_schichten and fremd_id in bohrungen_nach_id:
            vorhanden = bohrungen_nach_id[fremd_id]
            if (nx, ny) != (vorhanden["x"], vorhanden["y"]):
                abgelehnt.append({"zeile": zeile_nr, "grund": f"doppelte id mit abweichender Lage: {fremd_id}"})
                continue
            if schicht is not None:
                vorhanden["layers"].append(schicht)
            continue
        if fremd_id in gesehene_ids:
            abgelehnt.append({"zeile": zeile_nr, "grund": f"doppelte id: {fremd_id}"})
            continue
        gesehene_ids.add(fremd_id)
        roh_name = zelle(zeile, "name")
        kurzname = str(roh_name).strip() if not _leerer_wert(roh_name) else fremd_id
        datum = _datum_text(zelle(zeile, "datum"))
        b = {
            "code": kurzname,
            "name": kurzname,
            "fremd_id": fremd_id,
            "kind": "Bohrung",
            "x": nx,
            "y": ny,
            "crs_epsg": nepsg,
            "gok_nhn": gok,
            "gok_source": "SGD" if gok is not None else None,
            "end_depth": teufe if (teufe is not None and teufe > 0) else None,
            "datum": datum,
            "layers": [schicht] if schicht is not None else [],
            "issues": [],
        }
        kandidaten.append((zeile_nr, b))
        if hat_schichten:
            bohrungen_nach_id[fremd_id] = b
    # Vektorisierte Umrechnung UTM -> (Laenge, Breite) je Zone und Pruefung ueber laender.land_am_punkt
    nach_zone: dict[int, list[int]] = {}
    for idx, (_, b) in enumerate(kandidaten):
        nach_zone.setdefault(utm.zone(b["crs_epsg"]), []).append(idx)
    lon_lat: list[tuple[float, float]] = [(0.0, 0.0)] * len(kandidaten)
    for zone_nr, indizes in nach_zone.items():
        xs = [kandidaten[i][1]["x"] for i in indizes]
        ys = [kandidaten[i][1]["y"] for i in indizes]
        lons, lats = utm.zu_geo(xs, ys, zone_nr)
        for i, lon, lat in zip(indizes, lons, lats):
            lon_lat[i] = (float(lon), float(lat))
    punkt_land: dict[tuple[float, float], str | None] = {}
    abgeschlossen: list[dict] = []
    for (zeile_nr, b), (lon, lat) in zip(kandidaten, lon_lat):
        schluessel = (round(b["x"], 3), round(b["y"], 3))
        if schluessel not in punkt_land:
            punkt_land[schluessel] = laender.land_am_punkt(lon, lat)
        if not punkt_land[schluessel]:
            abgelehnt.append({"zeile": zeile_nr, "grund": "Lage außerhalb Deutschlands"})
            continue
        abgeschlossen.append(_bohrung_abschliessen(b, quelle_info, heute, inner_name))
    abgelehnt.sort(key=lambda a: a["zeile"])
    return abgeschlossen, abgelehnt


def _spalten_aufloesen(spalten: list[str], zuordnung: dict, inner_name: str) -> tuple[dict[str, str], int | None]:
    """Prueft alle zugeordneten Spaltennamen gegen die echten Spalten der Datei; bestimmt ggf. ein festes EPSG."""
    echte: dict[str, str] = {}
    for s in spalten:
        echte[s] = s
        echte.setdefault(s.lower(), s)
    z_map: dict[str, str] = {}
    festes_epsg: int | None = None
    for feld in _ZUORDNUNG_FELDER:
        if feld not in zuordnung or _leerer_wert(zuordnung[feld]):
            continue
        wert = zuordnung[feld]
        if feld == "epsg":
            if isinstance(wert, str) and wert.strip() in echte:
                z_map["epsg"] = echte[wert.strip()]
            elif isinstance(wert, str) and wert.strip().lower() in echte:
                z_map["epsg"] = echte[wert.strip().lower()]
            elif isinstance(wert, int) or re.search(r"\d", str(wert)):
                festes_epsg = _epsg_normal_pruefen(wert)
            else:
                raise ValueError(f"{inner_name}: zugeordnete Spalte {wert!r} für 'epsg' existiert nicht in {spalten}")
            continue
        name = str(wert).strip()
        echter_name = echte.get(name) or echte.get(name.lower())
        if not echter_name:
            raise ValueError(f"{inner_name}: zugeordnete Spalte {name!r} für {feld!r} existiert nicht in {spalten}")
        z_map[feld] = echter_name
    return z_map, festes_epsg


def _lesen_gpkg(
    daten: bytes,
    inner_name: str,
    quelle_info: tuple[str, str, str, str, str, str, bool],
    zuordnung: dict | None,
    heute: date,
) -> tuple[list[dict], list[dict]]:
    con, pfad = _gpkg_oeffnen_ro(daten, inner_name)
    try:
        cur = con.cursor()
        wunsch_tabelle = str(zuordnung["tabelle"]).strip() if (zuordnung and zuordnung.get("tabelle")) else None
        _, tabelle, spalten, geom_spalte, pk_spalte, datei_epsg = _gpkg_metadaten(cur, inner_name, wunsch_tabelle)
        # lesen wendet nie still einen Vorschlag an: ohne zuordnung gelten nur der Standard-Geometrieblob und der PK
        if zuordnung:
            z_map, festes_epsg = _spalten_aufloesen(spalten, zuordnung, inner_name)
            if "id" not in z_map and pk_spalte:
                z_map["id"] = pk_spalte
        else:
            z_map = {"id": pk_spalte or spalten[0]}
            festes_epsg = None
        if ("x" in z_map) ^ ("y" in z_map):
            raise ValueError(f"{inner_name}: x und y müssen gemeinsam zugeordnet werden")
        if "x" not in z_map and not geom_spalte:
            raise ValueError(f"{inner_name}: weder Geometriespalte noch x/y-Spalten zugeordnet")
        wirksames_epsg = festes_epsg if festes_epsg is not None else datei_epsg
        if "epsg" not in z_map and wirksames_epsg is not None:
            wirksames_epsg = _epsg_normal_pruefen(wirksames_epsg)
        spalten_sql = ", ".join(_quote_ident(s) for s in spalten)
        abfrage = f"SELECT {spalten_sql} FROM {_quote_ident(tabelle)}"
        spalten_index = {s: i for i, s in enumerate(spalten)}
        geom_idx = spalten_index.get(geom_spalte) if geom_spalte else None
        zeilen = cur.execute(abfrage)
        return _tabellen_zeilen_verarbeiten(
            zeilen,
            spalten_index,
            z_map,
            wirksames_epsg,
            geom_idx,
            cur,
            quelle_info,
            heute,
            inner_name,
            start_zeile=1,
        )
    finally:
        con.close()
        pfad.unlink(missing_ok=True)


def _lesen_csv(
    daten: bytes,
    inner_name: str,
    quelle_info: tuple[str, str, str, str, str, str, bool],
    zuordnung: dict | None,
    heute: date,
) -> tuple[list[dict], list[dict]]:
    if not zuordnung:
        raise ValueError(f"{inner_name}: CSV-Import erfordert eine ausdrückliche Spaltenzuordnung (zuordnung)")
    for pflicht in ("id", "x", "y", "epsg"):
        if pflicht not in zuordnung or _leerer_wert(zuordnung[pflicht]):
            raise ValueError(f"{inner_name}: Pflichtfeld {pflicht!r} fehlt in der CSV-Zuordnung")
    text, _ = _csv_dekodieren(daten, inner_name)
    trenner = _csv_trenner(text)
    leser = csv.reader(io.StringIO(text), delimiter=trenner)
    try:
        kopf_roh = next(leser)
    except StopIteration:
        raise ValueError(f"{inner_name}: CSV-Datei ist leer") from None
    kopf = [s.strip() for s in kopf_roh]
    if not any(kopf):
        raise ValueError(f"{inner_name}: CSV-Kopfzeile ist leer")
    z_map, festes_epsg = _spalten_aufloesen(kopf, zuordnung, inner_name)
    spalten_index = {s: i for i, s in enumerate(kopf)}
    nicht_leere_zeilen = (z for z in leser if any(str(w).strip() for w in z))
    return _tabellen_zeilen_verarbeiten(
        nicht_leere_zeilen,
        spalten_index,
        z_map,
        festes_epsg,
        geom_idx=None,
        cur_gpkg=None,
        quelle_info=quelle_info,
        heute=heute,
        inner_name=inner_name,
        start_zeile=2,
    )


# ---------------------------------------------------------------- Oeffentliche Schnittstelle
def lesen(
    daten: bytes,
    name: str,
    quelle: dict,
    zuordnung: dict | None = None,
    heute: date | None = None,
) -> dict:
    """Liest Bohrdaten aus einer Datei (.xml, .gml, .gpkg, .csv oder einzeln in .zip) in das kanonische JSON
    wie boreholeml.importieren, ergaenzt um abgelehnt: [{zeile, grund}]."""
    heute = heute or date.today()
    inhalt, inner_name = _entpacken_einzeln(daten, name)
    fmt = _format_erkennen(inhalt, inner_name)
    quelle_info = _quelle_daten(quelle, name, heute)
    bereinigt = _zuordnung_bereinigen(zuordnung)
    if fmt == "boreholeml":
        bohrungen, abgelehnt = _lesen_boreholeml(inhalt, inner_name, quelle_info, heute)
    elif fmt == "inspire-gml":
        bohrungen, abgelehnt = _lesen_inspire_gml(inhalt, inner_name, quelle_info, heute)
    elif fmt == "gpkg":
        bohrungen, abgelehnt = _lesen_gpkg(inhalt, inner_name, quelle_info, bereinigt, heute)
    elif fmt == "csv":
        bohrungen, abgelehnt = _lesen_csv(inhalt, inner_name, quelle_info, bereinigt, heute)
    else:
        raise ValueError(f"{name}: unbekanntes Format {fmt}")
    return {
        "document": {
            "file": name,
            "sha256": hashlib.sha256(daten).hexdigest(),
            "parser_version": "bohrdaten_datei",
            "pages": None,
        },
        "boreholes": bohrungen,
        "soundings": {},
        "abgelehnt": abgelehnt,
    }


def im_umkreis(doc: dict, x: float, y: float, epsg: int, radius: float) -> dict:
    """Filtert die Bohrungen eines gelesenen Dokuments nach dem Abstand um (x, y, epsg) in der Struktur von
    bohrdaten.abfragen ({treffer, fehler}, nach Abstand sortiert, schichten und schichten_n gesetzt)."""
    radius = float(radius)
    if radius < 0:
        raise ValueError("Radius darf nicht negativ sein")
    zx, zy, zepsg = utm_normal(x, y, _epsg_normal_pruefen(epsg))
    ziel_zone = utm.zone(zepsg)
    treffer: list[dict] = []
    fehler: list[dict] = []
    for b in (doc or {}).get("boreholes") or []:
        bx, by = b.get("x"), b.get("y")
        b_epsg = b.get("crs_epsg")
        dienst = b.get("quelle", "DATEI")
        if bx is None or by is None or b_epsg is None:
            fehler.append({"dienst": dienst, "fehler": f"Bohrung {b.get('code', '?')} ohne gültige Koordinaten"})
            continue
        if b_epsg == zepsg:
            nx, ny = float(bx), float(by)
            if abs(nx - zx) > radius + 0.1 or abs(ny - zy) > radius + 0.1:
                continue
        else:
            try:
                nx, ny, nepsg = utm_normal(bx, by, int(b_epsg))
            except ValueError as err:
                fehler.append({"dienst": dienst, "fehler": str(err)})
                continue
            if nepsg != zepsg:
                lon, lat = utm.zu_geo(nx, ny, utm.zone(nepsg))
                rx, ry = utm.von_geo(lon, lat, ziel_zone)
                nx, ny = float(rx), float(ry)
            if abs(nx - zx) > radius + 0.1 or abs(ny - zy) > radius + 0.1:
                continue
        abstand_roh = math.hypot(nx - zx, ny - zy)
        abstand = round(abstand_roh, 1)
        if abstand > radius:
            continue
        schichten = b.get("layers") or []
        mit_petro = any(ly.get("soil_class") for ly in schichten)
        profil = b.get("profil") or b.get("profil_url") or None
        schichten_art = (
            "boreholeml"
            if mit_petro
            else ("ohne Petrographie" if schichten else ("grafik" if profil else "keine"))
        )
        fremd_id = b.get("fremd_id") or b.get("code") or "?"
        kurzname = b.get("name")
        if not kurzname:
            code = str(b.get("code") or fremd_id)
            praefix = f"{dienst}-"
            kurzname = code[len(praefix):] if code.startswith(praefix) else code
        treffer.append({
            "dienst": dienst,
            "id": fremd_id,
            "name": kurzname,
            "x": round(nx, 2),
            "y": round(ny, 2),
            "gok": b.get("gok_nhn"),
            "teufe": b.get("end_depth"),
            "datum": b.get("datum"),
            "profil": profil,
            "schichten_n": len(schichten),
            "schichten": schichten_art,
            "abstand": abstand,
        })
    treffer.sort(key=lambda t: (t["abstand"], str(t["id"])))
    return {
        "mitte": [round(zx, 2), round(zy, 2)],
        "epsg": zepsg,
        "radius": radius,
        "treffer": treffer,
        "fehler": fehler,
    }
