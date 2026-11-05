---
title: "GroundTwin documentation: index"
date: 2026-10-23
updated: 2026-11-05
tags: [index, geo_agent]
aliases: [Index, Map of documents]
---

# GroundTwin documentation: index

Entry point. Goal of the whole set: move from "PDF → Excel for one specific drawing" to a
**layout-independent** extraction that recovers all the data of the Bodengutachten and feeds a
**Baugrundmodell** (Supabase → IFC 4.3 → That Open).

The notes are in English and keep the German technical terms of the Gutachten and of the app
(Bohrung, Schicht, GOK, Lageplan, Längsschnitt…): see the [glossary](glossary.md).

> [!NOTE]
> Summary: v1 depended on fixed positions and colours. Extraction v4 reads the drawing instead
> (geometry, labels, OCR) and is measured on real, stress and synthetic PDFs; the step app turns it
> into a reviewed Baugrundmodell in IFC 4.3. Next: open data and open-source projects (BoreholeML,
> BGR, geoportals, 3D Tiles) in [23](23_open_data_integration.md).

## Start here

- [Architecture and Baugrundmodell](ARCHITECTURE_BAUGRUNDMODELL.md): evaluation, benchmark of tools, Supabase + workers + That Open architecture, IFC 4.3; read it first for the full picture.
- [11 Decisions and conclusions](11_decisions.md): all conclusions in one table, with evidence and status; read it if you only have 5 minutes.
- [16 Lessons learned](16_lessons_learned.md): **project memory**, all the explicit rules (process, input, geometry, labels, text, water, second sources, swissgeol, IFC/Supabase, environment).
- [German–English glossary](glossary.md): geotechnical and swissgeol terms.

## The app today

- [21 Step app, norms and new calibration](21_app_schritte_normen.md): the full-screen app (Gutachten → Bohrungen → Lage → Einheiten → Modell, FastAPI + integrated viewer), warnings for unclassified Schichten, mini database DIN 4023 / EN ISO 14688-1 / DIN 18196 with colours, calibration by distance + reference point + lock, column diameter, description and norm on every Schicht of the IFC, Gelände (DGM) to check and fill the GOK, BoreholeML for the Geologische Dienste.
- [20 Viewer with TwinBimM controls, Lage on the plan and Prüfstand](20_lage_pruefung_viewer.md): TwinBimM controls, camera for models > 5 km, Bohrungen placed on the PDF of the Lageplan/Längsschnitt, own distances in the row, automatic nachführen and einchecken of the review state.
- [18 Layer modeler and That Open viewer](18_layer_modeler.md): automatic Bodenschichten (Einheiten by correlation, surfaces, closed solids), IFC 4.3 and web viewer; results against synthetic ground truth and with Berlin.
- [17 Extraction algorithm v4](17_extraction_algorithm.md): specification by stages E0–E9, parameters and their origin, confidence and canonical output.
- [22 Online: deployment from GitHub](22_deployment.md): free on your own PC with a Cloudflare tunnel (`start_online.bat`), the app as a container (`Dockerfile`, Render blueprint with disk and password), the free hosts compared, why not Vercel, environment variables, measured memory, security, AGPL license and CI.

## Next

- [23 Open data and open-source integration](23_open_data_integration.md): evaluation and intervention plan for BoreholeML, the BGR Bohrpunktkarte and the state geological surveys, a Baugrundmodell from a point, the Umgebungsmodell (DGM + LoD2 buildings), basemaps, Cesium / 3D Tiles and OpenStreetMap.
- [24 Agent team (proposal)](24_agent_team.md): Claude as orchestrator and Gemini as specialists — where Claude's tokens go (measured), what the Google subscription and the Gemini API allow, roles, protocol, permissions, metrics and the roadmap.

## Extraction: problem and design

- [01 Diagnosis: fixed layout assumptions](01_diagnosis_fixed_layout.md): inventory with code lines and measured failures of v1; why it fails with another office.
- [02 Layout-independent Bohrprofil](02_bohrprofil_generalization.md): columns from geometry, scale by regression, description, merging; the core of the solution.
- [03 Längsschnitt without constants](03_laengsschnitt_generalization.md): axes, tunnel, vector geology; design for the second PDF.
- [04 Schraffur DIN 4023](04_schraffur_din4023.md): the graphic column as a second signal, classified with the legend.
- [05 Sondierungen DPH/CPT](05_sondierungen.md): digitising curves with calibrated axes.
- [06 Grundwasser](06_grundwasser.md): symbol, keywords, colour and water lines.
- [07 Coordinates and georeferencing](07_coordinates.md): tables, Lageplan, alignment; German CRSs; it unlocks 3D.

## Measurement

- [09 Validation and benchmark](09_validation_benchmark.md): v1 / v2 / swissgeol results, ground truth format, corpus and metrics.
- [12 Real corpus with public Gutachten](12_public_corpus.md): where to get real PDFs, how to evaluate them without ground truth, legal use.
- [15 Results with real PDFs](15_results_real_pdfs.md): v1 / v3 / v4 / swissgeol with public Gutachten, blind tests, the test bench in three layers, ablation and perturbations.

## Reuse, licensing and collaboration

- [08 swissgeol: what to reuse](08_swissgeol_reuse.md): module map, test on our PDFs, strategies and license.
- [13 Collaboration with swisstopo](13_swisstopo_collaboration.md): what they give us and what we give them, first steps, drafts of issues and email.
- [14 Licensing: internal today, third parties tomorrow](14_licensing.md): AGPL, options, pypdfium2 test, primitives layer.

## History

Kept because the decisions refer to them; the current state is in the sections above.

- [10 Implementation plan](10_implementation_plan.md): the first plan (steps 0–8, 2026-10-23); what was done and how is in [11 Decisions](11_decisions.md).
- [19 App v2: from the PDF to the Baugrundmodell](19_app_v2.md): the Streamlit app, superseded by the step app ([21](21_app_schritte_normen.md)).
- Removed spikes, in the git history at commit `03be932`: [IFC + That Open spike](https://github.com/martinpazmino/GroundTwin/tree/03be932/spikes/ifc_thatopen) (superseded by `services/modeler` and `apps/web`), prototype v3 and the first comparison runners ([extractor history](../services/extractor/README.md#history)), the frozen predictions of the blind rounds 3 and 4 ([benchmark history](../benchmark/README.md#history)).

## Code

- [Extractor](../services/extractor/README.md): extraction v4 used by the app, prototype v2, stress cases and the synthetic PDF generator.
- [`baugrundmodell` modeler](../services/modeler/README.md): canonical JSON → Einheiten → solids → IFC 4.3 (`IfcGeomodel`), norms database, with tests.
- [Web app and viewer](../apps/web/README.md): step app and That Open Engine viewer; Einheiten, properties, sections, vertical exaggeration, Lage editor.
- [Benchmark](../benchmark/README.md): public corpus, ground truth, blind test, regression, ablation and perturbations.
- [Supabase](../supabase/README.md): migration tested on PostGIS and loader of the canonical JSON.
- [Geodaten](../services/geodaten/README.md): DGM from files, the GOK check and BoreholeML export/import (pieces of [23](23_open_data_integration.md)).
- [Examples of the app](../data/beispiele/README.md): Berlin, Talheim, demo and synthetic PDF.

## How to read

```
Architecture ─► 11 Decisions ─► 16 Lessons
      │
      ▼
01 Diagnosis ─► 02 Bohrprofil ─► 04 Schraffur
      │               │   └──────► 05 Sondierungen · 06 Grundwasser · 07 Coordinates
      │               ▼
      └──────────► 03 Längsschnitt
08 swissgeol ─► 13 swisstopo collaboration
      │              14 Licensing
      ▼
09 Validation ◄─ 12 Public corpus ─► 15 Real results ─► 17 Algorithm
      ▼                                                         │
10 Plan (history)                                               ▼
                                                 18 Layer modeler + That Open viewer
                                                                ▼
                                                        19 App v2 (history)
                                                                ▼
                                            20 Lage and Prüfstand ─► 21 Step app
                                                                ▼
                                                  22 Online (own PC, container)
                                                                ▼
                                                  23 Open data integration (plan)
```

Up: [Repository README](../README.md)
