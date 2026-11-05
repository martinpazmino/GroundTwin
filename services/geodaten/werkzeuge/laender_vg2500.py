"""Erzeugt geodaten/laender.geojson: die Grenzen der 16 Laender aus den Verwaltungsgebieten 1 : 2 500 000 (VG2500)
des BKG, vereinfacht und in WGS84 - damit die App weiss, in welchem Land ein Punkt liegt (Dienste der Laender).

VG2500 steht unter der Datenlizenz Deutschland - Namensnennung - Version 2.0 (Quellenvermerk unten, auch in der
Datei). Die Rechtecke der Dienste ueberlappen sich (ein Klick in Sachsen-Anhalt nannte Brandenburg); die Flaechen
nicht. Genauigkeit der Vereinfachung: rund 150 m (fuer die Wahl des Landes genug, nicht fuer Grenzfragen).

    python services/geodaten/werkzeuge/laender_vg2500.py [<DE_VG2500.gpkg>]
    (ohne Datei: Download von daten.gdz.bkg.bund.de in einen Zwischenordner; braucht shapely und pyproj)
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import shapely
from pyproj import Transformer
from shapely import wkb
from shapely.geometry import mapping
from shapely.ops import unary_union

QUELLE = "https://daten.gdz.bkg.bund.de/produkte/vg/vg2500/aktuell/vg2500_12-31.utm32s.gpkg.zip"
ZIEL = Path(__file__).resolve().parents[1] / "geodaten" / "laender.geojson"
TOLERANZ = 0.0015                         # Grad, rund 150 m
VERMERK = ("© BKG (2025) dl-de/by-2-0, Datenquellen: https://sgx.geodatenzentrum.de/web_public/gdz/datenquellen/"
           "datenquellen_vg_nuts.pdf; vereinfacht (rund 150 m) und nach WGS84 umgerechnet")


def _gpkg_geometrie(blob: bytes):
    """GeoPackage-Geometrie: Kopf (Magic GP, Flags, SRS, Envelope) + WKB."""
    flags = blob[3]
    umhuelle = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(flags >> 1) & 0b111]
    return wkb.loads(bytes(blob[8 + umhuelle:]))


def main(gpkg: Path | None = None) -> None:
    if gpkg is None:
        with urllib.request.urlopen(QUELLE, timeout=120) as r:
            daten = r.read()
        ordner = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(io.BytesIO(daten)) as z:
            name = next(n for n in z.namelist() if n.endswith(".gpkg"))
            z.extract(name, ordner)
        gpkg = ordner / name
    db = sqlite3.connect(gpkg)
    zeilen = db.execute("select GEN, SN_L, geom from vg2500_lan where GF = 9").fetchall()
    umrechnung = Transformer.from_crs(25832, 4326, always_xy=True)

    def nach_wgs84(xy: np.ndarray) -> np.ndarray:
        return np.column_stack(umrechnung.transform(xy[:, 0], xy[:, 1]))

    merkmale = []
    for name, schluessel, blob in sorted(zeilen, key=lambda z: z[1]):
        flaeche = unary_union(_gpkg_geometrie(blob))
        flaeche = shapely.transform(flaeche, nach_wgs84).simplify(TOLERANZ, preserve_topology=True)
        geo = json.loads(json.dumps(mapping(flaeche)), parse_float=lambda v: round(float(v), 5))
        x0, y0, x1, y1 = flaeche.bounds
        merkmale.append({"type": "Feature", "properties": {"land": name, "schluessel": schluessel,
                                                           "gebiet_wgs84": [round(x0, 4), round(y0, 4), round(x1, 4),
                                                                            round(y1, 4)]},
                         "geometry": geo})
    if len(merkmale) != 16:
        raise SystemExit(f"{len(merkmale)} Länder statt 16 – VG2500 geändert?")
    ausgabe = {"type": "FeatureCollection", "name": "laender", "quelle": QUELLE, "namensnennung": VERMERK,
               "features": merkmale}
    ZIEL.write_text(json.dumps(ausgabe, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{ZIEL} ({ZIEL.stat().st_size / 1024:.0f} KB, {len(merkmale)} Länder)")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
