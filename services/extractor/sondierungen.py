"""Extraktionsstufe fuer Sondierungen (DPH/DPL/DPM/DPSH/SRS und CPT/CPTu) als eigenstaendige Stufe.

Verarbeitet Tabellen, Vektordiagramme (Treppenkurven, gefuellte Balken, Mehrkurven-CPT mit
linearer/invertierter/logarithmischer Achse), Laengsschnitte mit NHN-Hoehenmassstab,
mehrseitige Fortsetzungen, zensierte Randwerte sowie gescannte Diagramme und Tabellen
nach allgemeinen Zeichnungs-, Text- und Geometriemerkmalen (ohne PDF- oder Bueroausnahmen).
"""
from __future__ import annotations

import math
import re
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prototyp_v4 import (  # noqa: E402
    Seg,
    _merge,
    _xform_drawing,
    adaptive_dpi,
    find_columns,
    ocr_words,
    page_class,
    raster_segments,
    rows,
)
import textebene  # noqa: E402

# Alle allgemeinen Regeln sind einzeln fuer Ablationen abschaltbar.
REGELN: dict[str, bool] = {
    "tabelle_kopf_schlagzahl": True,
    "tabelle_luecken_melden": True,
    "achse_arithmetisch_und_rahmen": True,
    "tiefe_nicht_bohrungscode": True,
    "cpt_log_achse": True,
    "cpt_kurven_trennen": True,
    "zensierte_randwerte": True,
    "mehrseitig_verbinden": True,
    "laengsschnitt_hoehenmassstab": True,
    "scan_konservativ": True,
    "endpruefung_monoton_und_achse": True,
    "einzelstriche_verketten": True,
    "achse_zeile_ausgerichtet": True,     # #54: Wertachse = ausgerichtete Zeile (U09: '0.0' der Tiefenachse)
    "tickstriche_am_rahmen": True,        # #55: linke Tickstriche nur am Rahmen (nicht Schraffur des Nachbarprofils)
    "kurze_rahmen": True,                 # #55: Mindesthoehe des Diagrammrahmens 36 statt 52 pt (x Seitenfaktor)
    "nn_vor_wert": True,                  # #55: Ansatzhoehe 'NN+8,83m'
    "rs_rammsondierung": True,            # #55: 'RS 1' = Rammsondierung, Art aus der Seite ('DPL-5')
    "stationscode": True,                 # #54: DPH-0+550-G (Code mit Station und Zusatz) ungekuerzt
}

DPH_ARTEN = {"DPH", "DPL", "DPM", "DPSH", "SRS"}
CPT_ARTEN = {"CPT", "CPTu"}

# Kuerzel- und Kontextmuster (nach textebene.falten anwendbar)
SOND_KOPF_RE = re.compile(
    r"^(?:Sondierung(?:\s*Nr\.?)?\s*:?\s*|"
    r"(?:Schwere|Leichte|Mittelschwere)\s+Rammsondierung\s+|"
    r"Drucksondierung\s+)?"
    r"(DPSH|CPTu|CPT|DPH|DPL|DPM|SRS|RS)\s*[-]?\s*(\d+[a-z]?(?:/\d{2})?(?:\+\d{3}(?:-[A-Z][A-Za-z0-9,]{0,6})?)?)"
    r"(?:\s*\((Fortsetzung|Forts\.?|Fts\.?)\)|\s*[-–:]\s*.*)?$",
    re.I,
)
SOND_SUCH_RE = re.compile(
    r"\b(DPSH|CPTu|CPT|DPH|DPL|DPM|SRS|RS)\s*[-]?\s*(\d+[a-z]?(?:/\d{2})?(?:\+\d{3}(?:-[A-Z][A-Za-z0-9,]{0,6})?)?)"
    r"(?:\s*\((Fortsetzung|Forts\.?|Fts\.?)\))?(?![\w+])",
    re.I,
)
def _code(art: str, nr: str) -> str:
    """'DPH 1'; mit Station wie gedruckt 'DPH-0+550-G' (#54). Ohne Regel: Station abschneiden (altes Verhalten)."""
    if "+" in nr:
        return f"{art}-{nr}" if REGELN["stationscode"] else f"{art} {nr.split('+')[0]}"
    return f"{art} {nr}"


ARCHIV_SOND_RE = re.compile(r"^(DS\s*\d+[a-z]?/\d{2}|D\s*\d+[a-z]?/\d{2}|R\s*\d+[a-z]?)$")
BOHR_CODE_RE = re.compile(r"^(?:B|BK|KB|KRB|RKS|BS|GWM|SCH|RB|SST)\s*\d+[a-z]?(?:/\d{2}|/[IVX]+)?$")

SOND_KONTEXT_RE = re.compile(
    r"rammsond|drucksond|\b(?:dph|dpl|dpm|dpsh|cpt|cptu|srs)\b|"
    r"schlagzahl|schlae?ge|n\s*10|spitzenwiderstand|mantelreibung|reibungsverhae?ltnis|q_?c|f_?s|r_?f",
    re.I,
)
CPT_KONTEXT_RE = re.compile(
    r"drucksond|\bcptu?\b|spitzenwiderstand|mantelreibung|reibungsverhae?ltnis|\bq_?c\b|\bf_?s\b|\br_?f\b",
    re.I,
)
NEGATIV_KONTEXT_RE = re.compile(
    r"\b(?:c\s*b\s*r|stempelweg|stempeldruck|rqd|koe?rnungslinie|sieblinie|"
    r"proctor|kompressionsversuch|scherversuch|durchlae?ssigkeit|"
    r"sondierbohrung|bohrfortschritt|rammbarkeit|"
    r"rammprotokoll|fertigrammpfahl|bohrpfahl|rammpfahl|pfahlrammung|"
    r"ea-pfae?hle|pfahl\s*\d+)\b|"
    r"schl(?:agzahl|ae?ge)\s*/\s*(?:25|50|100)\s*cm|"
    r"din\s*(?:en\s*iso\s*)?17892",
    re.I,
)
PROSA_VERBEN_RE = re.compile(
    r"\b(?:wurden|wurde|durchgefue?hrt|empfohlen|abgeteuft|nachgewiesen|ausgefue?hrt|ergeben|zeigen)\b",
    re.I,
)
LABOR_SPALTE_RE = re.compile(
    r"wassergehalt|flie(?:ss|ß)grenze|ausrollgrenze|plastizitae?tszahl|qb,?k|qs,?k|"
    r"bodengruppe|frost|verdichtbar|analysen|mg/kg|\bcbr\b|stempeldruck|bohrfortschritt|\brqd\b",
    re.I,
)

ANSATZ_RE = re.compile(
    r"(?:Ansatz(?:punkt|h[oö]e?he)|GOK)\s*:?\s*([+-]?\s*\d{1,4}[.,]\d{1,3})\b|"
    r"([+-]\s*\d{2,4}[.,]\d{2,3})\s*m(?:\s*(?:ue?\.?)?\s*(?:NHN|NN))?\b|"
    r"(?:^|\s)(\d{2,4}[.,]\d{2,3})\s*m(?:\s*ue?\.?)?\s*(?:NHN|NN)\b|"
    r"\bNN\s*([+-]\s*\d{1,4}[.,]\d{1,3})\s*m\b",     # 'NN+8,83m' (Wert nach NN, #55)
    re.I,
)
ENDTIEFE_RE = re.compile(r"Endtiefe\s*:?\s*(\d{1,3}[.,]\d{1,2})\s*m\b", re.I)
ABBRUCH_AUF_CM_RE = re.compile(r"(\d{2,3})\s*Schl[äa]e?ge\s*auf\s*(\d{1,2})\s*cm", re.I)
ABBRUCH_100_RE = re.compile(r"(?:100\s*/\s*10\s*cm|Sonde\s*steht\s*auf|Rammabbruch)", re.I)
FORTSETZUNG_RE = re.compile(r"\s*\((?:Fortsetzung|Forts\.?|Fts\.?)\)\s*$", re.I)
ZAHL_RE = re.compile(r"^-?\d+(?:[.,]\d+)?$")
TIEFE_ZELLE_RE = re.compile(r"^\d{1,3}[.,]\d{1,2}$")
NHN_TICK_RE = re.compile(r"^[+-]?\d{1,4}[.,]\d{2}m?$")
ZENSIERT_MARGIN_RE = re.compile(r"^(?:N\s*10\s*)?[>≥]\s*(\d+(?:[.,]\d+)?)$", re.I)
LAENGS_CUE_RE = re.compile(r"lae?ngsschnitt|hoe?henschnitt|hoe?henmae?(?:ss|ß)ig|\d+\+\d{3}|station", re.I)
CUE_SCHNELL_RE = re.compile(
    r"dph|dpl|dpm|dpsh|cpt|srs|rammsond|drucksond|schlagzahl|n\s*10|"
    r"spitzenwiderstand|mantelreibung|reibungsverh|tiefe|teufe|sondier|lae?ngsschnitt|hoe?henschnitt|"
    r"\bds\s*\d|\bd\s*\d+/\d+|\br\s*\d",
    re.I,
)


def _norm_code(code: str | None) -> str:
    return re.sub(r"\s+", "", str(code or "")).upper()


def _f(text: str) -> float:
    return float(text.replace(" ", "").replace(",", ".").rstrip("m"))


def _rs_art(sd) -> str | None:
    """#55: 'RS 1' (Rammsondierung) nennt die Sonde nicht; die Seite sagt sie ('leichte Rammsonde (DPL-5)')."""
    arten = {m.group(1).upper() for _, t in sd.zeilen for m in re.finditer(r"\b(DPSH|DPH|DPM|DPL)(?=\b|-)", t)}
    return arten.pop() if len(arten) == 1 else None


def _art_norm(art: str) -> str:
    gross = art.upper()
    if gross == "CPTU":
        return "CPTu"
    return gross


def _falten_norm(text: str) -> str:
    return re.sub(r"\s+", " ", textebene.falten(text)).strip()


def _split_numerische_woerter(rect: pymupdf.Rect, token: str) -> list[tuple[pymupdf.Rect, float]]:
    """Zerlegt OCR-verklebte Achsenwerte wie '0,600,55' anteilig in Einzelwerte."""
    tok = token.strip()
    if ZAHL_RE.fullmatch(tok):
        try:
            return [(rect, _f(tok))]
        except ValueError:
            return []
    treffer = list(re.finditer(r"-?\d+[.,]\d{1,3}", tok))
    if len(treffer) < 2:
        return []
    gesamt = max(len(tok), 1)
    out: list[tuple[pymupdf.Rect, float]] = []
    for m in treffer:
        try:
            val = _f(m.group(0))
        except ValueError:
            continue
        a = m.start() / gesamt
        b = m.end() / gesamt
        r = pymupdf.Rect(
            rect.x0 + a * rect.width,
            rect.y0,
            rect.x0 + b * rect.width,
            rect.y1,
        )
        out.append((r, val))
    return out


def _ols_fit(xs: np.ndarray, ys: np.ndarray) -> tuple[float, float, float, float]:
    """Berechnet OLS y = a*x + b sowie R^2 und max. absolutes Residuum."""
    a, b = np.polyfit(xs, ys, 1)
    pred = a * xs + b
    res = np.abs(ys - pred)
    ss_res = float(np.sum((ys - pred) ** 2))
    ss_tot = float(np.sum((ys - np.mean(ys)) ** 2))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-12 else 0.0
    return float(a), float(b), r2, float(np.max(res))


def _arithmetische_folge_ok(vals: list[float], tol_rel: float = 0.06) -> bool:
    if len(vals) < 3:
        return False
    diffs = np.diff(vals)
    if np.all(diffs > 1e-6):
        ad = diffs
    elif np.all(diffs < -1e-6):
        ad = -diffs
    else:
        return False
    med = float(np.median(ad))
    if med <= 1e-9:
        return False
    return float(np.max(ad) - np.min(ad)) <= tol_rel * med + 1e-5


def _tiefenlineal_folge_ok(vals: list[float], tol_rel: float = 0.06) -> bool:
    """Prueft Tiefenlineal-Folgen inkl. optionalem Teil-Endtiefen-Tick (z. B. 1..9, 9,30) oder Einzel-Luecke."""
    if _arithmetische_folge_ok(vals, tol_rel=tol_rel):
        return True
    if len(vals) >= 4:
        # Letzter Tick darf kuerzere Endtiefe sein (z. B. marl_251 S.24: 1..9, 9,30; S.27: 1..6, 6,30)
        if _arithmetische_folge_ok(vals[:-1], tol_rel=tol_rel):
            med = float(np.median(np.diff(vals[:-1])))
            if 0.0 < vals[-1] - vals[-2] <= (1.0 + tol_rel) * med + 1e-4:
                return True
    if len(vals) >= 6:
        # Einzelne OCR-Luecke (z. B. fehlendes '8,0' in 1..20 -> Schritt 2*med) zulassen
        diffs = np.diff(vals)
        if np.all(diffs > 1e-6):
            med = float(np.median(diffs))
            if med > 1e-9 and all(
                round(d / med) in (1, 2) and abs(d / med - round(d / med)) <= 0.12
                for d in diffs
            ):
                if sum(round(d / med) == 1 for d in diffs) >= int(0.8 * len(diffs)):
                    return True
    return False


def _beste_arith_unterfolge(
    eintraege: list[tuple[pymupdf.Rect, float]],
    nur_steigend: bool = True,
) -> list[tuple[pymupdf.Rect, float]]:
    """Waehlt laengste saubere lineare Tick-Teilfolge (toleriert einzelne OCR-Ausreisser)."""
    if len(eintraege) < 2:
        return eintraege
    eintraege = sorted(eintraege, key=lambda e: (e[0].y0 + e[0].y1) / 2.0)
    # Deduplizierung identischer (y, wert)
    dedup: list[tuple[pymupdf.Rect, float]] = []
    for r, v in eintraege:
        yc = (r.y0 + r.y1) / 2.0
        if dedup and abs(((dedup[-1][0].y0 + dedup[-1][0].y1) / 2.0) - yc) < 3.0 and abs(dedup[-1][1] - v) < 1e-4:
            continue
        dedup.append((r, v))
    if len(dedup) < 3:
        return dedup

    # Versuche direkt und mit max. 2 Ausreissern (z. B. OCR '00' statt '0.0')
    kandidaten = [dedup]
    if len(dedup) >= 4:
        for i in range(len(dedup)):
            kandidaten.append(dedup[:i] + dedup[i + 1 :])
    beste: list[tuple[pymupdf.Rect, float]] = []
    for cand in kandidaten:
        ys = np.array([(r.y0 + r.y1) / 2.0 for r, _ in cand], dtype=float)
        vs = np.array([v for _, v in cand], dtype=float)
        if nur_steigend and not np.all(np.diff(vs) > 1e-6):
            continue
        if not nur_steigend and not (np.all(np.diff(vs) > 1e-6) or np.all(np.diff(vs) < -1e-6)):
            continue
        a, _b, r2, _ = _ols_fit(ys, vs)
        if r2 >= 0.995 and ((nur_steigend and a > 0) or (not nur_steigend and a != 0)):
            if len(cand) > len(beste):
                beste = cand
    if beste:
        return beste
    # Fallback: laengste streng monotone Teilfolge
    dp: list[list[tuple[pymupdf.Rect, float]]] = [[e] for e in dedup]
    for i in range(len(dedup)):
        for j in range(i):
            cond = dedup[j][1] < dedup[i][1] if nur_steigend else dedup[j][1] != dedup[i][1]
            if cond and len(dp[j]) + 1 > len(dp[i]):
                dp[i] = dp[j] + [dedup[i]]
    return max(dp, key=len) if dp else dedup


@dataclass
class _SeitenDaten:
    seite_nr: int
    breite: float
    hoehe: float
    scale_f: float
    pclass: str
    scanned: bool
    quelle: str
    words: list[tuple]
    text_lines: list[tuple[pymupdf.Rect, str]]
    zeilen: list[tuple[pymupdf.Rect, str]]
    drawings: list[dict]
    segs: list[Seg]
    raster_segs: list[Seg]
    bohr_spalten: list = field(default_factory=list)
    page: pymupdf.Page = None  # type: ignore[assignment]


def _seiten_primitive(page: pymupdf.Page, seite_nr: int, ocr: bool) -> _SeitenDaten:
    """Bereitet rotierte Seitenprimitive ohne globale Seiteneffekte auf prototyp_v4.RULES auf."""
    m = page.rotation_matrix
    scale_f = min(page.rect.width, page.rect.height) / 595.0
    raw_words = page.get_text("words")
    words = [(pymupdf.Rect(w[:4]) * m, w[4], w[5], w[6]) for w in raw_words]
    word_nos = [int(w[7]) if len(w) > 7 else i for i, w in enumerate(raw_words)]
    raw_drawings = page.get_drawings()
    pclass = page_class(page, words, raw_drawings)
    scanned = pclass in ("raster", "raster_ocr") or (len(raw_drawings) < 5 and bool(page.get_images()))

    quelle = "Text"
    if ocr and pclass in ("raster", "raster_ocr", "vektor_ohne_text"):
        native = [r for r, *_ in words]
        ocr_w = [
            w for w in ocr_words(page)
            if not any((w[0] & r).get_area() > 0.3 * max(w[0].get_area(), 1e-6) for r in native)
        ]
        if ocr_w:
            words.extend(ocr_w)
            word_nos.extend(range(len(ocr_w)))
            quelle = "OCR"

    lines_map: dict[tuple, list] = defaultdict(list)
    for (r, t, b, ln), wno in zip(words, word_nos):
        lines_map[(b, ln)].append((r, t, wno))
    text_lines: list[tuple[pymupdf.Rect, str]] = []
    for ws in lines_map.values():
        if len({w[2] for w in ws}) == len(ws):
            ws.sort(key=lambda w: w[2])
        else:
            cxs = [(w[0].x0 + w[0].x1) / 2 for w in ws]
            cys = [(w[0].y0 + w[0].y1) / 2 for w in ws]
            if max(cxs) - min(cxs) >= max(cys) - min(cys):
                ws.sort(key=lambda w: (w[0].x0, w[2]))
            else:
                ws.sort(key=lambda w: (w[0].y0, w[2]))
        rr = pymupdf.Rect(ws[0][0])
        for q, _, _ in ws[1:]:
            rr |= q
        text_lines.append((rr, " ".join(t for _, t, _ in ws)))
    zeilen = rows(text_lines, dy=3.0 * scale_f)

    seiten_text = _falten_norm(" ".join(t for _, t in zeilen))
    hat_cue = bool(CUE_SCHNELL_RE.search(seiten_text))

    # Dichte Nicht-Sondierungs-Rasterseiten (z. B. talheim.pdf S.9 mit 26035 Vektoren) schnell ueberspringen
    drawings: list[dict] = []
    if not scanned or (hat_cue and len(raw_drawings) < 5000):
        drawings = [_xform_drawing(d, m) for d in raw_drawings]

    segs: list[Seg] = []
    if not (scanned and len(drawings) < 5):
        for d in drawings:
            stroked = d.get("color") is not None and "s" in d.get("type", "")
            fill = d.get("fill")
            coloured_fill = fill is not None and min(fill) < 0.97
            if not stroked and not coloured_fill:
                continue
            w = d.get("width") or 0.0
            dashed = d.get("dashes") not in (None, "[] 0", "[] 0.0")
            for it in d["items"]:
                if it[0] == "l":
                    pts = [(it[1], it[2])]
                elif it[0] == "re":
                    r = it[1]
                    pts = [(r.tl, r.tr), (r.tr, r.br), (r.br, r.bl), (r.bl, r.tl)]
                elif it[0] == "qu":
                    q = it[1]
                    pts = [(q.ul, q.ur), (q.ur, q.lr), (q.lr, q.ll), (q.ll, q.ul)]
                else:
                    continue
                for a, b in pts:
                    segs.append(Seg(min(a.x, b.x), min(a.y, b.y), max(a.x, b.x), max(a.y, b.y), w, stroked, dashed))

    r_segs: list[Seg] = []
    if scanned and hat_cue:
        r_segs = raster_segments(page)
        segs.extend(r_segs)

    bohr_spalten_roh = find_columns(segs) if segs else []
    if REGELN["tiefe_nicht_bohrungscode"] and bohr_spalten_roh:
        phrasen = _lokale_phrasen(words, scale_f)
        bohr_spalten = [
            col for col in bohr_spalten_roh
            if any(
                BOHR_CODE_RE.match(_falten_norm(t))
                and abs(((r.x0 + r.x1) / 2.0) - ((col.rect.x0 + col.rect.x1) / 2.0)) <= 65.0 * scale_f
                and -15.0 * scale_f <= col.rect.y0 - r.y1 <= 320.0 * scale_f
                for r, t in phrasen
            )
        ]
    else:
        bohr_spalten = bohr_spalten_roh
    return _SeitenDaten(
        seite_nr=seite_nr,
        breite=page.rect.width,
        hoehe=page.rect.height,
        scale_f=scale_f,
        pclass=pclass,
        scanned=scanned,
        quelle=quelle,
        words=words,
        text_lines=text_lines,
        zeilen=zeilen,
        drawings=drawings,
        segs=segs,
        raster_segs=r_segs,
        bohr_spalten=bohr_spalten,
        page=page,
    )


@dataclass
class _Kopf:
    rect: pymupdf.Rect
    code: str
    art: str
    ist_fortsetzung: bool = False
    ansatzhoehe: float | None = None


def _suche_ansatzhoehe(
    zeilen: list[tuple[pymupdf.Rect, str]],
    x_ref: float,
    y_ref: float,
    scale_f: float,
    nachbarn_x: list[float] | None = None,
) -> float | None:
    """Sucht Ansatzhoehe (m NHN / NN) nahe dem Sondierungskopf ohne Nachbarprofil-Uebergriff."""
    kands: list[tuple[float, float]] = []
    x_left = (95.0 if nachbarn_x else 140.0) * scale_f
    x_right = 90.0 * scale_f
    for r, t in zeilen:
        if r.y0 < y_ref - 35 * scale_f or r.y0 > y_ref + 95 * scale_f:
            continue
        if r.x1 < x_ref - x_left or r.x0 > x_ref + x_right:
            continue
        rx = (r.x0 + r.x1) / 2.0
        if nachbarn_x:
            if any(
                min(x_ref, rx) + 15.0 * scale_f < nx < max(x_ref, rx) - 15.0 * scale_f
                for nx in nachbarn_x
            ):
                continue
            if abs(rx - x_ref) > 45.0 * scale_f and any(
                abs(rx - nx) < 0.35 * abs(rx - x_ref) for nx in nachbarn_x
            ):
                continue
        tf = _falten_norm(t)
        for m in ANSATZ_RE.finditer(tf):
            roh = m.group(1) or m.group(2) or m.group(3) or (m.group(4) if REGELN["nn_vor_wert"] else None)
            if not roh:
                continue
            try:
                val = _f(roh)
            except ValueError:
                continue
            if -50.0 <= val <= 3000.0:
                dist = abs(r.y0 - y_ref) + 0.3 * max(0.0, abs(rx - x_ref) - 40 * scale_f)
                kands.append((dist, val))
    if not kands:
        return None
    kands.sort(key=lambda e: e[0])
    return kands[0][1]


def _bohr_code_ziffer_rects(words: list[tuple], scale_f: float) -> list[pymupdf.Rect]:
    """Liefert Bounding-Rects von Ziffern-Tokens innerhalb erkannter Bohrungscodes (L14)."""
    sortiert = sorted(words, key=lambda w: (round(((w[0].y0 + w[0].y1) / 2.0) / (3.0 * scale_f)), w[0].x0))
    gruppen: list[list[tuple[pymupdf.Rect, str]]] = []
    for w in sortiert:
        r, t = pymupdf.Rect(w[0]), str(w[1])
        yc = (r.y0 + r.y1) / 2.0
        if gruppen:
            prev_r, _ = gruppen[-1][-1]
            prev_yc = (prev_r.y0 + prev_r.y1) / 2.0
            if abs(yc - prev_yc) <= 4.0 * scale_f and -4.0 * scale_f <= r.x0 - prev_r.x1 <= 24.0 * scale_f:
                gruppen[-1].append((r, t))
                continue
        gruppen.append([(r, t)])
    ziffer_rects: list[pymupdf.Rect] = []
    for grp in gruppen:
        if len(grp) < 2:
            continue
        phrase = _falten_norm(" ".join(t for _, t in grp))
        if BOHR_CODE_RE.match(phrase):
            for r, t in grp[1:]:
                if ZAHL_RE.fullmatch(t.strip()):
                    ziffer_rects.append(r)
            continue
        for (r_a, t_a), (r_b, t_b) in zip(grp, grp[1:]):
            if r_b.x0 - r_a.x1 <= 14.0 * scale_f:
                paar = _falten_norm(f"{t_a} {t_b}")
                if BOHR_CODE_RE.match(paar) and ZAHL_RE.fullmatch(t_b.strip()):
                    ziffer_rects.append(r_b)
    return ziffer_rects


def _lokale_phrasen(words: list[tuple], scale_f: float) -> list[tuple[pymupdf.Rect, str]]:
    """Gruppiert Woerter nur bei kleinem horizontalem Abstand (verhindert Zeilenverschmelzung ueber zwei Profile)."""
    sortiert = sorted(words, key=lambda w: (round(((w[0].y0 + w[0].y1) / 2.0) / (3.0 * scale_f)), w[0].x0))
    gruppen: list[list[tuple[pymupdf.Rect, str]]] = []
    for w in sortiert:
        r, t = pymupdf.Rect(w[0]), str(w[1])
        yc = (r.y0 + r.y1) / 2.0
        if gruppen:
            prev_r, _ = gruppen[-1][-1]
            prev_yc = (prev_r.y0 + prev_r.y1) / 2.0
            if abs(yc - prev_yc) <= 4.0 * scale_f and -4.0 * scale_f <= r.x0 - prev_r.x1 <= 24.0 * scale_f:
                gruppen[-1].append((r, t))
                continue
        gruppen.append([(r, t)])
    out: list[tuple[pymupdf.Rect, str]] = []
    for g in gruppen:
        rr = pymupdf.Rect(g[0][0])
        for r, _ in g[1:]:
            rr |= r
        out.append((rr, " ".join(t for _, t in g)))
    return out


def _finde_koepfe(sd: _SeitenDaten) -> list[_Kopf]:
    """Erkennt Sondierungskoepfe (DPH/DPL/DPM/DPSH/CPT/CPTu/SRS sowie kontextgesicherte Archivcodes)."""
    koepfe: list[_Kopf] = []
    sf = sd.scale_f
    phrasen = _lokale_phrasen(sd.words, sf)

    def _kontext_um(rect: pymupdf.Rect, radius: float) -> str:
        teile = []
        for r, t in phrasen:
            if (
                r.x1 >= rect.x0 - radius
                and r.x0 <= rect.x1 + radius
                and r.y1 >= rect.y0 - radius
                and r.y0 <= rect.y1 + radius
            ):
                teile.append(_falten_norm(t))
        return " ".join(teile)

    gesehen: set[tuple[str, int, int]] = set()
    for r, t in phrasen:
        tf = _falten_norm(t)
        if not tf or BOHR_CODE_RE.match(tf):
            continue
        # Prosa-Satz ausschliessen
        if len(tf.split()) > 9 or PROSA_VERBEN_RE.search(tf):
            continue
        if re.search(r"R\s*\d+\s*:", tf):
            continue

        m = SOND_KOPF_RE.match(tf)
        if m:
            art_raw, nr, fts = m.group(1), m.group(2), m.group(3)
            if art_raw.upper() == "RS" and not REGELN["rs_rammsondierung"]:
                continue
            art = (_rs_art(sd) or "DPH") if art_raw.upper() == "RS" else _art_norm(art_raw)
            code = f"RS {nr}" if art_raw.upper() == "RS" else _code(art, nr)
            if fts and not REGELN["mehrseitig_verbinden"]:
                code = f"{code} ({fts})"
            key = (_norm_code(code), round(r.x0 / (25 * sf)), round(r.y0 / (25 * sf)))
            if key not in gesehen:
                gesehen.add(key)
                koepfe.append(_Kopf(r, code, art, bool(fts)))
            continue

        # Teil-Treffer in laengeren Kopfzeilen (z. B. 'Anlage 4.1 Schwere Rammsondierung DPH 1')
        if len(tf.split()) <= 8 and not NEGATIV_KONTEXT_RE.search(tf):
            for sm in SOND_SUCH_RE.finditer(tf):
                if sm.group(1).upper() == "RS" and not REGELN["rs_rammsondierung"]:
                    continue
                art = (_rs_art(sd) or "DPH") if sm.group(1).upper() == "RS" else _art_norm(sm.group(1))
                code = f"RS {sm.group(2)}" if sm.group(1).upper() == "RS" else _code(art, sm.group(2))
                fts = sm.group(3)
                if fts and not REGELN["mehrseitig_verbinden"]:
                    code = f"{code} ({fts})"
                key = (_norm_code(code), round(r.x0 / (25 * sf)), round(r.y0 / (25 * sf)))
                if key not in gesehen:
                    gesehen.add(key)
                    koepfe.append(_Kopf(r, code, art, bool(fts)))

    # Archivcodes (R1, R2, D 7/16, DS 1/17) aus Einzelwoertern/Zeilen nur mit lokalem Sondierungskontext
    for r, t in phrasen:
        tf = _falten_norm(t)
        m = ARCHIV_SOND_RE.match(tf)
        if not m:
            continue
        cand = re.sub(r"\s+", " ", m.group(1)).strip()
        if cand.startswith("R"):
            if cand in ("R 0", "R0"):
                continue
            um = _kontext_um(r, 95 * sf)
            if NEGATIV_KONTEXT_RE.search(um) or not re.search(r"\b(?:dph|dpl|dpm|dpsh|rammsond)\b", um, re.I):
                continue
            art = "DPH"
            if re.search(r"\bdpl\b", um, re.I):
                art = "DPL"
            elif re.search(r"\bdpm\b", um, re.I):
                art = "DPM"
        else:
            um = _kontext_um(r, 200 * sf)
            if not CPT_KONTEXT_RE.search(um):
                continue
            art = "CPT"
        key = (_norm_code(cand), round(r.x0 / (25 * sf)), round(r.y0 / (25 * sf)))
        if key not in gesehen:
            gesehen.add(key)
            koepfe.append(_Kopf(r, cand, art, False))

    bohr_phrasen_x = [
        ((r.x0 + r.x1) / 2.0, r.y0)
        for r, t in phrasen
        if BOHR_CODE_RE.match(_falten_norm(t))
    ]
    for k in koepfe:
        x_ref = (k.rect.x0 + k.rect.x1) / 2.0
        y_ref = k.rect.y0
        nachbarn_x: list[float] = []
        for ok in koepfe:
            okx = (ok.rect.x0 + ok.rect.x1) / 2.0
            if abs(okx - x_ref) > 25.0 * sf and abs(ok.rect.y0 - y_ref) <= 180.0 * sf:
                nachbarn_x.append(okx)
        for bx, by in bohr_phrasen_x:
            if y_ref - 160.0 * sf <= by <= y_ref + 120.0 * sf and abs(bx - x_ref) > 25.0 * sf:
                nachbarn_x.append(bx)
        for col in sd.bohr_spalten:
            if col.rect.y1 >= y_ref - 35.0 * sf and col.rect.y0 <= y_ref + 260.0 * sf:
                cx = (col.rect.x0 + col.rect.x1) / 2.0
                if abs(cx - x_ref) > 25.0 * sf:
                    nachbarn_x.append(cx)
        k.ansatzhoehe = _suche_ansatzhoehe(phrasen, x_ref, y_ref, sf, nachbarn_x=nachbarn_x)
    return koepfe


def _naechster_kopf(koepfe: list[_Kopf], rect: pymupdf.Rect, scale_f: float,
                    erlaubte_arten: set[str] | None = None) -> _Kopf | None:
    """Ordnet einen Diagramm- oder Tabellenbereich dem plausibelsten Kopf zu."""
    cands: list[tuple[float, _Kopf]] = []
    cx = (rect.x0 + rect.x1) / 2.0
    for k in koepfe:
        if erlaubte_arten and k.art not in erlaubte_arten:
            continue
        # Bevorzugt ueber dem Rahmen oder auf derselben Seite falls nur ein Kopf existiert
        dy = rect.y0 - k.rect.y1
        kcx = (k.rect.x0 + k.rect.x1) / 2.0
        horiz_ov = (
            min(rect.x1 + 60 * scale_f, k.rect.x1 + 60 * scale_f)
            - max(rect.x0 - 60 * scale_f, k.rect.x0 - 60 * scale_f)
        )
        if -25 * scale_f <= dy <= 160 * scale_f and horiz_ov > 0:
            score = abs(dy) + 0.4 * abs(cx - kcx)
            cands.append((score, k))
    if cands:
        cands.sort(key=lambda e: e[0])
        return cands[0][1]
    # Seitenweiter Einzelkopf-Fallback
    passende = [k for k in koepfe if not erlaubte_arten or k.art in erlaubte_arten]
    einzigartig = {_norm_code(k.code): k for k in passende}
    if len(einzigartig) == 1:
        return next(iter(einzigartig.values()))
    if len(passende) > 1:
        best = min(
            passende,
            key=lambda k: abs((k.rect.x0 + k.rect.x1) / 2.0 - cx) + 0.5 * max(0.0, rect.y0 - k.rect.y1),
        )
        if abs((best.rect.x0 + best.rect.x1) / 2.0 - cx) < 180 * scale_f:
            return best
    return None


def _wort_zeilen(words: list[tuple], scale_f: float) -> list[list[tuple[pymupdf.Rect, str]]]:
    """Gruppiert Einzelwoerter zeilenweise (umgeht den PyMuPDF-Komma-Bug in Table.extract)."""
    sortiert = sorted(words, key=lambda w: ((w[0].y0 + w[0].y1) / 2.0, w[0].x0))
    out: list[list[tuple[pymupdf.Rect, str]]] = []
    for w in sortiert:
        r, t = pymupdf.Rect(w[0]), str(w[1])
        yc = (r.y0 + r.y1) / 2.0
        if out:
            ref_y = sum((e[0].y0 + e[0].y1) / 2.0 for e in out[-1]) / len(out[-1])
            if abs(yc - ref_y) <= 3.5 * scale_f:
                out[-1].append((r, t))
                continue
        out.append([(r, t)])
    for zeile in out:
        zeile.sort(key=lambda e: e[0].x0)
    return out


def _extrahiere_tabellen(sd: _SeitenDaten, koepfe: list[_Kopf]) -> list[dict]:
    """Extrahiert DPH/DPL/DPM-Wertetabellen (inkl. zweispaltiger Doppelpaare)."""
    sf = sd.scale_f
    gesamttext = _falten_norm(" ".join(t for _, t in sd.zeilen))
    if "tiefe" not in gesamttext.lower() and "teufe" not in gesamttext.lower():
        return []
    hat_schlag = bool(re.search(r"n\s*10|n\s*20|n\s*30|schlagzahl|schlae?ge", gesamttext, re.I))
    if REGELN["tabelle_kopf_schlagzahl"] and not hat_schlag:
        return []

    w_zeilen = _wort_zeilen(sd.words, sf)
    ergebnisse: list[dict] = []
    min_y_hdr = -1e9

    for idx, zeile in enumerate(w_zeilen):
        # Zwei moegliche Kopfzeilen innerhalb 18 pt zusammen betrachten (z. B. 'Tiefe' / '[m]')
        y_hdr = (zeile[0][0].y0 + zeile[0][0].y1) / 2.0
        if y_hdr <= min_y_hdr:
            continue
        kopf_woerter = list(zeile)
        if idx + 1 < len(w_zeilen):
            y_next = (w_zeilen[idx + 1][0][0].y0 + w_zeilen[idx + 1][0][0].y1) / 2.0
            if y_next - y_hdr <= 18.0 * sf:
                kopf_woerter.extend(w_zeilen[idx + 1])

        kopf_txt = _falten_norm(" ".join(t for _, t in kopf_woerter))
        if not re.search(r"\b(?:tiefe|teufe|sondiertiefe)\b", kopf_txt, re.I):
            continue

        if REGELN["tabelle_kopf_schlagzahl"]:
            if not re.search(r"\b(?:n\s*10|n_?10|n\s*20|n\s*30|schlagzahl|schl[äa]e?ge)\b", kopf_txt, re.I):
                continue
            if LABOR_SPALTE_RE.search(kopf_txt) or NEGATIV_KONTEXT_RE.search(kopf_txt):
                continue
            # Umgebungsueberschrift auf Labor- oder Pfahlnormen pruefen
            y_oben_lim = max(y_hdr - 120.0 * sf, min_y_hdr)
            nahe_oben = _falten_norm(
                " ".join(t for r, t in sd.zeilen if y_oben_lim <= r.y0 <= y_hdr + 5.0 * sf)
            )
            if (
                NEGATIV_KONTEXT_RE.search(nahe_oben)
                or LABOR_SPALTE_RE.search(nahe_oben)
                or re.search(r"(?:/|\bje)\s*(?:25|50|100)\s*cm", kopf_txt, re.I)
            ):
                continue

        # Tiefen-Spalten und zugehoerige Wertespalten bestimmen
        tiefe_koepfe = [
            (r, t) for r, t in zeile if re.match(r"^(?:tiefe|teufe|sondiertiefe)\b", _falten_norm(t), re.I)
        ]
        if not tiefe_koepfe:
            continue
        tiefe_koepfe.sort(key=lambda e: e[0].x0)

        wert_koepfe = [
            (r, t)
            for r, t in kopf_woerter
            if re.match(r"^(?:n\s*10|n_?10|n\s*20|n\s*30|schlagzahl|schlae?ge)", _falten_norm(t), re.I)
        ]
        if not REGELN["tabelle_kopf_schlagzahl"] and not wert_koepfe:
            # Ablation: irgendeine numerische Spalte rechts von Tiefe annehmen
            wert_koepfe = [(r, t) for r, t in zeile if r.x0 > tiefe_koepfe[0][0].x1 + 5 * sf]

        paare: list[tuple[tuple[float, float], tuple[float, float]]] = []
        if len(tiefe_koepfe) >= 2:
            abstand = min(tiefe_koepfe[i + 1][0].x0 - tiefe_koepfe[i][0].x0 for i in range(len(tiefe_koepfe) - 1))
            for i, (tr, _) in enumerate(tiefe_koepfe):
                tx0 = tr.x0 - 16 * sf
                tx1 = tr.x1 + 26 * sf
                if i + 1 < len(tiefe_koepfe):
                    tx1 = min(tx1, tiefe_koepfe[i + 1][0].x0 - 30 * sf)
                wx0 = tx1
                wx1 = tr.x0 + abstand - 14 * sf
                paare.append(((tx0, tx1), (wx0, wx1)))
        else:
            tr = tiefe_koepfe[0][0]
            tx0, tx1 = tr.x0 - 18 * sf, tr.x1 + 42 * sf
            rechts_wk = [wr for wr, _ in wert_koepfe if wr.x0 > tr.x0 + 10 * sf]
            if rechts_wk:
                wr = min(rechts_wk, key=lambda q: q.x0)
                tx1 = min(tx1, wr.x0 - 4 * sf)
                wx0 = wr.x0 - 14 * sf
                wx1 = wr.x1 + 48 * sf
            else:
                wx0 = tx1
                wx1 = tr.x1 + 115 * sf
            paare.append(((tx0, tx1), (wx0, wx1)))

        y_stop = float("inf")
        for j in range(idx + 1, len(w_zeilen)):
            z_k = w_zeilen[j]
            y_k = (z_k[0][0].y0 + z_k[0][0].y1) / 2.0
            if y_k <= y_hdr + 20.0 * sf:
                continue
            z_txt = _falten_norm(" ".join(t for _, t in z_k))
            if SOND_KOPF_RE.match(z_txt) and not TIEFE_ZELLE_RE.match(z_txt):
                y_stop = y_k - 2.0 * sf
                break
            k2_woerter = list(z_k)
            if j + 1 < len(w_zeilen):
                y_k2 = (w_zeilen[j + 1][0][0].y0 + w_zeilen[j + 1][0][0].y1) / 2.0
                if y_k2 - y_k <= 18.0 * sf:
                    k2_woerter.extend(w_zeilen[j + 1])
            k2_txt = _falten_norm(" ".join(t for _, t in k2_woerter))
            if re.search(r"\b(?:tiefe|teufe|sondiertiefe)\b", k2_txt, re.I) and re.search(
                r"\b(?:n\s*10|n_?10|n\s*20|n\s*30|schlagzahl|schl[äa]e?ge)\b", k2_txt, re.I
            ):
                y_stop = y_k - 2.0 * sf
                break

        daten_zeilen = [
            z for z in w_zeilen[idx + 1 :]
            if y_hdr + 8.0 * sf < (z[0][0].y0 + z[0][0].y1) / 2.0 < y_stop
        ]
        if not daten_zeilen:
            continue

        rohe_paare: list[tuple[float, int | float | dict | None, bool]] = []
        y_tab_max = y_hdr
        for tx_band, wx_band in paare:
            for z in daten_zeilen:
                t_toks = [t for r, t in z if tx_band[0] <= (r.x0 + r.x1) / 2.0 <= tx_band[1]]
                if not t_toks:
                    continue
                t_str = " ".join(t_toks).strip()
                if not TIEFE_ZELLE_RE.fullmatch(t_str):
                    continue
                d_val = _f(t_str)
                if d_val <= 0 or d_val > 120:
                    continue
                y_tab_max = max(y_tab_max, max(r.y1 for r, _ in z))
                w_toks = [t for r, t in z if wx_band[0] <= (r.x0 + r.x1) / 2.0 <= wx_band[1]]
                w_str = " ".join(w_toks).strip()
                if not w_str or w_str in ("-", "--", "L", "**)"):
                    rohe_paare.append((d_val, None, True))
                    continue
                m_zen = ZENSIERT_MARGIN_RE.match(w_str)
                if m_zen:
                    num = int(round(_f(m_zen.group(1))))
                    val_out: int | float | dict = (
                        {"wert": num, "zensiert": True} if REGELN["zensierte_randwerte"] else num
                    )
                    rohe_paare.append((d_val, val_out, False))
                    continue
                if re.fullmatch(r"\d{1,3}", w_str):
                    rohe_paare.append((d_val, int(w_str), False))
                    continue
                if not REGELN["tabelle_kopf_schlagzahl"] and re.fullmatch(r"\d+(?:[.,]\d+)?", w_str):
                    rohe_paare.append((d_val, _f(w_str), False))
                    continue
                rohe_paare.append((d_val, None, True))

        if len(rohe_paare) < 3:
            continue

        gefuellt = [p for p in rohe_paare if p[1] is not None]
        if len(gefuellt) < 3:
            continue

        # Gescannte Tabelle mit zu vielen verlorenen OCR-Schlagzahlen konservativ abweisen
        if sd.scanned and REGELN["scan_konservativ"]:
            max_d_gefuellt = max(p[0] for p in gefuellt)
            erw_zeilen = [p for p in rohe_paare if p[0] <= max_d_gefuellt + 1e-6]
            quote = len(gefuellt) / max(len(erw_zeilen), 1)
            if quote < 0.85:
                bbox_t = pymupdf.Rect(paare[0][0][0], y_hdr, paare[-1][1][1], y_tab_max)
                kopf = _naechster_kopf(koepfe, bbox_t, sf, DPH_ARTEN)
                if kopf:
                    ergebnisse.append(
                        {
                            "code": kopf.code,
                            "art": kopf.art,
                            "seite": sd.seite_nr,
                            "form": "tabelle",
                            "werte": [],
                            "endtiefe": round(max_d_gefuellt, 2),
                            "ansatzhoehe": kopf.ansatzhoehe,
                            "konfidenz": 0.35,
                            "hinweise": [
                                f"Gescannte Tabelle: nur {len(gefuellt)}/{len(erw_zeilen)} "
                                "N10-Werte per OCR lesbar (unter 85-%-Schwelle)."
                            ],
                            "beleg": {
                                "seiten": [sd.seite_nr],
                                "auch_auf_seiten": [],
                                "bbox": [round(bbox_t.x0, 1), round(bbox_t.y0, 1),
                                         round(bbox_t.x1, 1), round(bbox_t.y1, 1)],
                                "methode": "tabelle_scan_konservativ",
                                "achsen": {},
                            },
                            "quelle": sd.quelle,
                        }
                    )
                    min_y_hdr = y_tab_max + 2.0 * sf
                continue

        # Schrittweite dz bestimmen (meist 0,10 m; 0,50 m bei Labortabelle ohne Schlagzahlregel)
        sorted_gefuellt = sorted(gefuellt, key=lambda p: p[0])
        dts = [
            round(sorted_gefuellt[i + 1][0] - sorted_gefuellt[i][0], 3)
            for i in range(len(sorted_gefuellt) - 1)
            if sorted_gefuellt[i + 1][0] > sorted_gefuellt[i][0]
        ]
        dz = statistics.median(dts) if dts else 0.1
        for k_dz in (0.1, 0.2, 0.25, 0.5):
            if abs(dz - k_dz) <= 0.03:
                dz = k_dz
                break

        if REGELN["tabelle_kopf_schlagzahl"]:
            if dz > 0.15 and not re.search(r"\b(?:n\s*20|n\s*30|srs|20\s*cm|30\s*cm)\b", kopf_txt, re.I):
                continue

        hinweise: list[str] = []
        konf = 0.90 if not sd.scanned else 0.72
        sprung_gemeldet_tiefen: set[float] = set()
        vorher_roh: float | None = None
        for d_u, _, _ in gefuellt:
            d_u_r = round(d_u, 4)
            if vorher_roh is not None and d_u_r <= vorher_roh + 1e-6:
                if REGELN["tabelle_luecken_melden"] and d_u_r not in sprung_gemeldet_tiefen:
                    hinweise.append(f"Nicht-monotoner Tiefensprung in Tabelle bei {d_u_r:.2f} m")
                    konf = max(0.2, konf - 0.10)
                    sprung_gemeldet_tiefen.add(d_u_r)
            vorher_roh = d_u_r

        gefuellt = sorted_gefuellt
        werte: list[list] = []
        prev_u: float | None = None
        for d_u, val, _ in gefuellt:
            d_u_r = round(d_u, 4)
            d_o_r = round(max(0.0, d_u_r - dz), 4)
            if prev_u is not None and REGELN["tabelle_luecken_melden"]:
                if d_o_r > prev_u + 0.02:
                    hinweise.append(
                        f"Tiefenluecke in Tabelle: {prev_u:.2f}–{d_o_r:.2f} m fehlen (nicht interpoliert)"
                    )
                    konf = max(0.2, konf - 0.10)
                elif d_u_r <= prev_u + 1e-6 and d_u_r not in sprung_gemeldet_tiefen:
                    hinweise.append(f"Nicht-monotoner Tiefensprung in Tabelle bei {d_u_r:.2f} m")
                    konf = max(0.2, konf - 0.10)
            werte.append([d_o_r, d_u_r, val])
            prev_u = d_u_r

        bbox_t = pymupdf.Rect(paare[0][0][0], y_hdr, paare[-1][1][1], y_tab_max)
        kopf = _naechster_kopf(koepfe, bbox_t, sf, DPH_ARTEN)
        if kopf is None:
            if REGELN["tabelle_kopf_schlagzahl"]:
                continue
            code_str = "TABELLE 1"
            art_str = "DPH"
            ansatz = None
        else:
            code_str = kopf.code
            art_str = kopf.art
            ansatz = kopf.ansatzhoehe

        # Endtiefe-Angabe auf der Seite pruefen
        endtiefe = werte[-1][1]
        for r_z, t_z in sd.zeilen:
            if max(y_hdr - 120.0 * sf, min_y_hdr) <= r_z.y0 <= min(y_tab_max + 45.0 * sf, y_stop):
                m_end = ENDTIEFE_RE.search(_falten_norm(t_z))
                if m_end:
                    end_lbl = _f(m_end.group(1))
                    if end_lbl > endtiefe:
                        endtiefe = end_lbl
                    break

        ergebnisse.append(
            {
                "code": code_str,
                "art": art_str,
                "seite": sd.seite_nr,
                "form": "tabelle",
                "werte": werte,
                "endtiefe": round(float(endtiefe), 3),
                "ansatzhoehe": ansatz,
                "konfidenz": round(konf, 2),
                "hinweise": hinweise,
                "beleg": {
                    "seiten": [sd.seite_nr],
                    "auch_auf_seiten": [],
                    "bbox": [round(bbox_t.x0, 1), round(bbox_t.y0, 1),
                             round(bbox_t.x1, 1), round(bbox_t.y1, 1)],
                    "methode": "tabelle",
                    "achsen": {},
                },
                "quelle": sd.quelle,
            }
        )
        min_y_hdr = y_tab_max + 2.0 * sf

    return ergebnisse


def _anzahl_bohrprofile(sd: _SeitenDaten) -> int:
    """Zaehlt eigenstaendige Bohrprofile auf der Seite (zusammengehoerige Teilspalten eines Profils zusammengefasst)."""
    if not sd.bohr_spalten:
        return 0
    sf = sd.scale_f
    phrasen = _lokale_phrasen(sd.words, sf)
    bohr_codes: set[str] = set()
    for r, t in phrasen:
        tf = _falten_norm(t)
        if BOHR_CODE_RE.match(tf):
            if any(
                abs(((r.x0 + r.x1) / 2.0) - ((col.rect.x0 + col.rect.x1) / 2.0)) <= 75.0 * sf
                and -15.0 * sf <= col.rect.y0 - r.y1 <= 320.0 * sf
                for col in sd.bohr_spalten
            ):
                bohr_codes.add(_norm_code(tf))
    if bohr_codes:
        return len(bohr_codes)
    # Fallback ohne Code (z. B. tiefe_nicht_bohrungscode=False): Spalten horizontal mit 30-pt-Abstand clustern
    spalten = sorted(sd.bohr_spalten, key=lambda c: c.rect.x0)
    gruppen = 1
    prev_x1 = spalten[0].rect.x1
    for col in spalten[1:]:
        if col.rect.x0 - prev_x1 > 30.0 * sf:
            gruppen += 1
        prev_x1 = max(prev_x1, col.rect.x1)
    return gruppen


def _ist_laengsschnitt_seite(sd: _SeitenDaten, koepfe: list[_Kopf] | None = None) -> bool:
    """Prueft anhand allgemeiner Merkmale, ob eine Seite einen geologischen Laengsschnitt darstellt."""
    text = _falten_norm(" ".join(t for _, t in sd.zeilen))
    if LAENGS_CUE_RE.search(text):
        return True
    n_bohr = _anzahl_bohrprofile(sd)
    if n_bohr >= 2:
        return True
    if koepfe and len({_norm_code(k.code) for k in koepfe}) >= 3 and n_bohr >= 1:
        return True
    return False


def _laengsschnitt_nhn_regression(
    sd: _SeitenDaten, koepfe: list[_Kopf] | None = None
) -> tuple[float, float, float] | None:
    """Bestimmt gemeinsame NHN-Hoehenskala nhn = a_nhn * y + b_nhn fuer Laengsschnitte."""
    if not REGELN["laengsschnitt_hoehenmassstab"]:
        return None
    sf = sd.scale_f
    if not _ist_laengsschnitt_seite(sd, koepfe):
        return None

    kands: list[tuple[pymupdf.Rect, float]] = []
    for r, t, *_ in sd.words:
        tok = str(t).strip().rstrip("m")
        if not re.fullmatch(r"[+-]?\d{1,4}[.,]\d{2}", tok):
            continue
        try:
            v = _f(tok)
        except ValueError:
            continue
        if -50.0 <= v <= 3000.0:
            kands.append((pymupdf.Rect(r), v))

    # Nach x1 oder x0 gruppieren
    spalten: dict[int, list[tuple[pymupdf.Rect, float]]] = defaultdict(list)
    for r, v in kands:
        spalten[round(r.x1 / (6.0 * sf))].append((r, v))

    best: tuple[int, float, float, float] | None = None
    for grp in spalten.values():
        if len(grp) < 4:
            continue
        grp.sort(key=lambda e: (e[0].y0 + e[0].y1) / 2.0)
        # Fallende Werte nach unten (m NHN)
        ys = np.array([(r.y0 + r.y1) / 2.0 for r, _ in grp], dtype=float)
        vs = np.array([v for _, v in grp], dtype=float)
        if not np.all(np.diff(vs) < -1e-6):
            continue
        if REGELN["tickstriche_am_rahmen"]:               # #55: Label steht ueber/unter seinem Tickstrich -> Strich gilt
            striche = []
            for r, _ in grp:
                h = [g.y0 for g in sd.segs if g.horizontal and g.x0 <= r.x1 + 15 * sf and g.x1 >= r.x0 - 15 * sf
                     and r.y0 - 3 * sf <= g.y0 <= r.y1 + 3 * sf and g.x1 - g.x0 <= 40 * sf]
                striche.append(min(h, key=lambda y: abs(y - (r.y0 + r.y1) / 2.0)) if h else None)
            if sum(y is not None for y in striche) >= 0.8 * len(grp):
                ys = np.array([y if y is not None else m for y, m in zip(striche, ys)], dtype=float)
        diffs = -np.diff(vs)
        med = float(np.median(diffs))
        if med <= 1e-6 or float(np.max(diffs) - np.min(diffs)) > 0.08 * med + 1e-4:
            continue
        a, b, r2, res_max = _ols_fit(ys, vs)
        if a < 0 and r2 >= 0.998 and res_max <= 0.10:
            if best is None or len(grp) > best[0]:
                best = (len(grp), a, b, r2)
    if best is None:
        return None
    return best[1], best[2], best[3]


def _kandidaten_rahmen(sd: _SeitenDaten) -> list[tuple[pymupdf.Rect, str]]:
    """Findet Plotrahmen aus Rechtecken, zusammengesetzten H/V-Linien und L-Achsen."""
    sf = sd.scale_f
    min_h = 36.0 if REGELN["kurze_rahmen"] else 52.0      # #55: Rammdiagramm einer 2-m-Sondierung auf langem Blatt
    kands: list[tuple[pymupdf.Rect, str]] = []
    seite_flaeche = max(sd.breite * sd.hoehe, 1.0)

    # Quelle A: Explizite Rechtecke / Quads / geschlossene 4-Linien-Zeichnungen
    for d in sd.drawings:
        it = d["items"]
        r = pymupdf.Rect(d["rect"])
        if r.width < 32 * sf or r.height < min_h * sf:
            continue
        if r.get_area() > 0.85 * seite_flaeche:
            continue
        fill = d.get("fill")
        if fill is not None and min(fill) < 0.97 and not d.get("color"):
            continue
        if len(it) == 1 and it[0][0] in ("re", "qu"):
            kands.append((r, "re"))
        elif len(it) == 4 and all(x[0] == "l" for x in it):
            if all(abs(x[1].x - x[2].x) < 0.8 * sf or abs(x[1].y - x[2].y) < 0.8 * sf for x in it):
                kands.append((r, "re4"))
        elif len(it) == 2 and all(x[0] == "l" for x in it):
            # Quelle C: L-Achsen (z. B. marl_251 S.6)
            a1, b1 = it[0][1], it[0][2]
            a2, b2 = it[1][1], it[1][2]
            ist_h1 = abs(a1.y - b1.y) < 0.8 * sf and abs(a1.x - b1.x) >= 28 * sf
            ist_v1 = abs(a1.x - b1.x) < 0.8 * sf and abs(a1.y - b1.y) >= (min_h - 2) * sf
            ist_h2 = abs(a2.y - b2.y) < 0.8 * sf and abs(a2.x - b2.x) >= 28 * sf
            ist_v2 = abs(a2.x - b2.x) < 0.8 * sf and abs(a2.y - b2.y) >= (min_h - 2) * sf
            if (ist_h1 and ist_v2) or (ist_v1 and ist_h2):
                kands.append((r, "l_achse"))

    # Quelle B: Aus Segmenten zusammengesetzte Rahmen (hausham, marl_251, rednitzhembach, berlin_v67b)
    H: list[Seg] = []
    if sd.segs:
        gap = 2.5 * sf
        H = [s for s in _merge([s for s in sd.segs if s.horizontal and s.x1 - s.x0 >= 8 * sf], "h", gap=gap)
             if s.x1 - s.x0 >= 30 * sf]
        V = [s for s in _merge([s for s in sd.segs if s.vertical and s.y1 - s.y0 >= 12 * sf], "v", gap=gap)
             if s.y1 - s.y0 >= min_h * sf]
        # Ausserste Seitenrahmen verwerfen
        V = [v for v in V if v.y1 - v.y0 < 0.88 * sd.hoehe]
        H = [h for h in H if h.x1 - h.x0 < 0.88 * sd.breite]

        # V-Linien nach y-Spanne und verbindenden H-Linien zu Plot-Komponenten gruppieren
        v_gruppen: list[list[Seg]] = []
        V_sort = sorted(V, key=lambda v: (v.y0, v.x0))
        genutzt = [False] * len(V_sort)
        for i, v0 in enumerate(V_sort):
            if genutzt[i]:
                continue
            grp = [v0]
            genutzt[i] = True
            for j in range(i + 1, len(V_sort)):
                if genutzt[j]:
                    continue
                vj = V_sort[j]
                ov_y = min(v0.y1, vj.y1) - max(v0.y0, vj.y0)
                if ov_y >= 0.82 * max(v0.y1 - v0.y0, vj.y1 - vj.y0):
                    # Pruefen ob H-Linie zwischen links/rechts ueberbrueckt
                    x_min_g = min(s.x0 for s in grp)
                    x_max_g = max(s.x0 for s in grp)
                    nx0, nx1 = min(x_min_g, vj.x0), max(x_max_g, vj.x0)
                    if nx1 - nx0 <= 450 * sf and any(
                        h.x0 <= nx0 + 10 * sf and h.x1 >= nx1 - 10 * sf
                        and v0.y0 - 8 * sf <= h.y0 <= v0.y1 + 8 * sf
                        for h in H
                    ):
                        grp.append(vj)
                        genutzt[j] = True
            if len(grp) >= 2:
                v_gruppen.append(grp)

        for grp in v_gruppen:
            xs = sorted(v.x0 for v in grp)
            if xs[-1] - xs[0] < 32 * sf:
                continue
            x0_f, x1_f = xs[0], xs[-1]
            y0_v = min(v.y0 for v in grp)
            y1_v = max(v.y1 for v in grp)
            h_pass = [
                h for h in H
                if h.x0 <= x0_f + 10 * sf and h.x1 >= x1_f - 10 * sf
                and y0_v - 10 * sf <= h.y0 <= y1_v + 10 * sf
            ]
            y0_f = min((h.y0 for h in h_pass), default=y0_v)
            y1_f = max((h.y0 for h in h_pass), default=y1_v)
            if len(h_pass) >= 1 and y1_f - y0_f >= min_h * sf:
                r = pymupdf.Rect(x0_f, y0_f, x1_f, y1_f)
                if r.get_area() <= 0.85 * seite_flaeche:
                    kands.append((r, "seg_box"))

    if not REGELN["achse_arithmetisch_und_rahmen"]:
        # Ungerahmte Kurvenzeichnungen / freistehende Achslinien als schwache Rahmen zulassen
        for d in sd.drawings:
            l_anz = sum(1 for it in d["items"] if it[0] == "l")
            if l_anz < 4:
                continue
            dr = pymupdf.Rect(d["rect"])
            if dr.width < 15 * sf or dr.height < 40 * sf or dr.get_area() > 0.85 * seite_flaeche:
                continue
            if any((dr & kr).get_area() > 0.5 * dr.get_area() for kr, _ in kands):
                continue
            x0_o = dr.x0
            x1_o = max(dr.x1, dr.x0 + 35 * sf)
            y0_o, y1_o = dr.y0, dr.y1
            for h in H:
                if h.x0 <= dr.x1 + 20 * sf and h.x1 >= dr.x0 - 20 * sf:
                    if dr.y0 - 45 * sf <= h.y0 <= dr.y1 + 45 * sf:
                        x0_o = min(x0_o, h.x0)
                        x1_o = max(x1_o, h.x1)
                        y0_o = min(y0_o, h.y0)
                        y1_o = max(y1_o, h.y0)
            r_ohne = pymupdf.Rect(x0_o, y0_o, x1_o, y1_o)
            if r_ohne.width >= 32 * sf and r_ohne.height >= min_h * sf:
                kands.append((r_ohne, "ohne_rahmen"))

    # Deduplizierung ueber IoU (> 0.85), dabei 're' vor 'seg_box' vor 'l_achse' bevorzugen
    prio = {"re": 3, "re4": 2, "seg_box": 1, "l_achse": 0, "ohne_rahmen": -1}
    kands.sort(key=lambda e: (-prio.get(e[1], 0), e[0].get_area()))
    behalten: list[tuple[pymupdf.Rect, str]] = []
    for r, typ in kands:
        dup = False
        for kr, _ in behalten:
            inter = (r & kr).get_area()
            union = r.get_area() + kr.get_area() - inter
            if union > 0 and inter / union > 0.85:
                dup = True
                break
        if not dup:
            behalten.append((r, typ))
    return behalten


@dataclass
class _AchseX:
    band: str           # 'top' | 'bottom'
    skala: str          # 'linear' | 'log10'
    a_x: float
    b_x: float
    val_min: float
    val_max: float
    x_zero: float
    farbe: tuple[float, ...] | None
    label_txt: str
    ticks: list[tuple[float, float]]


def _kalibriere_x_achsen(sd: _SeitenDaten, rahmen: pymupdf.Rect) -> list[_AchseX]:
    """Findet und kalibriert eine oder mehrere horizontale Wertachsen oben/unten am Rahmen."""
    sf = sd.scale_f
    titel_zeilen_y = [
        (r.y0 + r.y1) / 2.0
        for r, t in sd.zeilen
        if SOND_SUCH_RE.search(_falten_norm(t)) or ARCHIV_SOND_RE.match(_falten_norm(t))
    ]

    baender = [
        ("top", rahmen.y0 - 34 * sf, rahmen.y0 + 5 * sf),
        ("bottom", rahmen.y1 - 5 * sf, rahmen.y1 + 34 * sf),
    ]
    achsen: list[_AchseX] = []
    min_ticks = 3 if (REGELN["achse_arithmetisch_und_rahmen"] and (not sd.scanned or REGELN["scan_konservativ"])) else 2
    bohr_ziffer_rects = _bohr_code_ziffer_rects(sd.words, sf) if REGELN["tiefe_nicht_bohrungscode"] else []

    for band_name, y_lo, y_hi in baender:
        toks: list[tuple[pymupdf.Rect, float]] = []
        for r, t, *_ in sd.words:
            yc = (r.y0 + r.y1) / 2.0
            if not (y_lo <= yc <= y_hi):
                continue
            if r.x1 < rahmen.x0 - 6 * sf or r.x0 > rahmen.x1 + 16 * sf:
                continue
            # Ueberschrift 'DPH 10' auf marl_251 S.26 nicht als Achsentick '10' mitzaehlen
            if any(abs(yc - ty) <= 4.5 * sf for ty in titel_zeilen_y):
                continue
            if bohr_ziffer_rects:
                rc = pymupdf.Point((r.x0 + r.x1) / 2.0, yc)
                r_area = max(pymupdf.Rect(r).get_area(), 1e-6)
                if any(ar.contains(rc) or (pymupdf.Rect(r) & ar).get_area() > 0.5 * r_area for ar in bohr_ziffer_rects):
                    continue
            toks.extend(_split_numerische_woerter(pymupdf.Rect(r), str(t)))

        if len(toks) < min_ticks:
            continue

        # Zeilenweise nach y_center gruppieren
        zeilen_grp: list[list[tuple[pymupdf.Rect, float]]] = []
        for r, v in sorted(toks, key=lambda e: ((e[0].y0 + e[0].y1) / 2.0, e[0].x0)):
            yc = (r.y0 + r.y1) / 2.0
            if zeilen_grp:
                ry = sum((e[0].y0 + e[0].y1) / 2.0 for e in zeilen_grp[-1]) / len(zeilen_grp[-1])
                if abs(yc - ry) <= 5.0 * sf:
                    zeilen_grp[-1].append((r, v))
                    continue
            zeilen_grp.append([(r, v)])

        kand_achsen: list[_AchseX] = []
        for grp in zeilen_grp:
            if REGELN["achse_zeile_ausgerichtet"] and len(grp) >= 3:
                # eine Achse ist eine ausgerichtete Zeile: '0.0' der Tiefenachse daneben gehoert nicht dazu (#54)
                med = float(np.median([(e[0].y0 + e[0].y1) / 2.0 for e in grp]))
                grp = [e for e in grp if abs((e[0].y0 + e[0].y1) / 2.0 - med) <= 3.0 * sf]
            grp.sort(key=lambda e: (e[0].x0 + e[0].x1) / 2.0)
            # Duplikate bei gleichem x/Wert entfernen
            clean: list[tuple[pymupdf.Rect, float]] = []
            for r, v in grp:
                xc = (r.x0 + r.x1) / 2.0
                if (
                    clean
                    and abs(((clean[-1][0].x0 + clean[-1][0].x1) / 2.0) - xc) < 3 * sf
                    and abs(clean[-1][1] - v) < 1e-4
                ):
                    continue
                clean.append((r, v))
            if len(clean) < min_ticks:
                continue

            xs = np.array([(r.x0 + r.x1) / 2.0 for r, _ in clean], dtype=float)
            vs = np.array([v for _, v in clean], dtype=float)
            ticks_xy = list(zip(xs.tolist(), vs.tolist()))

            # 1) Linear pruefen
            lin_ok = False
            if REGELN["achse_arithmetisch_und_rahmen"] and (not sd.scanned or REGELN["scan_konservativ"]):
                if _arithmetische_folge_ok(vs.tolist(), tol_rel=0.06):
                    a_x, b_x, r2, _ = _ols_fit(xs, vs)
                    if r2 >= 0.995 and abs(a_x) > 1e-9:
                        x_zero = -b_x / a_x
                        # 0-Punkt muss nahe rahmen.x0 (oder rahmen.x1 bei invertierter Achse) liegen
                        if a_x > 0 and abs(x_zero - rahmen.x0) <= 20 * sf:
                            lin_ok = True
                        elif a_x < 0 and abs(x_zero - rahmen.x1) <= 20 * sf:
                            lin_ok = True
                        elif min(vs) > 0 and abs(rahmen.x0 - xs[0]) <= 15 * sf:
                            # Achse ohne '0'-Tick (z. B. marl_251: 10..100), Extrapolation pruefen
                            if abs(x_zero - rahmen.x0) <= 20 * sf:
                                lin_ok = True
            else:
                a_x, b_x, r2, _ = _ols_fit(xs, vs)
                if abs(a_x) > 1e-9 and len(clean) >= 2:
                    x_zero = -b_x / a_x
                    lin_ok = True

            if lin_ok:
                kand_achsen.append(
                    _AchseX(
                        band=band_name,
                        skala="linear",
                        a_x=a_x,
                        b_x=b_x,
                        val_min=float(min(vs)),
                        val_max=float(max(vs)),
                        x_zero=float(x_zero if min(vs) <= 0 or a_x > 0 else rahmen.x1),
                        farbe=None,
                        label_txt="",
                        ticks=ticks_xy,
                    )
                )
                continue

            # 2) Logarithmisch (log10) pruefen
            if REGELN["cpt_log_achse"] and np.all(vs > 0):
                lvs = np.log10(vs)
                if _arithmetische_folge_ok(lvs.tolist(), tol_rel=0.06):
                    a_l, b_l, r2_l, _ = _ols_fit(xs, lvs)
                    if r2_l >= 0.995 and abs(a_l) > 1e-9:
                        kand_achsen.append(
                            _AchseX(
                                band=band_name,
                                skala="log10",
                                a_x=a_l,
                                b_x=b_l,
                                val_min=float(min(vs)),
                                val_max=float(max(vs)),
                                x_zero=float(xs[0]),
                                farbe=None,
                                label_txt="",
                                ticks=ticks_xy,
                            )
                        )
            elif not REGELN["cpt_log_achse"] and len(clean) >= min_ticks and np.all(np.diff(vs) > 0):
                # Ablation cpt_log_achse=False: zwinge lineare Regression auch auf Log-Achsen
                a_x, b_x, _, _ = _ols_fit(xs, vs)
                if abs(a_x) > 1e-9:
                    kand_achsen.append(
                        _AchseX(
                            band=band_name,
                            skala="linear",
                            a_x=a_x,
                            b_x=b_x,
                            val_min=float(min(vs)),
                            val_max=float(max(vs)),
                            x_zero=float(-b_x / a_x),
                            farbe=None,
                            label_txt="",
                            ticks=ticks_xy,
                        )
                    )

        if kand_achsen:
            # Naechstgelegene Achsenreihe am Rahmenrand waehlen
            achsen.append(max(kand_achsen, key=lambda ax: len(ax.ticks)))

    # Achsentext / Farbe aus der Umgebung (fuer CPT) ermitteln
    for ax in achsen:
        y_such = rahmen.y0 - 20 * sf if ax.band == "top" else rahmen.y1 + 20 * sf
        txt_list = [
            _falten_norm(t)
            for r, t in sd.zeilen
            if abs((r.y0 + r.y1) / 2.0 - y_such) <= 22 * sf
            and r.x1 >= rahmen.x0 - 20 * sf
            and r.x0 <= rahmen.x1 + 20 * sf
            and not ZAHL_RE.fullmatch(t.strip())
        ]
        ax.label_txt = " ".join(txt_list)
    return achsen


@dataclass
class _AchseY:
    a_y: float
    b_y: float
    quelle: str          # 'lokal' | 'nhn_lokal' | 'laengsschnitt_nhn'
    r2: float
    ticks: list[tuple[float, float]]


def _y_achse_endtiefe(y_ax: _AchseY, rahmen: pymupdf.Rect) -> float | None:
    """Bestimmt geschaetzte Endtiefe aus lokaler Tiefenskala oder Rahmenunterkante."""
    if y_ax.quelle == "lokal" and y_ax.ticks:
        return round(max(v for _, v in y_ax.ticks), 2)
    t_bot = y_ax.a_y * rahmen.y1 + y_ax.b_y
    return round(t_bot, 2) if t_bot > 0 else None


def _kalibriere_y_achse(
    sd: _SeitenDaten,
    rahmen: pymupdf.Rect,
    nhn_global: tuple[float, float, float] | None,
    ansatzhoehe: float | None,
) -> tuple[_AchseY | None, list[str]]:
    """Kalibriert Tiefe(y) = a_y * y + b_y ueber lokales Lineal oder NHN-Massstab."""
    sf = sd.scale_f
    hinweise: list[str] = []
    min_ticks = 3 if (REGELN["achse_arithmetisch_und_rahmen"] and (not sd.scanned or REGELN["scan_konservativ"])) else 2
    streng_arith = REGELN["achse_arithmetisch_und_rahmen"] and (not sd.scanned or REGELN["scan_konservativ"])
    bohr_ziffer_rects = _bohr_code_ziffer_rects(sd.words, sf) if REGELN["tiefe_nicht_bohrungscode"] else []

    # Kandidatenzahlen links vom Rahmen sammeln
    kands: list[tuple[pymupdf.Rect, float]] = []
    for r, t, *_ in sd.words:
        yc = (r.y0 + r.y1) / 2.0
        if not (rahmen.y0 - 10 * sf <= yc <= rahmen.y1 + 10 * sf):
            continue
        if not (rahmen.x0 - 65 * sf <= r.x1 <= rahmen.x0 + 5 * sf):
            continue
        if bohr_ziffer_rects:
            rc = pymupdf.Point((r.x0 + r.x1) / 2.0, yc)
            r_area = max(pymupdf.Rect(r).get_area(), 1e-6)
            if any(ar.contains(rc) or (pymupdf.Rect(r) & ar).get_area() > 0.5 * r_area for ar in bohr_ziffer_rects):
                continue
        tok = str(t).strip().rstrip("m")
        if not re.fullmatch(r"[+-]?\d{1,4}(?:[.,]\d{1,2})?", tok):
            continue
        try:
            v = _f(tok)
        except ValueError:
            continue
        kands.append((pymupdf.Rect(r), v))

    # Nach x1 gruppieren (und auch x0 pruefen)
    gruppen: list[list[tuple[pymupdf.Rect, float]]] = []
    by_x1: dict[int, list[tuple[pymupdf.Rect, float]]] = defaultdict(list)
    for r, v in kands:
        by_x1[round(r.x1 / (7.0 * sf))].append((r, v))
    gruppen.extend(by_x1.values())

    lokale_kands: list[tuple[float, _AchseY]] = []
    nhn_kands: list[tuple[float, _AchseY]] = []

    # Nur echte Gitterlinien (volle Rahmenbreite) oder linke Tick-Striche verwenden, keine Kurvensegmente
    h_line_ys = sorted({
        round(s.y0, 2)
        for s in _merge(
            [
                s for s in sd.segs
                if s.horizontal and (
                    (s.x0 <= rahmen.x0 + 6 * sf and s.x1 >= rahmen.x0 + 0.65 * rahmen.width)
                    or (s.x0 <= rahmen.x0 - 1.5 * sf and s.x1 <= rahmen.x0 + 4 * sf
                        and (not REGELN["tickstriche_am_rahmen"]       # #55: Schraffur links (Nachbarprofil) ist kein Tick
                             or (s.x1 >= rahmen.x0 - 12 * sf and rahmen.y0 - 10 * sf <= s.y0 <= rahmen.y1 + 10 * sf)))
                )
            ],
            "h",
            gap=2.5 * sf,
        )
    })

    def _snappe_y(sauber_list: list[tuple[pymupdf.Rect, float]]) -> np.ndarray:
        ys_mid = np.array([(r.y0 + r.y1) / 2.0 for r, _ in sauber_list], dtype=float)
        if not h_line_ys:
            return ys_mid
        vs_s = np.array([v for _, v in sauber_list], dtype=float)
        best_ys = ys_mid
        best_score: tuple[int, float] = (0, -1e9)
        min_treffer = max(3, int(0.70 * len(sauber_list)))
        if REGELN["tickstriche_am_rahmen"] and len(sauber_list) == 2:
            min_treffer = 2                                   # #55: kurze Sondierung (1,00 / 2,00): beide muessen einrasten

        for anker in ("mid", "bot", "top"):
            snapped: list[float] = []
            treffer = 0
            dists: list[float] = []
            for r, _ in sauber_list:
                ref = (r.y0 + r.y1) / 2.0 if anker == "mid" else (r.y1 if anker == "bot" else r.y0)
                cand_h = min(h_line_ys, key=lambda hy: abs(hy - ref))
                d = abs(cand_h - ref)
                if d <= 2.5 * sf:
                    snapped.append(cand_h)
                    treffer += 1
                    dists.append(d)
                else:
                    snapped.append(ref)
            if treffer >= min_treffer:
                ys_s = np.array(snapped, dtype=float)
                _, _, r2_s, _ = _ols_fit(ys_s, vs_s)
                if r2_s >= 0.998:
                    score = (treffer, -float(np.mean(dists)))
                    if score > best_score:
                        best_score = score
                        best_ys = ys_s
        return best_ys

    for grp in gruppen:
        if len(grp) < min_ticks:
            continue
        # 1) Steigendes Tiefenlineal
        sauber = _beste_arith_unterfolge(grp, nur_steigend=True)
        if len(sauber) >= min_ticks:
            vs_alle = [v for _, v in sauber]
            ok = (
                _tiefenlineal_folge_ok(vs_alle, tol_rel=0.06)
                if streng_arith
                else (len(vs_alle) >= 2 and all(b > a for a, b in zip(vs_alle, vs_alle[1:])))
            )
            if ok:
                # Bei Teil-Endtick (z. B. 1..9, 9,30) Regression auf regulaerem Praefix durchfuehren
                sauber_fit = sauber
                if (
                    len(sauber) >= 4
                    and not _arithmetische_folge_ok(vs_alle, tol_rel=0.06)
                    and _arithmetische_folge_ok(vs_alle[:-1], tol_rel=0.06)
                ):
                    sauber_fit = sauber[:-1]
                ys = _snappe_y(sauber_fit)
                vs = np.array([v for _, v in sauber_fit], dtype=float)
                a_y, b_y, r2, _ = _ols_fit(ys, vs)
                if a_y > 0 and (r2 >= 0.995 or not streng_arith):
                    tiefe_oben = a_y * rahmen.y0 + b_y
                    if -0.25 <= tiefe_oben <= 50.0:
                        dist_x = abs(rahmen.x0 - float(np.mean([r.x1 for r, _ in sauber_fit])))
                        lokale_kands.append(
                            (dist_x - 3.0 * len(sauber), _AchseY(a_y, b_y, "lokal", r2, list(zip(ys, vs))))
                        )

        # 2) Fallende lokale NHN-Leiste
        sauber_nhn = _beste_arith_unterfolge(grp, nur_steigend=False)
        if len(sauber_nhn) >= min_ticks:
            ys = _snappe_y(sauber_nhn) if len(sauber_nhn) >= 3 else np.array(
                [(r.y0 + r.y1) / 2.0 for r, _ in sauber_nhn], dtype=float
            )
            vs = np.array([v for _, v in sauber_nhn], dtype=float)
            nhn_ok = (
                _arithmetische_folge_ok(vs.tolist(), tol_rel=0.06)
                if streng_arith
                else (len(vs) >= 2 and bool(np.all(np.diff(vs) < -1e-6)))
            )
            if np.all(np.diff(vs) < -1e-6) and nhn_ok:
                a_n, b_n, r2_n, _ = _ols_fit(ys, vs)
                if a_n < 0 and (r2_n >= 0.995 or not streng_arith) and ansatzhoehe is not None:
                    a_y = -a_n
                    b_y = ansatzhoehe - b_n
                    dist_x = abs(rahmen.x0 - float(np.mean([r.x1 for r, _ in sauber_nhn])))
                    nhn_kands.append(
                        (dist_x, _AchseY(a_y, b_y, "nhn_lokal", r2_n, list(zip(ys, vs))))
                    )

    if lokale_kands:
        lokale_kands.sort(key=lambda e: e[0])
        return lokale_kands[0][1], hinweise
    if nhn_kands:
        nhn_kands.sort(key=lambda e: e[0])
        return nhn_kands[0][1], hinweise

    # 3) Gemeinsamer Laengsschnitt-NHN-Massstab (s03)
    if nhn_global is not None and REGELN["laengsschnitt_hoehenmassstab"]:
        a_n, b_n, r2_n = nhn_global
        a_y = -a_n
        if ansatzhoehe is not None:
            b_y = ansatzhoehe - b_n
            # Konsistenzpruefung: Rahmen-Oberkante sollte nahe Ansatzhoehe liegen
            t_top = a_y * rahmen.y0 + b_y
            if abs(t_top) > 0.15:
                hinweise.append(
                    f"Laengsschnitt: Rahmenoberkante weicht um {t_top:.2f} m von Ansatzhoehe ab"
                )
        else:
            b_y = -a_y * rahmen.y0
            hinweise.append(
                "Ansatzhoehe fehlt im Laengsschnitt: Tiefen nur relativ ab Rahmenoberkante berechnet"
            )
        return _AchseY(a_y, b_y, "laengsschnitt_nhn", r2_n, []), hinweise

    return None, hinweise


def _ist_bohrprofil_falle(sd: _SeitenDaten, rahmen: pymupdf.Rect, x_achsen: list[_AchseX],
                          kopf: _Kopf | None) -> bool:
    """L14 + Negativ-Fallenfilter: verwirft Bohrprofile, RQD-Legenden und CBR-Versuche."""
    if not REGELN["tiefe_nicht_bohrungscode"]:
        return False
    sf = sd.scale_f
    # Ueberlappung mit einer echten Bohrsaeule (nicht blosse Gitterstreifen eines Sondierungsrahmens)
    for col in sd.bohr_spalten:
        inter = rahmen & col.rect
        if not inter.is_empty and inter.get_area() > 0.35 * min(rahmen.get_area(), col.rect.get_area()):
            if kopf is None or abs(col.rect.width - rahmen.width) <= 8 * sf:
                return True
    # Kontext direkt am Rahmen und Kopf
    um_txt = _falten_norm(
        " ".join(
            t for r, t in sd.zeilen
            if r.x1 >= rahmen.x0 - 80 * sf and r.x0 <= rahmen.x1 + 80 * sf
            and r.y1 >= rahmen.y0 - 95 * sf and r.y0 <= rahmen.y1 + 60 * sf
        )
    )
    if NEGATIV_KONTEXT_RE.search(um_txt):
        return True
    if kopf is None:
        # Ohne expliziten Sondierungskopf nur akzeptieren, wenn eindeutiges Achsen-Stichwort vorhanden
        achsen_txt = " ".join(ax.label_txt for ax in x_achsen)
        if not SOND_KONTEXT_RE.search(achsen_txt):
            return True
    return False



def _rechteck(d: dict) -> pymupdf.Rect:
    """Huelle einer Zeichnung, um 0,5 pt erweitert: ein senkrechter oder waagrechter Einzelstrich hat
    sonst Breite oder Hoehe 0 und gilt in pymupdf als leer (jede Schnittmenge waere leer)."""
    return pymupdf.Rect(d["rect"]) + (-0.5, -0.5, 0.5, 0.5)

def _ist_gitterlinie(d: dict, rahmen: pymupdf.Rect, sf: float) -> bool:
    """Erkennt vollstaendige Gitterlinien, Rahmenlinien und weisse Masken."""
    r = pymupdf.Rect(d["rect"])
    fill = d.get("fill")
    color = d.get("color")
    if fill is not None and min(fill) >= 0.97 and color is None:
        return True
    if (
        abs(r.x0 - rahmen.x0) <= 2.5 * sf
        and abs(r.x1 - rahmen.x1) <= 2.5 * sf
        and abs(r.y0 - rahmen.y0) <= 2.5 * sf
        and abs(r.y1 - rahmen.y1) <= 2.5 * sf
        and len(d["items"]) <= 4
    ):
        return True
    if len(d["items"]) == 1 and d["items"][0][0] == "l":
        a, b = d["items"][0][1], d["items"][0][2]
        if abs(a.y - b.y) < 0.5 * sf and abs(a.x - b.x) >= 0.85 * rahmen.width:
            return True
        if abs(a.x - b.x) < 0.5 * sf and abs(a.y - b.y) >= 0.85 * rahmen.height:
            return True
        if color is not None and min(color) >= 0.72 and (d.get("width") or 0.0) <= 0.45 * sf:
            if abs(a.x - b.x) >= 0.4 * rahmen.width or abs(a.y - b.y) >= 0.4 * rahmen.height:
                return True
    return False



def _einzelstriche_verketten(drawings: list[dict], sf: float, min_glieder: int = 6) -> list[dict]:
    """Manche CAD-Exporte zeichnen eine Treppenkurve als einzelne Striche (je ein Pfad mit einem 'l').
    Striche gleicher Farbe und Breite, deren Enden aneinanderstossen (<= 0,5 pt), werden zu einem Pfad
    verkettet; nur Ketten mit mindestens ``min_glieder`` Gliedern zaehlen (eine Kurve, kein Gitter)."""
    einzeln = [d for d in drawings if len(d.get("items") or []) == 1 and d["items"][0][0] == "l"
               and d.get("fill") is None and d.get("color") is not None]
    gruppen: dict[tuple, list] = defaultdict(list)
    for d in einzeln:
        gruppen[(tuple(round(c, 3) for c in d["color"]), round(float(d.get("width") or 0), 2))].append(d["items"][0])
    tol = 0.5 * sf
    out: list[dict] = []
    for (farbe, breite), striche in gruppen.items():
        frei = list(striche)
        while frei:
            kette = [frei.pop(0)]
            gewachsen = True
            while gewachsen:
                gewachsen = False
                kopf, ende = kette[0][1], kette[-1][2]
                for i, (_, a, b) in enumerate(frei):
                    if abs(a.x - ende.x) <= tol and abs(a.y - ende.y) <= tol:
                        kette.append(frei.pop(i)); gewachsen = True; break
                    if abs(b.x - kopf.x) <= tol and abs(b.y - kopf.y) <= tol:
                        kette.insert(0, frei.pop(i)); gewachsen = True; break
            if len(kette) >= min_glieder:
                r = pymupdf.Rect(kette[0][1], kette[0][1])
                for _, a, b in kette:
                    r |= a
                    r |= b
                out.append({"items": kette, "color": farbe, "fill": None, "width": breite, "rect": r})
    return out

def _extrahiere_dph_vektor(
    sd: _SeitenDaten,
    rahmen: pymupdf.Rect,
    x_ax: _AchseX,
    y_ax: _AchseY,
) -> tuple[list[list], str]:
    """Extrahiert DPH-Schritte aus gefuellten Balken oder gestuften Vektor-Polylinien."""
    sf = sd.scale_f
    innen = [
        d for d in sd.drawings
        if not (_rechteck(d) & pymupdf.Rect(
            rahmen.x0 - 4 * sf, rahmen.y0 - 4 * sf, rahmen.x1 + 4 * sf, rahmen.y1 + 4 * sf
        )).is_empty
        and not _ist_gitterlinie(d, rahmen, sf)
    ]

    # Pfad A: Gefuellte horizontale Balken ('re', z. B. triefenstein_bp41)
    for d in innen:
        fill = d.get("fill")
        if fill is None or min(fill) >= 0.97:
            continue
        re_rects = [pymupdf.Rect(it[1]) for it in d["items"] if it[0] == "re"]
        balken = [
            r for r in re_rects
            if rahmen.x0 - 2 * sf <= r.x0 <= rahmen.x1 + 2 * sf
            and abs(r.x0 - x_ax.x_zero) <= 4.0 * sf
            and 0.03 <= y_ax.a_y * r.height <= 0.65
        ]
        if len(balken) >= 3:
            hs = [r.height for r in balken]
            med_h = statistics.median(hs)
            if max(hs) - min(hs) <= 0.4 * med_h:
                balken.sort(key=lambda r: r.y0)
                schritte: list[list] = []
                for r in balken:
                    t_o = round(max(0.0, y_ax.a_y * r.y0 + y_ax.b_y), 2)
                    t_u = round(y_ax.a_y * r.y1 + y_ax.b_y, 2)
                    n_val = max(0, int(round(x_ax.a_x * r.x1 + x_ax.b_x)))
                    if t_u > t_o:
                        schritte.append([t_o, t_u, n_val])
                if schritte:
                    return schritte, "vektor_balken"

    # Pfad B: Vertikale Segmente gestufter Treppenkurven
    v_segs: list[tuple[float, float, float]] = []
    if REGELN.get("einzelstriche_verketten", True):
        innen = innen + _einzelstriche_verketten(innen, sf)
    for d in innen:
        if d.get("color") is None and d.get("fill") is not None:
            continue
        l_items = [it for it in d["items"] if it[0] == "l"]
        if len(l_items) < 2:
            continue
        in_frame: list[tuple[float, float, float]] = []
        excursion: list[tuple[float, float, float]] = []
        for _, a, b in l_items:
            if abs(a.x - b.x) <= 0.6 * sf and abs(a.y - b.y) >= 1.2 * sf:
                x_m = (a.x + b.x) / 2.0
                y_a, y_b = min(a.y, b.y), max(a.y, b.y)
                # Achsenpfeile / Rahmenraender (z. B. hausham d[89]) nicht als Kurve behandeln
                am_rand = abs(x_m - rahmen.x0) <= 2.0 * sf or abs(x_m - rahmen.x1) <= 2.0 * sf
                if am_rand and ((y_b - y_a) >= 0.70 * rahmen.height or len(l_items) <= 8):
                    continue
                if y_b >= rahmen.y0 - 2 * sf and y_a <= rahmen.y1 + 2 * sf:
                    ya_c, yb_c = max(y_a, rahmen.y0), min(y_b, rahmen.y1)
                    if rahmen.x0 - 3 * sf <= x_m <= rahmen.x1 + 10 * sf:
                        in_frame.append((x_m, ya_c, yb_c))
                    elif rahmen.x0 - 80 * sf <= x_m <= rahmen.x1 + 120 * sf:
                        excursion.append((x_m, ya_c, yb_c))
        v_segs.extend(in_frame)
        if len(in_frame) >= 2:
            v_segs.extend(excursion)

    if len(v_segs) < 3:
        return [], ""

    dts = [y_ax.a_y * (yb - ya) for _, ya, yb in v_segs if y_ax.a_y * (yb - ya) >= 0.04]
    if not dts:
        return [], ""

    # Grundschrittweite dz bestimmen (0,10 m bei marl/hausham/stress, 0,50 m bei synth_B)
    anteil_10cm = sum(0.07 <= dt <= 0.13 for dt in dts)
    if anteil_10cm >= max(2, 0.15 * len(dts)):
        dz = 0.10
    else:
        med_dt = statistics.median(dts)
        dz = min((0.10, 0.20, 0.25, 0.50), key=lambda k: abs(k - med_dt))
        if abs(dz - med_dt) > 0.05:
            dz = round(med_dt, 2)

    t_min_roh = min(y_ax.a_y * ya + y_ax.b_y for _, ya, _ in v_segs)
    t_max_roh = max(y_ax.a_y * yb + y_ax.b_y for _, _, yb in v_segs)
    t_start = max(0.0, round(round(t_min_roh / dz) * dz, 2))
    if 0.0 < t_start <= dz + 1e-4:
        t_start = 0.0
    t_ende = round(round(t_max_roh / dz) * dz, 2)
    if t_ende <= t_start:
        return [], ""

    n_schritte = int(round((t_ende - t_start) / dz))
    min_seg_h = 0.30 * dz / max(y_ax.a_y, 1e-6)

    schritte_out: list[list] = []
    for i in range(n_schritte):
        t_o = round(t_start + i * dz, 2)
        t_u = round(t_start + (i + 1) * dz, 2)
        t_mitte = (t_o + t_u) / 2.0
        y_mitte = (t_mitte - y_ax.b_y) / y_ax.a_y
        kands = [
            (yb - ya, x_m)
            for x_m, ya, yb in v_segs
            if ya - 0.5 * sf <= y_mitte <= yb + 0.5 * sf and (yb - ya) >= min_seg_h
        ]
        if not kands:
            continue
        # Bei exakt ueberlappenden Segmenten das groessere / eindeutige Segment nehmen
        kands.sort(key=lambda e: e[0], reverse=True)
        x_wahl = kands[0][1]
        val_roh = x_ax.a_x * x_wahl + x_ax.b_x
        if -0.4 <= val_roh < 0.0:
            val_roh = 0.0
        schritte_out.append([t_o, t_u, int(round(val_roh))])

    return schritte_out, "vektor_treppe"


def _farbe_dist(c1: tuple[float, ...] | None, c2: tuple[float, ...] | None) -> float:
    if c1 is None or c2 is None or len(c1) != len(c2):
        return 9.9
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def _extrahiere_cpt_vektor(
    sd: _SeitenDaten,
    rahmen: pymupdf.Rect,
    x_achsen: list[_AchseX],
    y_ax: _AchseY,
) -> tuple[list[list], list[str], dict[str, tuple[str, float, float]]]:
    """Extrahiert Mehrkurven-CPT-Daten (q_c, f_s, R_f) und trennt Kurven nach Stil/Layer."""
    sf = sd.scale_f
    hinweise: list[str] = []
    innen = [
        d for d in sd.drawings
        if not (_rechteck(d) & pymupdf.Rect(
            rahmen.x0 - 4 * sf, rahmen.y0 - 4 * sf, rahmen.x1 + 4 * sf, rahmen.y1 + 4 * sf
        )).is_empty
        and not _ist_gitterlinie(d, rahmen, sf)
        and d.get("color") is not None
        and any(it[0] == "l" for it in d["items"])
    ]
    if not innen:
        return [], hinweise, {}

    # Legende oberhalb des Rahmens nach Linienmustern und Kanalnamen absuchen
    legende_stil: list[tuple[tuple, str]] = []
    for d in sd.drawings:
        r = pymupdf.Rect(d["rect"])
        if rahmen.y0 - 100 * sf <= r.y0 <= rahmen.y0 - 2 * sf and r.width <= 60 * sf and r.height <= 8 * sf:
            col = tuple(round(float(c), 2) for c in (d.get("color") or ()))
            dash = d.get("dashes") not in (None, "[] 0", "[] 0.0")
            w = round(float(d.get("width") or 0.0), 1)
            # Zugehoeriger Text rechts davon
            beschr = " ".join(
                t for tr, t in sd.zeilen
                if abs((tr.y0 + tr.y1) / 2.0 - (r.y0 + r.y1) / 2.0) <= 8 * sf
                and r.x1 - 5 * sf <= tr.x0 <= r.x1 + 120 * sf
            )
            if beschr:
                legende_stil.append(((col, dash, w), _falten_norm(beschr)))

    # Kurven gruppieren
    gruppen: dict[tuple, list[dict]] = defaultdict(list)
    for d in innen:
        if REGELN["cpt_kurven_trennen"]:
            col = tuple(round(float(c), 2) for c in (d.get("color") or ()))
            dash = d.get("dashes") not in (None, "[] 0", "[] 0.0")
            w = round(float(d.get("width") or 0.0), 1)
            layer = str(d.get("layer") or "")
            sig = (layer, col, dash, w)
        else:
            sig = ("alle",)
        gruppen[sig].append(d)

    def _kanal_name(txt: str) -> str | None:
        tl = txt.lower()
        if "q_c" in tl or "qc" in tl or "spitzenwiderstand" in tl:
            return "q_c"
        if "f_s" in tl or "fs" in tl or "mantelreibung" in tl:
            return "f_s"
        if "r_f" in tl or "rf" in tl or "reibungsverh" in tl:
            return "R_f"
        return None

    # Achsen Kanälen zuordnen
    ax_nach_kanal: dict[str, _AchseX] = {}
    for ax in x_achsen:
        kn = _kanal_name(ax.label_txt)
        if kn:
            ax_nach_kanal[kn] = ax
    if "q_c" not in ax_nach_kanal and x_achsen:
        # Primaerachse (bevorzugt oben)
        ax_nach_kanal["q_c"] = next((ax for ax in x_achsen if ax.band == "top"), x_achsen[0])
    if "f_s" not in ax_nach_kanal and len(x_achsen) >= 2:
        andere = [ax for ax in x_achsen if ax is not ax_nach_kanal.get("q_c")]
        if andere:
            ax_nach_kanal["f_s"] = andere[0]
    kanal_grenzen = {kn: (ax.skala, ax.val_min, ax.val_max) for kn, ax in ax_nach_kanal.items()}

    # Einzelsegmente je Gruppe sammeln (verhindert Bruecken ueber getrennte Zeichenpfade) und auf 0,20-m-Raster abtasten
    kurven_daten: dict[str, dict[float, float]] = defaultdict(dict)
    for sig, dliste in gruppen.items():
        segmente: list[tuple[tuple[float, float], tuple[float, float]]] = []
        alle_ys: list[float] = []
        for d in dliste:
            for it in d["items"]:
                if it[0] == "l":
                    a, b = it[1], it[2]
                    if abs(b.y - a.y) > 1e-4:
                        segmente.append(((a.x, a.y), (b.x, b.y)))
                        alle_ys.append(a.y)
                        alle_ys.append(b.y)
        if len(segmente) < 2 or not alle_ys:
            continue

        # Kanal bestimmen
        kanal: str | None = None
        if REGELN["cpt_kurven_trennen"]:
            layer, col, dash, w = sig
            kanal = _kanal_name(layer)
            if not kanal:
                for (l_col, l_dash, l_w), l_txt in legende_stil:
                    if _farbe_dist(col, l_col) < 0.15 and dash == l_dash and abs(w - l_w) <= 0.35:
                        kanal = _kanal_name(l_txt)
                        if kanal:
                            break
            if not kanal and len(ax_nach_kanal) >= 2:
                # Heuristik: durchgezogen / dicker -> q_c, gestrichelt / duenner -> f_s
                kanal = "f_s" if dash else "q_c"
        if not kanal:
            kanal = "q_c"

        ax = ax_nach_kanal.get(kanal) or ax_nach_kanal.get("q_c")
        if ax is None:
            continue

        t_lo = max(0.0, round(min(y_ax.a_y * y + y_ax.b_y for y in alle_ys) * 5.0) / 5.0)
        t_hi = round(max(y_ax.a_y * y + y_ax.b_y for y in alle_ys) * 5.0) / 5.0
        dz = 0.2
        n_steps = int(round((t_hi - t_lo) / dz)) + 1
        for i in range(n_steps):
            t_cur = round(t_lo + i * dz, 2)
            y_cur = (t_cur - y_ax.b_y) / y_ax.a_y
            xs_treffer: list[float] = []
            for (x1, y1), (x2, y2) in segmente:
                ymn, ymx = min(y1, y2), max(y1, y2)
                if ymn - 0.3 * sf <= y_cur <= ymx + 0.3 * sf:
                    frac = (y_cur - y1) / (y2 - y1)
                    frac = min(1.0, max(0.0, frac))
                    xs_treffer.append(x1 + frac * (x2 - x1))
            if not xs_treffer:
                continue
            x_val = xs_treffer[0] if REGELN["cpt_kurven_trennen"] else sum(xs_treffer) / len(xs_treffer)
            if ax.skala == "log10" and REGELN["cpt_log_achse"]:
                wert = round(10.0 ** (ax.a_x * x_val + ax.b_x), 3)
            else:
                wert = round(ax.a_x * x_val + ax.b_x, 3)
            # Bei nicht-getrennten Kurven bleiben mehrere Werte fuer dieselbe Tiefe uebrig -> letzter ueberschreibt
            kurven_daten[kanal][t_cur] = wert

    tiefen_alle = sorted({t for kd in kurven_daten.values() for t in kd})
    if not tiefen_alle:
        return [], hinweise, kanal_grenzen
    werte = [
        [
            t,
            kurven_daten.get("q_c", {}).get(t),
            kurven_daten.get("f_s", {}).get(t),
            kurven_daten.get("R_f", {}).get(t),
        ]
        for t in tiefen_alle
    ]
    return werte, hinweise, kanal_grenzen


def _zensierte_randwerte_anwenden(
    sd: _SeitenDaten,
    rahmen: pymupdf.Rect,
    x_ax: _AchseX,
    y_ax: _AchseY,
    werte: list[list],
) -> tuple[list[list], float | None, list[str], set[tuple[float, float]]]:
    """Erkennt zensierte Randwerte ('> 50', 'N10 > 50', '100/10cm', 'auf X cm') und Ueberlaufzahlen."""
    if not REGELN["zensierte_randwerte"] or not werte:
        return werte, None, [], set()

    sf = sd.scale_f
    hinweise: list[str] = []
    endtiefe_korr: float | None = None
    ueberlauf_tiefen: set[tuple[float, float]] = set()

    # 1) Rechte Randbeschriftung pro Schritt (Zeilen im Bereich [rahmen.x1 - 4, rahmen.x1 + 95])
    rand_zeilen: list[tuple[float, str]] = []
    for r, t in sd.zeilen:
        yc = (r.y0 + r.y1) / 2.0
        if rahmen.y0 - 4 * sf <= yc <= rahmen.y1 + 4 * sf and rahmen.x1 - 4 * sf <= r.x0 <= rahmen.x1 + 95 * sf:
            rand_zeilen.append((yc, _falten_norm(t)))

    for z in werte:
        t_o, t_u, v = z[0], z[1], z[2]
        if isinstance(v, dict):
            continue
        y_mid = (((t_o + t_u) / 2.0) - y_ax.b_y) / y_ax.a_y
        step_h_pt = max(4.0 * sf, (t_u - t_o) / max(y_ax.a_y, 1e-6))
        for yc, txt in rand_zeilen:
            if abs(yc - y_mid) > 0.65 * step_h_pt:
                continue
            m = ZENSIERT_MARGIN_RE.search(txt)
            if m and v >= 0.94 * x_ax.val_max:
                num = int(round(_f(m.group(1))))
                z[2] = {"wert": num, "zensiert": True}
                break
            # Reine Ueberlaufzahl (z. B. '44', '41' > 40, ohne 'X'/'XX'/'XXX')
            if re.fullmatch(r"\d{2,3}", txt):
                ov = int(txt)
                if ov > x_ax.val_max and v >= 0.94 * x_ax.val_max:
                    z[2] = ov
                    ueberlauf_tiefen.add((round(float(t_o), 3), round(float(t_u), 3)))
                    break

    # 2) Fussvermerke / Abbruch ('100 Schlaege auf X cm', '100/10cm', 'Sonde steht auf')
    fuss_txt = _falten_norm(
        " ".join(
            t for r, t in sd.zeilen
            if rahmen.y0 <= r.y0 <= rahmen.y1 + 90 * sf
            and rahmen.x0 - 80 * sf <= r.x1
            and r.x0 <= rahmen.x1 + 150 * sf
        )
    )
    m_auf = ABBRUCH_AUF_CM_RE.search(fuss_txt)
    if m_auf and werte:
        cap = int(m_auf.group(1))
        cm = int(m_auf.group(2))
        letzter = werte[-1]
        cur_val = letzter[2]["wert"] if isinstance(letzter[2], dict) else letzter[2]
        if cur_val >= 0.94 * cap and 1 <= cm <= 10:
            letzter[2] = {"wert": cap, "zensiert": True}
            if cm < 10:
                letzter[1] = round(letzter[0] + cm / 100.0, 2)
                endtiefe_korr = letzter[1]
                hinweise.append(f"Rammabbruch im letzten Schritt: {cap} Schlaege auf {cm} cm")

    elif ABBRUCH_100_RE.search(fuss_txt) and werte:
        letzter = werte[-1]
        cur_val = letzter[2]["wert"] if isinstance(letzter[2], dict) else letzter[2]
        if cur_val >= 0.94 * x_ax.val_max:
            letzter[2] = {"wert": int(round(x_ax.val_max)), "zensiert": True}
            hinweise.append("Rammabbruch am Achsenende (zensiert)")

    return werte, endtiefe_korr, hinweise, ueberlauf_tiefen


def _scan_dph_lesen(
    sd: _SeitenDaten,
    rahmen: pymupdf.Rect,
    x_ax: _AchseX,
    y_ax: _AchseY,
) -> tuple[list[list], float, list[str]]:
    """Konservative Raster-Extraktion fuer hohle 300-dpi-DPH-Balkenscans (oder leere Rueckgabe bei Unsicherheit)."""
    hinweise: list[str] = []
    # Pruefen der Scan-Qualitaetsgates wenn scan_konservativ aktiv
    dpi = adaptive_dpi(sd.page)
    f = 72.0 / dpi
    px_per_10cm = (0.10 / max(y_ax.a_y, 1e-6)) / f
    px_per_blow = (1.0 / max(abs(x_ax.a_x), 1e-6)) / f

    if REGELN["scan_konservativ"]:
        if len(x_ax.ticks) < 3 or len(y_ax.ticks) < 3:
            hinweise.append("Scan-Diagramm: unvollstaendige Achsenbeschriftung (< 3 Ticks) — keine Werte extrahiert.")
            return [], 0.35, hinweise
        if px_per_10cm < 12.0 or px_per_blow < 8.0:
            hinweise.append(
                f"Scan-Diagramm: zu geringe Aufloesung ({px_per_10cm:.1f} px/10 cm) — keine Werte extrahiert."
            )
            return [], 0.35, hinweise
        if y_ax.quelle == "nhn_lokal":
            versatz = y_ax.a_y * rahmen.y0 + y_ax.b_y
            if abs(versatz) > 0.04:
                hinweise.append(
                    f"Scan-Diagramm: lokale NHN-Hoehenachse nicht exakt auf Rahmenoberkante "
                    f"kalibriert (Versatz {versatz:+.2f} m) — keine Werte extrahiert."
                )
                return [], 0.35, hinweise

    try:
        pix = sd.page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    except (RuntimeError, ValueError) as exc:
        hinweise.append(f"Rasterbild konnte nicht gerendert werden: {exc}")
        return [], 0.30, hinweise
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
    h_img, w_img = img.shape

    x_zero_px = int(round(x_ax.x_zero / f))
    x_max_px = int(round((x_ax.val_max - x_ax.b_x) / x_ax.a_x / f))
    if x_max_px <= x_zero_px + 10:
        hinweise.append("Scan-Diagramm: ungueltige X-Achsen-Geometrie — keine Werte extrahiert.")
        return [], 0.35, hinweise

    y_top_px = max(0, int(round(rahmen.y0 / f)))
    y_bot_px = min(h_img - 1, int(round(rahmen.y1 / f)))
    t_bot_rahmen = y_ax.a_y * rahmen.y1 + y_ax.b_y
    t_end = round(max(0.0, t_bot_rahmen) * 10.0) / 10.0

    n_steps = int(round(t_end / 0.1))
    if n_steps < 5:
        return [], 0.35, ["Scan-Diagramm: zu geringe Sondiertiefe."]

    # Vertikale Gitterlinien (Vielfache von 10 Schlaegen) schraegungs-invariant lokal suchen
    g_nom: list[tuple[int, int]] = [
        (g, int(round((g - x_ax.b_x) / x_ax.a_x / f)))
        for g in range(0, int(round(x_ax.val_max)) + 1, 10)
    ]

    def _lokale_gitterlinien(y_mitte_p: int) -> list[tuple[int, int]]:
        wy0 = max(y_top_px, y_mitte_p - 140)
        wy1 = min(y_bot_px, y_mitte_p + 140)
        if wy1 <= wy0 + 20:
            return g_nom
        streifen = img[wy0:wy1, :] < 170
        out_g: list[tuple[int, int]] = []
        for g_val, gx_n in g_nom:
            x_lo = max(0, gx_n - 12)
            x_hi = min(w_img, gx_n + 13)
            if x_hi <= x_lo:
                out_g.append((g_val, gx_n))
                continue
            spalten_dicht = streifen[:, x_lo:x_hi].mean(axis=0)
            best_idx = int(np.argmax(spalten_dicht))
            if float(spalten_dicht[best_idx]) >= 0.65:
                out_g.append((g_val, x_lo + best_idx))
            else:
                out_g.append((g_val, gx_n))
        return out_g

    vor_schritte: list[dict] = []
    breiten_je_gitter: dict[int, list[int]] = defaultdict(list)

    for i in range(n_steps):
        t_o = round(i * 0.1, 2)
        t_u = round((i + 1) * 0.1, 2)
        y0_p = int(round(((t_o - y_ax.b_y) / y_ax.a_y) / f))
        y1_p = int(round(((t_u - y_ax.b_y) / y_ax.a_y) / f))
        if y1_p <= y_top_px + 2 or y0_p >= y_bot_px - 2:
            continue
        y0_p = max(y_top_px, y0_p)
        y1_p = min(y_bot_px, y1_p)
        if y1_p <= y0_p + 3:
            continue
        y_b1 = min(y1_p - 1, y_bot_px - 2)
        if y_b1 <= y0_p + 2:
            y_b1 = y1_p - 1
        loc_grids = _lokale_gitterlinien((y0_p + y1_p) // 2)
        xz_loc = next((gx for gv, gx in loc_grids if gv == 0), x_zero_px)
        xm_loc = next((gx for gv, gx in loc_grids if gv == int(round(x_ax.val_max))), x_max_px)
        band = img[y0_p + 2 : y_b1, max(0, xz_loc) : min(w_img, xm_loc + 6)]
        if band.size == 0:
            continue
        col_dark = (band < 170).mean(axis=0)

        # Hohle Balken: nur schmale rechte Kante dunkel (> 0.48) ausserhalb lokaler Gitterlinien
        kands_x: list[int] = []
        for cx in range(4, len(col_dark) - 2):
            gx = xz_loc + cx
            if any(abs(gx - gxp) <= 4 for _, gxp in loc_grids):
                continue
            if col_dark[cx] >= 0.48:
                kands_x.append(gx)

        g_breiten: dict[int, int] = {}
        for g_val, gx_loc in loc_grids:
            if 0 < g_val < int(round(x_ax.val_max)):
                gb = img[y0_p + 2 : y_b1, max(0, gx_loc - 8) : min(w_img, gx_loc + 9)] < 170
                bw = int((gb.mean(axis=0) >= 0.65).sum()) if gb.size else 0
                g_breiten[g_val] = bw
                if not any(abs(kx - gx_loc) <= 6 for kx in kands_x):
                    breiten_je_gitter[g_val].append(bw)

        vor_schritte.append(
            {
                "t_o": t_o,
                "t_u": t_u,
                "y0_p": y0_p,
                "y1_p": y1_p,
                "loc_grids": loc_grids,
                "xz_loc": xz_loc,
                "xm_loc": xm_loc,
                "col_dark": col_dark,
                "kands_x": kands_x,
                "g_breiten": g_breiten,
            }
        )

    # Basis-Strichbreite je leerer Innengitterlinie bestimmen (unteres Quartil)
    basis_gitter_w: dict[int, float] = {}
    for g_val, ws in breiten_je_gitter.items():
        if ws:
            basis_gitter_w[g_val] = float(np.percentile(ws, 25))

    def _horizontale_kante_ende(st: dict, prev_nonzero: bool) -> tuple[int | None, float]:
        """Prueft horizontale Balkengrenzen (nicht auf 0,5-m-Gitterlinien) ueber Gitterintervalle."""
        lg = st["loc_grids"]
        if len(lg) < 2:
            return None, 0.0

        def _covs_fuer_y(yk: int) -> list[float]:
            yk0, yk1 = max(0, yk - 4), min(h_img, yk + 5)
            if yk1 <= yk0:
                return []
            h_strip = (img[yk0:yk1, :] < 170).any(axis=0)
            covs: list[float] = []
            for (_, gx0), (_, gx1) in zip(lg[:-1], lg[1:]):
                a, b = max(0, gx0 + 4), min(w_img, gx1 - 4)
                covs.append(float(h_strip[a:b].mean()) if b > a else 0.0)
            return covs

        kand_ys: list[tuple[str, int]] = []
        bot_nicht_gitter = abs((st["t_u"] * 2.0) - round(st["t_u"] * 2.0)) >= 0.05
        if bot_nicht_gitter:
            kand_ys.append(("bot", st["y1_p"]))
        if abs((st["t_o"] * 2.0) - round(st["t_o"] * 2.0)) >= 0.05:
            kand_ys.append(("top", st["y0_p"]))
        if not kand_ys:
            kand_ys = [("bot", st["y1_p"]), ("top", st["y0_p"])]

        c_bot = _covs_fuer_y(st["y1_p"])
        best_ende: int | None = None
        max_cov0 = 0.0
        for kind, yk in kand_ys:
            covs = c_bot if yk == st["y1_p"] else _covs_fuer_y(yk)
            if covs:
                max_cov0 = max(max_cov0, covs[0])
            if kind == "top" and prev_nonzero:
                if not (bot_nicht_gitter and c_bot and c_bot[0] >= 0.55):
                    continue
            if covs and covs[0] >= 0.65:
                k_ende = 0
                while k_ende + 1 < len(covs) and covs[k_ende + 1] >= 0.60:
                    k_ende += 1
                if k_ende + 1 == len(covs) or covs[k_ende + 1] <= 0.35:
                    g_ziel = lg[k_ende + 1][0]
                    if best_ende is None or g_ziel > best_ende:
                        best_ende = g_ziel
        return best_ende, max_cov0

    schritte: list[list] = []
    unsicher_schritte = 0
    schraffur_treffer = 0
    nz_meta: list[tuple[int, int, bool, dict]] = []

    for st in vor_schritte:
        t_o, t_u = st["t_o"], st["t_u"]
        kands_x = st["kands_x"]
        xz_loc = st["xz_loc"]
        xm_loc = st["xm_loc"]
        col_dark = st["col_dark"]

        if kands_x:
            x_edge = max(kands_x)
            innen_band = col_dark[3 : max(4, (x_edge - xz_loc) - 3)]
            if len(innen_band) >= 6 and float((innen_band > 0.22).mean()) > 0.38:
                schraffur_treffer += 1
            x_korr = x_edge - (xz_loc - x_zero_px)
            n_val = max(0, int(round((x_ax.a_x * (x_korr * f) + x_ax.b_x))))
            schritte.append([t_o, t_u, n_val])
            if n_val > 0:
                clusters = 1 + sum(1 for a, b in zip(kands_x, kands_x[1:]) if b - a > 4)
                has_outline = False
                if x_edge > xz_loc + 8:
                    in_a, in_b = max(0, xz_loc + 3), min(w_img, x_edge - 2)
                    for yk in (st["y0_p"], st["y1_p"]):
                        yk0, yk1 = max(0, yk - 4), min(h_img, yk + 5)
                        if yk1 <= yk0 or in_b <= in_a:
                            continue
                        in_cov = float((img[yk0:yk1, in_a:in_b] < 170).any(axis=0).mean())
                        if in_cov >= 0.60:
                            if xm_loc - 5 > x_edge + 6:
                                out_a, out_b = max(0, x_edge + 5), min(w_img, xm_loc - 5)
                                out_cov = (
                                    float((img[yk0:yk1, out_a:out_b] < 170).any(axis=0).mean())
                                    if out_b > out_a else 0.0
                                )
                                if out_cov <= 0.40:
                                    has_outline = True
                                    break
                            else:
                                has_outline = True
                                break
                nz_meta.append((x_edge, clusters, has_outline, st))
            continue

        # 1) Verbreiterung der Innengitterlinie durch Balken-Aussenkante (unabhaengig von Nachbarschritten)
        g_gefunden: int | None = None
        verdickt = [
            gv
            for gv, bw in st["g_breiten"].items()
            if bw >= max(5, basis_gitter_w.get(gv, 4.0) + 1.0)
        ]
        if verdickt:
            g_gefunden = max(verdickt)

        # 2) Horizontale Balkengrenze endet genau auf einer vertikalen Gitterlinie (insb. Achsenmaximum)
        prev_nonzero = bool(schritte and schritte[-1][2] > 0)
        g_horiz, cov0 = _horizontale_kante_ende(st, prev_nonzero)
        if g_gefunden is None and g_horiz is not None:
            g_gefunden = g_horiz

        if g_gefunden is not None:
            schritte.append([t_o, t_u, g_gefunden])
            if g_gefunden > 0:
                xe_g = next((gx for gv, gx in st["loc_grids"] if gv == g_gefunden), xm_loc)
                nz_meta.append((xe_g, 1, True, st))
        elif cov0 <= 0.25:
            schritte.append([t_o, t_u, 0])
        else:
            unsicher_schritte += 1
            schritte.append([t_o, t_u, 0])

    if REGELN["scan_konservativ"]:
        if schraffur_treffer > max(3, int(0.15 * n_steps)):
            hinweise.append(
                "Scan-Diagramm: Schraffurmuster in Balken erschwert eindeutige Auswertung — keine Werte extrahiert."
            )
            return [], 0.35, hinweise
        if unsicher_schritte > max(2, int(0.05 * n_steps)):
            hinweise.append(
                f"Scan-Diagramm: {unsicher_schritte} Schritte auf Gitterlinien unsicher — keine Werte extrahiert."
            )
            return [], 0.35, hinweise
        if len(nz_meta) >= 3:
            outline_hits = sum(1 for _, _, ho, _ in nz_meta if ho)
            multi_hits = sum(1 for _, cl, _, _ in nz_meta if cl > 1)
            ng_trans_tot = 0
            ng_trans_ok = 0
            max_run = 1
            cur_run = 1
            for (xe_a, _, _, _), (xe_b, _, _, st_b) in zip(nz_meta, nz_meta[1:]):
                if abs(xe_b - xe_a) <= 3:
                    cur_run += 1
                    max_run = max(max_run, cur_run)
                else:
                    cur_run = 1
                if abs(xe_b - xe_a) >= 6:
                    yk = st_b["y0_p"]
                    yk0, yk1 = max(0, yk - 4), min(h_img, yk + 5)
                    if yk1 <= yk0:
                        continue
                    h_s = (img[yk0:yk1, :] < 170).any(axis=0)
                    x_hi = max(xe_a, xe_b)
                    xm_b = st_b["xm_loc"]
                    is_grid = False
                    if xm_b - 5 > x_hi + 6 and abs(st_b["t_o"] * 2.0 - round(st_b["t_o"] * 2.0)) < 0.06:
                        out_a, out_b = max(0, x_hi + 5), min(w_img, xm_b - 5)
                        if out_b > out_a and float(h_s[out_a:out_b].mean()) > 0.55:
                            is_grid = True
                    if is_grid:
                        continue
                    ng_trans_tot += 1
                    a_t = max(0, min(xe_a, xe_b) + 2)
                    b_t = min(w_img, max(xe_a, xe_b) - 2)
                    if b_t > a_t and float(h_s[a_t:b_t].mean()) >= 0.60:
                        ng_trans_ok += 1

            is_hollow = outline_hits >= max(3, int(0.45 * len(nz_meta)))
            is_stair = (
                ng_trans_tot >= 3
                and ng_trans_ok >= 0.65 * ng_trans_tot
                and multi_hits <= int(0.30 * len(nz_meta))
            )
            is_const = (
                ng_trans_tot < 3
                and multi_hits == 0
                and outline_hits >= 1
                and max_run >= 3
            )
            if not (is_hollow or is_stair or is_const):
                hinweise.append(
                    "Scan-Diagramm: keine geschlossene Balken- oder Treppenstruktur "
                    "(Rauschen/Artefakte) — keine Werte extrahiert."
                )
                return [], 0.35, hinweise

    while schritte and schritte[-1][2] == 0:
        schritte.pop()
    if not schritte:
        return [], 0.35, ["Scan-Diagramm: keine Balkenwerte gefunden — keine Werte extrahiert."]

    return schritte, 0.72, hinweise


def _extrahiere_diagramme(
    sd: _SeitenDaten,
    koepfe: list[_Kopf],
    nhn_global: tuple[float, float, float] | None,
) -> list[dict]:
    """Extrahiert Vektor- und Scan-Diagramme sowie Laengsschnitt-Sondierungen."""
    sf = sd.scale_f
    kand_rahmen = _kandidaten_rahmen(sd)
    ergebnisse: list[dict] = []
    abgedeckte_koepfe: set[int] = set()

    for rahmen, r_typ in kand_rahmen:
        # Bei achse_arithmetisch_und_rahmen=False laesst _kandidaten_rahmen auch ungerahmte Kurven zu
        x_achsen = _kalibriere_x_achsen(sd, rahmen)
        if not x_achsen:
            continue

        kopf = _naechster_kopf(koepfe, rahmen, sf)
        if _ist_bohrprofil_falle(sd, rahmen, x_achsen, kopf):
            continue

        if kopf is None:
            if REGELN["tiefe_nicht_bohrungscode"]:
                continue
            # Ablation tiefe_nicht_bohrungscode=False: Bohrprofil-Code / Platzhalter zulassen
            nahe_code = next(
                (t for r, t in sd.zeilen if BOHR_CODE_RE.match(_falten_norm(t)) and r.y0 <= rahmen.y0 + 10 * sf),
                "UNBEKANNT 1",
            )
            kopf = _Kopf(rahmen, nahe_code, "DPH", False, None)

        ansatz = kopf.ansatzhoehe
        if ansatz is None and sd.bohr_spalten:
            # In synthetischen Layouts mit direktem Bohrprofilbezug kann Ansatzhoehe am Nachbarprofil fehlen
            pass

        y_ax, y_hinweise = _kalibriere_y_achse(sd, rahmen, nhn_global, ansatz)
        if y_ax is None:
            continue

        if kopf in koepfe:
            abgedeckte_koepfe.add(koepfe.index(kopf))

        ist_laengsschnitt = (
            y_ax.quelle == "laengsschnitt_nhn"
            or r_typ == "l_achse"
            or _ist_laengsschnitt_seite(sd, koepfe)
        )
        form = "laengsschnitt" if ist_laengsschnitt else "diagramm"

        # Gescanntes Diagramm (auf Rasterseiten gibt es keine Vektor-Sondierungskurven)
        if sd.scanned:
            if kopf.art in CPT_ARTEN and REGELN["scan_konservativ"]:
                end_est = _y_achse_endtiefe(y_ax, rahmen)
                ergebnisse.append(
                    {
                        "code": kopf.code,
                        "art": kopf.art,
                        "seite": sd.seite_nr,
                        "form": form,
                        "werte": [],
                        "endtiefe": end_est,
                        "ansatzhoehe": ansatz,
                        "konfidenz": 0.35,
                        "hinweise": y_hinweise + [
                            "Raster-CPT/CPTu: Kurvenwerte wegen Mehrfachachsen, Schraffur und "
                            "geringer OCR-Achsensicherheit nicht extrahiert (konservative Scan-Regel)."
                        ],
                        "beleg": {
                            "seiten": [sd.seite_nr],
                            "auch_auf_seiten": [],
                            "bbox": [round(rahmen.x0, 1), round(rahmen.y0, 1),
                                     round(rahmen.x1, 1), round(rahmen.y1, 1)],
                            "methode": "raster_konservativ",
                            "achsen": {"x": len(x_achsen), "y_r2": round(y_ax.r2, 5)},
                        },
                        "quelle": sd.quelle,
                    }
                )
                continue

            werte_scan, konf_scan, scan_hinw = _scan_dph_lesen(sd, rahmen, x_achsen[0], y_ax)
            werte_scan, end_korr, zen_hinw, ueberlauf_scan = _zensierte_randwerte_anwenden(
                sd, rahmen, x_achsen[0], y_ax, werte_scan
            )
            endtiefe_s = end_korr or (
                werte_scan[-1][1] if werte_scan else _y_achse_endtiefe(y_ax, rahmen)
            )
            ergebnisse.append(
                {
                    "code": kopf.code,
                    "art": kopf.art,
                    "seite": sd.seite_nr,
                    "form": form,
                    "werte": werte_scan,
                    "endtiefe": endtiefe_s,
                    "ansatzhoehe": ansatz,
                    "konfidenz": round(konf_scan, 2),
                    "hinweise": y_hinweise + scan_hinw + zen_hinw,
                    "beleg": {
                        "seiten": [sd.seite_nr],
                        "auch_auf_seiten": [],
                        "bbox": [round(rahmen.x0, 1), round(rahmen.y0, 1),
                                 round(rahmen.x1, 1), round(rahmen.y1, 1)],
                        "methode": "raster_dph" if werte_scan else "raster_konservativ",
                        "achsen": {
                            "x_min": x_achsen[0].val_min,
                            "x_max": x_achsen[0].val_max,
                            "y_r2": round(y_ax.r2, 5),
                        },
                    },
                    "quelle": sd.quelle,
                    "_rand_ueberlauf": ueberlauf_scan,
                }
            )
            continue

        # Vektor-Diagramm: CPT vs DPH
        if kopf.art in CPT_ARTEN or len(x_achsen) >= 2:
            werte_cpt, cpt_hinw, kanal_grenzen = _extrahiere_cpt_vektor(sd, rahmen, x_achsen, y_ax)
            if not werte_cpt:
                continue
            ergebnisse.append(
                {
                    "code": kopf.code,
                    "art": kopf.art if kopf.art in CPT_ARTEN else "CPT",
                    "seite": sd.seite_nr,
                    "form": form,
                    "werte": werte_cpt,
                    "endtiefe": round(werte_cpt[-1][0], 2),
                    "ansatzhoehe": ansatz,
                    "konfidenz": 0.90 if not y_hinweise else 0.70,
                    "hinweise": y_hinweise + cpt_hinw,
                    "beleg": {
                        "seiten": [sd.seite_nr],
                        "auch_auf_seiten": [],
                        "bbox": [round(rahmen.x0, 1), round(rahmen.y0, 1),
                                 round(rahmen.x1, 1), round(rahmen.y1, 1)],
                        "methode": "vektor_cpt",
                        "achsen": {
                            "achsen_x": [(ax.band, ax.skala, ax.val_min, ax.val_max) for ax in x_achsen],
                            "kanaele": kanal_grenzen,
                            "y_r2": round(y_ax.r2, 5),
                        },
                    },
                    "quelle": sd.quelle,
                }
            )
            continue

        x_ax = x_achsen[0]
        werte_dph, methode = _extrahiere_dph_vektor(sd, rahmen, x_ax, y_ax)
        if not werte_dph:
            continue

        werte_dph, end_korr, zen_hinw, ueberlauf_dph = _zensierte_randwerte_anwenden(
            sd, rahmen, x_ax, y_ax, werte_dph
        )
        endtiefe = end_korr if end_korr is not None else werte_dph[-1][1]

        konf = 0.90 if not y_hinweise else 0.45
        if sd.quelle == "OCR":
            konf = max(0.25, konf - 0.15)

        ergebnisse.append(
            {
                "code": kopf.code,
                "art": kopf.art,
                "seite": sd.seite_nr,
                "form": form,
                "werte": werte_dph,
                "endtiefe": round(float(endtiefe), 3),
                "ansatzhoehe": ansatz,
                "konfidenz": round(konf, 2),
                "hinweise": y_hinweise + zen_hinw,
                "beleg": {
                    "seiten": [sd.seite_nr],
                    "auch_auf_seiten": [],
                    "bbox": [round(rahmen.x0, 1), round(rahmen.y0, 1),
                             round(rahmen.x1, 1), round(rahmen.y1, 1)],
                    "methode": methode,
                    "achsen": {
                        "x_min": x_ax.val_min,
                        "x_max": x_ax.val_max,
                        "y_quelle": y_ax.quelle,
                        "y_r2": round(y_ax.r2, 5),
                    },
                },
                "quelle": sd.quelle,
                "_rand_ueberlauf": ueberlauf_dph,
            }
        )

    # Konservativer Scan-Fallback fuer gescannte Diagrammkoepfe mit belegtem Tiefenlineal / CPT-Panels
    if sd.scanned and REGELN["scan_konservativ"]:
        seite_laengs = nhn_global is not None or _ist_laengsschnitt_seite(sd, koepfe)
        for idx, kopf in enumerate(koepfe):
            if idx in abgedeckte_koepfe:
                continue
            if any(_norm_code(e["code"]) == _norm_code(kopf.code) for e in ergebnisse):
                continue
            um_txt = _falten_norm(
                " ".join(
                    t for r, t in sd.zeilen
                    if r.x1 >= kopf.rect.x0 - 150 * sf and r.x0 <= kopf.rect.x1 + 250 * sf
                    and r.y0 >= kopf.rect.y0 - 30 * sf and r.y1 <= kopf.rect.y1 + 500 * sf
                )
            )
            hat_cpt_panel = kopf.art in CPT_ARTEN and bool(CPT_KONTEXT_RE.search(um_txt))
            # Lokales Tiefenlineal unterhalb des Kopfes pruefen (nach x1 gruppiert, schliesst Berichtsseiten aus)
            tiefe_spalten: dict[int, list[tuple[pymupdf.Rect, float]]] = defaultdict(list)
            for r, t, *_ in sd.words:
                if r.y0 < kopf.rect.y1 or r.y0 > kopf.rect.y1 + 650 * sf:
                    continue
                if not (kopf.rect.x0 - 100 * sf <= r.x0 <= kopf.rect.x1 + 140 * sf):
                    continue
                tok = str(t).strip().rstrip("m")
                if re.fullmatch(r"\d{1,2}[.,]\d{1,2}", tok):
                    try:
                        v = _f(tok)
                    except ValueError:
                        continue
                    if 0.0 <= v <= 100.0:
                        tiefe_spalten[round(r.x1 / (10.0 * sf))].append((pymupdf.Rect(r), v))
            end_est: float | None = None
            hat_lineal = False
            for grp in tiefe_spalten.values():
                if len(grp) < 3:
                    continue
                sauber_t = _beste_arith_unterfolge(grp, nur_steigend=True)
                t_vals = [v for _, v in sauber_t]
                if len(sauber_t) >= 4 and not _tiefenlineal_folge_ok(t_vals, tol_rel=0.08):
                    if _tiefenlineal_folge_ok(t_vals[1:], tol_rel=0.08):
                        sauber_t = sauber_t[1:]
                        t_vals = t_vals[1:]
                if len(sauber_t) >= 3 and _tiefenlineal_folge_ok(t_vals, tol_rel=0.08):
                    cand_end = round(max(t_vals), 2)
                    if end_est is None or len(sauber_t) > 3:
                        end_est = cand_end
                        hat_lineal = True

            if not (hat_cpt_panel or (hat_lineal and SOND_KONTEXT_RE.search(um_txt))):
                continue

            ergebnisse.append(
                {
                    "code": kopf.code,
                    "art": kopf.art,
                    "seite": sd.seite_nr,
                    "form": "laengsschnitt" if seite_laengs else "diagramm",
                    "werte": [],
                    "endtiefe": end_est,
                    "ansatzhoehe": kopf.ansatzhoehe,
                    "konfidenz": 0.35,
                    "hinweise": [
                        "Gescanntes Diagramm: Achsen/Kurven durch OCR/Aufloesung nicht sicher "
                        "auswertbar — keine Werte extrahiert (konservative Scan-Regel)."
                    ],
                    "beleg": {
                        "seiten": [sd.seite_nr],
                        "auch_auf_seiten": [],
                        "bbox": [round(kopf.rect.x0, 1), round(kopf.rect.y0, 1),
                                 round(kopf.rect.x1, 1), round(kopf.rect.y1, 1)],
                        "methode": "raster_konservativ",
                        "achsen": {},
                    },
                    "quelle": sd.quelle,
                }
            )

    return ergebnisse


def _endpruefung(
    sond: dict,
    seiten_daten: dict[int, _SeitenDaten],
    seiten_sond_anzahl: dict[int, int] | None = None,
) -> None:
    """Prueft Tiefenmonotonie, Achsgrenzen und benannte Endtiefe."""
    if not REGELN["endpruefung_monoton_und_achse"]:
        return
    werte = sond.get("werte") or []
    if not werte:
        return
    hinweise = sond.setdefault("hinweise", [])
    beleg = sond.get("beleg") or {}
    achsen = beleg.get("achsen") or {}

    # 1) Tiefenmonotonie
    art = str(sond.get("art") or "").upper()
    if art in DPH_ARTEN:
        sauber: list[list] = []
        letztes_u = -1e-6
        for z in werte:
            if len(z) < 3 or z[0] is None or z[1] is None:
                continue
            t_o, t_u = float(z[0]), float(z[1])
            if t_u <= t_o or t_o < letztes_u - 1e-4:
                hinweise.append(f"Nicht-monotone Tiefe bei {t_o:.2f}–{t_u:.2f} m bereinigt")
                continue
            sauber.append(z)
            letztes_u = t_u
        werte = sauber
    else:
        sauber = []
        letztes_t = -1e-6
        nicht_monoton_cpt = 0
        for z in werte:
            if len(z) < 2 or z[0] is None:
                continue
            t = float(z[0])
            if t <= letztes_t and sauber:
                nicht_monoton_cpt += 1
                continue
            sauber.append(z)
            letztes_t = t
        if nicht_monoton_cpt > 0:
            hinweise.append(f"{nicht_monoton_cpt} nicht-monotone CPT-Tiefenwerte bereinigt")
            sond["konfidenz"] = round(max(0.1, float(sond.get("konfidenz", 0.5)) - 0.10), 2)
        werte = sauber

    # 2) Achsgrenzen fuer unzensierte Werte
    if art in DPH_ARTEN and "x_max" in achsen:
        x_mn = float(achsen.get("x_min", 0.0))
        x_mx = float(achsen["x_max"])
        tol = max(1.0, 0.05 * max(x_mx - x_mn, 1.0))
        rand_ueberlauf = set(sond.get("_rand_ueberlauf") or ())
        gefiltert: list[list] = []
        ausserhalb = 0
        for z in werte:
            v = z[2]
            if isinstance(v, dict):
                gefiltert.append(z)
                continue
            fv = float(v)
            key_z = (round(float(z[0]), 3), round(float(z[1]), 3))
            if fv < min(0.0, x_mn) - tol or (fv > x_mx + tol and key_z not in rand_ueberlauf):
                ausserhalb += 1
                continue
            gefiltert.append(z)
        if ausserhalb:
            hinweise.append(f"{ausserhalb} unplausible Messwerte ausserhalb der Achsen verworfen")
            sond["konfidenz"] = round(max(0.1, float(sond.get("konfidenz", 0.5)) - 0.15), 2)
        werte = gefiltert
    elif art in CPT_ARTEN:
        kanaele = dict(achsen.get("kanaele") or {})
        if not kanaele and achsen.get("achsen_x"):
            ax_liste = list(achsen.get("achsen_x") or [])
            kanal_namen = ("q_c", "f_s", "R_f")
            for idx_ax, ax_info in enumerate(ax_liste[:3]):
                if len(ax_info) >= 4:
                    kanaele[kanal_namen[idx_ax]] = (ax_info[1], ax_info[2], ax_info[3])
        if kanaele:
            ausserhalb_cpt = 0
            gefiltert_cpt: list[list] = []
            kanal_idx = [("q_c", 1), ("f_s", 2), ("R_f", 3)]
            for z in werte:
                if len(z) < 2:
                    continue
                z_neu = list(z)
                for kn, idx_k in kanal_idx:
                    if idx_k >= len(z_neu) or z_neu[idx_k] is None or kn not in kanaele:
                        continue
                    val_k = z_neu[idx_k]
                    if isinstance(val_k, dict):
                        continue
                    skala_k, mn_k, mx_k = kanaele[kn]
                    mn_f, mx_f = float(mn_k), float(mx_k)
                    if mn_f > mx_f:
                        mn_f, mx_f = mx_f, mn_f
                    fv = float(val_k)
                    if skala_k == "log10":
                        lo_lim = min(mn_f * 0.8, mn_f - 0.05)
                        hi_lim = max(mx_f * 1.15, mx_f + 0.5)
                    else:
                        tol_c = max(0.05 * max(mx_f - mn_f, 1.0), 0.1)
                        lo_lim = mn_f - tol_c
                        hi_lim = mx_f + tol_c
                    if fv < lo_lim or fv > hi_lim:
                        z_neu[idx_k] = None
                        ausserhalb_cpt += 1
                if any(z_neu[idx_k] is not None for _, idx_k in kanal_idx if idx_k < len(z_neu)):
                    gefiltert_cpt.append(z_neu)
            if ausserhalb_cpt:
                hinweise.append(f"{ausserhalb_cpt} unplausible CPT-Messwerte ausserhalb der Achsen verworfen")
                sond["konfidenz"] = round(max(0.1, float(sond.get("konfidenz", 0.5)) - 0.15), 2)
            werte = gefiltert_cpt

    sond["werte"] = werte
    if not werte:
        return

    # 3) Abgleich mit gedruckter Endtiefe-Angabe auf beitragenden Seiten (bbox-bezogen)
    letzte_tiefe = float(werte[-1][1] if art in DPH_ARTEN else werte[-1][0])
    sond["endtiefe"] = round(letzte_tiefe, 3)
    seiten = list(beleg.get("seiten") or [sond.get("seite")])
    seiten_bboxes = beleg.get("_seiten_bboxes") or {}
    for s_nr in reversed(seiten):
        sd = seiten_daten.get(s_nr)
        if sd is None:
            continue
        sf = sd.scale_f
        bbox_s = seiten_bboxes.get(s_nr) or beleg.get("bbox")
        phrasen_s = _lokale_phrasen(sd.words, sf)
        nah_treffer: list[tuple[float, float]] = []
        weit_treffer: list[float] = []
        for r_p, t_p in phrasen_s:
            tf = _falten_norm(t_p)
            if ABBRUCH_AUF_CM_RE.search(tf):
                continue
            m = ENDTIEFE_RE.search(tf)
            if not m:
                continue
            lbl_end = _f(m.group(1))
            if bbox_s and len(bbox_s) == 4:
                bx0, by0, bx1, by1 = [float(c) for c in bbox_s]
                if (
                    bx0 - 80 * sf <= r_p.x1
                    and r_p.x0 <= bx1 + 120 * sf
                    and by0 - 110 * sf <= r_p.y1
                    and r_p.y0 <= by1 + 60 * sf
                ):
                    cx_b, cy_b = (bx0 + bx1) / 2.0, (by0 + by1) / 2.0
                    cx_p, cy_p = (r_p.x0 + r_p.x1) / 2.0, (r_p.y0 + r_p.y1) / 2.0
                    nah_treffer.append((abs(cx_p - cx_b) + abs(cy_p - cy_b), lbl_end))
                    continue
            weit_treffer.append(lbl_end)

        gewaehlt: float | None = None
        if nah_treffer:
            nah_treffer.sort(key=lambda e: e[0])
            gewaehlt = nah_treffer[0][1]
        elif weit_treffer and (seiten_sond_anzahl is None or seiten_sond_anzahl.get(int(s_nr), 1) <= 1):
            gewaehlt = weit_treffer[0]

        if gewaehlt is not None:
            if abs(gewaehlt - letzte_tiefe) > 0.06:
                hinweise.append(
                    f"Endtiefe laut Kurve ({letzte_tiefe:.2f} m) weicht von Angabe ({gewaehlt:.2f} m) ab"
                )
                sond["konfidenz"] = round(max(0.1, float(sond.get("konfidenz", 0.5)) - 0.10), 2)
            break


def _zusammenfuehren(
    roh_liste: list[dict],
    seiten_daten: dict[int, _SeitenDaten],
    dateiname: str,
) -> list[dict]:
    """Fuehrt mehrseitige Sondierungen zusammen und dedupliziert gleiche Seite / Laengsschnitt."""
    # 1) Gleiche Seite: Tabelle vor Diagramm (z. B. triefenstein_bp41)
    nach_seite_code: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for s in roh_liste:
        nach_seite_code[(int(s["seite"]), _norm_code(s["code"]))].append(s)

    seite_bereinigt: list[dict] = []
    for (_, _), gruppe in nach_seite_code.items():
        if len(gruppe) == 1:
            seite_bereinigt.append(gruppe[0])
            continue
        # Bevorzuge nicht-leere Tabelle > nicht-leeres Diagramm > rest
        prio = {"tabelle": 3, "diagramm": 2, "laengsschnitt": 1}
        gruppe.sort(key=lambda e: (bool(e.get("werte")), prio.get(e.get("form", ""), 0)), reverse=True)
        haupt = gruppe[0]
        for neben in gruppe[1:]:
            if haupt.get("werte") and neben.get("werte"):
                n_h = len(haupt["werte"])
                n_n = len(neben["werte"])
                if abs(n_h - n_n) > 2:
                    haupt.setdefault("hinweise", []).append(
                        f"Abgleich Tabelle/Diagramm: Schrittanzahl weicht ab ({n_h} vs {n_n})"
                    )
            if haupt.get("ansatzhoehe") is None and neben.get("ansatzhoehe") is not None:
                haupt["ansatzhoehe"] = neben["ansatzhoehe"]
        seite_bereinigt.append(haupt)

    seiten_sond_anzahl: dict[int, int] = defaultdict(int)
    for s in seite_bereinigt:
        for s_nr in (s.get("beleg") or {}).get("seiten") or [s.get("seite")]:
            if s_nr is not None:
                seiten_sond_anzahl[int(s_nr)] += 1

    # 2) Mehrseitige Fortsetzungen verbinden (s06_zweiseitig)
    if REGELN["mehrseitig_verbinden"]:
        nach_code: dict[str, list[dict]] = defaultdict(list)
        for s in seite_bereinigt:
            nach_code[_norm_code(s["code"])].append(s)
        nach_fortsetzung: list[dict] = []
        for _, grp in nach_code.items():
            grp.sort(key=lambda e: int(e["seite"]))
            if len(grp) == 1:
                nach_fortsetzung.append(grp[0])
                continue
            # Einzelblatt-Diagramme gleicher Sondierung verbinden wenn Tiefen fortlaufen
            aktive_kette = [grp[0]]
            for cand in grp[1:]:
                vor = aktive_kette[-1]
                if (
                    vor["form"] == cand["form"] == "diagramm"
                    and vor.get("werte")
                    and cand.get("werte")
                    and cand["seite"] > vor["seite"]
                ):
                    vor_end = float(vor["werte"][-1][1] if vor["art"] in DPH_ARTEN else vor["werte"][-1][0])
                    cand_start = float(cand["werte"][0][0])
                    if cand_start >= vor_end - 0.15:
                        vor["werte"] = vor["werte"] + cand["werte"]
                        vor["endtiefe"] = cand.get("endtiefe") or vor.get("endtiefe")
                        vor["beleg"]["seiten"] = sorted(
                            set(vor["beleg"].get("seiten", [vor["seite"]]) + [cand["seite"]])
                        )
                        vor["_rand_ueberlauf"] = (
                            set(vor.get("_rand_ueberlauf") or ())
                            | set(cand.get("_rand_ueberlauf") or ())
                        )
                        sb = dict(vor["beleg"].get("_seiten_bboxes") or {vor["seite"]: vor["beleg"].get("bbox")})
                        sb[cand["seite"]] = cand["beleg"].get("bbox")
                        vor["beleg"]["_seiten_bboxes"] = sb
                        vor["hinweise"] = list(dict.fromkeys(vor.get("hinweise", []) + cand.get("hinweise", [])))
                        continue
                aktive_kette.append(cand)
            nach_fortsetzung.extend(aktive_kette)
    else:
        nach_fortsetzung = seite_bereinigt

    # 3) Standalone vs Laengsschnitt deduplizieren (marl_251 S.6 vs S.22-27, rednitzhembach S.35 vs S.31-34)
    if REGELN["laengsschnitt_hoehenmassstab"]:
        nach_code_final: dict[str, list[dict]] = defaultdict(list)
        for s in nach_fortsetzung:
            nach_code_final[_norm_code(s["code"])].append(s)

        ausgabe: list[dict] = []
        for _, grp in nach_code_final.items():
            if len(grp) == 1:
                ausgabe.append(grp[0])
                continue
            standalone = [e for e in grp if e["form"] in ("tabelle", "diagramm")]
            laengs = [e for e in grp if e["form"] == "laengsschnitt"]
            if standalone and laengs:
                haupt = max(standalone, key=lambda e: (bool(e.get("werte")), len(e.get("werte") or [])))
                extra_seiten = sorted({int(e["seite"]) for e in laengs if e["seite"] != haupt["seite"]})
                haupt["beleg"]["auch_auf_seiten"] = sorted(
                    set(haupt["beleg"].get("auch_auf_seiten", []) + extra_seiten)
                )
                if haupt.get("ansatzhoehe") is None:
                    for e in laengs:
                        if e.get("ansatzhoehe") is not None:
                            haupt["ansatzhoehe"] = e["ansatzhoehe"]
                            break
                ausgabe.append(haupt)
            else:
                ausgabe.extend(grp)
    else:
        ausgabe = nach_fortsetzung

    for s in ausgabe:
        s["beleg"]["datei"] = dateiname
        s["hinweise"] = list(dict.fromkeys(s.get("hinweise") or []))
        _endpruefung(s, seiten_daten, seiten_sond_anzahl)
        s.pop("_rand_ueberlauf", None)
        if isinstance(s.get("beleg"), dict):
            s["beleg"].pop("_seiten_bboxes", None)

    ausgabe.sort(key=lambda s: (int(s["seite"]), str(s["code"])))
    return ausgabe


def lesen(pdf: Path | str, doc=None, ocr: bool = True) -> list[dict]:
    """Liest alle Sondierungen (DPH/DPL/DPM/DPSH/SRS und CPT/CPTu) aus einem PDF.

    Uebergebenes ``doc`` (pymupdf.Document) bleibt geoeffnet; ein selbst geoeffnetes
    Dokument wird im ``finally``-Block sauber geschlossen.
    """
    pfad = Path(pdf)
    eigenes_doc = doc is None
    if eigenes_doc:
        doc = pymupdf.open(pfad)

    roh_liste: list[dict] = []
    seiten_daten: dict[int, _SeitenDaten] = {}
    try:
        for pno, page in enumerate(doc):
            sd = _seiten_primitive(page, pno + 1, ocr=ocr)
            seiten_daten[sd.seite_nr] = sd
            koepfe = _finde_koepfe(sd)
            nhn_global = _laengsschnitt_nhn_regression(sd, koepfe)

            tab_sond = _extrahiere_tabellen(sd, koepfe)
            diag_sond = _extrahiere_diagramme(sd, koepfe, nhn_global)
            roh_liste.extend(tab_sond)
            roh_liste.extend(diag_sond)

        return _zusammenfuehren(roh_liste, seiten_daten, pfad.name)
    finally:
        if eigenes_doc:
            doc.close()
