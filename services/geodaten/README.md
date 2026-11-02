---
title: "Geodaten: DGM from files and BoreholeML"
date: 2026-11-02
tags: [open-data, dgm, gok, boreholeml]
aliases: [Geodaten, DGM, BoreholeML export]
---

# Geodaten: DGM from files and BoreholeML

Pieces of the open data integration ([23](../../docs/23_open_data_integration.md)): the DGM (phase P3)
and BoreholeML (phase P1, below).

The user downloads the DGM tiles of their Land (open data, usually DGM1) and loads them in the
*Lage* step. The app compares the GOK of the Gutachten with the terrain and proposes a missing
GOK. No network: nothing reveals the site of the project, and it works in every Land.

| File | What it does |
|---|---|
| [`geodaten/gelaende.py`](geodaten/gelaende.py) | Reading (XYZ text, ESRI ASCII grid, GeoTIFF; also ZIP/GZ and several tiles), bilinear sampling, GOK check and proposals |
| [`geodaten/boreholeml.py`](geodaten/boreholeml.py) | BoreholeML 3.2: export of reviewed Bohrungen, import of BoreholeML 3.x into the canonical JSON |
| [`geodaten/boreholeml_codes.json`](geodaten/boreholeml_codes.json) | Codes of the official codelists v2 that GroundTwin uses, each with the official name as evidence, and the code hierarchies |
| [`werkzeuge/boreholeml_codes.py`](werkzeuge/boreholeml_codes.py) | Generates the JSON from the official codelists; stops if a name is missing or ambiguous |

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

**GOK check** ([docs/21 §4.4](../../docs/21_app_schritte_normen.md#44-gelände-dgm-check-and-fill-the-gok)):

- |GOK − DGM| ≤ 0.5 m is unremarkable. A larger difference is marked: a pit, a fill, or a wrong
  Lage.
- A median above 1.0 m with the same sign for at least 80 % of the Bohrungen raises a warning
  about the Lage, the EPSG or the height reference.
- A missing GOK is only proposed. It is applied on a click and marked as source **DGM** in the
  app and in the IFC (`CPset_Herkunft.Hoehe`).

Tests: `python -m pytest tests/test_gelaende.py tests/test_gelaende_app.py`.

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

Up: [Documentation index](../../docs/README.md)

Related: [23 Open data integration](../../docs/23_open_data_integration.md) · [21 Step app](../../docs/21_app_schritte_normen.md) · [07 Coordinates](../../docs/07_coordinates.md) · [Norms database](../modeler/baugrundmodell/normen.json)
