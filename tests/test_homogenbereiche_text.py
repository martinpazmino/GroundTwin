"""Issue #21: Homogenbereiche des Gutachters aus dem Bericht - Tabelle, Abschnitt (ueber den Seitenwechsel) und Satz;
Bodengruppen in eckigen Klammern getrennt; ATV aus dem Abschnitt, sonst markiert."""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "extractor"))
import homogenbereiche_text as H  # noqa: E402


def test_gruppen_mit_klammern_und_stern():
    assert H.gruppen("A, [OU], [OH], SE, SU*, ST*") == (["A", "SE", "ST*", "SU*"], ["OH", "OU"])
    assert H.gruppen("GE, GW, GŪ, SU") == (["GE", "GU*", "GW", "SU"], [])


def test_tabelle_abschnitt_und_satz(tmp_path):
    doc = pymupdf.open()
    s = doc.new_page()
    s.insert_text((70, 60), "Die Homogenbereiche fuer Erdarbeiten (DIN 18300) und Bohrarbeiten (DIN 18301):", fontsize=9)
    for y, links, kopf in ((100, "ST*, UL, TL (Auelehm)", "Homogenbereich B"),
                           (130, "SE, SU, GW (Niederterrasse)", "Homogenbereich C")):
        s.insert_text((80, y), links, fontsize=9)
        s.insert_text((350, y), kopf, fontsize=9)
    s.insert_text((70, 200), "4.5 Homogenbereich 1 - aufgefuellter Oberboden", fontsize=9)
    s.insert_text((70, 215), "Bodengruppen nach DIN 18196: OH", fontsize=9)
    s.insert_text((70, 240), "Homogenbereich 2 - Auffuellboeden", fontsize=9)
    s = doc.new_page()                                                    # Fortsetzung auf der naechsten Seite
    s.insert_text((70, 60), "Bodengruppen nach DIN 18196:", fontsize=9)
    s.insert_text((70, 74), "GE, GW, SU", fontsize=9)
    s.insert_text((70, 100), "4.6 Bodenkennwerte", fontsize=9)
    s.insert_text((70, 115), "Bodengruppen nach DIN 18196: TL", fontsize=9)            # nach dem Abschnitt: nicht mehr 2
    s.insert_text((70, 140), "Der Oberboden bildet den Homogenbereich O1. In den Homogenbereich B3 werden die", fontsize=9)
    s.insert_text((70, 152), "quartaeren Loesslehme klassifiziert.", fontsize=9)
    doc.save(tmp_path / "h.pdf")
    je = {e["bereich"]: e for e in H.lesen(tmp_path / "h.pdf")}
    assert set(je) == {"B", "C", "1", "2", "O1", "B3"}
    assert (je["B"]["form"], je["B"]["name"], je["B"]["bodengruppen"]) == ("Tabelle", "Auelehm", ["ST*", "TL", "UL"])
    assert je["C"]["name"] == "Niederterrasse"
    assert je["1"]["bodengruppen"] == ["OH"] and je["1"]["name"] == "aufgefuellter Oberboden"
    assert je["2"]["bodengruppen"] == ["GE", "GW", "SU"]                                   # ueber den Seitenwechsel
    assert je["O1"]["name"] == "Oberboden" and je["B3"]["name"] == "quartaeren Loesslehme"
    assert all(e["atv"] == ["DIN 18300", "DIN 18301"] for e in je.values())


def test_ohne_atv_markiert(tmp_path):
    doc = pymupdf.open()
    doc.new_page().insert_text((70, 60), "Homogenbereich A - Kies", fontsize=9)
    doc.save(tmp_path / "o.pdf")
    (e,) = H.lesen(tmp_path / "o.pdf")
    assert e["atv"] == [] and "ATV im Bericht nicht genannt" in e["hinweise"]
