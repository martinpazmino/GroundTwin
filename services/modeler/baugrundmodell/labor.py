"""Laborwerte aus den Anlagen des Gutachtens je Schicht und Einheit (Issue #18).

Die Extraktion (services/extractor/labor.py) liefert Proben mit Bohrung(en), Tiefe von-bis und Werten. Hier:

- jede Probe haengt an der Schicht ihrer Bohrung, mit der sich ihr Tiefenbereich am meisten deckt (eine Probe ueber
  eine Schichtgrenze bekommt einen Hinweis; Mischproben haengen an jeder ihrer Bohrungen, markiert);
- je Einheit (oder Homogenbereich) die Statistik n, min, max, Mittel je Kennwert - gemessene Werte, keine
  charakteristischen (die setzt der Gutachter, docs/29);
- IFC ``CPset_Laborwerte`` an der Einheit: ``<Kennwert>_min/_max/_mean/_n`` (Namensregel DAUB Teil 3, docs/30 §6.1).
"""
from __future__ import annotations

import re
import statistics

PSET = "CPset_Laborwerte"
NAMEN = {"wassergehalt": "Wassergehalt", "wassergehalt_korrigiert": "Wassergehalt_korrigiert",
         "fliessgrenze": "Fliessgrenze", "ausrollgrenze": "Ausrollgrenze", "plastizitaetszahl": "Plastizitaetszahl",
         "konsistenzzahl": "Konsistenzzahl", "gluehverlust": "Gluehverlust", "kalkgehalt": "Kalkgehalt",
         "trockendichte": "Trockendichte", "proctordichte": "Proctordichte",
         "optimaler_wassergehalt": "Optimaler_Wassergehalt", "cbr": "CBR", "kf": "Durchlaessigkeit_kf",
         "ton": "Tonanteil", "schluff": "Schluffanteil", "sand": "Sandanteil", "kies": "Kiesanteil"}
EINHEIT = {"wassergehalt": "%", "wassergehalt_korrigiert": "%", "fliessgrenze": "%", "ausrollgrenze": "%",
           "plastizitaetszahl": "%", "konsistenzzahl": "", "gluehverlust": "%", "kalkgehalt": "%",
           "trockendichte": "g/cm³", "proctordichte": "g/cm³", "optimaler_wassergehalt": "%", "cbr": "%",
           "kf": "m/s", "ton": "%", "schluff": "%", "sand": "%", "kies": "%"}


def code(c: str) -> str:
    """'BS 5', 'BS5', 'bs 05' -> 'BS5' (Vergleich der Bohrungs-Codes)."""
    m = re.match(r"\s*([A-Za-z]+)\s*0*(\d+)\s*([a-z]?)", c or "")
    return f"{m.group(1).upper()}{m.group(2)}{m.group(3)}" if m else (c or "").replace(" ", "").upper()


def proben(docs: list[dict]) -> list[dict]:
    """Alle Proben der Dokumente mit Verweis 'Datei#Index'."""
    return [{**p, "ref": f"{d['document']['file']}#{i}", "dokument": d["document"]["file"]}
            for d in docs for i, p in enumerate(d.get("labor") or [])]


def an_schichten(bohrung: str, schichten: list[dict], alle: list[dict]) -> None:
    """Haengt die Proben dieser Bohrung an die Schicht mit der groessten Ueberdeckung (schichten[k]['labor'])."""
    c = code(bohrung)
    for p in alle:
        if c not in {code(x) for x in p.get("bohrungen") or []}:
            continue
        deckung = [(min(s["bis"], p["bis"]) - max(s["von"], p["von"]), k) for k, s in enumerate(schichten)]
        beste, k = max(deckung, default=(0.0, None))
        if k is None or beste <= 0:
            continue
        hinweise = list(p.get("hinweise") or [])
        if sum(d > 0.01 for d, _ in deckung) > 1:
            hinweise.append(f"Probe {p['von']:.2f}–{p['bis']:.2f} m reicht über eine Schichtgrenze".replace(".", ","))
        schichten[k].setdefault("labor", []).append({"ref": p.get("ref"), "bohrung": bohrung, "von": p["von"],
                                                     "bis": p["bis"], "werte": p["werte"], "hinweise": hinweise})


def statistik(schichten: list[dict]) -> dict[str, dict]:
    """Je Kennwert n, min, max, Mittel und die Proben (eine Mischprobe zaehlt einmal)."""
    gesehen, werte = set(), {}
    for s in schichten:
        for p in s.get("labor") or []:
            schluessel = p.get("ref") or (p["bohrung"], p["von"], p["bis"])
            if schluessel in gesehen:
                continue
            gesehen.add(schluessel)
            for k, v in p["werte"].items():
                werte.setdefault(k, []).append(float(v))
    return {k: {"n": len(v), "min": min(v), "max": max(v), "mittel": statistics.fmean(v), "einheit": EINHEIT.get(k, "")}
            for k, v in werte.items()}


def text(st: dict, k: str) -> str | None:
    """'12,1–22,8 % (n = 6, Mittel 16,4)'; kf in Zehnerpotenz."""
    if k not in st:
        return None
    s = st[k]
    f = (lambda x: f"{x:.1e}") if k == "kf" else (lambda x: f"{x:.2f}" if k in ("konsistenzzahl", "trockendichte",
                                                                               "proctordichte") else f"{x:.1f}")
    spanne = f(s["min"]) if s["min"] == s["max"] else f"{f(s['min'])}–{f(s['max'])}"
    return (f"{spanne} {s['einheit']} (n = {s['n']}, Mittel {f(s['mittel'])})".replace(".", ",")
            .replace(" (", " (").strip())


def pset(st: dict) -> dict:
    out = {}
    for k, s in st.items():
        n = NAMEN.get(k, k)
        out.update({f"{n}_min": s["min"], f"{n}_max": s["max"], f"{n}_mean": round(s["mittel"], 6), f"{n}_n": s["n"]})
    if out:
        out["Art"] = "gemessene Werte aus den Laborblättern des Gutachtens; keine charakteristischen Werte"
    return out
