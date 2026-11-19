"""Bodenkennwerte aus dem Gutachten in der App (Issue #18): Zeilen und Vorschlag, Zuordnung je Einheit, IFC-Pset."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
pytest.importorskip("fastapi")
import ifcopenshell  # noqa: E402
import ifcopenshell.util.element as ue  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c, tmp_path


def test_kennwerte_talheim_zuordnen_und_ifc(client):
    c, arbeit = client
    sig = c.post("/api/beispiel", json={"name": "talheim"}).json()["projekt"]
    k = c.get(f"/api/projekt/{sig}/bodenkennwerte").json()
    assert k["fehler"] == "" and len(k["zeilen"]) == 5 and k["einheiten"]
    erste = k["zeilen"][0]
    assert erste["seite"] == 5 and erste["werte"]["reibungswinkel"]["min"] == 25.0
    assert set(k["vorschlag"]) == set(k["einheiten"])                     # je Einheit ein Vorschlag oder ein Grund
    e = k["einheiten"][0]
    z = c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "bodenkennwerte",
                                                               "zuordnung": {e: erste["ref"], "gibtsnicht": "x#1"}}]})
    assert z.status_code == 200
    k2 = c.get(f"/api/projekt/{sig}/bodenkennwerte").json()
    assert k2["zuordnung"] == {e: erste["ref"]}                          # unbekannter Verweis faellt weg
    m = c.post(f"/api/projekt/{sig}/modell").json()
    f = ifcopenshell.open(str(arbeit / "web" / m["ifc"].lstrip("/").removeprefix("dateien/")))
    gm = f.by_type("IfcGeomodel")[0]
    ps = {x.Name: ue.get_psets(x) for r in gm.IsDecomposedBy for x in r.RelatedObjects}[e]["CPset_Bodenkennwerte_Gutachten"]
    assert ps["Reibungswinkel_min"] == 25.0 and ps["Quelle"] == "talheim.pdf, Seite 6"


def test_ohne_kennwerte_leer(client):
    c, _ = client
    sig = c.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    k = c.get(f"/api/projekt/{sig}/bodenkennwerte").json()
    assert k["fehler"] == "" and k["zeilen"] == [] and k["vorschlag"] == {}


def test_kennwerte_berlin_nach_hoehenbereich(client):
    """Berlin: die Zeilen sind Hoehenbereiche (m NHN); der Vorschlag ordnet nach der Lage der Einheiten zu."""
    c, _ = client
    sig = c.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    k = c.get(f"/api/projekt/{sig}/bodenkennwerte").json()
    bez = {r["ref"]: r["bezeichnung"] for r in k["zeilen"]}
    v = {e: bez.get(x["ref"]) for e, x in k["vorschlag"].items()}
    assert v["Auffuellung"] == "1 GOK bis +32,0" and v["Kies 1"] == "2 +32,0 bis +30,0"
    assert v["Kies 2"] == "3 +30,0 bis +21,0"
    assert all("m NHN" in x["grund"] or x["ref"] is None for x in k["vorschlag"].values())


def test_laborwerte_talheim_je_einheit_und_atv(client):
    """Talheim: 5 CBR-Blaetter; 4 Proben im Tonstein, 1 im Schluff; die ATV-Kennwerte zeigen 'Labor:' vor der Ansprache."""
    c, _ = client
    sig = c.post("/api/beispiel", json={"name": "talheim"}).json()["projekt"]
    lab = c.get(f"/api/projekt/{sig}/bodenkennwerte").json()["labor"]
    assert lab["proben"] == 5 and lab["ohne_schicht"] == []
    t = lab["je_einheit"]["Fels (Tonstein)"]
    assert t["wassergehalt"]["n"] == 4 and t["wassergehalt"]["text"] == "11,1–16,9 % (n = 4, Mittel 14,4)"
    hk = c.get(f"/api/projekt/{sig}/homogenbereiche/kennwerte?atv=DIN%2018300").json()
    fels = next(b for b in hk["bereiche"] if b["name"] == "Fels (Tonstein)")
    w = next(z for z in fels["kennwerte"] if z["nr"] == "9")
    assert w["wert"].startswith("Labor: 11,1–16,9 %")
