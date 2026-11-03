"""BoreholeML in der Schritt-App: Export gepruefter Bohrungen (Modell-Schritt) und Import wie ein Gutachten."""
from __future__ import annotations

import sys
import time
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


def auftrag_abwarten(client, aid: str) -> dict:
    for _ in range(200):
        a = client.get(f"/api/auftrag/{aid}").json()
        if a["fertig"]:
            return a
        time.sleep(0.05)
    raise AssertionError("Auftrag nicht fertig")


def test_export_nur_geprueft_und_import_als_projekt(client):
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    r = client.get(f"/api/projekt/{sig}/export/boreholeml")
    assert r.status_code == 400 and "keine exportierbare Bohrung" in r.json()["detail"]
    client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "alle_pruefen"}]})
    r = client.get(f"/api/projekt/{sig}/export/boreholeml", params={"organisation": "Ingenieurbüro Muster"})
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/xml")
    assert "boreholeml.xml" in r.headers["content-disposition"]
    text = r.content.decode("utf-8")
    assert text.startswith("<?xml") and "GroundTwin: 5 Bohrungen exportiert" in text and "S2a (ohne Koordinaten)" in text
    assert "Ingenieurbüro Muster" in text and text.count("<bml:Borehole ") == 5
    # dieselbe Datei wie ein Gutachten hochladen: Bohrungen mit Herkunft BoreholeML
    a = client.post("/api/gutachten", files={"dateien": ("bohrungen.xml", r.content, "application/xml")},
                    data={"ocr": "false"}).json()
    a = auftrag_abwarten(client, a["id"])
    assert not a["fehler"] and a["projekt"], a
    z = client.get(f"/api/projekt/{a['projekt']}").json()
    assert len(z["bohrungen"]) == 5
    b = z["bohrungen"][0]
    assert b["gok_quelle"] == "BoreholeML" and b["lage_aus"] == "BoreholeML (na)" and b["epsg"] == 25833
    assert b["hinweise"][0].startswith("aus BoreholeML")


def test_kaputte_xml_wird_gemeldet(client):
    a = client.post("/api/gutachten", files={"dateien": ("kaputt.xml", b"<a><b/></a>", "application/xml")},
                    data={"ocr": "false"}).json()
    a = auftrag_abwarten(client, a["id"])
    assert a["fehler"] and "keine BoreholeML-Bohrung" in a["fehler"][0] and not a["projekt"]
