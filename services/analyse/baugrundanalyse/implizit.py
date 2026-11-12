"""Implizite Interpolation mit GemPy als dritte Methode des Schichtmodells (docs/27 G3, D105, D106).

Je Grenzflaeche ein eigenes Skalarfeld (eine Gruppe mit einem Element: so kann jede Einheit auskeilen, docs/27 §3.2),
aus den Kontakten der Flaeche und einer Orientierung, ausgewertet in senkrechten Saeulen an den Knoten des Netzes:
die Hoehe, an der die Saeule die Flaeche schneidet. Alles andere bleibt beim Schichtmodell (freie Grenzen, Zensur,
Verschnitt, Ausdehnung, geschlossene Koerper, IFC).

Orientierung ohne gemessenes Einfallen (D106): Ebene durch die Punkte der Flaeche (ab 3, nicht auf einer Linie); auf
einer Linie (Trasse) das Einfallen entlang der Linie, quer dazu horizontal; steiler als MAX_FALLEN_GRAD oder weniger
als 3 Punkte: horizontal. Ist fuer eine Einheit eine Orientierung eingegeben (Fallrichtung, Fallwinkel; z. B. aus
einem Gutachten oder einer geologischen Karte), gilt sie statt der berechneten (Quelle "Eingabe", docs/27 G4). Die Quelle
steht im Bericht.

Pruefungen je Flaeche: genau ein Schnitt je Saeule (sonst ist die Flaeche gefaltet) und an den Daten hoechstens
TOLERANZ daneben; sonst gilt fuer diese Flaeche der Duennplatten-Spline, mit Hinweis. An den Daten wird exakt gesetzt.

GemPy (EUPL-1.2) ist optional: ohne das Paket ist die Methode nicht verfuegbar, alles andere laeuft.
"""
from __future__ import annotations

import contextlib
import io
import math
import warnings

import numpy as np

MAX_EINGABE_GRAD = 80.0        # eingegebenes Fallen: bis hier (senkrecht kann ein Saeulenschnitt nicht abbilden)
MAX_FALLEN_GRAD = 30.0         # steiler aus Kontakten allein ist nicht glaubhaft (Lockergestein, Bohrabstand)
TOLERANZ = 0.05                # m: so weit darf das Feld an einem Kontakt daneben liegen, sonst Spline
STUFEN = (24, 12, 12)          # Saeulenabtastung: grob, dann zweimal im Intervall (gegen 48/16/16 hoechstens 3,5 cm, halbe Zeit)
RANGE = 1.7                    # Reichweite des Kerns (relativ, GemPy-Vorgabe der Beispiele) ...
C_O = 10.0                     # ... und Kovarianz bei 0; gemessen in docs/27 §3


def verfuegbar() -> bool:
    try:
        import gempy  # noqa: F401
    except Exception:
        return False
    return True


def _kollinear(xy: np.ndarray) -> bool:
    if len(xy) < 3:
        return True
    s = np.linalg.svd(xy - xy.mean(0), compute_uv=False)
    return s[1] <= 1e-6 * max(s[0], 1e-9)


def orientierung(xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray, str, float]:
    """(Zentrum, Pol-Vektor nach oben, Quelle, Fallwinkel in Grad) fuer die Punkte einer Flaeche."""
    xyz = np.asarray(xyz, dtype=float)
    c = xyz.mean(axis=0)
    oben = np.array([0.0, 0.0, 1.0])
    if len(xyz) < 2:
        return c, oben, "horizontal (zu wenige Kontakte)", 0.0
    if _kollinear(xyz[:, :2]):
        if np.ptp(xyz[:, 0]) + np.ptp(xyz[:, 1]) < 1e-9:
            return c, oben, "horizontal (Kontakte an einer Stelle)", 0.0
        u = np.linalg.svd(xyz - c)[2][0]                      # Richtung der Linie in 3D
        n = oben - np.dot(oben, u) * u                        # senkrecht zur Linie, so steil nach oben wie moeglich
        quelle = "entlang der Linie der Bohrungen, quer horizontal"
    elif len(xyz) < 3:
        return c, oben, "horizontal (zu wenige Kontakte)", 0.0
    else:
        n = np.linalg.svd(xyz - c)[2][-1]
        quelle = "Ebene durch die Kontakte"
    n = n / np.linalg.norm(n)
    if n[2] < 0:
        n = -n
    fallen = math.degrees(math.acos(min(1.0, float(n[2]))))
    if fallen > MAX_FALLEN_GRAD:
        return c, oben, f"horizontal (Ebene durch die Kontakte fiele {fallen:.0f}° ein, über {MAX_FALLEN_GRAD:.0f}°)", 0.0
    return c, n, quelle, fallen


def pol_aus(fallrichtung: float, fallwinkel: float) -> np.ndarray:
    """Pol-Vektor nach oben fuer Fallrichtung (Azimut, Grad von Nord im Uhrzeigersinn) und Fallwinkel (Grad)."""
    a, d = math.radians(fallrichtung), math.radians(fallwinkel)
    return np.array([math.sin(d) * math.sin(a), math.sin(d) * math.cos(a), math.cos(d)])


def _modell(xyz: np.ndarray, ausdehnung: list[float], zentrum: np.ndarray, pol: np.ndarray):
    import gempy as gp
    el = gp.data.StructuralElement(
        name="grenze", color="#888888",
        surface_points=gp.data.SurfacePointsTable.from_arrays(x=xyz[:, 0], y=xyz[:, 1], z=xyz[:, 2], names=["grenze"]),
        orientations=gp.data.OrientationsTable.initialize_empty())
    gruppe = gp.data.StructuralGroup(name="folge", elements=[el], structural_relation=gp.data.StackRelationType.ERODE)
    frame = gp.data.StructuralFrame(structural_groups=[gruppe], color_gen=gp.data.ColorsGenerator())
    m = gp.data.GeoModel.from_args(
        name="grenze", structural_frame=frame, grid=gp.data.Grid(extent=ausdehnung, resolution=(4, 4, 4)),
        interpolation_options=gp.data.InterpolationOptions.from_args(range=RANGE, c_o=C_O, mesh_extraction=False,
                                                                     number_octree_levels=1))
    gp.add_orientations(geo_model=m, x=[zentrum[0]], y=[zentrum[1]], z=[zentrum[2]], elements_names=["grenze"],
                        pole_vector=np.array([pol]))
    return m


def _ids(m, punkte: np.ndarray) -> np.ndarray:
    import gempy as gp
    with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return np.asarray(gp.compute_model_at(m, punkte)).astype(int)


def saeulen(m, xy: np.ndarray, lo: float, hi: float) -> tuple[np.ndarray, np.ndarray]:
    """Schnitthoehe je Saeule und Anzahl der Wechsel (1 = eindeutig; 0 = nicht im Bereich; > 1 = gefaltet)."""
    n = len(xy)
    unten = np.full(n, lo)
    oben = np.full(n, hi)
    wechsel = np.zeros(n, int)
    for stufe, k in enumerate(STUFEN):
        zs = unten[:, None] + (oben - unten)[:, None] * np.linspace(0.0, 1.0, k + 1)[None, :]
        pkt = np.column_stack([np.repeat(xy[:, 0], k + 1), np.repeat(xy[:, 1], k + 1), zs.ravel()])
        ids = _ids(m, pkt).reshape(n, k + 1)
        d = np.diff(ids, axis=1) != 0
        if stufe == 0:
            wechsel = d.sum(axis=1)
        i = np.where(d.any(axis=1), d.argmax(axis=1), 0)
        rows = np.arange(n)
        unten, oben = zs[rows, i], zs[rows, i + 1]
    return (unten + oben) / 2.0, wechsel


def interpolieren(ziel: np.ndarray, xy: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Wie baugrundmodell.flaechen.interpolieren: Hoehe der Flaeche an den Zielpunkten, exakt an den Daten."""
    from baugrundmodell import flaechen
    xy = np.asarray(xy, dtype=float)
    z = np.asarray(z, dtype=float)
    ziel = np.asarray(ziel, dtype=float)
    xyz = np.column_stack([xy, z])
    zentrum, pol, _, fallen = orientierung(xyz)
    vorgabe = flaechen.orientierung_vorgabe()
    if vorgabe is not None:
        pol, fallen = pol_aus(*vorgabe), float(vorgabe[1])
    alle = np.vstack([ziel, xy])
    d = np.hypot(*(alle[:, None, :] - xy[None, :, :]).transpose(2, 0, 1)).min(axis=1)
    weite = float(d.max()) if len(d) else 0.0
    rand_z = max(5.0, math.tan(math.radians(max(fallen, MAX_FALLEN_GRAD))) * weite + 0.25 * float(np.ptp(z)))
    lo, hi = float(z.min()) - rand_z, float(z.max()) + rand_z
    rand_xy = max(5.0, 0.05 * float(np.ptp(alle, axis=0).max()))
    ausdehnung = [float(alle[:, 0].min()) - rand_xy, float(alle[:, 0].max()) + rand_xy,
                  float(alle[:, 1].min()) - rand_xy, float(alle[:, 1].max()) + rand_xy, lo, hi]
    try:
        m = _modell(xyz, ausdehnung, zentrum, pol)
        werte, wechsel = saeulen(m, alle, lo, hi)
    except Exception as err:                                  # GemPy lehnt die Daten ab (z. B. doppelte Punkte)
        flaechen.hinweis(f"implizit: GemPy lehnt eine Fläche ab ({type(err).__name__}) – Dünnplatten-Spline")
        return flaechen.interpolieren(ziel, xy, z, "tps")
    an_daten = werte[len(ziel):]
    if (wechsel != 1).any() or np.abs(an_daten - z).max() > TOLERANZ:
        gefaltet = int((wechsel > 1).sum())
        flaechen.hinweis("implizit: eine Fläche ist "
                         + (f"gefaltet ({gefaltet} Säulen schneiden sie mehrfach)" if gefaltet else
                            f"an den Bohrungen bis {np.abs(an_daten - z).max():.2f} m daneben".replace(".", ","))
                         + " – für sie gilt der Dünnplatten-Spline")
        return flaechen.interpolieren(ziel, xy, z, "tps")
    out = werte[:len(ziel)]
    dz = np.hypot(*(ziel[:, None, :] - xy[None, :, :]).transpose(2, 0, 1))
    treffer = dz.min(axis=1) < 1e-9
    out[treffer] = z[dz[treffer].argmin(axis=1)]                # an den Bohrungen exakt
    return out


def beschreiben(einheiten, kontakte, bohrungen) -> list[dict]:
    """Orientierung je Einheit (Quelle und Fallen) aus ihren exakten Unterkanten oder der Eingabe: fuer Bericht und IFC."""
    from baugrundmodell import flaechen
    vorgaben = flaechen.orientierungen_holen()
    out = []
    for j, e in enumerate(einheiten):
        p = [(b.x, b.y, ks[j].z) for b, ks in zip(bohrungen, kontakte) if ks[j].art == "exakt" and ks[j].status == "vorhanden"]
        if j in vorgaben:
            richtung, fallen = vorgaben[j]
            out.append({"einheit": e.name, "quelle": "Eingabe", "fallen_grad": round(fallen, 1),
                        "fallrichtung_grad": round(richtung, 0) if fallen > 0 else None, "kontakte": len(p)})
            continue
        if len(p) < 2:
            out.append({"einheit": e.name, "quelle": "keine Unterkante gemessen", "fallen_grad": None, "kontakte": len(p)})
            continue
        _, pol, quelle, fallen = orientierung(np.array(p, dtype=float))
        richtung = None
        if fallen > 0:
            richtung = round((math.degrees(math.atan2(pol[0], pol[1])) + 360.0) % 360.0, 0)   # Fallrichtung (Azimut)
        out.append({"einheit": e.name, "quelle": quelle, "fallen_grad": round(fallen, 1), "fallrichtung_grad": richtung,
                    "kontakte": len(p)})
    return out


interpolieren.beschreiben = beschreiben                    # der Modellierer fragt danach (modell.bauen)


def registrieren() -> bool:
    """Methode "implizit" beim Modellierer anmelden; False ohne GemPy."""
    if not verfuegbar():
        return False
    from baugrundmodell import flaechen
    flaechen.ERWEITERUNGEN["implizit"] = interpolieren
    return True
