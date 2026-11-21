"""Synthetische Stressfaelle fuer Sondierungen (DPH und CPT) mit bekannter Grundwahrheit.

Die acht Faelle decken die zentralen Extraktions- und Falsch-Positiv-Pruefungen ab:
- s01_dph_diagramm: Vektor-Rammdiagramm (M 1:50) mit Gitter und Endtiefen-Angabe
- s02_dph_tabelle: linierte 3-Spalten-Tabelle mit absichtlicher Tiefenluecke (2,10-2,30 m)
- s03_dph_laengsschnitt: DPH im Laengsschnitt (H 1:100) auf gemeinsamer NHN-Skala ohne lokales Lineal
- s04_cpt_linear_log: Drucksondierung (CPT) mit linearer q_c- und logarithmischer f_s-Achse
- s05_zensiert: abgeschnittene Rammschlagzahlen (> 50, N10 > 50) am rechten Rand
- s06_zweiseitig: ueber zwei Seiten fortgesetztes Rammdiagramm (0-5 m und 5-9 m)
- s07_falle_bohrprofil_lineal: Falle L14 (Bohrprofile mit Tiefen-/Hoehenleiste ohne Sondierung)
- s08_falle_labortabelle: Falle Labortabelle (DIN EN ISO 17892 statt Schlagzahlen)

    python services/extractor/stress_sondierungen.py <ausgabeordner>
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import tempfile
from pathlib import Path

import pymupdf

PT_PER_M_1_1 = 1000.0 / 25.4 * 72.0  # 1 m Natur bei M 1:1 in PDF-Punkt (2834,6457 pt/m)

SCHRAFFUR_BODEN = {
    "Mutterboden": "diag",
    "Sand": "dots",
    "Kies": "circles",
    "Schluff": "vticks",
    "Ton": "hdash",
}


def _fmt(wert: float, dezimal: str = ",", nachkomma: int = 2) -> str:
    return f"{wert:.{nachkomma}f}".replace(".", dezimal)


def _text_zentriert_x(
    seite: pymupdf.Page,
    x_mitte: float,
    y_basis: float,
    text: str,
    schriftgroesse: float,
    farbe: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    breite = pymupdf.get_text_length(text, fontsize=schriftgroesse)
    seite.insert_text((x_mitte - breite / 2.0, y_basis), text, fontsize=schriftgroesse, color=farbe)


def _text_rechts_y(
    seite: pymupdf.Page,
    x_rechts: float,
    y_mitte: float,
    text: str,
    schriftgroesse: float,
    farbe: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    breite = pymupdf.get_text_length(text, fontsize=schriftgroesse)
    seite.insert_text((x_rechts - breite, y_mitte + 0.39 * schriftgroesse), text, fontsize=schriftgroesse, color=farbe)


def _linie(
    seite: pymupdf.Page,
    a: tuple[float, float],
    b: tuple[float, float],
    breite: float = 0.6,
    farbe: tuple[float, float, float] = (0.0, 0.0, 0.0),
    strichmuster: str | None = None,
) -> None:
    seite.draw_line(pymupdf.Point(*a), pymupdf.Point(*b), color=farbe, width=breite, dashes=strichmuster)


def _schraffur(seite: pymupdf.Page, rechteck: pymupdf.Rect, art: str) -> None:
    """Zeichnet geotechnische Schraffurmuster in ein Schichtrechteck."""
    form = seite.new_shape()
    schritt = 6.0
    ys = [rechteck.y0 + schritt / 2.0 + i * schritt for i in range(int(rechteck.height // schritt))]
    xs = [rechteck.x0 + schritt / 2.0 + i * schritt for i in range(int(rechteck.width // schritt))]
    if art == "dots":
        for y in ys:
            for x in xs:
                form.draw_circle(pymupdf.Point(x, y), 0.45)
        form.finish(color=None, fill=(0.0, 0.0, 0.0))
    elif art == "circles":
        for y in ys:
            for x in xs:
                form.draw_circle(pymupdf.Point(x, y), 1.6)
        form.finish(color=(0.0, 0.0, 0.0), width=0.3)
    elif art == "hdash":
        for y in ys:
            form.draw_line(pymupdf.Point(rechteck.x0, y), pymupdf.Point(rechteck.x1, y))
        form.finish(color=(0.0, 0.0, 0.0), width=0.3, dashes="[3 2] 0")
    elif art == "vticks":
        for y in ys:
            for x in xs:
                form.draw_line(pymupdf.Point(x, y - 2.0), pymupdf.Point(x, y + 2.0))
        form.finish(color=(0.0, 0.0, 0.0), width=0.3)
    elif art == "diag":
        for x in range(int(rechteck.x0 - rechteck.height), int(rechteck.x1), 5):
            a = pymupdf.Point(x, rechteck.y1)
            b = pymupdf.Point(x + rechteck.height, rechteck.y0)
            t0 = max(0.0, (rechteck.x0 - a.x) / rechteck.height)
            t1 = min(1.0, (rechteck.x1 - a.x) / rechteck.height)
            if t1 > t0:
                form.draw_line(a + (b - a) * t0, a + (b - a) * t1)
        form.finish(color=(0.0, 0.0, 0.0), width=0.3)
    form.commit()


def _bohrsaeule_zeichnen(
    seite: pymupdf.Page,
    x0: float,
    y_gok: float,
    ppm: float,
    code: str,
    gok: float,
    schichten: list[tuple[float, str, str]],
    saeulenbreite: float = 22.0,
    kopf_y: float | None = None,
    mit_grundwasser: float | None = None,
) -> None:
    """Zeichnet eine kompakte Bohrsaeule fuer Laengsschnitt und L14-Falle."""
    endtiefe = schichten[-1][0]
    y_ende = y_gok + endtiefe * ppm
    y_titel = kopf_y if kopf_y is not None else y_gok - 38.0
    seite.insert_text((x0 - 4.0, y_titel), code, fontsize=9.5)
    seite.insert_text((x0 - 12.0, y_gok - 10.0), f"+{_fmt(gok)} m NHN", fontsize=6.5)

    _linie(seite, (x0, y_gok), (x0, y_ende), 0.8)
    _linie(seite, (x0 + saeulenbreite, y_gok), (x0 + saeulenbreite, y_ende), 0.8)
    _linie(seite, (x0, y_gok), (x0 + saeulenbreite, y_gok), 0.8)

    vorher = 0.0
    for unterkante, bodenart, beschreibung in schichten:
        y0 = y_gok + vorher * ppm
        y1 = y_gok + unterkante * ppm
        _schraffur(seite, pymupdf.Rect(x0, y0, x0 + saeulenbreite, y1), SCHRAFFUR_BODEN.get(bodenart, "dots"))
        _linie(seite, (x0 - 8.0, y1), (x0 + saeulenbreite, y1), 0.6)
        _text_rechts_y(seite, x0 - 10.0, y1, _fmt(unterkante), 6.0)
        seite.insert_text((x0 + saeulenbreite + 6.0, (y0 + y1) / 2.0 + 2.2), beschreibung, fontsize=6.5)
        vorher = unterkante

    if mit_grundwasser is not None:
        yg = y_gok + mit_grundwasser * ppm
        gx = x0 + saeulenbreite + 4.0
        seite.draw_polyline(
            [(gx, yg - 6.0), (gx + 7.0, yg - 6.0), (gx + 3.5, yg), (gx, yg - 6.0)],
            color=(0.0, 0.0, 1.0),
            fill=(0.0, 0.0, 1.0),
            closePath=True,
            width=0.4,
        )
        _linie(seite, (x0 + saeulenbreite, yg), (gx + 10.0, yg), 0.4, farbe=(0.0, 0.0, 1.0))
        seite.insert_text((gx + 11.0, yg - 1.5), _fmt(mit_grundwasser), fontsize=6.0, color=(0.0, 0.0, 1.0))


def _wert_nummer(eintrag: int | float | dict) -> float:
    if isinstance(eintrag, dict):
        return float(eintrag["wert"])
    return float(eintrag)


def _zeichne_dph_treppenkurve(
    seite: pymupdf.Page,
    x0: float,
    y_oben: float,
    rahmen_breite: float,
    x_max: float,
    ppm: float,
    schritte: list[tuple[float, float, int | dict]],
    tiefen_start: float = 0.0,
    strichbreite: float = 1.0,
) -> None:
    """Zeichnet jeden 10-cm-Schritt mit eigenem vertikalem Segment fuer saubere Treppenerkennung."""
    punkte: list[tuple[float, float]] = []
    for t_oben, t_unten, rohwert in schritte:
        wert = min(_wert_nummer(rohwert), x_max)
        x = x0 + (wert / x_max) * rahmen_breite
        y0 = y_oben + (t_oben - tiefen_start) * ppm
        y1 = y_oben + (t_unten - tiefen_start) * ppm
        punkte.append((x, y0))
        punkte.append((x, y1))
    seite.draw_polyline(punkte, color=(0.0, 0.0, 0.0), width=strichbreite, closePath=False)


def _validiere_wahrheit(wahrheit: dict, pdf_pfad: Path, dok: pymupdf.Document) -> None:
    """Prueft Konsistenz zwischen erzeugtem PDF und Grundwahrheits-JSON."""
    erwartete_schluessel = {"file", "source", "sha256", "transkribiert_von", "notes", "sondierungen"}
    if set(wahrheit.keys()) != erwartete_schluessel:
        raise ValueError(f"{pdf_pfad.name}: unerwartete JSON-Schluessel {sorted(wahrheit.keys())}")
    if wahrheit["file"] != pdf_pfad.name:
        raise ValueError(f"{pdf_pfad.name}: Dateiname stimmt nicht ({wahrheit['file']})")
    if wahrheit["source"] != "synthetisch" or wahrheit["transkribiert_von"] != "synthetisch":
        raise ValueError(f"{pdf_pfad.name}: source/transkribiert_von muessen 'synthetisch' sein")
    if not re.fullmatch(r"[0-9a-f]{64}", wahrheit["sha256"]):
        raise ValueError(f"{pdf_pfad.name}: ungueltiger sha256")
    tatsaechlicher_hash = hashlib.sha256(pdf_pfad.read_bytes()).hexdigest()
    if wahrheit["sha256"] != tatsaechlicher_hash:
        raise ValueError(f"{pdf_pfad.name}: sha256 weicht von PDF-Bytes ab")
    if not wahrheit["notes"]:
        raise ValueError(f"{pdf_pfad.name}: leere notes")

    seitenzahl = dok.page_count
    sond_schluessel = {
        "code",
        "art",
        "seite",
        "auch_auf_seiten",
        "form",
        "ansatzhoehe",
        "endtiefe",
        "werte",
        "stichprobe",
        "unsicher",
    }
    for s in wahrheit["sondierungen"]:
        if set(s.keys()) != sond_schluessel:
            raise ValueError(f"{pdf_pfad.name}: fehlende Schluessel in {s.get('code')}")
        if not (1 <= s["seite"] <= seitenzahl):
            raise ValueError(f"{pdf_pfad.name}: seite {s['seite']} ausserhalb 1..{seitenzahl}")
        for ap in s["auch_auf_seiten"]:
            if not (1 <= ap <= seitenzahl) or ap == s["seite"]:
                raise ValueError(f"{pdf_pfad.name}: ungueltige Folgeseite {ap}")
        if s["form"] not in {"diagramm", "tabelle", "laengsschnitt"}:
            raise ValueError(f"{pdf_pfad.name}: ungueltige form {s['form']}")
        if s["endtiefe"] <= 0 or not s["werte"]:
            raise ValueError(f"{pdf_pfad.name}: leere Werte oder Endtiefe <= 0")
        if s["art"] == "DPH":
            vorher = -1e-9
            for zeile in s["werte"]:
                t_o, t_u, _ = zeile
                if not (0.0 <= t_o < t_u) or t_o < vorher - 1e-9:
                    raise ValueError(f"{pdf_pfad.name}: nicht-monotone DPH-Tiefe {zeile}")
                vorher = t_u
            if abs(s["werte"][-1][1] - s["endtiefe"]) > 1e-6:
                raise ValueError(f"{pdf_pfad.name}: Endtiefe stimmt nicht mit letzter DPH-Zeile ueberein")
        elif s["art"] == "CPT":
            vorher = -1e-9
            for zeile in s["werte"]:
                if zeile[0] <= vorher:
                    raise ValueError(f"{pdf_pfad.name}: nicht-monotone CPT-Tiefe {zeile}")
                vorher = zeile[0]
            if abs(s["werte"][-1][0] - s["endtiefe"]) > 1e-6:
                raise ValueError(f"{pdf_pfad.name}: Endtiefe stimmt nicht mit letzter CPT-Zeile ueberein")
        soll_sp = min(10, len(s["werte"]))
        if len(s["stichprobe"]) != soll_sp:
            raise ValueError(f"{pdf_pfad.name}: erwartet {soll_sp} Stichproben, gefunden {len(s['stichprobe'])}")
        for sp in s["stichprobe"]:
            if not (1 <= sp["seite"] <= seitenzahl) or "pt" not in sp["lage"]:
                raise ValueError(f"{pdf_pfad.name}: ungueltige Stichprobe {sp}")


def _speichere(
    ordner: Path,
    name: str,
    dok: pymupdf.Document,
    sondierungen: list[dict],
    notes: str,
) -> str:
    pdf_pfad = ordner / f"{name}.pdf"
    dok.save(pdf_pfad)
    sha = hashlib.sha256(pdf_pfad.read_bytes()).hexdigest()
    wahrheit = {
        "file": f"{name}.pdf",
        "source": "synthetisch",
        "sha256": sha,
        "transkribiert_von": "synthetisch",
        "notes": notes,
        "sondierungen": sondierungen,
    }
    _validiere_wahrheit(wahrheit, pdf_pfad, dok)
    dok.close()
    (ordner / f"{name}.json").write_text(json.dumps(wahrheit, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return name


def _fall_s01_dph_diagramm(ordner: Path) -> str:
    dok = pymupdf.open()
    seite = dok.new_page(width=595, height=842)
    ppm = PT_PER_M_1_1 / 50.0  # M 1:50 = 56,6929 pt/m
    x0, y0, rahmen_b, rahmen_tiefe = 150.0, 150.0, 300.0, 7.0
    x1 = x0 + rahmen_b
    y1 = y0 + rahmen_tiefe * ppm
    x_max = 50.0

    seite.insert_text((60, 52), "Rammsondierung nach DIN EN ISO 22476-2", fontsize=8.5)
    seite.insert_text((x0, 80), "DPH 1", fontsize=12)
    seite.insert_text((x0, 96), "Ansatzhöhe: +59,17 m NHN", fontsize=8)
    seite.insert_text((330, 80), "Maßstab 1:50", fontsize=8)
    seite.insert_text((330, 96), "Endtiefe: 6,00 m", fontsize=8)
    _text_zentriert_x(seite, (x0 + x1) / 2.0, 126.0, "Schlagzahl N10 [Schläge / 10 cm]", 8.0)
    seite.insert_text((84, 142), "Tiefe [m]", fontsize=7.5)

    for n in (0, 10, 20, 30, 40, 50):
        xt = x0 + (n / x_max) * rahmen_b
        _linie(seite, (xt, y0 - 4.0), (xt, y0), 0.5)
        _text_zentriert_x(seite, xt, y0 - 7.0, str(n), 7.0)
        if 0 < n < 50:
            _linie(seite, (xt, y0), (xt, y1), 0.25, farbe=(0.82, 0.82, 0.82))

    for d in range(8):
        yt = y0 + d * ppm
        _linie(seite, (x0 - 4.0, yt), (x0, yt), 0.5)
        _text_rechts_y(seite, x0 - 7.0, yt, _fmt(float(d)), 7.0)
        if 0 < d < 7:
            _linie(seite, (x0, yt), (x1, yt), 0.25, farbe=(0.82, 0.82, 0.82))

    seite.draw_rect(pymupdf.Rect(x0, y0, x1, y1), color=(0.0, 0.0, 0.0), fill=None, width=0.8)

    n10_liste = [
        2, 2, 3, 3, 4, 5, 6, 6, 8, 9,
        10, 11, 12, 12, 14, 15, 16, 14, 13, 12,
        11, 12, 14, 17, 19, 21, 23, 24, 22, 20,
        18, 19, 22, 25, 27, 29, 30, 30, 32, 34,
        35, 36, 33, 31, 29, 28, 30, 33, 35, 37,
        38, 39, 40, 41, 42, 40, 39, 41, 42, 42,
    ]
    schritte = [(round(i * 0.1, 1), round((i + 1) * 0.1, 1), n) for i, n in enumerate(n10_liste)]
    _zeichne_dph_treppenkurve(seite, x0, y0, rahmen_b, x_max, ppm, schritte, strichbreite=1.0)
    seite.insert_text((x1 + 6.0, y0 + 6.0 * ppm + 2.5), "Endtiefe 6,00 m", fontsize=7.0)

    stichprobe = []
    for idx in (0, 6, 12, 18, 24, 30, 36, 42, 48, 59):
        t_o, t_u, n = schritte[idx]
        xs = x0 + (n / x_max) * rahmen_b
        ys = y0 + ((t_o + t_u) / 2.0) * ppm
        stichprobe.append({
            "tiefe": t_u,
            "wert": n,
            "seite": 1,
            "lage": f"Diagramm x={xs:.1f}, y={ys:.1f} pt",
        })

    sond = [{
        "code": "DPH 1",
        "art": "DPH",
        "seite": 1,
        "auch_auf_seiten": [],
        "form": "diagramm",
        "ansatzhoehe": 59.17,
        "endtiefe": 6.0,
        "werte": [list(z) for z in schritte],
        "stichprobe": stichprobe,
        "unsicher": [],
    }]
    return _speichere(
        ordner,
        "s01_dph_diagramm",
        dok,
        sond,
        "Vektor-DPH-Diagramm M 1:50 mit 60 Schritten (0,0-6,0 m) in 7,0-m-Rahmen und hellgrauem Gitter",
    )


def _fall_s02_dph_tabelle(ordner: Path) -> str:
    dok = pymupdf.open()
    seite = dok.new_page(width=595, height=842)

    seite.insert_text((60, 52), "Rammsondierung nach DIN EN ISO 22476-2 (Wertetabelle)", fontsize=8.5)
    seite.insert_text((60, 76), "Sondierung Nr.: DPH 4", fontsize=11)
    seite.insert_text((60, 94), "Sondierart: DPH", fontsize=8)
    seite.insert_text((220, 94), "Ansatzhöhe: +312,40 m NHN", fontsize=8)
    seite.insert_text((400, 94), "Endtiefe: 4,00 m", fontsize=8)

    spalten = [60.0, 155.0, 275.0, 525.0]
    y_oben = 120.0
    kopf_h = 20.0
    zeilen_h = 15.0

    # Absichtliche Tiefenluecke: 2,10, 2,20 und 2,30 m fehlen
    tiefen_unten = [round(i * 0.1, 1) for i in range(1, 21)] + [round(i * 0.1, 1) for i in range(24, 41)]
    n10_roh = [
        3, 4, 4, 5, 6, 7, 8, 9, 11, 10,
        12, 13, 14, 15, 16, 15, 17, 18, 19, 20,
        25, 26, 28, 27, 29, 30, 31, 33, 32, 34,
        35, 36, 34, 35, 37, 36, 38,
    ]
    zeilen = [(round(t - 0.1, 1), t, n) for t, n in zip(tiefen_unten, n10_roh)]

    kopf = ["Tiefe [m]", "N10 (Schlagzahl)", "Bemerkung"]
    for j, titel in enumerate(kopf):
        seite.insert_text((spalten[j] + 8.0, y_oben + 13.0), titel, fontsize=8.0)

    y_cur = y_oben + kopf_h
    for _, t_u, n in zeilen:
        seite.insert_text((spalten[0] + 10.0, y_cur + 11.0), _fmt(t_u), fontsize=7.5)
        seite.insert_text((spalten[1] + 14.0, y_cur + 11.0), str(n), fontsize=7.5)
        seite.insert_text((spalten[2] + 10.0, y_cur + 11.0), "-", fontsize=7.5)
        y_cur += zeilen_h

    y_unten = y_cur
    _linie(seite, (spalten[0], y_oben), (spalten[-1], y_oben), 0.7)
    _linie(seite, (spalten[0], y_oben + kopf_h), (spalten[-1], y_oben + kopf_h), 0.7)
    for k in range(len(zeilen) + 1):
        yk = y_oben + kopf_h + k * zeilen_h
        _linie(seite, (spalten[0], yk), (spalten[-1], yk), 0.5)
    for xs in spalten:
        _linie(seite, (xs, y_oben), (xs, y_unten), 0.5)

    stichprobe = []
    for idx in (0, 5, 10, 15, 19, 20, 24, 28, 32, 36):
        _, t_u, n = zeilen[idx]
        ys = y_oben + kopf_h + idx * zeilen_h + zeilen_h / 2.0
        stichprobe.append({
            "tiefe": t_u,
            "wert": n,
            "seite": 1,
            "lage": f"Tabelle Zeile {idx + 1} x={spalten[1] + 14.0:.1f}, y={ys:.1f} pt",
        })

    sond = [{
        "code": "DPH 4",
        "art": "DPH",
        "seite": 1,
        "auch_auf_seiten": [],
        "form": "tabelle",
        "ansatzhoehe": 312.4,
        "endtiefe": 4.0,
        "werte": [list(z) for z in zeilen],
        "stichprobe": stichprobe,
        "unsicher": [],
    }]
    return _speichere(
        ordner,
        "s02_dph_tabelle",
        dok,
        sond,
        "Linierte DPH-Tabelle (DPH 4, 37 Datenzeilen) mit absichtlicher "
        "Tiefenluecke 2,10-2,30 m (Sprung 2,00 -> 2,40 m)",
    )


def _fall_s03_dph_laengsschnitt(ordner: Path) -> str:
    dok = pymupdf.open()
    seite = dok.new_page(width=842, height=595)
    ppm = PT_PER_M_1_1 / 100.0  # H 1:100 = 28,3465 pt/m
    nhn_oben = 64.0
    y_oben = 120.0

    def y_nhn(hoehe: float) -> float:
        return y_oben + (nhn_oben - hoehe) * ppm

    seite.insert_text((50, 38), "Geotechnischer Längsschnitt   L 1:500, H 1:100", fontsize=10)
    seite.insert_text((42, 102), "Höhe [m NHN]", fontsize=7.5)

    x_achse = 95.0
    _linie(seite, (x_achse, y_nhn(64.0)), (x_achse, y_nhn(50.0)), 0.8)
    for nhn in range(64, 49, -1):
        yt = y_nhn(float(nhn))
        _linie(seite, (x_achse - 4.0, yt), (x_achse, yt), 0.5)
        _text_rechts_y(seite, x_achse - 6.0, yt, _fmt(float(nhn)), 6.5)

    # Stationsleiste unten
    _linie(seite, (x_achse, 542.0), (760.0, 542.0), 0.5)
    seite.insert_text((45, 545), "Station [m]", fontsize=6.5)
    for sx, slbl in ((180.0, "0+000"), (340.0, "0+050"), (500.0, "0+100"), (660.0, "0+150")):
        _linie(seite, (sx, 539.0), (sx, 545.0), 0.5)
        _text_zentriert_x(seite, sx, 554.0, slbl, 6.5)

    b1_schichten = [
        (0.4, "Mutterboden", "Mutterboden"),
        (2.2, "Sand", "Sand"),
        (4.5, "Kies", "Kies"),
        (6.0, "Ton", "Ton"),
    ]
    b2_schichten = [
        (0.3, "Mutterboden", "Mutterboden"),
        (1.8, "Sand", "Sand"),
        (4.0, "Schluff", "Schluff"),
        (6.5, "Ton", "Ton"),
    ]
    _bohrsaeule_zeichnen(seite, 180.0, y_nhn(61.8), ppm, "B 1", 61.8, b1_schichten, kopf_y=82.0)
    _bohrsaeule_zeichnen(seite, 620.0, y_nhn(60.4), ppm, "B 2", 60.4, b2_schichten, kopf_y=82.0)

    # DPH 3 bei wahrer NHN-Hoehe, Breite 90 pt (> 80 pt), OHNE lokales Tiefenlineal
    x_dph, b_dph, x_max = 380.0, 90.0, 40.0
    ansatz = 61.2
    endtiefe = 5.0
    y_dph_oben = y_nhn(ansatz)
    y_dph_unten = y_nhn(ansatz - endtiefe)

    seite.insert_text((x_dph, y_dph_oben - 36.0), "DPH 3", fontsize=9.5)
    seite.insert_text((x_dph, y_dph_oben - 23.0), "Ansatzhöhe: +61,20 m NHN", fontsize=7.0)
    _text_zentriert_x(seite, x_dph + b_dph / 2.0, y_dph_oben - 13.0, "N10", 6.5)

    for n in (0, 10, 20, 30, 40):
        xt = x_dph + (n / x_max) * b_dph
        _linie(seite, (xt, y_dph_oben - 3.0), (xt, y_dph_oben), 0.5)
        _text_zentriert_x(seite, xt, y_dph_oben - 4.0, str(n), 6.0)
        if 0 < n < 40:
            _linie(seite, (xt, y_dph_oben), (xt, y_dph_unten), 0.2, farbe=(0.82, 0.82, 0.82))

    seite.draw_rect(
        pymupdf.Rect(x_dph, y_dph_oben, x_dph + b_dph, y_dph_unten),
        color=(0.0, 0.0, 0.0),
        fill=None,
        width=0.8,
    )
    seite.insert_text((x_dph, y_dph_unten + 11.0), "Endtiefe: 5,00 m", fontsize=6.5)

    # Gelaendelinie nur zwischen den Aufschluessen
    gok_farbe = (0.45, 0.30, 0.15)
    _linie(seite, (x_achse, y_nhn(62.1)), (180.0, y_nhn(61.8)), 0.6, farbe=gok_farbe)
    _linie(seite, (202.0, y_nhn(61.8)), (x_dph, y_dph_oben), 0.6, farbe=gok_farbe)
    _linie(seite, (x_dph + b_dph, y_dph_oben), (620.0, y_nhn(60.4)), 0.6, farbe=gok_farbe)
    _linie(seite, (642.0, y_nhn(60.4)), (760.0, y_nhn(60.1)), 0.6, farbe=gok_farbe)

    n10_liste = [
        2, 3, 4, 4, 5, 6, 7, 8, 7, 9,
        10, 12, 13, 15, 14, 16, 18, 19, 17, 16,
        15, 17, 19, 21, 23, 24, 22, 20, 22, 25,
        27, 28, 30, 29, 31, 32, 34, 33, 31, 29,
        28, 30, 32, 34, 35, 36, 34, 33, 35, 36,
    ]
    schritte = [(round(i * 0.1, 1), round((i + 1) * 0.1, 1), n) for i, n in enumerate(n10_liste)]
    _zeichne_dph_treppenkurve(seite, x_dph, y_dph_oben, b_dph, x_max, ppm, schritte, strichbreite=0.8)

    stichprobe = []
    for idx in (0, 5, 10, 15, 20, 25, 30, 35, 42, 49):
        t_o, t_u, n = schritte[idx]
        xs = x_dph + (n / x_max) * b_dph
        ys = y_dph_oben + ((t_o + t_u) / 2.0) * ppm
        stichprobe.append({
            "tiefe": t_u,
            "wert": n,
            "seite": 1,
            "lage": f"Laengsschnitt x={xs:.1f}, y={ys:.1f} pt",
        })

    sond = [{
        "code": "DPH 3",
        "art": "DPH",
        "seite": 1,
        "auch_auf_seiten": [],
        "form": "laengsschnitt",
        "ansatzhoehe": ansatz,
        "endtiefe": endtiefe,
        "werte": [list(z) for z in schritte],
        "stichprobe": stichprobe,
        "unsicher": [],
    }]
    return _speichere(
        ordner,
        "s03_dph_laengsschnitt",
        dok,
        sond,
        "Laengsschnitt H 1:100 mit gemeinsamer NHN-Skala (64-50 m), "
        "Bohrungen B 1/B 2 und DPH 3 ohne lokales Tiefenlineal",
    )


def _fall_s04_cpt_linear_log(ordner: Path) -> str:
    dok = pymupdf.open()
    seite = dok.new_page(width=595, height=842)
    ppm = PT_PER_M_1_1 / 50.0  # M 1:50 = 56,6929 pt/m
    x0, y0, rahmen_b, endtiefe = 120.0, 180.0, 360.0, 8.0
    x1 = x0 + rahmen_b
    y1 = y0 + endtiefe * ppm

    blau = (0.0, 0.2, 0.8)
    rot = (0.8, 0.1, 0.1)

    seite.insert_text((60, 50), "Drucksondierung (CPT) nach DIN EN ISO 22476-1", fontsize=8.5)
    seite.insert_text((x0, 76), "CPT 1", fontsize=12)
    seite.insert_text((x0, 92), "Ansatzhöhe: +34,80 m NHN", fontsize=8)
    seite.insert_text((330, 76), "Maßstab 1:50", fontsize=8)
    seite.insert_text((330, 92), "Endtiefe: 8,00 m", fontsize=8)

    # Legende
    seite.draw_rect(pymupdf.Rect(x0, 104.0, x1, 128.0), color=(0.3, 0.3, 0.3), fill=None, width=0.5)
    _linie(seite, (x0 + 10.0, 116.0), (x0 + 45.0, 116.0), 1.4, farbe=blau)
    seite.insert_text((x0 + 52.0, 119.0), "q_c [MPa] (linear)", fontsize=7.5, color=blau)
    _linie(seite, (x0 + 190.0, 116.0), (x0 + 225.0, 116.0), 0.7, farbe=rot, strichmuster="[4 2] 0")
    seite.insert_text((x0 + 232.0, 119.0), "f_s [kPa] (log10)", fontsize=7.5, color=rot)

    # Linke Tiefenachse (0,00 .. 8,00)
    seite.insert_text((62, 172), "Tiefe [m]", fontsize=7.5)
    for d in range(9):
        yt = y0 + d * ppm
        _linie(seite, (x0 - 4.0, yt), (x0, yt), 0.5)
        _text_rechts_y(seite, x0 - 7.0, yt, _fmt(float(d)), 7.0)
        if 0 < d < 8:
            _linie(seite, (x0, yt), (x1, yt), 0.25, farbe=(0.85, 0.85, 0.85))

    # Obere lineare Achse q_c [MPa] (0..25)
    _text_zentriert_x(seite, (x0 + x1) / 2.0, 148.0, "q_c [MPa]", 8.0, farbe=blau)
    for qc in (0, 5, 10, 15, 20, 25):
        xt = x0 + (qc / 25.0) * rahmen_b
        _linie(seite, (xt, y0 - 4.0), (xt, y0), 0.5, farbe=blau)
        _text_zentriert_x(seite, xt, y0 - 8.0, str(qc), 7.0, farbe=blau)
        if 0 < qc < 25:
            _linie(seite, (xt, y0), (xt, y1), 0.2, farbe=(0.88, 0.88, 0.88))

    # Untere logarithmische Achse f_s [kPa] (0,1..100)
    for fs_wert, beschriftung in ((0.1, "0,1"), (1.0, "1"), (10.0, "10"), (100.0, "100")):
        xt = x0 + (math.log10(fs_wert) + 1.0) / 3.0 * rahmen_b
        _linie(seite, (xt, y1), (xt, y1 + 4.0), 0.5, farbe=rot)
        _text_zentriert_x(seite, xt, y1 + 13.0, beschriftung, 7.0, farbe=rot)
    _text_zentriert_x(seite, (x0 + x1) / 2.0, y1 + 27.0, "f_s [kPa] (log)", 8.0, farbe=rot)

    seite.draw_rect(pymupdf.Rect(x0, y0, x1, y1), color=(0.0, 0.0, 0.0), fill=None, width=0.8)

    # 41 Stuetzstellen im 0,20-m-Abstand
    qc_werte = [
        1.2, 1.5, 1.8, 2.4, 3.1, 4.5, 6.2, 7.8, 8.4, 7.9,
        6.5, 5.2, 4.1, 3.3, 2.8, 3.5, 5.4, 8.2, 11.5, 13.8,
        15.2, 16.4, 15.9, 14.1, 11.8, 9.4, 7.2, 6.0, 5.5, 6.8,
        9.2, 12.6, 15.8, 18.4, 20.1, 21.5, 22.0, 20.8, 19.2, 18.5, 19.0,
    ]
    fs_werte = [
        1.4, 1.8, 2.3, 3.0, 4.2, 6.5, 9.8, 13.5, 15.0, 14.2,
        12.0, 9.5, 8.2, 7.4, 6.8, 7.9, 11.2, 18.5, 28.0, 36.0,
        42.0, 48.0, 45.0, 39.0, 31.0, 24.0, 17.5, 14.0, 12.8, 16.2,
        25.0, 38.0, 52.0, 64.0, 74.0, 82.0, 85.0, 78.0, 69.0, 62.0, 65.0,
    ]

    punkte_qc = []
    punkte_fs = []
    werte = []
    for i, (qc, fs_w) in enumerate(zip(qc_werte, fs_werte)):
        tiefe = round(i * 0.2, 1)
        yt = y0 + tiefe * ppm
        x_qc = x0 + (qc / 25.0) * rahmen_b
        x_fs = x0 + (math.log10(fs_w) + 1.0) / 3.0 * rahmen_b
        punkte_qc.append((x_qc, yt))
        punkte_fs.append((x_fs, yt))
        werte.append([tiefe, qc, fs_w, None])

    oc_qc = dok.add_ocg("CPT_qc")
    oc_fs = dok.add_ocg("CPT_fs")
    seite.draw_polyline(punkte_qc, color=blau, width=1.4, closePath=False, oc=oc_qc)
    seite.draw_polyline(punkte_fs, color=rot, width=0.7, dashes="[4 2] 0", closePath=False, oc=oc_fs)

    stichprobe = []
    for idx in (0, 4, 8, 12, 16, 20, 24, 28, 34, 40):
        tiefe, qc, fs_w, _ = werte[idx]
        x_qc, yt = punkte_qc[idx]
        x_fs, _ = punkte_fs[idx]
        stichprobe.append({
            "tiefe": tiefe,
            "wert": {"q_c": qc, "f_s": fs_w},
            "seite": 1,
            "lage": f"Diagramm qc=({x_qc:.1f}, {yt:.1f}) pt, fs=({x_fs:.1f}, {yt:.1f}) pt",
        })

    sond = [{
        "code": "CPT 1",
        "art": "CPT",
        "seite": 1,
        "auch_auf_seiten": [],
        "form": "diagramm",
        "ansatzhoehe": 34.8,
        "endtiefe": endtiefe,
        "werte": werte,
        "stichprobe": stichprobe,
        "unsicher": [],
    }]
    return _speichere(
        ordner,
        "s04_cpt_linear_log",
        dok,
        sond,
        "CPT mit linearer q_c-Achse (0..25 MPa) oben, logarithmischer f_s-Achse (0,1..100 kPa) unten und 2 OCG-Kurven",
    )


def _zeichne_dph_seite(
    seite: pymupdf.Page,
    code_kopf: str,
    ansatzhoehe: float,
    x0: float,
    y0: float,
    rahmen_b: float,
    x_max: float,
    tiefen_start: float,
    tiefen_ende: float,
    ppm: float,
    schritte: list[tuple[float, float, int | dict]],
    fusszeile: str,
) -> None:
    """Hilfsfunktion fuer einseitige und mehrseitige DPH-Diagramme im Massstab 1:30."""
    x1 = x0 + rahmen_b
    y1 = y0 + (tiefen_ende - tiefen_start) * ppm

    seite.insert_text((60, 52), "Rammsondierung nach DIN EN ISO 22476-2", fontsize=8.5)
    seite.insert_text((x0, y0 - 44.0), code_kopf, fontsize=11.0)
    seite.insert_text((x0, y0 - 31.0), f"Ansatzhöhe: +{_fmt(ansatzhoehe)} m NHN", fontsize=8.0)
    _text_zentriert_x(seite, (x0 + x1) / 2.0, y0 - 19.0, "Schlagzahl N10 [Schläge / 10 cm]", 7.0)
    seite.insert_text((x0 - 48.0, y0 - 19.0), "Tiefe [m]", fontsize=6.5)

    for n in range(0, int(x_max) + 1, 10):
        xt = x0 + (n / x_max) * rahmen_b
        _linie(seite, (xt, y0 - 3.0), (xt, y0), 0.5)
        _text_zentriert_x(seite, xt, y0 - 5.0, str(n), 6.5)
        if 0 < n < x_max:
            _linie(seite, (xt, y0), (xt, y1), 0.25, farbe=(0.82, 0.82, 0.82))

    d_start_int = int(round(tiefen_start))
    d_ende_int = int(round(tiefen_ende))
    for d in range(d_start_int, d_ende_int + 1):
        yt = y0 + (d - tiefen_start) * ppm
        _linie(seite, (x0 - 4.0, yt), (x0, yt), 0.5)
        _text_rechts_y(seite, x0 - 6.0, yt, _fmt(float(d)), 6.5)
        if d_start_int < d < d_ende_int:
            _linie(seite, (x0, yt), (x1, yt), 0.25, farbe=(0.82, 0.82, 0.82))

    seite.draw_rect(pymupdf.Rect(x0, y0, x1, y1), color=(0.0, 0.0, 0.0), fill=None, width=0.7)
    _zeichne_dph_treppenkurve(
        seite,
        x0,
        y0,
        rahmen_b,
        x_max,
        ppm,
        schritte,
        tiefen_start=tiefen_start,
        strichbreite=1.2,
    )
    seite.insert_text((x0, y1 + 20.0), fusszeile, fontsize=7.5)


def _fall_s05_zensiert(ordner: Path) -> str:
    dok = pymupdf.open()
    seite = dok.new_page(width=595, height=842)
    ppm = PT_PER_M_1_1 / 30.0  # M 1:30 = 94,4882 pt/m
    x0, y0, rahmen_b, x_max = 120.0, 160.0, 280.0, 50.0
    ansatz = 54.2
    endtiefe = 4.0

    rohwerte: list[int | dict] = [
        3, 4, 6, 8, 7, 10, 12, 15, 14, 18,
        22, 25, 24, 28, 31, 35, 33, 38, 42, 44,
        41, 39,
        {"wert": 50, "zensiert": True},
        {"wert": 50, "zensiert": True},
        36, 32, 29, 27, 25, 28, 31, 34, 37, 40,
        43, 45, 47, 49,
        {"wert": 50, "zensiert": True},
        {"wert": 50, "zensiert": True},
    ]
    schritte = [(round(i * 0.1, 1), round((i + 1) * 0.1, 1), w) for i, w in enumerate(rohwerte)]

    _zeichne_dph_seite(
        seite,
        "DPH 5",
        ansatz,
        x0,
        y0,
        rahmen_b,
        x_max,
        0.0,
        endtiefe,
        ppm,
        schritte,
        "Endtiefe: 4,00 m (Rammabbruch bei N10 > 50)",
    )

    # Randtexte fuer zensierte Schritte (2,2-2,4 m und 3,8-4,0 m)
    rand_x = x0 + rahmen_b + 5.0
    for idx, hinweistext in ((22, "> 50"), (23, "> 50"), (38, "N10 > 50"), (39, "N10 > 50")):
        t_o, t_u, _ = schritte[idx]
        y_mitte = y0 + ((t_o + t_u) / 2.0) * ppm
        seite.insert_text((rand_x, y_mitte + 0.39 * 6.5), hinweistext, fontsize=6.5)

    stichprobe = []
    for idx in (0, 4, 9, 14, 19, 22, 23, 29, 35, 39):
        t_o, t_u, w = schritte[idx]
        xs = x0 + (min(_wert_nummer(w), x_max) / x_max) * rahmen_b
        ys = y0 + ((t_o + t_u) / 2.0) * ppm
        lage = f"Diagramm x={xs:.1f}, y={ys:.1f} pt"
        if isinstance(w, dict):
            lage = f"Diagramm (Randbeschriftung x={rand_x:.1f}) x={xs:.1f}, y={ys:.1f} pt"
        stichprobe.append({
            "tiefe": t_u,
            "wert": w,
            "seite": 1,
            "lage": lage,
        })

    sond = [{
        "code": "DPH 5",
        "art": "DPH",
        "seite": 1,
        "auch_auf_seiten": [],
        "form": "diagramm",
        "ansatzhoehe": ansatz,
        "endtiefe": endtiefe,
        "werte": [list(z) for z in schritte],
        "stichprobe": stichprobe,
        "unsicher": [],
    }]
    return _speichere(
        ordner,
        "s05_zensiert",
        dok,
        sond,
        "Zensierte Rammschlagzahlen bei 2,2-2,4 m ('> 50') und 3,8-4,0 m ('N10 > 50') am Achsenmaximum 50",
    )


def _fall_s06_zweiseitig(ordner: Path) -> str:
    dok = pymupdf.open()
    ppm = PT_PER_M_1_1 / 30.0  # M 1:30 = 94,4882 pt/m
    x0, y0, rahmen_b, x_max = 120.0, 150.0, 280.0, 50.0
    ansatz = 112.4
    endtiefe = 9.0

    n10_s1 = [
        4, 5, 5, 6, 7, 8, 8, 9, 10, 11,
        12, 13, 12, 14, 15, 16, 15, 14, 16, 17,
        18, 19, 20, 19, 21, 22, 23, 21, 20, 22,
        24, 25, 24, 26, 27, 25, 23, 24, 25, 26,
        27, 26, 25, 24, 26, 27, 28, 27, 26, 28,
    ]
    n10_s2 = [
        27, 29, 30, 31, 30, 32, 33, 34, 33, 35,
        36, 35, 34, 36, 37, 38, 39, 38, 37, 39,
        40, 41, 40, 42, 43, 41, 40, 42, 43, 44,
        43, 42, 44, 45, 44, 45, 46, 45, 44, 46,
    ]
    schritte_s1 = [(round(i * 0.1, 1), round((i + 1) * 0.1, 1), n) for i, n in enumerate(n10_s1)]
    schritte_s2 = [(round(5.0 + i * 0.1, 1), round(5.0 + (i + 1) * 0.1, 1), n) for i, n in enumerate(n10_s2)]

    seite1 = dok.new_page(width=595, height=842)
    _zeichne_dph_seite(
        seite1,
        "DPH 2",
        ansatz,
        x0,
        y0,
        rahmen_b,
        x_max,
        0.0,
        5.0,
        ppm,
        schritte_s1,
        "Fortsetzung siehe Seite 2 (ab 5,00 m)",
    )

    seite2 = dok.new_page(width=595, height=842)
    _zeichne_dph_seite(
        seite2,
        "DPH 2 (Fortsetzung)",
        ansatz,
        x0,
        y0,
        rahmen_b,
        x_max,
        5.0,
        9.0,
        ppm,
        schritte_s2,
        "Endtiefe: 9,00 m",
    )

    alle_schritte = schritte_s1 + schritte_s2
    stichprobe = []
    for idx in (4, 14, 24, 34, 48, 50, 59, 69, 79, 89):
        t_o, t_u, n = alle_schritte[idx]
        s_nr = 1 if idx < 50 else 2
        t_basis = 0.0 if s_nr == 1 else 5.0
        xs = x0 + (n / x_max) * rahmen_b
        ys = y0 + (((t_o + t_u) / 2.0) - t_basis) * ppm
        stichprobe.append({
            "tiefe": t_u,
            "wert": n,
            "seite": s_nr,
            "lage": f"Diagramm S.{s_nr} x={xs:.1f}, y={ys:.1f} pt",
        })

    sond = [{
        "code": "DPH 2",
        "art": "DPH",
        "seite": 1,
        "auch_auf_seiten": [2],
        "form": "diagramm",
        "ansatzhoehe": ansatz,
        "endtiefe": endtiefe,
        "werte": [list(z) for z in alle_schritte],
        "stichprobe": stichprobe,
        "unsicher": [],
    }]
    return _speichere(
        ordner,
        "s06_zweiseitig",
        dok,
        sond,
        "Zweiseitige DPH 2 (Seite 1: 0,0-5,0 m; Seite 2: 5,0-9,0 m mit Lineal ab 5,00 m), als eine Sondierung vereint",
    )


def _fall_s07_falle_bohrprofil_lineal(ordner: Path) -> str:
    dok = pymupdf.open()
    seite = dok.new_page(width=595, height=842)
    ppm = PT_PER_M_1_1 / 50.0  # M 1:50 = 56,6929 pt/m
    y_oben = 140.0
    endtiefe = 6.5

    seite.insert_text((50, 50), "Geotechnischer Schnitt: B 1 - B 2    L 1:500, H 1:50", fontsize=10)
    seite.draw_rect(pymupdf.Rect(40.0, 80.0, 555.0, 590.0), color=(0.0, 0.0, 0.0), fill=None, width=0.5)

    # Hoehenleiste mit Dreiecken links (45,20 .. 39,20 m NHN)
    ex = 65.0
    for i in range(7):
        yt = y_oben + i * ppm
        seite.draw_polyline(
            [(ex, yt - 5.0), (ex + 6.0, yt - 5.0), (ex + 3.0, yt), (ex, yt - 5.0)],
            color=(0.0, 0.0, 0.0),
            closePath=True,
            width=0.4,
        )
        seite.insert_text((ex + 9.0, yt + 1.5), _fmt(45.2 - i), fontsize=5.5)

    # Arithmetisches Tiefenlineal (0,00 .. 6,50 m in 0,50-m-Schritten)
    rx = 132.0
    _linie(seite, (rx, y_oben), (rx, y_oben + endtiefe * ppm), 0.5)
    seite.insert_text((rx - 26.0, y_oben - 10.0), "Tiefe [m]", fontsize=6.5)
    for i in range(14):
        d = i * 0.5
        yt = y_oben + d * ppm
        _linie(seite, (rx - 4.0, yt), (rx, yt), 0.4)
        _text_rechts_y(seite, rx - 6.0, yt, _fmt(d), 6.0)

    schichten = [
        (0.3, "Mutterboden", "Mutterboden, humos"),
        (1.8, "Sand", "Feinsand, braun"),
        (3.4, "Kies", "Kies, sandig"),
        (5.0, "Schluff", "Schluff, tonig"),
        (6.5, "Ton", "Ton, steif"),
    ]
    _bohrsaeule_zeichnen(
        seite,
        195.0,
        y_oben,
        ppm,
        "B 1",
        45.2,
        schichten,
        saeulenbreite=24.0,
        kopf_y=y_oben - 30.0,
        mit_grundwasser=2.4,
    )
    _bohrsaeule_zeichnen(
        seite,
        395.0,
        y_oben,
        ppm,
        "B 2",
        45.5,
        schichten,
        saeulenbreite=24.0,
        kopf_y=y_oben - 30.0,
    )

    # Horizontale Entfernungsachse (0 .. 50 m)
    y_entf = 555.0
    _linie(seite, (150.0, y_entf), (450.0, y_entf), 0.5)
    seite.insert_text((70, y_entf + 3.0), "Entfernung [m]", fontsize=6.5)
    for m in range(0, 51, 10):
        xt = 150.0 + (m / 50.0) * 300.0
        _linie(seite, (xt, y_entf), (xt, y_entf + 4.0), 0.5)
        _text_zentriert_x(seite, xt, y_entf + 13.0, str(m), 6.5)

    return _speichere(
        ordner,
        "s07_falle_bohrprofil_lineal",
        dok,
        [],
        "Falle L14: Bohrprofile B 1 und B 2 mit Tiefenlineal (0,00-6,50 m), "
        "Hoehenleiste und Entfernungsachse ohne Sondierung -> 0 Sondierungen",
    )


def _fall_s08_falle_labortabelle(ordner: Path) -> str:
    dok = pymupdf.open()
    seite = dok.new_page(width=595, height=842)

    seite.insert_text((50, 60), "Anlage 5: Ergebnisse bodenmechanischer Laborversuche", fontsize=11)
    seite.insert_text(
        (50, 76),
        "Wassergehalt (DIN EN ISO 17892-1) und Zustandsgrenzen (DIN EN ISO 17892-12)",
        fontsize=8,
    )

    spalten = [50.0, 115.0, 180.0, 275.0, 365.0, 455.0, 545.0]
    y_oben = 100.0
    kopf_h = 32.0
    zeilen_h = 22.0

    kopf_zweizeilig = [
        ("Aufschluss", ""),
        ("Tiefe", "[m]"),
        ("Wassergehalt", "w [%]"),
        ("Fließgrenze", "w_L [%]"),
        ("Ausrollgrenze", "w_P [%]"),
        ("Plastizitätszahl", "I_P [%]"),
    ]
    for j, (z1, z2) in enumerate(kopf_zweizeilig):
        seite.insert_text((spalten[j] + 5.0, y_oben + 12.0), z1, fontsize=7.5)
        if z2:
            seite.insert_text((spalten[j] + 5.0, y_oben + 23.0), z2, fontsize=7.5)

    daten = [
        ("B 1", "0,50", "18,4", "36", "18", "18"),
        ("B 1", "1,00", "21,0", "42", "20", "22"),
        ("B 1", "1,50", "24,6", "48", "22", "26"),
        ("B 1", "2,00", "27,8", "52", "24", "28"),
        ("B 1", "2,50", "22,5", "40", "19", "21"),
        ("RKS 2", "3,00", "19,2", "34", "17", "17"),
        ("RKS 2", "3,50", "25,1", "45", "21", "24"),
        ("RKS 2", "4,00", "28,4", "51", "23", "28"),
        ("RKS 2", "4,50", "26,0", "47", "22", "25"),
        ("RKS 2", "5,00", "23,7", "41", "20", "21"),
    ]

    for i, zeile in enumerate(daten):
        yi = y_oben + kopf_h + i * zeilen_h
        for j, zelle in enumerate(zeile):
            seite.insert_text((spalten[j] + 6.0, yi + 14.0), zelle, fontsize=7.5)

    y_unten = y_oben + kopf_h + len(daten) * zeilen_h
    seite.draw_rect(pymupdf.Rect(spalten[0], y_oben, spalten[-1], y_unten), color=(0.0, 0.0, 0.0), fill=None, width=0.6)
    _linie(seite, (spalten[0], y_oben + kopf_h), (spalten[-1], y_oben + kopf_h), 0.7)
    for i in range(1, len(daten)):
        yi = y_oben + kopf_h + i * zeilen_h
        _linie(seite, (spalten[0], yi), (spalten[-1], yi), 0.4)
    for xs in spalten[1:-1]:
        _linie(seite, (xs, y_oben), (xs, y_unten), 0.4)

    return _speichere(
        ordner,
        "s08_falle_labortabelle",
        dok,
        [],
        "Falle Labortabelle (DIN EN ISO 17892): Tiefenspalte Tiefe [m] "
        "mit Laborwerten statt Schlagzahlen -> 0 Sondierungen",
    )


def build(ordner: Path | str) -> list[str]:
    """Erzeugt alle acht synthetischen Sondierungs-Stressfaelle im Zielordner."""
    ziel = Path(ordner)
    ziel.mkdir(parents=True, exist_ok=True)
    erzeugt = [
        _fall_s01_dph_diagramm(ziel),
        _fall_s02_dph_tabelle(ziel),
        _fall_s03_dph_laengsschnitt(ziel),
        _fall_s04_cpt_linear_log(ziel),
        _fall_s05_zensiert(ziel),
        _fall_s06_zweiseitig(ziel),
        _fall_s07_falle_bohrprofil_lineal(ziel),
        _fall_s08_falle_labortabelle(ziel),
    ]
    codes: list[str] = []
    for name in erzeugt:
        wahrheit = json.loads((ziel / f"{name}.json").read_text(encoding="utf-8"))
        codes.extend(s["code"] for s in wahrheit["sondierungen"])
    if len(codes) != len(set(codes)):
        raise ValueError(f"Doppelte Sondierungs-Codes in Stressfaellen: {codes}")
    return erzeugt


if __name__ == "__main__":
    ausgabe = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.gettempdir()) / "stress_sondierungen"
    for fallname in build(ausgabe):
        print(fallname)
