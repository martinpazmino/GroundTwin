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


# ---------------------------------------------------------------- Vorschlag je Anwendungsfall (docs/28 §5)
# Verhalten im Bau aus der Bodenart der Einheit (normen.json, Feld "art"); nur Einheiten gleichen Verhaltens koennen
# einen Bereich bilden. Unbekanntes bleibt immer einzeln.
_NICHTBINDIG = {"Kies", "Sand", "Steine", "Bloecke"}
_BINDIG_BODEN = {"Schluff", "Ton"}
_BEFESTIGT = {"Beton", "Asphalt", "Schwarzdecke", "Pflaster"}        # gebundene Schichten, kein Boden
# Geologische Benennungen, die sich im Bau anders verhalten als ihre Hauptbodenart (Entscheidung des Nutzers zu #21,
# 2026-11-22): Hangschutt ist gemischtkoernig mit Steinen/Bloecken, Wiesenkalk/Seekreide kalkig-organogen und
# setzungsempfindlich. Beide bekommen im Vorschlag immer einen eigenen Bereich, nie "bindig".
_EIGENER_BEREICH = {"Hangschutt": "hangschutt", "Wiesenkalk": "wiesenkalk"}
MIN_ANTEIL_GRUPPE = 0.5        # Bodengruppe trennt nur, wenn mindestens die Haelfte der Schichten sie nennt
VERHALTEN_TEXT = {"anthropogen": "anthropogen (Auffüllung)", "befestigt": "befestigt (Beton, Asphalt, Pflaster)",
                  "organisch": "organisch", "fels": "Fels",
                  "hangschutt": "Hangschutt (gemischtkörnig, mit Steinen)",
                  "wiesenkalk": "Wiesenkalk/Seekreide (kalkig-organogen)",
                  "nichtbindig": "nichtbindig", "bindig": "bindig", "unbekannt": "nicht klassifiziert"}


def _verhalten(bodenarten: list[str]) -> str:
    from .normen import KLASSEN
    arten = set()
    for b in bodenarten:
        art = "fels" if b.startswith("Fels") else KLASSEN.get(b, {}).get("art", "unbekannt")   # auch "Fels (Tonstein)"
        if b in _BEFESTIGT:
            arten.add("befestigt")
        elif b in _EIGENER_BEREICH:
            arten.add(_EIGENER_BEREICH[b])
        elif art == "boden":
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
        return "grob", f"{len(nr)} Kennwerte: nur das Verhalten (nichtbindig, bindig, organisch, anthropogen, befestigt, Fels)"
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
    if g and gruppen[g] < MIN_ANTEIL_GRUPPE * n:            # einzelne Nennung: traegt die Einheit nicht
        g = None
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
        elif st == "grob" or v in ("anthropogen", "befestigt", "organisch", "fels", *_EIGENER_BEREICH.values()):
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


# ---------------------------------------------------------------- Bereiche des Gutachters (Issue #21)
def gutachten_bereiche(docs: list[dict], code: str) -> list[dict]:
    """Homogenbereiche, die der Gutachter im Bericht festlegt (Extraktion homogenbereiche_text), fuer eine ATV;
    Bereiche ohne genannte ATV gelten fuer jede (mit Hinweis)."""
    out = []
    for d in docs:
        for e in d.get("homogenbereiche_gutachten") or []:
            if not e.get("atv") or code in e["atv"]:
                out.append({**e, "dokument": d["document"]["file"]})
    return out


def vorschlag_aus_gutachten(code: str, einheiten: list[dict], bereiche_gutachten: list[dict]) -> dict:
    """Vorschlag, der von den Bereichen des Gutachters ausgeht: je Einheit der Bereich, dessen Name sie nennt
    (Name vor Bodenart vor Bodengruppe vor Hauptgruppe); gleich gute Bereiche = keine Zuordnung. Ergebnis wie
    vorschlag_fuer, dazu die Einheiten ohne Bereich (mit Grund) und die Bereiche ohne Einheit: dort weichen Modell
    und Gutachten voneinander ab."""
    from . import bodenkennwerte as bk
    zuordnung, grund, ohne = {}, {}, []
    for e in einheiten:
        m = merkmale(e)
        e2 = {**e, "bodengruppe": m["bodengruppe"]}
        bewertet = []
        for g in bereiche_gutachten:
            zeile = {"bezeichnung": f"{g.get('name', '')} {g.get('ortsueblich', '')}",
                     "bodengruppen": g.get("bodengruppen", []) + (g.get("bodengruppen_auffuellung", [])
                                                                   if m["verhalten"] == "anthropogen" else [])}
            p, warum = bk._treffer(e2, zeile)
            if not p and (w := bk.hauptgruppe_trifft(e2, g.get("bodengruppen", []))):
                p, warum = 0.5, w
            if p:
                bewertet.append((p, warum, g))
        if not bewertet:
            ohne.append({"einheit": e["name"], "grund": "kein Bereich des Gutachtens nennt sie"})
            continue
        best = max(p for p, _, _ in bewertet)
        oben = [(w, g) for p, w, g in bewertet if p == best]
        if len(oben) > 1:
            ohne.append({"einheit": e["name"], "grund": "passt gleich gut zu " + ", ".join(g["bereich"] for _, g in oben)})
            continue
        zuordnung[e["name"]] = oben[0][1]["bereich"]
        grund[e["name"]] = oben[0][0]
    bereiche_ = []
    for g in bereiche_gutachten:
        drin = [e["name"] for e in einheiten if zuordnung.get(e["name"]) == g["bereich"]]
        bereiche_.append({"name": g["bereich"], "titel": g.get("name") or "", "einheiten": drin,
                          "grund": "; ".join(f"{x}: {grund[x]}" for x in drin) or "keine Einheit des Modells",
                          "bodengruppen": g.get("bodengruppen", []), "seite": g.get("seite"),
                          "dokument": g.get("dokument")})
    return {"atv": code, "quelle": "Gutachten", "zuordnung": zuordnung, "bereiche": bereiche_,
            "einheiten_ohne_bereich": ohne, "bereiche_ohne_einheit": [b["name"] for b in bereiche_ if not b["einheiten"]]}


# ---------------------------------------------------------------- Kennwerte aus den Beschreibungen (docs/28 §6)
# Was die Schichtbeschreibungen des Extrakts hergeben: nur Ansprache (Worte), keine Laborwerte. Je Kennwert die
# Angaben mit ihrer Haeufigkeit; alles andere bleibt offen und wird so genannt.
_PLASTIZITAET = {"L": "leicht plastisch", "M": "mittelplastisch", "A": "ausgeprägt plastisch"}
NUR_LABOR = "nicht im Extrakt (Laborwert bzw. Tabelle im Gutachtentext)"


def _haeufig(werte: list[str], n: int) -> str:
    from collections import Counter
    return ", ".join(f"{w} ({k}/{n})" for w, k in Counter(werte).most_common(4))


# Kennwert der ATV-Matrix -> Laborwerte (services/extractor/labor.py, an den Schichten)
_LABOR = {"9": ("wassergehalt",), "10b": ("plastizitaetszahl",), "11b": ("konsistenzzahl",), "12": ("kf",),
          "14": ("kalkgehalt",), "16": ("gluehverlust",), "5": ("trockendichte",)}


def _labor_kennwerte(out: dict[str, str], schichten: list[dict]) -> None:
    """Gemessene Werte vor der Ansprache: Spanne, n und Mittel aus den Laborblaettern."""
    from . import labor
    st = labor.statistik(schichten)
    if not st:
        return
    for nr, keys in _LABOR.items():
        t = [labor.text(st, k) for k in keys if k in st]
        if t:
            zusatz = {"5": "Trockendichte, ", "16": "Glühverlust, "}.get(nr, "")
            out[nr] = f"Labor: {zusatz}{'; '.join(t)}"
    if all(k in st for k in ("ton", "schluff", "sand")):
        f = lambda k: f"{st[k]['mittel']:.0f}" if k in st else "–"                      # noqa: E731
        out["2"] = (f"Labor: T/U/S/G im Mittel {f('ton')}/{f('schluff')}/{f('sand')}/{f('kies')} % "
                    f"(n = {st['sand']['n']})")


def kennwerte_aus_beschreibung(schichten: list[dict]) -> dict[str, str]:
    """Kennwert-Nr -> Angabe aus den Beschreibungen ("steif (5/8), weich (1/8)"); nur was genannt ist."""
    from .normen import deuten
    n = len(schichten)
    ds = [deuten(s.get("beschreibung"), s.get("bodenart")) for s in schichten]
    out: dict[str, str] = {}

    def setze(nr: str, werte: list[str], zusatz: str = "") -> None:
        if werte and nr not in out:                    # Laborwerte gehen der Ansprache vor
            out[nr] = _haeufig(werte, n) + zusatz

    _labor_kennwerte(out, schichten)
    setze("1", [d.benennung for d in ds if d.benennung])
    setze("3a", ["Steine genannt" for d in ds if any(a.klasse == "Steine" for a in d.nebenanteile) or d.klasse == "Steine"],
          " – nur Ansprache, kein Massenanteil")
    setze("3b", ["Blöcke genannt" for d in ds if any(a.klasse == "Bloecke" for a in d.nebenanteile) or d.klasse == "Bloecke"],
          " – nur Ansprache, kein Massenanteil")
    gruppen = [d.bodengruppe.strip("[]") for d in ds if d.bodengruppe]
    setze("10a", [_PLASTIZITAET[g[1]] for g in gruppen if g[0] in "TU" and len(g) > 1 and g[1] in _PLASTIZITAET],
          " – aus der Bodengruppe")
    setze("11a", [d.konsistenz for d in ds if d.konsistenz])
    setze("13", [d.lagerung for d in ds if d.lagerung], " – Ansprache")
    setze("14", [d.kalk for d in ds if d.kalk], " – Ansprache")
    setze("16", ["organische Anteile genannt" for d in ds
                 if any(a.klasse in ("Torf", "Mudde") or "humos" in a.text or "organ" in a.text for a in d.nebenanteile)],
          " – nur Ansprache, kein Glühverlust")
    setze("17", [d.benennung for d in ds if d.benennung and d.klasse in ("Torf", "Mudde", "Mutterboden")])
    setze("19", [d.bodengruppe for d in ds if d.bodengruppe])
    return out


def kennwerte_bereich(code: str, schichten: list[dict]) -> dict:
    """Fuer eine ATV: je verlangtem Kennwert die Angabe aus den Beschreibungen oder offen."""
    aus = kennwerte_aus_beschreibung(schichten)
    zeilen = [{"nr": k["nr"], "name": k["name"], "art": k["art"], "wert": aus.get(k["nr"])} for k in kennwerte(code)]
    return {"schichten": len(schichten), "kennwerte": zeilen,
            "belegt": sum(z["wert"] is not None for z in zeilen), "verlangt": len(zeilen)}


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
