# Changelog

Notable changes to GroundTwin. The format follows [Keep a Changelog](https://keepachangelog.com/);
the version is the app version shown in the footer (`server/api.py`, `VERSION`).

## [Unreleased]

### Added
- Standort ohne Gutachten: a Baugrundmodell from a point, marked as **Vorerkundung** (decisions D85, D94).
  - *Gutachten* step: a point in ETRS89/UTM starts a project; the Bohrungen der Länder, the DGM and the buildings
    come from around it.
  - Reifegrad Gutachten / Vorerkundung / gemischt from the origin of the Bohrungen: in the header, the *Modell*
    step, the viewer, the report and the IFC (`CPset_Baugrundmodell.Reifegrad`, `CPset_Herkunft` per Bohrung).
  - Archive Schichten get a fixed confidence of 0.5.
  - A Gutachten added to a Standort becomes a new project that takes the Bohrungen der Länder, the query, the
    DGM and the buildings with it; both sources stay apart (gemischt).
- *Lage* step: LoD2 buildings of Berlin, Brandenburg and NRW around the site (decisions D86, D93).
  - Fetched on a click from the CityGML tiles of the Länder (1 × 1 km, UTM + DHHN2016).
  - In the IFC as context, one `IfcBuildingElementProxy` per building with the license of its service.
  - A *Gebäude* button in the viewer shows or hides them.
- Gelände from the DGM of the Land (decision D92).
  - *Lage* step: the DGM1 of the cut-out around the Bohrungen from the WCS of Brandenburg with Berlin
    and NRW, only on a click, with source, license and attribution.
  - The top of the model follows the DGM and stays exactly on the GOK at each Bohrung. Relief over
    1 m between the Bohrungen is marked as not explored.
  - The terrain around the model is an `IfcGeographicElement` TERRAIN in the IFC, with a *Gelände*
    button in the viewer.
- *Lage* step: Bohrungen der Länder (Berlin, Brandenburg, NRW, Baden-Württemberg) around the site,
  queried only on a click (decisions D85, D88, D91).
  - A Gegenprobe of the Bohrungen of the Gutachten that the Land also has.
  - Import of the BoreholeML Schichtdaten with source, license and date.
- BoreholeML 3.2, the exchange format of the state geological surveys (decisions D84, D90).
  - Export of the reviewed Bohrungen in the *Modell* step, with the sender organisation; valid against
    the official XSD.
  - Codes from the official codelists v2, mapped by name.
  - Import of BoreholeML files in the *Gutachten* step, with the origin marked.
- *Lage* step: Gelände (DGM) from the user's files (XYZ, ASCII grid, GeoTIFF, ZIP, several tiles).
  - The GOK is checked against the terrain, with a warning for a systematic deviation.
  - A missing GOK is taken on a click and marked as source DGM in the app and the IFC.
  - Code in `services/geodaten`, decision D89.
- Evaluation and intervention plan for open data and open-source integrations
  ([docs/23](docs/23_open_data_integration.md)): BoreholeML, BGR Bohrpunktkarte and the state
  geological surveys, DGM and LoD2 for the Umgebungsmodell, basemap.de, Cesium / 3D Tiles,
  OpenStreetMap.
- `.editorconfig`, issue and pull request templates, security policy, this changelog.

### Changed
- The project list counts the imported Bohrungen der Länder.
- A service of the Land that does not answer gives a message (HTTP 502) instead of a server error.
- A dropped connection to a service of the Land is retried (up to three attempts).
- Repository layout: the extraction moved from `spikes/extraktion_v2` to `services/extractor`, the
  test bench from `spikes/korpus` to `benchmark`, the Supabase migration from `spikes/supabase` to
  `supabase`. The extraction code is unchanged (identical regression results).
- The benchmark tools (`eval_real.py`, `blind_test.py`, `screen_corpus.py`) use the current
  extraction v4; a new blind test freezes v4 predictions.
- `.gitignore`: PDFs (except the examples), IFC files, logs and test outputs are never committed.

### Fixed
- Viewer: after the *Lage* step a model over 300 m was never fully in view (That Open's orbit mode limited the
  distance to 300 m and moved the target); the camera now keeps its limit and its target when the mode changes.
- Viewer: the camera no longer stands inside the model or a building when the first model or the first LoD2
  buildings arrive during the *Lage* step, and the first Bohrungen of an empty Standort are fitted into view.

### Removed
- Old experiments, kept in the git history and linked from the docs: prototype v3, the spike
  runners for v1/v2/swissgeol, the IFC spike, the v3 baseline, the frozen predictions of past blind
  rounds and two unused v1 diagrams.

## [3.0] – 2026-10-28

### Added
- Full-screen step app (FastAPI + lit + That Open viewer): Gutachten → Bohrungen → Lage → Einheiten
  → Modell ([docs/21](docs/21_app_schritte_normen.md)).
- Norms database DIN 4023 / EN ISO 14688-1 / DIN 18196, reading of every description, IFC
  `CPset_Bodenansprache`.
- Lage: calibration by scale + reference point + lock, EPSG list with plausibility warning, points on
  the plan.
- Online operation: container, Render blueprint, password, upload limit, CI; free option with a
  Cloudflare tunnel ([docs/22](docs/22_deployment.md)).
- License AGPL-3.0-or-later, third-party licenses, documentation in English.

### Changed
- Streamlit only serves the Excel v1 page.

## [2.0] – 2026-10-27

### Added
- Streamlit app v2: PDF → extraction v4 → review → automatic Baugrundmodell → That Open viewer
  ([docs/19](docs/19_app_v2.md)).
- Layer modeler with automatic Einheiten, closed solids and IFC 4.3 ([docs/18](docs/18_layer_modeler.md)).
- Viewer with the TwinBimM controls, Lage on the plan PDF, Prüfstand and einchecken
  ([docs/20](docs/20_lage_pruefung_viewer.md)).

## [1.0]

### Added
- Excel nach Vorlage: Bohrprofil + Längsschnitt (Hamburg layout) → Excel with 4 sheets
  ([description](geo_agent/README.md)).
