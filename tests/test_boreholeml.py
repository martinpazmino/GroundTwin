"""BoreholeML 3.2 (services/geodaten/geodaten/boreholeml.py): Codetabelle, Export gepruefter Bohrungen, Import,
Rundreise; Pruefung gegen das amtliche XSD und Import der amtlichen Beispiele nur mit Netz (sonst uebersprungen)."""
from __future__ import annotations

import copy
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "services" / "geodaten"), str(REPO / "services" / "modeler")]
from baugrundmodell.normen import klassen_liste  # noqa: E402
from geodaten import boreholeml as bml  # noqa: E402

BERLIN = json.loads((REPO / "data" / "beispiele" / "berlin_v67b.json").read_text(encoding="utf-8"))
NS = {"bml": bml.BML, "gml": bml.GML, "gmd": bml.GMD, "sf": bml.SF}
BEISPIEL = "https://schemas.bgr.de/boreholeml/3.2/examples/borehole_BDN_2119BD0027.xml"


def geprueft(doc: dict) -> dict:
    d = copy.deepcopy(doc)
    for b in d["boreholes"]:
        for ly in b.get("layers") or []:
            ly["geprueft"] = True
    return d


def bohrungen(xml: bytes) -> dict[str, ET.Element]:
    return {b.findtext("bml:id", namespaces=NS): b for b in ET.fromstring(xml).iterfind(".//bml:Borehole", NS)}


@pytest.fixture(scope="module")
def export_berlin():
    return bml.exportieren([geprueft(BERLIN)], projekt="Berlin V-67b-VE", organisation="Büro", sig="abc",
                           heute=date(2026, 11, 2))


# ---------------------------------------------------------------- Codetabelle
def test_codetabelle_deckt_alle_bodenarten_der_app():
    klassen = {k["klasse"] for k in klassen_liste()} - {"unklassifiziert"}
    assert klassen <= set(bml.CODES["bodenart"]), klassen - set(bml.CODES["bodenart"])
    for k, v in bml.CODES["bodenart"].items():
        assert v["petrographie"]["code"] and v["petrographie"]["liste"] == "RockNameList", k
    assert bml.CODES["quelle"]["versionen"]["RockNameList"].startswith("version 2.")
    assert bml.bodenart_aus("fS", None) == ("Sand", "")                 # Feinsand -> Sand ueber die Hierarchie
    assert bml.bodenart_aus("T", None) == ("Ton", "")                   # nicht Glimmerton / Lauenburger Ton
    assert bml.bodenart_aus("la", "yf")[0] == "Auffuellung"
    beton, hinweis = bml.bodenart_aus("fa", "y")
    assert beton == "Beton" and "mehrdeutig" in hinweis
    assert bml.bodenart_aus("KMat", None)[0] is None
    assert bml.bodenart_aus("Kst", None) == ("Fels (Kalkstein)", "")    # nicht Kreidestein (DIN 4023 Tab. 3, docs/28)
    assert bml.bodenart_aus("Kst", "kt")[0] == "Fels (Kalktuff)" and bml.bodenart_aus("T", "glä")[0] == "Baenderton"
    assert bml.bodenart_aus("K", "ka")[0] == "Wiesenkalk" and bml.bodenart_aus("l", "hgx")[0] == "Hangschutt"


# ---------------------------------------------------------------- Export
def test_export_berlin_kopf_lage_und_schichten(export_berlin):
    xml, bericht = export_berlin
    assert bericht["exportiert"] == ["422C-460", "422C-461", "422C-5525", "422C-5526", "422C-5527"]
    assert {a["code"]: a["grund"] for a in bericht["ausgelassen"]} == {"S2a": "ohne Koordinaten", "B 1/17": "keine Schichten"}
    b = bohrungen(xml)["422C-460"]
    punkt = b.find("bml:location/gml:Point", NS)
    assert punkt.get("srsName").endswith("/5556") and punkt.findtext("gml:pos", namespaces=NS).split()[2] == "36.25"
    assert b.findtext("bml:boreholeStatus", namespaces=NS) == "bo"
    assert b.findtext("bml:codingStandard", namespaces=NS) == "DIN4022"
    assert b.findtext("bml:drillingPurpose", namespaces=NS) == "GTE"
    assert b.findtext("bml:organisation/bml:BoreholeProvider/gmd:organisationName/*", namespaces=NS) == "Büro"
    assert b.findtext("bml:origin/bml:Origin/bml:levelMethod", namespaces=NS) == "F"
    erste = b.find("bml:intervalSeries/bml:IntervalSeries/bml:layer/bml:Interval", NS)
    assert erste.findtext("bml:rockCode", namespaces=NS) == "A (S)"
    assert erste.findtext("bml:geoGenesis", namespaces=NS) == "yf"            # Auffuellung aus der Deutung
    assert erste.findtext("bml:lithology/bml:Lithology/bml:rockName", namespaces=NS) == "S"
    assert erste.findtext("bml:descriptiveText/*", namespaces=NS) == "Sand/Auffullung/grau/trocken"
    anzahl = len(b.findall("bml:intervalSeries/bml:IntervalSeries/bml:layer", NS))
    assert anzahl == len(next(x for x in BERLIN["boreholes"] if x["code"] == "422C-460")["layers"])


def test_export_laesst_aus_was_nicht_belegt_ist():
    d = geprueft(BERLIN)
    b0, b1, b2, b3 = d["boreholes"][:4]
    b0["layers"][1]["geprueft"] = False                                       # nicht vollstaendig geprueft
    b1["crs_epsg"], b1["x"] = 31468, 4594774.3                                # Gauss-Krueger
    b2["gok_source"] = "relativ"                                              # Hoehe nur relativ
    b3["crs_epsg"] = None
    _, bericht = bml.exportieren([d], projekt="P")
    gruende = {a["code"]: a["grund"] for a in bericht["ausgelassen"]}
    assert gruende["422C-460"] == "nicht vollständig geprüft"
    assert gruende["422C-461"].startswith("EPSG:31468") and gruende["422C-5525"] == "ohne GOK in m NHN"
    assert gruende["422C-5526"] == "ohne Koordinatensystem (EPSG)"
    with pytest.raises(ValueError, match="keine exportierbare Bohrung"):
        bml.exportieren([BERLIN], projekt="P")                                 # nichts geprueft


def test_export_zonenkennung_hoehe_aus_dgm_und_lage_vom_plan():
    d = geprueft(BERLIN)
    b = next(x for x in d["boreholes"] if x["code"] == "422C-5527")
    b.update(crs_epsg=5650, x=33000000.0 + b["x"], gok_source="DGM", coord_source="Plan (kalibriert)")
    xml, _ = bml.exportieren([{**d, "boreholes": [b]}], projekt="P", dgm_zelle=1.0)
    e = bohrungen(xml)["422C-5527"]
    assert e.find("bml:location/gml:Point", NS).get("srsName").endswith("/5556")
    assert e.findtext("bml:location/gml:Point/gml:pos", namespaces=NS).startswith("394909.300 ")
    assert e.findtext("bml:origin/bml:Origin/bml:originalLocation", namespaces=NS).startswith("33394909.300 ")
    assert e.findtext("bml:origin/bml:Origin/bml:levelMethod", namespaces=NS) == "D1"
    assert e.findtext("bml:origin/bml:Origin/bml:locationMethod", namespaces=NS) == "K"
    xml, _ = bml.exportieren([{**d, "boreholes": [b]}], projekt="P", dgm_zelle=2.5)
    assert bohrungen(xml)["422C-5527"].findtext("bml:origin/bml:Origin/bml:levelMethod", namespaces=NS) == "D"


# ---------------------------------------------------------------- Import und Rundreise
def test_rundreise_berlin(export_berlin):
    xml, _ = export_berlin
    doc = bml.importieren(xml, "berlin.xml")
    neu = {b["code"]: b for b in doc["boreholes"]}
    for alt in BERLIN["boreholes"]:
        if alt["code"] not in neu:
            continue
        b = neu[alt["code"]]
        assert (b["x"], b["y"], b["crs_epsg"], b["gok_nhn"]) == (pytest.approx(alt["x"]), pytest.approx(alt["y"]),
                                                                 alt["crs_epsg"], pytest.approx(alt["gok_nhn"]))
        assert [(ly["top_depth"], ly["bottom_depth"]) for ly in b["layers"]] == \
               [(pytest.approx(ly["top_depth"]), pytest.approx(ly["bottom_depth"])) for ly in alt["layers"]]
        assert [ly["soil_class"] for ly in b["layers"]] == [ly.get("soil_class") or None for ly in alt["layers"]]
        assert b["gok_source"] == "BoreholeML" and b["issues"][0].startswith("aus BoreholeML")
    assert len(neu) == 5


SYNTHETISCH = b"""<?xml version="1.0" encoding="UTF-8"?>
<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:bml="https://schemas.bgr.de/boreholeml/3.0.1" xmlns:gmd="http://www.isotc211.org/2005/gmd"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <wfs:member>
    <bml:Borehole gml:id="B1">
      <bml:location><gml:Point gml:id="B1_L" srsName="EPSG:5555"><gml:pos>490000.0 5960000.0 12.50</gml:pos></gml:Point></bml:location>
      <bml:id>9999XX0001</bml:id>
      <bml:shortName><gmd:LocalisedCharacterString>RKS 7</gmd:LocalisedCharacterString></bml:shortName>
      <bml:totalLength uom="m">6.00</bml:totalLength>
      <bml:databaseSource>BDN</bml:databaseSource>
      <bml:groundwaterEncountered>true</bml:groundwaterEncountered>
      <bml:groundwater><bml:Groundwater><bml:entryDepth uom="m">2.40</bml:entryDepth></bml:Groundwater></bml:groundwater>
      <bml:intervalSeries><bml:IntervalSeries><bml:version>0</bml:version>
        <bml:layer><bml:Interval><bml:from uom="m">0</bml:from><bml:to uom="m">6</bml:to>
          <bml:lithology><bml:Lithology><bml:rockName>U</bml:rockName></bml:Lithology></bml:lithology>
        </bml:Interval></bml:layer></bml:IntervalSeries></bml:intervalSeries>
      <bml:intervalSeries><bml:IntervalSeries><bml:version>1</bml:version>
        <bml:layer><bml:Interval><bml:from uom="m">0.00</bml:from><bml:to uom="m">1.00</bml:to>
          <bml:rockCode>A</bml:rockCode>
          <bml:geoGenesis>yf</bml:geoGenesis>
          <bml:lithology><bml:Lithology><bml:rockName>la</bml:rockName></bml:Lithology></bml:lithology>
        </bml:Interval></bml:layer>
        <bml:layer><bml:Interval><bml:from uom="m">1.00</bml:from><bml:to uom="m">4.00</bml:to>
          <bml:rockNameText><gmd:LocalisedCharacterString>Feinsand, schluffig</gmd:LocalisedCharacterString></bml:rockNameText>
          <bml:lithology><bml:Lithology><bml:rockName>U</bml:rockName><bml:percentageTo>30</bml:percentageTo></bml:Lithology></bml:lithology>
          <bml:lithology><bml:Lithology><bml:rockName>fS</bml:rockName><bml:percentageTo>100</bml:percentageTo></bml:Lithology></bml:lithology>
        </bml:Interval></bml:layer>
        <bml:layer><bml:Interval><bml:from uom="m">4.00</bml:from><bml:to uom="m">5.00</bml:to>
          <bml:lithology><bml:Lithology><bml:rockName>KMat</bml:rockName></bml:Lithology></bml:lithology>
        </bml:Interval></bml:layer>
        <bml:layer><bml:Interval><bml:from uom="m">5.00</bml:from><bml:to uom="m">6.00</bml:to>
          <bml:lithology xsi:nil="true"/>
        </bml:Interval></bml:layer>
      </bml:IntervalSeries></bml:intervalSeries>
    </bml:Borehole>
  </wfs:member>
</wfs:FeatureCollection>"""


def test_import_version_hierarchie_hauptanteil_und_markierung():
    doc = bml.importieren(SYNTHETISCH, "wfs.xml")
    b = doc["boreholes"][0]
    assert (b["code"], b["fremd_id"], b["crs_epsg"], b["x"], b["gok_nhn"], b["end_depth"]) == \
           ("RKS 7", "9999XX0001", 25832, 490000.0, 12.5, 6.0)
    assert b["herkunft"] == "SGD" and b["coord_source"] == "BoreholeML (BDN)"
    assert b["groundwater"] == [{"depth": 2.4, "nhn": 10.1, "kind": "angetroffen"}]
    assert "2 Schichtenverzeichnisse" in " ".join(b["issues"])
    klassen = [ly["soil_class"] for ly in b["layers"]]
    assert klassen == ["Auffuellung", "Sand", None, None]                    # Version 1; fS (100 %) vor U (30 %)
    assert b["layers"][1]["description_raw"] == "Feinsand, schluffig"
    assert "KMat" in b["layers"][2]["issues"][0] and b["layers"][3]["issues"]


def test_import_fehler():
    with pytest.raises(ValueError, match="kein lesbares XML"):
        bml.importieren(b"<<kein xml", "x.xml")
    with pytest.raises(ValueError, match="keine BoreholeML-Bohrung"):
        bml.importieren(b"<a><b/></a>", "x.xml")


# ---------------------------------------------------------------- mit Netz: amtliches XSD und Beispiel
def _laden(url: str) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=30) as antwort:
            return antwort.read()
    except OSError as err:
        pytest.skip(f"{url} nicht erreichbar ({err})")


@pytest.fixture(scope="module")
def schema(tmp_path_factory):
    xmlschema = pytest.importorskip("xmlschema")
    huelle = tmp_path_factory.mktemp("xsd") / "huelle.xsd"
    huelle.write_text(
        '<schema xmlns="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:groundtwin:pruefhuelle">'
        f'<import namespace="{bml.BML}" schemaLocation="https://schemas.bgr.de/boreholeml/3.2/BoreholeML.xsd"/>'
        f'<import namespace="{bml.SF}" '
        'schemaLocation="https://schemas.opengis.net/ogcapi/features/part1/1.0/xml/core-sf.xsd"/></schema>',
        encoding="utf-8")
    try:
        return xmlschema.XMLSchema(str(huelle), uri_mapper=lambda u: u.replace("http://schemas.opengis.net/",
                                                                              "https://schemas.opengis.net/"))
    except Exception as err:                                                  # Netz fehlt oder Server antwortet nicht
        pytest.skip(f"amtliche Schemas nicht ladbar ({type(err).__name__})")


def test_export_ist_gueltig_nach_amtlichem_xsd(schema, export_berlin):
    fehler = [str(f)[:200] for f in schema.iter_errors(export_berlin[0].decode("utf-8"))]
    assert not fehler, fehler
    beispiel = _laden(BEISPIEL)
    assert schema.is_valid(beispiel.decode("utf-8"))                         # der Pruefer selbst stimmt


def test_amtliches_beispiel_importieren():
    doc = bml.importieren(_laden(BEISPIEL), "borehole_BDN_2119BD0027.xml")
    b = doc["boreholes"][0]
    assert (b["crs_epsg"], b["gok_nhn"], len(b["layers"])) == (25832, pytest.approx(1.49), 10)
    assert {ly["soil_class"] for ly in b["layers"]} == {"Schluff", "Ton"}


# ---------------------------------------------------------------- Issue #26: Art und Datum der Wasserstaende
def _mit_arten() -> dict:
    d = geprueft(BERLIN)
    b = d["boreholes"][0]
    b["groundwater"] = [{"depth": 3.8, "kind": "angetroffen", "observed_on": "2020-04-14"},
                        {"depth": 3.1, "kind": "Ruhewasser", "observed_on": "2020-04-15"},
                        {"depth": 0.9, "kind": "Schichtenwasser"}]
    d["boreholes"][1]["groundwater"] = [{"depth": 3.6, "kind": "gemessen"}]     # Art offen: nur Text
    return d


def test_export_wasserstaende_mit_art_und_datum_rundreise():
    d = _mit_arten()
    xml, _ = bml.exportieren([d], projekt="Berlin", sig="abc", heute=date(2026, 11, 19))
    bh = bohrungen(xml)
    gw = bh[d["boreholes"][0]["code"]].find("bml:groundwater/bml:Groundwater", NS)
    assert gw.findtext("bml:entryDepth", namespaces=NS) == "3.80"
    assert gw.findtext("bml:entryDateTime", namespaces=NS) == "2020-04-14"
    assert gw.findtext("bml:balancedLevel", namespaces=NS) == "3.10"
    assert gw.find("bml:endLevel", NS) is None
    assert bh[d["boreholes"][1]["code"]].find("bml:groundwater", NS) is None   # Art offen: kein Feld
    text = ET.tostring(bh[d["boreholes"][0]["code"]], encoding="unicode")
    assert "0,90 m u. GOK (Schichtenwasser)" in text
    zurueck = {b["code"]: b for b in bml.importieren(xml, "x.xml")["boreholes"]}
    assert sorted((g["kind"], g["depth"], g.get("observed_on")) for g in zurueck[d["boreholes"][0]["code"]]["groundwater"]) \
        == [("Ruhewasser", 3.1, "2020-04-15"), ("angetroffen", 3.8, "2020-04-14")]


def test_export_mit_wasserarten_ist_gueltig_nach_amtlichem_xsd(schema):
    xml, _ = bml.exportieren([_mit_arten()], projekt="Berlin", sig="abc", heute=date(2026, 11, 19))
    fehler = [str(f)[:200] for f in schema.iter_errors(xml.decode("utf-8"))]
    assert not fehler, fehler


# ---------------------------------------------------------------- Issue #27 Teil 4: Sondierungen
def _demo_mit_sondierungen():
    sys.path.insert(0, str(REPO))
    from ui import projekt as pj
    from ui import sondierung as sd
    docs = [json.loads((REPO / "data" / "beispiele" / "demo_synthetisch.json").read_text(encoding="utf-8"))]
    p = pj.neues_projekt(docs, "t")
    for sid, x, y in (("0:S0", 565030, 5933020), ("0:S1", 565050, 5933030), ("0:S2", 565080, 5933060)):
        for feld, wert in (("x", x), ("y", y), ("geprueft", sid != "0:S1")):
            pj.aendern(docs, p, {"op": "sondierung", "sondierung": sid, "feld": feld, "wert": wert})
    pj.alle_pruefen(docs, p, True)
    drin, raus = sd.fuer_ifc(docs, p)
    return pj.wirksame_docs(docs, p), drin, raus, docs


def test_export_sondierungen_als_investigation_rundreise():
    v, drin, raus, docs = _demo_mit_sondierungen()
    xml, ber = bml.exportieren(v, projekt="Demo", sig="abc", heute=date(2026, 11, 22), sondierungen=drin,
                               sondierungen_draussen=raus, epsg_projekt=25832)
    assert ber["sondierungen"] == ["DPH 1", "CPT 1"] and len(ber["exportiert"]) == 12
    assert {"code": "DPH 2", "grund": "Sondierung nicht geprüft"} in ber["ausgelassen"]
    bh = bohrungen(xml)
    dph = bh["DPH 1"]
    assert dph.find("bml:intervalSeries", NS) is None                       # kein Schichtenverzeichnis
    assert dph.find("bml:drillingMethod", NS).get(f"{{{bml.XSI}}}nil") == "true"   # DPH: kein Code in der Liste
    assert bh["CPT 1"].findtext("bml:drillingMethod", namespaces=NS) == "DPU"
    inv = dph.find("bml:investigation/bml:Investigation", NS)
    assert inv.findtext("bml:investigationType", namespaces=NS) == "SM"
    pv = inv.find("bml:investigationDetail/bml:Measurement/bml:measurementResult/bml:ParameterValues", NS)
    assert pv.findtext("bml:parameterCommon", namespaces=NS) == "SON"
    zeilen = ET.tostring(pv.find("bml:valueMatrix", NS), encoding="unicode", method="text").strip().splitlines()
    assert zeilen[0] == "tiefe_unten_m;N10" and len(zeilen) == 61
    zurueck = bml.importieren(xml, "x.xml")
    assert len(zurueck["boreholes"]) == 12                                   # Sondierungen keine Bohrungen
    s = {x["code"]: x for x in zurueck["sondierungen"]}
    gelesen = docs[0]["sondierungen"][0]["werte"]
    assert [w[2] for w in s["DPH 1"]["werte"]] == [float(w[2]) for w in gelesen] and s["DPH 1"]["art"] == "DPH"
    assert (s["CPT 1"]["art"], len(s["CPT 1"]["werte"]), s["CPT 1"]["x"]) == ("CPT", 41, 565080.0)


def test_export_zensierte_n10_bleiben_zensiert():
    v, drin, _, _ = _demo_mit_sondierungen()
    for s in drin:
        s["geprueft"] = True
    dph2 = next(s for s in drin if s["code"] == "DPH 2")
    assert dph2["zensierte"]                                                 # s05: Werte ueber der Achse
    xml, _ = bml.exportieren(v, projekt="Demo", sig="abc", heute=date(2026, 11, 22), sondierungen=drin, epsg_projekt=25832)
    s = {x["code"]: x for x in bml.importieren(xml, "x.xml")["sondierungen"]}
    zens = [w for w in s["DPH 2"]["werte"] if isinstance(w[2], dict)]
    assert len(zens) == len(dph2["zensierte"]) and all(w[2]["zensiert"] for w in zens)


def test_export_mit_sondierungen_ist_gueltig_nach_amtlichem_xsd(schema):
    v, drin, raus, _ = _demo_mit_sondierungen()
    xml, _ = bml.exportieren(v, projekt="Demo", sig="abc", heute=date(2026, 11, 22), sondierungen=drin,
                             sondierungen_draussen=raus, epsg_projekt=25832)
    fehler = [str(f)[:200] for f in schema.iter_errors(xml.decode("utf-8"))]
    assert not fehler, fehler
