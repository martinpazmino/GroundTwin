"""Bodenkennwerte aus dem Gutachten je Einheit (Issue #18).

Die Extraktion (services/extractor/kennwerte.py) liest die Kennwert-Tabellen des Gutachtens als Zeilen mit
Bezeichnung, Bodengruppen und Werten (min/max). Hier werden sie den Einheiten des Modells zugeordnet:

- Vorschlag (nur ein Vorschlag, uebernommen mit einem Klick): je Einheit die Zeile, deren Bezeichnung den Namen oder
  die Hauptbodenart der Einheit nennt, oder deren Bodengruppen die haeufigste Bodengruppe der Einheit enthalten;
  mehrere gleich gute Zeilen = kein Vorschlag (markiert, nie geraten).
- IFC: ``CPset_Bodenkennwerte_Gutachten`` an der Einheit, Spannen als ``<Kennwert>_min`` / ``_max`` (Namensregel von
  DAUB Teil 3 §4.5, docs/30 §6.1), mit Seite, Bezeichnung und Zuordnung. ``_char`` setzt GroundTwin nie: der
  charakteristische Wert ist Sache des Gutachters (docs/29).
"""
from __future__ import annotations

import re
import unicodedata

PSET = "CPset_Bodenkennwerte_Gutachten"
IFC_NAME = {"wichte": "Wichte", "wichte_auftrieb": "Wichte_Auftrieb", "reibungswinkel": "Reibungswinkel",
            "kohaesion": "Kohaesion", "kohaesion_undrainiert": "Kohaesion_undrainiert", "steifemodul": "Steifemodul"}
EINHEIT = {"wichte": "kN/m3", "wichte_auftrieb": "kN/m3", "reibungswinkel": "Grad", "kohaesion": "kN/m2",
           "kohaesion_undrainiert": "kN/m2", "steifemodul": "MN/m2"}
# Wortstaemme der Bodenarten, wie sie in Tabellen stehen ('Kiese', 'Sande', 'Auffuellungen')
_STAMM = {"Auffuellung": ("auffull",), "Kies": ("kies",), "Sand": ("sand",), "Schluff": ("schluff",), "Ton": ("ton",),
          "Torf": ("torf",), "Mudde": ("mudde",), "Mutterboden": ("mutterbod", "oberbod", "humus"),
          "Oberboden": ("oberbod", "mutterbod", "humus"), "Lehm": ("lehm",), "Geschiebemergel": ("geschiebemerg",),
          "Mergel": ("mergel",), "Steine": ("stein",), "Bloecke": ("block",), "Schwarzdecke": ("asphalt", "schwarzdeck"),
          "Beton": ("beton",)}


def _klein(t: str) -> str:
    t = (t or "").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "Oe")
    t = t.replace("Ü", "Ue").replace("ß", "ss")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return t.lower().replace("ue", "u").replace("ae", "a").replace("oe", "o")


def eintraege(docs: list[dict]) -> list[dict]:
    """Alle Kennwert-Zeilen der Dokumente mit Verweis 'Datei#Index'."""
    out = []
    for d in docs:
        datei = d["document"]["file"]
        for i, e in enumerate(d.get("kennwerte") or []):
            out.append({**e, "ref": f"{datei}#{i}", "dokument": datei})
    return out


def _treffer(einheit: dict, e: dict) -> tuple[int, str]:
    """Punkte und Grund: 3 = voller Name der Einheit, 2 = Name/Bodenart als Hauptwort in der Bezeichnung,
    1 = Bodengruppe der Einheit in der Zeile."""
    bez = _klein(e.get("bezeichnung", ""))
    voll = _klein(einheit["name"])
    if len(voll) >= 3 and re.search(rf"(?<!\w){re.escape(voll)}(?!\w)", bez):
        return 3, f"Name „{einheit['name']}“ in der Bezeichnung"
    namen = [einheit["name"]] + list(einheit.get("bodenarten") or [])
    for n in namen:
        n = re.sub(r"^.*\((.+)\).*$", r"\1", n)       # 'Fels (Tonstein)' -> 'Tonstein'
        for stamm in _STAMM.get(n) or (_klein(n)[:max(4, len(_klein(n)) - 1)],):
            # das Hauptwort zaehlt, nicht das Beiwort: 'Sand, kiesig' nennt Sand, nicht Kies
            woerter = re.findall(rf"\b{re.escape(_klein(stamm))}\w*", bez)
            if len(stamm) >= 3 and any(not re.search(r"(?:ig|ige|igen|iger|haltig)$", w) for w in woerter):
                return 2, f"„{n}“ in der Bezeichnung"
    g = einheit.get("bodengruppe")
    if g and g in (e.get("bodengruppen") or []):
        return 1, f"Bodengruppe {g} in der Zeile"
    return 0, ""


# Hauptgruppe der Bodengruppen nach DIN 18196 (erster Buchstabe) je Bodenart der App
HAUPTGRUPPE = {"Sand": "S", "Kies": "G", "Schluff": "U", "Ton": "T", "Torf": "H", "Mudde": "O", "Mutterboden": "O",
               "Auffuellung": "A"}


def hauptgruppe_trifft(einheit: dict, gruppen: list[str]) -> str | None:
    """Schwaechster Hinweis: eine Bodengruppe der Zeile hat die Hauptgruppe der Bodenart ('Sand' -> S*)."""
    for n in [einheit["name"]] + list(einheit.get("bodenarten") or []):
        h = HAUPTGRUPPE.get(re.sub(r"\s*\d+$", "", n))
        if h and any(g.startswith(h) for g in gruppen):
            return f"Bodengruppe {h}… zur Bodenart {n}"
    return None


MIN_ANTEIL_HOEHE = 0.5          # so viel der Maechtigkeit einer Einheit muss im Hoehenbereich einer Zeile liegen
KNAPP_HOEHE = 0.2               # liegen zwei Bereiche naeher beieinander, gibt es keinen Vorschlag (markiert)


def einheit_hoehen(bohrungen: list[dict]) -> dict[str, list[tuple[float, float]]]:
    """Je Einheit die Abschnitte (oben, unten) in m NHN an den Bohrungen (Bericht 'bohrungen'), bis zur Endteufe;
    Bohrungen mit relativer Hoehe zaehlen nicht."""
    out: dict[str, list[tuple[float, float]]] = {}
    for b in bohrungen or []:
        if b.get("hoehe") == "relativ":
            continue
        ende = b.get("endteufe_nhn")
        for z in b.get("einheiten") or []:
            ok, uk = z["ok_modell"], max(z["uk_modell"], ende) if ende is not None else z["uk_modell"]
            if ok - uk > 0.01:
                out.setdefault(z["einheit"], []).append((ok, uk))
    return out


def _hoehen_treffer(abschnitte: list[tuple[float, float]], e: dict) -> tuple[float, str]:
    """Anteil der Maechtigkeit der Einheit im Hoehenbereich der Zeile (oben None = GOK)."""
    if "hoehe_unten" not in e or not abschnitte:
        return 0.0, ""
    oben = e.get("hoehe_oben")
    oben = float("inf") if oben is None else oben
    gesamt = sum(ok - uk for ok, uk in abschnitte)
    drin = sum(max(0.0, min(ok, oben) - max(uk, e["hoehe_unten"])) for ok, uk in abschnitte)
    anteil = drin / gesamt if gesamt > 0 else 0.0
    oben_t = "GOK" if e.get("hoehe_oben") is None else f"{e['hoehe_oben']:+.1f}"
    return anteil, f"{anteil:.0%} der Mächtigkeit in {oben_t} bis {e['hoehe_unten']:+.1f} m NHN".replace(".", ",")


def vorschlag(einheiten: list[dict], zeilen: list[dict], bohrungen: list[dict] | None = None) -> dict:
    """Je Einheit (Bericht: name, bodenarten, schichten) die passende Zeile oder ein Hinweis, warum keine.
    bohrungen (Bericht): fuer Zeilen mit Hoehenbereich zaehlt, wie viel der Einheit darin liegt (2 Punkte ab der
    Haelfte, wie ein Name)."""
    from .homogenbereiche import merkmale
    hoehen = einheit_hoehen(bohrungen or [])
    out = {}
    for e in einheiten:
        e2 = {**e, "bodengruppe": merkmale(e).get("bodengruppe")}
        bewertet = []
        anteile = sorted((_hoehen_treffer(hoehen.get(e["name"], []), z)[0] for z in zeilen), reverse=True)
        if len(anteile) > 1 and anteile[0] >= MIN_ANTEIL_HOEHE and anteile[0] - anteile[1] < KNAPP_HOEHE:
            out[e["name"]] = {"ref": None, "grund": f"liegt in zwei Höhenbereichen ({anteile[0]:.0%} / {anteile[1]:.0%}): "
                                                    "von Hand wählen"}
            continue
        for z in zeilen:
            p, g = _treffer(e2, z)
            anteil, warum = _hoehen_treffer(hoehen.get(e["name"], []), z)
            if anteil >= MIN_ANTEIL_HOEHE and 2 + anteil > p:
                p, g = 2 + anteil, warum           # der groesste Anteil gewinnt, ein voller Name (3) bleibt vorn
            if p > 0:
                bewertet.append((p, g, z))
        if not bewertet:
            out[e["name"]] = {"ref": None, "grund": "keine Zeile nennt die Einheit"}
            continue
        best = max(p for p, _, _ in bewertet)
        oben = [(g, z) for p, g, z in bewertet if p == best]
        if len(oben) > 1:
            out[e["name"]] = {"ref": None, "grund": f"{len(oben)} Zeilen passen gleich gut: von Hand wählen",
                              "kandidaten": [z["ref"] for _, z in oben]}
        else:
            out[e["name"]] = {"ref": oben[0][1]["ref"], "grund": oben[0][0]}
    return out


def pset(e: dict, zuordnung: str = "vom Bearbeiter bestätigt") -> dict:
    """Pset-Werte einer Zeile: <Kennwert>_min/_max (Einheit im Namen der Doku), Text, wo keine Zahl lesbar war."""
    out = {"Quelle": f"{e.get('dokument', 'Gutachten')}, Seite {int(e.get('seite', 0)) + 1}",
           "Bezeichnung_im_Gutachten": e.get("bezeichnung") or None, "Zuordnung": zuordnung,
           "Art": "Angabe des Gutachters (Tabelle), nicht von GroundTwin festgelegt"}
    for k, w in (e.get("werte") or {}).items():
        n = IFC_NAME.get(k)
        if not n:
            continue
        if "min" in w:
            out[f"{n}_min"] = float(w["min"])
            out[f"{n}_max"] = float(w["max"])
        elif w.get("text") and w["text"] not in ("-", "–"):
            out[f"{n}_Text"] = w["text"]
    if e.get("hinweise"):
        out["Hinweise"] = "; ".join(e["hinweise"])
    return out


def pruefen(zuordnung: dict | None, refs: set[str]) -> dict | None:
    """Zuordnung Einheit -> Verweis; unbekannte Verweise fallen weg. Keine Zuordnung (kein dict) -> ValueError (400)."""
    if zuordnung is not None and not isinstance(zuordnung, dict):
        raise ValueError("Bodenkennwerte: Zuordnung als {Einheit: Verweis}")
    z = {str(k): str(v) for k, v in (zuordnung or {}).items() if v and str(v) in refs}
    return z or None
