"""Bewertbarkeit je Projekt (Issue #35, A3, docs/29 §8.3): der Planer des Wissenskatalogs auf den Grundgroessen des
Projekts, in der App (Zustand und Route) und im Bericht des Informationspakets. Handpruefung an Berlin und Talheim."""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    arbeit = tmp_path_factory.mktemp("arbeit")
    alt, pl.ARBEIT = pl.ARBEIT, arbeit
    with TestClient(app_erstellen(arbeit)) as c:
        yield c
    pl.ARBEIT = alt


def bereitschaft(client, name, *ops):
    sig = client.post("/api/beispiel", json={"name": name}).json()["projekt"]
    if ops:
        assert client.post(f"/api/projekt/{sig}/aendern", json={"ops": list(ops)}).status_code == 200
    b = client.get(f"/api/projekt/{sig}/bereitschaft").json()
    assert client.get(f"/api/projekt/{sig}").json()["bereitschaft"] == b                 # gleich im Zustand
    return sig, b, {e["id"]: e for e in b["eintraege"]}


def ids(lst):
    return {x["id"] for x in lst}


def test_berlin_von_hand(client):
    """Berlin: Lage UTM, GOK, Wasserstaende mit Art; kein Labor; Sondierungen ohne Lage zaehlen nicht."""
    _, b, e = bereitschaft(client, "berlin")
    assert ids(b["verfuegbar"]) == {"bohrung.schichten", "bohrung.lage", "bohrung.gok", "boden.beschreibung",
                                    "grundwasser.staende", "grundwasser.art"}
    for k in ("modell.schichtenmodell", "analyse.kreuzprobe", "analyse.unsicherheit", "analyse.grundwasserflaeche",
              "hb.vorschlag"):
        assert e[k]["status"] == "moeglich", k
    assert e["daub.tbm_vorauswahl_boden"]["status"] == "hinweisend" and e["daub.tbm_vorauswahl_boden"]["abdeckung"] == "2/8"
    assert e["labor.statistik_einheit"]["status"] == "blockiert" and ids(e["labor.statistik_einheit"]["fehlt"]) == {"labor.messwerte"}
    assert e["hb.kennwerte_ansprache"]["status"] == "blockiert"
    fehlend = {f["id"]: f for f in b["fehlend"]}
    assert fehlend["hb.zuordnung"]["eingabe"] is True and "VOB/C" in fehlend["hb.zuordnung"]["liefert"]
    assert b["zusammenfassung"] == {"moeglich": 8, "hinweisend": 1, "blockiert": 5}


def test_talheim_von_hand_und_mit_homogenbereichen(client):
    """Talheim: Reihe (Lage angenommen), Labor nur mit Wassergehalt -> I_c fehlt w_L und w_P."""
    sig, b, e = bereitschaft(client, "talheim")
    m = e["modell.schichtenmodell"]
    assert m["status"] == "hinweisend" and ids(m["angenommen"]) == {"bohrung.lage"}
    assert e["labor.statistik_einheit"]["status"] == "moeglich"
    assert ids(e["labor.konsistenzzahl"]["fehlt"]) == {"labor.fliessgrenze", "labor.ausrollgrenze"}
    namen = [x["name"] for x in client.post(f"/api/projekt/{sig}/modell").json()["bericht"]["einheiten"]]
    r = client.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "homogenbereiche", "atv": "DIN 18300",
                                                                  "zuordnung": {namen[0]: "A"}}]})
    assert r.status_code == 200
    e2 = {x["id"]: x for x in r.json()["zustand"]["bereitschaft"]["eintraege"]}
    assert e2["hb.kennwerte_ansprache"]["status"] == "moeglich"                       # Zuordnung des Planers da


def test_reihenfolge_und_unbekanntes_projekt(client):
    _, b, _ = bereitschaft(client, "demo")
    reihenfolge = [x["status"] for x in b["eintraege"]]
    assert reihenfolge == sorted(reihenfolge, key=["moeglich", "hinweisend", "blockiert"].index)
    assert client.get("/api/projekt/nichtda/bereitschaft").status_code == 404


def test_bewertbarkeit_im_informationspaket(client):
    sig, b, _ = bereitschaft(client, "berlin")
    r = client.get(f"/api/projekt/{sig}/export/agsi")
    assert r.status_code == 200
    z = zipfile.ZipFile(io.BytesIO(r.content))
    man = json.loads(z.read("manifest.json"))
    assert man["bereitschaft"]["zusammenfassung"] == b["zusammenfassung"]
    md = z.read("bericht.md").decode()
    assert "## Bewertbarkeit" in md and "DAUB" in md and "Korngrößenverteilung" in md
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "services/wissen/schemas/manifest.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(man)
