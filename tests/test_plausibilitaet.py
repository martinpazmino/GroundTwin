"""Tests fuer den Plausibilitaetsbericht je Bohrung (ui/plausibilitaet.py und server/arbeitsplatz.py)."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from server.arbeitsplatz import Arbeitsplatz  # noqa: E402
from ui import plausibilitaet as pb  # noqa: E402
from ui import projekt as pj  # noqa: E402


def _bohrung(
    code: str = "B 1",
    schichten: list[tuple[float, float, str]] | None = None,
    gok: float | None = 50.0,
    end_depth: float | None = 5.0,
    gw: list[float] | None = None,
    x: float | None = 500000.0,
    y: float | None = 5700000.0,
    epsg: int | None = 25832,
) -> dict:
    if schichten is None:
        schichten = [(0.0, 2.0, "Sand"), (2.0, 5.0, "Kies")]
    return {
        "code": code,
        "kind": "Bohrung",
        "gok_nhn": gok,
        "end_depth": end_depth,
        "x": x,
        "y": y,
        "crs_epsg": epsg,
        "coord_source": "PDF" if x is not None else None,
        "layers": [
            {
                "top_depth": o,
                "bottom_depth": u,
                "description_raw": art,
                "soil_class": art,
                "confidence": 1.0,
                "issues": [],
                "provenance": [{"page": 0, "method": "test", "bbox": None}],
            }
            for o, u, art in schichten
        ],
        "groundwater": [{"depth": t} for t in (gw or [])],
        "groundwater_status": None,
        "issues": [],
        "provenance": [{"page": 0}],
    }


def _projekt(*bohrungen: dict) -> tuple[list[dict], pj.Projekt]:
    docs = [{
        "document": {"file": "test.pdf", "sha256": "0" * 64, "parser_version": "test", "pages": 1},
        "boreholes": list(bohrungen),
        "soundings": {},
    }]
    return docs, pj.neues_projekt(docs, "test")


def _befunde(docs: list[dict], p: pj.Projekt, code: str = "B 1") -> list[dict]:
    zeile = next(z for z in pb.pruefen(docs, p) if z["code"] == code)
    return zeile["befunde"]


def test_reihenfolge_ausgeloest_und_unter_schwelle():
    # Unterkante == Oberkante und Unterkante < Oberkante -> Warnung
    docs, p = _projekt(_bohrung(schichten=[(0.0, 2.0, "Sand"), (2.0, 2.0, "Schluff"), (2.0, 5.0, "Kies")]))
    b = _befunde(docs, p)
    rf = [f for f in b if f["regel"] == "reihenfolge"]
    assert len(rf) == 1 and rf[0]["stufe"] == "warnung" and rf[0]["schicht"] == 1
    assert "2,00 m" in rf[0]["text"]

    # Nicht nach Oberkante sortiert (zweite Schicht beginnt vor der ersten) -> Warnung
    docs2, p2 = _projekt(_bohrung(schichten=[(1.0, 5.0, "Kies"), (0.0, 1.0, "Sand")]))
    rf2 = [f for f in _befunde(docs2, p2) if f["regel"] == "reihenfolge"]
    assert len(rf2) == 1 and rf2[0]["stufe"] == "warnung" and rf2[0]["schicht"] == 1

    # Korrekte Reihenfolge -> kein Befund
    docs_ok, p_ok = _projekt(_bohrung(schichten=[(0.0, 2.0, "Sand"), (2.0, 5.0, "Kies")]))
    assert _befunde(docs_ok, p_ok) == []


def test_luecke_und_ueberlappung_ausgeloest_und_knapp_unter_schwelle():
    # Luecke 0,02 m (> 0,01 m) -> Warnung
    docs, p = _projekt(_bohrung(schichten=[(0.0, 1.0, "Sand"), (1.02, 5.0, "Kies")]))
    b = _befunde(docs, p)
    assert len(b) == 1 and b[0]["regel"] == "luecke" and b[0]["stufe"] == "warnung" and b[0]["schicht"] == 1
    assert "0,02 m" in b[0]["text"] and "1,00 m" in b[0]["text"] and "1,02 m" in b[0]["text"]

    # Knapp an/unter der Schwelle (genau 0,01 m) -> keine Warnung
    docs_ok, p_ok = _projekt(_bohrung(schichten=[(0.0, 1.0, "Sand"), (1.01, 5.0, "Kies")]))
    assert _befunde(docs_ok, p_ok) == []

    # Ueberlappung 0,02 m (> 0,01 m) -> Warnung
    docs_u, p_u = _projekt(_bohrung(schichten=[(0.0, 1.02, "Sand"), (1.0, 5.0, "Kies")]))
    bu = _befunde(docs_u, p_u)
    assert len(bu) == 1 and bu[0]["regel"] == "ueberlappung" and bu[0]["stufe"] == "warnung" and bu[0]["schicht"] == 1
    assert "0,02 m" in bu[0]["text"] and "1,00 m" in bu[0]["text"] and "1,02 m" in bu[0]["text"]

    # Ueberlappung genau 0,01 m -> keine Warnung
    docs_u_ok, p_u_ok = _projekt(_bohrung(schichten=[(0.0, 1.01, "Sand"), (1.0, 5.0, "Kies")]))
    assert _befunde(docs_u_ok, p_u_ok) == []


def test_beginn_ausgeloest_und_knapp_unter_schwelle():
    # Erste Schicht beginnt bei 0,06 m (> 0,05 m) -> Hinweis
    docs, p = _projekt(_bohrung(schichten=[(0.06, 5.0, "Sand")]))
    b = _befunde(docs, p)
    assert len(b) == 1 and b[0]["regel"] == "beginn" and b[0]["stufe"] == "hinweis" and b[0]["schicht"] == 0
    assert "0,06 m" in b[0]["text"]

    # Knapp an/unter der Schwelle (0,05 m) -> kein Hinweis
    docs_ok, p_ok = _projekt(_bohrung(schichten=[(0.05, 5.0, "Sand")]))
    assert _befunde(docs_ok, p_ok) == []


def test_endteufe_ausgeloest_knapp_unter_schwelle_und_ohne_angabe():
    # Abweichung 0,11 m (> 0,1 m) -> Warnung
    docs, p = _projekt(_bohrung(schichten=[(0.0, 4.89, "Sand")], end_depth=5.0))
    b = _befunde(docs, p)
    assert len(b) == 1 and b[0]["regel"] == "endteufe" and b[0]["stufe"] == "warnung" and b[0]["schicht"] is None
    assert "5,00 m" in b[0]["text"] and "0,11 m" in b[0]["text"] and "4,89 m" in b[0]["text"]

    # Knapp an/unter der Schwelle (0,10 m) -> keine Warnung
    docs_ok, p_ok = _projekt(_bohrung(schichten=[(0.0, 4.9, "Sand")], end_depth=5.0))
    assert _befunde(docs_ok, p_ok) == []

    # Keine Endteufe angegeben -> nichts
    docs_leer, p_leer = _projekt(_bohrung(schichten=[(0.0, 3.0, "Sand")], end_depth=None))
    assert _befunde(docs_leer, p_leer) == []


def test_duenn_ausgeloest_und_knapp_ueber_schwelle():
    # Schicht 0,04 m (< 0,05 m) -> Hinweis
    docs, p = _projekt(_bohrung(schichten=[(0.0, 1.0, "Sand"), (1.0, 1.04, "Schluff"), (1.04, 5.0, "Kies")]))
    b = _befunde(docs, p)
    assert len(b) == 1 and b[0]["regel"] == "duenn" and b[0]["stufe"] == "hinweis" and b[0]["schicht"] == 1
    assert "0,04 m" in b[0]["text"]

    # Genau 0,05 m -> kein Hinweis
    docs_ok, p_ok = _projekt(_bohrung(schichten=[(0.0, 1.0, "Sand"), (1.0, 1.05, "Schluff"), (1.05, 5.0, "Kies")]))
    assert _befunde(docs_ok, p_ok) == []


def test_grundwasser_ausgeloest_und_im_bereich():
    # Tiefer als Endteufe (5,05 m > 5,00 m) und ueber GOK (-0,10 m < 0 m) -> Warnungen
    docs, p = _projekt(_bohrung(gw=[-0.1, 5.05], end_depth=5.0))
    b = _befunde(docs, p)
    assert len(b) == 2 and all(f["regel"] == "grundwasser" and f["stufe"] == "warnung" and f["schicht"] is None for f in b)
    assert "-0,10 m" in b[0]["text"] and "5,05 m" in b[1]["text"] and "5,00 m" in b[1]["text"]

    # Genau an GOK (0,0 m) und genau bei Endteufe (5,0 m) -> keine Warnung
    docs_ok, p_ok = _projekt(_bohrung(gw=[0.0, 5.0], end_depth=5.0))
    assert _befunde(docs_ok, p_ok) == []


def test_gok_fehlt_nennt_gok_quelle():
    docs, p = _projekt(_bohrung(gok=None))
    zeile = pb.pruefen(docs, p)[0]
    assert zeile["gok_quelle"] == ""
    b = zeile["befunde"]
    assert len(b) == 1 and b[0]["regel"] == "gok_fehlt" and b[0]["stufe"] == "hinweis" and b[0]["schicht"] is None
    assert "gok_quelle" in b[0]["text"] and "fehlt" in b[0]["text"]

    # Mit GOK -> kein Befund gok_fehlt, Quelle ist PDF
    docs_ok, p_ok = _projekt(_bohrung(gok=42.5))
    zeile_ok = pb.pruefen(docs_ok, p_ok)[0]
    assert zeile_ok["gok_quelle"] == "PDF" and zeile_ok["befunde"] == []


def test_gok_nachbarn_ausgeloest_und_unter_schwelle():
    # 3 Bohrungen im Umkreis von 200 m, gleiche EPSG: B 1 weicht um 3,10 m (> 3 m) vom Median (50,00 m) ab
    docs, p = _projekt(
        _bohrung("B 1", gok=53.1, x=500000.0, y=5700000.0, epsg=25832),
        _bohrung("B 2", gok=50.0, x=500100.0, y=5700000.0, epsg=25832),
        _bohrung("B 3", gok=50.0, x=500000.0, y=5700150.0, epsg=25832),
    )
    b = _befunde(docs, p, "B 1")
    assert len(b) == 1 and b[0]["regel"] == "gok_nachbarn" and b[0]["stufe"] == "hinweis" and b[0]["schicht"] is None
    assert "3,10 m" in b[0]["text"] and "50,00 m NHN" in b[0]["text"]
    assert "B 2" in b[0]["text"] and "B 3" in b[0]["text"]

    # Knapp an/unter der Schwelle (3,00 m Abweichung) -> kein Hinweis
    docs_ok, p_ok = _projekt(
        _bohrung("B 1", gok=53.0, x=500000.0, y=5700000.0, epsg=25832),
        _bohrung("B 2", gok=50.0, x=500100.0, y=5700000.0, epsg=25832),
        _bohrung("B 3", gok=50.0, x=500000.0, y=5700150.0, epsg=25832),
    )
    assert _befunde(docs_ok, p_ok, "B 1") == []

    # Weniger als 2 Nachbarn im 200-m-Umkreis (B 3 ist 201 m entfernt) oder anderes EPSG -> kein Hinweis
    docs_weit, p_weit = _projekt(
        _bohrung("B 1", gok=60.0, x=500000.0, y=5700000.0, epsg=25832),
        _bohrung("B 2", gok=50.0, x=500100.0, y=5700000.0, epsg=25832),
        _bohrung("B 3", gok=50.0, x=500201.0, y=5700000.0, epsg=25832),
        _bohrung("B 4", gok=50.0, x=500050.0, y=5700000.0, epsg=25833),
    )
    assert _befunde(docs_weit, p_weit, "B 1") == []


def test_nutzer_korrektur_aendert_ergebnis_und_bericht_veraendert_daten_nicht(tmp_path):
    # Ausgangszustand: Luecke zwischen Schicht 1 (bis 1,80 m) und Schicht 2 (ab 2,00 m) sowie Endteufe-Abweichung
    docs, p = _projekt(_bohrung("B 1", schichten=[(0.0, 1.8, "Sand"), (2.0, 4.5, "Kies")], end_depth=5.0))
    docs_vorher = copy.deepcopy(docs)
    p_vorher = copy.deepcopy(p)

    bericht1 = pb.pruefen(docs, p)
    regeln1 = {f["regel"] for f in bericht1[0]["befunde"]}
    assert regeln1 == {"luecke", "endteufe"}
    # Der Bericht veraendert weder docs noch Projekt
    assert docs == docs_vorher and p == p_vorher

    # Korrektur des Nutzers ueber pj.aendern: Unterkante Schicht 0 auf 2,00 m, Unterkante Schicht 1 auf 5,00 m
    pj.aendern(docs, p, {"op": "schicht", "id": "0:0", "k": 0, "feld": "unten", "wert": 2.0})
    pj.aendern(docs, p, {"op": "schicht", "id": "0:0", "k": 1, "feld": "unten", "wert": 5.0})
    assert pb.pruefen(docs, p)[0]["befunde"] == []

    # Oberkante Schicht 0 auf 0,10 m setzen -> loest "beginn" aus
    pj.aendern(docs, p, {"op": "schicht", "id": "0:0", "k": 0, "feld": "oben", "wert": 0.1})
    regeln2 = [f["regel"] for f in pb.pruefen(docs, p)[0]["befunde"]]
    assert regeln2 == ["beginn"]

    # Server liefert plausibilitaet im Zustand neben pruefstand
    ap = Arbeitsplatz(tmp_path)
    sig = ap.anlegen(docs_vorher)
    z = ap.zustand(sig)
    assert "plausibilitaet" in z and len(z["plausibilitaet"]) == 1
    assert {f["regel"] for f in z["plausibilitaet"][0]["befunde"]} == {"luecke", "endteufe"}
