"""Messwerte der Sondierungen je Einheit des Modells (Issue #29): N10 (DPH) und q_c (CPT) nach der Hoehe den Einheiten
zugeordnet, die das Modell an der Lage der Sondierung zeigt. Nur gemessene Werte und ihre Statistik; keine Korrelation
auf Lagerungsdichte oder Konsistenz (die legt der Gutachter fest, docs/05, docs/29). Liest das Modell, aendert nichts.
"""
from __future__ import annotations

import numpy as np

from .virtuell import _dreieck


def _wert(v) -> tuple[float | None, bool]:
    if isinstance(v, dict):
        return (None if v.get("wert") is None else float(v["wert"])), bool(v.get("zensiert"))
    return (None if v is None else float(v)), False


def werte_je_einheit(m, sondierungen: list[dict]) -> tuple[dict[str, dict], list[str]]:
    """sondierungen: im Projekt, mit Lage (x, y wie die Bohrungen), GOK und Werten (ui.sondierung.fuer_ifc).

    Rueckgabe ({Einheit: {"N10": [...], "q_c": [...], "zensiert": n, "sondierungen": [Codes]}}, Hinweise). Die Tiefe
    wird mit der GOK der Sondierung in m NHN umgerechnet; ein Wert gehoert zur Einheit, in deren Hoehenbereich am
    Ort der Sondierung er liegt. Werte ueber dem Modell oder unter seiner Basis bleiben draussen."""
    je: dict[str, dict] = {}
    hinweise: list[str] = []
    for s in sondierungen:
        p = np.array([float(s["x"]) - m.ursprung[0], float(s["y"]) - m.ursprung[1]])
        treffer = _dreieck(m, p)
        if treffer is None:
            hinweise.append(f"{s['code']}: Lage außerhalb des Modells – nicht zugeordnet")
            continue
        knoten, w = treffer
        z = m.flaechen[:, knoten] @ w                     # Gelaende, Unterkanten der Einheiten am Ort
        gok = float(s["gok"])
        if abs(gok - z[0]) > 1.0:
            hinweise.append(f"{s['code']}: GOK {gok:.2f} weicht {gok - z[0]:+.2f} m vom Modell ab – Zuordnung prüfen")
        dph = str(s.get("art", "")).upper().startswith(("DP", "SRS"))
        draussen = 0
        for r in s.get("werte") or []:
            if dph:
                if len(r) < 3:
                    continue
                wert, zen = _wert(r[2])
                tiefe = (float(r[0]) + float(r[1])) / 2
                groesse = "N10"
            else:
                if len(r) < 2 or r[1] is None:
                    continue
                wert, zen = float(r[1]), False
                tiefe = float(r[0])
                groesse = "q_c"
            if wert is None:
                continue
            h = gok - tiefe
            j = next((k for k in range(len(m.einheiten)) if z[k + 1] <= h < z[k] and z[k] - z[k + 1] > 0.01), None)
            if j is None:
                draussen += 1
                continue
            e = je.setdefault(m.einheiten[j].name, {"N10": [], "q_c": [], "zensiert": 0, "sondierungen": []})
            e[groesse].append(wert)
            e["zensiert"] += int(zen)
            if s["code"] not in e["sondierungen"]:
                e["sondierungen"].append(s["code"])
        if draussen:
            hinweise.append(f"{s['code']}: {draussen} Werte über dem Modell oder unter seiner Basis – nicht zugeordnet")
    return je, hinweise


def zusammenfassen(teile: list[dict]) -> dict | None:
    """Werte mehrerer Einheiten (eines Homogenbereichs) zusammenlegen; None ohne Werte."""
    out = {"N10": [], "q_c": [], "zensiert": 0, "sondierungen": []}
    for t in teile:
        out["N10"] += t["N10"]
        out["q_c"] += t["q_c"]
        out["zensiert"] += t["zensiert"]
        out["sondierungen"] += [c for c in t["sondierungen"] if c not in out["sondierungen"]]
    return out if out["N10"] or out["q_c"] else None
