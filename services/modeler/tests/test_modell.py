"""Synthetische Faelle mit bekannter Wahrheit: Einheiten, Kontakte, Koerper, IFC."""
from __future__ import annotations

import math

import numpy as np
import pytest

from baugrundmodell import synthetisch as syn
from baugrundmodell.einheiten import (Abschnitt, Bohrung, ausrichten, bohrungen_aus_extraktion,
                                      einheiten_aus_vorgabe, korrelieren)
from baugrundmodell.flaechen import ZENSUR_MARGE, interpolieren
from baugrundmodell.ifc4x3 import prisma
from baugrundmodell.koerper import pruefen
from baugrundmodell.modell import bauen, bericht, ifc_schreiben


def modell(fall, **kw):
    docs = [syn.dokument(fall)]
    return bauen(docs, **kw), docs


def namen(m):
    return [e.name for e in m.einheiten]


def status(m, einheit):
    j = namen(m).index(einheit)
    return {b.code: ks[j].status for b, ks in zip(m.bohrungen, m.kontakte)}


def maechtigkeit_an(m, einheit, code):
    j, bi = namen(m).index(einheit), [b.code for b in m.bohrungen].index(code)
    return m.flaechen[j][bi] - m.flaechen[j + 1][bi]


@pytest.mark.parametrize("name", sorted(syn.FAELLE))
@pytest.mark.parametrize("methode", ["idw", "tps"])
def test_invarianten(name, methode):
    """Fuer jeden Fall: Kontakte exakt, Maechtigkeit >= 0, Koerper geschlossen, Volumen konsistent."""
    m, _ = modell(syn.FAELLE[name](), methode=methode)
    assert m.max_abweichung < 1e-6
    assert np.all(np.diff(m.flaechen, axis=0) <= 1e-9)
    assert np.all(m.flaechen >= m.basis - 1e-9)
    for k in m.koerper:
        assert k["pruefung"]["geschlossen"], k["name"]
        # Knoten auf mm gerundet: hoechstens 1 mm x Grundflaeche Unterschied
        assert k["pruefung"]["volumen"] == pytest.approx(k["volumen_m3"], abs=1e-3 * m.parameter["flaeche_m2"])
        assert k["volumen_m3"] >= 0


def test_tps_trifft_geneigte_ebenen():
    """Ebene Wahrheit: der Duennplatten-Spline (mit linearem Trend) gibt sie im ganzen Gebiet wieder."""
    fall = syn.geneigt()
    m, _ = modell(fall, methode="tps")
    assert namen(m) == ["Auffuellung", "Sand", "Geschiebemergel", "Ton"]
    x = m.punkte[:, 0] + m.ursprung[0] - syn.URSPRUNG[0]
    y = m.punkte[:, 1] + m.ursprung[1] - syn.URSPRUNG[1]
    wahr = [np.array([fall.gok(a, b) for a, b in zip(x, y)])] + \
           [np.array([uk(a, b) for a, b in zip(x, y)]) for _, uk in fall.einheiten[:-1]]
    for j, w in enumerate(wahr):
        assert np.abs(m.flaechen[j] - w).max() < 1e-3, j


def test_auskeilen():
    m, _ = modell(syn.auskeilen())
    assert namen(m) == ["Auffuellung", "Sand", "Torf", "Geschiebemergel", "Ton"]
    st = status(m, "Torf")
    assert {c for c, s in st.items() if s == "vorhanden"} == {"B1", "B4", "B7"}
    assert all(s == "fehlt" for c, s in st.items() if c not in {"B1", "B4", "B7"})
    for c in ("B2", "B3", "B5", "B6", "B8", "B9"):
        assert abs(maechtigkeit_an(m, "Torf", c)) < 1e-9
    assert maechtigkeit_an(m, "Torf", "B1") == pytest.approx(2.0, abs=0.01)


def test_linse_teilt_den_sand():
    """Kies nur in B5: die anderen Bohrungen haben einen durchgehenden Sand, der in Sand 1 / Sand 2 geteilt wird."""
    m, _ = modell(syn.linse())
    assert namen(m) == ["Auffuellung", "Sand 1", "Kies", "Sand 2", "Geschiebemergel"]
    assert {c for c, s in status(m, "Kies").items() if s == "vorhanden"} == {"B5"}
    for b, ks in zip(m.bohrungen, m.kontakte):
        if b.code == "B5":
            continue
        sand = next(a for a in b.abschnitte if a.klasse == "Sand")
        j1 = namen(m).index("Sand 1")
        assert ks[j1].art == "frei"                     # Grenze irgendwo im ungeteilten Sand
        assert abs(maechtigkeit_an(m, "Kies", b.code)) < 1e-9
        gesamt = maechtigkeit_an(m, "Sand 1", b.code) + maechtigkeit_an(m, "Sand 2", b.code)
        assert gesamt == pytest.approx(sand.ok - sand.uk, abs=1e-6)
        assert maechtigkeit_an(m, "Sand 1", b.code) > 0 and maechtigkeit_an(m, "Sand 2", b.code) > 0
    # die Linse duennt zu den Nachbarn aus: Ausduennung auf Hoehe der Linsenmitte von B5 (31.25 m NHN)
    bi = [b.code for b in m.bohrungen].index("B1")
    assert m.flaechen[namen(m).index("Kies")][bi] == pytest.approx(31.25, abs=0.01)


def test_linse_bleibt_lokal():
    """Eine Linse aus einer Bohrung liegt nicht duenn unter dem ganzen Gebiet (IDW waere ueberall > 0):
    sie endet etwa auf halbem Weg zu den Nachbarn ohne Kies (Wahrheit: Radius 20 m, Abstand 50 m)."""
    m, _ = modell(syn.linse())
    j = namen(m).index("Kies")
    d = m.flaechen[j] - m.flaechen[j + 1]
    b5 = [b.code for b in m.bohrungen].index("B5")
    r = np.hypot(*(m.punkte - m.punkte[b5]).T)
    assert r[d > 0.005].max() < 30.0
    assert any("Ausdehnung begrenzt" in h for h in m.koerper[j]["hinweise"])
    kegel = math.pi * 20.0 ** 2 * 1.5 / 3
    assert m.koerper[j]["volumen_m3"] < 3 * kegel


def test_zensiert():
    """Ostreihe endet im Sand: tiefere Einheiten dort unbekannt, Sandunterkante unter Endteufe - Marge."""
    m, _ = modell(syn.zensiert())
    kurz = {"B3", "B6", "B9"}
    assert {c for c, s in status(m, "Geschiebemergel").items() if s == "unbekannt"} == kurz
    j = namen(m).index("Sand")
    for bi, b in enumerate(m.bohrungen):
        if b.code in kurz:
            assert m.kontakte[bi][j].art == "zensiert"
            assert m.flaechen[j + 1][bi] <= b.ende - ZENSUR_MARGE + 1e-6


def test_stoerungen_markiert_statt_versteckt():
    m, _ = modell(syn.stoerungen())
    aus = {a["code"]: a["grund"] for a in m.ausgeschlossen}
    assert aus == {"RKS 7": "keine Koordinaten", "RKS 8": "Ansatzhoehe (GOK) unbekannt"}
    b5 = next(b for b in m.bohrungen if b.code == "B5")
    assert any("zugeschlagen" in h for h in b5.hinweise)
    assert namen(m) == ["Auffuellung", "Sand", "Geschiebemergel", "Ton"]


def test_vorgabe_fasst_bodenarten_zusammen():
    """Gutachter-Vorgabe: Sand und Kies eine Einheit -> keine Linse, mehrere Abschnitte je Einheit (C)."""
    vorgabe = einheiten_aus_vorgabe([{"name": "Auffuellung"}, {"name": "Sande und Kiese", "bodenarten": ["Sand", "Kies"]},
                                     {"name": "Geschiebemergel"}])
    m, _ = modell(syn.linse(), vorgabe=vorgabe)
    assert namen(m) == ["Auffuellung", "Sande und Kiese", "Geschiebemergel"]
    assert not m.hinweise
    bi = [b.code for b in m.bohrungen].index("B5")
    assert maechtigkeit_an(m, "Sande und Kiese", "B5") == pytest.approx(
        m.bohrungen[bi].abschnitte[0].uk - m.bohrungen[bi].abschnitte[-1].ok, abs=1e-6)


def test_vorgabe_unbekannte_bodenart_wird_markiert():
    vorgabe = einheiten_aus_vorgabe([{"name": "Auffuellung"}, {"name": "Sand"}, {"name": "Ton"}])
    m, _ = modell(syn.geneigt(), vorgabe=vorgabe)
    assert "Geschiebemergel" in namen(m)
    assert any("Geschiebemergel" in h and "keine vorgegebene" in h for h in m.hinweise)


def test_reihenfolge_der_eingabe_egal():
    fall = syn.demo()
    doc = syn.dokument(fall)
    rueck = dict(doc, boreholes=doc["boreholes"][::-1])
    assert namen(bauen([doc])) == namen(bauen([rueck]))


def test_eine_und_zwei_bohrungen():
    fall = syn.geneigt()
    fall.bohrungen = fall.bohrungen[:1]
    m, _ = modell(fall, methode="tps")
    assert len(m.einheiten) == 4 and all(k["pruefung"]["geschlossen"] for k in m.koerper)
    assert np.ptp(m.flaechen[1]) < 1e-9                          # eine Bohrung: waagerechte Flaechen
    fall = syn.geneigt()
    fall.bohrungen = fall.bohrungen[:2]                          # Bohrlinie: Korridor, TPS faellt auf IDW zurueck
    m, _ = modell(fall, methode="tps")
    assert m.max_abweichung < 1e-6 and all(k["pruefung"]["geschlossen"] for k in m.koerper)


def test_ausrichtung_bevorzugt_hoehe():
    """Zwei Kieslagen in A, eine in B: B's Kies wird der hoehengleichen Lage zugeordnet, die andere fehlt."""
    a = Bohrung("A", 0, 0, 40, [Abschnitt("Sand", 40, 36, []), Abschnitt("Kies", 36, 34, []), Abschnitt("Sand", 34, 30, []),
                                Abschnitt("Kies", 30, 28, []), Abschnitt("Sand", 28, 20, [])], "x")
    b = Bohrung("B", 30, 0, 40, [Abschnitt("Sand", 40, 31, []), Abschnitt("Kies", 31, 28.5, []),
                                 Abschnitt("Sand", 28.5, 20, [])], "x")
    einheiten, zuordnung, _ = korrelieren([a, b])
    assert [e.name for e in einheiten] == ["Sand 1", "Kies 1", "Sand 2", "Kies 2", "Sand 3"]
    ops = {e.name: op for op, _, e in zuordnung["B"]}
    assert ops["Kies 1"] == "S" and ops["Sand 2"] == "E" and ops["Kies 2"] == "M"


def test_unter_endteufe_unbekannt_nicht_fehlend():
    a = Bohrung("A", 0, 0, 40, [Abschnitt("Sand", 40, 30, []), Abschnitt("Ton", 30, 20, [])], "x")
    kurz = Bohrung("K", 10, 0, 40, [Abschnitt("Sand", 40, 35, [])], "x")
    einheiten, zuordnung, _ = korrelieren([a, kurz])
    assert [op for op, _, _ in zuordnung["K"]] == ["M", "T"]
    _, ops = ausrichten(kurz, einheiten, [(40, 30, 0, 10), (30, 20, 10, 20)])
    assert ops[-1][0] == "T"


def test_gelaendefolgende_schichten_bei_starkem_gefaelle():
    """Auffuellung 1 m unter Gelaende in Bohrungen mit 20 m GOK-Unterschied: eine Einheit (nach Tiefe), nicht drei."""
    def bohr(code, x, gok):
        return Bohrung(code, x, 0, gok, [Abschnitt("Auffuellung", gok, gok - 1, []), Abschnitt("Schluff", gok - 1, gok - 4, []),
                                         Abschnitt("Fels", gok - 4, gok - 8, [])], "x")
    einheiten, _, _ = korrelieren([bohr("A", 0, 770), bohr("B", 40, 760), bohr("C", 80, 750)])
    assert [e.name for e in einheiten] == ["Auffuellung", "Schluff", "Fels"]


def test_interpolatoren_exakt():
    xy = np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0], [7.0, 8.0]])
    z = np.array([1.0, 2.0, 3.0, 5.0])
    for meth in ("idw", "tps"):
        assert np.allclose(interpolieren(xy, xy, z, meth), z)


def test_prisma_nach_aussen_orientiert():
    kn, fl = prisma(0.0, 0.0, 10.0, 8.0, r=1.0, n=12)
    p = pruefen(kn, fl)
    assert p["geschlossen"]
    assert p["volumen"] == pytest.approx(2.0 * 0.5 * 12 * math.sin(2 * math.pi / 12), rel=1e-9)


def test_ifc_valide(tmp_path):
    import ifcopenshell
    import ifcopenshell.validate
    m, docs = modell(syn.demo())
    pfad = tmp_path / "demo.ifc"
    ifc_schreiben(m, pfad, docs)
    f = ifcopenshell.open(str(pfad))
    log = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, log)
    assert log.statements == []
    gm = f.by_type("IfcGeomodel")
    assert len(gm) == 1 and len(f.by_type("IfcBorehole")) == len(m.bohrungen)
    einheiten = [s for s in f.by_type("IfcGeotechnicalStratum") if (s.Description or "").startswith("Modelleinheit")]
    assert [s.Name for s in einheiten] == namen(m)
    assert all(fs.Closed for fs in f.by_type("IfcTriangulatedFaceSet"))
    # Laengeneinheit Meter: Koordinaten, Tiefen und Georeferenz sind in m geschrieben
    import ifcopenshell.util.unit
    assert ifcopenshell.util.unit.calculate_unit_scale(f) == 1.0
    mc = f.by_type("IfcMapConversion")[0]
    assert (mc.Eastings, mc.Northings) == tuple(m.ursprung)
    b = bericht(m)
    assert b["pruefungen"]["alle_koerper_geschlossen"] and b["vorlage_einheiten"][0]["name"] == "Auffuellung"


def test_lokales_system_und_herkunft(tmp_path):
    """Lage ohne EPSG (manuell/schematisch) ist ein lokales System; Herkunft von Lage und Hoehe bleibt sichtbar."""
    import ifcopenshell
    doc = syn.dokument(syn.geneigt())
    for b in doc["boreholes"]:
        b["crs_epsg"] = None
        b["coord_source"] = "schematisch"
    doc["boreholes"][0]["gok_source"] = "relativ"
    m = bauen([doc])
    assert m.epsg is None and len(m.bohrungen) == 9
    assert any("ohne Georeferenz" in h for h in m.hinweise)
    assert any("schematische Lage" in h for h in m.hinweise) and any("relative Hoehen" in h for h in m.hinweise)
    ifc_schreiben(m, tmp_path / "lokal.ifc", [doc])
    f = ifcopenshell.open(str(tmp_path / "lokal.ifc"))
    assert not f.by_type("IfcMapConversion")
    werte = {p.Name: p.NominalValue.wrappedValue for p in f.by_type("IfcPropertySingleValue") if p.Name in ("Lage", "Hoehe")}
    assert werte["Lage"] == "schematisch"


def test_mehrheit_bestimmt_das_system():
    doc = syn.dokument(syn.geneigt())
    doc["boreholes"][0]["crs_epsg"] = None                     # eine Bohrung lokal, acht georeferenziert
    m = bauen([doc])
    assert m.epsg == syn.EPSG and len(m.bohrungen) == 8
    assert m.ausgeschlossen[0]["grund"].startswith("anderes Koordinatensystem (lokal")


def test_trasse_ueber_5_km():
    """Grosse Modelle: Knotenzahl begrenzt, Puffer waechst mit dem Bohrabstand, Laufzeit und IFC klein genug."""
    import time
    from baugrundmodell.modell import MAX_KNOTEN
    t = time.time()
    m, docs = modell(syn.trasse())
    assert time.time() - t < 20
    xy = m.punkte
    assert np.ptp(xy[:, 0]) > 5000 and len(xy) <= 1.1 * MAX_KNOTEN
    assert 30 <= m.parameter["puffer_m"] <= 100
    assert m.max_abweichung < 1e-6 and all(k["pruefung"]["geschlossen"] for k in m.koerper)


def test_grosse_modellgrenze_von_hand():
    """Puffer 500 m und Raster 0.5 m von Hand: das Raster wird vergroebert (Knotenbudget), mit Hinweis."""
    from baugrundmodell.modell import MAX_KNOTEN
    m = bauen([syn.dokument(syn.demo())], raster=0.5, puffer=500.0)
    assert m.parameter["puffer_m"] == 500.0 and m.parameter["raster_m"] > 0.5
    assert len(m.punkte) <= 1.1 * MAX_KNOTEN and any("vergroebert" in h for h in m.hinweise)
    assert all(k["pruefung"]["geschlossen"] for k in m.koerper)


def test_fester_ursprung_und_pruefstand(tmp_path):
    import ifcopenshell
    doc = syn.dokument(syn.geneigt())
    doc["boreholes"][0]["geprueft"] = True
    doc["boreholes"][0]["layers"][0].update(geprueft=True, korrigiert=True, konfidenz_extraktion=0.4)
    m = bauen([doc], ursprung=(565000.0, 5933000.0))
    assert m.ursprung == (565000.0, 5933000.0)
    ifc_schreiben(m, tmp_path / "p.ifc", [doc], pruefstand="v1 · 9/9 Bohrungen geprueft")
    f = ifcopenshell.open(str(tmp_path / "p.ifc"))
    werte = {}
    for pv in f.by_type("IfcPropertySingleValue"):
        werte.setdefault(pv.Name, []).append(pv.NominalValue.wrappedValue if pv.NominalValue else None)
    assert werte["Pruefstand"] == ["v1 · 9/9 Bohrungen geprueft"] and werte["Ursprung_Rechtswert"] == [565000.0]
    assert werte["Geprueft"].count(True) == 2 and werte["Korrigiert"] == [True]


def test_ausschluss_ohne_koordinaten():
    doc = syn.dokument(syn.geneigt())
    for b in doc["boreholes"]:
        b["x"] = None
    bohrungen, aus, epsg = bohrungen_aus_extraktion([doc])
    assert bohrungen == [] and epsg is None and len(aus) == 9
    with pytest.raises(ValueError):
        bauen([doc])


def test_bodenansprache_beschreibungen_und_durchmesser(tmp_path):
    """Jede Schicht traegt ihre Beschreibung und die Deutung nach Norm; jede Einheit die Beschreibungen ihrer
    Schichten; Bohrsaeulen mit Durchmesser von Hand (je Bohrung) oder automatisch nach Modellgroesse."""
    import ifcopenshell
    import ifcopenshell.util.element
    import ifcopenshell.validate
    doc = syn.dokument(syn.demo())
    b0 = doc["boreholes"][0]
    b0["layers"][0]["description_raw"] = "Anschüttung, Schluff, stark tonig, kiesig, weich-steif"
    b0["layers"][1]["description_raw"] = "mS, fs', u, mitteldicht"
    m = bauen([doc])
    pfad = tmp_path / "ansprache.ifc"
    ifc_schreiben(m, pfad, [doc], durchmesser_je={b0["code"]: 0.3})
    f = ifcopenshell.open(str(pfad))
    log = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, log)
    assert log.statements == []
    bohrung = next(b for b in f.by_type("IfcBorehole") if b.Name == b0["code"])
    ps = ifcopenshell.util.element.get_psets(bohrung)
    assert ps["CPset_Darstellung"]["Durchmesser_m"] == 0.3
    assert ps["CPset_Darstellung"]["Durchmesser_Quelle"] == "manuell (Bohrung)"
    andere = next(b for b in f.by_type("IfcBorehole") if b.Name != b0["code"])
    assert ifcopenshell.util.element.get_psets(andere)["CPset_Darstellung"]["Durchmesser_m"] == \
        m.parameter["durchmesser_auto_m"]
    schichten = ifcopenshell.util.element.get_decomposition(bohrung)
    oben = next(s for s in schichten if " 0.00-" in s.Name)
    ps = ifcopenshell.util.element.get_psets(oben)
    assert ps["CPset_Schichtenverzeichnis"]["Beschreibung"].startswith("Anschüttung, Schluff")
    assert ps["CPset_Bodenansprache"]["Kurzzeichen_DIN4023"] == "A (U, t̅, g)"
    assert ps["CPset_Bodenansprache"]["Konsistenz"] == "weich bis steif"
    assert ps["CPset_Bodenansprache"]["Farbname_DIN4023"] == "grau"
    # Beschreibung als IfcText (Freitext), Kurzzeichen als IfcLabel
    beschreibung = [p for p in f.by_type("IfcPropertySingleValue") if p.Name == "Beschreibung"]
    assert beschreibung and all(p.NominalValue.is_a("IfcText") for p in beschreibung)
    # Kanten der Saeule: Radius 0.15 m um die Achse
    rep = oben.Representation.Representations[0].Items[0]
    xy = np.array(rep.Coordinates.CoordList)[:, :2]
    assert np.allclose(np.hypot(*(xy - xy.mean(axis=0)).T), 0.15, atol=1e-6)
    # Einheiten: Beschreibungen ihrer Schichten und Benennungen nach Norm
    einheit = next(s for s in f.by_type("IfcGeotechnicalStratum") if s.Name == "Sand 1" or s.Name == "Sand")
    me = ifcopenshell.util.element.get_psets(einheit)["CPset_Modelleinheit"]
    assert "mS, fs', u" in me["Beschreibungen"] and "Mittelsand" in me["Benennungen"]
    assert me["Farbname_DIN4023"] == "orange"
    b = bericht(m)
    sand = next(e for e in b["einheiten"] if e["name"] in ("Sand", "Sand 1"))
    assert any(s["beschreibung"] == "mS, fs', u, mitteldicht" and s["bohrung"] == b0["code"] for s in sand["schichten"])


# ---------------------------------------------------------------- Gelaende aus dem DGM (umgebung.py, docs/23 P3b)
class DGM:
    """Raster wie geodaten.gelaende.Raster: Knoten (i, j) bei (x0 + j*dx, y0 - i*dy)."""

    def __init__(self, x0, y0, dx, z, epsg=syn.EPSG):
        self.x0, self.y0, self.dx, self.dy, self.z, self.epsg = x0, y0, dx, dx, np.asarray(z, dtype=np.float32), epsg


def dgm_fuer(fall, rand=150.0, dx=1.0, buckel=(0.0, 0.0, 0.0), epsg=syn.EPSG):
    """DGM aus der GOK-Funktion des Falls (lokal zum syn.URSPRUNG) plus ein Buckel (x, y, Hoehe) zwischen Bohrungen."""
    xs = [b[1] for b in fall.bohrungen]
    ys = [b[2] for b in fall.bohrungen]
    x0, x1 = min(xs) - rand, max(xs) + rand
    y0, y1 = min(ys) - rand, max(ys) + rand
    gx = np.arange(x0, x1 + dx, dx)
    gy = np.arange(y1, y0 - dx, -dx)
    X, Y = np.meshgrid(gx, gy)
    z = np.vectorize(fall.gok)(X, Y) + buckel[2] * np.exp(-((X - buckel[0]) ** 2 + (Y - buckel[1]) ** 2) / 100.0)
    return DGM(x0 + syn.URSPRUNG[0], y1 + syn.URSPRUNG[1], dx, z, epsg)


def test_gelaende_aus_dgm_exakt_an_bohrungen_und_im_dgm_dazwischen():
    """Oberkante = DGM zwischen den Bohrungen (Buckel bleibt), an den Bohrungen exakt die GOK (+0,8 m an einer)."""
    from baugrundmodell.umgebung import abtasten
    fall = syn.demo()
    buckel = (106.8, 33.1, 2.0)                                # 37 m von der naechsten Bohrung: dort wirkt keine GOK
    r = dgm_fuer(fall, buckel=buckel)
    docs = [syn.dokument(fall)]
    docs[0]["boreholes"][0]["gok_nhn"] += 0.8                   # Bohrung 1: GOK 0,8 m ueber dem DGM (Aufschuettung?)
    m = bauen(docs, gelaende=r, gelaende_info={"name": "Test-DGM"})
    gel = m.parameter["gelaende"]
    assert gel["quelle"] == "DGM" and gel["gok_minus_dgm_max_m"] == pytest.approx(0.8, abs=0.01)
    gok = np.array([b.gok for b in m.bohrungen])
    assert np.abs(m.flaechen[0][:len(gok)] - gok).max() < 1e-9 and m.max_abweichung < 1e-6
    weit = cKDTree_abstand(m) > gel["reichweite_m"]
    dgm = abtasten(r, m.punkte + np.asarray(m.ursprung))
    assert weit.sum() > 50 and np.abs(m.flaechen[0][weit] - dgm[weit]).max() < 1e-6
    lokal = m.punkte + np.asarray(m.ursprung) - np.asarray(syn.URSPRUNG)
    am_buckel = np.hypot(lokal[:, 0] - buckel[0], lokal[:, 1] - buckel[1]) < 4.0
    glatt = np.vectorize(fall.gok)(lokal[:, 0], lokal[:, 1])   # was die Interpolation der GOK ergaebe
    assert am_buckel.any() and (m.flaechen[0][am_buckel] - glatt[am_buckel]).min() > 1.0
    # der Buckel ist nicht erkundet: markiert, nicht versteckt
    assert gel["ueber_interpolation_max_m"] > 1.5 and any("nicht erkundet" in h for h in m.hinweise)
    assert np.all(np.diff(m.flaechen, axis=0) <= 1e-9)
    assert all(k["pruefung"]["geschlossen"] for k in m.koerper)
    assert m.dgm is r


def cKDTree_abstand(m):
    from scipy.spatial import cKDTree
    xy_b = np.array([(b.x - m.ursprung[0], b.y - m.ursprung[1]) for b in m.bohrungen])
    return cKDTree(xy_b).query(m.punkte)[0]


def test_gelaende_faellt_zurueck_und_sagt_warum():
    """Luecke im Gebiet, anderes System: Gelaende aus den GOK wie bisher, mit Hinweis statt still."""
    fall = syn.demo()
    ohne = bauen([syn.dokument(fall)])
    luecke = dgm_fuer(fall)
    luecke.z[luecke.z.shape[0] // 2, luecke.z.shape[1] // 2] = np.nan
    for r, wort in ((luecke, "nicht ganz ab"), (dgm_fuer(fall, epsg=25833), "EPSG:25833")):
        m = bauen([syn.dokument(fall)], gelaende=r)
        assert m.parameter["gelaende"]["quelle"] == "GOK" and m.dgm is None
        assert any(wort in h for h in m.hinweise)
        assert np.allclose(m.flaechen, ohne.flaechen)


def test_ifc_mit_gelaende_um_das_modell(tmp_path):
    """IfcGeographicElement TERRAIN: offen, in Metern, teilt die Randknoten des Modells; IFC bleibt fehlerfrei."""
    import ifcopenshell
    import ifcopenshell.util.element
    import ifcopenshell.util.unit
    import ifcopenshell.validate
    fall = syn.demo()
    r = dgm_fuer(fall, rand=60.0)
    docs = [syn.dokument(fall)]
    m = bauen(docs, gelaende=r, gelaende_info={"name": "Test-DGM", "raster_m": 1.0,
                                               "quelle_dienst": {"titel": "WCS Test", "lizenz": "dl-de/zero-2.0"}})
    pfad = tmp_path / "gelaende.ifc"
    assert ifc_schreiben(m, pfad, docs)["gelaende"]
    f = ifcopenshell.open(str(pfad))
    log = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, log)
    assert log.statements == []
    assert ifcopenshell.util.unit.calculate_unit_scale(f) == 1.0
    (g,) = f.by_type("IfcGeographicElement")
    assert g.PredefinedType == "TERRAIN"
    fs = g.Representation.Representations[0].Items[0]
    assert fs.is_a("IfcTriangulatedFaceSet") and not fs.Closed
    knoten = np.array(fs.Coordinates.CoordList)
    ps = ifcopenshell.util.element.get_psets(g)["CPset_Gelaende"]
    assert ps["Lizenz"] == "dl-de/zero-2.0" and 30 < ps["Abstand_m"] <= 100
    # jeder Randknoten des Modells (mit seiner Oberkante) ist Knoten des Gelaendes: keine Fuge
    rand = np.unique(m.rand)
    innen = np.c_[m.punkte[rand], m.flaechen[0][rand]]
    from scipy.spatial import cKDTree
    assert cKDTree(knoten).query(innen)[0].max() < 1e-9
    assert "DGM Test-DGM" in ifcopenshell.util.element.get_psets(f.by_type("IfcGeomodel")[0])["CPset_Baugrundmodell"]["Gelaende"]
    # Dreiecke von oben gegen den Uhrzeigersinn (Normale nach oben)
    d = np.array(fs.CoordIndex) - 1
    a, b, c = knoten[d[:, 0]], knoten[d[:, 1]], knoten[d[:, 2]]
    assert np.all((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0]) > 0)


def test_ohne_dgm_kein_gelaende_im_ifc(tmp_path):
    import ifcopenshell
    m, docs = modell(syn.demo())
    assert not ifc_schreiben(m, tmp_path / "ohne.ifc", docs)["gelaende"]
    assert len(ifcopenshell.open(str(tmp_path / "ohne.ifc")).by_type("IfcGeographicElement")) == 0


# ---------------------------------------------------------------- LoD2-Gebaeude der Umgebung (ifc4x3.gebaeude, docs/23 P4)
def quader(x, y, b, t, z0, h, loch=False):
    """Gebaeude als Quader (Boden, vier Waende, Dach) im System des Falls; eine Wand mit Fensterloch."""
    e0, n0 = syn.URSPRUNG
    p = [(e0 + x, n0 + y), (e0 + x + b, n0 + y), (e0 + x + b, n0 + y + t), (e0 + x, n0 + y + t)]
    fl = [{"art": "Boden", "ring": [(*q, z0) for q in reversed(p)], "loecher": []},
          {"art": "Dach", "ring": [(*q, z0 + h) for q in p], "loecher": []}]
    for k in range(4):
        a, c = p[k], p[(k + 1) % 4]
        ring = [(*a, z0), (*c, z0), (*c, z0 + h), (*a, z0 + h), (*a, z0)]       # geschlossen wie im GML
        loecher = []
        if loch and k == 0:
            loecher = [[(a[0] + 1, a[1], z0 + 1), (a[0] + 2, a[1], z0 + 1), (a[0] + 2, a[1], z0 + 2), (a[0] + 1, a[1], z0 + 2)]]
        fl.append({"art": "Wand", "ring": ring, "loecher": loecher})
    return {"id": f"DEBE_TEST_{x:g}", "funktion": "31001_1000", "dachform": "1000", "hoehe": h, "flaechen": fl}


def test_ifc_mit_lod2_gebaeuden(tmp_path):
    """IfcBuildingElementProxy je Gebaeude: Waende/Boden und Dach mit eigener Farbe, Loch als FaceWithVoids, Lizenz."""
    import ifcopenshell
    import ifcopenshell.util.element
    import ifcopenshell.util.unit
    import ifcopenshell.validate
    m, docs = modell(syn.demo())
    geb = [quader(-40, -30, 12, 8, 30.0, 9.5, loch=True), quader(170, 40, 6, 6, 31.0, 4.0)]
    pfad = tmp_path / "gebaeude.ifc"
    erg = ifc_schreiben(m, pfad, docs, gebaeude=geb, gebaeude_info={"Lizenz": "dl-de/zero-2.0", "Quelle": "Test"})
    assert erg["gebaeude"] == 2
    f = ifcopenshell.open(str(pfad))
    log = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, log)
    assert log.statements == []
    assert ifcopenshell.util.unit.calculate_unit_scale(f) == 1.0
    proxies = f.by_type("IfcBuildingElementProxy")
    assert len(proxies) == 2 and all(p.ObjectType == "LoD2-Gebäude (Umgebung)" for p in proxies)
    ps = ifcopenshell.util.element.get_psets(proxies[0])["CPset_Gebaeude"]
    assert ps["Lizenz"] == "dl-de/zero-2.0" and ps["GML_ID"] == "DEBE_TEST_-40" and ps["Hoehe_m"] == 9.5
    items = proxies[0].Representation.Representations[0].Items
    assert [len(i.Faces) for i in items] == [5, 1] and not any(i.Closed for i in items)
    assert len(f.by_type("IfcIndexedPolygonalFaceWithVoids")) == 1
    # lokal zum Ursprung, Hoehen unveraendert (m NHN), geschlossene Ringe ohne doppelten Punkt
    k = np.array(items[1].Coordinates.CoordList)
    assert np.allclose(k[:, 2], 39.5) and len(k) == 4
    assert k[:, 0].min() == pytest.approx(syn.URSPRUNG[0] - 40 - m.ursprung[0])
