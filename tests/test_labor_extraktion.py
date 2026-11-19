"""Issue #18: Laborblaetter der Anlagen - Ergebnis 'Name = Zahl', 'Name | Einheit | Zahl', Tabelle mit mehreren
Proben (letzte Spalte), T/U/S/G, Mischprobe, Achsen sind keine Ergebnisse, chemische Analysen bleiben aussen vor."""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "extractor"))
import labor as L  # noqa: E402


def _blatt(doc, zeilen):
    s = doc.new_page()
    for i, z in enumerate(zeilen):
        s.insert_text((60, 50 + 13 * i), z, fontsize=8)


def test_blaetter(tmp_path):
    doc = pymupdf.open()
    _blatt(doc, ["Fliess- und Ausrollgrenze DIN EN ISO 17892-12", "Wassergehalt w [%]", "24.0", "26.0",   # Achse
                 "Wassergehalt w =", "16.5 %", "Fließgrenze wL =", "29.9 %", "Ausrollgrenze wP =", "13.6 %",
                 "Plastizitätszahl IP =", "16.3 %", "Konsistenzzahl IC =", "0.70",
                 "Entnahmestelle:  BS 1 + 2", "Tiefe:  2,4 - 3,7", "Projektnr.: P 41.7186"])
    _blatt(doc, ["Körnungslinie DIN EN ISO 17892-4", "Entnahmestelle:", "Tiefe:", "Bodenart:", "T/U/S/G [%]:",
                 "BS 5", "2,5 - 3,5", "T, u", "18.7/70.1/11.2/ -"])
    _blatt(doc, ["Wassergehalt nach DIN EN ISO 17892-1", "Entnahmestelle:", "Tiefe:", "Feuchte Probe [g]:",
                 "Wassergehalt [%]", "BS 3", "2,4 - 3,5", "599.63", "547.18", "12.07",
                 "BS 4", "4,0 - 5,0", "429.72", "387.09", "15.36"])
    _blatt(doc, ["C B R - V E R S U C H", "Entnahmestelle", "-", "BK2 (5,0-6,0m)", "Trockendichte", "g/cm³", "1,775",
                 "Wassergehalt vor dem Versuch", "%", "13,1", "CBR - WERT", "%", "23"])
    _blatt(doc, ["PRÜFBERICHT", "Analysennummer 201152", "Entnahmestelle BS 9", "Tiefe 1,0 - 2,0", "Wassergehalt =", "9 %"])
    doc.save(tmp_path / "l.pdf")
    je = {(tuple(p["bohrungen"]), p["von"]): p for p in L.lesen(tmp_path / "l.pdf")}
    a = je[(("BS 1", "BS 2"), 2.4)]
    assert a["werte"] == {"wassergehalt": 16.5, "fliessgrenze": 29.9, "ausrollgrenze": 13.6,
                          "plastizitaetszahl": 16.3, "konsistenzzahl": 0.7}               # Achse 24.0 kein Ergebnis
    assert any("Mischprobe" in h for h in a["hinweise"]) and a["bis"] == 3.7
    assert je[(("BS 5",), 2.5)]["werte"] == {"ton": 18.7, "schluff": 70.1, "sand": 11.2}  # '-' = keine Kies-Angabe
    assert je[(("BS 3",), 2.4)]["werte"] == {"wassergehalt": 12.07}                      # letzte Spalte
    assert je[(("BS 4",), 4.0)]["werte"] == {"wassergehalt": 15.36}
    assert je[(("BK 2",), 5.0)]["werte"] == {"trockendichte": 1.775, "wassergehalt": 13.1, "cbr": 23.0}
    assert (("BS 9",), 1.0) not in je                                                    # Chemie: nicht gelesen


def test_unplausibel_markiert():
    assert L._pruefen({"konsistenzzahl": 4.0}) == ["konsistenzzahl: 4.0 außerhalb -1–2.5 -"]
    assert L._pruefen({"fliessgrenze": 30.0, "ausrollgrenze": 15.0, "plastizitaetszahl": 10.0}) == ["IP ≠ wL − wP"]
