# GroundTwin (Geo_Agent) — project memory

## Goal
From a Bodengutachten in PDF build the **Baugrundmodell**: validated, traceable Bohrungen →
Supabase → IFC 4.3 geometry in That Open Engine. Architecture: `docs/ARCHITECTURE_BAUGRUNDMODELL.md`.
The old app (`app.py`, `geo_agent/`, Streamlit) is v1: fixed positions, 0/58 Bohrungen on other offices' PDFs.
Repository `github.com/martinpazmino/GroundTwin` (formerly CAD_Extract and GeoIM; GitHub redirects the old names),
license **AGPL-3.0-or-later** (D79).

## Read before touching the extraction
- `docs/16_lessons_learned.md`: explicit rules (process P1–P21, input E, geometry G, labels L/T, text B, water W,
  second sources S, swissgeol R, model M, environment X). Respect them.
- `docs/17_extraction_algorithm.md`: specification of the algorithm (stages, parameters, confidence).
- `docs/15_results_real_pdfs.md`: blind and training results.
- `docs/11_decisions.md`: decisions D1–D103 (D100–D103 proposed).
- `docs/18_layer_modeler.md`: layer model (N3) and That Open viewer.
- `docs/19_app_v2.md`: Streamlit app v2 (history; superseded by 21).
- `docs/20_lage_pruefung_viewer.md`: viewer with TwinBimM controls, models > 5 km, Lage on the plan, Prüfstand.
- `docs/21_app_schritte_normen.md`: step app (FastAPI + viewer), norms for the description, new calibration.
- `docs/22_deployment.md`: free online from your own PC (Cloudflare tunnel), container (Render), free hosts compared,
  why not Vercel, variables, memory, CI.
- `docs/23_open_data_integration.md`: open data and open-source integration (BoreholeML, BGR Bohrpunktkarte, DGM +
  LoD2 Umgebungsmodell, 3D Tiles, Cesium/OSM): evaluation and plan P0–P6.
- `docs/25_laender_dgm_lod2_research.md`, `docs/26_laender_bohrungen_options.md`: DGM1/LoD2 and Bohrungen of the
  Länder without a service (survey, live checks, options; `bohrdaten_wms.py` prototype, not wired).
- `docs/24_agent_team.md`: agent team (MVP built in `agenten/`): Claude as orchestrator, Gemini API agents (no tools,
  patches in worktrees, Claude approves), measured token profile, Google subscription limits (no automation through `agy`).

## Working rules
- **Blind test**: with a new PDF, freeze the predictions (`benchmark/blind_test.py freeze`)
  and **push them to the repo before opening the PDF**; then transcribe the ground truth in `benchmark/groundtruth/`.
- Always keep blind figures apart from training figures.
- Every change to the extraction passes the regression on real PDFs, stress cases and synthetic ones:
  `python benchmark/regression.py --module services/extractor/prototyp_v4.py --real <pdfs> --stress <ordner>
  --synth <ordner> --baseline benchmark/baseline_v4.json` (stress cases: `stress_cases.py`; OCR with
  `GEO_OCR_CACHE=<dir>`). In addition: `ablation.py` (which rule protects which case) and `perturb.py`
  (rotate/scale/raster).
- General rules (features of the drawing), never exceptions per PDF or office.
- A doubtful value is **marked** (issue / low confidence), never hidden. A false Bohrung is worse than a missing one.
- Third-party PDFs are **not** pushed to the repo: only URL, `sha256` and factual data.
- **Documentation in English**, keeping the German technical terms of the Gutachten and the app (Bohrung, Schicht,
  GOK, Lageplan, Längsschnitt, Einheit… see `docs/glossary.md`); linked notes (Up/Related, frontmatter); doc file
  names in English (D82). **Code, comments and UI texts in German.**

## App, model and viewer
- Step app (docs/21): `python -m server` (Windows: `start.bat`, port 8500) = FastAPI (`server/`) + page
  `apps/web/dist` (lit + viewer). Streamlit (`app.py`, `start_excel.bat`) only for Excel v1.
- **Focus (D99, docs/21 §1.1–1.2)**: the use case is a Gutachten shown interactively and checked for plausibility, also
  against the Bohrungen der Länder. Start = two paths of the same weight (Gutachten PDF / Standort point); each step
  shows its core and folds the rest under **Erweitert** (Lage: DGM, Gebäude, Darstellung; Einheiten: model settings;
  Modell: further exports, 3D Tiles, BoreholeML, GeolDG, Überhöhung), open when it holds data. **Never delete a
  function; fold it.** A new function goes under *Erweitert* unless it serves the use case.
- Project rules in `ui/projekt.py` (`aendern(op)`): warnings = **unklassifiziert** Schichten (not confidence), all
  reviewed, remove/restore, Ø of the columns, calibration (scale by distance or 1:n + reference point + rotation /
  vertical scale + lock), dragging only with the lock (plan x/y; section: height only without a GOK from the PDF),
  points on the locked plan (place, assign to a Bohrung, delete).
  Extraction/model in `ui/pipeline.py`; the extraction is used from `services/extractor/prototyp_v4.py` without
  touching it.
- Gelände (D89, D92, docs/21 §4.4): `services/geodaten` (package `geodaten`) reads the user's DGM files (XYZ, ASCII,
  GeoTIFF, ZIP) without network, or fetches the DGM1 of the Land on a click (`dgm_dienst.py`, WCS of Brandenburg with
  Berlin, NRW, NI and MV in `dienste.json`); the GOK check marks, a missing GOK is applied on a click (`gok_quelle` DGM, IFC
  `CPset_Herkunft.Hoehe`); never replaces a GOK from the PDF. The top of the model follows the DGM, exact at the
  GOK (`services/modeler/baugrundmodell/umgebung.py`, setting `gelaende_dgm`), terrain around it as
  `IfcGeographicElement` TERRAIN. Tests `tests/test_gelaende*.py`, `tests/test_dgm_dienst*.py`.
- BoreholeML 3.2 (D84, D90, docs/21 §5.1): `services/geodaten/geodaten/boreholeml.py` exports only reviewed
  Bohrungen with ETRS89/UTM and GOK (EPSG 5555/5556), codes from `boreholeml_codes.json` (regenerate with
  `werkzeuge/boreholeml_codes.py`, mapped by official names, P15); import marks the origin. Must stay valid against
  the official XSD: `tests/test_boreholeml.py` (needs network; opengis only over https, X31).
- Bohrungen der Länder (D91, docs/21 §4.5): `geodaten/bohrdaten.py` + `dienste.json` (services with license and
  evidence; all 16 Länder, D98: 5 with Bohrungen services (NW, BW, HH with Schichten; BE, BB Kopf; DGM also NI, MV; LoD2 also NI, BY, RP, MV, SN, docs/25), the other 11 as portal links marked *ungeprueft*; the Land from
  VG2500 borders in `geodaten/laender.py`, at a border both); query **only on a click**; Gegenprobe against the Gutachten; import only BoreholeML with Schichtdaten into
  `fremd.json` (codes `NW-…`, `herkunft` SGD, never exported back). Tests use the service dummy of
  `tests/test_bohrdaten.py`; two tests ask the real services (skip offline). Every request goes through
  `geodaten/netz.py` (TLS: system store + certifi, X33); `scripts/dienste_pruefen.py` checks all services from the
  user's machine.
- Dienste der Länder (D98, docs/21 §4.8): the file is `services/geodaten/geodaten/dienste.json`, the tool is
  `dienste.html` (`server/dienste_werkzeug.py`, `geodaten/dienste.py`: validate, complete, order, save atomically with
  the version read, `pruefen_live`); `GET/PUT /api/dienste`, `POST /api/dienste/pruefen`. Editing only without a
  password or with `GEO_AGENT_DIENSTE_BEARBEITEN=1`; online only saved entries are checked (no address from the
  request). `GEO_AGENT_DIENSTE` puts the registry elsewhere. Tests `tests/test_dienste_werkzeug.py` (on a copy).
  Untested links stay *ungeprueft* until someone checks them; never mark a link geprueft without a check.
- Gebäude (D86, D93, docs/21 §4.6): `geodaten/gebaeude.py` reads the LoD2 CityGML tiles (AdV profile, UTM +
  DHHN2016) of BE, BB, NW, NI (1 km) and BY, RP, MV, SN (2 km, `kachel_km`) on a click (`dienste.json`, per grid and tile the first service that has it) into
  `gebaeude.json`; IFC context as `IfcBuildingElementProxy` with the license of its service, viewer button *Gebäude*; the Länder of the
  cut-out (radius = half its diagonal), the Land of the centre first.
  Tests `tests/test_gebaeude*.py`.
- Standort ohne Gutachten (D94, docs/21 §4.7): `standort_anlegen` in `server/arbeitsplatz.py` (point in ETRS89/UTM,
  Germany only) makes an empty project whose point is the centre of the queries and the origin of the scene; Reifegrad
  Gutachten / Vorerkundung / gemischt from the `herkunft` of the Bohrungen (`ui/projekt.py`, `baugrundmodell.modell`),
  shown in the header, the *Modell* step, the viewer band, the report and the IFC; a PDF added to a Standort becomes a
  new project with the Bohrungen der Länder, query, DGM and buildings. Tests `tests/test_standort_app.py`.
  The point can come from a map pop-up (D97, `apps/web/src/app/karte.ts`: Leaflet, basemap.de/OSM tiles loaded only
  when it opens; `GET /api/standort/punkt` converts the click with `utm.von_geo` and lists `bohrdaten.am_ort`); a
  Standort project shows no Lageplan sections in *Lage*; examples `STANDORT_BEISPIELE` (Dortmund, Karlsruhe, Berlin).
  Tests `tests/test_karte.py`.
- 3D Tiles for Cesium (D87, D95, docs/21 §5.2): `geodaten/tiles3d.py` turns the exported IFC into 3D Tiles 1.1 (one
  GLB each for model, terrain, buildings), every vertex exactly UTM → ECEF (`geodaten/utm.py`), heights + ζ of the
  GCG2016 (`geodaten/quasigeoid.py`, fetched once from cdn.proj.org into `<arbeit>/cache`, sha256, never committed);
  only ETRS89/UTM; ETRS89 not converted to WGS84 and said so. Tests `tests/test_tiles3d.py`; check with the official
  validator and CesiumJS: `node scripts/check_tiles3d.mjs <export> <tools>` (tools outside the repo).
- GeolDG help (D96, docs/21 §5.3): `geodaten/geoldg.py` + `geoldg.json` (every rule with § and link): deadlines of
  §§ 8–10 from `p.geoldg` (op `geoldg`), a checklist per own Bohrung (✓ / ⚑ not from the PDF / ✗), and the package
  (`export/geoldg`: BoreholeML, IFC, report, model documentation, `pruefliste.csv`); refused without own Bohrungen.
  A help, never legal advice. Tests `tests/test_geoldg.py`.
- Norms (DIN 4023 / EN ISO 14688-1 / DIN 18196): `services/modeler/baugrundmodell/normen.json` + `normen.py`, with
  evidence per value; read them, never apply them silently (proposal with a click). IFC: `CPset_Bodenansprache` per
  Schicht.
- `services/modeler` (package `baugrundmodell`): `python -m baugrundmodell model.ifc a.json [...] --bericht report.json`;
  tests `cd services/modeler && python -m pytest tests`. Every change: exact contacts, closed solids, IFC without
  errors, **unit METRE** (M17).
- `apps/web` (step app `src/app`, viewer `src/viewer`: TwinBimM controls, Lage editor): after changing anything
  `npm run build` and **commit `apps/web/dist`** (the server uses it without Node); web-ifc 0.0.77 (X9). Test:
  `python scripts/testplan.py <plans>` and in `apps/web` `node scripts/check.mjs <model.ifc> <plans> <screenshots>` (19).
- End to end: `python -m server --port <p> --kein-browser --arbeit <empty>` and `node scripts/check_app.mjs
  http://localhost:<p> <plans> <screenshots>` (54 checks, also when run twice on the same server; B3, B4, B5 (with 3D Tiles) and F need the network and are left out when the service cannot be reached; with a password: `GEO_AGENT_PASSWORT=…`). `pkill`/`pgrep -f`
  in a separate command (X3, X19).
- Online (docs/22, D80): `Dockerfile` (python:3.13-slim, OCR off with `--build-arg OCR=0`, data in `/data`, user
  1000) and the `render.yaml` blueprint. Variables: `PORT`, `GEO_AGENT_HOST`, `GEO_AGENT_PASSWORT` (HTTP Basic except
  `/gesund`), `GEO_AGENT_BENUTZER`, `GEO_AGENT_MAX_MB`, `GEO_AGENT_ARBEIT`, `GEO_AGENT_QUELLCODE`,
  `GEO_AGENT_DIENSTE`, `GEO_AGENT_DIENSTE_BEARBEITEN`. The *Quellcode* link
  (AGPL § 13) stays. Dependencies: `requirements-server.txt` + exact versions in `constraints.txt` (D81; renewed with
  `pip freeze`); CI `.github/workflows/pruefungen.yml`. Third parties: `THIRD_PARTY_LICENSES.md`; rules:
  `CONTRIBUTING.md`.
- **Agententeam (docs/24, D100–D103)**: `python -m agenten pruefen` (all checks, one verdict: read it instead of
  logs), `doku`, `stand` (start a session with it), `review`, `diagnose --befehl "…"` (Gemini proposes, the patch waits
  in a worktree), `tests --modul … --ziel tests/…` (kept only if it kills mutants), `uebernehmen <id>` /
  `verwerfen <id>` (only after reading the patch), `uebergabe` (task file in `agenten/auftraege/` for Antigravity, the
  user starts it), `kosten`. Delegate loops of three or more turns or more than ~20 k tokens of reading; review diffs
  in groups ≤ ~15 k tokens (the lite models wave large diffs through, docs/24 §9). Agent findings are claims: verify
  every high or medium one in the code. Settings in `.env`
  (`agenten/env.beispiel`); paid models only with `AI_ALLOW_PAID_API=true`. Tests `tests/test_agenten.py`.
- Free online (D83): `start_online.bat` / `scripts/online.py` start the server **always with a password** and a
  Cloudflare Quick Tunnel (`cloudflared`, `CLOUDFLARED` for the path); it refuses a server already running on the
  port. Test `tests/test_online.py` with a simulated cloudflared.

## Environment (cloud sessions)
- Geodata hosts of docs/23 §7 (BGR, schemas.bgr.de, BKG, Länder) allowed since 2026-11-02 (before: X30);
  schemas.opengis.net only over https (X31); cdn.proj.org (GCG2016) reachable, overpass-api.de and
  api.boreholes.swissgeol.ch not (2026-11-04). Municipal websites were blocked (the user uploads the PDFs); pypi, npm
  and GitHub reachable.
- Heavy dependencies in venvs in the scratchpad: `venv` (pymupdf, opencv, rapidocr), `sgvenv` (swissgeol).
- Docker (X25, X26): start `dockerd` in the background with the longest time limit; apt blocked → `--build-arg OCR=0`,
  `--network host`, the session's proxy and CA as a secret. vercel.com, render.com, gnu.org and flaviocopes.com
  blocked (Vercel docs: Vercel MCP or search).
- The GitHub tools of the session only accept the repository name in the session scope (X29).
- Working branch given by the session; do not open a PR unless asked.
