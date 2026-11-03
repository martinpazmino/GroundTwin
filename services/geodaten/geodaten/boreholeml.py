"""BoreholeML 3.2 – das Austauschformat der Staatlichen Geologischen Dienste (AK BoreholeML4, MIT-Lizenz, docs/23).

Export: gepruefte Bohrungen (wirksame Werte der App) als OGC-API-FeatureCollection mit bml:Borehole, so wie die
amtlichen Beispiele. Nur was belegt ist, wird kodiert: Petrographie/Genese, Konsistenz, Lagerung, Kalk und Feuchte
ueber boreholeml_codes.json (amtliche Namen als Beleg); die Beschreibung aus dem Gutachten steht immer im Klartext
(descriptiveText). Grundwasserstaende stehen nur als Text, weil das PDF Anschnitt und Ruhewasser nicht unterscheidet.

Import: bml:Borehole (3.0.1 bis 3.2) in das kanonische JSON der Extraktion, mit Herkunft; SEP3-Codes werden ueber
die Hierarchie der Codelisten einer Bodenart der App zugeordnet, sonst bleibt die Schicht unklassifiziert (markiert).
"""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

BML = "https://schemas.bgr.de/boreholeml/3.2"
GML = "http://www.opengis.net/gml/3.2"
GMD = "http://www.isotc211.org/2005/gmd"
GCO = "http://www.isotc211.org/2005/gco"
SF = "http://www.opengis.net/ogcapi-features-1/1.0/sf"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMA_ORT = (f"{SF} https://schemas.opengis.net/ogcapi/features/part1/1.0/xml/core-sf.xsd "
              f"{BML} https://schemas.bgr.de/boreholeml/3.2/BoreholeML.xsd")
CODES = json.loads(Path(__file__).with_name("boreholeml_codes.json").read_text(encoding="utf-8"))
CL = CODES["quelle"]["url"]
EPSG_URI = "http://www.opengis.net/def/crs/EPSG/0/"
# Lage: horizontales System -> (UTM + DHHN92-Hoehe, Abzug der Zonenkennung im Rechtswert). Fuer UTM mit DHHN2016 gibt
# es kein zusammengesetztes EPSG; wie die amtlichen Beispiele 5555/5556 (Unterschied zu DHHN2016 wenige cm).
SYSTEME_3D = {25831: (5554, 0.0), 25832: (5555, 0.0), 4647: (5555, 32_000_000.0),
              25833: (5556, 0.0), 5650: (5556, 33_000_000.0)}
HORIZONTAL = {5554: 25831, 5555: 25832, 5556: 25833}

for _p, _ns in (("bml", BML), ("gml", GML), ("gmd", GMD), ("gco", GCO), ("sf", SF), ("xsi", XSI)):
    ET.register_namespace(_p, _ns)


# ---------------------------------------------------------------- Bausteine
def _e(eltern: ET.Element, ns: str, name: str, text=None, **attr) -> ET.Element:
    el = ET.SubElement(eltern, f"{{{ns}}}{name}", {k.replace("__", ":"): str(v) for k, v in attr.items()})
    if text is not None:
        el.text = str(text)
    return el


def _nil(eltern: ET.Element, name: str) -> ET.Element:
    return _e(eltern, BML, name, **{f"{{{XSI}}}nil": "true"})


def _code(eltern: ET.Element, name: str, eintrag: dict) -> ET.Element:
    return _e(eltern, BML, name, eintrag["code"], codeSpace=f"{CL}{eintrag['liste']}.xml")


def _text(eltern: ET.Element, name: str, text: str, sprache: bool = True) -> ET.Element:
    el = _e(eltern, BML, name)
    attr = {"locale": f"{CL}DE.xml"} if sprache else {}
    _e(el, GMD, "LocalisedCharacterString", text, **attr)
    return el


def _laenge(eltern: ET.Element, name: str, wert: float) -> ET.Element:
    return _e(eltern, BML, name, f"{float(wert):.2f}", uom="m")


def _ncname(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text)


def _m(v: float) -> str:
    return f"{float(v):.2f}".replace(".", ",")


# ---------------------------------------------------------------- Export
def exportierbar(b: dict) -> str:
    """Grund, warum eine Bohrung nicht exportiert wird ('' = exportierbar)."""
    schichten = b.get("layers") or []
    if b.get("herkunft") in ("SGD", "BoreholeML"):
        return "aus dem Bestand des Landes bzw. einer BoreholeML-Datei, nicht aus dem Gutachten"
    if not schichten:
        return "keine Schichten"
    if not all(ly.get("geprueft") for ly in schichten):
        return "nicht vollständig geprüft"
    if b.get("x") is None or b.get("y") is None:
        return "ohne Koordinaten"
    epsg = b.get("crs_epsg")
    if not epsg:
        return "ohne Koordinatensystem (EPSG)"
    if int(epsg) not in SYSTEME_3D:
        return f"EPSG:{int(epsg)} – für BoreholeML in ETRS89/UTM umrechnen"
    if b.get("gok_nhn") is None or b.get("gok_source") == "relativ":
        return "ohne GOK in m NHN"
    return ""


def exportieren(dokumente: list[dict], *, projekt: str, organisation: str = "", sig: str = "groundtwin",
                heute: date | None = None, dgm_zelle: float | None = None) -> tuple[bytes, dict]:
    """dokumente: wirksame Dokumente (kanonisches JSON mit Korrekturen, Pruefvermerken und Quellen der Lage/GOK).

    Rueckgabe: BoreholeML (UTF-8) und Bericht {exportiert, ausgelassen [{code, grund}], hinweise}."""
    from baugrundmodell.normen import UNKLASSIFIZIERT, deuten   # Deutung wie in der App (services/modeler)

    heute = heute or date.today()
    wurzel = ET.Element(f"{{{SF}}}FeatureCollection", {f"{{{XSI}}}schemaLocation": SCHEMA_ORT})
    bericht: dict = {"exportiert": [], "ausgelassen": [], "hinweise": []}
    nicht_kodiert: dict[str, int] = {}
    for d in dokumente:
        for b in d.get("boreholes") or []:
            grund = exportierbar(b)
            if grund:
                bericht["ausgelassen"].append({"code": b.get("code", "?"), "grund": grund})
                continue
            nr = len(bericht["exportiert"]) + 1
            _bohrung(_e(wurzel, SF, "featureMember"), b, d, f"GT_{_ncname(sig)}_{nr}", projekt, organisation, heute,
                     dgm_zelle, deuten, UNKLASSIFIZIERT, nicht_kodiert)
            bericht["exportiert"].append(b["code"])
    if not bericht["exportiert"]:
        raise ValueError("keine exportierbare Bohrung: " + "; ".join(f"{a['code']}: {a['grund']}"
                                                                      for a in bericht["ausgelassen"][:8]))
    bericht["hinweise"] = [
        "Höhen als DHHN92 gekennzeichnet (EPSG 5554/5555/5556 wie die amtlichen Beispiele; „m NHN“ im Gutachten, "
        "Unterschied zu DHHN2016 wenige cm).",
        "Grundwasserstände nur als Text im Schichtenverzeichnis: das PDF unterscheidet Anschnitt und Ruhewasser nicht.",
        "Kodierung der Schichten: Kurzzeichen nach DIN 4022/4023 (codingStandard DIN4022), Beschreibung aus dem "
        "Gutachten im Klartext; Petrographie und Genese über die amtlichen Codelisten.",
    ] + [f"nicht kodiert (steht in der Beschreibung): {k} – {n} Schichten" for k, n in sorted(nicht_kodiert.items())]
    ET.indent(wurzel, space="  ")
    return ET.tostring(wurzel, encoding="utf-8", xml_declaration=True), bericht


def _bohrung(mitglied: ET.Element, b: dict, d: dict, fid: str, projekt: str, organisation: str, heute: date,
             dgm_zelle: float | None, deuten, unklassifiziert: str, nicht_kodiert: dict) -> None:
    epsg = int(b["crs_epsg"])
    epsg3d, abzug = SYSTEME_3D[epsg]
    x, y, gok = float(b["x"]) - abzug, float(b["y"]), float(b["gok_nhn"])
    ende = float(b.get("end_depth") or max(ly["bottom_depth"] for ly in b["layers"]))
    bh = _e(mitglied, BML, "Borehole", **{f"{{{GML}}}id": fid})
    _e(bh, GML, "identifier", b["code"], codeSpace=f"urn:groundtwin:{_ncname(projekt) or 'projekt'}")
    punkt = _e(_e(bh, BML, "location"), GML, "Point", **{f"{{{GML}}}id": f"{fid}_LOC", "srsName": f"{EPSG_URI}{epsg3d}"})
    _e(punkt, GML, "pos", f"{x:.3f} {y:.3f} {gok:.2f}")
    linie = _e(_e(bh, BML, "boreholePath"), GML, "LineString",
               **{f"{{{GML}}}id": f"{fid}_PATH", "srsName": f"{EPSG_URI}{epsg3d}"})
    _e(linie, GML, "posList", f"{x:.3f} {y:.3f} {gok:.2f} {x:.3f} {y:.3f} {gok - ende:.2f}")
    _e(bh, BML, "id", b["code"])
    _text(bh, "shortName", b["code"])
    _text(bh, "fullName", f"{projekt} {b['code']}".strip())
    fest = CODES["fest"]
    _code(bh, "boreholeStatus", fest["BoreholeStatusList"])
    _laenge(bh, "totalLength", ende)
    seg = _e(_e(bh, BML, "boreholeSegment"), BML, "BoreholeSegment")
    _laenge(seg, "from", 0.0)
    _laenge(seg, "to", ende)
    _e(seg, BML, "azimuth", "0.00", uom="deg")
    _e(seg, BML, "inclination", "0.00", uom="deg")
    _code(seg, "segmentDataQuality", fest["SegmentDataQualityList"])
    _code(bh, "databaseSource", fest["DatabaseSourceList"])
    _e(bh, BML, "exportDate", heute.isoformat())
    _e(_e(bh, BML, "language"), GMD, "LanguageCode", "deu", codeList=f"{CL}LanguageCode.xml", codeListValue="deu")
    _code(bh, "codingStandard", fest["CodingStandardList"])
    anbieter = _e(_e(bh, BML, "organisation"), BML, "BoreholeProvider")
    _e(_e(anbieter, GMD, "organisationName"), GCO, "CharacterString", organisation.strip() or "nicht angegeben")
    _e(_e(anbieter, GMD, "role"), GMD, "CI_RoleCode", "originator",
       codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode",
       codeListValue="originator")
    if projekt:
        _e(bh, BML, "project", projekt)
    _nil(bh, "owner")
    _nil(bh, "locationName")
    herkunft = _e(_e(bh, BML, "origin"), BML, "Origin")
    _e(herkunft, BML, "originalLocation", f"{float(b['x']):.3f} {y:.3f}", srsName=f"{EPSG_URI}{epsg}")
    _e(herkunft, BML, "elevation", f"{gok:.2f}")
    lage = CODES["lage"].get(b.get("coord_source") or "PDF") or CODES["lage"]["PDF"]
    _code(herkunft, "locationMethod", lage)
    _code(herkunft, "levelMethod", _hoehenbestimmung(b.get("gok_source"), dgm_zelle))
    _nil(bh, "drillingDate")
    _nil(bh, "drillingMethod")
    _code(bh, "drillingPurpose", fest["DrillingPurposeList"])
    gw = b.get("groundwater") or []
    if gw:
        _e(bh, BML, "groundwaterEncountered", "true")
    elif (b.get("groundwater_status") or "").lower().startswith("kein"):
        _e(bh, BML, "groundwaterEncountered", "false")
    else:
        _nil(bh, "groundwaterEncountered")
    _nil(bh, "lastHorizon")
    _nil(bh, "drillingProcess")
    reihe = _e(_e(bh, BML, "intervalSeries"), BML, "IntervalSeries")
    _e(reihe, BML, "version", "1")
    _text(reihe, "description", "Schichtenverzeichnis aus dem Gutachten")
    datei = (d.get("document") or {}).get("file") or "Gutachten"
    notiz = (f"Aus dem Gutachten {datei} mit GroundTwin gelesen und vom Bearbeiter geprüft; Beschreibung nach "
             "DIN 4022 / DIN EN ISO 14688-1, Kurzzeichen nach DIN 4023.")
    if gw:
        notiz += (" Grundwasser im Bohrprofil: " + ", ".join(f"{_m(g['depth'])} m u. GOK" for g in gw)
                  + " (Anschnitt oder Ruhewasser im PDF nicht unterschieden).")
    _text(reihe, "stratlogDescription", notiz)
    for ly in b["layers"]:
        _schicht(_e(_e(reihe, BML, "layer"), BML, "Interval"), ly, deuten, unklassifiziert, nicht_kodiert)
    _nil(bh, "installationDetail")


def _hoehenbestimmung(quelle: str | None, dgm_zelle: float | None) -> dict:
    hoehe = CODES["hoehe"]
    if quelle == "DGM":
        weite = f"DGM{int(round(dgm_zelle))}" if dgm_zelle and abs(dgm_zelle - round(dgm_zelle)) < 1e-6 else "DGM"
        return hoehe.get(weite, hoehe["DGM"])
    return hoehe.get(quelle or "PDF", hoehe["PDF"])


def _schicht(iv: ET.Element, ly: dict, deuten, unklassifiziert: str, nicht_kodiert: dict) -> None:
    klasse = ly.get("soil_class") or None
    beschreibung = (ly.get("description_raw") or "").strip()
    n = deuten(beschreibung, klasse)
    _laenge(iv, "from", ly["top_depth"])
    _laenge(iv, "to", ly["bottom_depth"])
    if n.din4023:
        _e(iv, BML, "rockCode", n.din4023)
    if n.benennung:
        _text(iv, "rockNameText", n.benennung)
    ba = CODES["bodenart"].get(klasse or "")
    genese = (ba or {}).get("genese")
    if not genese:                                         # Deutung: "A (S)" = Auffuellung aus Sand, "Mu" = Oberboden
        kurz = (n.din4023 or "").split(",")[0].split("(")[0].strip()
        genese = {"A": CODES["bodenart"]["Auffuellung"]["genese"],
                  "Mu": CODES["bodenart"]["Mutterboden"]["genese"]}.get(kurz)
    if genese:
        _code(iv, "geoGenesis", genese)
    for name, schluessel, wert in (("carbonateContent", "kalk", n.kalk), ("waterContent", "feuchte", n.feuchte),
                                   ("consistency", "konsistenz", n.konsistenz), ("compactness", "lagerung", n.lagerung)):
        if not wert:
            continue
        eintrag = CODES[schluessel].get(wert)
        if eintrag:
            _code(iv, name, eintrag)
        else:
            nicht_kodiert[f"{schluessel} „{wert}“"] = nicht_kodiert.get(f"{schluessel} „{wert}“", 0) + 1
    if beschreibung:
        _text(iv, "descriptiveText", beschreibung, sprache=False)
    if ba:
        lith = _e(_e(iv, BML, "lithology"), BML, "Lithology")
        _code(lith, "rockName", ba["petrographie"])
        if n.bodenfarbe:
            _text(lith, "rockColorText", n.bodenfarbe)
    else:
        nicht_kodiert[f"Bodenart „{klasse or unklassifiziert}“"] = nicht_kodiert.get(
            f"Bodenart „{klasse or unklassifiziert}“", 0) + 1
        _nil(iv, "lithology")
    _nil(iv, "stratigraphy")


# ---------------------------------------------------------------- Import
_UMKEHR_ZWEI: dict[tuple, list[str]] = {}
_UMKEHR_EINS: dict[str, list[str]] = {}
for _k, _v in CODES["bodenart"].items():                  # Reihenfolge der Tabelle: zuerst die allgemeine Bodenart
    if _v["genese"]:
        _UMKEHR_ZWEI.setdefault((_v["petrographie"]["code"], _v["genese"]["code"]), []).append(_k)
    else:
        _UMKEHR_EINS.setdefault(_v["petrographie"]["code"], []).append(_k)


# Nur beim Import: kuenstliches Lockermaterial ohne Genese ist eine Auffuellung (der Export schreibt la + yf)
_NUR_IMPORT = {"la": "Auffuellung"}


def _kette(code: str | None, eltern: dict) -> list[str]:
    out = []
    while code and code not in out:
        out.append(code)
        code = eltern.get(code)
    return out


def bodenart_aus(petro: str | None, genese: str | None) -> tuple[str | None, str]:
    """(Bodenart der App, Hinweis) zu Petrographie (+ Genese); ueber die Hierarchie der Codelisten (fS -> S -> Sand).
    Passen mehrere Bodenarten (kuenstlicher Feststoff: Beton, Asphalt …), gilt die erste und der Hinweis nennt alle."""
    treffer = None
    for g in _kette(genese, CODES["genese_eltern"]):
        for p in _kette(petro, CODES["petrographie_eltern"]):
            if treffer is None and (p, g) in _UMKEHR_ZWEI:
                treffer = _UMKEHR_ZWEI[(p, g)]
    for p in _kette(petro, CODES["petrographie_eltern"]):
        if treffer is None and p in _UMKEHR_EINS:
            treffer = _UMKEHR_EINS[p]
    if not treffer and any(p in _NUR_IMPORT for p in _kette(petro, CODES["petrographie_eltern"])):
        treffer = [next(_NUR_IMPORT[p] for p in _kette(petro, CODES["petrographie_eltern"]) if p in _NUR_IMPORT)]
    if not treffer:
        return None, (f"Petrographie „{petro}“ keiner Bodenart zugeordnet" if petro else "keine Petrographie angegeben")
    andere = [k for k in treffer[1:] if k not in ("Glimmerton", "Lauenburger Ton")]   # Namen, keine Lithologie
    return treffer[0], (f"mehrdeutig ({', '.join(treffer[:1] + andere)}) – {treffer[0]} angenommen" if andere else "")


def _lokal(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _kind(el: ET.Element, name: str) -> ET.Element | None:
    return next((c for c in el if _lokal(c) == name), None)


def _kinder(el: ET.Element, name: str) -> list[ET.Element]:
    return [c for c in el if _lokal(c) == name]


def _textwert(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return " ".join(t.strip() for t in el.itertext() if t.strip())


def _zahl(el: ET.Element | None) -> float | None:
    try:
        return float(_textwert(el))
    except ValueError:
        return None


def _epsg(srs: str | None) -> int | None:
    m = re.search(r"(\d+)\s*$", srs or "")
    return int(m.group(1)) if m else None


def importieren(daten: bytes, name: str = "boreholeml.xml") -> dict:
    """BoreholeML (FeatureCollection oder einzelne Bohrung) -> ein Dokument im kanonischen JSON der Extraktion."""
    try:
        wurzel = ET.fromstring(daten)
    except ET.ParseError as err:
        raise ValueError(f"{name}: kein lesbares XML ({err})") from None
    if _lokal(wurzel) == "ExceptionReport":
        raise ValueError(f"{name}: Fehlermeldung des Dienstes – {_textwert(wurzel)[:300]}")
    bohrungen = [el for el in wurzel.iter() if _lokal(el) == "Borehole" and "boreholeml" in el.tag]
    if not bohrungen:
        raise ValueError(f"{name}: keine BoreholeML-Bohrung (bml:Borehole) gefunden")
    rahmen = next((el.get("srsName") for el in wurzel.iter() if _lokal(el) == "Envelope" and el.get("srsName")), None)
    return {"document": {"file": name, "sha256": hashlib.sha256(daten).hexdigest(), "parser_version": "boreholeml",
                         "pages": None},
            "boreholes": [_bohrung_lesen(b, rahmen) for b in bohrungen], "soundings": {}}


def _bohrung_lesen(bh: ET.Element, rahmen_srs: str | None = None) -> dict:
    hinweise: list[str] = []
    punkt = next((el for el in bh.iter() if _lokal(el) == "Point"), None)
    werte = [float(v) for v in _textwert(_kind(punkt, "pos") if punkt is not None else None).split()] if punkt is not None else []
    eigener = next((el.get("srsName") for el in bh.iter() if _lokal(el) == "Envelope" and el.get("srsName")), None)
    epsg = _epsg((punkt.get("srsName") if punkt is not None else None) or eigener or rahmen_srs)
    x = y = gok = None
    if len(werte) >= 2:
        x, y = werte[0], werte[1]
    if len(werte) >= 3:
        gok = werte[2]
    if epsg in HORIZONTAL:
        epsg = HORIZONTAL[epsg]
    herkunft = next((el for el in bh.iter() if _lokal(el) == "Origin"), None)
    if gok is None and herkunft is not None:
        gok = _zahl(_kind(herkunft, "elevation"))
    code = _textwert(_kind(bh, "shortName")) or _textwert(_kind(bh, "id")) or "?"
    quelle = _textwert(_kind(bh, "databaseSource")) or "BoreholeML"
    reihen = [el for el in bh.iter() if _lokal(el) == "IntervalSeries"]
    reihe = max(reihen, key=lambda r: _zahl(_kind(r, "version")) or 0.0) if reihen else None
    if len(reihen) > 1:
        hinweise.append(f"{len(reihen)} Schichtenverzeichnisse – das mit der höchsten Version übernommen")
    schichten = []
    for lage in (_kinder(reihe, "layer") if reihe is not None else []):
        iv = _kind(lage, "Interval")
        if iv is not None:
            schichten.append(_schicht_lesen(iv, quelle))
    if not schichten:
        hinweise.append("ohne Schichtdaten (nicht freigegeben oder nicht vorhanden)")
    elif all(ly["soil_class"] is None for ly in schichten):
        hinweise.append("Schichten ohne Petrographie (nur Tiefen bzw. Stratigraphie freigegeben)")
    gw = []
    for g in (el for el in bh.iter() if _lokal(el) == "Groundwater"):
        for feld, art in (("entryDepth", "angetroffen"), ("balancedLevel", "Ruhewasser"), ("endLevel", "Bohrende")):
            t = _zahl(_kind(g, feld))
            if t is not None:
                gw.append({"depth": t, "nhn": None if gok is None else round(gok - t, 2), "kind": art})
    ende = _zahl(_kind(bh, "totalLength"))
    fremd_id = _textwert(_kind(bh, "id"))
    hinweise.insert(0, f"aus BoreholeML ({quelle}{', ID ' + fremd_id if fremd_id else ''}) – nicht aus dem Gutachten")
    return {"code": code, "kind": "Bohrung", "gok_nhn": gok, "gok_source": "BoreholeML" if gok is not None else None,
            "end_depth": ende,
            "x": x, "y": y, "crs_epsg": epsg, "coord_source": f"BoreholeML ({quelle})",
            "herkunft": "SGD" if quelle not in ("na", "FA") else "BoreholeML", "quelle": quelle,
            "fremd_id": fremd_id,
            "layers": schichten, "groundwater": gw,
            "groundwater_status": {"true": "", "false": "kein Grundwasser"}.get(_textwert(_kind(bh, "groundwaterEncountered")), ""),
            "checks": {}, "issues": hinweise,
            "provenance": [{"page": None, "bbox": None, "method": "BoreholeML"}]}


def _schicht_lesen(iv: ET.Element, quelle: str) -> dict:
    lithologien = []
    for lit in (el for el in iv if _lokal(el) == "lithology"):
        l2 = _kind(lit, "Lithology")
        if l2 is None:
            continue
        anteil = _zahl(_kind(l2, "percentage")) or _zahl(_kind(l2, "percentageTo")) or 0.0
        lithologien.append((anteil, _textwert(_kind(l2, "rockName")), _textwert(_kind(l2, "rockColorText"))))
    haupt = max(lithologien, key=lambda t: t[0]) if lithologien else (0.0, "", "")
    genese = _textwert(_kind(iv, "geoGenesis")) or None
    klasse, hinweis = bodenart_aus(haupt[1] or None, genese)
    text = "; ".join(t for t in (_textwert(_kind(iv, "rockNameText")), _textwert(_kind(iv, "descriptiveText"))) if t)
    hinweise = [hinweis] if hinweis else []
    return {"top_depth": _zahl(_kind(iv, "from")), "bottom_depth": _zahl(_kind(iv, "to")),
            "description_raw": text, "soil_class": klasse, "hatch_class": None, "confidence": None,
            "label_confirmed": None, "issues": hinweise, "rock_code": _textwert(_kind(iv, "rockCode")) or None,
            "provenance": [{"page": None, "method": f"BoreholeML ({quelle})"}]}
