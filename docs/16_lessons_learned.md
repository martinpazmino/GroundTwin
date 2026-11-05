---
title: "Lessons learned (project memory)"
date: 2026-10-26
tags: [lessons, memory, extraction, validation]
aliases: [Lessons learned, Lessons, Memory]
---

# Lessons learned (project memory)

**What this note is for:** everything learned, written as **explicit rules** that any person (or
agent) must respect when touching the extraction. Each rule says what to do, why (evidence) and
which test watches it. If a rule stops being met, a test must turn red.

**Goal of the project (do not lose sight of it):** from a Bodengutachten in PDF, build the
**Baugrundmodell**: validated, traceable Bohrung data → Supabase → IFC 4.3 geometry in That Open
Engine ([Architecture](ARCHITECTURE_BAUGRUNDMODELL.md)). The extraction is not the end: what
matters is that every value reaches the model **with its provenance and its confidence**, and that a
doubtful value stays **marked**, never hidden.

> [!IMPORTANT]
> Rules L1–L18 come from real PDFs ([15](15_results_real_pdfs.md)). The figures after each fix are
> training figures; the blind rounds gave **0/13** and **11/29**. A new rule is only accepted if it
> does not break the regression set (§P5).

## P. Process and measurement

| # | Rule | Why / evidence |
|---|---|---|
| P1 | **Measure blind before fixing.** Freeze the predictions for every new PDF before opening it | v3 got 29/29 in training and **0/13** in the first blind round ([15 §6](15_results_real_pdfs.md#6-blind-test-hausham-and-rednitzhembach)) |
| P2 | **Push the frozen predictions to the repo** (with the `sha256` of the PDF and the code revision) **before** transcribing the ground truth | The git history proves the order; round 3: `5325ead`/`2d4d5e7` → ground truth `acc5cd5` (D29) |
| P3 | Always separate **blind figures** from **training figures** in every report | Avoids fooling ourselves (D24) |
| P4 | The main metric is the **silent error**: a wrong value marked as certain. A false Bohrung is worse than one not found | v1 marked wrong Bodenarten green ([01](01_diagnosis_fixed_layout.md)); swissgeol invented 55 Bohrungen in 9 PDFs |
| P5 | **Every change is measured against the full set** (real PDFs + synthetic) before it is pushed | A rule from round 3 broke B 4 of Rednitzhembach and only the regression set caught it |
| P6 | A new rule must be **general** (describe a feature of the drawing), never an exception for a PDF, an office or a coordinate | The fixed positions of v1 are the root cause of its 0/58 |
| P7 | The ground truth is transcribed **from the image** and checked against a second source (Schichtenverzeichnis, report) when there is one | The Schichtenverzeichnis confirmed 14/14 transcribed Bohrungen |
| P8 | The PDFs are **not** pushed to the repo; only URL, `sha256` and factual data | Internal use of other people's work (D16, D23) |
| P9 | **Perturb the PDFs that already work** (rotate, scale, rasterise) with the same ground truth: it finds failures the originals hide | Rotating Wesel revealed that the Schichtenverzeichnis reader used unrotated coordinates |
| P10 | **Ablation**: switch off each rule and see which case gets worse. A rule whose removal makes nothing worse is not protected by any test | [`ablation.py`](../benchmark/ablation.py): 22 of 28 rules protected ([table](../benchmark/ablation_v4.md)) |
| P11 | **One stress case per lesson**: the real failure becomes a minimal PDF that reproduces it. Writing the case for an unprotected rule often uncovers a new failure | [`stress_cases.py`](../services/extractor/stress_cases.py), 17 cases; s15 uncovered the L14 failure |
| P12 | Also measure **precision to the centimetre** (exact boundaries), not only the 5 cm tolerance | v3 414/515 exact, v4 509/515 after T2 |
| P13 | **A new input on a page can break the end-to-end test** (Playwright strict mode): a second `.datei-knopf input` or `select.epsg` made two locators ambiguous. Give every input a unique accessible name (`aria-label`) and scope locators to their section; run `check_app.mjs` after every UI change | DGM section in the *Lage* step, 2026-11-02 |
| P14 | **An expected 4xx in the end-to-end test goes through `page.request`**, not `fetch` in the page: the browser logs a failed request as a console error and the run fails on "Seitenfehler" | BoreholeML check in section D, 2026-11-02 |
| P15 | **Codes of another vocabulary are mapped by their official names, never by matching abbreviations**: `Ko` is coal in the BoreholeML RockNameList but conglomerate in DIN 4023; Auffüllung, Löss or Mudde are genesis, not petrography. A generator reads the official lists and stops on a missing or ambiguous name | `services/geodaten/werkzeuge/boreholeml_codes.py` |
| P16 | **A green check is not a right picture: look at the screenshots.** All 42 end-to-end checks passed while the screenshot of the Standort model showed only the grid (the camera stood inside the model), and later the one with the LoD2 buildings showed a wall. A check that only reads states (`reifegrad`, counts) cannot see that; now three checks project the corners of the hull into the image and require the camera outside the model | `scripts/check_app.mjs` (`huelleImBild`, B5 and F) |
| P17 | **After each phase, a round of edge cases and a second end-to-end run**: the happy path was green while a project name with "–" or "✓" broke every export, the "/" in the label of a Standort became a path when resetting, a second Standort on the same point silently renamed the first, a zone prefix put imported Bohrungen 32,000 km away, and a second e2e run on the same server failed. Cases: a Land without services, BW, zone prefix, special characters, reset, the same input twice, a rerun | test round 2026-11-03: 5 new tests in `test_standort_app.py`, `test_server.py`, `test_bohrdaten_app.py`; e2e rerunnable |
| P18 | **The Land's data never goes back to the Land as the user's own.** An export to an authority takes only what this investigation produced: BoreholeML skips `herkunft = SGD`, and the GeolDG package is refused for a project without own Bohrungen. The UI hid the button, but the API built a package whose "Bewertungsdaten" were a Vorerkundung model of the Länder's Bohrungen | Edge-case round 2026-11-04, `test_app_standort_ohne_eigene_bohrung` |
| P19 | **Rules from a law: each with its § and link, read from the official text, and the app says it is a help.** `geoldg.json` holds every deadline, item and hint with the paragraph and the URL on gesetze-im-internet.de; a passed deadline reads *verstrichen* (the app cannot know whether it was met); calendar months end on the same day or the last day of a shorter month (as § 188 BGB: 30 November + 3 months = 28 February, 30 November 2027 + 3 = 29 February 2028). A mutation of a rule (14 → 15 days, a marked Lage counted as proven, the Länder's Bohrungen counted as own) turns the tests red | `tests/test_geoldg.py` (`test_monatsfrist`, mutation check 2026-11-04) |
| P20 | **What the user cannot use must say why, where it is shown.** The list of the Bohrungen der Länder explained the limit only next to the import button, which appears only when something can be imported: in Berlin it showed 38 rows with *Profil ↗* and no reason, and the user asked why they were "not allowed". Now a line counts the rows that cannot be taken over, per Land and reason (header only with the profile as an image, no Schichtenverzeichnis, no petrography) | User report 2026-11-04; `check_app.mjs` B3 |
| P21 | **Every function makes the screen heavier; fold, do not delete.** A manager found the app overloaded after six phases of open data: model from a Standort, DGM, buildings, Cesium and GeolDG sat next to the use case (show a Gutachten and check it). Each step now shows the use case and folds the rest under *Erweitert*, which opens by itself once it holds data (a loaded DGM, a setting off the default, GeolDG dates). Ask after each phase what the first use case still needs on the screen | Feedback 2026-11-05; D99; `check_app.mjs` (folded parts, two paths) |

## E. Input: what kind of PDF it is

| # | Rule | Evidence |
|---|---|---|
| L1 | Do not assume rectangles or fills: **reduce everything to segments** | Ghostscript/PDF24 left Wachenroth as 965 loose segments |
| L2 | **Normalise the rotation** (`page.rotation_matrix`) of words and paths before any geometry | Talheim (`/Rotate 90`), Marl p. 19, Wesel p. 17 (`/Rotate 270`) |
| L11 | **Scan = same logic**: segments from the image (OpenCV) and text from the OCR layer | Rednitzhembach 4/4 after the raster adapter |
| L17 | **AutoCAD with SHX fonts**: the text of the drawing is lines; there is no text layer even though it is vector. Detect it (many paths, almost no words) and send it through OCR | Wesel p. 17: 1389 paths, 18 loose "words" |
| L18 | **Raster without a text layer** (portal screenshots, archive scans): our own OCR is needed | Berlin: 11 Bohrungen in images; OCR (RapidOCR) reads depths and elevations with confidence 0.6–0.9 |
| E1 | Classify every page **before** extracting: vector+text · vector without text (SHX) · raster+OCR · raster without text | All four classes appeared in 9 Gutachten |
| E2 | A scan can carry **vector noise** (hundreds of paths from the OCR software): with an image > 80 % it is still a scan, and both image **and** vector segments are used | Swiss KB5: 220 paths |
| E3 | **Every module takes its primitives from the same normalised layer** (E1); never `page.get_text()` directly | The SV reader failed on rotated pages because it skipped the rotation |
| L18b | The OCR layer of a scan **loses text** ("2 / I", labels of B 4): complement it with our own OCR where there are no words | A7367, Rednitzhembach |
| E4 | OCR reads the Schraffur of Kies (circles) as `000`: do not count those tokens as text | Case s12 |
| E5 | The page size of a scan (or of a reduced printed PDF) is **not** that of the paper: the `M 1:100` in the title block does not give the scale in PDF points; the labels decide. If the title block contradicts them, the Bohrung comes out **without Schichten** and with a warning | KB5; perturbation at 70 %: false boundaries 57 → 2 |
| E7 | In raster, a column drawn only with **colour fills without an outline** gives no dark lines: edges between colours (gradient) have to be detected, not only a black threshold | Raster perturbation of Hausham (DC-Software) |
| E6 | OCR **loses spaces** (`KeinWasser`, `RKS 1-Betonweg`, `GW2.53m`, `36,25mNHN`): every text pattern must accept optional spaces and must not depend on `\b` between a letter and a digit | Raster perturbation: GW status 3/20 |

## G. Geometry: column and boundaries

| # | Rule | Evidence |
|---|---|---|
| G1 | Column = **pair of stroked verticals**, width 8–80 pt, height ≥ 2.5 × width | Works in 7 different offices |
| G2 | Boundary = **continuous** (not dashed) horizontal that touches **both edges** (±0.6 pt; scan ±1.6 pt) | L6: the Schraffur of Ton and the double line of Schwarzdecke crossed the column |
| G3 | Nested columns (inner strip, GWM pipe): keep the one with the **thickest edges** | Talheim GWM |
| G4 | A column with numbers inside is a **table**, not a Bohrung | L5: table "B 6" of Wachenroth at M 1:12 |
| G5 | Every boundary must be **confirmed 1:1 by a label**; otherwise it is marked (not deleted) | Talheim BK5: 1 extra boundary marked |

## T. Labels, scale and headers

| # | Rule | Evidence |
|---|---|---|
| L3 | The **position** of the label is not reliable (offset, above, below); some offices label the **top** (with 0.00), others the **base**. The scale is chosen by **how many labels** each candidate confirms (direct, by order, text `1:75`) | Talheim 65/65 |
| L8 | Labels with the unit attached (`0.20m`), decimal comma or point | Hausham (DC-Software) |
| L9 | Non-normalised scales exist (log fitted to the sheet, M ≈ 1:35; Triefenstein 1:30): valid if ≥ 80 % of ≥ 3 labels confirm them | Hausham RKS, Triefenstein |
| L14 | A group of values in **arithmetic progression** is an **axis** (elevation ruler, scale of a DPH diagram), not Schicht labels, **if** it has a round step (0.1 · 0.25 · 0.3 · 0.5 · 1 m…) and ≥ 8 values, or more values than the column has boundaries. Schichten of equal thickness (0.4 · 0.8 · 1.2…) are still labels | Marl BS 10 (DPH axis); case s15 (the first version of the rule deleted real labels) |
| L15 | A column of values **in pairs** (Von/Bis of samples) are not Schicht labels | Marl (IDAT/GeoDin) |
| L15b | A column without any confirmed label while the neighbouring ones have them → it is not a log (e.g. GWM construction drawing). If **no** column on the page has labels (OCR lost), the title-block scale is accepted and marked | Marl GWM 10; Rednitzhembach B 4 |
| L4 | In the height representation the header sits far above the column: associate the header with the column **below** it, without a vertical limit | Wachenroth section, Talheim |
| L13 | The header can carry a **suffix**: `RKS 1 - Betonweg 0+050`, `B 1 Bohrung Nr.` | Triefenstein 0/5 because of this |
| T1 | Third-party codes do not follow the `B 1` pattern: `422C-460`, `B 7/16`, `S 2a`, `DS 1/17`. The prefix list must be **configurable** and extended from the legend and the Lageplan of the document itself | Berlin |
| L12 | The same Bohrung appears on its own sheet and in the section: prefer the **titled sheet** with fewer Bohrungen; a confirmation < 50 % does not count | Wachenroth B 2, Rednitzhembach B 4 |
| T2 | A boundary confirmed by a label is delivered with the **printed value** (3.50), not the geometry (3.49) | Exact precision 414 → 509 of 515 |
| T3 | Sheet with **a single header**: it is anchored to the column with the most labels even if the header is far away (forms with a centred header) | KB5 |
| T4 | If the lines do not fit but the labels form a **clean straight line** with a normalised scale: the boundaries are the labels, the lines only confirm | KB5 (raster Schraffur creates extra lines) |
| T5 | A column with ≥ 3 depths **inside** it is the depth column of the form, not the log | KB5 |

## B. Text and Bodenart

| # | Rule | Evidence |
|---|---|---|
| L7 | Classify by the main **noun**, not by substrings: `Sandstein` is rock, `Tonstein` rock, `Beton`/`Schwarzdecke` man-made, `Oberboden` = Mutterboden | v1: Sandstein→Sand, Beton→Ton marked "certain" |
| L16 | If there is no noun, use the DIN 4023 / EN ISO 14688 **abbreviation** at the start (`U, t, s´` → Schluff; `fS` → Sand; `A (S, u´)` → Auffüllung; `Gr`, `Sa`, `Si`, `Cl`) | Triefenstein, Marl |
| B1 | The text can come with **leader lines** (not centred on the Schicht): assign it by the label convention or by the leader line, not only by `y` | Marl BS 10: 5 Schichten without Bodenart |
| B2 | Always keep the **original text** next to the class | Traceability (model §5.1) |
| B3 | Read the description **by norm** with evidence per value (DIN 4023 / ISO 14688-1 / DIN 18196 / practice / colour only): prepare the text (decimal comma ≠ separator, joined words `FeinsandbisMittelsand`, apostrophes and overlines), main = first noun or Kurzzeichen, *Auffüllung*/*Mutterboden*/geological name + soil = material; foreign materials by **word start** (`Toneisenstein` is not iron) | [21 §3](21_app_schritte_normen.md#3-mini-database-of-norms) |
| B4 | What the norm reads differently from the extraction is **marked**, not changed: "Sand/Auffullung" is fill (13 Schichten in Berlin); `Mg` is ambiguous (Geschiebemergel / made ground); the Bodengruppe only if it is written | Berlin, `test_normen.py` |

## W. Water

| # | Rule | Evidence |
|---|---|---|
| W1 | The triangle can sit next to the **neighbouring column**; the end of the **water line** assigns the Bohrung | Talheim |
| L10 | Not water: triangles in an aligned series (elevation ruler), a triangle with an elevation next to it, a triangle at the GOK | Hausham |
| L10b | Water also comes as **text**: `GW 2.53m`, `Wasserstand nach Sondierung 3,00 m`, `Wasseranschnitt 3.8`, "Ruhewasser" | Hausham, Triefenstein, Berlin |
| W2 | "kein Grundwasser", "trocken", "kein Wassereintritt" are **data**, not absences | Wachenroth 6/6, Wesel |
| W3 | Missing: symbols from the legend ("angebohrt" with two strokes) | Talheim BK2 (the only GW lost in training) |
| W4 | Missing: the **water symbol in raster** (▽ ▼ drawn in a scan); today it is only detected as vector or as text. Tried: OpenCV triangular contours find the Schraffur (146 false GW) and not the symbol, even when requiring a water line → rule switched off; next attempt: a template of the symbol taken from the legend | Raster perturbation: Hausham GW 4/4 → 0/4 |

## S. Second sources and cross-checks

| # | Rule | Evidence |
|---|---|---|
| S1 | The **Schichtenverzeichnis** (DIN 4022 form) is the most stable source: depth in column 1, name under `a)`, water in column 3. **Always** read it and compare it 1:1 with the log | Hausham 9/9 and Triefenstein 5/5 "SV ok"; Wesel 24/24 only from there (D30) |
| S2 | Read numbers from tables **per cell** with their words and bbox, never from flattened text | `565 081,64` came out as `"56508164\n,"` ([07](07_coordinates.md)) |
| S3 | The title of a form can be **spaced out** (`S c h i c h t e n v e r z e i c h n i s`) and the text **duplicated** (two layers): normalise before searching | Wesel |
| S4 | Rammsondierungen can come as a **table of values** (N10 every 10 cm) instead of a curve | Triefenstein pp. 32–35 |
| S5 | Coordinates appear in tables, in portal title blocks (`Rechtswert (UTM 33N): 394774,3`) or in the Lageplan; without them there is no real 3D | Berlin (in an image), Halle (GW table 26/26) |
| S6 | The log can be **only a text table** (Tiefe \| Beschreibung) without a graphic column; accept it only if ≥ 60 % of the intervals give a Bodenart (DPH and lab tables do not) | A7367 (Switzerland) |
| S8 | A **scanned** Schichtenverzeichnis is read the same way through OCR if the reader uses the common primitives: OCR glues the marker to the text (`a)Auffullung`), drops umlauts (`Auffullung`) and spaces (`B1` on one page, `B 1` on another): compare **normalised** codes and accept forms without umlauts | Raster perturbation: Triefenstein 0/5 → 5/5, Wesel 0/24 → 24/24 |
| S7 | Label and value in the title block can be **separate blocks** on the same row (`Höhe in m ü.M.:` · `668.99`): join by row before searching | A7367 |
| S9 | The **services of the Länder deliver differently**: Berlin and Brandenburg only header data and the Schichtenverzeichnis as an image; NRW and Baden-Württemberg BoreholeML 3.0 (old namespace `infogeo.de`), in Baden-Württemberg often without petrography. Mark what is missing (*Schichten ohne Petrographie*), never guess | Queries of 2026-11-02 |
| S10 | **Do not trust the metadata of a service blindly**: the NRW BoreholeML WFS announces an area in Lower Saxony and puts the CRS only on the envelope of the collection (`gml:Point` without `srsName`), and errors come as an `ExceptionReport` with HTTP 200. Take the area from a second source (OGC API) and inherit the CRS as GML says | `dienste.json`, `boreholeml.importieren` |
| S11 | **A Bohrung of the Gutachten is often already at the Land**: names, Lage and GOK of the Berlin example match the state database (≤ 0.05 m). Such a match is an independent check of the calibration, and it shows that archive Bohrungen of a Gutachten come from there | Gegenprobe in the *Lage* step |
| S12 | **Check what a coverage really delivers before trusting it**: the DescribeCoverage of the Baden-Württemberg DGM1 WCS announces a range of 0–255, and GetCoverage gives 16-bit whole metres, resampled to the requested box (pixel 1.005 m). Brandenburg and NRW give float32 on the exact 1 m grid. One test cut-out per service, read with the real reader, decides | `dienste.json` (`geprueft_nicht_aufgenommen`) |
| S13 | **WCS 2.0.1 (MapServer) of the Länder**: SUBSET with the axis labels of the coverage (`x`, `y`), bounds on whole metres give whole cells (pixel centres at .5), SCALEFACTOR coarsens large cut-outs, a box outside gives HTTP 400 with an ExceptionReport and a box inside the envelope but outside the Land gives only NoData | `dgm_dienst.py` |
| S14 | **LoD2 of the Länder comes the same way, the OGC API does not**: Berlin (ATOM), Brandenburg and NRW (open data portals) publish CityGML tiles of 1 × 1 km in the AdV profile, ETRS89/UTM + DHHN2016 (`urn:adv:crs:ETRS89_UTM33*DE_DHHN2016_NH`). The NRW OGC API for 3D buildings answers `crs` and `bbox-crs` with HTTP 400 and gives ellipsoidal heights in CRS84h. Use the tiles: one reader for three Länder | `dienste.json`, `gebaeude.py` |
| S15 | **The ground of a LoD2 building is the lowest DGM point of its footprint**, not the mean: against the DGM1, the lowest point matches within cm (Berlin 97 %, Marl 100 % within 0.5 m), the mean differs by metres on slopes. Compare like with like before calling a height wrong | P4 acceptance check |
| S16 | **A model from a point needs released Schichtdaten**: Berlin and Brandenburg publish only the header of their Bohrungen (with a profile image), NRW and Baden-Württemberg the Schichten as BoreholeML. Check what a service releases before choosing the site of an acceptance test: the P5 acceptance planned in Berlin moved to Marl (NRW), 11 Bohrungen within 250 m | [23 §5](23_open_data_integration.md#5-intervention-plan), D94 |
| S17 | **The same Lage in two forms: UTM with and without zone prefix** (EPSG 4647 / 25832, 5650 / 25833). Gutachten in NRW often write the prefix, the services of the Länder never do. Convert imported Bohrungen into the system of the project, compare the Gegenprobe in one system, carry DGM and buildings into the system of a Gutachten added to a Standort; another zone stays as it is and is marked (GOK check *anderes System*, a hint at the buildings) | `geodaten/utm.py`, `Arbeitsplatz._ins_system`, `test_standort_mit_zonenkennung_und_gutachten_ohne` |
| S18 | **UTM values alone do not place a point in Germany.** The ranges 150–850 km east and 5,200–6,150 km north hold in every zone: a point in Paris in zone 31 passed the check of the Standort. Check the zone (32 or 33) and the longitude/latitude after converting back | `Arbeitsplatz._in_deutschland`, `test_standort_in_einer_anderen_zone_abgelehnt` |
| S19 | **The profile images of Berlin (GeODin portal) answered an HTML error page from the cloud session**, for the URL the WFS gives (`getimage … LAYOUT=5 … IMAGETYPE=JPG`): reading the Schichten from them could not be tested here. Check such a source from the user's machine before building on it | 2026-11-04 |
| S20 | **The area of a service is not the area of its Land.** Rectangles of the services overlap: Berlin also asked Brandenburg (which has no Bohrungen there), the LoD2 fallback took a Berlin tile from Brandenburg in the test only, and a click in Saxony-Anhalt listed Brandenburg. The Land from its borders (VG2500, 150 m) fixes it; at a border ask both (centre plus a radius), the Land of the centre first | `tests/test_bohrdaten.py`, `tests/test_gebaeude.py` (border cut-out Berlin/Brandenburg) |
| S21 | **No data service is not no data.** 12 of 16 Länder offer their Bohrungen only in a viewer or on request; "0 Bohrungen" hid that. Name the portal as a link and mark it *ungeprüft* while nobody tested it | D98 |

## R. swissgeol: what to copy and what not

| # | Rule | Evidence |
|---|---|---|
| R1 | Copy its **tolerance of formats** in labels (units, OCR, positions) and the exclusion of arithmetic progressions | swissgeol 13/13 in blind round 2 where v3 got 0 |
| R2 | Do not copy its assignment of Bohrungen without geometric validation: it produces **many false ones** and does not read German elevations | 55 false Bohrungen and 6/50 GOK in 9 PDFs |
| R3 | AGPL license (like PyMuPDF): internal use without problems; for third parties, our own primitives layer (D17, D18) | [14](14_licensing.md) |

## M. Model, IFC and That Open

| # | Rule | Evidence |
|---|---|---|
| M1 | IFC 4.3: `IfcBorehole` ⊃ `IfcGeotechnicalStratum`; model in `IfcGeomodel`; georeferencing with `IfcMapConversion` + `IfcProjectedCRS` | Spike validated without schema errors |
| M2 | That Open's `IfcImporter` **discards** the geotechnical classes by default: add `IFCBOREHOLE`, `IFCGEOMODEL`, `IFCGEOTECHNICALSTRATUM` to `importer.classes.elements` | 0 → 16 elements with geometry |
| M3 | Encapsulate the IFC writer: IFC 4.4 replaces `IfcGeotechnicalStratum` with `IfcGeoScienceFeature` | 4.4 draft |
| M4 | Without coordinates, the section model (station, NHN) already adds value; with local coordinates from the Lageplan a relative 3D can be built | [Architecture §7.1](ARCHITECTURE_BAUGRUNDMODELL.md#71-ladder-of-levels-each-one-is-deliverable) |
| M5 | An **empty Pset** is invalid IFC: create the Pset only if there are values | Exporter: 5 schema errors → 0 |
| M6 | PostGIS installed in `extensions`: **qualify** `extensions.geometry`, otherwise the migration only works inside Supabase | [`supabase/`](../supabase/README.md) |
| M7 | The full chain already works with a real PDF: OCR → canonical JSON → PostGIS → georeferenced IFC 4.3 → That Open (80 strata) | Berlin ([15 §8](15_results_real_pdfs.md)) |
| M8 | **Below the Endteufe is unknown, not absent**: treating it as absence pinches out the deep Einheiten at every short Bohrung | Case `zensiert`, Berlin ([18](18_layer_modeler.md)) |
| M9 | The same Bodenart at another elevation is **another Einheit** (Sand 1 / Sand 2): correlate by class **and** elevation, not only by name | Berlin 422C-461: two levels of Kies |
| M10 | A lens missing inside a continuous Abschnitt: the boundary is **free** inside the Abschnitt; place it at the interpolated middle of the lens, not at a Schicht boundary | Case `linse`, Berlin 422C-460 |
| M11 | Bohrungen as mesh **nodes** + exact interpolator ⇒ the model reproduces every contact (always check it: maximum deviation in the report) | 0.0 m in all cases |
| M12 | IDW only reaches 0 at the Bohrungen themselves: an Einheit seen in one Bohrung spreads thinly under the whole site. Limit the extent (presence indicator) | Lens volume ×6.3 → ×1.9 |
| M13 | Thickness thresholds on the **surfaces**, not only on the mesh: otherwise the volume of the IFC and that of the model differ | The volume test caught it (5 m³) |
| M14 | Reading geology needs **vertical exaggeration** (site 150 m × 20 m); scale `model.object` in y around the base: the Fragments raycast uses `matrixWorld` and keeps working. Transparency with `depthWrite: false` | Viewer screenshots |
| M15 | With relief (Talheim: GOK 749–772 m) correlation by absolute elevation splits one shallow Schicht into several Einheiten: also compare the **depth below GOK** and keep the smaller distance | 15 → 6 Einheiten ([19](19_app_v2.md)) |
| M16 | A model without coordinates is only honest as a **schematic**: say so in the app, in the IFC (`Lage`) and in the viewer (`Lagebezug`) | App v2 |
| M17 | `ifcopenshell.api.unit.assign_unit()` **without arguments sets millimetres**: with coordinates in metres the model comes out 1000× too small in any viewer and the `IfcMapConversion` is wrong. Explicit units and a `calculate_unit_scale == 1` test | The 6 km Trasse measured 6 m ([20 §2](20_lage_pruefung_viewer.md#2-moving-the-geometry-and-models-over-5-km)) |
| M18 | That Open camera: perspective near 1 / far 1000, orthographic 0.1 / 1000 at 200 m from the target: **everything > 1 km disappears**. Recompute near/far on every move from the scene size (orthographic: negative near) | Trasse: far 24.6 km, near 0.02 m up close |
| M19 | An IFC that is already local to the project origin is loaded **without `COORDINATE_TO_ORIGIN`** (web-ifc shifts it by default): that way IFC and scene share coordinates. For IFCs with large global coordinates it must stay on | Pins = IFC to the cm |
| M20 | Calibrating a plan with 2 points: Lageplan = **similarity** (complex numbers, `q = u − i·v` because the rows go down); Längsschnitt = **separate scales** for station and height (the drawing's exaggeration is undone). Show the resulting scale and rotation so that the user spots a bad point | 1:500 / 10.0°; 1:500 / 1:100 |
| M21 | BUI 3.4: `Component.create` decides stateful/stateless by the **arity** of the template (`() =>` returns an element, not `[el, update]`); tooltips with `<bim-tooltip>` inside the button (`tooltip-title` is obsolete); `bim-label` cuts to one line (use `<p>`); `bim-dropdown` needs `.value` (it does not follow the `checked` of its options after the first render) | Errors and warnings at the first start |
| M22 | camera-controls applies `fitToSphere(…, false)` on the next `update()`: call `controls.update(0)` before measuring the scale of the view | The offset next to the panel went off screen |
| M23 | CSS: a child with `display:none` in a grid makes the next one take its column (0 px): set `grid-column`; and `[hidden]` loses against `display:grid/flex` (`[hidden]{display:none!important}`) | 0 px viewer when folding the panel; a loading notice that never went away |
| M24 | The ifcopenshell IFC carries **date and time in the header**: the same model gives another hash after a restart. As the model fingerprint (einchecken, caches) use the **key of its inputs**, not the bytes of the IFC | False *seitdem geändert* after restarting the app |
| M25 | Inside Streamlit the iframe measures **0 px** until `setFrameHeight` arrives: framing at that moment gives an aspect of 0/0 and `fitToSphere` leaves the camera at **NaN** with no way back (black viewer, hidden marks). Frame only with a size (ResizeObserver, pending framing) and repair a non-finite camera | Cold start of the app ([20](20_lage_pruefung_viewer.md)) |
| M26 | BUI: `bim-toolbar-section` sets the `label-hidden` of its buttons from its `vertical` when it mounts (and lit does not set it again if the value does not change): for an icon-only bar, use our own groups (`div`) inside `bim-toolbar` | Bar with labels despite `label-hidden` |
| M27 | A lit app with a persistent foreign component (the viewer): keep it in a fixed element of the template and **do not move it** to another parent (web components unmount and remount); show or hide it with CSS; with `display:none` the framing waits for a size (M25) | Viewer that does not reload between *Lage* and *Modell* |
| M28 | Calibrating with **scale (measured distance or 1:n) + reference point + rotation** is as exact as two control points and easier to check; locking the plan before dragging avoids moving Bohrungen by accident | 1:500 · 10.0° from the UI; D67 |
| M29 | That Open, `RendererMode.MANUAL`: with `turnOffOnManualMode` every `update()` draws **without** postproduction and 50 ms later **with** it. If something requests frames all the time (every mouse move, a 1 s interval) the image alternates forever: flicker. Decide the postproduction yourself (`turnOffOnManualMode = false`, `manualDefaultStyle` = style), right before drawing (`renderer.onBeforeUpdate`, after moving the camera), only on real activity (camera, loading, dragging); never in Lage mode; no redraw just for moving the mouse | Plan that flickered even when transparent; `check.mjs` B, `check_app.mjs` C2 |
| M30 | three.js `GTAOPass` sets `PERSPECTIVE_CAMERA` **only when created**: after switching to orthographic it keeps decoding the depth as perspective and, with the negative `near` of the orthographic camera (M18), gives false shadows or a **black viewer** depending on the GPU. Update the *define* (and `needsUpdate`) on every projection change | User's screenshot: black Lage with a valid HUD |
| M31 | 6–7 digit coordinates in the scene: the **origin** must be close to what is shown. Without Bohrungen with a position, the origin comes from the reference point of the calibrated plan; if the origin changes, the camera (and the saved view) moves by the same amount; if the plan jumps far away when its coordinate is typed, the camera follows it; the vertices of the plan are relative to its corner (Float32) | The first dropped Bohrung moved the origin and everything disappeared; empty preview |
| M32 | A pending "pick a point" blocked **all** dragging without a warning. When locking the plan, when starting to drag from the list or with the plan locked, cancel the pending pick | `check_app.mjs` C2 |
| M33 | EPSG never as a free number: a **list** (DE/AT/CH, codes and names verified with pyproj) and a **plausibility range** per system (digits, zone prefix); an unknown code from the PDF is shown marked, not hidden | "EPSG 52" in the HUD; R 74,848.90 → "fits no system" |
| M34 | Orthographic view with a negative `near`: `Raycaster.setFromCamera` starts the ray **at the camera plane**; what lies between `near` and the camera (e.g. the raised GOK of a Bohrung) is never hit. Move the origin to `near` in all our own rays; and draw the plan at the height of the Bohrungen, not at a fixed elevation | Bohrungen with a GOK could not be dragged, GWM without a GOK could |
| M35 | That Open `setOrthoCamera` derives the orthographic frame from the perspective camera (depth to the target) and `setOrthoPerspCameraAspect` scales it with the previous size of the viewer: without a placed camera or with the viewer still without a size it comes out **negative or huge** (image rotated by 180°, zoom stuck at `minZoom`). Normalise after every change of projection and of size | Calibration with «Drehung 180»; plan invisible when opened directly |
| M36 | **A terrain beside the model needs shared edge nodes, not a second surface**: a DGM sheet over the model would cover its top twice (flicker) and a cut-out hole leaves gaps. Rings along the outward normals of the model edge start at its edge nodes; the top pulled onto the GOK fades out before the edge, so model and terrain meet without a step | `umgebung.ring`, test `test_ifc_mit_gelaende_um_das_modell` |
| M37 | **That Open's orbit mode moves the camera**: `camera.set("Orbit")` sets `maxDistance = 300` and the distance to the target to the distance of the camera from the **origin of the scene**. After the *Lage* step every fit and every wheel turn stopped at 300 m (models over 300 m never fully in view), and with the camera far from the origin the target jumped millions of metres. Switch modes only through `KAMERA.modus`, which restores the camera and our limit | `kamera.ts`, `check_app.mjs` F |
| M38 | **A remembered view goes stale when the scene changes under it**: the view saved before *Lage* was the empty start view of a Standort (the model came later around the camera) or a view from before the LoD2 buildings (five times higher, the camera inside one). Remember only a view that showed something, drop it when the first model or the first buildings arrive, fit the first content of an empty scene, and put the origin of a Standort at its point so the first Bohrungen do not move it. Removing the model (reset) forgets all of it, including the Reifegrad band: a second e2e run caught a stale "model already seen" | `viewer.ts`, `projekt.ursprung`, `check_app.mjs` B5 and F |
| M39 | **Cesium needs ellipsoidal heights; GroundTwin has NHN.** h = H + ζ with the quasigeoid GCG2016 (34–51 m in Germany): without ζ the model lies under the globe. ETRS89 is fixed to Europe and drifts from ITRF/WGS84 by about 2.5 cm a year (about 0.9 m in 2026): not converted silently, stated in the tileset. Check heights in the real Cesium, not only in our maths: `sampleHeightMostDetailed` at three Bohrungen, against PROJ | `tiles3d.py`, `scripts/check_tiles3d.mjs` (within 1 mm) |
| M40 | **A GeoTIFF grid can be read without GDAL, if every TIFF option is honoured.** The GCG2016 of PROJ-data is tiled 256 × 256, Deflate, float32, PixelIsPoint, with the floating-point predictor 3 (per row: differences of bytes, then byte planes, big-endian): ignoring the predictor gives plausible-looking nonsense. Compare against PROJ at reference points (0.1 mm) and with a synthetic grid written by our own encoder | `quasigeoid.py`, `tests/test_tiles3d.py` |
| M41 | **Make sure the validator checks the content, not just the JSON.** The 3d-tiles-validator also runs the glTF validator on every GLB; a deliberately broken GLB must turn it red before a "0 errors" counts | P6a negative test |
| M42 | **The first content can come with its model.** The viewer showed the first Bohrungen of an empty scene whole — but only "without a model". After *verwerfen* and the same Bohrungen imported again, the model came from the cache at the same moment (hidden in the Lage editor), so the view stayed on the empty scene (camera inside, Bohrungen outside). In the Lage editor fit the first content whatever the model does. And a check must wait for "the model of the current state is in the viewer", not for "one more load": a cached model needs none. Found only by running the end-to-end check twice on the same server (it failed in the version before too) | `check_app.mjs` F, second run; `viewer.ts` `anwenden` |

## X. Working environment

| # | Rule | Evidence |
|---|---|---|
| X1 | In Claude's environment, downloading Gutachten from municipal websites is **blocked** (403/000); pypi and GitHub are not. The user uploads the PDFs | Rounds 1–3 |
| X2 | Test heavy dependencies (swissgeol, OCR) in **separate environments** in the scratchpad; swissgeol pins PyMuPDF 1.26.3 | `sgvenv` |
| X3 | `pkill -f pattern` in a command that contains that text anywhere **kills itself** (also with `[p]attern` if the name appears later in the same command): run `pkill` in a separate command | Exit 144 three times |
| X4 | `python -I` does not add the script's folder to `sys.path`: scripts must insert it themselves | `ablation.py` |
| X5 | `show_pdf_page` ignores the `/Rotate` of the source page; compensate when recomposing PDFs | First version of `perturb.py` |
| X6 | Expensive OCR → **cache per page image** (hash) so that regression and ablation are fast | `GEO_OCR_CACHE` |
| X7 | Every process that loads the OCR model takes several GB: 4 ablation processes in parallel **ran out of memory and restarted the container**. Load the model only on a cache miss and use ≤ 2 processes | Restart during the final ablation |
| X8 | The ablation reloads the module for every configuration: **do not edit the module while it runs** (versions would mix); test changes in a copy with another name | Final ablation |
| X9 | **web-ifc 0.0.78**: the browser `web-ifc.wasm` does not match its JS (`StreamMeshes called with 4 arguments, expected 3`); in Node it works. In the viewer, 0.0.77 | `apps/web` |
| X10 | That Open downloads WASM (`autoSetWasm`) and worker (`getWorker`) from unpkg by default: copy them to `public/vendor` (`npm run vendor`) to work offline and with pinned versions | `apps/web` |
| X11 | `vite preview` serves `dist/`: an IFC copied to `public/` after the build is not visible; the check copies the IFC to `dist/` | Screenshots with old volumes |
| X12 | Streamlit reloads modules when files change: rebuilding the viewer with the app running leaves it without its component (`dist/index.html` is missing for a moment). Restart the app after the build | Viewer not loading in the test |
| X13 | A new element above the component (e.g. the extraction's `st.status`) **re-mounts** it: new iframe, state reset. The tests detect the iframe change | `check_app.mjs` |
| X14 | Streamlit serves the component's files with `mimetypes`; on Windows the registry can give `text/plain` for `.js` and block modules/workers: register the types in the app | `ui/viewer.py` (precaution; not seen on Windows yet) |
| X15 | With SwiftShader (Chromium without a GPU) a frame with postproduction takes ~1 s: whatever is updated "every frame" (DOM marks, state) lags behind and same-origin iframes block the page. The tests wait for frames (`requestAnimationFrame` ×2) and read the state at that moment; on-demand rendering eases it | `check.mjs`, `check_app.mjs` |
| X16 | `vite build` **empties `dist/`** (including copied test IFCs); and the server answers a missing file with `index.html`: check the `content-type` before passing it to web-ifc | `OpenModel … reading 'arguments'` |
| X17 | The project autosave makes a repeated test start with the previous state: the app tests press *Alle Korrekturen verwerfen* (⋯ menu) when opening each project | `check_app.mjs` |
| X18 | Playwright: `page.mouse` uses window coordinates; an iframe below the fold has to be brought into view (e.g. a click on one of its elements) before dragging | Dragging without effect in the app |
| X19 | X3 also applies to `pgrep -f pattern \| xargs kill`: the command that contains it matches itself | Exit 144 |
| X20 | Keyboard shortcuts: ignore them only in text fields, **not** with the focus on a button (after pressing *Nächste* the focus stays on it and ↓ stopped working); close menus after an action | `check_app.mjs` A |
| X21 | Playwright: the value of an `<input>` is not part of the text of its row (`hasText` does not find it): find the index by `value` with `evaluate` | *Einheiten* test |
| X22 | A render error that only appears on the user's GPU (black, flicker) is not visible in SwiftShader: measure the **sequence of frames** (wrap `postproduction.update` and `three.render`) instead of looking at screenshots, and reproduce the exact case (here: no Bohrung with coordinates) | Reproduction of the user's screenshot |
| X23 | A Node `console.log` is lost if `timeout` kills the process with its output in a pipe: write to a file (`> log 2>&1`) | Reproduction scripts without output |
| X24 | **Realistic** test data: elevations of hundreds of m NHN, Bohrungen without a GOK, and the app also opened directly by URL. With 38 m NHN and always the same path through the steps, two camera errors passed all tests | `testplan.py` (GOK + 300 m), `check_app.mjs` C2/C3 |
| X25 | **Docker in the cloud session:** the daemon is not running (start `dockerd` in the background) and deb.debian.org is blocked (apt fails): build with `--build-arg OCR=0`, `--network host`, the session proxy's `HTTPS_PROXY` and its CA as a secret (`--secret id=ca,src=…` and `PIP_CERT=/run/secrets/ca` in a test Dockerfile). The CI tests the container's OCR. `check_app.mjs` logs in with `GEO_AGENT_PASSWORT` | Image 1.15 GB, 28/28 `check_app.mjs` against the container ([22](22_deployment.md)) |
| X26 | A `dockerd` started as a background shell stops when that shell's time limit runs out (30 min by default): start it with the longest limit and check `docker info` before building | Build failed with "no such file … docker.sock" halfway through |
| X27 | Generic environment variable names collide with the system: tcsh sets `HOST` to the machine name, which would have put the server on the network. Use app-specific names (`GEO_AGENT_HOST`); `PORT` stays because the platforms set it | Review of `server/__main__.py` |
| X28 | Local health checks with `urllib` must bypass the proxy (`ProxyHandler({})`): a company proxy from `HTTP_PROXY` does not know this machine's 127.0.0.1 | `scripts/online.py` |
| X29 | The repository was renamed twice (CAD_Extract → GeoIM → GroundTwin). `git push` keeps working through GitHub's redirect and prints "This repository moved"; the session's GitHub tools only accept the name in the session scope. When a push mentions a move, check `list_repos` and update links | Push output; Actions run read via the old name |
| X30 | Geodata services (BGR, BKG / basemap.de, state geoportals) and `schemas.bgr.de` are blocked in the cloud session, also for WebFetch (proxy 403 or name not resolved). Research with WebSearch, develop against fixtures and list the hosts to allow ([23 §7](23_open_data_integration.md#7-hosts-to-allow-in-the-cloud-session)) | curl and WebFetch, 2026-11-02 |
| X31 | `schemas.opengis.net` answers only over **https** through the session proxy (http: no connection); the BoreholeML XSD imports GML/ISO 19139 with `http://`. Validate with `xmlschema` and a `uri_mapper` http → https; the first load of all schemas takes about 30 s | `tests/test_boreholeml.py` |
| X32 | A state service can drop connections (`Connection reset by peer` from the Brandenburg WCS, on some days 2 of 3 requests). Retry a dropped connection up to three times with a short pause, never a timeout or an HTTP error; in the end-to-end check the expected HTTP 502 of a skipped service is no page error | `_holen` in `geodaten`, `scripts/check_app.mjs` |
| X33 | **Windows has new root certificates only after a browser needed them**; Python's `ssl` reads only what is already in the store. Since 2026 gdi.berlin.de is signed through "Telekom Security TLS RSA Root 2023": on the user's PC every Berlin query failed with `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`, while Linux and the CI passed (Mozilla bundle). Verify against the system store **plus** certifi (`netz.ssl_kontext`), never switch verification off, do not retry a certificate error, and check every service from the user's machine with `scripts/dienste_pruefen.py` | User report 2026-11-03, `tests/test_netz.py` |
| X34 | **HTTP headers are latin-1**: a download named after the project ("Gutachten – Neubau ✓") made Starlette fail on every export. Send `filename=` as an ASCII fallback and `filename*=UTF-8''…` (RFC 6266), without the characters Windows forbids in file names (`<>:"/\|?*`) | `server/api.py herunterladen`, `test_export_mit_sonderzeichen_im_namen` |
| X35 | **Playwright `getByLabel` also matches the help button** `Hilfe: <label>` (its `aria-label` contains the text) and fails in strict mode: use `{ exact: true }` | GeolDG check in `check_app.mjs` D |
| X36 | **The loser of a `Promise.race` with `waitForFunction` keeps polling.** After the next page load `window.app` is briefly the element `#app` (named access on `window`) and the predicate throws a page error. End the waiter with a flag set right after the race and use optional chaining | 3D Tiles check in `check_app.mjs` B5 |
| X37 | **Headless Chromium formats `<input type="date">` after the process locale**, not `--lang` or the context locale: for German screenshots start it with `LANG=de_DE.UTF-8` | `docs/img/21_geoldg.jpg` |
| X38 | **A new example is a new button with a familiar name** (P13 again): *Standort Berlin-Friedrichshain* made `getByRole("button", { name: /Berlin/ })` ambiguous. Anchor the names of examples in the checks (`/^Berlin V-67b/`) | `check_app.mjs` B |
| X39 | **A site that refuses automated clients is not worked around.** A browser user agent to read a Länder portal was refused by the session as bot-check circumvention. Enter the official link as *ungeprüft* and let the user check it with the tool (*Prüfen*) or in the browser | 2026-11-05 |
| X40 | **A class name of a new page can collide with the global CSS of the app.** The tool page reused `app.css`: `.feld input { width: 8.5rem }` shrank its form, `button.link` turned chips into underlined links, `.suche` was full width; and the other way round, a new global `.ungeprueft` of the app turned the chips of the tool into orange pills. Check every page in a screenshot after a CSS change; give the classes of a part a prefix of their own (`chip-…`) | Tool *Dienste der Länder* |
| X41 | **A `<select>` with lit: bind `.value` as well as `?selected`.** Changing the entry left the select blank when the value was not among the options (*Brandenburg mit Berlin* is a display name, not a Land): a free text with a datalist fits a display name | Tool *Dienste der Länder* |

Up: [Index](README.md)

Related: [15 Real results](15_results_real_pdfs.md) · [11 Decisions](11_decisions.md) · [09 Validation](09_validation_benchmark.md) · [Architecture](ARCHITECTURE_BAUGRUNDMODELL.md) · [18 Layer modeler](18_layer_modeler.md) · [21 Step app and norms](21_app_schritte_normen.md) · [22 Online](22_deployment.md) · [23 Open data](23_open_data_integration.md)
