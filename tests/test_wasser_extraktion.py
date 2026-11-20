"""Issue #26: Art und Datum je Wasserstand aus dem Text am Symbol / im Schichtenverzeichnis, Staende im Berichtstext
(Bemessungswasserstand, HGW, MHGW). Ohne Stichwort bleibt die Art unbestimmt (nie geraten)."""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "extractor"))
import prototyp_v4 as P  # noqa: E402


@pytest.mark.parametrize("text, kind, datum", [
    ("GW 3.62m (14.04.2020)", "unbestimmt", "2020-04-14"),                 # Hausham: nur Datum am Symbol
    ("Ruhewasser 3.62m u. AP 14.04.2020", "Ruhewasser", "2020-04-14"),     # Hausham: Schichtenverzeichnis
    ("Feinsand/hellgrau/Wasseranschnitt3.8", "angetroffen", None),         # Berlin: Beschreibung
    ("3,50 02.99 Ruhewasserstand", "Ruhewasser", None),                    # '02.99' ist kein Datum
    ("Grundwasser nach Bohrende 2,10 m 07.03.23", "Bohrende", "2023-03-07"),
    ("Schichtenwasser angetroffen", "Schichtenwasser", None),
    ("Kote 741.00m", "unbestimmt", None),
])
def test_gw_info(text, kind, datum):
    i = P.gw_info(text)
    assert i["kind"] == kind and i.get("observed_on") == datum
    assert ("evidence" in i) == (kind != "unbestimmt" or datum is not None)    # Beleg nur, wenn etwas gelesen wurde


def test_wasserstaende_im_berichtstext(tmp_path):
    doc = pymupdf.open()
    s = doc.new_page()
    s.insert_text((50, 80), "Es wird ein bauzeitlicher Bemessungswasserstand in Höhe von +32,80 m NHN empfohlen.")
    s.insert_text((50, 110), "Der zu erwartende hoechste Grundwasserstand zeHGW = +33,50 m NHN.")
    s.insert_text((50, 140), "Es wird ein MHGW von 75,0 m ü. NHN abgeschaetzt.")
    s.insert_text((50, 170), "Der Bemessungswasserstand liegt auf Gelaendeoberkante.")              # ohne Zahl: nichts
    s = doc.new_page()
    s.insert_text((50, 80), "Wiederholt: Bemessungswasserstand +32,80 m NHN.")                     # doppelt: einmal
    w = P.wasserstaende_text(doc)
    assert [(x["kind"], x["nhn"], x["page"]) for x in w] == \
        [("Bemessungswasserstand", 32.8, 0), ("zeHGW", 33.5, 0), ("MHGW", 75.0, 0)]
    assert "32,80" in w[0]["evidence"]


def test_text_am_symbol_nur_in_der_zeile():
    R = pymupdf.Rect
    zeilen = [(R(200, 318, 260, 326), "GW 3.62m"), (R(262, 318, 320, 326), "(14.04.2020)"),
              (R(200, 340, 300, 348), "Ruhewasser 5.00m"),                 # tiefer: andere Zeile
              (R(500, 318, 560, 326), "Ruhewasser")]                       # weit rechts: andere Spalte
    t = P._gw_text_am(zeilen, 215, 322)
    assert t == "GW 3.62m (14.04.2020)"
    assert P.gw_info(t)["kind"] == "unbestimmt"
