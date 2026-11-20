"""Homogenbereiche, die der Gutachter im Bericht festlegt (Issue #21): eigene Stufe, prototyp_v4.py bleibt unberuehrt.

Drei allgemeine Formen, nie nach Buero oder PDF:

T  Tabelle: eine Zelle "Homogenbereich X" und links daneben (gleiche Hoehe) die Bodengruppen und der Name
   ("ST*, UL, UM, OU, TL (Auelehm) | Homogenbereich B").
L  Abschnitt: Ueberschrift "Homogenbereich X - Name", darunter bis zur naechsten Ueberschrift Zeilen wie
   "Bodengruppen nach DIN 18196: GE, GW, SU", "Ortsuebliche Bezeichnung: Auffuellung" (auch ueber den Seitenwechsel).
S  Satz: "Der Oberboden bildet den Homogenbereich O1", "Der Beton wird als Homogenbereich A1 bezeichnet".

Die ATV (DIN 18300, 18301 ...) sind die, die im Abschnitt der Homogenbereiche genannt werden; nennt er keine, bleibt
die Liste leer und das wird gesagt (nie geraten). Bodengruppen in eckigen Klammern sind Auffuellungen dieser Art
(DIN 18196): sie stehen getrennt, weil sie nicht fuer den gewachsenen Boden gelten.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pymupdf

import textebene

CODE = r"(?:[A-Z]{1,3}\s?\d{1,2}[a-z]?|[A-Z]{1,2}|\d{1,2})"
KOPF_RE = re.compile(rf"^\s*(?:\d+(?:\.\d+)*\.?\s+)?Homogenbereich\s+({CODE})(?![\w/])\s*(?:[–\-:]\s*(.+))?$")
SATZ_RE = re.compile(rf"\b(?:Der|Die|Das)\s+([A-ZÄÖÜ][\wäöüß\-]+)\s+(?:wird\s+als|bildet\s+den|bilden\s+den|gehört\s+zum)\s+"
                     rf"Homogenbereich\s+({CODE})\b")
SATZ_IN_RE = re.compile(rf"\bIn\s+den\s+Homogenbereich\s+({CODE})\s+(?:werden|wird)\s+(?:die|der|das)\s+"
                        rf"([\wäöüß\- ]{{3,60}}?)\s+(?:klassifiziert|eingestuft|zugeordnet|gestellt)")
SATZ_PAAR_RE = re.compile(rf"\b([A-ZÄÖÜ][\wäöüß\-]+)\s+und\s+([A-ZÄÖÜ][\wäöüß\-]+)\s+werden\s+den\s+Homogenbereichen\s+"
                          rf"({CODE})\s+und\s+({CODE})\s+(?:zugeteilt|zugeordnet)")
GRUPPEN_RE = re.compile(r"^Bodengruppe\w*\s*(?:\(?\s*(?:nach|gem\.?|gem[äa](?:ß|ss|B)?)\s*)?(?:DIN\s*18\s?196\)?)?\s*:?\s*(.*)$", re.I)
ORTSUEBLICH_RE = re.compile(r"Orts[üu]bliche\s+Bezeichnung\s*:?\s*(.*)", re.I)
TIEFE_RE = re.compile(r"Tiefe\s+(?:oberer|unterer)\s+Horizont", re.I)
ABSCHNITT_RE = re.compile(r"^\s*\d+(?:\.\d+)+\.?\s+[A-ZÄÖÜ][a-zäöüß]")          # '4.6 Bodenkennwerte'
ATV_RE = re.compile(r"DIN\s*18\s?3(\d\d)\b")
GRUPPE_RE = re.compile(r"(\[)?(?<![A-Za-z])((?:[GSTUO][WIEUTLMAH]\*?|HN|HZ|OK|F|A))(?![A-Za-z])(\])?")
PLURAL_RE = re.compile(rf"^\s*(?:\d+(?:\.\d+)*\.?\s+)?Homogenbereiche\s+({CODE}(?:\s*(?:/|,|und|bis)\s*{CODE})+)\s*$")


def _norm(t: str) -> str:
    return " ".join((t or "").replace("­", "").split())


def gruppen(text: str) -> tuple[list[str], list[str]]:
    """Bodengruppen DIN 18196 aus einem Text: (gewachsen, in eckigen Klammern = Auffuellung dieser Art)."""
    frei, klammer = [], []
    for m in GRUPPE_RE.finditer(text.replace("Ū", "U*")):
        g = m.group(2).replace("Ū", "U*")
        (klammer if m.group(1) or m.group(3) else frei).append(g)
    return sorted(set(frei)), sorted(set(klammer) - set(frei))


def _zeilen(seite) -> list[tuple[pymupdf.Rect, str]]:
    out = []
    for blk in seite.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            t = _norm(" ".join(s["text"] for s in ln["spans"]))
            if t:
                out.append((pymupdf.Rect(ln["bbox"]), t))
    return sorted(out, key=lambda e: (round(e[0].y0 / 3), e[0].x0))


def _links_der_zeile(r, zeilen, bloecke) -> list:
    """Form T: Bloecke links eines Tabellenkopfs 'Homogenbereich X' im Band bis zur Mitte der Nachbar-Koepfe
    derselben Spalte; leer, wenn links nichts mit Bodengruppen oder Namen steht (dann ist es eine Ueberschrift)."""
    spalte = [rr for rr, tt in zeilen if KOPF_RE.match(tt) and abs(rr.x0 - r.x0) < 30]
    ys = [(rr.y0 + rr.y1) / 2 for rr in spalte]
    y = (r.y0 + r.y1) / 2
    oben = max([(a + y) / 2 for a in ys if a < y - 1] or [y - 30])
    unten = min([(a + y) / 2 for a in ys if a > y + 1] or [y + 30])
    links = [b for b in bloecke if b[0].x1 < r.x0 - 2 and oben <= (b[0].y0 + b[0].y1) / 2 <= unten]
    zelle = " ".join(b[1] for b in links)
    return links if GRUPPE_RE.search(zelle) or re.search(r"\([^)]*[a-zäöü]", zelle) else []


def _name(je: dict, code: str, name: str, nr: int, beleg: str) -> None:
    e = je.setdefault(code.replace(" ", ""), _neu(code, name, nr, "Satz", beleg))
    e["name"] = e["name"] or name.strip()


def _neu(code: str, name: str, seite: int, form: str, beleg: str) -> dict:
    return {"bereich": code.replace(" ", ""), "name": name.strip(" –-:"), "bodengruppen": [], "bodengruppen_auffuellung": [],
            "seite": seite, "form": form, "beleg": beleg[:160], "atv": [], "hinweise": []}


def lesen(pdf, doc=None, ocr: bool = True) -> list[dict]:
    """Alle Homogenbereiche des Berichts (Seite 0-basiert), je Bereich einmal (spaetere Angaben ergaenzen).
    Gescannte Seiten ueber die OCR (textebene); dann quelle 'OCR' und ein Hinweis."""
    doc = doc or pymupdf.open(pdf)
    quelle = ["Text"]
    je: dict[str, dict] = {}
    offen: dict | None = None                       # Abschnitt (Form L), der ueber Zeilen und Seiten weiterlaeuft
    atv_text = ""
    for nr, seite in enumerate(doc):
        if "Homogenbereich" not in seite.get_text() and offen is None and not textebene.ist_scan(seite):
            continue
        s = textebene.lesen(seite, ocr)
        text = s.text
        if "Homogenbereich" not in text and offen is None:
            continue
        zeilen = sorted(s.zeilen, key=lambda e: (round(e[0].y0 / 3), e[0].x0))
        # Woerter, nicht Bloecke: ein Block fasst oft Name und Kopf zusammen ('(Auelehm) Homogenbereich B')
        bloecke = sorted(s.woerter, key=lambda w: (round(w[0].y0 / 3), w[0].x0))
        quelle[0] = s.quelle if quelle[0] != "OCR" else "OCR"
        if "Homogenbereich" in text:
            atv_text += " " + text
        flach = _norm(text)                          # Form S: Saetze ueber Zeilenumbrueche hinweg
        for sm in SATZ_RE.finditer(flach):
            _name(je, sm.group(2), sm.group(1), nr, sm.group(0))
        for sm in SATZ_IN_RE.finditer(flach):
            _name(je, sm.group(1), sm.group(2), nr, sm.group(0))
        for sm in SATZ_PAAR_RE.finditer(flach):
            _name(je, sm.group(3), sm.group(1), nr, sm.group(0))
            _name(je, sm.group(4), sm.group(2), nr, sm.group(0))
        for r, t in zeilen:
            if offen and (ABSCHNITT_RE.match(t) and "Homogenbereich" not in t):
                offen = None                         # neuer Abschnitt des Berichts: Bereich zu Ende
            if (pm := PLURAL_RE.match(t)):           # 'Homogenbereiche B1/B2': Bereiche ohne eigenen Abschnitt
                for c in re.findall(CODE, pm.group(1)):
                    je.setdefault(c.replace(" ", ""), _neu(c, "", nr, "Abschnitt", t))
                offen = None
                continue
            m = KOPF_RE.match(t)
            if m:
                links = _links_der_zeile(r, zeilen, bloecke)
                e = je.setdefault(m.group(1).replace(" ", ""), _neu(m.group(1), m.group(2) or "", nr,
                                                                   "Tabelle" if links else "Abschnitt", t))
                if links:                            # Form T: Bodengruppen und Name links in der Zeile
                    zelle = " ".join(b[1] for b in links)
                    frei, kl = gruppen(zelle)
                    e["bodengruppen"] = sorted(set(e["bodengruppen"]) | set(frei))
                    e["bodengruppen_auffuellung"] = sorted(set(e["bodengruppen_auffuellung"]) | set(kl))
                    if not e["name"] and (n := re.findall(r"\(([^)]*[a-zäöü][^)]*)\)", zelle)):
                        e["name"] = n[-1].strip()
                    e["beleg"] = (zelle + " | " + t)[:160]
                    offen = None
                else:
                    offen = e
                continue
            if offen is None:
                continue
            if (g := GRUPPEN_RE.search(t)):
                rest = g.group(1) or " ".join(t2 for r2, t2 in zeilen if r2.x0 > r.x1 and abs(r2.y0 - r.y0) < 4)
                if not rest:                         # Wert in der Zeile darunter
                    rest = next((t2 for r2, t2 in zeilen if r2.y0 > r.y0 + 1 and abs(r2.y0 - r.y1) < 14), "")
                frei, kl = gruppen(rest)
                offen["bodengruppen"] = sorted(set(offen["bodengruppen"]) | set(frei))
                offen["bodengruppen_auffuellung"] = sorted(set(offen["bodengruppen_auffuellung"]) | set(kl))
            elif (o := ORTSUEBLICH_RE.search(t)) and not offen.get("ortsueblich"):
                wert = o.group(1) or next((t2 for r2, t2 in zeilen if r2.y0 > r.y0 + 1 and abs(r2.y0 - r.y1) < 14), "")
                offen["ortsueblich"] = wert
                offen["name"] = offen["name"] or wert
    atv = sorted({f"DIN 183{m}" for m in ATV_RE.findall(atv_text)})
    out = []
    for e in je.values():
        e["atv"] = atv
        e["quelle"] = quelle[0]
        if quelle[0] == "OCR":
            e["hinweise"].append("aus der OCR gescannter Seiten: am PDF prüfen")
        if not atv:
            e["hinweise"].append("ATV im Bericht nicht genannt")
        if not e["bodengruppen"] and not e["bodengruppen_auffuellung"]:
            e["hinweise"].append("ohne Bodengruppen (Zuordnung nach dem Namen)")
        if not e["name"]:
            e["hinweise"].append("ohne Namen")
        out.append(e)
    return out


if __name__ == "__main__":                            # python homogenbereiche_text.py <pdf>
    import json
    print(json.dumps(lesen(Path(sys.argv[1])), indent=1, ensure_ascii=False))
