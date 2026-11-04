"""Geologiedatengesetz (GeolDG): was GroundTwin fuer die Uebermittlung an den Geologischen Dienst liefert, was fehlt.

Hilfe, keine Rechtsberatung. Die Regeln stehen mit Beleg (Paragraph, URL) in geoldg.json, gelesen am Gesetzestext auf
gesetze-im-internet.de. Je Bohrung: was die App hat (Lage, Ansatzhoehe, Endteufe, gepruefte Schichten) und was aus dem
Bohrprotokoll kommen muss (Bohrverfahren, Ausbau, Proben, Messungen, Labor); die Fristen aus den Daten der
Untersuchung; das Modell mit seiner Dokumentation als Bewertungsdaten (§ 10 Abs. 2 Satz 1 Nr. 2).

Status je Punkt: ok (belegt, aus dem PDF und geprueft), markiert (vorhanden, aber nicht aus dem PDF oder angenommen),
offen (in der App nachholbar: Lage, GOK, Pruefung), ergaenzen (liest die App nicht: aus dem Bohrprotokoll).
"""
from __future__ import annotations

import calendar
import csv
import io
import json
import re
import zipfile
from datetime import date, timedelta
from pathlib import Path

from . import boreholeml

REGELN = json.loads(Path(__file__).with_name("geoldg.json").read_text(encoding="utf-8"))
PUNKTE = {p["id"]: p for p in REGELN["punkte"]}
FREMD = ("SGD", "BoreholeML")                           # nicht aus dem Gutachten: liegt dem Land schon vor
LAGE_AUS_PDF = ("", "PDF", "tabelle", "text")             # Quellen der Extraktion (prototyp_v4: Tabelle, Text)
LAGE_TEXT = {"manuell (Tabelle)": "in der Tabelle eingetragen", "Plan (kalibriert)": "aus dem kalibrierten Plan abgegriffen",
             "manuell (Viewer)": "im Viewer gesetzt (Plan ohne Kalibrierung)"}
GOK_TEXT = {"DGM": "aus dem DGM übernommen, nicht gemessen", "manuell": "manuell eingetragen"}
LAGE_MODELL = {"text": "aus dem Gutachten (Text)", "tabelle": "aus dem Gutachten (Tabelle)", "PDF": "aus dem Gutachten",
               **LAGE_TEXT}                              # Herkunft im Pruefbericht des Modellierers
HOEHE_MODELL = {"m NHN": "aus dem Gutachten"}


# ---------------------------------------------------------------- Fristen
def datum(text) -> date | None:
    """ISO-Datum (JJJJ-MM-TT) oder None; ValueError bei anderem Text."""
    if text in (None, ""):
        return None
    try:
        return date.fromisoformat(str(text))
    except ValueError:
        raise ValueError(f"Datum „{text}“: JJJJ-MM-TT erwartet") from None


def angaben_pruefen(angaben: dict) -> dict:
    """Angaben der Untersuchung {beginn, abschluss, behoerde} geprueft und normiert (leer = unbekannt)."""
    beginn, abschluss = datum(angaben.get("beginn")), datum(angaben.get("abschluss"))
    if beginn and abschluss and abschluss < beginn:
        raise ValueError("Abschluss der Untersuchung liegt vor ihrem Beginn")
    return {"beginn": beginn.isoformat() if beginn else "", "abschluss": abschluss.isoformat() if abschluss else "",
            "behoerde": bool(angaben.get("behoerde"))}


def plus_monate(d: date, n: int) -> date:
    """Monatsfrist wie § 188 Abs. 2 und 3 BGB: derselbe Tag n Monate spaeter, fehlt er, der letzte Tag des Monats."""
    j, m = divmod(d.month - 1 + n, 12)
    jahr, monat = d.year + j, m + 1
    return date(jahr, monat, min(d.day, calendar.monthrange(jahr, monat)[1]))


def fristen(angaben: dict, heute: date) -> list[dict]:
    """Fristen nach §§ 8–10 mit Datum, wenn Beginn bzw. Abschluss bekannt sind; tage = Tage bis zur Frist (< 0 vorbei)."""
    a = angaben_pruefen(angaben or {})
    bezug = {"beginn": datum(a["beginn"]), "abschluss": datum(a["abschluss"])}
    out = []
    for f in REGELN["fristen"]:
        behoerde = a["behoerde"] and "regel_behoerde" in f
        bis = None
        if bezug[f["bezug"]] and (behoerde or not f.get("nur_behoerde")):
            d = bezug[f["bezug"]]
            bis = d + timedelta(days=f["tage"]) if "tage" in f else plus_monate(d, f["monate"])
        out.append({"id": f["id"], "titel": f["titel"], "regel": f["regel_behoerde"] if behoerde else f["regel"],
                    "beleg": f["beleg_behoerde"] if behoerde else f["beleg"], "url": f["url"],
                    "bezug": f["bezug"], "bis": bis.isoformat() if bis else None,
                    "tage": (bis - heute).days if bis else None})
    return out


# ---------------------------------------------------------------- je Bohrung
def _m(v: float) -> str:
    return f"{float(v):.2f}".replace(".", ",")


def _zahl(v, stellen: int = 2) -> str:
    """Zahl mit Dezimalkomma; '?' wenn sie fehlt."""
    return "?" if v is None else f"{float(v):,.{stellen}f}".replace(",", " ").replace(".", ",")


def bohrung(b: dict, reihe: bool = False) -> dict:
    """Pruefliste einer Bohrung (wirksame Werte wie im Modell): {code, art, punkte {id: [status, wert]}, bereit,
    boreholeml (Grund, warum nicht; '' = exportierbar)}. Nur die Punkte, die die App kennt; die aus dem Bohrprotokoll
    (quelle 'protokoll' in geoldg.json) sind fuer alle Bohrungen gleich zu ergaenzen."""
    punkte: dict[str, list[str]] = {}
    x, y, epsg, quelle = b.get("x"), b.get("y"), b.get("crs_epsg"), b.get("coord_source") or ""
    if reihe:
        punkte["lage"] = ["offen", "nur Station im Längsschnitt – Lage nach Koordinaten nötig"]
    elif x is None or y is None:
        punkte["lage"] = ["offen", "ohne Koordinaten"]
    elif not epsg:
        punkte["lage"] = ["offen", f"{_m(x)} / {_m(y)} ohne Koordinatensystem (EPSG)"]
    else:
        text = f"{_m(x)} / {_m(y)} (EPSG:{int(epsg)})"
        if quelle in LAGE_AUS_PDF:
            punkte["lage"] = ["ok", f"{text}, aus dem Gutachten"]
        else:
            punkte["lage"] = ["markiert", f"{text}, {LAGE_TEXT.get(quelle, quelle)}"]
    gok, gq = b.get("gok_nhn"), b.get("gok_source") or "PDF"
    if gok is None:
        punkte["ansatzhoehe"] = ["offen", "ohne GOK"]
    elif gq == "relativ":
        punkte["ansatzhoehe"] = ["offen", "nur relativ (0 m), nicht in m NHN"]
    elif gq in GOK_TEXT:
        punkte["ansatzhoehe"] = ["markiert", f"{_m(gok)} m NHN, {GOK_TEXT[gq]}"]
    else:
        punkte["ansatzhoehe"] = ["ok", f"{_m(gok)} m NHN, aus dem Gutachten"]
    punkte["verlauf"] = ["markiert", "lotrecht angenommen (Neigung im Gutachten nicht gelesen)"]
    schichten = b.get("layers") or []
    ende = b.get("end_depth") or max((ly["bottom_depth"] for ly in schichten), default=None)
    punkte["endteufe"] = ["ok", f"{_m(ende)} m u. GOK"] if ende else ["offen", "ohne Endteufe"]
    geprueft = sum(bool(ly.get("geprueft")) for ly in schichten)
    if not schichten:
        punkte["schichtenverzeichnis"] = ["offen", "keine Schichten"]
    elif geprueft < len(schichten):
        punkte["schichtenverzeichnis"] = ["offen", f"{geprueft}/{len(schichten)} Schichten geprüft"]
    else:
        punkte["schichtenverzeichnis"] = ["ok", f"{len(schichten)} Schichten, geprüft"]
    bereit = all(punkte[k][0] in ("ok", "markiert") for k in ("lage", "ansatzhoehe", "endteufe", "schichtenverzeichnis"))
    return {"code": b.get("code", "?"), "art": REGELN["art"].get(b.get("kind") or "", ""), "punkte": punkte,
            "bereit": bereit, "boreholeml": "nur Lage nach Koordinaten" if reihe else boreholeml.exportierbar(b)}


def pruefen(bohrungen: list[dict], angaben: dict | None = None, *, heute: date | None = None, reihe: bool = False,
            sondierungen: int = 0, standort: bool = False) -> dict:
    """Uebersicht fuer die App und das Paket: Fristen, Prueflisten der eigenen Bohrungen, Bohrungen der Laender
    (nicht zu uebermitteln) und Hinweise mit Beleg. bohrungen: wirksame Bohrungen im Modell (kanonisches JSON)."""
    heute = heute or date.today()
    eigene, fremd = [], []
    for b in bohrungen:
        if b.get("herkunft") in FREMD:
            fremd.append({"code": b.get("code", "?"), "herkunft": b["herkunft"]})
        else:
            eigene.append(bohrung(b, reihe))
    offen = [{"code": e["code"], "was": "; ".join(f"{PUNKTE[k]['titel']}: {w}" for k, (s, w) in e["punkte"].items()
                                                if s == "offen")} for e in eigene if not e["bereit"]]
    hinweise = [dict(h) for h in REGELN["hinweise"]]
    if sondierungen:
        hinweise.insert(0, {"text": f"{sondierungen} Sondierungen im Gutachten: Messdaten sind Fachdaten im Sinne von "
                                    "§ 3 Abs. 3 Nr. 2, aber nicht im BoreholeML – die Übermittlung mit der Behörde klären.",
                            "beleg": "§ 3 Abs. 3 Nr. 2", "url": "https://www.gesetze-im-internet.de/geoldg/__3.html"})
    return {
        "quelle": REGELN["quelle"], "angaben": angaben_pruefen(angaben or {}), "heute": heute.isoformat(),
        "fristen": fristen(angaben or {}, heute), "abschluss": REGELN["abschluss"],
        "punkte": [{k: p[k] for k in ("id", "titel", "beleg", "quelle")} for p in REGELN["punkte"]],
        "bohrungen": eigene, "fremd": fremd,
        "zusammenfassung": {"eigene": len(eigene), "bereit": sum(e["bereit"] for e in eigene),
                            "boreholeml": sum(not e["boreholeml"] for e in eigene), "fremd": len(fremd),
                            "offen": offen},
        "vorerkundung": standort and not eigene, "anzeige_inhalt": REGELN["anzeige_inhalt"], "hinweise": hinweise}


# ---------------------------------------------------------------- Paket (ZIP) fuer den Geologischen Dienst
STATUS_TEXT = {"ok": "✓", "markiert": "⚑", "offen": "✗"}


def dateiname(name: str) -> str:
    """Name fuer einen Pfad im ZIP: ohne Trenner und Zeichen, die Windows nicht erlaubt ('Standort 1 / 2' -> '_')."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .") or "baugrundmodell"


def _de(iso: str | None) -> str:
    return date.fromisoformat(iso).strftime("%d.%m.%Y") if iso else ""


def frist_text(f: dict) -> str:
    if not f["bis"]:
        offen = {"beginn": " – Beginn eintragen", "abschluss": " – Abschluss eintragen"}[f["bezug"]]
        return f"{f['titel']}: {f['regel']} ({f['beleg']}){offen if f['regel'].startswith('spätestens') else ''}"
    lage = f"noch {f['tage']} Tage" if f["tage"] > 0 else "heute" if f["tage"] == 0 else "verstrichen"
    return f"{f['titel']}: {f['regel']} ({f['beleg']}) – bis {_de(f['bis'])}, {lage}"


def tabelle(u: dict) -> bytes:
    """Prueftabelle je Bohrung (CSV, Semikolon, UTF-8 mit BOM fuer Excel): Werte der App und leere Spalten zum
    Ergaenzen aus dem Bohrprotokoll."""
    puffer = io.StringIO()
    w = csv.writer(puffer, delimiter=";", lineterminator="\r\n")
    w.writerow(["Bohrung", "Hinweis zur Art"] + [f"{p['titel']} ({p['beleg']})" for p in u["punkte"]]
               + ["Bohrdatum", "BoreholeML"])
    for e in u["bohrungen"]:
        werte = [f"{STATUS_TEXT[e['punkte'][p['id']][0]]} {e['punkte'][p['id']][1]}" if p["id"] in e["punkte"] else ""
                 for p in u["punkte"]]
        w.writerow([e["code"], e["art"]] + werte + ["", "ja" if not e["boreholeml"] else f"nein: {e['boreholeml']}"])
    return ("﻿" + puffer.getvalue()).encode("utf-8")


def liesmich(u: dict, projekt: str, enthalten: list[str], fehlt: list[str]) -> str:
    z = u["zusammenfassung"]
    zeilen = [f"GroundTwin – Paket für den Geologischen Dienst (GeolDG): {projekt}", f"Erstellt am {_de(u['heute'])}.",
              "", u["quelle"]["hinweis"], f"Gesetzestext: {u['quelle']['url']}", "", "FRISTEN"]
    zeilen += [f"- {frist_text(f)}" for f in u["fristen"]]
    zeilen += [f"- {u['abschluss']['text']} ({u['abschluss']['beleg']})", "", "INHALT"]
    zeilen += [f"- {t}" for t in enthalten]
    if fehlt:
        zeilen += ["", "NICHT IM PAKET"] + [f"- {t}" for t in fehlt]
    zeilen += ["", "BOHRUNGEN",
               f"- {z['eigene']} eigene Bohrungen; für {z['bereit']} liefert GroundTwin Lage, Ansatzhöhe, Endteufe und "
               f"das geprüfte Schichtenverzeichnis, {z['boreholeml']} davon im BoreholeML."]
    if z["fremd"]:
        zeilen.append(f"- {z['fremd']} Bohrungen der Länder bzw. aus BoreholeML-Dateien: liegen dem Land vor, nicht "
                      "im Paket.")
    zeilen += [f"- offen: {o['code']} – {o['was']}" for o in z["offen"]]
    zeilen += ["- Aus dem Bohrprotokoll ergänzen (Spalten in pruefliste.csv): "
               + "; ".join(f"{p['titel']} ({p['beleg']})" for p in u["punkte"] if p["quelle"] == "protokoll") + "."]
    zeilen += ["- Zeichen: ✓ aus dem Gutachten und geprüft · ⚑ vorhanden, aber nicht aus dem PDF oder angenommen · "
               "✗ in GroundTwin offen · leer: aus dem Bohrprotokoll ergänzen.", "", "HINWEISE"]
    zeilen += [f"- {h['text']} ({h['beleg']}, {h['url']})" for h in u["hinweise"]]
    a = u["anzeige_inhalt"]
    zeilen += ["", f"INHALT EINER ANZEIGE ({a['beleg']}, für weitere Untersuchungen)"] + [f"- {t}" for t in a["punkte"]]
    zeilen += [f"- {a['aus_der_app']}"]
    return "\r\n".join(zeilen) + "\r\n"


def modelldokumentation(bericht: dict, projekt: str, pruefstand: str, quellen: list[str]) -> str:
    """Dokumentation des raeumlichen Modells (§ 10 Abs. 2 Satz 1 Nr. 2) aus dem Pruefbericht: Bezug, Methode,
    Einheiten, Bohrungen mit Herkunft von Lage und GOK, Pruefungen und Grenzen (was gemessen, was interpretiert ist)."""
    par = bericht.get("parameter") or {}
    pr = bericht.get("pruefungen") or {}
    methode = {"idw": "inverse Distanzgewichtung (IDW, p = 2)", "tps": "Dünnplatten-Spline (TPS)"}.get(
        par.get("methode"), str(par.get("methode")))
    ursprung = bericht.get("ursprung") or (0.0, 0.0)
    zeilen = [f"Modelldokumentation – Baugrundmodell {projekt}".rstrip(),
              f"Erzeugt mit GroundTwin (Modellierer {bericht.get('modellierer', '?')}); Reifegrad: {bericht.get('reifegrad')}.",
              f"Prüfstand: {pruefstand}.", "",
              "BEZUG",
              f"- Lage: {'EPSG:' + str(bericht['epsg']) if bericht.get('epsg') else 'lokales System (ohne Georeferenz)'}; "
              f"Höhen in m NHN wie im Gutachten; Einheit Meter.",
              f"- Lokaler Ursprung des IFC: {_m(ursprung[0])} / {_m(ursprung[1])}.", "",
              "METHODE",
              f"- Schichtgrenzen zwischen den Bohrungen interpoliert: {methode}, Raster {_zahl(par.get('raster_m'))} m, "
              f"Rand {_zahl(par.get('puffer_m'))} m um die Bohrungen; Modellbasis {_zahl(par.get('basis_nhn'))} m NHN.",
              f"- Oberkante: {((par.get('gelaende') or {}).get('quelle')) or 'GOK'}.",
              f"- An den Bohrungen exakt (größte Abweichung {_zahl(pr.get('max_abweichung_an_bohrungen_m'), 3)} m); "
              f"alle Körper geschlossen: {'ja' if pr.get('alle_koerper_geschlossen') else 'nein'}.", "",
              "EINHEITEN"]
    for e in bericht.get("einheiten") or []:
        zeilen.append(f"- {e['name']}: {', '.join(e['bodenarten'])}; {_zahl(e['volumen_m3'], 0)} m³, bis "
                      f"{_zahl(e['maechtigkeit_max_m'])} m mächtig, in {len(e['bohrungen'])} Bohrungen")
    zeilen += ["", "BOHRUNGEN (Lage, Höhe: Herkunft)"]
    for b in bericht.get("bohrungen") or []:
        zeilen.append(f"- {b['code']}: {_m(b['x'])} / {_m(b['y'])}, GOK {_m(b['gok'])} m NHN; Lage "
                      f"{LAGE_MODELL.get(b.get('lage'), b.get('lage'))}, Höhe {HOEHE_MODELL.get(b.get('hoehe'), b.get('hoehe'))}; "
                      f"Endteufe {_m(b['endteufe_nhn'])} m NHN")
    if bericht.get("ausgeschlossen"):
        zeilen += ["", "NICHT IM MODELL"] + [f"- {a.get('code')}: {a.get('grund')}" for a in bericht["ausgeschlossen"]]
    zeilen += ["", "GRENZEN",
               "- Gemessen sind nur die Schichten in den Bohrungen; zwischen ihnen ist der Verlauf interpoliert "
               "(Interpretation, keine Messung).",
               "- Verlauf der Bohrungen lotrecht angenommen; Einheiten aus den Bodenarten zusammengefasst."]
    zeilen += [f"- {h}" for h in bericht.get("hinweise") or []]
    if quellen:
        zeilen += ["", "DATEN DRITTER"] + [f"- {q}" for q in quellen]
    return "\r\n".join(zeilen) + "\r\n"


def paket(u: dict, projekt: str, dateien: dict[str, bytes], fehlt: list[str]) -> bytes:
    """ZIP: LIESMICH.txt, pruefliste.csv, pruefliste.json und die Dateien {Pfad: Inhalt} (Fach-/Bewertungsdaten)."""
    beschreibung = {"fachdaten_GeolDG_9/": "Fachdaten nach § 9 (Kennzeichnung nach § 17 Abs. 1 Nr. 2)",
                    "bewertungsdaten_GeolDG_10/": "Bewertungsdaten nach § 10 (Kennzeichnung nach § 17 Abs. 1 Nr. 3)"}
    enthalten = [f"{pfad} – {next((t for o, t in beschreibung.items() if pfad.startswith(o)), '')}".rstrip(" –")
                 for pfad in dateien]
    enthalten += ["pruefliste.csv – je Bohrung: Werte aus GroundTwin, leere Spalten zum Ergänzen aus dem Bohrprotokoll",
                  "pruefliste.json – dieselbe Übersicht maschinenlesbar"]
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("LIESMICH.txt", liesmich(u, projekt, enthalten, fehlt).encode("utf-8"))
        z.writestr("pruefliste.csv", tabelle(u))
        z.writestr("pruefliste.json", json.dumps(u, ensure_ascii=False, indent=1).encode("utf-8"))
        for pfad, inhalt in dateien.items():
            z.writestr(pfad, inhalt)
    return puffer.getvalue()
