"""DGM vom Land in der Schritt-App: Abruf auf Klick, GOK-Pruefung, Oberkante des Modells, Gelaende im IFC, Schalter.

Der Dienst ist durch die Attrappe aus test_dgm_dienst ersetzt (Gelaende = Ebene durch die GOK des Berliner Beispiels).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "tests")]
pytest.importorskip("fastapi")
from test_dgm_dienst import attrappe, dd  # noqa: E402
from test_gelaende_app import EBENE, OHNE_GOK, app, zeilen  # noqa: E402,F401  (app: Fixture)

from geodaten.bohrdaten import DienstFehler  # noqa: E402


def test_dgm_vom_land_pruefung_modell_und_ifc(app, monkeypatch, tmp_path):
    import ifcopenshell
    import ifcopenshell.util.element
    c, sig = app
    aufrufe = []
    monkeypatch.setattr(dd, "_holen", attrappe(aufrufe, hoehe=EBENE))
    z = c.post(f"/api/projekt/{sig}/dgm/abruf", json={}).json()
    info = z["gelaende"]["info"]
    assert len(aufrufe) == 1 and "COVERAGEID=bb_dgm" in aufrufe[0]
    assert info["quelle"]["dienst"] == "BB-DGM1" and info["name"] == "WCS BB DGM 1m (Brandenburg mit Berlin)"
    assert info["dx"] == 1.0 and info["epsg"] == 25833 and info["dateien"] == []
    st = zeilen(z)
    assert st[OHNE_GOK]["status"] == "ohne_gok" and st["422C-460"]["status"] == "ok"
    # Modell: Oberkante aus dem DGM, Gelaende um das Modell im IFC mit Lizenz und Namensnennung
    m = c.post(f"/api/projekt/{sig}/modell").json()
    gel = m["bericht"]["parameter"]["gelaende"]
    assert not m["fehler"] and gel["quelle"] == "DGM" and gel["quelle_dienst"]["dienst"] == "BB-DGM1"
    pfad = tmp_path / "modell.ifc"
    pfad.write_bytes(c.get(m["ifc"]).content)
    f = ifcopenshell.open(str(pfad))
    (g,) = f.by_type("IfcGeographicElement")
    ps = ifcopenshell.util.element.get_psets(g)["CPset_Gelaende"]
    assert g.PredefinedType == "TERRAIN" and ps["Lizenz"] == "dl-de/by-2.0" and "GeoBasis-DE/LGB" in ps["Namensnennung"]
    # Schalter: Oberkante wieder aus den GOK, kein Gelaende im IFC
    c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "einstellungen", "gelaende_dgm": False}]})
    m2 = c.post(f"/api/projekt/{sig}/modell").json()
    assert m2["bericht"]["parameter"]["gelaende"]["quelle"] == "GOK" and m2["schluessel"] != m["schluessel"]
    pfad.write_bytes(c.get(m2["ifc"]).content)
    assert len(ifcopenshell.open(str(pfad)).by_type("IfcGeographicElement")) == 0


def test_dgm_vom_land_fehler(app, monkeypatch):
    c, sig = app

    def kaputt(url, zeit):
        raise DienstFehler("keine Antwort in 120 s")
    monkeypatch.setattr(dd, "_holen", kaputt)
    r = c.post(f"/api/projekt/{sig}/dgm/abruf", json={})
    assert r.status_code == 502 and "Dienst des Landes" in r.json()["detail"] and "keine Antwort" in r.json()["detail"]
    assert c.get(f"/api/projekt/{sig}").json()["gelaende"] is None
    talheim = c.post("/api/beispiel", json={"name": "talheim"}).json()["projekt"]
    r = c.post(f"/api/projekt/{talheim}/dgm/abruf", json={})
    assert r.status_code == 400 and "Koordinaten" in r.json()["detail"]
