"""Erkundungsvorschlag (docs/27 G4): wo bringt die naechste Bohrung am meisten?

Gemessen (docs/27 §6.4): bei einer Rinne zwischen den Bohrungen liegen IDW, Spline und GemPy gleich weit daneben
(3,5 bis 4,2 m mittlerer Fehler der Maechtigkeit); zwei Bohrungen am Rand senken ihn auf 0,3 bis 0,45 m. Die Grenze
ist die Information, nicht die Methode. Deshalb sagt die Analyse, wo die Information fehlt:

- Lage der Grenzflaechen: sigma der Unterkanten je Knoten (unsicherheit), zusammengefasst als Wurzel der Quadratsumme;
- Ausdehnung: fuer jede Einheit, die nicht in allen Bohrungen vorkommt, der Anteil "vorhanden" der Nachbarbohrungen
  (IDW, wie das Modell ihre Ausdehnung begrenzt); am unsichersten bei 0,5, gewichtet mit ihrer mittleren Maechtigkeit
  in den Bohrungen, in denen sie vorkommt.

Die Punkte werden nacheinander gewaehlt: der hoechste Wert, dann wird um ihn herum (ein Bohrabstand) gesperrt. Nicht
naeher als ein Viertel des Bohrabstands an einer vorhandenen Bohrung. Ein Vorschlag, keine Planung: Zugang, Leitungen
und Baufeld kennt das Modell nicht.
"""
from __future__ import annotations

import numpy as np
from baugrundmodell.flaechen import interpolieren
from scipy.spatial import cKDTree

SPERRE = 1.0                   # um einen Vorschlag: so viele Bohrabstaende gesperrt (gemessen, docs/27 §6.4)
NAEHE = 0.25                   # nicht naeher an einer vorhandenen Bohrung (Bohrabstaende)


def _ausdehnung(m) -> tuple[np.ndarray, list[tuple[str, np.ndarray]]]:
    """Summe der gewichteten Unsicherheit der Ausdehnung je Knoten, und je Einheit ihr Anteil."""
    nb = len(m.bohrungen)
    xy_b = m.punkte[:nb]
    gesamt = np.zeros(len(m.punkte))
    teile = []
    for j, e in enumerate(m.einheiten):
        ind = {bi: 1.0 if ks[j].status == "vorhanden" else 0.0 for bi, ks in enumerate(m.kontakte) if ks[j].status != "unbekannt"}
        if not ind or min(ind.values()) == 1.0 or max(ind.values()) == 0.0:
            continue
        bi = np.array(sorted(ind))
        p = interpolieren(m.punkte, xy_b[bi], np.array([ind[i] for i in bi]), "idw")
        da = [b for b in bi if ind[b] == 1.0]
        dicke = float(np.mean([m.flaechen[j][b] - m.flaechen[j + 1][b] for b in da])) if da else 0.0
        teil = (1.0 - np.abs(2.0 * p - 1.0)) * dicke
        gesamt += teil
        teile.append((e.name, teil))
    return gesamt, teile


def vorschlaege(m, unsicherheit: dict, anzahl: int = 3) -> list[dict]:
    nb = len(m.bohrungen)
    xy_b = m.punkte[:nb]
    nn = float(np.median(cKDTree(xy_b).query(xy_b, k=2)[0][:, 1])) if nb > 1 else 20.0
    sig = np.nan_to_num(unsicherheit["_sigma"][1:], nan=0.0)
    lage = np.sqrt((sig ** 2).sum(axis=0))
    ausd, teile = _ausdehnung(m)
    wert = lage + ausd
    d_bohrung = cKDTree(xy_b).query(m.punkte)[0]
    wert[d_bohrung < NAEHE * nn] = -1.0
    out = []
    frei = wert.copy()
    for _ in range(anzahl):
        k = int(np.argmax(frei))
        if frei[k] <= 0:
            break
        grund = []
        if teile:
            name, t = max(teile, key=lambda nt: nt[1][k])
            if t[k] > 0.05:
                grund.append(f"Ausdehnung von {name} unsicher")
        j = int(np.argmax(sig[:, k]))
        if sig[j, k] > 0.05:
            grund.append(f"Unterkante {m.einheiten[j].name} ± {sig[j, k]:.2f} m".replace(".", ","))
        out.append({"x": round(float(m.punkte[k, 0] + m.ursprung[0]), 2), "y": round(float(m.punkte[k, 1] + m.ursprung[1]), 2),
                    "wert_m": round(float(wert[k]), 2), "lage_m": round(float(lage[k]), 2),
                    "ausdehnung_m": round(float(ausd[k]), 2),
                    "abstand_naechste_bohrung_m": round(float(d_bohrung[k]), 1), "grund": "; ".join(grund) or "größte Unsicherheit"})
        frei[np.hypot(*(m.punkte - m.punkte[k]).T) < SPERRE * nn] = -1.0
    return out
