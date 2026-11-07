"""LoD2-Gebaeude der Laender (services/geodaten/geodaten/gebaeude.py): Kacheln, CityGML lesen, Ausschnitt, Rueckfall.

Die Dienste ersetzt eine Attrappe mit synthetischem AdV-CityGML (Waende mit Loch, Dach, Boden, Abschlussflaeche,
Gebaeudeteil). Ein Test holt eine echte Berliner Kachel (ohne Netz: uebersprungen).
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "services" / "geodaten"))
from geodaten import gebaeude as gb  # noqa: E402
from geodaten.bohrdaten import DienstFehler  # noqa: E402

KOPF = ('<?xml version="1.0" encoding="UTF-8"?><core:CityModel xmlns:core="http://www.opengis.net/citygml/1.0" '
        'xmlns:bldg="http://www.opengis.net/citygml/building/1.0" xmlns:gml="http://www.opengis.net/gml" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">')


def ring(punkte):
    return " ".join(f"{x} {y} {z}" for x, y, z in punkte + punkte[:1])         # geschlossen wie im AdV-Profil


def flaeche(art, aussen, loch=None):
    innen = f'<gml:interior><gml:LinearRing><gml:posList srsDimension="3">{ring(loch)}</gml:posList></gml:LinearRing></gml:interior>' if loch else ""
    return (f'<bldg:boundedBy><bldg:{art}><bldg:lod2MultiSurface><gml:MultiSurface><gml:surfaceMember><gml:Polygon>'
            f'<gml:exterior><gml:LinearRing><gml:posList srsDimension="3">{ring(aussen)}</gml:posList></gml:LinearRing></gml:exterior>'
            f'{innen}</gml:Polygon></gml:surfaceMember></gml:MultiSurface></bldg:lod2MultiSurface></bldg:{art}></bldg:boundedBy>')


def haus(gid, x, y, z=35.0, h=8.0, teil=True):
    p = [(x, y), (x + 10, y), (x + 10, y + 8), (x, y + 8)]
    w = [[(*p[k], z), (*p[(k + 1) % 4], z), (*p[(k + 1) % 4], z + h), (*p[k], z + h)] for k in range(4)]
    inhalt = (flaeche("WallSurface", w[0], loch=[(x + 2, y, z + 2), (x + 4, y, z + 2), (x + 4, y, z + 4), (x + 2, y, z + 4)])
              + "".join(flaeche("WallSurface", r) for r in w[1:])
              + flaeche("RoofSurface", [(*q, z + h) for q in p]) + flaeche("GroundSurface", [(*q, z) for q in reversed(p)])
              + flaeche("ClosureSurface", w[1]))
    anbau = ""
    if teil:                                                         # Gebaeudeteil mit eigenem Dach
        anbau = ('<bldg:consistsOfBuildingPart><bldg:BuildingPart gml:id="' + gid + '_T">'
                 + flaeche("RoofSurface", [(x + 10, y, z + 3), (x + 14, y, z + 3), (x + 14, y + 8, z + 3), (x + 10, y + 8, z + 3)])
                 + "</bldg:BuildingPart></bldg:consistsOfBuildingPart>")
    return (f'<core:cityObjectMember><bldg:Building gml:id="{gid}"><bldg:function>31001_1000</bldg:function>'
            f'<bldg:roofType>1000</bldg:roofType><bldg:measuredHeight uom="urn:adv:uom:m">{h}</bldg:measuredHeight>'
            f'{inhalt}{anbau}</bldg:Building></core:cityObjectMember>')


def kachel(*haeuser) -> bytes:
    return (KOPF + "".join(haeuser) + "</core:CityModel>").encode("utf-8")


def gezippt(daten: bytes, name="LoD2_33_394_5818_1_BE.xml") -> bytes:
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w") as z:
        z.writestr(name, daten)
        z.writestr("lod2_meta.html", "<html></html>")
    return puffer.getvalue()


def attrappe(kacheln: dict[str, bytes], aufrufe: list | None = None):
    def holer(url, zeit):
        if aufrufe is not None:
            aufrufe.append(url)
        for teil, daten in kacheln.items():
            if teil in url:
                if isinstance(daten, Exception):
                    raise daten
                return daten
        raise gb.KeineKachel("Kachel nicht vorhanden")
    return holer


def test_kacheln_und_ausschnitt():
    assert gb.kacheln(394670, 5818238, 395010, 5818569) == [(394, 5818), (395, 5818)]
    assert gb.kacheln(394000, 5818000, 395000, 5819000) == [(394, 5818)]                 # rechter Rand ausschliesslich
    assert gb.ausschnitt([(394774.3, 5818338.1), (394909.3, 5818442.5)], 100) == (394674, 5818238, 395010, 5818543)


def test_citygml_lesen():
    (b,) = list(gb.lesen(gezippt(kachel(haus("DEBE_1", 394800, 5818300))), "zip"))
    arten = [f["art"] for f in b["flaechen"]]
    assert arten.count("Wand") == 4 and arten.count("Dach") == 2 and arten.count("Boden") == 1   # Abschluss weg, Teil dabei
    assert (b["id"], b["funktion"], b["dachform"], b["hoehe"]) == ("DEBE_1", "31001_1000", "1000", 8.0)
    wand = b["flaechen"][0]
    assert len(wand["ring"]) == 4 and wand["ring"][0] != wand["ring"][-1] and len(wand["loecher"]) == 1


def test_abruf_mit_rueckfall_ausschnitt_und_lizenz():
    # Ausschnitt an der Grenze Berlin/Brandenburg (bei x = 406900): Mitte in Berlin, Kachel 407 nur bei Brandenburg
    aufrufe = []
    holer = attrappe({"LoD2_406_5818": gezippt(kachel(haus("DEBE_1", 406500, 5818200), haus("DEBE_WEIT", 406100, 5818900))),
                      "lod2_33407-5818": gezippt(kachel(haus("DEBB_1", 407000, 5818250, teil=False)), "lod2_33407-5818_geb.gml")},
                     aufrufe)
    geb, q = gb.abrufen(406300, 5818100, 407100, 5818400, 25833, holer=holer)
    assert sorted(b["id"] for b in geb) == ["DEBB_1", "DEBE_1"]                  # DEBE_WEIT liegt ausserhalb
    assert {b["id"]: b["dienst"] for b in geb} == {"DEBE_1": "BE-LOD2", "DEBB_1": "BB-LOD2"}
    assert [d["dienst"] for d in q["dienste"]] == ["BE-LOD2", "BB-LOD2"] and q["kacheln"] == 2 and q["ohne_kachel"] == []
    assert "GeoBasis-DE/LGB" in q["dienste"][1]["namensnennung"]
    assert sum("gdi.berlin.de" in u for u in aufrufe) == 2 and sum("geobasis-bb" in u for u in aufrufe) == 1


def test_mitten_in_berlin_nur_der_dienst_von_berlin():
    """Die Rechtecke beider Dienste decken Berlin; die Laendergrenzen nicht: Brandenburg wird nicht mehr gefragt."""
    aufrufe = []
    holer = attrappe({"LoD2_394_5818": gezippt(kachel(haus("DEBE_1", 394800, 5818300)))}, aufrufe)
    geb, q = gb.abrufen(394670, 5818238, 395010, 5818569, 25833, holer=holer)
    assert [b["id"] for b in geb] == ["DEBE_1"] and q["ohne_kachel"] == ["395/5818"]
    assert aufrufe and all("gdi.berlin.de" in u for u in aufrufe)


def test_zonenkennung_und_fehler():
    holer = attrappe({"LoD2_394_5818": gezippt(kachel(haus("DEBE_1", 394800, 5818300)))})
    geb, q = gb.abrufen(33394700, 5818250, 33394950, 5818500, 5650, holer=holer)
    assert geb[0]["flaechen"][0]["ring"][0][0] == pytest.approx(33394800.0) and q["ausschnitt"][0] == 33394700
    with pytest.raises(DienstFehler, match="keine Antwort"):
        gb.abrufen(394700, 5818250, 394950, 5818500, 25833, holer=attrappe({"LoD2_394": DienstFehler("keine Antwort in 120 s"),
                                                                            "lod2_33394": DienstFehler("keine Antwort in 120 s")}))
    leer, q = gb.abrufen(394700, 5818250, 394950, 5818500, 25833, holer=attrappe({}))
    assert leer == [] and q["ohne_kachel"] == ["394/5818"]
    with pytest.raises(ValueError, match="kein LoD2-Dienst für diesen Ort .angebunden: Berlin, Brandenburg, "
                                         "Niedersachsen, Nordrhein-Westfalen; im Portal des Landes: .*https://"):
        gb.abrufen(705000, 5300000, 705300, 5300300, 25832, holer=attrappe({}))            # Bayern: Portal genannt
    with pytest.raises(ValueError, match="Kacheln"):
        gb.abrufen(390000, 5815000, 394500, 5819500, 25833, holer=attrappe({}))           # 5 x 5 km


def test_kaputte_kachel_wird_gemeldet():
    with pytest.raises(DienstFehler, match="kein ZIP"):
        list(gb.lesen(b"PK kaputt", "zip"))
    with pytest.raises(DienstFehler, match="nicht lesbar"):
        list(gb.lesen(b"<core:CityModel", "gml"))


def test_live_berlin():
    """Echte Kachel 394/5818 (Berliner Beispiel): Gebaeude mit Waenden und Daechern ueber dem Boden."""
    try:
        geb, q = gb.abrufen(394700, 5818250, 394950, 5818500, 25833)
    except DienstFehler as err:
        pytest.skip(f"Dienst nicht erreichbar ({err})")
    assert q["dienste"][0]["dienst"] == "BE-LOD2" and len(geb) > 10
    ganz = 0
    for b in geb:                                   # manche Bauwerke sind nur Waende (z. B. Mauern, Funktion 53001_1800)
        boden = [p[2] for f in b["flaechen"] if f["art"] == "Boden" for p in f["ring"]]
        dach = [p[2] for f in b["flaechen"] if f["art"] == "Dach" for p in f["ring"]]
        if boden and dach:
            ganz += 1
            assert min(dach) > min(boden) and 20 < min(boden) < 60
    assert ganz > 0.7 * len(geb)
