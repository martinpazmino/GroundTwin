"""Issue #26: Wasserstands-Tabelle im Bericht - Art aus Fussnote, Spalte oder Satz (nie geraten), Zusammenfuehren
mit den Staenden der Bohrungen (ergaenzen oder neu mit Beleg und Meldung)."""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "extractor"))
import wassertabelle as W  # noqa: E402


def _pdf(pfad, zeilen):
    doc = pymupdf.open()
    s = doc.new_page()
    for i, z in enumerate(zeilen):
        s.insert_text((60, 50 + 12 * i), z, fontsize=8)
    doc.save(pfad)


def test_tabelle_mit_fussnote_und_satz(tmp_path):
    _pdf(tmp_path / "w.pdf", ["Vom 01.07. bis 15.10.2020 wurde Grundwasser in den Aufschluessen wie folgt nach Bohrende",
                              "eingemessen.", "Tabelle 2", "Aufschluss", "Wasserstaende", "[m u. GOK]", "Wasserart",
                              "KRB 1/20", "3,74", "Grundwasser", "KRB 2/20", "3,00*", "Grundwasser",
                              "KRB 3/20", "1,20", "Schichtenwasser", "KRB 4/20", "-", "kein Wasser",
                              "*) Grundwasseranschnitt"])
    z = {r["code"]: r for r in W.lesen(tmp_path / "w.pdf")}
    assert (z["KRB 1/20"]["kind"], z["KRB 1/20"]["depth"]) == ("Bohrende", 3.74)          # aus dem Satz
    assert z["KRB 2/20"]["kind"] == "angetroffen" and "Fußnote" in z["KRB 2/20"]["evidence"]
    assert z["KRB 3/20"]["kind"] == "Schichtenwasser"                                    # Spalte vor Satz
    assert "KRB 4/20" not in z                                                           # ohne Tiefe keine Zeile
    assert "observed_on" not in z["KRB 1/20"]                                            # Zeitraum ist kein Messtag


def test_ohne_tabelle_nichts(tmp_path):
    _pdf(tmp_path / "o.pdf", ["Grundwasser wurde in keiner Bohrung angetroffen.", "B 1", "3,20"])
    assert W.lesen(tmp_path / "o.pdf") == []                                              # kein 'm u. GOK'


def test_einarbeiten():
    doc = {"boreholes": [{"code": "KRB 1/20", "gok_nhn": 80.0, "groundwater": [{"depth": 3.74, "kind": "unbestimmt"}]},
                         {"code": "KRB 2/20", "gok_nhn": 81.0, "groundwater": [], "groundwater_status": "kein Grundwasser"}]}
    zeilen = [{"code": "KRB 1/20", "depth": 3.75, "kind": "Bohrende", "page": 9, "evidence": "Tabelle S. 10"},
              {"code": "KRB2/20", "depth": 3.0, "kind": "angetroffen", "page": 9, "evidence": "Tabelle S. 10"},
              {"code": "KRB 9/20", "depth": 2.0, "kind": "Bohrende", "page": 9, "evidence": "x"}]
    n = W.einarbeiten(doc, zeilen)
    assert n == {"ergaenzt": 1, "neu": 1, "ohne_bohrung": 1}
    b1, b2 = doc["boreholes"]
    assert b1["groundwater"][0]["kind"] == "Bohrende" and len(b1["groundwater"]) == 1      # gleiche Tiefe: ergaenzt
    assert b2["groundwater"][0] == {"depth": 3.0, "nhn": 78.0, "kind": "angetroffen", "evidence": "Tabelle S. 10"}
    assert any("nicht im Profil" in i for i in b2["issues"]) and any("kein Grundwasser" in i for i in b2["issues"])
