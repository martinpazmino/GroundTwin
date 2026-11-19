"""Art und Datum der Wasserstaende (Issue #26): Stichworte, Datum, Vorrang fuer die Grundwasserflaeche, IFC."""
from __future__ import annotations

import ifcopenshell
import ifcopenshell.util.element as ue
import ifcopenshell.validate
import pytest
from baugrundmodell import synthetisch as syn
from baugrundmodell import wasser
from baugrundmodell.modell import bauen, ifc_schreiben


@pytest.mark.parametrize("text, art", [
    ("Ruhewasser 3.62m u. AP 14.04.2020", "Ruhewasser"),
    ("Ruhewasserstand muGOK", "Ruhewasser"),
    ("Grundwasser angestiegen", "Ruhewasser"),
    ("Grundwasserstand nach Bohrende", "Bohrende"),
    ("Wasseranschnitt 3.8", "angetroffen"),
    ("Grundwasser angetroffen bei 2,40 m", "angetroffen"),
    ("Schichtenwasser angetroffen", "Schichtenwasser"),
    ("Stauwasser über dem Lehm", "Schichtenwasser"),
    ("GW 3.62m (14.04.2020)", None),
    ("", None),
])
def test_art_aus_text(text, art):
    assert wasser.art_aus_text(text) == art


@pytest.mark.parametrize("text, iso", [
    ("GW 3.62m (14.04.2020)08:58h", "2020-04-14"),
    ("Ruhewasserstand 07.03.23", "2023-03-07"),
    ("am 1.7.1998 gemessen", "1998-07-01"),
    ("Kote 741.00m", None),                      # keine Kote als Datum
    ("31.13.2020", None),                         # kein Monat 13
    ("Vom 01.07. bis 15.10.2020", "2020-10-15"),  # '01.07.' ohne Jahr ist kein Datum
])
def test_datum_aus_text(text, iso):
    assert wasser.datum_aus_text(text) == iso


def test_alte_werte_und_vorrang():
    assert wasser.art("gemessen") == "unbestimmt" and wasser.art(None) == "unbestimmt"
    assert wasser.art("nach_bohrende") == "Bohrende" and wasser.art("Ruhewasser") == "Ruhewasser"
    st = [{"depth": 2.0, "kind": "angetroffen"}, {"depth": 1.6, "kind": "Ruhewasser"},
          {"depth": 0.8, "kind": "Schichtenwasser"}]
    a, s = wasser.wahl(st)
    assert a == "Ruhewasser" and [g["depth"] for g in s] == [1.6]
    assert wasser.wahl([{"depth": 0.8, "kind": "Schichtenwasser"}]) == (None, [])   # Schichtenwasser nie
    assert wasser.wahl([{"depth": 3.0, "kind": "gemessen"}])[0] == "unbestimmt"


def test_ifc_traegt_art_und_datum(tmp_path):
    d = syn.dokument(syn.FAELLE["demo"]())
    b0, b1 = d["boreholes"][:2]
    b0["groundwater"] = [{"depth": 2.2, "kind": "angetroffen", "observed_on": "2020-04-14"},
                         {"depth": 1.5, "kind": "Ruhewasser", "observed_on": "2020-04-15"},
                         {"depth": 0.6, "kind": "Schichtenwasser"}]
    b1["groundwater"] = [{"depth": 3.0, "kind": "gemessen"}]          # aeltere Extraktion
    m = bauen([d])
    pfad = tmp_path / "m.ifc"
    ifc_schreiben(m, pfad, [d])
    f = ifcopenshell.open(str(pfad))
    lg = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, lg)
    assert not lg.statements, lg.statements[:3]
    je = {x.Name: ue.get_psets(x) for x in f.by_type("IfcBorehole")}
    p0 = je[b0["code"]]
    assert p0["Pset_BoreholeCommon"]["GroundwaterDepth"] == pytest.approx(1.5)      # Ruhewasser, nicht Schichtenwasser
    gw = p0["CPset_Grundwasser"]
    assert gw["Art_Modell"] == "Ruhewasser" and gw["Datum"] == "2020-04-15" and gw["Art_offen"] is False
    assert "0.60 m (Schichtenwasser)" in gw["Staende"] and "2.20 m (angetroffen (Anschnitt), 2020-04-14)" in gw["Staende"]
    p1 = je[b1["code"]]["CPset_Grundwasser"]
    assert p1["Art_Modell"] == "Art nicht angegeben" and p1["Art_offen"] is True
