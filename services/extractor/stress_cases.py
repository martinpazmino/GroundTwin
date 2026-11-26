"""Stressfaelle: je Lektion (docs/16) ein kleines PDF mit bekannter Wahrheit.

Die Faelle bilden die Merkmale nach, an denen v1-v3 bei echten Gutachten gescheitert sind
(Titel mit Zusatz, gedrehte Seite, Achsen, Probenspalte, Kuerzel, SHX-Text, Raster, ...).
Jede Datei bekommt eine Wahrheit im Format von benchmark/groundtruth/*.json.

    python stress_cases.py <ausgabeordner>
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

PT_PER_M_1_1 = 1000 / 25.4 * 72            # 1 m Natur bei M 1:1 in pt
HATCH = {"Mutterboden": "diag", "Sand": "dots", "Kies": "circles", "Schluff": "vticks", "Ton": "hdash",
         "Auffuellung": "cross", "Beton": "diag", "Schwarzdecke": "double"}


@dataclass
class Spec:
    code: str
    layers: list[tuple[float, str, str]]          # (Unterkante, Bodenart, Beschreibung)
    title: str = "{code}"
    gok: float | None = None
    scale: int = 50
    scale_text: str | None = "M 1:50"
    label_side: str = "left"                      # left | right
    convention: str = "base"                      # base | top
    unit: str = ""                                # '' | 'm'
    decimal: str = ","
    label_dy: float = 2.5                         # Grundlinie relativ zur Grenzlinie
    ruler: float | None = None                    # Schrittweite einer Tiefenleiste links (m)
    elev_triangles: bool = False                  # Dreiecke je Meter an einer Hoehenleiste
    samples: bool = False                         # Probenspalte Von/Bis
    gw: tuple[str, float] | None = None           # ("symbol"|"text"|"desc", Tiefe)
    no_gw: str | None = None                      # 'Kein Wasser', 'trocken', ...
    gwm: bool = False                             # Ausbauplan GWM neben dem Profil
    shx: bool = False                             # Tiefen als Striche (AutoCAD-SHX), kein Text
    leader: bool = False                          # Beschreibung mit Fuehrungslinie versetzt
    coords: tuple[float, float] | None = None
    col_w: float = 22.0
    top_y: float = 150.0
    x0: float = 200.0
    extra: dict = field(default_factory=dict)


def _fmt(v: float, dec: str) -> str:
    return f"{v:.2f}".replace(".", dec)


# --------------------------------------------------------------------------
# Strichschrift (Ziffern), wie AutoCAD-SHX: Linien statt Text
# --------------------------------------------------------------------------
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def stroke_text(page, x: float, y: float, s: str, h: float = 6.0) -> None:
    w = h * 0.55
    sh = page.new_shape()
    for ch in s:
        if ch in ",.":
            sh.draw_line(pymupdf.Point(x + 0.5, y), pymupdf.Point(x, y + 1.5))
            x += w * 0.6
            continue
        pts = {"a": ((0, 0), (1, 0)), "b": ((1, 0), (1, .5)), "c": ((1, .5), (1, 1)), "d": ((0, 1), (1, 1)),
               "e": ((0, .5), (0, 1)), "f": ((0, 0), (0, .5)), "g": ((0, .5), (1, .5))}
        for sgm in SEG.get(ch, ""):
            (ax, ay), (bx, by) = pts[sgm]
            sh.draw_line(pymupdf.Point(x + ax * w, y - h + ay * h), pymupdf.Point(x + bx * w, y - h + by * h))
        x += w * 1.4
    sh.finish(color=(0, 0, 0), width=0.5)
    sh.commit()


def _hatch(page, r: pymupdf.Rect, kind: str) -> None:
    sh = page.new_shape()
    step = 6.0
    ys = [r.y0 + step / 2 + i * step for i in range(int(r.height // step))]
    xs = [r.x0 + step / 2 + i * step for i in range(int(r.width // step))]
    if kind == "dots":
        for y in ys:
            for x in xs:
                sh.draw_circle(pymupdf.Point(x, y), 0.45)
        sh.finish(color=None, fill=(0, 0, 0))
    elif kind == "circles":
        for y in ys:
            for x in xs:
                sh.draw_circle(pymupdf.Point(x, y), 1.6)
        sh.finish(color=(0, 0, 0), width=0.3)
    elif kind == "hdash_wide":                    # Ton: gestrichelte Linien ueber die volle Breite, 12 pt Abstand
        for y in [r.y0 + 6 + i * 12 for i in range(int((r.height - 6) // 12))]:
            sh.draw_line(pymupdf.Point(r.x0, y), pymupdf.Point(r.x1, y))
        sh.finish(color=(0, 0, 0), width=0.3, dashes="[3 2] 0")
    elif kind == "hdash":                         # Ton: Striche ueber die ganze Breite (Falle L6)
        for y in ys:
            sh.draw_line(pymupdf.Point(r.x0, y), pymupdf.Point(r.x1, y))
        sh.finish(color=(0, 0, 0), width=0.3, dashes="[3 2] 0")
    elif kind == "vticks":
        for y in ys:
            for x in xs:
                sh.draw_line(pymupdf.Point(x, y - 2), pymupdf.Point(x, y + 2))
        sh.finish(color=(0, 0, 0), width=0.3)
    elif kind in ("diag", "cross"):
        for x in range(int(r.x0 - r.height), int(r.x1), 5):
            a, b = pymupdf.Point(x, r.y1), pymupdf.Point(x + r.height, r.y0)
            t0, t1 = max(0.0, (r.x0 - a.x) / r.height), min(1.0, (r.x1 - a.x) / r.height)
            if t1 > t0:
                sh.draw_line(a + (b - a) * t0, a + (b - a) * t1)
        sh.finish(color=(0, 0, 0), width=0.3)
    elif kind == "double":                        # Schwarzdecke: zwei durchgehende Linien (Falle L6)
        for y in (r.y0 + r.height * 0.4, r.y0 + r.height * 0.6):
            sh.draw_line(pymupdf.Point(r.x0, y), pymupdf.Point(r.x1, y))
        sh.finish(color=(0, 0, 0), width=0.3)
    sh.commit()


def _line(page, a, b, w=0.6, dashes=None):
    page.draw_line(pymupdf.Point(*a), pymupdf.Point(*b), color=(0, 0, 0), width=w, dashes=dashes)


def draw_profile(page, s: Spec) -> None:
    ppm = PT_PER_M_1_1 / s.scale
    top, x0 = s.top_y, s.x0
    col = pymupdf.Rect(x0, top, x0 + s.col_w, top + s.layers[-1][0] * ppm)
    page.insert_text(s.extra.get("title_xy", (x0 - 20, top - 40)), s.title.format(code=s.code), fontsize=10)
    if s.gok is not None:
        page.insert_text((x0 - 20, top - 26), f"NHN {_fmt(s.gok, s.decimal)} m", fontsize=7)
    if s.coords:
        page.insert_text((x0 + 120, top - 40), f"Rechtswert (UTM 33N): {_fmt(s.coords[0], ',')[:-1]}", fontsize=6)
        page.insert_text((x0 + 120, top - 31), f"Hochwert (UTM 33N): {_fmt(s.coords[1], ',')[:-1]}", fontsize=6)
    # Saeule als einzelne Segmente (Ghostscript-Stil, L1)
    _line(page, (col.x0, col.y0), (col.x0, col.y1), 0.8)
    _line(page, (col.x1, col.y0), (col.x1, col.y1), 0.8)
    prev = 0.0
    for k, (bot, soil, desc) in enumerate(s.layers):
        y0, y1 = top + prev * ppm, top + bot * ppm
        _hatch(page, pymupdf.Rect(col.x0, y0, col.x1, y1), s.extra.get("hatch", {}).get(soil, HATCH.get(soil, "dots")))
        _line(page, (col.x0 - (14 if s.label_side == "left" else 0), y1),
              (col.x1 + (14 if s.label_side == "right" else 0), y1), 0.6)
        val = prev if s.convention == "top" else bot
        lab = _fmt(val, s.decimal) + s.unit
        ly = (y0 if s.convention == "top" else y1) + s.label_dy
        lx = col.x0 - 34 if s.label_side == "left" else col.x1 + 4
        if k in s.extra.get("label_skip", ()):
            pass                                   # Schicht ohne Tiefenlabel
        elif s.shx:
            stroke_text(page, lx, ly, lab)
        else:
            page.insert_text((lx, ly), lab, fontsize=6.5)
        ty = (y0 + y1) / 2 + 2
        tx = col.x1 + (60 if s.leader else 40)
        if s.leader:                               # Text versetzt mit Fuehrungslinie (L3, B1)
            ty = y0 + 8
            _line(page, (col.x1 + 2, (y0 + y1) / 2), (tx - 2, ty - 2), 0.3)
        if s.extra.get("desc_from_label"):         # mehrzeilige Beschreibung ab dem Label (laeuft in die naechste Schicht)
            for i, part in enumerate(desc.split("|")):
                page.insert_text((tx + 30, ly + i * 8), part.strip(), fontsize=6.5)
        else:
            page.insert_text((tx, ty), desc, fontsize=6.5)
        prev = bot
    _line(page, (col.x0, top), (col.x1, top), 0.8)
    if s.convention == "top" and not s.shx:          # Endteufe auch beschriftet
        page.insert_text((col.x1 + 4 if s.label_side == "right" else col.x0 - 34, col.y1 + 9),
                         _fmt(s.layers[-1][0], s.decimal) + s.unit, fontsize=6.5)
    if s.scale_text:
        page.insert_text((x0 - 20, col.y1 + 30), s.scale_text, fontsize=8)
    if s.ruler:                                    # Tiefenleiste links: arithmetische Folge (L14)
        rx = x0 - 120
        _line(page, (rx, top), (rx, col.y1), 0.5)
        n = int(round(s.layers[-1][0] / s.ruler))
        for i in range(n + 1):
            y = top + i * s.ruler * ppm
            _line(page, (rx, y), (rx + 4, y), 0.4)
            page.insert_text((rx - 26, y + 2), _fmt(i * s.ruler, s.decimal), fontsize=6)
    if s.elev_triangles and s.gok is not None:     # Hoehenleiste mit Dreieck je Meter (L10)
        ex = x0 - 160
        for i in range(int(s.layers[-1][0]) + 1):
            y = top + i * ppm
            page.draw_polyline([(ex, y - 5), (ex + 6, y - 5), (ex + 3, y), (ex, y - 5)], color=(0, 0, 0),
                               closePath=True, width=0.4)
            page.insert_text((ex + 9, y), _fmt(s.gok - i, s.decimal), fontsize=5.5)
    if s.samples:                                  # Probenspalte Von/Bis (L15)
        sx = col.x0 - 90
        prev = 0.0
        for bot, *_ in s.layers:
            mid = top + (prev + bot) / 2 * ppm
            page.draw_rect(pymupdf.Rect(sx - 10, mid - 6, sx - 4, mid), color=(0, 0, 0), width=0.3)
            page.insert_text((sx, mid - 1), _fmt(prev, s.decimal), fontsize=6)
            page.insert_text((sx, mid + 7), _fmt(bot, s.decimal), fontsize=6)
            prev = bot
    if s.gw:
        kind, d = s.gw
        y = top + d * ppm
        if kind == "symbol":
            gx = col.x0 - 60
            page.draw_polyline([(gx, y - 6), (gx + 7, y - 6), (gx + 3.5, y), (gx, y - 6)], color=(0, 0, 1),
                               fill=(0, 0, 1), closePath=True, width=0.4)
            _line(page, (gx, y), (col.x0, y), 0.4)
            page.insert_text((gx + 9, y - 2), f"{_fmt(d, s.decimal)}", fontsize=6)
        elif kind == "text":
            page.insert_text((col.x0 - 70, y), f"GW {_fmt(d, '.')}m", fontsize=6.5)
    if "dach" in s.extra:                          # W3: Dach (zwei Striche) auf der Wasserlinie, Bedeutung in der Legende
        y = top + s.extra["dach"] * ppm
        gx = col.x0 - 60
        page.draw_polyline([(gx, y), (gx + 3.5, y - 6), (gx + 7, y)], color=(0, 0, 1), width=0.4)
        _line(page, (gx - 3, y), (col.x0, y), 0.4)
        page.insert_text((gx + 9, y - 2), f"{_fmt(s.extra['dach'], s.decimal)}", fontsize=6)
    if s.extra.get("legende"):                     # Legende unten: volles Dreieck = Ruhewasser, Dach = angebohrt
        ly = 780
        page.draw_polyline([(60, ly - 6), (67, ly - 6), (63.5, ly), (60, ly - 6)], color=(0, 0, 1), fill=(0, 0, 1),
                           closePath=True, width=0.4)
        _line(page, (57, ly), (80, ly), 0.4)
        page.insert_text((90, ly - 1), "Ruhewasserstand", fontsize=7)
        ly = 800
        page.draw_polyline([(60, ly), (63.5, ly - 6), (67, ly)], color=(0, 0, 1), width=0.4)
        _line(page, (57, ly), (80, ly), 0.4)
        page.insert_text((90, ly - 1), "Grundwasser angebohrt", fontsize=7)
    if s.no_gw:
        page.insert_text((x0 - 20, col.y1 + 18), s.no_gw, fontsize=7)
    if s.gwm:                                      # Ausbauplan einer GWM rechts (L15b)
        gx = x0 + 260
        page.insert_text((gx - 10, top - 40), "GWM " + s.code.split()[-1], fontsize=10)
        _line(page, (gx, top), (gx, col.y1 * 0.9 + top * 0.1), 0.9)
        _line(page, (gx + 14, top), (gx + 14, col.y1 * 0.9 + top * 0.1), 0.9)
        for f in (0.2, 0.55):
            y = top + (col.y1 - top) * f
            _line(page, (gx, y), (gx + 14, y), 0.6)
        page.insert_text((gx + 20, top + 20), "Vollrohr DN 50", fontsize=6)


def draw_dph_axis(page, x0: float, top: float, ppm: float, depth: float, code: str) -> None:
    """Rammdiagramm mit Tiefenachse 1,00 ... und Gitter (Falle L14)."""
    page.insert_text((x0, top - 40), "DPH " + code.split()[-1], fontsize=9)
    w = 60.0
    _line(page, (x0, top), (x0, top + depth * ppm), 0.5)
    _line(page, (x0 + w, top), (x0 + w, top + depth * ppm), 0.5)
    for i in range(int(depth) + 1):
        y = top + i * ppm
        _line(page, (x0, y), (x0 + w, y), 0.3)
        if i:
            page.insert_text((x0 - 18, y + 2), f"{i},00", fontsize=6)
    for i in range(1, 6):
        _line(page, (x0 + i * w / 6, top), (x0 + i * w / 6, top + depth * ppm), 0.2)


def sv_pages(doc, code: str, layers, gw_note: str, spaced: bool = True, dup: bool = True) -> None:
    """Formblatt Schichtenverzeichnis (DIN 4022), eine Seite je 6 Schichten."""
    chunks = [layers[i:i + 6] for i in range(0, len(layers), 6)]
    for blatt, chunk in enumerate(chunks, 1):
        p = doc.new_page(width=595, height=842)
        for rep in range(2 if dup else 1):          # doppelter Text wie bei Wesel (S3)
            title = "S c h i c h t e n v e r z e i c h n i s" if spaced else "Schichtenverzeichnis"
            p.insert_text((200, 40), title, fontsize=10)
            p.insert_text((150, 56), "für Bohrungen ohne durchgehende Gewinnung von gekernten Proben", fontsize=8)
            p.insert_text((45, 100), "Bohrung", fontsize=8)
            p.insert_text((55, 112), "Nr.:", fontsize=8)
            p.insert_text((130, 112), code, fontsize=8)
            p.insert_text((155, 112), f"/ Blatt {blatt}", fontsize=8)
            for i, t in enumerate(["Bis", "... m", "unter", "Ansatz-", "punkt"]):
                p.insert_text((40, 160 + i * 9), t, fontsize=7)
            p.insert_text((80, 150), "a)", fontsize=7)
            p.insert_text((93, 150), "Benennung der Bodenart", fontsize=7)
            p.insert_text((80, 168), "b)", fontsize=7)
            p.insert_text((93, 168), "Ergänzende Bemerkungen", fontsize=7)
            for i, t in enumerate(["Bemerkungen", "Sonderproben", "Wasserführung", "Bohrwerkzeuge"]):
                p.insert_text((375, 160 + i * 9), t, fontsize=7)
        p.draw_rect(pymupdf.Rect(35, 140, 560, 205), color=(0, 0, 0), width=0.5)
        y = 215
        for bot, soil, desc in chunk:
            for rep in range(2 if dup else 1):
                p.insert_text((80, y + 8), "a)", fontsize=7)
                p.insert_text((93, y + 8), desc, fontsize=7)
                p.insert_text((80, y + 30), "b)", fontsize=7)
                p.insert_text((80, y + 52), "c)", fontsize=7)
                p.insert_text((50, y + 45), _fmt(bot, ","), fontsize=7)
                p.insert_text((372, y + 8), "erdfeucht", fontsize=7)
            p.draw_rect(pymupdf.Rect(35, y, 560, y + 90), color=(0, 0, 0), width=0.4)
            y += 90
        if blatt == len(chunks):
            p.insert_text((372, y - 70), gw_note, fontsize=7)


def _truth(code, layers, gok=None, gw=(), status=None, kind="bohrung", page=1, xy=None):
    out, top = [], 0.0
    for bot, soil, _ in layers:
        out.append({"top": top, "bottom": bot, "soil": soil})
        top = bot
    b = {"code": code, "kind": kind, "page": page, "gok": gok, "layers": out, "gw_depths": list(gw)}
    if status:
        b["gw_status"] = status
    if xy:
        b["xy"] = list(xy)
    return b


L_STD = [(0.3, "Mutterboden", "Mutterboden, humos, braun"), (1.8, "Sand", "Feinsand, mittelsandig, braun"),
         (3.4, "Kies", "Kies, sandig, grau"), (5.0, "Schluff", "Schluff, tonig, steif"),
         (6.5, "Ton", "Ton, schluffig, halbfest")]
L_ABBR = [(0.14, "Beton", "Beton"), (0.6, "Auffuellung", "A (S, u´, g´)"), (1.8, "Schluff", "U, t, s´"),
          (2.2, "Ton", "T, u, s´"), (3.3, "Sand", "fS, ms´, u´"), (4.5, "Kies", "G, s, u´")]


def build(out: Path) -> list[str]:
    out.mkdir(parents=True, exist_ok=True)
    made = []

    def save(name, doc, boreholes, note):
        doc.save(out / f"{name}.pdf")
        (out / f"{name}.json").write_text(json.dumps(
            {"file": f"{name}.pdf", "notes": note, "boreholes": boreholes}, indent=1, ensure_ascii=False))
        made.append(name)

    # s01 Kontrolle: Basis-Labels links, M 1:50, GOK, GW-Symbol
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    s = Spec("B 1", L_STD, gok=45.20, gw=("symbol", 2.4))
    draw_profile(p, s)
    save("s01_kontrolle", doc, [_truth("B 1", L_STD, 45.20, [2.4])], "Kontrolle (L1 Segmente, G1-G5)")

    # s02 gedrehte Seite: Inhalt um 90 Grad gedreht gezeichnet, /Rotate 90 stellt ihn aufrecht (L2)
    src = pymupdf.open(); draw_profile(src.new_page(width=595, height=842), Spec("B 2", L_STD, gok=44.10, gw=("symbol", 3.1)))
    doc = pymupdf.open(); p = doc.new_page(width=842, height=595)
    p.show_pdf_page(p.rect, src, 0, rotate=90)
    p.set_rotation(90)
    save("s02_gedreht", doc, [_truth("B 2", L_STD, 44.10, [3.1])], "Seite /Rotate 90 (L2)")

    # s03 Titel mit Zusatz, Nicht-Normmassstab 1:30, Tiefenleiste (Triefenstein-artig)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    lay = [(0.14, "Beton", "Beton"), (0.35, "Sand", "S, u´, g´"), (1.8, "Schluff", "U, t, s´"),
           (3.3, "Schluff", "U, t*, s´"), (4.5, "Schluff", "U, t, s´")]
    draw_profile(p, Spec("RKS 1", lay, title="{code} - Betonweg 0+050", scale=30, scale_text="Höhenmaßstab 1:30",
                         label_dy=-1.5, ruler=0.3, gw=("symbol", 3.0)))
    save("s03_titel_zusatz", doc, [_truth("RKS 1", lay, None, [3.0], kind="rks")], "L13, L9, L14 (Leiste)")

    # s04 Labels mit Einheit rechts, GW als Text, Hoehenleiste mit Dreiecken; zweites Profil 'Kein Wasser'
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("B 3", L_STD, gok=741.97, label_side="right", unit="m", decimal=".", gw=("text", 2.53),
                         elev_triangles=True, scale=40, scale_text=None))
    p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("RKS 4", L_STD[:4], gok=742.10, label_side="right", unit="m", decimal=".",
                         no_gw="Kein Wasser", elev_triangles=True, scale=40, scale_text=None))
    save("s04_einheit_gwtext", doc, [_truth("B 3", L_STD, 741.97, [2.53]),
                                     _truth("RKS 4", L_STD[:4], 742.10, [], "kein Grundwasser", "rks", 2)],
         "L8, L9 (M 1:40 ohne Text), L10, L10b, W2")

    # s05 Oberkanten-Konvention mit 0,00, Text mit Fuehrungslinien (L3, B1)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("BK 5", L_STD, gok=770.17, convention="top", label_side="right", leader=True,
                         scale=75, scale_text="Höhenmaßstab 1:75"))
    save("s05_oberkante", doc, [_truth("BK 5", L_STD, 770.17)], "L3 (Oberkante, 0,00), B1")

    # s06 Probenspalte Von/Bis + GWM-Ausbau daneben (Marl-artig)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("BS 6", L_STD, gok=61.05, samples=True, gwm=True))
    save("s06_proben_gwm", doc, [_truth("BS 6", L_STD, 61.05)], "L15, L15b")

    # s07 Schnitt mit zwei Bohrungen und DPH-Achsen + Einzelblaetter (L4, L12, L14)
    doc = pymupdf.open(); p = doc.new_page(width=842, height=595)
    p.insert_text((40, 40), "Geotechnischer Schnitt  L 1:500, H 1:100", fontsize=9)
    for i, (code, gok) in enumerate((("BS 7", 60.4), ("BS 8", 60.8))):
        sp = Spec(code, L_STD, gok=gok, scale=100, scale_text=None, x0=150 + i * 330, top_y=120)
        draw_profile(p, sp)
        draw_dph_axis(p, sp.x0 + 60, sp.top_y, PT_PER_M_1_1 / 100, 8.0, code)
    for code, gok in (("BS 7", 60.4), ("BS 8", 60.8)):
        draw_profile(doc.new_page(width=595, height=842), Spec(code, L_STD, gok=gok, title="Bohrung {code}"))
    save("s07_schnitt_dph", doc, [_truth("BS 7", L_STD, 60.4, page=2), _truth("BS 8", L_STD, 60.8, page=3)],
         "L4, L12, L14")

    # s08 nur Kuerzel + Beton (L16, L7)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("RKS 9", L_ABBR, scale=25, scale_text="Höhenmaßstab 1:25"))
    save("s08_kuerzel", doc, [_truth("RKS 9", L_ABBR, kind="rks")], "L16, L7")

    # s09 Schraffur-Fallen: Ton-Striche ueber volle Breite, Schwarzdecke als Doppellinie (L6)
    lay = [(0.25, "Schwarzdecke", "Schwarzdecke"), (0.8, "Auffuellung", "Auffüllung, Kies, sandig"),
           (2.6, "Ton", "Ton, schluffig, steif"), (4.0, "Sand", "Sand, kiesig")]
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("B 10", lay, gok=52.0, scale=25, scale_text="M 1:25"))
    save("s09_schraffur", doc, [_truth("B 10", lay, 52.0)], "L6/G2 (Doppellinie Schwarzdecke ist bekannte Schwaeche)")

    # s10 Tabellenfalle: 'B 6' mit steigenden Zahlen, kein Profil (L5, G4)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    p.insert_text((60, 80), "Tabelle 3: Probenliste", fontsize=10)
    for i in range(8):
        y = 110 + i * 22
        p.draw_rect(pymupdf.Rect(60, y, 400, y + 22), color=(0, 0, 0), width=0.5)
        _line(p, (120, y), (120, y + 22), 0.5)
        _line(p, (140, y), (140, y + 22), 0.5)
        p.insert_text((65, y + 14), "B 6" if i == 0 else f"MP {i}", fontsize=8)
        p.insert_text((123, y + 14), _fmt(0.5 * (i + 1), ","), fontsize=7)
        p.insert_text((150, y + 14), f"{_fmt(0.5 * i, ',')} - {_fmt(0.5 * (i + 1), ',')} m", fontsize=8)
    save("s10_tabelle", doc, [], "L5, G4: kein Aufschluss")

    # s11 SHX: Tiefen als Striche, Schichtenverzeichnis als Text (L17, S1, S3)
    lay = [(0.1, "Auffuellung", "Auffüllung (Schluff, sandig)"), (1.2, "Auffuellung", "Auffüllung (Schluff, sandig)"),
           (2.2, "Auffuellung", "Auffüllung (Beton + Eisen)"), (5.4, "Sand", "Sand, kiesig"),
           (10.2, "Kies", "Kies, sandig"), (13.6, "Schluff", "Schluff, tonig"), (14.7, "Ton", "Ton, schluffig")]
    doc = pymupdf.open()
    draw_profile(doc.new_page(width=595, height=842), Spec("B 11", lay, shx=True, scale=200, scale_text=None))
    sv_pages(doc, "B 11", lay, "kein Wassereintritt von 0,00 m bis 14,70 m")
    save("s11_shx_sv", doc, [_truth("B 11", lay, None, [], "kein Grundwasser", page=1)], "L17, S1, S3, W2")

    # s12 Raster ohne Text: s01 als Bild (L18)
    src = pymupdf.open(out / "s01_kontrolle.pdf")
    pix = src[0].get_pixmap(dpi=200)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    p.insert_image(p.rect, pixmap=pix)
    save("s12_raster", doc, [_truth("B 1", L_STD, 45.20, [2.4])], "L18: Rasterbild ohne Textlage")

    # s13 Fremdaufschluss mit Portal-Code, GOK-Text und UTM-Koordinaten (T1, S5)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    lay = [(2.0, "Auffuellung", "Sand / Auffüllung / grau / trocken"), (3.5, "Sand", "Sand / Boden / grau"),
           (3.8, "Sand", "Feinsand / hellgrau / Wasseranschnitt 3.8"), (6.0, "Kies", "Feinkies / grau / Schichtwasser")]
    draw_profile(p, Spec("422C-460", lay, title="Bohrung {code}", gok=36.25, scale=100, scale_text=None,
                         coords=(394774.3, 5818338.1)))
    save("s13_fremdcode", doc, [_truth("422C-460", lay, 36.25, [3.8], xy=(394774.3, 5818338.1))], "T1, S5, L10b")
    # s14 Massstabstext widerspricht den Labels: Bohrung melden, keine Schichten raten (E5)
    lay = [(0.5, "Mutterboden", "Mutterboden"), (1.2, "Sand", "Sand, kiesig"), (2.0, "Kies", "Kies, sandig"),
           (2.6, "Sand", "Sand"), (3.4, "Schluff", "Schluff, tonig"), (4.1, "Ton", "Ton"), (4.8, "Sand", "Sand"),
           (5.5, "Kies", "Kies")]
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("B 14", lay, gok=50.0, scale=50, scale_text="M 1:100", label_dy=11,
                         extra={"label_skip": {0, 2, 4, 6}}))
    save("s14_massstab_widerspruch", doc, [_truth("B 14", lay, 50.0)],
         "E5: Massstabstext 1:100, Zeichnung 1:50, nur 4 versetzte Labels -> Bohrung ohne Schichten, keine falschen Grenzen")

    # s15 Oberkanten-Labels, Beschreibung mehrzeilig ab dem Label, laeuft in die naechste Schicht (L3)
    lay = [(0.4, "Sand", "Sand, schluffig,|braun, locker,|Kiesnester"), (0.8, "Ton", "Ton, schluffig,|steif, grau,|Kiesnester"),
           (1.2, "Sand", "Sand, fein,|gelb, dicht,|Kiesnester"), (1.6, "Ton", "Ton, sandig,|weich, braun,|Kiesnester"),
           (2.0, "Sand", "Sand, mittel,|grau,|Kiesnester")]
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("BK 15", lay, gok=40.0, convention="top", label_side="right", label_dy=9, scale=50,
                         extra={"desc_from_label": True}))
    save("s15_oberkante_mehrzeilig", doc, [_truth("BK 15", lay, 40.0)], "L3: Text gehoert zum Label, nicht zur Lage im Intervall")

    # s16 Einzelblatt, Kopf weit links oben ueber dem Schriftfeld (T3)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("B 16", L_STD, gok=48.0, x0=330, extra={"title_xy": (40, 70)}))
    save("s16_kopf_fern", doc, [_truth("B 16", L_STD, 48.0)], "T3: ein Kopf, ein Profil, Abstand > 70 pt")

    # s17 gestrichelte Ton-Schraffur ueber die volle Breite mit 12 pt Abstand (G2)
    lay = [(0.3, "Mutterboden", "Mutterboden"), (2.5, "Ton", "Ton, schluffig, steif"), (4.0, "Sand", "Sand")]
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("B 17", lay, gok=45.0, extra={"hatch": {"Ton": "hdash_wide"}}))
    save("s17_schraffur_gestrichelt", doc, [_truth("B 17", lay, 45.0)], "G2: gestrichelte Waagrechte sind Schraffur")

    # s18 Legende mit zwei Wassersymbolen: volles Dreieck (Ruhewasser) und Dach aus zwei Strichen (angebohrt), W3
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("BK 18", L_STD, gok=45.0, gw=("symbol", 1.8), extra={"dach": 3.6, "legende": True}))
    save("s18_legende_dach", doc, [_truth("BK 18", L_STD, 45.0, [1.8, 3.6])], "W3: Dach-Symbol aus der Legende")

    # s19 dasselbe Dach ohne Legende: kein Wasserstand (eine Form zaehlt nur, wenn die Legende sie als Wasser kennt)
    doc = pymupdf.open(); p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("BK 19", L_STD, gok=45.0, extra={"dach": 3.6}))
    save("s19_dach_ohne_legende", doc, [_truth("BK 19", L_STD, 45.0, [])], "W3: ohne Legende kein Dach-Stand")

    def _als_scan(src_doc: pymupdf.Document, dpi: int = 150) -> pymupdf.Document:
        scan = pymupdf.open()
        for seite in src_doc:
            q = scan.new_page(width=seite.rect.width, height=seite.rect.height)
            q.insert_image(q.rect, pixmap=seite.get_pixmap(dpi=dpi))
        return scan

    # s20 Scan (150 dpi) mit vollem GW-Dreieck und Wasserlinie: genau 1 Stand (W4)
    src = pymupdf.open(); sp = Spec("B 20", L_STD, gok=45.20, gw=("symbol", 2.8))
    draw_profile(src.new_page(width=595, height=842), sp)
    save("s20_raster_gw_symbol", _als_scan(src), [_truth("B 20", L_STD, 45.20, [2.8])],
         "W4: Scan (150 dpi) mit vollem GW-Dreieck und Wasserlinie")

    # s21 Scan mit Schraffur aus Dreiecken/Winkeln in der Saeule ohne Wasser: 0 Staende (W4)
    src = pymupdf.open(); p = src.new_page(width=595, height=842)
    sp = Spec("B 21", L_STD, gok=45.20)
    draw_profile(p, sp)
    ppm = PT_PER_M_1_1 / sp.scale
    for d_m in (0.8, 1.3, 2.2, 2.8, 4.0, 4.6, 5.6):
        yy = sp.top_y + d_m * ppm
        p.draw_polyline([(sp.x0 + 3, yy - 6), (sp.x0 + 10, yy - 6), (sp.x0 + 6.5, yy), (sp.x0 + 3, yy - 6)],
                        color=(0, 0, 0), fill=(0, 0, 0), closePath=True, width=0.4)
        p.draw_polyline([(sp.x0 + 12, yy), (sp.x0 + 15.5, yy - 6), (sp.x0 + 19, yy)], color=(0, 0, 0), width=0.4)
        _line(p, (sp.x0 + 2.5, yy), (sp.x0 + sp.col_w - 2.5, yy), 0.4)
    save("s21_raster_schraffur_dreiecke", _als_scan(src), [_truth("B 21", L_STD, 45.20, [])],
         "W4: Scan mit Dreiecks-/Winkel-Schraffur in der Saeule ohne Wasser")

    # s22 Scan mit offenem Dreieck ohne Wasserlinie, Hoehenmarke mit Kote, Leiste und GOK-Dreieck: 0 Staende (W4, L10)
    src = pymupdf.open(); p = src.new_page(width=595, height=842)
    sp = Spec("B 22", L_STD, gok=742.50, elev_triangles=True)
    draw_profile(p, sp)
    y1 = sp.top_y + 2.5 * ppm
    p.draw_polyline([(sp.x0 - 55, y1 - 7), (sp.x0 - 48, y1 - 7), (sp.x0 - 51.5, y1), (sp.x0 - 55, y1 - 7)],
                    color=(0, 0, 0), closePath=True, width=0.5)
    y2 = sp.top_y + 3.8 * ppm
    p.draw_polyline([(sp.x0 - 80, y2 - 7), (sp.x0 - 73, y2 - 7), (sp.x0 - 76.5, y2), (sp.x0 - 80, y2 - 7)],
                    color=(0, 0, 0), closePath=True, width=0.5)
    _line(p, (sp.x0 - 80, y2), (sp.x0 - 30, y2), 0.4)
    p.insert_text((sp.x0 - 68, y2 - 1), "738,70m", fontsize=6.5)
    p.draw_polyline([(sp.x0 + 8, sp.top_y - 6), (sp.x0 + 14, sp.top_y - 6), (sp.x0 + 11, sp.top_y),
                     (sp.x0 + 8, sp.top_y - 6)], color=(0, 0, 0), fill=(0, 0, 0), closePath=True, width=0.4)
    save("s22_raster_dreieck_ohne_linie", _als_scan(src), [_truth("B 22", L_STD, 742.50, [])],
         "W4: Scan mit offenem Dreieck ohne Wasserlinie und Hoehenmarke mit Kote")

    # s23 Scan mit Legende: volles Dreieck (Ruhewasser) + Dach (angebohrt) -> 2 Staende (W3 + W4)
    src = pymupdf.open()
    draw_profile(src.new_page(width=595, height=842),
                 Spec("BK 23", L_STD, gok=45.0, gw=("symbol", 1.8), extra={"dach": 3.6, "legende": True}))
    save("s23_raster_legende_dach", _als_scan(src), [_truth("BK 23", L_STD, 45.0, [1.8, 3.6])],
         "W3+W4: Scan mit Legende fuer volles Dreieck und Dach-Symbol")

    # s24 Scan mit Tiefenlineal (ohne Einzel-Schichtlabels, ohne Massstabstext) und vollem GW-Dreieck -> 1 Stand (E5/W5)
    src = pymupdf.open(); p = src.new_page(width=595, height=842)
    sp24 = Spec("B 24", L_STD, gok=45.20, scale=50, scale_text=None, ruler=1.0,
                extra={"label_skip": set(range(len(L_STD)))})
    draw_profile(p, sp24)
    y_gw24, gx24 = sp24.top_y + 2.8 * (PT_PER_M_1_1 / sp24.scale), sp24.x0 - 60
    p.draw_polyline([(gx24, y_gw24 - 6), (gx24 + 7, y_gw24 - 6), (gx24 + 3.5, y_gw24), (gx24, y_gw24 - 6)],
                    color=(0, 0, 1), fill=(0, 0, 1), closePath=True, width=0.4)
    _line(p, (gx24, y_gw24), (sp24.x0, y_gw24), 0.4)
    save("s24_raster_tiefenlineal_gw", _als_scan(src), [_truth("B 24", L_STD, 45.20, [2.8])],
         "E5/W5: Scan mit OCR-Tiefenlineal und GW-Dreieck")

    # s25 Scan mit Tiefenlineal (1:100), das den Grenzbeschriftungen (1:50) widerspricht -> kein Stand, Hinweis (E5)
    src = pymupdf.open(); p = src.new_page(width=595, height=842)
    sp25 = Spec("B 25", L_STD, gok=45.20, scale=50, scale_text=None, label_dy=11, extra={"label_skip": {0, 2}})
    draw_profile(p, sp25)
    ppm25 = PT_PER_M_1_1 / sp25.scale
    rx25 = sp25.x0 - 120
    _line(p, (rx25, sp25.top_y), (rx25, sp25.top_y + 6.5 * ppm25), 0.5)
    for i in range(7):
        yy = sp25.top_y + i * ppm25
        _line(p, (rx25, yy), (rx25 + 4, yy), 0.4)
        p.insert_text((rx25 - 26, yy + 2), _fmt(2.0 * i, ","), fontsize=6)
    y_gw25, gx25 = sp25.top_y + 2.8 * ppm25, sp25.x0 - 60
    p.draw_polyline([(gx25, y_gw25 - 6), (gx25 + 7, y_gw25 - 6), (gx25 + 3.5, y_gw25), (gx25, y_gw25 - 6)],
                    color=(0, 0, 1), fill=(0, 0, 1), closePath=True, width=0.4)
    _line(p, (gx25, y_gw25), (sp25.x0, y_gw25), 0.4)
    save("s25_raster_lineal_widerspruch", _als_scan(src), [_truth("B 25", L_STD, 45.20, [])],
         "E5: Scan mit Tiefenlineal im Widerspruch zu den Grenzbeschriftungen -> kein Stand, Hinweis")

    # s26 Schichtenverzeichnis mit Wasserstand ('Wasser angetroffen bei 3,00 m u. GOK') -> 1 Stand (W5)
    doc = pymupdf.open()
    draw_profile(doc.new_page(width=595, height=842), Spec("RKS 26", L_ABBR, shx=True, scale=200, scale_text=None))
    sv_pages(doc, "RKS 26", L_ABBR, "Wasser angetroffen bei 3,00 m u. GOK am 18.07.2023", spaced=False, dup=False)
    save("s26_sv_wasserstand", doc, [_truth("RKS 26", L_ABBR, None, [3.0], kind="rks", page=1)],
         "W5: Wasserstand mit Art, Datum und Beleg aus dem Schichtenverzeichnis")

    # s27 Schichtenverzeichnis mit 'kein Grundwasser' -> kein Stand, groundwater_status (W2/W5)
    doc = pymupdf.open()
    draw_profile(doc.new_page(width=595, height=842), Spec("RKS 27", L_ABBR, shx=True, scale=200, scale_text=None))
    sv_pages(doc, "RKS 27", L_ABBR, "kein Grundwasser angetroffen", spaced=False, dup=False)
    save("s27_sv_kein_grundwasser", doc,
         [_truth("RKS 27", L_ABBR, None, [], "kein Grundwasser", kind="rks", page=1)],
         "W2/W5: Schichtenverzeichnis 'kein Grundwasser' -> 0 Staende, groundwater_status")

    # s28 Zeichen einer Zeile auf leicht unterschiedlicher Grundlinie / gemischte Schriftgroesse ('B 2') (#49)
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    sp28 = Spec("B 2", L_STD, title="", gok=45.20, gw=("symbol", 2.8))
    draw_profile(p, sp28)
    # 'B' normal (10 pt), '2' groesser und minimal hoeher -> gleiche Zeile, aber y0('2') < y0('B')
    p.insert_text((sp28.x0 - 20, sp28.top_y - 40), "B", fontsize=10)
    p.insert_text((sp28.x0 - 10, sp28.top_y - 40.6), "2", fontsize=12)
    save("s28_zeile_grundlinie", doc, [_truth("B 2", L_STD, 45.20, [2.8])],
         "E9/#49: Woerter einer Zeile mit versetzter Grundlinie / gemischter Schriftgroesse ('B 2')")

    # s29 Laengsschnitt mit kalibrierter NHN-Achse und HGW/MGW-Linien (#26 2b, W6)
    import synth_laengsschnitt as sl
    doc = pymupdf.open()
    p = doc.new_page(width=842, height=595)
    g29 = sl._zeichne_grundgeruest(
        p,
        gok_punkte=[(0.0, 46.8), (0.5, 47.2), (1.0, 46.6)],
        bohrungen=[("B 29a", 0.2, 47.0, [2.0, 5.5, 9.0]), ("B 29b", 0.8, 46.8, [1.8, 5.0, 8.8])],
    )
    for art, hoehe, lx in (("HGW", 42.50, g29["x1"] - 32), ("MGW", 40.20, g29["x0"] + 6)):
        yy = sl._nhn_zu_y(hoehe, g29["nhn_oben"], g29["y_oben"], g29["pt_pro_m"])
        p.draw_line((g29["x0"], yy), (g29["x1"], yy), color=(0.0, 0.25, 0.9), width=0.9, dashes="[6 3] 0")
        p.insert_text((lx, yy - 3), art, fontsize=7.5, color=(0.0, 0.25, 0.9))
    doc.save(out / "s29_ls_wasserlinien.pdf")
    (out / "s29_ls_wasserlinien.json").write_text(json.dumps({
        "file": "s29_ls_wasserlinien.pdf",
        "notes": "W6/#26 2b: Laengsschnitt mit HGW (42.50) und MGW (40.20 m NHN); keine Bohrungs-GW",
        "boreholes": [],
        "wasserlinien": [
            {"art": "HGW", "nhn": 42.50, "seite": 1, "konstant": True},
            {"art": "MGW", "nhn": 40.20, "seite": 1, "konstant": True},
        ],
    }, indent=1, ensure_ascii=False))
    made.append("s29_ls_wasserlinien")

    # s30 Laengsschnitt-Fallen (unbeschriftet, GOK, blaue Schichtgrenze, mehrdeutiges MHGW) -> 0 Wasserlinien (#26 2b)
    doc = pymupdf.open()
    p = doc.new_page(width=842, height=595)
    g30 = sl._zeichne_grundgeruest(
        p,
        gok_punkte=[(0.0, 46.8), (0.5, 47.2), (1.0, 46.6)],
        bohrungen=[("B 30a", 0.2, 47.0, [2.0, 5.5, 9.0]), ("B 30b", 0.8, 46.8, [1.8, 5.0, 8.8])],
    )
    y_unb = sl._nhn_zu_y(44.0, g30["nhn_oben"], g30["y_oben"], g30["pt_pro_m"])
    p.draw_line((g30["x0"], y_unb), (g30["x1"], y_unb), color=(0.0, 0.2, 0.9), width=0.9, dashes="[5 3] 0")
    y_a30 = sl._nhn_zu_y(39.2, g30["nhn_oben"], g30["y_oben"], g30["pt_pro_m"])
    p.draw_line((g30["x0"], y_a30), (g30["x1"], y_a30), color=(0.0, 0.2, 0.9), width=0.8, dashes="[5 3] 0")
    p.draw_line((g30["x0"], y_a30 + 5.0), (g30["x1"], y_a30 + 5.0), color=(0.0, 0.2, 0.9), width=0.8, dashes="[5 3] 0")
    p.insert_text((g30["x0"] + 20, y_a30 + 4.5), "MHGW", fontsize=7, color=(0.0, 0.2, 0.9))
    doc.save(out / "s30_ls_wasserlinien_fallen.pdf")
    (out / "s30_ls_wasserlinien_fallen.json").write_text(json.dumps({
        "file": "s30_ls_wasserlinien_fallen.pdf",
        "notes": "W6/#26 2b: Fallen (unbeschriftete blaue Linie, mehrdeutiges MHGW) -> 0 Wasserlinien",
        "boreholes": [],
        "wasserlinien": [],
    }, indent=1, ensure_ascii=False))
    made.append("s30_ls_wasserlinien_fallen")

    # s31 Projekt-Nr. im Schriftfeld ('B 231411') ist keine Bohrung (T6, #54)
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("B 1", L_STD, gok=45.20, gw=("symbol", 2.4)))
    # Schriftfeld ueber einer zweiten Saeule (Schnitt ohne eigenen Kopf): die Nummer steht wie ein Kopf darueber
    draw_profile(p, Spec("B 231411", L_STD, title="", x0=400, scale_text=None))
    p.insert_text((330, 110), "Projekt-Nr.:", fontsize=8)
    p.insert_text((380, 110), "B 231411", fontsize=8)
    save("s31_projektnummer", doc, [_truth("B 1", L_STD, 45.20, [2.4])],
         "T6/#54: Projekt-Nr. 'B 231411' im Schriftfeld -> keine Bohrung")

    # s32 Code mit Station 'SB-0+550-N3', Ansatzpunkt mit Bezug (T7, #54)
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    draw_profile(p, Spec("SB-0+550-N3", L_STD, unit="m", decimal=".", gw=("symbol", 2.4)))
    p.insert_text((180, 128), "Ansatzpunkt: 476.76 m NHN (OK-Schiene)", fontsize=7)
    save("s32_stationscode", doc, [_truth("SB-0+550-N3", L_STD, 476.76, [2.4])],
         "T7/#54: Code mit Station, GOK 'Ansatzpunkt: ... m NHN (OK-Schiene)'")

    # s33 Schnitt-Stil: Labels 'Tiefe (Hoehe)', Linie ohne Label in der Schicht, blaues Wasserlabel mit Datum,
    #     GOK allein unter dem Kopf (T8, T9, W7, #54)
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    s33 = Spec("KRB 7", L_STD, label_side="right", extra={"label_skip": range(len(L_STD))})
    draw_profile(p, s33)
    ppm = PT_PER_M_1_1 / s33.scale
    p.insert_text((s33.x0 - 10, s33.top_y - 22), "45.20 m", fontsize=8)
    for bot, _, _ in L_STD:
        p.insert_text((s33.x0 + s33.col_w + 4, s33.top_y + bot * ppm + 2.5),
                      f"{bot:.2f} ({45.20 - bot:.2f})", fontsize=6)
    y_fremd = s33.top_y + 2.6 * ppm                       # Linie ohne Label (Probe/Schraffur) in 1.80-3.40
    _line(p, (s33.x0, y_fremd), (s33.x0 + s33.col_w, y_fremd), 0.6)
    y_w = s33.top_y + 2.8 * ppm
    for a_, b_ in (((s33.x0 - 12, y_w - 6), (s33.x0 - 5, y_w - 6)), ((s33.x0 - 12, y_w - 6), (s33.x0 - 8.5, y_w)),
                   ((s33.x0 - 5, y_w - 6), (s33.x0 - 8.5, y_w))):   # Dreieck aus Einzelstrichen (Schnitt-Software)
        p.draw_line(a_, b_, color=(0, 0, 1), width=0.6)
    p.draw_line((s33.x0 - 80, y_w), (s33.x0, y_w), color=(0, 0, 1), width=0.6)
    p.insert_text((s33.x0 - 80, y_w - 2), "2.80 (42.40)", fontsize=6, color=(0, 0, 1))
    p.insert_text((s33.x0 - 72, y_w + 7), "02.03.22", fontsize=6, color=(0, 0, 1))
    save("s33_schnitt_doppellabel", doc, [_truth("KRB 7", L_STD, 45.20, [2.8], kind="rks")],
         "T8/T9/W7/#54: 'Tiefe (Hoehe)', Linie ohne Label keine Grenze, blaues Wasserlabel, GOK unter dem Kopf")

    # s34 Unterkanten-Labels ohne 0,00, Beschreibung ueber ihrem Label, duenne Schichten, DPH-Achse daneben (T10, #54)
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    s34 = Spec("BS 1", [(b, so, "") for b, so, _ in L_ABBR], gok=45.20, scale=100, scale_text="M 1:100",
               label_side="right", decimal=".")
    draw_profile(p, s34)
    ppm = PT_PER_M_1_1 / s34.scale
    for bot, _, desc in L_ABBR:
        p.insert_text((s34.x0 + s34.col_w + 6, s34.top_y + bot * ppm - 6), desc, fontsize=6)
    ax = s34.x0 + s34.col_w + 110                         # Tiefenachse eines Rammdiagramms: 0.0, 1.0, ...
    for i in range(5):
        p.insert_text((ax, s34.top_y + i * ppm + 2), f"{i}.0", fontsize=6)
    save("s34_unterkante_text_darueber", doc, [_truth("BS 1", L_ABBR, 45.20, kind="rks")],
         "T10/#54: Unterkanten-Labels ohne 0,00, Beschreibung ueber dem Label, Achse 0.0 eines DPH daneben")

    # s35 Wasserlabel 'GW 0.94m' (schwarz) mit Datum in der Labelspalte, Symbol daneben an falscher Hoehe (W7b, #54)
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    s35 = Spec("B 3", L_STD, gok=45.20)
    draw_profile(p, s35)
    ppm = PT_PER_M_1_1 / s35.scale
    y_lab = s35.top_y + 1.2 * ppm                         # Label gestapelt, nicht an der Wassertiefe 2,40
    p.insert_text((s35.x0 - 110, y_lab), "GW", fontsize=6.5)
    p.insert_text((s35.x0 - 90, y_lab), "2.40m", fontsize=6.5)
    p.insert_text((s35.x0 - 95, y_lab + 9), "(21.10.2024)", fontsize=6)
    y_sym = y_lab + 2
    p.draw_polyline([(s35.x0 - 60, y_sym - 6), (s35.x0 - 53, y_sym - 6), (s35.x0 - 56.5, y_sym), (s35.x0 - 60, y_sym - 6)],
                    color=(0, 0, 1), fill=(0, 0, 1), closePath=True, width=0.4)
    _line(p, (s35.x0 - 60, y_sym), (s35.x0, y_sym), 0.4)
    save("s35_gw_label_text", doc, [_truth("B 3", L_STD, 45.20, [2.4])],
         "W7b/#54: Label 'GW 2.40m' mit Datum gilt, das Symbol daneben steht an anderer Hoehe")

    # s36 dieselbe Bohrung zweimal unter anderem Code (Einzelblatt 'B 4', im Schnitt 'B 4a') (T11, #54)
    doc = pymupdf.open()
    p = doc.new_page(width=842, height=595)
    draw_profile(p, Spec("B 4", L_STD, gok=45.20, x0=150))
    draw_profile(p, Spec("B 4a", L_STD, gok=45.20, x0=500, scale_text=None))
    save("s36_doppel_anderer_code", doc, [_truth("B 4", L_STD, 45.20)],
         "T11/#54: gleiche GOK und Grenzen unter zweitem Code -> eine Bohrung mit Hinweis")
    return made


if __name__ == "__main__":
    for n in build(Path(sys.argv[1])):
        print(n)
