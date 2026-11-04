"""Baugrundmodell als 3D Tiles 1.1 fuer CesiumJS, Cesium for Unreal, QGIS 3D (docs/23 §2.5, D87, Phase P6).

Aus dem IFC des Modells: jedes Element trianguliert (IfcOpenShell), jeder Punkt exakt umgerechnet - ETRS89/UTM ->
geographisch (Krueger-Reihen) -> geozentrisch, die Hoehe ellipsoidisch aus m NHN + Quasigeoid GCG2016. Der Inhalt
liegt lokal in Ost/Nord/Oben um die Mitte des Baugrundmodells (glTF: y nach oben); die Wurzelkachel traegt die
Transformation von dort ins Geozentrische. Je Gruppe ein GLB: Baugrundmodell (Einheiten und Bohrsaeulen), Gelaende,
Gebaeude - Kontext der Laender getrennt, damit er sich im Ziel weglassen laesst.

Bewusst nicht umgerechnet: ETRS89 in ITRF/WGS84 (2026 rund 0,9 m Versatz nach Nordost) - das sagt die Datei.
"""
from __future__ import annotations

import io
import json
import os
import struct
import tempfile
import zipfile
from pathlib import Path

import numpy as np

from . import utm
from .quasigeoid import QUELLE as GEOID_QUELLE
from .quasigeoid import Gitter

GRUPPEN = (("baugrundmodell", "Baugrundmodell (Einheiten und Bohrsäulen)"), ("gelaende", "Gelände (DGM des Landes)"),
           ("gebaeude", "Gebäude (LoD2 der Länder)"))
FEHLER_WURZEL = 1000.0                               # m: Kinder werden in ueblichen Abstaenden immer geladen


def _gruppe(klasse: str) -> str:
    return {"IfcGeographicElement": "gelaende", "IfcBuildingElementProxy": "gebaeude"}.get(klasse, "baugrundmodell")


def _elemente(ifc: bytes) -> tuple[list[dict], tuple[float, float, float]]:
    """Dreiecke je Element (lokale IFC-Koordinaten) und der Bezug der IfcMapConversion (Ost, Nord, Hoehe)."""
    import ifcopenshell
    import ifcopenshell.geom

    with tempfile.TemporaryDirectory() as ordner:   # IfcOpenShell liest Dateien am sichersten vom Pfad
        pfad = Path(ordner) / "modell.ifc"
        pfad.write_bytes(ifc)
        f = ifcopenshell.open(str(pfad))
        umrechnung = f.by_type("IfcMapConversion")
        bezug = ((umrechnung[0].Eastings, umrechnung[0].Northings, umrechnung[0].OrthogonalHeight or 0.0)
                 if umrechnung else (0.0, 0.0, 0.0))
        einstellungen = ifcopenshell.geom.settings()
        einstellungen.set("use-world-coords", True)
        elemente = []
        it = ifcopenshell.geom.iterator(einstellungen, f, max(1, min(8, os.cpu_count() or 1)))
        if it.initialize():
            while True:
                form = it.get()
                g = form.geometry
                el = f.by_id(form.id)
                flaechen = np.asarray(g.faces, dtype=np.uint32).reshape(-1, 3)
                if len(flaechen):
                    farben = []
                    for m in g.materials:
                        rgb = tuple(m.diffuse.components) if hasattr(m.diffuse, "components") else tuple(m.diffuse)
                        alpha = 1.0 - (m.transparency if m.transparency == m.transparency else 0.0)
                        farben.append((*[float(c) for c in rgb[:3]], max(0.05, min(1.0, float(alpha)))))
                    elemente.append({"klasse": el.is_a(), "guid": el.GlobalId, "name": el.Name or "",
                                     "beschreibung": getattr(el, "Description", None) or "",
                                     "punkte": np.asarray(g.verts, dtype=float).reshape(-1, 3), "flaechen": flaechen,
                                     "material": np.asarray(g.material_ids, dtype=int), "farben": farben or [(0.7,) * 3 + (1.0,)]})
                if not it.next():
                    break
    return elemente, bezug


def _lokal(punkte_utm: np.ndarray, epsg: int, geoid: Gitter, ursprung) -> np.ndarray:
    """UTM (Rechtswert, Hochwert, m NHN) -> lokal Ost/Nord/Oben um den Ursprung (geozentrisch exakt)."""
    zone = utm.zone(epsg)
    versatz = utm.versatz(epsg, {32: 25832, 33: 25833}.get(zone, epsg)) or 0.0
    laenge, breite = utm.zu_geo(punkte_utm[:, 0] + versatz, punkte_utm[:, 1], zone)
    zeta = geoid.werte(laenge, breite)
    if np.isnan(zeta).any():
        raise ValueError("Modell liegt teilweise außerhalb des Quasigeoids GCG2016 (nur Deutschland) – "
                         "3D Tiles brauchen ellipsoidische Höhen")
    p = utm.ecef(laenge, breite, punkte_utm[:, 2] + zeta)
    p0, basis = ursprung
    return (p - p0) @ basis


def _glb(teile: list[dict]) -> bytes:
    """glTF 2.0 binaer: ein Knoten je Element, je Farbe ein Primitiv; Normalen rechnet der Leser (flach)."""
    materialien: dict[tuple, int] = {}
    knoten, netze, zugriffe, sichten = [], [], [], []
    puffer = bytearray()

    def ablegen(daten: bytes, ziel: int) -> int:
        while len(puffer) % 4:
            puffer.append(0)
        sichten.append({"buffer": 0, "byteOffset": len(puffer), "byteLength": len(daten), "target": ziel})
        puffer.extend(daten)
        return len(sichten) - 1

    for teil in teile:
        pos = teil["gltf"].astype(np.float32)
        z_pos = len(zugriffe)
        zugriffe.append({"bufferView": ablegen(pos.tobytes(), 34962), "componentType": 5126, "count": int(len(pos)),
                         "type": "VEC3", "min": pos.min(0).tolist(), "max": pos.max(0).tolist()})
        primitive = []
        for mat_id in sorted(set(teil["material"].tolist())):
            auswahl = teil["flaechen"][teil["material"] == mat_id]
            if not len(auswahl):
                continue
            farbe = teil["farben"][mat_id if 0 <= mat_id < len(teil["farben"]) else 0]
            linear = tuple(round(float(c) ** 2.2, 4) for c in farbe[:3]) + (round(farbe[3], 3),)   # glTF: linear
            if linear not in materialien:
                materialien[linear] = len(materialien)
            z_idx = len(zugriffe)
            zugriffe.append({"bufferView": ablegen(auswahl.astype(np.uint32).tobytes(), 34963), "componentType": 5125,
                             "count": int(auswahl.size), "type": "SCALAR"})
            primitive.append({"attributes": {"POSITION": z_pos}, "indices": z_idx, "material": materialien[linear],
                              "mode": 4})
        netze.append({"name": teil["name"], "primitives": primitive})
        knoten.append({"name": teil["name"] or teil["klasse"], "mesh": len(netze) - 1,
                       "extras": {"IFC": teil["klasse"], "GlobalId": teil["guid"], "Name": teil["name"],
                                  "Beschreibung": teil["beschreibung"]}})
    mats = [{"pbrMetallicRoughness": {"baseColorFactor": list(rgba), "metallicFactor": 0.0, "roughnessFactor": 1.0},
             "doubleSided": True, **({"alphaMode": "BLEND"} if rgba[3] < 1 else {})}
            for rgba, _ in sorted(materialien.items(), key=lambda t: t[1])]
    while len(puffer) % 4:
        puffer.append(0)
    gltf = {"asset": {"version": "2.0", "generator": "GroundTwin"}, "scene": 0,
            "scenes": [{"nodes": list(range(len(knoten)))}], "nodes": knoten, "meshes": netze, "materials": mats,
            "accessors": zugriffe, "bufferViews": sichten, "buffers": [{"byteLength": len(puffer)}]}
    text = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    text += b" " * (-len(text) % 4)
    gesamt = 12 + 8 + len(text) + 8 + len(puffer)
    return (struct.pack("<4sII", b"glTF", 2, gesamt) + struct.pack("<I4s", len(text), b"JSON") + text
            + struct.pack("<I4s", len(puffer), b"BIN\x00") + bytes(puffer))


def _kasten(lokal: np.ndarray) -> list[float]:
    """Achsparalleler Quader (lokal Ost/Nord/Oben) als 3D-Tiles-box."""
    lo, hi = lokal.min(0), lokal.max(0)
    mitte, halb = (lo + hi) / 2, np.maximum((hi - lo) / 2, 0.01)
    return [*mitte.tolist(), float(halb[0]), 0.0, 0.0, 0.0, float(halb[1]), 0.0, 0.0, 0.0, float(halb[2])]


def exportieren(ifc: bytes, epsg: int, geoid: Gitter, info: dict | None = None) -> tuple[bytes, dict]:
    """IFC des Modells -> ZIP mit tileset.json, je Gruppe ein GLB und LIESMICH.txt. Rueckgabe (ZIP, Angaben)."""
    info = info or {}
    elemente, (e0, n0, h0) = _elemente(ifc)
    if not elemente:
        raise ValueError("IFC ohne Geometrie")
    for el in elemente:
        el["utm"] = el["punkte"] + [e0, n0, h0]
    kern = [el for el in elemente if _gruppe(el["klasse"]) == "baugrundmodell"] or elemente
    alle = np.vstack([el["utm"] for el in kern])
    mitte = (alle.min(0) + alle.max(0)) / 2
    zone = utm.zone(epsg)
    versatz = utm.versatz(epsg, {32: 25832, 33: 25833}.get(zone, epsg)) or 0.0
    laenge0, breite0 = (float(v) for v in utm.zu_geo(mitte[0] + versatz, mitte[1], zone))
    zeta0 = float(geoid.werte(laenge0, breite0))
    if np.isnan(zeta0):
        raise ValueError("Modell liegt außerhalb des Quasigeoids GCG2016 (nur Deutschland)")
    p0 = utm.ecef(laenge0, breite0, mitte[2] + zeta0)
    basis = utm.enu_basis(laenge0, breite0)
    for el in elemente:
        lokal = _lokal(el["utm"], epsg, geoid, (p0, basis))
        el["lokal"] = lokal
        el["gltf"] = np.column_stack([lokal[:, 0], lokal[:, 2], -lokal[:, 1]])     # glTF: x Ost, y oben, z Sued
    transform = [*basis[:, 0], 0.0, *basis[:, 1], 0.0, *basis[:, 2], 0.0, *p0.tolist(), 1.0]
    kinder, dateien = [], {}
    for name, titel in GRUPPEN:
        teile = [el for el in elemente if _gruppe(el["klasse"]) == name]
        if not teile:
            continue
        dateien[f"{name}.glb"] = _glb(teile)
        kinder.append({"boundingVolume": {"box": _kasten(np.vstack([t["lokal"] for t in teile]))}, "geometricError": 0.0,
                       "content": {"uri": f"{name}.glb"}, "extras": {"Inhalt": titel, "Elemente": len(teile)}})
    angaben = {
        "Projekt": info.get("projekt") or "", "Reifegrad": info.get("reifegrad") or "",
        "Lagebezug": f"ETRS89/UTM Zone {zone} (EPSG:{epsg}), jeder Punkt geozentrisch umgerechnet; ETRS89 nicht in "
                     "ITRF/WGS84 überführt (2026 rund 0,9 m Versatz)",
        "Hoehenbezug": "ellipsoidisch (ETRS89) = m NHN (DHHN2016) + Quasigeoid GCG2016",
        "Ursprung": {"Laenge": round(laenge0, 9), "Breite": round(breite0, 9), "Hoehe_NHN": round(float(mitte[2]), 3),
                     "Quasigeoid_zeta": round(zeta0, 4)},
        "Namensnennung": [GEOID_QUELLE["namensnennung"], *info.get("namensnennung", [])],
    }
    tileset = {"asset": {"version": "1.1", "generator": "GroundTwin", "extras": angaben},
               "geometricError": FEHLER_WURZEL,
               "root": {"transform": [float(v) for v in transform],
                        "boundingVolume": {"box": _kasten(np.vstack([el["lokal"] for el in elemente]))},
                        "geometricError": FEHLER_WURZEL, "refine": "ADD", "children": kinder}}
    zip_puffer = io.BytesIO()
    with zipfile.ZipFile(zip_puffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("tileset.json", json.dumps(tileset, ensure_ascii=False, indent=1))
        for name, daten in dateien.items():
            z.writestr(name, daten)
        z.writestr("LIESMICH.txt", _liesmich(angaben, [k["extras"]["Inhalt"] for k in kinder]))
    return zip_puffer.getvalue(), angaben


def _liesmich(angaben: dict, inhalte: list[str]) -> str:
    u = angaben["Ursprung"]
    zeilen = [
        f"GroundTwin – Baugrundmodell als 3D Tiles 1.1 ({angaben['Projekt']})",
        "",
        f"Reifegrad: {angaben['Reifegrad'] or '–'}",
        "Inhalt: " + "; ".join(inhalte),
        f"Lage: {angaben['Lagebezug']}",
        f"Höhen: {angaben['Hoehenbezug']}",
        f"Mitte: {u['Laenge']:.7f}° O, {u['Breite']:.7f}° N, {u['Hoehe_NHN']:.2f} m NHN (zeta {u['Quasigeoid_zeta']:.3f} m)",
        "",
        "Laden in CesiumJS (Ordner über einen Webserver bereitstellen):",
        '  const tileset = await Cesium.Cesium3DTileset.fromUrl("tileset.json");',
        "  viewer.scene.primitives.add(tileset); viewer.zoomTo(tileset);",
        "  Unter der Geländeoberfläche: viewer.scene.globe.translucency.enabled = true (oder Gelände ausblenden).",
        "",
        "Die Baugrundinterpretation ersetzt nicht das Gutachten. Quellen und Lizenzen:",
        *[f"  {n}" for n in angaben["Namensnennung"]],
    ]
    return "\n".join(zeilen) + "\n"
