"""Wissenskatalog v0 und Planer (Issue #34, A2, docs/29 §3): Eintraege gueltig und belegt, Verweise auf den
bestehenden Code aufloesbar, Planer auf synthetischen Projekten (nur Bohrprofile; + Labor; + CPT)."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in ("services/wissen", "services/modeler", "services/analyse"):
    sys.path.insert(0, str(ROOT / p))

import wissen  # noqa: E402

BOHRPROFILE = {"bohrung.schichten", "bohrung.lage", "bohrung.gok", "boden.beschreibung"}
LABOR = {"labor.messwerte", "labor.wassergehalt", "labor.fliessgrenze", "labor.ausrollgrenze", "labor.korngroesse",
         "labor.kf"}


def test_katalog_ist_in_ordnung_und_belegt():
    assert wissen.pruefen() == []
    k = wissen.katalog()
    assert len(k) >= 14
    assert all(e["source"]["citation"].strip() for e in k.values())
    # verified nur, wo die Quelle gelesen wurde (docs/30 §3: DAUB SLS/EPB gegen die Seite geprueft)
    assert k["daub.tbm_vorauswahl_boden"]["source"]["verified"] is True
    assert k["labor.konsistenzzahl"]["source"]["verified"] is False
    benutzt = {g for e in k.values() for g in e["inputs"].get("required", []) + e["inputs"].get("optional", [])
               + e["outputs"]}
    assert set(wissen.groessen()) - benutzt == set() or set(wissen.groessen()) - benutzt <= {
        "sondierung.dph_n10", "sondierung.cpt_qc"}                        # Sondierungen: noch kein Eintrag (A4)


def test_eintraege_gueltig_nach_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "services/wissen/schemas/katalog_eintrag.schema.json").read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    for e in wissen.katalog().values():
        v.validate(e)


@pytest.mark.parametrize("eintrag", [e for e in wissen.katalog().values() if e.get("implementierung")],
                         ids=lambda e: e["id"])
def test_verweise_auf_den_bestehenden_code_loesen_sich_auf(eintrag):
    modul, funktion = eintrag["implementierung"].split(":")
    assert callable(getattr(importlib.import_module(modul), funktion))
    if eintrag.get("daten_datei"):
        assert (ROOT / eintrag["daten_datei"]).exists()


def test_daub_tabelle_vollstaendig():
    t = wissen.katalog()["daub.tbm_vorauswahl_boden"]["daten"]["tabellen"]
    assert len(t) == 7
    for name, z in t.items():
        assert len(z["SLS"]) == len(z["EPB"]) == len(z["klassen"]), name
        if "grenzen" in z:
            assert len(z["grenzen"]) == len(z["klassen"]) - 1, name
        assert z["groesse"] in wissen.groessen(), name


def status(plan, k):
    return plan["eintraege"][k]["status"]


def test_planer_nur_bohrprofile():
    p = wissen.planen(BOHRPROFILE)
    assert status(p, "modell.schichtenmodell") == "moeglich" and status(p, "analyse.unsicherheit") == "moeglich"
    assert status(p, "hb.vorschlag") == "moeglich"
    assert status(p, "labor.konsistenzzahl") == "blockiert"
    assert p["eintraege"]["labor.konsistenzzahl"]["fehlt"] == ["labor.ausrollgrenze", "labor.fliessgrenze",
                                                               "labor.wassergehalt"] or set(
        p["eintraege"]["labor.konsistenzzahl"]["fehlt"]) == {"labor.wassergehalt", "labor.fliessgrenze", "labor.ausrollgrenze"}
    d = p["eintraege"]["daub.tbm_vorauswahl_boden"]
    assert d["status"] == "hinweisend" and d["abdeckung"] == "2/8"           # nur Konsistenz/Lagerung aus der Ansprache
    f = p["fehlende_grundgroessen"]
    assert "labor.konsistenzzahl" in f["labor.wassergehalt"]["benoetigt_fuer"]
    assert f["labor.wassergehalt"]["schaltet_frei"] == []                  # allein reicht es nicht (w_L, w_P fehlen)
    assert f["labor.korngroesse"]["schaltet_frei"] == ["labor.feinkornanteil"]
    assert f["hb.zuordnung"]["eingabe"] is True and f["hb.zuordnung"]["schaltet_frei"] == ["hb.kennwerte_ansprache"]
    assert "17892-4" in f["labor.korngroesse"]["liefert"]


def test_planer_mit_labor():
    p = wissen.planen(BOHRPROFILE | LABOR)
    for k in ("labor.konsistenzzahl", "labor.feinkornanteil", "labor.durchlaessigkeit", "labor.statistik_einheit"):
        assert status(p, k) == "moeglich", k
    assert p["eintraege"]["daub.tbm_vorauswahl_boden"]["abdeckung"] == "5/8"
    assert set(p["fehlende_grundgroessen"]) >= {"tunnel.stuetzdruck", "boden.abrasivitaet_aequ"}


def test_planer_mit_cpt_zeigt_ungenutzte_groesse():
    p = wissen.planen(BOHRPROFILE | {"sondierung.cpt_qc"})
    assert p["ungenutzt"] == ["sondierung.cpt_qc"]                          # Korrelationen kommen mit A4 (#29)


def test_planer_ohne_lage_und_gok_nimmt_an_und_ohne_schichten_blockiert():
    p = wissen.planen({"bohrung.schichten", "boden.beschreibung"})
    m = p["eintraege"]["modell.schichtenmodell"]
    assert m["status"] == "hinweisend" and set(m["angenommen"]) == {"bohrung.lage", "bohrung.gok"}
    leer = wissen.planen(set())
    assert status(leer, "modell.schichtenmodell") == "blockiert"
    assert {"modell.schichtenmodell", "analyse.kreuzprobe"} <= set(leer["fehlende_grundgroessen"]["bohrung.schichten"]["schaltet_frei"])
    assert wissen.planen({"gibt.es_nicht"})["unbekannt"] == ["gibt.es_nicht"]


def test_pruefen_findet_zyklus_unbekannte_groesse_und_doppelten_erzeuger():
    g = {"a.x": {}, "a.y": {}, "h.mensch": {"eingabe": True}}
    basis = {"version": "1.0.0", "kind": "rule", "authority": "expert", "source": {"citation": "Test", "verified": False},
             "validity": {}, "uncertainty": {"model": "none"}, "when_missing": {}, "tests": ["t"]}
    k = {"e.eins": {**basis, "id": "e.eins", "inputs": {"required": ["a.x"]}, "outputs": ["a.y"]},
         "e.zwei": {**basis, "id": "e.zwei", "inputs": {"required": ["a.y"]}, "outputs": ["a.x"]},
         "e.drei": {**basis, "id": "e.drei", "inputs": {"required": ["a.z"]}, "outputs": ["a.y", "h.mensch"]}}
    f = wissen.pruefen(k, g)
    assert any("Zyklus" in x for x in f) and any("a.z nicht in groessen" in x for x in f)
    assert any("schon von" in x for x in f) and any("nur ein Mensch" in x for x in f)


def test_protokoll_passt_ins_manifest():
    jsonschema = pytest.importorskip("jsonschema")
    w = wissen.protokoll("labor.konsistenzzahl", ["E1/LAB_WASSERGEHALT/Labor", "E1/LAB_FLIESSGRENZE/Labor"],
                         "E1/IC", "boden.konsistenzzahl", ["Q1"], gueltig=False)
    assert w["kind"] == "derived" and w["herkunft"]["katalog"] == {"id": "labor.konsistenzzahl", "version": "1.0.0"}
    schema = json.loads((ROOT / "services/wissen/schemas/manifest.schema.json").read_text(encoding="utf-8"))
    m = {"format": "groundtwin-manifest/1", "projekt": "T", "erzeugt": "2026-11-24T00:00:00Z", "quellen": [], "werte": [w]}
    jsonschema.Draft202012Validator(schema).validate(m)


@pytest.mark.parametrize("name,erwartet,nicht", [
    ("talheim", {"bohrung.schichten", "boden.beschreibung", "labor.messwerte", "labor.wassergehalt"}, set()),
    ("demo_synthetisch", {"bohrung.schichten", "sondierung.dph_n10"}, {"labor.messwerte"}),
    ("berlin_v67b", {"bohrung.schichten", "bohrung.gok", "grundwasser.staende"}, {"labor.messwerte"}),
])
def test_verfuegbar_aus_den_beispielen(name, erwartet, nicht):
    d = json.loads((ROOT / f"data/beispiele/{name}.json").read_text(encoding="utf-8"))
    da = wissen.verfuegbar_aus_dokumenten(d if isinstance(d, list) else [d])
    assert erwartet <= da and not (nicht & da)
