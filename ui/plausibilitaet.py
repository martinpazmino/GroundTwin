"""Plausibilitaetsbericht je Bohrung: prueft die wirksamen (korrigierten) Werte eines Projekts auf Widersprueche und
markiert sie als Warnung oder Hinweis. Korrigiert nie automatisch (AGENTS.md: zweifelhafte Werte markieren, nie
still uebernehmen). Die GOK-Pruefung gegen das DGM liegt in geodaten.gelaende.gok_pruefen (Schritt Lage).
"""
from __future__ import annotations

import math
import statistics

from ui import projekt as pj

# Schwellen der Plausibilitaetspruefung (in Metern bzw. Anzahl):
# Rundung im Bohrprofil liegt bei 1 cm (0,01 m); erst oberhalb von 0,01 m ist eine Luecke oder Ueberlappung echt.
SCHWELLE_LUECKE_M = 0.01
# Bis 5 cm (0,05 m) unter GOK kann ein Belag oder Oberbodenabtrag ohne eigene Schicht vorliegen.
SCHWELLE_BEGINN_M = 0.05
# Zwischen angegebener Endteufe und tiefster Schichtunterkante sind bis 10 cm (0,1 m) Rundungs-/Sumpftoleranz ueblich.
SCHWELLE_ENDTEUFE_M = 0.1
# Schichten unter 5 cm (0,05 m) sind im Baugrundmodell kaum darstellbar und oft ein Zahlendreher in den Tiefen.
SCHWELLE_DUENN_M = 0.05
# Im Umkreis von 200 m (typische Baufeldgroesse) sind mehr als 3 m Abweichung vom Nachbar-Median (ab 2 Nachbarn)
# ein Hinweis auf einen Tippfehler, falschen Hoehenbezug oder starkes Relief (gegen das DGM im Schritt Lage pruefen).
UMKREIS_NACHBARN_M = 200.0
SCHWELLE_GOK_NACHBARN_M = 3.0
MIN_NACHBARN = 2

_EPS = 1e-6


def _befund(regel: str, stufe: str, text: str, schicht: int | None = None) -> dict:
    return {"regel": regel, "stufe": stufe, "text": text, "schicht": schicht}


def pruefe_reihenfolge(schichten: list[tuple[int, float, float]]) -> list[dict]:
    """Schichten nach Oberkante sortiert; Unterkante <= Oberkante einer Schicht -> Warnung."""
    out: list[dict] = []
    vorher_oben: float | None = None
    for k, oben, unten in schichten:
        if round(unten - oben, 6) <= 0.0:
            out.append(_befund(
                "reihenfolge", "warnung",
                f"Schicht {k + 1}: Unterkante ({pj.de(unten)} m) liegt nicht unter der Oberkante ({pj.de(oben)} m).",
                k,
            ))
        elif vorher_oben is not None and round(oben - vorher_oben, 6) < 0.0:
            out.append(_befund(
                "reihenfolge", "warnung",
                f"Schicht {k + 1}: Oberkante ({pj.de(oben)} m) liegt über der vorherigen Schicht "
                f"({pj.de(vorher_oben)} m).",
                k,
            ))
        vorher_oben = oben
    return out


def pruefe_luecke_ueberlappung(sortiert: list[tuple[int, float, float]]) -> list[dict]:
    """Zwischen Unterkante einer Schicht und Oberkante der naechsten mehr als 0,01 m -> Warnung."""
    out: list[dict] = []
    for (_, _, unten_vor), (k, oben, _) in zip(sortiert, sortiert[1:]):
        diff = round(oben - unten_vor, 6)
        if diff > SCHWELLE_LUECKE_M + _EPS:
            out.append(_befund(
                "luecke", "warnung",
                f"Lücke von {pj.de(diff)} m zwischen {pj.de(unten_vor)} m und {pj.de(oben)} m (Schicht {k + 1}).",
                k,
            ))
        elif -diff > SCHWELLE_LUECKE_M + _EPS:
            betrag = abs(diff)
            out.append(_befund(
                "ueberlappung", "warnung",
                f"Überlappung von {pj.de(betrag)} m zwischen {pj.de(oben)} m und {pj.de(unten_vor)} m "
                f"(Schicht {k + 1}).",
                k,
            ))
    return out


def pruefe_beginn(sortiert: list[tuple[int, float, float]]) -> list[dict]:
    """Die erste Schicht beginnt mehr als 0,05 m unter 0 -> Hinweis."""
    if not sortiert:
        return []
    k, oben, _ = sortiert[0]
    if round(oben, 6) > SCHWELLE_BEGINN_M + _EPS:
        return [_befund(
            "beginn", "hinweis",
            f"Erste Schicht (Schicht {k + 1}) beginnt erst bei {pj.de(oben)} m "
            f"(mehr als {pj.de(SCHWELLE_BEGINN_M)} m unter 0 m).",
            k,
        )]
    return []


def pruefe_endteufe(end_depth: float | None, tiefste_unten: float | None) -> list[dict]:
    """Angegebene Endteufe weicht mehr als 0,1 m von der tiefsten korrigierten Unterkante ab -> Warnung."""
    if end_depth is None or tiefste_unten is None:
        return []
    abw = round(abs(end_depth - tiefste_unten), 6)
    if abw > SCHWELLE_ENDTEUFE_M + _EPS:
        return [_befund(
            "endteufe", "warnung",
            f"Angegebene Endteufe ({pj.de(end_depth)} m) weicht um {pj.de(abw)} m von der tiefsten "
            f"Schichtunterkante ({pj.de(tiefste_unten)} m) ab.",
            None,
        )]
    return []


def pruefe_duenn(schichten: list[tuple[int, float, float]]) -> list[dict]:
    """Schicht duenner als 0,05 m -> Hinweis."""
    out: list[dict] = []
    for k, oben, unten in schichten:
        dicke = round(unten - oben, 6)
        if 0.0 < dicke < SCHWELLE_DUENN_M - _EPS:
            out.append(_befund(
                "duenn", "hinweis",
                f"Schicht {k + 1} ({pj.de(oben)}–{pj.de(unten)} m) ist nur {pj.de(dicke)} m mächtig "
                f"(< {pj.de(SCHWELLE_DUENN_M)} m).",
                k,
            ))
    return out


def pruefe_grundwasser(gw_tiefen: list[float], endteufe: float | None) -> list[dict]:
    """Grundwasser tiefer als die Endteufe oder ueber GOK (Tiefe < 0) -> Warnung."""
    out: list[dict] = []
    for tiefe in gw_tiefen:
        if round(tiefe, 6) < -_EPS:
            out.append(_befund(
                "grundwasser", "warnung",
                f"Grundwasser bei {pj.de(tiefe)} m liegt über GOK (< 0,00 m).",
                None,
            ))
        elif endteufe is not None and round(tiefe - endteufe, 6) > _EPS:
            out.append(_befund(
                "grundwasser", "warnung",
                f"Grundwasser bei {pj.de(tiefe)} m liegt tiefer als die Endteufe ({pj.de(endteufe)} m).",
                None,
            ))
    return out


def pruefe_gok_fehlt(gok: float | None) -> list[dict]:
    """Keine GOK -> Hinweis (Verweis auf die Tabelle und das DGM im Schritt Lage; die Quelle steht in gok_quelle)."""
    if gok is not None:
        return []
    return [_befund(
        "gok_fehlt", "hinweis",
        "Keine GOK (weder aus dem PDF noch eingetragen) – in der Tabelle eintragen oder im Schritt Lage aus dem DGM "
        "übernehmen.",
        None,
    )]


def pruefe_gok_nachbarn(eintrag: dict, alle: list[dict]) -> list[dict]:
    """GOK weicht mehr als 3 m vom Median der Bohrungen im Umkreis von 200 m ab (gleiche EPSG, >= 2 Nachbarn)."""
    gok, x, y, epsg = eintrag["gok"], eintrag["x"], eintrag["y"], eintrag["epsg"]
    if gok is None or x is None or y is None or epsg is None:
        return []
    nachbarn = [
        andere for andere in alle
        if andere["id"] != eintrag["id"]
        and andere["gok"] is not None
        and andere["x"] is not None
        and andere["y"] is not None
        and andere["epsg"] == epsg
        and math.hypot(andere["x"] - x, andere["y"] - y) <= UMKREIS_NACHBARN_M + _EPS
    ]
    if len(nachbarn) < MIN_NACHBARN:
        return []
    med = float(statistics.median(n["gok"] for n in nachbarn))
    abw = round(abs(gok - med), 6)
    if abw <= SCHWELLE_GOK_NACHBARN_M + _EPS:
        return []
    namen = ", ".join(n["code"] for n in nachbarn)
    return [_befund(
        "gok_nachbarn", "hinweis",
        f"GOK ({pj.de(gok)} m NHN) weicht um {pj.de(abw)} m vom Median ({pj.de(med)} m NHN) der Nachbarn im Umkreis "
        f"von {UMKREIS_NACHBARN_M:.0f} m ab ({namen}; im Schritt Lage gegen das DGM prüfen).",
        None,
    )]


def pruefen(docs: list[dict], p: pj.Projekt) -> list[dict]:
    """Plausibilitaetsbericht fuer alle Bohrungen im Modell (liest nur ueber ui/projekt.py, aendert nichts)."""
    doppelt = pj.doppelte(docs)
    modell_bohrungen: list[dict] = []
    for bid, _, b in pj.bohrungen(docs):
        if not pj.wert(p, bid, b, "modell", doppelt):
            continue
        schichten_roh: list[tuple[int, float, float]] = []
        for k, ly in enumerate(b.get("layers") or []):
            oben = pj.zahl(pj.schicht_wert(p, bid, k, ly, "oben"))
            unten = pj.zahl(pj.schicht_wert(p, bid, k, ly, "unten"))
            if oben is not None and unten is not None:
                schichten_roh.append((k, oben, unten))
        epsg_z = pj.zahl(pj.wert(p, bid, b, "epsg"))
        gw_tiefen: list[float] = []
        for g in b.get("groundwater") or []:
            t = pj.zahl(g.get("depth") if isinstance(g, dict) else g)
            if t is not None:
                gw_tiefen.append(t)
        modell_bohrungen.append({
            "id": bid,
            "code": b["code"],
            "schichten": schichten_roh,
            "end_depth": pj.zahl(b.get("end_depth")),
            "gw_tiefen": gw_tiefen,
            "gok": pj.zahl(pj.wert(p, bid, b, "gok")),
            "gok_quelle": pj.gok_quelle(p, bid, b),
            "x": pj.zahl(pj.wert(p, bid, b, "x")),
            "y": pj.zahl(pj.wert(p, bid, b, "y")),
            "epsg": int(epsg_z) if epsg_z else None,
        })

    out: list[dict] = []
    for e in modell_bohrungen:
        schichten = e["schichten"]
        gueltige = [s for s in schichten if round(s[2] - s[1], 6) > 0.0]
        sortiert = sorted(gueltige, key=lambda s: (s[1], s[2], s[0]))
        tiefste_unten = max((s[2] for s in schichten), default=None)
        # Grundwasser gegen die tiefere von angegebener Endteufe und tiefster Unterkante: fehlt unten eine Schicht,
        # meldet das schon die Regel endteufe; Wasser in diesem Bereich ist kein zweiter Widerspruch
        tiefen = [v for v in (tiefste_unten, e["end_depth"]) if v is not None]
        endteufe_wirksam = max(tiefen) if tiefen else None

        befunde: list[dict] = []
        befunde.extend(pruefe_reihenfolge(schichten))
        befunde.extend(pruefe_luecke_ueberlappung(sortiert))
        befunde.extend(pruefe_beginn(sortiert))
        befunde.extend(pruefe_endteufe(e["end_depth"], tiefste_unten))
        befunde.extend(pruefe_duenn(schichten))
        befunde.extend(pruefe_grundwasser(e["gw_tiefen"], endteufe_wirksam))
        befunde.extend(pruefe_gok_fehlt(e["gok"]))
        befunde.extend(pruefe_gok_nachbarn(e, modell_bohrungen))

        out.append({
            "id": e["id"],
            "code": e["code"],
            "gok_quelle": e["gok_quelle"],
            "befunde": befunde,
        })
    return out
