# Changelog

Notable changes to GroundTwin. The format follows [Keep a Changelog](https://keepachangelog.com/);
the version is the app version shown in the footer (`server/api.py`, `VERSION`).

## [Unreleased]

### Added
- **Homogenbereiche (VOB/C)** (docs/28): Einheiten per Gewerk (ATV) to Homogenbereiche in the step
  Einheiten, with the Kennwerte each ATV asks for; IFC Pset `CPset_Homogenbereich_<ATV>` on Einheiten and Bodenschichten,
  and a model of Homogenbereiche only.
- **Grundwasserfläche** (Ground Analysis G5, docs/27 §6.6): a surface through the water levels of the Bohrungen, dry
  Bohrungen as a check, hints instead of silent assumptions, shown blue in the viewer; not in the IFC and not a design
  water level.
- **Orientation entered per Einheit** for the implicit method (docs/27 §6.5): Fallrichtung and Fallwinkel replace the
  fitted plane; source `Eingabe` in the report and the IFC; the Kreuzprobe uses it too.
- **Ground Analysis in the viewer** (docs/27 §6.2): the base of an Einheit coloured by σ, and the virtuelle Bohrung by a
  click in the viewer.
- **Erkundungsvorschlag** (Ground Analysis G4, docs/27 §6.4): where the next Bohrung improves the model most, from the
  uncertainty of the bases and of the extent of the Einheiten; validated on a Rinne against random positions.
- **Implicit interpolation with GemPy** (Ground Analysis G3, docs/27 §6.3), optional (`requirements-analyse.txt`): one
  scalar field per surface, orientation from the contacts, exact at the Bohrungen, spline for folded surfaces.
- **Ground Analysis in the app** (phase G2, docs/27 §6.2): step Einheiten → Erweitert, Kreuzprobe, Unsicherheit per Einheit
  and virtuelle Bohrung on a click.
- **Ground Analysis, phase G1** (`services/analyse`, docs/27): Kreuzprobe (how well the layer model predicts a Bohrung it
  has not seen; names Bohrungen their neighbours do not let expect), Unsicherheit per Einheit and node, and the virtuelle
  Bohrung at any point, on the command line.
- **Hints of Bohrungen for Länder without their own WFS** in *Bohrungen der Länder* (WMS-GetFeatureInfo of the BGR, and
  Bremen): Lage, GOK, Teufe and a profile link where there is one. Only a hint: no Schichten, never into the model, and
  the portal of the Land stays (decision D104, docs/26).
- **LoD2 of Bayern, Rheinland-Pfalz, Mecklenburg-Vorpommern and Sachsen** (2 × 2 km tiles: each service on its own grid)
  and **Bohrungen with Schichtdaten from Hamburg** (BoreholeML 3.0 WFS of the Geologisches Landesamt).
- **DGM1 vom Land for Niedersachsen and Mecklenburg-Vorpommern, LoD2 for Niedersachsen** (WCS / 1-km tiles, CC BY 4.0),
  surveyed and checked live for all 13 Länder without a service (docs/25); first work of Antigravity, rechecked by Claude.
- Survey of borehole sources of the Länder without a WFS and a WMS-GetFeatureInfo prototype for head data
  (`geodaten/bohrdaten_wms.py`, BGR for 13 Länder and Bremen; docs/26).
- Plausibility report per Bohrung in the Bohrungen step (`ui/plausibilitaet.py`, docs/21 §2.1).
- **Plausibility report per Bohrung** (`ui/plausibilitaet.py`, `plausibilitaet` in `server/arbeitsplatz.py`, *Bohrungen* step in `apps/web/src/app/schritt_bohrungen.ts`, `tests/test_plausibilitaet.py`, [docs/21 §2.1](docs/21_app_schritte_normen.md#21-plausibility-report-per-bohrung)): checks the effective (corrected) values for `reihenfolge`, `luecke`/`ueberlappung`, `beginn`, `endteufe`, `duenn`, `grundwasser`, `gok_fehlt` and `gok_nachbarn` without modifying data.
- **Agent team** for development (`agenten/`, docs/24): one command for all checks with a short verdict, a docs
  link/number check and a session state; Gemini agents through the API (review of a diff, diagnosis of a failing check
  with the fix applied in a git worktree, merged only on Claude's approval); a task hand-off to Antigravity; token and
  cost records of agents and of Claude; tests written by an agent, kept only if they kill mutants of the module.
  Shared spec for non-Claude agents: `AGENTS.md`. Measured on three real tasks (docs/24 §9).
- Tests for `geodaten/laender.py` (`tests/test_laender.py`): areas instead of rectangles, the Land of the centre
  first, UTM zones and the zone prefix.
- **All 16 Länder** in the registry of services (decision D98): the 12 Länder without a data service with their
  portals for Bohrungen, DGM and LoD2 as links, plus the Bohrpunktkarte of the BGR, marked *ungeprüft* (entered, not
  tested). A query in such a Land names the portal instead of "0 Bohrungen".
- Tool **Dienste der Länder** (`dienste.html`, link on the start page and in the menu ⋯): all services and portals as
  a table Land × theme; edit, check against the real service, save (validated, ordered, with the version read).
  Online with a password: read and check only (`GEO_AGENT_DIENSTE_BEARBEITEN=1` to edit); `GEO_AGENT_DIENSTE` keeps
  the registry elsewhere. The app uses a saved change at once.
- Standort ohne Gutachten **from a map** (decision D97): a pop-up with the basemap.de map of the BKG (or OpenStreetMap);
  a click sets the point in ETRS89/UTM and shows what the services of the Länder deliver there.
- Standort examples: Dortmund (NRW, Bohrungen with Schichtdaten), Karlsruhe (Baden-Württemberg, Schichten often
  without petrography) and Berlin (header data only: terrain and buildings, no layer model).
- *Lage* step of a Standort project: no Lageplan sections (the point is already georeferenced); a *Standort*
  section with the point and the services there; *Bohrungen der Länder* first and open.
- *Bohrungen der Länder*: a line says why a Bohrung cannot be taken over (Berlin and Brandenburg give the
  Schichtenverzeichnis only as an image).
- *Modell* step: the Baugrundmodell as **3D Tiles 1.1 for Cesium** (CesiumJS, Cesium for Unreal, QGIS 3D;
  decisions D87, D95).
  - One glTF tile each for the model, the terrain and the buildings, read from the exported IFC.
  - Every vertex converted exactly from ETRS89/UTM; heights made ellipsoidal with the quasigeoid GCG2016 of the
    BKG (CC BY 4.0, fetched once from the PROJ CDN and checked by sha256).
  - Valid for the official 3d-tiles-validator; in CesiumJS the top of the model lies within 1 mm of the expected
    height (`scripts/check_tiles3d.mjs`).
- *Modell* step: **GeolDG help** for the transmission to the Geologischer Dienst (decision D96).
  - Deadlines of §§ 8–10 from the dates of the investigation.
  - Per Bohrung what GroundTwin delivers (Lage, Ansatzhöhe, Endteufe, reviewed Schichtenverzeichnis, marked when
    not from the PDF) and what comes from the Bohrprotokoll.
  - A package with the Fachdaten (BoreholeML), the Bewertungsdaten (IFC, report, model documentation) and a
    checklist to fill in. Every rule with its § and a link to the law; a help, not legal advice.
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
- Colours of Fels and geological Benennungen after DIN 4023 Tabelle 2 and 3 (e.g. Mergelstein and
  Geschiebemergel violettblau, Löß oliv), replacing display choices (docs/28 §5).
- **The UI puts the first use case in front** (decision D99): a Gutachten shown interactively and checked for
  plausibility, also against the Bohrungen of the Länder. Nothing was removed.
  - Start page with **two paths of the same weight**: *Gutachten* (drop the PDF) and *Standort* (a point on the map).
    OCR, typed coordinates, examples and older projects are folded; the first step is called *Start*.
  - *Lage*: one sentence on the state and the next step; *Vergleich mit Bohrungen der Länder* open; Gelände (DGM),
    Gebäude (LoD2) and Darstellung under **Erweitert** (open as soon as a DGM or buildings are loaded); the Lageplan
    sections fold once every Bohrung has a position.
  - *Einheiten*: the model settings under *Erweitert*, below the Einheiten (open when one differs from the default).
  - *Modell*: IFC and Prüfbericht in front; the other exports, 3D Tiles, BoreholeML, GeolDG and the Überhöhung under
    *Erweitert*.
- The Land of a point comes from **the borders of the Länder** (VG2500 of the BKG), not from the overlapping
  rectangles of the services: Berlin no longer asks Brandenburg, a click in Saxony-Anhalt no longer names Brandenburg;
  at a border both Länder are asked, the Land of the centre first (also for the LoD2 tiles).
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
- *Lage* after *Alle Korrekturen verwerfen* and the same Bohrungen der Länder imported again: the view now shows
  them whole. Their model came from the cache together with them and kept the view on the empty scene (lesson M42).
- Standort: a point in another UTM zone (for example Paris in zone 31) passed the check "in Germany"; the zone and the
  longitude/latitude are checked now.
- Exports with a project name containing characters outside latin-1 (for example "–" or "✓", common in file names of
  Gutachten) failed; download names now go as UTF-8 with an ASCII fallback, without the characters Windows forbids.
- Standort: the same point a second time opens the existing project (name and step stay) instead of renaming it;
  resetting keeps the name and returns to the *Lage* step; the dialog says that imported Bohrungen der Länder, DGM
  and buildings go too.
- Zone prefix (EPSG 4647/5650): Bohrungen der Länder come into the system of the project, the Gegenprobe compares in
  one system, and a Gutachten added to a Standort gets the Bohrungen, DGM and buildings in its own system. Buildings in
  another system than the Bohrungen are now marked instead of silently left out of the IFC.
- Clear messages: a site without a service of the Land, a model or a BoreholeML export without Bohrungen.
- Viewer: after a reset the next model is fitted into view again, and the Reifegrad band of the previous project
  disappears when the project changes.
- Services of the Länder on Windows: Berlin failed with `CERTIFICATE_VERIFY_FAILED` (its new Telekom root was not
  yet in the Windows store). TLS now checks against the system store and the Mozilla roots (certifi); a certificate
  error is reported clearly and not retried. `scripts/dienste_pruefen.py` checks every service from this computer.
- Viewer: after the *Lage* step a model over 300 m was never fully in view (That Open's orbit mode limited the
  distance to 300 m and moved the target); the camera now keeps its limit and its target when the mode changes.
- Viewer: the camera no longer stands inside the model or a building when the first model or the first LoD2
  buildings arrive during the *Lage* step, and the first Bohrungen of an empty Standort are fitted into view.

- End-to-end check: the BoreholeML check counted the switched-off 3D Tiles button too, and the waiter of the 3D
  Tiles check kept polling into the next page (a page error); both fixed with the GeolDG check.

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
