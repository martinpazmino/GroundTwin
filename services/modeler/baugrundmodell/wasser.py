"""Art und Datum der Wasserstaende (Issue #26, docs/06 §4).

Ein Wasserstand einer Bohrung hat eine Tiefe, eine Art und, wenn das Gutachten es sagt, ein Datum. Die Art kommt aus
dem Text am Symbol, aus dem Schichtenverzeichnis oder aus der Legende; steht nichts da, bleibt sie *unbestimmt* und
wird nie geraten. Aeltere Extraktionen schreiben ``kind: "gemessen"``: das ist dasselbe wie *unbestimmt*.

Arten (Werte von ``kind``):
- ``angetroffen``: beim Bohren angetroffen (Anschnitt, Wasserzutritt, angebohrt)
- ``Ruhewasser``: Ruhewasserspiegel, auch "angestiegen" (der Stand, auf den das Wasser steigt)
- ``Bohrende``: nach Bohrende gemessen
- ``Schichtenwasser``: Schichten-, Stau- oder Sickerwasser; kein zusammenhaengendes Grundwasser, bleibt getrennt
- ``unbestimmt``: Art im Gutachten nicht angegeben

Bemessungswasserstand, HGW, MGW und MHGW sind keine Staende einer Bohrung; sie stehen im Text des Gutachtens und
gehoeren zum Projekt (``wasserstaende`` der Extraktion).
"""
from __future__ import annotations

import re

ARTEN = ("Ruhewasser", "Bohrende", "angetroffen", "unbestimmt", "Schichtenwasser")
# fuer die Grundwasserflaeche: je Bohrung die erste vorhandene Art (Ruhewasser ist der Stand, auf den das Wasser steigt)
VORRANG = ("Ruhewasser", "Bohrende", "unbestimmt", "angetroffen")
TEXT = {"Ruhewasser": "Ruhewasser", "Bohrende": "nach Bohrende", "angetroffen": "angetroffen (Anschnitt)",
        "Schichtenwasser": "Schichtenwasser", "unbestimmt": "Art nicht angegeben"}

_ALT = {"gemessen": "unbestimmt", "ruhe": "Ruhewasser", "ruhewasser": "Ruhewasser", "nach_bohrende": "Bohrende",
        "bohrende": "Bohrende", "angetroffen": "angetroffen", "schichtenwasser": "Schichtenwasser",
        "unbestimmt": "unbestimmt"}

# Reihenfolge zaehlt: "Grundwasser angestiegen" ist Ruhewasser, "Schichtenwasser angetroffen" ist Schichtenwasser
SCHLUESSEL = (
    ("Schichtenwasser", re.compile(r"schichtenwasser|stauwasser|sickerwasser", re.I)),
    ("Bohrende", re.compile(r"nach\s*(?:dem\s*)?bohrende|bohrende", re.I)),
    ("Ruhewasser", re.compile(r"ruhe\s*wasser|ruhewsp|\bRWS?p?\b|angestiegen", re.I)),
    ("angetroffen", re.compile(r"angetroffen|angebohrt|anschnitt|wasserzutritt|zulauf", re.I)),
)
DATUM_RE = re.compile(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.(\d{4}|\d{2})(?![\d.])")


def art(kind: str | None) -> str:
    """Art eines Wasserstands, auch aus aelteren Werten ("gemessen" → unbestimmt)."""
    return _ALT.get((kind or "").strip().lower(), "unbestimmt") if kind not in ARTEN else kind


def art_aus_text(text: str) -> str | None:
    """Art aus einem Stichwort im Text; None, wenn keines dasteht (dann bleibt die Art unbestimmt)."""
    for a, rx in SCHLUESSEL:
        if rx.search(text or ""):
            return a
    return None


def datum_aus_text(text: str) -> str | None:
    """Erstes gueltiges Datum dd.mm.yy(yy) als ISO; zweistellige Jahre: 00-69 → 20xx, 70-99 → 19xx."""
    for m in DATUM_RE.finditer(text or ""):
        t, mo, j = int(m.group(1)), int(m.group(2)), m.group(3)
        jahr = int(j) if len(j) == 4 else (2000 + int(j) if int(j) < 70 else 1900 + int(j))
        if 1 <= t <= 31 and 1 <= mo <= 12 and 1950 <= jahr <= 2100:
            return f"{jahr:04d}-{mo:02d}-{t:02d}"
    return None


def wahl(staende: list[dict]) -> tuple[str | None, list[dict]]:
    """Fuer die Grundwasserflaeche: die Art mit Vorrang und ihre Staende (Schichtenwasser nie)."""
    for a in VORRANG:
        s = [g for g in staende if art(g.get("kind")) == a]
        if s:
            return a, s
    return None, []
