"""Laborversuche aus den Anlagen des Gutachtens (Issue #18): eigene Stufe, prototyp_v4.py bleibt unberuehrt.

Gelesen werden Pruefblaetter der bodenmechanischen Versuche (Wassergehalt, Zustandsgrenzen, Korngroessenverteilung,
Gluehverlust, Kalkgehalt, Durchlaessigkeit, Proctor, CBR). Allgemeine Regeln der Formblaetter, nie je Labor:

- Probe: ein Bohrungs-Code mit Tiefe von-bis ("Entnahmestelle: BS 5", "Tiefe: 2,5 - 3,5"; "BK2 (5,0-6,0m)");
  "BS 1 + 2" ist eine Mischprobe aus zwei Bohrungen.
- Wert: "Name = Zahl" (ausdrueckliches Ergebnis) vor "Name | Einheit | Zahl"; eine Achsbeschriftung
  ("Wassergehalt w [%] | 24.0") ist kein Ergebnis.
- Mehrere Proben auf einem Blatt (Tabelle): je Probe die letzte Zahl ihrer Zeile = Ergebnis des Blatts
  (Formblaetter stellen das Ergebnis in die letzte Spalte); ebenso Blaetter ohne "=" (Gluehverlust).
- Korngroessen: "T/U/S/G [%]: 13.1/16.9/69.8/0.3".

Werte ausserhalb der moeglichen Spanne bekommen einen Hinweis (markiert, nicht verworfen). Chemische Analysen
(Umwelt) sind keine bodenmechanischen Versuche und bleiben aussen vor.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pymupdf

import textebene

CODE_RE = re.compile(r"(?<![A-Za-z0-9])((?:B|BK|KB|KRB|RKS|BS|GWM|SCH|DPH|RB|S)\s?\d{1,3}[a-z]?(?:/\d{2})?)"
                     r"((?:\s*(?:\+|,|und)\s*\d{1,3}[a-z]?)*)(?![\d.,])")
TIEFE_RE = re.compile(r"(\d{1,2}[.,]\d{1,2})\s*[-–]\s*(\d{1,2}[.,]\d{1,2})\s*m?\b")
ZAHL_RE = re.compile(r"^\s*[<>≤≥~]?\s*(-?\d+(?:[.,]\d+)?)\s*(?:%|g/cm³|g/cm3|t/m³|m/s|kN/m³)?\s*$")
EINHEIT_TOKEN = re.compile(r"^\s*(?:%|\[%\]|g/cm³|g/cm3|t/m³|m/s|kN/m³|-)\s*$")
KF_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*[·x*]?\s*10\s*(?:\^|E)?\s*([-−–]\s*\d{1,2})")

# Versuch (aus Norm oder Titel des Blatts) und das Ergebnis, das die letzte Zahl einer Probe ist
VERSUCHE = (
    ("zustandsgrenzen", re.compile(r"17892-12|Zustandsgrenzen|Fliess-\s*und\s*Ausrollgrenze", re.I), None),
    ("korngroesse", re.compile(r"17892-4|Kornungslinie|Korngrossenverteilung", re.I), None),
    ("gluehverlust", re.compile(r"18\s?128|Gluhverlust", re.I), "gluehverlust"),
    ("kalkgehalt", re.compile(r"18\s?129|Kalkgehalt", re.I), "kalkgehalt"),
    ("durchlaessigkeit", re.compile(r"17892-11|18\s?130|Durchlassigkeit", re.I), None),
    ("proctor", re.compile(r"18\s?127|Proctor", re.I), None),
    ("cbr", re.compile(r"CBR", re.I), None),
    ("wassergehalt", re.compile(r"17892-1(?!\d)|Wassergehalt\s+nach", re.I), "wassergehalt"),
)
# Kennwert -> Namen im Blatt (ohne Einheit); Reihenfolge zaehlt (korrigierter vor einfachem Wassergehalt)
NAMEN = (
    ("wassergehalt_korrigiert", re.compile(r"^Korr\.?\s*Wassergehalt", re.I)),
    ("wassergehalt", re.compile(r"^(?:nat(?:urlicher|\.)\s*)?Wassergehalt(?:\s*w)?(?:\s*vor\s*dem\s*Versuch)?\s*(?:=|\[%\]|$)", re.I)),
    ("fliessgrenze", re.compile(r"^Fliessgrenze(?:\s*wL)?\s*(?:=|$)", re.I)),
    ("ausrollgrenze", re.compile(r"^Ausrollgrenze(?:\s*wP)?\s*(?:=|$)", re.I)),
    ("plastizitaetszahl", re.compile(r"^Plastizitatszahl(?:\s*I\s*P)?\s*(?:=|$)", re.I)),
    ("konsistenzzahl", re.compile(r"^Konsistenzzahl(?:\s*I\s*C)?\s*(?:=|$)", re.I)),
    ("gluehverlust", re.compile(r"^Gluhverlust(?:\s*V\s*gl)?\s*(?:=|\[%\]|$)", re.I)),
    ("kalkgehalt", re.compile(r"^Kalkgehalt(?:\s*V\s*Ca)?\s*(?:=|\[%\]|$)", re.I)),
    ("trockendichte", re.compile(r"^(?:Proctor-?)?Trockendichte(?:\s*ρ\s*d)?\s*(?:=|$)", re.I)),
    ("proctordichte", re.compile(r"^Proctordichte(?:\s*ρ\s*Pr)?\s*(?:=|$)", re.I)),
    ("optimaler_wassergehalt", re.compile(r"^optimaler\s+Wassergehalt(?:\s*w\s*Pr)?\s*(?:=|$)", re.I)),
    ("cbr", re.compile(r"^CBR\s*-?\s*WERT\s*(?:=|$)", re.I)),
)
EINHEITEN = {"wassergehalt": "%", "wassergehalt_korrigiert": "%", "fliessgrenze": "%", "ausrollgrenze": "%",
             "plastizitaetszahl": "%", "konsistenzzahl": "-", "gluehverlust": "%", "kalkgehalt": "%",
             "trockendichte": "g/cm³", "proctordichte": "g/cm³", "optimaler_wassergehalt": "%", "cbr": "%",
             "kf": "m/s", "ton": "%", "schluff": "%", "sand": "%", "kies": "%"}
MOEGLICH = {"wassergehalt": (0, 400), "wassergehalt_korrigiert": (0, 400), "fliessgrenze": (5, 400),
            "ausrollgrenze": (0, 200), "plastizitaetszahl": (0, 300), "konsistenzzahl": (-1, 2.5),
            "gluehverlust": (0, 100), "kalkgehalt": (0, 100), "trockendichte": (0.2, 2.8), "proctordichte": (0.5, 2.6),
            "optimaler_wassergehalt": (0, 100), "cbr": (0, 300), "kf": (1e-13, 1.0),
            "ton": (0, 100), "schluff": (0, 100), "sand": (0, 100), "kies": (0, 100)}
CHEMIE_RE = re.compile(r"Prufbericht|Analysennummer|Ersatzbaustoff|LAGA|Feststoff|Eluat|PAK|Schwermetall", re.I)


def _f(s: str) -> float:
    return float(s.replace(",", "."))


def _tokens(s) -> list[str]:
    """Zeilen in Lesereihenfolge; Umlaute gefaltet nur fuer OCR-Text (die Regeln kennen beide Schreibweisen)."""
    return [textebene.falten(t.strip()) for t in s.text.splitlines() if t.strip()]


def proben_auf(tokens: list[str]) -> list[tuple[int, list[str], float, float]]:
    """(Token-Index, Bohrungen, von, bis) je Probe: Code mit Tiefe im selben oder im naechsten Token."""
    out = []
    for i, t in enumerate(tokens):
        m = CODE_RE.search(t)
        if not m or "Projekt" in t:
            continue
        rest = t[m.end():]
        naechster = tokens[i + 1] if i + 1 < len(tokens) else ""
        tm = TIEFE_RE.search(rest) or TIEFE_RE.match(naechster) or \
            (TIEFE_RE.search(naechster) if re.match(r"Tiefe\b", naechster) else None)
        if not tm:
            continue
        basis = re.match(r"([A-Za-z]+)\s?", m.group(1)).group(1)
        codes = [re.sub(r"\s+", " ", m.group(1))] + [f"{basis} {n}" for n in re.findall(r"\d{1,3}[a-z]?", m.group(2))]
        codes = [re.sub(r"^([A-Za-z]+)(\d)", r"\1 \2", c) for c in codes]
        out.append((i, codes, _f(tm.group(1)), _f(tm.group(2))))
    return out


def _wert_nach(tokens: list[str], i: int) -> float | None:
    """Erste Zahl nach dem Namen: 'Name = | 16.5 %' oder 'Name | % | 13,1'; eine Achse (Zahl direkt nach
    'Name [%]' ohne '=') zaehlt nicht."""
    t = tokens[i]
    inline = re.search(r"=\s*([<>]?\s*-?\d+(?:[.,]\d+)?)", t)
    if inline:
        return _f(inline.group(1).lstrip("<> "))
    hat_gleich = t.rstrip().endswith("=")
    for k in range(i + 1, min(i + 4, len(tokens))):
        if EINHEIT_TOKEN.match(tokens[k]):
            hat_gleich = True                         # 'Name | % | Zahl': Einheit als eigene Zelle
            continue
        m = ZAHL_RE.match(tokens[k])
        if m and hat_gleich:
            return _f(m.group(1))
        return None
    return None


def _pruefen(werte: dict) -> list[str]:
    out = []
    for k, v in werte.items():
        lo, hi = MOEGLICH.get(k, (None, None))
        if lo is not None and not (lo <= v <= hi):
            out.append(f"{k}: {v} außerhalb {lo}–{hi} {EINHEITEN.get(k, '')}")
    if all(k in werte for k in ("fliessgrenze", "ausrollgrenze", "plastizitaetszahl")) and \
            abs(werte["fliessgrenze"] - werte["ausrollgrenze"] - werte["plastizitaetszahl"]) > 0.6:
        out.append("IP ≠ wL − wP")
    return out


def lesen(pdf, doc=None, ocr: bool = True) -> list[dict]:
    """Alle Proben mit Werten (Seite 0-basiert); dieselbe Probe auf mehreren Blaettern wird zusammengefuehrt."""
    doc = doc or pymupdf.open(pdf)
    je: dict[tuple, dict] = {}
    for nr, seite in enumerate(doc):
        s = textebene.lesen(seite, ocr)
        tokens = _tokens(s)
        text = " ".join(tokens)
        if CHEMIE_RE.search(text) or "Entnahme" not in text and "Probe" not in text:
            continue
        versuch, letzte = next(((v, l) for v, rx, l in VERSUCHE if rx.search(text)), (None, None))
        if versuch is None:
            continue
        proben = proben_auf(tokens)
        if not proben:
            continue
        ergebnisse: list[tuple[tuple, dict]] = []
        werte_hinweis: list[str] = []
        if len(proben) == 1:
            werte = {}
            for i, t in enumerate(tokens):
                for k, rx in NAMEN:
                    if k not in werte and rx.search(t) and (w := _wert_nach(tokens, i)) is not None:
                        werte[k] = w
                        break
            feld = r"\s*(\d+(?:[.,]\d+)?|-)\s*"            # '-': Fraktion nicht vorhanden/bestimmt
            if versuch == "korngroesse" and "T/U/S/G" in text and \
                    (m := re.search(rf"{feld}/{feld}/{feld}/{feld}(?=\s|$)", text[text.find("T/U/S/G") + 7:])):
                werte.update({k: _f(v) for k, v in zip(("ton", "schluff", "sand", "kies"), m.groups()) if v != "-"})
            if (m := KF_RE.search(text)) and (versuch == "durchlaessigkeit" or re.search(r"\bk\s*\[m/s\]", text)):
                werte["kf"] = _f(m.group(1)) * 10 ** int(m.group(2).replace("−", "-").replace("–", "-").replace(" ", ""))
                if versuch != "durchlaessigkeit":
                    hinweis_kf = re.search(r"k\s*\[m/s\]\s*\(([^)]+)\)", text)
                    werte_hinweis.append("kf aus der Kornverteilung" + (f" ({hinweis_kf.group(1)})" if hinweis_kf else "")
                                         + ", nicht gemessen")
            if letzte and letzte not in werte:        # Ergebnis = letzte Zahl des Blatts
                zahlen = [ZAHL_RE.match(t) for t in tokens[proben[0][0]:]]
                zahlen = [_f(z.group(1)) for z in zahlen if z]
                if zahlen:
                    werte[letzte] = zahlen[-1]
            _, codes, von, bis = proben[0]
            ergebnisse.append(((tuple(codes), von, bis), werte))
        elif letzte:                                  # Tabelle: je Probe die letzte Zahl ihrer Zeile
            grenzen = [p[0] for p in proben] + [len(tokens)]
            for (i, codes, von, bis), ende in zip(proben, grenzen[1:]):
                zahlen = [_f(z.group(1)) for t in tokens[i + 2:ende] if (z := ZAHL_RE.match(t))]
                if zahlen:
                    ergebnisse.append(((tuple(codes), von, bis), {letzte: zahlen[-1]}))
        bodenart = next((tokens[i + 1] for i, t in enumerate(tokens) if t.startswith("Bodenart:") and t == "Bodenart:"
                         and i + 1 < len(tokens)), "")
        for schluessel, werte in ergebnisse:
            if not werte:
                continue
            p = je.setdefault(schluessel, {"bohrungen": list(schluessel[0]), "von": schluessel[1], "bis": schluessel[2],
                                           "werte": {}, "versuche": [], "seiten": [], "hinweise": []})
            for k, v in werte.items():
                p["werte"].setdefault(k, v)
            p["versuche"] = sorted(set(p["versuche"]) | {versuch})
            p["seiten"] = sorted(set(p["seiten"]) | {nr})
            p["hinweise"] += [h for h in werte_hinweis if h not in p["hinweise"]]
            p["quelle"] = "OCR" if s.quelle == "OCR" or p.get("quelle") == "OCR" else "Text"
            if s.quelle == "OCR" and not any("OCR" in h for h in p["hinweise"]):
                p["hinweise"].append("aus der OCR eines gescannten Blatts: Werte am PDF prüfen")
            if len(schluessel[0]) > 1 and "Mischprobe" not in " ".join(p["hinweise"]):
                p["hinweise"].append(f"Mischprobe aus {', '.join(schluessel[0])}")
            if bodenart and "bodenart" not in p:
                p["bodenart"] = bodenart
    out = list(je.values())
    for p in out:
        p["hinweise"] += _pruefen(p["werte"])
    return out


if __name__ == "__main__":                            # python labor.py <pdf>
    import json
    print(json.dumps(lesen(Path(sys.argv[1])), indent=1, ensure_ascii=False))
