"""Synthetische Laengsschnitte mit Wasserlinien (und Fallen) fuer Issue #26 Teil 2b.

Muster wie synth_bohrprofil.py: erzeugt reproduzierbare Vektor-PDFs mit bekannter Wahrheit
(Feld ``wasserlinien`` im JSON-Format) fuer Entwicklung, Ablation und Regression.

Faelle:
  ls01_konstant        Kalibrierte NHN-Achse + Stationen, 2 waagrechte blaue Wasserlinien (HGW, MGW)
  ls02_geneigt         Geneigte/polygonale Wasserlinien (Bemessungswasserstand, GW 14.05.2024) mit Stuetzpunkten
  ls03_text_abgleich   Berichtstext + Laengsschnitt: 1x Uebereinstimmung (+/-5 cm -> 1 Eintrag), 1x Widerspruch (-> 2 + Hinweis)
  ls04_fallen          4 Fallen -> 0 Wasserlinien: blaue Linie ohne Beschriftung, Gelaendelinie (GOK),
                       blaue Schichtgrenze, mehrdeutige Beschriftung 'MHGW' zwischen zwei nahen blauen Linien
  ls05_unkalibriert    Blaue gestrichelte Linie mit 'HGW', aber ohne kalibrierte NHN-Achse -> 0 Wasserlinien + Hinweis

    python synth_laengsschnitt.py <ausgabeordner>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pymupdf


def _nhn_zu_y(nhn: float, nhn_oben: float, y_oben: float, pt_pro_m: float) -> float:
    return y_oben + (nhn_oben - nhn) * pt_pro_m


def _zeichne_grundgeruest(
    page: pymupdf.Page,
    *,
    x0: float = 90.0,
    x1: float = 740.0,
    y_oben: float = 110.0,
    nhn_oben: float = 50.0,
    nhn_unten: float = 36.0,
    nhn_schritt: float = 2.0,
    pt_pro_m: float = 25.0,
    mit_nhn_achse: bool = True,
    mit_stationen: bool = True,
    station_max: float = 200.0,
    gok_punkte: list[tuple[float, float]] | None = None,
    bohrungen: list[tuple[str, float, float, list[float]]] | None = None,
) -> dict:
    """Zeichnet Achsen, Bohrungssaeulen und Gelaendelinie; gibt Achsenparameter zurueck."""
    y_unten = _nhn_zu_y(nhn_unten, nhn_oben, y_oben, pt_pro_m)
    page.insert_text((x0, 55), "Geologischer Längsschnitt A–A'", fontsize=11)

    if mit_nhn_achse:
        for ax_x, align_dx in ((x0 - 15, -36), (x1 + 15, 6)):
            page.draw_line((ax_x, y_oben), (ax_x, y_unten), color=(0, 0, 0), width=0.6)
            v = nhn_oben
            while v >= nhn_unten - 1e-6:
                yy = _nhn_zu_y(v, nhn_oben, y_oben, pt_pro_m)
                page.draw_line((ax_x - 3, yy), (ax_x + 3, yy), color=(0, 0, 0), width=0.5)
                page.insert_text((ax_x + align_dx, yy + 2.2), f"{v:.2f}".replace(".", ","), fontsize=6.5)
                v -= nhn_schritt
        page.insert_text((x0 - 52, y_oben - 12), "m NHN", fontsize=6.5)

    if mit_stationen:
        y_st = y_unten + 24
        page.draw_line((x0, y_st), (x1, y_st), color=(0, 0, 0), width=0.6)
        n_st = 5
        for i in range(n_st):
            st = station_max * i / (n_st - 1)
            xx = x0 + (x1 - x0) * i / (n_st - 1)
            page.draw_line((xx, y_st - 3), (xx, y_st + 3), color=(0, 0, 0), width=0.5)
            km = int(st // 1000)
            rest = int(round(st % 1000))
            page.insert_text((xx - 12, y_st + 12), f"{km}+{rest:03d}", fontsize=6.5)

    # Bohrungssaeulen (schmale Rechtecke)
    if bohrungen:
        for code, frac_x, gok, grenzen_t in bohrungen:
            bx = x0 + (x1 - x0) * frac_x
            yt = _nhn_zu_y(gok, nhn_oben, y_oben, pt_pro_m)
            yb = _nhn_zu_y(gok - grenzen_t[-1], nhn_oben, y_oben, pt_pro_m)
            page.draw_line((bx - 6, yt), (bx - 6, yb), color=(0, 0, 0), width=0.7)
            page.draw_line((bx + 6, yt), (bx + 6, yb), color=(0, 0, 0), width=0.7)
            page.draw_line((bx - 6, yt), (bx + 6, yt), color=(0, 0, 0), width=0.7)
            for t in grenzen_t:
                yg = _nhn_zu_y(gok - t, nhn_oben, y_oben, pt_pro_m)
                page.draw_line((bx - 6, yg), (bx + 6, yg), color=(0, 0, 0), width=0.5)
            page.insert_text((bx - 8, yt - 14), code, fontsize=7)

    # Gelaendelinie (GOK, schwarz durchgezogen)
    if gok_punkte:
        pts = [
            pymupdf.Point(x0 + (x1 - x0) * fx, _nhn_zu_y(h, nhn_oben, y_oben, pt_pro_m))
            for fx, h in gok_punkte
        ]
        page.draw_polyline(pts, color=(0, 0, 0), width=1.0)
        page.insert_text((pts[-1].x + 4, pts[-1].y + 2), "GOK", fontsize=6.5)

    return {"x0": x0, "x1": x1, "y_oben": y_oben, "nhn_oben": nhn_oben, "pt_pro_m": pt_pro_m, "station_max": station_max}


def build(out: Path) -> list[str]:
    """Erzeugt alle synthetischen Laengsschnitte (PDF + Wahrheit JSON) in ``out``."""
    out.mkdir(parents=True, exist_ok=True)
    made: list[str] = []

    def speichern(name: str, doc: pymupdf.Document, wasserlinien: list[dict], hinweis: str,
                  text_wasserstaende: list[dict] | None = None):
        pdf_pfad = out / f"{name}.pdf"
        doc.save(pdf_pfad)
        doc.close()
        sha = hashlib.sha256(pdf_pfad.read_bytes()).hexdigest()
        gt = {
            "file": pdf_pfad.name,
            "sha256": sha,
            "source": "synthetisch (services/extractor/synth_laengsschnitt.py)",
            "notes": hinweis,
            "boreholes": [],
            "wasserlinien": wasserlinien,
        }
        if text_wasserstaende is not None:
            gt["text_wasserstaende"] = text_wasserstaende
        (out / f"{name}.json").write_text(json.dumps(gt, indent=1, ensure_ascii=False), encoding="utf-8")
        made.append(name)

    bohr_std = [("B 1", 0.15, 47.0, [2.0, 5.5, 9.0]), ("B 2", 0.50, 47.5, [2.2, 6.0, 9.5]),
                ("B 3", 0.85, 46.8, [1.8, 5.0, 8.8])]
    gok_std = [(0.0, 46.8), (0.15, 47.0), (0.50, 47.5), (0.85, 46.8), (1.0, 46.6)]

    # ls01: Zwei konstante waagrechte blaue gestrichelte Wasserlinien (HGW, MGW)
    doc = pymupdf.open()
    p = doc.new_page(width=842, height=595)
    g = _zeichne_grundgeruest(p, gok_punkte=gok_std, bohrungen=bohr_std)
    for art, hoehe, seite_lbl in (("HGW", 42.50, "rechts"), ("MGW", 40.20, "links")):
        yy = _nhn_zu_y(hoehe, g["nhn_oben"], g["y_oben"], g["pt_pro_m"])
        p.draw_line((g["x0"], yy), (g["x1"], yy), color=(0.0, 0.25, 0.9), width=0.9, dashes="[6 3] 0")
        lx = g["x1"] - 32 if seite_lbl == "rechts" else g["x0"] + 6
        p.insert_text((lx, yy - 3), art, fontsize=7.5, color=(0.0, 0.25, 0.9))
    speichern(
        "ls01_konstant", doc,
        [{"art": "HGW", "nhn": 42.50, "seite": 1, "konstant": True},
         {"art": "MGW", "nhn": 40.20, "seite": 1, "konstant": True}],
        "Synthetisch: 2 waagrechte blaue gestrichelte Wasserlinien (HGW 42.50, MGW 40.20 m NHN)",
    )

    # ls02: Geneigte Wasserlinien (Bemessungswasserstand + GW mit Datum) mit Stationen
    doc = pymupdf.open()
    p = doc.new_page(width=842, height=595)
    g = _zeichne_grundgeruest(p, nhn_oben=62.0, nhn_unten=48.0, station_max=300.0,
                              gok_punkte=[(0.0, 60.0), (0.5, 59.5), (1.0, 58.8)],
                              bohrungen=[("B 1", 0.15, 59.8, [2.0, 6.0, 9.0]), ("B 2", 0.85, 59.0, [2.0, 5.5, 8.5])])
    bem_pts = [(0.0, 58.40), (0.5, 57.65), (1.0, 56.90)]
    gw_pts = [(0.0, 55.80), (0.5, 55.20), (1.0, 54.60)]
    for lbl, pts, dash in (("Bemessungswasserstand", bem_pts, "[8 3] 0"), ("GW 14.05.2024", gw_pts, "[4 2] 0")):
        ppts = [pymupdf.Point(g["x0"] + (g["x1"] - g["x0"]) * fx, _nhn_zu_y(h, g["nhn_oben"], g["y_oben"], g["pt_pro_m"]))
                for fx, h in pts]
        p.draw_polyline(ppts, color=(0.0, 0.2, 0.85), width=0.9, dashes=dash)
        p.insert_text((ppts[0].x + 8, ppts[0].y - 4), lbl, fontsize=7.5, color=(0.0, 0.2, 0.85))
    speichern(
        "ls02_geneigt", doc,
        [
            {"art": "Bemessungswasserstand", "seite": 1, "konstant": False,
             "stuetzpunkte": [{"station": 0.0, "nhn": 58.40}, {"station": 150.0, "nhn": 57.65}, {"station": 300.0, "nhn": 56.90}]},
            {"art": "GW", "datum": "2024-05-14", "seite": 1, "konstant": False,
             "stuetzpunkte": [{"station": 0.0, "nhn": 55.80}, {"station": 150.0, "nhn": 55.20}, {"station": 300.0, "nhn": 54.60}]},
        ],
        "Synthetisch: 2 geneigte Wasserlinien (Bemessungswasserstand + GW 14.05.2024) mit Stationen",
    )

    # ls03: Abgleich Text <-> Laengsschnitt (1x gleich +/-5 cm -> 1 Eintrag; 1x Widerspruch -> 2 Eintraege + Hinweis)
    doc = pymupdf.open()
    p0 = doc.new_page(width=595, height=842)
    p0.insert_text((70, 100), "4. Grundwasserverhaeltnisse", fontsize=11)
    p0.insert_text((70, 130), "Der Bemessungswasserstand liegt bei +43,20 m NHN.", fontsize=9)
    p0.insert_text((70, 150), "Der HGW wird mit +42,80 m NHN angegeben.", fontsize=9)
    p1 = doc.new_page(width=842, height=595)
    g = _zeichne_grundgeruest(p1, gok_punkte=gok_std, bohrungen=bohr_std)
    for lbl, hoehe in (("Bemessungswasserstand", 43.22), ("HGW", 42.10)):
        yy = _nhn_zu_y(hoehe, g["nhn_oben"], g["y_oben"], g["pt_pro_m"])
        p1.draw_line((g["x0"], yy), (g["x1"], yy), color=(0.0, 0.2, 0.9), width=0.9, dashes="[6 3] 0")
        p1.insert_text((g["x0"] + 10, yy - 3), lbl, fontsize=7.5, color=(0.0, 0.2, 0.9))
    speichern(
        "ls03_text_abgleich", doc,
        [{"art": "Bemessungswasserstand", "nhn": 43.22, "seite": 2, "konstant": True},
         {"art": "HGW", "nhn": 42.10, "seite": 2, "konstant": True}],
        "Synthetisch: Text + Laengsschnitt (Bemessungswasserstand gleich +/-5 cm -> 1 Eintrag; HGW Widerspruch -> 2 + Hinweis)",
        text_wasserstaende=[{"art": "Bemessungswasserstand", "nhn": 43.20, "seite": 1},
                            {"art": "HGW", "nhn": 42.80, "seite": 1}],
    )

    # ls04: Alle 4 Fallen -> 0 Wasserlinien erlaubt
    doc = pymupdf.open()
    p = doc.new_page(width=842, height=595)
    g = _zeichne_grundgeruest(p, gok_punkte=gok_std, bohrungen=bohr_std)
    # Falle 1: blaue gestrichelte Linie OHNE Beschriftung
    y_f1 = _nhn_zu_y(44.0, g["nhn_oben"], g["y_oben"], g["pt_pro_m"])
    p.draw_line((g["x0"], y_f1), (g["x1"], y_f1), color=(0.0, 0.2, 0.9), width=0.9, dashes="[5 3] 0")
    # Falle 2: blaue Gelaendelinie (liegt auf GOK der Bohrungen) mit Beschriftung 'HGW' daneben
    gok_pts_px = [pymupdf.Point(g["x0"] + (g["x1"] - g["x0"]) * fx, _nhn_zu_y(h, g["nhn_oben"], g["y_oben"], g["pt_pro_m"]))
                  for fx, h in gok_std]
    p.draw_polyline(gok_pts_px, color=(0.0, 0.2, 0.9), width=0.8, dashes="[4 2] 0")
    # Falle 3: Schichtgrenze in Blau durch die Grenzen der Bohrungen (Tiefe 5.5/6.0/5.0 -> 41.5/41.5/41.8)
    sg_pts = [(0.0, 41.5), (0.15, 41.5), (0.50, 41.5), (0.85, 41.8), (1.0, 41.8)]
    p.draw_polyline([pymupdf.Point(g["x0"] + (g["x1"] - g["x0"]) * fx, _nhn_zu_y(h, g["nhn_oben"], g["y_oben"], g["pt_pro_m"]))
                     for fx, h in sg_pts], color=(0.0, 0.3, 0.85), width=0.8)
    p.insert_text((g["x0"] + 15, _nhn_zu_y(41.5, g["nhn_oben"], g["y_oben"], g["pt_pro_m"]) - 3), "Sand / Ton", fontsize=7)
    # Falle 4: Beschriftung 'MHGW' mehrdeutig mittig zwischen zwei nahen blauen Linien (4 pt Abstand)
    y_a = _nhn_zu_y(39.2, g["nhn_oben"], g["y_oben"], g["pt_pro_m"])
    y_b = y_a + 5.0
    p.draw_line((g["x0"], y_a), (g["x1"], y_a), color=(0.0, 0.2, 0.9), width=0.8, dashes="[5 3] 0")
    p.draw_line((g["x0"], y_b), (g["x1"], y_b), color=(0.0, 0.2, 0.9), width=0.8, dashes="[5 3] 0")
    p.insert_text((g["x0"] + 20, (y_a + y_b) / 2 + 2), "MHGW", fontsize=7, color=(0.0, 0.2, 0.9))
    speichern(
        "ls04_fallen", doc, [],
        "Fallen (0 Wasserlinien): unbeschriftete blaue Linie, Gelaendelinie, blaue Schichtgrenze, mehrdeutiges 'MHGW'",
    )

    # ls05: Unkalibriert (keine NHN-Achse) -> 0 Wasserlinien + Hinweis
    doc = pymupdf.open()
    p = doc.new_page(width=842, height=595)
    g = _zeichne_grundgeruest(p, mit_nhn_achse=False, mit_stationen=True, gok_punkte=gok_std, bohrungen=bohr_std)
    yy = _nhn_zu_y(42.5, g["nhn_oben"], g["y_oben"], g["pt_pro_m"])
    p.draw_line((g["x0"], yy), (g["x1"], yy), color=(0.0, 0.2, 0.9), width=0.9, dashes="[6 3] 0")
    p.insert_text((g["x0"] + 10, yy - 3), "HGW", fontsize=7.5, color=(0.0, 0.2, 0.9))
    speichern(
        "ls05_unkalibriert", doc, [],
        "Falle (0 Wasserlinien): HGW-Linie ohne kalibrierte NHN-Hoehenachse -> nicht uebernommen, Hinweis",
    )

    return made


if __name__ == "__main__":
    for n in build(Path(sys.argv[1])):
        print(n)
