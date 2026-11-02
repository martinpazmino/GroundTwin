"""Erzeugt geodaten/boreholeml_codes.json aus den amtlichen BoreholeML-Codelisten (v2, MIT-Lizenz, AK BoreholeML4).

Jede Zuordnung (Bodenart der App -> Petrographie/Genese, Konsistenz, Lagerung, Kalk, Feuchte, Hoehen- und
Lagebestimmung, feste Kopfangaben) wird ueber den amtlichen deutschen Namen in der Codeliste gesucht; gespeichert
werden Code, Name und Liste als Beleg (wie normen.json). Fehlt ein Name oder ist er mehrdeutig, bricht das Skript ab.

    python services/geodaten/werkzeuge/boreholeml_codes.py [<ordner_mit_codelisten>]
    (ohne Ordner: Download von https://schemas.bgr.de/boreholeml/codelists/v2/ in einen Zwischenordner)
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

BASIS = "https://schemas.bgr.de/boreholeml/codelists/v2/"
ZIEL = Path(__file__).resolve().parents[1] / "geodaten" / "boreholeml_codes.json"
NS = {"gml": "http://www.opengis.net/gml/3.2", "gmx": "http://www.isotc211.org/2005/gmx",
      "bmlcl": "https://schemas.bgr.de/boreholeml/codelists/v2"}

# Bodenart der App (normen.json) -> (Petrographie in RockNameList, Genese in GeoGenesisList oder None, Hinweis)
BODENART = {
    "Kies": ("Kies", None, ""), "Sand": ("Sand", None, ""), "Schluff": ("Schluff", None, ""), "Ton": ("Ton", None, ""),
    "Steine": ("Steine", None, ""), "Bloecke": ("Blöcke", None, ""), "Torf": ("Torf", None, ""),
    "Mudde": ("Organisches Lockergestein", "Mudde", ""),
    "Mutterboden": ("Lockergestein", "Humoser Oberboden", "Petrographie des Oberbodens nicht bestimmt"),
    "Auffuellung": ("Künstliches Lockermaterial", "Auffüllung", ""),
    "Geschiebemergel": ("Mergel", "Till", ""), "Geschiebelehm": ("Lehm", "entkalkter Till", ""),
    "Loess": ("Schluff", "Löss", ""), "Loesslehm": ("Lehm", "Lösslehm", ""),
    "Lehm": ("Lehm", None, ""), "Mergel": ("Mergel", None, ""),
    "Klei": ("Ton", "Marsch", "Klei als Marschenton"),
    "Glimmerton": ("Ton", None, "lithostratigraphischer Name nicht kodiert"),
    "Lauenburger Ton": ("Ton", None, "lithostratigraphischer Name nicht kodiert"),
    "Beton": ("Künstlicher Feststoff", "Anthropogene Bildungen", ""),
    "Asphalt": ("Künstlicher Feststoff", "Anthropogene Bildungen", ""),
    "Schwarzdecke": ("Künstlicher Feststoff", "Anthropogene Bildungen", ""),
    "Pflaster": ("Künstlicher Feststoff", "Anthropogene Bildungen", ""),
    "Fels": ("Festgestein", None, ""),
    "Fels (Sandstein)": ("Sandstein", None, ""), "Fels (Schluffstein)": ("Schluffstein", None, ""),
    "Fels (Tonstein)": ("Tonstein", None, ""), "Fels (Mergelstein)": ("Mergelstein", None, ""),
    "Fels (Kalkstein)": ("Kalkstein", None, ""), "Fels (Konglomerat)": ("Konglomerat", None, ""),
    "Fels (Brekzie)": ("Breccie", None, ""), "Fels (Dolomit)": ("Dolomitstein", None, ""),
    "Fels (Tonschiefer)": ("Tonschiefer", None, ""), "Fels (Quarzit)": ("Quarzit", None, ""),
    "Fels (Granit)": ("Granit", None, ""), "Fels (Gneis)": ("Gneis", None, ""), "Fels (Basalt)": ("Basalt", None, ""),
    "Fels (Gips)": ("Gips", None, ""), "Fels (Anhydrit)": ("Anhydrit", None, ""),
}
# Deutung nach Norm (normen.py) -> Name in der Codeliste; Hinweis, wo die Begriffe nicht gleich sind
KONSISTENZ = {w: (w, "") for w in ("breiig", "weich", "steif", "halbfest", "fest")}
LAGERUNG = {"sehr locker": ("sehr locker", ""), "locker": ("locker gelagert", ""),
            "mitteldicht": ("mitteldicht gelagert", ""), "dicht": ("dicht gelagert", ""), "sehr dicht": ("sehr dicht", "")}
KALK = {"kalkfrei": ("karbonatfrei", "kalkfrei (keine Reaktion mit HCl) als karbonatfrei"),
        "schwach kalkhaltig": ("kalkarm", "schwach kalkhaltig als kalkarm"),
        "kalkhaltig": ("kalkhaltig", ""),
        "stark kalkhaltig": ("kalkreich", "stark kalkhaltig als kalkreich")}
FEUCHTE = {"trocken": ("trocken", ""), "erdfeucht": ("feucht (bergfeucht)", ""), "feucht": ("feucht (bergfeucht)", ""),
           "nass": ("nass", ""), "naß": ("nass", "")}
# Quelle der GOK bzw. der Lage in der App -> Hoehen-/Lagebestimmung
HOEHE = {"PDF": "Fremdangabe", "manuell": "Fremdangabe", "DGM": "aus digitalem Geländemodell bestimmt",
         "DGM1": "aus DGM 1 ermittelt", "DGM2": "aus DGM 2 ermittelt", "DGM5": "aus DGM 5 ermittelt",
         "DGM25": "aus DGM 25 ermittelt", "DGM50": "aus DGM 50 ermittelt"}
LAGE = {"PDF": "Fremdangabe, von Firma oder Einsender", "manuell (Tabelle)": "Fremdangabe, von Firma oder Einsender",
        "Plan (kalibriert)": "aus der Karte abgelesen", "manuell (Viewer)": "geschätzt"}
FEST = {"BoreholeStatusList": "gebohrt/abgeteuft", "DatabaseSourceList": "sonstige Datenbank/nicht angegeben",
        "CodingStandardList": "DIN 4022-1 oder DIN 4022-2", "SegmentDataQualityList": "angenommen",
        "DrillingPurposeList": "Geotechnische Untersuchung, Baugrund"}
LISTEN = ("RockNameList", "GeoGenesisList", "ConsistencyList", "CompactnessList", "CarbonateContentList",
          "WaterContentList", "LevelMethodList", "LocationMethodList", *FEST)


def eltern(pfad: Path) -> dict[str, str]:
    """Code -> Code der uebergeordneten Stufe (Hierarchie der Codeliste, fuer den Import: fS -> S)."""
    eintraege = [(e.findtext("gml:identifier", "", NS).strip(), e.findtext("bmlcl:keyID", "", NS).strip(),
                  e.findtext("bmlcl:parentID", "", NS).strip())
                 for e in ET.parse(pfad).getroot().iterfind("gmx:codeEntry/bmlcl:BMLML_CodeDefinition", NS)]
    code_von = {k: c for c, k, _ in eintraege}
    return {c: code_von[p] for c, _, p in eintraege if p in code_von}


def liste_lesen(pfad: Path) -> tuple[dict[str, list[str]], str]:
    """Name -> Codes einer Codeliste und ihre Versionszeile."""
    text = pfad.read_text(encoding="utf-8")
    version = (re.search(r"<!--\s*(version[^>]*?)\s*-->", text) or re.search(r"<gml:remarks>([^<]+)", text))
    namen: dict[str, list[str]] = {}
    for e in ET.fromstring(text.encode("utf-8")).iterfind("gmx:codeEntry/bmlcl:BMLML_CodeDefinition", NS):
        namen.setdefault(e.findtext("gml:name", "", NS).strip(), []).append(e.findtext("gml:identifier", "", NS).strip())
    return namen, version.group(1).strip() if version else ""


def eintrag(listen: dict, liste: str, name: str, hinweis: str = "") -> dict:
    codes = listen[liste][0].get(name)
    if not codes:
        sys.exit(f"{liste}: Name '{name}' nicht gefunden")
    if len(set(codes)) > 1:
        sys.exit(f"{liste}: Name '{name}' mehrdeutig {codes}")
    out = {"code": codes[0], "name": name, "liste": liste}
    if hinweis:
        out["hinweis"] = hinweis
    return out


def main() -> None:
    ordner = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="bml_codelisten_"))
    for liste in LISTEN:
        pfad = ordner / f"{liste}.xml"
        if not pfad.exists():
            urllib.request.urlretrieve(BASIS + pfad.name, pfad)
    listen = {liste: liste_lesen(ordner / f"{liste}.xml") for liste in LISTEN}
    daten = {
        "format": "groundtwin-boreholeml-codes/1",
        "beschreibung": "Codes der amtlichen BoreholeML-Codelisten v2 fuer den Export von GroundTwin, je mit dem "
                        "amtlichen Namen als Beleg. Erzeugt mit services/geodaten/werkzeuge/boreholeml_codes.py.",
        "quelle": {"url": BASIS, "lizenz": "MIT, AK BoreholeML4 (https://gitlab.opencode.de/ak-boreholeml4/boreholeml)",
                   "erzeugt": date.today().isoformat(), "versionen": {n: v for n, (_, v) in listen.items()}},
        "bodenart": {k: {"petrographie": eintrag(listen, "RockNameList", p),
                         "genese": eintrag(listen, "GeoGenesisList", g) if g else None,
                         **({"hinweis": h} if h else {})} for k, (p, g, h) in BODENART.items()},
        "konsistenz": {k: eintrag(listen, "ConsistencyList", n, h) for k, (n, h) in KONSISTENZ.items()},
        "lagerung": {k: eintrag(listen, "CompactnessList", n, h) for k, (n, h) in LAGERUNG.items()},
        "kalk": {k: eintrag(listen, "CarbonateContentList", n, h) for k, (n, h) in KALK.items()},
        "feuchte": {k: eintrag(listen, "WaterContentList", n, h) for k, (n, h) in FEUCHTE.items()},
        "hoehe": {k: eintrag(listen, "LevelMethodList", n) for k, n in HOEHE.items()},
        "lage": {k: eintrag(listen, "LocationMethodList", n) for k, n in LAGE.items()},
        "fest": {liste: eintrag(listen, liste, n) for liste, n in FEST.items()},
        "petrographie_eltern": eltern(ordner / "RockNameList.xml"),
        "genese_eltern": eltern(ordner / "GeoGenesisList.xml"),
    }
    ZIEL.write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"geschrieben: {ZIEL} ({len(daten['bodenart'])} Bodenarten)")


if __name__ == "__main__":
    main()
