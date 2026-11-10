"""Kreuzprobe (Leave-one-out): sagt das Modell eine Bohrung voraus, die es nicht gesehen hat?

Je Bohrung wird das Schichtmodell ohne sie gerechnet (gleiche Einheiten und Kontakte der uebrigen Bohrungen, gleiche
Regeln: freie Grenzen, Zensur, Verschnitt, Ausdehnung) und an ihrer Stelle ausgewertet. Verglichen werden nur
gemessene Groessen: exakte Unterkanten, vorhanden/fehlt, und bei Bohrungen, die in einer Einheit enden, ob die
Unterkante unter der Endteufe bleibt.
"""
from __future__ import annotations

import numpy as np
from baugrundmodell.flaechen import schichtmodell
from scipy.spatial import cKDTree

METHODEN = ("idw", "tps")
MIN_BOHRUNGEN = 3              # mit zwei Bohrungen sagt eine nur sich selbst voraus: keine Kreuzprobe
PRAESENZ_MIN = 0.05            # m: ab dieser Maechtigkeit gilt eine Einheit an der Stelle als vorhergesagt
AUFFAELLIG_MIN = 0.5           # m und ...
AUFFAELLIG_FAKTOR = 3.0        # ... x Median der groessten Fehler der anderen, gerechnet OHNE die verdaechtige Bohrung
AUFFAELLIG_HOECHSTENS = 3      # so viele Bohrungen mit dem groessten Fehler werden geprueft


def _masse(e: list[float]) -> dict:
    if not e:
        return {"n": 0, "mae": None, "rmse": None, "max": None, "bias": None}
    a = np.asarray(e, dtype=float)
    return {"n": len(a), "mae": round(float(np.abs(a).mean()), 3), "rmse": round(float(np.sqrt((a ** 2).mean())), 3),
            "max": round(float(np.abs(a).max()), 3), "bias": round(float(a.mean()), 3)}


def stuetz_abstand(m, j: int) -> tuple[np.ndarray, cKDTree | None]:
    """Bohrungen mit exakter Unterkante der Einheit j (Indizes) und ihr Suchbaum (None ohne solche)."""
    idx = np.array([bi for bi, ks in enumerate(m.kontakte) if ks[j].art == "exakt" and ks[j].status == "vorhanden"], int)
    return idx, (cKDTree(m.punkte[idx]) if len(idx) else None)


def vorhersage(m, ohne: int, methode: str, ausser: frozenset[int] = frozenset()) -> np.ndarray:
    """Flaechen (Gelaende, Unterkanten) an der Stelle der Bohrung `ohne`, gerechnet aus allen anderen (ohne `ausser`)."""
    nb = len(m.bohrungen)
    rest = [i for i in range(nb) if i != ohne and i not in ausser]
    xy = m.punkte[:nb]                                      # das Netz fuehrt die Bohrungen zuerst (flaechen.netz)
    punkte = np.vstack([xy[rest], xy[ohne:ohne + 1]])
    oben = np.r_[m.flaechen[0][rest], m.flaechen[0][ohne]] if m.dgm is not None else None   # DGM: Gelaende bekannt
    sm = schichtmodell([m.bohrungen[i] for i in rest], [m.kontakte[i] for i in rest], punkte, xy[rest], m.basis,
                       methode, oben=oben)
    return sm["flaechen"][:, -1]


def _groesste(m, methode: str, ausser: frozenset[int]) -> dict[int, float]:
    """Groesster Fehler der exakten Unterkanten je Bohrung, wenn die Bohrungen `ausser` gar nicht mitrechnen."""
    out = {}
    for bi in range(len(m.bohrungen)):
        if bi in ausser:
            continue
        f = vorhersage(m, bi, methode, ausser)
        e = [abs(f[j + 1] - k.z) for j, k in enumerate(m.kontakte[bi]) if k.art == "exakt" and k.status == "vorhanden"]
        if e:
            out[bi] = float(max(e))
    return out


def _auffaellige(m, methode: str, groesste: dict[int, float]) -> list[dict]:
    """Bohrungen, die ihre Nachbarn nicht erwarten lassen. Geprueft werden die drei mit dem groessten Fehler, jede
    fuer sich: auffaellig ist sie, wenn ihr Fehler AUFFAELLIG_FAKTOR x den Median der anderen uebersteigt, gerechnet
    ohne sie. (Nicht nacheinander entfernen: jede entfernte Bohrung macht neue Luecken und neue Ausreisser.)"""
    out = []
    if len(m.bohrungen) <= MIN_BOHRUNGEN:
        return out
    for kandidat in sorted(groesste, key=groesste.get, reverse=True)[:AUFFAELLIG_HOECHSTENS]:
        if groesste[kandidat] <= AUFFAELLIG_MIN:
            break
        ohne = _groesste(m, methode, frozenset({kandidat}))
        median = float(np.median(list(ohne.values()))) if ohne else 0.0
        if groesste[kandidat] > max(AUFFAELLIG_MIN, AUFFAELLIG_FAKTOR * median):
            out.append({"bohrung": m.bohrungen[kandidat].code, "fehler_m": round(groesste[kandidat], 2),
                        "median_der_anderen_ohne_sie_m": round(median, 2)})
    return out


def kreuzprobe(m, methoden: tuple[str, ...] = METHODEN) -> dict:
    nb, n = len(m.bohrungen), len(m.einheiten)
    if nb < MIN_BOHRUNGEN:
        raise ValueError(f"Kreuzprobe braucht mindestens {MIN_BOHRUNGEN} Bohrungen im Modell (vorhanden: {nb})")
    xy = m.punkte[:nb]
    nachbar = cKDTree(xy).query(xy, k=2)[0][:, 1]
    stuetz = [stuetz_abstand(m, j) for j in range(n)]
    out: dict = {"methode_modell": m.parameter.get("methode", "idw"), "bohrungen": nb, "methoden": {}, "_fehler": {}}
    for methode in methoden:
        roh: list[tuple[int, int, float, float]] = []       # (Bohrung, Einheit, Abstand zur naechsten Stuetzbohrung, Fehler)
        gelaende: list[float] = []
        praesenz = [{"richtig": 0, "falsch_vorhanden": 0, "falsch_fehlend": 0} for _ in range(n)]
        zensur: list[tuple[int, int, float]] = []
        for bi in range(nb):
            f = vorhersage(m, bi, methode)
            if m.dgm is None:
                gelaende.append(float(f[0] - m.bohrungen[bi].gok))
            for j, k in enumerate(m.kontakte[bi]):
                da = f[j] - f[j + 1] >= PRAESENZ_MIN
                if k.status != "unbekannt":
                    wahr = k.status == "vorhanden"
                    praesenz[j]["richtig" if da == wahr else "falsch_vorhanden" if da else "falsch_fehlend"] += 1
                if k.art == "exakt" and k.status == "vorhanden":
                    idx, baum = stuetz[j]
                    andere = idx[idx != bi]
                    d = float(np.hypot(*(xy[andere] - xy[bi]).T).min()) if len(andere) else float("nan")
                    roh.append((bi, j, d, float(f[j + 1] - k.z)))
                elif k.art == "zensiert" and k.status == "vorhanden" and f[j + 1] > k.hi + 1e-6:
                    zensur.append((bi, j, float(f[j + 1] - k.hi)))   # Einheit laut Modell zu Ende, die Bohrung steht noch darin
        alle = [e for *_, e in roh]
        auff = _auffaellige(m, methode, {bi: max(abs(x) for i, _, _, x in roh if i == bi) for bi in {i for i, *_ in roh}})
        codes = {a["bohrung"] for a in auff}
        je_bohrung = []
        for bi, b in enumerate(m.bohrungen):
            e = [x for i, _, _, x in roh if i == bi]
            ms = _masse(e)
            je_bohrung.append({"code": b.code, "abstand_naechste_m": round(float(nachbar[bi]), 1), "n": ms["n"],
                               "mae": ms["mae"], "max": ms["max"],
                               "auffaellig": b.code in codes})
        out["methoden"][methode] = {
            "gesamt": _masse(alle),
            "einheiten": [{"name": m.einheiten[j].name, **_masse([x for _, jj, _, x in roh if jj == j]),
                           "praesenz": praesenz[j],
                           "endteufe_verletzt": [{"bohrung": m.bohrungen[bi].code, "um_m": round(um, 2)}
                                                 for bi, jj, um in zensur if jj == j]} for j in range(n)],
            "bohrungen": je_bohrung,
            "gelaende": _masse(gelaende) if m.dgm is None else None,
            "auffaellig": auff}
        out["_fehler"][methode] = roh
    mit = {k: v["gesamt"]["mae"] for k, v in out["methoden"].items() if v["gesamt"]["n"]}
    out["beste"] = min(mit, key=mit.get) if mit else None
    out["hinweise"] = _hinweise(m, out)
    return out


def _hinweise(m, k: dict) -> list[str]:
    h = []
    eigene = k["methoden"].get(k["methode_modell"])
    if eigene and not eigene["gesamt"]["n"]:
        h.append("keine exakte Unterkante in den Bohrungen: die Kreuzprobe hat nichts zu vergleichen")
    if k["beste"] and eigene and k["beste"] != k["methode_modell"] and eigene["gesamt"]["n"]:
        b = k["methoden"][k["beste"]]["gesamt"]["mae"]
        if b < 0.8 * eigene["gesamt"]["mae"]:
            h.append(f"Methode {k['beste']} sagt die Bohrungen besser voraus ({b:.2f} m statt "
                     f"{eigene['gesamt']['mae']:.2f} m mittlerer Fehler) – in den Modelleinstellungen wählbar")
    if eigene:
        if eigene["auffaellig"]:
            liste = ", ".join(f"{a['bohrung']} ({a['fehler_m']:.2f} m)".replace(".", ",") for a in eigene["auffaellig"])
            h.append(f"Bohrungen, die ihre Nachbarn nicht erwarten lassen: {liste} neben der Vorhersage – Linse, Rinne "
                     "oder Fehler in Tiefen oder Lage? prüfen")
        fv = sum(e["praesenz"]["falsch_vorhanden"] + e["praesenz"]["falsch_fehlend"] for e in eigene["einheiten"])
        if fv:
            h.append(f"{fv}-mal sagt das Modell eine Einheit falsch als vorhanden oder fehlend voraus "
                     "(Linsen, auskeilende Schichten): ihre Ausdehnung ist unsicher")
    return h
