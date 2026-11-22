"""Informationspaket v0 (Issue #33, A1, D108, docs/29): AGSi 1.0.1 + Manifest + Bericht aus dem, was GroundTwin schon hat.

- AGSi ist fuer **interpretierte** Daten (Modell, Einheiten, Statistik); Fachdaten (Bohrungen) liegen als BoreholeML
  daneben und werden als Dokument referenziert (docs/30 §1). Die Bohrungen erscheinen im Modell als
  ``agsiObservationExpHole`` mit Spalten, die auf die Einheit zeigen.
- AGSi verbietet eigene Attribute (``additionalProperties: false``): Wertart, Herkunft und Offenes stehen im Manifest
  (``services/wissen/schemas/manifest.schema.json``), verknuepft ueber die AGSi-IDs.
- Nur *properties* (gemessen oder aus der Ansprache), nie ``agsiDataParameterValue``: charakteristische Werte setzt der
  Ingenieur (D108). Die Kennwerte aus den Tabellen des Gutachtens sind Parameter des Gutachters und bleiben offen.
- ``caseID`` = Art der Statistik (``Labor``, ``Ansprache``), nicht die Wertart (docs/30 §6.2).
- Generische Schema-Validatoren pruefen weder eindeutige IDs noch Verweise: das macht ``pruefen``.
"""
from __future__ import annotations

import hashlib
import io
import json
import uuid
import zipfile
from datetime import date

from baugrundmodell import homogenbereiche as hb
from baugrundmodell import labor
from baugrundmodell.modell import einheit_schichten

AGSI_VERSION = "1.0.1"
AGSI_LINK = "https://ags-data-format-wg.gitlab.io/agsi/agsi_standard/1.0.1/"
MANIFEST_FORMAT = "groundtwin-manifest/1"
CASES = {"Labor": "Statistik der Laborwerte aus den Anlagen des Gutachtens (gemessen)",
         "Ansprache": "aus den Schichtbeschreibungen gedeutet (DIN 4023 / DIN EN ISO 14688-1), keine Laborwerte"}
_NS = uuid.UUID("5f0c6a8e-3b4d-4c1e-9a77-2d1f0e6b9c11")      # feste UUIDs: gleiches Projekt = gleiche Kennung


def _uuid(*teile: str) -> str:
    return str(uuid.uuid5(_NS, "|".join(teile)))


def _crs(m, bericht: dict) -> dict:
    hoehen = sorted({b.hoehe for b in m.bohrungen})
    z = ("NHN (Normalhöhennull) wie im Gutachten angegeben; Höhensystem (DHHN92/DHHN2016) nicht geprüft"
         if hoehen == ["m NHN"] else f"Höhen: {', '.join(hoehen)} (siehe Manifest)")
    if m.epsg:
        xy = f"EPSG:{m.epsg}"
        beschreibung = f"Lage EPSG:{m.epsg}, Höhen in m"
    else:
        xy = "lokal (ohne Georeferenz: Reihe oder Plan ohne Koordinaten)"
        beschreibung = "lokales System des Projekts"
    return {"systemID": "CRS1", "description": beschreibung, "systemType": "XYZ", "systemNameXY": xy,
            "systemNameZ": z, "axisNameX": "Rechtswert" if m.epsg else "X", "axisNameY": "Hochwert" if m.epsg else "Y",
            "axisNameZ": "Höhe", "axisUnitsXY": "m", "axisUnitsZ": "m"}


def bauen(m, bericht: dict, docs: list[dict], *, projekt: str, ifc_uri: str, boreholeml_uri: str | None = None,
          homogenbereiche: dict[str, dict[str, str]] | None = None, analyse: dict | None = None,
          datum: str | None = None, version: str = "") -> tuple[dict, dict]:
    """(AGSi, Manifest). m: baugrundmodell.Modell, bericht: dessen Bericht, docs: Modell-Eingabe (mit Korrekturen).

    analyse: Zusammenfassung der Ground Analysis (Kreuzprobe, Unsicherheit) oder None. Nichts wird geraten: was fehlt,
    steht im Manifest unter ``offen``.
    """
    datum = datum or date.today().isoformat()
    projekt = projekt or "Baugrundmodell"
    werte: list[dict] = []
    offen: list[dict] = []
    vollst: dict[str, float] = {}

    # ---- Quellen und Dokumente
    quellen, q_von_datei, dokumente = [], {}, []
    for i, d in enumerate(docs):
        info = d["document"]
        qid = f"Q{i + 1}"
        q_von_datei[info["file"]] = qid
        art = "boreholeml" if str(info["file"]).lower().endswith(".xml") else "gutachten"
        q = {"id": qid, "art": art, "datei": info["file"]}
        if isinstance(info.get("sha256"), str) and len(info["sha256"]) == 64:
            q["sha256"] = info["sha256"]
        quellen.append(q)
        dokumente.append({"documentID": f"DOC{i + 1}", "title": info["file"],
                          "description": "Bodengutachten (PDF)" if art == "gutachten" else "BoreholeML (Fachdaten)",
                          "remarks": f"sha256 {info.get('sha256') or 'unbekannt'}; Datei nicht im Paket (liegt dem Empfänger vor)"})
    dokumente.append({"documentID": "IFC", "title": "Baugrundmodell (IFC 4.3)", "documentURI": ifc_uri,
                      "description": "Geometrie der Einheiten, Bohrsäulen, Psets (CPset_*)"})
    if boreholeml_uri:
        dokumente.append({"documentID": "BML", "title": "Fachdaten der Bohrungen (BoreholeML 3.2)",
                          "documentURI": boreholeml_uri, "description": "geprüfte Bohrungen mit ETRS89/UTM und GOK"})
    else:
        offen.append({"was": "BoreholeML (Fachdaten)", "warum": "keine exportierbare Bohrung (nur geprüfte mit "
                      "ETRS89/UTM und GOK); die Bohrungen stehen als Beobachtungen im AGSi-Modell"})

    # ---- Codes: Eigenschaften (Laborwerte, Kennwerte nach VOB/C), Fälle, Einheiten als geologyCode
    codes_eig: dict[str, dict] = {}
    codes_geo: list[dict] = []

    # ---- Modell der Einheiten
    p = m.parameter
    elemente, hole_einheit = [], {}
    for j, (e, eb) in enumerate(zip(m.einheiten, bericht["einheiten"])):
        eid = f"E{j + 1}"
        codes_geo.append({"codeID": eid, "description": e.name, "isStandard": False})
        schichten = einheit_schichten(m, j)
        for s in schichten:
            hole_einheit[(s["bohrung"], round(float(s["von"]), 3))] = eid
        el = {"elementID": eid, "elementName": e.name, "elementType": "Geological unit",
              "description": f"Bodenarten: {', '.join(eb['bodenarten'])}; {_anzahl(len(schichten), 'Schicht', 'en')} "
                             f"aus {_anzahl(len(eb['bohrungen']['vorhanden']), 'Bohrung', 'en')}; "
                             f"Volumen {eb['volumen_m3']:.0f} m³",
              "colourRGB": eb["farbe"], "geometryObject": "agsiGeometryFromFile",
              "agsiGeometry": {"geometryID": f"G{j + 1}", "geometryType": "Volume", "fileFormat": "IFC",
                               "fileFormatVersion": "IFC4X3_ADD2", "fileURI": ifc_uri,
                               "filePart": f"IfcGeomodel/IfcGeotechnicalStratum Name='{e.name}'",
                               "description": "geschlossener Körper der Einheit (Layer-Cake)"}}
        werte.append({"agsi_id": f"G{j + 1}", "groesse": "geometrie.einheit", "kind": "modelled",
                      "herkunft": {"quellen": sorted({q_von_datei.get(b.dokument, "?") for b in m.bohrungen}),
                                   "methode": f"Schichtenmodell {str(p.get('methode', 'idw')).upper()}: exakt an den "
                                              "Bohrungen, dazwischen interpoliert"}})
        st = labor.statistik(schichten)
        summ = []
        for k, s in sorted(st.items()):
            code = f"LAB_{k.upper()}"
            codes_eig.setdefault(code, {"codeID": code, "description": labor.NAMEN.get(k, k), "units": s["einheit"],
                                        "isStandard": False})
            did = f"{eid}/{code}/Labor"
            summ.append({"dataID": did, "codeID": code, "caseID": "Labor", "valueMin": s["min"], "valueMax": s["max"],
                         "valueMean": round(s["mittel"], 6), "valueCount": s["n"]})
            werte.append({"agsi_id": did, "groesse": f"labor.{k}", "kind": "observed",
                          "herkunft": {"quellen": sorted({q_von_datei.get(b.dokument, "?") for b in m.bohrungen
                                                          if b.code in {x["bohrung"] for x in schichten}}),
                                       "methode": "Statistik (n, min, max, Mittel) der Laborproben dieser Einheit",
                                       "eingaben": sorted({pr["ref"] for x in schichten for pr in x.get("labor") or []
                                                           if pr.get("ref")})},
                          "unsicherheit": {"statistik_n": s["n"]}})
        if summ:
            el["agsiDataPropertySummary"] = summ
        elemente.append(el)
        n_b = len(eb["bohrungen"]["vorhanden"])
        exakt = sum(1 for b in bericht["bohrungen"] for x in b["einheiten"]
                    if x["einheit"] == e.name and x["status"] == "vorhanden" and x["unterkante_art"] == "exakt")
        if n_b:
            vollst[f"{eid}/Unterkante_belegt"] = round(min(1.0, exakt / n_b), 3)

    # ---- Bohrungen als Beobachtungen (Spalten zeigen auf die Einheit)
    loecher, gesehen = [], set()
    bb = {(b["code"], b["dokument"]): b for b in bericht["bohrungen"]}
    for i, b in enumerate(m.bohrungen):
        hid = f"B{i + 1}"
        doppelt = sum(x.code == b.code for x in m.bohrungen) > 1
        if b.code in gesehen:
            offen.append({"was": f"Bohrung {b.code}", "warum": "Code doppelt; Spalten ohne Einheit, weil die Zuordnung "
                          "über den Code nicht eindeutig ist", "fuer": [hid]})
        gesehen.add(b.code)
        info = bb.get((b.code, b.dokument), {})
        spalten = []
        for k, s in enumerate(b.schichten):
            von, bis = float(s["von"]), float(s["bis"])
            sp = {"columnID": f"{hid}/S{k + 1}", "topDepth": von, "bottomDepth": bis,
                  "topElevation": round(b.gok - von, 3), "bottomElevation": round(b.gok - bis, 3),
                  "description": s.get("beschreibung") or "", "legendCode": s.get("bodenart") or ""}
            eid = hole_einheit.get((b.code, round(von, 3)))
            if eid and not doppelt:
                sp["geologyCode"] = eid
            spalten.append(sp)
        loch = {"holeID": hid, "holeName": b.code, "topCoordinate": [round(b.x, 3), round(b.y, 3), round(b.gok, 3)],
                "verticalHoleDepth": round(b.gok - b.ende, 3), "holeType": "Bohrung",
                "agsiObservationColumn": spalten,
                "remarks": f"Lage: {b.lage}; Höhe: {b.hoehe}; Herkunft: {b.herkunft}; Dokument: {b.dokument}"}
        loecher.append(loch)
        q = [q_von_datei.get(b.dokument, "?")]
        werte.append({"agsi_id": hid, "groesse": "bohrung.lage_gok", "kind": "observed" if b.lage not in
                      ("manuell", "schematisch", "Plan (kalibriert)") else "interpreted",
                      "herkunft": {"quellen": q, "methode": f"Lage: {b.lage}; Höhe: {b.hoehe}"}})
        werte.append({"agsi_id": f"{hid}/Spalten", "groesse": "bohrung.schichten", "kind": "observed",
                      "herkunft": {"quellen": q, "methode": "Schichtenverzeichnis/Bohrprofil des Dokuments"}})
        if not info:
            offen.append({"was": f"Bohrung {b.code}", "warum": "nicht im Prüfbericht gefunden", "fuer": [hid]})
    for a in bericht.get("ausgeschlossen") or []:
        offen.append({"was": f"Bohrung {a.get('code')}", "warum": f"nicht im Modell: {a.get('grund')}"})

    modelle = [{"modelID": "M1", "modelName": f"Baugrundmodell {projekt}",
                "description": f"Layer-Cake aus {len(m.bohrungen)} Bohrungen, {len(m.einheiten)} Einheiten "
                               f"(GroundTwin, Reifegrad {bericht.get('reifegrad') or '–'})",
                "coordSystemID": "CRS1", "modelType": "Geological model", "category": "Observational",
                "domain": "Engineering geology", "input": "Bohrungen der Dokumente in DOCS",
                "method": f"Schichtenmodell, Interpolation {str(p.get('methode', 'idw')).upper()}, Raster "
                          f"{float(p.get('raster_m') or 0):.1f} m; Kontakte an den Bohrungen exakt "
                          f"(Abweichung {bericht['pruefungen']['max_abweichung_an_bohrungen_m']} m)",
                "usage": "Zur Darstellung und Plausibilisierung des Gutachtens. Keine Bemessungswerte; "
                         "charakteristische Werte legt der Ingenieur fest.",
                "uncertainty": _unsicherheit_text(analyse),
                "documentSetID": "DOCS", "agsiModelElement": elemente,
                "agsiObservationSet": [{"observationSetID": "OS1", "description": "Bohrungen im Modell",
                                        "documentSetID": "DOCS", "agsiObservationExpHole": loecher}]}]

    # ---- je ATV ein Modell der Homogenbereiche (Kennwerte aus der Ansprache)
    namen = [e.name for e in m.einheiten]
    for atv, je in sorted((homogenbereiche or {}).items()):
        bereiche_, hinweise = hb.bereiche(je, namen)
        el_hb = []
        for k, b in enumerate(x for x in bereiche_ if x["bereich"]):
            eid = f"HB{_kurz(atv)}/{k + 1}"
            schichten = [s for n in b["einheiten"] for s in einheit_schichten(m, namen.index(n))]
            kw = hb.kennwerte_bereich(atv, schichten)
            summ = []
            for z in kw["kennwerte"]:
                code = f"VOBC_{z['nr']}"
                codes_eig.setdefault(code, {"codeID": code, "description": f"Kennwert {z['nr']} VOB/C: {z['name']}",
                                            "isStandard": False})
                if z["wert"] is None:
                    offen.append({"was": f"{atv} {b['bereich']}: Kennwert {z['nr']} {z['name']}",
                                  "warum": "nicht aus den Beschreibungen ableitbar (Labor oder Gutachter)", "fuer": [eid]})
                    continue
                did = f"{eid}/{code}/Ansprache"
                summ.append({"dataID": did, "codeID": code, "caseID": "Ansprache", "valueSummaryText": str(z["wert"])})
                werte.append({"agsi_id": did, "groesse": f"vobc.{z['nr']}", "kind": "interpreted",
                              "herkunft": {"quellen": sorted({q_von_datei.get(b2.dokument, "?") for b2 in m.bohrungen
                                                              if b2.code in {s['bohrung'] for s in schichten}}),
                                           "methode": "aus den Schichtbeschreibungen gedeutet (normen.json)"}})
            vollst[f"{eid}/Kennwerte_belegt"] = round(kw["belegt"] / kw["verlangt"], 3) if kw["verlangt"] else 1.0
            el = {"elementID": eid, "elementName": b["bereich"], "elementType": f"Homogenbereich {atv}",
                  "description": f"{hb.gewerk(atv)}: Einheiten {', '.join(b['einheiten'])}",
                  "geometryObject": "agsiGeometryFromFile",
                  "agsiGeometry": {"geometryID": f"G{eid}", "geometryType": "Volume", "fileFormat": "IFC",
                                   "fileFormatVersion": "IFC4X3_ADD2", "fileURI": ifc_uri,
                                   "filePart": "IfcGeotechnicalStratum mit CPset_Homogenbereich_"
                                               f"{atv.replace(' ', '')}.Homogenbereich='{b['bereich']}'"}}
            if summ:
                el["agsiDataPropertySummary"] = summ
            el_hb.append(el)
        for h in hinweise:
            offen.append({"was": f"Homogenbereiche {atv}", "warum": h})
        if el_hb:
            modelle.append({"modelID": f"M-HB{_kurz(atv)}", "modelName": f"Homogenbereiche {atv} ({hb.gewerk(atv)})",
                            "coordSystemID": "CRS1", "modelType": "Homogenbereiche (VOB/C)", "category": "Observational",
                            "method": "Einheiten des Baugrundmodells je Gewerk zu Bereichen gruppiert (Zuordnung des "
                                      "Planers); Kennwerte aus der Ansprache, Laborwerte im Modell M1",
                            "usage": "Ausschreibung nach VOB/C; Bandbreiten der Kennwerte legt der Planer fest.",
                            "documentSetID": "DOCS", "agsiModelElement": el_hb})

    offen.append({"was": "Kennwerte aus den Tabellen des Gutachtens",
                  "warum": "Parameter des Gutachters (agsiDataParameterValue); Abbildung noch nicht entschieden – "
                           "im IFC als CPset_Bodenkennwerte_Gutachten"})
    offen.append({"was": "Sondierungen", "warum": "Fachdaten: im IFC (IfcBorehole Sondierung) und im BoreholeML, "
                  "nicht im AGSi-Modell"})
    offen.append({"was": "charakteristische Werte", "warum": "setzt der Ingenieur (D108); GroundTwin liefert keine"})
    if analyse is None:
        offen.append({"was": "Ground Analysis", "warum": "nicht gerechnet (unter drei Bohrungen oder nicht verlangt)"})

    agsi = {
        "agsSchema": {"name": "AGSi", "version": AGSI_VERSION, "link": AGSI_LINK},
        "agsFile": {"fileUUID": _uuid(projekt, datum), "title": f"Baugrundmodell {projekt}",
                    "projectTitle": projekt, "description": "Informationspaket v0 aus GroundTwin (Issue #33)",
                    "producedBy": f"GroundTwin {version}".strip(), "date": datum, "status": "Entwurf",
                    "remarks": "Wertart und Herkunft je Wert im manifest.json (AGSi erlaubt keine eigenen Attribute)"},
        "agsProject": {"projectUUID": _uuid(projekt), "projectName": projekt, "projectCountry": "Deutschland",
                       "agsProjectCoordinateSystem": [_crs(m, bericht)],
                       "agsProjectDocumentSet": [{"documentSetID": "DOCS", "description": "Quellen und Dateien des Pakets",
                                                  "agsProjectDocument": dokumente}],
                       "agsProjectCodeSet": [
                           {"codeSetID": "CS_EIG", "description": "Eigenschaften (GroundTwin, nicht AGS-Standard)",
                            "usedByObject": "agsiDataPropertySummary", "usedByAttribute": "codeID",
                            "agsProjectCode": sorted(codes_eig.values(), key=lambda c: c["codeID"])},
                           {"codeSetID": "CS_CASE", "description": "Art der Statistik",
                            "usedByObject": "agsiDataPropertySummary", "usedByAttribute": "caseID",
                            "agsProjectCode": [{"codeID": k, "description": v, "isStandard": False}
                                               for k, v in CASES.items()]},
                           {"codeSetID": "CS_GEO", "description": "Einheiten des Baugrundmodells",
                            "usedByObject": "agsiObservationColumn", "usedByAttribute": "geologyCode",
                            "agsProjectCode": codes_geo}]},
        "agsiModel": modelle}
    manifest = {"format": MANIFEST_FORMAT, "projekt": projekt, "erzeugt": f"{datum}T00:00:00Z",
                "groundtwin_version": version or "unbekannt", "quellen": quellen, "werte": werte,
                "offen": offen, "vollstaendigkeit": vollst}
    if analyse is not None:
        manifest["analyse"] = analyse
    return agsi, manifest


def _anzahl(n: int, wort: str, plural: str) -> str:
    return f"{n} {wort}{'' if n == 1 else plural}"


def _kurz(atv: str) -> str:
    return atv.replace("DIN", "").replace(" ", "").replace("GK", "-GK")


def _unsicherheit_text(analyse: dict | None) -> str:
    basis = "Grenzen zwischen den Bohrungen interpoliert (bestmögliche Schätzung, keine Bemessungsgrundlage)."
    if not analyse:
        return basis + " Ground Analysis nicht gerechnet."
    k = (analyse.get("kreuzprobe") or {}).get("gesamt") or {}
    teile = [basis]
    if k.get("mae") is not None:
        teile.append(f"Kreuzprobe (eine Bohrung weglassen): mittlerer Fehler der Unterkanten {k['mae']} m, "
                     f"größter {k.get('max')} m, n = {k.get('n')}.")
    if analyse.get("sigma_max_m") is not None:
        teile.append(f"Unsicherheit der Grenzen bis σ = {analyse['sigma_max_m']} m (Monte Carlo).")
    return " ".join(teile)


# ---------------------------------------------------------------- Pruefung (IDs und Verweise, Encoding 8.3)
def pruefen(agsi: dict) -> list[str]:
    """Eindeutige IDs je Art und aufloesbare Verweise; leer = in Ordnung."""
    fehler: list[str] = []
    ids: dict[str, list[str]] = {}

    def sammeln(o, pfad=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if k.endswith("ID") and isinstance(v, str) and k not in ("coordSystemID", "documentSetID", "codeID",
                                                                         "caseID", "alignmentID", "investigationID",
                                                                         "valueProfileIndVarCodeID"):
                    ids.setdefault(k, []).append(v)
                sammeln(v, f"{pfad}/{k}")
        elif isinstance(o, list):
            for x in o:
                sammeln(x, pfad)

    sammeln(agsi)
    for art, liste in ids.items():
        doppelt = sorted({x for x in liste if liste.count(x) > 1})
        if doppelt:
            fehler.append(f"{art} doppelt: {', '.join(doppelt)}")
    proj = agsi.get("agsProject") or {}
    crs = {c.get("systemID") for c in proj.get("agsProjectCoordinateSystem") or []}
    sets = {s["documentSetID"] for s in proj.get("agsProjectDocumentSet") or []}
    codes: dict[tuple[str, str], set[str]] = {}
    for cs in proj.get("agsProjectCodeSet") or []:
        codes.setdefault((cs["usedByObject"], cs["usedByAttribute"]), set()).update(
            c["codeID"] for c in cs.get("agsProjectCode") or [])
    for mo in agsi.get("agsiModel") or []:
        if mo.get("coordSystemID") and mo["coordSystemID"] not in crs:
            fehler.append(f"{mo['modelID']}: coordSystemID {mo['coordSystemID']} unbekannt")
        if mo.get("documentSetID") and mo["documentSetID"] not in sets:
            fehler.append(f"{mo['modelID']}: documentSetID {mo['documentSetID']} unbekannt")
        for el in mo.get("agsiModelElement") or []:
            for s in el.get("agsiDataPropertySummary") or []:
                if s["codeID"] not in codes.get(("agsiDataPropertySummary", "codeID"), set()):
                    fehler.append(f"{s.get('dataID')}: codeID {s['codeID']} nicht im Codeset")
                if s.get("caseID") and s["caseID"] not in codes.get(("agsiDataPropertySummary", "caseID"), set()):
                    fehler.append(f"{s.get('dataID')}: caseID {s['caseID']} nicht im Codeset")
        for os_ in mo.get("agsiObservationSet") or []:
            if os_.get("documentSetID") and os_["documentSetID"] not in sets:
                fehler.append(f"{os_['observationSetID']}: documentSetID unbekannt")
            for h in os_.get("agsiObservationExpHole") or []:
                for c in h.get("agsiObservationColumn") or []:
                    if c.get("geologyCode") and c["geologyCode"] not in codes.get(("agsiObservationColumn",
                                                                                     "geologyCode"), set()):
                        fehler.append(f"{c['columnID']}: geologyCode {c['geologyCode']} nicht im Codeset")
    return fehler


def manifest_pruefen(agsi: dict, manifest: dict) -> list[str]:
    """Jeder Wert im Manifest zeigt auf eine AGSi-ID (oder einen Teil davon), jeder Datenwert im AGSi hat einen
    Manifest-Eintrag mit Wertart und Quelle (Abnahme #33)."""
    fehler = []
    alle: set[str] = set()

    def sammeln(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("dataID", "elementID", "holeID", "geometryID", "columnID") and isinstance(v, str):
                    alle.add(v)
                sammeln(v)
        elif isinstance(o, list):
            for x in o:
                sammeln(x)

    sammeln(agsi)
    im_manifest = {w["agsi_id"] for w in manifest["werte"]}
    for w in manifest["werte"]:
        basis = w["agsi_id"].split("/Spalten")[0]
        if basis not in alle:
            fehler.append(f"Manifest {w['agsi_id']}: keine solche AGSi-ID")
        if not w.get("kind") or not w["herkunft"].get("quellen"):
            fehler.append(f"Manifest {w['agsi_id']}: ohne Wertart oder Quelle")
    for mo in agsi["agsiModel"]:
        for el in mo.get("agsiModelElement") or []:
            for s in el.get("agsiDataPropertySummary") or []:
                if s["dataID"] not in im_manifest:
                    fehler.append(f"{s['dataID']}: kein Manifest-Eintrag")
    return fehler


# ---------------------------------------------------------------- Bericht und Paket
def bericht_md(agsi: dict, manifest: dict) -> str:
    """Bericht aus denselben Daten wie AGSi und Manifest (Deutsch, fuer Menschen)."""
    m1 = agsi["agsiModel"][0]
    z = [f"# {agsi['agsFile']['title']}", "",
         f"Informationspaket v0, erzeugt {agsi['agsFile']['date']} mit {agsi['agsFile']['producedBy']}. "
         f"AGSi {AGSI_VERSION} (interpretiertes Modell), Geometrie im IFC, Wertart und Herkunft je Wert im Manifest.", "",
         "## Grundlagen", ""]
    for q in manifest["quellen"]:
        z.append(f"- {q['id']}: {q.get('datei', '')} ({q['art']}), sha256 `{q.get('sha256', 'unbekannt')}`")
    crs = agsi["agsProject"]["agsProjectCoordinateSystem"][0]
    z += ["", f"Lage: {crs['systemNameXY']}. Höhen: {crs['systemNameZ']}.", "",
          "## Einheiten", "", "| ID | Einheit | Beschreibung | Laborwerte | Unterkante belegt |", "|---|---|---|---|---|"]
    for el in m1["agsiModelElement"]:
        lab = ", ".join(f"{s['codeID'].removeprefix('LAB_').lower()} (n = {s['valueCount']})"
                        for s in el.get("agsiDataPropertySummary") or []) or "–"
        bel = manifest["vollstaendigkeit"].get(f"{el['elementID']}/Unterkante_belegt")
        z.append(f"| {el['elementID']} | {el['elementName']} | {el['description']} | {lab} | "
                 f"{'–' if bel is None else f'{bel:.0%}'} |")
    loecher = m1["agsiObservationSet"][0]["agsiObservationExpHole"]
    z += ["", f"## Bohrungen ({len(loecher)})", ""]
    z += [f"- {h['holeID']} {h['holeName']}: GOK {h['topCoordinate'][2]} m, Tiefe {h['verticalHoleDepth']} m, "
          f"{len(h['agsiObservationColumn'])} Schichten" for h in loecher]
    for mo in agsi["agsiModel"][1:]:
        z += ["", f"## {mo['modelName']}", ""]
        for el in mo["agsiModelElement"]:
            kw = "; ".join(f"{s['codeID']}: {s['valueSummaryText']}" for s in el.get("agsiDataPropertySummary") or [])
            z.append(f"- **{el['elementName']}** – {el['description']}" + (f". {kw}" if kw else ""))
    z += ["", "## Unsicherheit", "", m1["uncertainty"], "", "## Offen", ""]
    z += [f"- {o['was']}: {o['warum']}" for o in manifest["offen"]]
    kinds: dict[str, int] = {}
    for w in manifest["werte"]:
        kinds[w["kind"]] = kinds.get(w["kind"], 0) + 1
    z += ["", "## Wertarten im Manifest", "", ", ".join(f"{k}: {n}" for k, n in sorted(kinds.items())), "",
          "Charakteristische Werte enthält dieses Paket nicht: die legt der Ingenieur fest (D108).", ""]
    return "\n".join(z)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def paket(agsi: dict, manifest: dict, stamm: str, dateien: dict[str, bytes]) -> bytes:
    """ZIP: <stamm>_agsi.json, manifest.json, bericht.md, LIESMICH.txt und die referenzierten Dateien (IFC, BoreholeML).
    Das Manifest nennt jede Datei mit sha256 (ausser sich selbst)."""
    agsi_b = (json.dumps(agsi, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    md = bericht_md(agsi, manifest).encode("utf-8")
    alle = {f"{stamm}_agsi.json": agsi_b, "bericht.md": md, **dateien}
    manifest = {**manifest, "teile": {n: {"pfad": n, "sha256": _sha(b), "format": n.rsplit(".", 1)[-1]}
                                      for n, b in sorted(alle.items())}}
    liesmich = (f"Informationspaket {manifest['projekt']} (GroundTwin, Issue #33)\n\n"
                f"{stamm}_agsi.json  AGSi {AGSI_VERSION}: Modell der Einheiten, Homogenbereiche, Bohrungen als "
                "Beobachtungen\nmanifest.json      Wertart und Herkunft je Wert, Vollständigkeit, Offenes, sha256 "
                "der Dateien\nbericht.md         Bericht aus denselben Daten\n"
                + "".join(f"{n}  referenziert im AGSi\n" for n in sorted(dateien))
                + "\nOffen:\n" + "".join(f"- {o['was']}: {o['warum']}\n" for o in manifest["offen"])
                + "\nKeine charakteristischen Werte: die legt der Ingenieur fest.\n")
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in sorted(alle.items()):
            z.writestr(n, b)
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")
        z.writestr("LIESMICH.txt", liesmich)
    return puffer.getvalue()
