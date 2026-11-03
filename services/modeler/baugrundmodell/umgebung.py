"""Gelaende aus einem DGM: Oberkante des Modells und Gelaende um das Modell (docs/23 §2.4, Phase P3b).

Das DGM kommt als Raster mit x0, y0 (Mitte der Zelle oben links), dx, dy, z (NaN = Luecke) und epsg, z. B.
geodaten.gelaende.Raster; der Modellierer haengt nicht von diesem Paket ab.

Oberkante: das DGM, an den Bohrungen auf ihre GOK gezogen. Die Korrektur GOK - DGM klingt mit dem Abstand zur naechsten
Bohrung bis zur Reichweite ab: an den Bohrungen bleibt das Modell exakt, am Rand geht es ins DGM ueber.
Umgebung: Ring um das Modellgebiet aus dem DGM, der die Randknoten des Modells teilt (keine Fuge, keine doppelte
Flaeche ueber dem Modell); im IFC ein IfcGeographicElement TERRAIN.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.spatial import cKDTree

from .flaechen import interpolieren

REICHWEITE_MAX = 25.0          # m: weiter wirkt die GOK einer Bohrung nicht auf das Gelaende
HINWEIS_AB = 1.0               # m: weicht das DGM so weit von der Interpolation der GOK ab, wird es markiert
UMGEBUNG_STANDARD = 100.0      # m um das Modellgebiet
RINGE_MAX = 40                 # Ringe der Umgebung (Schrittweite waechst mit dem Abstand)


def abtasten(r, xy: np.ndarray) -> np.ndarray:
    """DGM bilinear an den Punkten (gleiches System wie das Raster); NaN ausserhalb und an Luecken."""
    z = np.asarray(r.z, dtype=float)
    zeilen, spalten = z.shape
    fj = (xy[:, 0] - float(r.x0)) / float(r.dx)
    fi = (float(r.y0) - xy[:, 1]) / float(r.dy)
    out = np.full(len(xy), np.nan)
    eps = 1e-6
    ok = (fj >= -eps) & (fj <= spalten - 1 + eps) & (fi >= -eps) & (fi <= zeilen - 1 + eps)
    if not ok.any():
        return out
    j0 = np.clip(np.floor(fj[ok]).astype(int), 0, max(spalten - 2, 0))
    i0 = np.clip(np.floor(fi[ok]).astype(int), 0, max(zeilen - 2, 0))
    j1, i1 = np.minimum(j0 + 1, spalten - 1), np.minimum(i0 + 1, zeilen - 1)
    tj = np.where(j1 > j0, np.clip(fj[ok] - j0, 0.0, 1.0), 0.0)
    ti = np.where(i1 > i0, np.clip(fi[ok] - i0, 0.0, 1.0), 0.0)
    summe = np.zeros(len(j0))
    luecke = np.zeros(len(j0), dtype=bool)
    for i, j, w in ((i0, j0, (1 - ti) * (1 - tj)), (i0, j1, (1 - ti) * tj), (i1, j0, ti * (1 - tj)), (i1, j1, ti * tj)):
        v = z[i, j]
        fehlt = ~np.isfinite(v)
        luecke |= fehlt & (w > 1e-12)                  # eine Luecke zaehlt nur, wenn sie Gewicht hat
        summe += np.where(fehlt, 0.0, v) * w
    out[ok] = np.where(luecke, np.nan, summe)
    return out


def _m(v: float) -> str:
    return f"{v:.1f}".replace(".", ",")


def oberkante(r, punkte: np.ndarray, ursprung: tuple[float, float], xy_b: np.ndarray, gok_b: np.ndarray,
              raster: float, nn: float, methode: str = "idw") -> tuple[np.ndarray | None, dict]:
    """Gelaende an den Netzknoten (lokal) aus dem DGM; die Bohrungen sind die ersten Knoten des Netzes.

    Rueckgabe: (Hoehen oder None, Angaben fuer Bericht und IFC). None, wenn das DGM das Gebiet nicht ganz abdeckt.
    Liegt das DGM zwischen den Bohrungen deutlich ueber oder unter der Interpolation der GOK (Damm, Senke, Baugrube),
    steht das als Hinweis da: die oberste Einheit ist dort nicht erkundet.
    """
    z_dgm = abtasten(r, punkte + np.asarray(ursprung, dtype=float))
    fehlend = int((~np.isfinite(z_dgm)).sum())
    if fehlend:
        return None, {"quelle": "GOK", "hinweis": f"DGM deckt das Modellgebiet nicht ganz ab ({fehlend} Knoten ohne "
                                                  f"Höhe) – Gelände aus den GOK der Bohrungen interpoliert"}
    nb = len(xy_b)
    korrektur_b = np.asarray(gok_b, dtype=float) - z_dgm[:nb]
    reichweite = float(max(2.0 * raster, min(REICHWEITE_MAX, 0.5 * nn)))
    abstand, _ = cKDTree(xy_b).query(punkte)
    abklingen = np.clip(1.0 - (abstand / reichweite) ** 2, 0.0, None) ** 2
    oben = z_dgm + interpolieren(punkte, xy_b, korrektur_b, "idw") * abklingen
    oben[:nb] = gok_b                                     # exakt an den Bohrungen (gegen Rundung)
    d = oben - interpolieren(punkte, xy_b, np.asarray(gok_b, dtype=float), methode)
    ueber, unter = max(float(d.max()), 0.0), max(float(-d.min()), 0.0)
    info = {"quelle": "DGM", "reichweite_m": round(reichweite, 1),
            "gok_minus_dgm_max_m": round(float(np.abs(korrektur_b).max()), 3),
            "gok_minus_dgm_median_m": round(float(np.median(korrektur_b)), 3),
            "ueber_interpolation_max_m": round(ueber, 2), "unter_interpolation_max_m": round(unter, 2)}
    if max(ueber, unter) > HINWEIS_AB:
        info["hinweis"] = (f"Gelände aus dem DGM bis {_m(ueber)} m über und {_m(unter)} m unter der Interpolation der GOK "
                           f"(Damm, Senke, Baugrube?) – dort ist die oberste Einheit nicht erkundet")
    return oben, info


def _randschleife(rand: np.ndarray) -> list[int] | None:
    """Randknoten in Reihenfolge (Gebiet links); None, wenn der Rand nicht eine einfache Schleife ist."""
    nach = {int(u): int(v) for u, v in rand}
    if len(nach) != len(rand) or not nach:
        return None
    start = min(nach)
    schleife = [start]
    while (v := nach.get(schleife[-1])) is not None and v != start:
        schleife.append(v)
        if len(schleife) > len(nach):
            return None
    return schleife if v == start and len(schleife) == len(nach) else None


def ring(r, punkte: np.ndarray, rand: np.ndarray, oben: np.ndarray, ursprung: tuple[float, float],
         abstand: float = UMGEBUNG_STANDARD, schritt: float = 5.0) -> dict | None:
    """Gelaende um das Modellgebiet: Knoten (lokal, z NHN) und Dreiecke (gegen den Uhrzeigersinn von oben).

    Ring 0 sind die Randknoten des Modells mit ihrer Oberkante; die weiteren Ringe liegen entlang der Normalen
    (konvexes Gebiet: die Strahlen kreuzen sich nicht) bis zum Abstand, hoechstens bis zum Rand des DGM.
    """
    schleife = _randschleife(rand)
    if schleife is None or len(schleife) < 3:
        return None
    p = punkte[schleife]
    vor, nach = p - np.roll(p, 1, axis=0), np.roll(p, -1, axis=0) - p
    normale = np.c_[vor[:, 1], -vor[:, 0]] / np.linalg.norm(vor, axis=1)[:, None] \
        + np.c_[nach[:, 1], -nach[:, 0]] / np.linalg.norm(nach, axis=1)[:, None]
    normale /= np.linalg.norm(normale, axis=1)[:, None]          # nach aussen (Gebiet links des Randes)
    zeilen, spalten = np.asarray(r.z).shape
    lo = np.array([float(r.x0), float(r.y0) - (zeilen - 1) * float(r.dy)]) - np.asarray(ursprung, dtype=float)
    hi = np.array([float(r.x0) + (spalten - 1) * float(r.dx), float(r.y0)]) - np.asarray(ursprung, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):          # Strahl bis zum Rand des DGM
        t = np.where(normale > 0, (hi - p) / normale, np.where(normale < 0, (lo - p) / normale, np.inf))
    weit = float(min(abstand, np.nanmin(t.min(axis=1))))
    if not weit > 0:
        return None
    n_ringe = int(min(RINGE_MAX, max(1, math.ceil(weit / max(schritt, 0.1)))))
    knoten = [np.c_[p, oben[schleife]]]
    for k in range(1, n_ringe + 1):
        xy = p + normale * (weit * k / n_ringe)
        knoten.append(np.c_[xy, abtasten(r, xy + np.asarray(ursprung, dtype=float))])
    knoten = np.vstack(knoten)
    n = len(schleife)
    i = np.arange(n)
    dreiecke = []
    for k in range(n_ringe):
        a, b = k * n + i, k * n + (i + 1) % n
        c, d = (k + 1) * n + (i + 1) % n, (k + 1) * n + i
        dreiecke += [np.c_[a, c, b], np.c_[a, d, c]]
    dreiecke = np.vstack(dreiecke)
    dreiecke = dreiecke[np.isfinite(knoten[dreiecke, 2]).all(axis=1)]   # Luecken im DGM bleiben offen
    if not len(dreiecke):
        return None
    benutzt = np.unique(dreiecke)
    neu = np.full(len(knoten), -1)
    neu[benutzt] = np.arange(len(benutzt))
    return {"knoten": knoten[benutzt], "dreiecke": neu[dreiecke], "abstand_m": round(weit, 1),
            "schritt_m": round(weit / n_ringe, 2), "randknoten": n}
