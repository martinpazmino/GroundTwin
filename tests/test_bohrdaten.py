"""Bohrungen der Laender (services/geodaten/geodaten/bohrdaten.py): Lage, Auswahl der Dienste, Abfrage mit Attrappe
der Dienste (Kopfdaten und BoreholeML), Gegenprobe mit dem Gutachten, Uebernahme; dazu Abfragen am echten Dienst
(Berlin, NRW) - ohne Netz uebersprungen."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "services" / "geodaten"), str(REPO / "services" / "modeler")]
from geodaten import bohrdaten as bd  # noqa: E402

BERLIN = json.loads((REPO / "data" / "beispiele" / "berlin_v67b.json").read_text(encoding="utf-8"))

KOPF_BE = """<?xml version="1.0" encoding="UTF-8"?>
<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:bohrdaten="http://gdi.berlin.de/bohrdaten">
  <wfs:member><bohrdaten:bohrpunkte gml:id="b1">
    <bohrdaten:schluessel>422C00460</bohrdaten:schluessel><bohrdaten:xcoord>394774.32</bohrdaten:xcoord>
    <bohrdaten:ycoord>5818338.12</bohrdaten:ycoord><bohrdaten:endteufe>20.0</bohrdaten:endteufe>
    <bohrdaten:ansatzhoehe>36.25</bohrdaten:ansatzhoehe><bohrdaten:bohrende>1993-02-17</bohrdaten:bohrende>
    <bohrdaten:langname>422C-460</bohrdaten:langname>
    <bohrdaten:profil_lang>https://gdi.berlin.de/ext/bohrungen/getimage?ID=1</bohrdaten:profil_lang>
    <bohrdaten:geom><gml:Point gml:id="p1" srsName="urn:ogc:def:crs:EPSG::25833"><gml:pos>394774.32 5818338.12</gml:pos></gml:Point></bohrdaten:geom>
  </bohrdaten:bohrpunkte></wfs:member>
  <wfs:member><bohrdaten:bohrpunkte gml:id="b2">
    <bohrdaten:schluessel>999X00001</bohrdaten:schluessel><bohrdaten:endteufe>8.0</bohrdaten:endteufe>
    <bohrdaten:ansatzhoehe>35.1</bohrdaten:ansatzhoehe><bohrdaten:langname>999X-1</bohrdaten:langname>
    <bohrdaten:geom><gml:Point gml:id="p2"><gml:pos>394860.0 5818400.0</gml:pos></gml:Point></bohrdaten:geom>
  </bohrdaten:bohrpunkte></wfs:member>
  <wfs:member><bohrdaten:bohrpunkte gml:id="b3">
    <bohrdaten:schluessel>999X00002</bohrdaten:schluessel><bohrdaten:langname>999X-2</bohrdaten:langname>
    <bohrdaten:geom><gml:Point gml:id="p3"><gml:pos>395300.0 5818700.0</gml:pos></gml:Point></bohrdaten:geom>
  </bohrdaten:bohrpunkte></wfs:member>
</wfs:FeatureCollection>""".encode()


def bml_nw(ids: list[str]) -> bytes:
    """BoreholeML 3.0 wie der Dienst in NRW: CRS nur am Rahmen der Sammlung, Kurzname, Schichten mit Petrographie."""
    lage = {"DABO_1": (368100.0, 5724420.0), "DABO_2": (368150.0, 5724380.0)}
    bohrungen = "".join(f"""
  <wfs:member><bml:Borehole gml:id="{i}">
    <bml:location><gml:Point gml:id="{i}_L"><gml:pos>{lage[i][0]} {lage[i][1]} 60.0</gml:pos></gml:Point></bml:location>
    <bml:id>{i}</bml:id>
    <bml:shortName><gmd:LocalisedCharacterString>{i[-1]}</gmd:LocalisedCharacterString></bml:shortName>
    <bml:totalLength uom="m">6.0</bml:totalLength>
    <bml:databaseSource>DABO</bml:databaseSource>
    <bml:intervalSeries><bml:IntervalSeries><bml:version>0</bml:version>
      <bml:layer><bml:Interval><bml:from uom="m">0</bml:from><bml:to uom="m">0.3</bml:to>
        <bml:lithology><bml:Lithology><bml:rockName>lo</bml:rockName></bml:Lithology></bml:lithology></bml:Interval></bml:layer>
      <bml:layer><bml:Interval><bml:from uom="m">0.3</bml:from><bml:to uom="m">4</bml:to>
        <bml:lithology><bml:Lithology><bml:rockName>fS</bml:rockName></bml:Lithology></bml:lithology></bml:Interval></bml:layer>
      <bml:layer><bml:Interval><bml:from uom="m">4</bml:from><bml:to uom="m">6</bml:to>
        <bml:lithology><bml:Lithology><bml:rockName>U</bml:rockName></bml:Lithology></bml:lithology></bml:Interval></bml:layer>
    </bml:IntervalSeries></bml:intervalSeries>
  </bml:Borehole></wfs:member>""" for i in ids if i in lage)                    # unbekannte Kennungen liefert der Dienst nicht
    return f"""<?xml version="1.0" encoding="utf-8"?>
<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:bml="http://www.infogeo.de/boreholeml/3.0" xmlns:gmd="http://www.isotc211.org/2005/gmd">
  <wfs:boundedBy><gml:Envelope srsName="urn:ogc:def:crs:EPSG::5555" srsDimension="3">
    <gml:lowerCorner>368000 5724300 50</gml:lowerCorner><gml:upperCorner>368200 5724500 61</gml:upperCorner></gml:Envelope></wfs:boundedBy>
  {bohrungen}
</wfs:FeatureCollection>""".encode()


AUSNAHME = b"""<?xml version="1.0"?><ExceptionReport xmlns="http://www.opengis.net/ows/1.1"><Exception exceptionCode="X">
<ExceptionText>Request rejected</ExceptionText></Exception></ExceptionReport>"""


def attrappe(aufrufe: list | None = None):
    """Statt Netz: Berlin liefert Kopfdaten, Brandenburg ist nicht erreichbar, NRW liefert BoreholeML."""
    def holer(url: str, zeit: float) -> bytes:
        if aufrufe is not None:
            aufrufe.append(url)
        if "gdi.berlin.de" in url:
            return KOPF_BE
        if "brandenburg" in url:
            raise bd.DienstFehler("nicht erreichbar (Attrappe)")
        if "bml3.nrw.de" in url and "RESOURCEID=" in url:
            return bml_nw(url.split("RESOURCEID=")[1].split("&")[0].split(","))
        if "bml3.nrw.de" in url:
            return bml_nw(["DABO_1", "DABO_2"])
        return AUSNAHME
    return holer


# ---------------------------------------------------------------- Lage und Dienste
@pytest.mark.parametrize("e,n,zone,lon,lat", [(394774.3, 5818338.1, 33, 13.449673, 52.505003),
                                               (368228.4, 5724116.5, 32, 7.095175, 51.65258),
                                               (512295.7, 5403623.3, 32, 9.167388, 48.785487)])
def test_utm_zu_geo_wie_proj(e, n, zone, lon, lat):
    """Vergleichswerte aus PROJ (pyproj 3.8, ETRS89): Abweichung unter 0,1 mm."""
    l2, b2 = bd.utm_zu_geo(e, n, zone)
    assert abs(l2 - lon) < 2e-6 and abs(b2 - lat) < 2e-6


def test_dienste_am_ort_und_systeme():
    # das Land aus den Laendergrenzen (VG2500), nicht aus den Rechtecken: Berlin fragt Brandenburg nicht mehr mit
    assert [d["id"] for d in bd.dienste_am_ort(394774.3, 5818338.1, 25833)] == ["BE"]
    assert [d["id"] for d in bd.dienste_am_ort(407692.0, 5818077.0, 25833)] == ["BB"]    # Brandenburg an der Grenze
    assert [d["id"] for d in bd.dienste_am_ort(407692.0, 5818077.0, 25833, radius=1500)] == ["BB", "BE"]  # Mitte zuerst
    assert [d["id"] for d in bd.dienste_am_ort(368228.4, 5724116.5, 25832)] == ["NW"]
    assert [d["id"] for d in bd.dienste_am_ort(32512295.7, 5403623.3, 4647)] == ["BW"]   # Zonenkennung im Rechtswert
    assert bd.dienste_am_ort(705000.0, 5300000.0, 25832) == []                           # Bayern: kein Datendienst
    assert bd.dienste_am_ort(285763.0, 5795714.0, 25833) == []                           # Sachsen-Anhalt, nicht BB
    with pytest.raises(ValueError, match="ETRS89/UTM"):
        bd.dienste_am_ort(4594774.3, 5818338.1, 31468)
    for d in bd.DIENSTE:                                                                 # jede Angabe mit Beleg
        assert d["beleg"].startswith("https://") and d["namensnennung"] and d["status"] in ("geprueft", "ungeprueft")
        if d["art"] in bd.BOHRDIENSTE + ("wcs-dgm", "lod2-kacheln"):                     # angebunden: geprueft, Lizenz
            assert d["status"] == "geprueft" and d["geprueft"] and d["lizenz"]


# ---------------------------------------------------------------- Abfrage mit Attrappe
def test_abfrage_kopfdaten_umkreis_fehler_und_gegenprobe():
    aufrufe: list[str] = []
    erg = bd.abfragen(394836.0, 5818414.0, 25833, 250, holer=attrappe(aufrufe))
    assert erg["dienste"] == ["BE"] and erg["fehler"] == [] and erg["portale"] == []      # nur Berlin, mit Dienst
    assert [t["name"] for t in erg["treffer"]] == ["999X-1", "422C-460"]                  # nach Abstand; 999X-2 zu weit
    t = erg["treffer"][1]
    assert (t["schichten"], t["gok"], t["teufe"], t["datum"]) == ("grafik", 36.25, 20.0, "1993-02-17")
    assert t["profil"].startswith("https://gdi.berlin.de/") and erg["treffer"][0]["schichten"] == "keine"
    assert "SRSNAME=urn:ogc:def:crs:EPSG::25833" in aufrufe[0] and "BBOX=394586.0,5818164.0" in aufrufe[0]
    assert erg["quellen"][0]["lizenz"] == "dl-de/zero-2.0"
    eigene = [{"id": f"0:{i}", "code": b["code"], "x": b.get("x"), "y": b.get("y"), "gok": b.get("gok_nhn")}
              for i, b in enumerate(BERLIN["boreholes"])]
    gp = bd.doppelte(erg["treffer"], eigene)
    assert gp == {"anzahl": 1, "lage_max": 0.03, "gok_max": 0.0}                       # 2 cm in x und in y
    assert t["gutachten"] == "422C-460" and t["abweichung_gok"] == 0.0 and "gutachten" not in erg["treffer"][0]


def test_doppelte_nach_name_oder_abstand():
    treffer = [{"name": "B 1", "x": 100.0, "y": 0.0, "gok": 10.0}, {"name": "X9", "x": 0.0, "y": 2.0, "gok": None},
               {"name": "B1", "x": 500.0, "y": 0.0, "gok": 10.0}]
    gp = bd.doppelte(treffer, [{"id": "0:0", "code": "B1", "x": 120.0, "y": 0.0, "gok": 10.3},
                               {"id": "0:1", "code": "RKS 7", "x": 0.0, "y": 0.0, "gok": None}])
    assert [t.get("gutachten") for t in treffer] == ["B1", "RKS 7", None]   # Name (20 m), Abstand (2 m), zu weit (380 m)
    assert gp == {"anzahl": 2, "lage_max": 20.0, "gok_max": 0.3}


def test_boreholeml_dienst_auflisten_und_uebernehmen():
    erg = bd.abfragen(368120.0, 5724400.0, 25832, 250, holer=attrappe())
    assert [(t["name"], t["schichten"], t["schichten_n"]) for t in erg["treffer"]] == [("1", "boreholeml", 3), ("2", "boreholeml", 3)]
    doc = bd.holen("NW", ["DABO_2", "DABO_9"], holer=attrappe())
    b = doc["boreholes"][0]
    assert (b["code"], b["fremd_id"], b["herkunft"], b["crs_epsg"], b["gok_nhn"]) == ("NW-2", "DABO_2", "SGD", 25832, 60.0)
    assert b["issues"][0].startswith("aus Bohrpunkte boreholeML Full (Nordrhein-Westfalen), ID DABO_2, dl-de/by-2.0")
    assert [ly["soil_class"] for ly in b["layers"]] == [None, "Sand", "Schluff"]          # lo bleibt unklassifiziert
    assert doc["fehlen"] == ["DABO_9"] and "{jahr}" not in b["namensnennung"]
    with pytest.raises(ValueError, match="nur Kopfdaten"):
        bd.holen("BE", ["422C00460"], holer=attrappe())


def test_an_der_landesgrenze_beide_dienste_und_fehler_je_dienst():
    erg = bd.abfragen(407692.0, 5818077.0, 25833, 1500, holer=attrappe())             # Brandenburg, Berlin im Umkreis
    assert erg["dienste"] == ["BB", "BE"] and [f["dienst"] for f in erg["fehler"]] == ["BB", "BB"]
    assert erg["portale"] == []                                                       # beide Laender mit Dienst


def test_grenze_zu_einem_land_ohne_dienst_nennt_dessen_portal():
    # NRW an der Grenze zu Niedersachsen (bei x = 428500): NW abgefragt, fuer Niedersachsen das Portal und die BGR-Karte
    erg = bd.abfragen(428300.0, 5800000.0, 25832, 500, holer=attrappe())
    assert erg["dienste"] == ["NW"] and [p["dienst"] for p in erg["portale"]] == ["NI", "DE-BGR"]   # bundesweit zuletzt
    nur_nrw = bd.abfragen(368120.0, 5724400.0, 25832, 250, holer=attrappe())
    assert nur_nrw["portale"] == []


def test_kein_dienst_sagt_was_angebunden_ist_und_wo_die_daten_sind():
    satz = bd.ohne_dienst(691567.3, 5334734.3, 25832, "dgm")                          # München
    assert satz.startswith("angebunden: Berlin, Brandenburg, Nordrhein-Westfalen; im Portal des Landes: ")
    assert "https://" in satz and "Deutschland" not in satz
    assert bd.ohne_dienst(691567.3, 5334734.3, 25832, "bohrungen").startswith(
        "angebunden: Baden-Württemberg, Berlin, Brandenburg, Nordrhein-Westfalen; im Portal des Landes: ")


def test_land_ohne_datendienst_nennt_portale():
    erg = bd.abfragen(691567.3, 5334734.3, 25832, 250, holer=attrappe())              # München: Bayern
    assert erg["dienste"] == [] and erg["fehler"] == [] and erg["treffer"] == []
    portale = {p["dienst"]: p for p in erg["portale"]}
    assert set(portale) == {"BY", "DE-BGR"} and portale["BY"]["url"].startswith("https://www.umweltatlas.bayern.de")
    assert all(p["status"] == "ungeprueft" for p in portale.values())


def test_ausnahme_des_dienstes_wird_fehler():
    erg = bd.abfragen(512300.0, 5403600.0, 25832, 100, holer=attrappe())                  # BW -> Attrappe: Ausnahme
    assert erg["treffer"] == [] and erg["fehler"][0]["dienst"] == "BW" and "Request rejected" in erg["fehler"][0]["fehler"]


# ---------------------------------------------------------------- am echten Dienst (Netz)
def _live(f):
    try:
        return f()
    except bd.DienstFehler as err:
        pytest.skip(f"Dienst nicht erreichbar ({err})")


def test_berlin_echt_gegenprobe_mit_dem_beispiel():
    erg = _live(lambda: bd.abfragen(394836.0, 5818414.0, 25833, 250))
    if any(f["dienst"] == "BE" for f in erg["fehler"]):
        pytest.skip(f"Berlin nicht erreichbar: {erg['fehler']}")
    eigene = [{"id": f"0:{i}", "code": b["code"], "x": b.get("x"), "y": b.get("y"), "gok": b.get("gok_nhn")}
              for i, b in enumerate(BERLIN["boreholes"])]
    gp = bd.doppelte(erg["treffer"], eigene)
    assert gp["anzahl"] == 5 and gp["lage_max"] <= 0.1 and gp["gok_max"] <= 0.05, gp


def test_nrw_echt_schichtdaten_holen():
    erg = _live(lambda: bd.abfragen(368100.0, 5724400.0, 25832, 150))
    mit = [t for t in erg["treffer"] if t["schichten"] == "boreholeml"]
    if not mit:
        pytest.skip(f"NRW ohne Antwort: {erg['fehler']}")
    doc = _live(lambda: bd.holen("NW", [mit[0]["id"]]))
    b = doc["boreholes"][0]
    assert b["code"].startswith("NW-") and b["layers"] and any(ly["soil_class"] for ly in b["layers"])
