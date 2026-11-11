"""Homogenbereiche in der App (docs/28): Zuordnung je ATV über aendern, IFC-Modell aus Bereichen, Daten der Matrix."""
from __future__ import annotations

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


def test_daten_der_matrix(client):
    d = client.get("/api/homogenbereiche").json()
    assert len(d["atv"]) == 11 and "Abbildung 8" in d["quelle"]
    assert d["matrix"]["DIN 18300"]["19"] == "erforderlich"


def test_zuordnen_und_ifc_aus_homogenbereichen(client):
    import ifcopenshell
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    m = client.post(f"/api/projekt/{sig}/modell").json()
    namen = [e["name"] for e in m["bericht"]["einheiten"]]
    aendern = lambda *ops: client.post(f"/api/projekt/{sig}/aendern", json={"ops": list(ops)})
    r = aendern({"op": "hb_modell", "wert": "DIN 18300"})
    assert r.status_code == 400 and "keine Homogenbereiche" in r.text              # erst zuordnen
    assert aendern({"op": "homogenbereiche", "atv": "DIN 9", "zuordnung": {}}).status_code == 400
    zu = {namen[0]: "B1", namen[1]: "B2", namen[2]: "B2"}
    r = aendern({"op": "homogenbereiche", "atv": "DIN 18300", "zuordnung": zu})
    assert r.status_code == 200 and r.json()["zustand"]["homogenbereiche"] == {"DIN 18300": zu}
    ifc_einheiten = client.post(f"/api/projekt/{sig}/modell").json()["ifc"]
    r = aendern({"op": "hb_modell", "wert": "DIN 18300"})
    assert r.status_code == 200 and r.json()["zustand"]["hb_modell"] == "DIN 18300"
    m2 = client.post(f"/api/projekt/{sig}/modell").json()
    assert m2["schluessel"] == m["schluessel"] and m2["ifc"] != ifc_einheiten   # gleiche Geometrie, anderes IFC
    inhalt = client.get(m2["ifc"]).content
    f = ifcopenshell.file.from_string(inhalt.decode())
    gm = f.by_type("IfcGeomodel")[0]
    namen_ifc = {x.Name for r in gm.IsDecomposedBy for x in r.RelatedObjects}
    assert {"B1", "B2"} <= namen_ifc and f"{namen[3]} (ohne Homogenbereich)" in namen_ifc
    # Zuordnung loeschen: das Modell faellt auf Einheiten zurueck
    r = aendern({"op": "homogenbereiche", "atv": "DIN 18300", "zuordnung": None})
    z = r.json()["zustand"]
    assert z["homogenbereiche"] is None and z["hb_modell"] is None
