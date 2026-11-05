"""LoD2-Gebaeude in der Schritt-App: Abruf auf Klick, gebaeude.json, IFC mit Gebaeuden und Lizenz je Dienst, Entfernen.

Die Kacheln liefert die Attrappe aus test_gebaeude (Berliner Beispiel: Kachel 394/5818 von Berlin, 395/5818 aus
Brandenburg, damit beide Lizenzen im IFC stehen). Mitten in Berlin waehlt die App nur den Berliner Dienst
(Laendergrenzen); der Test stellt deshalb einen Projektort an der Landesgrenze nach (beide Dienste am Ort).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "tests")]
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from test_gebaeude import attrappe, gb, gezippt, haus, kachel  # noqa: E402
from geodaten import bohrdaten  # noqa: E402
from ui import pipeline as pl  # noqa: E402

KACHELN = {"LoD2_394_5818": gezippt(kachel(haus("DEBE_1", 394800, 5818300), haus("DEBE_2", 394860, 5818480))),
           "lod2_33395-5818": gezippt(kachel(haus("DEBB_1", 395000, 5818400, teil=False)), "lod2_33395-5818_geb.gml")}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    monkeypatch.setattr(gb, "_holen", attrappe(KACHELN))
    monkeypatch.setattr(gb, "dienste_am_ort", lambda *a, **k: [bohrdaten.dienst("BE-LOD2"), bohrdaten.dienst("BB-LOD2")])
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c


def test_gebaeude_abruf_ifc_und_entfernen(client, tmp_path):
    import ifcopenshell
    import ifcopenshell.util.element
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    assert client.get(f"/api/projekt/{sig}").json()["gebaeude"] is None                  # nichts ohne Klick
    z = client.post(f"/api/projekt/{sig}/gebaeude/abruf", json={}).json()
    g = z["gebaeude"]
    assert g["anzahl"] == 3 and g["epsg"] == 25833 and [d["dienst"] for d in g["quelle"]["dienste"]] == ["BE-LOD2", "BB-LOD2"]
    m = client.post(f"/api/projekt/{sig}/modell").json()
    assert not m["fehler"]
    pfad = tmp_path / "m.ifc"
    pfad.write_bytes(client.get(m["ifc"]).content)
    f = ifcopenshell.open(str(pfad))
    lizenz = {ifcopenshell.util.element.get_psets(e)["CPset_Gebaeude"]["GML_ID"]:
              ifcopenshell.util.element.get_psets(e)["CPset_Gebaeude"]["Lizenz"] for e in f.by_type("IfcBuildingElementProxy")}
    assert lizenz == {"DEBE_1": "dl-de/zero-2.0", "DEBE_2": "dl-de/zero-2.0", "DEBB_1": "dl-de/by-2.0"}
    # der Export (IFC-Datei) traegt sie ebenfalls; Entfernen nimmt sie aus dem naechsten IFC
    export = client.get(f"/api/projekt/{sig}/export/ifc").content
    assert export.count(b"IFCBUILDINGELEMENTPROXY") == 3
    z = client.delete(f"/api/projekt/{sig}/gebaeude").json()
    assert z["gebaeude"] is None
    m2 = client.post(f"/api/projekt/{sig}/modell").json()
    assert m2["ifc"] != m["ifc"]
    pfad.write_bytes(client.get(m2["ifc"]).content)
    assert len(ifcopenshell.open(str(pfad)).by_type("IfcBuildingElementProxy")) == 0


def test_gebaeude_fehler(client, monkeypatch):
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    monkeypatch.setattr(gb, "_holen", attrappe({}))                                       # keine Kachel: kein Gebaeude
    r = client.post(f"/api/projekt/{sig}/gebaeude/abruf", json={})
    assert r.status_code == 400 and "keine LoD2-Gebäude" in r.json()["detail"]
    monkeypatch.setattr(gb, "_holen", attrappe({"LoD2": gb.DienstFehler("keine Antwort in 120 s"),
                                                "lod2_33": gb.DienstFehler("keine Antwort in 120 s")}))
    r = client.post(f"/api/projekt/{sig}/gebaeude/abruf", json={})
    assert r.status_code == 502 and "keine Antwort" in r.json()["detail"]
    talheim = client.post("/api/beispiel", json={"name": "talheim"}).json()["projekt"]
    r = client.post(f"/api/projekt/{talheim}/gebaeude/abruf", json={})
    assert r.status_code == 400 and "Koordinaten" in r.json()["detail"]
