"""Sondierungen in den Kennwerten der Homogenbereiche (Issue #29): N10/q_c je Einheit nach der Hoehe am Ort der
Sondierung zugeordnet, als Messwerte neben der Ansprache, nie eingestuft."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in ("", "services/modeler", "services/analyse"):
    sys.path.insert(0, str(ROOT / p))
pytest.importorskip("fastapi")
from baugrundanalyse import sondierung_je_einheit, sondierung_zusammenfassen  # noqa: E402
from baugrundmodell import homogenbereiche as hb  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    arbeit = tmp_path_factory.mktemp("arbeit")
    alt, pl.ARBEIT = pl.ARBEIT, arbeit
    with TestClient(app_erstellen(arbeit)) as c:
        yield c
    pl.ARBEIT = alt


def demo_mit_lage(client):
    """Demo mit Lage der drei Sondierungen (3/2 m neben B 1–3)."""
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    z = client.get(f"/api/projekt/{sig}").json()
    ops = []
    for s, b in zip(z["sondierungen"], z["bohrungen"][:3]):
        ops += [{"op": "sondierung", "sondierung": s["id"], "feld": "x", "wert": b["x"] + 3},
                {"op": "sondierung", "sondierung": s["id"], "feld": "y", "wert": b["y"] + 2}]
    assert client.post(f"/api/projekt/{sig}/aendern", json={"ops": ops}).status_code == 200
    return sig


def test_kennwerte_mit_sondierung(client):
    sig = demo_mit_lage(client)
    k = client.get(f"/api/projekt/{sig}/homogenbereiche/kennwerte", params={"atv": "DIN 18300"}).json()
    assert k["fehler"] == ""
    texte = {b["name"]: {z["nr"]: z["wert"] for z in b["kennwerte"]} for b in k["bereiche"]}
    sand = texte["Sand 1"]["13"]
    assert "Sondierung DPH: N10" in sand and "Sondierung CPT: q_c" in sand and "MN/m²" in sand
    assert "nicht eingestuft" in sand and "zensiert" in sand                       # zensierte N10 gezaehlt
    for t in texte.values():                                                         # nie eingestuft
        for w in t.values():
            assert not w or not any(x in w for x in ("mitteldicht", "Lagerungsdichte D =", "I_D"))
    assert any("nicht zugeordnet" in h for h in k["sondierung_hinweise"])           # Werte ueber dem Modell gemeldet
    # Bewertbarkeit: Sondierungen mit Lage zaehlen jetzt
    b = client.get(f"/api/projekt/{sig}/bereitschaft").json()
    st = {e["id"]: e["status"] for e in b["eintraege"]}
    assert st["sondierung.n10_je_einheit"] == "moeglich" and st["sondierung.qc_je_einheit"] == "moeglich"


def test_ohne_lage_keine_sondierungswerte(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)                                    # eigenes Projekt ohne Lage
    with TestClient(app_erstellen(tmp_path)) as client:
        _ohne_lage(client)


def _ohne_lage(client):
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    k = client.get(f"/api/projekt/{sig}/homogenbereiche/kennwerte", params={"atv": "DIN 18300"}).json()
    assert not any("Sondierung" in (z["wert"] or "") for b in k["bereiche"] for z in b["kennwerte"])
    assert k["sondierung_hinweise"] == []


def test_zuordnung_nach_hoehe_und_bindig_bei_konsistenz():
    class E:
        def __init__(self, n): self.name = n

    import numpy as np

    class M:                                                                       # ein Dreieck, zwei Einheiten
        ursprung = (0.0, 0.0)
        punkte = np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0]])
        dreiecke = np.array([[0, 1, 2]])
        flaechen = np.array([[10.0] * 3, [7.0] * 3, [0.0] * 3])                    # GOK 10, Basis A 7, Basis B 0
        einheiten = [E("A"), E("B")]

    s = {"code": "DPH 9", "art": "DPH", "x": 2.0, "y": 2.0, "gok": 10.0,
         "werte": [[0.0, 0.1, 3], [2.9, 3.0, 5], [3.0, 3.1, 20], [4.0, 4.1, {"wert": 50, "zensiert": True}],
                   [11.0, 11.1, 9]]}
    je, hinweise = sondierung_je_einheit(M, [s, {**s, "code": "DPH 10", "x": 50.0}])
    assert je["A"]["N10"] == [3, 5] and je["B"]["N10"] == [20, 50] and je["B"]["zensiert"] == 1
    assert any("außerhalb" in h for h in hinweise) and any("1 Werte" in h for h in hinweise)
    pool = sondierung_zusammenfassen([je["A"], je["B"]])
    assert pool["N10"] == [3, 5, 20, 50] and pool["sondierungen"] == ["DPH 9"]
    assert sondierung_zusammenfassen([]) is None
    ton = [{"beschreibung": "Ton, steif", "bodenart": "Ton"}]
    kw = {z["nr"]: z["wert"] for z in hb.kennwerte_bereich("DIN 18300", ton, pool)["kennwerte"]}
    assert "Sondierung DPH" in (kw.get("11b") or "") and "11a" not in kw           # bindig: Konsistenz, die 18300 verlangt
    kw = {z["nr"]: z["wert"] for z in hb.kennwerte_bereich("DIN 18311", ton, pool)["kennwerte"]}
    assert "Sondierung DPH" in (kw.get("11a") or "")                                 # 18311 verlangt 11a
    sand = [{"beschreibung": "Sand, mitteldicht", "bodenart": "Sand"}]
    kw = {z["nr"]: z["wert"] for z in hb.kennwerte_bereich("DIN 18300", sand, pool)["kennwerte"]}
    assert kw["13"].startswith("mitteldicht") and "Sondierung DPH" in kw["13"]       # neben der Ansprache
