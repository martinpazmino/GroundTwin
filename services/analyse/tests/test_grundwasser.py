"""Grundwasserflaeche (docs/27 G5): exakt an den Staenden, trockene Bohrungen als Gegenprobe, Meldungen statt
stiller Annahmen, Kreuzprobe ab vier Staenden."""
from __future__ import annotations

import copy

import numpy as np
from baugrundmodell import synthetisch as syn
from baugrundmodell.modell import bauen

from baugrundanalyse import grundwasser
from baugrundanalyse.grundwasser import HINWEIS_ZEIT


def _docs(stand):
    """Demo-Fall; stand(code, gok) -> Liste von Tiefen, "trocken" oder None."""
    d = syn.dokument(syn.FAELLE["demo"]())
    for b in d["boreholes"]:
        s = stand(b["code"], b["gok_nhn"])
        if s == "trocken":
            b["groundwater_status"] = "kein Grundwasser"
        elif s:
            b["groundwater"] = [{"depth": t, "nhn": round(b["gok_nhn"] - t, 2), "kind": "gemessen"} for t in s]
    return [d]


def test_ebene_wasserflaeche_exakt_und_kreuzprobe():
    # Wasser bei 40,0 m NHN ueberall: an jeder Bohrung Tiefe = GOK - 40
    docs = _docs(lambda code, gok: [round(gok - 40.0, 2)])
    m = bauen(docs)
    g = grundwasser(m, docs)
    nb = len(m.bohrungen)
    assert g["gemessen"] == nb and np.allclose(g["z"][:nb], 40.0, atol=0.01)
    assert np.allclose(g["z"], 40.0, atol=0.05)                 # waagerecht auch zwischen den Bohrungen
    assert g["kreuzprobe"]["max_m"] <= 0.05 and not g["widersprueche"]
    assert HINWEIS_ZEIT in g["hinweise"]


def test_trockene_bohrung_widerspricht_und_wird_gemeldet():
    docs0 = _docs(lambda code, gok: None)
    m = bauen(docs0)
    trocken = m.bohrungen[0].code
    hoch = max(b.gok for b in m.bohrungen) - 0.5                  # Wasser knapp unter dem hoechsten Gelaende
    docs = _docs(lambda code, gok: "trocken" if code == trocken else [round(gok - min(hoch, gok - 0.2), 2)])
    g = grundwasser(m, docs)
    assert g["trocken"] == 1 and [w["code"] for w in g["widersprueche"]] == [trocken]
    assert any("widersprechen" in h for h in g["hinweise"])


def test_ohne_staende_ein_stand_und_spanne():
    docs = _docs(lambda code, gok: None)
    m = bauen(docs)
    g = grundwasser(m, docs)
    assert g["z"] is None and g["gemessen"] == 0 and "keine Bohrung" in g["hinweise"][0]
    erste = m.bohrungen[0].code
    docs1 = _docs(lambda code, gok: [1.0, 2.5] if code == erste else None)
    g1 = grundwasser(m, docs1)
    assert g1["gemessen"] == 1 and np.allclose(g1["z"], m.bohrungen[0].gok - 1.0)   # der hoechste Stand gilt
    assert any("waagerecht" in h for h in g1["hinweise"]) and any("Spanne 1,50" in h for h in g1["hinweise"])
    assert g1["kreuzprobe"] is None


def test_ueber_gelaende_wird_gemeldet_und_aendert_nichts():
    docs = _docs(lambda code, gok: [0.1])
    m = bauen(docs)
    vorher = copy.deepcopy(m.flaechen)
    # ein Stand weit ueber dem Gelaende (z. B. Tippfehler oder gespannt): negative Tiefe
    docs[0]["boreholes"][0]["groundwater"] = [{"depth": -3.0, "nhn": None, "kind": "gemessen"}]
    g = grundwasser(m, docs)
    assert g["ueber_gelaende_knoten"] > 0 and any("über dem Gelände" in h for h in g["hinweise"])
    assert np.array_equal(vorher, m.flaechen)                      # liest das Modell, aendert nichts
