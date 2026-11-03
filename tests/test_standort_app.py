"""Standort-Projekt ohne Gutachten (docs/23 §2.3, Phase P5): Punkt -> Bohrungen der Laender -> Modell als Vorerkundung;
ein Gutachten dazu nimmt Bohrungen der Laender, Pruefstand, Abfrage und DGM mit (gemischt, beide Quellen getrennt).

Der Dienst NRW ist durch die Attrappe aus test_bohrdaten ersetzt (DABO_1, DABO_2 bei Marl).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "tests")]
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from test_bohrdaten import attrappe, bd  # noqa: E402
from test_bohrdaten_app import MARL  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    monkeypatch.setattr(bd, "_holen", attrappe())
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c


def standort(client, **kw) -> str:
    r = client.post("/api/standort", json={"x": 368130.0, "y": 5724400.0, "epsg": 25832, "name": "Marl Nord", **kw})
    assert r.status_code == 200, r.text
    return r.json()["projekt"]


def dgm_marl() -> bytes:
    zeilen = [f"{x:.1f} {y:.1f} {60.0 + 0.001 * (x - 368000):.3f}" for y in range(5724200, 5724601, 5)
              for x in range(367900, 368401, 5)]
    return ("\n".join(zeilen) + "\n").encode()


def test_standort_bohrungen_der_laender_modell_vorerkundung(client):
    import ifcopenshell
    import ifcopenshell.util.element
    sig = standort(client)
    z = client.get(f"/api/projekt/{sig}").json()
    assert z["standort"] == {"x": 368130.0, "y": 5724400.0, "epsg": 25832} and z["name"] == "Marl Nord"
    assert z["lage_modus"] == "koordinaten" and z["schritt"] == "lage" and z["bohrungen"] == []
    assert z["reifegrad"]["stufe"] == "Vorerkundung"
    # Nullpunkt der Szene am Standort (auf 100 m): die Bohrungen der Laender kommen dazu, ohne dass er springt
    assert z["viewer"]["ursprung"] == [368100.0, 5724400.0] and z["viewer"]["epsg"] == 25832
    assert standort(client) == sig                                           # derselbe Punkt: dasselbe Projekt
    # Abfrage um den Punkt, Uebernahme, Modell: Vorerkundung im Bericht und im IFC
    s = client.post(f"/api/projekt/{sig}/sgd/abfrage", json={"radius": 250}).json()["sgd"]
    assert s["mitte"] == [368130.0, 5724400.0] and {t["id"] for t in s["treffer"]} == {"DABO_1", "DABO_2"}
    r = client.post(f"/api/projekt/{sig}/sgd/uebernehmen",
                    json={"auswahl": [{"dienst": "NW", "id": "DABO_1"}, {"dienst": "NW", "id": "DABO_2"}]}).json()
    z = r["zustand"]
    assert sorted(b["code"] for b in z["bohrungen"]) == ["NW-1", "NW-2"] and z["reifegrad"]["stufe"] == "Vorerkundung"
    assert z["viewer"]["ursprung"] == [368100.0, 5724400.0]
    eintrag = next(e for e in client.get("/api/projekte").json() if e["signatur"] == sig)
    assert eintrag["standort"] and eintrag["bohrungen"] == 2 and eintrag["fremd"] == 2      # Liste zaehlt sie mit
    m = client.post(f"/api/projekt/{sig}/modell").json()
    assert not m["fehler"] and m["bericht"]["reifegrad"] == "Vorerkundung"
    assert any(h.startswith("Vorerkundung") for h in m["hinweise"])
    ifc = client.get(f"/api/projekt/{sig}/export/ifc").content
    pfad = Path(client.app.state.arbeitsplatz.arbeit) / "vorerkundung.ifc"
    pfad.write_bytes(ifc)
    f = ifcopenshell.open(str(pfad))
    assert ifcopenshell.util.element.get_psets(f.by_type("IfcGeomodel")[0])["CPset_Baugrundmodell"]["Reifegrad"] == "Vorerkundung"
    # Schichten aus dem Archiv: feste niedrige Konfidenz
    sch = client.get(f"/api/projekt/{sig}/bohrung/{z['bohrungen'][0]['id']}").json()["schichten"]
    assert sch and all(s["konfidenz"] == 0.5 for s in sch)


def test_standort_falsche_koordinaten(client):
    r = client.post("/api/standort", json={"x": 4594774.3, "y": 5818338.1, "epsg": 31468})
    assert r.status_code == 400 and "ETRS89/UTM" in r.json()["detail"]
    r = client.post("/api/standort", json={"x": 368130.0, "y": 4724400.0, "epsg": 25832})
    assert r.status_code == 400 and "nicht in Deutschland" in r.json()["detail"]


def test_gutachten_zum_standort_gemischt_und_getrennt(client):
    sig = standort(client)
    client.post(f"/api/projekt/{sig}/sgd/abfrage", json={"radius": 250})
    z = client.post(f"/api/projekt/{sig}/sgd/uebernehmen", json={"auswahl": [{"dienst": "NW", "id": "DABO_1"}]}).json()["zustand"]
    nw1 = next(b for b in z["bohrungen"] if b["code"] == "NW-1")
    client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "geprueft", "id": nw1["id"], "wert": True}]})
    r = client.post(f"/api/projekt/{sig}/dgm", files=[("dateien", ("marl.xyz", dgm_marl(), "text/plain"))], data={"epsg": "25832"})
    assert r.status_code == 200, r.text
    # Gutachten (als Extraktion) zum Standort: neues Projekt mit beiden Quellen
    a = client.post("/api/gutachten", files=[("dateien", ("marl_gutachten.json", json.dumps(MARL).encode(), "application/json"))],
                    data={"ocr": "false", "standort": sig}).json()
    for _ in range(200):
        a = client.get(f"/api/auftrag/{a['id']}").json()
        if a["fertig"]:
            break
        time.sleep(0.05)
    assert a["fertig"] and not a["fehler"] and a["projekt"] and a["projekt"] != sig
    z = client.get(f"/api/projekt/{a['projekt']}").json()
    codes = {b["code"]: b for b in z["bohrungen"]}
    assert set(codes) == {"B1", "B2", "NW-1"} and z["reifegrad"] == {"stufe": "gemischt", "anzahl": {"Gutachten": 2, "SGD": 1}}
    assert codes["NW-1"]["id"] == "1:0" and codes["NW-1"]["geprueft"]                    # Kennung umgezogen, Haken mit
    assert z["gelaende"]["info"]["name"] == "marl.xyz" and z["sgd"]["gegenprobe"]["anzahl"] == 0
    assert next(n for n in z["viewer"]["bohrungen"] if n["code"] == "NW-1")["herkunft"] == "SGD"
    m = client.post(f"/api/projekt/{a['projekt']}/modell").json()
    assert m["bericht"]["reifegrad"] == "gemischt"
    # das Standort-Projekt bleibt unveraendert bestehen
    assert client.get(f"/api/projekt/{sig}").json()["reifegrad"]["stufe"] == "Vorerkundung"


def test_unbekannter_standort_beim_hochladen(client):
    r = client.post("/api/gutachten", files=[("dateien", ("m.json", json.dumps(MARL).encode(), "application/json"))],
                    data={"standort": "gibtsnicht"})
    assert r.status_code == 404
