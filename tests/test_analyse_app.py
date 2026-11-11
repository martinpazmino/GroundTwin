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
    vorher = client.get(f"/api/projekt/{sig}").json()

    b = a["bohrungen"][0]
    v = client.post(f"/api/projekt/{sig}/analyse/punkt", json={"x": b["x"] + 6, "y": b["y"] + 3}).json()
    assert v["fehler"] == "" and v["naechste_bohrung"] == b["code"] and v["schichten"]
    assert v["schichten"][0]["sigma_unten_m"] is not None and v["herkunft"].startswith("Modell")
    weit = client.post(f"/api/projekt/{sig}/analyse/punkt", json={"x": b["x"] + 9000, "y": b["y"]}).json()
    assert "außerhalb des Modells" in weit["fehler"]
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
