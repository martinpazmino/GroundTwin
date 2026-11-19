"""Text einer Seite fuer die Zusatzstufen (Kennwerte, Labor, Homogenbereiche): Textebene oder OCR (Issue #18).

Eine Seite ohne Textebene, aber mit Bild (Scan), wird mit derselben OCR gelesen wie die Bohrprofile
(prototyp_v4.ocr_words: RapidOCR, Cache ueber GEO_OCR_CACHE). Ein OCR-Kasten ist eine Zeile; Woerter und Zeilen
haben Ansichtskoordinaten wie die Textebene, so dass die Regeln der Stufen unveraendert gelten. Ohne OCR-Paket
bleibt die Seite stumm (``ocr`` False, die Stufe meldet das).

Woher der Text kommt, steht im Ergebnis (``quelle``: "Text" oder "OCR"): OCR-Werte sind unsicherer und werden so
gekennzeichnet, nie still mit der Textebene gleichgesetzt.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pymupdf

MIN_TEXT = 30                  # Zeichen: darunter gilt eine Seite mit Bild als Scan


@dataclass
class Seite:
    text: str
    zeilen: list[tuple[pymupdf.Rect, str]] = field(default_factory=list)
    woerter: list[tuple[pymupdf.Rect, str]] = field(default_factory=list)
    bloecke: list[tuple[pymupdf.Rect, str]] = field(default_factory=list)
    quelle: str = "Text"


FALTEN = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "Ä": "A", "Ö": "O", "Ü": "U", "β": "ss"})


def falten(t: str) -> str:
    """Fuer den Vergleich mit Regeln: Umlaute ohne Punkte, ß als ss (die OCR verliert sie oft: 'gema', 'Kohasion')."""
    return (t or "").translate(FALTEN).replace("ß", "ss")


def _norm(t: str) -> str:
    return " ".join((t or "").replace("­", "").split())


def ist_scan(seite: pymupdf.Page) -> bool:
    return len(seite.get_text().strip()) < MIN_TEXT and bool(seite.get_images())


def lesen(seite: pymupdf.Page, ocr: bool = True) -> Seite:
    """Zeilen, Woerter und Bloecke der Seite; bei einem Scan aus der OCR (Zeile = Block)."""
    if not (ocr and ist_scan(seite)):
        zeilen = []
        for blk in seite.get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                t = _norm(" ".join(s["text"] for s in ln["spans"]))
                if t:
                    zeilen.append((pymupdf.Rect(ln["bbox"]), t))
        woerter = [(pymupdf.Rect(w[:4]), w[4]) for w in seite.get_text("words")]
        bloecke = [(pymupdf.Rect(b[:4]), _norm(b[4])) for b in seite.get_text("blocks") if b[4].strip()]
        return Seite(seite.get_text(), zeilen, woerter, bloecke, "Text")
    try:
        from prototyp_v4 import ocr_words
    except ImportError:
        return Seite("", quelle="OCR nicht verfuegbar")
    roh = ocr_words(seite)
    je: dict[int, list] = {}
    for r, t, nr, _ in roh:
        je.setdefault(nr, []).append((pymupdf.Rect(r), t))
    zeilen = []
    for ws in je.values():
        rr = pymupdf.Rect(ws[0][0])
        for r, _ in ws[1:]:
            rr |= r
        zeilen.append((rr, _norm(" ".join(t for _, t in ws))))
    zeilen.sort(key=lambda e: (round(e[0].y0 / 3), e[0].x0))
    woerter = [(r, t) for ws in je.values() for r, t in ws]
    return Seite("\n".join(t for _, t in zeilen), zeilen, woerter, list(zeilen), "OCR")
