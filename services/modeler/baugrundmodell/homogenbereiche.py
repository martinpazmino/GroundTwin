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


# ---------------------------------------------------------------- Vorschlag je Anwendungsfall (docs/28 §6)
# Verhalten im Bau aus der Bodenart der Einheit (normen.json, Feld "art"); nur Einheiten gleichen Verhaltens koennen
# einen Bereich bilden. Unbekanntes bleibt immer einzeln.
_NICHTBINDIG = {"Kies", "Sand", "Steine", "Bloecke"}
_BINDIG_BODEN = {"Schluff", "Ton"}
VERHALTEN_TEXT = {"anthropogen": "anthropogen (Auffüllung)", "organisch": "organisch", "fels": "Fels",
                  "nichtbindig": "nichtbindig", "bindig": "bindig", "unbekannt": "nicht klassifiziert"}


def _verhalten(bodenarten: list[str]) -> str:
    from .normen import KLASSEN
    arten = set()
    for b in bodenarten:
        art = KLASSEN.get(b, {}).get("art", "unbekannt")
        if art == "boden":
            arten.add("nichtbindig" if b in _NICHTBINDIG else "bindig" if b in _BINDIG_BODEN else "unbekannt")
        elif art == "geologisch":
            arten.add("bindig")                   # Geschiebemergel, Loess, Lehm, Klei, Mergel: feinkoernig gepraegt
        else:
            arten.add(art)
    return arten.pop() if len(arten) == 1 else "unbekannt"     # gemischte Einheit: nicht zusammenlegen


def stufe(code: str) -> tuple[str, str]:
    """Wie fein ein Vorschlag fuer die ATV unterscheidet, aus ihren Kennwerten (nicht je ATV festgelegt)."""
    nr = {k["nr"] for k in kennwerte(code)}
    if len(nr) <= 7:
        return "grob", f"{len(nr)} Kennwerte: nur das Verhalten (nichtbindig, bindig, organisch, anthropogen, Fels)"
    if nr & {"4", "18"}:
        return "fein", ("Mineralogie bzw. Abrasivität verlangt (Kennwert 4/18): dazu Bodengruppe bzw. Bodenart und "
                        "Steine/Blöcke getrennt")
    return "standard", "dazu die Bodengruppe DIN 18196 (sonst die Hauptbodenart) getrennt"


def merkmale(einheit: dict) -> dict:
    """Verhalten, haeufigste genannte Bodengruppe und Steine/Bloecke einer Einheit (Bericht: name, bodenarten, schichten)."""
    from collections import Counter

    from .normen import deuten
    gruppen: Counter = Counter()
    steine = 0
    for s in einheit.get("schichten") or []:
        d = deuten(s.get("beschreibung"), s.get("bodenart"))
        if d.bodengruppe:
            gruppen[d.bodengruppe.strip("[]")] += 1
        if any(a.klasse in ("Steine", "Bloecke") for a in d.nebenanteile) or d.klasse in ("Steine", "Bloecke"):
            steine += 1
    n = len(einheit.get("schichten") or [])
    g = gruppen.most_common(1)[0][0] if gruppen else None
    return {"verhalten": _verhalten(list(einheit.get("bodenarten") or [])), "bodengruppe": g,
            "bodengruppe_anteil": f"{gruppen[g]}/{n}" if g else None, "steinig": n > 0 and steine * 2 >= n,
            "hauptbodenart": (einheit.get("bodenarten") or ["?"])[0]}


def vorschlag_fuer(code: str, einheiten: list[dict]) -> dict:
    """Vorschlag fuer eine ATV: Einheiten, die sich fuer dieses Gewerk gleich verhalten, in einem Bereich.

    einheiten: wie bericht()["einheiten"] (Reihenfolge von oben). Ergebnis: Zuordnung, Bereiche mit Begruendung, Stufe.
    Ein Vorschlag, nie still angewendet: uebernommen wird er erst mit einem Klick.
    """
    st, regel = stufe(code)
    schluessel: dict[str, tuple] = {}
    begruendung: dict[tuple, str] = {}
    for e in einheiten:
        m = merkmale(e)
        v = m["verhalten"]
        if v == "unbekannt":
            k, grund = ("einzeln", e["name"]), "nicht eindeutig klassifiziert: eigener Bereich"
        elif st == "grob" or v in ("anthropogen", "organisch", "fels"):
            k, grund = (v,), VERHALTEN_TEXT[v]
        else:
            art = m["bodengruppe"] or m["hauptbodenart"]
            k = (v, art) + ((m["steinig"],) if st == "fein" else ())
            grund = f"{VERHALTEN_TEXT[v]}, " + (f"Bodengruppe {m['bodengruppe']} ({m['bodengruppe_anteil']} Schichten)"
                                                if m["bodengruppe"] else f"Hauptbodenart {m['hauptbodenart']}")
            if st == "fein":
                grund += ", mit Steinen/Blöcken" if m["steinig"] else ", ohne Steine/Blöcke"
        schluessel[e["name"]] = k
        begruendung.setdefault(k, grund)
    namen: dict[tuple, str] = {}
    for e in einheiten:                                    # Namen in der Reihenfolge der obersten Einheit
        k = schluessel[e["name"]]
        if k not in namen:
            namen[k] = daten()["namensvorlage"].format(n=len(namen) + 1)
    zuordnung = {e["name"]: namen[schluessel[e["name"]]] for e in einheiten}
    bereiche_ = [{"name": namen[k], "einheiten": [e["name"] for e in einheiten if schluessel[e["name"]] == k],
                  "grund": begruendung[k]} for k in namen]
    return {"atv": code, "stufe": st, "regel": regel, "zuordnung": zuordnung, "bereiche": bereiche_}


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
