"""3D Tiles fuer Cesium (services/geodaten/geodaten/tiles3d.py, quasigeoid.py, utm.py; docs/23 §2.5, D87, Phase P6).

Vergleichswerte aus PROJ (pyproj 3.8, ETRS89, Quasigeoid de_bkg_gcg2016.tif). Ohne Netz: das Quasigeoid ist durch ein
kleines, synthetisches Gitter ersetzt (gleiches TIFF-Format: Kacheln, Deflate, Gleitkomma-Praediktor); ein Test holt
die echte Datei (ohne Netz: uebersprungen).
"""
from __future__ import annotations

import hashlib
import io
import json
import struct
import sys
import zipfile
import zlib
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "services" / "geodaten")]
from geodaten import quasigeoid as qg, tiles3d, utm  # noqa: E402
from geodaten.netz import DienstFehler  # noqa: E402

# (EPSG, Rechtswert, Hochwert, m NHN, Laenge, Breite, zeta GCG2016, X, Y, Z geozentrisch ETRS89) - aus PROJ
PROJ = [(25833, 394774.3, 5818338.1, 35.2, 13.4496729128, 52.5050027515, 39.2499, 3783872.8689, 904913.0218, 5037262.5262),
        (25832, 368130.0, 5724400.0, 60.0, 7.0936462523, 51.6551050227, 44.8611, 3934842.6618, 489667.4487, 4979169.0647),
        (25832, 800000.0, 5400000.0, 500.0, 13.0760444234, 48.6808574684, 45.5144, 4110106.0475, 954640.3050, 4767609.9355)]


@pytest.mark.parametrize("epsg,e,n,h,lon,lat,zeta,x,y,z", PROJ)
def test_utm_geographisch_geozentrisch_wie_proj(epsg, e, n, h, lon, lat, zeta, x, y, z):
    laenge, breite = utm.zu_geo(e, n, utm.zone(epsg))
    assert abs(laenge - lon) < 1e-8 and abs(breite - lat) < 1e-8                         # unter 1 mm
    assert np.abs(utm.ecef(lon, lat, h + zeta) - [x, y, z]).max() < 1e-3
    assert (utm.zone(4647), utm.zone(5650), utm.zone(25833)) == (32, 33, 33)
    with pytest.raises(ValueError, match="kein ETRS89/UTM"):
        utm.zone(31468)
    basis = utm.enu_basis(lon, lat)
    assert np.allclose(basis.T @ basis, np.eye(3)) and np.allclose(basis[:, 2], utm.ecef(lon, lat, 1.0) - utm.ecef(lon, lat, 0.0))


def tiff_gitter(werte: np.ndarray, laenge0: float, breite0: float, dl: float, db: float, kachel: int = 16) -> bytes:
    """GeoTIFF wie PROJ-data: Kacheln, Deflate, Gleitkomma-Praediktor (3), float32, PixelIsPoint, NoData -32768."""
    zeilen, spalten = werte.shape
    kacheln = []
    for z0 in range(0, zeilen, kachel):
        for s0 in range(0, spalten, kachel):
            k = np.full((kachel, kachel), -32768.0, dtype=">f4")
            teil = werte[z0:z0 + kachel, s0:s0 + kachel]
            k[:teil.shape[0], :teil.shape[1]] = teil
            ebenen = k.view(np.uint8).reshape(kachel, kachel, 4).transpose(0, 2, 1).reshape(kachel, kachel * 4)
            diff = np.diff(ebenen.astype(np.int16), axis=1, prepend=0).astype(np.uint8)
            kacheln.append(zlib.compress(diff.tobytes()))
    tags = [(256, 4, [spalten]), (257, 4, [zeilen]), (258, 3, [32]), (259, 3, [8]), (277, 3, [1]), (317, 3, [3]),
            (322, 3, [kachel]), (323, 3, [kachel]), (324, 4, None), (325, 4, [len(k) for k in kacheln]), (339, 3, [3]),
            (33550, 12, [dl, db, 0.0]), (33922, 12, [0.0, 0.0, 0.0, laenge0, breite0, 0.0]),
            (34735, 3, [1, 1, 0, 1, 1025, 0, 1, 2]), (42113, 2, b"-32768\x00")]
    kopf = 8
    ifd_laenge = 2 + 12 * len(tags) + 4
    daten_ort = kopf + ifd_laenge
    zusatz, eintraege = bytearray(), []
    kachel_ort = daten_ort + 4096                     # Platz fuer die Zusatzwerte davor
    offsets = []
    for k in kacheln:
        offsets.append(kachel_ort)
        kachel_ort += len(k)
    for tag, typ, werte_t in tags:
        if tag == 324:
            werte_t = offsets
        if typ == 2:
            roh = werte_t
            anzahl = len(roh)
        else:
            zeichen = {3: "H", 4: "I", 12: "d"}[typ]
            roh = struct.pack(f"<{len(werte_t)}{zeichen}", *werte_t)
            anzahl = len(werte_t)
        if len(roh) <= 4:
            eintraege.append(struct.pack("<HHI", tag, typ, anzahl) + roh.ljust(4, b"\x00"))
        else:
            eintraege.append(struct.pack("<HHII", tag, typ, anzahl, daten_ort + len(zusatz)))
            zusatz.extend(roh)
            zusatz.extend(b"\x00" * (len(zusatz) % 2))
    assert len(zusatz) < 4096
    ifd = struct.pack("<H", len(tags)) + b"".join(eintraege) + struct.pack("<I", 0)
    datei = b"II*\x00" + struct.pack("<I", kopf) + ifd + bytes(zusatz).ljust(4096, b"\x00") + b"".join(kacheln)
    return datei


def deutschland_gitter(zeta=lambda lon, lat: 40.0 + 0.5 * (lon - 10) - 0.25 * (lat - 51)) -> bytes:
    """Grobes Gitter ueber Deutschland (0,5 Grad), Werte als Ebene - bilinear exakt."""
    lon = 5.0 + 0.5 * np.arange(21)
    lat = 56.0 - 0.5 * np.arange(22)
    werte = np.array([[zeta(lo, la) for lo in lon] for la in lat], dtype=np.float32)
    return tiff_gitter(werte, 5.0, 56.0, 0.5, 0.5)


def test_quasigeoid_lesen_wie_geschrieben():
    g = qg.lesen(deutschland_gitter())
    assert (g.laenge0, g.breite0, g.dlaenge, g.dbreite, g.zeta.shape) == (5.0, 56.0, 0.5, 0.5, (22, 21))
    w = g.werte([10.0, 13.4497, 7.0936, 4.0], [51.0, 52.505, 51.655, 51.0])
    assert w[0] == pytest.approx(40.0) and w[1] == pytest.approx(40.0 + 0.5 * 3.4497 - 0.25 * 1.505, abs=1e-5)
    assert np.isnan(w[3])                                                              # westlich des Gitters


def test_quasigeoid_laden_pruefsumme_und_zwischenspeicher(tmp_path, monkeypatch):
    daten = deutschland_gitter()
    monkeypatch.setattr(qg, "SHA256", hashlib.sha256(daten).hexdigest())
    monkeypatch.setattr(qg, "_GELADEN", {})
    aufrufe = []

    def holer(url, zeit):
        aufrufe.append(url)
        return daten
    g = qg.laden(tmp_path, holer=holer)
    assert aufrufe == [qg.URL] and (tmp_path / qg.DATEI).read_bytes() == daten and g.zeta.shape == (22, 21)
    monkeypatch.setattr(qg, "_GELADEN", {})
    qg.laden(tmp_path, holer=holer)
    assert len(aufrufe) == 1                                                           # aus dem Arbeitsordner
    monkeypatch.setattr(qg, "_GELADEN", {})
    (tmp_path / qg.DATEI).unlink()
    with pytest.raises(DienstFehler, match="Prüfsumme stimmt nicht"):
        qg.laden(tmp_path, holer=lambda url, zeit: daten + b"x")
    assert not (tmp_path / qg.DATEI).exists()
    with pytest.raises(DienstFehler, match="nicht geladen .* ablegen"):
        qg.laden(tmp_path, holer=lambda url, zeit: (_ for _ in ()).throw(DienstFehler("keine Antwort in 60 s")))


def test_quasigeoid_echt_wie_proj(tmp_path, monkeypatch):
    """Die echte Datei vom PROJ-CDN (1 MB): zeta wie PROJ auf 0,1 mm."""
    monkeypatch.setattr(qg, "_GELADEN", {})
    try:
        g = qg.laden(tmp_path)
    except DienstFehler as err:
        pytest.skip(f"PROJ-CDN nicht erreichbar ({err})")
    for _, _, _, _, lon, lat, zeta, *_ in PROJ:
        assert float(g.werte(lon, lat)) == pytest.approx(zeta, abs=1e-4)
    assert np.isnan(g.werte(6.1945, 47.8190))                                           # Schweiz: ausserhalb


# ---------------------------------------------------------------- Export ueber die App
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402

ZETA = 40.0


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    daten = deutschland_gitter(lambda lon, lat: ZETA)
    monkeypatch.setattr(qg, "SHA256", hashlib.sha256(daten).hexdigest())
    monkeypatch.setattr(qg, "_GELADEN", {})
    monkeypatch.setattr(qg.netz, "holen", lambda url, zeit: daten)
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c


def glb_lesen(daten: bytes) -> tuple[dict, bytes]:
    magie, version, laenge = struct.unpack_from("<4sII", daten, 0)
    assert magie == b"glTF" and version == 2 and laenge == len(daten)
    jl, jt = struct.unpack_from("<I4s", daten, 12)
    assert jt == b"JSON"
    gltf = json.loads(daten[20:20 + jl])
    bl, bt = struct.unpack_from("<I4s", daten, 20 + jl)
    assert bt == b"BIN\x00" and gltf["buffers"][0]["byteLength"] == bl
    return gltf, daten[28 + jl:28 + jl + bl]


def punkte(gltf: dict, binaer: bytes) -> np.ndarray:
    alle = []
    for netz in gltf["meshes"]:
        z = gltf["accessors"][netz["primitives"][0]["attributes"]["POSITION"]]
        sicht = gltf["bufferViews"][z["bufferView"]]
        p = np.frombuffer(binaer, dtype="<f4", count=z["count"] * 3, offset=sicht["byteOffset"]).reshape(-1, 3)
        assert np.allclose(p.min(0), z["min"], atol=1e-4) and np.allclose(p.max(0), z["max"], atol=1e-4)
        alle.append(p)
    return np.vstack(alle)


def test_export_3dtiles_berlin_lage_und_hoehe_wie_proj(client):
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    r = client.get(f"/api/projekt/{sig}/export/3dtiles")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/zip" and "_3dtiles.zip" in r.headers["content-disposition"]
    z = zipfile.ZipFile(io.BytesIO(r.content))
    assert sorted(z.namelist()) == ["LIESMICH.txt", "baugrundmodell.glb", "tileset.json"]
    ts = json.loads(z.read("tileset.json"))
    assert ts["asset"]["version"] == "1.1" and ts["root"]["refine"] == "ADD"
    assert "GCG2016" in ts["asset"]["extras"]["Hoehenbezug"] and "BKG" in ts["asset"]["extras"]["Namensnennung"][0]
    gltf, binaer = glb_lesen(z.read("baugrundmodell.glb"))
    namen = {k["extras"]["IFC"] for k in gltf["nodes"]}
    assert namen == {"IfcGeotechnicalStratum"} and all(m["doubleSided"] for m in gltf["materials"])
    # jeder Punkt: glTF (y oben) -> z oben -> Kacheltransformation -> geozentrisch
    lokal = punkte(gltf, binaer)
    enu = np.column_stack([lokal[:, 0], -lokal[:, 2], lokal[:, 1]])
    t = np.array(ts["root"]["transform"]).reshape(4, 4).T
    geoz = enu @ t[:3, :3].T + t[:3, 3]
    # 422C-460 (Rechtswert 394774.3, Hochwert 5818338.1, GOK 36.25 m NHN): Lage aus PROJ, Hoehe + zeta
    soll = utm.ecef(13.4496729128, 52.5050027515, 36.25 + ZETA)
    oben = utm.enu_basis(13.4496729128, 52.5050027515)[:, 2]
    d = geoz - soll
    hoehe, waagrecht = d @ oben, np.linalg.norm(d - np.outer(d @ oben, oben), axis=1)
    nah = waagrecht < 1.0
    assert nah.any() and abs(hoehe[nah].max()) < 0.01                                  # Oberkante auf der GOK, auf 1 cm
    assert (z.read("LIESMICH.txt").decode("utf-8")).startswith("GroundTwin – Baugrundmodell als 3D Tiles 1.1")


def test_export_3dtiles_nur_mit_utm(client):
    sig = client.post("/api/beispiel", json={"name": "talheim"}).json()["projekt"]
    r = client.get(f"/api/projekt/{sig}/export/3dtiles")
    assert r.status_code == 400 and "nur mit Lage nach Koordinaten" in r.json()["detail"]


def test_export_3dtiles_ausserhalb_des_quasigeoids(client, monkeypatch):
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    leer = tiff_gitter(np.full((4, 4), -32768.0, dtype=np.float32), 5.0, 56.0, 0.5, 0.5)
    monkeypatch.setattr(qg, "SHA256", hashlib.sha256(leer).hexdigest())
    monkeypatch.setattr(qg, "_GELADEN", {})
    for datei in Path(client.app.state.arbeitsplatz.arbeit, "cache").glob("*.tif"):
        datei.unlink()
    monkeypatch.setattr(qg.netz, "holen", lambda url, zeit: leer)
    r = client.get(f"/api/projekt/{sig}/export/3dtiles")
    assert r.status_code == 400 and "außerhalb des Quasigeoids GCG2016" in r.json()["detail"]


def test_glb_gueltig_und_kasten():
    """Kleines GLB: Ausrichtung auf 4 Byte, min/max, ein Material je Farbe; Quader mit Mindestgroesse."""
    teil = {"klasse": "IfcGeotechnicalStratum", "guid": "x", "name": "Sand", "beschreibung": "",
            "gltf": np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float), "flaechen": np.array([[0, 1, 2]], dtype=np.uint32),
            "material": np.array([0]), "farben": [(1.0, 0.5, 0.0, 1.0)]}
    gltf, binaer = glb_lesen(tiles3d._glb([teil]))
    assert len(binaer) % 4 == 0 and gltf["materials"][0]["pbrMetallicRoughness"]["baseColorFactor"][1] == round(0.5 ** 2.2, 4)
    assert gltf["accessors"][1]["componentType"] == 5125 and gltf["accessors"][1]["count"] == 3
    assert tiles3d._kasten(np.array([[0, 0, 5], [10, 0, 5]], dtype=float))[3:] == [5.0, 0, 0, 0, 0.01, 0, 0, 0, 0.01]
