"""Digitales Gelaendemodell vom Dienst des Landes (WCS 2.0.1; docs/23 §2.4, Phase P3b).

Abgerufen wird nur auf Klick (D88): die Anfrage sendet den Ausschnitt um die Bohrungen an den Dienst. Welche Dienste es
gibt, steht mit Beleg in dienste.json (art "wcs-dgm"); was geprueft und nicht aufgenommen wurde, steht dort mit Grund
(Baden-Wuerttemberg liefert ganze Meter, Bayern hat keinen freien WCS). Das Ergebnis ist ein gelaende.Raster wie aus
einer Datei des Nutzers: GOK-Pruefung, fehlende GOK und Gelaende im Modell arbeiten damit gleich.
"""
from __future__ import annotations

import math
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime

import numpy as np

from . import gelaende
from .bohrdaten import AGENT, DienstFehler, dienste_am_ort, namensnennung, utm_normal

ZEIT = 120                     # s je Abruf (1 km2 bei 1 m: ca. 4 MB)
MAX_PIXEL = 3000               # je Richtung; groessere Ausschnitte mit groeberem Raster (SCALEFACTOR, ganzzahlig)
RAND_STANDARD = 100.0          # m um die Bohrungen
RAND_GRENZEN = (0.0, 1000.0)
_PRAEFIX = {4647: 32_000_000.0, 5650: 33_000_000.0}       # Zonenkennung im Rechtswert


def _holen(url: str, zeit: float) -> bytes:
    anfrage = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(anfrage, timeout=zeit) as antwort:
            return antwort.read()
    except TimeoutError:
        raise DienstFehler(f"keine Antwort in {zeit:g} s") from None
    except urllib.error.HTTPError as err:
        text = _ausnahme(err.read())                       # WCS: Fehler als ExceptionReport mit HTTP 400
        raise DienstFehler(f"HTTP {err.code}" + (f": {text}" if text else "")) from None
    except (urllib.error.URLError, OSError) as err:
        raise DienstFehler(f"nicht erreichbar ({getattr(err, 'reason', err)})") from None


def _ausnahme(daten: bytes) -> str:
    """Text eines OWS-ExceptionReport ('' wenn keiner)."""
    try:
        wurzel = ET.fromstring(daten)
    except ET.ParseError:
        return ""
    texte = [" ".join((e.text or "").split()) for e in wurzel.iter() if e.tag.endswith("ExceptionText")]
    return "; ".join(t for t in texte if t)[:300] or wurzel.tag.split("}")[-1]


def url(d: dict, x0: float, y0: float, x1: float, y1: float, faktor: int = 1) -> str:
    """GetCoverage (KVP) fuer den Ausschnitt im System des Dienstes; faktor > 1: Raster faktor-mal groeber."""
    ax, ay = d["achsen"]
    werte = [("SERVICE", "WCS"), ("VERSION", "2.0.1"), ("REQUEST", "GetCoverage"), ("COVERAGEID", d["coverage"]),
             ("FORMAT", "image/tiff"), ("SUBSET", f"{ax}({x0:.0f},{x1:.0f})"), ("SUBSET", f"{ay}({y0:.0f},{y1:.0f})")]
    if faktor > 1:
        werte.append(("SCALEFACTOR", f"{1 / faktor:.6g}"))
    return d["url"] + "?" + urllib.parse.urlencode(werte, safe="(),/")


def ausschnitt(bohrungen: list[tuple[float, float]], rand: float = RAND_STANDARD) -> tuple[float, float, float, float]:
    """Rechteck um die Bohrungen plus Rand, auf ganze Meter (Zellgrenzen der DGM1 der Laender)."""
    rand = min(max(float(rand), RAND_GRENZEN[0]), RAND_GRENZEN[1])
    xs, ys = [b[0] for b in bohrungen], [b[1] for b in bohrungen]
    return (math.floor(min(xs) - rand), math.floor(min(ys) - rand), math.ceil(max(xs) + rand), math.ceil(max(ys) + rand))


def abrufen(x0: float, y0: float, x1: float, y1: float, epsg: int, holer=None,
            heute: date | None = None) -> tuple[gelaende.Raster, dict]:
    """DGM des Ausschnitts (im System des Projekts) vom Dienst des Landes, in dem seine Mitte liegt.

    Rueckgabe: Raster (EPSG des Projekts, auch mit Zonenkennung) und Quelle (Dienst, Lizenz, Namensnennung, Zeit).
    """
    holer = holer or _holen
    praefix = _PRAEFIX.get(int(epsg), 0.0)
    x0n, y0n, system = utm_normal(x0, y0, epsg)
    x1n, y1n, _ = utm_normal(x1, y1, epsg)
    if x1n <= x0n or y1n <= y0n:
        raise ValueError("Ausschnitt leer")
    am_ort = dienste_am_ort((x0n + x1n) / 2, (y0n + y1n) / 2, system, arten=("wcs-dgm",))
    if not am_ort:
        raise ValueError("kein DGM-Dienst für diesen Ort (bisher Brandenburg mit Berlin und NRW) – DGM als Datei laden")
    fehler = []
    for d in am_ort:
        if int(d["system"]) != system:
            fehler.append(f"{d['land']}: nur EPSG:{d['system']}")
            continue
        try:
            r = _laden(d, x0n, y0n, x1n, y1n, holer)
        except DienstFehler as err:
            fehler.append(f"{d['land']}: {err}")
            continue
        if praefix:
            r.x0 += praefix
        r.epsg = int(epsg)
        quelle = {"dienst": d["id"], "land": d["land"], "titel": d["titel"], "anbieter": d["anbieter"],
                  "lizenz": d["lizenz"], "lizenz_url": d["lizenz_url"], "namensnennung": namensnennung(d, heute),
                  "beleg": d["beleg"], "abgerufen": datetime.now().strftime("%Y-%m-%d %H:%M"),
                  "ausschnitt": [round(v + (praefix if k % 2 == 0 else 0.0), 1) for k, v in enumerate((x0n, y0n, x1n, y1n))],
                  "raster_m": round(r.dx, 3)}
        return r, quelle
    raise DienstFehler("; ".join(fehler))


def _laden(d: dict, x0: float, y0: float, x1: float, y1: float, holer) -> gelaende.Raster:
    seite = max(x1 - x0, y1 - y0) / float(d.get("raster_m", 1.0))
    faktor = max(1, math.ceil(seite / MAX_PIXEL))
    daten = holer(url(d, x0, y0, x1, y1, faktor), ZEIT)
    if daten.lstrip()[:1] == b"<":                         # XML statt Bild: ExceptionReport (manche Dienste mit HTTP 200)
        raise DienstFehler(_ausnahme(daten) or "Antwort ist kein Bild")
    try:
        r = gelaende.lesen("dgm.tif", daten)
    except gelaende.DGMFehler as err:
        if "keine gültige Höhe" in str(err):
            raise DienstFehler(f"keine Höhen im Ausschnitt – liegt das Projekt in {d['land']}?") from None
        raise DienstFehler(f"Antwort nicht lesbar: {err}") from None
    if r.epsg not in (None, int(d["system"])):
        raise DienstFehler(f"Antwort in EPSG:{r.epsg} statt EPSG:{d['system']}")
    if not np.isfinite(r.z).any():
        raise DienstFehler(f"keine Höhen im Ausschnitt – liegt das Projekt in {d['land']}?")
    return r
