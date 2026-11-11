"""Baugrundmodell (N3, Layer-Cake) aus kanonischen Extraktions-JSONs: Einheiten -> Flaechen -> Koerper -> IFC.

Ablauf und Parameter: docs/18_layer_modeler.md.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.spatial import cKDTree

from . import __version__
from .einheiten import (Bohrung, Einheit, Kontakt, bohrungen_aus_extraktion, kontakte, korrelieren)
from .flaechen import (ERWEITERUNGEN, MIN_MAECHTIGKEIT, PRAESENZ_SCHWELLE, gebiet, hinweise_holen, hinweise_starten, netz,
                       orientierungen_setzen,
                       schichtmodell)
from .ifc4x3 import IfcAusgabe, farbe, hexfarbe
from .koerper import koerper, pruefen, volumen_prismen
from .normen import deuten, farbinfo
from .umgebung import UMGEBUNG_STANDARD, oberkante, ring


@dataclass
class Modell:
    epsg: int | None
    ursprung: tuple[float, float]
    bohrungen: list[Bohrung]
    ausgeschlossen: list[dict]
    einheiten: list[Einheit]
    kontakte: list[list[Kontakt]]
    punkte: np.ndarray                 # lokal (m)
    dreiecke: np.ndarray
    rand: np.ndarray
    flaechen: np.ndarray               # (Einheiten+1, Punkte): Gelaende, Unterkanten
    abstand: np.ndarray                # Abstand jedes Knotens zur naechsten Bohrung (m)
    basis: float
    parameter: dict
    koerper: list[dict] = field(default_factory=list)
    hinweise: list[str] = field(default_factory=list)
    max_abweichung: float = 0.0
    zensurpunkte: int = 0
    ausgeduennt: list[int] = field(default_factory=list)   # Knoten je Einheit, an denen die Ausdehnung endet
    zuordnung: dict[str, list[tuple]] = field(default_factory=dict)   # je Bohrung: (op, Abschnitt, Einheit)
    dgm: object | None = None          # Raster des DGM, wenn das Gelaende daraus kommt (Umgebung im IFC)


# Grosse Modelle (Trassen > 5 km): Knotenzahl begrenzen statt Raster fest; Puffer waechst mit dem Bohrabstand
MAX_KNOTEN = 30000
RASTER_GRENZEN = (0.5, 10.0)          # m, solange die Knotenzahl reicht
PUFFER_GRENZEN = (5.0, 100.0)         # m


FREMD = ("SGD", "BoreholeML")          # Bohrungen, die nicht aus einem Gutachten-PDF stammen


def reifegrad(bohrungen: list[Bohrung]) -> tuple[str, dict[str, int]]:
    """Reife des Modells (docs/23 §2.3): Gutachten, Vorerkundung (nur Fremddaten) oder gemischt; Anzahl je Herkunft."""
    anzahl: dict[str, int] = {}
    for b in bohrungen:
        anzahl[b.herkunft] = anzahl.get(b.herkunft, 0) + 1
    fremd = sum(n for h, n in anzahl.items() if h in FREMD)
    return ("Gutachten" if fremd == 0 else "Vorerkundung" if fremd == len(bohrungen) else "gemischt"), anzahl


def standard_durchmesser(ausdehnung: float) -> float:
    """Durchmesser der Bohrsaeulen zur Darstellung: mit der Modellgroesse, damit sie auf Trassen sichtbar bleiben."""
    return round(float(np.clip(ausdehnung / 300.0, 0.8, 12.0)), 1)


def standard_puffer(nn: float) -> float:
    return float(np.clip(0.5 * nn, *PUFFER_GRENZEN))


def standard_raster(flaeche: float) -> float:
    """Raster ~ Gebietsgroesse/40, mindestens so grob, dass MAX_KNOTEN nicht ueberschritten werden."""
    return float(max(np.clip(math.sqrt(flaeche) / 40.0, *RASTER_GRENZEN), math.sqrt(flaeche / MAX_KNOTEN)))


def bauen(docs: list[dict], vorgabe: list[Einheit] | None = None, methode: str = "idw",
          raster: float | None = None, puffer: float | None = None, basis: float | None = None,
          ursprung: tuple[float, float] | None = None, gelaende=None, gelaende_info: dict | None = None,
          orientierung: dict[str, dict] | None = None) -> Modell:
    """ursprung: fester lokaler Nullpunkt (App: bleibt beim Verschieben von Bohrungen stehen, die Ansicht springt nicht).

    gelaende: DGM-Raster (x0, y0, dx, dy, z, epsg) fuer die Oberkante (umgebung.py); gelaende_info: Name und Quelle.
    orientierung: je Einheit {"fallrichtung", "fallwinkel"} in Grad, eingegeben (docs/27 G4); nutzt nur eine
    Erweiterung, die danach fragt (implizit); steht mit Quelle "Eingabe" im Bericht.
    """
    bohrungen, ausgeschlossen, epsg = bohrungen_aus_extraktion(docs)
    if not bohrungen:
        raise ValueError("keine modellfaehige Bohrung (Koordinaten, GOK und Schichten noetig)")
    einheiten, zuordnung, hinweise = korrelieren(bohrungen, vorgabe)
    if epsg is None:
        hinweise.append("Lage ohne Georeferenz (lokales System)")
    schema = [b.code for b in bohrungen if b.lage == "schematisch"]
    if schema:
        hinweise.append(f"schematische Lage (Abstaende nicht vermessen, nur zur Anschauung): {', '.join(schema)}")
    relativ = [b.code for b in bohrungen if b.hoehe.startswith("relativ")]
    if relativ:
        hinweise.append(f"relative Hoehen (GOK unbekannt, 0 m gesetzt): {', '.join(relativ)}")
    ks = [kontakte(b, zuordnung[b.code], einheiten) for b in bohrungen]
    if ursprung is None:
        ursprung = (round(float(np.mean([b.x for b in bohrungen])), -1), round(float(np.mean([b.y for b in bohrungen])), -1))
    ursprung = (float(ursprung[0]), float(ursprung[1]))
    xy_b = np.array([(b.x - ursprung[0], b.y - ursprung[1]) for b in bohrungen])
    if len(bohrungen) > 1:
        nn = float(np.median(cKDTree(xy_b).query(xy_b, k=2)[0][:, 1]))
    else:
        nn = 20.0
    puffer = puffer if puffer is not None else standard_puffer(nn)
    ausdehnung = float(max(np.ptp(xy_b[:, 0]), np.ptp(xy_b[:, 1]), 20.0))
    polygon = gebiet(xy_b, puffer)
    flaeche = 0.5 * abs(np.dot(polygon[:, 0], np.roll(polygon[:, 1], 1)) - np.dot(polygon[:, 1], np.roll(polygon[:, 0], 1)))
    if raster is None:
        raster = standard_raster(flaeche)
    elif raster < math.sqrt(flaeche / MAX_KNOTEN):          # grosse Modellgrenze von Hand: Knotenzahl begrenzen
        grob = math.sqrt(flaeche / MAX_KNOTEN)
        hinweise.append(f"Raster {raster:.2f} m auf {grob:.2f} m vergroebert (hoechstens {MAX_KNOTEN} Knoten "
                        f"fuer {flaeche / 1e6:.2f} km2)")
        raster = grob
    punkte, dreiecke, rand = netz(polygon, xy_b, raster)
    tiefste = min(b.ende for b in bohrungen)
    if basis is None:
        basis = tiefste
    elif basis > tiefste:
        hinweise.append(f"Modellbasis {basis:.2f} m NHN ueber der tiefsten Endteufe {tiefste:.2f}: tiefere Daten abgeschnitten")
    grad, je_herkunft = reifegrad(bohrungen)
    if grad == "Vorerkundung":
        hinweise.append("Vorerkundung: nur Bohrungen aus Datenbanken der Länder bzw. BoreholeML-Dateien, kein Gutachten – "
                        "Schichten nicht gegen ein PDF geprüft")
    elif grad == "gemischt":
        hinweise.append("gemischt: " + ", ".join(f"{n} {h}" for h, n in sorted(je_herkunft.items()))
                        + " – Bohrungen ohne Gutachten sind nicht gegen ein PDF geprüft")
    oben, gel = None, {"quelle": "GOK"}
    if gelaende is not None:
        oben, gel = _gelaende(gelaende, bohrungen, epsg, punkte, ursprung, xy_b, raster, nn, methode)
        gel.update(gelaende_info or {})
        if gel.get("hinweis"):
            hinweise.append(gel["hinweis"])
    erweiterung = ERWEITERUNGEN.get(methode)
    vorgaben = _orientierungen(orientierung, einheiten, hinweise) if hasattr(erweiterung, "beschreiben") else {}
    hinweise_starten()
    orientierungen_setzen(vorgaben)
    try:
        sm = schichtmodell(bohrungen, ks, punkte, xy_b, basis, methode, oben=oben)
        beschrieben = erweiterung.beschreiben(einheiten, ks, bohrungen) if hasattr(erweiterung, "beschreiben") else None
    finally:
        orientierungen_setzen(None)
    hinweise += hinweise_holen()
    m = Modell(epsg, ursprung, bohrungen, ausgeschlossen, einheiten, ks, punkte, dreiecke, rand, sm["flaechen"],
               sm["abstand"], basis, {"methode": methode, "raster_m": raster, "puffer_m": puffer,
                                      "basis_nhn": basis, "flaeche_m2": float(flaeche), "ausdehnung_m": ausdehnung,
                                      "durchmesser_auto_m": standard_durchmesser(ausdehnung),
                                      "praesenz_schwelle": PRAESENZ_SCHWELLE, "gelaende": gel,
                                      "reifegrad": grad, "herkunft": je_herkunft,
                                      **({"orientierung": beschrieben} if beschrieben is not None else {}),
                                      **({"orientierung_vorgabe": {str(j): list(v) for j, v in vorgaben.items()}}
                                         if vorgaben else {})},
               hinweise=hinweise, max_abweichung=sm["max_abweichung_bohrungen"],
               zensurpunkte=sum(len(z) for z in sm["zensur"]), ausgeduennt=sm["ausgeduennt"], zuordnung=zuordnung)
    m.dgm = gelaende if oben is not None else None
    _koerper(m)
    return m


def _orientierungen(orientierung: dict[str, dict] | None, einheiten: list[Einheit],
                    hinweise: list[str]) -> dict[int, tuple[float, float]]:
    """Eingegebene Orientierungen nach Einheit-Index; unbekannte Namen werden gemeldet, nicht still verworfen."""
    out: dict[int, tuple[float, float]] = {}
    namen = {e.name: j for j, e in enumerate(einheiten)}
    for name, v in (orientierung or {}).items():
        if name not in namen:
            hinweise.append(f"Orientierung für '{name}' nicht verwendet: keine solche Einheit im Modell")
            continue
        out[namen[name]] = (float(v["fallrichtung"]) % 360.0, float(v["fallwinkel"]))
    return out


def _gelaende(r, bohrungen: list[Bohrung], epsg: int | None, punkte: np.ndarray, ursprung: tuple[float, float],
              xy_b: np.ndarray, raster: float, nn: float, methode: str) -> tuple[np.ndarray | None, dict]:
    """Oberkante aus dem DGM, wenn System, Lage und Hoehen der Bohrungen dazu passen; sonst None mit Grund."""
    if not epsg or not getattr(r, "epsg", None) or int(r.epsg) != int(epsg):
        return None, {"quelle": "GOK", "hinweis": f"DGM in EPSG:{getattr(r, 'epsg', None)}, Modell in EPSG:{epsg} – "
                                                  f"Gelände aus den GOK der Bohrungen interpoliert"}
    fremd = [b.code for b in bohrungen if b.lage == "schematisch" or b.hoehe.startswith("relativ")]
    if fremd:
        return None, {"quelle": "GOK", "hinweis": f"Gelände aus den GOK der Bohrungen: schematische Lage oder "
                                                  f"relative Höhe passt nicht zum DGM ({', '.join(fremd)})"}
    return oberkante(r, punkte, ursprung, xy_b, np.array([b.gok for b in bohrungen]), raster, nn, methode)


def gelaende_text(gel: dict) -> str:
    """Herkunft des Gelaendes in einem Satz (IFC, Bericht)."""
    if gel.get("quelle") != "DGM":
        return "aus den GOK der Bohrungen interpoliert" + (f" ({gel['hinweis']})" if gel.get("hinweis") else "")
    return (f"DGM {gel.get('name') or ''}".rstrip() + f", an den Bohrungen auf die GOK gezogen (Reichweite "
            f"{gel['reichweite_m']:g} m; GOK - DGM bis {gel['gok_minus_dgm_max_m']:g} m, Median "
            f"{gel['gok_minus_dgm_median_m']:g} m)")


def _koerper(m: Modell) -> None:
    nummer: dict[str, int] = {}
    for j, e in enumerate(m.einheiten):
        oben, unten = m.flaechen[j], m.flaechen[j + 1]
        d = oben - unten
        nummer[e.klasse] = nummer.get(e.klasse, 0) + 1
        st = {"vorhanden": [], "fehlt": [], "unbekannt": []}
        for b, ks in zip(m.bohrungen, m.kontakte):
            st[ks[j].status].append(b.code)
        info = {"name": e.name, "bodenarten": sorted(e.klassen), "rgb": farbe(sorted(e.klassen)[0], nummer[e.klasse]),
                "bohrungen": st}
        kp = koerper(m.punkte, m.dreiecke, m.rand, oben, unten)
        traeger = d >= MIN_MAECHTIGKEIT
        hinweise = []
        if np.all(np.abs(unten - m.basis) < 1e-6):
            hinweise.append("Unterkante = Modellbasis (keine Bohrung erreicht die Unterkante)")
        if not st["vorhanden"]:
            hinweise.append("in keiner Bohrung angetroffen")
        if m.ausgeduennt and m.ausgeduennt[j]:
            hinweise.append("Ausdehnung begrenzt: endet etwa auf halbem Weg zu Bohrungen ohne diese Einheit")
        if kp is None:
            info.update(knoten=None, flaechen=None, pruefung={"geschlossen": True, "volumen": 0.0}, volumen_m3=0.0)
        else:
            pr = pruefen(*kp)
            info.update(knoten=kp[0], flaechen=kp[1], pruefung=pr,
                        volumen_m3=volumen_prismen(m.punkte, m.dreiecke, oben, unten))
        info.update(maechtigkeit_max=float(d.max()),
                    maechtigkeit_mittel=float(d[traeger].mean()) if traeger.any() else 0.0,
                    max_abstand_bohrung=float(m.abstand[traeger].max()) if traeger.any() else None,
                    hinweise=hinweise)
        m.koerper.append(info)


def einheit_schichten(m: Modell, j: int) -> list[dict]:
    """Schichten des PDFs, die die Einheit j bilden: Bohrung, Tiefe, Bodenart und Beschreibung."""
    e = m.einheiten[j]
    out = []
    for b in m.bohrungen:
        idx: list[int] = []
        for op, i, einheit in m.zuordnung.get(b.code, []):
            if einheit is e and op in ("M", "C", "E") and i is not None:
                idx += b.abschnitte[i].schichten
        for k in sorted(set(idx)):
            if k < len(b.schichten):
                out.append({"bohrung": b.code, **b.schichten[k]})
    return out


def _benennungen(schichten: list[dict]) -> str:
    """Benennungen nach Norm mit Haeufigkeit: 'Mittelsand, schwach schluffig (3x); Feinsand (1x)'."""
    zaehler: dict[str, int] = {}
    for s in schichten:
        d = deuten(s["beschreibung"], s["bodenart"])
        if d.benennung:
            zaehler[d.benennung] = zaehler.get(d.benennung, 0) + 1
    return "; ".join(f"{n} ({k}x)" for n, k in sorted(zaehler.items(), key=lambda t: -t[1]))


def ifc_schreiben(m: Modell, pfad, docs: list[dict], bohrsaeulen: bool = True,
                  projekt: str = "Baugrundmodell aus Gutachten", pruefstand: str | None = None,
                  durchmesser: float | None = None, durchmesser_je: dict[str, float] | None = None,
                  umgebung: float = UMGEBUNG_STANDARD, gebaeude: list[dict] | None = None,
                  gebaeude_info: dict | None = None) -> dict:
    """IfcGeomodel (Einheiten) + IfcBorehole (Bohrsaeulen der modellierten Bohrungen) + Gelaende um das Modell.

    pruefstand: Stand der Pruefung durch den Nutzer (App: "Einchecken"), steht im CPset_Baugrundmodell.
    durchmesser: Saeulen aller Bohrungen in m (None = automatisch nach Modellgroesse); durchmesser_je: je Code.
    umgebung: Gelaende aus dem DGM so weit um das Modellgebiet (m; 0 = keines), nur wenn die Oberkante aus dem DGM kommt.
    gebaeude: LoD2-Gebaeude der Umgebung im System des Modells (geodaten.gebaeude), gebaeude_info: Quelle und Lizenz.
    """
    aus = IfcAusgabe(projekt, m.epsg, m.ursprung)
    quellen = sorted({d["document"]["file"] for d in docs})
    n = len(m.einheiten)
    einheiten = []
    for j, k in enumerate(m.koerper):
        if k["knoten"] is None:
            continue
        schichten = einheit_schichten(m, j)
        einheiten.append({
            "name": k["name"], "knoten": k["knoten"], "flaechen": k["flaechen"], "rgb": k["rgb"],
            "geschlossen": k["pruefung"]["geschlossen"], "beschreibung": f"Modelleinheit {j + 1}/{n}",
            "eigenschaften": {
                "Einheit": k["name"], "Reihenfolge": j + 1, "Bodenarten": ", ".join(k["bodenarten"]),
                "Farbe": hexfarbe(k["rgb"]), "Volumen_m3": round(k["volumen_m3"], 1),
                "Maechtigkeit_max_m": round(k["maechtigkeit_max"], 2),
                "Maechtigkeit_mittel_m": round(k["maechtigkeit_mittel"], 2),
                "Max_Abstand_Bohrung_m": round(k["max_abstand_bohrung"], 1) if k["max_abstand_bohrung"] is not None else None,
                "Bohrungen_vorhanden": ", ".join(k["bohrungen"]["vorhanden"]),
                "Bohrungen_fehlt": ", ".join(k["bohrungen"]["fehlt"]),
                "Bohrungen_unbekannt": ", ".join(k["bohrungen"]["unbekannt"]),
                "Geschlossen": bool(k["pruefung"]["geschlossen"]),
                "Farbname_DIN4023": farbinfo(k["bodenarten"][0])["name"],
                # alle Beschreibungen aus dem PDF, die diese Einheit bilden, und ihre Benennung nach Norm
                "Beschreibungen": " | ".join(f"{s['bohrung']} {s['von']:.2f}-{s['bis']:.2f} m: {s['beschreibung'] or '-'}"
                                             for s in schichten),
                "Benennungen": _benennungen(schichten),
                "Hinweise": "; ".join(k["hinweise"])}})
    p = m.parameter
    aus.geomodell(f"Baugrundmodell (Layer-Cake, {p['methode'].upper()})", einheiten, {
        "Verfahren": "Layer-Cake: Einheiten per Schichtfolgen-Korrelation, Flaechen exakt an den Bohrungen",
        "Interpolation": {"idw": "IDW p=2", "tps": "Duennplatten-Spline",
                          "implizit": "implizit (GemPy, ein Skalarfeld je Flaeche; Orientierung siehe Bericht)"
                          }.get(p["methode"], p["methode"]),
        "Raster_m": round(p["raster_m"], 2), "Puffer_m": round(p["puffer_m"], 1),
        "Modellbasis_NHN": round(m.basis, 2), "Lagebezug": f"EPSG:{m.epsg}" if m.epsg else "lokal (ohne Georeferenz)",
        "Bohrungen_im_Modell": ", ".join(b.code for b in m.bohrungen),
        "Nicht_im_Modell": "; ".join(f"{a['code']} ({a['grund']})" for a in m.ausgeschlossen),
        "Quellen": ", ".join(quellen), "Modellierer": f"baugrundmodell {__version__}",
        "Ursprung_Rechtswert": m.ursprung[0], "Ursprung_Hochwert": m.ursprung[1],
        "Gelaende": gelaende_text(p.get("gelaende") or {}),
        "Reifegrad": p.get("reifegrad"),
        "Herkunft_Bohrungen": ", ".join(f"{h} {n}" for h, n in sorted((p.get("herkunft") or {}).items())),
        "Pruefstand": pruefstand, "Hinweise": "; ".join(m.hinweise)})
    gelaende = None
    if m.dgm is not None and umgebung > 0:
        gelaende = ring(m.dgm, m.punkte, m.rand, m.flaechen[0], m.ursprung, umgebung, schritt=p["raster_m"])
    if gelaende is not None:
        gel = p.get("gelaende") or {}
        quelle = gel.get("quelle_dienst") or {}
        aus.gelaende(gelaende["knoten"], gelaende["dreiecke"], {
            "DGM": gel.get("name"), "Raster_DGM_m": gel.get("raster_m"),
            "Dienst": quelle.get("titel"), "Anbieter": quelle.get("anbieter"), "Lizenz": quelle.get("lizenz"),
            "Namensnennung": quelle.get("namensnennung"), "Abgerufen": quelle.get("abgerufen"),
            "Abstand_m": gelaende["abstand_m"], "Schrittweite_m": gelaende["schritt_m"],
            "Hinweis": "Gelände um das Baugrundmodell; innerhalb bildet die Oberkante des Modells das Gelände "
                       "(an den Bohrungen auf ihre GOK gezogen)"})
    if bohrsaeulen:
        codes = {b.code: b for b in m.bohrungen}
        auto = standard_durchmesser(m.parameter.get("ausdehnung_m", 100.0))
        for d in docs:
            for b in d["boreholes"]:
                vb = codes.get(b["code"])
                if vb is not None and vb.dokument == d["document"]["file"] and abs(vb.x - b["x"]) < 0.5:
                    if (durchmesser_je or {}).get(b["code"]):
                        dm, quelle = float(durchmesser_je[b["code"]]), "manuell (Bohrung)"
                    elif durchmesser:
                        dm, quelle = float(durchmesser), "manuell (Projekt)"
                    else:
                        dm, quelle = auto, "automatisch (Darstellung nach Modellgroesse)"
                    aus.bohrung(d["document"], b, (vb.x - m.ursprung[0], vb.y - m.ursprung[1]), vb.lage, vb.hoehe,
                                durchmesser=dm, durchmesser_quelle=quelle)
    n_gebaeude = 0
    if gebaeude:
        e0, n0 = m.ursprung
        lokal = [{**b, "flaechen": [{"art": fl["art"], "ring": [(p[0] - e0, p[1] - n0, p[2]) for p in fl["ring"]],
                                     "loecher": [[(p[0] - e0, p[1] - n0, p[2]) for p in r] for r in fl.get("loecher") or []]}
                                    for fl in b["flaechen"]]} for b in gebaeude]
        info = gebaeude_info or {}
        n_gebaeude = aus.gebaeude(lokal, {k: v for k, v in info.items() if isinstance(v, (str, int, float))},
                                  info.get("dienste") or {})
    aus.schreiben(pfad)
    return {"einheiten": len(einheiten), "bohrungen": len(m.bohrungen), "gelaende": gelaende is not None,
            "gebaeude": n_gebaeude}


def bericht(m: Modell) -> dict:
    """Pruefbericht (JSON): Einheiten, Zuordnung je Bohrung, Ausschluesse, Pruefungen, Vorlage fuer --einheiten."""
    bohr = []
    for bi, (b, ks) in enumerate(zip(m.bohrungen, m.kontakte)):
        zeilen = []
        for j, (e, k) in enumerate(zip(m.einheiten, ks)):
            zeilen.append({"einheit": e.name, "status": k.status, "unterkante_art": k.art,
                           "ok_modell": round(float(m.flaechen[j][bi]), 3),
                           "uk_modell": round(float(m.flaechen[j + 1][bi]), 3)})
        bohr.append({"code": b.code, "dokument": b.dokument, "x": b.x, "y": b.y, "gok": b.gok,
                     "lage": b.lage, "hoehe": b.hoehe,
                     "endteufe_nhn": round(b.ende, 3),
                     "abschnitte": [{"bodenart": a.klasse, "ok": round(a.ok, 3), "uk": round(a.uk, 3)} for a in b.abschnitte],
                     "einheiten": zeilen, "hinweise": b.hinweise})
    return {
        "modellierer": __version__, "epsg": m.epsg, "ursprung": m.ursprung, "parameter": m.parameter,
        "reifegrad": m.parameter.get("reifegrad", "Gutachten"),
        "einheiten": [{"name": k["name"], "bodenarten": k["bodenarten"], "farbe": hexfarbe(k["rgb"]),
                       "volumen_m3": round(k["volumen_m3"], 1), "maechtigkeit_max_m": round(k["maechtigkeit_max"], 2),
                       "geschlossen": bool(k["pruefung"]["geschlossen"]), "bohrungen": k["bohrungen"],
                       "schichten": einheit_schichten(m, j), "hinweise": k["hinweise"]} for j, k in enumerate(m.koerper)],
        "bohrungen": bohr,
        "ausgeschlossen": m.ausgeschlossen,
        "pruefungen": {"max_abweichung_an_bohrungen_m": round(m.max_abweichung, 4),
                       "alle_koerper_geschlossen": all(k["pruefung"]["geschlossen"] for k in m.koerper),
                       "zensurpunkte": m.zensurpunkte,
                       "netz": {"knoten": int(len(m.punkte)), "dreiecke": int(len(m.dreiecke))}},
        "hinweise": m.hinweise,
        "vorlage_einheiten": [{"name": e.name, "bodenarten": sorted(e.klassen)} for e in m.einheiten],
    }
