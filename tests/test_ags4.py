"""AGS4-Export (#30, docs/30 §5): nur Geprueftes, gueltig gegen den offiziellen Checker der AGS (python-ags4)."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
for p in ("services/geodaten", "services/modeler"):
    if str(REPO / p) not in sys.path:
        sys.path.insert(0, str(REPO / p))
from geodaten import ags4  # noqa: E402

DOCS = [{"document": {"file": "gutachten.pdf"}, "boreholes": [
    {"code": "BK 1", "x": 393507.12, "y": 5708058.4, "crs_epsg": 25832, "gok_nhn": 82.31, "end_depth": 6.0,
     "layers": [
         {"top_depth": 0, "bottom_depth": 0.4, "description_raw": "Mutterboden, schluffig, humos", "geprueft": True},
         {"top_depth": 0.4, "bottom_depth": 3.2, "description_raw": 'Feinsand, schwach schluffig, "locker", grau–braun',
          "geprueft": True},
         {"top_depth": 3.2, "bottom_depth": 6.0, "description_raw": "Geschiebemergel (Schluff, tonig, steif), Größtkorn 20 mm",
          "geprueft": True}],
     "groundwater": [{"depth": 2.1, "kind": "angetroffen", "observed_on": "2022-03-02"},
                     {"depth": 1.8, "kind": "Ruhewasser", "observed_on": "2022-03-03"},
                     {"depth": 2.5, "kind": "unbestimmt"}]},
    {"code": "BK 2", "layers": [{"top_depth": 0, "bottom_depth": 2, "description_raw": "Kies", "geprueft": True}]},
    {"code": "BK 3", "layers": [{"top_depth": 0, "bottom_depth": 2, "description_raw": "Kies", "geprueft": False}]}]}]
SONDIERUNGEN = [
    {"code": "DPH 1", "art": "DPH", "x": 393510.0, "y": 5708060.0, "epsg": 25832, "gok": 82.2, "endtiefe": 0.5,
     "geprueft": True, "dokument": "gutachten.pdf", "seite": 12,
     "werte": [[0.0, 0.1, 2], [0.1, 0.2, 3], [0.2, 0.3, 5], [0.3, 0.4, 8], [0.4, 0.5, ">50"]],
     "kurven": [("N10", [0.1, 0.2, 0.3, 0.4, 0.5], [2, 3, 5, 8, 50], "Schläge/10 cm")], "zensierte": [(0.4, 0.5, 50)]},
    {"code": "CPT 1", "art": "CPT", "x": 393512.0, "y": 5708061.0, "epsg": 25832, "gok": 82.0, "endtiefe": 0.4,
     "geprueft": True, "kurven": [("q_c", [0.0, 0.2, 0.4], [0.5, 3.2, 8.1], "MN/m²"), ("R_f", [0.0, 0.2, 0.4], [1.2, 0.8, 0.6], "%"),
                                  ("f_s", [0.0, 0.2], [10, 20], "wie im Diagramm (Einheit nicht gelesen)")]},
    {"code": "CPT 2", "art": "CPT", "geprueft": True,
     "kurven": [("q_c", [0.0], [1.0], "wie im Diagramm (Einheit nicht gelesen)")]},
    {"code": "DPH 2", "art": "DPH", "geprueft": False, "kurven": [("N10", [0.1], [3], "Schläge/10 cm")]}]


def gruppen(text: str) -> dict[str, list[dict]]:
    """Kleiner Leser fuer die Pruefung des Inhalts (die Form prueft der offizielle Checker)."""
    out, kopf, name = {}, [], ""
    for zeile in text.split("\r\n"):
        if not zeile:
            continue
        f = [x.replace('""', '"') for x in zeile[1:-1].split('","')]
        if f[0] == "GROUP":
            name = f[1]
            out[name] = []
        elif f[0] == "HEADING":
            kopf = f[1:]
        elif f[0] == "DATA":
            out[name].append(dict(zip(kopf, f[1:])))
    return out


@pytest.fixture(scope="module")
def export():
    return ags4.exportieren(DOCS, projekt="Probe Ä", sig="abc123", heute=date(2026, 11, 28), sondierungen=SONDIERUNGEN,
                            version="3.0")


def test_gueltig_gegen_den_offiziellen_checker(export, tmp_path):
    AGS4 = pytest.importorskip("python_ags4.AGS4")
    datei = tmp_path / "probe.ags"
    datei.write_bytes(export[0])
    fehler = AGS4.check_file(str(datei))
    regeln = {k: v for k, v in fehler.items() if k.startswith(("Rule", "AGS Format Rule", "General"))}
    assert regeln == {}, regeln
    assert any("4.1.1" in z["desc"] for z in fehler["Summary of data"])


def test_ascii_crlf_und_nur_gepruefte(export):
    inhalt, bericht = export
    inhalt.decode("ascii")                                        # Regel 1
    assert b"\r\n" in inhalt and b"\n" not in inhalt.replace(b"\r\n", b"")
    assert bericht["exportiert"] == ["BK 1", "BK 2"] and bericht["sondierungen"] == ["DPH 1", "CPT 1"]
    gruende = {a["code"]: a["grund"] for a in bericht["ausgelassen"]}
    assert gruende["BK 3"] == "nicht vollständig geprüft" and gruende["DPH 2"] == "Sondierung nicht geprüft"
    assert "ohne gelesene Einheit" in gruende["CPT 2"]                   # nie umgerechnet ohne Einheit


def test_inhalt_lage_schichten_wasser_und_sondierungen(export):
    g = gruppen(export[0].decode("ascii"))
    loca = {z["LOCA_ID"]: z for z in g["LOCA"]}
    assert (loca["BK 1"]["LOCA_NATE"], loca["BK 1"]["LOCA_GREF"], loca["BK 1"]["LOCA_GL"]) == ("393507.12", "EPSG:25832", "82.31")
    assert loca["BK 2"]["LOCA_NATE"] == "" and "ohne Koordinaten" in loca["BK 2"]["LOCA_REM"]
    assert {"ABBR_HDNG": "LOCA_GREF", "ABBR_CODE": "EPSG:25832", "ABBR_DESC": "ETRS89 / UTM zone 32N"} in g["ABBR"]
    geol = [z for z in g["GEOL"] if z["LOCA_ID"] == "BK 1"]
    assert geol[2]["GEOL_DESC"].startswith("Geschiebemergel") and "Groesstkorn" in geol[2]["GEOL_DESC"]   # umschrieben
    assert geol[1]["GEOL_DESC"] == 'Feinsand, schwach schluffig, "locker", grau-braun'
    assert geol[1]["GEOL_REM"] == "DIN 4023: fS, u'"
    # Anschnitt ist WSTG; Ruhewasser und Staende ohne Art sind kein Anschnitt (DREM), die Art nie geraten
    assert [(z["WSTG_DPTH"], z["WSTG_DTIM"]) for z in g["WSTG"]] == [("2.10", "2022-03-02")]
    assert [z["DREM_REM"] for z in g["DREM"]] == ["Ruhewasserspiegel am 2022-03-03", "Wasserstand, Art im Gutachten nicht angegeben"]
    dprb = g["DPRB"]
    assert [(z["DPRB_DPTH"], z["DPRB_BLOW"]) for z in dprb] == [("0.00", "2"), ("0.10", "3"), ("0.20", "5"), ("0.30", "8"), ("0.40", "50")]
    assert dprb[-1]["DPRB_REM"].startswith("mindestens") and g["DPRG"][0]["DPRG_TYPE"] == "DPH"
    scpt = g["SCPT"]
    assert [(z["SCPT_RES"], z["SCPT_FRR"], z["SCPT_FRES"]) for z in scpt] == [("0.500", "1.20", ""), ("3.200", "0.80", ""),
                                                                                ("8.100", "0.60", "")]
    assert "nicht uebertragen: f_s" in g["SCPG"][0]["SCPG_REM"]
    assert g["TRAN"][0]["TRAN_AGS"] == "4.1.1" and g["PROJ"][0]["PROJ_NAME"] == "Probe Ae"


def test_ohne_exportierbares_wird_abgelehnt():
    with pytest.raises(ValueError, match="keine exportierbare Bohrung"):
        ags4.exportieren([{"boreholes": [DOCS[0]["boreholes"][2]]}], projekt="x")


def test_export_ueber_die_app(tmp_path, monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    sys.path.insert(0, str(REPO))
    from server.api import app_erstellen
    from ui import pipeline as pl

    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    with TestClient(app_erstellen(tmp_path)) as c:
        sig = c.post("/api/beispiel", json={"name": "berlin"}).json()["projekt"]
        r = c.get(f"/api/projekt/{sig}/export/ags4")
        assert r.status_code == 400 and "keine exportierbare Bohrung" in r.json()["detail"]
        c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "alle_pruefen"}]})
        r = c.get(f"/api/projekt/{sig}/export/ags4")
        assert r.status_code == 200 and ".ags" in r.headers["content-disposition"]
        g = gruppen(r.content.decode("ascii"))
        im_modell = [b for b in c.get(f"/api/projekt/{sig}").json()["bohrungen"] if b["modell"]]
        assert len(g["LOCA"]) == len(im_modell) == 6 and g["GEOL"] and g["TRAN"][0]["TRAN_PROD"].startswith("GroundTwin")
        mit_lage = [z for z in g["LOCA"] if z["LOCA_GREF"]]
        assert len(mit_lage) == 5 and all(z["LOCA_GREF"] == "EPSG:25833" for z in mit_lage)
        AGS4 = pytest.importorskip("python_ags4.AGS4")
        (tmp_path / "berlin.ags").write_bytes(r.content)
        fehler = AGS4.check_file(str(tmp_path / "berlin.ags"))
        assert {k: v for k, v in fehler.items() if k.startswith(("Rule", "AGS Format Rule", "General"))} == {}
