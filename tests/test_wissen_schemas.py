"""Schemas von GroundTwin Analysis (D108, Issue #32): Katalogeintrag und Manifest nehmen gueltige Beispiele an und
weisen die Fehler ab, die D108 ausschliesst (charakteristischer Wert ohne Ingenieur, abgeleiteter Wert ohne
Katalogeintrag, unbekannte Wertart)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")
SCHEMAS = Path(__file__).resolve().parents[1] / "services" / "wissen" / "schemas"


def schema(name):
    s = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(s)
    return jsonschema.Draft202012Validator(s)


EINTRAG = {
    "id": "cpt.sbt.robertson2009", "version": "1.0.0", "kind": "correlation", "authority": "correlation",
    "source": {"citation": "Robertson (2009), Interpretation of cone penetration tests", "edition": 2009, "verified": False},
    "inputs": {"required": ["cpt.qt", "cpt.fs", "stress.sigma_v0", "stress.sigma_v0_eff"], "optional": ["cpt.u2"]},
    "outputs": ["soil.sbt_zone", "soil.ic"],
    "preconditions": ["cone calibration known"], "validity": {"soil.ic": [1.0, 4.0]},
    "uncertainty": {"model": "categorical", "note": "±0.1 Ic an den Zonengrenzen als mehrdeutig"},
    "when_missing": {"stress.sigma_v0_eff": "block"}, "tests": ["tests/wissen/cpt_sbt_cases.json"],
}
MANIFEST = {
    "format": "groundtwin-manifest/1", "projekt": "Demo", "erzeugt": "2026-11-22T12:00:00Z",
    "quellen": [{"id": "Q1", "art": "gutachten", "datei": "demo.pdf", "sha256": "0" * 64}],
    "werte": [
        {"agsi_id": "E1/Reibungswinkel", "groesse": "soil.phi", "kind": "derived",
         "herkunft": {"quellen": ["Q1"], "katalog": {"id": "dph.lagerung.din4094", "version": "1.0.0"}, "eingaben": ["S1/N10"]},
         "unsicherheit": {"transformation": 2.5, "statistik_n": 3}},
        {"agsi_id": "E1/N10", "groesse": "dph.n10", "kind": "observed", "herkunft": {"quellen": ["Q1"], "seite": 22}},
        {"agsi_id": "E1/phi_k", "groesse": "soil.phi_k", "kind": "interpreted", "charakteristisch": True,
         "eingegeben_von": "Ingenieur (Name im Projekt)", "herkunft": {"quellen": ["Q1"]}},
    ],
}


def test_gueltige_beispiele():
    schema("katalog_eintrag.schema.json").validate(EINTRAG)
    schema("manifest.schema.json").validate(MANIFEST)


@pytest.mark.parametrize("aendern", [
    lambda m: m["werte"][2].pop("eingegeben_von"),                       # charakteristisch ohne Ingenieur
    lambda m: m["werte"][0]["herkunft"].pop("katalog"),                  # abgeleitet ohne Katalogeintrag
    lambda m: m["werte"][1].update(kind="geschaetzt"),                   # unbekannte Wertart
    lambda m: m["werte"][1].update(sigma=0.1),                           # fremdes Attribut
])
def test_manifest_weist_ab(aendern):
    m = copy.deepcopy(MANIFEST)
    aendern(m)
    with pytest.raises(jsonschema.ValidationError):
        schema("manifest.schema.json").validate(m)


@pytest.mark.parametrize("aendern", [
    lambda e: e["source"].pop("verified"),                               # Quelle ohne Pruefvermerk
    lambda e: e.update(kind="formel"),
    lambda e: e.update(outputs=[]),
    lambda e: e["when_missing"].update({"cpt.qt": "raten"}),
])
def test_katalogeintrag_weist_ab(aendern):
    e = copy.deepcopy(EINTRAG)
    aendern(e)
    with pytest.raises(jsonschema.ValidationError):
        schema("katalog_eintrag.schema.json").validate(e)
