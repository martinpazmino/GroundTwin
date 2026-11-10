"""Unsicherheit der Grenzflaechen: wie weit kann jede Unterkante zwischen den Bohrungen liegen?

Zwei Anteile, je Knoten und Einheit, zusammen sigma = Wurzel(Messung^2 + Abstand^2):

- Messung: Monte Carlo. Jede exakte Schichtgrenze wird um eine Normalverteilung (SIGMA_EXAKT) verschoben, das
  Schichtmodell mit allen Regeln neu gerechnet (freie Grenzen, Zensur, Verschnitt, Ausdehnung). Die Streuung der
  Laeufe ist dieser Anteil; an den Bohrungen bleibt nur er.
- Abstand: die Kreuzprobe misst, wie weit die Vorhersage an einer nicht gesehenen Bohrung daneben liegt. Aus ihren
  Fehlern e im Abstand d zur naechsten Stuetzbohrung folgt c = Median(e^2 / d) / 0,455 (lineares Variogramm; der
  Median statt des Mittels, damit eine einzelne Bohrung mit 76 m Fehler - gesehen in Hamburg - nicht alles bestimmt;
  0,455 ist der Median der Chi-Quadrat-Verteilung mit einem Freiheitsgrad). An einem Knoten im Abstand d gilt
  sigma^2 = c * d. Unter fuenf Fehlern je Einheit gilt der Wert aller Einheiten zusammen.

Das ist eine Streuung unter diesen Annahmen, keine Garantie; die Annahmen stehen im Ergebnis.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
from baugrundmodell.flaechen import schichtmodell
from baugrundmodell.koerper import volumen_prismen

from .kreuzprobe import kreuzprobe, stuetz_abstand

SIGMA_EXAKT = 0.10             # m: Schichtgrenzen im Bohrprofil sind auf dm bis cm angegeben und beim Bohren verschmiert
MIN_FEHLER_JE_EINHEIT = 5      # darunter c aus allen Einheiten zusammen
CHI2_MEDIAN = 0.4549           # Median von Chi-Quadrat(1): Median(e^2) / 0,4549 schaetzt die Varianz, robust gegen Ausreisser
MIN_ABSTAND = 0.01             # m: verschobene Grenzen einer Bohrung bleiben in ihrer Reihenfolge


def _verschoben(m, rng: np.random.Generator, sigma: float) -> list[list]:
    """Kontakte mit verschobenen exakten Grenzen; gleiche Grenze (Einheit fehlt: Maechtigkeit 0) bleibt gleich."""
    out = []
    for b, ks in zip(m.bohrungen, m.kontakte):
        grenzen = sorted({round(k.z, 4) for k in ks if k.art == "exakt"}, reverse=True)
        neu, vor = {}, b.gok
        for z in grenzen:
            vor = min(z + rng.normal(0.0, sigma), vor - MIN_ABSTAND)
            neu[z] = vor
        out.append([replace(k, z=neu[round(k.z, 4)]) if k.art == "exakt" else k for k in ks])
    return out


def _c_je_einheit(m, kreuz: dict) -> tuple[list[float | None], list[int], float | None]:
    roh = kreuz["_fehler"].get(kreuz["methode_modell"]) or []
    n = len(m.einheiten)
    je = [[e * e / d for _, j, d, e in roh if j == jj and np.isfinite(d) and d > 0] for jj in range(n)]
    alle = [x for l in je for x in l]
    gesamt = float(np.median(alle)) / CHI2_MEDIAN if alle else None
    return ([float(np.median(l)) / CHI2_MEDIAN if len(l) >= MIN_FEHLER_JE_EINHEIT else gesamt for l in je],
            [len(l) for l in je], gesamt)


def unsicherheit(m, kreuz: dict | None = None, laeufe: int = 100, sigma_exakt: float = SIGMA_EXAKT,
                 seed: int = 1) -> dict:
    kreuz = kreuz or kreuzprobe(m)
    n, nb = len(m.einheiten), len(m.bohrungen)
    methode = m.parameter.get("methode", "idw")
    xy_b = m.punkte[:nb]
    oben = m.flaechen[0]
    rng = np.random.default_rng(seed)
    summe = np.zeros_like(m.flaechen)
    quadrat = np.zeros_like(m.flaechen)
    volumen = np.zeros((laeufe, n))
    for r in range(laeufe):
        f = schichtmodell(m.bohrungen, _verschoben(m, rng, sigma_exakt), m.punkte, xy_b, m.basis, methode, oben=oben)["flaechen"]
        summe += f
        quadrat += f * f
        volumen[r] = [volumen_prismen(m.punkte, m.dreiecke, f[j], f[j + 1]) for j in range(n)]
    messung = np.sqrt(np.maximum(quadrat / laeufe - (summe / laeufe) ** 2, 0.0)) if laeufe else np.zeros_like(m.flaechen)
    messung[0] = 0.0                                         # Gelaende gilt als gegeben (nur Rundung)
    c, n_fehler, c_gesamt = _c_je_einheit(m, kreuz)
    abstand = np.zeros_like(m.flaechen)
    d_stuetz = np.full_like(m.flaechen, np.nan)
    for j in range(n):
        idx, baum = stuetz_abstand(m, j)
        if baum is None or c[j] is None:
            abstand[j + 1] = np.nan                          # keine Bohrung erreicht die Unterkante: nicht bezifferbar
            continue
        d_stuetz[j + 1] = baum.query(m.punkte)[0]
        abstand[j + 1] = np.sqrt(c[j] * d_stuetz[j + 1])
    sigma = np.sqrt(messung ** 2 + abstand ** 2)
    andere = "tps" if methode == "idw" else "idw"
    f2 = schichtmodell(m.bohrungen, m.kontakte, m.punkte, xy_b, m.basis, andere, oben=oben)["flaechen"]
    einheiten = []
    for j, e in enumerate(m.einheiten):
        traeger = (m.flaechen[j] - m.flaechen[j + 1]) >= 0.005            # nur wo die Einheit vorkommt
        s = sigma[j + 1][traeger]
        diff = np.abs(f2[j + 1] - m.flaechen[j + 1])[traeger]
        bekannt = traeger.any() and np.isfinite(s).any()
        einheiten.append({
            "name": e.name,
            "unterkante_bezifferbar": bool(bekannt),
            "c_m2_je_m": None if c[j] is None else round(c[j], 4), "kreuz_fehler": n_fehler[j],
            "c_aus": "Einheit" if n_fehler[j] >= MIN_FEHLER_JE_EINHEIT else "allen Einheiten" if c[j] is not None else None,
            "sigma_mittel_m": round(float(np.nanmean(s)), 2) if bekannt else None,
            "sigma_p95_m": round(float(np.nanpercentile(s, 95)), 2) if bekannt else None,
            "sigma_max_m": round(float(np.nanmax(s)), 2) if bekannt else None,
            "sigma_messung_mittel_m": round(float(messung[j + 1][traeger].mean()), 3) if traeger.any() else None,
            "volumen_m3": {"modell": round(volumen_prismen(m.punkte, m.dreiecke, m.flaechen[j], m.flaechen[j + 1]), 1),
                           "p5": round(float(np.percentile(volumen[:, j], 5)), 1) if laeufe else None,
                           "p95": round(float(np.percentile(volumen[:, j], 95)), 1) if laeufe else None},
            "methoden_differenz_m": {"gegen": andere,
                                     "median": round(float(np.median(diff)), 2) if traeger.any() else None,
                                     "p95": round(float(np.percentile(diff, 95)), 2) if traeger.any() else None,
                                     "max": round(float(diff.max()), 2) if traeger.any() else None}})
    hinweise = []
    ohne = [x["name"] for x in einheiten if not x["unterkante_bezifferbar"]]
    if ohne:
        hinweise.append("Unterkante nicht bezifferbar (keine Bohrung erreicht sie oder kein Fehler aus der Kreuzprobe): "
                        + ", ".join(ohne))
    return {"laeufe": laeufe, "methode": methode, "sigma_exakt_m": sigma_exakt, "seed": seed,
            "c_alle_einheiten_m2_je_m": None if c_gesamt is None else round(c_gesamt, 4),
            "einheiten": einheiten, "hinweise": hinweise,
            "annahmen": [f"exakte Schichtgrenzen streuen normalverteilt mit {sigma_exakt:.2f} m",
                         "zwischen den Bohrungen wächst die Streuung mit der Wurzel des Abstands zur nächsten Bohrung, "
                         "die die Unterkante erreicht; der Faktor stammt aus der Kreuzprobe dieses Modells",
                         "Gelände (GOK, DGM) und Lage der Bohrungen gelten als gegeben",
                         "die Volumenspanne enthält nur den Anteil der Messung, nicht den des Abstands"],
            "_sigma": sigma, "_sigma_messung": messung, "_sigma_abstand": abstand, "_abstand_stuetz": d_stuetz}


def zusammenfassung(u: dict) -> dict:
    """Ohne die Felder je Knoten (als JSON schreibbar)."""
    return {k: v for k, v in u.items() if not k.startswith("_")}
