"""Issue #18: gescannte Seiten ueber die OCR in den Zusatzstufen (Kennwerte, Homogenbereiche, Labor). Die OCR selbst
wird hier durch feste Woerter ersetzt (kein OCR-Paket noetig); geprueft wird, dass die Regeln auf OCR-Text greifen,
die Herkunft 'OCR' markiert wird und verlorene Umlaute ('gema', 'Kohasion') nicht stoeren."""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "extractor"))
import prototyp_v4  # noqa: E402
import homogenbereiche_text as H  # noqa: E402
import kennwerte as K  # noqa: E402
import labor as L  # noqa: E402
import textebene as T  # noqa: E402


def _scan(pfad, seiten):
    """PDF aus Bildseiten (ohne Textebene); seiten: Liste von Zeilenlisten [(x, y, text)] fuer die falsche OCR."""
    doc = pymupdf.open()
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 40, 40), False)
    pix.clear_with(255)
    for _ in seiten:
        doc.new_page().insert_image(pymupdf.Rect(0, 0, 595, 842), pixmap=pix)
    doc.save(pfad)


@pytest.fixture()
def falsche_ocr(monkeypatch):
    seiten: list[list[tuple[float, float, str]]] = []

    def ocr_words(page, dpi=None, min_conf=0.5):
        out = []
        for i, (x, y, text) in enumerate(seiten[page.number]):
            pos = x
            for tok in text.split():
                out.append((pymupdf.Rect(pos, y, pos + 6 * len(tok), y + 9), tok, 100000 + i, 0))
                pos += 6 * len(tok) + 4
        return out
    # textebene holt ocr_words aus sys.modules['prototyp_v4'] - das kann ein anderes Modulobjekt sein (ui.pipeline laedt
    # den Extraktor selbst): beide ersetzen
    for mod in {id(prototyp_v4): prototyp_v4, id(sys.modules["prototyp_v4"]): sys.modules["prototyp_v4"]}.values():
        monkeypatch.setattr(mod, "ocr_words", ocr_words)
    return seiten


def test_scan_erkannt_und_zeilen_aus_der_ocr(tmp_path, falsche_ocr):
    falsche_ocr.append([(60, 60, "Homogenbereich B: gewachsener Baugrund"), (60, 80, "Bodengruppe gema DIN 18196: SU*")])
    _scan(tmp_path / "s.pdf", falsche_ocr)
    s = T.lesen(pymupdf.open(tmp_path / "s.pdf")[0])
    assert s.quelle == "OCR" and [t for _, t in s.zeilen][0] == "Homogenbereich B: gewachsener Baugrund"
    (e,) = H.lesen(tmp_path / "s.pdf")
    assert (e["bereich"], e["name"], e["bodengruppen"], e["quelle"]) == ("B", "gewachsener Baugrund", ["SU*"], "OCR")
    assert any("OCR" in h for h in e["hinweise"])
    assert H.lesen(tmp_path / "s.pdf", ocr=False) == []                       # ohne OCR: stumm, nichts erfunden


def test_kennwerte_aus_gescannter_tabelle(tmp_path, falsche_ocr):
    zeilen = [(170, 90, "Wichte"), (240, 90, "Auftrieb"), (310, 90, "Reibungswinkel"), (400, 90, "Kohasion"),
              (470, 90, "Steifemodul"), (470, 100, "MN/m?")]
    for y, bez, werte in ((140, "Oberboden", ("16 - 18", "6-8")),               # OCR: leere Zellen ohne '-'
                          (175, "Sand, schluffig", ("18", "10", "32,5", "0", "35"))):
        zeilen.append((70, y, bez))
        zeilen += [(x, y, w) for x, w in zip((175, 245, 320, 410, 475), werte)]
    falsche_ocr.append(zeilen)
    _scan(tmp_path / "k.pdf", falsche_ocr)
    z = K.lesen(tmp_path / "k.pdf")
    assert [e["bezeichnung"] for e in z] == ["Oberboden", "Sand, schluffig"]
    assert (z[0]["werte"]["wichte"]["min"], z[0]["werte"]["wichte"]["max"]) == (16.0, 18.0)
    assert z[1]["werte"]["kohaesion"]["min"] == 0.0 and z[1]["werte"]["steifemodul"]["max"] == 35.0
    assert all(e["quelle"] == "OCR" and any("OCR" in h for h in e["hinweise"]) for e in z)


def test_laborblatt_gescannt_ohne_umlaute(tmp_path, falsche_ocr):
    falsche_ocr.append([(60, 60, "Fliess- und Ausrollgrenze DIN EN ISO 17892-12"), (60, 80, "Entnahmestelle: BS 5"),
                        (60, 95, "Tiefe: 2,5 - 3,5"), (60, 110, "Plastizitatszahl IP = 10.2 %"),
                        (60, 125, "Konsistenzzahl IC = 0.58")])
    _scan(tmp_path / "l.pdf", falsche_ocr)
    (p,) = L.lesen(tmp_path / "l.pdf")
    assert p["werte"] == {"plastizitaetszahl": 10.2, "konsistenzzahl": 0.58} and p["quelle"] == "OCR"
