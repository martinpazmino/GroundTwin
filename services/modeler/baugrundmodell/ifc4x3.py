"""IFC4X3-Ausgabe: Bohrsaeulen (N1: IfcBorehole ⊃ IfcGeotechnicalStratum) und Schichtmodell
(N3: IfcGeomodel ⊃ IfcGeotechnicalStratum als geschlossene Koerper).

Koordinaten lokal zum Ursprung (gerundeter Schwerpunkt), Georeferenz ueber IfcMapConversion.
That Open: die Geotechnik-Klassen muessen in importer.classes.elements stehen (Architektur 8.2).
Description unterscheidet die beiden Ebenen fuer den Viewer: "Modelleinheit" / "Bohrsaeule".
"""
from __future__ import annotations

import numpy as np
import ifcopenshell.api as api
import ifcopenshell.api.aggregate  # noqa: F401
import ifcopenshell.api.context  # noqa: F401
import ifcopenshell.api.geometry  # noqa: F401
import ifcopenshell.api.georeference  # noqa: F401
import ifcopenshell.api.project  # noqa: F401
import ifcopenshell.api.pset  # noqa: F401
import ifcopenshell.api.root  # noqa: F401
import ifcopenshell.api.spatial  # noqa: F401
import ifcopenshell.api.style  # noqa: F401
import ifcopenshell.api.unit  # noqa: F401

from .koerper import dreiecke_aus
from .normen import KLASSEN, UNKLASSIFIZIERT, bekannt, deuten, farbinfo, ifc_eigenschaften

GELAENDE_RGB = (0.55, 0.66, 0.44)          # Gelaende: gedecktes Gruen, hebt sich von den Bodenfarben (Auffuellung grau) ab
WAND_RGB = (0.88, 0.86, 0.82)              # LoD2-Gebaeude: helle Waende ...
DACH_RGB = (0.66, 0.36, 0.30)              # ... und ziegelrote Daecher


def rgb_aus(hexwert: str) -> tuple[float, float, float]:
    return tuple(int(hexwert[i:i + 2], 16) / 255 for i in (1, 3, 5))


# Farben der Bodenarten nach DIN 4023 (Normen-Datenbank normen.json; "" = unklassifiziert)
FARBEN = {k: rgb_aus(e["farbe"]) for k, e in KLASSEN.items() if k != UNKLASSIFIZIERT}
FARBEN[""] = rgb_aus(KLASSEN[UNKLASSIFIZIERT]["farbe"])
# Wiederholungen derselben Bodenart unterscheidbar: Anteil Weiss (+) bzw. Schwarz (-) je Nummer
ABTOENUNG = (0.0, 0.5, -0.35, 0.75, -0.55)
# Lange Texte als IfcText (IfcLabel ist fuer kurze Bezeichnungen gedacht, 255 Zeichen)
TEXTE = ("Beschreibung", "Beschreibungen", "Benennungen", "Hinweise", "Hinweise_Deutung", "Quelle")


def farbschluessel(klasse: str | None) -> str:
    """Klasse mit eigener Farbe (auch 'Fels (Tonstein)'), sonst '' (unklassifiziert)."""
    return klasse if bekannt(klasse) else ""


def farbe(klasse: str | None, nummer: int = 1) -> tuple[float, float, float]:
    rgb = np.array(rgb_aus(farbinfo(farbschluessel(klasse) or None)["hex"]))
    t = ABTOENUNG[(nummer - 1) % len(ABTOENUNG)]
    rgb = rgb + (1.0 - rgb) * t if t >= 0 else rgb * (1.0 + t)
    return tuple(float(c) for c in np.clip(rgb, 0.0, 1.0))


def hexfarbe(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(c * 255):02x}" for c in rgb)


def _ohne_doppelte(idx: list[int]) -> list[int]:
    """Aufeinanderfolgende gleiche Punkte (auch erster = letzter) entfernen."""
    out = [i for k, i in enumerate(idx) if k == 0 or i != idx[k - 1]]
    while len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def prisma(cx: float, cy: float, z_oben: float, z_unten: float, r: float = 0.5, n: int = 12):
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ring = [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in ang]
    knoten = [(float(x), float(y), float(z_oben)) for x, y in ring] + \
             [(float(x), float(y), float(z_unten)) for x, y in ring]
    flaechen = [list(range(n)), list(range(n, 2 * n))[::-1]]      # nach aussen orientiert
    for i in range(n):
        j = (i + 1) % n
        flaechen.append([i, n + i, n + j, j])
    return knoten, flaechen


class IfcAusgabe:
    def __init__(self, projekt: str, epsg: int | None, ursprung: tuple[float, float]):
        f = self.f = api.project.create_file(version="IFC4X3")
        self.projekt = api.root.create_entity(f, ifc_class="IfcProject", name=projekt)
        # Meter ausdruecklich: assign_unit ohne Angaben setzt Millimeter, alle Koordinaten sind aber in m
        # (sonst zeigt jeder Viewer das Modell 1000-fach verkleinert und die Georeferenz stimmt nicht).
        api.unit.assign_unit(f, units=[api.unit.add_si_unit(f, unit_type=t)
                                       for t in ("LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT")])
        model3d = api.context.add_context(f, context_type="Model")
        self.body = api.context.add_context(f, context_type="Model", context_identifier="Body",
                                            target_view="MODEL_VIEW", parent=model3d)
        self.ursprung = ursprung
        if epsg:
            api.georeference.add_georeferencing(f)
            api.georeference.edit_georeferencing(
                f, projected_crs={"Name": f"EPSG:{epsg}"},
                coordinate_operation={"Eastings": float(ursprung[0]), "Northings": float(ursprung[1]),
                                      "OrthogonalHeight": 0.0})
        self.site = api.root.create_entity(f, ifc_class="IfcSite", name="Baufeld")
        api.aggregate.assign_object(f, products=[self.site], relating_object=self.projekt)
        self._stile: dict[tuple, object] = {}

    def _stil(self, rgb: tuple[float, float, float], name: str):
        schluessel = tuple(round(c, 4) for c in rgb)
        if schluessel not in self._stile:
            st = api.style.add_style(self.f, name=name)
            api.style.add_surface_style(self.f, style=st, ifc_class="IfcSurfaceStyleShading", attributes={
                "SurfaceColour": {"Name": None, "Red": rgb[0], "Green": rgb[1], "Blue": rgb[2]}})
            self._stile[schluessel] = st
        return self._stile[schluessel]

    def _geometrie(self, produkt, knoten, flaechen, rgb, stilname, geschlossen=False):
        """IfcTriangulatedFaceSet: zwei Entitaeten je Koerper statt einer je Flaeche (Trassen: 80k Flaechen)."""
        dreiecke = dreiecke_aus(flaechen) + 1                        # IFC zaehlt ab 1
        punkte = self.f.create_entity("IfcCartesianPointList3D",
                                      CoordList=[tuple(map(float, k)) for k in np.asarray(knoten, dtype=float)])
        flaeche = self.f.create_entity("IfcTriangulatedFaceSet", Coordinates=punkte, Closed=bool(geschlossen),
                                       CoordIndex=[tuple(map(int, d)) for d in dreiecke])
        rep = self.f.create_entity("IfcShapeRepresentation", ContextOfItems=self.body,
                                   RepresentationIdentifier="Body", RepresentationType="Tessellation", Items=[flaeche])
        api.style.assign_representation_styles(self.f, shape_representation=rep,
                                               styles=[self._stil(rgb, stilname)])
        api.geometry.assign_representation(self.f, product=produkt, representation=rep)
        api.geometry.edit_object_placement(self.f, product=produkt)

    def _pset(self, produkt, name: str, werte: dict):
        werte = {k: (self.f.create_entity("IfcText", v) if isinstance(v, str) and (k in TEXTE or len(v) > 255) else v)
                 for k, v in werte.items() if v is not None and v != ""}
        if werte:                                       # leere Psets sind ungueltiges IFC
            ps = api.pset.add_pset(self.f, product=produkt, name=name)
            api.pset.edit_pset(self.f, pset=ps, properties=werte)

    def bohrung(self, dokument: dict, b: dict, xy: tuple[float, float], lage: str, hoehe: str | None = None,
                durchmesser: float = 1.0, durchmesser_quelle: str = "Standard (Darstellung)"):
        """IfcBorehole mit Schichten als Prismen (N1); xy lokal. Durchmesser der Saeule in m (Darstellung)."""
        f = self.f
        ent = api.root.create_entity(f, ifc_class="IfcBorehole", name=b["code"])
        api.spatial.assign_container(f, products=[ent], relating_structure=self.site)
        api.geometry.edit_object_placement(f, product=ent)
        if b.get("groundwater"):
            self._pset(ent, "Pset_BoreholeCommon", {"GroundwaterDepth": float(b["groundwater"][0]["depth"])})
        prov = (b.get("provenance") or [{}])[0]
        self._pset(ent, "CPset_Herkunft", {
            "Dokument": dokument["file"], "SHA256": dokument.get("sha256"), "Parser": dokument.get("parser_version"),
            "Seite": int(prov["page"]) + 1 if prov.get("page") is not None else None, "Methode": prov.get("method"),
            "Lage": lage, "Hoehe": hoehe or ("m NHN" if b.get("gok_nhn") is not None else "relativ (GOK unbekannt)"),
            "Grundwasserstatus": b.get("groundwater_status"),
            "Abgleich_SV": (b.get("checks") or {}).get("schichtenverzeichnis"),
            "Labelbestaetigung": float((b.get("checks") or {}).get("label_support") or 0.0),
            # Pruefung durch den Nutzer (App): nur wenn der Schluessel gesetzt ist
            "Geprueft": bool(b["geprueft"]) if "geprueft" in b else None,
            # Bohrungen aus der Datenbank eines Landes (docs/23 §2.3): Herkunft, Quelle und Lizenz bleiben sichtbar
            "Herkunft": b.get("herkunft") or "Gutachten", "Datenquelle": b.get("namensnennung"),
            "Lizenz": b.get("lizenz"), "Abgerufen": b.get("abgerufen")})
        self._pset(ent, "CPset_Darstellung", {"Durchmesser_m": round(float(durchmesser), 3),
                                               "Durchmesser_Quelle": durchmesser_quelle})
        z0 = b["gok_nhn"] if b.get("gok_nhn") is not None else 0.0
        strata = []
        for ly in b["layers"]:
            s = api.root.create_entity(
                f, ifc_class="IfcGeotechnicalStratum", predefined_type="SOLID",
                name=f"{b['code']} {ly['top_depth']:.2f}-{ly['bottom_depth']:.2f} {ly['soil_class'] or '?'}")
            s.Description = "Bohrsaeule"
            kn, fl = prisma(xy[0], xy[1], z0 - ly["top_depth"], z0 - ly["bottom_depth"], r=float(durchmesser) / 2)
            self._geometrie(s, kn, fl, farbe(ly["soil_class"]), farbschluessel(ly["soil_class"]) or "unbekannt",
                            geschlossen=True)
            self._pset(s, "Pset_GeotechnicalStratumCommon", {"Status": "EXISTING"})
            pv = (ly.get("provenance") or [{}])[0]
            self._pset(s, "CPset_Schichtenverzeichnis", {
                "Bodenart": ly["soil_class"] or "unbekannt", "Beschreibung": ly.get("description_raw"),
                "Tiefe_OK_m": float(ly["top_depth"]), "Tiefe_UK_m": float(ly["bottom_depth"]),
                "Konfidenz": float(ly.get("confidence") or 0.0), "Label_bestaetigt": bool(ly.get("label_confirmed")),
                "Quelle": f"{dokument['file']} S.{int(pv.get('page') or 0) + 1} {pv.get('method')} bbox {pv.get('bbox')}",
                "Geprueft": bool(ly["geprueft"]) if "geprueft" in ly else None,
                "Korrigiert": bool(ly["korrigiert"]) if ly.get("korrigiert") else None,
                "Konfidenz_Extraktion": float(ly["konfidenz_extraktion"]) if ly.get("konfidenz_extraktion") is not None else None,
                "Hinweise": "; ".join(ly.get("issues") or [])})
            # Deutung der Beschreibung nach DIN 4023 / DIN EN ISO 14688-1 / DIN 18196 (normen.py)
            ansprache = ifc_eigenschaften(deuten(ly.get("description_raw"), ly.get("soil_class")))
            ansprache.pop("Beschreibung")                 # steht schon im CPset_Schichtenverzeichnis
            self._pset(s, "CPset_Bodenansprache", ansprache)
            strata.append(s)
        if strata:
            api.aggregate.assign_object(f, products=strata, relating_object=ent)
        return ent

    def geomodell(self, name: str, einheiten: list[dict], eigenschaften: dict):
        """IfcGeomodel mit einem geschlossenen Koerper je Einheit.

        einheiten: [{"name", "knoten", "flaechen", "rgb", "beschreibung", "eigenschaften"}]
        """
        f = self.f
        gm = api.root.create_entity(f, ifc_class="IfcGeomodel", name=name)
        api.spatial.assign_container(f, products=[gm], relating_structure=self.site)
        api.geometry.edit_object_placement(f, product=gm)
        self._pset(gm, "CPset_Baugrundmodell", eigenschaften)
        koerper = []
        for e in einheiten:
            s = api.root.create_entity(f, ifc_class="IfcGeotechnicalStratum", name=e["name"], predefined_type="SOLID")
            s.Description = e.get("beschreibung") or "Modelleinheit"
            self._geometrie(s, e["knoten"], e["flaechen"], e["rgb"], e["name"], geschlossen=e.get("geschlossen", True))
            self._pset(s, "Pset_GeotechnicalStratumCommon", {"Status": "EXISTING"})
            self._pset(s, "CPset_Modelleinheit", e["eigenschaften"])
            koerper.append(s)
        if koerper:
            api.aggregate.assign_object(f, products=koerper, relating_object=gm)
        return gm

    def gelaende(self, knoten, dreiecke, eigenschaften: dict):
        """IfcGeographicElement TERRAIN: offene Dreiecksflaeche des Gelaendes um das Baugrundmodell (lokal, m NHN)."""
        f = self.f
        g = api.root.create_entity(f, ifc_class="IfcGeographicElement", name="Gelände (DGM)", predefined_type="TERRAIN")
        g.Description = "Gelaende um das Baugrundmodell"
        api.spatial.assign_container(f, products=[g], relating_structure=self.site)
        self._geometrie(g, knoten, np.asarray(dreiecke, dtype=np.int64), GELAENDE_RGB, "Gelaende", geschlossen=False)
        self._pset(g, "CPset_Gelaende", eigenschaften)
        return g

    def gebaeude(self, gebaeude: list[dict], eigenschaften: dict, je_dienst: dict[str, dict] | None = None) -> int:
        """LoD2-Gebaeude der Umgebung: je Gebaeude ein IfcBuildingElementProxy (USERDEFINED "LoD2-Gebäude (Umgebung)")
        mit zwei offenen IfcPolygonalFaceSet (Waende und Boden, Dach) - Flaechen mit Loechern als FaceWithVoids.

        gebaeude: [{id, funktion, dachform, hoehe, dienst, flaechen [{art, ring, loecher}]}] lokal (m NHN);
        je_dienst: Quelle, Lizenz und Namensnennung je Dienst (Berlin und Brandenburg koennen gemischt sein).
        """
        f = self.f
        wand, dach = self._stil(WAND_RGB, "Gebaeude Wand"), self._stil(DACH_RGB, "Gebaeude Dach")
        n = 0
        for b in gebaeude:
            items, stile = [], []
            for arten, stil in ((("Wand", "Boden"), wand), (("Dach",), dach)):
                fs = self._facetten([fl for fl in b["flaechen"] if fl["art"] in arten])
                if fs is not None:
                    items.append(fs)
                    stile.append(stil)
            if not items:
                continue
            g = api.root.create_entity(f, ifc_class="IfcBuildingElementProxy", name=f"Gebäude {b.get('id') or n + 1}",
                                       predefined_type="USERDEFINED")
            g.ObjectType = "LoD2-Gebäude (Umgebung)"
            g.Description = "Bestand aus dem LoD2 des Landes"
            api.spatial.assign_container(f, products=[g], relating_structure=self.site)
            rep = f.create_entity("IfcShapeRepresentation", ContextOfItems=self.body, RepresentationIdentifier="Body",
                                  RepresentationType="Tessellation", Items=items)
            api.style.assign_representation_styles(f, shape_representation=rep, styles=stile)
            api.geometry.assign_representation(f, product=g, representation=rep)
            api.geometry.edit_object_placement(f, product=g)
            self._pset(g, "CPset_Gebaeude", {**eigenschaften, **(je_dienst or {}).get(b.get("dienst"), {}),
                                             "GML_ID": b.get("id"), "Funktion": b.get("funktion"),
                                             "Dachform": b.get("dachform"),
                                             "Hoehe_m": round(float(b["hoehe"]), 2) if b.get("hoehe") is not None else None})
            n += 1
        return n

    def _facetten(self, flaechen: list[dict]):
        """Offenes IfcPolygonalFaceSet aus Ringen (Punkte je Gebaeude auf mm zusammengefasst, Indizes ab 1)."""
        if not flaechen:
            return None
        index: dict[tuple, int] = {}

        def nr(p) -> int:
            k = (round(float(p[0]), 3), round(float(p[1]), 3), round(float(p[2]), 3))
            if k not in index:
                index[k] = len(index) + 1
            return index[k]

        faces = []
        for fl in flaechen:
            aussen = _ohne_doppelte([nr(p) for p in fl["ring"]])
            if len(aussen) < 3:
                continue
            innen = [r for r in (_ohne_doppelte([nr(p) for p in ring]) for ring in fl.get("loecher") or []) if len(r) >= 3]
            if innen:
                faces.append(self.f.create_entity("IfcIndexedPolygonalFaceWithVoids", CoordIndex=tuple(aussen),
                                                  InnerCoordIndices=[tuple(r) for r in innen]))
            else:
                faces.append(self.f.create_entity("IfcIndexedPolygonalFace", CoordIndex=tuple(aussen)))
        if not faces:
            return None
        punkte = self.f.create_entity("IfcCartesianPointList3D", CoordList=[k for k, _ in sorted(index.items(), key=lambda t: t[1])])
        return self.f.create_entity("IfcPolygonalFaceSet", Coordinates=punkte, Closed=False, Faces=faces)

    def schreiben(self, pfad) -> None:
        self.f.write(str(pfad))
