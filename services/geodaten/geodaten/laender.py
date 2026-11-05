"""In welchem Land liegt ein Punkt? Grenzen der 16 Laender aus VG2500 des BKG (laender.geojson, dl-de/by-2.0,
erzeugt mit werkzeuge/laender_vg2500.py, auf rund 150 m vereinfacht).

Die Gebiete der Dienste sind Rechtecke und ueberlappen sich (ein Klick in Sachsen-Anhalt nannte Brandenburg); die
Flaechen nicht. Liegt ein Punkt in keinem Land (See, Kueste), gelten wieder die Rechtecke der Dienste.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from shapely import prepared
from shapely.geometry import Point, shape

from . import utm

DATEI = Path(__file__).with_name("laender.geojson")
LAENDER = ("Schleswig-Holstein", "Hamburg", "Niedersachsen", "Bremen", "Nordrhein-Westfalen", "Hessen",
           "Rheinland-Pfalz", "Baden-Württemberg", "Bayern", "Saarland", "Berlin", "Brandenburg",
           "Mecklenburg-Vorpommern", "Sachsen", "Sachsen-Anhalt", "Thüringen")


@lru_cache(maxsize=1)
def _flaechen() -> list[tuple[str, object, list[float]]]:
    daten = json.loads(DATEI.read_text(encoding="utf-8"))
    return [(f["properties"]["land"], prepared.prep(shape(f["geometry"])), f["properties"]["gebiet_wgs84"])
            for f in daten["features"]]


@lru_cache(maxsize=1)
def namensnennung() -> str:
    return json.loads(DATEI.read_text(encoding="utf-8"))["namensnennung"]


def gebiet(land: str) -> list[float] | None:
    """Rechteck eines Landes (WGS84: Laenge/Breite min, max)."""
    return next((g for name, _, g in _flaechen() if name == land), None)


def land_am_punkt(laenge: float, breite: float) -> str | None:
    p = Point(float(laenge), float(breite))
    return next((name for name, flaeche, _ in _flaechen() if flaeche.contains(p)), None)


def laender_um(x: float, y: float, epsg: int, radius: float = 0.0) -> list[str]:
    """Laender am Punkt (ETRS89/UTM) und, mit Radius in m, im Umkreis (acht Punkte am Rand): das Land der Mitte zuerst."""
    xn, yn, normal = utm.utm_normal(x, y, epsg)
    punkte = [(xn, yn)] + ([(xn + radius * math.cos(w), yn + radius * math.sin(w))
                            for w in (k * math.pi / 4 for k in range(8))] if radius > 0 else [])
    out: list[str] = []
    for px, py in punkte:
        laenge, breite = utm.zu_geo(px, py, utm.zone(normal))
        land = land_am_punkt(float(laenge), float(breite))
        if land and land not in out:
            out.append(land)
    return out
