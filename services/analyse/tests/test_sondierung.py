"""Tests fuer Issue #28: Schichtwechsel aus Sondierungen (DPH/CPT) als optionale Stuetzpunkte im Schichtmodell."""
from __future__ import annotations

import json
from pathlib import Path

import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.validate
import numpy as np
import pytest
from baugrundmodell.modell import bauen, ifc_schreiben

from baugrundanalyse.sondierung import (
    abstand_studie,
    kreuzprobe_sondierungen,
    schichtwechsel_erkennen,
    stuetzpunkte_zuordnen,
    synthetischer_fall,
)

BEISPIELE = Path(__file__).resolve().parents[3] / "data" / "beispiele"


def test_schichtwechsel_erkennen_dph_und_cpt_ignoriert_einzelstein():
    # DPH mit klarem Sprung bei 3,0 m (N10: 8 -> 28) und einer einzelnen Steinspitze bei 1,5 m
    werte_dph = [[round(0.1 * k, 2), round(0.1 * (k + 1), 2), 28.0 if k >= 30 else (30.0 if k == 15 else 8.0)]
                 for k in range(60)]
    erk = schichtwechsel_erkennen({"code": "DPH 1", "art": "DPH", "gok": 40.0, "werte": werte_dph})
    assert erk["groesse"] == "N10" and erk["hinweis"] is None
    assert len(erk["wechsel"]) == 1
    w = erk["wechsel"][0]
    assert w["tiefe_m"] == pytest.approx(3.0, abs=0.15)
    assert w["z_nhn"] == pytest.approx(37.0, abs=0.15)
    assert 0.50 <= w["konfidenz"] <= 0.95
    assert "bodenart" not in w                                 # nie eine Bodenart raten

    # CPT mit Sprung bei 4,0 m (q_c: 3,0 -> 18,0 MN/m2)
    werte_cpt = [[round(0.05 * (k + 1), 2), 18.0 if k >= 80 else 3.0, 0.1, 1.0] for k in range(140)]
    erk_c = schichtwechsel_erkennen({"code": "CPT 1", "art": "CPT", "gok": 35.0, "werte": werte_cpt})
    assert erk_c["groesse"] == "q_c" and len(erk_c["wechsel"]) == 1
    assert erk_c["wechsel"][0]["tiefe_m"] == pytest.approx(4.0, abs=0.15)


def test_ohne_sprung_wird_vollstaendig_abgelehnt():
    sf = synthetischer_fall("ohne_sprung")
    m = bauen([sf.doc])
    kp = kreuzprobe_sondierungen(m, sf.sondierungen, wahrheit=sf.fall)
    for meth in ("idw", "tps"):
        d = kp["methoden"][meth]
        assert d["stuetzpunkte_voll"] == 0
        assert d["abgelehnt_voll"] == len(sf.sondierungen)
        assert d["falsche_grenzen_voll"] == 0 and d["falsche_grenzen_loo"] == 0
        assert d["delta_mae_m"] == 0.0


@pytest.mark.parametrize("fall_name", ["rinne", "cpt_rinne"])
def test_rinne_verbessert_kreuzprobe_ohne_falsche_grenzen(fall_name):
    sf = synthetischer_fall(fall_name)
    m = bauen([sf.doc])
    kp = kreuzprobe_sondierungen(m, sf.sondierungen, wahrheit=sf.fall)
    for meth in ("idw", "tps"):
        d = kp["methoden"][meth]
        assert d["stuetzpunkte_voll"] > 0
        assert d["falsche_grenzen_voll"] == 0
        assert d["falsche_grenzen_loo"] == 0
        sand = next(e for e in d["einheiten"] if e["name"] == "Sand")
        assert sand["delta_mae_m"] < -0.20                     # deutliche Verbesserung an der Rinnenbasis


def test_linse_lehnt_mehrdeutige_wechsel_ab_null_falsche():
    sf = synthetischer_fall("linse")
    m = bauen([sf.doc])
    kp = kreuzprobe_sondierungen(m, sf.sondierungen, wahrheit=sf.fall)
    for meth in ("idw", "tps"):
        d = kp["methoden"][meth]
        assert d["abgelehnt_voll"] >= 2
        assert any("mehrdeutig" in g for g in d["ablehnungsgruende_loo"])
        assert d["falsche_grenzen_voll"] == 0
        assert d["falsche_grenzen_loo"] == 0


def test_abstand_studie_nahe_sondierung_hilft_mehr():
    studie = abstand_studie("rinne", abstaende=(5.0, 20.0, 35.0))
    mae_idw = [r["methoden"]["idw"]["mit"]["mae"] for r in studie]
    mae_tps = [r["methoden"]["tps"]["mit"]["mae"] for r in studie]
    assert mae_idw[0] < mae_idw[1] < mae_idw[2]
    assert mae_tps[0] < mae_tps[1] < mae_tps[2]
    assert all(r["methoden"]["idw"]["falsche_grenzen_loo"] == 0 for r in studie)
    assert all(r["methoden"]["tps"]["falsche_grenzen_loo"] == 0 for r in studie)


@pytest.mark.parametrize("datei", ["berlin_v67b.json", "demo_synthetisch.json"])
def test_beispiele_ohne_lage_bleiben_unveraendert(datei):
    doc = json.loads((BEISPIELE / datei).read_text(encoding="utf-8"))
    m = bauen([doc])
    kp = kreuzprobe_sondierungen(m, doc.get("sondierungen") or [])
    for meth in ("idw", "tps"):
        d = kp["methoden"][meth]
        assert d["stuetzpunkte_voll"] == 0
        assert d["abgelehnt_voll"] == len(doc.get("sondierungen") or [])
        assert d["delta_mae_m"] == 0.0


def test_modell_mit_sondierungen_standard_aus_und_ifc_gueltig(tmp_path):
    sf = synthetischer_fall("rinne")
    m_basis = bauen([sf.doc])
    assert m_basis.parameter["sondierungen_stuetzpunkte"] is False
    zuo = stuetzpunkte_zuordnen(m_basis, sf.sondierungen)
    assert zuo["stuetzpunkte"]
    assert all(p["quelle"] == "Sondierung" for p in zuo["stuetzpunkte"])

    # Standard AUS: uebergebene Zusatzpunkte bleiben wirkungslos
    m_aus = bauen([sf.doc], zusatz_stuetzpunkte=zuo["stuetzpunkte"])
    assert m_aus.parameter["sondierungen_stuetzpunkte"] is False
    assert np.array_equal(m_aus.flaechen, m_basis.flaechen)

    # Option EIN: Flaechen aendern sich zwischen den Bohrungen, Bohrkontakte bleiben exakt, IFC in METRE ohne Fehler
    m_ein = bauen([sf.doc], sondierungen_stuetzpunkte=True, zusatz_stuetzpunkte=zuo["stuetzpunkte"])
    assert m_ein.parameter["sondierungen_stuetzpunkte"] is True
    assert len(m_ein.parameter["stuetzpunkte_sondierung"]) == len(zuo["stuetzpunkte"])
    assert not np.array_equal(m_ein.flaechen, m_basis.flaechen)
    assert m_ein.max_abweichung < 1e-6
    assert all(k["pruefung"]["geschlossen"] for k in m_ein.koerper)
    assert any("Stützpunkte aus Sondierungen" in h for h in m_ein.hinweise)

    ifc_pfad = tmp_path / "rinne_sondierung.ifc"
    ifc_schreiben(m_ein, ifc_pfad, [sf.doc])
    f = ifcopenshell.open(str(ifc_pfad))
    assert ifcopenshell.util.unit.calculate_unit_scale(f) == pytest.approx(1.0)  # M17: Einheit METRE
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, logger)
    assert logger.statements == []
