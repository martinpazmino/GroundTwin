"""Bodenkennwerte aus dem Gutachten je Einheit (Issue #18): Vorschlag nach Name/Bodenart, gleich gute Zeilen ohne
Vorschlag, IFC-Pset mit _min/_max (DAUB-Namensregel), gueltiges IFC."""
from __future__ import annotations

import ifcopenshell
import ifcopenshell.util.element as ue
import ifcopenshell.validate
import pytest
from baugrundmodell import bodenkennwerte as bk
from baugrundmodell import synthetisch as syn
from baugrundmodell.modell import bauen, einheit_schichten, ifc_schreiben


def _zeile(bez, gruppen=(), **werte):
    return {"bezeichnung": bez, "name": "", "bodengruppen": list(gruppen), "seite": 14, "form": "Tabelle",
            "hinweise": [], "werte": {k: {"text": f"{a} - {b}", "min": a, "max": b} for k, (a, b) in werte.items()}}


def _einheiten(m):
    return [{"name": e.name, "bodenarten": sorted(e.klassen), "schichten": einheit_schichten(m, j)}
            for j, e in enumerate(m.einheiten)]


def test_vorschlag_nach_name_und_gleichstand():
    zeilen = [{**_zeile("Schicht 3 – Pleistozäne Kiese (dichte Lagerung)", wichte=(21, 21)), "ref": "a#0"},
              {**_zeile("Auffüllungen, locker", wichte=(19, 20)), "ref": "a#1"},
              {**_zeile("Sand, kiesig", wichte=(19, 19)), "ref": "a#2"},
              {**_zeile("Sand, schluffig", wichte=(18, 19)), "ref": "a#3"}]
    e = [{"name": "Kies", "bodenarten": ["Kies"], "schichten": []},
         {"name": "Auffuellung", "bodenarten": ["Auffuellung"], "schichten": []},
         {"name": "Sand", "bodenarten": ["Sand"], "schichten": []},
         {"name": "Fels (Tonstein)", "bodenarten": ["Fels (Tonstein)"], "schichten": []}]
    v = bk.vorschlag(e, zeilen)
    assert v["Kies"]["ref"] == "a#0" and v["Auffuellung"]["ref"] == "a#1"
    assert v["Sand"]["ref"] is None and v["Sand"]["kandidaten"] == ["a#2", "a#3"]       # zwei gleich gute: keiner
    assert v["Fels (Tonstein)"]["ref"] is None and "keine Zeile" in v["Fels (Tonstein)"]["grund"]


def test_pset_min_max_und_text():
    z = _zeile("Auelehm (UL, TL)", wichte=(14, 20), steifemodul=(1.0, 10.0))
    z["werte"]["kohaesion"] = {"text": "-"}
    z["werte"]["steifemodul_x"] = {"text": "?"}                                           # unbekannt: faellt weg
    z["werte"]["reibungswinkel"] = {"text": "18√t"}
    ps = bk.pset({**z, "dokument": "g.pdf"})
    assert (ps["Wichte_min"], ps["Wichte_max"], ps["Steifemodul_max"]) == (14.0, 20.0, 10.0)
    assert ps["Reibungswinkel_Text"] == "18√t" and "Kohaesion_Text" not in ps and ps["Quelle"] == "g.pdf, Seite 15"
    assert not any(k.endswith("_char") for k in ps)                                     # setzt der Gutachter


def test_ifc_traegt_kennwerte_an_der_einheit(tmp_path):
    d = syn.dokument(syn.FAELLE["demo"]())
    m = bauen([d])
    namen = [e.name for e in m.einheiten]
    d["kennwerte"] = [_zeile(f"Schicht {i + 1} – {n}", wichte=(18 + i, 19 + i), reibungswinkel=(30, 32.5))
                      for i, n in enumerate(namen)]
    refs = {e["ref"] for e in bk.eintraege([d])}
    zu = bk.pruefen({namen[0]: f"{d['document']['file']}#0", namen[1]: "fremd#9"}, refs)
    assert zu == {namen[0]: f"{d['document']['file']}#0"}                                   # unbekannter Verweis faellt weg
    v = bk.vorschlag(_einheiten(m), bk.eintraege([d]))
    assert all(v[n]["ref"] == f"{d['document']['file']}#{i}" for i, n in enumerate(namen))
    pfad = tmp_path / "m.ifc"
    ifc_schreiben(m, pfad, [d], bodenkennwerte=zu)
    f = ifcopenshell.open(str(pfad))
    lg = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, lg)
    assert not lg.statements, lg.statements[:3]
    gm = f.by_type("IfcGeomodel")[0]
    strata = {x.Name: ue.get_psets(x) for r in gm.IsDecomposedBy for x in r.RelatedObjects}
    ps = strata[namen[0]][bk.PSET]
    assert (ps["Wichte_min"], ps["Wichte_max"], ps["Reibungswinkel_max"]) == (18.0, 19.0, pytest.approx(32.5))
    assert bk.PSET not in strata[namen[1]]


def _bohrung(code, gok, ende, abschnitte, hoehe="m NHN"):
    return {"code": code, "gok": gok, "hoehe": hoehe, "endteufe_nhn": ende,
            "einheiten": [{"einheit": e, "ok_modell": ok, "uk_modell": uk} for e, ok, uk in abschnitte]}


def test_vorschlag_nach_hoehenbereich():
    """Zeilen mit Hoehenbereich (Berlin: 'GOK bis +32,0'): die Einheit geht zur Zeile, in der ihre Maechtigkeit
    ueberwiegend liegt; knapp zwischen zwei Zeilen = kein Vorschlag; relative Hoehen zaehlen nicht."""
    zeilen = [{**_zeile("1 GOK bis +32,0"), "hoehe_oben": None, "hoehe_unten": 32.0, "ref": "b#0"},
              {**_zeile("2 +32,0 bis +30,0"), "hoehe_oben": 32.0, "hoehe_unten": 30.0, "ref": "b#1"},
              {**_zeile("3 +30,0 bis +21,0"), "hoehe_oben": 30.0, "hoehe_unten": 21.0, "ref": "b#2"}]
    bohr = [_bohrung("B1", 36.0, 20.0, [("Oben", 36.0, 32.2), ("Mitte", 32.2, 30.1), ("Unten", 30.1, 25.0),
                                        ("Knapp", 25.0, 23.0), ("Tief", 23.0, 10.0)]),
            _bohrung("B2", 36.0, 20.0, [("Knapp", 32.0, 30.0)]),
            _bohrung("B3", 0.0, -9.0, [("Rel", 0.0, -9.0)], hoehe="relativ")]
    e = [{"name": n, "bodenarten": [], "schichten": []} for n in ("Oben", "Mitte", "Unten", "Knapp", "Tief", "Rel")]
    v = bk.vorschlag(e, zeilen, bohr)
    assert (v["Oben"]["ref"], v["Mitte"]["ref"], v["Unten"]["ref"]) == ("b#0", "b#1", "b#2")
    assert "m NHN" in v["Mitte"]["grund"]
    assert v["Knapp"]["ref"] is None and "zwei Höhenbereichen" in v["Knapp"]["grund"]   # 2 m in Zeile 3, 2 m in Zeile 2
    assert v["Tief"]["ref"] == "b#2"                                     # bis zur Endteufe (20): 3 m in Zeile 3
    assert v["Rel"]["ref"] is None                                       # relative Hoehe: kein Hoehenvergleich
