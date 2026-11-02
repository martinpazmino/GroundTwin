# Changelog

Notable changes to GroundTwin. The format follows [Keep a Changelog](https://keepachangelog.com/);
the version is the app version shown in the footer (`server/api.py`, `VERSION`).

## [Unreleased]

### Added
- `.editorconfig`, issue and pull request templates, security policy, this changelog.

### Changed
- Repository layout: the extraction moved from `spikes/extraktion_v2` to `services/extractor`, the
  test bench from `spikes/korpus` to `benchmark`, the Supabase migration from `spikes/supabase` to
  `supabase`. The extraction code is unchanged (identical regression results).
- The benchmark tools (`eval_real.py`, `blind_test.py`, `screen_corpus.py`) use the current
  extraction v4; a new blind test freezes v4 predictions.
- `.gitignore`: PDFs (except the examples), IFC files, logs and test outputs are never committed.

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
