"""Tests fuer die Zeilen-Leserichtung unabhaengig von y0-Schwankungen (Issue #49).

Ohne Netz:
- Stressfall s28 (gemischte Schriftgroesse / versetzte Grundlinie 'B 2'): mit Regel richtig, ohne Regel reproduziert
  der Fall den Fehler ('2 B' statt 'B 2').
- Verwackeln von y0 innerhalb jeder Zeile um +/-0,8 pt auf normalem und 90°-gedrehtem Profil liefert exakt
  dasselbe Extraktionsergebnis (Bohrungen, Grenzen, Bodenarten, GOK, GW).
- Auch sondierungen._seiten_primitive bleibt bei +/-0,8 pt y0-Wackeln innerhalb einer Zeile stabil.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pymupdf
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "extractor"))

import prototyp_v4 as v4  # noqa: E402
import sondierungen as sd  # noqa: E402
import stress_cases as sc  # noqa: E402


def _extrahieren(pdf: Path) -> dict:
    bhs, dph = v4.extract(pdf)
    return v4.to_canonical(pdf, bhs, dph)


def _kanon_signatur(doc: dict) -> list[dict]:
    return [
        {
            "code": b["code"],
            "gok_nhn": b.get("gok_nhn"),
            "layers": [(ly["top_depth"], ly["bottom_depth"], ly["soil_class"]) for ly in b.get("layers", [])],
            "gw": sorted(g["depth"] for g in b.get("groundwater", [])),
        }
        for b in sorted(doc.get("boreholes", []), key=lambda x: x["code"])
    ]


def test_s28_zeile_grundlinie_und_ablation(tmp_path: Path):
    """s28 hat y0('2') < y0('B') in derselben Zeile: mit line_reading_order 1/1 'B 2', ohne Regel 0/1."""
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    sp = sc.Spec("B 2", sc.L_STD, title="", gok=45.20, gw=("symbol", 2.8))
    sc.draw_profile(p, sp)
    p.insert_text((sp.x0 - 20, sp.top_y - 40), "B", fontsize=10)
    p.insert_text((sp.x0 - 10, sp.top_y - 40.6), "2", fontsize=12)
    pdf = tmp_path / "s28_zeile_grundlinie.pdf"
    doc.save(pdf)
    doc.close()

    # Vorbedingung: MuPDF legt 'B' und '2' in dieselbe Zeile, mit y0('2') < y0('B')
    with pymupdf.open(pdf) as d:
        ws = [w for w in d[0].get_text("words") if w[4] in ("B", "2")]
    assert len(ws) == 2
    b_w, z_w = (ws[0], ws[1]) if ws[0][4] == "B" else (ws[1], ws[0])
    assert (b_w[5], b_w[6]) == (z_w[5], z_w[6]), "B und 2 muessen in derselben (Block, Zeile) liegen"
    assert z_w[1] < b_w[1], "y0('2') muss kleiner als y0('B') sein"

    # Mit Regel: exakt B 2, 5 Schichten, GOK, GW
    res_an = _extrahieren(pdf)
    assert [b["code"] for b in res_an["boreholes"]] == ["B 2"]
    assert len(res_an["boreholes"][0]["layers"]) == 5
    assert res_an["boreholes"][0]["gok_nhn"] == pytest.approx(45.20, abs=0.01)
    assert [g["depth"] for g in res_an["boreholes"][0]["groundwater"]] == [pytest.approx(2.8, abs=0.05)]

    # Ohne Regel (Ablation): Fehler wird reproduziert ('2 B' statt 'B 2')
    alt = v4.RULES["line_reading_order"]
    try:
        v4.RULES["line_reading_order"] = False
        res_aus = _extrahieren(pdf)
        assert [b["code"] for b in res_aus["boreholes"]] == []
    finally:
        v4.RULES["line_reading_order"] = alt


@pytest.mark.parametrize("rotation", [0, 90])
def test_y0_verwackeln_innerhalb_zeile_identisch(tmp_path: Path, monkeypatch, rotation: int):
    """+/-0,8 pt Wackeln auf y0/y1 jedes Wortes darf das Extraktionsergebnis nicht veraendern."""
    src = pymupdf.open()
    sc.draw_profile(src.new_page(width=595, height=842), sc.Spec("B 1", sc.L_STD, gok=45.20, gw=("symbol", 2.8)))
    if rotation:
        doc = pymupdf.open()
        p = doc.new_page(width=842, height=595)
        p.show_pdf_page(p.rect, src, 0, rotate=rotation)
        p.set_rotation(rotation)
        src.close()
    else:
        doc = src
    pdf = tmp_path / f"wackel_rot{rotation}.pdf"
    doc.save(pdf)
    doc.close()

    referenz = _kanon_signatur(_extrahieren(pdf))
    assert len(referenz) == 1 and referenz[0]["code"] == "B 1"

    orig_get_text = pymupdf.Page.get_text
    rng = random.Random(49)

    def wackel_get_text(self, option="text", *args, **kwargs):
        out = orig_get_text(self, option, *args, **kwargs)
        if option == "words":
            geackelt = []
            for w in out:
                # Innerhalb derselben Zeile gegensaetzlich um bis zu +/-0,8 pt verwackeln
                dy = rng.uniform(-0.8, 0.8)
                geackelt.append((w[0], w[1] + dy, w[2], w[3] + dy, w[4], w[5], w[6], w[7]))
            return geackelt
        return out

    monkeypatch.setattr(pymupdf.Page, "get_text", wackel_get_text)
    gewackelt = _kanon_signatur(_extrahieren(pdf))
    assert gewackelt == referenz


def test_sondierungen_primitive_y0_verwackelt(tmp_path: Path):
    """Auch sondierungen._seiten_primitive liest 'DPH 1' richtig, wenn y0('1') < y0('DPH')."""
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    p.insert_text((100, 100), "DPH", fontsize=10)
    p.insert_text((124, 99.3), "1", fontsize=12)
    pdf = tmp_path / "dph_wackel.pdf"
    doc.save(pdf)
    doc.close()

    with pymupdf.open(pdf) as d:
        daten = sd._seiten_primitive(d[0], 1, ocr=False)
    assert any("DPH 1" in t for _, t in daten.text_lines)
