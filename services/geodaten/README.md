---
title: "Geodaten: DGM from files"
date: 2026-11-02
tags: [open-data, dgm, gok]
aliases: [Geodaten, DGM]
---

# Geodaten: DGM from files

First piece of the open data integration ([23](../../docs/23_open_data_integration.md), phase P3).
The user downloads the DGM tiles of their Land (open data, usually DGM1) and loads them in the
*Lage* step. The app compares the GOK of the Gutachten with the terrain and proposes a missing
GOK. No network: nothing reveals the site of the project, and it works in every Land.

| File | What it does |
|---|---|
| [`geodaten/gelaende.py`](geodaten/gelaende.py) | Reading (XYZ text, ESRI ASCII grid, GeoTIFF; also ZIP/GZ and several tiles), bilinear sampling, GOK check and proposals |

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

Up: [Documentation index](../../docs/README.md)

Related: [23 Open data integration](../../docs/23_open_data_integration.md) · [21 Step app](../../docs/21_app_schritte_normen.md) · [07 Coordinates](../../docs/07_coordinates.md)
