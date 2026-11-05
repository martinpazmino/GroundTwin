"""Laender am Punkt (geodaten/laender.py, VG2500): Flaechen statt Rechtecke, Umkreis, Land der Mitte zuerst, Zonen.

Erster Entwurf vom Testautor des Agententeams (python -m agenten tests, docs/24 §9) mit Mutationsprobe; von Claude
geprueft und geschaerft (genaue Erwartungen, Zonen, Reihenfolge).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "services" / "geodaten")]
from geodaten import laender, utm  # noqa: E402

BERLIN_MITTE = (394774.3, 5818338.1)            # ETRS89/UTM 33, rund 13,45° O / 52,505° N


def _utm33(laenge: float, breite: float) -> tuple[float, float]:
    x, y = utm.von_geo(laenge, breite, 33)
    return float(x), float(y)


def test_land_am_punkt_flaechen_und_ausserhalb():
    assert laender.land_am_punkt(13.405, 52.52) == "Berlin"
    assert laender.land_am_punkt(11.58, 48.13) == "Bayern"
    assert laender.land_am_punkt(13.27, 52.395) == "Brandenburg"          # im Rechteck von Berlin, nicht in der Flaeche
    assert laender.land_am_punkt(2.35, 48.85) is None                     # Paris


def test_laender_um_ohne_radius_nur_die_mitte():
    assert laender.laender_um(*BERLIN_MITTE, 25833) == ["Berlin"]
    assert laender.laender_um(*BERLIN_MITTE, 25833, radius=0) == ["Berlin"]


def test_laender_um_mit_radius_ohne_doppelte_und_mitte_zuerst():
    assert laender.laender_um(*BERLIN_MITTE, 25833, radius=1000) == ["Berlin"]        # acht Randpunkte, ein Land
    assert laender.laender_um(*BERLIN_MITTE, 25833, radius=50_000) == ["Berlin", "Brandenburg"]
    assert laender.laender_um(*_utm33(13.27, 52.395), 25833, radius=5000) == ["Brandenburg", "Berlin"]


def test_laender_um_ausserhalb_ohne_none():
    assert laender.laender_um(0, 0, 25833, radius=1000) == []


def test_laender_um_zonen_und_zonenkennung():
    x32, y32 = utm.von_geo(13.4497, 52.5050, 32)                          # Berlin in Zone 32 gerechnet
    assert laender.laender_um(float(x32), float(y32), 25832) == ["Berlin"]
    assert laender.laender_um(33_000_000 + BERLIN_MITTE[0], BERLIN_MITTE[1], 5650) == ["Berlin"]   # mit Zonenkennung


def test_gebiet_und_namensnennung():
    assert all(laender.gebiet(land) is not None for land in laender.LAENDER)
    w, s, o, n = laender.gebiet("Hessen")
    assert w < 9.0 < o and s < 50.5 < n                                   # Rechteck um Frankfurt/Main
    assert laender.gebiet("Atlantis") is None
    assert "BKG" in laender.namensnennung()
