"""Ground Analysis in der App (docs/27, Phase G2): Kreuzprobe und Unsicherheit zum Modell, virtuelle Bohrung."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c


def test_analyse_zum_modell_und_virtuelle_bohrung(client):
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    a = client.post(f"/api/projekt/{sig}/analyse", json={"laeufe": 20}).json()
    assert a["fehler"] == "" and a["kreuzprobe"]["bohrungen"] == 12
    assert set(a["kreuzprobe"]["methoden"]) == {"idw", "tps"} and a["kreuzprobe"]["beste"] == "tps"
    assert a["unsicherheit"]["laeufe"] == 20 and len(a["unsicherheit"]["einheiten"]) >= 5
    assert "_sigma" not in json.dumps(a) and a["sigma_max_m"] > 0
    assert len(a["bohrungen"]) == 12 and len(a["mitte"]) == 2
    assert 1 <= len(a["vorschlaege"]) <= 3 and all(v["grund"] and v["abstand_naechste_bohrung_m"] > 0 for v in a["vorschlaege"])
    vorher = client.get(f"/api/projekt/{sig}").json()

    b = a["bohrungen"][0]
    v = client.post(f"/api/projekt/{sig}/analyse/punkt", json={"x": b["x"] + 6, "y": b["y"] + 3}).json()
    assert v["fehler"] == "" and v["naechste_bohrung"] == b["code"] and v["schichten"]
    assert v["schichten"][0]["sigma_unten_m"] is not None and v["herkunft"].startswith("Modell")
    weit = client.post(f"/api/projekt/{sig}/analyse/punkt", json={"x": b["x"] + 9000, "y": b["y"]}).json()
    assert "außerhalb des Modells" in weit["fehler"]
    f = client.get(f"/api/projekt/{sig}/analyse/flaeche/0").json()
    assert f["fehler"] == "" and f["name"] == a["unsicherheit"]["einheiten"][0]["name"]
    assert len(f["punkte"]) == len(f["sigma"]) and max(max(d) for d in f["dreiecke"]) < len(f["punkte"])
    assert f["sigma_max"] > 0 and len(f["punkte"][0]) == 3
    assert client.get(f"/api/projekt/{sig}/analyse/flaeche/99").json()["fehler"]
    nachher = client.get(f"/api/projekt/{sig}").json()
    assert nachher["bohrungen"] == vorher["bohrungen"]                         # die Analyse aendert nichts


def test_analyse_ohne_modell_oder_mit_zu_wenig_bohrungen(client):
    sig = client.post("/api/standort", json={"x": 600000.0, "y": 5800000.0, "epsg": 25832, "name": "leer"}).json()["projekt"]
    a = client.post(f"/api/projekt/{sig}/analyse", json={}).json()
    assert a["fehler"] and "Bohrung" in a["fehler"]
    v = client.post(f"/api/projekt/{sig}/analyse/punkt", json={"x": 600000.0, "y": 5800000.0}).json()
    assert v["fehler"]


def test_interpolation_implizit_ueber_die_app(client):
    """docs/27 G3: mit GemPy ist "implizit" wählbar, das Modell bleibt exakt und nennt die Orientierung je Einheit."""
    info = client.get("/api/info").json()
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    r = client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "einstellungen", "methode": "implizit"}]})
    assert r.status_code == 200, r.text
    m = client.post(f"/api/projekt/{sig}/modell").json()
    if not info["implizit"]:                                     # ohne GemPy: klare Meldung statt Modell
        assert "GemPy" in m["fehler"]
        return
    assert m["fehler"] == "" and m["bericht"]["parameter"]["methode"] == "implizit"
    assert m["bericht"]["pruefungen"]["max_abweichung_an_bohrungen_m"] <= 0.05
    assert m["bericht"]["pruefungen"]["alle_koerper_geschlossen"]
    assert len(m["bericht"]["parameter"]["orientierung"]) == len(m["bericht"]["einheiten"])
    falsch = client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "einstellungen", "methode": "kriging"}]})
    assert falsch.status_code == 400 and "implizit" in falsch.text


def test_orientierung_eingeben_ueber_die_app(client):
    """docs/27 G4: Fallrichtung und Fallwinkel je Einheit; geprüft beim Ändern, im Bericht als Quelle "Eingabe"."""
    info = client.get("/api/info").json()
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    aendern = lambda o: client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "einstellungen", **o}]})
    for falsch, text in (({"X": {"fallrichtung": 10, "fallwinkel": 85}}, "0–80"),
                         ({"X": {"fallrichtung": 400, "fallwinkel": 5}}, "0–360"),
                         ({"X": {"fallrichtung": 10}}, "Fallrichtung und Fallwinkel")):
        r = aendern({"orientierung": falsch})
        assert r.status_code == 400 and text in r.text, r.text
    leer = aendern({"orientierung": {"X": {"fallrichtung": "", "fallwinkel": None}}})
    assert leer.status_code == 200 and leer.json()["zustand"]["einstellungen"]["orientierung"] is None
    if not info["implizit"]:
        return
    aendern({"methode": "implizit"})
    erste = client.post(f"/api/projekt/{sig}/modell").json()["bericht"]["einheiten"][0]["name"]
    r = aendern({"orientierung": {erste: {"fallrichtung": 450, "fallwinkel": 0}}})
    assert r.status_code == 400                                  # 450 liegt nicht in 0–360
    r = aendern({"orientierung": {erste: {"fallrichtung": 90, "fallwinkel": 10}}})
    assert r.status_code == 200, r.text
    m = client.post(f"/api/projekt/{sig}/modell").json()
    o = {e["einheit"]: e for e in m["bericht"]["parameter"]["orientierung"]}
    assert o[erste]["quelle"] == "Eingabe" and o[erste]["fallen_grad"] == 10 and o[erste]["fallrichtung_grad"] == 90
    assert m["bericht"]["pruefungen"]["max_abweichung_an_bohrungen_m"] <= 0.05      # an den Bohrungen exakt


def test_grundwasserflaeche_ueber_die_app(client):
    """docs/27 G5: Berlin (echte Daten, zwei gemessene Stände) gibt eine Fläche durch beide Stände; die Demo ohne
    Wasserstände sagt es, statt eine Fläche zu erfinden."""
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    g = client.get(f"/api/projekt/{sig}/analyse/grundwasser").json()
    assert g["fehler"] == "" and g["gemessen"] == 2 and g["flaeche"]["name"] == "Grundwasser"
    z = {s["code"]: s.get("z") for s in g["staende"]}
    assert z["422C-460"] == 32.45 and z["422C-461"] == 32.65
    assert 32.4 <= g["flaeche"]["z_min"] <= g["flaeche"]["z_max"] <= 32.7       # zwischen den Ständen, kein Überschwingen
    assert len(g["flaeche"]["punkte"]) > 3 and g["kreuzprobe"] is None              # unter vier Ständen keine Kreuzprobe
    assert any("kein Bemessungswasserstand" in h for h in g["hinweise"])
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    g = client.get(f"/api/projekt/{sig}/analyse/grundwasser").json()
    assert g["fehler"] == "" and g["flaeche"] is None and "keine Bohrung" in g["hinweise"][0]
