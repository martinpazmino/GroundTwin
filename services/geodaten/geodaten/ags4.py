"""AGS4 – das Austauschformat der Association of Geotechnical and Geoenvironmental Specialists (docs/30 §5, #30).

Weg zu PLAXIS und Leapfrog ohne Bentley-Bibliotheken: AGS4 → OpenGround / Leapfrog Works → PLAXIS. Exportiert werden
die Fakten (factual), wie bei BoreholeML nur Geprueftes:

- Bohrungen mit vollstaendig geprueftem Schichtenverzeichnis: LOCA (Lage, GOK, Endtiefe), GEOL (Beschreibung des
  Gutachtens im Klartext, Kurzzeichen nach DIN 4023 in GEOL_REM), Grundwasser: angetroffene Staende und Schichtenwasser
  als Wasseranschnitt (WSTG), Ruhewasser, nach Bohrende und Staende ohne Art als Tiefenbemerkung (DREM) – ein
  Ruhewasserspiegel ist kein Anschnitt, die Art steht im Text, nie geraten.
- Gepruefte Sondierungen mit Werten: Rammsondierungen als DPRG/DPRB (N10 je 10 cm, '>' als Bemerkung), Drucksondierungen
  als SCPG/SCPT nur mit bekannter Einheit (MPa, MN/m²): eine Kurve ohne gelesene Einheit wird nicht umgerechnet, sondern
  ausgelassen und im Bericht genannt.

Lage in LOCA_NATE/LOCA_NATN mit dem System als eigener Abkuerzung in LOCA_GREF (`EPSG:25832`, im ABBR erklaert), Hoehe
in LOCA_GL (m NHN, LOCA_DATM). Ohne Koordinaten bleibt die Lage leer (vermerkt). Die Datei ist ASCII (AGS4-Regel 1):
Umlaute werden umschrieben (ä → ae), das steht in TRAN_REM. Pruefung gegen den offiziellen Checker (python-ags4 des
AGS Data Format Working Group) in tests/test_ags4.py.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date

AGS_VERSION = "4.1.1"
GRUPPEN = {     # Reihenfolge der Ueberschriften wie im Standard-Woerterbuch 4.1.1 (Regel 7), nur die benutzten
    "PROJ": ["PROJ_ID", "PROJ_NAME", "PROJ_LOC", "PROJ_CLNT", "PROJ_CONT", "PROJ_ENG", "PROJ_MEMO"],
    "TRAN": ["TRAN_ISNO", "TRAN_DATE", "TRAN_PROD", "TRAN_STAT", "TRAN_DESC", "TRAN_AGS", "TRAN_RECV", "TRAN_DLIM",
             "TRAN_RCON", "TRAN_REM"],
    "LOCA": ["LOCA_ID", "LOCA_TYPE", "LOCA_STAT", "LOCA_NATE", "LOCA_NATN", "LOCA_GREF", "LOCA_GL", "LOCA_REM",
             "LOCA_FDEP", "LOCA_PURP", "LOCA_DATM"],
    "GEOL": ["LOCA_ID", "GEOL_TOP", "GEOL_BASE", "GEOL_DESC", "GEOL_REM"],
    "WSTG": ["LOCA_ID", "WSTG_DPTH", "WSTG_DTIM", "WSTG_REM"],
    "DREM": ["LOCA_ID", "DREM_TOP", "DREM_BASE", "DREM_REM"],
    "DPRG": ["LOCA_ID", "DPRG_TESN", "DPRG_TYPE", "DPRG_MASS", "DPRG_DROP", "DPRG_REM"],
    "DPRB": ["LOCA_ID", "DPRG_TESN", "DPRB_DPTH", "DPRB_BLOW", "DPRB_INC", "DPRB_REM"],
    "SCPG": ["LOCA_ID", "SCPG_TESN", "SCPG_TYPE", "SCPG_REM"],
    "SCPT": ["LOCA_ID", "SCPG_TESN", "SCPT_DPTH", "SCPT_RES", "SCPT_FRES", "SCPT_REM", "SCPT_FRR"],
}
TYPEN = {       # Datentyp je Ueberschrift (Standard-Woerterbuch); was fehlt, ist Text (X)
    "PROJ_ID": "ID", "LOCA_ID": "ID", "TRAN_DATE": "DT", "LOCA_TYPE": "PA", "LOCA_STAT": "PA", "LOCA_GREF": "PA",
    "LOCA_NATE": "2DP", "LOCA_NATN": "2DP", "LOCA_GL": "2DP", "LOCA_FDEP": "2DP", "GEOL_TOP": "2DP", "GEOL_BASE": "2DP",
    "WSTG_DPTH": "2DP", "WSTG_DTIM": "DT", "DREM_TOP": "2DP", "DREM_BASE": "2DP", "DPRG_TYPE": "PA", "DPRG_MASS": "1DP",
    "DPRG_DROP": "0DP", "DPRB_DPTH": "2DP", "DPRB_BLOW": "0DP", "DPRB_INC": "0DP", "SCPG_TYPE": "PA",
    "SCPT_DPTH": "2DP", "SCPT_RES": "3DP", "SCPT_FRES": "4DP", "SCPT_FRR": "2DP",
}
EINHEITEN = {   # Einheit je Ueberschrift; Datum im Format des Feldes (AGS4: die Einheit eines DT ist sein Format)
    "TRAN_DATE": "yyyy-mm-dd", "LOCA_NATE": "m", "LOCA_NATN": "m", "LOCA_GL": "m", "LOCA_FDEP": "m",
    "GEOL_TOP": "m", "GEOL_BASE": "m", "WSTG_DPTH": "m", "WSTG_DTIM": "yyyy-mm-dd", "DREM_TOP": "m", "DREM_BASE": "m",
    "DPRG_MASS": "kg", "DPRG_DROP": "mm", "DPRB_DPTH": "m", "DPRB_INC": "mm", "SCPT_DPTH": "m", "SCPT_RES": "MPa",
    "SCPT_FRES": "MPa", "SCPT_FRR": "%",
}
EINHEIT_TEXT = {"m": "metre", "mm": "millimetre", "kg": "kilogram", "MPa": "megapascal", "%": "percentage",
                "yyyy-mm-dd": "year month day"}
TYP_TEXT = {"ID": "Unique Identifier", "X": "Text", "PA": "Text listed in ABBR Group", "DT": "Date time in international "
            "format", "0DP": "Value; required number of decimal places, 0", "1DP": "Value; required number of decimal "
            "places, 1", "2DP": "Value; required number of decimal places, 2", "3DP": "Value; required number of "
            "decimal places, 3", "4DP": "Value; required number of decimal places, 4"}
# Rammsonden nach DIN EN ISO 22476-2 = Abkuerzungen des Woerterbuchs (Masse und Fallhoehe dort genannt)
RAMMSONDE = {"DPL": ("DPL", 10.0, 500, "Light dynamic probe (10kg hammer mass/500mm drop)"),
             "DPM": ("DPM", 30.0, 500, "Medium dynamic probe (30kg hammer mass/500mm drop)"),
             "DPH": ("DPH", 50.0, 500, "Heavy dynamic probe (50kg hammer mass/500mm drop)"),
             "DPSH": ("DPSH-B", 63.5, 750, "Superheavy (63.5kg hammer mass/750mm drop)")}
MPA = {"mpa", "mn/m²", "mn/m2", "mn/m^2"}
WASSERANSCHNITT = {"angetroffen", "schichtenwasser"}
ART_TEXT = {"angetroffen": "Grundwasser angetroffen (Anschnitt)", "schichtenwasser": "Schichtenwasser",
            "ruhewasser": "Ruhewasserspiegel", "ruhe": "Ruhewasserspiegel", "bohrende": "Wasserstand nach Bohrende",
            "nach_bohrende": "Wasserstand nach Bohrende"}
SYSTEME = {25831: "ETRS89 / UTM zone 31N", 25832: "ETRS89 / UTM zone 32N", 25833: "ETRS89 / UTM zone 33N",
           4647: "ETRS89 / UTM zone 32N (zE-N, Zonenkennung im Rechtswert)",
           5650: "ETRS89 / UTM zone 33N (zE-N, Zonenkennung im Rechtswert)",
           31466: "DHDN / 3-degree Gauss-Kruger zone 2", 31467: "DHDN / 3-degree Gauss-Kruger zone 3",
           31468: "DHDN / 3-degree Gauss-Kruger zone 4", 31469: "DHDN / 3-degree Gauss-Kruger zone 5"}
UMSCHRIFT = {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss", "²": "2", "³": "3",
             "°": " Grad", "µ": "u", "–": "-", "—": "-", "„": '"', "“": '"', "”": '"', "‚": "'", "‘": "'", "’": "'",
             "…": "...", "×": "x", "±": "+/-", "≤": "<=", "≥": ">=", " ": " "}


def ascii_text(t) -> str:
    """AGS4-Regel 1: nur ASCII. Deutsche Zeichen umschreiben, sonstige Akzente abtrennen; Zeilenumbrueche als Leerzeichen."""
    s = "".join(UMSCHRIFT.get(c, c) for c in str(t if t is not None else ""))
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).strip()


def _zahl(v, stellen: int) -> str:
    return "" if v is None else f"{float(v):.{stellen}f}"


def _datum(t) -> str:
    m = re.fullmatch(r"\s*(\d{4}-\d{2}-\d{2})(?:[T ].*)?", str(t or ""))
    return m.group(1) if m else ""


def _art(g: dict) -> str:
    return str(g.get("kind") or "").strip().lower()


def _wert(spalte: str, v) -> str:
    typ = TYPEN.get(spalte, "X")
    if typ.endswith("DP") and v not in (None, ""):
        return _zahl(v, int(typ[0]))
    return ascii_text(v)


def bohrung_exportierbar(b: dict) -> str:
    """Grund, warum eine Bohrung nicht nach AGS4 geht ('' = exportierbar)."""
    if b.get("herkunft") in ("SGD", "BoreholeML"):
        return "aus dem Bestand des Landes bzw. einer BoreholeML-Datei, nicht aus dem Gutachten"
    if not b.get("layers"):
        return "keine Schichten"
    if not all(ly.get("geprueft") for ly in b["layers"]):
        return "nicht vollständig geprüft"
    return ""


def sondierung_exportierbar(s: dict) -> str:
    """Grund, warum eine Sondierung nicht nach AGS4 geht ('' = exportierbar)."""
    if not s.get("geprueft"):
        return "Sondierung nicht geprüft"
    if not s.get("kurven") or not any(k[1] for k in s["kurven"]):
        return "Sondierung ohne gelesene Werte"
    art = str(s.get("art") or "").upper()
    if art.startswith("CP") and not _cpt_kurven(s)[0]:
        return "Drucksondierung ohne gelesene Einheit von q_c (MPa / MN/m²): nicht umgerechnet"
    if not art.startswith(("DP", "SRS", "CP")):
        return f"Sondierungsart {s.get('art')} ohne AGS4-Gruppe"
    return ""


def _cpt_kurven(s: dict) -> tuple[dict, list[str]]:
    """Kurven einer CPT mit bekannter Einheit in MPa (q_c, f_s) bzw. % (R_f); ausgelassene mit Grund."""
    gut, raus = {}, []
    for name, tiefen, werte, einheit, *_ in s.get("kurven") or []:
        e = str(einheit or "").strip().lower().replace(" ", "")
        if name in ("q_c", "f_s") and e in MPA:
            gut[name] = dict(zip(tiefen, werte))
        elif name in ("q_c", "f_s") and e in ("kpa", "kn/m²", "kn/m2"):
            gut[name] = {t: w / 1000.0 for t, w in zip(tiefen, werte)}
        elif name == "R_f" and e == "%":
            gut[name] = dict(zip(tiefen, werte))
        else:
            raus.append(f"{name} (Einheit nicht gelesen: {einheit})")
    if "q_c" not in gut:
        return {}, raus
    return gut, raus


def exportieren(dokumente: list[dict], *, projekt: str, organisation: str = "", sig: str = "groundtwin",
                heute: date | None = None, sondierungen: list[dict] | None = None,
                sondierungen_draussen: list[dict] | None = None, version: str = "") -> tuple[bytes, dict]:
    """dokumente: wirksame Dokumente (wie fuer BoreholeML); sondierungen: ui.sondierung.fuer_ifc (mit Lage und GOK).

    Rueckgabe: AGS4-Datei (ASCII, CRLF) und Bericht {exportiert, sondierungen, ausgelassen [{code, grund}], hinweise}."""
    from baugrundmodell.normen import deuten   # Kurzzeichen nach DIN 4023 wie in der App (services/modeler)

    heute = heute or date.today()
    zeilen: dict[str, list[dict]] = {g: [] for g in GRUPPEN}
    abkuerzungen: dict[tuple[str, str], str] = {("LOCA_STAT", "FINAL"): "Final data"}
    bericht: dict = {"exportiert": [], "sondierungen": [], "ausgelassen": [], "hinweise": []}
    ids: set[str] = set()

    def loca_id(code: str) -> str:
        basis = ascii_text(code) or "LOC"
        k, n = basis, 2
        while k in ids:
            k, n = f"{basis}_{n}", n + 1
        ids.add(k)
        return k

    def lage(eintrag: dict, x, y, epsg, gok, gok_relativ: bool) -> list[str]:
        fehlt = []
        if x is not None and y is not None and epsg:
            gref = f"EPSG:{int(epsg)}"
            eintrag.update(LOCA_NATE=x, LOCA_NATN=y, LOCA_GREF=gref)
            abkuerzungen[("LOCA_GREF", gref)] = SYSTEME.get(int(epsg), f"EPSG {int(epsg)}")
        else:
            fehlt.append("ohne Koordinaten (Lage leer)")
        if gok is not None and not gok_relativ:
            eintrag.update(LOCA_GL=gok, LOCA_DATM="m NHN (DHHN)")
        else:
            fehlt.append("ohne GOK in m NHN (LOCA_GL leer)")
        return fehlt

    for d in dokumente:
        datei = (d.get("document") or {}).get("file") or "Gutachten"
        for b in d.get("boreholes") or []:
            grund = bohrung_exportierbar(b)
            if grund:
                bericht["ausgelassen"].append({"code": b.get("code", "?"), "grund": grund})
                continue
            lid = loca_id(b["code"])
            ende = b.get("end_depth") or max(float(ly["bottom_depth"]) for ly in b["layers"])
            e = {"LOCA_ID": lid, "LOCA_TYPE": "EH", "LOCA_STAT": "FINAL", "LOCA_FDEP": ende,
                 "LOCA_PURP": "Baugrunderkundung"}
            abkuerzungen[("LOCA_TYPE", "EH")] = "Exploratory Hole"
            fehlt = lage(e, b.get("x"), b.get("y"), b.get("crs_epsg"), b.get("gok_nhn"), b.get("gok_source") == "relativ")
            e["LOCA_REM"] = "; ".join([f"Bohrung {b['code']} aus dem Gutachten {datei}, mit GroundTwin gelesen und vom "
                                       "Bearbeiter geprueft; Bohrverfahren siehe Gutachten"] + fehlt)
            zeilen["LOCA"].append(e)
            for ly in b["layers"]:
                text = ly.get("description_raw") or ly.get("description") or ""
                dt = deuten(text, ly.get("soil_class"))
                zeilen["GEOL"].append({"LOCA_ID": lid, "GEOL_TOP": ly["top_depth"], "GEOL_BASE": ly["bottom_depth"],
                                       "GEOL_DESC": text or ly.get("soil_class") or "ohne Beschreibung",
                                       "GEOL_REM": f"DIN 4023: {dt.din4023}" if dt.din4023 else ""})
            for g in sorted(b.get("groundwater") or [], key=lambda g: float(g["depth"])):
                art, tag = _art(g), _datum(g.get("observed_on"))
                text = ART_TEXT.get(art, "Wasserstand, Art im Gutachten nicht angegeben")
                if art in WASSERANSCHNITT:
                    zeilen["WSTG"].append({"LOCA_ID": lid, "WSTG_DPTH": g["depth"], "WSTG_DTIM": tag,
                                           "WSTG_REM": text})
                else:
                    zeilen["DREM"].append({"LOCA_ID": lid, "DREM_TOP": g["depth"], "DREM_BASE": g["depth"],
                                           "DREM_REM": text + (f" am {tag}" if tag else "")})
            bericht["exportiert"].append(b["code"])

    for r in sondierungen_draussen or []:
        bericht["ausgelassen"].append({"code": r["code"], "grund": r["grund"]})
    for s in sondierungen or []:
        grund = sondierung_exportierbar(s)
        if grund:
            bericht["ausgelassen"].append({"code": s["code"], "grund": grund})
            continue
        art = str(s.get("art") or "").upper()
        lid = loca_id(s["code"])
        quelle = f"{s['code']} aus dem Gutachten {s.get('dokument') or ''} S. {s.get('seite') or '?'}, geprueft"
        e = {"LOCA_ID": lid, "LOCA_STAT": "FINAL", "LOCA_FDEP": s.get("endtiefe"), "LOCA_PURP": "Baugrunderkundung"}
        fehlt = lage(e, s.get("x"), s.get("y"), s.get("epsg"), s.get("gok"), False)
        if art.startswith("CP"):
            e["LOCA_TYPE"] = "SCP"
            abkuerzungen[("LOCA_TYPE", "SCP")] = "Static cone penetrometer"
            kurven, raus = _cpt_kurven(s)
            zeilen["SCPG"].append({"LOCA_ID": lid, "SCPG_TESN": "1", "SCPG_TYPE": "",
                                   "SCPG_REM": f"Drucksondierung ({s.get('art')}) nach DIN EN ISO 22476-1; " + quelle
                                   + (f"; nicht uebertragen: {', '.join(raus)}" if raus else "")})
            for t in sorted(kurven["q_c"]):
                zeilen["SCPT"].append({"LOCA_ID": lid, "SCPG_TESN": "1", "SCPT_DPTH": t, "SCPT_RES": kurven["q_c"][t],
                                       "SCPT_FRES": (kurven.get("f_s") or {}).get(t),
                                       "SCPT_FRR": (kurven.get("R_f") or {}).get(t)})
        else:
            e["LOCA_TYPE"] = "DP"
            abkuerzungen[("LOCA_TYPE", "DP")] = "Dynamic probe sampling"
            typ = next((v for k, v in RAMMSONDE.items() if art.startswith(k)), None)
            dprg = {"LOCA_ID": lid, "DPRG_TESN": "1",
                    "DPRG_REM": f"Rammsondierung ({s.get('art')}) nach DIN EN ISO 22476-2; " + quelle}
            if typ:
                dprg.update(DPRG_TYPE=typ[0], DPRG_MASS=typ[1], DPRG_DROP=typ[2])
                abkuerzungen[("DPRG_TYPE", typ[0])] = typ[3]
            else:
                dprg["DPRG_REM"] += "; Sondentyp im Gutachten nicht genannt"
            zeilen["DPRG"].append(dprg)
            n10 = next(k for k in s["kurven"] if k[0] == "N10")
            ueber = {round(float(u), 2) for _, u, _ in s.get("zensierte") or []}
            oben_von = {round(float(r[1]), 3): float(r[0]) for r in s.get("werte") or [] if len(r) >= 2}
            for unten, w in zip(n10[1], n10[2]):
                oben = oben_von.get(round(float(unten), 3), max(0.0, float(unten) - 0.1))
                bem = ["mindestens (Wert ueber der Achse)"] if round(float(unten), 2) in ueber else []
                if abs(float(unten) - oben - 0.1) > 0.005:      # N10 gilt je 10 cm; eine laengere Stufe nicht umrechnen
                    bem.append(f"Stufe {oben:.2f}-{float(unten):.2f} m, N10 je 10 cm")
                zeilen["DPRB"].append({"LOCA_ID": lid, "DPRG_TESN": "1", "DPRB_DPTH": oben, "DPRB_BLOW": round(float(w)),
                                       "DPRB_INC": 100, "DPRB_REM": "; ".join(bem)})
        e["LOCA_REM"] = "; ".join([f"Sondierung {quelle}"] + fehlt)
        zeilen["LOCA"].append(e)
        bericht["sondierungen"].append(s["code"])

    if not bericht["exportiert"] and not bericht["sondierungen"]:
        gruende = "; ".join(f"{a['code']}: {a['grund']}" for a in bericht["ausgelassen"][:8])
        raise ValueError("keine exportierbare Bohrung: " + (gruende or "keine Bohrung im Projekt"))

    bericht["hinweise"] = [
        "AGS4-Datei in ASCII (Regel 1): Umlaute umschrieben (ae, oe, ue, ss).",
        "Lage als EPSG-Code in LOCA_GREF (eigene Abkuerzung, im ABBR erklaert), Hoehe LOCA_GL in m NHN.",
        "Ruhewasser, Wasserstand nach Bohrende und Staende ohne Art als Tiefenbemerkung (DREM), nicht als Anschnitt.",
        "Schichten: Beschreibung des Gutachtens im Klartext (GEOL_DESC), Kurzzeichen nach DIN 4023 in GEOL_REM; "
        "keine Legenden- oder Geologiecodes (GEOL_LEG/GEOL_GEOL).",
    ]
    zeilen["PROJ"].append({"PROJ_ID": ascii_text(sig) or "groundtwin", "PROJ_NAME": projekt or "Baugrundmodell",
                           "PROJ_MEMO": "Fakten aus dem Gutachten, mit GroundTwin gelesen und geprueft"})
    zeilen["TRAN"].append({"TRAN_ISNO": "1", "TRAN_DATE": heute.isoformat(),
                           "TRAN_PROD": f"GroundTwin {version}".strip(), "TRAN_STAT": "Fakten, geprueft",
                           "TRAN_DESC": "Bohrungen und Sondierungen aus dem Gutachten", "TRAN_AGS": AGS_VERSION,
                           "TRAN_RECV": organisation or "nicht angegeben", "TRAN_DLIM": "|", "TRAN_RCON": "+",
                           "TRAN_REM": " ".join(bericht["hinweise"])})
    return _datei(zeilen, abkuerzungen), bericht


def _gruppe(name: str, spalten: list[str], daten: list[dict]) -> list[list[str]]:
    return ([["GROUP", name], ["HEADING", *spalten], ["UNIT", *[EINHEITEN.get(s, "") for s in spalten]],
             ["TYPE", *[TYPEN.get(s, "X") for s in spalten]]]
            + [["DATA", *[_wert(s, z.get(s)) for s in spalten]] for z in daten])


def _datei(zeilen: dict[str, list[dict]], abkuerzungen: dict[tuple[str, str], str]) -> bytes:
    """Gruppen in der Reihenfolge der Abhaengigkeit, dazu ABBR, TYPE und UNIT mit allem, was benutzt ist."""
    bloecke = [_gruppe(g, GRUPPEN[g], zeilen[g]) for g in GRUPPEN if zeilen[g]]
    benutzt = {s for g in GRUPPEN if zeilen[g] for s in GRUPPEN[g]}
    typen = sorted({TYPEN.get(s, "X") for s in benutzt} | {"X", "PA"})
    einheiten = sorted({EINHEITEN[s] for s in benutzt if s in EINHEITEN})
    bloecke.append(_gruppe("ABBR", ["ABBR_HDNG", "ABBR_CODE", "ABBR_DESC"],
                           [{"ABBR_HDNG": h, "ABBR_CODE": c, "ABBR_DESC": t} for (h, c), t in sorted(abkuerzungen.items())]))
    bloecke.append(_gruppe("TYPE", ["TYPE_TYPE", "TYPE_DESC"],
                           [{"TYPE_TYPE": t, "TYPE_DESC": TYP_TEXT[t]} for t in typen]))
    bloecke.append(_gruppe("UNIT", ["UNIT_UNIT", "UNIT_DESC"],
                           [{"UNIT_UNIT": u, "UNIT_DESC": EINHEIT_TEXT[u]} for u in einheiten]))
    text = "\r\n\r\n".join("\r\n".join(",".join('"' + f.replace('"', '""') + '"' for f in z) for z in b) for b in bloecke)
    return (text + "\r\n").encode("ascii")
