"""Virtuelle Bohrung: was erwartet das Modell an einem Punkt, und mit welcher Streuung?

Gelesen wird das Modell, wie es gezeigt wird (lineare Interpolation im Dreieck des Netzes): Gelaende aus dem DGM,
begrenzte Ausdehnung von Linsen und der Verschnitt sind darin enthalten.
"""
from __future__ import annotations

import numpy as np

MIN_SCHICHT = 0.01             # m: duennere Einheiten gelten am Punkt als nicht vorhanden


def _dreieck(m, p: np.ndarray) -> tuple[np.ndarray, np.ndarray] | None:
    """Knoten des Dreiecks um p und seine baryzentrischen Gewichte; None ausserhalb des Netzes."""
    a, b, c = (m.punkte[m.dreiecke[:, k]] for k in range(3))
    det = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    with np.errstate(divide="ignore", invalid="ignore"):
        w0 = ((b[:, 1] - c[:, 1]) * (p[0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (p[1] - c[:, 1])) / det
        w1 = ((c[:, 1] - a[:, 1]) * (p[0] - c[:, 0]) + (a[:, 0] - c[:, 0]) * (p[1] - c[:, 1])) / det
    w2 = 1.0 - w0 - w1
    innen = np.nonzero((w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9))[0]
    if not len(innen):
        return None
    t = innen[0]
    return m.dreiecke[t], np.array([w0[t], w1[t], w2[t]])


def virtuelle_bohrung(m, x: float, y: float, unsicherheit: dict | None = None) -> dict:
    """x, y im System des Projekts (wie die Bohrungen). ValueError ausserhalb des Modells."""
    p = np.array([float(x) - m.ursprung[0], float(y) - m.ursprung[1]])
    treffer = _dreieck(m, p)
    if treffer is None:
        raise ValueError("Punkt liegt außerhalb des Modells (Gebiet der Bohrungen mit Rand)")
    knoten, w = treffer
    z = m.flaechen[:, knoten] @ w
    nb = len(m.bohrungen)
    d = np.hypot(*(m.punkte[:nb] - p).T)
    sig = unsicherheit["_sigma"][:, knoten] if unsicherheit else None
    schichten = []
    for j, e in enumerate(m.einheiten):
        dicke = float(z[j] - z[j + 1])
        if dicke < MIN_SCHICHT:
            continue
        s = None
        if sig is not None and np.isfinite(sig[j + 1]).all():
            s = float(np.sqrt((sig[j + 1] ** 2) @ w))                  # Varianz linear im Dreieck
        offen = abs(z[j + 1] - m.basis) < 1e-6
        schichten.append({"einheit": e.name, "bodenarten": sorted(e.klassen),
                          "oben_nhn": round(float(z[j]), 2), "unten_nhn": round(float(z[j + 1]), 2),
                          "tiefe_oben_m": round(float(z[0] - z[j]), 2), "tiefe_unten_m": round(float(z[0] - z[j + 1]), 2),
                          "maechtigkeit_m": round(dicke, 2),
                          "sigma_unten_m": None if s is None else round(s, 2),
                          "unten_95_nhn": None if s is None else [round(float(z[j + 1] - 1.96 * s), 2),
                                                                 round(float(z[j + 1] + 1.96 * s), 2)],
                          "unterkante_offen": bool(offen)})
    hinweise = []
    if schichten and schichten[-1]["unterkante_offen"]:
        hinweise.append("unterste Einheit: Unterkante = Modellbasis (keine Bohrung erreicht sie)")
    return {"x": float(x), "y": float(y), "gok_nhn": round(float(z[0]), 2), "endteufe_m": round(float(z[0] - m.basis), 2),
            "naechste_bohrung": m.bohrungen[int(d.argmin())].code, "abstand_m": round(float(d.min()), 1),
            "schichten": schichten, "hinweise": hinweise, "herkunft": "Modell (virtuelle Bohrung, keine Messung)"}
