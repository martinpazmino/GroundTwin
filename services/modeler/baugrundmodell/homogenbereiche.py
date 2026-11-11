"""Homogenbereiche nach VOB/C (docs/28): Einheiten des Schichtmodells je Gewerk (ATV) zu Homogenbereichen zusammenfassen.

Ein Homogenbereich ist kein geologischer Begriff, sondern einer der Ausschreibung: Boden, der sich fuer ein Gewerk
gleich verhaelt. Dieselbe Schicht kann darum fuer DIN 18300 (Erdarbeiten) in einem anderen Bereich liegen als fuer
DIN 18301 (Bohrarbeiten). Die Zuordnung trifft der Planer; hier wird sie gespeichert, geprueft und ins IFC geschrieben:

- je Einheit und Bodenschicht ein Pset CPset_Homogenbereich_<ATV> (welcher Bereich, welche Kennwerte die ATV verlangt);
- auf Wunsch ein Modell nur aus Homogenbereichen: je Bereich ein IfcGeotechnicalStratum aus den Koerpern seiner
  Einheiten (gleiche Geometrie, anders gruppiert).

Welche Kennwerte je ATV anzugeben sind, steht in homogenbereiche.json mit Quelle; nichts davon wird still angewendet.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

DATEI = Path(__file__).with_name("homogenbereiche.json")
FARBEN = ["#c8553d", "#2a9d8f", "#e9c46a", "#457b9d", "#8d5a97", "#f4a261", "#6a994e", "#bc4749", "#277da1",
          "#b5838d", "#90be6d", "#577590"]          # je Bereich gut unterscheidbar (keine Bodenartfarben)


@lru_cache(maxsize=1)
def daten() -> dict:
    return json.loads(DATEI.read_text(encoding="utf-8"))


def atv_liste() -> list[dict]:
    return daten()["atv"]


def gewerk(code: str) -> str:
    for a in atv_liste():
        if a["code"] == code:
            return a["gewerk"]
    raise ValueError(f"unbekannte ATV '{code}' – bekannt: {', '.join(a['code'] for a in atv_liste())}")


def kennwerte(code: str) -> list[dict]:
    """Die Kennwerte, die die ATV fuer Boden verlangt: [{nr, name, art}] in der Reihenfolge der Matrix."""
    gewerk(code)
    zeile = daten()["matrix"][code]
    return [{**k, "art": zeile[k["nr"]]} for k in daten()["kennwerte"] if k["nr"] in zeile]


def kennwerte_text(code: str) -> str:
    """'1 ortsübliche Bezeichnung; 2 Korngrößenverteilung; …' mit Zusatz, wo die Art nicht schlicht erforderlich ist."""
    return "; ".join(f"{k['nr']} {k['name']}" + ("" if k["art"] == "erforderlich" else f" ({k['art']})")
                     for k in kennwerte(code))


def pset_name(code: str) -> str:
    return "CPset_Homogenbereich_" + re.sub(r"[^0-9A-Za-z]+", "", code)


def pruefen(zuordnung: dict | None) -> dict | None:
    """{ATV: {Einheit: Bereich}} pruefen und bereinigen; leerer Bereich = nicht zugeordnet. None = keine."""
    if not zuordnung:
        return None
    if not isinstance(zuordnung, dict):
        raise ValueError("Homogenbereiche: je ATV eine Zuordnung Einheit → Bereich")
    out = {}
    for code, je in zuordnung.items():
        gewerk(code)
        if not isinstance(je, dict):
            raise ValueError(f"Homogenbereiche {code}: Zuordnung Einheit → Bereich erwartet")
        sauber = {}
        for einheit, bereich in je.items():
            b = re.sub(r"\s+", " ", str(bereich or "")).strip()
            if len(b) > 40:
                raise ValueError(f"Homogenbereich '{b[:20]}…': höchstens 40 Zeichen")
            if b:
                sauber[str(einheit)] = b
        if sauber:
            out[code] = sauber
    return out or None


def vorschlag(einheiten: list[str]) -> dict[str, str]:
    """Erste Zuordnung: je Einheit ein eigener Bereich (B1, B2, … von oben). Zusammenfassen entscheidet der Planer."""
    vorlage = daten()["namensvorlage"]
    return {e: vorlage.format(n=i + 1) for i, e in enumerate(einheiten)}


def bereiche(je: dict[str, str], einheiten: list[str]) -> tuple[list[dict], list[str]]:
    """Bereiche in Modellreihenfolge (nach ihrer obersten Einheit) mit ihren Einheiten, und Hinweise.

    Einheiten ohne Bereich bleiben je ein eigener Eintrag (bereich None): nichts verschwindet aus dem Modell.
    """
    hinweise = [f"Homogenbereich-Zuordnung für '{e}': keine solche Einheit im Modell" for e in je if e not in einheiten]
    out: list[dict] = []
    nach_name: dict[str, dict] = {}
    for e in einheiten:
        b = je.get(e)
        if b is None:
            out.append({"bereich": None, "einheiten": [e]})
            continue
        if b not in nach_name:
            nach_name[b] = {"bereich": b, "einheiten": []}
            out.append(nach_name[b])
        nach_name[b]["einheiten"].append(e)
    ohne = [x["einheiten"][0] for x in out if x["bereich"] is None]
    if ohne:
        hinweise.append("ohne Homogenbereich: " + ", ".join(ohne))
    return out, hinweise


def farbe(n: int) -> str:
    return FARBEN[n % len(FARBEN)]
