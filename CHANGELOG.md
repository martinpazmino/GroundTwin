# Changelog

Notable changes to GroundTwin. The format follows [Keep a Changelog](https://keepachangelog.com/);
the version is the app version shown in the footer (`server/api.py`, `VERSION`).

## [Unreleased]

### Added
- AGS4 export (#30, docs/21 §5.1a): reviewed Bohrungen and Sondierungen in AGS 4.1.1 for OpenGround, Leapfrog and the
  route to PLAXIS. Ruhewasser is a depth remark, not a water strike; CPT values only with a read unit. Valid against the
  checker of the AGS Data Format Working Group (`python-ags4`, tests). Also in the AGSi package.
- Readiness (#35): fines class from the description (DIN 4023 guide values, DIN 18196); "no fines named" is shown as
  *assumed*, and the DAUB pre-selection names it (Berlin: DAUB 3/9, hinweisend). Catalogue entry
  `ansprache.feinkornanteil_klasse` (docs/29 §8.3).
- Sondierungen (#54): a frame must be closed at the top and the bottom (a line along the bottom of two panels no
  longer merges them), aborted CPT with a depth axis `0`/`1` are read (hint), values keep the channel of the axis they
  are read on. Planfeststellung (training) 19 → 23/24, 0 false values. Sondierungen stress `s15` (docs/16 G7).
- Sondierungen (#54): the header of a neighbouring diagram no longer hides value ticks; only frame edges join panels
  (curve steps or a section line across two panels no longer merge them). U09 DPH 5/5, Planfeststellung CPT/DPH
  15 → 19/24. Stress `s13`, `s14`.
- #55 completed: water label between two columns goes to the matching GOK, then to the side of the page's labels (W7c);
  T15 ignores a laboratory note beside the descriptions; `Grasnarbe` is Mutterboden; Sondierungen: frames down to
  25 × page factor (RS of 1.7 m), Endtiefe from the end label below the curve end (values not invented). A20 (training):
  200/200 Bohrungen, Bodenart 985/993, 0 false GW, RS 30/30 with Endtiefe 30/30. Stress `s45`, Sondierungen `s12`.
- One text block per layer (#55, docs/16 T15): multi-line descriptions starting at the label of their lower edge are
  assigned block by block. A20 (training): Bodenart 711 → 891/993. Stress `s44`.
- Water symbol points down (#55, docs/16 W9): the arrowhead of an axis and the Ansatzpunkt marker `NN+…` of a
  neighbouring diagram are no water. A20 (training): false levels 6 → 1, GW-Status 25/25. Stress `s43`.
- Sondierungen (#55): shorter diagram frames on long sheets, depth and NHN labels snapped to their lines (the hatching
  of a neighbouring profile is no tick). A20 RS 24 → 29/30 found, Endtiefe 20 → 28/30; U09 and Planfeststellung
  Endtiefen better. Stress `s11`.
- Blind round 7 (docs/15 §8.11): two reports without Bohrprofile, 0 false. Talheim training PDF back in the regression:
  T12 no longer reads `Anschüttung` as a well installation (10/10 again); all 13 real PDFs without regression.
- Prefixes from the legend of the page (#54 item 5, docs/16 T14): `BK = Rammkernbohrung`, `S = Baggerschurf` make
  `BK A/1`, `S A1` codes; double labels `Tiefe (Höhe)` are the data (T9: confirm the nearest line within 10 cm, a label
  without a line is a boundary). Planfeststellung (training): 41 → 95/115 Bohrungen, water 5 → 67/69, 0 false
  boundaries. Stress `s41`, `s42`.
- Blind round 6 (A20 Unterlage 20.1, docs/15 §8.10): ground truth 200 Bohrungen and 30 RS; rules from it (#55): an
  installation drawing of a well is no Bohrprofil (T12), codes `BS 105A`/`BS 22.1` (T13), water label `0,75 GW` with
  `NN+…` under it (W7b), T11 only with the same number in the code; Sondierungen `RS n` with the Art of the page and the
  Ansatzhöhe `NN+8,83m`. A20 (training): 200/200 Bohrungen, 0 false. `blind_test.py score` reads `gw_status` from the
  frozen detail (it was always 0).
- Rules from blind round 5 (#54, docs/16 T6–T11, W7, W7b, docs/15 §8.9): a title-block number is no Bohrung code,
  codes with a station (`B-5+365-G`, `DPH-0+550-G`), GOK from `Ansatzpunkt …`/`… m ü. NN`/a lone height under the
  header, boundaries need the `Tiefe (Höhe)` label where the drawing uses it, the label convention from the position of
  the text, the water label (blue `3.10 (213.21)` or `GW 0.94m`, with date) wins over the symbol, the same Bohrung
  under two codes is one Bohrung; Sondierungen: codes with a station uncut, value axis as one aligned row. Stress cases
  `s31`–`s36`, Sondierungen `s09`. BER (training): 0 → 79/80 Bohrungen, water 64/64, 0 false.
- Blind round 6 frozen (A20 Unterlage 20.1, before and after #54).
- Blind round 5 (docs/15 §8.8): four German reports with Sondierungen, predictions frozen before opening, ground truth
  for 200 Bohrungen and 109 Sondierungen (values not transcribed), `blind_test.py score` also scores frozen
  Sondierungen (strict by code and by page). Main findings: one false Bohrung from a project number, codes with a
  station not read, GOK and water 0.
- Sondierungen in the Homogenbereich Kennwerte (Issue #29): N10 (DPH) and q_c (CPT) assigned per Einheit by height
  at the Sondierung's Lage (`baugrundanalyse/sondierung_einheiten.py`); range, median, n and censored values shown
  next to the Ansprache at Kennwert 13 (Lagerungsdichte) or 11a/11b (bindig), as measured values, never classified;
  hints for values outside the model; two catalogue entries. `tests/test_sondierung_kennwerte.py`, docs/28 §6.1.
- Readiness view per project (Issue #35, A3): *Modell → Erweitert → Bewertbarkeit* shows what the project can assess
  (möglich / hinweisend / blockiert from the knowledge catalogue), what is missing and which test or document provides
  it; in the project state, `GET /api/projekt/{sig}/bereitschaft`, the AGSi manifest and report.
  `tests/test_bereitschaft_app.py`, one end-to-end check, docs/29 §8.3.
- Knowledge catalogue v0 and planner (Issue #34, A2 of GroundTwin Analysis): package `wissen` with a vocabulary of
  quantities (what provides each), 14 entries (existing rules and analyses as entries pointing to their code, plus the
  DAUB TBM pre-selection SLS/EPB as data), planner (möglich / hinweisend / blockiert, missing inputs, what each would
  unlock), computed dependency graph, PROV-style record in the manifest format. `tests/test_wissen.py`, docs/29 §8.2.
- Water lines in the Längsschnitt (Issue #26 part 2b, rule `ls_wasserlinien`, W6): reads HGW, MGW, MHGW, HHGW, zeHGW,
  MNGW, Bemessungswasserstand, Bauwasserstand and `GW <Datum>` polylines from calibrated vector Längsschnitte
  (NHN margin axis or borehole GOKs + `H 1:n`, optional station axis `0+100`, legend abbreviations, GOK and
  Schichtgrenze exclusion, ambiguity rejection with hints) into document `wasserstaende` (`quelle: "Laengsschnitt"` /
  `"Text+Laengsschnitt"`, contradiction hints, never in borehole groundwater or G5). Real corpus: `marl_251` p. 6
  `Bauwasserstand` `54.17–56.05 m NHN`, 0 false across all 13 real PDFs; synthetic generator
  `services/extractor/synth_laengsschnitt.py` (5 cases incl. 4 traps, 6/6 right, 0 false); stress `s29`–`s30`;
  `tests/test_wasserlinien_laengsschnitt.py`; docs/03 §6, docs/06 §4, docs/16 W6, docs/17 E7.6.
- Information package v0 (Issue #33, A1 of GroundTwin Analysis): export `agsi` (Modell → Erweitert) with AGSi 1.0.1
  (Einheiten, Homogenbereiche per ATV, Bohrungen as observations, Laborwerte as property summaries), manifest (value
  kind and source per value, completeness, open items, Kreuzprobe), report, IFC and BoreholeML; valid against the
  official AGSi JSON Schema; ids and references checked by the exporter. `services/geodaten/geodaten/agsi.py`,
  `tests/test_agsi.py`, docs/29 §8.1.
- Sondierungen as optional support points for the layer model (Issue #28, default OFF `sondierungen_stuetzpunkte=False`):
  changepoint detection on DPH `N10` and CPT `q_c` (`services/analyse/baugrundanalyse/sondierung.py`), unambiguous unit
  assignment against the baseline model without guessing a Bodenart, leak-free leave-one-out Kreuzprobe, synthetic ground
  truth cases (`eben`, `geneigt`, `rinne`, `cpt_rinne`, `linse`, `ohne_sprung`) and distance study (`docs/27 §6.8`,
  `docs/16` M43). Cuts Rinne base MAE by 24–34 % with 0 false boundaries; keeps Bohrung contacts exact, solids closed and
  IFC 4.3 valid in METRE; tests `services/analyse/tests/test_sondierung.py`.
- GroundTwin Analysis schemas (D108 accepted, Issue #32): `services/wissen/schemas/katalog_eintrag.schema.json` (one
  catalogue entry: kind, authority, verified source, inputs/outputs, validity, uncertainty, `when_missing`, tests) and
  `manifest.schema.json` (value kind and provenance per AGSi object; a characteristic value only with the engineer who
  entered it, a derived value only with its catalogue entry); tests `tests/test_wissen_schemas.py`.

### Changed
- Dienste der Länder (Issue #19): 30 of the 38 portal links checked live and marked *geprueft* with licence,
  attribution and a machine-checkable proof (`beleg`); 8 stay *ungeprueft* with their reason (Saarland, Sachsen-Anhalt
  outage, Thüringen captcha). docs/26 §4.
- Extraction word order within a line independent of PyMuPDF version (Issue #49, rule `line_reading_order`, E9):
  words of a `(block, line)` in `prototyp_v4.py`, `sondierungen.py` and `prototyp_v2.py` are ordered by MuPDF's
  `word_no` (reading direction, fallback main axis) instead of `(y0, x0)`, and `_gw_text_am` / Schichtenverzeichnis
  `a)` names cluster lines with `rows(..., dy=3.0)` instead of `round(y0)`. Identical scores across PyMuPDF 2.0 and
  2.1 (`real/rednitzhembach` 4/4 Bohrungen, 15/15 Grenzen, 0 false); new stress case `s28_zeile_grundlinie` and jitter
  tests `tests/test_zeilen_leserichtung.py`; `requirements-server.txt` sets `PyMuPDF>=2.0`.
- Homogenbereiche matrix checked against the ATV full text (Issue #17): DIN 18301:2023-09 no longer asks for
  Kohäsion (removed); DIN 18304, 18311, 18324 (2019-09) equal; DIN 18302 has no Homogenbereiche. Field `geprueft`
  per ATV, test `test_matrix_gegen_volltext_der_atv`, docs/28 §10a.
- Decisions D100–D109 accepted (Issues #24, #32).
- Homogenbereiche proposal (Issue #21, user decision): Hangschutt and Wiesenkalk always get a Bereich of their own,
  never *bindig*.

### Added (earlier)
- Water levels in scans (Issue #40, by Antigravity, checked by Claude): depth scale from an OCR depth/elevation ruler
  or `M 1:n` + GOK when interior lines vanish (rule `raster_massstab_ocr`, E8; a ruler contradicting the labels is
  rejected and marked), and water levels read cell by cell from scanned Schichtenverzeichnis pages (rule `sv_wasser`,
  W5). raster150 GW 6/18 → 13/18, 0 false; regression real/stress/synth without regression; stress s24–s27.
- Sondierungen in BoreholeML (Issue #27 part 4): reviewed Sondierungen with values, UTM Lage and GOK as `bml:Borehole`
  with the curve as `bml:investigation` (type SM, parameter SON, CSV `valueMatrix`, censored steps `>`), DPU for CPT;
  valid against the official XSD; the import reads them back as Sondierungen with their Lage (docs/05 §8).
- Sondierungen in the IFC (Issue #27 part 3): `IfcBorehole` with `ObjectType` `Sondierung DPH/CPT`, a slim column
  at its Lage, `CPset_Sondierung`, `CPset_Herkunft` and the curve as `IfcPropertyTableValue` (N10, q_c, f_s); those
  without Lage or GOK stay out and are named in step *Modell*; the viewer counts them apart (docs/05 §7).
- Sondierungen in the project and the app (Issue #27 part 2): extracted with every PDF, listed in step *Bohrungen*
  with their curve (DPH steps, CPT q_c/f_s) and the PDF page; reviewed / removed, GOK from the PDF or entered, Lage
  entered or set on the locked Lageplan, ▼ markers in the Lage editor; `GET /api/projekt/{sig}/sondierung/{sid}`
  (docs/05 §6).
- Sondierungen (DPH/DPL/DPM/DPSH, CPT/CPTu) read from real Gutachten as a stage of its own
  (`services/extractor/sondierungen.py`): tables, vector diagrams, Längsschnitte, diagrams over two pages, censored
  values, scans withheld when unsure; measuring tool `benchmark/sondierungen_eval.py` with ground truth of 32
  Sondierungen and a baseline; on the training PDFs 1281/1564 DPH steps with 0 false values (Issue #27 part 1, docs/05 §5).
- House rules as tests (`tests/test_hausregeln.py`): layers of the code, network only through `netz.py`, nothing
  swallowed silently, no third-party PDFs, ground truth with sha256, no secrets or model ids, no `_char`, and the
  baseline bound to the hash of `prototyp_v4.py` (`regression.py --write` writes `baseline_v4.modul.json`) (docs/31).
- Feature map `docs/feature_map.json` with a proof per function, checked against every API route and project
  operation (`tests/test_funktionskarte.py`); CI fails when `apps/web/dist` does not match the source; commands
  `/regel` and `/verifizieren` for agents (docs/31, D109).
- Water level tables in the report (Aufschluss | Wasserstand m u. GOK | Wasserart): kind from footnote, column or the
  sentence on the table, merged into the levels of the Bohrungen with evidence (Issue #26, docs/06 §4).
- Scanned report pages are read by OCR in the Kennwerte, laboratory and Homogenbereich stages; results carry
  `quelle: OCR` and a hint (Issue #18, docs/28 §10b).
- Laboratory sheets of the annexes (Wassergehalt, Zustandsgrenzen, Korngröße, Glühverlust, CBR, Proctor …) read per
  sample, attached to the Schicht of their Bohrung, summarised per Einheit (n, min, max, mean), filling the Kennwerte
  of the ATV as "Labor:" and written to the IFC as `CPset_Laborwerte` (Issue #18, docs/28 §9b).
- Bodenkennwerte rows given as height ranges (`GOK bis +32,0` m NHN) are proposed for the Einheit whose thickness
  lies mostly in that range; close splits are left for the user (Issue #18, docs/28 §9).
- Homogenbereiche the Gutachter defines (table, section or sentence) read from the report; the proposal per ATV starts
  from them, assigns the Einheiten by name, Bodenart and Bodengruppe, and lists the differences (Einheiten without a
  Bereich, Bereiche without an Einheit); a click takes it over (Issue #21, docs/28 §10).
- Bodenkennwerte from the report tables (Wichte, Reibungswinkel, Kohäsion, Steifemodul …; table or list per Schicht)
  read by a separate extraction stage, assigned to the Einheiten by a proposal and a click (step Einheiten), written
  to the IFC as `CPset_Bodenkennwerte_Gutachten` with `<Kennwert>_min/_max`; never a characteristic value of our own
  (Issue #18, docs/28 §9).
- Grundwasser: kind (angetroffen, Ruhewasser, nach Bohrende, Schichtenwasser, or not stated) and date of each level
  from the text at the symbol and the Schichtenverzeichnis; Bemessungswasserstand, HGW, MHGW from the report text.
  The Grundwasserfläche prefers Ruhewasser, keeps Schichtenwasser out and names mixed kinds and days; kind and date
  go to the IFC (`CPset_Grundwasser`) and to BoreholeML (`bml:Groundwater`). A kind the Gutachten does not state stays
  open (Issue #26, docs/06 §4).
- Homogenbereiche: what the layer descriptions say about the Kennwerte an ATV asks for (Konsistenz, Bodengruppe,
  Lagerungsdichte …), per Bereich with the share of Schichten, in the app and the IFC; laboratory values stay open
  (docs/28 §6). Ground Analysis warns when the Lage is only schematic (docs/28 §7).
- Geological Benennungen of DIN 4023 Tabelle 3 recognised in descriptions: Hangschutt, Wiesenkalk (Seekalk,
  Seekreide, Kalkmudde), Bänderton, Kreidestein, Kalktuff (docs/28 §8).
- **Homogenbereiche (VOB/C)** (docs/28): Einheiten per Gewerk (ATV) to Homogenbereiche in the step
  Einheiten, with the Kennwerte each ATV asks for; IFC Pset `CPset_Homogenbereich_<ATV>` on Einheiten and Bodenschichten,
  and a model of Homogenbereiche only. A proposal per Anwendungsfall merges Einheiten that behave alike for the
  chosen ATV (how fine follows from its Kennwerte), with a reason per Bereich, applied on a click.
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
  Geschiebemergel violettblau, Löß oliv), replacing display choices (docs/28 §8).
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
