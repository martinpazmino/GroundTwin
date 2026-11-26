"""Regeln aus den Blindrunden 5 und 6 (Issues #54, #55, docs/16 T6-T14, W7): ohne Netz und ohne echte Gutachten.

Die Stressfaelle s31-s42 werden im Test erzeugt (stress_cases.py, mit Wahrheit) und mit demselben Werkzeug bewertet
wie die Regression (benchmark/eval_real.score). Jede Regel zeigt, dass sie greift: Regel aus -> Fall faellt.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("pymupdf")

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "services" / "extractor", ROOT / "benchmark"):
    sys.path.insert(0, str(p))

import prototyp_v4 as v4  # noqa: E402
import stress_cases as sc  # noqa: E402
from eval_real import norm, score  # noqa: E402

FAELLE = ["s31_projektnummer", "s32_stationscode", "s33_schnitt_doppellabel", "s34_unterkante_text_darueber",
          "s35_gw_label_text", "s36_doppel_anderer_code", "s37_ausbauplan", "s38_code_zusatz",
          "s39_kein_wasser", "s40_gw_label_nn", "s41_legende_kuerzel",
          "s42_doppellabel_ohne_linie"]


@pytest.fixture(scope="module")
def stress(tmp_path_factory) -> Path:
    ordner = tmp_path_factory.mktemp("stress54")
    sc.build(ordner)
    return ordner


@pytest.fixture
def regeln():
    alt = dict(v4.RULES)
    yield v4.RULES
    v4.RULES.clear()
    v4.RULES.update(alt)


def bewerten(ordner: Path, fall: str) -> dict:
    wahrheit = json.loads((ordner / f"{fall}.json").read_text(encoding="utf-8"))
    bhs, _ = v4.extract(ordner / f"{fall}.pdf")
    found = {norm(b.code): {"gok": b.gok, "bottoms": [ly.bottom for ly in b.layers],
                            "soils": [(ly.top, ly.bottom, ly.soil) for ly in b.layers], "gw": b.gw_depths} for b in bhs}
    return score(wahrheit, found)


def voll(bruch: str) -> bool:
    a, b = bruch.split("/")
    return a == b


@pytest.mark.parametrize("fall", FAELLE)
def test_fall_ganz_ohne_falsche(stress, fall):
    e = bewerten(stress, fall)
    assert e["falsche Bohrungen"] == 0 and e["falsche Grenzen"] == 0 and e["falsches GW"] == 0, e
    for k in ("Bohrungen", "Grenzen", "Bodenart", "GOK", "GW"):
        assert voll(e[k]), (k, e)


SCHUTZ = [
    ("kein_schriftfeld_code", "s31_projektnummer", "falsche Bohrungen"),   # 'Projekt-Nr.: B 231411'
    ("station_heads", "s32_stationscode", "Bohrungen"),                    # 'SB-0+550-N3'
    ("gok_unter_kopf", "s33_schnitt_doppellabel", "GOK"),                  # '45.20 m' unter dem Kopf
    ("doppel_labels", "s33_schnitt_doppellabel", "falsche Grenzen"),       # Linie ohne 'Tiefe (Hoehe)'
    ("gw_blaue_labels", "s33_schnitt_doppellabel", "GW"),                  # blaues Label, Dreieck aus Einzelstrichen
    ("top_null_gedruckt", "s34_unterkante_text_darueber", "Bodenart"),     # Beschreibung ueber dem Label
    ("gw_label_text", "s35_gw_label_text", "falsches GW"),                  # 'GW 2.40m' gilt, nicht das Symbol
    ("doppel_anderer_code", "s36_doppel_anderer_code", "falsche Bohrungen"),  # 'B 4' und 'B 4a' = eine Bohrung
    ("ausbau_kein_profil", "s37_ausbauplan", "falsche Bohrungen"),          # Ausbauplan GWM (#55)
    ("code_zusatz", "s38_code_zusatz", "Bohrungen"),                         # 'BS 105A', 'BS 22.1' (#55)
    ("gw_label_text", "s40_gw_label_nn", "falsches GW"),                     # '2,40 GW' + 'NN+42,80m' (#55)
    ("legende_kuerzel", "s41_legende_kuerzel", "Bohrungen"),                # 'BK A/1', 'S B2' aus der Legende (#54)
    ("doppel_labels", "s42_doppellabel_ohne_linie", "Grenzen"),             # Doppellabel ohne Linie (#54)
]


@pytest.mark.parametrize("regel,fall,merkmal", SCHUTZ)
def test_regel_aus_fall_faellt(stress, regeln, regel, fall, merkmal):
    regeln[regel] = False
    e = bewerten(stress, fall)
    if merkmal.startswith("falsch"):
        assert e[merkmal] > 0, (regel, e)
    else:
        assert not voll(e[merkmal]), (regel, e)
