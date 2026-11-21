"""Stufe Sondierungen (services/extractor/sondierungen.py, Issue #27, docs/05 §5): ohne Netz und ohne echte Gutachten.

Die Faelle werden im Test erzeugt: die acht Stressfaelle (stress_sondierungen.py, mit Wahrheit) und eigene Proben in
einem anderen Layout (Achse 0-40, Kurve als Polylinie oder als Einzelstriche). Bewertet wird mit demselben Werkzeug
wie die Messung (benchmark/sondierungen_eval.py). Jede Pruefung zeigt auch, dass sie greift ("Regel aus -> Fall faellt").
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pytest

pymupdf = pytest.importorskip("pymupdf")

REPO = Path(__file__).resolve().parents[1]
for p in (REPO / "services" / "extractor", REPO / "benchmark"):
    sys.path.insert(0, str(p))

import sondierungen  # noqa: E402
import sondierungen_eval as ev  # noqa: E402
import stress_sondierungen  # noqa: E402


@pytest.fixture(scope="module")
def stress(tmp_path_factory) -> Path:
    ordner = tmp_path_factory.mktemp("stress_sondierungen")
    stress_sondierungen.build(ordner)
    return ordner


@pytest.fixture
def regeln():
    """Schalter nach jedem Test zuruecksetzen (Ablation im Test)."""
    alt = dict(sondierungen.REGELN)
    yield sondierungen.REGELN
    sondierungen.REGELN.clear()
    sondierungen.REGELN.update(alt)


def bewerten(pdf: Path, wahrheit: dict) -> dict:
    preds, seiten, ms = ev.extrahiere_sondierungen(sondierungen, pdf, ocr=False)
    ergebnis, _ = ev._bewerte_fall(wahrheit, preds, seiten, ms)
    return ergebnis


def anteil(bruch: str) -> tuple[int, int]:
    a, b = bruch.split("/")
    return int(a), int(b)


FAELLE = ["s01_dph_diagramm", "s02_dph_tabelle", "s03_dph_laengsschnitt", "s04_cpt_linear_log",
          "s05_zensiert", "s06_zweiseitig", "s07_falle_bohrprofil_lineal", "s08_falle_labortabelle"]


@pytest.mark.parametrize("fall", FAELLE)
def test_stressfall_ganz_und_ohne_falsche_werte(stress, fall):
    wahrheit = json.loads((stress / f"{fall}.json").read_text(encoding="utf-8"))
    e = bewerten(stress / f"{fall}.pdf", wahrheit)
    assert e["falsche_sondierungen"] == 0 and e["falsche_werte"] == 0, e
    for k in ("gefunden", "code_richtig", "endtiefe_5cm", "dph_schritt_1", "cpt_punkte"):
        a, b = anteil(e[k])
        assert a == b, (k, e)


# Ablation (docs/05 §5.4): welche Regel welchen Fall schuetzt; ohne sie faellt der Fall.
SCHUTZ = [
    ("tabelle_kopf_schlagzahl", "s08_falle_labortabelle", "falsche_sondierungen"),   # Laborwerte sind keine N10
    ("tabelle_kopf_schlagzahl", "s01_dph_diagramm", "falsche_werte"),
    ("achse_arithmetisch_und_rahmen", "s06_zweiseitig", "dph_schritt_1"),
    ("mehrseitig_verbinden", "s06_zweiseitig", "falsche_werte"),               # Fortsetzung als eigene Sondierung
    ("laengsschnitt_hoehenmassstab", "s03_dph_laengsschnitt", "gefunden"),        # Achse je Seite neu
]


@pytest.mark.parametrize("regel,fall,merkmal", SCHUTZ)
def test_regel_aus_fall_faellt(stress, regeln, regel, fall, merkmal):
    wahrheit = json.loads((stress / f"{fall}.json").read_text(encoding="utf-8"))
    regeln[regel] = False
    e = bewerten(stress / f"{fall}.pdf", wahrheit)
    if merkmal in ("falsche_sondierungen", "falsche_werte"):
        assert e[merkmal] > 0, (regel, fall, e)
    else:
        a, b = anteil(e[merkmal])
        assert a < b, (regel, fall, e)


def probe(pfad: Path, werte: list[int], einzelstriche: bool = False, titel: str = "DPH 4", nmax: int = 40,
          schritt: int = 5, mpt: float = 56.693) -> Path:
    """Eigenes Layout (nicht aus stress_sondierungen): Rahmen, Achse oben, Tiefenlineal links, Treppenkurve."""
    doc = pymupdf.open()
    p = doc.new_page(width=595, height=842)
    x0, y0, breite = 120, 140, 300
    h = len(werte) * 0.1 * mpt
    p.insert_text((x0, y0 - 45), titel, fontsize=12)
    p.draw_rect(pymupdf.Rect(x0, y0, x0 + breite, y0 + h), color=(0, 0, 0), width=0.8)
    for n in range(0, nmax + 1, schritt):
        x = x0 + n / nmax * breite
        p.insert_text((x - 4, y0 - 6), str(n), fontsize=7)
        p.draw_line((x, y0), (x, y0 + h), color=(.7, .7, .7), width=0.3)
    for m in range(0, int(len(werte) * 0.1) + 1):
        p.insert_text((x0 - 14, y0 + m * mpt + 3), str(m), fontsize=7)
    pts = []
    for i, n in enumerate(werte):
        xa = x0 + n / nmax * breite
        pts += [(xa, y0 + i * 0.1 * mpt), (xa, y0 + (i + 1) * 0.1 * mpt)]
    if einzelstriche:
        for a, b in zip(pts, pts[1:]):
            p.draw_line(a, b, color=(0, 0, 0), width=1.2)
    else:
        p.draw_polyline(pts, color=(0, 0, 0), width=1.2)
    doc.save(pfad)
    return pfad


def gelesen(pdf: Path) -> list[dict]:
    return sondierungen.lesen(pdf, ocr=False)


@pytest.mark.parametrize("variante", [dict(), dict(einzelstriche=True), dict(nmax=50, schritt=10),
                                      dict(titel="Rammsondierung DPM 2"), dict(mpt=28.35)])
def test_eigenes_layout_alle_stufen_ohne_falsche(tmp_path, variante):
    werte = [random.Random(i).randint(1, 35) for i in range(40)]
    out = gelesen(probe(tmp_path / "p.pdf", werte, **variante))
    assert len(out) == 1, out
    s = out[0]
    gef = [v[2] for v in s["werte"]]
    assert len(gef) == len(werte)
    assert all(abs(g - w) <= 1 for g, w in zip(gef, werte)), list(zip(gef, werte))
    assert s["endtiefe"] == pytest.approx(len(werte) * 0.1)


def test_einzelstriche_brauchen_die_regel(tmp_path, regeln):
    """Manche CAD-Exporte zeichnen die Treppe als Einzelstriche: ohne Verkettung keine Sondierung (aber nie falsch)."""
    werte = [random.Random(i).randint(1, 35) for i in range(40)]
    pdf = probe(tmp_path / "e.pdf", werte, einzelstriche=True)
    regeln["einzelstriche_verketten"] = False
    out = gelesen(pdf)
    assert all(not s["werte"] for s in out), "ohne Regel duerfen keine Werte entstehen"
    regeln["einzelstriche_verketten"] = True
    assert len(gelesen(pdf)[0]["werte"]) == 40


def test_text_mit_tiefen_tabellen_ist_keine_sondierung(tmp_path):
    """Wasserstands- und Kennwerttabellen (Tiefen, Zahlen) im Bericht sind keine Sondierungen."""
    doc = pymupdf.open()
    p = doc.new_page()
    zeilen = ["Tabelle 2: Wasserstaende", "Aufschluss   Wasserstand [m u. GOK]   Wasserart",
              "KRB 1/20   3,74   Grundwasser", "KRB 2/20   3,61   Grundwasser",
              "Tabelle 6: Bodenkennwerte", "Tiefe [m]   Wichte   Reibungswinkel",
              "0,10   18   30", "0,20   19   32", "0,30   20   35", "0,40   20   35"]
    for i, z in enumerate(zeilen):
        p.insert_text((60, 80 + i * 16), z, fontsize=9)
    doc.save(tmp_path / "t.pdf")
    assert gelesen(tmp_path / "t.pdf") == []


def test_ausgabe_traegt_herkunft(tmp_path):
    werte = [random.Random(i).randint(1, 35) for i in range(30)]
    s = gelesen(probe(tmp_path / "h.pdf", werte))[0]
    for k in ("code", "art", "seite", "form", "werte", "endtiefe", "konfidenz", "hinweise", "beleg", "quelle"):
        assert k in s, k
    assert s["art"] == "DPH" and s["form"] == "diagramm" and s["quelle"] == "Text"
    assert 0 < s["konfidenz"] <= 1


def test_cpt_kurven_trennen_haelt_qc_und_fs_auseinander(stress, regeln):
    """Zwei Kurven je Diagramm (q_c, f_s): ohne Trennung nach Stil vermischt die Stufe sie (Fehler q_c > 10 %)."""
    wahrheit = json.loads((stress / "s04_cpt_linear_log.json").read_text(encoding="utf-8"))
    assert (bewerten(stress / "s04_cpt_linear_log.pdf", wahrheit)["cpt_qc_mittel_pct"] or 0) < 1
    regeln["cpt_kurven_trennen"] = False
    assert bewerten(stress / "s04_cpt_linear_log.pdf", wahrheit)["cpt_qc_mittel_pct"] > 10
