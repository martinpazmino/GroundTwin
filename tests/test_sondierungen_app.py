"""Sondierungen im Projekt und in der App (Issue #27 Teil 2, docs/05 §6): Liste, Pruefen, Entfernen, GOK, Lage
(Eingabe und Punkt auf dem gesperrten Plan), Detail mit Werten. Ohne Netz: Beispiel demo_synthetisch (drei
synthetische Sondierungen aus den Stressfaellen) und Berlin (echte Extraktion, Scans ohne Werte)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from ui import projekt as pj  # noqa: E402
from ui import sondierung as sd  # noqa: E402

BEISPIELE = REPO / "data" / "beispiele"


def lade(name: str) -> list[dict]:
    return [json.loads((BEISPIELE / name).read_text(encoding="utf-8"))]


def test_liste_aus_der_extraktion():
    docs = lade("demo_synthetisch.json")
    p = pj.neues_projekt(docs, "t")
    z = sd.zeilen(docs, p)
    assert [r["code"] for r in z] == ["DPH 1", "DPH 2", "CPT 1"]
    dph = z[0]
    assert dph["id"] == "0:S0" and dph["art"] == "DPH" and dph["werte_n"] == 60 and dph["endtiefe"] == 6.0
    assert dph["gok"] == 38.6 and dph["gok_quelle"] == "PDF" and dph["endtiefe_aus"] == "Werte"
    assert dph["x"] is None and not dph["geprueft"] and not dph["entfernt"]
    assert z[1]["zensiert"] >= 1                                    # Werte ueber der Achse zaehlen
    assert pj.pruefstand(docs, p)["sondierungen"] == [0, 3]


def test_scans_ohne_werte_sagen_es():
    docs = lade("berlin_v67b.json")
    z = sd.zeilen(docs, pj.neues_projekt(docs, "t"))
    assert len(z) == 6 and all(r["werte_n"] == 0 for r in z)
    assert all(r["endtiefe_aus"] == "Achse (≈)" for r in z)          # geschaetzt, nicht gelesen
    assert all(any("ohne Werte" in h for h in r["hinweise"]) for r in z)


def test_pruefen_entfernen_gok_und_lage():
    docs = lade("demo_synthetisch.json")
    p = pj.neues_projekt(docs, "t")
    pj.aendern(docs, p, {"op": "sondierung", "sondierung": "0:S0", "feld": "geprueft", "wert": True})
    pj.aendern(docs, p, {"op": "sondierung", "sondierung": "0:S2", "feld": "modell", "wert": False})
    pj.aendern(docs, p, {"op": "sondierung", "sondierung": "0:S1", "feld": "gok", "wert": "40,25"})
    pj.aendern(docs, p, {"op": "sondierung", "sondierung": "0:S1", "feld": "x", "wert": 565030})
    pj.aendern(docs, p, {"op": "sondierung", "sondierung": "0:S1", "feld": "y", "wert": 5933020})
    z = {r["code"]: r for r in sd.zeilen(docs, p)}
    assert z["DPH 1"]["geprueft"] and z["CPT 1"]["entfernt"]
    assert z["DPH 2"]["gok"] == 40.25 and z["DPH 2"]["gok_quelle"] == "Eingabe"
    assert (z["DPH 2"]["x"], z["DPH 2"]["y"], z["DPH 2"]["lage_aus"]) == (565030, 5933020, "manuell")
    assert pj.pruefstand(docs, p)["sondierungen"] == [1, 2]
    assert [v["code"] for v in sd.viewer(docs, p)] == ["DPH 1", "DPH 2"]
    q = pj.laden(pj.speichern(p))                                    # bleibt beim Speichern
    assert sd.zeilen(docs, q) == sd.zeilen(docs, p)
    pj.aendern(docs, p, {"op": "sondierung", "sondierung": "0:S1", "feld": "gok", "wert": None})
    assert sd.zeilen(docs, p)[1]["gok_quelle"] == "PDF"              # Eingabe zurueck, wieder aus dem PDF
    for falsch in ({"sondierung": "0:S9", "feld": "geprueft", "wert": True},
                   {"sondierung": "0:S0", "feld": "werte", "wert": []},
                   {"sondierung": "0:S0", "feld": "gok", "wert": "hoch"},
                   {"sondierung": "0:S0", "feld": "gok", "wert": 99999}):
        with pytest.raises(ValueError):
            pj.aendern(docs, p, {"op": "sondierung", **falsch})


def test_lage_vom_gesperrten_plan():
    docs = lade("demo_synthetisch.json")
    p = pj.neues_projekt(docs, "t")
    with pytest.raises(ValueError):                                 # ohne gesperrten Plan keine Punkte
        pj.aendern(docs, p, {"op": "punkt", "x": 1, "y": 2, "sondierung": "0:S0"})
    p.unterlage = {"art": "plan", "kalibrierung": {"bezug": {"u": 0, "v": 0, "x": 0, "y": 0}, "gesperrt": True,
                                                   "epsg": 25832}}
    pj.aendern(docs, p, {"op": "punkt", "x": 565010.5, "y": 5933012.25, "sondierung": "0:S0"})
    pj.aendern(docs, p, {"op": "punkt", "x": 565100.0, "y": 5933050.0})            # freier Punkt P1
    pj.aendern(docs, p, {"op": "punkt_zuordnen", "punkt": "P1", "sondierung": "0:S2"})
    z = {r["code"]: r for r in sd.zeilen(docs, p)}
    assert (z["DPH 1"]["x"], z["DPH 1"]["epsg"], z["DPH 1"]["lage_aus"]) == (565010.5, 25832, "Plan (kalibriert)")
    assert z["CPT 1"]["x"] == 565100.0 and p.punkte == []
    pj.aendern(docs, p, {"op": "punkt", "x": 565000, "y": 5933000})                # P2 bleibt Bohrungen zuordenbar
    bid = pj.bohrungen_liste(docs, p)[0]["id"]
    pj.aendern(docs, p, {"op": "punkt_zuordnen", "punkt": "P2", "bohrung": bid})
    assert pj.bohrungen_liste(docs, p)[0]["x"] == 565000


def test_detail_mit_werten_und_beleg():
    docs = lade("demo_synthetisch.json")
    p = pj.neues_projekt(docs, "t")
    d = sd.detail(docs, p, "0:S2")
    assert d["sondierung"]["art"] == "CPT" and len(d["werte"]) == 41 and d["beleg"]
    assert sd.detail(docs, p, "0:S0")["einheiten"] == {"N10": "Schläge/10 cm"}


fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path / "pipeline")
    with TestClient(app_erstellen(tmp_path)) as c:
        yield c


def test_ueber_die_app(client):
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    z = client.get(f"/api/projekt/{sig}").json()
    assert [s["code"] for s in z["sondierungen"]] == ["DPH 1", "DPH 2", "CPT 1"]
    assert z["pruefstand"]["sondierungen"] == [0, 3] and len(z["viewer"]["sondierungen"]) == 3
    r = client.post(f"/api/projekt/{sig}/aendern",
                    json={"ops": [{"op": "sondierung", "sondierung": "0:S0", "feld": "geprueft", "wert": True}]})
    assert r.status_code == 200
    d = client.get(f"/api/projekt/{sig}/sondierung/0:S0").json()
    assert d["sondierung"]["geprueft"] and len(d["werte"]) == 60
    assert client.get(f"/api/projekt/{sig}/sondierung/0:S7").status_code == 404
    r = client.post(f"/api/projekt/{sig}/aendern",
                    json={"ops": [{"op": "sondierung", "sondierung": "0:S0", "feld": "gok", "wert": "x"}]})
    assert r.status_code == 400


def test_ifc_mit_sondierungen():
    """Teil 3: je Sondierung mit Lage und GOK eine IfcBorehole 'Sondierung <Art>' mit Saeule an der richtigen Stelle,
    Herkunft, Pruefvermerk und der Kurve als IfcPropertyTableValue; ohne Lage bleibt sie draussen (mit Grund)."""
    ifcopenshell = pytest.importorskip("ifcopenshell")
    validate = pytest.importorskip("ifcopenshell.validate")
    import numpy as np

    from ui import pipeline as pl
    docs = lade("demo_synthetisch.json")
    p = pj.neues_projekt(docs, "t")
    for sid, x, y in (("0:S0", 565030.0, 5933020.0), ("0:S2", 565080.0, 5933060.0)):
        pj.aendern(docs, p, {"op": "sondierung", "sondierung": sid, "feld": "x", "wert": x})
        pj.aendern(docs, p, {"op": "sondierung", "sondierung": sid, "feld": "y", "wert": y})
    pj.aendern(docs, p, {"op": "sondierung", "sondierung": "0:S0", "feld": "geprueft", "wert": True})
    drin, raus = sd.fuer_ifc(docs, p)
    assert [s["code"] for s in drin] == ["DPH 1", "CPT 1"] and raus == [{"id": "0:S1", "code": "DPH 2", "grund": "ohne Lage"}]
    e = pj.einstellungen(p)
    v = pj.modell_eingabe(docs, p, e)
    m = pl.modell_bauen(v.docs, p.vorgabe, e.methode, e.puffer, e.raster, e.basis, pj.ursprung(p, v))
    f = ifcopenshell.file.from_string(pl.ifc_bytes(m, v.docs, sondierungen=drin).decode())
    log = validate.json_logger()
    validate.validate(f, log)
    assert not log.statements, log.statements[:3]
    sond = {b.Name: b for b in f.by_type("IfcBorehole") if (b.ObjectType or "").startswith("Sondierung")}
    assert set(sond) == {"DPH 1", "CPT 1"} and sond["DPH 1"].ObjectType == "Sondierung DPH"
    assert len([b for b in f.by_type("IfcBorehole") if b.Description != "Sondierung"]) == 12   # Bohrungen unveraendert

    def psets(b):
        return {r.RelatingPropertyDefinition.Name: r.RelatingPropertyDefinition for r in b.IsDefinedBy}

    ps = psets(sond["DPH 1"])
    werte = {q.Name: q.NominalValue.wrappedValue for q in ps["CPset_Sondierung"].HasProperties}
    assert werte["GOK_NHN"] == 38.6 and werte["Endtiefe_m"] == 6.0 and werte["Geprueft"] is True
    (n10,) = ps["CPset_Sondierung_Werte"].HasProperties
    assert n10.Name == "N10" and len(n10.DefiningValues) == 60
    gelesen = [r[2] for r in docs[0]["sondierungen"][0]["werte"]]
    assert [w.wrappedValue for w in n10.DefinedValues] == [float(x) for x in gelesen]   # unveraendert
    cpt = {q.Name for q in psets(sond["CPT 1"])["CPset_Sondierung_Werte"].HasProperties}
    assert {"q_c", "f_s"} <= cpt
    # Saeule: Mitte an der Lage (lokal = absolut - Ursprung), von der GOK bis GOK - Endtiefe
    rep = sond["DPH 1"].Representation.Representations[0].Items[0]
    k = np.array(rep.Coordinates.CoordList)
    assert np.allclose(k[:, :2].mean(axis=0), [565030.0 - m.ursprung[0], 5933020.0 - m.ursprung[1]], atol=0.01)
    assert np.isclose(k[:, 2].max(), 38.6) and np.isclose(k[:, 2].min(), 32.6)
    assert next(q.NominalValue.wrappedValue for g in f.by_type("IfcGeomodel") for r in g.IsDefinedBy
                for q in r.RelatingPropertyDefinition.HasProperties if q.Name == "Sondierungen_im_IFC") == "DPH 1, CPT 1"


def test_modell_nennt_sondierungen_ohne_lage(client):
    sig = client.post("/api/beispiel", json={"name": "demo"}).json()["projekt"]
    client.post(f"/api/projekt/{sig}/aendern", json={"ops": [
        {"op": "sondierung", "sondierung": "0:S0", "feld": "x", "wert": 565030},
        {"op": "sondierung", "sondierung": "0:S0", "feld": "y", "wert": 5933020}]})
    m = client.post(f"/api/projekt/{sig}/modell", json={}).json()
    assert "Sondierungen nicht im IFC: DPH 2 (ohne Lage), CPT 1 (ohne Lage)" in m["hinweise"]
    ifc = client.get(m["ifc"]).text
    assert "'Sondierung DPH'" in ifc and "'DPH 2'" not in ifc
