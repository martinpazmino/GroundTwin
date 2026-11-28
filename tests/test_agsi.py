"""Informationspaket v0 (Issue #33, A1): AGSi 1.0.1 + Manifest + Bericht ueber die App.

Ohne Netz: Aufbau, eindeutige IDs und Verweise, Manifest (Wertart und Quelle je Wert, Schema von A0), keine Parameter.
Mit Netz: gueltig nach dem amtlichen AGSi-JSON-Schema 1.0.1 (2019-09) mit Formatpruefung (sha256 des ZIP geprueft).
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "services" / "geodaten"))
sys.path.insert(0, str(ROOT / "services" / "modeler"))

from fastapi.testclient import TestClient  # noqa: E402
from geodaten import agsi  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402

SCHEMA_ZIP = "https://ags-data-format-wg.gitlab.io/agsi/agsi_standard/1.0.1/schema/AGSi_JSONSchema_v1-0-1.zip"
SCHEMA_SHA256 = "8d8529d80a25d4f5f1450583e3ea74cc8e9c5673b0e1ba9795d42893a61d6ef3"     # gelesen 2026-11-22


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    arbeit = tmp_path_factory.mktemp("arbeit")
    alt, pl.ARBEIT = pl.ARBEIT, arbeit
    with TestClient(app_erstellen(arbeit)) as c:
        yield c
    pl.ARBEIT = alt


def paket(client, name: str, *ops) -> tuple[zipfile.ZipFile, dict, dict, str]:
    sig = client.post("/api/beispiel", json={"name": name}).json()["projekt"]
    if ops:
        assert client.post(f"/api/projekt/{sig}/aendern", json={"ops": list(ops)}).status_code == 200
    r = client.get(f"/api/projekt/{sig}/export/agsi")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/zip" and "_agsi.zip" in r.headers["content-disposition"]
    z = zipfile.ZipFile(io.BytesIO(r.content))
    stamm = next(n for n in z.namelist() if n.endswith("_agsi.json"))
    return z, json.loads(z.read(stamm)), json.loads(z.read("manifest.json")), sig


def _alle(o, schluessel: str):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == schluessel:
                yield v
            yield from _alle(v, schluessel)
    elif isinstance(o, list):
        for x in o:
            yield from _alle(x, schluessel)


@pytest.fixture(scope="module")
def berlin(client):
    sig = client.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
    namen = [e["name"] for e in client.post(f"/api/projekt/{sig}/modell").json()["bericht"]["einheiten"]]
    zu = {namen[0]: "A", namen[1]: "B", namen[2]: "B"}
    return paket(client, "berlin", {"op": "alle_pruefen"},
                 {"op": "homogenbereiche", "atv": "DIN 18300", "zuordnung": zu}), zu


def test_berlin_paket_inhalt_ids_und_verweise(berlin):
    (z, a, man, _), zu = berlin
    stamm = a["agsProject"]["projectName"]
    namen = set(z.namelist())
    assert {"manifest.json", "bericht.md", "LIESMICH.txt"} <= namen
    assert any(n.startswith("geometrie/") and n.endswith(".ifc") for n in namen)
    assert any(n.startswith("fachdaten/") and n.endswith("_boreholeml.xml") for n in namen)      # alle geprueft
    assert any(n.startswith("fachdaten/") and n.endswith(".ags") for n in namen)                 # AGS4 (#30)
    assert a["agsSchema"] == {"name": "AGSi", "version": "1.0.1", "link": agsi.AGSI_LINK} and stamm
    assert agsi.pruefen(a) == [] and agsi.manifest_pruefen(a, man) == []
    m1 = a["agsiModel"][0]
    assert m1["category"] == "Observational" and all(e["elementType"] == "Geological unit" for e in m1["agsiModelElement"])
    # Geometrie verweist auf das IFC im Paket, jede Bohrungsspalte mit Einheit auf ein definiertes Codeset
    ifc = next(n for n in namen if n.endswith(".ifc"))
    assert {e["agsiGeometry"]["fileURI"] for e in m1["agsiModelElement"]} == {ifc}
    loecher = m1["agsiObservationSet"][0]["agsiObservationExpHole"]
    assert len(loecher) == 5 and all(h["topCoordinate"][0] > 390000 for h in loecher)          # UTM, nicht lokal
    assert any(c.get("geologyCode") for h in loecher for c in h["agsiObservationColumn"])
    # je ATV ein Modell der Homogenbereiche mit den zugeordneten Einheiten
    hb = [mo for mo in a["agsiModel"] if mo["modelType"] == "Homogenbereiche (VOB/C)"]
    assert len(hb) == 1 and {e["elementName"] for e in hb[0]["agsiModelElement"]} == set(zu.values())
    # keine Parameter (charakteristische Werte setzt der Ingenieur), nur Properties
    assert not list(_alle(a, "agsiDataParameterValue"))
    # Dateien im Manifest mit sha256, die zum Inhalt passen
    for n, t in man["teile"].items():
        assert hashlib.sha256(z.read(n)).hexdigest() == t["sha256"]


def test_manifest_jeder_wert_mit_wertart_und_quelle(berlin):
    jsonschema = pytest.importorskip("jsonschema")
    (z, a, man, _), _ = berlin
    schema = json.loads((ROOT / "services/wissen/schemas/manifest.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(man)
    ids = {w["agsi_id"] for w in man["werte"]}
    for d in _alle(a, "dataID"):
        assert d in ids
    assert all(w["kind"] and w["herkunft"]["quellen"] for w in man["werte"])
    assert {w["kind"] for w in man["werte"]} >= {"observed", "modelled", "interpreted"}
    assert not any(w.get("charakteristisch") for w in man["werte"])
    assert {o["was"] for o in man["offen"]} >= {"charakteristische Werte", "Kennwerte aus den Tabellen des Gutachtens"}
    assert man["analyse"]["kreuzprobe"]["gesamt"]["n"] > 0                                     # ab drei Bohrungen
    md = z.read("bericht.md").decode()
    assert "## Einheiten" in md and "Homogenbereiche DIN 18300" in md and "Offen" in md


def test_talheim_laborwerte_als_property_summary(client):
    z, a, man, _ = paket(client, "talheim")
    summ = [s for e in a["agsiModel"][0]["agsiModelElement"] for s in e.get("agsiDataPropertySummary") or []]
    assert summ and all(s["caseID"] == "Labor" and s["valueCount"] >= 1 and s["valueMin"] <= s["valueMax"]
                        for s in summ)
    kind = {w["agsi_id"]: w for w in man["werte"]}
    assert all(kind[s["dataID"]]["kind"] == "observed" and kind[s["dataID"]]["herkunft"]["eingaben"] for s in summ)
    assert not any(n.startswith("fachdaten/") for n in z.namelist())                         # nichts geprueft
    assert any(o["was"] == "BoreholeML (Fachdaten)" for o in man["offen"])
    assert agsi.pruefen(a) == [] and agsi.manifest_pruefen(a, man) == []


def test_pruefen_findet_doppelte_ids_und_tote_verweise(berlin):
    (_, a, man, _), _ = berlin
    b = json.loads(json.dumps(a))
    els = b["agsiModel"][0]["agsiModelElement"]
    els[1]["elementID"] = els[0]["elementID"]
    b["agsiModel"][0]["coordSystemID"] = "FEHLT"
    hole = b["agsiModel"][0]["agsiObservationSet"][0]["agsiObservationExpHole"][0]
    hole["agsiObservationColumn"][0]["geologyCode"] = "E99"
    f = agsi.pruefen(b)
    assert any("elementID doppelt" in x for x in f) and any("coordSystemID" in x for x in f)
    assert any("geologyCode E99" in x for x in f)
    m2 = {**man, "werte": man["werte"][1:]}
    m2["werte"].append({"agsi_id": "GIBTS/NICHT", "groesse": "x", "kind": "observed", "herkunft": {"quellen": ["Q1"]}})
    assert any("keine solche AGSi-ID" in x for x in agsi.manifest_pruefen(a, m2))


# ---------------------------------------------------------------- mit Netz: amtliches AGSi-JSON-Schema
@pytest.fixture(scope="module")
def agsi_schema():
    jsonschema = pytest.importorskip("jsonschema")
    try:
        with urllib.request.urlopen(SCHEMA_ZIP, timeout=30) as antwort:
            daten = antwort.read()
    except OSError as err:
        pytest.skip(f"AGSi-Schema nicht erreichbar ({err})")
    assert hashlib.sha256(daten).hexdigest() == SCHEMA_SHA256, "AGSi-Schema geaendert: neu lesen und sha256 setzen"
    schema = json.loads(zipfile.ZipFile(io.BytesIO(daten)).read("AGSi_JSONSchema_v1-0-1_2019-09.json"))
    cls = jsonschema.Draft201909Validator
    cls.check_schema(schema)
    return cls(schema, format_checker=cls.FORMAT_CHECKER)


@pytest.mark.parametrize("name", ["berlin", "talheim", "demo"])
def test_gueltig_nach_amtlichem_agsi_schema(client, agsi_schema, name):
    _, a, _, _ = paket(client, name)
    fehler = sorted(agsi_schema.iter_errors(a), key=str)
    assert not fehler, [f"{list(e.absolute_path)}: {e.message}" for e in fehler[:5]]


def test_gueltig_mit_homogenbereichen_und_boreholeml(berlin, agsi_schema):
    (_, a, _, _), _ = berlin
    assert not list(agsi_schema.iter_errors(a))
