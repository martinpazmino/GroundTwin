"""Ground Analysis (docs/27, Phase G1): Kreuzprobe, Unsicherheit, virtuelle Bohrung an den synthetischen Faellen."""
from __future__ import annotations

import copy
import json
import time

import numpy as np
import pytest
from baugrundmodell import synthetisch as syn
from baugrundmodell.modell import bauen

from baugrundanalyse import analyse, kreuzprobe, unsicherheit, virtuelle_bohrung
from baugrundanalyse.__main__ import main


def modell(name: str, **kw):
    return bauen([syn.dokument(syn.FAELLE[name]())], **kw)


def einheit(k: dict, methode: str, name: str) -> dict:
    return next(e for e in k["methoden"][methode]["einheiten"] if e["name"] == name)


# ------------------------------------------------------------------ Kreuzprobe
def test_kreuzprobe_geneigte_ebenen_tps_exakt_idw_nicht():
    # Messwerte aus docs/27 §3.1: Unterkante Sand, IDW 0,78 m, Duennplatten-Spline 0,00 m
    k = kreuzprobe(modell("geneigt"))
    assert k["methoden"]["tps"]["gesamt"]["mae"] < 0.01 and k["methoden"]["tps"]["gesamt"]["n"] == 27
    assert einheit(k, "idw", "Sand")["mae"] == pytest.approx(0.78, abs=0.02)
    assert k["beste"] == "tps" and k["methode_modell"] == "idw"
    assert any("tps sagt die Bohrungen besser voraus" in h for h in k["hinweise"])
    assert einheit(k, "idw", "Ton")["n"] == 0                              # Unterkante von keiner Bohrung erreicht
    assert k["methoden"]["idw"]["gelaende"]["n"] == 9                      # ohne DGM wird auch die GOK vorhergesagt
    json.dumps({x: v for x, v in k.items() if not x.startswith("_")})


def test_kreuzprobe_linse_ausdehnung_unsicher():
    k = kreuzprobe(modell("linse"))
    p = einheit(k, "idw", "Kies")["praesenz"]
    assert p["falsch_vorhanden"] + p["falsch_fehlend"] >= 1 and p["richtig"] >= 6
    assert any("Ausdehnung ist unsicher" in h for h in k["hinweise"])
    # die Linse steckt nur in B5: die Kreuzprobe kann Geologie und Fehler nicht trennen und fragt deshalb
    assert [a["bohrung"] for a in k["methoden"]["tps"]["auffaellig"]] == ["B5"]
    assert any("B5" in h and "Linse, Rinne oder Fehler" in h for h in k["hinweise"])


def test_kreuzprobe_findet_die_bohrung_mit_falschen_tiefen():
    doc = syn.dokument(syn.geneigt())
    falsch = doc["boreholes"][4]
    for ly in falsch["layers"][1:]:                                         # alle Grenzen ab der zweiten Schicht 3 m zu tief
        ly["top_depth"] += 3.0
        ly["bottom_depth"] += 3.0
    falsch["layers"][0]["bottom_depth"] += 3.0
    k = kreuzprobe(bauen([doc], methode="tps"))                              # die falsche Bohrung verdirbt auch ihre Nachbarn
    v = k["methoden"]["tps"]
    assert [b["code"] for b in v["bohrungen"] if b["auffaellig"]] == [falsch["code"]]
    assert v["auffaellig"] == [{"bohrung": "B5", "fehler_m": 3.0, "median_der_anderen_ohne_sie_m": 0.0}]
    assert any("B5 (3,00 m)" in h and "prüfen" in h for h in k["hinweise"])
    # IDW liegt auf geneigten Ebenen selbst 0,6 bis 1,6 m daneben: 3 m heben sich davon nicht genug ab
    assert k["methoden"]["idw"]["auffaellig"] == []
    assert kreuzprobe(bauen([syn.dokument(syn.geneigt())], methode="tps"))["methoden"]["tps"]["auffaellig"] == []


def test_kreuzprobe_braucht_drei_bohrungen_und_aendert_das_modell_nicht():
    doc = syn.dokument(syn.geneigt())
    doc["boreholes"] = doc["boreholes"][:2]
    with pytest.raises(ValueError, match="mindestens 3 Bohrungen"):
        kreuzprobe(bauen([doc]))
    m = modell("demo")
    vorher, kontakte = m.flaechen.copy(), copy.deepcopy(m.kontakte)
    kreuzprobe(m)
    unsicherheit(m, laeufe=5)
    assert np.array_equal(m.flaechen, vorher) and m.kontakte == kontakte


# ------------------------------------------------------------------ Unsicherheit
def test_unsicherheit_waechst_mit_dem_abstand_und_ist_wiederholbar():
    m = modell("demo")
    u = unsicherheit(m, laeufe=40, seed=3)
    s, nb = u["_sigma"], len(m.bohrungen)
    assert np.all(s[0] == 0.0)                                              # Gelaende gilt als gegeben
    j = [e.name for e in m.einheiten].index("Auffuellung") + 1
    weit = int(np.argmax(m.abstand))
    assert s[j][:nb].max() < 0.2 < s[j][weit]                               # an den Bohrungen nur die Messung
    assert np.all(np.diff(s[j][np.argsort(u["_abstand_stuetz"][j])][::200]) > -0.15)   # im Groben steigend
    e = {x["name"]: x for x in u["einheiten"]}
    assert not e["Ton"]["unterkante_bezifferbar"] and e["Ton"]["sigma_mittel_m"] is None
    assert any("Ton" in h for h in u["hinweise"])
    v = e["Sand 1"]["volumen_m3"]
    assert v["p5"] < v["modell"] < v["p95"]
    assert e["Auffuellung"]["methoden_differenz_m"]["gegen"] == "tps"
    assert np.array_equal(unsicherheit(m, laeufe=40, seed=3)["_sigma"][1:6], s[1:6])
    assert len(u["annahmen"]) == 4


def test_unsicherheit_ohne_vorhersagefehler_bleibt_die_messung():
    # geneigte Ebenen mit dem Spline: die Kreuzprobe trifft exakt -> kein Anteil aus dem Abstand
    m = modell("geneigt", methode="tps")
    u = unsicherheit(m, laeufe=60)
    j = [e.name for e in m.einheiten].index("Sand") + 1
    assert np.allclose(u["_sigma_abstand"][j], 0.0, atol=1e-6)
    assert 0.03 < u["_sigma"][j].mean() < 0.2                               # in der Groesse von SIGMA_EXAKT


# ------------------------------------------------------------------ virtuelle Bohrung
def test_virtuelle_bohrung_an_einer_bohrung_gleich_der_bohrung():
    m = modell("demo")
    u = unsicherheit(m, laeufe=20)
    b, ks = m.bohrungen[3], m.kontakte[3]
    v = virtuelle_bohrung(m, b.x, b.y, u)
    assert v["gok_nhn"] == pytest.approx(b.gok, abs=0.01) and v["abstand_m"] == 0.0 and v["naechste_bohrung"] == b.code
    for s in v["schichten"]:
        j = [e.name for e in m.einheiten].index(s["einheit"])
        if ks[j].art == "exakt":
            assert s["unten_nhn"] == pytest.approx(ks[j].z, abs=0.01)
            assert s["sigma_unten_m"] < 0.2
    assert v["schichten"][-1]["unterkante_offen"] and v["herkunft"].startswith("Modell")


def test_virtuelle_bohrung_zwischen_den_bohrungen_und_ausserhalb():
    m = modell("demo")
    u = unsicherheit(m, laeufe=20)
    a, b = m.bohrungen[0], m.bohrungen[1]
    v = virtuelle_bohrung(m, (a.x + b.x) / 2, (a.y + b.y) / 2, u)
    tiefen = [(s["tiefe_oben_m"], s["tiefe_unten_m"]) for s in v["schichten"]]
    assert tiefen[0][0] == 0.0 and all(o < u_ for o, u_ in tiefen)
    assert all(t1[1] == pytest.approx(t2[0], abs=0.011) for t1, t2 in zip(tiefen, tiefen[1:]))   # lueckenlos
    erste = v["schichten"][0]
    assert erste["sigma_unten_m"] > 0.1 and erste["unten_95_nhn"][0] < erste["unten_nhn"] < erste["unten_95_nhn"][1]
    assert virtuelle_bohrung(m, a.x, a.y)["schichten"][0]["sigma_unten_m"] is None      # ohne Unsicherheit: nur das Modell
    json.dumps(v)
    with pytest.raises(ValueError, match="außerhalb des Modells"):
        virtuelle_bohrung(m, a.x + 5000.0, a.y)


# ------------------------------------------------------------------ zusammen, Kommandozeile, Zeit
def test_analyse_als_json_und_unter_zehn_sekunden():
    m = modell("demo")
    t0 = time.time()
    a = analyse(m, laeufe=100)
    assert time.time() - t0 < 10.0                                          # Abnahme G1: 12 Bohrungen unter 10 s
    text = json.dumps(a, ensure_ascii=False)
    assert "_sigma" not in text and a["unsicherheit"]["laeufe"] == 100 and a["kreuzprobe"]["bohrungen"] == 12


def test_kommandozeile(tmp_path, capsys):
    doc = syn.dokument(syn.demo())
    (tmp_path / "a.json").write_text(json.dumps(doc), encoding="utf-8")
    b = doc["boreholes"][0]
    aus = tmp_path / "analyse.json"
    assert main([str(tmp_path / "a.json"), "--laeufe", "10", "--punkt", str(b["x"] + 6), str(b["y"] + 3),
                 "--bericht", str(aus)]) == 0
    text = capsys.readouterr().out
    assert "Kreuzprobe (12 Bohrungen)" in text and "Virtuelle Bohrung" in text and "±" in text
    d = json.loads(aus.read_text(encoding="utf-8"))
    assert set(d) == {"kreuzprobe", "unsicherheit", "virtuelle_bohrung"}
    doc["boreholes"] = doc["boreholes"][:2]
    (tmp_path / "b.json").write_text(json.dumps(doc), encoding="utf-8")
    assert main([str(tmp_path / "b.json")]) == 2 and "Keine Analyse" in capsys.readouterr().out


# ------------------------------------------------------------------ Luecken aus der Mutationsprobe
def test_kreuzprobe_endteufe_je_bohrung_und_genau_drei_bohrungen():
    doc = syn.dokument(syn.geneigt())
    b5 = doc["boreholes"][4]
    sand = b5["layers"][1]
    sand["bottom_depth"] += 4.0                                             # B5 endet im Sand, 4 m tiefer als dessen
    b5["layers"] = b5["layers"][:2]                                         # Unterkante bei den Nachbarn
    k = kreuzprobe(bauen([doc], methode="tps"))
    verletzt = einheit(k, "tps", "Sand")["endteufe_verletzt"]
    assert [v["bohrung"] for v in verletzt] == ["B5"] and verletzt[0]["um_m"] == pytest.approx(4.0, abs=0.05)
    assert einheit(k, "tps", "Auffuellung")["endteufe_verletzt"] == []

    v = kreuzprobe(modell("geneigt"))["methoden"]["idw"]
    assert [b["n"] for b in v["bohrungen"]] == [3] * 9 and sum(b["n"] for b in v["bohrungen"]) == v["gesamt"]["n"]
    assert max(b["max"] for b in v["bohrungen"]) == v["gesamt"]["max"]
    assert len({b["mae"] for b in v["bohrungen"]}) > 1                      # je Bohrung eigene Fehler, nicht alle gleich

    drei = syn.dokument(syn.geneigt())
    drei["boreholes"] = drei["boreholes"][:3]
    k3 = kreuzprobe(bauen([drei]))
    assert k3["bohrungen"] == 3 and k3["methoden"]["idw"]["auffaellig"] == []


def test_kreuzprobe_hinweise_nur_wenn_sie_zutreffen():
    assert kreuzprobe(modell("geneigt", methode="tps"))["hinweise"] == []   # Modell nutzt schon die bessere Methode
    h = kreuzprobe(modell("geneigt"))["hinweise"]
    assert len(h) == 1 and "0.00 m statt 0.66 m" in h[0]


def test_unsicherheit_faktor_je_einheit_und_methodenvergleich():
    from baugrundmodell.flaechen import schichtmodell
    m = modell("geneigt")
    u = unsicherheit(m, laeufe=30)
    e = {x["name"]: x for x in u["einheiten"]}
    assert e["Sand"]["c_aus"] == "Einheit" and e["Sand"]["kreuz_fehler"] == 9
    assert e["Sand"]["c_m2_je_m"] > 1.3 * e["Auffuellung"]["c_m2_je_m"] > 0   # Sand faellt steiler: groesserer Fehler
    assert e["Ton"]["c_aus"] == "allen Einheiten" and e["Ton"]["kreuz_fehler"] == 0
    j = [x.name for x in m.einheiten].index("Sand") + 1
    weit = int(np.nanargmax(u["_abstand_stuetz"][j]))
    assert u["_sigma_abstand"][j][weit] == pytest.approx(np.sqrt(e["Sand"]["c_m2_je_m"] * u["_abstand_stuetz"][j][weit]), rel=0.01)
    assert 0.03 < e["Sand"]["sigma_messung_mittel_m"] < 0.15
    nb = len(m.bohrungen)
    tps = schichtmodell(m.bohrungen, m.kontakte, m.punkte, m.punkte[:nb], m.basis, "tps", oben=m.flaechen[0])["flaechen"]
    assert e["Sand"]["methoden_differenz_m"]["max"] == pytest.approx(float(np.abs(tps[j] - m.flaechen[j]).max()), abs=0.01)
    assert e["Sand"]["methoden_differenz_m"]["max"] > 0.5

    linse = modell("linse")                                                 # Kennzahlen nur dort, wo die Einheit vorkommt
    ul = unsicherheit(linse, laeufe=10)
    jk = [x.name for x in linse.einheiten].index("Kies")
    da = (linse.flaechen[jk] - linse.flaechen[jk + 1]) >= 0.005
    assert 0 < da.sum() < len(da) / 2
    kies = next(x for x in ul["einheiten"] if x["name"] == "Kies")
    assert kies["sigma_max_m"] == pytest.approx(float(np.nanmax(ul["_sigma"][jk + 1][da])), abs=0.01)


def test_verschobene_grenzen_bleiben_in_ihrer_reihenfolge():
    import sys
    us = sys.modules["baugrundanalyse.unsicherheit"]
    m = modell("demo")
    for seed in range(5):
        for b, ks in zip(m.bohrungen, us._verschoben(m, np.random.default_rng(seed), 2.0)):   # 2 m: weit ueber den Schichtdicken
            z = [k.z for k in ks if k.art == "exakt"]
            assert all(a >= c for a, c in zip(z, z[1:])) and (not z or z[0] < b.gok)
    gleich = us._verschoben(m, np.random.default_rng(0), 0.0)
    for alt, neu in zip(m.kontakte, gleich):
        assert [k.z for k in neu if k.art == "exakt"] == pytest.approx([k.z for k in alt if k.art == "exakt"], abs=0.011)


def test_virtuelle_bohrung_bereich_95_je_schicht():
    m = modell("demo")
    u = unsicherheit(m, laeufe=20)
    a, b = m.bohrungen[2], m.bohrungen[5]
    v = virtuelle_bohrung(m, (a.x + b.x) / 2, (a.y + b.y) / 2, u)
    mit = [s for s in v["schichten"] if s["sigma_unten_m"] is not None]
    assert len(mit) >= 3
    for s in mit:
        assert s["unten_95_nhn"][0] == pytest.approx(s["unten_nhn"] - 1.96 * s["sigma_unten_m"], abs=0.03)
        assert s["unten_95_nhn"][1] == pytest.approx(s["unten_nhn"] + 1.96 * s["sigma_unten_m"], abs=0.03)
    assert v["hinweise"] == ["unterste Einheit: Unterkante = Modellbasis (keine Bohrung erreicht sie)"]
