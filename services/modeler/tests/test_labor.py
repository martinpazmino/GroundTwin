"""Laborwerte je Schicht und Einheit (Issue #18): Probe an der Schicht mit der groessten Ueberdeckung, Mischprobe an
jeder Bohrung, Statistik n/min/max/Mittel, Kennwerte der ATV vor der Ansprache, IFC CPset_Laborwerte."""
from __future__ import annotations

import ifcopenshell
import ifcopenshell.util.element as ue
import ifcopenshell.validate
import pytest
from baugrundmodell import homogenbereiche as hb
from baugrundmodell import labor
from baugrundmodell import synthetisch as syn
from baugrundmodell.modell import bauen, einheit_schichten, ifc_schreiben


def test_code_und_zuordnung_an_schichten():
    assert labor.code("BS 05") == labor.code("bs5") == "BS5" and labor.code("BK 2a") == "BK2a"
    s = [{"von": 0.0, "bis": 1.0}, {"von": 1.0, "bis": 4.0}, {"von": 4.0, "bis": 6.0}]
    proben = [{"bohrungen": ["BS 1", "BS 2"], "von": 2.4, "bis": 3.7, "werte": {"wassergehalt": 16.5}, "ref": "a#0"},
              {"bohrungen": ["BS 1"], "von": 3.3, "bis": 4.5, "werte": {"wassergehalt": 22.8}, "ref": "a#1"},
              {"bohrungen": ["BS 9"], "von": 1.0, "bis": 2.0, "werte": {"wassergehalt": 9.0}, "ref": "a#2"}]
    labor.an_schichten("BS1", s, proben)
    assert [p["ref"] for p in s[1]["labor"]] == ["a#0", "a#1"] and "labor" not in s[2]   # 3,3-4,5: mehr in Schicht 2
    assert any("Schichtgrenze" in h for h in s[1]["labor"][1]["hinweise"])
    st = labor.statistik(s)["wassergehalt"]
    assert (st["n"], st["min"], st["max"]) == (2, 16.5, 22.8) and st["mittel"] == pytest.approx(19.65)
    assert labor.text(labor.statistik(s), "wassergehalt") == "16,5–22,8 % (n = 2, Mittel 19,6)"


def test_modell_kennwerte_der_atv_und_ifc(tmp_path):
    d = syn.dokument(syn.FAELLE["demo"]())
    b = d["boreholes"][0]
    ly = b["layers"][1]
    mitte = (ly["top_depth"] + ly["bottom_depth"]) / 2
    d["labor"] = [{"bohrungen": [b["code"]], "von": mitte - 0.2, "bis": mitte + 0.2, "hinweise": [],
                   "werte": {"wassergehalt": 18.0, "plastizitaetszahl": 12.0, "konsistenzzahl": 0.8,
                             "ton": 10.0, "schluff": 30.0, "sand": 60.0, "gluehverlust": 2.5}}]
    m = bauen([d])
    j = next(j for j, _ in enumerate(m.einheiten) if any("labor" in s for s in einheit_schichten(m, j)))
    sch = einheit_schichten(m, j)
    kw = hb.kennwerte_aus_beschreibung(sch)
    assert kw["9"].startswith("Labor: 18,0 %") and kw["10b"].startswith("Labor: 12,0")
    assert kw["11b"].startswith("Labor: 0,80") and kw["16"].startswith("Labor: Glühverlust, 2,5")
    assert kw["2"] == "Labor: T/U/S/G im Mittel 10/30/60/– % (n = 1)"
    pfad = tmp_path / "m.ifc"
    ifc_schreiben(m, pfad, [d])
    f = ifcopenshell.open(str(pfad))
    lg = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, lg)
    assert not lg.statements, lg.statements[:3]
    gm = f.by_type("IfcGeomodel")[0]
    strata = {x.Name: ue.get_psets(x) for r in gm.IsDecomposedBy for x in r.RelatedObjects}
    ps = strata[m.einheiten[j].name][labor.PSET]
    assert (ps["Wassergehalt_min"], ps["Wassergehalt_n"], ps["Konsistenzzahl_mean"]) == (18.0, 1, 0.8)
    assert "keine charakteristischen" in ps["Art"]
    assert any(labor.PSET not in v for v in strata.values())             # nur, wo eine Probe liegt
