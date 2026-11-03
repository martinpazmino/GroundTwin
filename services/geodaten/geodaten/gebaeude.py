"""Gebaeude der Laender (LoD2) um das Projekt: Umgebungsmodell (docs/23 §2.4, Phase P4, D86).

Berlin, Brandenburg und NRW geben ihre 3D-Gebaeudemodelle LoD2 als Kacheln von 1 x 1 km im AdV-CityGML-Profil
heraus, in ETRS89/UTM mit Hoehen im DHHN2016 - demselben Rahmen wie das Baugrundmodell: kein Quasigeoid, keine
Meridiankonvergenz. Abgerufen wird nur auf Klick (D88); die Kachelnummern verraten die Lage des Projekts auf 1 km.
Welche Dienste es gibt, steht mit Beleg in dienste.json (art "lod2-kacheln"). Je Kachel gilt der erste Dienst, der
sie hat (Berlin vor Brandenburg: Brandenburg liefert fuer Berlin 404).

Gelesen werden Wand-, Dach- und Bodenflaechen (mit Loechern) je Gebaeude samt Gebaeudeteilen; Abschlussflaechen
(ClosureSurface) sind gedacht und bleiben weg. Ein Gebaeude zaehlt, wenn sein Grundriss den Ausschnitt beruehrt.
"""
from __future__ import annotations

import io
import math
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime

from .bohrdaten import AGENT, VERSUCHE, DienstFehler, dienste_am_ort, namensnennung, utm_normal

ZEIT = 120                     # s je Kachel (NRW: 25 MB GML ohne Kompression)
MAX_KACHELN = 9                # 3 x 3 km; mehr ist kein Umfeld mehr
RAND_STANDARD = 100.0          # m um die Bohrungen (wie das DGM vom Land)
_PRAEFIX = {4647: 32_000_000.0, 5650: 33_000_000.0}
_BLDG = "{http://www.opengis.net/citygml/building/"           # CityGML 1.0 und 2.0
_GML = "{http://www.opengis.net/gml}"
FLAECHEN = {"WallSurface": "Wand", "RoofSurface": "Dach", "GroundSurface": "Boden",
            "OuterCeilingSurface": "Dach", "OuterFloorSurface": "Boden"}


class KeineKachel(DienstFehler):
    """Der Dienst hat diese Kachel nicht (HTTP 404): naechster Dienst oder keine Gebaeude dort."""


def _holen(url: str, zeit: float) -> bytes:
    anfrage = urllib.request.Request(url, headers={"User-Agent": AGENT})
    for versuch in range(1, VERSUCHE + 1):
        try:
            with urllib.request.urlopen(anfrage, timeout=zeit) as antwort:
                return antwort.read()
        except TimeoutError:
            raise DienstFehler(f"keine Antwort in {zeit:g} s") from None
        except urllib.error.HTTPError as err:
            if err.code == 404:
                raise KeineKachel("Kachel nicht vorhanden") from None
            raise DienstFehler(f"HTTP {err.code}") from None
        except (urllib.error.URLError, OSError) as err:
            if isinstance(getattr(err, "reason", None), TimeoutError):   # Zeitueberschreitung beim Verbinden: nicht neu
                raise DienstFehler(f"keine Antwort in {zeit:g} s") from None
            if versuch < VERSUCHE:                         # Verbindung abgebrochen (z. B. reset by peer): kurz warten, neu
                time.sleep(versuch)
                continue
            raise DienstFehler(f"nicht erreichbar ({getattr(err, 'reason', err)})") from None
    raise AssertionError("unerreichbar")


def kacheln(x0: float, y0: float, x1: float, y1: float, km: int = 1) -> list[tuple[int, int]]:
    """Kacheln (Rechts-, Hochwert der linken unteren Ecke in km), die das Rechteck beruehren."""
    k = 1000.0 * km
    return [(e * km, n * km) for e in range(math.floor(x0 / k), math.floor((x1 - 1e-6) / k) + 1)
            for n in range(math.floor(y0 / k), math.floor((y1 - 1e-6) / k) + 1)]


def ausschnitt(bohrungen: list[tuple[float, float]], rand: float = RAND_STANDARD) -> tuple[float, float, float, float]:
    rand = min(max(float(rand), 0.0), 1000.0)
    xs, ys = [b[0] for b in bohrungen], [b[1] for b in bohrungen]
    return (math.floor(min(xs) - rand), math.floor(min(ys) - rand), math.ceil(max(xs) + rand), math.ceil(max(ys) + rand))


# ---------------------------------------------------------------- CityGML lesen
def lesen(daten: bytes, format: str = "gml"):
    """Gebaeude aus einer Kachel (GML oder ZIP mit GML): {id, funktion, dachform, hoehe, flaechen [{art, ring, loecher}]}."""
    if format == "zip" or daten[:2] == b"PK":
        try:
            archiv = zipfile.ZipFile(io.BytesIO(daten))
        except zipfile.BadZipFile:
            raise DienstFehler("Kachel ist kein ZIP") from None
        with archiv:
            for name in archiv.namelist():
                if name.lower().endswith((".gml", ".xml")):
                    with archiv.open(name) as f:
                        yield from _gebaeude(f)
    else:
        yield from _gebaeude(io.BytesIO(daten))


def _gebaeude(f):
    try:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag.startswith(_BLDG) and el.tag.endswith("}Building"):
                b = _ein_gebaeude(el)
                el.clear()                                   # Speicher: Kacheln haben 20+ MB
                if b is not None:
                    yield b
    except ET.ParseError as err:
        raise DienstFehler(f"CityGML nicht lesbar ({err})") from None


def _kind(el, name: str) -> str | None:
    for k in el:
        if k.tag.startswith(_BLDG) and k.tag.endswith("}" + name) and (k.text or "").strip():
            return k.text.strip()
    return None


def _ring(teil) -> list[tuple[float, float, float]]:
    pos = teil.find(f".//{_GML}posList")
    if pos is not None and pos.text:
        d = int(pos.get("srsDimension") or 3)
        werte = [float(v) for v in pos.text.split()]
        punkte = [tuple(werte[i:i + 3]) for i in range(0, len(werte) - d + 1, d)] if d == 3 else []
    else:
        punkte = [tuple(float(v) for v in p.text.split()[:3]) for p in teil.iter(f"{_GML}pos") if p.text]
    out: list[tuple[float, float, float]] = []
    for p in punkte:
        q = (round(p[0], 3), round(p[1], 3), round(p[2], 3))
        if len(q) == 3 and (not out or q != out[-1]):
            out.append(q)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()                                            # Ring geschlossen: letzter Punkt doppelt
    return out


def _ein_gebaeude(el) -> dict | None:
    flaechen = []
    for s in el.iter():
        if not s.tag.startswith(_BLDG):
            continue
        art = FLAECHEN.get(s.tag.rsplit("}", 1)[1])
        if art is None:
            continue
        for poly in s.iter(f"{_GML}Polygon"):
            aussen, innen = None, []
            for teil in poly:
                if teil.tag == f"{_GML}exterior":
                    aussen = _ring(teil)
                elif teil.tag == f"{_GML}interior":
                    r = _ring(teil)
                    if len(r) >= 3:
                        innen.append(r)
            if aussen and len(aussen) >= 3:
                flaechen.append({"art": art, "ring": aussen, "loecher": innen})
    if not flaechen:
        return None
    hoehe = _kind(el, "measuredHeight")
    try:
        hoehe = float(hoehe) if hoehe is not None else None
    except ValueError:
        hoehe = None
    return {"id": el.get(f"{_GML}id") or "", "funktion": _kind(el, "function"), "dachform": _kind(el, "roofType"),
            "hoehe": hoehe, "flaechen": flaechen}


def _rahmen(b: dict) -> tuple[float, float, float, float]:
    xs = [p[0] for f in b["flaechen"] for p in f["ring"]]
    ys = [p[1] for f in b["flaechen"] for p in f["ring"]]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------- Abruf
def abrufen(x0: float, y0: float, x1: float, y1: float, epsg: int, holer=None,
            heute: date | None = None) -> tuple[list[dict], dict]:
    """Gebaeude im Ausschnitt (System des Projekts, auch mit Zonenkennung) aus den Kacheln der Laender.

    Rueckgabe: (Gebaeude mit Koordinaten im System des Projekts, Quelle mit Diensten, Lizenzen, Kacheln, Fehlern).
    """
    holer = holer or _holen
    praefix = _PRAEFIX.get(int(epsg), 0.0)
    x0n, y0n, system = utm_normal(x0, y0, epsg)
    x1n, y1n, _ = utm_normal(x1, y1, epsg)
    if x1n <= x0n or y1n <= y0n:
        raise ValueError("Ausschnitt leer")
    am_ort = [d for d in dienste_am_ort((x0n + x1n) / 2, (y0n + y1n) / 2, system, arten=("lod2-kacheln",))
              if int(d["system"]) == system]
    if not am_ort:
        raise ValueError("kein LoD2-Dienst für diesen Ort (bisher Berlin, Brandenburg, NRW)")
    ks = kacheln(x0n, y0n, x1n, y1n)
    if len(ks) > MAX_KACHELN:
        raise ValueError(f"Ausschnitt braucht {len(ks)} Kacheln (höchstens {MAX_KACHELN}) – Rand verkleinern")
    gebaeude: dict[str, dict] = {}
    genutzt: dict[str, dict] = {}
    fehler, ohne = [], []
    for e, n in ks:
        for d in am_ort:
            try:
                daten = holer(d["url"].format(e=e, n=n), ZEIT)
                gefunden = list(lesen(daten, d.get("format", "gml")))
            except KeineKachel:
                continue
            except DienstFehler as err:
                fehler.append(f"{d['land']}, Kachel {e}/{n}: {err}")
                continue
            genutzt[d["id"]] = d
            for b in gefunden:
                bx0, by0, bx1, by1 = _rahmen(b)
                if bx1 >= x0n and bx0 <= x1n and by1 >= y0n and by0 <= y1n and b["id"] not in gebaeude:
                    b["dienst"] = d["id"]
                    gebaeude[b["id"] or f"{e}_{n}_{len(gebaeude)}"] = b
            break
        else:
            ohne.append(f"{e}/{n}")
    if not genutzt and fehler:
        raise DienstFehler("; ".join(fehler))
    liste = list(gebaeude.values())
    if praefix:
        for b in liste:
            for f in b["flaechen"]:
                f["ring"] = [(p[0] + praefix, p[1], p[2]) for p in f["ring"]]
                f["loecher"] = [[(p[0] + praefix, p[1], p[2]) for p in r] for r in f["loecher"]]
    quelle = {"dienste": [{"dienst": d["id"], "land": d["land"], "titel": d["titel"], "anbieter": d["anbieter"],
                           "lizenz": d["lizenz"], "lizenz_url": d["lizenz_url"],
                           "namensnennung": namensnennung(d, heute), "beleg": d["beleg"]} for d in genutzt.values()],
              "abgerufen": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "ausschnitt": [x0n + praefix, y0n, x1n + praefix, y1n], "kacheln": len(ks),
              "ohne_kachel": ohne, "fehler": fehler}
    return liste, quelle
