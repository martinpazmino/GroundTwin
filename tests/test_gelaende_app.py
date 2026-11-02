"""DGM in der Schritt-App: hochladen, GOK gegen das Gelaende pruefen, fehlende GOK uebernehmen (docs/23 §2.4)."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.api import app_erstellen  # noqa: E402
from ui import pipeline as pl  # noqa: E402

BERLIN = json.loads((REPO / "data" / "beispiele" / "berlin_v67b.json").read_text(encoding="utf-8"))
OHNE_GOK = "422C-5527"


def ebene_fit(docs):
    """Ebene durch die GOK der Berliner Bohrungen mit Koordinaten (kleinste Quadrate)."""
    pts = [(b["x"], b["y"], b["gok_nhn"]) for b in BERLIN["boreholes"] if b.get("x") is not None]
    a = np.array([[1.0, x - 394800.0, y - 5818400.0] for x, y, _ in pts])
    k, *_ = np.linalg.lstsq(a, np.array([z for *_, z in pts]), rcond=None)
    return lambda x, y: float(k[0] + k[1] * (x - 394800.0) + k[2] * (y - 5818400.0))


EBENE = ebene_fit(BERLIN)


def dgm_xyz(versatz: float = 0.0, d: float = 2.0) -> bytes:
    zeilen = []
    for y in np.arange(5818300.0, 5818500.0 + d / 2, d):
        for x in np.arange(394700.0, 394950.0 + d / 2, d):
            zeilen.append(f"{x:.1f} {y:.1f} {EBENE(x, y) + versatz:.3f}")
    return ("\n".join(zeilen) + "\n").encode()


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(pl, "ARBEIT", tmp_path)
    with TestClient(app_erstellen(tmp_path)) as c:
        docs = copy.deepcopy(BERLIN)
        for b in docs["boreholes"]:
            if b["code"] == OHNE_GOK:
                b["gok_nhn"] = None                       # eine Bohrung ohne GOK im PDF
        sig = c.app.state.arbeitsplatz.anlegen([docs])
        yield c, sig


def hochladen(c, sig, daten: bytes, epsg="25833", name="dgm1.xyz", status=200):
    r = c.post(f"/api/projekt/{sig}/dgm", files=[("dateien", (name, daten, "text/plain"))], data={"epsg": epsg})
    assert r.status_code == status, r.text
    return r.json()


def zeilen(z):
    return {r["code"]: r for r in z["gelaende"]["pruefung"]["zeilen"]}


def test_dgm_pruefen_und_gok_uebernehmen(app):
    c, sig = app
    assert c.get(f"/api/projekt/{sig}").json()["gelaende"] is None
    z = hochladen(c, sig, dgm_xyz())
    info, pr = z["gelaende"]["info"], z["gelaende"]["pruefung"]
    assert info["epsg"] == 25833 and info["dx"] == 2.0 and info["name"] == "dgm1.xyz" and "datei" not in info
    st = zeilen(z)
    assert st[OHNE_GOK]["status"] == "ohne_gok" and st[OHNE_GOK]["dgm"] == pytest.approx(EBENE(394909.3, 5818442.5), abs=0.01)
    assert st["S2a"]["status"] == "ohne_lage"
    for code in ("422C-460", "422C-461", "422C-5525", "422C-5526"):
        assert st[code]["status"] in ("ok", "abweichung") and abs(st[code]["differenz"]) < 0.5
    assert pr["vorschlaege"] == 1 and not any("im Mittel" in w for w in pr["warnungen"])
    # nur auf Klick: GOK aus dem DGM, markiert
    r = c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "gok_aus_dgm"}]}).json()
    assert r["meldungen"] == [f"GOK aus dem DGM: {OHNE_GOK}"]
    zeile = next(b for b in r["zustand"]["bohrungen"] if b["code"] == OHNE_GOK)
    assert zeile["gok_quelle"] == "DGM" and zeile["gok"] == pytest.approx(st[OHNE_GOK]["dgm"])
    assert zeilen(r["zustand"])[OHNE_GOK]["status"] == "aus_dgm"
    nadel = next(n for n in r["zustand"]["viewer"]["bohrungen"] if n["code"] == OHNE_GOK)
    assert nadel["gok_quelle"] == "DGM" and nadel["gok_bekannt"]
    # nichts mehr vorzuschlagen
    fehler = c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "gok_aus_dgm"}]})
    assert fehler.status_code == 400 and "ohne GOK" in fehler.json()["detail"]
    # das Modell nimmt die Bohrung jetzt mit; das IFC nennt die Hoehenquelle
    m = c.post(f"/api/projekt/{sig}/modell").json()
    assert not m["fehler"] and OHNE_GOK in {b["code"] for b in m["bericht"]["bohrungen"]}
    ifc = c.get(f"/api/projekt/{sig}/export/ifc").content.decode("utf-8", "replace")
    assert "aus dem DGM (m NHN)" in ifc
    # von Hand geaendert: Quelle manuell
    bid = zeile["id"]
    r = c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "bohrung", "id": bid, "feld": "gok", "wert": 35.0}]}).json()
    assert next(b for b in r["zustand"]["bohrungen"] if b["id"] == bid)["gok_quelle"] == "manuell"


def test_systematische_abweichung_und_anderes_system(app):
    c, sig = app
    z = hochladen(c, sig, dgm_xyz(versatz=-3.0))           # Gelaende 3 m tiefer: GOK liegt 3 m darueber
    w = " ".join(z["gelaende"]["pruefung"]["warnungen"])
    assert "im Mittel" in w and "über dem DGM" in w and z["gelaende"]["pruefung"]["median"] == pytest.approx(3.0, abs=0.3)
    z = hochladen(c, sig, dgm_xyz(), epsg="25832")         # ersetzt das DGM; Bohrungen sind in 25833
    st = zeilen(z)
    assert st["422C-460"]["status"] == "anderes_system" and "anderen System" in " ".join(z["gelaende"]["pruefung"]["warnungen"])
    z = hochladen(c, sig, dgm_xyz(), epsg="25833")         # dieselbe Datei, richtiges System: kein alter Stand im Speicher
    assert zeilen(z)["422C-460"]["status"] == "ok" and z["gelaende"]["info"]["epsg"] == 25833


def test_fehler_reihe_und_entfernen(app):
    c, sig = app
    r = hochladen(c, sig, b"kein dgm", status=400)
    assert "dgm1.xyz" in r["detail"]
    assert hochladen(c, sig, dgm_xyz(), epsg="utm", status=400)["detail"].startswith("EPSG")
    hochladen(c, sig, dgm_xyz())
    leer = c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "gok_aus_dgm", "ids": []}]})   # leere Auswahl
    assert leer.status_code == 400 and "ohne GOK" in leer.json()["detail"]
    z = c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "lage_modus", "wert": "reihe"}]}).json()["zustand"]
    assert z["gelaende"]["pruefung"] is None and "Koordinaten" in z["gelaende"]["fehler"]
    z = c.post(f"/api/projekt/{sig}/aendern", json={"ops": [{"op": "lage_modus", "wert": "koordinaten"},
                                                           {"op": "gok_aus_dgm"}]}).json()["zustand"]
    z = c.delete(f"/api/projekt/{sig}/dgm").json()
    assert z["gelaende"] is None
    assert next(b for b in z["bohrungen"] if b["code"] == OHNE_GOK)["gok_quelle"] == "DGM"   # uebernommene GOK bleibt
    hochladen(c, "nichtda", dgm_xyz(), status=404)         # unbekanntes Projekt
