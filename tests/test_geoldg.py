"""Hilfe zum Geologiedatengesetz (services/geodaten/geodaten/geoldg.py, docs/21 §5.3, D96, Phase P6).

Fristen nach §§ 8-10 GeolDG, Pruefliste je Bohrung (was die App liefert, was aus dem Bohrprotokoll kommt) und das
Paket fuer den Geologischen Dienst (BoreholeML, IFC, Pruefbericht, Modelldokumentation, Pruefliste).
"""
from __future__ import annotations

import csv
import io
import json
import sys
import zipfile
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "services" / "geodaten")]
from geodaten import boreholeml, geoldg  # noqa: E402

HEUTE = date(2026, 11, 4)


def schicht(oben: float, unten: float, geprueft: bool = True) -> dict:
    return {"top_depth": oben, "bottom_depth": unten, "description_raw": "Sand, mittelsandig", "soil_class": "Sand",
            "geprueft": geprueft}


def bohrung(**kw) -> dict:
    b = {"code": "BK1", "kind": "kernbohrung", "x": 368130.0, "y": 5724400.0, "crs_epsg": 25832, "coord_source": "tabelle",
         "gok_nhn": 60.5, "end_depth": 6.0, "layers": [schicht(0.0, 2.0), schicht(2.0, 6.0)]}
    b.update(kw)
    return b


# ---------------------------------------------------------------- Fristen
@pytest.mark.parametrize("von, monate, bis", [(date(2026, 1, 15), 3, date(2026, 4, 15)),
                                              (date(2026, 11, 30), 3, date(2027, 2, 28)),    # Monatsende (§ 188 BGB)
                                              (date(2027, 11, 30), 3, date(2028, 2, 29)),    # Schaltjahr
                                              (date(2026, 5, 31), 6, date(2026, 11, 30)),
                                              (date(2026, 10, 31), 3, date(2027, 1, 31))])
def test_monatsfrist(von, monate, bis):
    assert geoldg.plus_monate(von, monate) == bis


def test_fristen_aus_beginn_und_abschluss():
    ohne = {f["id"]: f for f in geoldg.fristen({}, HEUTE)}
    assert set(ohne) == {"anzeige", "fachdaten", "bewertungsdaten"} and all(f["bis"] is None for f in ohne.values())
    assert ohne["anzeige"]["beleg"] == "§ 8 Satz 1" and ohne["fachdaten"]["beleg"] == "§ 9 Abs. 1 Satz 1"
    assert ohne["bewertungsdaten"]["regel"] == "auf Verlangen der zuständigen Behörde"
    f = {f["id"]: f for f in geoldg.fristen({"beginn": "2026-09-01", "abschluss": "2026-09-30"}, HEUTE)}
    assert f["anzeige"]["bis"] == "2026-08-18" and f["anzeige"]["tage"] < 0               # zwei Wochen vor Beginn
    assert f["fachdaten"]["bis"] == "2026-12-30" and f["fachdaten"]["tage"] == 56          # drei Monate nach Abschluss
    assert f["bewertungsdaten"]["bis"] is None                                            # nur auf Verlangen
    b = {f["id"]: f for f in geoldg.fristen({"abschluss": "2026-09-30", "behoerde": True}, HEUTE)}
    assert b["bewertungsdaten"]["bis"] == "2027-03-30" and b["bewertungsdaten"]["beleg"] == "§ 10 Abs. 2 Satz 2"
    assert b["anzeige"]["bis"] is None and b["fachdaten"]["bis"] == "2026-12-30"
    assert geoldg.fristen({"abschluss": "2026-11-04"}, date(2027, 2, 4))[1]["tage"] == 0
    assert "verstrichen" in geoldg.frist_text(f["anzeige"]) and "noch 56 Tage" in geoldg.frist_text(f["fachdaten"])
    assert "Abschluss eintragen" in geoldg.frist_text(ohne["fachdaten"])


@pytest.mark.parametrize("angaben, meldung", [({"beginn": "4.11.2026"}, "JJJJ-MM-TT"),
                                              ({"beginn": "2026-10-01", "abschluss": "2026-09-30"}, "vor ihrem Beginn")])
def test_angaben_werden_geprueft(angaben, meldung):
    with pytest.raises(ValueError, match=meldung):
        geoldg.angaben_pruefen(angaben)


# ---------------------------------------------------------------- je Bohrung
def test_bohrung_aus_dem_gutachten_vollstaendig():
    e = geoldg.bohrung(bohrung())
    assert e["bereit"] and e["boreholeml"] == "" and e["art"] == ""
    p = e["punkte"]
    assert p["lage"] == ["ok", "368130,00 / 5724400,00 (EPSG:25832), aus dem Gutachten"]
    assert p["ansatzhoehe"] == ["ok", "60,50 m NHN, aus dem Gutachten"] and p["endteufe"] == ["ok", "6,00 m u. GOK"]
    assert p["schichtenverzeichnis"] == ["ok", "2 Schichten, geprüft"]
    assert p["verlauf"][0] == "markiert" and "lotrecht angenommen" in p["verlauf"][1]       # angenommen, markiert
    # was die App nicht liest, steht nicht je Bohrung, sondern einmal als Punkt aus dem Bohrprotokoll
    assert set(p) == {k for k, r in geoldg.PUNKTE.items() if r["quelle"] == "app"}


@pytest.mark.parametrize("aenderung, punkt, status, text", [
    ({"coord_source": "Plan (kalibriert)"}, "lage", "markiert", "aus dem kalibrierten Plan abgegriffen"),
    ({"coord_source": "manuell (Viewer)"}, "lage", "markiert", "im Viewer gesetzt"),
    ({"x": None}, "lage", "offen", "ohne Koordinaten"),
    ({"crs_epsg": None}, "lage", "offen", "ohne Koordinatensystem"),
    ({"gok_nhn": None}, "ansatzhoehe", "offen", "ohne GOK"),
    ({"gok_nhn": 0.0, "gok_source": "relativ"}, "ansatzhoehe", "offen", "nur relativ"),
    ({"gok_source": "DGM"}, "ansatzhoehe", "markiert", "aus dem DGM übernommen, nicht gemessen"),
    ({"gok_source": "manuell"}, "ansatzhoehe", "markiert", "manuell eingetragen"),
    ({"layers": [schicht(0.0, 2.0), schicht(2.0, 6.0, False)]}, "schichtenverzeichnis", "offen", "1/2 Schichten geprüft"),
    ({"layers": [], "end_depth": None}, "schichtenverzeichnis", "offen", "keine Schichten"),
])
def test_bohrung_markiert_und_offen(aenderung, punkt, status, text):
    b = bohrung(**aenderung)
    e = geoldg.bohrung(b)
    assert e["punkte"][punkt][0] == status and text in e["punkte"][punkt][1]
    assert e["bereit"] == (status != "offen")                    # markiert ist vorhanden (nicht aus dem PDF)
    assert e["boreholeml"] == boreholeml.exportierbar(b)          # dieselbe Regel wie der BoreholeML-Export


def test_bohrung_in_der_reihe_und_kuerzel():
    e = geoldg.bohrung(bohrung(x=20.0, y=0.0, crs_epsg=None, coord_source="schematisch"), reihe=True)
    assert e["punkte"]["lage"][0] == "offen" and "Längsschnitt" in e["punkte"]["lage"][1] and not e["bereit"]
    assert e["boreholeml"] == "nur Lage nach Koordinaten"
    assert "Ausbau" in geoldg.bohrung(bohrung(code="GWM 1", kind="gwm"))["art"]
    assert "Schurf" in geoldg.bohrung(bohrung(code="SCH 2", kind="schurf"))["art"]
    assert "Kleinbohrung" in geoldg.bohrung(bohrung(code="RKS 3", kind="rks"))["art"]


def test_uebersicht_bohrungen_der_laender_sondierungen_vorerkundung():
    eigene = [bohrung(), bohrung(code="BK2", gok_nhn=None)]
    fremd = bohrung(code="NW-1", herkunft="SGD")
    u = geoldg.pruefen(eigene + [fremd], {"abschluss": "2026-09-30"}, heute=HEUTE, sondierungen=2)
    z = u["zusammenfassung"]
    assert (z["eigene"], z["bereit"], z["boreholeml"], z["fremd"]) == (2, 1, 1, 1)
    assert z["offen"] == [{"code": "BK2", "was": "Ansatzhöhe (GOK): ohne GOK"}]
    assert u["fremd"] == [{"code": "NW-1", "herkunft": "SGD"}] and not u["vorerkundung"]
    assert u["hinweise"][0]["beleg"] == "§ 3 Abs. 3 Nr. 2" and "2 Sondierungen" in u["hinweise"][0]["text"]
    assert u["angaben"] == {"beginn": "", "abschluss": "2026-09-30", "behoerde": False}
    v = geoldg.pruefen([fremd], heute=HEUTE, standort=True)
    assert v["vorerkundung"] and v["zusammenfassung"]["eigene"] == 0
    # jede Regel mit Beleg im Gesetzestext
    for r in u["fristen"] + u["hinweise"] + [u["abschluss"], u["anzeige_inhalt"]]:
        assert r["beleg"].startswith("§") and r["url"].startswith("https://www.gesetze-im-internet.de/geoldg/__")
    assert all(p["beleg"].startswith("§") for p in u["punkte"])


def test_pruefliste_csv_und_dateiname():
    u = geoldg.pruefen([bohrung(), bohrung(code="BK2", coord_source="Plan (kalibriert)")], heute=HEUTE)
    text = geoldg.tabelle(u).decode("utf-8")
    assert text.startswith("﻿")                                     # Excel erkennt UTF-8
    zeilen = list(csv.reader(io.StringIO(text[1:]), delimiter=";"))
    assert len(zeilen) == 3 and zeilen[0][0] == "Bohrung" and zeilen[0][-2:] == ["Bohrdatum", "BoreholeML"]
    spalten = {k: i for i, k in enumerate(zeilen[0])}
    lage = next(k for k in spalten if k.startswith("Lage der Bohrung (§ 9"))
    verfahren = next(k for k in spalten if k.startswith("Bohrverfahren"))
    assert zeilen[1][spalten[lage]].startswith("✓ 368130,00") and zeilen[2][spalten[lage]].startswith("⚑ ")
    assert zeilen[1][spalten[verfahren]] == "" and zeilen[1][-1] == "ja"   # aus dem Bohrprotokoll: leer zum Ergaenzen
    assert geoldg.dateiname("Standort 368130 / 5724400 (EPSG:25832)") == "Standort 368130 _ 5724400 (EPSG_25832)"
    assert geoldg.dateiname(" .. ") == "baugrundmodell"


# ---------------------------------------------------------------- in der App
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c


def paket(client, sig: str, **params) -> zipfile.ZipFile:
    r = client.get(f"/api/projekt/{sig}/export/geoldg", params=params)
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/zip" and "_geoldg.zip" in r.headers["content-disposition"]
    return zipfile.ZipFile(io.BytesIO(r.content))


def test_app_fristen_im_projekt_und_falsche_eingaben(client, tmp_path):
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    g = client.get(f"/api/projekt/{sig}").json()["geoldg"]
    assert g["zusammenfassung"]["eigene"] == 6 and g["zusammenfassung"]["bereit"] == 0      # noch nichts geprueft
    assert {o["code"] for o in g["zusammenfassung"]["offen"]} >= {"422C-460", "S2a"}
    r = client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "geoldg", "beginn": "2026-05-04",
                                                                  "abschluss": "2026-06-30", "behoerde": True}]})
    assert r.status_code == 200 and r.json()["meldungen"] == ["Angaben zur Untersuchung übernommen"]
    f = {f["id"]: f for f in r.json()["zustand"]["geoldg"]["fristen"]}
    assert (f["anzeige"]["bis"], f["fachdaten"]["bis"], f["bewertungsdaten"]["bis"]) == ("2026-04-20", "2026-09-30", "2026-12-30")
    for falsch in ({"abschluss": "2026-05-01"}, {"beginn": "gestern"}):            # vor dem Beginn, kein Datum
        r = client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "geoldg", **falsch}]})
        assert r.status_code == 400
    assert client.get(f"/api/projekt/{sig}").json()["geoldg"]["angaben"] == {
        "beginn": "2026-05-04", "abschluss": "2026-06-30", "behoerde": True}
    # bleibt im Projekt (neuer Server liest denselben Ordner)
    with TestClient(app_erstellen(tmp_path)) as c2:
        assert c2.get(f"/api/projekt/{sig}").json()["geoldg"]["angaben"]["abschluss"] == "2026-06-30"
    client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "geoldg", "beginn": "", "behoerde": False}]})
    a = client.get(f"/api/projekt/{sig}").json()["geoldg"]["angaben"]
    assert a == {"beginn": "", "abschluss": "2026-06-30", "behoerde": False}


def test_app_paket_fach_und_bewertungsdaten(client):
    import ifcopenshell
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "alle_pruefen"},
                                                             {"op": "geoldg", "abschluss": "2026-09-30"}]})
    z = paket(client, sig, organisation="Ingenieurbüro Muster")
    stamm = client.get(f"/api/projekt/{sig}").json()["name"]
    assert sorted(z.namelist()) == sorted([
        "LIESMICH.txt", "pruefliste.csv", "pruefliste.json", f"fachdaten_GeolDG_9/{stamm}_boreholeml.xml",
        f"bewertungsdaten_GeolDG_10/{stamm}.ifc", f"bewertungsdaten_GeolDG_10/{stamm}_pruefbericht.json",
        "bewertungsdaten_GeolDG_10/modelldokumentation.txt"])
    # Fachdaten: die fuenf Bohrungen mit Koordinaten im BoreholeML, S2a (ohne Lage) nicht
    xml = z.read(f"fachdaten_GeolDG_9/{stamm}_boreholeml.xml").decode("utf-8")
    assert xml.count("<bml:Borehole ") == 5 and "Ingenieurbüro Muster" in xml and "S2a" in xml.split("-->")[0]
    # Bewertungsdaten: IFC, Pruefbericht und Dokumentation des Modells
    pfad = Path(client.app.state.arbeitsplatz.arbeit) / "geoldg.ifc"
    pfad.write_bytes(z.read(f"bewertungsdaten_GeolDG_10/{stamm}.ifc"))
    assert len(ifcopenshell.open(str(pfad)).by_type("IfcGeotechnicalStratum")) > 0
    bericht = json.loads(z.read(f"bewertungsdaten_GeolDG_10/{stamm}_pruefbericht.json"))
    assert bericht["epsg"] == 25833 and len(bericht["bohrungen"]) == 5
    doku = z.read("bewertungsdaten_GeolDG_10/modelldokumentation.txt").decode("utf-8")
    assert "EPSG:25833" in doku and "interpoliert" in doku and "422C-460: 394774,30 / 5818338,10" in doku
    assert "Lage aus dem Gutachten (Text)" in doku and "lotrecht angenommen" in doku and "S2a" in doku
    # LIESMICH: Fristen mit Datum, Inhalt mit Kennzeichnung (§ 17), offene Bohrung, Hinweise mit Beleg
    text = z.read("LIESMICH.txt").decode("utf-8")
    assert "spätestens drei Monate nach Abschluss (§ 9 Abs. 1 Satz 1) – bis 30.12.2026" in text
    assert "Kennzeichnung nach § 17 Abs. 1 Nr. 2" in text and "Kennzeichnung nach § 17 Abs. 1 Nr. 3" in text
    assert "offen: S2a – Lage der Bohrung: ohne Koordinaten" in text and "keine Rechtsberatung" in text
    assert "https://www.gesetze-im-internet.de/geoldg/__14.html" in text
    u = json.loads(z.read("pruefliste.json"))
    assert u["zusammenfassung"]["bereit"] == 5 and u["zusammenfassung"]["boreholeml"] == 5
    assert len(z.read("pruefliste.csv").decode("utf-8-sig").strip().splitlines()) == 7       # Kopf + 6 Bohrungen


def test_app_paket_sagt_was_fehlt(client):
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    text = paket(client, sig).read("LIESMICH.txt").decode("utf-8")                 # nichts geprueft: kein BoreholeML
    teil = text.split("NICHT IM PAKET")[1].split("BOHRUNGEN")[0]
    assert "BoreholeML (Fachdaten): keine exportierbare Bohrung (6 × nicht vollständig geprüft; je Bohrung in pruefliste.csv)" in teil
    assert "das Gutachten selbst" in teil
    # Talheim (ohne Koordinaten, Reihe): Lage offen, Modell schematisch
    sig = client.post("/api/beispiel", json={"name": "talheim"}).json()["projekt"]
    g = client.get(f"/api/projekt/{sig}").json()["geoldg"]
    assert g["bohrungen"] and all(e["punkte"]["lage"][0] == "offen" and e["boreholeml"] == "nur Lage nach Koordinaten"
                                  for e in g["bohrungen"])
    assert "BoreholeML (Fachdaten)" in paket(client, sig).read("LIESMICH.txt").decode("utf-8")


def test_app_standort_ohne_eigene_bohrung(client):
    r = client.post("/api/standort", json={"x": 368130.0, "y": 5724400.0, "epsg": 25832, "name": "Marl Nord"})
    g = client.get(f"/api/projekt/{r.json()['projekt']}").json()["geoldg"]
    assert g["vorerkundung"] and g["zusammenfassung"]["eigene"] == 0 and g["bohrungen"] == []
    assert "Prognose der Schichten" in g["anzeige_inhalt"]["aus_der_app"]
    # kein Paket: ein Modell nur aus Bohrungen der Laender ist keine Bewertung dieser Untersuchung
    r = client.get(f"/api/projekt/{r.json()['projekt']}/export/geoldg")
    assert r.status_code == 400 and "keine eigene Bohrung" in r.json()["detail"]
