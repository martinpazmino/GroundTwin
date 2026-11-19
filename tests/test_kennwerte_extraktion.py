"""Issue #18: Bodenkennwerte aus dem Text des Gutachtens - Tabelle mit Spalten (auch Kopf ueber zwei Zeilen) und
Liste je Schicht; Spannen, Tausenderpunkt, kN/m2 -> MN/m2, unplausible Werte markiert."""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "extractor"))
import kennwerte as K  # noqa: E402


@pytest.mark.parametrize("text, param, kopf, erwartet", [
    ("11 - 20", "wichte", "", (11.0, 20.0)),
    ("17,0", "wichte", "", (17.0, 17.0)),
    ("300 - 10.000", "steifemodul", "[kN/m2]", (0.3, 10.0)),      # Tausenderpunkt, kN/m2 -> MN/m2
    ("2 - 10 MN/m 2", "steifemodul", "", (2.0, 10.0)),
    ("22,5 – 27,5 °", "reibungswinkel", "", (22.5, 27.5)),
    ("-", "kohaesion", "", None),
    ("18√𝑡 / 72√𝑡", "steifemodul", "", None),                    # keine Zahl: nur Text
])
def test_wert(text, param, kopf, erwartet):
    w = K.wert(text, param, kopf)
    assert (None if "min" not in w else (w["min"], w["max"])) == erwartet
    assert w["text"]


def test_param_von():
    assert K.param_von("Reibungswinkel φ’k") == "reibungswinkel"
    assert K.param_von("Wichte γ’k") == "wichte_auftrieb" and K.param_von("Wichte γk") == "wichte"
    assert K.param_von("Wichte, unter Auftrieb γ`k") == "wichte_auftrieb"
    assert K.param_von("undränierte Scherfestigkeit cu") == "kohaesion_undrainiert"
    assert K.param_von("Steifemodul ES,k [kN/m2]") == "steifemodul"
    assert K.param_von("Kohä­sion c'") == "kohaesion"                       # weiches Trennzeichen
    assert K.param_von("Wandreibungswinkel (δ = 2/3 . ϕ´)") is None            # eigene Zahl: keine Kopfzelle
    assert K.param_von("Für die Berechnung können die Werte der Tabelle mit dem Reibungswinkel angesetzt werden") is None


def _tabelle(pfad):
    doc = pymupdf.open()
    s = doc.new_page()
    s.insert_text((70, 60), "Tabelle 6: Geotechnische Bodenkennwerte", fontsize=9)
    # Standardschrift ohne griechische Zeichen: die Namen genuegen (die Symbole prueft test_param_von)
    for x, t1, t2 in ((170, "Wichte", "[kN/m3]"), (240, "Auftrieb", "[kN/m3]"), (310, "Reibungs-", "winkel"),
                      (400, "Kohäsion", "[kN/m2]"), (470, "Steifemodul", "[kN/m2]")):
        s.insert_text((x, 90), t1, fontsize=8)
        s.insert_text((x, 100), t2, fontsize=8)
    s.insert_text((320, 110), "[°]", fontsize=8)
    for y, bez, werte in ((140, "Auffüllung (A, [GE])", ("11 - 20", "1 - 12", "15 - 32", "0 - 5", "300 - 10.000")),
                          (175, "Auelehm (UL, TL)", ("14 - 20", "4 - 10", "15 - 27", "0 - 5", "1.000 - 10.000")),
                          (210, "Niederterrasse (SE, GW)", ("17 - 22", "10 - 12", "28 - 37", "0 - 5", "20.000 - 30.000"))):
        s.insert_text((70, y), bez, fontsize=8)
        for x, w in zip((175, 245, 320, 410, 475), werte):
            s.insert_text((x, y), w, fontsize=8)
    s.insert_text((70, 300), "Die Werte gelten für die beschriebenen Böden ohne baubedingte Auflockerung.", fontsize=9)
    doc.save(pfad)


def test_tabelle_mit_spalten(tmp_path):
    _tabelle(tmp_path / "t.pdf")
    z = K.lesen(tmp_path / "t.pdf")
    assert [e["form"] for e in z] == ["Tabelle"] * 3
    assert [e["bezeichnung"] for e in z] == ["Auffüllung (A, [GE])", "Auelehm (UL, TL)", "Niederterrasse (SE, GW)"]
    a = z[0]["werte"]
    assert (a["wichte"]["min"], a["wichte"]["max"]) == (11.0, 20.0)
    assert (a["reibungswinkel"]["min"], a["reibungswinkel"]["max"]) == (15.0, 32.0)      # Kopf ueber zwei Zeilen
    assert (a["steifemodul"]["min"], a["steifemodul"]["max"]) == (0.3, 10.0)            # kN/m2 -> MN/m2
    assert any("Wichte unter Auftrieb" in h for h in z[0]["hinweise"])                   # 1 kN/m3: markiert
    assert z[1]["bodengruppen"] == ["TL", "UL"] and z[2]["bodengruppen"] == ["GW", "SE"]


def test_liste_je_schicht(tmp_path):
    doc = pymupdf.open()
    s = doc.new_page()
    y = 80
    namen = ("Reibungswinkel", "Kohäsion", "Wichte", "Wichte unter Auftrieb", "Steifemodul")
    for kopf, werte in (("Schicht 2 - Auffüllung", zip(namen, ("30,0°", "0 kN/m²", "20 kN/m³", "10 kN/m³", "5 MN/m²"))),
                        ("Schicht 3 - Pleistozäne Kiese",
                         zip(namen, ("37,5°", "0 kN/m²", "21 kN/m³", "11 kN/m³", "80 MN/m²")))):
        s.insert_text((70, y), kopf, fontsize=9)
        y += 16
        for sym, w in werte:
            s.insert_text((80, y), sym, fontsize=9)
            s.insert_text((200, y), w, fontsize=9)
            y += 13
        y += 10
    doc.save(tmp_path / "l.pdf")
    z = K.lesen(tmp_path / "l.pdf")
    assert [(e["form"], e["bezeichnung"]) for e in z] == [("Liste", "Schicht 2 - Auffüllung"),
                                                          ("Liste", "Schicht 3 - Pleistozäne Kiese")]
    assert z[1]["werte"]["reibungswinkel"]["min"] == 37.5 and z[1]["werte"]["steifemodul"]["max"] == 80.0
    assert z[0]["werte"]["wichte_auftrieb"]["min"] == 10.0


def test_fliesstext_ohne_tabelle(tmp_path):
    doc = pymupdf.open()
    s = doc.new_page()
    s.insert_text((70, 80), "Dem Sand wird ein Steifemodul von ca. Es = 40 MN/m2 zugeordnet.", fontsize=9)
    s.insert_text((70, 100), "Die Wichte und der Reibungswinkel folgen aus der Tabelle; die Kohäsion ist null.", fontsize=9)
    doc.save(tmp_path / "f.pdf")
    assert K.lesen(tmp_path / "f.pdf") == []
