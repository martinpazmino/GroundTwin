"""Quasigeoid GCG2016 des BKG: ellipsoidische Hoehe h (ETRS89) = Normalhoehe H (DHHN2016, m NHN) + zeta.

Gebraucht fuer 3D Tiles (Cesium rechnet ellipsoidisch): ohne zeta laege das Modell in Deutschland 34-51 m zu tief.
Quelle: PROJ-data (cdn.proj.org/de_bkg_gcg2016.tif), aus dem GCG2016 des BKG umgesetzt, CC BY 4.0, (c) BKG. Geladen
wird nur auf Abruf (Export), mit sha256 geprueft und im Arbeitsordner gehalten - nichts davon im Repository.

Gelesen ohne GDAL: TIFF mit Kacheln, Deflate und Gleitkomma-Praediktor (TIFF Technical Note 3), float32, Gitter in
Grad (ETRS89), PixelIsPoint. Bilinear wie PROJ (tests/test_tiles3d.py: gleich auf 0,1 mm).
"""
from __future__ import annotations

import hashlib
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import netz
from .netz import DienstFehler

URL = "https://cdn.proj.org/de_bkg_gcg2016.tif"
SHA256 = "598f18324dea7f8e72421d18add7ac6228259adf91eeb335cc9c27d98484f7ac"
DATEI = "de_bkg_gcg2016.tif"
ZEIT = 60
QUELLE = {"titel": "German Combined Quasigeoid 2016 (GCG2016)", "anbieter": "Bundesamt für Kartographie und Geodäsie (BKG)",
          "lizenz": "CC BY 4.0", "lizenz_url": "https://creativecommons.org/licenses/by/4.0/",
          "namensnennung": "© Bundesamt für Kartographie und Geodäsie (BKG), GCG2016, CC BY 4.0 (über PROJ-data)",
          "beleg": URL}
_TYP = {1: ("B", 1), 2: ("s", 1), 3: ("H", 2), 4: ("I", 4), 11: ("f", 4), 12: ("d", 8), 16: ("Q", 8)}


@dataclass
class Gitter:
    """Knoten (i, j) liegt bei (laenge0 + j*dlaenge, breite0 - i*dbreite); NaN = ausserhalb."""
    laenge0: float
    breite0: float
    dlaenge: float
    dbreite: float
    zeta: np.ndarray

    def werte(self, laenge, breite) -> np.ndarray:
        """zeta in m, bilinear; NaN, wo ein Nachbarknoten fehlt (ausserhalb Deutschlands)."""
        s = (np.asarray(laenge, dtype=float) - self.laenge0) / self.dlaenge
        z = (self.breite0 - np.asarray(breite, dtype=float)) / self.dbreite
        j, i = np.floor(s).astype(int), np.floor(z).astype(int)
        zeilen, spalten = self.zeta.shape
        innen = (i >= 0) & (j >= 0) & (i < zeilen - 1) & (j < spalten - 1)
        i, j = np.where(innen, i, 0), np.where(innen, j, 0)
        fs, fz = s - j, z - i
        g = self.zeta
        wert = (g[i, j] * (1 - fs) * (1 - fz) + g[i, j + 1] * fs * (1 - fz) + g[i + 1, j] * (1 - fs) * fz
                + g[i + 1, j + 1] * fs * fz)
        return np.where(innen, wert, np.nan)


def _tags(daten: bytes) -> dict[int, tuple | str]:
    if daten[:4] != b"II*\x00":
        raise ValueError("kein TIFF (little endian) – Quasigeoid-Datei beschädigt?")
    ifd = struct.unpack_from("<I", daten, 4)[0]
    tags: dict[int, tuple | str] = {}
    for k in range(struct.unpack_from("<H", daten, ifd)[0]):
        tag, typ, anzahl, wert = struct.unpack_from("<HHII", daten, ifd + 2 + 12 * k)
        if typ not in _TYP:
            continue
        zeichen, groesse = _TYP[typ]
        ort = ifd + 2 + 12 * k + 8 if groesse * anzahl <= 4 else wert
        if typ == 2:
            tags[tag] = daten[ort:ort + anzahl].rstrip(b"\x00").decode("latin-1")
        else:
            tags[tag] = struct.unpack_from(f"<{anzahl}{zeichen}", daten, ort)
    return tags


def lesen(daten: bytes) -> Gitter:
    """GCG2016 aus der GeoTIFF-Datei von PROJ-data (gekachelt, Deflate, Praediktor 3, float32)."""
    t = _tags(daten)
    breite, hoehe = t[256][0], t[257][0]
    if t.get(258, (0,))[0] != 32 or t.get(339, (0,))[0] != 3 or t.get(259, (0,))[0] not in (1, 8, 32946):
        raise ValueError("Quasigeoid: float32 mit Deflate oder ohne Kompression erwartet")
    if 322 not in t:
        raise ValueError("Quasigeoid: gekacheltes TIFF erwartet")
    kb, kh = t[322][0], t[323][0]
    praediktor, deflate = t.get(317, (1,))[0], t[259][0] != 1
    zeta = np.full((hoehe, breite), np.nan, dtype=np.float32)
    je_zeile = -(-breite // kb)
    for nr, (anfang, laenge) in enumerate(zip(t[324], t[325])):
        roh = daten[anfang:anfang + laenge]
        roh = np.frombuffer(zlib.decompress(roh) if deflate else roh, dtype=np.uint8).reshape(kh, kb * 4)
        if praediktor == 3:                          # Differenzen je Zeile aufheben, dann Bytes nach Wertigkeit
            roh = np.cumsum(roh, axis=1, dtype=np.uint64).astype(np.uint8)
            werte = np.ascontiguousarray(roh.reshape(kh, 4, kb).transpose(0, 2, 1)).view(">f4").reshape(kh, kb)
        else:
            werte = roh.view("<f4").reshape(kh, kb)
        z0, s0 = (nr // je_zeile) * kh, (nr % je_zeile) * kb
        zeta[z0:z0 + kh, s0:s0 + kb] = werte[:min(kh, hoehe - z0), :min(kb, breite - s0)]
    nodata = t.get(42113)
    if nodata:
        zeta[zeta == np.float32(float(str(nodata).strip()))] = np.nan
    dl, db = t[33550][0], t[33550][1]
    i, j, _, laenge, breite_oben, _ = t[33922][:6]
    punkt = False
    geo = t.get(34735)
    if geo:                                          # GTRasterTypeGeoKey 1025: 2 = PixelIsPoint
        for k in range(4, len(geo), 4):
            if geo[k] == 1025 and geo[k + 1] == 0:
                punkt = geo[k + 3] == 2
    laenge0, breite0 = laenge - i * dl, breite_oben + j * db
    if not punkt:                                    # PixelIsArea: Passpunkt ist die Ecke, Knoten in der Mitte
        laenge0, breite0 = laenge0 + dl / 2, breite0 - db / 2
    return Gitter(float(laenge0), float(breite0), float(dl), float(db), zeta)


_GELADEN: dict[str, Gitter] = {}


def laden(ordner: Path, holer=None) -> Gitter:
    """GCG2016 aus dem Arbeitsordner; fehlt die Datei, einmal vom PROJ-CDN holen (1 MB) und mit sha256 pruefen."""
    pfad = Path(ordner) / DATEI
    if str(pfad) in _GELADEN:
        return _GELADEN[str(pfad)]
    daten = pfad.read_bytes() if pfad.exists() else b""
    if hashlib.sha256(daten).hexdigest() != SHA256:
        try:
            daten = (holer or netz.holen)(URL, ZEIT)
        except DienstFehler as err:
            raise DienstFehler(f"Quasigeoid GCG2016 nicht geladen ({err}) – ohne Netz: {URL} in {pfad.parent} "
                               "ablegen") from None
        if hashlib.sha256(daten).hexdigest() != SHA256:
            raise DienstFehler("Quasigeoid GCG2016: Prüfsumme stimmt nicht – Datei nicht verwendet")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        zwischen = pfad.with_suffix(".tmp")
        zwischen.write_bytes(daten)
        zwischen.replace(pfad)
    _GELADEN[str(pfad)] = gitter = lesen(daten)
    return gitter
