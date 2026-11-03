"""Digitales Gelaendemodell (DGM) aus Dateien, die der Nutzer selbst herunterlaedt (Open Data der Laender, docs/23
§2.4): XYZ-Text, ESRI-ASCII-Raster (.asc) oder GeoTIFF, auch als ZIP/GZ und in mehreren Kacheln. Ohne Netz und ohne
GDAL: numpy und Pillow. Hoehen in m NHN wie die GOK der Gutachten; das Koordinatensystem steht nur im GeoTIFF, sonst
gibt es der Nutzer an.

Wofuer: die GOK aus dem PDF gegen das Gelaende pruefen (eine systematische Abweichung verraet eine falsche Lage, ein
falsches EPSG oder einen anderen Hoehenbezug) und eine fehlende GOK vorschlagen. Ein Vorschlag wird nie still
uebernommen (docs/16: ein zweifelhafter Wert wird markiert, nicht versteckt).
"""
from __future__ import annotations

import gzip
import io
import math
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

MAX_KNOTEN = 16_000_000          # 4 x 4 km bei 1 m Raster; fuer lange Trassen ein groeberes DGM (DGM5) nehmen
MAX_ENTPACKT = 700 * 1024 ** 2   # Bytes je entpackter Datei (Schutz vor Zip-Bomben)
TOL_OK = 0.5                     # m: |GOK - DGM| bis hierher unauffaellig (DGM1 ca. +-0,2 m, Aushub, Bewuchs)
TOL_SYSTEMATISCH = 1.0           # m: Median aller Abweichungen, ab dem Lage, EPSG oder Hoehenbezug verdaechtig sind
HOEHE_MIN, HOEHE_MAX = -500.0, 9000.0   # plausible Hoehen in m (sonst Einheit oder NoData falsch)
NODATA_TYPISCH = (-9999.0, -99999.0, -32767.0, -32768.0)
ENDUNGEN = (".xyz", ".txt", ".csv", ".asc", ".tif", ".tiff")


def _de(v: float, stellen: int = 2) -> str:
    """Zahl wie in der Oberflaeche (Dezimalkomma)."""
    return f"{v:.{stellen}f}".replace(".", ",")


class DGMFehler(ValueError):
    """Die Datei ist kein lesbares DGM; die Meldung geht so an die Oberflaeche."""


@dataclass
class Raster:
    """Regelmaessiges Gitter: Knoten (i, j) liegt bei (x0 + j*dx, y0 - i*dy); Zeile 0 ist der noerdlichste Rand."""
    x0: float
    y0: float
    dx: float
    dy: float
    z: np.ndarray                 # float32 (zeilen, spalten), NaN = keine Hoehe
    epsg: int | None = None

    def ausdehnung(self) -> tuple[float, float, float, float]:
        """(x_min, y_min, x_max, y_max) der Knoten."""
        zeilen, spalten = self.z.shape
        return (self.x0, self.y0 - (zeilen - 1) * self.dy, self.x0 + (spalten - 1) * self.dx, self.y0)

    def hoehe(self, x: float, y: float) -> float | None:
        """Bilinear zwischen den vier Nachbarknoten; None ausserhalb oder wenn ein beteiligter Knoten keine Hoehe hat."""
        zeilen, spalten = self.z.shape
        fj, fi = (x - self.x0) / self.dx, (self.y0 - y) / self.dy
        rand = 1e-6
        if not (-rand <= fj <= spalten - 1 + rand and -rand <= fi <= zeilen - 1 + rand):
            return None
        j0 = min(max(int(math.floor(fj)), 0), max(spalten - 2, 0))
        i0 = min(max(int(math.floor(fi)), 0), max(zeilen - 2, 0))
        j1, i1 = min(j0 + 1, spalten - 1), min(i0 + 1, zeilen - 1)
        tj = min(max(fj - j0, 0.0), 1.0) if j1 > j0 else 0.0
        ti = min(max(fi - i0, 0.0), 1.0) if i1 > i0 else 0.0
        summe = gewicht = 0.0
        for i, j, w in ((i0, j0, (1 - ti) * (1 - tj)), (i0, j1, (1 - ti) * tj), (i1, j0, ti * (1 - tj)), (i1, j1, ti * tj)):
            if w <= 1e-12:
                continue
            v = float(self.z[i, j])
            if v != v:                                    # NaN: Luecke im DGM
                return None
            summe += w * v
            gewicht += w
        return summe / gewicht if gewicht > 0 else None

    def info(self) -> dict:
        """Kurzbeschreibung fuer Projekt und Oberflaeche."""
        zeilen, spalten = self.z.shape
        gueltig = np.isfinite(self.z)
        return {"epsg": self.epsg, "dx": self.dx, "dy": self.dy, "zeilen": int(zeilen), "spalten": int(spalten),
                "x0": self.x0, "y0": self.y0, "ausdehnung": [round(v, 3) for v in self.ausdehnung()],
                "zmin": round(float(np.nanmin(self.z)), 2) if gueltig.any() else None,
                "zmax": round(float(np.nanmax(self.z)), 2) if gueltig.any() else None,
                "abdeckung": round(float(gueltig.mean()), 4)}


# ---------------------------------------------------------------- Lesen
def dateien_lesen(dateien: list[tuple[str, bytes]], epsg: int | None = None) -> Raster:
    """Eine oder mehrere Dateien (auch ZIP/GZ) lesen und zu einem Raster zusammenfuegen."""
    teile = []
    for name, daten in _entpacken(dateien):
        try:
            teile.append(lesen(name, daten))
        except DGMFehler as err:
            raise DGMFehler(f"{name}: {err}") from None
    if not teile:
        raise DGMFehler("keine DGM-Datei gefunden (XYZ, ASCII-Raster .asc oder GeoTIFF)")
    r = teile[0] if len(teile) == 1 else zusammenfuegen(teile)
    if r.epsg is None and epsg:
        r.epsg = int(epsg)
    return r


def _entpacken(dateien: list[tuple[str, bytes]]):
    for name, daten in dateien:
        klein = name.lower()
        if klein.endswith(".zip") or daten[:4] == b"PK\x03\x04":
            try:
                archiv = zipfile.ZipFile(io.BytesIO(daten))
            except zipfile.BadZipFile as err:
                raise DGMFehler(f"{name}: ZIP nicht lesbar") from err
            for eintrag in archiv.infolist():
                if eintrag.is_dir() or not eintrag.filename.lower().endswith(ENDUNGEN + (".gz",)):
                    continue
                if eintrag.file_size > MAX_ENTPACKT:
                    raise DGMFehler(f"{eintrag.filename}: zu groß ({eintrag.file_size / 1024 ** 2:.0f} MB entpackt)")
                yield from _entpacken([(eintrag.filename, archiv.read(eintrag))])
        elif klein.endswith(".gz") or daten[:2] == b"\x1f\x8b":
            try:
                inhalt = gzip.GzipFile(fileobj=io.BytesIO(daten)).read(MAX_ENTPACKT + 1)
            except OSError as err:
                raise DGMFehler(f"{name}: GZ nicht lesbar") from err
            if len(inhalt) > MAX_ENTPACKT:
                raise DGMFehler(f"{name}: zu groß entpackt")
            yield name[:-3] if klein.endswith(".gz") else name, inhalt
        else:
            yield name, daten


def lesen(name: str, daten: bytes) -> Raster:
    """Eine Datei nach Inhalt (sonst Endung) lesen."""
    if daten[:4] in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
        r = _geotiff(daten)
    elif re.match(rb"\s*ncols\b", daten[:64], re.IGNORECASE) or Path(name).suffix.lower() == ".asc":
        r = _ascii_raster(daten)
    else:
        r = _xyz(daten)
    _nodata_und_plausibel(r)
    return r


def _nodata_und_plausibel(r: Raster, nodata: float | None = None) -> None:
    z = r.z
    for wert in ((nodata,) if nodata is not None else ()) + NODATA_TYPISCH:
        z[z == np.float32(wert)] = np.nan
    z[z < -1e30] = np.nan
    if not np.isfinite(z).any():
        raise DGMFehler("keine gültige Höhe in der Datei")
    zmin, zmax = float(np.nanmin(z)), float(np.nanmax(z))
    if zmin < HOEHE_MIN or zmax > HOEHE_MAX:
        raise DGMFehler(f"Höhen {_de(zmin, 1)} … {_de(zmax, 1)} unplausibel – in Metern? NoData-Wert?")


def _zahlen(text: bytes, spalten: int | None) -> np.ndarray:
    """Zahlenblock (Leerzeichen, Tab, Semikolon oder Komma als Trenner; Dezimalkomma bei Semikolon/Tab)."""
    probe = text[:4096]
    if b";" in probe:
        text = text.replace(b",", b".").replace(b";", b" ")
    elif b"," in probe:
        zeile = probe.strip().split(b"\n")[0]
        if b"." in zeile or len(zeile.split()) < 2:   # 390000.5,5820000.5,34.2 -> Komma trennt
            text = text.replace(b",", b" ")
        else:                                          # 390000,5 5820000,5 34,2 -> Dezimalkomma
            text = text.replace(b",", b".")
    try:
        werte = np.loadtxt(io.BytesIO(text), dtype=np.float64, ndmin=2,
                           usecols=tuple(range(spalten)) if spalten else None)
    except ValueError as err:
        raise DGMFehler("Zahlen nicht lesbar") from err
    return werte


def _xyz(daten: bytes) -> Raster:
    """XYZ-Text: eine Zeile je Rasterpunkt 'x y z' (Kopfzeilen ohne Zahlen werden uebersprungen)."""
    zeilen = daten.split(b"\n", 50)
    start = 0
    for k, zeile in enumerate(zeilen[:50]):
        if re.match(rb"\s*[-+]?\d", zeile):
            start = k
            break
    else:
        raise DGMFehler("keine Zahlenzeilen (x y z)")
    rumpf = b"\n".join(zeilen[start:]) if start else daten
    werte = _zahlen(rumpf, 3)
    if werte.shape[1] < 3:
        raise DGMFehler("XYZ braucht drei Spalten x y z")
    x, y, z = werte[:, 0], werte[:, 1], werte[:, 2]
    if len(x) < 4:
        raise DGMFehler("zu wenige Punkte")
    dx, dy = _abstand(x), _abstand(y)
    xmin, ymax = float(x.min()), float(y.max())
    fj, fi = (x - xmin) / dx, (ymax - y) / dy
    j, i = np.rint(fj).astype(np.int64), np.rint(fi).astype(np.int64)
    daneben = (np.abs(fj - j) > 0.01) | (np.abs(fi - i) > 0.01)
    if daneben.mean() > 0.001:
        raise DGMFehler("die Punkte liegen auf keinem regelmäßigen Raster")
    spalten, zeilen_n = int(j.max()) + 1, int(i.max()) + 1
    _knoten_pruefen(zeilen_n, spalten, dx)
    gitter = np.full((zeilen_n, spalten), np.nan, dtype=np.float32)
    gitter[i[~daneben], j[~daneben]] = z[~daneben]
    return Raster(xmin, ymax, dx, dy, gitter)


def _abstand(werte: np.ndarray) -> float:
    """Rasterweite aus den Koordinaten einer Achse (haeufigster Abstand benachbarter Werte)."""
    u = np.unique(np.round(werte, 3))
    if len(u) < 2:
        raise DGMFehler("alle Punkte auf einer Linie – kein Raster")
    d = np.diff(u)
    d = d[d > 1e-6]
    werte_, anzahl = np.unique(np.round(d, 3), return_counts=True)
    weite = float(werte_[np.argmax(anzahl)])
    if weite <= 0:
        raise DGMFehler("Rasterweite nicht bestimmbar")
    return weite


def _knoten_pruefen(zeilen: int, spalten: int, dx: float) -> None:
    if zeilen * spalten > MAX_KNOTEN:
        raise DGMFehler(f"zu groß: {spalten} × {zeilen} Knoten bei {dx:g} m – höchstens "
                        f"{MAX_KNOTEN / 1e6:.0f} Mio. (Kacheln nur um die Bohrungen wählen oder ein gröberes DGM)")


def _ascii_raster(daten: bytes) -> Raster:
    """ESRI-ASCII-Raster: Kopf (ncols, nrows, xllcorner|xllcenter, yll…, cellsize, NODATA_value), Zeilen von Nord."""
    kopf: dict[str, float] = {}
    rest = daten
    while True:
        zeile, _, danach = rest.partition(b"\n")
        teile = zeile.split()
        if len(teile) == 2 and re.match(rb"[A-Za-z_]+$", teile[0]):
            try:
                kopf[teile[0].decode().lower()] = float(teile[1].replace(b",", b"."))
            except ValueError as err:
                raise DGMFehler("Kopf des ASCII-Rasters nicht lesbar") from err
            rest = danach
            continue
        break
    try:
        spalten, zeilen = int(kopf["ncols"]), int(kopf["nrows"])
        weite = kopf.get("cellsize") or kopf["dx"]
    except KeyError as err:
        raise DGMFehler(f"Kopf des ASCII-Rasters unvollständig ({err.args[0]} fehlt)") from None
    weite_y = kopf.get("dy", weite)
    _knoten_pruefen(zeilen, spalten, weite)
    if "xllcenter" in kopf:
        x0 = kopf["xllcenter"]
        y0 = kopf["yllcenter"] + (zeilen - 1) * weite_y
    else:
        x0 = kopf["xllcorner"] + weite / 2
        y0 = kopf["yllcorner"] + (zeilen - 0.5) * weite_y
    werte = _zahlen(rest, None).astype(np.float32).ravel()
    if werte.size != zeilen * spalten:
        raise DGMFehler(f"{werte.size} Werte statt {zeilen} × {spalten}")
    r = Raster(float(x0), float(y0), float(weite), float(weite_y), werte.reshape(zeilen, spalten))
    if "nodata_value" in kopf:
        r.z[r.z == np.float32(kopf["nodata_value"])] = np.nan
    return r


# GeoTIFF: Tags und GeoKeys (OGC GeoTIFF 1.1)
_TAG_SKALA, _TAG_PASSPUNKT, _TAG_MATRIX, _TAG_GEOKEYS, _TAG_NODATA = 33550, 33922, 34264, 34735, 42113
_KEY_RASTERTYP, _KEY_GEOGRAFISCH, _KEY_PROJIZIERT = 1025, 2048, 3072


def _geokeys(werte) -> dict[int, int]:
    werte = list(werte or [])
    if len(werte) < 4:
        return {}
    out = {}
    for k in range(int(werte[3])):
        eintrag = werte[4 + 4 * k: 8 + 4 * k]
        if len(eintrag) == 4 and eintrag[1] == 0:          # Wert steht direkt im Verzeichnis
            out[int(eintrag[0])] = int(eintrag[3])
    return out


def _geotiff(daten: bytes) -> Raster:
    from PIL import Image                                  # Pillow ist ohnehin Abhaengigkeit des Servers

    try:
        bild = Image.open(io.BytesIO(daten))
        tags = dict(bild.tag_v2)
        if len(bild.getbands()) != 1:
            raise DGMFehler("GeoTIFF mit mehreren Kanälen ist ein Bild, kein DGM (Höhen als ein Kanal erwartet)")
        spalten, zeilen = bild.size
        _knoten_pruefen(zeilen, spalten, float((tags.get(_TAG_SKALA) or (1.0,))[0]))   # vor dem Dekodieren
        z = np.asarray(bild, dtype=np.float32).copy()
    except DGMFehler:
        raise
    except Exception as err:                               # Pillow kennt manche Kompressionen/Kachelungen nicht
        raise DGMFehler(f"GeoTIFF nicht lesbar ({type(err).__name__}) – als XYZ oder ASCII-Raster exportieren") from err
    keys = _geokeys(tags.get(_TAG_GEOKEYS))
    epsg = keys.get(_KEY_PROJIZIERT)
    if epsg in (None, 0, 32767):
        if keys.get(_KEY_GEOGRAFISCH):
            raise DGMFehler("DGM in geographischen Koordinaten (Grad) – bitte in UTM/Gauß-Krüger (m)")
        epsg = None
    punkt = keys.get(_KEY_RASTERTYP, 1) == 2               # PixelIsPoint: Passpunkt ist die Pixelmitte
    if _TAG_MATRIX in tags:
        m = [float(v) for v in tags[_TAG_MATRIX]]
        if abs(m[1]) > 1e-9 or abs(m[4]) > 1e-9:
            raise DGMFehler("gedrehtes GeoTIFF wird nicht unterstützt")
        dx, dy, links, oben = m[0], -m[5], m[3], m[7]
    elif _TAG_SKALA in tags and _TAG_PASSPUNKT in tags:
        sx, sy = float(tags[_TAG_SKALA][0]), float(tags[_TAG_SKALA][1])
        i, j, _, x, y, _ = (float(v) for v in tags[_TAG_PASSPUNKT][:6])
        dx, dy, links, oben = sx, sy, x - i * sx, y + j * sy
    else:
        raise DGMFehler("TIFF ohne Georeferenz (GeoTIFF-Tags fehlen)")
    if dx <= 0 or dy <= 0:
        raise DGMFehler("Rasterweite im GeoTIFF ungültig")
    x0, y0 = (links, oben) if punkt else (links + dx / 2, oben - dy / 2)
    r = Raster(float(x0), float(y0), float(dx), float(dy), z, epsg)
    nodata = tags.get(_TAG_NODATA)
    if nodata not in (None, ""):
        try:
            r.z[r.z == np.float32(float(str(nodata).strip("\x00 ")))] = np.nan
        except ValueError:
            pass
    return r


def zusammenfuegen(teile: list[Raster]) -> Raster:
    """Kacheln mit gleicher Rasterweite und auf demselben Gitter zu einem Raster."""
    a = teile[0]
    epsgs = {t.epsg for t in teile if t.epsg}
    if len(epsgs) > 1:
        raise DGMFehler(f"Kacheln in verschiedenen Systemen: {', '.join(f'EPSG:{e}' for e in sorted(epsgs))}")
    for t in teile[1:]:
        if abs(t.dx - a.dx) > 1e-6 * a.dx or abs(t.dy - a.dy) > 1e-6 * a.dy:
            raise DGMFehler(f"Kacheln mit verschiedener Rasterweite ({a.dx:g} m und {t.dx:g} m)")
        for d in ((t.x0 - a.x0) / a.dx, (a.y0 - t.y0) / a.dy):
            if abs(d - round(d)) > 0.01:
                raise DGMFehler("Kacheln liegen nicht auf demselben Raster")
    x0 = min(t.x0 for t in teile)
    y0 = max(t.y0 for t in teile)
    x1 = max(t.ausdehnung()[2] for t in teile)
    y1 = min(t.ausdehnung()[1] for t in teile)
    spalten, zeilen = int(round((x1 - x0) / a.dx)) + 1, int(round((y0 - y1) / a.dy)) + 1
    _knoten_pruefen(zeilen, spalten, a.dx)
    gitter = np.full((zeilen, spalten), np.nan, dtype=np.float32)
    for t in teile:
        j, i = int(round((t.x0 - x0) / a.dx)), int(round((y0 - t.y0) / a.dy))
        h, w = t.z.shape
        ziel = gitter[i:i + h, j:j + w]
        np.copyto(ziel, t.z, where=np.isfinite(t.z))
    return Raster(x0, y0, a.dx, a.dy, gitter, epsgs.pop() if epsgs else None)


# ---------------------------------------------------------------- Speichern (Projektordner)
def speichern(r: Raster, pfad: Path) -> dict:
    """Raster als .npy (schnell wieder geladen) und Kopfdaten fuer das Projekt."""
    pfad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pfad.with_suffix(".tmp.npy")
    np.save(tmp, r.z)
    tmp.replace(pfad)
    return r.info()


def laden(pfad: Path, kopf: dict) -> Raster:
    return Raster(float(kopf["x0"]), float(kopf["y0"]), float(kopf["dx"]), float(kopf["dy"]),
                  np.load(pfad), kopf.get("epsg"))


# ---------------------------------------------------------------- GOK pruefen und vorschlagen
def gok_pruefen(r: Raster, bohrungen: list[dict]) -> dict:
    """GOK der Bohrungen gegen das DGM.

    bohrungen: {id, code, x, y, epsg, gok, gok_quelle}. Je Bohrung ein Status: ok, abweichung (|GOK - DGM| > TOL_OK),
    ohne_gok (mit Vorschlag), aus_dgm (GOK schon aus dem DGM), ausserhalb, ohne_lage, anderes_system. Dazu Warnungen:
    systematische Abweichung (Median > TOL_SYSTEMATISCH, gleiches Vorzeichen) und Bohrungen ausserhalb.
    """
    zeilen, abw = [], []
    for b in bohrungen:
        z = {"id": b["id"], "code": b["code"], "gok": b.get("gok"), "dgm": None, "differenz": None}
        x, y = b.get("x"), b.get("y")
        if x is None or y is None:
            z["status"] = "ohne_lage"
        elif b.get("epsg") and r.epsg and int(b["epsg"]) != int(r.epsg):
            z["status"] = "anderes_system"
        else:
            h = r.hoehe(float(x), float(y))
            if h is None:
                z["status"] = "ausserhalb"
            else:
                z["dgm"] = round(h, 2)
                if b.get("gok") is None:
                    z["status"] = "ohne_gok"
                elif b.get("gok_quelle") == "DGM":
                    z["status"] = "aus_dgm"
                else:
                    d = float(b["gok"]) - h
                    z["differenz"] = round(d, 2)
                    z["status"] = "ok" if abs(d) <= TOL_OK else "abweichung"
                    abw.append(d)
        zeilen.append(z)
    warnungen = []
    median = float(np.median(abw)) if abw else None
    if median is not None and len(abw) >= 2 and abs(median) > TOL_SYSTEMATISCH:
        gleich = sum(1 for d in abw if d * median > 0) / len(abw)
        if gleich >= 0.8:
            warnungen.append(f"Die GOK liegt im Mittel {_de(abs(median))} m {'über' if median > 0 else 'unter'} dem DGM "
                             f"({len(abw)} Bohrungen): Lage (EPSG, Kalibrierung) oder Höhenbezug prüfen (örtliche "
                             "Höhe statt NHN?); auch Aushub oder Auffüllung seit der Befliegung möglich.")
    einzeln = [z["code"] for z in zeilen if z["status"] == "abweichung"]
    if einzeln and not warnungen:
        warnungen.append(f"GOK weicht um mehr als {_de(TOL_OK, 1)} m vom DGM ab: {', '.join(einzeln)} – Gutachten und "
                         "Lage prüfen (Baugrube, Auffüllung?).")
    draussen = [z["code"] for z in zeilen if z["status"] == "ausserhalb"]
    if draussen:
        warnungen.append(f"{len(draussen)} Bohrungen außerhalb des DGM ({', '.join(draussen[:6])}"
                         f"{' …' if len(draussen) > 6 else ''}): Kachel fehlt oder anderes Koordinatensystem.")
    fremd = [z["code"] for z in zeilen if z["status"] == "anderes_system"]
    if fremd:
        warnungen.append(f"{len(fremd)} Bohrungen in einem anderen System als das DGM (EPSG:{r.epsg}) – nicht verglichen.")
    return {"zeilen": zeilen, "verglichen": len(abw), "median": None if median is None else round(median, 2),
            "max": round(max(abs(d) for d in abw), 2) if abw else None,
            "vorschlaege": sum(1 for z in zeilen if z["status"] == "ohne_gok"), "warnungen": warnungen,
            "toleranz": TOL_OK}


def gok_vorschlaege(r: Raster, bohrungen: list[dict], ids: list[str] | None = None) -> dict[str, float]:
    """id -> Hoehe aus dem DGM fuer Bohrungen ohne GOK (oder nur die genannten ids, die keine GOK aus dem PDF haben)."""
    pruefung = gok_pruefen(r, bohrungen)
    return {z["id"]: z["dgm"] for z in pruefung["zeilen"]
            if z["status"] == "ohne_gok" and (ids is None or z["id"] in ids)}
