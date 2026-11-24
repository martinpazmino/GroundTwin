"""Tests ohne Netz fuer Wasserlinien im Laengsschnitt (Issue #26 Teil 2b, Regel ls_wasserlinien).

Prueft alle 5 synthetischen Laengsschnitte aus synth_laengsschnitt.py:
- ls01_konstant: HGW und MGW exakt (+/-0,05 m), quelle="Laengsschnitt", nie als Bohrungs-GW
- ls02_geneigt: Bemessungswasserstand und GW <Datum> mit Stuetzpunkten je Station
- ls03_text_abgleich: Uebereinstimmung (+/-5 cm) -> 1 Eintrag mit beiden Belegen; Widerspruch -> 2 Eintraege + Hinweis
- ls04_fallen: 0 falsche Wasserlinien bei allen 4 Fallen + Hinweis fuer mehrdeutiges MHGW
- ls05_unkalibriert: 0 Wasserlinien ohne kalibrierte NHN-Achse + Hinweis
- Ablation: RULES["ls_wasserlinien"] = False schaltet die Erkennung sauber ab
- Gedrehter Laengsschnitt (/Rotate 90): identische Wasserlinien
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pymupdf
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "extractor"))

import prototyp_v4 as v4  # noqa: E402
import synth_laengsschnitt as sl  # noqa: E402


def _extrahieren(pdf: Path) -> dict:
    bhs, dph = v4.extract(pdf)
    return v4.to_canonical(pdf, bhs, dph)


def test_synthetische_laengsschnitte_alle_faelle(tmp_path: Path):
    sl.build(tmp_path)

    # ls01: konstant (HGW 42.50, MGW 40.20)
    k1 = _extrahieren(tmp_path / "ls01_konstant.pdf")
    w1 = {e["kind"]: e for e in k1["wasserstaende"]}
    assert set(w1) == {"HGW", "MGW"}
    assert w1["HGW"]["nhn"] == pytest.approx(42.50, abs=0.05)
    assert w1["MGW"]["nhn"] == pytest.approx(40.20, abs=0.05)
    assert all(e["quelle"] == "Laengsschnitt" for e in w1.values())
    assert all(not b.get("groundwater") for b in k1["boreholes"])

    # ls02: geneigt mit Stationen + Datum
    k2 = _extrahieren(tmp_path / "ls02_geneigt.pdf")
    w2 = {e["kind"]: e for e in k2["wasserstaende"]}
    assert set(w2) == {"Bemessungswasserstand", "GW"}
    assert w2["GW"]["observed_on"] == "2024-05-14"
    bem_pts = w2["Bemessungswasserstand"]["stuetzpunkte"]
    assert len(bem_pts) == 3
    assert bem_pts[0]["nhn"] == pytest.approx(58.40, abs=0.05)
    assert bem_pts[-1]["nhn"] == pytest.approx(56.90, abs=0.05)
    assert bem_pts[-1]["station"] - bem_pts[0]["station"] == pytest.approx(300.0, abs=3.0)

    # ls03: Text <-> Laengsschnitt Abgleich
    k3 = _extrahieren(tmp_path / "ls03_text_abgleich.pdf")
    bem3 = [e for e in k3["wasserstaende"] if e["kind"] == "Bemessungswasserstand"]
    hgw3 = [e for e in k3["wasserstaende"] if e["kind"] == "HGW"]
    assert len(bem3) == 1
    assert bem3[0]["quelle"] == "Text+Laengsschnitt"
    assert len(bem3[0]["belege"]) == 2
    assert len(hgw3) == 2
    assert {e["quelle"] for e in hgw3} == {"Text", "Laengsschnitt"}
    assert all("hinweis" in e and "Widerspruch" in e["hinweis"] for e in hgw3)
    assert any("Widerspruch" in h for h in k3.get("wasserlinien_hinweise", []))

    # ls04: Alle 4 Fallen -> 0 Wasserlinien + Hinweis fuer mehrdeutiges MHGW
    k4 = _extrahieren(tmp_path / "ls04_fallen.pdf")
    assert k4["wasserstaende"] == []
    assert any("MHGW" in h for h in k4.get("wasserlinien_hinweise", []))

    # ls05: Unkalibriert -> 0 Wasserlinien + Hinweis
    k5 = _extrahieren(tmp_path / "ls05_unkalibriert.pdf")
    assert k5["wasserstaende"] == []
    assert any("NHN" in h for h in k5.get("wasserlinien_hinweise", []))


def test_ablation_ls_wasserlinien(tmp_path: Path):
    sl.build(tmp_path)
    pdf = tmp_path / "ls01_konstant.pdf"
    alt = v4.RULES["ls_wasserlinien"]
    try:
        v4.RULES["ls_wasserlinien"] = False
        k_aus = _extrahieren(pdf)
        assert k_aus["wasserstaende"] == []
    finally:
        v4.RULES["ls_wasserlinien"] = alt


def test_gedrehter_laengsschnitt_rot90(tmp_path: Path):
    sl.build(tmp_path)
    src = pymupdf.open(tmp_path / "ls01_konstant.pdf")
    doc = pymupdf.open()
    r = src[0].rect
    q = doc.new_page(width=r.height, height=r.width)
    q.show_pdf_page(q.rect, src, 0, rotate=90)
    q.set_rotation(90)
    rot_pdf = tmp_path / "ls01_rot90.pdf"
    doc.save(rot_pdf)
    doc.close()
    src.close()

    k = _extrahieren(rot_pdf)
    w = {e["kind"]: e for e in k["wasserstaende"]}
    assert set(w) == {"HGW", "MGW"}
    assert w["HGW"]["nhn"] == pytest.approx(42.50, abs=0.05)
    assert w["MGW"]["nhn"] == pytest.approx(40.20, abs=0.05)


def test_widerspruechliche_nhn_achsen_abgelehnt(tmp_path: Path):
    """Zwei widerspruechliche NHN-Achsen (links/rechts um 2 m versetzt) -> 0 Wasserlinien + Hinweis."""
    doc = pymupdf.open()
    p = doc.new_page(width=842, height=595)
    g = sl._zeichne_grundgeruest(p, mit_nhn_achse=False, mit_stationen=True)
    # Linke Achse: 50..36, rechte Achse: 52..38 (2 m Widerspruch)
    for ax_x, align_dx, offset in ((g["x0"] - 15, -36, 0.0), (g["x1"] + 15, 6, 2.0)):
        for i in range(8):
            v = 50.0 - 2.0 * i + offset
            yy = g["y_oben"] + i * 2.0 * g["pt_pro_m"]
            p.insert_text((ax_x + align_dx, yy + 2.2), f"{v:.2f}".replace(".", ","), fontsize=6.5)
    yy = sl._nhn_zu_y(42.5, g["nhn_oben"], g["y_oben"], g["pt_pro_m"])
    p.draw_line((g["x0"], yy), (g["x1"], yy), color=(0.0, 0.25, 0.9), width=0.9, dashes="[6 3] 0")
    p.insert_text((g["x0"] + 10, yy - 3), "HGW", fontsize=7.5, color=(0.0, 0.25, 0.9))
    pdf = tmp_path / "ls_widerspruch_achsen.pdf"
    doc.save(pdf)
    doc.close()

    k = _extrahieren(pdf)
    assert k["wasserstaende"] == []
    assert any("Widerspruechliche NHN" in h for h in k.get("wasserlinien_hinweise", []))
