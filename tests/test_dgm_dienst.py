"""DGM vom Dienst des Landes (services/geodaten/geodaten/dgm_dienst.py): Ausschnitt, WCS-Anfrage, Fehler, Zonenkennung.

Die Dienste ersetzt eine Attrappe, die fuer den angefragten Ausschnitt ein GeoTIFF wie die WCS der Laender liefert
(1 m, float32, NoData -9999). Zwei Tests fragen die echten Dienste (ohne Netz: uebersprungen).
"""
from __future__ import annotations

import re
import sys
import urllib.parse
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "services" / "geodaten"), str(REPO / "tests")]
from geodaten import dgm_dienst as dd, gelaende  # noqa: E402
from geodaten.bohrdaten import DienstFehler  # noqa: E402
from test_gelaende import geotiff  # noqa: E402


def ebene(x, y):
    return 35.0 + 0.004 * (x - 394800.0) - 0.003 * (y - 5818400.0)


def attrappe(aufrufe: list | None = None, hoehe=ebene, antwort: bytes | None = None):
    """WCS GetCoverage: Ausschnitt aus SUBSET lesen, GeoTIFF (EPSG des Dienstes) zurueck; SCALEFACTOR vergroebert."""
    def holer(url: str, zeit: float) -> bytes:
        if aufrufe is not None:
            aufrufe.append(url)
        if antwort is not None:
            return antwort
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        (x0, x1), (y0, y1) = [tuple(float(v) for v in re.findall(r"\(([-\d.]+),([-\d.]+)\)", s)[0]) for s in q["SUBSET"]]
        d = 1.0 / float(q.get("SCALEFACTOR", ["1"])[0])
        system = 25833 if "isk.geobasis-bb.de" in url else 25832
        xs = np.arange(x0 + d / 2, x1, d)
        ys = np.arange(y1 - d / 2, y0, -d)
        X, Y = np.meshgrid(xs, ys)
        return geotiff(np.vectorize(hoehe)(X, Y), x0, y1, d, epsg=system)
    return holer


def test_ausschnitt_auf_ganze_meter_und_rand_begrenzt():
    assert dd.ausschnitt([(394774.3, 5818338.1), (394909.3, 5818442.5)], 100) == (394674, 5818238, 395010, 5818543)
    assert dd.ausschnitt([(100.5, 200.5)], 5000) == (-900, -800, 1101, 1201)            # Rand hoechstens 1 km


def test_abrufen_berlin_georeferenz_quelle_und_gok():
    aufrufe = []
    r, q = dd.abrufen(394674, 5818238, 395010, 5818543, 25833, holer=attrappe(aufrufe))
    assert len(aufrufe) == 1 and "COVERAGEID=bb_dgm" in aufrufe[0] and "SUBSET=x(394674,395010)" in aufrufe[0]
    assert "SCALEFACTOR" not in aufrufe[0]
    assert (r.x0, r.y0, r.dx, r.epsg) == (394674.5, 5818542.5, 1.0, 25833) and r.z.shape == (305, 336)
    assert r.hoehe(394774.3, 5818338.1) == pytest.approx(ebene(394774.3, 5818338.1), abs=1e-4)
    assert q["dienst"] == "BB-DGM1" and q["lizenz"] == "dl-de/by-2.0" and "GeoBasis-DE/LGB" in q["namensnennung"]
    assert q["ausschnitt"] == [394674.0, 5818238.0, 395010.0, 5818543.0] and q["raster_m"] == 1.0
    pr = gelaende.gok_pruefen(r, [{"id": "0:0", "code": "B1", "x": 394774.3, "y": 5818338.1, "epsg": 25833,
                                   "gok": ebene(394774.3, 5818338.1) + 0.2, "gok_quelle": "PDF"}])
    assert pr["zeilen"][0]["status"] == "ok" and pr["zeilen"][0]["differenz"] == pytest.approx(0.2, abs=0.01)


def test_zonenkennung_bleibt_im_system_des_projekts():
    r, q = dd.abrufen(32368000, 5724300, 32368300, 5724500, 4647, holer=attrappe())
    assert r.epsg == 4647 and r.x0 == pytest.approx(32368000.5) and q["dienst"] == "NW-DGM1"
    assert q["ausschnitt"][0] == 32368000.0 and q["namensnennung"].startswith("Geobasis NRW")


def test_grosser_ausschnitt_mit_groeberem_raster():
    aufrufe = []
    r, _ = dd.abrufen(390000, 5815000, 394000, 5819000, 25833, holer=attrappe(aufrufe))
    assert "SCALEFACTOR=0.5" in aufrufe[0] and r.dx == 2.0 and r.z.shape == (2000, 2000)


def test_fehler_werden_gemeldet_nicht_versteckt():
    bericht = (b'<?xml version="1.0"?><ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/2.0"><ows:Exception>'
               b'<ows:ExceptionText>Image extent does not intersect</ows:ExceptionText></ows:Exception></ows:ExceptionReport>')
    with pytest.raises(DienstFehler, match="Image extent does not intersect"):
        dd.abrufen(394674, 5818238, 395010, 5818543, 25833, holer=attrappe(antwort=bericht))
    with pytest.raises(DienstFehler, match="keine Höhen im Ausschnitt"):
        dd.abrufen(394674, 5818238, 395010, 5818543, 25833, holer=attrappe(hoehe=lambda x, y: -9999.0))
    with pytest.raises(ValueError, match="kein DGM-Dienst"):
        dd.abrufen(705000, 5300000, 705300, 5300300, 25832, holer=attrappe())          # Bayern: kein WCS
    with pytest.raises(ValueError, match="ETRS89/UTM"):
        dd.abrufen(4594700, 5818300, 4594900, 5818500, 31468, holer=attrappe())         # Gauss-Krueger


def test_ausnahme_text_aus_http_fehler():
    assert dd._ausnahme(b"<ExceptionReport><Exception><ExceptionText> Fehler  im\nDienst </ExceptionText>"
                        b"</Exception></ExceptionReport>") == "Fehler im Dienst"
    assert dd._ausnahme(b"kein xml") == ""


def _live(*args):
    try:
        return dd.abrufen(*args)
    except DienstFehler as err:
        pytest.skip(f"Dienst nicht erreichbar ({err})")


def test_live_berlin_und_nrw():
    """Echte Dienste: Gelaende am Berliner Beispiel (um 36 m NHN) und in Marl (NRW, um 60 m NHN)."""
    r, q = _live(394674, 5818238, 395010, 5818543, 25833)
    assert q["dienst"] == "BB-DGM1" and r.dx == 1.0 and 30 < r.hoehe(394774.3, 5818338.1) < 40
    r, q = _live(368000, 5724300, 368300, 5724500, 25832)
    assert q["dienst"] == "NW-DGM1" and r.dx == 1.0 and 50 < float(np.nanmean(r.z)) < 70
