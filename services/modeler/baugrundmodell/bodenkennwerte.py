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
_STAMM = {"Auffuellung": "auffull", "Kies": "kies", "Sand": "sand", "Schluff": "schluff", "Ton": "ton",
          "Torf": "torf", "Mudde": "mudde", "Mutterboden": "mutterbod", "Oberboden": "oberbod", "Lehm": "lehm",
          "Geschiebemergel": "geschiebemerg", "Mergel": "mergel", "Steine": "stein", "Bloecke": "block"}


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
        stamm = _STAMM.get(n) or _klein(n)[:max(4, len(_klein(n)) - 1)]
        # das Hauptwort zaehlt, nicht das Beiwort: 'Sand, kiesig' nennt Sand, nicht Kies
        woerter = re.findall(rf"\b{re.escape(_klein(stamm))}\w*", bez)
        if len(stamm) >= 3 and any(not re.search(r"(?:ig|ige|igen|iger|haltig)$", w) for w in woerter):
            return 2, f"„{n}“ in der Bezeichnung"
    g = einheit.get("bodengruppe")
    if g and g in (e.get("bodengruppen") or []):
        return 1, f"Bodengruppe {g} in der Zeile"
    return 0, ""


def vorschlag(einheiten: list[dict], zeilen: list[dict]) -> dict:
    """Je Einheit (Bericht: name, bodenarten, schichten) die passende Zeile oder ein Hinweis, warum keine."""
    from .homogenbereiche import merkmale
    out = {}
    for e in einheiten:
        e2 = {**e, "bodengruppe": merkmale(e).get("bodengruppe")}
        bewertet = [(p, g, z) for z in zeilen for p, g in [_treffer(e2, z)] if p > 0]
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
    """Zuordnung Einheit -> Verweis; unbekannte Verweise fallen weg."""
    z = {str(k): str(v) for k, v in (zuordnung or {}).items() if v and str(v) in refs}
    return z or None
