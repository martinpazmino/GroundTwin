"""Karte als Pop-up fuer den Standort ohne Gutachten (docs/21 §4.7, D97): Klick (Laenge/Breite) -> ETRS89/UTM,
die Dienste der Laender am Ort, Punkte ausserhalb Deutschlands, Beispiele am Standort.

Vergleichswerte aus PROJ (pyproj 3.8, ETRS89 -> UTM), wie in tests/test_tiles3d.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "services" / "geodaten")]
from geodaten import bohrdaten, utm  # noqa: E402

# (EPSG, Rechtswert, Hochwert, Laenge, Breite) aus PROJ
PROJ = [(25833, 394774.3, 5818338.1, 13.4496729128, 52.5050027515),
        (25832, 368130.0, 5724400.0, 7.0936462523, 51.6551050227),
        (25832, 800000.0, 5400000.0, 13.0760444234, 48.6808574684)]


@pytest.mark.parametrize("epsg, e, n, lon, lat", PROJ)
def test_geographisch_nach_utm_wie_proj(epsg, e, n, lon, lat):
    x, y = utm.von_geo(lon, lat, utm.zone(epsg))
    assert abs(float(x) - e) < 1e-3 and abs(float(y) - n) < 1e-3                    # unter 1 mm


def test_hin_und_zurueck_in_beiden_zonen_und_zone_nach_laenge():
    rng = np.random.default_rng(7)
    e, n = rng.uniform(170_000, 830_000, 500), rng.uniform(5_200_000, 6_150_000, 500)
    for zone in (32, 33):
        x, y = utm.von_geo(*utm.zu_geo(e, n, zone), zone)
        assert np.abs(x - e).max() < 1e-3 and np.abs(y - n).max() < 1e-3
    assert (utm.zone_fuer(6.0), utm.zone_fuer(11.99), utm.zone_fuer(12.0), utm.zone_fuer(14.9)) == (32, 32, 33, 33)


def test_dienste_am_ort():
    berlin = bohrdaten.am_ort(394774.3, 5818338.1, 25833)
    arten = {(d["dienst"], d["art"]) for d in berlin}
    assert {("BE", "bohrungen"), ("BB-DGM1", "dgm"), ("BE-LOD2", "gebaeude")} <= arten
    assert "nur Kopfdaten" in next(d["text"] for d in berlin if d["dienst"] == "BE")
    marl = bohrdaten.am_ort(368130.0, 5724400.0, 25832)
    assert "mit Schichtdaten" in next(d["text"] for d in marl if d["dienst"] == "NW")
    muenchen = bohrdaten.am_ort(691567.3, 5334734.3, 25832)                          # Bayern: nur Portale, als Link
    assert [d["dienst"] for d in muenchen if d["art"] == "bohrungen"] == ["BY", "DE-BGR", "DE-BGR-WMS"]
    assert "kein Datendienst – im Portal ansehen" in muenchen[0]["text"] and muenchen[0]["url"].startswith("https://")
    assert {d["art"] for d in muenchen} == {"bohrungen", "dgm", "gebaeude"}
    assert {d["status"] for d in muenchen if d["art"] != "gebaeude" and d["dienst"] != "DE-BGR-WMS"} == {"ungeprueft"}
    lod2 = [d for d in muenchen if d["art"] == "gebaeude"]                             # LoD2 Bayern seit 2026-11-07
    assert [(d["dienst"], d["status"], d["url"]) for d in lod2] == [("BY-LOD2-GML", "geprueft", "")]
    assert all(d["url"] == "" and d["status"] == "geprueft" for d in berlin)            # angebunden: kein Portal-Link


# ---------------------------------------------------------------- in der App
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c


def test_klick_in_die_karte(client):
    r = client.get("/api/standort/punkt", params={"laenge": 13.4496729128, "breite": 52.5050027515}).json()
    assert (r["x"], r["y"], r["epsg"]) == (394774.3, 5818338.1, 25833)
    assert any(d["dienst"] == "BE" and "nur Kopfdaten" in d["text"] for d in r["dienste"])
    r = client.get("/api/standort/punkt", params={"laenge": 7.0936462523, "breite": 51.6551050227}).json()
    assert (r["x"], r["y"], r["epsg"]) == (368130.0, 5724400.0, 25832)
    r = client.get("/api/standort/punkt", params={"laenge": 7.0936462523, "breite": 51.6551050227, "epsg": 4647}).json()
    assert (r["x"], r["epsg"]) == (32368130.0, 4647)                                  # mit Zonenkennung
    r = client.get("/api/standort/punkt", params={"laenge": 11.575, "breite": 48.137}).json()
    assert r["epsg"] == 25832 and "kein Datendienst" in r["dienste"][0]["text"]       # München: Portal statt Dienst


@pytest.mark.parametrize("laenge, breite", [(2.35, 48.85), (16.37, 48.21), (10.0, 46.0)])   # Paris, Wien, Alpen-Süd
def test_klick_ausserhalb_deutschlands(client, laenge, breite):
    r = client.get("/api/standort/punkt", params={"laenge": laenge, "breite": breite})
    assert r.status_code == 400 and "nicht in Deutschland" in r.json()["detail"]


def test_standort_in_einer_anderen_zone_abgelehnt(client):
    # Paris in Zone 31 hat Rechts- und Hochwert im selben Bereich wie Deutschland: die Zahlen allein reichten nicht
    r = client.post("/api/standort", json={"x": 452314.9, "y": 5410984.9, "epsg": 25831})
    assert r.status_code == 400 and "nicht in Deutschland" in r.json()["detail"]


def test_beispiele_am_standort(client):
    info = client.get("/api/info").json()
    standorte = [b for b in info["beispiele"] if b.get("standort")]
    assert [b["name"] for b in standorte] == ["standort_dortmund", "standort_karlsruhe", "standort_berlin"]
    r = client.post("/api/beispiel", json={"name": "standort_dortmund"}).json()
    assert r["schritt"] == "lage"
    z = client.get(f"/api/projekt/{r['projekt']}").json()
    assert z["name"] == "Beispiel Dortmund" and z["standort"]["epsg"] == 25832 and z["reifegrad"]["stufe"] == "Vorerkundung"
    assert any(d["dienst"] == "NW" and "Schichtdaten" in d["text"] for d in z["standort"]["dienste"])
    client.post(f"/api/projekt/{r['projekt']}/aendern", json={"ops": [{"op": "schritt", "wert": "modell"}]})
    nochmal = client.post("/api/beispiel", json={"name": "standort_dortmund"}).json()
    assert nochmal == {"projekt": r["projekt"], "schritt": "modell"}                  # dasselbe Projekt, wie zuletzt
    berlin = client.get(f"/api/projekt/{client.post('/api/beispiel', json={'name': 'standort_berlin'}).json()['projekt']}").json()
    assert berlin["standort"]["epsg"] == 25833 and any("nur Kopfdaten" in d["text"] for d in berlin["standort"]["dienste"])
    assert client.post("/api/beispiel", json={"name": "standort_nirgendwo"}).status_code == 404
