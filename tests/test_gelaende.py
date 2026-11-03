"""DGM aus Dateien (services/geodaten/geodaten/gelaende.py): XYZ, ASCII-Raster, GeoTIFF, Kacheln, GOK-Pruefung."""
from __future__ import annotations

import gzip
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "geodaten"))
from geodaten import gelaende as g  # noqa: E402


def ebene(x, y):
    """Geneigtes Gelaende: bilinear wird eine Ebene exakt wiedergegeben."""
    return 30.0 + 0.01 * (x - 390000.0) + 0.02 * (y - 5820000.0)


def xyz_text(x0=390000.5, y0=5820000.5, nx=20, ny=15, d=1.0, trenner=" ", komma=False, kopf=True, f=ebene) -> bytes:
    zeilen = ["X Y Z"] if kopf else []
    for i in range(ny):
        for j in range(nx):
            x, y = x0 + j * d, y0 + i * d
            werte = [f"{x:.2f}", f"{y:.2f}", f"{f(x, y):.3f}"]
            if komma:
                werte = [w.replace(".", ",") for w in werte]
            zeilen.append(trenner.join(werte))
    return ("\n".join(zeilen) + "\n").encode()


def geotiff(z: np.ndarray, links: float, oben: float, d: float, epsg: int | None = 25832, punkt=False,
            nodata: str | None = "-9999", geografisch=False, kompression=None) -> bytes:
    from PIL import Image, TiffImagePlugin
    ifd = TiffImagePlugin.ImageFileDirectory_v2()
    ifd[33550] = (d, d, 0.0)
    ifd.tagtype[33550] = 12
    ifd[33922] = (0.0, 0.0, 0.0, links, oben, 0.0)
    ifd.tagtype[33922] = 12
    if geografisch:
        keys = (1, 1, 0, 2, 1025, 0, 1, 1, 2048, 0, 1, 4258)
    else:
        keys = (1, 1, 0, 2, 1025, 0, 1, 2 if punkt else 1, 3072, 0, 1, epsg or 32767)
    ifd[34735] = keys
    ifd.tagtype[34735] = 3
    if nodata is not None:
        ifd[42113] = nodata
        ifd.tagtype[42113] = 2
    puffer = io.BytesIO()
    Image.fromarray(z.astype(np.float32), mode="F").save(puffer, format="TIFF", tiffinfo=ifd, compression=kompression)
    return puffer.getvalue()


# ---------------------------------------------------------------- Lesen
@pytest.mark.parametrize("trenner,komma", [(" ", False), ("\t", False), (";", True), (",", False), ("\t", True)])
def test_xyz_trenner_und_dezimalkomma(trenner, komma):
    r = g.lesen("kachel.xyz", xyz_text(trenner=trenner, komma=komma))
    assert r.z.shape == (15, 20) and r.dx == pytest.approx(1.0) and r.dy == pytest.approx(1.0)
    assert r.hoehe(390007.25, 5820003.75) == pytest.approx(ebene(390007.25, 5820003.75), abs=1e-3)
    assert r.epsg is None


def test_xyz_ohne_raster_wird_abgelehnt():
    rng = np.random.default_rng(1)
    pts = rng.uniform(0, 100, size=(200, 2)) + [390000, 5820000]
    text = "\n".join(f"{x:.3f} {y:.3f} 30.0" for x, y in pts).encode()
    with pytest.raises(g.DGMFehler, match="regelmäßigen Raster"):
        g.lesen("wolke.xyz", text)


def test_ascii_raster_ecke_und_mitte_mit_nodata():
    kopf = "ncols 4\nnrows 3\nxllcorner 1000\nyllcorner 2000\ncellsize 2\nNODATA_value -9999\n"
    werte = "-9999 101 102 103\n104 105 106 107\n108 109 110 111\n"
    r = g.lesen("dgm.asc", (kopf + werte).encode())
    assert (r.x0, r.y0) == (1001.0, 2005.0)                # Mitte der Zelle oben links
    assert np.isnan(r.z[0, 0]) and r.z[1, 1] == 105
    assert r.hoehe(1003.0, 2003.0) == pytest.approx(105.0)
    assert r.hoehe(1002.0, 2004.0) is None                 # Nachbar ohne Hoehe
    mitte = "ncols 4\nnrows 3\nxllcenter 1001\nyllcenter 2001\ncellsize 2\n" + werte.replace("-9999", "100")
    r2 = g.lesen("dgm.asc", mitte.encode())
    assert (r2.x0, r2.y0) == (1001.0, 2005.0) and r2.hoehe(1001.0, 2005.0) == pytest.approx(100.0)


@pytest.mark.parametrize("kompression", [None, "tiff_lzw", "tiff_adobe_deflate"])
def test_geotiff_georeferenz_epsg_nodata(kompression):
    z = np.arange(12, dtype=np.float32).reshape(3, 4) + 100
    z[0, 0] = -9999
    r = g.lesen("dgm.tif", geotiff(z, 1000.0, 2000.0, 2.0, kompression=kompression))
    assert r.epsg == 25832 and (r.x0, r.y0, r.dx) == (1001.0, 1999.0, 2.0)   # PixelIsArea: Ecke -> Mitte
    assert np.isnan(r.z[0, 0]) and r.hoehe(1003.0, 1997.0) == pytest.approx(105.0)
    p = g.lesen("dgm.tif", geotiff(z, 1000.0, 2000.0, 2.0, punkt=True))
    assert (p.x0, p.y0) == (1000.0, 2000.0)                                    # PixelIsPoint: Passpunkt = Mitte


def test_geotiff_abgelehnt_geografisch_mehrkanalig_ohne_georeferenz():
    z = np.full((3, 4), 50.0, dtype=np.float32)
    with pytest.raises(g.DGMFehler, match="geographischen"):
        g.lesen("dgm.tif", geotiff(z, 10.0, 50.0, 0.001, geografisch=True))
    from PIL import Image
    rgb = io.BytesIO()
    Image.new("RGB", (4, 3)).save(rgb, format="TIFF")
    with pytest.raises(g.DGMFehler, match="Kanälen"):
        g.lesen("foto.tif", rgb.getvalue())
    grau = io.BytesIO()
    Image.fromarray(z, mode="F").save(grau, format="TIFF")
    with pytest.raises(g.DGMFehler, match="Georeferenz"):
        g.lesen("ohne.tif", grau.getvalue())


def test_kacheln_aus_zip_und_gz_werden_zusammengefuegt():
    a = xyz_text(x0=390000.5, nx=10, ny=10)
    b = xyz_text(x0=390010.5, nx=10, ny=10, kopf=False)
    archiv = io.BytesIO()
    with zipfile.ZipFile(archiv, "w") as zf:
        zf.writestr("dgm1_a.xyz", a)
        zf.writestr("liesmich.pdf", b"%PDF-")             # wird uebersprungen
    r = g.dateien_lesen([("kacheln.zip", archiv.getvalue()), ("dgm1_b.xyz.gz", gzip.compress(b))], epsg=25833)
    assert r.z.shape == (10, 20) and r.epsg == 25833 and np.isfinite(r.z).all()
    assert r.hoehe(390009.9, 5820004.2) == pytest.approx(ebene(390009.9, 5820004.2), abs=1e-3)   # ueber die Kachelgrenze


def test_kacheln_mit_anderer_weite_oder_anderem_system():
    a = g.lesen("a.xyz", xyz_text(d=1.0))
    b = g.lesen("b.xyz", xyz_text(x0=390100.0, d=2.0))
    with pytest.raises(g.DGMFehler, match="Rasterweite"):
        g.zusammenfuegen([a, b])
    a.epsg, c = 25832, g.lesen("c.xyz", xyz_text(x0=390050.5))
    c.epsg = 25833
    with pytest.raises(g.DGMFehler, match="verschiedenen Systemen"):
        g.zusammenfuegen([a, c])


def test_grenzen_groesse_und_plausibilitaet(monkeypatch):
    monkeypatch.setattr(g, "MAX_KNOTEN", 100)
    with pytest.raises(g.DGMFehler, match="zu groß"):
        g.lesen("gross.xyz", xyz_text(nx=20, ny=15))
    monkeypatch.setattr(g, "MAX_KNOTEN", 16_000_000)
    with pytest.raises(g.DGMFehler, match="unplausibel"):
        g.lesen("cm.xyz", xyz_text(f=lambda x, y: 123456.0))
    with pytest.raises(g.DGMFehler, match="keine DGM-Datei"):
        g.dateien_lesen([("nur.zip", _zip({"bild.png": b"x"}))])


def _zip(inhalt: dict[str, bytes]) -> bytes:
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w") as zf:
        for name, daten in inhalt.items():
            zf.writestr(name, daten)
    return puffer.getvalue()


def test_speichern_und_laden(tmp_path):
    r = g.lesen("a.xyz", xyz_text())
    r.epsg = 25832
    kopf = g.speichern(r, tmp_path / "dgm.npy")
    neu = g.laden(tmp_path / "dgm.npy", kopf)
    assert neu.epsg == 25832 and np.array_equal(neu.z, r.z)
    assert kopf["zmin"] < kopf["zmax"] and kopf["abdeckung"] == 1.0


# ---------------------------------------------------------------- GOK pruefen
def bohrung(code, x, y, gok, quelle="PDF", epsg=25832):
    return {"id": code, "code": code, "x": x, "y": y, "epsg": epsg, "gok": gok, "gok_quelle": quelle}


@pytest.fixture
def dgm():
    r = g.lesen("a.xyz", xyz_text(nx=40, ny=40))
    r.epsg = 25832
    return r


def test_gok_pruefung_status(dgm):
    x, y = 390010.0, 5820010.0
    h = ebene(x, y)
    erg = g.gok_pruefen(dgm, [
        bohrung("B1", x, y, h + 0.2), bohrung("B2", x + 5, y, ebene(x + 5, y) - 0.8),
        bohrung("B3", x, y + 5, None, ""), bohrung("B4", x + 1, y, round(ebene(x + 1, y), 2), "DGM"),
        bohrung("B5", 391000.0, y, 40.0), bohrung("B6", None, None, 40.0), bohrung("B7", x, y, 40.0, epsg=25833)])
    status = {z["code"]: z["status"] for z in erg["zeilen"]}
    assert status == {"B1": "ok", "B2": "abweichung", "B3": "ohne_gok", "B4": "aus_dgm", "B5": "ausserhalb",
                      "B6": "ohne_lage", "B7": "anderes_system"}
    assert erg["verglichen"] == 2 and erg["vorschlaege"] == 1
    texte = " ".join(erg["warnungen"])
    assert "B2" in texte and "außerhalb" in texte and "anderen System" in texte
    assert next(z for z in erg["zeilen"] if z["code"] == "B3")["dgm"] == pytest.approx(ebene(x, y + 5), abs=0.01)


def test_systematische_abweichung_verraet_lage_oder_hoehenbezug(dgm):
    pts = [(390005.0 + 3 * k, 5820005.0 + 2 * k) for k in range(5)]
    erg = g.gok_pruefen(dgm, [bohrung(f"B{k}", x, y, ebene(x, y) + 2.5 + 0.1 * k) for k, (x, y) in enumerate(pts)])
    assert erg["median"] == pytest.approx(2.7, abs=0.01)
    assert len(erg["warnungen"]) == 1 and "im Mittel 2,70 m über dem DGM" in erg["warnungen"][0]
    gemischt = g.gok_pruefen(dgm, [bohrung("A", *pts[0], ebene(*pts[0]) + 2.0), bohrung("B", *pts[1], ebene(*pts[1]) - 2.0),
                                   bohrung("C", *pts[2], ebene(*pts[2]) + 2.0)])
    assert not any("im Mittel" in w for w in gemischt["warnungen"])          # Vorzeichen gemischt: keine Systematik


def test_gok_vorschlaege_nur_ohne_gok(dgm):
    b = [bohrung("B1", 390010.0, 5820010.0, None, ""), bohrung("B2", 390012.0, 5820010.0, 31.0),
         bohrung("B3", 390014.0, 5820010.0, None, "")]
    alle = g.gok_vorschlaege(dgm, b)
    assert set(alle) == {"B1", "B3"} and alle["B1"] == pytest.approx(ebene(390010.0, 5820010.0), abs=0.01)
    assert set(g.gok_vorschlaege(dgm, b, ["B3", "B2"])) == {"B3"}
