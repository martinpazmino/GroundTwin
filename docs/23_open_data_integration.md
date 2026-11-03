---
title: "23 Open data and open-source integration: evaluation and intervention plan"
date: 2026-11-02
tags: [open-data, boreholeml, bgr, geoportal, dgm, lod2, 3d-tiles, cesium, openstreetmap, plan]
aliases: [Open data integration, Umgebungsmodell, BoreholeML, Bohrpunktkarte, Intervention plan]
---

# 23 Open data and open-source integration: evaluation and intervention plan

**Question:** can GroundTwin be connected with open data and open-source projects (BoreholeML, the
BGR Bohrpunktkarte, the geoportals of the Länder, Cesium, OpenStreetMap) to add an Umgebungsmodell
(DGM + LoD2 buildings) and to build a Baugrundmodell from a point instead of a PDF?

**Conclusion:**

- **Yes, all of it is possible with free data and free software**, in this order:
  1. **BoreholeML** export and import: the exchange format of the SGD and the BGR.
  2. **Existing Bohrungen** from the Bohrpunktkarte and the state services, as a second source next
     to the Gutachten.
  3. **DGM** of the Länder: it fills a missing GOK, checks the GOK and the Lage of the PDF, and gives
     the terrain surface.
  4. **LoD2 buildings** for the Umgebungsmodell.
  5. A **"Standort" start** (a point instead of a PDF) that builds a Baugrundmodell from 2 + 3.
- **The model from a point has a lower maturity** and is marked as **Vorerkundung** everywhere
  (app, viewer, IFC). Its data are archive Bohrungen of unknown quality, often old or far away, with
  SEP3 codes instead of a DIN 4023 description. Only the Schichtdaten that the Land has released are
  available. It never replaces the Gutachten and is never mixed with it silently.
- **Cesium and OpenStreetMap are not needed at the core.**
  - The 3D context fits into the existing That Open viewer with 3D Tiles (3DTilesRendererJS,
    Apache-2.0).
  - Cesium becomes an optional *export target*: the Baugrundmodell as 3D Tiles. No Cesium ion.
  - OSM is a fallback where the official open data end: outside Germany, or a Land without LoD2.
- **Effort:** about 5–8 weeks for one person for the phases P0–P5 (§5); P6 is optional.
- **Status (2026-11-03):** P0 to P5 are done.
  - A Baugrundmodell from a point (Standort start, P5), marked as Vorerkundung in the app, the viewer, the
    report and the IFC; a Gutachten added later keeps both sources apart
    ([21 §4.7](21_app_schritte_normen.md#47-standort-ohne-gutachten-a-vorerkundung-from-a-point)).
  - The LoD2 buildings of Berlin, Brandenburg and NRW around the site, in the IFC and the viewer
    ([21 §4.6](21_app_schritte_normen.md#46-gebäude-lod2-buildings-around-the-site)).
  - The DGM of the Land by WCS on a click (Brandenburg with Berlin, NRW), the top of the model
    from the DGM and the terrain around it in the IFC
    ([21 §4.4](21_app_schritte_normen.md#44-gelände-dgm-gok-check-dgm-from-the-land-terrain-in-the-model)).
  - Bohrungen der Länder around the site, with a Gegenprobe against the Gutachten and the import of
    BoreholeML Schichtdaten ([21 §4.5](21_app_schritte_normen.md#45-bohrungen-der-länder-existing-boreholes-around-the-site)).
  - BoreholeML 3.2 export of the reviewed Bohrungen, valid against the official XSD, and import of
    BoreholeML files ([21 §5.1](21_app_schritte_normen.md#51-boreholeml-for-the-geologische-dienste)).
  - The DGM comes from files the user downloads: GOK check and missing GOK on a click
    ([21 §4.4](21_app_schritte_normen.md#44-gelände-dgm-gok-check-dgm-from-the-land-terrain-in-the-model)).
- **Before anything is fetched from outside:**
  - Nothing is fetched without an explicit click, and the button says what is sent (D88, D91).
    Querying a service reveals the site of a confidential project.
  - Every fetched dataset carries its source, license and date.
- **Cloud session:** the geodata hosts of §7 are allowed since 2026-11-02 (before, they were
  blocked: lesson X30).

## 1. Today and the gap

| Wish | GroundTwin today | Gap |
|---|---|---|
| Georeferenced point on a map (Cesium / OSM) | Lage step: plan calibrated to an EPSG code (UTM, Gauß-Krüger, LV95…), coordinates per Bohrung, `IfcMapConversion` in the IFC | No basemap. A point cannot be the entry of a project |
| Umgebungsmodell: DGM surface + LoD2 buildings | Only the Baugrundmodell. GOK from the PDF or by hand (`gok_quelle`: PDF / manuell), the terrain interpolated between the Bohrungen | No terrain or buildings. No independent check of GOK and Lage |
| BoreholeML | Canonical JSON (`to_canonical`), IFC 4.3, Excel | No exchange format of the SGD |
| BGR Bohrpunktkarte | Not used | Existing Bohrungen around the site are invisible |
| Baugrundmodell from a point | Needs a PDF | No project without a Gutachten |

## 2. Evaluation of the sources

### 2.1 BoreholeML: the exchange format of the Länder

- **What it is:**
  - The XML/GML schema with which the SGD of the Länder and the BGR exchange Bohrdaten. The Länder
    deliver it through WFS services.
  - Current version 3.2.0 (2025-09-09), maintained by the working group AK BoreholeML4. Codelists
    v2: v2.1 of April 2025, written for 3.1.
  - The schemas moved from infogeo.de to `schemas.bgr.de` on 2024-07-01. Development happens on
    `gitlab.opencode.de/ak-boreholeml4/boreholeml`.
  - Official examples: a header-only one, and a complete Bohrung of the NRW database DABO with
    Schichten, Grundwasser, logs and Ausbau.
- **Content:**
  - Stammdaten.
  - Schichtdaten coded with **SEP3** (geological symbol key, version 3).
  - Grundwasser measurements, logging and samples, technical data.
- **Use for GroundTwin:**
  - **Import:** the Bohrungen of the state services arrive in this format (§2.2).
  - **Export:** the Gutachten that GroundTwin reads becomes the format of the SGD. Under the GeolDG
    a drilling is notified at least two weeks before it starts (§ 8). Its results, such as the
    Schichtenverzeichnis, are submitted at the latest three months after it ends (§ 9). A prefilled
    file saves typing.
  - Which SGD accept a BoreholeML upload from third parties is **[to be verified]**. Many accept
    SEP3 files (the LBEG offers free SEP3 software) or online forms.
- **Mapping of the canonical JSON** (element names are taken from the XSD in P1; the schemas could
  not be read from the session, §7):

| Canonical JSON | BoreholeML content | Note |
|---|---|---|
| `code`, `kind` | Name and kind of the Bohrung | — |
| `x`, `y`, `crs_epsg` | Location | — |
| `gok_nhn` | Collar elevation | Datum DHHN2016 (NHN) |
| `end_depth` | Final depth (Endteufe) | — |
| `layers[].top_depth`, `layers[].bottom_depth` | Schicht depths | — |
| `layers[].description_raw` | Description text | — |
| `layers[].soil_class` | Petrography as a SEP3 code | Needs a **DIN 4023 → SEP3 table** in the norms database, with evidence per code. Doubtful codes are marked, as with the norms |
| `groundwater[]` | Grundwasser measurements | Depth, NHN, kind |
| `confidence`, `issues`, `provenance` | — | No place in BoreholeML: kept in a GroundTwin companion JSON. An export only from **reviewed** Bohrungen |

- **License:** the format and the codelists are public. **Effort:** export with schema validation
  about 1 week; import about 3–5 days.

### 2.2 BGR Bohrpunktkarte Deutschland and the state services

- **What it is:**
  - A web application of the BGR with the SGD of the 16 Länder: about **2 million Bohrungen**
    (about 80,000 km of drilling).
  - The Länder deliver their data through WFS services in BoreholeML.
  - The BGR WMS *Deutscher Bohrungsnachweis (GBL)* shows the header data: a density raster at
    small scales, single points at large ones.
- **What is free:**
  - The Stammdaten and part of the Schichtdaten. The rest must be requested from the Land.
  - The GeolDG decides by category. Non-state Nachweisdaten (who, where, how deep) become public at
    the latest three months after the deadline (§ 26). Schichtdaten and evaluations follow stricter
    rules, which is why only part of them is free.
- **State services** (endpoints from catalogue entries and the metadata, not requested from the
  session; examples, the full list is built in P0):

| Land | Service | Content and license |
|---|---|---|
| Brandenburg (LBGR) | WFS `https://inspire.brandenburg.de/services/bpk_wfs` (1.0 / 1.1 / 2.0) | Bohrungen with and without a digital Schichtenverzeichnis (2018: about 29,000, 18,000 with Schichtenverzeichnis), coded with SEP3. Tagged opendata. The data categories are set by a general order (Allgemeinverfügung) of the LBGR |
| Nordrhein-Westfalen (GD NRW) | Dataset *Bohrungen in NRW* (DABO + Bohranzeige); vector tiles `https://ogc-api.nrw.de/brgnrw/v1`; BoreholeML WFS `www.bml3.nrw.de/service/bml` (1.1.0) | A status per Bohrung says whether its Schichtdaten are released. INSPIRE metadata: no limits on public access (one harvested copy says otherwise: verify) |
| Baden-Württemberg (LGRB) | BoreholeML WFS 2.0 `https://services.lgrb-bw.de/boreholeml/services/bml` | **[to be verified]** |
| Berlin | Geological Bohrdaten, WMS + WFS | About 160,000 Bohrungen, structure according to SEP3 |
| Niedersachsen (LBEG) | NIBIS, download | More than 300,000 Bohrungen |

- **Assessment:**
  - **The header data are nationwide and good for a Vorerkundung:** which Bohrungen exist near the
    site, how deep, from which year.
  - **Schichtdaten only where released.** Every Land has its own service, version and codes, so the
    integration needs a **common adapter (BoreholeML over WFS) with one entry per Land**. Start with
    the Länder of the corpus: Berlin, Brandenburg, NRW, Baden-Württemberg and Bayern.
  - **A synergy:** since 2020 every Bohrung is notified to the SGD, so the Bohrungen of a Gutachten
    may already be in the state database.
    - Matching by distance and depth finds the duplicates. The data of the Gutachten win.
    - The coordinates of the SGD check the Lage calibration of the plan.

### 2.3 A Baugrundmodell from a point (Standort start)

**Flow** (proposal):

1. Step 1 (*Gutachten*) gets a second card next to the PDF upload: **"Standort wählen"**. A click on
   the basemap or typed coordinates with an EPSG code, and a radius (for example 250 m).
2. The server queries the GBL and the state service. The *Bohrungen* step lists what it found:
   distance, depth, year, data owner, Schichtdaten yes/no, license.
3. The user picks the Bohrungen.
   - Their Schichten go from SEP3 to the Bodenart of the app through the norms database: a
     proposal, never applied silently, as with DIN 4023.
   - The Lage is known: no calibration.
4. The existing modeler builds the Einheiten and the solids.

**Maturity is marked, never hidden** (the same rule as for a doubtful value):

- Each Bohrung carries `herkunft` (Gutachten / SGD / manuell), source, date and license.
- The project carries a `reifegrad`: Gutachten, **Vorerkundung** or gemischt. It is shown as a
  banner in the viewer, a property in the IFC and a line in the report.
- Schichten from archive data get a fixed lower confidence. In the Prüfstand they count as "accepted
  by the user", not "checked against the PDF".
- If a Gutachten PDF is added later, both kinds of Bohrung stay apart: different symbols, and each
  one can be excluded from the model.

**Limits:**

- Archive Bohrungen are often old, very deep (water wells) or very shallow.
- Their quality is unknown. There are no Sondierungen or soil parameters, and the distances to the
  site can be large.
- Correlating Einheiten over large distances can invent continuity. The viewer should show the
  distance to the nearest Bohrung as a simple, honest measure of uncertainty.

### 2.4 Umgebungsmodell: DGM and LoD2 buildings

**DGM (terrain):**

- DGM1 (1 m grid) is open data in many Länder:
  - NRW (dl-de/zero, OpenGeodata).
  - Berlin (dl-de/zero).
  - Baden-Württemberg (INSPIRE WCS DGM1).
- A secondary overview says that every Land offered free high-resolution elevation models by
  2024/25; this is checked per Land in P0.
- The heights are in **DHHN2016 (NHN), the same datum as the GOK of the Gutachten**, so no height
  conversion is needed.

**Four uses of the DGM, in order of value:**

1. **Check the GOK and the Lage.** After the calibration, compare the GOK of each Bohrung from the
   PDF with the DGM at its x/y.
   - A median difference over about 1 m points to a wrong EPSG code, a wrong calibration or another
     height system.
   - It is marked as a warning: an independent check of the Lage step.
2. **Fill a missing GOK** with `gok_quelle = DGM1`. Today the height is dragged by hand in the
   section.
3. **Terrain surface** of the model, instead of interpolating the GOK of the Bohrungen. In IFC 4.3
   it is an `IfcGeographicElement` of type TERRAIN.
4. Visual context.

**LoD2 buildings:**

- LoD2 CityGML is open data in many Länder:
  - Bayern (CityGML 1.0).
  - Mecklenburg-Vorpommern (ATOM feed, 2 × 2 km tiles).
  - Niedersachsen, Sachsen, Hamburg.
  - Berlin (dl-de/zero).
  - NRW (dl-de/zero, OGC API Features `ogc-api.nrw.de/3dg/v1`).
- It comes in ETRS89/UTM with NHN heights: the frame of the Baugrundmodell.

**basemap.de 3D:**

- The LoD2 of all Länder as **3D Tiles**, plus a terrain mesh from DGM5, in one service for
  Germany.
- Tilesets in the BKG documentation:
  - `https://sgx.geodatenzentrum.de/gdz_basemapde_3d_gebaeude/lod2_4978_dgm5.json`: EPSG:4978, on
    the DGM5.
  - Variants at height 0 and in EPSG:3857.
- The license of the 3D service is **[to be verified]**. The raster and vector basemap.de products
  use dl-de/by-2.0 or CC BY 4.0, with the attribution "© GeoBasis-DE / BKG (year)".

**Two traps when 3D Tiles meet the model:**

- **Heights.**
  - 3D Tiles in EPSG:4978 use ellipsoidal heights; the model uses NHN. The relation is
    H(DHHN2016) = h(ETRS89) − ζ, where ζ is the quasigeoid height (GCG2016). In a worked example of
    Rheinland-Pfalz ζ = 47.94 m.
  - Without the conversion the buildings float by ζ, several tens of metres, above the model. ζ
    changes slowly, so one value per project is enough for a site of a few kilometres.
- **Grid north.**
  - The IFC is in UTM grid coordinates; a tileset placed at a latitude/longitude uses true north.
    The difference is the meridian convergence: about 2.3° at the edge of a UTM zone at 50° N (more
    where a Land uses zone 32 east of 12° E), which is about 20 m at 500 m from the origin.
  - The transformation must rotate by it and apply the UTM scale factor. pyproj gives both.

**Viewer integration, two ways:**

| Way | How | For | Against |
|---|---|---|---|
| **a) 3D Tiles in the That Open viewer** | 3DTilesRendererJS (Apache-2.0, needs three ≥ 0.167; the viewer uses three 0.185 + That Open 3.6), group in the scene, ECEF → project frame | Fast, all of Germany, nothing to store; the 3D BAG viewer of the Netherlands uses the same library | Height and north traps, runtime dependency on the BKG server, to be tested with the post-processing of the viewer (flicker) |
| **b) Server cut-out of DGM1 + LoD2 CityGML** | The server fetches the project area (for example 500 × 500 m), triangulates it and writes context into the IFC or a separate `Umgebung.ifc` | Exact (NHN, UTM), offline, other BIM tools see it | Download per Land, CityGML parsing, more code |

**Recommendation:**

- DGM by way **b)** first, because it serves the GOK checks.
- Buildings by way **a)** for viewing, then way **b)** for the export.

### 2.5 Basemaps: OpenStreetMap, basemap.de and Cesium

- **2D background** for the Standort card and the Lage step.
  - Choice: basemap.de Web Raster / Vektor (official) or OSM tiles.
  - A light map library would draw it: MapLibre GL JS (BSD-3-Clause) or Leaflet (BSD-2-Clause).
  - It would also allow placing the Lageplan over the basemap by two points.
  - The OSM tile servers have a usage policy (no heavy use) and require "© OpenStreetMap
    contributors". For production, use basemap.de or your own tiles.
- **Cesium.**
  - CesiumJS (Apache-2.0) is a complete globe engine. Next to That Open it would be a second 3D
    engine with its own camera and controls: not worth it inside the app.
  - Cesium ion, the hosted tiling and terrain service, has paid plans for commercial use. Check its
    current terms; GroundTwin does not need it.
  - What makes sense is **exporting the Baugrundmodell as 3D Tiles**: IFC → glTF (IfcOpenShell) →
    a tileset with one tile and its ECEF transform. Anyone can then load it in CesiumJS, Cesium for
    Unreal or QGIS 3D.
- **OSM as a fallback** for buildings where there is no LoD2 open data.
  - Footprints with `height` or `building:levels` become LoD1 blocks, fetched through the Overpass
    API under its usage policy.
  - ODbL: attribution, and share-alike for a derived database.

### 2.6 Open-source projects worth connecting

| Project | License | What for | When |
|---|---|---|---|
| [swissgeol boreholes suite](https://github.com/swisstopo/swissgeol-boreholes-suite) (swisstopo) | MIT | Borehole management of Switzerland with an API; reference data model; the Swiss examples of the corpus. Its extraction is already evaluated ([08](08_swissgeol_reuse.md)) | P6 |
| [3DTilesRendererJS](https://github.com/NASA-AMMOS/3DTilesRendererJS) (npm `3d-tiles-renderer` 0.5.3) | Apache-2.0 | 3D Tiles in three.js / That Open | P4 |
| [OWSLib](https://github.com/geopython/OWSLib) | BSD-3-Clause | WFS / WCS / WMS client in Python | P2, P3 |
| pyproj / PROJ | MIT | CRS, meridian convergence, scale factor, heights | P3, P4 |
| rasterio (GDAL) | BSD-3-Clause | DGM GeoTIFF: sampling, cut-out | P3 |
| lxml | BSD-3-Clause | BoreholeML and CityGML | P1, P4 |
| cjio | MIT | CityJSON, where a Land delivers it | P4 |
| [3DCityDB](https://github.com/3dcitydb/3dcitydb) v5 + [pg2b3dm](https://github.com/Geodan/pg2b3dm) | Apache-2.0 / MIT | City models in PostGIS and their 3D Tiles, if GroundTwin ever keeps its own city database (Supabase) | Later |
| [CesiumJS](https://github.com/CesiumGS/cesium) | Apache-2.0 | Consumer of the 3D Tiles export | P6 |
| GemPy | EUPL-1.2 | Implicit geological modelling ([architecture](ARCHITECTURE_BAUGRUNDMODELL.md) F5); compatibility of the EUPL with the AGPL to be checked before use | Later |

All of these licenses can be combined with the AGPL-3.0-or-later of GroundTwin (Apache-2.0, MIT and
BSD into AGPLv3; EUPL-1.2 to be checked). New dependencies go into `THIRD_PARTY_LICENSES.md`.

## 3. Data licenses and obligations

| License | Where | Obligation | In GroundTwin |
|---|---|---|---|
| dl-de/zero-2.0 | NRW, Berlin (DGM1, LoD2) | None | Source shown anyway |
| dl-de/by-2.0, CC BY 4.0 | basemap.de, many Länder | Attribution with source and year; note changes | Attribution line in the viewer, in the IFC and in the report |
| ODbL | OpenStreetMap | Attribution; share-alike for derived databases | Only as a fallback; attribution |
| Terms of the SGD | Bohrdaten | Per Land and per GeolDG category; header data free, Schichtdaten in part | Source, date and license per Bohrung; only released data |

Rules:

- Every fetched dataset is stored in the project with `quelle`, `lizenz`, `abgerufen` and `url`.
- The data stay in a cache in the work folder. **Nothing third-party goes into the repository**, the
  same rule as for the PDFs.
- Tests use small fixtures that we create, or dl-de/zero data with their source.

## 4. Architecture of the integration (proposal)

**Code:**

- New package `services/geodaten` (code and comments in German):

| Module | What it does |
|---|---|
| `dienste.json` | Registry of the services per Land: URL, version, license, attribution and evidence (link to the metadata), like `normen.json` |
| `boreholeml.py` | Import and export |
| `bohrdaten.py` | GBL and state adapters, SEP3 → Bodenart |
| `gelaende.py` | DGM: WCS / download, sampling, cut-out, mesh |
| `gebaeude.py` | LoD2 CityGML / 3D Tiles parameters |
| `hoehen.py` | NHN ↔ ellipsoid, meridian convergence |

- Server endpoints:
  - `POST /api/standort`: new project from a point.
  - `GET /api/projekt/{sig}/umgebung/bohrungen?radius=`.
  - `POST /api/projekt/{sig}/umgebung/gelaende`.
  - `GET /api/projekt/{sig}/export/boreholeml`, next to the existing exports.

**Data model:**

- Per Bohrung: `herkunft` (Gutachten / SGD / manuell).
- Per GOK: `gok_quelle` with the new value `DGM1`.
- Per project: `reifegrad` (Gutachten / Vorerkundung / gemischt) and a list `quellen`.
- In the IFC: a property set with the Herkunft per Bohrung and the sources of the project.

**Operation:**

- Everything external is optional. A project switch "keine externen Dienste" covers confidential
  projects, and the app works offline as today.
- Cache in `ARBEIT/geodaten/<dienst>/…` with a time stamp, plus timeouts and clear messages when a
  service does not answer.

**Viewer:**

- Toggles for Gelände, Gebäude and Fremdbohrungen (another symbol).
- The attribution line.
- The Vorerkundung banner.

## 5. Intervention plan

| Phase | Content | Acceptance | Effort |
|---|---|---|---|
| **P0 Preparation** | Allow the hosts (§7). `dienste.json` for BGR + Berlin, Brandenburg, NRW, Baden-Württemberg and Bayern, with license and evidence per entry. GetCapabilities and the official BoreholeML examples saved as fixtures. Confirm the license of basemap.de 3D. Decide D84–D88 | Every entry has a link to its metadata; the fixtures load offline | 1–2 days |
| **P1 BoreholeML** | Export of the reviewed Bohrungen (canonical JSON → BoreholeML 3.x), DIN 4023 → SEP3 table in the norms database, schema validation; import of the official examples as a round trip | The export validates against the XSD without errors; the round trip of the examples loses no Schicht; unknown codes are marked | 1 week |
| **P2 Existing Bohrungen** | Query by area (GBL + state WFS), list with distance and status, import of released Schichtdaten as `herkunft = SGD`, duplicates with the Gutachten, symbols and attribution in the viewer | For the site of the Berlin example and one site in NRW: the Bohrungen within 250 m are listed, at least one is imported with its Schichten and modelled; duplicates found; no Bohrung without source and license | 1–2 weeks |
| **P3 DGM** | GOK check and fill, terrain surface in the model and in the IFC (`IfcGeographicElement` TERRAIN) | The GOK of the georeferenced Berlin example (EPSG:25833) and of a second georeferenced Gutachten against DGM1 within ±0.5 m, or the difference explained; a wrong EPSG code in a test raises the warning; the IFC still validates, solids closed, unit METRE | 1 week |
| **P4 Umgebungsmodell** | Buildings: basemap.de 3D Tiles in the viewer (toggle) with ζ and the meridian convergence; then LoD2 CityGML of the Land as IFC context or `Umgebung.ifc` | Buildings in place (±1 m in plan, ±0.5 m in height at a known building) on two sites in different Länder; the viewer stays fluid and does not flicker; attribution visible | 1–2 weeks |
| **P5 Standort start** | Step 1 accepts a point; the project uses P2 and P3; `reifegrad = Vorerkundung` in the app, the IFC and the report; a PDF can be added later | From a point in Berlin, a model with ≥ 3 SGD Bohrungen in under a minute; Vorerkundung visible everywhere; with the PDF added, both sources stay apart | 1 week |
| **P6 Optional** | 3D Tiles export for Cesium; GeolDG help (prefilled BoreholeML / SEP3 for the SGD); swissgeol boreholes for Switzerland; OSM fallback; 3DCityDB if a project database is needed | Per item | Per item |

**Status (2026-11-03):**

| Phase | State |
|---|---|
| P0: service registry | **Done for four Länder.** [`dienste.json`](../services/geodaten/geodaten/dienste.json): Berlin, Brandenburg, NRW, Baden-Württemberg with license, attribution and evidence; area per service (NRW from its OGC API: its capabilities name a wrong area). Open: Bayern; the BGR GBL has no feature service (its WFS answers 404, only the WMS map exists) |
| P1: BoreholeML export and import | **Done.** [`boreholeml.py`](../services/geodaten/geodaten/boreholeml.py), code table from the official codelists v2 with the official names as evidence, export valid against the official XSD 3.2, import of the official examples and round trip; *Modell* and *Gutachten* steps ([21 §5.1](21_app_schritte_normen.md#51-boreholeml-for-the-geologische-dienste)); 11 tests + 1 end-to-end check |
| P2: Bohrungen of the state services | **Done.** [`bohrdaten.py`](../services/geodaten/geodaten/bohrdaten.py), *Lage* step ([21 §4.5](21_app_schritte_normen.md#45-bohrungen-der-länder-existing-boreholes-around-the-site)): query only on a click, Gegenprobe (Berlin example: 5 of 5 found, ≤ 0.05 m), import of the BoreholeML Schichtdaten of NRW and Baden-Württemberg; 13 tests + 1 end-to-end check. The GBL is not queried: as a WMS it gives a map, not data |
| P3a: DGM from files, GOK check and fill | **Done.** [`services/geodaten`](../services/geodaten/README.md), *Lage* step ([21 §4.4](21_app_schritte_normen.md#44-gelände-dgm-gok-check-dgm-from-the-land-terrain-in-the-model)), 21 tests + 4 end-to-end checks |
| P3b: DGM through WCS, terrain surface in the model and the IFC | **Done.** [`dgm_dienst.py`](../services/geodaten/geodaten/dgm_dienst.py) (WCS 2.0.1 of Brandenburg with Berlin and NRW; Baden-Württemberg delivers whole metres, Bayern has no free WCS), top of the model from the DGM and `IfcGeographicElement` TERRAIN ([`umgebung.py`](../services/modeler/baugrundmodell/umgebung.py), [21 §4.4](21_app_schritte_normen.md#44-gelände-dgm-gok-check-dgm-from-the-land-terrain-in-the-model)); 13 tests + 3 end-to-end checks |
| P4: Umgebungsmodell (buildings) | **Done with the LoD2 of the Länder.** [`gebaeude.py`](../services/geodaten/geodaten/gebaeude.py): CityGML tiles of 1 × 1 km of Berlin, Brandenburg and NRW in ETRS89/UTM + DHHN2016, so no ζ and no convergence; `IfcBuildingElementProxy` per building with its license ([21 §4.6](21_app_schritte_normen.md#46-gebäude-lod2-buildings-around-the-site)). Heights in place: the ground of each building is the lowest DGM point of its footprint, median 0.00 m in Berlin and Marl. The basemap.de 3D Tiles (way a) are not needed for these Länder; they stay an option for the others |
| P5: Standort start (a Baugrundmodell from a point, Vorerkundung) | **Done, in NRW.** Card *Standort ohne Gutachten* in step 1, the point is the centre of the queries and the origin of the scene; Reifegrad Gutachten / Vorerkundung / gemischt from the *Herkunft* of the Bohrungen in the header, the *Modell* step, the viewer, the report and the IFC (`CPset_Baugrundmodell.Reifegrad`, `CPset_Herkunft` per Bohrung); archive Schichten with confidence 0.5; a PDF added later becomes a new project that takes the Bohrungen der Länder, the query, DGM and buildings with it ([21 §4.7](21_app_schritte_normen.md#47-standort-ohne-gutachten-a-vorerkundung-from-a-point), D94). Acceptance in **Marl instead of Berlin**: Berlin publishes only the header of its Bohrungen, no Schichtdaten, so no model can come from there. In Marl: 11 SGD Bohrungen within 250 m, model in 15 s; 4 tests + 5 end-to-end checks. Open: a map of the distance to the nearest Bohrung in the viewer (per Einheit the IFC carries its maximum distance) |
| P6: Optional (3D Tiles export, GeolDG help, swissgeol, OSM fallback, 3DCityDB) | Open |

**Why this order:**

- P1 needs no network, defines the data mapping that P2 and P5 use, and is useful at once (export).
- P3 comes before P4 because the DGM pays off in the core (GOK and Lage) and is simpler.
- P5 comes last because it rests on P2 and P3.

**Tests:**

- Each phase adds pytest cases with fixtures and keeps the end-to-end check of the app green.
- The extraction (`prototyp_v4.py`) is not touched, so the regression does not change.

**Risks:**

| Risk | Answer |
|---|---|
| Heterogeneous services per Land (WFS 1.1 / 2.0, BoreholeML 3.0–3.2, own codes) | One adapter, an entry per Land in `dienste.json`, tests per entry; start with five Länder |
| Schichtdaten released only in part; old Schichtenverzeichnisse | Maturity and Herkunft always visible; never silent |
| License of basemap.de 3D unclear | Verify in P0; otherwise LoD2 CityGML of the Länder |
| Heights and north (ζ, meridian convergence) | Test against a known building; ζ and the transform stored in the project |
| Service down or slow | Cache, timeouts, the app works without it |
| Confidentiality: a query reveals the site | Switch "keine externen Dienste"; documented in `SECURITY.md` when the feature ships |

## 6. What it does not do

- It does not replace the Gutachten or the engineer's interpretation (DIN 4020 / EN 1997-2): a
  Vorerkundung model is a first picture for planning the investigation.
- It does not redistribute third-party data: it fetches, caches and cites them.
- It does not touch the extraction or its benchmark.

## 7. Hosts to allow in the cloud session

Only for developing in Claude's cloud environment. A user who runs the app on their own PC needs
nothing. Blocked on 2026-11-02 (proxy 403 or not resolved, also for WebFetch), allowed the same day:

- `services.bgr.de`, `schemas.bgr.de`, `boreholemap.bgr.de`, `gitlab.opencode.de` (BGR, BoreholeML).
- `sgx.geodatenzentrum.de`, `sg.geodatenzentrum.de`, `basemap.de` (BKG).
- State services, to be added per Land:
  - `inspire.brandenburg.de`.
  - `ogc-api.nrw.de`, `www.bml3.nrw.de`, `www.wms.nrw.de`, `www.opengeodata.nrw.de`.
  - `services.lgrb-bw.de`.
  - `gdi.berlin.de`.
- `tile.openstreetmap.org`, `overpass-api.de` (OSM fallback).
- `schemas.opengis.net` only answers over **https**: the BoreholeML XSD imports GML and ISO 19139 with
  `http://`, so the check maps them to `https://` (`xmlschema`, `uri_mapper`; X31).

Where: the cloud environment menu in the session's title bar → Edit → Network access. Choose a
broader access level, or add these hosts under Allowed domains and keep "Allow package managers"
ticked ([steps](https://code.claude.com/docs/en/cloud-environments#network-access)).

## 8. Proposed decisions

Recorded in [11 Decisions](11_decisions.md) as **proposed**:

- **D84:** BoreholeML 3.x as the exchange format for Bohrungen, import and export, with SEP3 for
  petrography. The export comes first.
- **D85:** Third-party Bohrungen only with source, license and date. They are marked
  `herkunft = SGD`; a model that uses them carries the maturity Vorerkundung. Never merged silently
  with the Gutachten.
- **D86:** The Umgebungsmodell comes from the official open data of the Länder (DGM1, LoD2) in
  ETRS89/UTM + DHHN2016. basemap.de 3D Tiles are for viewing; OSM is only a fallback.
- **D87:** No Cesium engine and no Cesium ion inside the app. An optional 3D Tiles export serves
  Cesium users.
- **D88:** External services are optional and can be switched off per project (confidentiality).
  The app keeps working offline.

## 9. Sources

BGR and BoreholeML:

- [BGR: Borehole Map of Germany](https://www.bgr.bund.de/EN/Themen/Geodatenmanagement/Bohrpunktkarte-Deutschland/bohrpunktkarte-deutschland_node_en.html)
- [Geodatenkatalog: Borehole Map Germany](https://gdk.gdi-de.org/geonetwork/srv/api/records/f9c33c9d-335d-4878-a73b-efe654f4814a)
- [BGR: German Borehole Locations (WMS)](https://resource.bgr.de/Metadata/DataService/391189fa-f506-4a08-a056-fbb6968649fb)
- [BoreholeML 3.0.1: new location](https://schemas.bgr.de/boreholeml/3.0.1/README.md)
- [BoreholeML example: complete DABO Bohrung](https://schemas.bgr.de/boreholeml/3.0/examples/borehole_complete_DABO_138513.xml)
- [BoreholeML codelists v2: coding standards (SEP3)](https://schemas.bgr.de/boreholeml/codelists/v2/CodingStandardList.xml)
- [BGR: BoreholeML and other exchange formats](https://bgr.bund.de/Infogeo/DE/Home/BoreholeML/Objectives/other_formats.html)

State services and GeolDG:

- [Geodatenkatalog: Bohrpunktkarte Brandenburg](https://gdk.gdi-de.org/geonetwork/srv/api/records/18c3f2ff-1553-46b5-9772-91eaebacccff)
- [open.nrw: Bohrungen in NRW](https://ckan.open.nrw.de/dataset/7a5c72ee-198e-4e58-80bf-a5d1e6196c7f)
- [OGC API NRW: Bohrungen (tiles)](https://ogc-api.nrw.de/brgnrw/v1/tiles)
- [Berlin: Geologische Bohrdaten](https://gdi.berlin.de/geonetwork/srv/api/records/bb30f2e3-f41e-3d60-972b-3b9240fac94a)
- [LBEG: download guide](https://www.lbeg.niedersachsen.de/download/142022/Anleitung_zum_Download.pdf)
- [HLNUG: GeolDG notification and transmission](https://www.hlnug.de/fileadmin/dokumente/geologie/geologie/Merkblatt-HLNUG-Anzeige-und-Ergebnisuebermittlung.pdf)
- [GeolDG § 26](https://www.gesetze-im-internet.de/geoldg/__26.html)

Terrain, buildings and heights:

- [BKG: basemap.de 3D documentation](https://sg.geodatenzentrum.de/web_public/gdz/dokumentation/deu/basemap.de_3d.pdf)
- [basemap.de workshop: 3D visualisation](https://basemap.de/data/website/workshops/03_2023/5_basemap_3D_Visualisierung.pdf)
- [Berlin: LoD2 building models](https://gdi.berlin.de/geonetwork/srv/api/records/3c7c49af-00a4-3bcd-bc00-20e7f0f1b7bf)
- [LGL BW: WCS 2.0 customer information (DGM1)](https://bwmm-support.lgl-bw.de/export/sites/lgl/Produkte/Galerien/Dokumente/Kundeninformation_WCS_2_0.pdf)
- [SAGA: DGM1 NRW (dl-de/zero)](https://saga-gis.sourceforge.io/saga_tool_doc/9.12.0/io_webservices_9.html)
- [Berlin: DGM1](https://gdi.berlin.de/data/dgm1/docs/dgm1.pdf)
- [German DGM datasets (overview)](https://help.emd.dk/mediawiki/index.php/German_DGM_datasets)
- [LVermGeo RLP: quasigeoid model](https://lvermgeo.rlp.de/fileadmin/lvermgeo/pdf/faltblaetter_broschueren/Quasigeoidmodell_Rheinland_Pfalz.pdf)
- [BKG: quasigeoid](https://sg.geodatenzentrum.de/web_public/gdz/dokumentation/eng/quasigeoid_eng.pdf)

Viewers and tools:

- [3DTilesRendererJS](https://github.com/NASA-AMMOS/3DTilesRendererJS)
- [FOSS4G 2021: a web 3D viewer for 11 million buildings (3D BAG)](https://callforpapers.2021.foss4g.org/foss4g2021/talk/VQUHDU)
- [CesiumJS](https://github.com/CesiumGS/cesium)
- [OSM tile usage policy](https://operations.osmfoundation.org/policies/tiles/)
- [OSM copyright and license](https://www.openstreetmap.org/copyright)

Up: [Index](README.md)

Related: [07 Coordinates](07_coordinates.md) · [18 Layer modeler](18_layer_modeler.md) · [21 Step app and norms](21_app_schritte_normen.md) · [Architecture](ARCHITECTURE_BAUGRUNDMODELL.md) · [11 Decisions](11_decisions.md) · [14 Licensing](14_licensing.md) · [Glossary](glossary.md)
