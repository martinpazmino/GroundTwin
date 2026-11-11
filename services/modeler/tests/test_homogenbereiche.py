"""Homogenbereiche nach VOB/C (docs/28): Matrix der Kennwerte je ATV, Zuordnung pruefen, Psets je Einheit und
Bodenschicht, Modell nur aus Homogenbereichen (gleiche Koerper, gueltiges IFC in Metern)."""
from __future__ import annotations

import ifcopenshell
import ifcopenshell.util.element as ue
import ifcopenshell.util.unit
import ifcopenshell.validate
import pytest
from baugrundmodell import homogenbereiche as hb
from baugrundmodell import synthetisch as syn
from baugrundmodell.modell import bauen, ifc_schreiben


def test_matrix_wie_abbildung_8():
    codes = [a["code"] for a in hb.atv_liste()]
    assert len(codes) == 11 and set(hb.daten()["matrix"]) == set(codes)
    # DIN 18300 Erdarbeiten: die 13 Kennwerte der ATV
    assert [k["nr"] for k in hb.kennwerte("DIN 18300")] == ["1", "2", "3a", "3b", "3c", "5", "7", "9", "10b", "11b",
                                                            "13", "16", "19"]
    assert all(k["art"] == "erforderlich" for k in hb.kennwerte("DIN 18300"))
    schild = {k["nr"] for k in hb.kennwerte("DIN 18312") if k["art"].startswith("ergänzend")}
    assert schild == {"4", "6", "8", "16"}                    # dunkelgrau: Vortrieb mit Schildmaschinen
    assert "DIN 18915" in dict((k["nr"], k["art"]) for k in hb.kennwerte("DIN 18320"))["19"]
    assert "prüfen" in dict((k["nr"], k["art"]) for k in hb.kennwerte("DIN 18313"))["5"]
    assert len(hb.kennwerte("DIN 18324")) == 19 and "Abbildung 8" in hb.daten()["quelle"]
    assert hb.pset_name("DIN 18300 GK 1") == "CPset_Homogenbereich_DIN18300GK1"
    with pytest.raises(ValueError, match="unbekannte ATV"):
        hb.kennwerte("DIN 9999")


def test_pruefen_und_bereiche():
    assert hb.pruefen(None) is None and hb.pruefen({"DIN 18300": {"Sand": "  "}}) is None
    assert hb.pruefen({"DIN 18300": {"Sand": " B  2 "}}) == {"DIN 18300": {"Sand": "B 2"}}
    with pytest.raises(ValueError, match="unbekannte ATV"):
        hb.pruefen({"DIN 1": {"Sand": "B1"}})
    with pytest.raises(ValueError, match="40 Zeichen"):
        hb.pruefen({"DIN 18300": {"Sand": "x" * 41}})
    g, h = hb.bereiche({"A": "B1", "C": "B1", "Weg": "B9"}, ["A", "B", "C"])
    assert [(x["bereich"], x["einheiten"]) for x in g] == [("B1", ["A", "C"]), (None, ["B"])]
    assert any("Weg" in x for x in h) and any("ohne Homogenbereich: B" in x for x in h)
    assert hb.vorschlag(["A", "B"]) == {"A": "B1", "B": "B2"}


def _modell():
    docs = [syn.dokument(syn.FAELLE["demo"]())]
    m = bauen(docs)
    n = [e.name for e in m.einheiten]
    zu = {"DIN 18300": {n[0]: "B1", n[1]: "B2", n[2]: "B2", n[3]: "B3"}, "DIN 18301": {x: "B1" for x in n}}
    return docs, m, n, zu


def _gueltig(f):
    lg = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, lg)
    assert not lg.statements, lg.statements[:3]
    assert ifcopenshell.util.unit.get_project_unit(f, "LENGTHUNIT").Name == "METRE"


def _strata(f):
    gm = f.by_type("IfcGeomodel")[0]
    return [x for r in gm.IsDecomposedBy for x in r.RelatedObjects]


def test_psets_je_einheit_und_bodenschicht(tmp_path):
    docs, m, n, zu = _modell()
    ifc_schreiben(m, tmp_path / "e.ifc", docs, homogenbereiche=zu)
    f = ifcopenshell.open(str(tmp_path / "e.ifc"))
    _gueltig(f)
    je = {s.Name: ue.get_psets(s) for s in _strata(f)}
    assert len(je) == len(n)
    assert je[n[1]]["CPset_Homogenbereich_DIN18300"]["Homogenbereich"] == "B2"
    assert je[n[1]]["CPset_Homogenbereich_DIN18300"]["Einheiten_im_Bereich"] == f"{n[1]}, {n[2]}"
    assert "13 Lagerungsdichte" in je[n[1]]["CPset_Homogenbereich_DIN18300"]["Kennwerte_erforderlich"]
    assert je[n[5]]["CPset_Homogenbereich_DIN18300"]["Homogenbereich"] == "nicht zugeordnet"
    assert je[n[5]]["CPset_Homogenbereich_DIN18301"]["Homogenbereich"] == "B1"
    # Bodenschichten der Bohrsaeulen: nach der Hoehe ihrer Einheit; eine Schicht in zwei Einheiten nennt beide
    saeulen = {s.Name: ue.get_psets(s).get("CPset_Homogenbereich_DIN18300", {}) for s in f.by_type("IfcGeotechnicalStratum")
               if s.Description == "Bohrsaeule"}
    assert saeulen["B 1 0.00-0.80 Auffuellung"]["Homogenbereich"] == "B1"
    geteilt = saeulen["B 1 4.00-6.00 Sand"]
    assert geteilt["Homogenbereich"] == "B2 / B3" and "2 Einheiten" in geteilt["Hinweis"]


def test_modell_nur_aus_homogenbereichen(tmp_path):
    docs, m, n, zu = _modell()
    r = ifc_schreiben(m, tmp_path / "h.ifc", docs, homogenbereiche=zu, nur_homogenbereiche="DIN 18300")
    f = ifcopenshell.open(str(tmp_path / "h.ifc"))
    _gueltig(f)
    strata = {s.Name: s for s in _strata(f)}
    # B1, B2 (zwei Einheiten), B3 und die Einheiten ohne Bereich einzeln, markiert
    assert r["einheiten"] == len(strata) == 3 + (len(n) - 4)
    assert {"B1", "B2", "B3"} <= set(strata)
    assert all(f"{x} (ohne Homogenbereich)" in strata for x in n[4:])
    b2 = strata["B2"]
    assert len(b2.Representation.Representations[0].Items) == 2 and all(i.Closed for i in b2.Representation.Representations[0].Items)
    ps = ue.get_psets(b2)
    vol = sum(k["volumen_m3"] for k in m.koerper if k["name"] in (n[1], n[2]))
    assert ps["CPset_Homogenbereich_DIN18300"]["Volumen_m3"] == pytest.approx(vol, abs=0.2)
    assert ps["CPset_Homogenbereich_DIN18300"]["Koerper"] == 2 and "CPset_Modelleinheiten" in ps
    assert ps["CPset_Homogenbereich_DIN18301"]["Homogenbereich"] == "B1"     # andere ATV: alle Einheiten dort B1
    gm = ue.get_psets(f.by_type("IfcGeomodel")[0])["CPset_Baugrundmodell"]
    assert gm["Modellart"] == "Homogenbereiche DIN 18300" and "ohne Homogenbereich" in gm["Hinweise"]
    with pytest.raises(ValueError, match="keine Homogenbereiche"):
        ifc_schreiben(m, tmp_path / "x.ifc", docs, homogenbereiche=zu, nur_homogenbereiche="DIN 18304")


def test_vorschlag_je_anwendungsfall():
    """Der Vorschlag haengt von den Kennwerten der ATV ab: wenige Kennwerte -> nur das Verhalten; sonst Bodengruppe bzw.
    Hauptbodenart getrennt; Mineralogie/Abrasivitaet -> dazu Steine/Bloecke. Gleiche Einheiten fallen zusammen."""
    from baugrundmodell.modell import bericht
    docs, m, n, _ = _modell()
    b = bericht(m)["einheiten"]
    gk1 = hb.vorschlag_fuer("DIN 18300 GK 1", b)
    assert gk1["stufe"] == "grob" and [g["einheiten"] for g in gk1["bereiche"]] == [
        ["Auffuellung"], ["Sand 1", "Kies", "Sand 2"], ["Torf"], ["Geschiebemergel", "Ton"]]
    erd = hb.vorschlag_fuer("DIN 18300", b)
    assert erd["stufe"] == "standard" and ["Sand 1", "Sand 2"] in [g["einheiten"] for g in erd["bereiche"]]
    assert ["Kies"] in [g["einheiten"] for g in erd["bereiche"]]
    assert all(g["grund"] for g in erd["bereiche"]) and erd["zuordnung"]["Sand 2"] == erd["zuordnung"]["Sand 1"]
    assert hb.vorschlag_fuer("DIN 18324", b)["stufe"] == "fein"
    assert [g["name"] for g in gk1["bereiche"]] == ["B1", "B2", "B3", "B4"]          # von oben nummeriert
    # Bodengruppe aus den Beschreibungen trennt, was nach der Bodenart gleich waere; Unbekanntes bleibt einzeln
    e = [{"name": "S1", "bodenarten": ["Sand"], "schichten": [{"beschreibung": "Mittelsand, SE", "bodenart": "Sand"}]},
         {"name": "S2", "bodenarten": ["Sand"], "schichten": [{"beschreibung": "Sand, schluffig, SU*", "bodenart": "Sand"}]},
         {"name": "S3", "bodenarten": ["Sand"], "schichten": [{"beschreibung": "Feinsand, SE", "bodenart": "Sand"}]},
         {"name": "X", "bodenarten": ["unklassifiziert"], "schichten": []},
         {"name": "Y", "bodenarten": ["unklassifiziert"], "schichten": []}]
    v = hb.vorschlag_fuer("DIN 18300", e)
    assert v["zuordnung"]["S1"] == v["zuordnung"]["S3"] != v["zuordnung"]["S2"]
    assert v["zuordnung"]["X"] != v["zuordnung"]["Y"]
    assert hb.vorschlag_fuer("DIN 18300 GK 1", e)["zuordnung"]["S2"] == v["zuordnung"]["S1"]
