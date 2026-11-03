"""ETRS89/UTM in Deutschland: Zonen 32 und 33, mit oder ohne Zonenkennung im Rechtswert (25832 / 4647, 25833 / 5650).

Gutachten in NRW schreiben den Rechtswert oft mit Zonenkennung (32368130), die Dienste der Laender liefern ohne
(368130). Beides ist dieselbe Lage; vermischt im Projekt lagen die Bohrungen 32 000 km auseinander (docs/16 S17).
"""
from __future__ import annotations

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
