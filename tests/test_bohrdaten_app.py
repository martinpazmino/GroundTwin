"""Bohrungen der Laender in der Schritt-App: Abfrage nur auf Klick, Gegenprobe mit dem Gutachten, Uebernahme mit
Herkunft, Modell, kein Rueckexport, Zuruecksetzen. Die Dienste sind durch die Attrappe aus test_bohrdaten ersetzt."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "tests")]
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from test_bohrdaten import attrappe, bd  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    monkeypatch.setattr(bd, "_holen", attrappe())
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c


def schicht(oben, unten, klasse, text):
    return {"top_depth": oben, "bottom_depth": unten, "description_raw": text, "soil_class": klasse, "confidence": 0.9,
            "issues": [], "provenance": [{"page": 0, "method": "test"}]}


MARL = {"document": {"file": "marl_test.pdf", "sha256": "0" * 64, "parser_version": "test", "pages": 1},
        "boreholes": [{"code": f"B{i}", "x": 368100.0 + 30 * i, "y": 5724400.0, "crs_epsg": 25832, "gok_nhn": 60.0,
                       "end_depth": 6.0, "layers": [schicht(0, 2, "Sand", "Sand, schwach schluffig"),
                                                    schicht(2, 6, "Schluff", "Schluff, tonig")],
                       "groundwater": [], "issues": [], "provenance": [{"page": 0}]} for i in (1, 2)],
        "soundings": {}}


def test_berlin_gegenprobe_und_nur_kopfdaten(client):
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    assert client.get(f"/api/projekt/{sig}").json()["sgd"] is None                 # nichts ohne Klick
    z = client.post(f"/api/projekt/{sig}/sgd/abfrage", json={"radius": 250}).json()
    s = z["sgd"]
    assert [t["name"] for t in s["treffer"]] == ["999X-1", "422C-460"] and {f["dienst"] for f in s["fehler"]} == {"BB"}
    t = s["treffer"][1]
    assert t["gutachten"] == "422C-460" and not t["uebernehmbar"] and s["gegenprobe"]["anzahl"] == 1
    r = client.post(f"/api/projekt/{sig}/sgd/uebernehmen", json={"auswahl": [{"dienst": "BE", "id": t["id"]}]})
    assert r.status_code == 400 and "nur Kopfdaten" in r.json()["detail"]
    z = client.delete(f"/api/projekt/{sig}/sgd").json()
    assert z["sgd"] is None


def test_nrw_uebernehmen_modellieren_kein_rueckexport_zuruecksetzen(client):
    sig = client.app.state.arbeitsplatz.anlegen([MARL])
    s = client.post(f"/api/projekt/{sig}/sgd/abfrage", json={"radius": 250}).json()["sgd"]
    assert [(t["name"], t["uebernehmbar"]) for t in s["treffer"]] == [("2", True), ("1", True)]   # nach Abstand zur Mitte
    r = client.post(f"/api/projekt/{sig}/sgd/uebernehmen", json={"auswahl": [{"dienst": "NW", "id": "DABO_1"}]}).json()
    assert r["meldungen"] == ["1 Bohrungen der Länder übernommen (NW-1)"]
    z = r["zustand"]
    b = next(x for x in z["bohrungen"] if x["code"] == "NW-1")
    assert b["hinweise"][0].startswith("aus Bohrpunkte boreholeML Full (Nordrhein-Westfalen), ID DABO_1")
    assert b["lage_aus"] == "SGD Nordrhein-Westfalen" and b["gok_quelle"] == "BoreholeML" and b["id"] == "1:0"
    assert next(n for n in z["viewer"]["bohrungen"] if n["code"] == "NW-1")["herkunft"] == "SGD"
    assert {t["name"]: t["uebernommen"] for t in z["sgd"]["treffer"]} == {"1": True, "2": False}
    nochmal = client.post(f"/api/projekt/{sig}/sgd/uebernehmen", json={"auswahl": [{"dienst": "NW", "id": "DABO_1"}]})
    assert nochmal.status_code == 400 and "schon im Projekt" in nochmal.json()["detail"]
    m = client.post(f"/api/projekt/{sig}/modell").json()
    assert not m["fehler"] and "NW-1" in {x["code"] for x in m["bericht"]["bohrungen"]}
    # die Bohrung des Landes geht nicht als Gutachten-Bohrung zurueck an den Dienst
    client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "alle_pruefen"}]})
    text = client.get(f"/api/projekt/{sig}/export/boreholeml").content.decode("utf-8")
    assert "GroundTwin: 2 Bohrungen exportiert (B1, B2)" in text and "NW-1 (aus dem Bestand des Landes" in text
    # neu geladen (Server-Neustart) bleibt die Uebernahme; Zuruecksetzen nimmt sie heraus
    client.app.state.arbeitsplatz._projekte.clear()
    assert len(client.get(f"/api/projekt/{sig}").json()["bohrungen"]) == 3
    z = client.post(f"/api/projekt/{sig}/zuruecksetzen").json()
    assert len(z["bohrungen"]) == 2 and z["sgd"] is None


def test_ohne_koordinaten_keine_abfrage(client):
    sig = client.post("/api/beispiel", json={"name": "talheim"}).json()["projekt"]
    r = client.post(f"/api/projekt/{sig}/sgd/abfrage", json={})
    assert r.status_code == 400 and "Koordinaten" in r.json()["detail"]
