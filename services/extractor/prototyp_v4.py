"""Prototyp v4: Extraktion nach der Spezifikation docs/17_extraction_algorithm.md.

Stufen (je Seite, dann je Dokument):
  E0  Seitenklasse: vektor | vektor_ohne_text (AutoCAD-SHX) | raster (Bild ohne Text) | raster_ocr (Scan)
  E1  Primitive: Woerter (Textlage oder OCR) und Segmente (Vektor oder Bild), in Ansichtskoordinaten
  E2  Koepfe: Kuerzel mit Zusatz ('RKS 1 - Weg'), 'Bohrung <Code>' auch zweizeilig, Fremdcodes
  E3  Saeulen: Paare senkrechter Kanten, Grenzen = durchgehende Waagrechte ueber die volle Breite
  E4  Tiefen: Labelgruppen (ohne Achsen, Probenpaare, Tabellen), Massstab = Kandidat mit den
      meisten bestaetigten Labels (direkt / Reihenfolge / Massstabstext)
  E5  Schichten: 1:1-Bestaetigung je Grenze; unbestaetigte Grenze mit gleicher Schraffur
      ober- und unterhalb ist eine Schraffurlinie (Doppellinie Schwarzdecke)
  E6  Bodenart: Substantiv -> Fels/Anthropogen -> DIN-/ISO-Kuerzel; Originaltext bleibt erhalten
  E7  Grundwasser: Symbol + Wasserlinie, 'GW 2.53m', 'Wasseranschnitt 3.8', 'kein Wasser' als Befund
  E8  Zweitquellen: Schichtenverzeichnis (DIN 4022), Koordinatentabelle, Rechts-/Hochwert im Text
  E9  Zusammenfuehren: Duplikate, Abgleich Profil <-> SV, Konfidenz, kanonisches JSON (Arquitectura §5.1)

Jede Regel aus docs/16 ist in RULES einzeln abschaltbar (Ablation: regression.py --disable).
Stand: Trainingszahlen; die einzige ehrliche Zahl ist die naechste Blindrunde (docs/15).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prototyp_v2 import (DATE_RE, GOK_RE, PT_TO_M_AT_1_1, classify_hatch, coordinate_table,  # noqa: E402
                         hatch_features, soil, soundings)

ID_RE = re.compile(r"^(B|BK|KB|KRB|RKS|BS|GWM|SCH)\s*(\d+[a-z]?)(/\d{2})?$")
HEAD_RE = re.compile(r"^((?:B|BK|KB|KRB|RKS|BS|GWM|SCH)\s*\d+[a-z]?(?:/\d{2})?)(?:\s*[-–:]\s*[A-Za-zÄÖÜäöü0-9].*)?$")
# Code mit Station (Strecken): 'B-5+365-G', 'SB-0+550-N3', 'SB-7+700-N11,5' (#54)
STATION_HEAD_RE = re.compile(r"^((?:B|BK|KB|KRB|RKS|BS|SB|GWM|SCH)-\d{1,3}\+\d{3}(?:-[A-Z][A-Za-z0-9,]{0,6})?)$")
GOK_UE_NN_RE = re.compile(r"([+-]?\d{1,4}[.,]\d{1,2})\s*m\s*(?:ü|ue)\.?\s*(?:NN|NHN)\b", re.I)
GOK_ALLEIN_RE = re.compile(r"^([+-]?\d{1,4}[.,]\d{2})\s*m$")
SCHRIFTFELD_RE = re.compile(r"(?:Projekt|Auftrag|Akten|Bericht|Zeichnungs|Plan|Anlagen?)\s*-?\s*(?:Nr|Nummer)\.?\s*:?\s*$", re.I)
DEPTH_RE = re.compile(r"^\d{1,3}[.,]\d{1,2}\s?m?$")              # DC-Software: '0.20m'
GW_TEXT_RE = re.compile(r"(?<![A-Za-z])GW(?![A-Za-z]).*?(\d{1,3}[.,]\d{1,2})\s?m(?![A-Za-z])|(\d{1,3}[.,]\d{1,2})\s?m\s*u\.?\s*GOK", re.I)
SCALE_RE = re.compile(r"(?:M(?:a(?:ss|ß)stab)?\.?|H(?:ö|oe)hen-?Ma(?:ss|ß)stab)?\s*1\s*:\s*(\d{2,4})\b")
NO_GW_RE = re.compile(r"kein(?:e)?\s*(?:Grund)?wasser|GW\s*nicht\s*angetroffen|trocken", re.I)   # OCR verliert Leerzeichen
ROCK_SUFFIX = ("stein", "fels")
ANTHROPOGEN = {"beton": "Beton", "asphalt": "Asphalt", "schwarzdecke": "Schwarzdecke",
               "pflaster": "Pflaster", "anschuettung": "Auffuellung", "anschüttung": "Auffuellung",
               "auffuellung": "Auffuellung", "auffüllung": "Auffuellung", "schotter": "Auffuellung",
               "auffullung": "Auffuellung", "anschuttung": "Auffuellung"}     # OCR ohne Umlaut (E6)
TOPSOIL = {"oberboden", "mutterboden", "humus"}
# Hauptbodenart als Kuerzel am Anfang der Beschreibung (DIN 4023 bzw. EN ISO 14688)
ABBR_RE = re.compile(r"^\s*(Mu|Mg|Gr|Sa|Si|Cl|Co|A|[fmg]?S|[fmg]?G|U|T|X|H|F)(?=[\s,(?´'*]|$)")
ABBR = {"Mu": "Mutterboden", "Mg": "Auffuellung", "A": "Auffuellung", "Gr": "Kies", "G": "Kies",
        "Sa": "Sand", "S": "Sand", "Si": "Schluff", "U": "Schluff", "Cl": "Ton", "T": "Ton",
        "Co": "Steine", "X": "Steine", "H": "Torf", "F": "Mudde"}
STANDARD_SCALES = (10, 20, 25, 33, 50, 75, 100, 125, 150, 200, 250, 500, 1000)

# Regeln aus docs/16 (Lektion in Klammern); False = fuer Ablationen abgeschaltet
RULES = {
    "rotation": True,            # L2   Ansichtskoordinaten bei /Rotate
    "dashed_exclusion": True,    # G2   gestrichelte Waagrechte sind Schraffur
    "table_filter": True,        # G4   Zahlen in der Saeule = Tabelle
    "nonstandard_scale": True,   # L9   Nicht-Normmassstab bei starker Bestaetigung
    "head_suffix": True,         # L13  'RKS 1 - Betonweg 0+050'
    "generic_heads": True,       # T1   'Bohrung 422C-460', Archivcodes 'S 2a'
    "axis_filter": True,         # L14  arithmetische Folgen sind Achsen
    "paired_filter": True,       # L15  Probenspalte Von/Bis
    "labelless_column": True,    # L15b Saeule ohne Labels neben Saeulen mit Labels
    "top_convention": True,      # L3   Labels an der Oberkante (mit 0,00)
    "abbreviations": True,       # L16  DIN-4023-/ISO-Kuerzel
    "gw_symbol_filter": True,    # L10  Leisten-, Koten- und GOK-Dreiecke sind kein Wasser
    "gw_text": True,             # L10b 'GW 2.53m'
    "gw_description": True,      # L10b 'Wasseranschnitt 3.8' in der Schichtbeschreibung
    "gw_art": True,              # #26  Art und Datum je Stand aus dem Text am Symbol / im SV; Staende im Berichtstext
    "gw_legende": True,          # W3   Symbole der Legende: V (zwei Striche) als Stand, Art je Form (voll / V)
    "dup_preference": True,      # L12  Einzelblatt/Titel vor Schnitt
    "sv_source": True,           # S1   Schichtenverzeichnis als Zweitquelle
    "ocr": True,                 # L17/L18 OCR fuer Seiten ohne Textlage
    "coords_text": True,         # S5   Rechts-/Hochwert im Text
    "hatch_continuity": True,    # L6   Doppellinie innerhalb einer Schicht
    "label_snap": True,          # T2   bestaetigte Grenze = gedruckter Labelwert
    "scan_with_vectors": True,   # E2   Scan mit OCR-Textlage trotz Vektorrauschen
    "single_sheet_anchor": True, # T3   ein Kopf + ein Profil auf der Seite gehoeren zusammen
    "depth_table": True,         # S6   Schichtenliste als Texttabelle (Tiefe | Beschreibung)
    "ocr_supplement": True,      # L18b eigene OCR ergaenzt eine luckenhafte OCR-Textlage
    "label_first": True,         # T4   Labels bilden eine saubere Gerade, Linien nicht: Labels sind die Daten
    "ocr_decimal_fix": True,     # R1   '0950' -> 9,50 (OCR ohne Komma)
    "scale_contradiction": True, # E5   Massstabstext ohne Bestaetigung durch vorhandene Labels: keine Grenzen
    "raster_gw_symbol": True,    # W4   GW-Symbol im Scan: Vorlagenabgleich an waagrechten Linien + Formpruefung
    "raster_gw_legende": True,   # W4   Legende im Scan lesen (kleine Symbole links vom Wassertext, fuer Dach + Art)
    "raster_massstab_ocr": True, # E5   Tiefenmassstab im Scan aus OCR-Tiefenlineal/Hoehenleiste oder M 1:n + Ansatzhoehe
    "sv_wasser": True,           # W5   Wasserstaende im Schichtenverzeichnis spaltenweise mit Art, Datum und Beleg lesen
    "line_reading_order": True,  # E9   Woerter einer Zeile in Leserichtung (word_no/Achse), nicht nach y0 (#49)
    "ls_wasserlinien": True,     # W6   Wasserlinien (HGW/MGW/Bemessungswasserstand/GW <Datum>) im Laengsschnitt (#26 2b)
    "kein_schriftfeld_code": True,  # T6 Nummer im Schriftfeld ('Projekt-Nr.: B 231411', > 4 Ziffern) ist kein Code (#54)
    "station_heads": True,       # T7   Code mit Station 'B-5+365-G', 'SB-0+550-N3' (#54)
    "gok_unter_kopf": True,      # T8   Ansatzhoehe '216.31 m' allein zwischen Kopf und Saeule (#54)
    "doppel_labels": True,       # T9   Grenzen mit Label 'Tiefe (Hoehe)': Linie ohne Label ist keine Grenze (#54)
    "top_null_gedruckt": True,   # T10  ohne gedrucktes 0,00: Text direkt ueber dem Label = Unterkanten-Konvention (#54)
    "doppel_anderer_code": True, # T11  gleiche GOK + Grenzen unter anderem Code = dieselbe Bohrung (#54)
    "gw_label_text": True,       # W7b  Label 'GW 0.94m' (auch schwarz) mit Datum gilt, nicht das Symbol (#54)
    "gw_blaue_labels": True,     # W7   blaues Wasserlabel '3.10 (213.21)' + Datum gilt, nicht das Dreieck (#54)
}

CODE_TOKEN = r"[A-Z0-9][A-Za-z0-9]*(?:[-/.][A-Za-z0-9]+)*"
GENERIC_HEAD_RE = re.compile(r"^(?:Bohrung|[A-ZÄÖÜ][a-zäöü]*bohrung|Bohrprofil|Aufschluss|Rammkernsondierung)"
                             r"\s*(?:Nr\.?)?\s*:?\s*(.{0,20}?)\s*$")
FREE_CODE_RE = re.compile(r"[A-Z0-9][A-Z0-9 ./\-]{0,14}?[a-z]?")             # 'SST KB 5', 'RB 2 / I', '422C-460'
GOK_EXTRA_RE = re.compile(r"(?:H(?:ö|oe)he|Kote|Ansatzh(?:ö|oe)he|Gel(?:ä|ae)ndeh(?:ö|oe)he|Bezugspunkt)[^\d\n]{0,30}?"
                          r"([+-]?\d{1,4}[.,]\d{1,2})|(\d{1,4}[.,]\d{1,2})\s*m\s*(?:ü|ue)\.?\s*(?:M\.|NN|NHN)", re.I)
LV_COORD_RE = re.compile(r"Koordinaten\D{0,5}?(\d['’ ]?\d{3}\s?\d{3}(?:[.,]\d+)?|\d{3}\s?\d{3}(?:[.,]\d+)?)\s*/\s*"
                         r"(\d['’ ]?\d{3}\s?\d{3}(?:[.,]\d+)?|\d{3}\s?\d{3}(?:[.,]\d+)?)")
ARCHIVE_HEAD_RE = re.compile(r"^(S\s*\d+[a-z]?)$")            # Archivbohrungen 'S 1', 'S2a'
# Art und Datum eines Wasserstands (Issue #26) aus dem Text daneben; ohne Stichwort bleibt die Art "unbestimmt"
# (nie geraten). Reihenfolge zaehlt: "Grundwasser angestiegen" ist Ruhewasser, "Schichtenwasser angetroffen" ist
# Schichtenwasser. Gleiche Regeln wie baugrundmodell.wasser.
GW_ART = (("Schichtenwasser", re.compile(r"schichtenwasser|stauwasser|sickerwasser", re.I)),
          ("Bohrende", re.compile(r"bohrende", re.I)),
          ("Ruhewasser", re.compile(r"ruhe\s*wasser|angestiegen", re.I)),
          ("angetroffen", re.compile(r"angetroffen|angebohrt|anschnitt|wasserzutritt", re.I)))
GW_DATUM_RE = re.compile(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.(\d{4}|\d{2})(?![\d.])")
# Staende im Text des Gutachtens, keine Staende einer Bohrung: Bemessungswasserstand, (ze)HGW, MHGW, MGW
WSP_TEXT_RE = re.compile(r"(Bemessungs(?:grund)?wasserstand|zeHGW|HHGW|MHGW|HGW|MGW|MNGW)\b([^0-9]{0,60}?)"
                         r"\+?\s?(\d{1,4}[.,]\d{1,2})\s*m\s*(?:ü\.?\s*)?NHN", re.I)
# Beschriftung einer Wasserlinie im Laengsschnitt (Issue #26 Teil 2b)
WSP_LINIE_RE = re.compile(
    r"\b(Bemessungs(?:grund)?wasserstand|Bauwasserstand|zeHGW|HHGW|MHGW|HGW|MGW|MNGW)\b"
    r"|\bGW\s*(?:am\s*)?(\d{1,2}\.\d{1,2}\.\d{2,4})\b",
    re.I,
)
STATION_RE = re.compile(r"^(?:km\s*)?(\d{1,2})\+(\d{3}(?:[.,]\d{1,3})?)$", re.I)
WATER_DESC_RE = re.compile(r"Wasser(?:anschnitt|stand|spiegel|zutritt)\s*(?:bei|in|:)?\s*(\d{1,2}[.,]\d{1,2})", re.I)
COORD_E_RE = re.compile(r"(?:Rechtswert|Ostwert|Easting|\bRW\b)(?:\D|UTM\d{2}N?){0,30}?(\d{6,8}(?:[.,]\d+)?)", re.I)
COORD_N_RE = re.compile(r"(?:Hochwert|Nordwert|Northing|\bHW\b)(?:\D|UTM\d{2}N?){0,30}?(\d{7}(?:[.,]\d+)?)", re.I)
UTM_ZONE_RE = re.compile(r"UTM\s*(3[23])", re.I)


def ckey(code: str) -> str:
    """Vergleichsschluessel fuer Codes: OCR schreibt 'B 1' mal als 'B1' (E6)."""
    return re.sub(r"\s+", "", code).upper()


def plausible_scale(m: float, tol: float = 0.04) -> bool:
    """Zeichnungen verwenden Normmassstaebe; M 1:12 aus einer Tabelle ist ein Fehlalarm."""
    return any(abs(m - s) <= tol * s for s in STANDARD_SCALES)


# ---------------------------------------------------------------------------
# Primitive in Ansichtskoordinaten
# ---------------------------------------------------------------------------
@dataclass
class Seg:
    x0: float
    y0: float
    x1: float
    y1: float
    width: float
    stroked: bool
    dashed: bool = False

    @property
    def horizontal(self) -> bool:
        return abs(self.y1 - self.y0) < 0.3

    @property
    def vertical(self) -> bool:
        return abs(self.x1 - self.x0) < 0.3


def _xform_drawing(d: dict, m: pymupdf.Matrix) -> dict:
    items = []
    for it in d["items"]:
        op = it[0]
        if op == "re":
            items.append(("re", pymupdf.Rect(it[1]) * m))
        elif op == "qu":
            items.append(("qu", pymupdf.Quad(it[1]) * m))
        else:
            items.append((op, *[p * m if hasattr(p, "x") else p for p in it[1:]]))
    return {**d, "items": items, "rect": pymupdf.Rect(d["rect"]) * m}


def adaptive_dpi(page: pymupdf.Page) -> int:
    """~3300 px lange Seite, 200-300 dpi: verkleinerte Seiten werden schaerfer gerendert."""
    return int(min(300, max(200, 3300 / (max(page.rect.width, page.rect.height) / 72))))


def raster_segments(page: pymupdf.Page, dpi: int | None = None) -> list[Seg]:
    """Gescannte Seite: waagrechte/senkrechte Linien per Morphologie aus dem Bild (wie swissgeol strip logs).

    Liefert dieselben Seg-Objekte wie der Vektorweg, damit Saeulen-/Grenzlogik unveraendert bleibt.
    """
    try:
        import cv2
    except ImportError:                                  # optional: ohne OpenCV kein Rasterweg
        return []
    dpi = dpi or adaptive_dpi(page)
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
    binary = (img < 150).astype(np.uint8)
    k = max(15, int(dpi * 0.12))                         # ~3 mm Mindestlaenge
    f = 72.0 / dpi
    out = []
    for kernel, horizontal in ((np.ones((1, k), np.uint8), True), (np.ones((k, 1), np.uint8), False)):
        lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        n, _, stats, _ = cv2.connectedComponentsWithStats(lines)
        for x, y, w, h, _area in stats[1:n]:
            if horizontal and h <= 10 * dpi / 200:      # Scan: Linien sind 2-4x breiter als im Vektor
                yc = (y + h / 2) * f
                out.append(Seg(x * f, yc, (x + w) * f, yc, h * f, True))
            elif not horizontal and w <= 10 * dpi / 200:
                xc = (x + w / 2) * f
                out.append(Seg(xc, y * f, xc, (y + h) * f, w * f, True))
    return out


_OCR = None


def ocr_words(page: pymupdf.Page, dpi: int | None = None, min_conf: float = 0.5) -> list[tuple]:
    """Text aus dem Seitenbild (RapidOCR/ONNX, Apache-2.0), als Woerter in Ansichtskoordinaten.

    Ein OCR-Kasten ist eine Zeile; die Woerter darin bekommen anteilige x-Bereiche.
    """
    global _OCR
    dpi = dpi or adaptive_dpi(page)                      # verkleinerte Seiten schaerfer rendern
    pix = page.get_pixmap(dpi=dpi)
    cache = None
    if os.environ.get("GEO_OCR_CACHE"):                  # Cache je Seitenbild (Tests laufen oft)
        cache = Path(os.environ["GEO_OCR_CACHE"]) / (hashlib.md5(pix.samples).hexdigest() + f"_{dpi}.json")
    if cache and cache.exists():
        res = json.loads(cache.read_text())              # Modell erst bei Cache-Fehlschlag laden (Speicher, X7)
    else:
        if _OCR is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                _OCR = RapidOCR()
            except ImportError:                          # ohne OCR bleibt die Seite stumm (und wird gemeldet)
                _OCR = False
        if not _OCR:
            return []
        img = np.ascontiguousarray(np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3])
        res, _ = _OCR(img)
        res = [[[[float(c) for c in q] for q in box], txt, float(conf)] for box, txt, conf in (res or [])]
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(res))
    f = 72.0 / dpi
    out = []
    for i, (box, txt, conf) in enumerate(res or []):
        if float(conf) < min_conf or not txt.strip():
            continue
        xs, ys = [q[0] * f for q in box], [q[1] * f for q in box]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        txt = txt.strip()
        pos = 0
        for tok in txt.split():
            k = txt.index(tok, pos)
            a, b = k / len(txt), (k + len(tok)) / len(txt)
            out.append((pymupdf.Rect(x0 + a * (x1 - x0), y0, x0 + b * (x1 - x0), y1), tok, 100000 + i, 0))
            pos = k + len(tok)
    return out


def page_class(page: pymupdf.Page, words, drawings) -> str:
    """E0: vektor | vektor_ohne_text | raster | raster_ocr."""
    m = page.rotation_matrix
    imgs = [r for r in (pymupdf.Rect(i["bbox"]) * m & page.rect for i in page.get_image_info()) if not r.is_empty]
    cov = min(1.0, sum(r.get_area() for r in imgs) / max(page.rect.get_area(), 1.0))
    inside = sum(1 for r, *_ in words if any(i.contains((r.tl + r.br) / 2) for i in imgs))
    if cov > 0.45 and inside < 10:
        return "raster"                                  # Bild ohne Textlage (Portal-Screenshot, Archivscan)
    if cov > 0.8 and (len(drawings) < 5 or RULES["scan_with_vectors"]):
        return "raster_ocr"                              # Scan mit OCR-Textlage (auch mit Vektorrauschen)
    if len(drawings) >= 150 and len(words) < 25:
        return "vektor_ohne_text"                        # AutoCAD mit SHX-Schrift: Text sind Linien
    return "vektor"


_RASTER_GW_TEMPLATES: dict[tuple, list] = {}


def _raster_gw_templates(dpi: int, heights: tuple[float, ...] = (4.2, 5.4, 6.8, 8.6),
                         aspects: tuple[float, ...] = (1.05, 1.45, 2.0)) -> list:
    """Synthetische Grauwert-Vorlagen (0=Strich, 255=Papier) fuer GW-Symbole auf einer waagrechten Linie:
    volles, offenes und halb gefuelltes Dreieck (DIN 4023) sowie Dach (V, nur mit Legende, W3)."""
    key = (dpi, heights, aspects)
    if key in _RASTER_GW_TEMPLATES:
        return _RASTER_GW_TEMPLATES[key]
    import cv2
    f = 72.0 / dpi
    tmpls = []
    for h_pt in heights:
        for aspect in aspects:
            h = max(6, int(round(h_pt / f)))
            w = max(7, int(round(h_pt * aspect / f)))
            w += (w + 1) % 2                                 # ungerade Breite fuer exakte Spitze in der Mitte
            pad_x, pad_top, pad_bot = max(2, int(round(1.6 / f))), max(2, int(round(1.6 / f))), max(2, int(round(1.0 / f)))
            H_img, W_img = pad_top + h + pad_bot, w + 2 * pad_x
            cx, y_top, y_bot, x_l, x_r = pad_x + w // 2, pad_top, pad_top + h, pad_x, pad_x + w - 1
            lw = max(1, int(round(0.65 / f)))

            def _canvas():
                c = np.full((H_img, W_img), 255, dtype=np.uint8)
                cv2.line(c, (0, y_bot), (W_img - 1, y_bot), 0, lw)
                return c

            tri = np.array([[x_l, y_top], [x_r, y_top], [cx, y_bot]], dtype=np.int32)
            # voll, offen, rechts halb gefuellt, links halb gefuellt (DIN 4023)
            c = _canvas(); cv2.fillPoly(c, [tri], 0)
            tmpls.append(("voll", w, h, pad_x, pad_top, c))
            c = _canvas(); cv2.polylines(c, [tri], True, 0, lw, cv2.LINE_AA)
            tmpls.append(("offen", w, h, pad_x, pad_top, c))
            c = _canvas(); cv2.polylines(c, [tri], True, 0, lw, cv2.LINE_AA)
            cv2.fillPoly(c, [np.array([[cx, y_top], [x_r, y_top], [cx, y_bot]], dtype=np.int32)], 0)
            tmpls.append(("voll", w, h, pad_x, pad_top, c))
            c = _canvas(); cv2.polylines(c, [tri], True, 0, lw, cv2.LINE_AA)
            cv2.fillPoly(c, [np.array([[x_l, y_top], [cx, y_top], [cx, y_bot]], dtype=np.int32)], 0)
            tmpls.append(("voll", w, h, pad_x, pad_top, c))
            # Dach (zwei Schraege ohne Querstrich, Spitze oben)
            c = _canvas()
            cv2.line(c, (x_l, y_bot), (cx, y_top), 0, lw, cv2.LINE_AA)
            cv2.line(c, (x_r, y_bot), (cx, y_top), 0, lw, cv2.LINE_AA)
            tmpls.append(("v", w, h, pad_x, pad_top, c))
    _RASTER_GW_TEMPLATES[key] = tmpls
    return tmpls


def _raster_hlines(img: np.ndarray, dpi: int, min_len_pt: float = 15.0) -> list[Seg]:
    """Waagrechte Linien fuer W4: dunkle Linien (<155, immun gegen farbige Saeulenfuellungen) plus
    duenne geglaettete Linien (<215 nach Abzug dicker Flaechen), kollinear zusammengefuegt."""
    import cv2
    f = 72.0 / dpi
    max_h = max(3, int(round(3.5 / f)))
    k_dark = max(8, int(round(min_len_pt / f)))
    k_thin = max(7, int(round(min(10.0, min_len_pt) / f)))
    segs = []
    for mask, k, mlen in (((img < 155).astype(np.uint8), k_dark, min_len_pt),
                          (None, k_thin, min(10.0, min_len_pt))):
        if mask is None:
            b2 = (img < 215).astype(np.uint8)
            thick = cv2.morphologyEx(b2, cv2.MORPH_OPEN, np.ones((max_h + 2, 1), np.uint8))
            mask = np.where(thick == 0, b2, 0).astype(np.uint8)
        lines = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((1, k), np.uint8))
        n, _, stats, _ = cv2.connectedComponentsWithStats(lines)
        for x, y, w, h, _ in stats[1:n]:
            if h <= max_h and w * f >= mlen:
                yc = (y + h / 2.0) * f
                segs.append(Seg(x * f, yc, (x + w) * f, yc, h * f, True))
    if not segs:
        return []
    return [s for s in _merge(segs, "h", gap=8.0) if s.x1 - s.x0 >= min_len_pt]


def _verify_raster_gw(img: np.ndarray, x_l: int, y_top: int, x_r: int, y_bot: int, form: str, dpi: int,
                      is_legend: bool = False) -> bool:
    """Strenge Formpruefung auf dem Graubild: schliesst Buchstaben (V, W, 7, T, M), Kreise und Kaesten aus."""
    import cv2
    H_img, W_img = img.shape
    f = 72.0 / dpi
    w, h = x_r - x_l, y_bot - y_top
    cx = (x_l + x_r) / 2.0
    if x_l < 2 or y_top < 3 or x_r >= W_img - 2 or y_bot >= H_img - 2 or w < 5 or h < 5:
        return False
    patch = img[max(0, y_top - 2):min(H_img, y_bot + 3), max(0, x_l - 2):min(W_img, x_r + 3)]
    bg, fg = float(np.percentile(patch, 92)), float(np.percentile(patch, 5))
    if bg - fg < 60:
        return False
    thr = bg - 0.35 * (bg - fg)
    rad = max(1, int(round(0.65 / f)))
    y0_b, y1_b = max(0, y_top - rad - 1), min(H_img, y_bot + rad + 2)
    x0_b, x1_b = max(0, x_l - rad - 1), min(W_img, x_r + rad + 2)
    sub_min = cv2.erode(img[y0_b:y1_b, x0_b:x1_b], np.ones((2 * rad + 1, 2 * rad + 1), np.uint8))

    def line_cov(ax: float, ay: float, bx: float, by: float) -> float:
        steps = max(7, int(round(max(abs(bx - ax), abs(by - ay)))))
        xs = np.round(np.linspace(ax, bx, steps)).astype(int) - x0_b
        ys = np.round(np.linspace(ay, by, steps)).astype(int) - y0_b
        return float((sub_min[ys, xs] < thr).mean())

    def corner_dark(px: int, py: int, cr: int) -> bool:
        csub = img[max(0, py - cr):min(H_img, py + cr + 1), max(0, px - cr):min(W_img, px + cr + 1)]
        return bool(csub.size and float(csub.min()) < thr)

    box = img[y_top:y_bot + 1, x_l:x_r + 1]
    yy, xx = np.mgrid[0:box.shape[0], 0:box.shape[1]]
    dx, t = np.abs(xx - (w / 2.0)), yy / max(h, 1.0)
    pad_edge = max(2, rad + 1)

    if form == "v":
        if not corner_dark(int(round(cx)), y_top, max(1, rad)):
            return False
        if line_cov(x_l, y_bot - 1, cx, y_top) < 0.72 or line_cov(x_r, y_bot - 1, cx, y_top) < 0.72:
            return False
        half_span = t * (w / 2.0)
        mask_out = (yy >= 1) & (yy < h - 1) & (dx > half_span + pad_edge)
        mask_in = (yy >= 2) & (yy < h - max(1, rad)) & (dx < half_span - pad_edge)
        out_f = float((box[mask_out] < thr).mean()) if mask_out.any() else 0.0
        in_f = float((box[mask_in] < thr).mean()) if mask_in.any() else 0.0
        return out_f <= 0.16 and in_f <= 0.25

    cr = max(1, int(round(0.65 / f)))
    if not (corner_dark(x_l, y_top, cr) and corner_dark(x_r, y_top, cr)):   # schliesst Kreise aus
        return False
    if line_cov(x_l, y_top, x_r, y_top) < 0.75 or line_cov(x_l, y_top, cx, y_bot) < 0.75 \
            or line_cov(x_r, y_top, cx, y_bot) < 0.75:
        return False
    margin_bot = max(1, int(round(1.1 / f)))
    half_span = (1.0 - t) * (w / 2.0)
    mask_out = (yy >= 1) & (yy < h - margin_bot) & (dx > half_span + pad_edge)
    if mask_out.any() and float((box[mask_out] < thr).mean()) > 0.15:       # weisser Aussenraum neben den Schenkeln
        return False
    if not is_legend:
        ya0, ya1 = max(0, y_top - max(2, int(round(2.5 / f)))), max(0, y_top - max(1, int(round(1.0 / f))))
        above = img[ya0:ya1, x_l:x_r + 1]
        if above.size and float((above < thr).mean()) > 0.18:               # frei ueber der Oberkante
            return False
    # Verjuengung nach unten: oben breit, bei 65 % Hoehe deutlich schmaler (schliesst Kreise/Kaesten aus)
    row_top = box[0:min(box.shape[0], max(2, rad + 1)), :] < thr
    y_lo_row = int(round(h * 0.65))
    row_low = box[max(0, y_lo_row - 1):min(box.shape[0], y_lo_row + 2), :] < thr
    top_cols, low_cols = np.where(row_top.any(axis=0))[0], np.where(row_low.any(axis=0))[0]
    w_top = int(top_cols[-1] - top_cols[0]) if len(top_cols) >= 2 else 0
    w_low = int(low_cols[-1] - low_cols[0]) if len(low_cols) >= 2 else w
    return w_top >= 0.72 * w and w_low <= 0.68 * w_top


def _match_raster_gw_on_hlines(img: np.ndarray, hlines: list[Seg], dpi: int, allow_v: bool = False,
                               heights: tuple[float, ...] = (4.2, 5.4, 6.8, 8.6),
                               aspects: tuple[float, ...] = (1.05, 1.45, 2.0),
                               thresh: float = 0.62, is_legend: bool = False) -> list[tuple]:
    """Vorlagenabgleich ausschliesslich in schmalen Streifen ueber waagrechten Linien."""
    import cv2
    f = 72.0 / dpi
    H_img, W_img = img.shape
    tmpls = _raster_gw_templates(dpi, heights=heights, aspects=aspects)
    max_h_px = int(round((max(heights) + 3.0) / f)) + 4
    pad_end = max(8, int(round(10.0 / f)))
    cands = []
    for s in hlines:
        lx0, lx1, y_bot_target = int(round(s.x0 / f)), int(round(s.x1 / f)), int(round(s.y0 / f))
        sy0, sy1 = max(0, y_bot_target - max_h_px), min(H_img, y_bot_target + max(4, int(round(2.5 / f))))
        sx0, sx1 = max(0, lx0 - pad_end), min(W_img, lx1 + pad_end)
        strip = img[sy0:sy1, sx0:sx1]
        if strip.shape[0] < 10 or strip.shape[1] < 10:
            continue
        hits = []
        for form, tw, th, pad_x, pad_top, tmpl in tmpls:
            if form == "v" and not allow_v:
                continue
            th_img, tw_img = tmpl.shape
            if strip.shape[0] < th_img or strip.shape[1] < tw_img:
                continue
            ty_exp = (y_bot_target - sy0) - (pad_top + th)
            y_lo, y_hi = max(0, ty_exp - 2), min(strip.shape[0] - th_img, ty_exp + 2)
            if y_lo > y_hi:
                continue
            res = cv2.matchTemplate(strip[y_lo:y_hi + th_img, :], tmpl, cv2.TM_CCOEFF_NORMED)
            ys_m, xs_m = np.where(res >= thresh)
            if not len(xs_m):
                continue
            used_x: list[int] = []
            for idx in np.argsort(res[ys_m, xs_m])[::-1]:
                my, mx = int(ys_m[idx]), int(xs_m[idx])
                if any(abs(mx - ux) < tw * 0.6 for ux in used_x):
                    continue
                used_x.append(mx)
                gx_l, gy_top = sx0 + mx + pad_x, sy0 + y_lo + my + pad_top
                gx_r, gy_bot = gx_l + tw - 1, gy_top + th
                if _verify_raster_gw(img, gx_l, gy_top, gx_r, gy_bot, form, dpi, is_legend=is_legend):
                    hits.append((float(res[my, mx]), form, gx_l * f, gy_top * f, gx_r * f, gy_bot * f, s))
        hits.sort(key=lambda e: -e[0])
        kept = []
        for h_ in hits:
            cx = (h_[2] + h_[4]) / 2
            if not any(abs((k[2] + k[4]) / 2 - cx) < 5.0 for k in kept):
                kept.append(h_)
        # Periodisches Muster (Zier-/Schraffurreihe auf einer Linie): >= 3 Treffer in festem Abstand verwerfen
        if not is_legend and len(kept) >= 3:
            xs_k = sorted((h_[2] + h_[4]) / 2 for h_ in kept)
            diffs = np.diff(xs_k)
            if diffs.min() > 0 and (diffs.max() - diffs.min()) <= 0.25 * float(np.median(diffs)):
                continue
        cands.extend(kept)
    return cands


def _as_raster_drawing(form: str, x0: float, y0: float, x1: float, y1: float,
                       wline: Seg | None = None, is_legend: bool = False) -> dict:
    """Formtreffer als Pseudo-Zeichnung im gleichen Format wie Vektorpfade fuer _groundwater/gw_legende."""
    cx = (x0 + x1) / 2
    if form == "v":
        pts = [pymupdf.Point(x0, y1), pymupdf.Point(cx, y0), pymupdf.Point(x1, y1)]
        items = [("l", pts[0], pts[1]), ("l", pts[1], pts[2])]
        fill, typ = None, "s"
    else:
        pts = [pymupdf.Point(x0, y0), pymupdf.Point(x1, y0), pymupdf.Point(cx, y1)]
        items = [("l", pts[0], pts[1]), ("l", pts[1], pts[2]), ("l", pts[2], pts[0])]
        fill, typ = ((0, 0, 0), "fs") if form == "voll" else (None, "s")
    out = {"items": items, "rect": pymupdf.Rect(x0, y0, x1, y1), "type": typ, "color": (0, 0, 0),
           "fill": fill, "raster": True}
    if is_legend:
        out["raster_legend"] = True
    if wline is not None:
        out["wline"] = Seg(min(wline.x0, x0), wline.y0, max(wline.x1, x1), wline.y0, wline.width, True)
    return out


def raster_gw_symbols(page: pymupdf.Page, cols: list["Column"], acols: list["Column"],
                      lines: list, dpi: int = 200) -> list[dict]:
    """W4: GW-Symbole (Dreieck voll/offen/halb, Dach mit Legende) im Scan an waagrechten Wasserlinien.

    Laeuft nur auf gescannten Seiten mit verankerten Bohrungen, prueft nur den Hoehenbereich der Saeulen
    sowie die kleinen Legendenfelder links von Wassertexten und schliesst alle Saeuleninnenflaechen aus.
    """
    if not acols:
        return []
    try:
        import cv2  # noqa: F401
    except ImportError:
        return []
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
    f = 72.0 / dpi
    H_img, W_img = img.shape
    out: list[dict] = []
    # 1. Legende im Scan (W3 + W4): nur die kleinen Felder links von Zeilen mit Wassertext
    allow_v = False
    if RULES["raster_gw_legende"] and RULES["gw_legende"]:
        leg_drawings: list[dict] = []
        for r, t in lines:
            if len(t) > 60 or not re.search(r"wasser|angebohrt|angestiegen", t, re.I):
                continue
            if gw_info(t)["kind"] == "unbestimmt":
                continue
            x0, x1 = max(0, int(round((r.x0 - 92) / f))), min(W_img, int(round((r.x0 + 4) / f)))
            y0, y1 = max(0, int(round((r.y0 - 16) / f))), min(H_img, int(round((r.y1 + 16) / f)))
            if x1 - x0 < 15 or y1 - y0 < 10:
                continue
            crop = img[y0:y1, x0:x1]
            hl = _raster_hlines(crop, dpi, min_len_pt=8.0)
            for _sc, form, gx0, gy0, gx1, gy1, _s in _match_raster_gw_on_hlines(
                    crop, hl, dpi, allow_v=True, heights=(2.8, 3.6, 4.8, 6.2),
                    aspects=(1.05, 1.5, 2.0), thresh=0.58, is_legend=True):
                leg_drawings.append(_as_raster_drawing(form, gx0 + x0 * f, gy0 + y0 * f,
                                                       gx1 + x0 * f, gy1 + y0 * f, is_legend=True))
        out.extend(leg_drawings)
        allow_v = "v" in gw_legende(leg_drawings, lines)
    # 2. Profilbereich: waagrechte Linien >= 15 pt im Hoehenband der verankerten Saeulen (ohne Innen-/Durchgangslinien)
    y_lo = min(c.rect.y0 for c in acols) - 6
    y_hi = max(c.rect.y1 for c in acols) + 6
    max_w = 0.75 * page.rect.width
    real_cols = [c for c in cols if c in acols or not any(
        abs(c.rect.x1 - a.rect.x0) < 3 or abs(c.rect.x0 - a.rect.x1) < 3 or (c.rect & a.rect).get_area() > 0
        for a in acols)]

    def _passende_linie(s: Seg) -> bool:
        if not (y_lo <= s.y0 <= y_hi and s.x1 - s.x0 < max_w):
            return False
        if any(c.rect.x0 - 2 <= s.x0 and s.x1 <= c.rect.x1 + 2 and c.rect.y0 - 2 <= s.y0 <= c.rect.y1 + 2
               for c in real_cols):
            return False                                    # Schichtgrenze in einer Saeule
        if any(s.x0 < c.rect.x0 - 5 and s.x1 > c.rect.x1 + 5 and c.rect.y0 - 2 <= s.y0 <= c.rect.y1 + 2 for c in acols):
            return False                                    # Trenn-/GOK-Linie quer durch eine Saeule
        return any(min(abs(c.rect.x0 - s.x0), abs(c.rect.x1 - s.x0),
                       abs(c.rect.x0 - s.x1), abs(c.rect.x1 - s.x1)) <= 105 for c in acols)

    hlines = [s for s in _raster_hlines(img, dpi, min_len_pt=15.0) if _passende_linie(s)]
    for _sc, form, x0, y0, x1, y1, s in _match_raster_gw_on_hlines(img, hlines, dpi, allow_v=allow_v):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if any(c.rect.x0 - 2 <= cx <= c.rect.x1 + 2 and c.rect.y0 - 2 <= cy <= c.rect.y1 + 2 for c in real_cols):
            continue                                        # Symbol in einer Saeule = Schraffur
        out.append(_as_raster_drawing(form, x0, y0, x1, y1, wline=s))
    return out


def _zeile_ordnen(ws: list[tuple[pymupdf.Rect, str, int]]) -> list[tuple[pymupdf.Rect, str, int]]:
    """Woerter einer (Block, Zeile)-Gruppe in Leserichtung ordnen (Issue #49).

    Nutzt die Wortnummer aus MuPDF/OCR (folgt der Zeilenrichtung `dir`, auch bei gedrehtem oder
    senkrechtem Text); fehlen eindeutige Wortnummern, nach Hauptachse der Zeile (x0 bei waagrecht,
    sonst y0) - nie nach (y0, x0) innerhalb einer waagrechten Zeile.
    """
    if len(ws) <= 1:
        return ws
    if len({w[2] for w in ws}) == len(ws):
        return sorted(ws, key=lambda w: w[2])
    cxs = [(w[0].x0 + w[0].x1) / 2 for w in ws]
    cys = [(w[0].y0 + w[0].y1) / 2 for w in ws]
    if max(cxs) - min(cxs) >= max(cys) - min(cys):
        return sorted(ws, key=lambda w: (w[0].x0, w[2]))
    return sorted(ws, key=lambda w: (w[0].y0, w[2]))


def primitives(page: pymupdf.Page):
    m = page.rotation_matrix if RULES["rotation"] else pymupdf.Matrix(1, 1)
    raw_words = page.get_text("words")
    words = [(pymupdf.Rect(w[:4]) * m, w[4], w[5], w[6]) for w in raw_words]
    word_nos = [int(w[7]) if len(w) > 7 else i for i, w in enumerate(raw_words)]
    drawings = [_xform_drawing(d, m) for d in page.get_drawings()]
    segs: list[Seg] = []
    pclass = page_class(page, words, drawings)
    scanned = pclass in ("raster", "raster_ocr")
    if scanned:                                          # Linien aus dem Bild
        segs = raster_segments(page)
    if (pclass in ("raster", "vektor_ohne_text") and RULES["ocr"]) or (pclass == "raster_ocr" and RULES["ocr_supplement"]):
        native = [r for r, *_ in words]
        ocr_extra = [w for w in ocr_words(page) if not any((w[0] & r).get_area() > 0.3 * w[0].get_area() for r in native)]
        words += ocr_extra
        word_nos += list(range(len(ocr_extra)))
    for d in ([] if scanned and len(drawings) < 5 else drawings):   # Vektoren neben dem Bild behalten
        stroked = d.get("color") is not None and "s" in d.get("type", "")
        fill = d.get("fill")
        coloured_fill = fill is not None and min(fill) < 0.97          # weisse Masken ignorieren
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
    lines: dict[tuple, list] = defaultdict(list)
    for (r, t, b, ln), wno in zip(words, word_nos):
        lines[(b, ln)].append((r, t, wno))
    text_lines = []
    for ws in lines.values():
        if RULES["line_reading_order"]:
            ws = _zeile_ordnen(ws)
        else:
            ws.sort(key=lambda x: (x[0].y0, x[0].x0))
        r = pymupdf.Rect(ws[0][0])
        for q, _, _ in ws[1:]:
            r |= q
        text_lines.append((r, " ".join(t for _, t, _ in ws)))
    return words, text_lines, drawings, segs, scanned, pclass


def _merge(segs: list[Seg], axis: str, gap: float = 1.5) -> list[Seg]:
    """Kollineare Segmente (gleiche y bzw. x) zu durchgehenden Linien zusammenfuegen."""
    groups: dict[float, list[Seg]] = defaultdict(list)
    for s in segs:
        groups[round((s.y0 if axis == "h" else s.x0) * 2) / 2].append(s)
    out = []
    for key, ss in groups.items():
        ss.sort(key=lambda s: s.x0 if axis == "h" else s.y0)
        cur = ss[0]
        lo, hi, w, st = (cur.x0, cur.x1, cur.width, cur.stroked) if axis == "h" else (cur.y0, cur.y1, cur.width, cur.stroked)
        for s in ss[1:]:
            a, b = (s.x0, s.x1) if axis == "h" else (s.y0, s.y1)
            if a <= hi + gap:
                hi, w, st = max(hi, b), max(w, s.width), st or s.stroked
            else:
                out.append(Seg(lo, key, hi, key, w, st) if axis == "h" else Seg(key, lo, key, hi, w, st))
                lo, hi, w, st = a, b, s.width, s.stroked
        out.append(Seg(lo, key, hi, key, w, st) if axis == "h" else Seg(key, lo, key, hi, w, st))
    return out


# ---------------------------------------------------------------------------
# Saeulen aus Kantenpaaren
# ---------------------------------------------------------------------------
@dataclass
class Column:
    rect: pymupdf.Rect
    bounds: list[float]          # y aller Grenzen inkl. Ober- und Unterkante
    weight: float                # Strichstaerke der Raender


def find_columns(segs: list[Seg], wmin=8, wmax=80, min_ratio=2.5, merge_tol=0.8) -> list[Column]:
    # Schraffurlinien (gestrichelt oder knapp innerhalb der Raender) sind keine Schichtgrenzen
    H = _merge([s for s in segs if s.horizontal and s.x1 - s.x0 >= 3
                and not (s.dashed and RULES["dashed_exclusion"])], "h")
    V = [v for v in _merge([s for s in segs if s.vertical and s.y1 - s.y0 >= 3 and s.stroked], "v")
         if v.y1 - v.y0 >= 30]
    V.sort(key=lambda v: v.x0)
    cols = []
    for a, b in itertools.combinations(V, 2):
        w = b.x0 - a.x0
        if not (wmin <= w <= wmax):
            continue
        y0, y1 = max(a.y0, b.y0), min(a.y1, b.y1)
        h = y1 - y0
        if h < min_ratio * w or h < 0.9 * min(a.y1 - a.y0, b.y1 - b.y0):
            continue
        ys = sorted(s.y0 for s in H if s.x0 <= a.x0 + 0.6 and s.x1 >= b.x0 - 0.6 and y0 - 1 <= s.y0 <= y1 + 1)
        bounds = []
        for y in [y0] + ys + [y1]:
            if not bounds or y - bounds[-1] > merge_tol:
                bounds.append(y)
            elif y == y1:
                bounds[-1] = y1                               # doppelte Unterkante -> eine Grenze
        cols.append(Column(pymupdf.Rect(a.x0, y0, b.x0, y1), bounds, min(a.width, b.width)))
    # verschachtelte Kandidaten (Innenstreifen, Rohr einer GWM) -> den mit kraeftigeren Raendern behalten
    cols.sort(key=lambda c: (-round(c.weight, 1), -len(c.bounds), -c.rect.width))
    kept: list[Column] = []
    for c in cols:
        if not any(k.rect.x0 - 1 <= c.rect.x0 and c.rect.x1 <= k.rect.x1 + 1 and
                   min(k.rect.y1, c.rect.y1) - max(k.rect.y0, c.rect.y0) > 0.8 * c.rect.height for k in kept):
            kept.append(c)
    return kept


# ---------------------------------------------------------------------------
# Klassifikation: Substantiv, Fels, Anthropogen
# ---------------------------------------------------------------------------
def classify_v3(text: str) -> str:
    for raw in re.findall(r"[A-Za-zÄÖÜäöüß]+", text):
        w = raw.lower()
        if not raw[0].isupper() or w.endswith(("ig", "haltig", "lich")):
            continue                                   # nur Substantive
        if w in TOPSOIL:
            return "Mutterboden"
        if w in ANTHROPOGEN:
            return ANTHROPOGEN[w]
        if w.endswith(ROCK_SUFFIX) and w != "steine":
            return f"Fels ({raw})"
        cls, sure = soil.classify(raw)
        if sure:
            return cls
    if RULES["abbreviations"] and (m := ABBR_RE.match(text)):   # 'U, t, s´' -> Schluff, 'fS' -> Sand
        k = m.group(1)
        return ABBR.get(k) or ABBR.get(k[-1], "")
    return ""


# ---------------------------------------------------------------------------
# Tiefen: Labels finden und den Grenzen zuordnen
# ---------------------------------------------------------------------------
def depth_value(t: str) -> float | None:
    """Tiefenlabel -> Wert; OCR verliert manchmal das Komma ('0950' = 9,50, R1)."""
    if DEPTH_RE.match(t):
        return float(t.rstrip("m ").replace(",", "."))
    if RULES["ocr_decimal_fix"] and re.fullmatch(r"0\d{3}", t):
        return int(t) / 100
    return None


def label_groups(words, col: Column, cols: list[Column], scanned: bool = False):
    """Dezimalzahlen-Spalten, die dieser Saeule am naechsten liegen (nicht einer Nachbarsaeule)."""
    def hdist(r, c):
        return max(c.rect.x0 - r.x1, r.x0 - c.rect.x1, 0)
    cands = []
    for r, t, *_ in words:
        v = depth_value(t)
        if v is None or v > 150:
            continue
        cy = (r.y0 + r.y1) / 2
        if not (col.rect.y0 - 8 <= cy <= col.rect.y1 + 150) or hdist(r, col) > 110:
            continue
        near = [c for c in cols if c.rect.y0 - 8 <= cy <= c.rect.y1 + 150]
        if min(near, key=lambda c: hdist(r, c)) is not col:
            continue
        cands.append((r, v))
    groups: dict[int, list] = defaultdict(list)
    for r, v in cands:
        groups[round(r.x0 / 4)].append((r, v))
    out = []
    for g in groups.values():
        g.sort(key=lambda e: e[0].y0)
        g = _longest_non_decreasing(g)                    # versprengte Zahlen (andere Texte) entfernen
        if len(g) >= 2 and not (RULES["axis_filter"] and _axis(g, col)) and not (RULES["paired_filter"] and _paired(g)) \
                and not (scanned and RULES["raster_massstab_ocr"] and _is_ruler_group(g, col)):
            out.append(g)
    return sorted(out, key=lambda g: (-len(g), hdist(g[0][0], col)))


RULER_NUM_RE = re.compile(r"^~?[+-]?\d{1,4}(?:[.,]\d{1,2})?\s?m?$")
RULER_STEPS = (0.1, 0.2, 0.25, 0.3, 0.5, 1.0, 2.0, 2.5, 5.0, 10.0)


def _is_ruler_group(g, col: Column) -> bool:
    """L14 im Scan: ein kurzes Tiefenlineal (>= 4 Werte mit rundem Schritt auf einer Geraden, das nicht auf den
    Schichtgrenzen der Saeule sitzt) ist eine Achse und keine Schichtbeschriftung."""
    if len(g) < 4:
        return False
    vs = [v for _, v in g]
    d = np.diff(vs)
    step = round(vs[1] - vs[0], 2)
    if d.min() <= 0 or float(d.max() - d.min()) > 0.015 or not any(abs(step - r) < 0.015 for r in RULER_STEPS):
        return False
    ys = np.array([(r.y0 + r.y1) / 2 for r, _ in g])
    a, b = np.polyfit(ys, np.array(vs), 1)
    if a <= 0 or float(np.max(np.abs(np.polyval([a, b], ys) - vs))) > 0.04 * max(step, 0.25):
        return False
    if len(col.bounds) <= 2:
        return True
    return label_support(col, g, float(a), float(-a * col.bounds[0]), tol=0.04) < 0.6 * len(g)


def _arith_ruler_subseq(items: list[tuple[pymupdf.Rect, float, bool]], decreasing: bool = False):
    """Laengste arithmetische Teilfolge (>= 4 Werte, runder Schritt, Geraden-Restfehler <= 4 % des Schritts)."""
    if len(items) < 4:
        return None
    dedup: list[tuple[pymupdf.Rect, float, bool]] = []
    for it in sorted(items, key=lambda e: (e[0].y0 + e[0].y1) / 2):
        if not dedup or abs((it[0].y0 + it[0].y1) / 2 - (dedup[-1][0].y0 + dedup[-1][0].y1) / 2) > 3.0:
            dedup.append(it)
    best = None
    steps = (0.2, 0.25, 0.5, 1.0, 2.0, 2.5, 5.0, 10.0) if decreasing else RULER_STEPS
    for s in steps:
        signed_s = -s if decreasing else s
        for i in range(len(dedup)):
            chain = [dedup[i]]
            for j in range(i + 1, len(dedup)):
                dv = dedup[j][1] - chain[-1][1]
                if abs(dv - signed_s) <= 0.02 * max(s, 1.0) or abs(dv - 2 * signed_s) <= 0.02 * max(s, 1.0):
                    chain.append(dedup[j])
            if len(chain) < 4:
                continue
            ys = np.array([(r.y0 + r.y1) / 2 for r, _, _ in chain])
            vs = np.array([v for _, v, _ in chain])
            a, b = np.polyfit(ys, vs, 1)
            res = float(np.max(np.abs(np.polyval([a, b], ys) - vs)))
            slope = -float(a) if decreasing else float(a)
            if slope > 0 and res <= 0.04 * max(s, 0.25) and \
                    (plausible_scale(slope / PT_TO_M_AT_1_1, tol=0.06) or RULES["nonstandard_scale"]):
                if best is None or len(chain) > len(best[2]):
                    best = (slope, float(b), chain, s)
    return best


def raster_ruler_scale(words, col: Column, cols: list[Column], gok: float | None = None) -> tuple[float, float] | None:
    """E5: Tiefenmassstab im Scan aus OCR-Zahlen eines Tiefenlineals oder einer Hoehenleiste (>= 4 Werte,
    arithmetische Reihe, senkrecht ausgerichtet)."""
    def hdist(r, c):
        return max(c.rect.x0 - r.x1, r.x0 - c.rect.x1, 0)
    y_min = min(c.rect.y0 for c in cols) - 40
    y_max = max(c.rect.y1 for c in cols) + 150
    x_left_min = min(c.rect.x0 for c in cols)
    local_buckets: dict[tuple[str, int], list] = defaultdict(list)
    page_buckets: dict[tuple[str, int], list] = defaultdict(list)
    for r, t, *_ in words:
        ts = t.strip()
        if not RULER_NUM_RE.match(ts):
            continue
        try:
            v = float(re.sub(r"[~m\s]", "", ts).replace(",", "."))
        except ValueError:
            continue
        cy = (r.y0 + r.y1) / 2
        if not (y_min <= cy <= y_max):
            continue
        is_int = not bool(DEPTH_RE.match(ts))
        near = [c for c in cols if c.rect.y0 - 35 <= cy <= c.rect.y1 + 150]
        if col.rect.y0 - 35 <= cy <= col.rect.y1 + 150 and hdist(r, col) <= 160 and near \
                and min(near, key=lambda c: hdist(r, c)) is col:
            local_buckets[("L", round(r.x0 / 6))].append((r, v, is_int))
            local_buckets[("R", round(r.x1 / 6))].append((r, v, is_int))
        if r.x1 <= x_left_min + 20 or (near and min(near, key=lambda c: hdist(r, c)) is col and hdist(r, col) <= 160):
            page_buckets[("L", round(r.x0 / 6))].append((r, v, is_int))
            page_buckets[("R", round(r.x1 / 6))].append((r, v, is_int))
    best_depth = None
    for items in local_buckets.values():
        cand = _arith_ruler_subseq(items, decreasing=False)
        if not cand:
            continue
        a, _, chain, _ = cand
        g_pairs = [(r, v) for r, v, _ in chain]
        all_int = all(is_int for _, _, is_int in chain)
        if not (all_int or _axis(g_pairs, col) or _is_ruler_group(g_pairs, col)):
            continue
        if best_depth is None or len(chain) > best_depth[0]:
            best_depth = (len(chain), a, float(-a * col.bounds[0]))
    if best_depth:
        return best_depth[1], best_depth[2]
    best_elev = None
    for items in page_buckets.values():
        cand = _arith_ruler_subseq(items, decreasing=True)
        if not cand:
            continue
        a, b_elev, chain, s = cand
        if gok is not None:
            elev_top = -a * col.bounds[0] + b_elev
            if abs(elev_top - gok) > max(0.35, 0.25 * s):
                continue
        if best_elev is None or len(chain) > best_elev[0]:
            best_elev = (len(chain), a, float(-a * col.bounds[0]))
    return (best_elev[1], best_elev[2]) if best_elev else None


def _arithmetic(g, tol: float = 0.011) -> bool:
    """Lineal, Hoehenleiste, Tiefenachse eines Rammdiagramms: >= 5 Werte mit gleichem Abstand (wie swissgeol)."""
    v = [x for _, x in g]
    d = np.diff(v)
    return len(v) >= 5 and d.min() > 0 and float(d.max() - d.min()) <= tol


def _axis(g, col: Column) -> bool:
    """L14: Lineal/Diagrammachse = arithmetische Folge mit rundem Schritt und >= 8 Werten, oder mehr Werte
    als die Saeule Grenzen hat. Gleich dicke Schichten (0,4 / 0,8 / 1,2 ...) bleiben Labels (s15)."""
    if not _arithmetic(g):
        return False
    step = round(g[1][1] - g[0][1], 2)
    round_step = any(abs(step - r) < 0.011 for r in (0.1, 0.2, 0.25, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0))
    return (round_step and len(g) >= 8) or len(g) > len(col.bounds) + 1


def _paired(g) -> bool:
    """Probenspalte: Von/Bis-Paare, fast jeder Wert steht doppelt untereinander."""
    v = [round(x, 2) for _, x in g]
    return len(v) >= 6 and len(set(v)) <= 0.7 * len(v)


def _longest_non_decreasing(g):
    best = [[e] for e in g]
    for i in range(len(g)):
        for j in range(i):
            if g[j][1] <= g[i][1] and len(best[j]) + 1 > len(best[i]):
                best[i] = best[j] + [g[i]]
    return max(best, key=len) if best else []


def label_support(col: Column, labels, a: float, b: float, tol: float = 0.03) -> int:
    """Wie viele Labelwerte werden von irgendeiner Grenze (Tiefe = a*y+b) bestaetigt?"""
    depths = [a * y + b for y in col.bounds]
    return sum(any(abs(d - v) <= tol for d in depths) for _, v in labels)


def choose_scale(col: Column, groups, scale_txt: list[int]):
    """Kandidaten: direkt, Reihenfolge (je Labelgruppe) und Massstabstext; Auswahl nach Bestaetigung."""
    cands = []
    for g in groups:
        f = fit_depths(col, g)
        if not f:
            continue
        sup = label_support(col, g, f[0], f[1])
        # Normmassstab ODER starke Bestaetigung (DC-Software skaliert Profile seitenfuellend, z. B. 1:35)
        if plausible_scale(f[0] / PT_TO_M_AT_1_1) or (RULES["nonstandard_scale"] and len(g) >= 3 and sup >= 0.8 * len(g)):
            cands.append((sup, f[2], f[0], f[1], f[3], g))
    for m in sorted(set(scale_txt)):
        a = m * PT_TO_M_AT_1_1
        b = -a * col.bounds[0]
        g = groups[0] if groups else []
        pairs = [(y, v) for _, v in g for y in col.bounds if abs(a * y + b - v) <= 0.03]
        cands.append((label_support(col, g, a, b), "massstab-text", a, b, pairs, g))
    if not cands:
        return None
    prio = {"direkt": 2, "reihenfolge": 1, "massstab-text": 0}
    best = max(cands, key=lambda c: (c[0], prio[c[1]]))
    return best[2], best[3], best[1], best[4], best[0], len(best[5])


def label_line(groups, min_n: int = 5, max_res: float = 0.2):
    """T4: Labelwerte linear ueber ihre Lage (y-Mitte) - unabhaengig von den Linien.

    Liefert (a, b, gruppe) mit Tiefe = a*y + b, wenn >= min_n Labels mit max. Restfehler max_res m passen.
    """
    best = None
    for g in groups:
        if len(g) < min_n:
            continue
        keep = list(range(len(g)))
        while True:                                       # gestapelte Labels (Fuehrungslinien) als Ausreisser
            ys = np.array([(g[i][0].y0 + g[i][0].y1) / 2 for i in keep])
            vs = np.array([g[i][1] for i in keep])
            a, b = np.polyfit(ys, vs, 1)
            res = np.abs(np.polyval([a, b], ys) - vs)
            if res.max() <= max_res or len(keep) - 1 < max(min_n, 0.75 * len(g)):
                break
            keep.pop(int(res.argmax()))
        # Massstab muss ein Normmassstab sein: sonst koennte jede Zahlenreihe eine 'Gerade' bilden
        # >= 8 Labels auf einer Geraden sind starke Evidenz, auch bei verkleinertem Druck (Massstab krumm)
        if a > 0 and res.max() <= max_res and (plausible_scale(a / PT_TO_M_AT_1_1) or len(keep) >= 8):
            # gestapelte Labels (Rest <= 1 m) bleiben Daten; weit abseits (Kote '52,35') gehoert nicht dazu
            g_ok = [e for e in g if abs(a * (e[0].y0 + e[0].y1) / 2 + b - e[1]) <= 1.0]
            if best is None or len(g_ok) > len(best[2]):
                best = (float(a), float(b), g_ok)
    return best


def fit_depths(col: Column, labels):
    """Liefert (a, b, modus, paare): Tiefe = a*y + b."""
    B = col.bounds
    # direkt: Label sitzt auf der Grenzlinie (Grundlinie oder Mitte)
    direct = []
    for r, v in labels:
        y = min(B, key=lambda yb: min(abs(r.y1 - yb), abs((r.y0 + r.y1) / 2 - yb)))
        if min(abs(r.y1 - y), abs((r.y0 + r.y1) / 2 - y)) <= 4.5:
            direct.append((y, v))
    if len(direct) >= max(2, 0.6 * len(labels)):
        pts = [(B[0], 0.0)] + [p for p in direct if p[0] != B[0]]
        a, b = np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)
        if a > 0:
            return a, b, "direkt", direct
    # Reihenfolge: k-tes Label <-> k-te Grenze, ueberzaehlige Grenzen/Labels testweise weglassen
    vals = sorted(v for _, v in labels)
    best = None
    for drop_b in range(0, min(4, len(B) + 1)):
        for keep in itertools.combinations(range(len(B)), len(B) - drop_b):
            yb = [B[i] for i in keep]
            for vv in (vals, [v for v in vals if v > 0]):
                if len(vv) != len(yb) or len(vv) < 2:
                    continue
                if vv[0] > 0:                                   # Unterkanten -> Oberkante = 0 dazu
                    if B[0] in yb:
                        continue
                    yy, vvv = [B[0]] + yb, [0.0] + vv
                else:
                    yy, vvv = yb, vv
                a, b = np.polyfit(yy, vvv, 1)
                res = float(np.max(np.abs(np.polyval([a, b], yy) - vvv)))
                if a > 0 and (best is None or res < best[0]):
                    best = (res, a, b, list(zip(yy, vvv)))
        if best and best[0] < 0.03:
            break
    if best and best[0] < 0.06:
        return best[1], best[2], "reihenfolge", best[3]
    return None


# ---------------------------------------------------------------------------
# Datenklassen
# ---------------------------------------------------------------------------
@dataclass
class Layer:
    top: float
    bottom: float
    soil: str = ""
    soil_hatch: str = ""
    label_confirmed: bool = False
    issues: list[str] = field(default_factory=list)
    text: str = ""                   # Originalbeschreibung (B2)
    confidence: float = 0.0


@dataclass
class Borehole:
    code: str
    page: int
    scale: float | None
    mode: str
    gok: float | None = None
    layers: list[Layer] = field(default_factory=list)
    gw_depths: list[float] = field(default_factory=list)
    gw_status: str | None = None
    gw_info: dict = field(default_factory=dict)  # Tiefe -> {"kind", "observed_on", "evidence"} (Issue #26)
    east: float | None = None
    north: float | None = None
    duplicates: list[str] = field(default_factory=list)
    cross_check: str = ""            # Abgleich mit dem Schichtenverzeichnis
    crs: int | None = None
    coord_source: str = ""
    page_class: str = ""
    bbox: tuple = ()
    fit: tuple = ()                  # Tiefe = a * y + b (Ansichtskoordinaten der Seite)
    issues: list[str] = field(default_factory=list)
    support: float = 0.0
    single_sheet: bool = False
    titled: bool = False


def gw_info(text: str) -> dict:
    """Art und Datum aus dem Text bei einem Wasserstand; der Text bleibt als Beleg."""
    kind = next((a for a, rx in GW_ART if rx.search(text or "")), "unbestimmt")
    datum = None
    for m in GW_DATUM_RE.finditer(text or ""):
        t_, mo, j = int(m.group(1)), int(m.group(2)), m.group(3)
        jahr = int(j) if len(j) == 4 else (2000 + int(j) if int(j) < 70 else 1900 + int(j))
        if 1 <= t_ <= 31 and 1 <= mo <= 12 and 1950 <= jahr <= 2100:
            datum = f"{jahr:04d}-{mo:02d}-{t_:02d}"
            break
    out = {"kind": kind}
    if datum:
        out["observed_on"] = datum
    if kind != "unbestimmt" or datum:
        out["evidence"] = " ".join((text or "").split())[:120]
    return out


def _gw_text_am(lines, x: float, y: float) -> str:
    """Text rechts oder links neben einem Wassersymbol: Zeilen, deren Mitte hoechstens 9 pt ueber/unter der
    Spitze liegt und die nicht weiter als 90 pt vom Symbol beginnen (Datum und Art stehen am Symbol, DIN 4023)."""
    near = [(r, t) for r, t in lines if abs((r.y0 + r.y1) / 2 - y) <= 9 and min(abs(r.x0 - x), abs(r.x1 - x)) <= 90]
    if RULES["line_reading_order"]:
        return " ".join(t for _, t in rows(near, dy=3.0))
    return " ".join(t for r, t in sorted(near, key=lambda e: (round(e[0].y0), e[0].x0)))


def wasserstaende_text(doc, prims: dict | None = None) -> list[dict]:
    """Bemessungswasserstand, HGW, MHGW, MGW aus dem Text des Gutachtens (m NHN, Seite, Beleg); je Art und Hoehe
    einmal. Nur Zahlen mit 'm NHN' - ein Stand 'auf Gelaendeoberkante' ohne Zahl bleibt im Text.
    Ohne prims nur die Textebene (Fliesstext, keine Lage noetig): gescannte Seiten tragen dann nichts bei."""
    out, seen = [], set()
    for pno, page in enumerate(doc):
        plines = prims[pno][1] if prims and pno in prims else [(None, page.get_text())]
        flat = " ".join(" ".join(t for _, t in plines).split())
        for m in WSP_TEXT_RE.finditer(flat):
            art = m.group(1)
            art = "Bemessungswasserstand" if art.lower().startswith("bemessung") else art
            nhn = float(m.group(3).replace(",", "."))
            if (art, nhn) in seen:
                continue
            seen.add((art, nhn))
            out.append({"kind": art, "nhn": nhn, "page": pno, "quelle": "Text",
                        "evidence": flat[max(0, m.start() - 40):m.end() + 20]})
    return out


# ---------------------------------------------------------------------------
# E7c: Wasserlinien im Laengsschnitt (Issue #26 Teil 2b, Regel ls_wasserlinien)
# ---------------------------------------------------------------------------
_NHN_SCHRITTE = (0.25, 0.5, 1.0, 2.0, 2.5, 5.0, 10.0, 20.0, 25.0, 50.0)
_GOK_LABEL_RE = re.compile(r"^\s*(?:GOK|Gel(?:ä|ae)nde(?:oberkante|linie)?|OK\s*Gel(?:ä|ae)nde)\s*$", re.I)
_WSP_ART_NORM = {
    "bemessungswasserstand": "Bemessungswasserstand",
    "bemessungsgrundwasserstand": "Bemessungswasserstand",
    "bauwasserstand": "Bauwasserstand",
    "zehgw": "zeHGW",
    "hhgw": "HHGW",
    "mhgw": "MHGW",
    "hgw": "HGW",
    "mgw": "MGW",
    "mngw": "MNGW",
}


def _ols_gerade(xs: np.ndarray, ys: np.ndarray) -> tuple[float, float, float, float]:
    """Lineare Regression ys = a * xs + b; gibt (a, b, r2, max_res) zurueck."""
    xm, ym = float(np.mean(xs)), float(np.mean(ys))
    dx = xs - xm
    den = float(np.dot(dx, dx))
    if den <= 1e-12:
        return 0.0, ym, 0.0, float("inf")
    a = float(np.dot(dx, ys - ym) / den)
    b = ym - a * xm
    pred = a * xs + b
    res = np.abs(ys - pred)
    ss_tot = float(np.sum((ys - ym) ** 2))
    ss_res = float(np.sum((ys - pred) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 1.0
    return a, b, r2, float(np.max(res))


def _nhn_achse(words, text_lines, segs) -> tuple[tuple[float, float, float, str] | None, str | None]:
    """Kalibriert die Hoehenachse nhn = a * y + b (a < 0) eines Laengsschnitts.

    1. Senkrechte NHN-Hoehenleiste (>= 4 fallende Werte in runder Schrittweite, R^2 >= 0.998, Residuum <= 0.10 m).
       Bei zwei Achsen (links/rechts) muessen beide innerhalb 0.15 m uebereinstimmen.
    2. Fallback ohne Randleiste: >= 2 verankerte Bohrungssaeulen mit GOK (+m NHN) und Hoehenmassstab H 1:n,
       deren gemeinsamer Achsenabschnitt b = gok - a * y_top innerhalb 0.10 m uebereinstimmt.
    """
    kands: list[tuple[pymupdf.Rect, float]] = []
    for r, t, *_ in words:
        tok = str(t).strip().rstrip("m")
        if not re.fullmatch(r"[+-]?\d{1,4}[.,]\d{1,2}", tok):
            continue
        v = float(tok.replace(",", "."))
        if -50.0 <= v <= 3000.0:
            kands.append((pymupdf.Rect(r), v))

    achsen: list[tuple[int, float, float, float, float]] = []  # (n, x_mitte, a, b, r2)
    for align in (0, 1):
        spalten: dict[int, list[tuple[pymupdf.Rect, float]]] = defaultdict(list)
        for r, v in kands:
            spalten[round((r.x0 if align == 0 else r.x1) / 6.0)].append((r, v))
        for grp in spalten.values():
            if len(grp) < 4:
                continue
            grp.sort(key=lambda e: (e[0].y0 + e[0].y1) / 2.0)
            dedup: list[tuple[pymupdf.Rect, float]] = []
            for r, v in grp:
                yc = (r.y0 + r.y1) / 2.0
                if not dedup or abs(yc - (dedup[-1][0].y0 + dedup[-1][0].y1) / 2.0) > 2.0:
                    dedup.append((r, v))
            if len(dedup) < 4:
                continue
            ys = np.array([(r.y0 + r.y1) / 2.0 for r, _ in dedup], dtype=float)
            vs = np.array([v for _, v in dedup], dtype=float)
            if not np.all(np.diff(vs) < -1e-6):
                continue
            diffs = -np.diff(vs)
            med = float(np.median(diffs))
            if med <= 1e-6 or not any(abs(med - s) <= 0.02 * s for s in _NHN_SCHRITTE):
                continue
            if float(np.max(diffs) - np.min(diffs)) > 0.08 * med + 1e-4:
                continue
            a, b, r2, res_max = _ols_gerade(ys, vs)
            if a < 0 and r2 >= 0.998 and res_max <= 0.10:
                xm = float(np.mean([(r.x0 + r.x1) / 2.0 for r, _ in dedup]))
                if not any(abs(xm - ex[1]) < 30.0 for ex in achsen):
                    achsen.append((len(dedup), xm, a, b, r2))
    if achsen:
        achsen.sort(key=lambda e: (-e[0], -e[4]))
        best = achsen[0]
        if len(achsen) >= 2:
            for alt in achsen[1:]:
                if abs(alt[1] - best[1]) > 100.0:
                    # Pruefen, ob beide Achsen auf dem Bildbereich uebereinstimmen
                    y_test = np.array([100.0, 400.0, 700.0])
                    if float(np.max(np.abs((best[2] * y_test + best[3]) - (alt[2] * y_test + alt[3])))) > 0.15:
                        return None, "Widerspruechliche NHN-Hoehenachsen im Laengsschnitt: Kalibrierung verworfen"
        return (best[2], best[3], best[4], "NHN-Achse"), None

    # Fallback: GOK an >= 2 Bohrungssaeulen + expliziter Hoehenmassstab H 1:n (z. B. marl_251 S. 6)
    volltext = " ".join(t for _, t in text_lines)
    m_h = re.search(r"(?:H(?:ö|oe)hen-?Ma(?:ss|ß)stab|\bH)\s*1\s*:\s*(\d{2,4})\b", volltext)
    if m_h and segs:
        scale_h = int(m_h.group(1))
        a_h = -scale_h * PT_TO_M_AT_1_1
        cols = find_columns(segs)
        bs_vals: list[tuple[float, float]] = []
        for c in cols:
            cx = (c.rect.x0 + c.rect.x1) / 2.0
            y_top = c.bounds[0]
            best_g = None
            for r, t in text_lines:
                if abs((r.x0 + r.x1) / 2.0 - cx) <= 95.0 and y_top - 80.0 <= (r.y0 + r.y1) / 2.0 <= y_top + 15.0:
                    mg = GOK_RE.search(t)
                    if mg:
                        g_tok = mg.group(1) or mg.group(2)
                        g_val = float(g_tok.replace(",", "."))
                        dist = abs((r.x0 + r.x1) / 2.0 - cx) + abs(r.y1 - y_top)
                        if best_g is None or dist < best_g[0]:
                            best_g = (dist, g_val)
            if best_g is not None:
                bs_vals.append((best_g[1], best_g[1] - a_h * y_top))
        # Groesster konsistenter Cluster (b innerhalb 0.12 m) mit >= 2 verschiedenen GOKs
        best_cl: list[tuple[float, float]] = []
        for _, b0 in bs_vals:
            cl = [(g, b) for g, b in bs_vals if abs(b - b0) <= 0.12]
            if len(cl) > len(best_cl):
                best_cl = cl
        if len(best_cl) >= 2:
            goks = [g for g, _ in best_cl]
            bs = [b for _, b in best_cl]
            if max(goks) - min(goks) >= 0.15 and max(bs) - min(bs) <= 0.12:
                return (a_h, float(np.median(bs)), 0.999, f"GOK+H1:{scale_h}"), None
    return None, None


def _station_achse(words) -> tuple[float, float] | None:
    """Kalibriert die Stationsachse station_m = ax * x + bx aus Beschriftungen wie '0+100'."""
    zeilen: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for r, t, *_ in words:
        m = STATION_RE.match(str(t).strip())
        if m:
            st = int(m.group(1)) * 1000.0 + float(m.group(2).replace(",", "."))
            zeilen[round(((r.y0 + r.y1) / 2.0) / 4.0)].append(((r.x0 + r.x1) / 2.0, st))
    best = None
    for grp in zeilen.values():
        if len(grp) < 2:
            continue
        grp.sort(key=lambda e: e[0])
        xs = np.array([e[0] for e in grp], dtype=float)
        sts = np.array([e[1] for e in grp], dtype=float)
        if not np.all(np.diff(sts) > 1e-3):
            continue
        ax, bx, r2, res_max = _ols_gerade(xs, sts)
        if ax > 0 and (len(grp) == 2 or (r2 >= 0.995 and res_max <= 1.0)):
            if best is None or len(grp) > best[0]:
                best = (len(grp), ax, bx)
    return (best[1], best[2]) if best else None


def _wasser_legende_kuerzel(text_lines) -> tuple[dict[str, str], pymupdf.Rect | None]:
    """Liest Kuerzel aus einer Legende ('Bau' -> 'Bauwasserstand', 'Bem' -> 'Bemessungswasserstand')."""
    leg_hdr = [r for r, t in text_lines if re.match(r"^\s*Legende\b", t, re.I)]
    if not leg_hdr:
        return {}, None
    hdr = leg_hdr[0]
    leg_box = pymupdf.Rect(hdr.x0 - 25.0, hdr.y0 - 5.0, hdr.x0 + 360.0, hdr.y0 + 260.0)
    in_leg = [(r, t.strip()) for r, t in text_lines if leg_box.intersects(r) and t.strip()]
    kuerzel: dict[str, str] = {}
    for r_art, t_art in in_leg:
        m = WSP_LINIE_RE.search(t_art)
        if not m or not m.group(1):
            continue
        art = _WSP_ART_NORM.get(m.group(1).lower(), m.group(1))
        yc = (r_art.y0 + r_art.y1) / 2.0
        for r_k, t_k in in_leg:
            if r_k == r_art or r_k.x1 > r_art.x0 + 2.0:
                continue
            if abs((r_k.y0 + r_k.y1) / 2.0 - yc) <= 10.0 and re.fullmatch(r"[A-Za-zÄÖÜäöü]{2,8}", t_k):
                if t_k.lower() != art.lower():
                    kuerzel[t_k] = art
    return kuerzel, leg_box


def _wasserlinien_polylinien(drawings, page_w: float, page_h: float) -> list[dict]:
    """Sammelt offene gezeichnete Polylinien (blau oder gestrichelt, >= 80 pt breit, keine Rahmen)."""
    polylinien: list[dict] = []
    kurze_blaue: list[tuple[tuple[float, ...], float, float, float, float, float]] = []

    for d in drawings:
        col = d.get("color")
        if col is None or "s" not in d.get("type", ""):
            continue
        ist_blau = len(col) == 3 and col[2] > col[0] + 0.12 and col[2] > 0.25
        ist_gestrichelt = d.get("dashes") not in (None, "[] 0", "[] 0.0")
        if not (ist_blau or ist_gestrichelt):
            continue
        # Nur Linien-Items ('l'); Rechtecke ('re') und Quads ('qu') sind Rahmen/Kasten
        l_items = [(it[1], it[2]) for it in d.get("items", ()) if it[0] == "l"]
        if not l_items:
            continue
        # Zusammenhaengende Ketten bilden
        ketten: list[list[tuple[float, float]]] = []
        for a, b in l_items:
            p0, p1 = (float(a.x), float(a.y)), (float(b.x), float(b.y))
            if ketten and abs(ketten[-1][-1][0] - p0[0]) <= 1.5 and abs(ketten[-1][-1][1] - p0[1]) <= 1.5:
                ketten[-1].append(p1)
            else:
                ketten.append([p0, p1])
        for k in ketten:
            xs = [p[0] for p in k]
            ys = [p[1] for p in k]
            span_x, span_y = max(xs) - min(xs), max(ys) - min(ys)
            if min(ys) < 12.0 or max(ys) > page_h - 12.0:
                continue
            if span_x >= 80.0 and (span_y <= 2.0 or span_x >= 2.5 * span_y):
                k_sort = k if k[0][0] <= k[-1][0] else list(reversed(k))
                polylinien.append({
                    "pts": k_sort, "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
                    "blau": ist_blau, "gestrichelt": ist_gestrichelt,
                })
            elif ist_blau and 3.0 <= span_x < 80.0 and span_y <= 2.5:
                ck = tuple(round(c, 2) for c in col)
                kurze_blaue.append((ck, round(d.get("width") or 0.0, 2), min(xs), max(xs), (min(ys) + max(ys)) / 2.0, span_x))

    # Gestrichelte CAD-Einzelsegmente gleicher Farbe/Hoehe zu einer Polylinie verketten (G6)
    gruppen: dict[tuple, list[tuple[float, float, float]]] = defaultdict(list)
    for ck, w_, x0_, x1_, yc_, _ in kurze_blaue:
        gruppen[(ck, w_, round(yc_ / 2.0))].append((x0_, x1_, yc_))
    for segs_g in gruppen.values():
        if len(segs_g) < 4:
            continue
        segs_g.sort(key=lambda s: s[0])
        cur = [segs_g[0]]
        for s in segs_g[1:]:
            if s[0] - cur[-1][1] <= 25.0:
                cur.append(s)
            else:
                if len(cur) >= 4 and cur[-1][1] - cur[0][0] >= 80.0:
                    ym = float(np.median([c[2] for c in cur]))
                    polylinien.append({"pts": [(cur[0][0], ym), (cur[-1][1], ym)],
                                       "x0": cur[0][0], "x1": cur[-1][1], "y0": ym, "y1": ym,
                                       "blau": True, "gestrichelt": True})
                cur = [s]
        if len(cur) >= 4 and cur[-1][1] - cur[0][0] >= 80.0:
            ym = float(np.median([c[2] for c in cur]))
            polylinien.append({"pts": [(cur[0][0], ym), (cur[-1][1], ym)],
                               "x0": cur[0][0], "x1": cur[-1][1], "y0": ym, "y1": ym,
                               "blau": True, "gestrichelt": True})
    return polylinien


def _y_auf_linie(pts: list[tuple[float, float]], x: float) -> float:
    """Lineare Interpolation der y-Koordinate einer Polylinie an Stelle x (am Rand geklemmt)."""
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        if x0 <= x <= x1:
            if abs(x1 - x0) <= 1e-6:
                return (y0 + y1) / 2.0
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return pts[-1][1]


def _linie_ist_gok_oder_schicht(pl: dict, cols: list[Column], text_lines) -> str | None:
    """Prueft, ob eine Polylinie eine Gelaendelinie (GOK) oder Schichtgrenze ist (Regel c)."""
    pts = pl["pts"]
    # Ueberlappende Spalten je x-Lage zusammenfassen; gleichmaessige Gitter (z. B. DPH-Raster, L14) ignorieren
    echte_cols: list[Column] = []
    for c in cols:
        if any(abs((c.rect.x0 + c.rect.x1) / 2.0 - (e.rect.x0 + e.rect.x1) / 2.0) < 25.0 for e in echte_cols):
            continue
        echte_cols.append(c)

    gok_hits, schicht_hits, crossed = 0, 0, 0
    for c in echte_cols:
        cx = (c.rect.x0 + c.rect.x1) / 2.0
        if not (pl["x0"] - 10.0 <= cx <= pl["x1"] + 10.0):
            continue
        yl = _y_auf_linie(pts, cx)
        if abs(yl - c.bounds[0]) <= 4.5:
            gok_hits += 1
        else:
            # Gleichmaessiges Tiefengitter (DPH-Raster, >= 6 Grenzen und Mehrheit im selben Rasterabstand, L14)
            if len(c.bounds) >= 6:
                ds = np.diff(c.bounds)
                med_d = float(np.median(ds))
                if med_d >= 5.0 and int(np.sum(np.abs(ds - med_d) <= 1.5)) >= max(5, int(0.6 * len(ds))):
                    continue
            crossed += 1
            if any(abs(yl - b) <= 3.5 for b in c.bounds[1:]):
                schicht_hits += 1
    if gok_hits >= 2 and gok_hits >= 0.5 * (gok_hits + crossed):
        return "Gelaendelinie"
    if schicht_hits >= 2 and schicht_hits >= 0.6 * crossed:
        return "Schichtgrenze"
    for r, t in text_lines:
        if _GOK_LABEL_RE.search(t):
            cx = (r.x0 + r.x1) / 2.0
            cy = (r.y0 + r.y1) / 2.0
            if pl["x0"] - 40.0 <= cx <= pl["x1"] + 40.0 and abs(_y_auf_linie(pts, cx) - cy) <= 10.0:
                return "Gelaendelinie"
    return None


def wasserlinien_laengsschnitt(doc, prims: dict | None = None) -> tuple[list[dict], list[str]]:
    """Liest HGW/MGW/Bemessungswasserstand/Bauwasserstand/GW-Linien aus Laengsschnitten (Issue #26 2b).

    Eine Linie wird nur uebernommen, wenn (a) eine eindeutige Beschriftung mit Wasserart an ihr haengt,
    (b) die NHN-Hoehenachse kalibriert ist und (c) sie weder Gelaendelinie noch Schichtgrenze ist.
    Unklare Faelle werden nie ausgegeben, sondern als Hinweis gemeldet.
    """
    if not RULES["ls_wasserlinien"]:
        return [], []
    out: list[dict] = []
    hinweise: list[str] = []

    for pno, page in enumerate(doc):
        if prims and pno in prims:
            words, text_lines, drawings, segs, scanned, _ = prims[pno]
            if scanned or not drawings:
                continue
        else:
            raw_drawings = page.get_drawings()
            if not raw_drawings:
                continue
            m = page.rotation_matrix if RULES["rotation"] else pymupdf.Matrix(1, 1)
            raw_words = page.get_text("words")
            words = [(pymupdf.Rect(w[:4]) * m, w[4], w[5], w[6]) for w in raw_words]
            if page_class(page, words, raw_drawings) in ("raster", "raster_ocr"):
                continue
            drawings = [_xform_drawing(d, m) for d in raw_drawings]
            word_nos = [int(w[7]) if len(w) > 7 else i for i, w in enumerate(raw_words)]
            lmap: dict[tuple, list] = defaultdict(list)
            for (r, t, b, ln), wno in zip(words, word_nos):
                lmap[(b, ln)].append((r, t, wno))
            text_lines = []
            for ws in lmap.values():
                ws = _zeile_ordnen(ws) if RULES["line_reading_order"] else sorted(ws, key=lambda x: (x[0].y0, x[0].x0))
                rr = pymupdf.Rect(ws[0][0])
                for q, _, _ in ws[1:]:
                    rr |= q
                text_lines.append((rr, " ".join(t for _, t, _ in ws)))
            segs = []
            for d in drawings:
                stroked = d.get("color") is not None and "s" in d.get("type", "")
                fill = d.get("fill")
                if not stroked and not (fill is not None and min(fill) < 0.97):
                    continue
                w_ = d.get("width") or 0.0
                dashed = d.get("dashes") not in (None, "[] 0", "[] 0.0")
                for it in d["items"]:
                    if it[0] == "l":
                        pts = [(it[1], it[2])]
                    elif it[0] == "re":
                        r_ = it[1]
                        pts = [(r_.tl, r_.tr), (r_.tr, r_.br), (r_.br, r_.bl), (r_.bl, r_.tl)]
                    elif it[0] == "qu":
                        q_ = it[1]
                        pts = [(q_.ul, q_.ur), (q_.ur, q_.lr), (q_.lr, q_.ll), (q_.ll, q_.ul)]
                    else:
                        continue
                    for a_, b_ in pts:
                        segs.append(Seg(min(a_.x, b_.x), min(a_.y, b_.y), max(a_.x, b_.x), max(a_.y, b_.y), w_, stroked, dashed))
        polylinien = _wasserlinien_polylinien(drawings, page.rect.width, page.rect.height)
        if not polylinien:
            continue

        leg_kuerzel, leg_box = _wasser_legende_kuerzel(text_lines)

        # Beschriftungen mit Wasserart sammeln (ausserhalb der Legende)
        labels: list[tuple[pymupdf.Rect, str, str | None, str, str]] = []
        for r, t in text_lines:
            if leg_box is not None and leg_box.intersects(r):
                continue
            for m in WSP_LINIE_RE.finditer(t):
                if m.group(1):
                    art = _WSP_ART_NORM.get(m.group(1).lower(), m.group(1))
                    labels.append((r, art, None, m.group(0).strip(), ""))
                elif m.group(2):
                    gi = gw_info(m.group(0))
                    if gi.get("observed_on"):
                        labels.append((r, "GW", gi["observed_on"], m.group(0).strip(), ""))
        if leg_kuerzel:
            for r, t, *_ in words:
                if leg_box is not None and leg_box.intersects(r):
                    continue
                tok = t.strip()
                if tok in leg_kuerzel:
                    labels.append((r, leg_kuerzel[tok], None, tok, f"Legende: {tok} -> {leg_kuerzel[tok]}"))
        if not labels:
            continue

        # (b) NHN-Hoehenachse kalibrieren
        nhn_cal, cal_hinweis = _nhn_achse(words, text_lines, segs)
        if cal_hinweis:
            hinweise.append(f"S. {pno + 1}: {cal_hinweis}")
        if nhn_cal is None:
            # Pruefen, ob ein Label direkt an einer blauen/gestrichelten Linie haengt -> Hinweis
            for r, art, _, raw, _ in labels:
                cx, cy = (r.x0 + r.x1) / 2.0, (r.y0 + r.y1) / 2.0
                if any(pl["x0"] - 80.0 <= cx <= pl["x1"] + 80.0 and abs(_y_auf_linie(pl["pts"], cx) - cy) <= 14.0
                       for pl in polylinien):
                    hinweise.append(f"S. {pno + 1}: Wasserlinie '{raw}' ohne kalibrierte NHN-Hoehenachse nicht uebernommen")
            continue

        a_nhn, b_nhn, r2_nhn, cal_art = nhn_cal
        st_cal = _station_achse(words)
        # Fuer GOK-/Schichtgrenzen-Pruefung nur nicht-blaue Segmente nutzen, damit blaue Wasserlinien
        # selbst nicht als eigene Schichtgrenzen in col.bounds landen
        segs_ohne_blau: list[Seg] = []
        for d in drawings:
            col_d = d.get("color")
            if col_d is not None and len(col_d) == 3 and col_d[2] > col_d[0] + 0.12 and col_d[2] > 0.25:
                continue
            stroked = col_d is not None and "s" in d.get("type", "")
            fill = d.get("fill")
            if not stroked and not (fill is not None and min(fill) < 0.97):
                continue
            w_ = d.get("width") or 0.0
            dashed = d.get("dashes") not in (None, "[] 0", "[] 0.0")
            for it in d["items"]:
                if it[0] == "l":
                    pts_d = [(it[1], it[2])]
                elif it[0] == "re":
                    r_ = it[1]
                    pts_d = [(r_.tl, r_.tr), (r_.tr, r_.br), (r_.br, r_.bl), (r_.bl, r_.tl)]
                elif it[0] == "qu":
                    q_ = it[1]
                    pts_d = [(q_.ul, q_.ur), (q_.ur, q_.lr), (q_.lr, q_.ll), (q_.ll, q_.ul)]
                else:
                    continue
                for a_, b_ in pts_d:
                    segs_ohne_blau.append(Seg(min(a_.x, b_.x), min(a_.y, b_.y), max(a_.x, b_.x), max(a_.y, b_.y), w_, stroked, dashed))
        cols = find_columns(segs_ohne_blau)

        # (c) Gelaende- und Schichtlinien markieren
        for pl in polylinien:
            pl["ausgeschlossen"] = _linie_ist_gok_oder_schicht(pl, cols, text_lines)

        # (a) Jede Beschriftung eindeutig genau einer aktiven Wasserlinie zuordnen
        gewaehlt: dict[tuple[int, str, str | None], dict] = {}
        for r, art, datum, raw, leg_b in labels:
            cx, cy = (r.x0 + r.x1) / 2.0, (r.y0 + r.y1) / 2.0
            nahe = []
            for idx, pl in enumerate(polylinien):
                if pl["x0"] - 80.0 <= cx <= pl["x1"] + 80.0:
                    d = abs(_y_auf_linie(pl["pts"], cx) - cy)
                    if d <= 14.0:
                        nahe.append((d, idx, pl))
            if not nahe:
                continue
            nahe.sort(key=lambda e: e[0])
            d1, idx1, pl1 = nahe[0]
            if pl1["ausgeschlossen"]:
                if d1 <= 6.0:
                    hinweise.append(
                        f"S. {pno + 1}: Beschriftung '{raw}' liegt auf {pl1['ausgeschlossen']}: nicht als Wasserlinie uebernommen"
                    )
                continue
            if len(nahe) >= 2:
                d2 = nahe[1][0]
                if d2 <= 8.0 or (d2 - d1) < 4.0:
                    hinweise.append(
                        f"S. {pno + 1}: Wasserlinie unklar (mehrere Linien nahe '{raw}'): nicht uebernommen"
                    )
                    continue

            key = (idx1, art, datum)
            if key in gewaehlt:
                continue
            nhns = [round(a_nhn * y + b_nhn, 2) for _, y in pl1["pts"]]
            konstant = (max(nhns) - min(nhns)) <= 0.05
            nhn_val = round(float(np.median(nhns)), 2) if konstant else round(float(np.mean(nhns)), 2)
            beleg_teile = [f"Laengsschnitt S. {pno + 1}: {raw}"]
            if leg_b:
                beleg_teile.append(leg_b)
            beleg_teile.append(f"{cal_art} R²={r2_nhn:.3f}")
            eintrag: dict = {
                "kind": art,
                "nhn": nhn_val,
                "page": pno,
                "quelle": "Laengsschnitt",
                "confidence": 0.85 if (konstant or st_cal is not None) else 0.75,
                "evidence": "; ".join(beleg_teile),
            }
            if datum:
                eintrag["observed_on"] = datum
            if not konstant:
                if st_cal is not None:
                    ax_s, bx_s = st_cal
                    eintrag["stuetzpunkte"] = [
                        {"station": round(ax_s * x + bx_s, 1), "nhn": round(a_nhn * y + b_nhn, 2)}
                        for x, y in pl1["pts"]
                    ]
                else:
                    eintrag["stuetzpunkte"] = [
                        {"x_pt": round(x, 1), "nhn": round(a_nhn * y + b_nhn, 2)}
                        for x, y in pl1["pts"]
                    ]
            gewaehlt[key] = eintrag

        out.extend(gewaehlt.values())
    return out, hinweise


def _wasserstaende_zusammenfuehren(text_staende: list[dict], ls_staende: list[dict]) -> tuple[list[dict], list[str]]:
    """Fuehrt Wasserstaende aus Berichtstext und Laengsschnitt zusammen (Issue #26 2b).

    Gleiche Art und Hoehe (+/-5 cm, konstant) -> ein Eintrag mit beiden Belegen.
    Widerspruch (> 5 cm) -> beide Eintraege bleiben erhalten, jeweils mit Hinweis.
    """
    ergebnis = [dict(e, quelle=e.get("quelle", "Text")) for e in text_staende]
    hinweise: list[str] = []
    for ls in ls_staende:
        gleich = None
        widerspruch = None
        for idx, t in enumerate(ergebnis):
            if t.get("quelle") != "Text":
                continue
            if t["kind"] != ls["kind"] or t.get("observed_on") != ls.get("observed_on"):
                continue
            if "stuetzpunkte" not in ls and abs(float(t["nhn"]) - float(ls["nhn"])) <= 0.05:
                gleich = idx
                break
            widerspruch = idx
        if gleich is not None:
            t = ergebnis[gleich]
            t["quelle"] = "Text+Laengsschnitt"
            t["belege"] = [t["evidence"], ls["evidence"]]
            t["evidence"] = f"{t['evidence']} | {ls['evidence']}"
            t["confidence"] = 0.95
        elif widerspruch is not None:
            t = ergebnis[widerspruch]
            msg = (f"Widerspruch {ls['kind']}: Text {t['nhn']:.2f} m NHN (S. {t['page'] + 1}) "
                   f"vs. Laengsschnitt {ls['nhn']:.2f} m NHN (S. {ls['page'] + 1})")
            t["hinweis"] = msg
            neu = dict(ls)
            neu["hinweis"] = msg
            ergebnis.append(neu)
            hinweise.append(msg)
        else:
            ergebnis.append(dict(ls))
    return ergebnis, hinweise


def _gw_v(d) -> pymupdf.Point | None:
    """Dach aus zwei Strichen (Λ, ohne Querstrich), das auf der Wasserlinie steht: Mitte der Grundlinie, sonst None.
    Die Form heisst hier 'v' (Legende: z. B. 'angebohrt'); W3."""
    it, r = d["items"], d["rect"]
    if not (len(it) == 2 and all(x[0] == "l" for x in it) and 2 < r.width < 16 and 2 < r.height < 16):
        return None
    (p1, p2), (q1, q2) = (it[0][1], it[0][2]), (it[1][1], it[1][2])
    for a_, b_ in ((p1, p2), (p2, p1)):                      # gemeinsamer Punkt = Spitze oben
        for c_, e_ in ((q1, q2), (q2, q1)):
            if abs(a_.x - c_.x) < 0.6 and abs(a_.y - c_.y) < 0.6:
                if a_.y < b_.y - 1 and a_.y < e_.y - 1 and abs(b_.y - e_.y) < 0.6 and abs(b_.x - e_.x) > 2:
                    return pymupdf.Point((b_.x + e_.x) / 2, (b_.y + e_.y) / 2)
    return None


def _gw_voll(d, drawings) -> bool:
    """Dreieck mit Fuellung (eigene Flaeche im Rahmen des Dreiecks)."""
    r = d["rect"]
    return d.get("fill") is not None or any(e.get("fill") is not None and e["rect"].width < 12 and e["rect"].height < 12
                                            and (e["rect"] & r).get_area() > 0.4 * e["rect"].get_area()
                                            for e in drawings if e is not d)


def gw_legende(drawings, lines) -> dict:
    """W3: Wassersymbole der Legende je Form ('voll', 'offen', 'v') -> Art aus dem Text daneben (gw_info).
    Zusammengesetztes Symbol 'angestiegen' (V unten, volles Dreieck oben): V = Stand beim Anbohren (angetroffen),
    voll = angestiegener Stand. Zwei Eintraege mit verschiedener Art fuer dieselbe Form: unbrauchbar (None)."""
    out: dict[str, str | None] = {}
    tris = [d for d in drawings if len(d["items"]) == 3 and all(x[0] == "l" for x in d["items"])
            and 2 < d["rect"].width < 16 and 2 < d["rect"].height < 16]      # Legende: kleine Symbole
    for r, t in lines:
        if len(t) > 60 or not re.search(r"wasser|angebohrt|angestiegen", t, re.I):
            continue
        k = gw_info(t)["kind"]
        if k == "unbestimmt":
            continue
        band = lambda q: (r.y0 - 14 <= (q.y0 + q.y1) / 2 <= r.y1 + 14 and q.x1 <= r.x0 + 2 and r.x0 - q.x0 < 90)  # noqa: E731
        has_v = any(_gw_v(d) for d in drawings if band(d["rect"]))
        vt = [d for d in tris if band(d["rect"])]
        has_voll = any(_gw_voll(d, drawings) for d in vt)
        has_offen = any(not _gw_voll(d, drawings) for d in vt)
        neu = {}
        if has_v and has_voll:
            neu = {"v": "angetroffen" if "angestieg" in t.lower() else k, "voll": k}
        elif has_v:
            neu = {"v": k}
        elif has_voll:
            neu = {"voll": k}
        elif has_offen:
            neu = {"offen": k}
        for form, art in neu.items():
            out[form] = art if out.get(form, art) == art else None
    return out


def _groundwater(drawings, segs, col: Column, cols: list[Column], fit, words=(), lines=(), info=None):
    """Dreieck mit Spitze nach unten; Zuordnung ueber die waagrechte Wasserlinie. info: Tiefe -> Art/Datum aus dem
    Text am Symbol (Issue #26), sonst aus der Legende je Form (W3)."""
    a, b = fit
    H = [s for s in segs if s.horizontal]
    out = []
    legende = gw_legende(drawings, lines) if RULES["gw_legende"] else {}
    # Hoehenleisten tragen ein Dreieck je Meter: >= 3 gleich ausgerichtete Dreiecke in einer Spalte = Leiste
    tri_x = defaultdict(int)
    for d in drawings:
        if d.get("raster_legend"):
            continue
        it, r = d["items"], d["rect"]
        if len(it) == 3 and all(x[0] == "l" for x in it) and 3 < r.width < 16 and 3 < r.height < 16:
            tri_x[round(r.x0)] += 1
    ruler_x = {x for x, n in tri_x.items() if n >= 3}
    ruler_x_raster = {x for x in list(tri_x) if sum(tri_x.get(k, 0) for k in range(x - 2, x + 3)) >= 3}
    for d in drawings:
        if d.get("raster_legend"):
            continue
        it = d["items"]
        r = d["rect"]
        v_spitze = _gw_v(d) if "v" in legende else None    # V nur, wenn die Legende sie als Wasser kennt (W3)
        if not (len(it) == 3 and all(x[0] == "l" for x in it) and 3 < r.width < 16 and 3 < r.height < 16) \
                and v_spitze is None:
            continue
        rx_set = ruler_x_raster if d.get("raster") else ruler_x
        if RULES["gw_symbol_filter"] and any(abs(round(r.x0) - x) <= (2 if d.get("raster") else 1) for x in rx_set):
            continue
        # Hoehenmarke: Dreieck mit Kote daneben ('741.00m', '~770,17', im Scan auch '741.00mNHN')
        dy_kote = 8 if d.get("raster") else 5
        rx_kote = r"~?[+-]?\d{3,4}[.,]\d{2}\s?(?:m(?:NHN|NN)?)?" if d.get("raster") else r"~?\d{3,4}[.,]\d{2}\s?m?"
        if RULES["gw_symbol_filter"] and any(abs((wr.y0 + wr.y1) / 2 - (r.y0 + r.y1) / 2) < dy_kote
                                             and 0 < wr.x0 - r.x1 < 70 and re.fullmatch(rx_kote, t)
                                             for wr, t, *_ in words):
            continue
        pts = [x[1] for x in it]
        apex = v_spitze or max(pts, key=lambda p: p.y)
        if (v_spitze is None and sum(abs(p.y - apex.y) < 0.5 for p in pts) != 1) or \
                not (col.rect.y0 <= apex.y <= col.rect.y1 + 2):
            continue
        if d.get("raster") and any(c.rect.contains((r.tl + r.br) / 2) for c in cols):
            continue                                        # Bild-Dreieck in einer Saeule = Schraffur
        target = None
        h_cands = [d["wline"]] if d.get("raster") and d.get("wline") else H
        for s in h_cands:                                   # Wasserlinie an der Spitze
            tol_y = 1.8 if d.get("raster") else 1.5
            tol_x = 2.5 if d.get("raster") else 2.0
            if abs(s.y0 - apex.y) < tol_y and s.x0 - tol_x <= apex.x <= s.x1 + tol_x and s.x1 - s.x0 > 15:
                end = s.x1 if abs(s.x1 - apex.x) > abs(s.x0 - apex.x) else s.x0
                cand = min(cols, key=lambda c: min(abs(c.rect.x0 - end), abs(c.rect.x1 - end)))
                if d.get("raster"):
                    # Wasserlinie fuehrt zur Saeule (<= 100 pt) und laeuft nicht quer durch sie hindurch
                    if min(abs(cand.rect.x0 - end), abs(cand.rect.x1 - end)) > 100 \
                            or (s.x0 < cand.rect.x0 - 5 and s.x1 > cand.rect.x1 + 5):
                        continue
                target = cand
        if target is None:
            if d.get("raster") or v_spitze is not None:      # Bild und V nur mit Wasserlinie (sonst Schraffur, Haken)
                continue
            target = min(cols, key=lambda c: max(c.rect.x0 - r.x1, r.x0 - c.rect.x1, 0))
        if target is col:
            depth = round(float(a * apex.y + b), 2)
            if depth > 0.05 or not RULES["gw_symbol_filter"]:   # Dreieck an der GOK = Ansatzpunkt, kein Wasser
                out.append(depth)
                if info is not None and RULES["gw_art"]:
                    gi = gw_info(_gw_text_am(lines, apex.x, apex.y))
                    form = "v" if v_spitze is not None else ("voll" if _gw_voll(d, drawings) else "offen")
                    if gi["kind"] == "unbestimmt" and legende.get(form):
                        gi = {**gi, "kind": legende[form],
                              "evidence": (gi.get("evidence", "") + f" Legende: Symbol {form}").strip()}
                    if depth not in info or info[depth].get("kind") == "unbestimmt":
                        info[depth] = gi
    return sorted(set(out))


SV_CODE_RE = re.compile(r"(?<![A-Za-z0-9])((?:B|BK|KB|KRB|RKS|BS|GWM|SCH)\s*\d+[a-z]?(?:/\d{2})?)(?![\d.,])")
SV_NO_GW_RE = re.compile(r"kein(?:e[nr]?)?\s*(?:Grund)?wasser\w*|Wasser\s*nicht\s*angetroffen", re.I)
SV_GW_RE = re.compile(r"(?:Wasserstand|Wasserspiegel|Grundwasser\w*|Ruhewasser\w*|\bGW)\D{0,40}?(\d{1,2}[.,]\d{1,2})\s*m\b", re.I)
SV_GW_FULL_RE = re.compile(
    r"(?:Wasser(?:stand|spiegel|anschnitt|zutritt)"
    r"|Wasser\s+(?:angetroffen|angebohrt|eingemessen|nach\s+(?:Bohrende|Sondierung)|bei\b|in\b)"
    r"|(?:Grund|Ruhe|Schichten|Stau|Sicker)wasser\w*|\bGW\b)"
    r"(?:(?!(?:\bnicht\b|\bkein\w*\b))[^0-9\n]){0,45}?"
    r"(\d{1,2}[.,]\d{1,2})\s*m(?![A-Za-z0-9])",
    re.I,
)


def schichtenverzeichnis(doc, prims: dict | None = None) -> dict[str, dict]:
    """Formblatt 'Schichtenverzeichnis': Spalte 1 'Bis ... m unter Ansatzpunkt', Spalte 2 Bloecke a) bis i).

    Das Formblatt ist genormt und bei allen Bueros gleich aufgebaut: die Tiefe steht links vom a)-Block,
    im Block steht unter a) die Benennung. Liefert je Aufschluss Unterkanten, Benennung und Wasserangaben.
    """
    out: dict[str, dict] = {}
    for pno, page in enumerate(doc):
        # Primitive aus E1 (gedrehte Seiten, OCR bei Scans) - nie page.get_text() direkt (E3)
        pw, plines = prims[pno] if prims and pno in prims else primitives(page)[:2]
        txt = " ".join(t for _, t in plines)
        if "schichtenverzeichnis" not in re.sub(r"\s", "", txt).lower() or "Ansatz" not in txt:   # 'S c h i c h t e n ...'
            continue
        ws = {(round(r.x0), round(r.y0), t): (r.x0, r.y0, r.x1, r.y1, t) for r, t, *_ in pw}.values()   # doppelter Text
        hdr = [w for w in ws if w[4].startswith("Ansatz")]
        marks = sorted((w for w in ws if w[4] == "a)" or w[4].startswith("a)")), key=lambda w: w[1])  # OCR: 'a)Auffullung' 
        if not hdr or not marks:
            continue
        y_hdr = max(w[3] for w in hdr)
        x_a = min(w[0] for w in marks)
        x_col3 = min([w[0] - 4 for w in ws if re.match(r"Wasserf|Bohrwerkzeug", w[4]) and w[1] < y_hdr]
                     + [page.rect.width * 0.6])                                  # Spalte 3
        blocks = [w for w in marks if w[1] > y_hdr]
        hdr_codes: list[str] = []                           # 'B 1 Bohrung Nr.', 'Nr.: B 1 / Blatt 1', 'RKS 1 - Weg'
        for r, t in sorted(plines, key=lambda e: (e[0].y0, e[0].x0)):
            if r.y1 <= y_hdr:
                for m in SV_CODE_RE.finditer(re.sub(r"\s+", " ", t)):
                    if ckey(m.group(1)) not in {ckey(c) for c in hdr_codes}:
                        hdr_codes.append(m.group(1))
        code = hdr_codes[0] if hdr_codes else None
        if code is None or not blocks:
            continue
        rec = out.setdefault(ckey(code), {"code": code, "bottoms": [], "names": [], "gw": [], "gw_status": None,
                                          "pages": [], "gw_info": {}})
        rec["pages"].append(pno + 1)
        depths = sorted((w for w in ws if w[2] <= x_a + 1 and w[1] > y_hdr and DEPTH_RE.match(w[4])), key=lambda w: w[1])
        for d in depths:
            blk = [b for b in blocks if b[1] < d[1]]
            if not blk:
                continue
            b = blk[-1]
            y_b = min([w[1] for w in ws if w[4] == "b)" and w[1] > b[1] + 1] + [b[1] + 12])
            name_ws = [w for w in ws if b[1] - 3 <= w[1] < y_b - 1 and w[0] > b[2] and w[0] < x_col3 - 2]
            if RULES["line_reading_order"]:
                name = " ".join(t for _, t in rows([(pymupdf.Rect(w[:4]), w[4]) for w in name_ws], dy=3.0))
            else:
                name = " ".join(w[4] for w in sorted(name_ws, key=lambda w: (round(w[1]), w[0])))
            if b[4] != "a)":                                 # Benennung klebt am Marker (OCR)
                name = (b[4][2:] + " " + name).strip()
            rec["bottoms"].append(float(d[4].rstrip("m ").replace(",", ".")))
            rec["names"].append(name)
        if RULES["sv_wasser"]:
            if len(hdr_codes) == 1:                         # nur wenn das SV-Blatt eindeutig zu einer Bohrung gehoert
                x_col4 = min([w[0] - 4 for w in ws if re.match(r"Entnommene|Art$", w[4])
                              and w[1] < y_hdr + 30 and w[0] > x_col3 + 20] + [page.rect.width])
                col3_ws = sorted((w for w in ws if x_col3 - 25 <= w[0] < x_col4 and w[1] > y_hdr),
                                 key=lambda w: (round(w[1] / 3), w[0]))
                col2_ws = sorted((w for w in ws if x_a - 2 <= w[0] < x_col3 - 4 and w[1] > y_hdr),
                                 key=lambda w: (round(w[1] / 3), w[0]))
                cells: list[str] = []
                for cws in (col3_ws, col2_ws):
                    cur: list[str] = []
                    last_y = None
                    for w in cws:
                        if last_y is not None and w[1] - last_y > 16:
                            cells.append(" ".join(cur))
                            cur = []
                        cur.append(w[4])
                        last_y = w[1]
                    if cur:
                        cells.append(" ".join(cur))
                for s_txt in cells:
                    for m in SV_GW_FULL_RE.finditer(s_txt):
                        if re.search(r"\bkein\w*\s*$", s_txt[max(0, m.start() - 15):m.start()], re.I):
                            continue
                        beleg = " ".join(s_txt[max(0, m.start() - 25):min(len(s_txt), m.end() + 30)].split())
                        if {ckey(c.group(1)) for c in SV_CODE_RE.finditer(beleg)} - {ckey(code)}:
                            continue
                        d = float(m.group(1).replace(",", "."))
                        rec["gw"].append(d)
                        if RULES["gw_art"]:
                            gi = gw_info(beleg)
                            if beleg:
                                gi.setdefault("evidence", beleg[:120])
                            rec["gw_info"].setdefault(d, gi)
                    if not rec["gw"] and SV_NO_GW_RE.search(s_txt):
                        rec["gw_status"] = "kein Grundwasser"
        else:
            flat = " ".join(txt.split())
            for m in SV_GW_RE.finditer(flat):
                d = float(m.group(1).replace(",", "."))
                rec["gw"].append(d)
                if RULES["gw_art"]:                         # Stichwort davor, Datum dahinter ('Ruhewasser 3.62m u. AP 14.04.2020')
                    rec["gw_info"].setdefault(d, gw_info(flat[max(0, m.start() - 25):m.end() + 30]))
            if SV_NO_GW_RE.search(flat):
                rec["gw_status"] = "kein Grundwasser"
    return {k: v for k, v in out.items() if v["bottoms"]}


def _schriftfeld_nummer(r: pymupdf.Rect, code: str, lines) -> bool:
    """T6: 'Projekt-Nr.: B 231411' - mehr als 4 Ziffern oder ein Nummernfeld links in derselben Zeile."""
    if (m := re.search(r"\d+", code)) and len(m.group(0)) > 4:
        return True
    return any(abs(q.y0 - r.y0) < 3 and q.x1 <= r.x0 + 2 and r.x0 - q.x1 < 80 and SCHRIFTFELD_RE.search(u.strip())
               for q, u in lines)


def find_heads(lines) -> list[tuple[pymupdf.Rect, str]]:
    """E2: Koepfe. Kuerzel (mit Zusatz), 'Bohrung <Code>' (auch zweizeilig), Archivcodes."""
    heads = []
    for r, t in lines:
        t = re.sub(r"\s+", " ", t.strip())
        if RULES["station_heads"] and (m := STATION_HEAD_RE.match(t)):
            heads.append((r, m.group(1)))
            continue
        m = HEAD_RE.match(t) if RULES["head_suffix"] else ID_RE.match(t)
        if m and RULES["kein_schriftfeld_code"] and _schriftfeld_nummer(r, m.group(1) if RULES["head_suffix"] else m.group(0), lines):
            continue
        if m:
            heads.append((r, re.sub(r"\s+", " ", m.group(1) if RULES["head_suffix"] else m.group(0))))
            continue
        if not RULES["generic_heads"]:
            continue
        if (m := ARCHIVE_HEAD_RE.match(t)):
            heads.append((r, m.group(1)))
        elif (m := GENERIC_HEAD_RE.match(t)):
            code = m.group(1)
            if not code:                                  # 'Bohrung' / naechste Zeile '422C-460' (OCR: 'RB' + '2 / I')
                below = sorted([(q, u.strip()) for q, u in lines if -4 < q.y0 - r.y1 < 14
                                and q.x0 < r.x1 + 40 and q.x1 > r.x0 - 40], key=lambda e: (e[0].y0, e[0].x0))
                if below:
                    row = [e for e in below if abs(e[0].y0 - below[0][0].y0) < 3]
                    cand = re.sub(r"\s+", " ", " ".join(u for _, u in sorted(row, key=lambda e: e[0].x0)))
                    if FREE_CODE_RE.fullmatch(cand):
                        code = cand
                        for q, _ in row:
                            r = r | q
            if code and FREE_CODE_RE.fullmatch(code) and re.search(r"\d", code) and not DEPTH_RE.match(code) \
                    and not DATE_RE.search(code):
                heads.append((r, re.sub(r"\s*/\s*", "/", code)))
    return heads


def rows(lines, dy: float = 3.0) -> list[tuple]:
    """Zeilen derselben Hoehe zusammenfuegen (Schriftfeld: 'Hoehe in m ue.M.:' und '668.99' sind getrennte Bloecke)."""
    out: list[list] = []
    for r, t in sorted(lines, key=lambda e: (e[0].y0, e[0].x0)):
        if out and abs(out[-1][0].y0 - r.y0) < dy:
            out[-1][0] = out[-1][0] | r
            out[-1][1].append((r.x0, t))
        else:
            out.append([pymupdf.Rect(r), [(r.x0, t)]])
    return [(r, " ".join(t for _, t in sorted(parts))) for r, parts in out]


def page_gok(lines, y_max: float) -> float | None:
    """Ansatzhoehe aus dem Schriftfeld: 'NHN 45,20 m', 'Hoehe in m ue.M.: 668.99', 'Kote Bezugspunkt: ~788.6 m ue. M.'."""
    for r, t in rows(lines):
        if r.y0 > y_max:
            break
        if (m := GOK_RE.search(t)) or (m := GOK_EXTRA_RE.search(t)):
            return float((m.group(1) or m.group(2)).replace(",", "."))
    return None


def depth_table(words, lines, heads):
    """S6: Schichtenliste als Texttabelle - Spalte streng steigender Tiefen ab 0,00, Beschreibung rechts.

    Nur wenn die Seite genau einen Kopf hat und >= 60 % der Intervalle eine Bodenart ergeben
    (Rammsondier- und Labortabellen enthalten Zahlen, keine Bodenbeschreibung).
    """
    if len({c for _, c in heads}) != 1:
        return None
    groups: dict[int, list] = defaultdict(list)
    for r, t, *_ in words:
        if DEPTH_RE.match(t) and float(t.rstrip("m ").replace(",", ".")) <= 150:
            groups[round(r.x1 / 6)].append((r, float(t.rstrip("m ").replace(",", "."))))
    best = None
    for g in groups.values():
        g = _longest_non_decreasing(sorted(g, key=lambda e: e[0].y0))
        if len(g) < 4 or g[0][1] != 0.0 or _arithmetic(g) or any(b[1] <= a[1] for a, b in zip(g, g[1:])):
            continue
        x1 = max(r.x1 for r, _ in g)
        descs = [" ".join(t for r, t in sorted(lines, key=lambda e: e[0].y0)
                          if x1 + 8 < r.x0 < x1 + 320 and ra.y0 - 2 <= r.y0 < rb.y0 - 2)
                 for (ra, _), (rb, _) in zip(g, g[1:])]
        if sum(bool(classify_v3(d.split(",")[0]) or classify_v3(d)) for d in descs) < 0.6 * len(descs):
            continue
        if best is None or len(g) > len(best[0]):
            best = (g, descs)
    return best


def coords_from_text(lines, anchored) -> dict[str, tuple[float, float, int | None]]:
    """E8: 'Rechtswert (UTM 33N): 394774,3' / 'Hochwert ...' -> naechster Kopf derselben Seite."""
    es, ns = [], []
    for r, t in lines:
        tt = t.replace(" ", "")
        if (m := COORD_E_RE.search(tt)):
            es.append((r, float(m.group(1).replace(",", ".")), UTM_ZONE_RE.search(tt)))
        if (m := COORD_N_RE.search(tt)):
            ns.append((r, float(m.group(1).replace(",", "."))))
    out = {}
    for r, t in rows(lines):
        if (m := LV_COORD_RE.search(t)) and anchored:
            e, n = (float(re.sub(r"[ '’]", "", v).replace(",", ".")) for v in m.groups())
            epsg = 21781 if 480000 <= e <= 840000 and 70000 <= n <= 300000 else \
                2056 if 2480000 <= e <= 2840000 and 1070000 <= n <= 1300000 else None
            if epsg:
                out[anchored[0][1]] = (e, n, epsg)
    for re_, e, zone in es:
        n = min(ns, key=lambda q: abs(q[0].x0 - re_.x0) + abs(q[0].y0 - re_.y0), default=None)
        if n is None or abs(n[0].y0 - re_.y0) > 40:
            continue
        if not anchored:
            continue
        cx = (re_.x0 + re_.x1) / 2
        hr, code, col = min(anchored, key=lambda a: abs(((a[2].rect if a[2] else a[0]).x0
                                                        + (a[2].rect if a[2] else a[0]).x1) / 2 - cx))
        epsg = None
        if 200000 <= e <= 900000 and 5000000 <= n[1] <= 6200000:      # UTM ohne Zonenvorsatz
            epsg = 25800 + int(zone.group(1)) if zone else None
        elif 2000000 <= e <= 5999999:                                   # Gauss-Krueger, Zone = 1. Ziffer
            epsg = 31464 + int(str(int(e))[0])
        out[code] = (e, n[1], epsg)
    return out


def extract(pdf: Path):
    doc = pymupdf.open(pdf)
    swatches = []
    found: dict[str, list[Borehole]] = defaultdict(list)
    dph = {}
    xy_text: dict[str, tuple] = {}
    prims: dict[int, tuple] = {}
    for pno, page in enumerate(doc):
        words, lines, drawings, segs, scanned, pclass = primitives(page)
        prims[pno] = (words, lines)                       # einmal je Seite (OCR!), auch fuer das SV
        if any("BODENARTEN" in t.upper() for _, t in lines) and not swatches:
            from prototyp_v2 import legend_swatches
            swatches = legend_swatches(page)
        if page.rotation == 0:
            dph.update(soundings(page))
        cols = find_columns(segs, merge_tol=1.6 if scanned else 0.8)   # Scans zeichnen Linien doppelt
        scale_txt = [int(m) for _, t in lines for m in SCALE_RE.findall(t)]
        heads = find_heads(lines)
        anchored: list[tuple] = []
        used = set()
        for hr, code in heads:
            hx = (hr.x0 + hr.x1) / 2
            # bei hoehenmaessiger Darstellung steht der Kopf weit ueber der Saeule -> keine y-Grenze
            cand = [c for c in cols if c.rect.y0 > hr.y1 and abs((c.rect.x0 + c.rect.x1) / 2 - hx) < 70
                    and id(c) not in used]
            if RULES["table_filter"]:                    # Spalte voller Tiefenzahlen = Tiefenspalte des Formblatts
                cand = [c for c in cand if sum(1 for r, t, *_ in words if c.rect.contains(r) and DEPTH_RE.match(t)) < 3]
            if not cand:
                continue
            col = max(cand, key=lambda c: (round(c.weight, 1), len(c.bounds), -(c.rect.y0 - hr.y1),
                                           -abs((c.rect.x0 + c.rect.x1) / 2 - hx)))
            used.add(id(col))
            anchored.append((hr, code, col))
        sheet_anchor = False
        if RULES["single_sheet_anchor"] and not anchored and cols and len({c for _, c in heads}) == 1:
            # Einzelblatt: ein Kopf, irgendwo; das Profil ist die Saeule mit den meisten bestaetigten Labels
            # Labels je Kandidat ohne Konkurrenz zuordnen: im Formblatt steht die Tiefenspalte selbst als 'Saeule'
            scored = []
            for c in cols:
                gs = label_groups(words, c, [c])
                ch = choose_scale(c, gs, scale_txt)
                lf = label_line(gs) if RULES["label_first"] else None
                sc = max(ch[4] if ch else 0, len(lf[2]) if lf else 0)
                if sc >= 3:
                    scored.append((sc, len(c.bounds), c))
            scored = [(sc, c) for sc, _, c in sorted(scored, key=lambda e: (e[0], e[1]))]
            if scored:
                anchored = [(heads[0][0], heads[0][1], max(scored, key=lambda e: e[0])[1])]
                sheet_anchor = True
        # Tabellen aussortieren: in einer Bodensaeule stehen hoechstens kurze Kuerzel, keine Zahlenreihen
        if RULES["table_filter"]:
            anchored = [(hr, code, c) for hr, code, c in anchored
                        if sum(1 for r, t, *_ in words if c.rect.contains(r) and re.search(r"\d", t)
                               and not re.fullmatch(r"[0Oo]+", t)) <= 2]     # OCR liest Kies-Kreise als '000'
        acols = [c for _, _, c in anchored]
        if scanned and acols and RULES["raster_gw_symbol"]:
            drawings = drawings + raster_gw_symbols(page, cols, acols, lines)
        groups_all = [label_groups(words, c, [c] if sheet_anchor else acols, scanned=scanned) for _, _, c in anchored]
        chosen_all = [choose_scale(c, gs, scale_txt) for (_, _, c), gs in zip(anchored, groups_all)]
        page_has_labels = any(ch and ch[4] > 0 for ch in chosen_all)
        if RULES["coords_text"]:
            xy_text.update(coords_from_text(lines, anchored))
        for (hr, code, col), gs, chosen in zip(anchored, groups_all, chosen_all):
            hx = (hr.x0 + hr.x1) / 2
            gok = None
            for r, t in lines:
                if hr.y0 - 2 <= r.y0 <= col.rect.y0 + 4 and abs((r.x0 + r.x1) / 2 - hx) < 90 and (m := GOK_RE.search(t)):
                    gok = float((m.group(1) or m.group(2)).replace(",", "."))
                elif RULES["gok_unter_kopf"] and hr.y0 - 2 <= r.y0 <= col.rect.y0 + 4 \
                        and abs((r.x0 + r.x1) / 2 - hx) < 90 and (m := GOK_UE_NN_RE.search(t)):
                    gok = float(m.group(1).replace(",", "."))   # '193,01 m ü. NN', 'Ansatzpunkt: 476.76 m NHN'

            if gok is None and RULES["gok_unter_kopf"]:     # T8: '216.31 m' allein zwischen Kopf und Saeule (#54)
                unter = [r_t for r_t in lines if hr.y1 - 2 <= r_t[0].y0 and r_t[0].y1 <= col.rect.y0 + 1
                         and abs((r_t[0].x0 + r_t[0].x1) / 2 - hx) < 60 and GOK_ALLEIN_RE.match(r_t[1].strip())]
                if len(unter) == 1:
                    gok = float(GOK_ALLEIN_RE.match(unter[0][1].strip()).group(1).replace(",", "."))
            if gok is None and sheet_anchor:                  # Einzelblatt: Kopfdaten irgendwo ueber dem Profil
                gok = page_gok(lines, col.rect.y0)
            ruler_fit = raster_ruler_scale(words, col, [col] if sheet_anchor else acols, gok) \
                if (scanned and RULES["raster_massstab_ocr"]) else None
            if chosen is None and ruler_fit is not None:
                ra, rb = ruler_fit
                g0 = gs[0] if gs else []
                pairs_r = [(y, v) for _, v in g0 for y in col.bounds if abs(ra * y + rb - v) <= 0.04]
                chosen = (ra, rb, "lineal-ocr", pairs_r, label_support(col, g0, ra, rb, tol=0.04), len(g0))
            if chosen is None:
                continue
            a, b, mode, pairs, support, n_labels = chosen
            if support == 0 and page_has_labels and RULES["labelless_column"] and not sheet_anchor \
                    and mode != "lineal-ocr":
                continue                                    # Nachbarsaeulen haben Labels, diese nicht: Ausbau o. ae.
            lf = None
            if RULES["label_first"] and n_labels >= 5 and support < 0.5 * n_labels:
                lf = label_line(gs)
            if RULES["scale_contradiction"] and scanned and RULES["raster_massstab_ocr"] \
                    and ruler_fit is not None and gs and len(gs[0]) >= 3:
                ra, rb = ruler_fit
                g0 = gs[0]
                sup_r = label_support(col, g0, ra, rb, tol=0.05)
                max_v = max(v for _, v in g0)
                d_col_r = ra * (col.bounds[-1] - col.bounds[0])
                lf_widerspruch = lf is not None and abs(ra - lf[0]) / lf[0] > 0.12
                ohne_lf_widerspruch = lf is None and (
                    abs(d_col_r - max_v) > max(0.15, 0.03 * max_v)
                    or (mode in ("direkt", "reihenfolge") and abs(ra - a) / a > 0.12)
                )
                if sup_r < 0.3 * len(g0) and (lf_widerspruch or ohne_lf_widerspruch):
                    bh = Borehole(code, pno + 1, None, f"widerspruch ({sup_r}/{len(g0)} Labels)", gok)
                    bh.page_class, bh.bbox = pclass, tuple(round(v, 1) for v in col.rect)
                    bh.issues.append("Tiefenlineal und Grenzbeschriftungen widersprechen sich: Massstab verworfen")
                    found[ckey(code)].append(bh)
                    continue
            if not lf and RULES["scale_contradiction"] and mode in ("massstab-text", "lineal-ocr") and n_labels >= 3 \
                    and support < 0.3 * n_labels:
                # Im Scan fehlen oft die inneren Schichtlinien (len(bounds) == 2), waehrend Lineal oder M 1:n + GOK
                # und die Endtiefe am Saeulenfuss uebereinstimmen -> Tiefenmassstab fuer Wasserstaende nutzbar (E5/W5)
                max_v = max(v for _, v in gs[0]) if gs and gs[0] else 0.0
                d_col = a * (col.bounds[-1] - col.bounds[0])
                ocr_scale_ok = (scanned and RULES["raster_massstab_ocr"] and len(col.bounds) <= 2
                                and (ruler_fit is not None or (bool(scale_txt) and gok is not None))
                                and (ruler_fit is None or abs(ruler_fit[0] - a) / a <= 0.08)
                                and abs(d_col - max_v) <= max(0.08, 0.015 * max_v))
                if not ocr_scale_ok:
                    # Massstabstext/Lineal widerspricht den Labels (verkleinerter Druck): Schichten nicht raten
                    bh = Borehole(code, pno + 1, None, f"widerspruch ({support}/{n_labels} Labels)", gok)
                    bh.page_class, bh.bbox = pclass, tuple(round(v, 1) for v in col.rect)
                    bh.issues.append("Massstabstext und Tiefenlabels widersprechen sich: Schichten nicht ausgegeben")
                    found[ckey(code)].append(bh)
                    continue
                fit = (float(a), float(b))
                bh = Borehole(code, pno + 1, round(a / PT_TO_M_AT_1_1), f"lineal-ocr ({support}/{n_labels} Labels)", gok)
                bh.page_class, bh.bbox, bh.fit = pclass, tuple(round(v, 1) for v in col.rect), fit
                bh.issues.append("Innere Schichtlinien im Scan nicht erkannt: Tiefenmassstab aus OCR fuer Wasserstand")
                bh.gw_depths = _groundwater(drawings, segs, col, acols, fit, words, lines, bh.gw_info)
                near = rows([(r, t) for r, t in lines if hr.y0 - 2 <= r.y0 <= col.rect.y1 + 60
                             and abs((r.x0 + r.x1) / 2 - (col.rect.x0 + col.rect.x1) / 2) < 170])
                if not bh.gw_depths and RULES["gw_text"]:
                    for _, t in near:
                        if m := GW_TEXT_RE.search(t):
                            d = float((m.group(1) or m.group(2)).replace(",", "."))
                            if RULES["gw_art"]:
                                bh.gw_info.setdefault(d, gw_info(t))
                            bh.gw_depths.append(d)
                    bh.gw_depths = sorted(set(bh.gw_depths))
                if not bh.gw_depths and any(NO_GW_RE.search(t) for _, t in near):
                    bh.gw_status = "kein Grundwasser"
                found[ckey(code)].append(bh)
                continue
            if lf:                                           # T4: Grenzen = gedruckte Werte, Linien bestaetigen
                la, lb, g = lf
                bh = Borehole(code, pno + 1, round(la / PT_TO_M_AT_1_1), f"labels ({len(g)} Labels)", gok)
                bh.page_class, bh.fit, bh.support = pclass, (la, lb), len(g) / max(n_labels, 1)
                bh.bbox = tuple(round(v, 1) for v in col.rect)
                line_d = [la * y + lb for y in col.bounds]
                prev = 0.0
                for _, v in sorted(g, key=lambda e: e[1]):
                    if v <= prev:
                        continue
                    ly = Layer(prev, v, label_confirmed=True)
                    if not any(abs(d - v) <= 0.3 for d in line_d):
                        ly.issues.append("Label ohne Linie in +-0,3 m")
                    bh.layers.append(ly)
                    prev = v
                _assign_text(bh, col, lines, words, (la, lb), "labels", [(None, v) for _, v in g],
                             min([c.rect.x0 for c in acols if c.rect.x0 > col.rect.x1 + 5] + [page.rect.x1]))
                if any(NO_GW_RE.search(t) for _, t in lines):
                    bh.gw_status = "kein Grundwasser"
                found[ckey(code)].append(bh)
                continue
            fit = (a, b)
            bh = Borehole(code, pno + 1, round(a / PT_TO_M_AT_1_1), f"{mode} ({support}/{n_labels} Labels)", gok)
            bh.page_class = pclass
            bh.bbox = tuple(round(v, 1) for v in col.rect)
            bh.fit = (float(a), float(b))
            bh.support = support / n_labels if n_labels else 0.0
            bh.single_sheet = len(anchored) == 1                  # Einzelblatt schlaegt Schnitt/Uebersicht
            bh.titled = any(re.search(rf"(Bohrung|Bohrprofil|Profil|Sondierung)\s+{re.escape(code)}\b", t)
                            for _, t in lines)                     # Schriftfeld 'Bohrung B 4'
            bounds = list(col.bounds)
            depths = [round(float(a * y + b), 2) for y in bounds[1:]]
            confirmed = set()                                   # 1:1 - jedes Label bestaetigt nur die naechste Grenze
            label_by_y = {}                                     # Linie (y) -> gedruckter Wert
            for v in {round(v, 2) for _, v in pairs}:
                i = min(range(len(depths)), key=lambda k: abs(depths[k] - v), default=None)
                if i is not None and abs(depths[i] - v) <= 0.03:
                    confirmed.add(i)
                    label_by_y[bounds[i + 1]] = v
            dropped = []
            if RULES["hatch_continuity"] and bh.support >= 0.6:   # E5: Schraffurlinien statt Grenzen (L6)
                drop = set()
                inner = range(1, len(bounds) - 1)               # bounds[i] <-> depths[i - 1]
                for i in inner:
                    if (i - 1) in confirmed:
                        continue
                    # Begleitlinie: <= 2,5 pt neben einer bestaetigten Grenze (doppelt gezeichnete Linie)
                    if any(abs(bounds[i] - bounds[j]) <= 2.5 for j in inner if (j - 1) in confirmed):
                        drop.add(i)
                    # Doppellinie: zwei unbestaetigte Linien <= 8 pt, dazwischen keine Schraffur (Schwarzdecke)
                    j = i + 1
                    if j in inner and (j - 1) not in confirmed and bounds[j] - bounds[i] <= 8 and \
                            not np.any(hatch_features(drawings, pymupdf.Rect(col.rect.x0 + 0.5, bounds[i] + 0.5,
                                                                             col.rect.x1 - 0.5, bounds[j] - 0.5))):
                        drop |= {i, j}
                if drop:
                    dropped = [depths[i - 1] for i in sorted(drop)]
                    bounds = [y for i, y in enumerate(bounds) if i not in drop]
                    depths = [round(float(a * y + b), 2) for y in bounds[1:]]
                    confirmed = {i for i, y in enumerate(bounds[1:]) if y in label_by_y}
            prev = 0.0
            for i, y in enumerate(bounds[1:]):
                # bestaetigte Grenze: gedruckter Wert statt Geometrie (Zeichengenauigkeit +-1 pt)
                d = label_by_y.get(y, depths[i]) if RULES["label_snap"] else depths[i]
                ly = Layer(prev, d, label_confirmed=i in confirmed)
                if not ly.label_confirmed:
                    ly.issues.append("Grenze ohne bestaetigendes Label")
                rect = pymupdf.Rect(col.rect.x0, a and (prev - b) / a, col.rect.x1, y)
                ly.soil_hatch, _ = classify_hatch(hatch_features(drawings, rect), swatches) if swatches else ("", 0)
                bh.layers.append(ly)
                prev = d
            if dropped:
                bh.issues.append(f"Linien ohne Label mit gleicher Schraffur ober-/unterhalb entfernt: {dropped}")
            right_limit = min([c.rect.x0 for c in acols if c.rect.x0 > col.rect.x1 + 5] + [page.rect.x1])
            _assign_text(bh, col, lines, words, fit, mode, pairs, right_limit)
            bh.gw_depths = _groundwater(drawings, segs, col, acols, fit, words, lines, bh.gw_info)
            near = [(r, t) for r, t in lines if hr.y0 - 2 <= r.y0 <= col.rect.y1 + 60
                    and abs((r.x0 + r.x1) / 2 - (col.rect.x0 + col.rect.x1) / 2) < 170]
            near = rows(near)                                # 'GW' und '2.53m' als getrennte Bloecke (S7)
            if not bh.gw_depths and RULES["gw_text"]:       # Symbol als Schriftzeichen: 'GW 2.53m' im Text
                for _, t in near:
                    if m := GW_TEXT_RE.search(t):
                        d = float((m.group(1) or m.group(2)).replace(",", "."))
                        if RULES["gw_art"]:
                            bh.gw_info.setdefault(d, gw_info(t))
                        bh.gw_depths.append(d)
                bh.gw_depths = sorted(set(bh.gw_depths))
            if not bh.gw_depths and RULES["gw_description"]:  # 'Wasseranschnitt 3.8' in der Beschreibung
                desc = [(r, t) for r, t in lines if col.rect.y0 - 4 <= r.y0 <= col.rect.y1 + 4
                        and col.rect.x1 < r.x0 < right_limit]
                for _, t in desc:
                    if m := WATER_DESC_RE.search(t.replace(" ", "")):
                        d = float(m.group(1).replace(",", "."))
                        if RULES["gw_art"]:
                            bh.gw_info.setdefault(d, gw_info(t))
                        bh.gw_depths.append(d)
                bh.gw_depths = sorted(set(bh.gw_depths))
            if not bh.gw_depths and any(NO_GW_RE.search(t) for _, t in near):
                bh.gw_status = "kein Grundwasser"
            found[ckey(code)].append(bh)
        if RULES["depth_table"] and heads and not anchored and (tab := depth_table(words, lines, heads)):
            g, descs = tab
            code = heads[0][1]
            bh = Borehole(code, pno + 1, None, f"tabelle ({len(g)} Tiefen)", page_gok(lines, g[0][0].y0))
            bh.page_class = pclass
            bh.support = 1.0
            for (ra, va), (rb, vb), d in zip(g, g[1:], descs):
                bh.layers.append(Layer(va, vb, classify_v3(d.split(",")[0]) or classify_v3(d), label_confirmed=True, text=d))
            if scanned and RULES["raster_gw_symbol"] and len(g) >= 3:
                # Gescanntes massstaebliches Profil ohne dunklen Saeulenrand (E7): Gerade durch die Label-Grundlinien
                ys = np.array([r.y1 for r, _ in g])
                vs = np.array([v for _, v in g])
                a_, b_ = np.polyfit(ys, vs, 1)
                if a_ > 0 and float(np.max(np.abs(np.polyval([a_, b_], ys) - vs))) <= 0.15:
                    y0_c, y1_c = float((0 - b_) / a_), float((vs[-1] - b_) / a_)
                    x_g = float(np.median([r.x0 for r, _ in g]))
                    vcol = Column(pymupdf.Rect(x_g - 25, y0_c, x_g, y1_c), [], 0.0)
                    r_draw = drawings + raster_gw_symbols(page, cols + [vcol], [vcol], lines)
                    bh.gw_depths = _groundwater(r_draw, segs, vcol, [vcol], (float(a_), float(b_)),
                                                words, lines, bh.gw_info)
            if not bh.gw_depths and any(NO_GW_RE.search(t) for _, t in lines):
                bh.gw_status = "kein Grundwasser"
            if RULES["coords_text"]:
                xy_text.update(coords_from_text(lines, [(heads[0][0], code, None)]))
            found[ckey(code)].append(bh)
    coords = {ckey(k): v for k, v in coordinate_table(doc).items()}
    xy_text = {ckey(k): v for k, v in xy_text.items()}
    sv = schichtenverzeichnis(doc, prims) if RULES["sv_source"] else {}
    out = []
    for code, versions in found.items():               # code = ckey
        # GOK gefunden, Labels bestaetigen, groesster Massstab (= kleinste Zahl)
        # schwache Bestaetigung (< 50 %) zaehlt nicht mehr als keine
        if RULES["dup_preference"]:
            best = max(versions, key=lambda v: (bool(v.layers), v.gok is not None, v.titled, v.single_sheet,
                                                not v.mode.startswith("labels"),      # Linien+Labels vor nur Labels
                                                round(v.support, 1) if v.support >= 0.5 else 0.0, -(v.scale or 1e9)))
        else:
            best = max(versions, key=lambda v: v.support)
        best.duplicates = [f"S.{v.page} M1:{v.scale}" for v in versions if v is not best]
        if code in coords:
            best.east, best.north = coords[code]
            best.coord_source = "tabelle"
        elif code in xy_text:
            best.east, best.north, best.crs = xy_text[code]
            best.coord_source = "text"
        if rec := sv.get(code):
            _cross_check(best, rec)
        out.append(best)
    for code, rec in sv.items():                            # nur im Schichtenverzeichnis (Profil = Bild/SHX)
        if code in found:
            continue
        bh = Borehole(rec["code"], rec["pages"][0], None, "schichtenverzeichnis", gw_depths=sorted(set(rec["gw"])),
                      gw_status=None if rec["gw"] else rec["gw_status"], gw_info=dict(rec.get("gw_info") or {}))
        prev = 0.0
        for d, name in zip(rec["bottoms"], rec["names"]):
            bh.layers.append(Layer(prev, d, classify_v3(name.split(",")[0]) or classify_v3(name),
                                   label_confirmed=True, text=name))
            prev = d
        bh.cross_check = "nur SV"
        out.append(bh)
    if RULES["doppel_anderer_code"]:                  # T11: dieselbe Bohrung unter zwei Codes (Schnitt vs. Blatt)
        out = _doppel_anderer_code(out)
    if RULES["gw_blaue_labels"]:
        _blaue_wasserlabels(doc, out)
    if RULES["doppel_labels"]:
        _doppel_labels(doc, out)
    for bh in out:
        _confidence(bh)
    return out, dph


def _doppel_anderer_code(bhs: list) -> list:
    """T11 (#54): gleiche GOK (+-1 cm), dieselben Grenzen (gleiche Anzahl, je +-3 cm, >= 3) und dieselbe Nummer bzw.
    Station im Code ('B-8+180-G' / 'B-8+180-S3', 'B 4' / 'B 4a') = dieselbe Bohrung (Schnitt beschriftet anders als das Einzelblatt). Das Einzelblatt bleibt, der Code des anderen
    steht als Hinweis daneben; eine zweite Bohrung waere falsch."""
    raus: set[int] = set()
    for i, a in enumerate(bhs):
        for j in range(i + 1, len(bhs)):
            b = bhs[j]
            if i in raus or j in raus or a.gok is None or b.gok is None or abs(a.gok - b.gok) > 0.01:
                continue
            kern = [re.search(r"\d+(?:\+\d{3})?", c) for c in (a.code, b.code)]
            if not all(kern) or kern[0].group(0) != kern[1].group(0):
                continue                                  # BS 73 / BS 85: gleiche GOK und 5-m-Raster sind Zufall (Runde 6)
            ga, gb = [ly.bottom for ly in a.layers], [ly.bottom for ly in b.layers]
            if len(ga) < 3 or len(ga) != len(gb) or any(abs(x - y) > 0.03 for x, y in zip(ga, gb)):
                continue
            halten, weg = (a, b) if (a.single_sheet, a.titled) >= (b.single_sheet, b.titled) else (b, a)
            halten.issues.append(f"Dieselbe Bohrung als '{weg.code}' auf S.{weg.page} (gleiche GOK und Grenzen)")
            halten.duplicates.append(f"S.{weg.page} als {weg.code}")
            raus.add(j if weg is b else i)
    return [b for k, b in enumerate(bhs) if k not in raus]


WL_RE = re.compile(r"^(\d{1,2}[.,]\d{2})\s*m?\s*(?:\(\s*([+-]?\d{1,4}[.,]\d{2})\s*\))?$")


DOPPEL_RE = re.compile(r"^(\d{1,2}[.,]\d{2})\s*\(\s*([+-]?\d{1,4}[.,]\d{2})\s*\)$")


def _doppel_labels(doc, boreholes) -> None:
    """T9 (#54): traegt jede Grenze ein Label 'Tiefe (Hoehe)' mit Tiefe + Hoehe = GOK, ist eine Linie ohne Label keine
    Grenze (Schraffur, Probe, Fuehrungslinie). Nur wenn alle Doppellabels der Saeule eine bestaetigte Grenze sind."""
    zeilen: dict[int, list] = {}
    for bh in boreholes:
        if not (bh.bbox and bh.gok is not None and bh.mode != "schichtenverzeichnis" and len(bh.layers) > 1):
            continue
        if bh.page - 1 not in zeilen:
            zeilen[bh.page - 1] = [(pymupdf.Rect(ln["bbox"]), " ".join(sp["text"] for sp in ln["spans"]).strip())
                                   for blk in doc[bh.page - 1].get_text("dict")["blocks"] for ln in blk.get("lines", [])]
        x0, y0, x1, y1 = bh.bbox
        werte = []
        for r, t in zeilen[bh.page - 1]:
            if (m := DOPPEL_RE.match(t)) and x1 - 5 <= r.x0 <= x1 + 120 and y0 - 5 <= r.y0 <= y1 + 40:
                d, h = float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))
                if abs(d + h - bh.gok) <= 0.05:
                    werte.append(d)
        bestaetigt = [ly.bottom for ly in bh.layers if ly.label_confirmed]
        if len(werte) < 2 or not all(any(abs(w - g) <= 0.02 for g in bestaetigt) for w in werte):
            continue
        k = 0
        while k < len(bh.layers) - 1:
            ly = bh.layers[k]
            if not ly.label_confirmed and not any(abs(ly.bottom - w) <= 0.02 for w in werte):
                nx = bh.layers.pop(k + 1)
                bh.issues.append(f"Grenze {ly.bottom} m ohne Label 'Tiefe (Hoehe)' verworfen")
                ly.bottom, ly.soil, ly.text = nx.bottom, ly.soil or nx.soil, (ly.text + " " + nx.text).strip()
                ly.label_confirmed = nx.label_confirmed
                continue
            k += 1


def _ist_blau(farbe: int) -> bool:
    r, g, b = (farbe >> 16) & 255, (farbe >> 8) & 255, farbe & 255
    return b >= 128 and b > r + 60 and b > g + 30


def _blaue_wasserlabels(doc, boreholes) -> None:
    """W7 (#54): blaues Label '3.10 (213.21)' mit Datum links/rechts der Saeule. Das Label ist der Wert; das Dreieck
    steht in Schnitten oft verschoben. Mit Hoehe in Klammern muss Tiefe + Hoehe = GOK (+-5 cm) sein."""
    je_seite: dict[int, list] = defaultdict(list)
    for bh in boreholes:
        if bh.bbox and bh.mode != "schichtenverzeichnis":
            je_seite[bh.page - 1].append(bh)
    for pno, bhs in je_seite.items():
        spans, alle = [], []
        for blk in doc[pno].get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if sp["text"].strip():
                        alle.append((pymupdf.Rect(sp["bbox"]), sp["text"].strip()))
                        if _ist_blau(sp.get("color", 0)):
                            spans.append((pymupdf.Rect(sp["bbox"]), sp["text"].strip()))
        if RULES["gw_label_text"]:                         # W7b: 'GW' + '0.94m' in einer Zeile, Datum darunter
            gw_t = [q for q, u in alle if u == "GW"]
            for q, u in alle:
                if WL_RE.match(u) and any(abs((g.y0 + g.y1) / 2 - (q.y0 + q.y1) / 2) < 4 and 0 <= q.x0 - g.x1 < 50
                                          for g in gw_t):
                    spans.append((q, u))
        if not spans:
            continue
        blaue_linien = [dr for dr in doc[pno].get_drawings() if dr.get("color") and len(dr["color"]) == 3
                        and dr["color"][2] >= 0.5 and dr["color"][2] > dr["color"][0] + 0.2]
        labels: dict[int, list] = defaultdict(list)
        for r, t in spans:
            if not (m := WL_RE.match(t)):
                continue
            def abstand(bh):
                x0, y0, x1, y1 = bh.bbox
                if not (y0 - 5 <= (r.y0 + r.y1) / 2 <= y1 + 5):
                    return None
                dx = x0 - r.x1 if r.x1 <= x0 + 2 else (r.x0 - x1 if r.x0 >= x1 - 2 else None)
                return dx if dx is not None and dx < 160 else None
            nah = [(abstand(bh), i) for i, bh in enumerate(bhs) if abstand(bh) is not None]
            if not nah:
                continue
            i = min(nah)[1]
            d = float(m.group(1).replace(",", "."))
            h = float(m.group(2).replace(",", ".")) if m.group(2) else None
            datum = " ".join(u for q, u in alle if 0 <= q.y0 - r.y1 < 14 and abs(q.x0 - r.x0) < 40
                             and GW_DATUM_RE.search(u))
            labels[i].append((d, h, f"{t} {datum}".strip()))
        for i, ls in labels.items():
            bh = bhs[i]
            ok = []
            for d, h, beleg in ls:
                if h is not None and bh.gok is not None and abs(d + h - bh.gok) > 0.05:
                    bh.issues.append(f"Wasserlabel {beleg}: Tiefe + Hoehe passt nicht zur GOK {bh.gok}, nicht uebernommen")
                    continue
                ok.append((d, beleg))
            if not ok:
                continue
            alt = [x for x in bh.gw_depths if not any(abs(x - d) <= 0.03 for d, _ in ok)]
            if alt:
                bh.issues.append(f"Wassersymbol bei {alt} m ohne Label verworfen: das blaue Label gilt")
            bh.gw_depths = sorted({d for d, _ in ok})
            bh.gw_info = {k: v for k, v in bh.gw_info.items() if k in bh.gw_depths}
            if bh.fit:                                       # Wasserlinie/Symbol an der Saeule ist keine Schichtgrenze
                a, b = bh.fit
                x0, _, x1, _ = bh.bbox
                blau_y = [dr["rect"].y0 for dr in blaue_linien if dr["rect"].height < 0.5
                          and dr["rect"].x1 >= x0 - 15 and dr["rect"].x0 <= x1 + 15]
                k = 0
                while k < len(bh.layers) - 1:
                    ly = bh.layers[k]
                    if not ly.label_confirmed and any(abs((ly.bottom - b) / a - y) < 1.5 for y in blau_y):
                        nx = bh.layers.pop(k + 1)
                        bh.issues.append(f"Grenze {ly.bottom} m an der blauen Wasserlinie verworfen")
                        ly.bottom, ly.soil, ly.text = nx.bottom, ly.soil or nx.soil, (ly.text + " " + nx.text).strip()
                        ly.label_confirmed = nx.label_confirmed
                        continue
                    k += 1
            for d, beleg in ok:
                gi = gw_info(beleg)
                if d not in bh.gw_info or bh.gw_info[d].get("kind") == "unbestimmt":
                    bh.gw_info[d] = {**gi, "evidence": gi.get("evidence") or beleg}


def _confidence(bh: "Borehole") -> None:
    """Konfidenz je Schicht (0..1) aus unabhaengigen Signalen; Begruendung steht in docs/17 §E9."""
    sv_ok = bh.cross_check == "SV ok" or bh.cross_check == "nur SV"
    sv_bad = bh.cross_check.startswith("SV abweichend")
    for ly in bh.layers:
        c = 0.4
        c += 0.3 if ly.label_confirmed else 0.0
        c += 0.2 if sv_ok else (-0.2 if sv_bad else 0.0)
        c += 0.1 if ly.soil else 0.0
        if bh.mode.startswith("massstab-text") and bh.support == 0:
            c -= 0.2                                      # nur Massstab, keine Labels (OCR verloren)
        ly.confidence = round(max(0.0, min(1.0, c)), 2)


def _cross_check(bh: Borehole, rec: dict) -> None:
    """Profil gegen Schichtenverzeichnis: Unterkanten muessen 1:1 uebereinstimmen; Luecken fuellen."""
    prof = [ly.bottom for ly in bh.layers]
    miss = [d for d in rec["bottoms"] if not any(abs(d - p) <= 0.03 for p in prof)]
    extra = [p for p in prof if not any(abs(d - p) <= 0.03 for d in rec["bottoms"])]
    bh.cross_check = "SV ok" if not miss and not extra else f"SV abweichend: fehlt {miss}, nur im Profil {extra}"
    for d, name in zip(rec["bottoms"], rec["names"]):
        for ly in bh.layers:
            if abs(ly.bottom - d) <= 0.03 and not ly.soil:
                ly.soil = classify_v3(name.split(",")[0]) or classify_v3(name)
            if abs(ly.bottom - d) <= 0.03 and not ly.text:
                ly.text = name
    if not bh.gw_depths and rec["gw"]:
        bh.gw_depths = sorted(set(rec["gw"]))
    for d in bh.gw_depths:                              # Art/Datum aus dem SV, wo das Profil keine nennt (Issue #26)
        sv_i = next((i for t_, i in (rec.get("gw_info") or {}).items() if abs(t_ - d) <= 0.03), None)
        mine = bh.gw_info.get(d) or {"kind": "unbestimmt"}
        if sv_i and (mine["kind"] == "unbestimmt" or (not mine.get("observed_on") and sv_i.get("observed_on"))):
            neu = {"kind": mine["kind"] if mine["kind"] != "unbestimmt" else sv_i["kind"]}
            if datum := mine.get("observed_on") or sv_i.get("observed_on"):
                neu["observed_on"] = datum
            belege = [f"Profil: {mine['evidence']}" if mine.get("evidence") else "",
                      f"SV: {sv_i['evidence']}" if sv_i.get("evidence") else ""]
            if any(belege):
                neu["evidence"] = "; ".join(x for x in belege if x)
            bh.gw_info[d] = neu
    if not bh.gw_depths and not bh.gw_status and rec["gw_status"]:
        bh.gw_status = rec["gw_status"]


def _assign_text(bh: Borehole, col: Column, lines, words, fit, mode, pairs, right_limit):
    """Beschreibung -> Schicht. Konvention aus den Labels: mit 0,00 = Oberkante, sonst Lage im Intervall."""
    a, b = fit
    by_line: dict[tuple, list] = defaultdict(list)
    for r, t, blk, ln in words:
        if not DEPTH_RE.match(t):                         # Label und Text stehen oft in derselben Zeile
            by_line[(blk, ln)].append((r, t))
    lines = []
    for ws in by_line.values():
        ws.sort(key=lambda x: x[0].x0)
        r = pymupdf.Rect(ws[0][0])
        for q, _ in ws[1:]:
            r |= q
        lines.append((r, " ".join(t for _, t in ws)))
    right = [(r, t) for r, t in lines if col.rect.x1 + 2 < r.x0 < min(col.rect.x1 + 220, right_limit - 5)
             and (re.search(r"[A-Za-zÄÖÜäöü]{3}", t) or ABBR_RE.match(t)) and not DATE_RE.search(t)]
    tops = sorted(v for _, v in pairs)
    if RULES["top_convention"] and not mode.startswith("direkt") and tops and tops[0] == 0.0:
        lab = sorted([(r, float(t.rstrip("m ").replace(",", "."))) for r, t, *_ in words if DEPTH_RE.match(t)
                      and r.x0 > col.rect.x1 and float(t.rstrip("m ").replace(",", ".")) in tops], key=lambda e: e[0].y0)
        if RULES["top_null_gedruckt"]:                    # nur Labels an dieser Saeule, nicht die Achse daneben
            lab = [(r, v) for r, v in lab if r.x0 - col.rect.x1 < 60]
        if RULES["top_null_gedruckt"] and lab and not any(v == 0.0 for _, v in lab):
            # T10 (#54): ohne gedrucktes 0,00 entscheidet die Lage der Texte - beginnt er unter dem Label (Oberkante)
            # oder sitzt er direkt darueber (Unterkante, Beschreibung ueber dem Label)?
            unter = sum(1 for lr, _ in lab if any(-2 <= r.y0 - lr.y0 <= 12 and r.x0 >= lr.x1 - 1 for r, _t in right))
            ueber = sum(1 for lr, _ in lab if any(-1 <= lr.y0 - r.y1 <= 10 and abs(r.x0 - lr.x0) <= 8 for r, _t in right))
            if ueber > unter:
                lab = []
        for i, (lr, v) in enumerate(lab):
            nxt = lab[i + 1][0].y0 if i + 1 < len(lab) else lr.y0 + 200
            txt = " ".join(t for r, t in right if lr.y0 - 3 <= r.y0 < nxt - 3 and r.x0 >= lr.x1 - 1)
            for ly in bh.layers:
                if abs(ly.top - v) <= 0.03 and txt:
                    ly.soil = classify_v3(txt.split(",")[0]) or classify_v3(txt)
                    ly.text = txt
        if lab:                                           # sonst: Labels links -> Lage im Intervall
            return
    schon: set[int] = set()
    if RULES["top_null_gedruckt"]:                        # T10: Beschreibung steht ueber ihrem Unterkanten-Label
        bottoms = {ly.bottom for ly in bh.layers}
        unten = sorted([(r, v) for r, t, *_ in words if DEPTH_RE.match(t) and 0 < r.x0 - col.rect.x1 < 60
                        and (v := float(t.rstrip("m ").replace(",", "."))) in bottoms], key=lambda e: e[0].y0)
        # Konvention nur, wenn die Beschreibungszeile direkt ueber ihrem Label sitzt (gleiches x), bei >= 80 % der Labels
        direkt = {}
        for lr, v in unten:                               # die naechste Zeile direkt ueber dem Label (<= 10 pt)
            ueber = [(lr.y0 - r.y1, t) for r, t in right if -1 <= lr.y0 - r.y1 <= 10 and abs(r.x0 - lr.x0) <= 8]
            direkt[v] = [min(ueber)[1]] if ueber else []
        if len(unten) >= 2 and len(unten) >= 0.8 * len(bh.layers) and sum(1 for v in direkt.values() if v) >= 0.8 * len(unten):
            texte: dict[float, list] = defaultdict(list)
            for v, ts in direkt.items():
                if ts:
                    texte[v].extend(ts)
            for k, ly in enumerate(bh.layers):
                if ly.bottom in texte:
                    ly.text = " ".join(texte[ly.bottom])
                    ly.soil = classify_v3(texte[ly.bottom][0].split(",")[0]) or classify_v3(ly.text)
                    schon.add(k)
    for k, ly in enumerate(bh.layers):
        if k in schon:
            continue
        y0, y1 = (ly.top - b) / a, (ly.bottom - b) / a
        txt = " ".join(t for r, t in right if y0 - 2 <= (r.y0 + r.y1) / 2 < y1 + 2)
        if txt:
            ly.soil = classify_v3(txt.split(",")[0]) or classify_v3(txt)
            ly.text = txt


# ---------------------------------------------------------------------------
# E9: kanonisches JSON (docs/ARCHITECTURE_BAUGRUNDMODELL.md §5.1) - Eingang fuer Supabase und IFC
# ---------------------------------------------------------------------------
KIND = (("GWM", "gwm"), ("RKS", "rks"), ("KRB", "rks"), ("BS", "rks"), ("SCH", "schurf"),
        ("BK", "kernbohrung"), ("KB", "kernbohrung"), ("B", "kernbohrung"))
METHOD = {"vektor": "vector", "vektor_ohne_text": "vector+ocr", "raster": "raster+ocr", "raster_ocr": "raster+ocr_layer"}


def _kind(code: str) -> str:
    head = re.match(r"[A-Z]+", code)
    for prefix, kind in KIND:
        if head and head.group(0) == prefix:
            return kind
    return "kernbohrung"                                  # Fremdcodes ('422C-460', 'S 2a'): Bohrung


def to_canonical(pdf: Path, boreholes: list, dph: dict | None = None, version: str = "v4") -> dict:
    data = Path(pdf).read_bytes()
    out = {"document": {"file": Path(pdf).name, "sha256": hashlib.sha256(data).hexdigest(),
                        "parser_version": f"prototyp_{version}", "pages": pymupdf.open(pdf).page_count},
           "boreholes": [], "soundings": {k: [list(map(float, st)) for st in v] for k, v in (dph or {}).items()}}
    if RULES["gw_art"] or RULES["ls_wasserlinien"]:       # Bemessungswasserstand, HGW... (Issue #26 2a + 2b)
        with pymupdf.open(pdf) as wsp_doc:
            t_wsp = wasserstaende_text(wsp_doc) if RULES["gw_art"] else []
            ls_wsp, ls_hinw = wasserlinien_laengsschnitt(wsp_doc) if RULES["ls_wasserlinien"] else ([], [])
        wsp_alle, zus_hinw = _wasserstaende_zusammenfuehren(t_wsp, ls_wsp)
        out["wasserstaende"] = wsp_alle
        alle_hinw = ls_hinw + zus_hinw
        if alle_hinw:
            out["wasserlinien_hinweise"] = alle_hinw
    for bh in boreholes:
        method = "schichtenverzeichnis" if bh.mode == "schichtenverzeichnis" else METHOD.get(bh.page_class, "vector")
        layers = []
        for ly in bh.layers:
            prov = {"page": bh.page - 1, "method": method}
            if bh.fit and bh.bbox:
                a, b = bh.fit
                prov["bbox"] = [bh.bbox[0], round((ly.top - b) / a, 1), bh.bbox[2], round((ly.bottom - b) / a, 1)]
            layers.append({"top_depth": ly.top, "bottom_depth": ly.bottom, "description_raw": ly.text,
                           "soil_class": ly.soil or None, "hatch_class": ly.soil_hatch or None,
                           "confidence": ly.confidence, "label_confirmed": ly.label_confirmed,
                           "issues": ly.issues, "provenance": [prov]})
        gw = [{"depth": d, "nhn": round(bh.gok - d, 2) if bh.gok is not None else None,
               **(bh.gw_info.get(d) or {"kind": "unbestimmt"})} for d in bh.gw_depths]
        out["boreholes"].append({
            "code": bh.code, "kind": _kind(bh.code), "gok_nhn": bh.gok,
            "end_depth": bh.layers[-1].bottom if bh.layers else None,
            "x": bh.east, "y": bh.north, "crs_epsg": bh.crs, "coord_source": bh.coord_source or None,
            "layers": layers, "groundwater": gw, "groundwater_status": bh.gw_status,
            "checks": {"label_support": round(bh.support, 2), "scale": bh.scale, "mode": bh.mode,
                       "schichtenverzeichnis": bh.cross_check or None, "duplicates": bh.duplicates},
            "issues": bh.issues,
            "provenance": [{"page": bh.page - 1, "bbox": list(bh.bbox) if bh.bbox else None, "method": method}]})
    return out


if __name__ == "__main__":                                # python prototyp_v4.py <pdf> [<out.json>]
    src = Path(sys.argv[1])
    bhs, dph = extract(src)
    js = json.dumps(to_canonical(src, bhs, dph), indent=1, ensure_ascii=False)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(js)
    else:
        print(js)
