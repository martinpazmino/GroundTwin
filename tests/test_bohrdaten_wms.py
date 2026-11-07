"""Offline-Tests fuer services/geodaten/geodaten/bohrdaten_wms.py (docs/26 §2 Option b, §3).

Lizenz- und Datenschutzvermerk zu den gespeicherten Beispielantworten:
  1. BEISPIEL_BGR_GBL_XML: verkleinerter, anonymisierter Auszug einer WMS-GetFeatureInfo-Antwort
     des Dienstes `https://services.bgr.de/wms/geologie/gbl/` (Layer 0 „Einzelbohrungen Info“).
     Quelle/Lizenz: © BGR Hannover und Bayerisches Landesamt fuer Umwelt (LfU), BGR-Nutzungsbedingungen
     (Darstellungsdienst, https://www.bgr.bund.de/agb). Personenbezogene oder dienststelleninterne
     Kontaktdaten wurden vollstaendig entfernt.
  2. BEISPIEL_BREMEN_GML: verkleinerter, anonymisierter Auszug einer WMS-GetFeatureInfo-Antwort
     des Dienstes `https://geodienste.bremen.de/wms_bohrdatenbank` (Layer „Bohrpunkte_Bremen“).
     Quelle/Lizenz: CC BY 4.0 – © Freie Hansestadt Bremen, GeoInformation Bremen / Geologischer Dienst
     fuer Bremen (GDfB). Auftraggeber- und Firmenangaben wurden entfernt.
"""
from __future__ import annotations

from datetime import date

import pytest

from services.geodaten.geodaten import bohrdaten, bohrdaten_wms
from services.geodaten.geodaten.netz import DienstFehler

# Anonymisierte Beispielantwort: BGR GBL WMS 1.3.0 (INFO_FORMAT=text/xml, ESRI FeatureInfoResponse)
# Lizenz: BGR-Nutzungsbedingungen (Darstellungsdienst), © BGR Hannover / LfU Bayern
BEISPIEL_BGR_GBL_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<FeatureInfoResponse xmlns:esri_wms="http://www.esri.com/wms" xmlns="http://www.esri.com/wms">
  <FIELDS OBJECTID="588010"
          gml_ID="BIS-BY_7835BG000657"
          shortName="7835BG000657"
          fullName="7835BG000657"
          totalLength="6"
          boreholeWebLink="Null"
          databaseSource="BIS-BY"
          layerDataLegalAvail="KE"
          layerDataTechAvail="J"
          SGD="by"
          point="POINT (691496.631 5335507.964)"
          surfaceLevel="516,2"
          layerData="1"
          drillingDate="Null" />
  <FIELDS OBJECTID="606841"
          gml_ID="BIS-BY_7835BG010373"
          shortName="7835BG010373"
          fullName="7835BG010373"
          totalLength="15,8"
          boreholeWebLink="Null"
          databaseSource="BIS-BY"
          layerDataLegalAvail="KE"
          layerDataTechAvail="J"
          SGD="by"
          point="POINT (691525.039 5335498.064)"
          surfaceLevel="516,74"
          layerData="1"
          drillingDate="02.10.1981" />
  <FIELDS OBJECTID="999999"
          gml_ID="BIS-BY_WEIT_WEG"
          shortName="WEIT_WEG"
          totalLength="10,0"
          boreholeWebLink="Null"
          SGD="by"
          point="POINT (695000.0 5339000.0)"
          surfaceLevel="520,0"
          layerData="0"
          drillingDate="Null" />
</FeatureInfoResponse>
"""

# Anonymisierte Beispielantwort: Bremen WMS 1.1.1 (INFO_FORMAT=application/vnd.ogc.gml)
# Lizenz: CC BY 4.0, © Freie Hansestadt Bremen, GeoInformation Bremen / GDfB
BEISPIEL_BREMEN_GML = b"""<?xml version='1.0' encoding='UTF-8'?>
<FeatureCollection xmlns="http://www.opengis.net/wfs"
                   xmlns:gml="http://www.opengis.net/gml">
  <gml:featureMember>
    <Bohrungen0bis10m xmlns="http://qgis.org/gml" fid="Bohrungen 0 bis 10 m.47123">
      <id>47123</id>
      <akbez>2918_05_1594</akbez>
      <shortname>2918_05_1594</shortname>
      <longname>2918_05_1594</longname>
      <bid>2918GE0150</bid>
      <bohrung_von>2005-02-23</bohrung_von>
      <bohrung_bis>2005-02-23</bohrung_bis>
      <hoehe_bohransatz>2.95</hoehe_bohransatz>
      <endtiefe>5</endtiefe>
      <x_4647>32487461.0</x_4647>
      <y_4647>5882434.0</y_4647>
      <ksys>4647</ksys>
      <hsys>NN</hsys>
      <bohrprofil_pdf_url>https://gdfbgis.marum.de/download?shortname=2918_05_1594&amp;format=pdf</bohrprofil_pdf_url>
    </Bohrungen0bis10m>
  </gml:featureMember>
</FeatureCollection>
"""

BEISPIEL_EXCEPTION_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<ServiceExceptionReport version="1.3.0" xmlns="http://www.opengis.net/ogc">
  <ServiceException code="InvalidFormat">Parameter InfoFormat ungueltig.</ServiceException>
</ServiceExceptionReport>
"""


def test_url_wms_version_130_und_111():
    d_bgr = next(d for d in bohrdaten_wms.WMS_DIENSTE if d["id"] == "de-bgr-gbl-wms")
    url_130 = bohrdaten_wms._url_wms(d_bgr, "0", 691500.0, 5335500.0, 25832, 250.0)
    assert "VERSION=1.3.0" in url_130
    assert "CRS=EPSG:25832" in url_130
    assert "I=2" in url_130 and "J=2" in url_130 and "WIDTH=5" in url_130   # Mittelpixel deckt den Umkreis
    assert "INFO_FORMAT=text/xml" in url_130

    d_hb = next(d for d in bohrdaten_wms.WMS_DIENSTE if d["id"] == "hb-bohrungen-wms")
    url_111 = bohrdaten_wms._url_wms(d_hb, "Bohrpunkte_Bremen", 487461.0, 5882434.0, 25832, 250.0)
    assert "VERSION=1.1.1" in url_111
    assert "SRS=EPSG:25832" in url_111
    assert "X=2" in url_111 and "Y=2" in url_111
    assert "INFO_FORMAT=application/vnd.ogc.gml" in url_111


def test_wms_kopfdaten_bgr_gbl_esri_xml():
    d_bgr = next(d for d in bohrdaten_wms.WMS_DIENSTE if d["id"] == "de-bgr-gbl-wms")
    heute = date(2026, 11, 6)
    treffer = bohrdaten_wms.wms_kopfdaten(d_bgr, BEISPIEL_BGR_GBL_XML, epsg=25832, heute=heute)
    assert len(treffer) == 3

    t0 = treffer[0]
    assert t0["id"] == "BIS-BY_7835BG000657"
    assert t0["name"] == "7835BG000657"
    assert t0["x"] == pytest.approx(691496.63)
    assert t0["y"] == pytest.approx(5335507.96)
    assert t0["gok"] == pytest.approx(516.2)
    assert t0["teufe"] == pytest.approx(6.0)
    assert t0["datum"] is None
    assert t0["schichten"] == "portal"
    assert t0["herkunft"]["quelle"] == "SGD"
    assert t0["herkunft"]["methode"] == "WMS-GetFeatureInfo"
    assert t0["herkunft"]["sgd"] == "by"
    assert t0["herkunft"]["abgerufen"] == "2026-11-06"
    assert "2026" in t0["herkunft"]["namensnennung"]

    t1 = treffer[1]
    assert t1["gok"] == pytest.approx(516.74)
    assert t1["teufe"] == pytest.approx(15.8)
    assert t1["datum"] == "1981-10-02"


def test_wms_kopfdaten_bremen_gml_und_epsg4647_umrechnung():
    d_hb = next(d for d in bohrdaten_wms.WMS_DIENSTE if d["id"] == "hb-bohrungen-wms")
    heute = date(2026, 11, 6)
    treffer = bohrdaten_wms.wms_kopfdaten(d_hb, BEISPIEL_BREMEN_GML, epsg=25832, heute=heute)
    assert len(treffer) == 1

    t = treffer[0]
    assert t["id"] == "2918_05_1594"
    assert t["name"] == "2918_05_1594"
    # EPSG:4647 (32487461.0) -> EPSG:25832 (487461.0) durch Streifen der Zonenkennzahl 32
    assert t["x"] == pytest.approx(487461.0)
    assert t["y"] == pytest.approx(5882434.0)
    assert t["gok"] == pytest.approx(2.95)
    assert t["teufe"] == pytest.approx(5.0)
    assert t["datum"] == "2005-02-23"
    assert t["schichten"] == "grafik"
    assert t["profil"] == "https://gdfbgis.marum.de/download?shortname=2918_05_1594&format=pdf"
    assert t["herkunft"]["lizenz"] == "CC BY 4.0"


def test_abfragen_wms_filtert_radius_und_passt_zu_doppelte():
    heute = date(2026, 11, 6)
    # Punkt in Muenchen (Bayern): nur de-bgr-gbl-wms ist dort zustaendig
    erg = bohrdaten_wms.abfragen_wms(
        691500.0,
        5335500.0,
        25832,
        radius=100.0,
        holer=lambda url, zeit: BEISPIEL_BGR_GBL_XML,
        heute=heute,
    )
    assert erg["epsg"] == 25832
    assert erg["radius"] == 100.0
    assert erg["dienste"] == ["de-bgr-gbl-wms"]
    assert erg["fehler"] == []
    # Der 3. Treffer (WEIT_WEG) liegt ~5 km entfernt und wird durch radius=100.0 ausgefiltert
    assert [t["id"] for t in erg["treffer"]] == ["BIS-BY_7835BG000657", "BIS-BY_7835BG010373"]
    assert erg["treffer"][0]["abstand"] < erg["treffer"][1]["abstand"]
    assert erg["unvollstaendig"] == []

    # Gegenprobe gegen eine Bohrung des Gutachtens mit bohrdaten.doppelte()
    gutachten_bohrungen = [
        {"id": "B1", "code": "7835BG000657", "x": 691497.0, "y": 5335508.0, "gok": 516.3},
    ]
    gegen = bohrdaten.doppelte(erg["treffer"], gutachten_bohrungen)
    assert gegen["anzahl"] == 1
    assert erg["treffer"][0]["gutachten"] == "7835BG000657"
    assert erg["treffer"][0]["abweichung_gok"] == pytest.approx(0.1)


def test_zu_bohrungen_erfindet_keine_schichten_und_erhaelt_herkunft():
    d_hb = next(d for d in bohrdaten_wms.WMS_DIENSTE if d["id"] == "hb-bohrungen-wms")
    heute = date(2026, 11, 6)
    treffer = bohrdaten_wms.wms_kopfdaten(d_hb, BEISPIEL_BREMEN_GML, epsg=25832, heute=heute)
    doc = bohrdaten_wms.zu_bohrungen(treffer, heute=heute)

    assert len(doc["boreholes"]) == 1
    b = doc["boreholes"][0]
    assert b["code"] == "hb-bohrungen-wms-2918_05_1594"
    assert b["fremd_id"] == "2918_05_1594"
    assert b["x"] == pytest.approx(487461.0)
    assert b["y"] == pytest.approx(5882434.0)
    assert b["gok_nhn"] == pytest.approx(2.95)
    assert b["end_depth"] == pytest.approx(5.0)
    assert b["layers"] == []  # Unverhandelbar: niemals Schichten erfinden
    assert b["herkunft"] == "SGD"
    assert b["quelle"] == "hb-bohrungen-wms"
    assert b["lizenz"] == "CC BY 4.0"
    assert b["abgerufen"] == "2026-11-06"
    assert b["profil_url"] == "https://gdfbgis.marum.de/download?shortname=2918_05_1594&format=pdf"
    assert any("nur Kopfdaten" in hinweis for hinweis in b["issues"])


def test_wms_fehlerbehandlung_bei_service_exception():
    d_bgr = next(d for d in bohrdaten_wms.WMS_DIENSTE if d["id"] == "de-bgr-gbl-wms")
    with pytest.raises(DienstFehler, match="Fehlermeldung des WMS-Dienstes"):
        bohrdaten_wms.wms_kopfdaten(d_bgr, BEISPIEL_EXCEPTION_XML, epsg=25832)

    erg = bohrdaten_wms.abfragen_wms(
        691500.0,
        5335500.0,
        25832,
        holer=lambda url, zeit: BEISPIEL_EXCEPTION_XML,
    )
    assert erg["treffer"] == []
    assert len(erg["fehler"]) == 1
    assert erg["fehler"][0]["dienst"] == "de-bgr-gbl-wms"


def test_abfragen_wms_markiert_eine_gekappte_antwort(monkeypatch):
    # Liefert der Server so viele Treffer wie FEATURE_COUNT, fehlen vielleicht welche: markieren, nie still kappen
    monkeypatch.setattr(bohrdaten_wms, "TREFFER_MAX", 2)
    erg = bohrdaten_wms.abfragen_wms(691500.0, 5335500.0, 25832, radius=100.0,
                                     holer=lambda url, zeit: BEISPIEL_BGR_GBL_XML, heute=date(2026, 11, 6))
    assert erg["unvollstaendig"] == ["de-bgr-gbl-wms"]
