"""ETRS89/UTM in Deutschland: Zonen 32 und 33, mit oder ohne Zonenkennung im Rechtswert (25832 / 4647, 25833 / 5650).

Gutachten in NRW schreiben den Rechtswert oft mit Zonenkennung (32368130), die Dienste der Laender liefern ohne
(368130). Beides ist dieselbe Lage; vermischt im Projekt lagen die Bohrungen 32 000 km auseinander (docs/16 S17).
"""
from __future__ import annotations

import numpy as np

# GRS80 (ETRS89); WGS84 weicht im Ellipsoid um < 0,1 mm in der Hoehe ab
A_GRS80 = 6378137.0
F_GRS80 = 1 / 298.257222101
_E2 = F_GRS80 * (2 - F_GRS80)
_N = F_GRS80 / (2 - F_GRS80)
_A_REKT = A_GRS80 / (1 + _N) * (1 + _N ** 2 / 4 + _N ** 4 / 64)
# Krueger-Reihen bis n^3 (Karney 2011): gegen PROJ unter 1 mm in der ganzen Zone
_BETA = (_N / 2 - 2 * _N ** 2 / 3 + 37 * _N ** 3 / 96, _N ** 2 / 48 + _N ** 3 / 15, 17 * _N ** 3 / 480)
_DELTA = (2 * _N - 2 * _N ** 2 / 3 - 2 * _N ** 3, 7 * _N ** 2 / 3 - 8 * _N ** 3 / 5, 56 * _N ** 3 / 15)
_ALPHA = (_N / 2 - 2 * _N ** 2 / 3 + 5 * _N ** 3 / 16, 13 * _N ** 2 / 48 - 3 * _N ** 3 / 5, 61 * _N ** 3 / 240)
K0 = 0.9996

_UTM = {25831: (31, 0.0), 25832: (32, 0.0), 25833: (33, 0.0), 4647: (32, 32_000_000.0), 5650: (33, 33_000_000.0)}
_NORMAL = {31: 25831, 32: 25832, 33: 25833}


def utm_normal(x: float, y: float, epsg: int) -> tuple[float, float, int]:
    """ETRS89/UTM ohne Zonenkennung im Rechtswert (4647 -> 25832, 5650 -> 25833)."""
    if int(epsg) not in _UTM:
        raise ValueError(f"EPSG:{epsg} – für die Abfrage der Länder ETRS89/UTM nötig (25832/25833)")
    zone, abzug = _UTM[int(epsg)]
    return float(x) - abzug, float(y), _NORMAL[zone]


def versatz(von, nach) -> float | None:
    """Was zum Rechtswert kommt, um von einem System ins andere derselben Zone zu kommen (0 bei gleichem System);
    None, wenn eines kein ETRS89/UTM ist oder die Zonen verschieden sind (das waere eine echte Umrechnung)."""
    try:
        (zone_von, kennung_von), (zone_nach, kennung_nach) = _UTM[int(von)], _UTM[int(nach)]
    except (KeyError, TypeError, ValueError):
        return None
    return kennung_nach - kennung_von if zone_von == zone_nach else None


def zone(epsg: int) -> int:
    """UTM-Zone eines ETRS89/UTM-Systems (25832 und 4647 -> 32)."""
    if int(epsg) not in _UTM:
        raise ValueError(f"EPSG:{epsg} ist kein ETRS89/UTM")
    return _UTM[int(epsg)][0]


def zu_geo(e, n, zone_nr: int) -> tuple[np.ndarray, np.ndarray]:
    """ETRS89/UTM (Rechtswert ohne Zonenkennung, Nordhalbkugel) -> (Laenge, Breite) in Grad, vektoriell.
    Krueger-Reihen (Karney 2011); gegen PROJ unter 1 mm, auch 4 Grad vom Mittelmeridian (tests/test_tiles3d.py)."""
    xi = np.asarray(n, dtype=float) / (K0 * _A_REKT)
    eta = (np.asarray(e, dtype=float) - 500000.0) / (K0 * _A_REKT)
    xi1, eta1 = xi.copy(), eta.copy()
    for j, b in enumerate(_BETA, start=1):
        xi1 -= b * np.sin(2 * j * xi) * np.cosh(2 * j * eta)
        eta1 -= b * np.cos(2 * j * xi) * np.sinh(2 * j * eta)
    chi = np.arcsin(np.sin(xi1) / np.cosh(eta1))
    phi = chi + sum(d * np.sin(2 * j * chi) for j, d in enumerate(_DELTA, start=1))
    lam = np.arctan2(np.sinh(eta1), np.cos(xi1))
    return np.degrees(lam) + (zone_nr * 6 - 183), np.degrees(phi)


def zone_fuer(laenge: float) -> int:
    """UTM-Zone nach der Laenge (Deutschland: 32 westlich von 12 Grad Ost, 33 oestlich)."""
    return int((float(laenge) + 180.0) // 6.0) + 1


def von_geo(laenge, breite, zone_nr: int) -> tuple[np.ndarray, np.ndarray]:
    """(Laenge, Breite) in Grad -> ETRS89/UTM (Rechtswert ohne Zonenkennung, Hochwert), vektoriell. Umkehrung von
    zu_geo (Krueger-Reihen, Karney 2011); gegen PROJ unter 1 mm (tests/test_karte.py)."""
    phi = np.radians(np.asarray(breite, dtype=float))
    lam = np.radians(np.asarray(laenge, dtype=float) - (zone_nr * 6 - 183))
    e = np.sqrt(_E2)
    t = np.sinh(np.arctanh(np.sin(phi)) - e * np.arctanh(e * np.sin(phi)))       # konforme Breite (tan)
    xi1 = np.arctan2(t, np.cos(lam))
    eta1 = np.arctanh(np.sin(lam) / np.sqrt(1 + t ** 2))
    xi, eta = xi1.copy(), eta1.copy()
    for j, a in enumerate(_ALPHA, start=1):
        xi += a * np.sin(2 * j * xi1) * np.cosh(2 * j * eta1)
        eta += a * np.cos(2 * j * xi1) * np.sinh(2 * j * eta1)
    return 500000.0 + K0 * _A_REKT * eta, K0 * _A_REKT * xi


def ecef(laenge, breite, h) -> np.ndarray:
    """Geographische Koordinaten (Grad) und ellipsoidische Hoehe (m) -> geozentrisch (X, Y, Z) in m, Form (..., 3)."""
    lam, phi = np.radians(laenge), np.radians(breite)
    h = np.asarray(h, dtype=float)
    querkruemmung = A_GRS80 / np.sqrt(1 - _E2 * np.sin(phi) ** 2)
    return np.stack([(querkruemmung + h) * np.cos(phi) * np.cos(lam), (querkruemmung + h) * np.cos(phi) * np.sin(lam),
                     (querkruemmung * (1 - _E2) + h) * np.sin(phi)], axis=-1)


def enu_basis(laenge: float, breite: float) -> np.ndarray:
    """Spalten Ost, Nord, Oben am Punkt (geozentrisch); lokal = basis.T @ (P - P0), geozentrisch = basis @ lokal + P0."""
    lam, phi = np.radians(laenge), np.radians(breite)
    return np.array([[-np.sin(lam), -np.sin(phi) * np.cos(lam), np.cos(phi) * np.cos(lam)],
                     [np.cos(lam), -np.sin(phi) * np.sin(lam), np.cos(phi) * np.sin(lam)],
                     [0.0, np.cos(phi), np.sin(phi)]])
