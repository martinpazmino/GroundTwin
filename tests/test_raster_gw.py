"""Issue #20 (W4): Grundwasser-Symbol in gescannten Bohrprofilen ohne Netz und ohne echte Gutachten.

Jeder Test zeichnet ein Profil mit PyMuPDF, merkt sich die Woerter (ersetzt OCR deterministisch wie in
test_textebene_ocr.py), rendert die Seite zu einem Rasterbild (150 dpi) und legt das Bild als reine
Bildseite ohne Vektoren ab. Geprueft werden Treffer (voll/offen/halb/Dach mit Legende/gedreht),
Fehlalarm-Fallen (Dreiecks-Schraffur in der Saeule, Dreieck ohne Wasserlinie, Hoehenmarke mit Kote,
Hoehenleiste, GOK-Dreieck, Dach ohne Legende) sowie 'Regel aus -> altes Verhalten'.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "extractor"))
import prototyp_v4 as P  # noqa: E402
import stress_cases as S  # noqa: E402


def _als_scan(src: pymupdf.Document, ziel: Path, dpi: int = 150, rot90: bool = False) -> list[list[tuple]]:
    """Rendert jede Seite als 150-dpi-Bildseite ohne Textlage und liefert die Referenzwoerter je Seite."""
    scan = pymupdf.open()
    woerter = []
    for seite in src:
        ws = [(pymupdf.Rect(w[:4]) * seite.rotation_matrix, w[4], w[5], w[6]) for w in seite.get_text("words")]
        pix = seite.get_pixmap(dpi=dpi)
        if rot90:
            tmp = pymupdf.open()
            tp = tmp.new_page(width=seite.rect.width, height=seite.rect.height)
            tp.insert_image(tp.rect, pixmap=pix)
            q = scan.new_page(width=seite.rect.height, height=seite.rect.width)
            q.show_pdf_page(q.rect, tmp, 0, rotate=90)
            q.set_rotation(90)
        else:
            q = scan.new_page(width=seite.rect.width, height=seite.rect.height)
            q.insert_image(q.rect, pixmap=pix)
        woerter.append(ws)
    scan.save(ziel)
    return woerter


def _extrahieren(monkeypatch, pdf: Path, woerter: list[list[tuple]]):
    monkeypatch.setattr(P, "ocr_words", lambda page, dpi=None, min_conf=0.5: woerter[page.number])
    return P.extract(pdf)[0]


def test_regelschalter_vorhanden():
    """Die W4-Regeln sind in RULES einzeln abschaltbar (Ablation, P10)."""
    assert "raster_gw_symbol" in P.RULES and "raster_gw_legende" in P.RULES


def test_scan_volles_dreieck_mit_wasserlinie(tmp_path, monkeypatch):
    """(a) Scan mit vollem Dreieck und Wasserlinie -> genau 1 Stand, Regel aus -> 0 Staende."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    S.draw_profile(src.new_page(width=595, height=842), S.Spec("B 20", S.L_STD, gok=45.20, gw=("symbol", 2.8)))
    pdf = tmp_path / "voll.pdf"
    ws = _als_scan(src, pdf)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and len(bhs[0].gw_depths) == 1 and abs(bhs[0].gw_depths[0] - 2.8) <= 0.05

    monkeypatch.setitem(P.RULES, "raster_gw_symbol", False)
    bhs_aus = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs_aus) == 1 and bhs_aus[0].gw_depths == []


@pytest.mark.parametrize("halb, tiefe", [(False, 3.1), (True, 2.6)])
def test_scan_offenes_und_halb_gefuelltes_dreieck(tmp_path, monkeypatch, halb, tiefe):
    """Offenes Dreieck (Hausham RKS) und halb gefuelltes Dreieck (DIN 4023, Triefenstein) im Scan."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    p = src.new_page(width=595, height=842)
    sp = S.Spec("B 20b", S.L_STD, gok=45.20)
    S.draw_profile(p, sp)
    ppm = S.PT_PER_M_1_1 / sp.scale
    y, gx = sp.top_y + tiefe * ppm, sp.x0 - 60
    p.draw_polyline([(gx, y - 6.5), (gx + 7, y - 6.5), (gx + 3.5, y), (gx, y - 6.5)],
                    color=(0, 0, 0), closePath=True, width=0.5)
    if halb:
        p.draw_polyline([(gx + 3.5, y - 6.5), (gx + 7, y - 6.5), (gx + 3.5, y), (gx + 3.5, y - 6.5)],
                        color=(0, 0, 0), fill=(0, 0, 0), closePath=True, width=0.3)
    S._line(p, (gx, y), (sp.x0, y), 0.5)
    pdf = tmp_path / f"tri_{halb}.pdf"
    ws = _als_scan(src, pdf)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and len(bhs[0].gw_depths) == 1 and abs(bhs[0].gw_depths[0] - tiefe) <= 0.05


def test_scan_schraffur_dreiecke_in_saeule_kein_wasser(tmp_path, monkeypatch):
    """(b) Scan mit Schraffur aus Dreiecken und Winkeln in der Saeule ohne Wasser -> 0 Staende."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    p = src.new_page(width=595, height=842)
    sp = S.Spec("B 21", S.L_STD, gok=45.20)
    S.draw_profile(p, sp)
    ppm = S.PT_PER_M_1_1 / sp.scale
    for d_m in (0.8, 1.3, 2.2, 2.8, 4.0, 4.6, 5.6):
        yy = sp.top_y + d_m * ppm
        p.draw_polyline([(sp.x0 + 3, yy - 6), (sp.x0 + 10, yy - 6), (sp.x0 + 6.5, yy), (sp.x0 + 3, yy - 6)],
                        color=(0, 0, 0), fill=(0, 0, 0), closePath=True, width=0.4)
        p.draw_polyline([(sp.x0 + 12, yy), (sp.x0 + 15.5, yy - 6), (sp.x0 + 19, yy)], color=(0, 0, 0), width=0.4)
        S._line(p, (sp.x0 + 2.5, yy), (sp.x0 + sp.col_w - 2.5, yy), 0.4)
    pdf = tmp_path / "schraffur.pdf"
    ws = _als_scan(src, pdf)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and bhs[0].gw_depths == []


def test_scan_dreieck_ohne_wasserlinie_und_hoehenmarke(tmp_path, monkeypatch):
    """(c) Scan mit Dreieck ohne Wasserlinie, Hoehenmarke mit Kote, Hoehenleiste und GOK-Dreieck -> 0 Staende."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    p = src.new_page(width=595, height=842)
    sp = S.Spec("B 22", S.L_STD, gok=742.50, elev_triangles=True)
    S.draw_profile(p, sp)
    ppm = S.PT_PER_M_1_1 / sp.scale
    # Offenes Dreieck ohne Wasserlinie
    y1 = sp.top_y + 2.5 * ppm
    p.draw_polyline([(sp.x0 - 55, y1 - 7), (sp.x0 - 48, y1 - 7), (sp.x0 - 51.5, y1), (sp.x0 - 55, y1 - 7)],
                    color=(0, 0, 0), closePath=True, width=0.5)
    # Hoehenmarke mit Kote und Linie
    y2 = sp.top_y + 3.8 * ppm
    p.draw_polyline([(sp.x0 - 80, y2 - 7), (sp.x0 - 73, y2 - 7), (sp.x0 - 76.5, y2), (sp.x0 - 80, y2 - 7)],
                    color=(0, 0, 0), closePath=True, width=0.5)
    S._line(p, (sp.x0 - 80, y2), (sp.x0 - 30, y2), 0.4)
    p.insert_text((sp.x0 - 68, y2 - 1), "738,70m", fontsize=6.5)
    # GOK-Dreieck bei Tiefe 0,00
    p.draw_polyline([(sp.x0 + 8, sp.top_y - 6), (sp.x0 + 14, sp.top_y - 6), (sp.x0 + 11, sp.top_y),
                     (sp.x0 + 8, sp.top_y - 6)], color=(0, 0, 0), fill=(0, 0, 0), closePath=True, width=0.4)
    pdf = tmp_path / "ohne_linie.pdf"
    ws = _als_scan(src, pdf)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and bhs[0].gw_depths == []


def test_scan_legende_dach_und_ohne_legende(tmp_path, monkeypatch):
    """W3 + W4: Dach im Scan zaehlt nur mit Legende; Legenden-Regel aus -> nur das Dreieck."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    S.draw_profile(src.new_page(width=595, height=842),
                   S.Spec("BK 23", S.L_STD, gok=45.0, gw=("symbol", 1.8), extra={"dach": 3.6, "legende": True}))
    pdf = tmp_path / "mit_legende.pdf"
    ws = _als_scan(src, pdf)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and len(bhs[0].gw_depths) == 2
    assert abs(bhs[0].gw_depths[0] - 1.8) <= 0.05 and abs(bhs[0].gw_depths[1] - 3.6) <= 0.05
    assert bhs[0].gw_info[bhs[0].gw_depths[0]]["kind"] == "Ruhewasser"
    assert bhs[0].gw_info[bhs[0].gw_depths[1]]["kind"] == "angetroffen"

    monkeypatch.setitem(P.RULES, "raster_gw_legende", False)
    bhs_ohne = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs_ohne) == 1 and len(bhs_ohne[0].gw_depths) == 1 and abs(bhs_ohne[0].gw_depths[0] - 1.8) <= 0.05

    # Ohne Legende auf der Seite: Dach ergibt keinen Wasserstand
    monkeypatch.setitem(P.RULES, "raster_gw_legende", True)
    src2 = pymupdf.open()
    S.draw_profile(src2.new_page(width=595, height=842), S.Spec("BK 24", S.L_STD, gok=45.0, extra={"dach": 3.6}))
    pdf2 = tmp_path / "ohne_legende.pdf"
    ws2 = _als_scan(src2, pdf2)
    bhs2 = _extrahieren(monkeypatch, pdf2, ws2)
    assert len(bhs2) == 1 and bhs2[0].gw_depths == []


def test_scan_gedreht_90(tmp_path, monkeypatch):
    """Gedrehte gescannte Seite (/Rotate 90): GW-Symbol wird in Ansichtskoordinaten gefunden."""
    pytest.importorskip("cv2")
    src = pymupdf.open()
    S.draw_profile(src.new_page(width=595, height=842), S.Spec("B 25", S.L_STD, gok=45.20, gw=("symbol", 2.8)))
    pdf = tmp_path / "rot90.pdf"
    ws = _als_scan(src, pdf, rot90=True)

    bhs = _extrahieren(monkeypatch, pdf, ws)
    assert len(bhs) == 1 and len(bhs[0].gw_depths) == 1 and abs(bhs[0].gw_depths[0] - 2.8) <= 0.05
