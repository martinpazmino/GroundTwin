---
title: "Geodaten: DGM, BoreholeML and the services of the Länder"
date: 2026-11-02
updated: 2026-11-04
tags: [open-data, dgm, wcs, gok, boreholeml, 3d-tiles, geoldg]
aliases: [Geodaten, DGM, BoreholeML export]
---

# Geodaten: DGM, BoreholeML and the services of the Länder

Pieces of the open data integration ([23](../../docs/23_open_data_integration.md)): the DGM from files and
from the services of the Länder (phase P3), BoreholeML (phase P1), the Bohrungen der Länder (phases P0
and P2), their LoD2 buildings (phase P4), the 3D Tiles export and the GeolDG help (phase P6), below.

The user downloads the DGM tiles of their Land (open data, usually DGM1) and loads them in the
*Lage* step, or fetches the cut-out around the Bohrungen from the service of the Land with a click. The
app compares the GOK of the Gutachten with the terrain and proposes a missing GOK. Files need no
network: nothing reveals the site of the project, and they work in every Land.

| File | What it does |
|---|---|
| [`geodaten/gelaende.py`](geodaten/gelaende.py) | Reading (XYZ text, ESRI ASCII grid, GeoTIFF; also ZIP/GZ and several tiles), bilinear sampling, GOK check and proposals |
| [`geodaten/boreholeml.py`](geodaten/boreholeml.py) | BoreholeML 3.2: export of reviewed Bohrungen, import of BoreholeML 3.x into the canonical JSON |
| [`geodaten/boreholeml_codes.json`](geodaten/boreholeml_codes.json) | Codes of the official codelists v2 that GroundTwin uses, each with the official name as evidence, and the code hierarchies |
| [`werkzeuge/boreholeml_codes.py`](werkzeuge/boreholeml_codes.py) | Generates the JSON from the official codelists; stops if a name is missing or ambiguous |
| [`geodaten/dienste.json`](geodaten/dienste.json) | Services of the state geological surveys: URL, type, systems, area, fields, license, attribution and evidence |
| [`geodaten/bohrdaten.py`](geodaten/bohrdaten.py) | Query around the site (WFS 2.0), UTM → longitude/latitude without PROJ, Gegenprobe, import of BoreholeML Schichtdaten; `am_ort`: what every service of the Länder delivers at a point (map and Standort) |
| [`geodaten/gebaeude.py`](geodaten/gebaeude.py) | LoD2 buildings from the CityGML tiles of the Länder (1 × 1 km), streamed; walls, roof and ground with openings; cut-out, zone prefix |
| [`geodaten/utm.py`](geodaten/utm.py) | ETRS89/UTM with and without zone prefix (25832/4647, 25833/5650): normal form for the services, the offset between the two forms of one zone (lesson S17); UTM ↔ geodetic (Krüger series both ways, below 1 mm against PROJ; the zone by longitude for a click in the map), geodetic → ECEF and the east-north-up frame (GRS80) |
| [`geodaten/quasigeoid.py`](geodaten/quasigeoid.py) | Quasigeoid GCG2016 of the BKG (PROJ-data GeoTIFF, CC BY 4.0): fetched once into the work folder, checked by sha256, read without GDAL (tiles, Deflate, floating-point predictor), ζ bilinear like PROJ |
| [`geodaten/tiles3d.py`](geodaten/tiles3d.py) | 3D Tiles 1.1 from the exported IFC: one GLB each for model, terrain and buildings with the IFC class and GlobalId per node, exact ENU frame per tileset, heights H + ζ, `LIESMICH.txt` with sources and how to load it in CesiumJS |
| [`geodaten/geoldg.py`](geodaten/geoldg.py), [`geoldg.json`](geodaten/geoldg.json) | GeolDG help: deadlines of §§ 8–10, the checklist per Bohrung (what GroundTwin has, what comes from the Bohrprotokoll), the package for the Geologischer Dienst (Fachdaten, Bewertungsdaten, CSV, model documentation); every rule with its § and link |
| [`geodaten/netz.py`](geodaten/netz.py) | One way to every service of the Länder: user agent, up to three attempts after a dropped connection, TLS against the root certificates of the system **and** of Mozilla (certifi); a certificate error is reported clearly and not retried (lesson X33) |
| [`geodaten/dgm_dienst.py`](geodaten/dgm_dienst.py) | DGM1 of the cut-out around the Bohrungen from the WCS 2.0.1 of the Land (GeoTIFF, read by `gelaende.py`), coarser grid for large cut-outs, ExceptionReport and NoData as messages |

**Formats:**

- **XYZ:** one line per grid node, `x y z`.
  - Separated by spaces, tabs, `;` or `,`.
  - Decimal comma accepted with `;` or tabs.
  - Header lines are skipped.
  - The points must form a regular grid.
- **ASCII grid (`.asc`):** header with `ncols`, `nrows`, `xllcorner|xllcenter`, `cellsize` and
  `NODATA_value`.
- **GeoTIFF:** one band. Read with Pillow (libtiff): uncompressed, LZW, Deflate, floating-point
  predictor and tiles all work. EPSG from the GeoKeys, PixelIsArea and PixelIsPoint, `GDAL_NODATA`.
  - Not read: BigTIFF, rotated grids and geographic coordinates. Export these as XYZ.

**Limits:**

- At most 16 million nodes (4 × 4 km at 1 m). For a long Trasse, use a coarser DGM (DGM5).
- Heights must lie between −500 and 9,000 m (otherwise the unit or the NoData value is wrong).
- Tiles must share the same cell size, grid and EPSG.

**GOK check** ([docs/21 §4.4](../../docs/21_app_schritte_normen.md#44-gelände-dgm-gok-check-dgm-from-the-land-terrain-in-the-model)):

- |GOK − DGM| ≤ 0.5 m is unremarkable. A larger difference is marked: a pit, a fill, or a wrong
  Lage.
- A median above 1.0 m with the same sign for at least 80 % of the Bohrungen raises a warning
  about the Lage, the EPSG or the height reference.
- A missing GOK is only proposed. It is applied on a click and marked as source **DGM** in the
  app and in the IFC (`CPset_Herkunft.Hoehe`).

Tests: `python -m pytest tests/test_gelaende.py tests/test_gelaende_app.py`.

**DGM from the Land** (`dgm_dienst.py`, entries `wcs-dgm` in `dienste.json`):

| Land | Service | Delivers | License |
|---|---|---|---|
| Brandenburg with Berlin | WCS `isk.geobasis-bb.de/ows/dgm_wcs`, coverage `bb_dgm` | DGM1, float32, EPSG:25833 | dl-de/by-2.0 (© GeoBasis-DE/LGB; © Geoportal Berlin) |
| NRW | WCS `www.wcs.nrw.de/geobasis/wcs_nw_dgm`, coverage `nw_dgm` | DGM1, float32, EPSG:25832 | dl-de/zero-2.0 |

- Checked and not taken (with the reason in `dienste.json`): Baden-Württemberg (whole metres),
  Bayern (no free WCS).
- Only on a click: the request sends the cut-out to the service.
- More than 3,000 cells per side: a coarser grid (`SCALEFACTOR`).
- In the zone-prefixed systems (EPSG 4647, 5650), the raster stays in the system of the project.

Tests: `python -m pytest tests/test_dgm_dienst.py tests/test_dgm_dienst_app.py` (a dummy replaces the WCS;
one test asks the real ones).

## BoreholeML 3.2

The exchange format of the state geological surveys (AK BoreholeML4, MIT License; schema at
`schemas.bgr.de/boreholeml/3.2`). Details: [docs/21 §5.1](../../docs/21_app_schritte_normen.md#51-boreholeml-for-the-geologische-dienste).

**Export** (`exportieren`): an OGC API FeatureCollection of `bml:Borehole`, like the official examples.

- Only Bohrungen whose Schichten are all reviewed, with ETRS89/UTM coordinates and a GOK in m NHN.
  Every skipped one is reported with its reason.
- Location and path in EPSG 5555/5556 (UTM + DHHN92), as in the official examples: EPSG has no
  UTM + DHHN2016 compound.
- Per Schicht:
  - Kurzzeichen after DIN 4022/4023 as `rockCode` (`codingStandard` DIN4022).
  - The norm reading as `rockNameText`, the description of the Gutachten as `descriptiveText`.
  - Petrography, genesis, consistency, compactness, carbonate and water content as codes of the
    official lists, mapped by their **official names**, never by abbreviation (`Ko` is coal in the
    RockNameList, conglomerate in DIN 4023).
- Groundwater levels only as text: the PDF does not tell the level at encounter from the rest level.
- The export validates against the official XSD (`tests/test_boreholeml.py`, needs the network).

**Import** (`importieren`):

- BoreholeML 3.0.1 to 3.2, in any wrapper (OGC API, WFS).
- A compound EPSG becomes the horizontal one, and its height the GOK.
- Of several Schichtenverzeichnisse, the one with the highest version is taken. The main component
  is the one with the largest percentage.
- SEP3 codes reach a Bodenart of the app through the hierarchy of the codelists (fS → S → Sand).
  Anything else stays unklassifiziert and is marked.
- Every Bohrung carries its origin (`herkunft`, `quelle`, `fremd_id`, a hint in the app).

Tests: `python -m pytest tests/test_boreholeml.py tests/test_boreholeml_app.py`.

## Bohrungen der Länder

Details: [docs/21 §4.5](../../docs/21_app_schritte_normen.md#45-bohrungen-der-länder-existing-boreholes-around-the-site).

| Land | Service | Delivers | License |
|---|---|---|---|
| Berlin | WFS `gdi.berlin.de/services/wfs/bohrdaten` | header data, profile as image | dl-de/zero-2.0 |
| Brandenburg | WFS-BPK `inspire.brandenburg.de/services/bpk_wfs` | header data with / without Schichtenverzeichnis, image | dl-de/by-2.0 |
| NRW | BoreholeML WFS `www.bml3.nrw.de/service/bml` | BoreholeML 3.0 with the released Schichtdaten | dl-de/by-2.0 |
| Baden-Württemberg | BoreholeML WFS `services.lgrb-bw.de/boreholeml/services/bml` | BoreholeML 3.0, often without petrography | not stated by the service |

- Queried only on a click.
- The middle of the project goes to longitude/latitude (Snyder series, < 1 mm against PROJ) to pick the
  services. Then a WFS 2.0 GetFeature runs with a box in the project's UTM system.
- Errors of one service, including an `ExceptionReport` with HTTP 200, only mark that service.
- Imported Schichten get a fixed confidence of 0.5 (`KONFIDENZ_ARCHIV`): archive data, not checked against a PDF.
  A model only from them is a Vorerkundung ([docs/21 §4.7](../../docs/21_app_schritte_normen.md#47-standort-ohne-gutachten-a-vorerkundung-from-a-point)).

Tests: `python -m pytest tests/test_bohrdaten.py tests/test_bohrdaten_app.py` (a dummy replaces the services;
two tests ask the real ones).

**Checking the services from this computer:** `python scripts/dienste_pruefen.py` (Windows:
`.venv\Scripts\python scripts\dienste_pruefen.py`) asks every service of `dienste.json` for its capabilities (tile
services: their server only) and prints one line per service: reachable, or why not (certificate, HTTP, timeout).
It sends no Lage of a project. Tests of the network layer: `python -m pytest tests/test_netz.py` (a local HTTPS
server with its own root).


## Gebäude der Länder (LoD2)

Details: [docs/21 §4.6](../../docs/21_app_schritte_normen.md#46-gebäude-lod2-buildings-around-the-site).

| Land | Tiles | Format | License |
|---|---|---|---|
| Berlin | `gdi.berlin.de/data/a_lod2/atom/LoD2_{e}_{n}.zip` (ATOM feed) | ZIP with CityGML 1.0, EPSG:25833 + DHHN2016 | dl-de/zero-2.0 |
| Brandenburg | `data.geobasis-bb.de/…/lod2_gml/lod2_33{e}-{n}.zip` | ZIP with CityGML 1.0, EPSG:25833 + DHHN2016 | dl-de/by-2.0 |
| NRW | `www.opengeodata.nrw.de/…/lod2_gml/LoD2_32_{e}_{n}_1_NW.gml` | CityGML 1.0, EPSG:25832 + DHHN2016 | dl-de/zero-2.0 |

- Tiles of 1 × 1 km (`{e}`, `{n}` in km), at most 9 per request; per tile the first service that has it.
- Streamed with `iterparse`: an urban tile is 20–25 MB of GML.
- The NRW OGC API for 3D buildings rejects `crs`, so the tiles are used.

Tests: `python -m pytest tests/test_gebaeude.py tests/test_gebaeude_app.py` (a dummy replaces the tiles; one test
loads a real tile of Berlin).

## 3D Tiles and GeolDG (phase P6)

- **3D Tiles** ([21 §5.2](../../docs/21_app_schritte_normen.md#52-3d-tiles-for-cesium)): the grid
  `de_bkg_gcg2016.tif` (995,647 bytes, sha256 `598f1832…f7ac`) comes from `https://cdn.proj.org/` on the first export
  and stays in `<arbeit>/cache`; offline, put it there by hand. Tests: `python -m pytest tests/test_tiles3d.py` (a
  synthetic grid in the same TIFF format; one test fetches the real file). In Cesium:
  `node scripts/check_tiles3d.mjs <export> <tools>`.
- **GeolDG** ([21 §5.3](../../docs/21_app_schritte_normen.md#53-geoldg-what-goes-to-the-geologischer-dienst)): no
  network; the rules are read from `geoldg.json`, each with its § and the link to gesetze-im-internet.de. Tests:
  `python -m pytest tests/test_geoldg.py`.

Up: [Documentation index](../../docs/README.md)

Related: [23 Open data integration](../../docs/23_open_data_integration.md) · [21 Step app](../../docs/21_app_schritte_normen.md) · [07 Coordinates](../../docs/07_coordinates.md) · [Norms database](../modeler/baugrundmodell/normen.json)
