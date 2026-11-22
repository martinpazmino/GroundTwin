"""Issue #40 (E5/W5): Tiefenmassstab aus OCR im Scan und Wasserstaende aus dem Schichtenverzeichnis.

Alle Tests laufen ohne Netz und ohne echte Gutachten auf mit PyMuPDF erzeugten 150-dpi-Scans und
DIN-4022-Schichtenverzeichnissen (inkl. 'Regel aus -> altes Verhalten').
"""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "extractor"))
import prototyp_v4 as P  # noqa: E402
import stress_cases as S  # noqa: E402


def _als_scan(src: pymupdf.Document, ziel: Path, dpi: int = 150) -> list[list[tuple]]:
    """Rendert jede Seite als 150-dpi-Bildseite ohne Textlage und liefert die Referenzwoerter je Seite."""
    scan = pymupdf.open()
    woerter = []
    for seite in src:
        ws = [(pymupdf.Rect(w[:4]) * seite.rotation_matrix, w[4], w[5], w[6]) for w in seite.get_text("words")]
        pix = seite.get_pixmap(dpi=dpi)
        q = scan.new_page(width=seite.rect.width, height=seite.rect.height)
        q.insert_image(q.rect, pixmap=pix)
        woerter.append(ws)
    scan.save(ziel)
    return woerter


def _extrahieren(monkeypatch, pdf: Path, woerter: list[list[tuple]]):
    monkeypatch.setattr(P, "ocr_words", lambda page, dpi=None, min_conf=0.5: woerter[page.number])
    return P.extract(pdf)[0]


def test_regelschalter_vorhanden():
    """Beide neuen Regeln (Issue #40) stehen fuer Ablationen in RULES."""
    assert "raster_massstab_ocr" in P.RULES and "sv_wasser" in P.RULES


def test_scan_tiefenlineal_mit_gw_symbol(tmp_path, monkeypatch):
    """(a) Scan mit Tiefenlineal (ohne Einzel-Schichtlabels, ohne M 1:n) und Dreieck -> richtiger Stand (L14/E5)."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    p = src.new_page(width=595, height=842)
    sp = S.Spec("B 24", S.L_STD, gok=45.20, scale=50, scale_text=None, ruler=1.0,
                extra={"label_skip": set(range(len(S.L_STD)))})
    S.draw_profile(p, sp)
    ppm = S.PT_PER_M_1_1 / sp.scale
    y_gw, gx = sp.top_y + 2.8 * ppm, sp.x0 - 60
    p.draw_polyline([(gx, y_gw - 6), (gx + 7, y_gw - 6), (gx + 3.5, y_gw), (gx, y_gw - 6)],
                    color=(0, 0, 1), fill=(0, 0, 1), closePath=True, width=0.4)
    S._line(p, (gx, y_gw), (sp.x0, y_gw), 0.4)
    pdf = tmp_path / "lineal_gw.pdf"
    ws = _als_scan(src, pdf)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and bhs[0].scale == 50
    assert [round(ly.bottom, 1) for ly in bhs[0].layers] == [0.3, 1.8, 3.4, 5.0, 6.5]
    assert len(bhs[0].gw_depths) == 1 and abs(bhs[0].gw_depths[0] - 2.8) <= 0.05

    # Regel aus -> altes Verhalten: ohne Massstabstext und ohne Schichtlabels kein Massstab
    monkeypatch.setitem(P.RULES, "raster_massstab_ocr", False)
    bhs_aus = _extrahieren(monkeypatch, pdf, ws)
    assert bhs_aus == []


def test_scan_hoehenleiste_ohne_innere_schichtlinien(tmp_path, monkeypatch):
    """Scan ohne erkannte Innengrenzen (nur Kopf/Fuss der Saeule), aber mit Hoehenleiste, M 1:75 und GOK -> GW-Tiefe."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    p = src.new_page(width=595, height=842)
    ppm = S.PT_PER_M_1_1 / 75
    x0, top = 220.0, 160.0
    y_bot = top + 6.0 * ppm
    p.insert_text((x0 - 5, top - 40), "BK 1", fontsize=10)
    p.insert_text((x0 - 15, top - 22), "NHN 770,17 m", fontsize=7)
    p.insert_text((x0 - 15, y_bot + 30), "Höhenmaßstab 1:75", fontsize=8)
    # Saeule nur mit Ober- und Unterkante (wie im Scan bei farbiger Fuellung ohne schwarze Trennlinien)
    S._line(p, (x0, top), (x0, y_bot), 0.9)
    S._line(p, (x0 + 18, top), (x0 + 18, y_bot), 0.9)
    S._line(p, (x0, top), (x0 + 18, top), 0.9)
    S._line(p, (x0, y_bot), (x0 + 18, y_bot), 0.9)
    # Hoehenleiste links (772..763 m NN) und versetzte Oberkanten-Labels rechts
    for i in range(10):
        ym = top + (i - 1.83) * ppm
        p.insert_text((25, ym + 2), str(772 - i), fontsize=6.5)
    for k, v in enumerate((0.0, 0.35, 1.0, 2.5, 3.2, 4.0, 6.0)):
        p.insert_text((x0 + 38, top + k * 28 + 3), f"{v:.2f}".replace(".", ","), fontsize=6.5)
    # Volles GW-Dreieck mit Wasserlinie bei 3,00 m
    y_gw, gx = top + 3.0 * ppm, x0 - 55
    p.draw_polyline([(gx, y_gw - 6), (gx + 7, y_gw - 6), (gx + 3.5, y_gw), (gx, y_gw - 6)],
                    color=(0, 0, 1), fill=(0, 0, 1), closePath=True, width=0.4)
    S._line(p, (gx, y_gw), (x0, y_gw), 0.5)
    pdf = tmp_path / "hoehenleiste.pdf"
    ws = _als_scan(src, pdf)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and bhs[0].scale == 75
    assert len(bhs[0].gw_depths) == 1 and abs(bhs[0].gw_depths[0] - 3.0) <= 0.05

    monkeypatch.setitem(P.RULES, "raster_massstab_ocr", False)
    bhs_aus = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs_aus) == 1 and bhs_aus[0].scale is None and bhs_aus[0].gw_depths == []


def test_scan_lineal_widerspricht_grenzbeschriftungen(tmp_path, monkeypatch):
    """(b) Scan mit Lineal (1:100), das den Grenzbeschriftungen (1:50) widerspricht -> kein Stand, Hinweis."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    p = src.new_page(width=595, height=842)
    sp = S.Spec("B 25", S.L_STD, gok=45.20, scale=50, scale_text=None, label_dy=11, extra={"label_skip": {0, 2}})
    S.draw_profile(p, sp)
    ppm = S.PT_PER_M_1_1 / sp.scale
    rx = sp.x0 - 120
    S._line(p, (rx, sp.top_y), (rx, sp.top_y + 6.5 * ppm), 0.5)
    for i in range(7):
        yy = sp.top_y + i * ppm
        S._line(p, (rx, yy), (rx + 4, yy), 0.4)
        p.insert_text((rx - 26, yy + 2), S._fmt(2.0 * i, ","), fontsize=6)
    y_gw, gx = sp.top_y + 2.8 * ppm, sp.x0 - 60
    p.draw_polyline([(gx, y_gw - 6), (gx + 7, y_gw - 6), (gx + 3.5, y_gw), (gx, y_gw - 6)],
                    color=(0, 0, 1), fill=(0, 0, 1), closePath=True, width=0.4)
    S._line(p, (gx, y_gw), (sp.x0, y_gw), 0.4)
    pdf = tmp_path / "widerspruch.pdf"
    ws = _als_scan(src, pdf)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and bhs[0].scale is None
    assert bhs[0].layers == [] and bhs[0].gw_depths == []
    assert any("widersprechen sich" in iss for iss in bhs[0].issues)


def test_sv_wasserstand_art_datum_beleg_und_spaltentrennung(tmp_path, monkeypatch):
    """(c) SV-Text mit Wasserstand -> 1 Stand mit Art, Datum und Beleg; fremde Bohrung oder Regel aus -> ignoriert."""
    doc = pymupdf.open()
    S.draw_profile(doc.new_page(width=595, height=842), S.Spec("RKS 26", S.L_ABBR, shx=True, scale=200, scale_text=None))
    S.sv_pages(doc, "RKS 26", S.L_ABBR, "Wasser angetroffen bei 3,00 m u. GOK am 18.07.2023", spaced=False, dup=False)
    # Fremde Bohrung in einer Notiz darf nicht RKS 26 zugeordnet werden
    doc[-1].insert_text((372, 710), "In RKS 99 Wasser angetroffen bei 1,50 m", fontsize=7)
    pdf = tmp_path / "sv_wasser.pdf"
    doc.save(pdf)

    bhs, _ = P.extract(pdf)
    assert len(bhs) == 1 and bhs[0].gw_depths == [3.0]
    info = bhs[0].gw_info[3.0]
    assert info["kind"] == "angetroffen" and info.get("observed_on") == "2023-07-18"
    assert "3,00" in info.get("evidence", "")

    # Regel aus -> altes Verhalten: 'Wasser angetroffen bei ...' wird von der alten SV_GW_RE nicht gelesen
    monkeypatch.setitem(P.RULES, "sv_wasser", False)
    bhs_aus, _ = P.extract(pdf)
    assert len(bhs_aus) == 1 and bhs_aus[0].gw_depths == []


def test_sv_kein_grundwasser_status(tmp_path):
    """(d) SV-Text 'kein Grundwasser' -> 0 Staende und groundwater_status = 'kein Grundwasser'."""
    doc = pymupdf.open()
    S.draw_profile(doc.new_page(width=595, height=842), S.Spec("RKS 27", S.L_ABBR, shx=True, scale=200, scale_text=None))
    S.sv_pages(doc, "RKS 27", S.L_ABBR, "kein Grundwasser angetroffen", spaced=False, dup=False)
    pdf = tmp_path / "sv_kein_gw.pdf"
    doc.save(pdf)

    bhs, dph = P.extract(pdf)
    assert len(bhs) == 1 and bhs[0].gw_depths == [] and bhs[0].gw_status == "kein Grundwasser"
    kan = P.to_canonical(pdf, bhs, dph)
    assert kan["boreholes"][0]["groundwater"] == []
    assert kan["boreholes"][0]["groundwater_status"] == "kein Grundwasser"
