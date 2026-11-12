"""Erkundungsvorschlag (docs/27 G4): an einer Rinne zwischen den Bohrungen schlaegt die Analyse die Raender vor, und
zwei Bohrungen dort senken den Fehler mehr als zwei zufaellige (Wahrheit bekannt, synthetisch)."""
from __future__ import annotations

import numpy as np
from baugrundmodell import synthetisch as syn
from baugrundmodell.modell import bauen

from baugrundanalyse import unsicherheit, virtuelle_bohrung
from baugrundanalyse.vorschlag import vorschlaege

ACHSE, BREITE, SOHLE = 50.0, 20.0, 28.0


def rinne_basis(x, y):
    d = abs(x - ACHSE)
    return 40.0 if d >= BREITE / 2 else SOHLE + (40.0 - SOHLE) * (d / (BREITE / 2)) ** 2


E = [("Auffuellung", lambda x, y: 39.0), ("Torf", lambda x, y: min(39.0, rinne_basis(x, y))),
     ("Sand", lambda x, y: 32.0), ("Geschiebemergel", lambda x, y: 25.0), ("Ton", lambda x, y: 10.0)]
RASTER = [(f"B{i}", x, y, 20.0) for i, (x, y) in enumerate([(x, y) for x in (10, 50, 90) for y in (10, 30, 50)], 1)]


def fall(bh):
    return syn.Fall("rinne", lambda x, y: 40.0, E, bh)


def fehler(bh) -> float:
    m = bauen([syn.dokument(fall(bh))], methode="tps")
    f = []
    for x in np.arange(14, 87, 4.0):
        for y in (12.0, 30.0, 48.0):
            v = virtuelle_bohrung(m, syn.URSPRUNG[0] + x, syn.URSPRUNG[1] + y)
            torf = next((s["maechtigkeit_m"] for s in v["schichten"] if s["einheit"] == "Torf"), 0.0)
            wahr = max(0.0, 39 - max(rinne_basis(x, y), SOHLE)) if rinne_basis(x, y) < 39 else 0.0
            f.append(abs(torf - wahr))
    return float(np.mean(f))


def test_vorschlag_an_den_raendern_der_rinne_und_besser_als_zufall():
    m = bauen([syn.dokument(fall(RASTER))], methode="tps")
    v = vorschlaege(m, unsicherheit(m, laeufe=20), anzahl=2)
    xs = sorted(p["x"] - syn.URSPRUNG[0] for p in v)
    assert len(v) == 2 and 20 < xs[0] < 45 and 55 < xs[1] < 80                 # je ein Rand, nicht beide auf einer Seite
    assert all("Ausdehnung von Torf unsicher" in p["grund"] for p in v)
    assert all(p["abstand_naechste_bohrung_m"] >= 5 for p in v)
    neu = [(f"V{i}", p["x"] - syn.URSPRUNG[0], p["y"] - syn.URSPRUNG[1], 20.0) for i, p in enumerate(v)]
    ohne, mit = fehler(RASTER), fehler(RASTER + neu)
    rng = np.random.default_rng(1)
    zufall = [fehler(RASTER + [(f"Z{i}", float(rng.uniform(5, 95)), float(rng.uniform(5, 55)), 20.0) for i in range(2)])
              for _ in range(6)]
    assert mit < 0.6 * ohne and mit < float(np.median(zufall))


def test_vorschlag_ohne_unsicherheit_leer_und_reihenfolge():
    m = bauen([syn.dokument(syn.geneigt())], methode="tps")                    # Ebenen, Spline exakt: nur die Messung
    u = unsicherheit(m, laeufe=10)
    v = vorschlaege(m, u, anzahl=3)
    assert len(v) <= 3 and all(a["wert_m"] >= b["wert_m"] for a, b in zip(v, v[1:]))
    d = [np.hypot(a["x"] - b["x"], a["y"] - b["y"]) for i, a in enumerate(v) for b in v[i + 1:]]
    assert all(x >= 19.9 for x in d)                                            # mindestens ein Bohrabstand (20 m) dazwischen
