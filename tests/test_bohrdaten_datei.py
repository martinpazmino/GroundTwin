"""Offline-Tests fuer services/geodaten/geodaten/bohrdaten_datei.py (docs/26 §2 und §3, Option c).
Alle Proben werden im Test synthetisch erzeugt (GeoPackage ueber sqlite3, CSV in UTF-8 und cp1252, INSPIRE-GML,
BoreholeML-XML, ZIP). Keine Netzzugriffe, keine Daten Dritter im Repository.
"""
from __future__ import annotations
import io
import sqlite3
import struct
import sys
import zipfile
from datetime import date
from pathlib import Path
import pytest
REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "services" / "geodaten"), str(REPO / "services" / "modeler")]
from geodaten import bohrdaten as bd  # noqa: E402
from geodaten import bohrdaten_datei as bdd  # noqa: E402
HEUTE = date(2026, 11, 9)
QUELLE_MV = {
    "kennung": "MV",
    "titel": "Landesbohrdatenspeicher MV",
    "land": "Mecklenburg-Vorpommern",
    "lizenz": "CC BY-SA 3.0",
    "namensnennung": "© LUNG MV (CC BY-SA 3.0), {jahr}",
    "url": "https://umweltportal.mv-regierung.de/download/geologie/LBDS/bohrdaten_dl.zip",
}


def _gp_punkt_blob(x: float, y: float, srs_id: int = 100000, mit_envelope: bool = False, leer: bool = False) -> bytes:
    """Erzeugt einen OGC GeoPackage-Binary-Header + WKB-Point."""
    flags = 0x01                                                # Little-Endian Header
    if mit_envelope:
        flags |= (1 << 1)                                       # Envelope [minx, maxx, miny, maxy] (32 Bytes)
    if leer:
        flags |= (1 << 4)                                       # Empty-Geometry-Flag
    header = b"GP\x00" + bytes([flags]) + struct.pack("<i", srs_id)
    if mit_envelope:
        header += struct.pack("<dddd", x, x, y, y)
    wkb = b"\x01" + struct.pack("<Idd", 1, float(x), float(y))
    return header + wkb


def _synthetisches_gpkg(tmp_path: Path, srs_id: int = 100000) -> bytes:
    """Baut ein kleines GeoPackage wie bohrdaten_dl.gpkg (EPSG:5650 ueber WKT mit srs_id=100000)."""
    pfad = tmp_path / "probe_mv.gpkg"
    con = sqlite3.connect(pfad)
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE gpkg_spatial_ref_sys ("
        "srs_name TEXT, srs_id INTEGER PRIMARY KEY, organization TEXT, "
        "organization_coordsys_id INTEGER, definition TEXT)"
    )
    wkt_5650 = (
        'PROJCS["ETRS89_UTM_Zone_33d8",GEOGCS["GCS_ETRS89",DATUM["ETRS89",'
        'SPHEROID["GRS 1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],'
        'PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",15],'
        'PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",33500000],PARAMETER["false_northing",0],'
        'UNIT["metre",1]]'
    )
    cur.execute(
        "INSERT INTO gpkg_spatial_ref_sys VALUES (?, ?, ?, ?, ?)",
        ("ETRS89_UTM_Zone_33d8", srs_id, "NONE", srs_id, wkt_5650),
    )
    cur.execute(
        "CREATE TABLE gpkg_contents ("
        "table_name TEXT PRIMARY KEY, data_type TEXT, identifier TEXT, srs_id INTEGER)"
    )
    cur.execute("INSERT INTO gpkg_contents VALUES ('bohrdaten', 'features', 'bohrdaten', ?)", (srs_id,))
    cur.execute("INSERT INTO gpkg_contents VALUES ('layer_styles', 'attributes', 'layer_styles', 0)")
    cur.execute(
        "CREATE TABLE gpkg_geometry_columns ("
        "table_name TEXT, column_name TEXT, geometry_type_name TEXT, srs_id INTEGER, z TINYINT, m TINYINT)"
    )
    cur.execute("INSERT INTO gpkg_geometry_columns VALUES ('bohrdaten', 'geom', 'POINT', ?, 0, 0)", (srs_id,))
    cur.execute(
        'CREATE TABLE "bohrdaten" ('
        "fid INTEGER PRIMARY KEY, geom POINT, RW TEXT, HW TEXT, ZCOORDB REAL, ZCOORDE REAL, "
        "LONGNAME TEXT, BO_IDENT INTEGER, YRFROMNAME TEXT)"
    )
    zeilen = [
        # 1: Gültige Bohrung auf Rügen (Bergen, Zone 33 mit Zonenkennung 33 -> 398528, 6030275)
        (1, _gp_punkt_blob(33398528.0, 6030275.0, srs_id), "33398528", "6030275", 34.0, 5.0, "Bgn 1/67", 1001, "1967"),
        # 2: Zweite gültige Bohrung ~60 m entfernt (mit Envelope im GP-Blob)
        (2, _gp_punkt_blob(33398580.0, 6030300.0, srs_id, mit_envelope=True), "33398580", "6030300", 35.3, 10.0, "Bgn 2/70", 1002, "1970"),
        # 3: Doppelte BO_IDENT (1001) -> muss in abgelehnt landen
        (3, _gp_punkt_blob(33398600.0, 6030310.0, srs_id), "33398600", "6030310", 33.0, 8.0, "Bgn Dup", 1001, "1971"),
        # 4: Ohne Lage (leerer Blob und fehlende RW/HW) -> in abgelehnt
        (4, _gp_punkt_blob(0.0, 0.0, srs_id, leer=True), "", "", 12.0, 4.0, "Ohne Lage", 1004, "1980"),
        # 5: Außerhalb Deutschlands (Ostsee weit nördlich / Polen) -> in abgelehnt
        (5, _gp_punkt_blob(33600000.0, 6200000.0, srs_id), "33600000", "6200000", 0.0, 15.0, "Ausland", 1005, "1985"),
        # 6: Nicht zuordenbare Zahl in ZCOORDB -> in abgelehnt
        (6, _gp_punkt_blob(33398530.0, 6030280.0, srs_id), "33398530", "6030280", "ca. 30m", 6.0, "Zahl kaputt", 1006, "1990"),
    ]
    cur.executemany("INSERT INTO bohrdaten VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", zeilen)
    con.commit()
    con.close()
    return pfad.read_bytes()


def _als_zip(dateien: list[tuple[str, bytes]]) -> bytes:
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for datei_name, inhalt in dateien:
            zf.writestr(datei_name, inhalt)
    return puffer.getvalue()


# ---------------------------------------------------------------- GeoPackage & ZIP
def test_gpkg_felder_vorschlagen_und_lesen_mit_herkunft(tmp_path):
    gpkg = _synthetisches_gpkg(tmp_path)
    zip_bytes = _als_zip([("bohrdaten_dl.gpkg", gpkg), ("bohrdaten.pdf", b"%PDF-1.4 Doku")])
    info = bdd.felder_vorschlagen(zip_bytes, "bohrdaten_dl.zip")
    assert info["format"] == "gpkg" and info["datei"] == "bohrdaten_dl.gpkg"
    assert info["tabelle"] == "bohrdaten" and "bohrdaten" in info["tabellen"]
    assert info["geometrie_spalte"] == "geom" and info["epsg"] == 5650
    v = info["vorschlag"]
    assert (v["id"], v["name"], v["x"], v["y"], v["gok"], v["teufe"], v["datum"], v["epsg"]) == (
        "BO_IDENT", "LONGNAME", "RW", "HW", "ZCOORDB", "ZCOORDE", "YRFROMNAME", 5650,
    )
    # lesen mit bestätigter Zuordnung
    doc = bdd.lesen(zip_bytes, "bohrdaten_dl.zip", QUELLE_MV, zuordnung=v, heute=HEUTE)
    assert doc["document"]["file"] == "bohrdaten_dl.zip" and len(doc["document"]["sha256"]) == 64
    assert doc["soundings"] == {}
    assert len(doc["boreholes"]) == 2
    b0 = doc["boreholes"][0]
    assert (b0["code"], b0["fremd_id"], b0["name"]) == ("MV-Bgn 1/67", "1001", "Bgn 1/67")
    assert (b0["x"], b0["y"], b0["crs_epsg"]) == (pytest.approx(398528.0), pytest.approx(6030275.0), 25833)
    assert (b0["gok_nhn"], b0["end_depth"], b0["datum"]) == (pytest.approx(34.0), pytest.approx(5.0), "1967")
    assert b0["herkunft"] == "SGD" and b0["quelle"] == "MV" and b0["lizenz"] == "CC BY-SA 3.0"
    assert b0["namensnennung"] == "© LUNG MV (CC BY-SA 3.0), 2026" and b0["abgerufen"] == "2026-11-09"
    assert b0["coord_source"] == "SGD Mecklenburg-Vorpommern"
    assert b0["layers"] == []
    assert b0["issues"][0] == (
        "aus Landesbohrdatenspeicher MV (Mecklenburg-Vorpommern), ID 1001, CC BY-SA 3.0, "
        "abgerufen 09.11.2026 – nicht aus dem Gutachten"
    )
    assert any("ohne Schichtdaten" in h for h in b0["issues"])
    # Abgelehnte Zeilen: Zeile 3 (doppelte id), Zeile 4 (ohne Lage), Zeile 5 (außerhalb DE), Zeile 6 (Zahl kaputt)
    abg = {a["zeile"]: a["grund"] for a in doc["abgelehnt"]}
    assert set(abg) == {3, 4, 5, 6}
    assert "doppelte id" in abg[3]
    assert "ohne Lage" in abg[4]
    assert "außerhalb Deutschlands" in abg[5]
    assert "nicht zuordenbare Zahl" in abg[6]


def test_gpkg_punkt_aus_blob_und_ohne_stille_zuordnung(tmp_path):
    """Ohne bestätigte Zuordnung liest lesen nichts: der Primärschlüssel zählt nur Zeilen, er kennt keine Bohrung."""
    gpkg = _synthetisches_gpkg(tmp_path)
    with pytest.raises(ValueError, match="ausdrückliche Spaltenzuordnung"):
        bdd.lesen(gpkg, "probe_mv.gpkg", QUELLE_MV, zuordnung=None, heute=HEUTE)
    with pytest.raises(ValueError, match="Pflichtfeld 'id'"):
        bdd.lesen(gpkg, "probe_mv.gpkg", QUELLE_MV, zuordnung={"name": "LONGNAME"}, heute=HEUTE)
    # Mit Teil-Zuordnung ohne x/y kommt der Punkt aus dem GeoPackage-Blob
    doc_blob = bdd.lesen(
        gpkg,
        "probe_mv.gpkg",
        QUELLE_MV,
        zuordnung={"id": "BO_IDENT", "name": "LONGNAME", "gok": "ZCOORDB", "teufe": "ZCOORDE"},
        heute=HEUTE,
    )
    assert len(doc_blob["boreholes"]) == 2
    assert doc_blob["boreholes"][0]["gok_nhn"] == pytest.approx(34.0)
    assert doc_blob["boreholes"][0]["x"] == pytest.approx(398528.0)
    assert doc_blob["boreholes"][1]["x"] == pytest.approx(398580.0)   # mit 32-Byte-Envelope im GP-Blob
    with pytest.raises(ValueError, match="keine gültige GeoPackage"):
        bdd.lesen(b"kein sqlite", "kaputt.gpkg", QUELLE_MV)
    pfad_epsg = tmp_path / "org_epsg.gpkg"
    pfad_epsg.write_bytes(gpkg)
    con = sqlite3.connect(pfad_epsg)
    con.execute("UPDATE gpkg_spatial_ref_sys SET organization='EPSG', organization_coordsys_id=5650, definition='undefined' WHERE srs_id=100000")
    con.commit()
    con.close()
    assert bdd.felder_vorschlagen(pfad_epsg.read_bytes(), "org_epsg.gpkg")["epsg"] == 5650


# ---------------------------------------------------------------- CSV (Kopf & Langformat mit Schichten)
CSV_LANG_CP1252 = (
    "bohr_id;bohrname;rw;hw;epsg;gok_nhn;endteufe;datum;tiefe_von;tiefe_bis;sep3;beschreibung\n"
    "B1;RKS 1;394774,32;5818338,12;25833;36,25;6,0;17.02.1993;0,0;1,5;fS;Feinsand, gelbbraun, mitteldicht\n"
    "B1;RKS 1;394774,32;5818338,12;25833;36,25;6,0;17.02.1993;1,5;4,0;U;Schluff, schwach tonig\n"
    "B1;RKS 1;394774,32;5818338,12;25833;36,25;6,0;17.02.1993;4,0;6,0;UNBEKANNT_CODE;Mergelstein\n"
    # B2: mit Lücke (0..1, dann 1.5..3), Überlappung (2.5..4) und von >= bis (4..4)
    "B2;RKS 2;394800,0;5818350,0;25833;35,0;4,0;2020-05-01;0,0;1,0;G;Kies\n"
    "B2;RKS 2;394800,0;5818350,0;25833;35,0;4,0;2020-05-01;1,5;3,0;T;Ton\n"
    "B2;RKS 2;394800,0;5818350,0;25833;35,0;4,0;2020-05-01;2,5;4,0;S;Sand\n"
    "B2;RKS 2;394800,0;5818350,0;25833;35,0;4,0;2020-05-01;4,0;4,0;S;Nullschicht\n"
    # Fehlerhafte Zeilen:
    ";Ohne ID;394800,0;5818350,0;25833;35,0;4,0;;0,0;1,0;S;Fehlt ID\n"
    "B1;RKS 1 Falsch;399999,0;5818338,12;25833;36,25;6,0;;0,0;1,0;S;Abweichende Lage bei gleicher ID\n"
    "B3;RKS 3;394810,0;5818360,0;25833;35,0;4,0;;0,0;eins;S;Kaputte Tiefe\n"
).encode("cp1252")


def test_csv_erfordert_ausdrueckliche_zuordnung():
    info = bdd.felder_vorschlagen(CSV_LANG_CP1252, "schichten.csv")
    assert info["format"] == "csv" and info["trenner"] == ";" and info["kodierung"] in ("utf-8", "cp1252")
    assert info["vorschlag"]["id"] == "bohr_id" and info["vorschlag"]["von"] == "tiefe_von"
    with pytest.raises(ValueError, match="ausdrückliche Spaltenzuordnung"):
        bdd.lesen(CSV_LANG_CP1252, "schichten.csv", QUELLE_MV, zuordnung=None)
    with pytest.raises(ValueError, match="Pflichtfeld"):
        bdd.lesen(CSV_LANG_CP1252, "schichten.csv", QUELLE_MV, zuordnung={"id": "bohr_id", "x": "rw"})
    with pytest.raises(ValueError, match="existiert nicht"):
        bdd.lesen(
            CSV_LANG_CP1252,
            "schichten.csv",
            QUELLE_MV,
            zuordnung={"id": "bohr_id", "x": "rw", "y": "hw", "epsg": "gibt_es_nicht"},
        )


def test_csv_langformat_schichten_bodenart_konfidenz_und_markierungen():
    # Auch mit echten cp1252-Umlauten (äöüß) testen
    csv_bytes = CSV_LANG_CP1252.replace(b"gelbbraun", "rötlich-grünß".encode("cp1252"))
    info = bdd.felder_vorschlagen(csv_bytes, "schichten.csv")
    assert info["kodierung"] == "cp1252"
    # Quelle ohne Lizenz -> lizenz="unbekannt" und Hinweis in issues
    quelle_ohne_lizenz = {"kennung": "BE-CSV", "titel": "Nutzer-Export", "land": "Berlin"}
    doc = bdd.lesen(csv_bytes, "schichten.csv", quelle_ohne_lizenz, zuordnung=info["vorschlag"], heute=HEUTE)
    assert len(doc["boreholes"]) == 2
    b1, b2 = doc["boreholes"]
    assert b1["code"] == "BE-CSV-RKS 1" and b1["datum"] == "1993-02-17"
    assert b1["lizenz"] == "unbekannt"
    assert any("Lizenz" in h and "unbekannt" in h for h in b1["issues"])
    assert [ly["soil_class"] for ly in b1["layers"]] == ["Sand", "Schluff", None]
    assert all(ly["confidence"] == bd.KONFIDENZ_ARCHIV for ly in b1["layers"])
    assert "rötlich-grünß" in b1["layers"][0]["description_raw"]
    assert "UNBEKANNT_CODE" in b1["layers"][2]["issues"][0]
    # B2: Schichten werden NICHT repariert, aber Lücke, Überlappung und von >= bis in issues markiert
    assert [(ly["top_depth"], ly["bottom_depth"]) for ly in b2["layers"]] == [
        (0.0, 1.0), (1.5, 3.0), (2.5, 4.0), (4.0, 4.0)
    ]
    issues_b2 = " | ".join(b2["issues"])
    assert "Lücke" in issues_b2
    assert "Überlappung" in issues_b2
    assert "von >= bis" in issues_b2
    # Abgelehnte Zeilen (Zeilen 9, 10, 11)
    abg = {a["zeile"]: a["grund"] for a in doc["abgelehnt"]}
    assert set(abg) == {9, 10, 11}
    assert "fehlende ID" in abg[9]
    assert "doppelte id" in abg[10]
    assert "Schichttiefe" in abg[11]


def test_csv_komma_trenner_und_kopfdaten():
    csv_komma = (
        "id,name,x,y,gok,teufe\n"
        "K1,Bohrung 1,32368100.0,5724420.0,60.5,12.0\n"
        "K1,Bohrung 1 Dup,32368110.0,5724420.0,60.5,12.0\n"
        "K2,Ohne Y,32368100.0,,60.5,12.0\n"
        "K3,Neg Teufe,32368100.0,5724420.0,60.5,-3.0\n"
    ).encode("utf-8")
    info = bdd.felder_vorschlagen(csv_komma, "kopf.csv")
    assert info["trenner"] == ","
    zuordnung = {**info["vorschlag"], "epsg": 4647}
    doc = bdd.lesen(csv_komma, "kopf.csv", QUELLE_MV, zuordnung=zuordnung, heute=HEUTE)
    assert len(doc["boreholes"]) == 1
    b = doc["boreholes"][0]
    assert (b["x"], b["y"], b["crs_epsg"]) == (pytest.approx(368100.0), pytest.approx(5724420.0), 25832)
    assert b["layers"] == []
    assert [a["zeile"] for a in doc["abgelehnt"]] == [3, 4, 5]


# ---------------------------------------------------------------- INSPIRE GML & BoreholeML XML
INSPIRE_GML = b"""<?xml version="1.0" encoding="UTF-8"?>
<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:ge="http://inspire.ec.europa.eu/schemas/ge-core/4.0"
    xmlns:base="http://inspire.ec.europa.eu/schemas/base/3.3"
    xmlns:swe="http://www.opengis.net/swe/2.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <wfs:member>
    <ge:Borehole gml:id="HB_1">
      <ge:inspireId><base:Identifier><base:localId>2918_05_0001</base:localId></base:Identifier></ge:inspireId>
      <ge:name>HB 1</ge:name>
      <ge:boreholeLength xlink:href="14.3"><swe:Quantity><swe:uom xlink:href="m"/></swe:Quantity></ge:boreholeLength>
      <ge:elevation uomLabels="m">2.58</ge:elevation>
      <ge:location>
        <gml:Point srsName="http://www.opengis.net/def/crs/EPSG/0/25832" srsDimension="2">
          <gml:pos>487461.0 5882434.0</gml:pos>
        </gml:Point>
      </ge:location>
      <ge:logElement nilReason="other:unpopulated" xsi:nil="true"/>
    </ge:Borehole>
  </wfs:member>
  <wfs:member>
    <ge:Borehole gml:id="HB_DUP">
      <ge:inspireId><base:Identifier><base:localId>2918_05_0001</base:localId></base:Identifier></ge:inspireId>
      <ge:location>
        <gml:Point srsName="EPSG:25832"><gml:pos>487465.0 5882434.0</gml:pos></gml:Point>
      </ge:location>
    </ge:Borehole>
  </wfs:member>
  <wfs:member>
    <ge:Borehole gml:id="HB_OHNE_POS">
      <ge:inspireId><base:Identifier><base:localId>2918_05_0002</base:localId></base:Identifier></ge:inspireId>
    </ge:Borehole>
  </wfs:member>
  <wfs:member>
    <ge:Borehole gml:id="HB_KAPUTTE_LAENGE">
      <ge:inspireId><base:Identifier><base:localId>2918_05_0003</base:localId></base:Identifier></ge:inspireId>
      <ge:boreholeLength>unbekannt</ge:boreholeLength>
      <ge:location><gml:Point srsName="EPSG:25832"><gml:pos>487465.0 5882434.0</gml:pos></gml:Point></ge:location>
    </ge:Borehole>
  </wfs:member>
</wfs:FeatureCollection>"""


def test_inspire_gml_nur_kopfdaten_und_abgelehnte():
    info = bdd.felder_vorschlagen(INSPIRE_GML, "inspire.gml")
    assert info["format"] == "inspire-gml" and info["epsg"] == 25832
    doc = bdd.lesen(
        INSPIRE_GML,
        "inspire.gml",
        {"kennung": "HB", "titel": "INSPIRE Bremen", "land": "Bremen", "lizenz": "CC BY", "namensnennung": "© HB"},
        heute=HEUTE,
    )
    assert len(doc["boreholes"]) == 1
    b = doc["boreholes"][0]
    assert (b["code"], b["fremd_id"], b["gok_nhn"], b["end_depth"]) == ("HB-HB 1", "2918_05_0001", 2.58, 14.3)
    assert b["layers"] == []
    assert any("INSPIRE" in h or "ohne Schichtdaten" in h for h in b["issues"])
    assert [a["zeile"] for a in doc["abgelehnt"]] == [2, 3, 4]


def test_boreholeml_xml_ueber_boreholeml_importieren():
    from test_boreholeml import SYNTHETISCH
    doc = bdd.lesen(
         _als_zip([("bml.xml", SYNTHETISCH)]),
        "bml.zip",
        {"kennung": "NI", "titel": "LBEG Archiv", "land": "Niedersachsen", "lizenz": "dl-de/by-2.0", "namensnennung": "© LBEG"},
        heute=HEUTE,
    )
    assert len(doc["boreholes"]) == 1 and doc["abgelehnt"] == []
    b = doc["boreholes"][0]
    assert (b["code"], b["fremd_id"], b["crs_epsg"]) == ("NI-RKS 7", "9999XX0001", 25832)
    assert all(ly["confidence"] == bd.KONFIDENZ_ARCHIV for ly in b["layers"])
    assert [ly["soil_class"] for ly in b["layers"]] == ["Auffuellung", "Sand", None, None]


# ---------------------------------------------------------------- Sicherheit & Grenzen
def test_sicherheit_doctype_rar_zip_bombe_und_fremdes_epsg(monkeypatch):
    # 1. <!DOCTYPE in XML/GML ablehnen
    bose_xml = b'<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><a/>'
    with pytest.raises(ValueError, match="DOCTYPE"):
        bdd.felder_vorschlagen(bose_xml, "xxe.xml")
    with pytest.raises(ValueError, match="DOCTYPE"):
        bdd.lesen(bose_xml, "xxe.gml", QUELLE_MV)
    # 2. .rar ablehnen (Dateiendung, Magic-Bytes und im ZIP)
    with pytest.raises(ValueError, match="RAR"):
        bdd.felder_vorschlagen(b"Rar!\x1a\x07\x00...", "Bohrarchiv_HH.rar")
    with pytest.raises(ValueError, match="RAR"):
        bdd.lesen(_als_zip([("hh.rar", b"123")]), "hh.zip", QUELLE_MV)
    # 3. ZIP-Größengrenze beim Entpacken
    monkeypatch.setattr(bdd, "MAX_ENTPACKT", 100)
    grosses_zip = _als_zip([("gross.csv", b"id;x;y;epsg\n" + b"1;394000;5818000;25833\n" * 20)])
    with pytest.raises(ValueError, match="groß|Größengrenze"):
        bdd.lesen(grosses_zip, "gross.zip", QUELLE_MV, zuordnung={"id": "id", "x": "x", "y": "y", "epsg": "epsg"})
    # 4. Nicht von utm_normal unterstützte Koordinatensysteme -> ValueError mit EPSG im Text
    gml_4258 = INSPIRE_GML.replace(b"EPSG/0/25832", b"EPSG/0/4258")
    with pytest.raises(ValueError, match="4258"):
        bdd.lesen(gml_4258, "hb_4258.gml", QUELLE_MV)
    csv_31467 = b"id;x;y\nB1;3500000;5800000\n"
    with pytest.raises(ValueError, match="31467"):
        bdd.lesen(csv_31467, "gk.csv", QUELLE_MV, zuordnung={"id": "id", "x": "x", "y": "y", "epsg": 31467})


# ---------------------------------------------------------------- Umkreisfilter & Gegenprobe
def test_im_umkreis_sortiert_setzt_schichten_und_passt_zu_doppelte(tmp_path):
    gpkg = _synthetisches_gpkg(tmp_path)
    v = bdd.felder_vorschlagen(gpkg, "probe.gpkg")["vorschlag"]
    doc = bdd.lesen(gpkg, "probe.gpkg", QUELLE_MV, zuordnung=v, heute=HEUTE)
    # Exakte Grenze: Bohrung 1 liegt bei (398528, 6030275), Bohrung 2 bei (398580, 6030300) -> Abstand = 57.7 m
    erg_60 = bdd.im_umkreis(doc, 398528.0, 6030275.0, 25833, radius=60.0)
    assert erg_60["fehler"] == [] and erg_60["epsg"] == 25833 and erg_60["radius"] == 60.0
    assert [t["id"] for t in erg_60["treffer"]] == ["1001", "1002"]
    assert [t["abstand"] for t in erg_60["treffer"]] == [0.0, 57.7]
    assert all(t["schichten"] == "keine" and t["schichten_n"] == 0 for t in erg_60["treffer"])
    # Radius genau 57.7 m schließt 1002 ein, 57.6 m schließt 1002 aus
    assert len(bdd.im_umkreis(doc, 398528.0, 6030275.0, 25833, radius=57.7)["treffer"]) == 2
    assert len(bdd.im_umkreis(doc, 398528.0, 6030275.0, 25833, radius=57.6)["treffer"]) == 1
    # Gegenprobe über bohrdaten.doppelte
    gegen = bd.doppelte(
        erg_60["treffer"],
        [{"id": "G1", "code": "Bgn 1/67", "x": 398529.0, "y": 6030275.0, "gok": 34.2}],
    )
    assert gegen == {"anzahl": 1, "lage_max": 1.0, "gok_max": 0.2}
    assert erg_60["treffer"][0]["gutachten"] == "Bgn 1/67"
    # Negativer Radius oder fremdes EPSG -> ValueError
    with pytest.raises(ValueError, match="negativ"):
        bdd.im_umkreis(doc, 398528.0, 6030275.0, 25833, radius=-1.0)
    erg_f = bdd.im_umkreis({"boreholes": [{"code": "X", "x": None, "y": 6030275.0, "crs_epsg": 25833}]}, 398528.0, 6030275.0, 25833, 50.0)
    assert len(erg_f["fehler"]) == 1 and erg_f["treffer"] == []
    with pytest.raises(ValueError, match="31468"):
        bdd.im_umkreis(doc, 4500000.0, 5800000.0, 31468, radius=100.0)


# ---------------------------------------------------------------- Befunde an der echten Datei von MV (2026-11-09)
QUELLE = {"kennung": "T", "titel": "Test", "land": "Berlin", "lizenz": "x", "namensnennung": "y"}
LANG = {"id": "id", "x": "x", "y": "y", "epsg": "epsg", "von": "von", "bis": "bis", "petrographie": "p"}
KOPF = "id;x;y;epsg;von;bis;p\n"
BERLIN = "394774;5818338;25833"
Z_KOPF = {"id": "id", "x": "x", "y": "y", "epsg": "epsg"}


def _lang(zeilen: str) -> dict:
    return bdd.lesen((KOPF + zeilen).encode(), "t.csv", QUELLE, zuordnung=LANG, heute=HEUTE)


def _kopf_csv(zeilen: list[str], spalten: str = "bo_ident;prj_id;locid;x;y;epsg") -> bytes:
    return ("\n".join([spalten, *zeilen]) + "\n").encode()


def test_nicht_eindeutige_id_schlaegt_ein_eindeutiges_spaltenpaar_vor():
    # bo_ident wiederholt sich bei verschiedenen Bohrungen (MV: bis 204-mal), prj_id + locid ist je Zeile eindeutig
    daten = _kopf_csv(["7;P1;1;394774;5818338;25833", "7;P1;2;394800;5818338;25833", "8;P2;1;394900;5818338;25833"])
    info = bdd.felder_vorschlagen(daten, "a.csv")
    assert info["vorschlag"]["id"] == ["prj_id", "locid"] and "bo_ident" in info["id_hinweis"]
    doc = bdd.lesen(daten, "a.csv", QUELLE, zuordnung=info["vorschlag"], heute=HEUTE)
    assert [b["fremd_id"] for b in doc["boreholes"]] == ["P1/1", "P1/2", "P2/1"] and doc["abgelehnt"] == []
    eindeutig = _kopf_csv(["7;P1;1;394774;5818338;25833", "8;P2;1;394900;5818338;25833"])
    info = bdd.felder_vorschlagen(eindeutig, "a.csv")
    assert info["vorschlag"]["id"] == "bo_ident" and info["id_hinweis"] is None


def test_id_ohne_eindeutige_alternative_warnt_und_markiert_die_behaltene_bohrung():
    daten = _kopf_csv(["7;394774;5818338;25833", "7;394800;5818338;25833"], "id;x;y;epsg")
    info = bdd.felder_vorschlagen(daten, "a.csv")
    assert info["vorschlag"]["id"] == "id" and "keine andere Kennung" in info["id_hinweis"]
    doc = bdd.lesen(daten, "a.csv", QUELLE, zuordnung=info["vorschlag"], heute=HEUTE)
    assert len(doc["boreholes"]) == 1 and [a["zeile"] for a in doc["abgelehnt"]] == [3]
    assert any("steht noch 1-mal" in h for h in doc["boreholes"][0]["issues"])


def test_id_aus_mehreren_spalten_braucht_alle_teile():
    daten = _kopf_csv(["P1;1;394774;5818338;25833", ";2;394800;5818338;25833"], "a;b;x;y;epsg")
    z = {"id": ["a", "b"], "x": "x", "y": "y", "epsg": "epsg"}
    doc = bdd.lesen(daten, "a.csv", QUELLE, zuordnung=z, heute=HEUTE)
    assert [b["fremd_id"] for b in doc["boreholes"]] == ["P1/1"] and doc["abgelehnt"] == [{"zeile": 3, "grund": "fehlende ID"}]
    with pytest.raises(ValueError, match="existiert nicht"):
        bdd.lesen(daten, "a.csv", QUELLE, zuordnung={**z, "id": ["a", "fehlt"]})


@pytest.mark.parametrize("lon,lat,erwartet", [
    (12.0905, 54.1845, "markiert"),         # Warnemuende, Mole: an Land, aber nicht auf der Flaeche von VG2500
    (12.0000, 54.3800, "markiert"),         # rund 20 km vor der Kueste: Kuestenmeer
    (14.4200, 50.0800, "abgelehnt"),        # Prag: im Rechteck um Deutschland, aber weit vom naechsten Land
    (16.6000, 55.9000, "abgelehnt"),        # noerdlich von Bornholm, ausserhalb des Rechtecks
])
def test_lage_an_der_kueste_wird_markiert_und_nur_weit_draussen_abgelehnt(lon, lat, erwartet):
    x, y = bd.utm.von_geo(lon, lat, 33)
    daten = f"id;x;y;epsg\nA;{float(x)};{float(y)};25833\n".encode()
    doc = bdd.lesen(daten, "a.csv", QUELLE, zuordnung=Z_KOPF, heute=HEUTE)
    if erwartet == "markiert":
        assert doc["abgelehnt"] == [] and any("nicht auf der Landfläche" in h for h in doc["boreholes"][0]["issues"])
    else:
        assert doc["boreholes"] == [] and "außerhalb Deutschlands" in doc["abgelehnt"][0]["grund"]


def test_link_zum_schichtenverzeichnis_wird_gelesen_und_nur_als_http():
    daten = (b"id;x;y;epsg;svz_url\n"
             b"A;394774;5818338;25833;https://example.org/svz?a=1\n"
             b"B;394800;5818338;25833;javascript:alert(1)\n"
             b"C;394820;5818338;25833;\n")
    info = bdd.felder_vorschlagen(daten, "a.csv")
    assert info["vorschlag"]["profil"] == "svz_url"
    doc = bdd.lesen(daten, "a.csv", QUELLE, zuordnung=info["vorschlag"], heute=HEUTE)
    a, b, c = doc["boreholes"]
    assert a["profil"] == "https://example.org/svz?a=1" and b["profil"] is None and c["profil"] is None
    assert any("keine http" in h for h in b["issues"]) and not any("keine http" in h for h in c["issues"])
    t = {x["id"]: x for x in bdd.im_umkreis(doc, 394774.0, 5818338.0, 25833, 100.0)["treffer"]}
    assert (t["A"]["schichten"], t["A"]["profil"]) == ("grafik", "https://example.org/svz?a=1")
    assert (t["B"]["schichten"], t["C"]["schichten"]) == ("keine", "keine")


def test_unlesbare_schicht_steht_an_der_bohrung():
    doc = _lang(f"B;{BERLIN};0;2;S\nB;{BERLIN};2;4;U\nB;{BERLIN};4;sechs;T\n")
    b = doc["boreholes"][0]
    assert [(ly["top_depth"], ly["bottom_depth"]) for ly in b["layers"]] == [(0.0, 2.0), (2.0, 4.0)]
    assert any("Zeile 4" in h and "unvollständig" in h for h in b["issues"]) and doc["abgelehnt"][0]["zeile"] == 4


def test_gleiche_id_mit_anderer_lage_steht_an_der_bohrung():
    b = _lang(f"B;{BERLIN};0;2;S\nB;394900;5818338;25833;2;4;U\n")["boreholes"][0]
    assert len(b["layers"]) == 1 and any("abweichender Lage" in h and "unvollständig" in h for h in b["issues"])


def test_schichten_werden_nach_tiefe_geordnet_ohne_falsche_meldung():
    b = _lang(f"B;{BERLIN};4;6;S\nB;{BERLIN};0;2;S\nB;{BERLIN};2;4;S\n")["boreholes"][0]
    assert [ly["top_depth"] for ly in b["layers"]] == [0.0, 2.0, 4.0]
    assert not any("Überlappung" in h or "Lücke" in h for h in b["issues"])


@pytest.mark.parametrize("gok,text", [("0", "genau 0"), ("3708", "außerhalb"), ("-60", "außerhalb"), ("34,5", None), ("-9,9", None)])
def test_zweifelhafte_gok_wird_markiert_und_bleibt_stehen(gok, text):
    daten = f"id;x;y;epsg;gok\nA;394774;5818338;25833;{gok}\n".encode()
    b = bdd.lesen(daten, "a.csv", QUELLE, zuordnung={**Z_KOPF, "gok": "gok"}, heute=HEUTE)["boreholes"][0]
    assert b["gok_nhn"] == pytest.approx(float(gok.replace(",", ".")))
    assert any(text in h for h in b["issues"]) if text else not any("GOK" in h for h in b["issues"])


def test_eine_bohrung_ohne_lage_kippt_nicht_die_ganze_boreholeml_datei():
    xml = b"""<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:bml="http://www.infogeo.de/boreholeml/3.0">
      <wfs:member><bml:Borehole gml:id="a"><bml:location><gml:Point srsName="EPSG:25833"><gml:pos>394774 5818338</gml:pos></gml:Point></bml:location><bml:id>A</bml:id></bml:Borehole></wfs:member>
      <wfs:member><bml:Borehole gml:id="b"><bml:id>B</bml:id></bml:Borehole></wfs:member>
      <wfs:member><bml:Borehole gml:id="c"><bml:location><gml:Point><gml:pos>394800 5818338</gml:pos></gml:Point></bml:location><bml:id>C</bml:id></bml:Borehole></wfs:member>
    </wfs:FeatureCollection>"""
    doc = bdd.lesen(xml, "a.xml", QUELLE, heute=HEUTE)
    assert [b["fremd_id"] for b in doc["boreholes"]] == ["A"]
    assert doc["abgelehnt"] == [{"zeile": 2, "grund": "ohne Lage"}, {"zeile": 3, "grund": "ohne Koordinatensystem"}]


def test_beschaedigtes_geopackage_ist_ein_lesefehler_und_laesst_nichts_liegen(tmp_path, monkeypatch):
    p = tmp_path / "gross.gpkg"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE gpkg_contents (table_name TEXT, data_type TEXT, srs_id INTEGER)")
    con.execute("INSERT INTO gpkg_contents VALUES ('b', 'features', 25833)")
    con.execute("CREATE TABLE gpkg_geometry_columns (table_name TEXT, column_name TEXT, srs_id INTEGER)")
    con.execute("INSERT INTO gpkg_geometry_columns VALUES ('b', 'geom', 25833)")
    con.execute("CREATE TABLE b (fid INTEGER PRIMARY KEY, kennung TEXT, geom BLOB, txt TEXT)")
    con.executemany("INSERT INTO b VALUES (?, ?, ?, ?)",
                    [(i + 1, f"K{i}", _gp_punkt_blob(394774.0 + i, 5818338.0, 25833), "x" * 200) for i in range(3000)])
    con.commit()
    con.close()
    daten = bytearray(p.read_bytes())
    for i in range(len(daten) // 2, len(daten), 512):
        daten[i:i + 64] = b"\xa5" * 64
    ablage = tmp_path / "temp"
    ablage.mkdir()
    monkeypatch.setattr(bdd.tempfile, "tempdir", str(ablage))
    with pytest.raises(ValueError, match="nicht lesbar"):
        bdd.lesen(bytes(daten), "a.gpkg", QUELLE, zuordnung={"id": "kennung"})
    assert list(ablage.iterdir()) == []


def test_zuordnung_nur_bestaetigt_und_ohne_tippfehler():
    daten = b"id;x;y;epsg\nA;394774;5818338;25833\n"
    with pytest.raises(ValueError, match="nicht das Ergebnis"):
        bdd.lesen(daten, "a.csv", QUELLE, zuordnung=bdd.felder_vorschlagen(daten, "a.csv"))
    with pytest.raises(ValueError, match="unbekannte Felder.*guk"):
        bdd.lesen(daten, "a.csv", QUELLE, zuordnung={**Z_KOPF, "guk": "gok"})


def test_doctype_auch_in_utf16():
    for kodierung in ("utf-16", "utf-16-le", "utf-16-be"):
        xml = '<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE a [<!ENTITY e "x">]><a>&e;</a>'.encode(kodierung)
        with pytest.raises(ValueError, match="DOCTYPE"):
            bdd.felder_vorschlagen(xml, "a.gml")


def test_zeilennummer_ist_die_der_datei_auch_nach_leerzeilen():
    daten = b"\n\nid;x;y;epsg\n\nA;394774;5818338;25833\n\n;394800;5818338;25833\n"
    doc = bdd.lesen(daten, "a.csv", QUELLE, zuordnung=Z_KOPF, heute=HEUTE)
    assert len(doc["boreholes"]) == 1 and doc["abgelehnt"] == [{"zeile": 7, "grund": "fehlende ID"}]


def test_im_umkreis_anderes_system_und_fehlende_teile():
    doc = {"boreholes": [{"code": "A", "x": 394774.0, "y": 5818338.0, "crs_epsg": 25833, "quelle": "T", "fremd_id": "A"},
                         {"code": "B", "x": 394774.0, "y": None, "crs_epsg": 25833, "quelle": "T"},
                         {"code": "C", "x": 394774.0, "y": 5818338.0, "crs_epsg": None, "quelle": "T"}]}
    erg = bdd.im_umkreis(doc, 33394774.0, 5818338.0, 5650, 10.0)            # gleiche Zone mit Zonenkennung
    assert [t["id"] for t in erg["treffer"]] == ["A"] and len(erg["fehler"]) == 2
    x, y = bd.utm.von_geo(*bd.utm.zu_geo(394774.0, 5818338.0, 33), 32)      # andere Zone: umgerechnet derselbe Punkt
    erg = bdd.im_umkreis(doc, float(x), float(y), 25832, 1.0)
    assert [t["id"] for t in erg["treffer"]] == ["A"] and erg["treffer"][0]["abstand"] == 0.0


# ---------------------------------------------------------------- Grenzen, die die Mutationsprobe offen liess
def test_wkt_braucht_etrs_und_transversale_mercator():
    gut = 'PROJCS["ETRS89 / UTM",PROJECTION["Transverse_Mercator"],PARAMETER["central_meridian",15],PARAMETER["false_easting",500000]]'
    assert bdd._epsg_aus_wkt(gut) == 25833
    assert bdd._epsg_aus_wkt(gut.replace("ETRS89", "WGS84")) is None
    assert bdd._epsg_aus_wkt(gut.replace("Transverse_Mercator", "Lambert")) is None


@pytest.mark.parametrize("lon,lat,hinweis", [(5.4, 50.0, True), (15.5, 50.0, True), (10.0, 46.9, True), (10.0, 55.4, True),
                                             (5.39, 50.0, False), (15.51, 50.0, False), (10.0, 46.89, False), (10.0, 55.41, False)])
def test_rechteck_um_deutschland_schliesst_seine_raender_ein(monkeypatch, lon, lat, hinweis):
    monkeypatch.setattr(bdd.laender, "laender_um", lambda *a, **k: ["Bayern"])
    assert (bdd._land_in_der_naehe(0.0, 0.0, 25832, lon, lat) is not None) == hinweis


@pytest.mark.parametrize("hoehe", ["", "<ge:elevation/>", '<ge:elevation xsi:nil="true"/>', '<ge:elevation xsi:nil="true">5</ge:elevation>'])
def test_gml_ohne_gueltige_hoehe_hat_keine_gok(hoehe):
    gml = f"""<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:ge="http://inspire.ec.europa.eu/schemas/ge-core/4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <wfs:member><ge:Borehole gml:id="A">{hoehe}<ge:location><gml:Point srsName="EPSG:25833"><gml:pos>394774 5818338</gml:pos></gml:Point></ge:location>
      </ge:Borehole></wfs:member></wfs:FeatureCollection>""".encode()
    doc = bdd.lesen(gml, "a.gml", QUELLE, heute=HEUTE)
    assert doc["abgelehnt"] == [] and doc["boreholes"][0]["gok_nhn"] is None


@pytest.mark.parametrize("von,bis", [("", "2"), ("0", ""), ("x", "2"), ("0", "y")])
def test_schicht_ohne_lesbare_tiefe_wird_abgelehnt(von, bis):
    doc = _lang(f"B;{BERLIN};0;1;S\nB;{BERLIN};{von};{bis};U\n")
    assert [a["zeile"] for a in doc["abgelehnt"]] == [3] and len(doc["boreholes"][0]["layers"]) == 1


def test_radius_null_trifft_nur_den_punkt():
    doc = {"boreholes": [{"code": "A", "x": 394774.0, "y": 5818338.0, "crs_epsg": 25833, "quelle": "T", "fremd_id": "A"},
                         {"code": "B", "x": 394775.0, "y": 5818338.0, "crs_epsg": 25833, "quelle": "T", "fremd_id": "B"}]}
    assert [t["id"] for t in bdd.im_umkreis(doc, 394774.0, 5818338.0, 25833, 0.0)["treffer"]] == ["A"]


def test_lage_braucht_beide_werte():
    assert bdd._lage_pruefen(None, 5818338.0, 25833, {})[3] == "ohne Lage"
    assert bdd._lage_pruefen(394774.0, None, 25833, {})[3] == "ohne Lage"


def test_zip_nach_name_oder_inhalt_und_kein_sqlite_ohne_kopf():
    assert bdd._entpacken_einzeln(_als_zip([("a.csv", b"x")]), "a.dat")[1] == "a.csv"
    with pytest.raises(ValueError, match="ZIP-Archiv nicht lesbar"):
        bdd._entpacken_einzeln(b"kein zip", "a.zip")
    for daten in (b"kurz", b"x" * 32):
        with pytest.raises(ValueError, match="keine gültige GeoPackage"):
            bdd._gpkg_oeffnen_ro(daten, "a.gpkg")


def test_csv_trenner_bei_gleichstand_das_semikolon():
    assert bdd._csv_trenner("a,b;c") == ";" and bdd._csv_trenner("a,b,c;d") == "," and bdd._csv_trenner("\n\na;b") == ";"
