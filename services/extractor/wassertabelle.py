"""Wasserstands-Tabellen im Text des Gutachtens (Issue #26): eigene Stufe, prototyp_v4.py bleibt unberuehrt.

Viele Gutachten listen die Wasserstaende je Aufschluss in einer Tabelle ("Aufschluss | Wasserstand [m u. GOK] |
Wasserart"). Allgemeine Regeln, nie je Buero:

- Tabelle: eine Seite mit "Wasserst..." und "m u. GOK"; Zeile = Bohrungs-Code, dahinter (naechste Zeilen) eine Tiefe,
  wahlweise mit Fussnotenzeichen ("3,00*"), wahlweise die Wasserart ("Grundwasser", "Schichtenwasser").
- Art (nie geraten, Regeln von prototyp_v4.gw_info): die Fussnote eines Werts ("*) Grundwasseranschnitt") vor der
  Wasserart-Spalte vor dem Satz zur Tabelle ("... wie folgt nach Bohrende eingemessen"); sonst unbestimmt.
- Datum: ein einzelnes Datum im Satz; ein Zeitraum ("vom 01.07. bis 15.10.2020") ist kein Messtag und bleibt im Beleg.

``einarbeiten`` fuehrt die Zeilen mit den Staenden der Bohrungen zusammen: gleiche Tiefe (± 3 cm) -> Art/Datum
ergaenzen, wo sie fehlen; ein Stand, den das Profil nicht hat, kommt mit Beleg "Tabelle" dazu und wird gemeldet.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pymupdf

import textebene

CODE_RE = re.compile(r"^((?:B|BK|KB|KRB|RKS|BS|GWM|SCH|RB|S)\s?\d{1,3}[a-z]?(?:/\d{2})?)$")
TIEFE_RE = re.compile(r"^(\d{1,2}[.,]\d{1,2})\s*(\*+|\d\))?$")
FUSSNOTE_RE = re.compile(r"^(\*+|\d\))\s*\)?\s*(.{3,80})$")
WASSERART_RE = re.compile(r"^(Grundwasser|Schichtenwasser|Stauwasser|Sickerwasser|Ruhewasser|kein\w*.*)$", re.I)


def _f(s: str) -> float:
    return float(s.replace(",", "."))


def _art(text: str) -> dict:
    from prototyp_v4 import gw_info
    return gw_info(text)


def lesen(pdf, doc=None, ocr: bool = True) -> list[dict]:
    """Zeilen {code, depth, kind, observed_on?, evidence, page} aus den Wasserstands-Tabellen des Berichts."""
    doc = doc or pymupdf.open(pdf)
    out = []
    for nr, seite in enumerate(doc):
        s = textebene.lesen(seite, ocr)
        flach = " ".join(s.text.split())
        if not (re.search(r"Wasserst", flach) and re.search(r"m\s*u\.?\s*(?:GOK|GOF|AP|Ansatz)", flach)):
            continue
        tokens = [t.strip() for t in s.text.splitlines() if t.strip()]
        fussnoten = {m.group(1): m.group(2) for t in tokens if (m := FUSSNOTE_RE.match(t)) and not CODE_RE.match(t)}
        # Satz zur Tabelle: bis 160 Zeichen vor dem Verb (ein Datum '01.07.' beendet ihn nicht)
        satz = next((flach[max(0, m.start() - 160):m.end()].split(": ")[-1].strip()
                     for m in re.finditer(r"(?:Grund)?[Ww]asser\b.{0,120}?(?:eingemessen|gemessen|angetroffen|festgestellt)",
                                          flach)), "")
        satz_art = _art(satz) if satz else {"kind": "unbestimmt"}
        if re.search(r"\bvom\b.{0,30}\bbis\b|\d\.\s*(?:bis|–)\s*\d", satz, re.I):
            satz_art.pop("observed_on", None)              # Zeitraum, kein Messtag
        for i, t in enumerate(tokens):
            m = CODE_RE.match(t)
            if not m or i + 1 >= len(tokens):
                continue
            tm = TIEFE_RE.match(tokens[i + 1])
            if not tm:
                continue
            art_spalte = tokens[i + 2] if i + 2 < len(tokens) and WASSERART_RE.match(tokens[i + 2]) else ""
            zeichen = tm.group(2) or ""
            belege, info = [], {"kind": "unbestimmt"}
            if zeichen and zeichen in fussnoten:                     # Fussnote vor Spalte vor Satz
                info = _art(fussnoten[zeichen])
                belege.append(f"Fußnote {zeichen}) {fussnoten[zeichen]}")
            if info["kind"] == "unbestimmt" and art_spalte:
                info = _art(art_spalte)
                if info["kind"] != "unbestimmt":
                    belege.append(f"Wasserart: {art_spalte}")
            if info["kind"] == "unbestimmt" and satz_art["kind"] != "unbestimmt":
                info = dict(satz_art)
                belege.append("…" + satz[-110:] if len(satz) > 110 else satz)
            zeile = {"code": re.sub(r"\s+", " ", m.group(1)), "depth": _f(tm.group(1)), "kind": info["kind"],
                     "page": nr, "quelle": s.quelle,
                     "evidence": f"Tabelle S. {nr + 1}: {t} {tokens[i + 1]}" + (f" ({'; '.join(belege)})" if belege else "")}
            if info.get("observed_on"):
                zeile["observed_on"] = info["observed_on"]
            if art_spalte.lower().startswith("kein"):
                zeile["kind"] = "kein"
            out.append(zeile)
    return out


def _code(c: str) -> str:
    m = re.match(r"\s*([A-Za-z]+)\s*0*(\d+)\s*([a-z]?)", c or "")
    return f"{m.group(1).upper()}{m.group(2)}{m.group(3)}" if m else (c or "").replace(" ", "").upper()


def einarbeiten(doc: dict, zeilen: list[dict]) -> dict:
    """Die Tabellenzeilen in die Staende der Bohrungen (doc['boreholes'][*]['groundwater']); Rueckgabe: Zaehler."""
    je = {}
    for b in doc.get("boreholes") or []:
        je.setdefault(_code(b["code"]), []).append(b)
    zaehler = {"ergaenzt": 0, "neu": 0, "ohne_bohrung": 0}
    for z in zeilen:
        if z["kind"] == "kein":
            continue
        bs = je.get(_code(z["code"]))
        if not bs:
            zaehler["ohne_bohrung"] += 1
            continue
        for b in bs:
            gw = b.setdefault("groundwater", [])
            gleich = next((g for g in gw if abs(float(g["depth"]) - z["depth"]) <= 0.03), None)
            if gleich:
                if gleich.get("kind") in (None, "", "gemessen", "unbestimmt") and z["kind"] != "unbestimmt":
                    gleich["kind"] = z["kind"]
                    gleich["evidence"] = "; ".join(x for x in (gleich.get("evidence"), z["evidence"]) if x)
                    zaehler["ergaenzt"] += 1
                if z.get("observed_on") and not gleich.get("observed_on"):
                    gleich["observed_on"] = z["observed_on"]
                continue
            gok = b.get("gok_nhn")
            gw.append({"depth": z["depth"], "nhn": round(gok - z["depth"], 2) if gok is not None else None,
                       "kind": z["kind"], **({"observed_on": z["observed_on"]} if z.get("observed_on") else {}),
                       "evidence": z["evidence"]})
            gw.sort(key=lambda g: float(g["depth"]))
            b.setdefault("issues", []).append(f"Wasserstand {z['depth']:.2f} m aus der Tabelle im Bericht "
                                              f"(S. {z['page'] + 1}), nicht im Profil".replace(".", ",", 1))
            if (b.get("groundwater_status") or "").lower().startswith("kein"):
                b["issues"].append("Profil sagt 'kein Grundwasser', die Tabelle nennt einen Stand: prüfen")
            zaehler["neu"] += 1
    return zaehler


if __name__ == "__main__":                            # python wassertabelle.py <pdf>
    import json
    print(json.dumps(lesen(Path(sys.argv[1])), indent=1, ensure_ascii=False))
