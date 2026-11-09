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
    assert {k: z["standort"][k] for k in ("x", "y", "epsg")} == {"x": 368130.0, "y": 5724400.0, "epsg": 25832}
    assert z["name"] == "Marl Nord" and any(d["dienst"] == "NW" for d in z["standort"]["dienste"])   # Dienste am Ort
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


def test_standort_vorhanden_zuruecksetzen_und_leer(client):
    """Derselbe Punkt nochmal: nur oeffnen (Name und Schritt bleiben). Zuruecksetzen: Name bleibt, Schritt Lage.
    Ohne Bohrungen sagen Modell und Export, was fehlt."""
    sig = standort(client)
    client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "schritt", "wert": "modell"}]})
    r = client.post("/api/standort", json={"x": 368130.0, "y": 5724400.0, "epsg": 25832, "name": "Anders"}).json()
    assert r == {"projekt": sig, "vorhanden": True}
    z = client.get(f"/api/projekt/{sig}").json()
    assert z["name"] == "Marl Nord" and z["schritt"] == "modell"
    client.post(f"/api/projekt/{sig}/sgd/abfrage", json={"radius": 250})
    client.post(f"/api/projekt/{sig}/sgd/uebernehmen", json={"auswahl": [{"dienst": "NW", "id": "DABO_1"}]})
    z = client.post(f"/api/projekt/{sig}/zuruecksetzen").json()
    assert z["name"] == "Marl Nord" and z["schritt"] == "lage" and z["bohrungen"] == [] and z["sgd"] is None
    m = client.post(f"/api/projekt/{sig}/modell").json()
    assert m["fehler"].startswith("noch keine Bohrung – im Schritt Lage die Bohrungen der Länder abfragen")
    r = client.get(f"/api/projekt/{sig}/export/boreholeml")
    assert r.status_code == 400 and r.json()["detail"] == "keine exportierbare Bohrung: keine Bohrung im Projekt"
    # ohne Namen angelegt: Name aus dem Punkt, auch nach dem Zuruecksetzen (kein Pfad aus "x / y")
    sig2 = client.post("/api/standort", json={"x": 368600.0, "y": 5724700.0, "epsg": 25832}).json()["projekt"]
    assert client.post(f"/api/projekt/{sig2}/zuruecksetzen").json()["name"] == "Standort 368600 / 5724700 (EPSG:25832)"


def test_standort_ohne_dienst_des_landes(client):
    """Bayern: kein Datendienst fuer Bohrungen und DGM - gesagt statt still "0 Bohrungen", mit dem Portal des Landes."""
    sig = client.post("/api/standort", json={"x": 691000.0, "y": 5334000.0, "epsg": 25832}).json()["projekt"]
    s = client.post(f"/api/projekt/{sig}/sgd/abfrage", json={"radius": 250}).json()["sgd"]
    assert s["treffer"] == [] and s["dienste"] == ["DE-BGR-WMS"] and s["fehler"] == []   # nur der Hinweisdienst
    assert [p["dienst"] for p in s["portale"]] == ["BY", "DE-BGR"] and all(p["url"].startswith("https://") for p in s["portale"])
    r = client.post(f"/api/projekt/{sig}/dgm/abruf", json={})
    assert r.status_code == 400 and "kein DGM-Dienst für diesen Ort" in r.json()["detail"]
    assert "im Portal des Landes" in r.json()["detail"]


def test_standort_mit_zonenkennung_und_gutachten_ohne(client):
    """Standort in EPSG 4647 (Zonenkennung), der Dienst liefert 25832: Bohrungen der Laender kommen ins System des
    Standorts. Kommt ein Gutachten in 25832 dazu, gehen Bohrungen der Laender, DGM und Gebaeude in dessen System."""
    ap = client.app.state.arbeitsplatz
    sig = client.post("/api/standort", json={"x": 32368130.0, "y": 5724400.0, "epsg": 4647, "name": "Marl Zone"}).json()["projekt"]
    client.post(f"/api/projekt/{sig}/sgd/abfrage", json={"radius": 250})
    z = client.post(f"/api/projekt/{sig}/sgd/uebernehmen", json={"auswahl": [{"dienst": "NW", "id": "DABO_1"}]}).json()["zustand"]
    nw1 = next(b for b in z["viewer"]["bohrungen"] if b["code"] == "NW-1")
    assert nw1["x"] == pytest.approx(32_368_100.0) and z["viewer"]["epsg"] == 4647
    assert z["viewer"]["ursprung"] == [32_368_100.0, 5_724_400.0]
    zeilen = [f"{x + 32_000_000:.1f} {y:.1f} 60.000" for y in range(5724200, 5724601, 5) for x in range(367900, 368401, 5)]
    r = client.post(f"/api/projekt/{sig}/dgm", files=[("dateien", ("marl.xyz", ("\n".join(zeilen) + "\n").encode(), "text/plain"))],
                    data={"epsg": "4647"})
    assert r.status_code == 200, r.text
    _, p = ap.laden(sig)                                   # Gebaeude wie vom Land (im System des Standorts)
    ring = [[32_368_120.0, 5_724_380.0, 60.0], [32_368_130.0, 5_724_380.0, 60.0], [32_368_130.0, 5_724_390.0, 60.0]]
    (ap.ordner(sig) / "gebaeude.json").write_text(json.dumps({"epsg": 4647, "quelle": {}, "gebaeude": [
        {"id": "G1", "dienst": "NW-LOD2", "funktion": None, "dachform": None, "hoehe": None,
         "flaechen": [{"art": "Boden", "ring": ring, "loecher": []}]}]}), encoding="utf-8")
    p.gebaeude = {"anzahl": 1, "flaechen": 1, "epsg": 4647, "geladen": "2026-11-03 17:00", "stand": "abc",
                  "quelle": {"ausschnitt": [32_368_030.0, 5_724_300.0, 32_368_230.0, 5_724_500.0], "dienste": []}}
    ap.sichern(sig)
    assert "hinweis" not in client.get(f"/api/projekt/{sig}").json()["gebaeude"]
    a = client.post("/api/gutachten", files=[("dateien", ("marl_gutachten.json", json.dumps(MARL).encode(), "application/json"))],
                    data={"ocr": "false", "standort": sig}).json()
    for _ in range(200):
        a = client.get(f"/api/auftrag/{a['id']}").json()
        if a["fertig"]:
            break
        time.sleep(0.05)
    neu = a["projekt"]
    z = client.get(f"/api/projekt/{neu}").json()
    nw1 = next(b for b in z["viewer"]["bohrungen"] if b["code"] == "NW-1")
    assert nw1["x"] == pytest.approx(368_100.0) and z["viewer"]["epsg"] == 25832 and z["reifegrad"]["stufe"] == "gemischt"
    assert z["gelaende"]["info"]["epsg"] == 25832 and z["gelaende"]["info"]["x0"] == pytest.approx(367_900.0)
    assert all(zeile["status"] != "anderes_system" for zeile in z["gelaende"]["pruefung"]["zeilen"])
    assert z["gebaeude"]["epsg"] == 25832 and "hinweis" not in z["gebaeude"]
    g = json.loads((ap.ordner(neu) / "gebaeude.json").read_text(encoding="utf-8"))
    assert g["epsg"] == 25832 and g["gebaeude"][0]["flaechen"][0]["ring"][0][0] == pytest.approx(368_120.0)
    # das Standort-Projekt bleibt in seinem System (Datei und Kopf im Speicher)
    assert json.loads((ap.ordner(sig) / "gebaeude.json").read_text(encoding="utf-8"))["epsg"] == 4647
    _, ps = ap.laden(sig)
    assert ps.dgm["epsg"] == 4647 and ps.dgm["ausdehnung"][0] == pytest.approx(32_367_900.0)
    assert ps.gebaeude["quelle"]["ausschnitt"][0] == pytest.approx(32_368_030.0)
    # passen Gebaeude und Bohrungen nicht zusammen, wird es gesagt (nicht still aus dem IFC gelassen)
    _, p = ap.laden(neu)
    p.gebaeude["epsg"] = 25833
    assert "nicht ins Modell" in client.get(f"/api/projekt/{neu}").json()["gebaeude"]["hinweis"]
