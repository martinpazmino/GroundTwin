"""Implizite Methode mit GemPy (docs/27 G3, D105, D106): Orientierung ohne gemessenes Einfallen, exakte Kontakte,
geschlossene Koerper, gueltiges IFC in Metern, Rueckfall auf den Spline bei gefalteten Flaechen. Ohne GemPy: uebersprungen
(die Orientierung braucht GemPy nicht und laeuft immer)."""
from __future__ import annotations

import math

import numpy as np
import pytest
from baugrundmodell import flaechen
from baugrundmodell import synthetisch as syn
from baugrundmodell.modell import bauen, bericht, ifc_schreiben

from baugrundanalyse import implizit, kreuzprobe, unsicherheit


# ------------------------------------------------------------------ Orientierung (ohne GemPy)
def test_orientierung_ebene_linie_steil_und_wenige():
    # Ebene z = 10 - 0,05 x: Einfallen atan(0,05) = 2,86 Grad nach Osten (Fallrichtung 90 Grad)
    p = np.array([[0, 0, 10], [40, 0, 8], [0, 40, 10], [40, 40, 8], [20, 20, 9]], float)
    c, pol, quelle, fallen = implizit.orientierung(p)
    assert quelle == "Ebene durch die Kontakte" and fallen == pytest.approx(math.degrees(math.atan(0.05)), abs=0.01)
    assert pol[2] > 0 and np.allclose(c, p.mean(axis=0))
    e = implizit.beschreiben([type("E", (), {"name": "X"})()], [[type("K", (), {"art": "exakt", "status": "vorhanden", "z": z})()]
                                                                for z in p[:, 2]],
                             [type("B", (), {"x": x, "y": y})() for x, y in p[:, :2]])[0]
    assert e["fallrichtung_grad"] == 90.0 and e["kontakte"] == 5
    # auf einer Linie (Trasse): Einfallen entlang der Linie, quer horizontal
    linie = np.array([[0, 0, 10], [50, 0, 9], [100, 0, 8]], float)
    _, pol, quelle, fallen = implizit.orientierung(linie)
    assert quelle.startswith("entlang der Linie") and pol[1] == pytest.approx(0, abs=1e-9)
    assert fallen == pytest.approx(math.degrees(math.atan(0.02)), abs=0.01)
    # steiler als 30 Grad: nicht glaubhaft -> horizontal
    steil = np.array([[0, 0, 0], [10, 0, -10], [0, 10, 0], [10, 10, -10]], float)
    _, pol, quelle, fallen = implizit.orientierung(steil)
    assert quelle.startswith("horizontal (Ebene") and fallen == 0.0 and np.allclose(pol, [0, 0, 1])
    _, pol, quelle, _ = implizit.orientierung(np.array([[0, 0, 1], [5, 5, 2]], float)[:1])
    assert quelle.startswith("horizontal (zu wenige")


gempy = pytest.importorskip("gempy")


@pytest.fixture(autouse=True)
def angemeldet():
    assert implizit.registrieren()
    yield
    flaechen.ERWEITERUNGEN.pop("implizit", None)


def test_modell_implizit_exakt_geschlossen_und_ifc(tmp_path):
    import ifcopenshell
    import ifcopenshell.util.unit
    import ifcopenshell.validate
    for name in ("geneigt", "auskeilen", "linse"):
        docs = [syn.dokument(syn.FAELLE[name]())]
        m = bauen(docs, methode="implizit")
        assert m.max_abweichung <= implizit.TOLERANZ, name                    # Abnahme G3: Kontakte auf 5 cm
        assert all(k["pruefung"]["geschlossen"] for k in m.koerper), name
        assert m.parameter["methode"] == "implizit" and len(m.parameter["orientierung"]) == len(m.einheiten)
    pfad = tmp_path / "linse.ifc"
    ifc_schreiben(m, pfad, docs)
    f = ifcopenshell.open(str(pfad))
    log = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, log)
    assert log.statements == [] and ifcopenshell.util.unit.calculate_unit_scale(f) == 1.0
    text = pfad.read_text(errors="ignore")
    assert "implizit (GemPy" in text
    assert bericht(m)["parameter"]["orientierung"][0]["quelle"]


def test_implizit_gleich_dem_spline_auf_ebenen_und_besser_als_idw():
    m = bauen([syn.dokument(syn.geneigt())], methode="implizit")
    t = bauen([syn.dokument(syn.geneigt())], methode="tps")
    assert np.abs(m.flaechen - t.flaechen).max() < 0.05                        # Ebenen: beide treffen sie
    k = kreuzprobe(m)
    assert set(k["methoden"]) == {"idw", "tps", "implizit"} and k["methode_modell"] == "implizit"
    assert k["methoden"]["implizit"]["gesamt"]["mae"] < 0.1 < k["methoden"]["idw"]["gesamt"]["mae"]
    u = unsicherheit(m, k, laeufe=10)
    assert any("Dünnplatten-Spline gerechnet" in a for a in u["annahmen"])


def test_gefaltete_flaeche_faellt_auf_den_spline_zurueck():
    # zwei nahe Punkte mit 15 m Hoehenunterschied (wie die verfuellten Rinnen in Hamburg, docs/27 §3.1)
    xy = np.array([[0, 0], [3, 0], [60, 0], [0, 60], [60, 60], [30, 30]], float)
    z = np.array([5.0, -10.0, 5.0, 4.0, 5.0, 4.5])
    ziel = np.array([[10, 10], [50, 50], [1.5, 0.0]], float)
    flaechen.hinweise_starten()
    werte = flaechen.interpolieren(ziel, xy, z, "implizit")
    h = flaechen.hinweise_holen()
    spline = flaechen.interpolieren(ziel, xy, z, "tps")
    if h:                                                                       # gefaltet oder nicht exakt: Spline
        assert any("Dünnplatten-Spline" in x for x in h) and np.allclose(werte, spline)
    else:                                                                       # sonst muss sie eindeutig und exakt sein
        assert np.all(np.isfinite(werte))
    an = flaechen.interpolieren(xy, xy, z, "implizit")
    assert np.allclose(an, z)                                                   # an den Daten immer exakt


def test_ohne_anmeldung_klare_meldung():
    flaechen.ERWEITERUNGEN.pop("implizit", None)
    with pytest.raises(ValueError, match="nicht verfügbar"):
        bauen([syn.dokument(syn.geneigt())], methode="implizit")


def test_pol_aus_fallrichtung_und_fallwinkel():
    p = implizit.pol_aus(90.0, 30.0)                      # faellt nach Osten: Pol nach Osten und oben
    assert p == pytest.approx([0.5, 0.0, math.cos(math.radians(30))], abs=1e-9)
    assert implizit.pol_aus(0.0, 0.0) == pytest.approx([0, 0, 1])


def test_eingegebene_orientierung_gilt_und_bleibt_exakt():
    """docs/27 G4: eine eingegebene Orientierung ersetzt die berechnete, die Kontakte bleiben exakt; die Kreuzprobe
    rechnet mit derselben Eingabe; ein unbekannter Name wird gemeldet."""
    docs = [syn.dokument(syn.FAELLE["geneigt"]())]
    ohne = bauen(docs, methode="implizit")
    name = ohne.einheiten[0].name
    mit = bauen(docs, methode="implizit", orientierung={name: {"fallrichtung": 0, "fallwinkel": 20},
                                                        "Gibtsnicht": {"fallrichtung": 0, "fallwinkel": 5}})
    o = mit.parameter["orientierung"][0]
    assert o["quelle"] == "Eingabe" and o["fallen_grad"] == 20 and o["fallrichtung_grad"] == 0
    assert mit.parameter["orientierung"][1]["quelle"] != "Eingabe"
    assert mit.parameter["orientierung_vorgabe"] == {"0": [0.0, 20.0]}
    assert any("Gibtsnicht" in h for h in mit.hinweise)
    assert mit.max_abweichung <= implizit.TOLERANZ
    nb = len(mit.bohrungen)
    d = np.abs(mit.flaechen[1] - ohne.flaechen[1])
    assert d[:nb].max() <= 1e-6 and d.max() > 0.5            # an den Bohrungen gleich, dazwischen anders
    assert flaechen.orientierungen_holen() == {}             # nach dem Lauf keine Vorgabe uebrig
    # Kreuzprobe mit der Eingabe: eine Vorhersage entsteht mit der Vorgabe, danach ist sie wieder weg
    from baugrundanalyse.kreuzprobe import vorhersage
    f_mit, f_ohne = vorhersage(mit, 0, "implizit"), vorhersage(ohne, 0, "implizit")
    assert abs(f_mit[1] - f_ohne[1]) > 1e-3 and flaechen.orientierungen_holen() == {}
