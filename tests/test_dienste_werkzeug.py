"""Werkzeug „Dienste der Länder“ (server/dienste_werkzeug.py, geodaten/dienste.py, docs/21 §4.8, D98): Register lesen,
pruefen, speichern (mit Stand gegen stilles Ueberschreiben), im Netz nur lesen; die App fragt danach mit dem neuen Stand.

Gearbeitet wird auf einer Kopie von dienste.json; die echten Dienste ersetzen Attrappen (kein Netz).
"""
from __future__ import annotations

import base64
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "services" / "geodaten")]
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from geodaten import bohrdaten, netz  # noqa: E402
from geodaten import dienste as register  # noqa: E402
from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402

MUENCHEN = (691567.3, 5334734.3, 25832)


@pytest.fixture()
def kopie(tmp_path, monkeypatch):
    datei = tmp_path / "dienste.json"
    shutil.copy(register.DATEI, datei)
    monkeypatch.setattr(register, "DATEI", datei)
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    monkeypatch.delenv("GEO_AGENT_DIENSTE_BEARBEITEN", raising=False)
    yield datei
    monkeypatch.undo()
    bohrdaten.neu_laden(erzwingen=True)                  # wieder das Register aus dem Repo


def client(arbeit: Path, passwort: str = "") -> TestClient:
    kopf = {"Authorization": "Basic " + base64.b64encode(f"x:{passwort}".encode()).decode()} if passwort else {}
    return TestClient(app_erstellen(arbeit, passwort=passwort), headers=kopf)


def test_register_lesen(kopie, tmp_path):
    r = client(tmp_path).get("/api/dienste").json()
    assert r["bearbeiten"] and r["grund"] == "" and r["format"] == "groundtwin-dienste/2"
    assert r["laender"][0] == "Deutschland" and len(r["laender"]) == 17
    assert set(r["arten"]) == set(register.ARTEN) and r["arten"]["wcs-dgm"]["pflicht"] == ["coverage", "achsen", "system", "raster_m"]
    laender = {land for d in r["dienste"] for land in d.get("laender") or []}
    assert len(laender) == 16                                                  # alle Laender mit mindestens einem Eintrag
    for thema in register.THEMEN:                                              # und jedes Land in jedem Thema
        gedeckt = {land for d in r["dienste"] if register.thema(d) == thema for land in d.get("laender") or []}
        assert len(gedeckt) == 16, thema
    assert register.fehler({"dienste": r["dienste"]}) == []


def test_speichern_aendert_die_app_sofort(kopie, tmp_path):
    c = client(tmp_path)
    r = c.get("/api/dienste").json()
    by = next(d for d in r["dienste"] if d["id"] == "BY")
    by["url"] = "https://www.example.org/bayern-bohrungen"
    by["hinweis"] = "neu eingetragen"
    neu = {"id": "SN-WFS", "land": "Sachsen", "art": "portal-bohrungen", "titel": "Testportal", "anbieter": "LfULG",
           "url": "https://www.example.org/sachsen", "lizenz": "", "namensnennung": "LfULG", "beleg": "https://www.example.org/",
           "eigenes_feld": 7}
    s = c.put("/api/dienste", json={"dienste": r["dienste"] + [neu], "version": r["version"]})
    assert s.status_code == 200, s.text
    gespeichert = json.loads(kopie.read_text(encoding="utf-8"))
    sn = next(d for d in gespeichert["dienste"] if d["id"] == "SN-WFS")
    assert sn["laender"] == ["Sachsen"] and sn["status"] == "ungeprueft" and len(sn["gebiet_wgs84"]) == 4   # ergaenzt
    assert sn["eigenes_feld"] == 7 and list(sn)[-1] == "eigenes_feld"         # unbekannte Angaben bleiben, hinten
    ids = [d["id"] for d in gespeichert["dienste"]]
    assert ids[0] == "DE-BGR" and ids.index("SN") < ids.index("SN-WFS")          # Deutschland zuerst, dann je Land
    assert gespeichert["stand"] == s.json()["stand"] and s.json()["version"] != r["version"]
    # die App fragt sofort mit dem neuen Stand (ohne Neustart)
    muenchen = bohrdaten.am_ort(*MUENCHEN)
    assert next(d for d in muenchen if d["dienst"] == "BY")["url"] == "https://www.example.org/bayern-bohrungen"


def test_alter_stand_und_fehler_werden_abgelehnt(kopie, tmp_path):
    c = client(tmp_path)
    r = c.get("/api/dienste").json()
    vorher = kopie.read_bytes()
    assert c.put("/api/dienste", json={"dienste": r["dienste"], "version": "1"}).status_code == 409
    kaputt = [dict(d) for d in r["dienste"]]
    kaputt[0] = {**kaputt[0], "id": "klein", "url": "ftp://x"}
    kaputt.append({**kaputt[1]})                                               # Kennung doppelt
    kaputt.append({"id": "BY-LOD2X", "land": "Bayern", "art": "lod2-kacheln", "titel": "t", "anbieter": "a",
                   "url": "https://example.org/kachel.gml", "system": 25832, "format": "gml", "kachel_km": 1})
    kaputt.append({"id": "XX", "land": "Atlantis", "laender": ["Atlantis"], "art": "portal-dgm", "titel": "t",
                   "anbieter": "a", "url": "https://example.org"})
    s = c.put("/api/dienste", json={"dienste": kaputt, "version": r["version"]})
    assert s.status_code == 400
    text = s.json()["detail"]
    for teil in ("Großbuchstaben", "https://", "doppelt", "{e} und {n}", "Atlantis"):
        assert teil in text, teil
    assert kopie.read_bytes() == vorher                                        # nichts geschrieben


def test_im_netz_nur_lesen_und_gespeicherte_pruefen(kopie, tmp_path, monkeypatch):
    aufgerufen = []
    monkeypatch.setattr(netz, "erreichbar", lambda url, zeit: (aufgerufen.append(url), (200, b"<html>"))[1])
    c = client(tmp_path, passwort="geheim")
    r = c.get("/api/dienste").json()
    assert not r["bearbeiten"] and "GEO_AGENT_DIENSTE_BEARBEITEN" in r["grund"]
    assert c.put("/api/dienste", json={"dienste": r["dienste"], "version": r["version"]}).status_code == 403
    fremd = {"id": "X", "land": "Bayern", "art": "portal-dgm", "titel": "t", "anbieter": "a", "url": "http://169.254.169.254/"}
    assert c.post("/api/dienste/pruefen", json={"eintrag": fremd}).status_code == 403
    assert aufgerufen == []                                                    # keine Adresse aus der Anfrage
    p = c.post("/api/dienste/pruefen", json={"id": "BY"}).json()
    assert p["ok"] and p["id"] == "BY" and "HTTP 200" in p["meldung"] and aufgerufen[0].startswith("https://")
    assert c.post("/api/dienste/pruefen", json={"id": "GIBTSNICHT"}).status_code == 404
    monkeypatch.setenv("GEO_AGENT_DIENSTE_BEARBEITEN", "1")                   # ausdruecklich erlaubt
    assert client(tmp_path, passwort="geheim").get("/api/dienste").json()["bearbeiten"]


CAPS_WFS = (b'<wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs/2.0"><wfs:FeatureTypeList>'
            b'<wfs:FeatureType><wfs:Name>bohrungen:a</wfs:Name></wfs:FeatureType></wfs:FeatureTypeList></wfs:WFS_Capabilities>')


def test_pruefen_je_art(kopie, tmp_path, monkeypatch):
    c = client(tmp_path)
    monkeypatch.setattr(netz, "holen", lambda url, zeit: CAPS_WFS)
    p = c.post("/api/dienste/pruefen", json={"id": "BE"}).json()
    assert not p["ok"] and "aber ohne" in p["meldung"] and p["gefunden"] == ["bohrungen:a"]   # Typ fehlt: gemeldet
    entwurf = {**bohrdaten.dienst("BE"), "typen": ["bohrungen:a"]}
    assert c.post("/api/dienste/pruefen", json={"eintrag": entwurf}).json()["ok"]             # Entwurf beim Bearbeiten

    def kaputt(url, zeit):
        raise netz.DienstFehler("keine Antwort in 15 s")
    monkeypatch.setattr(netz, "erreichbar", kaputt)
    p = c.post("/api/dienste/pruefen", json={"id": "BY"}).json()
    assert not p["ok"] and "keine Antwort" in p["meldung"]
    kacheln = []
    monkeypatch.setattr(netz, "erreichbar", lambda url, zeit: (kacheln.append(url), (200, b"PK"))[1])
    p = c.post("/api/dienste/pruefen", json={"id": "NW-LOD2"}).json()
    assert p["ok"] and "{e}" not in kacheln[0] and kacheln[0].endswith("_1_NW.gml")         # Kachel in der Mitte
    s = c.post("/api/dienste/pruefen", json={"eintrag": {"id": "x", "art": "portal-dgm"}})
    assert s.status_code == 400 and "fehlt" in s.json()["detail"]


def test_die_seite_gibt_es(tmp_path):
    dist = REPO / "apps" / "web" / "dist" / "dienste.html"
    if not dist.exists():
        pytest.skip("apps/web nicht gebaut")
    assert "Dienste der Länder" in dist.read_text(encoding="utf-8")


def test_register_ausserhalb_des_repos(tmp_path, monkeypatch):
    """GEO_AGENT_DIENSTE (Container: /data): fehlt die Datei, beginnt sie als Kopie des Registers aus dem Repo."""
    ziel = tmp_path / "daten" / "dienste.json"
    monkeypatch.setattr(register, "DATEI", ziel)
    assert register.laden()["dienste"] == json.loads(register.STANDARD.read_text(encoding="utf-8"))["dienste"]
    assert ziel.exists() and register.version() == str(ziel.stat().st_mtime_ns)
    daten = register.laden()
    daten["dienste"] = [d for d in daten["dienste"] if d["id"] != "BY"]
    register.speichern(daten)
    assert "BY" not in {d["id"] for d in register.laden()["dienste"]}
    assert "BY" in {d["id"] for d in json.loads(register.STANDARD.read_text(encoding="utf-8"))["dienste"]}   # Repo bleibt
    monkeypatch.undo()
    bohrdaten.neu_laden(erzwingen=True)
