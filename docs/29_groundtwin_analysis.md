---
title: "29 GroundTwin Analysis: concept, knowledge architecture and roadmap"
date: 2026-11-17
tags: [groundtwin-analysis, ground-model, agsi, eurocode-7, knowledge-base, uncertainty, provenance, roadmap]
aliases: [GroundTwin Analysis, Analysis package, Knowledge catalogue]
status: accepted
---

# 29 GroundTwin Analysis: concept, knowledge architecture and roadmap

**GroundTwin Analysis** turns the heterogeneous information of a project (Gutachten, Bohrungen, Sondierungen,
groundwater, laboratory values, the layer model) into a standardised, traceable, analysis-ready package, and knows
**which engineering analyses that package supports, how reliably, and what is missing**. This note records the
concept after a research and architecture review (2026-11-16) and the first research results (2026-11-17,
[30](30_groundtwin_analysis_research.md)). Decision **D108** (proposed) in [11](11_decisions.md).

> [!IMPORTANT]
> **Status: proposed, nothing built.** The concept is sound, with two corrections to the original idea:
> 1. A **universal** engineering knowledge base does not exist in the literature. Correlations are conditional and
>    carry large transformation uncertainty (Phoon & Kulhawy 1999; Ching & Phoon 2014). The knowledge base therefore
>    stores applicability and uncertainty, and its main output is *what can be assessed and how reliably*.
> 2. The bottleneck is **data, not architecture**. Most target analyses (TBM selection, face support, settlement,
>    FEM, jet grouting) need grading, plasticity, strength and permeability values that GroundTwin does not yet
>    extract (#18, #26, #27).

## 1. Scope and naming

- GroundTwin Analysis is the **umbrella**. The existing component *Ground Analysis* (`services/analyse`, [27](27_ground_analysis_gempy.md))
  keeps its code and name and becomes one of its runners (spatial uncertainty, Kreuzprobe, Grundwasserfläche).
- GroundTwin delivers **derived values** with statistics and sources. Choosing **representative / characteristic
  values** stays with the engineer, as EN 1997:2024 prescribes and as DAUB states for its TBM selection tables
  ("the characteristic values from the geotechnical report serve as input", [30 §3](30_groundtwin_analysis_research.md#3-daub-tbm-selection-tables)).
- Design-level analyses (face support pressure, settlement prediction, FEM model building, jet-grouting design) stay
  with specialist software and the responsible engineer. GroundTwin prepares and documents their inputs and may run
  **screening** checks that say so on every output.

## 2. Terms (EN 1997:2024, DAUB, DGGT)

| GroundTwin | EN 1997:2024 | DAUB Teil 3 | AGSi |
|---|---|---|---|
| Bohrungen, Schichten, Sondierungen, water levels, lab results | ground investigation results | GeoDocu Model (factual) | AGS factual files, Observation group |
| Einheiten and layer model | Ground Model | Geological Model | `agsiModel`, `agsiModelElement` |
| Kennwerte statistics per Einheit/Bereich | derived values (GIR) | Geotechnical Model | `agsiDataPropertyValue` / `Summary` |
| Grundwasserfläche, water levels by kind | Ground Model (groundwater) | Hydrogeological Model | elements + properties |
| Homogenbereiche, tunnel sections | — (design side) | Geotechnical Synthesis Model | elements; parameters |
| values chosen by the engineer | representative / characteristic values (GDM) | characteristic values | `agsiDataParameterValue` |

## 3. Architecture

Five separated concerns; each has its own owner, change rate and tests.

| Layer | Holds | Where | Changes |
|---|---|---|---|
| **Information** | facts and interpretations of one project | project files today, Postgres (Supabase) planned; exchanged as the package (§4) | every project |
| **Knowledge** | rules, correlations, applicability ranges, analysis signatures, requirement tables | versioned files in the repo (YAML/JSON + JSON Schema), each entry with source and validity | by review, like code |
| **Dependencies** | what feeds what, what is missing | **computed** from the entries' input/output signatures, never drawn by hand | follows the catalogue |
| **Execution** | runners and a small planner | pure Python functions referenced by entry id; existing runners (modeler, Ground Analysis) | like code |
| **Semantic view** | linked-data export | optional JSON-LD/RDF with PROV-O and GSO terms | later, on demand |

The catalogue follows the pattern already used by `normen.json` (evidence per value) and `homogenbereiche.json`
(source and *prüfen* flags). An entry:

```yaml
id: cpt.sbt.robertson2009        # stable id, cited by every result
version: 1.0.0
kind: correlation                # rule | correlation | empirical_range | analysis | requirement
authority: correlation           # standard | correlation | empirical | expert | research
source: {citation: "…", edition: 2009, verified: false}   # verified only after the source text was read
inputs: {required: [cpt.qt, cpt.fs, stress.sigma_v0, stress.sigma_v0_eff], optional: [cpt.u2]}
outputs: [soil.sbt_zone, soil.ic]
preconditions: ["cone calibration known", "not for cemented or structured soils"]
validity: {ic: [1.0, 4.0]}
uncertainty: {model: categorical, note: "±0.1 Ic around zone boundaries reported as ambiguous"}
when_missing: {stress.sigma_v0_eff: block}
tests: [tests/wissen/cpt_sbt_cases.json]
```

**Why no ontology or knowledge graph first:** no mature ontology covers geotechnical parameters, correlations and
their validity (GSO covers geology); the hard part is collecting and testing rules with their sources, which typed
files with tests handle well; the planner needs reachability in a graph, not description-logic reasoning; stable ids
and PROV-style result records keep an RDF export mechanical later.

## 4. The package

No new exchange standard. A package of established formats plus one manifest:

| Part | Format | Content |
|---|---|---|
| Interpreted ground model | AGSi 1.0.1 JSON, validated against its JSON Schema | project, CRS, model elements (Einheiten, Homogenbereiche), property statistics, documents |
| Factual data | BoreholeML 3.2 (Germany); AGS4 (Leapfrog, OpenGround route) | Bohrungen, Schichten, water levels; later Sondierungen and lab |
| Geometry | IFC 4.3 (+ 3D Tiles) | strata, Bohrsäulen, terrain, Psets |
| Manifest | small JSON of our own, keyed by AGSi `dataID` / object ids | value kind and provenance per value, completeness, derivation log, uncertainty, open items, sha256 of sources |
| Report | HTML/Markdown generated from the same data | what is known, derived, missing; what each analysis could use |

The manifest is required because AGSi forbids additional attributes on every object (`additionalProperties: false`,
[30 §1](30_groundtwin_analysis_research.md#1-agsi-101)): value kind, provenance and σ per node have no place inside
AGSi.

## 5. Value kinds, uncertainty and provenance

Every value carries a mandatory **kind**: `observed`, `interpreted`, `derived`, `modelled`, `assumed`, `missing`. The
UI, the IFC and the package show it. An estimate can then never pass as a measurement.

Uncertainty is kept by component and not merged into one number when the components are not commensurable:
measurement, classification, transformation (correlation), statistical (few samples; counts always reported),
spatial and geological model (Kreuzprobe-calibrated σ, built), temporal (groundwater by kind and date), completeness.
Propagation by Monte Carlo where runners are cheap, first-order where chains are closed-form.

A derived value records the entry id and version that produced it and the ids of its inputs (maps onto PROV-O:
entity, activity, used). Catalogue entries are versioned; results reference the version, as the model key does for
geometry today.

## 6. Data requirements (summary)

What becomes possible as data are added. The planner will generate this per project; the full table with
current GroundTwin status is in the review and will be reviewed with a geotechnical engineer before it is used.

| Analysis | Bohrprofile only | + CPT/DPH | + groundwater by kind/date | + laboratory | GroundTwin today |
|---|---|---|---|---|---|
| Layer model, 3D | supported (with coordinates) | denser | – | – | built |
| Soil classification DIN 18196 | indicative | SBT only | – | supported | description-based |
| Homogenbereiche + Kennwerte | grouping, Ansprache | indicative | indicative | supported | grouping + Ansprache |
| Strength/stiffness | not possible | correlations | needed for σ′ | derived values | not built |
| Groundwater surface | indicative | – | supported | – | built (kinds mixed, #26) |
| TBM pre-selection (DAUB) | 3 of 7 inputs at best ([30 §4](30_groundtwin_analysis_research.md#4-experiment-daub-screening-from-descriptions)) | indicative | required | supported | not built |
| Face support, settlement | not possible | screening | required | screening | not built |
| FEM input | geometry | indicative | water | parameters | geometry built |

## 7. Use of LLMs

LLMs consume the package through deterministic, read-only tools (API or MCP): get package, list gaps, run planner,
run a catalogue entry. Every number in an answer must come from a tool result with an id. LLMs never write values into
the package without provenance and never are the analysis engine (not reproducible, not auditable). This extends the
existing rule *the LLM proposes, the geometry decides* (architecture §6.9).

## 8. Roadmap

| Phase | Content | Depends on |
|---|---|---|
| A0 | decisions and vocabulary (D108): scope, value kinds, package parts, catalogue schema (**done** 2026-11-22: `services/wissen/schemas`) | — |
| A1 | package v0: AGSi export + manifest + report from existing data (**built** 2026-11-22, §8.1) | A0 |
| A2 | catalogue v0 + planner; migrate `normen.json`, `homogenbereiche.json`, Homogenbereich proposal (**built** 2026-11-24, §8.2) | A0 |
| A3 | readiness view per project (§6 generated) in the app and the report (**built** 2026-11-25, §8.3; expert review open) | A2 |
| B | data extension: groundwater kind/date (#26), Sondierungen (#27), report tables and lab values (#18) | parallel; critical path |
| A4 | first correlations with uncertainty (CPT SBT, DPH density; #28, #29) | A2, B |
| A5 | exports: AGS4, PLAXIS-oriented boreholes/CPT, LLM tools (#30) | A1 |
| A6 | screening analyses (DAUB TBM pre-selection, clogging, face support, settlement) with an engineer partner | A2, B |
| A7 | semantic export (JSON-LD, PROV-O, GSO) on demand | A1 |

### 8.1 A1 built: information package v0 (Issue #33, 2026-11-22)

`services/geodaten/geodaten/agsi.py`, export `GET /api/projekt/{sig}/export/agsi` (app: *Modell → Erweitert → Weitere
Exporte → Informationspaket AGSi*). The ZIP holds:

| File | Content |
|---|---|
| `<name>_agsi.json` | AGSi 1.0.1: `agsProject` with CRS (EPSG of the project or local; heights as in the Gutachten, the height datum is not asserted), a document set (each source with sha256, the IFC, the BoreholeML), three code sets (`CS_EIG` property codes, `CS_CASE` cases, `CS_GEO` Einheiten). Model `M1` (*Geological model*, *Observational*): one `agsiModelElement` per Einheit (`Geological unit`, colour, geometry `agsiGeometryFromFile` → the IFC, `filePart` names the `IfcGeotechnicalStratum`), Laborwerte as `agsiDataPropertySummary` with `caseID` `Labor`; the Bohrungen as `agsiObservationExpHole` with one column per Schicht, `geologyCode` = Einheit. One model per ATV for the Homogenbereiche, Kennwerte from the descriptions with `caseID` `Ansprache`. |
| `geometrie/<name>.ifc` | the model as exported by the app |
| `fachdaten/<name>_boreholeml.xml` | factual data, only when reviewed Bohrungen with UTM and GOK exist |
| `manifest.json` | valid against `manifest.schema.json`: per AGSi id the value kind (`observed` Laborwerte, columns, positions; `interpreted` Kennwerte from the Ansprache, entered positions; `modelled` geometry), sources and inputs (sample references), completeness (`E<n>/Unterkante_belegt`, `HB…/Kennwerte_belegt`), open items, Ground Analysis summary (Kreuzprobe, σ if computed), sha256 of every file |
| `bericht.md`, `LIESMICH.txt` | report generated from the same data |

Rules kept: properties only, never `agsiDataParameterValue`; the Gutachten's Kennwerte tables are parameters of the
Gutachter and stay **open** (listed, in the IFC as `CPset_Bodenkennwerte_Gutachten`), as do Sondierungen (factual:
IFC and BoreholeML) and characteristic values (engineer). `caseID` carries the kind of statistic, not the value kind
(§6.2 of docs/30). The exporter checks unique ids and every reference (`agsi.pruefen`) and that every data value has a
manifest entry with kind and source (`agsi.manifest_pruefen`); an inconsistent package is refused.

Measured: Berlin, Talheim and the demo validate against the official AGSi JSON Schema 1.0.1 (2019-09) with format
checking (schema ZIP sha256 `8d8529d8…`, fetched by the test, never committed) and the manifest against its schema.
Tests `tests/test_agsi.py` (schema test skipped offline).

### 8.2 A2 built: knowledge catalogue v0 and planner (Issue #34, 2026-11-24)

Package `wissen` (`services/wissen/wissen`, see its README):
- a vocabulary of 35 quantities with what provides each;
- 14 entries: DIN 4023 class and DIN 18196 group from the description, Konsistenz/Lagerung from the Ansprache, layer
  model, Kreuzprobe, Unsicherheit, Grundwasserfläche, Labor statistics, I<sub>c</sub>, fines content, k,
  Homogenbereich proposal and Kennwerte, and the DAUB TBM pre-selection (SLS/EPB soil part);
- a planner with computed dependencies.

**Migration without changing behaviour:** an entry describes the knowledge (inputs, outputs, validity, uncertainty,
source, value kind) and points to the code and data that compute it today. Nothing is re-implemented, so the modeler,
Homogenbereiche and normen tests are untouched. A test checks that every pointer resolves.

**`verified`:** `true` only where the source text was read:
- DAUB SLS/EPB (docs/30 §3) and GroundTwin's own components;
- `false` for the norm-based rules whose text was not read here (DIN 4023/18196 tables from the user's templates, DIN
  EN ISO 17892) and for the VOB/C matrix (4 of 11 ATV checked, docs/28 §10a).

**Planner on the vocabulary:**
- **Bohrprofile only:** model, analyses and Homogenbereich proposal are *möglich*; Labor rules are blocked; DAUB is
  *hinweisend* at 2/8 inputs (Konsistenz and Lagerung from the Ansprache, as in docs/30 §4).
- **With laboratory sheets:** DAUB reaches 5/8; the rest (support pressure, swelling, abrasivity) is listed with the
  test or person that provides it.
- **CPT:** shows up as *ungenutzt* until A4 adds correlations.

The readiness view (A3, #35) renders this per project.

### 8.3 A3 built: readiness view per project (Issue #35, 2026-11-25)

The planner of §8.2 runs on the base quantities of each project. In the server this is `_bereitschaft`; it is in the
project state, at `GET /api/projekt/{sig}/bereitschaft`, and in the app under *Modell → Erweitert → Bewertbarkeit*.

Project rules:
- a Lage in the Reihe counts as **assumed** (schematic);
- Sondierungen count only with Lage, GOK and values, as in the IFC;
- a Homogenbereich mapping set by the planner counts as the input `hb.zuordnung`.

Each entry shows ✓ *möglich*, ◐ *hinweisend* (with what was assumed or how much was covered) or ✗ *blockiert* (with
what is missing). A list then names each missing quantity, the test or document that provides it, and how many
assessments need it.

The information package (A1) carries the same in `manifest.json` (`bereitschaft`) and as the section *Bewertbarkeit*
of `bericht.md`.

**Hand check:**

| Project | Base quantities | Result |
|---|---|---|
| Berlin | Schichten, Lage (UTM), GOK, description, Wasserstände with their kind; the 6 scanned Sondierungen have no Lage and do not count | 8 möglich, 1 hinweisend (DAUB 2/8), 7 blockiert (all Labor rules, Homogenbereich Kennwerte until a mapping exists, the two Sondierung statistics without a located Sondierung) |
| Talheim | Reihe, so the Lage is assumed and the layer model is *hinweisend*; Labor has only Wassergehalt (and CBR, Trockendichte, not used) | I<sub>c</sub> blocked for w_L and w_P; after a DIN 18300 mapping, Homogenbereich Kennwerte become *möglich* |

The DAUB pre-selection reaches 2 of 8 inputs from descriptions alone, consistent with the experiment of docs/30 §4.

**Still open in #35:**
- the review with the geotechnical expert;
- showing "no fines named" as an *assumed* value, which needs a catalogue entry for fines from the description.

Tests: `tests/test_bereitschaft_app.py` and one end-to-end check.

## 9. Alternatives considered

| Approach | Verdict |
|---|---|
| Ontology / knowledge graph first | not now: no mature target ontology, high cost, little demand; keep as export (A7) |
| **Relational data + declarative catalogue + standard package** | **recommended** |
| Export only, analyses in commercial tools (OpenGround, Leapfrog, PLAXIS) | downstream target of the recommended approach, not a replacement |
| LLM agent as the analysis engine | rejected as engine; fine as interface over deterministic tools |

## 10. Sources

Standards and guidelines: EN 1997-1/-2/-3:2024 and the
[JRC report on Ground Model and derived values](https://eurocodes.jrc.ec.europa.eu/news/jrc-technical-report-assembling-ground-model-and-derived-values);
[DAUB Modellanforderungen Teil 3: Baugrundmodell](https://www.daub-ita.de/fileadmin/documents/daub/gtcrec5/2023-05_DAUB-BIT-Modellanforderungen-T3_EN_fin.pdf);
[DAUB Selection of TBMs (rev. 08/2025)](https://www.daub-ita.de/fileadmin/documents/daub/gtcrec1/2025-08_Selection_of_Tunnel_Borng_Machines.pdf);
DGGT AK 2.14 [Fachmodell Baugrund](https://artikeldatenbank.ernst-und-sohn.de/artikel/gete-2021-1-das-fachmodell-baugrund-empfehlungen-des-arbeits-42086);
[EN 17412-1](https://www.evs.ee/en/evs-en-17412-1-2020).
Data models: [AGSi](https://ags-data-format-wg.gitlab.io/agsi/agsi_standard/latest/),
[OGC Geotech IE 24-008](https://docs.ogc.org/per/24-008.html), [GeoSciML](https://www.ogc.org/standard/geosciml/),
[IFC 4.3 IfcGeotechnicalStratum](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcGeotechnicalStratum.htm).
Ontologies and provenance: [GSO](https://zenodo.org/records/4743221), [PROV-O](https://w3.org/TR/prov-o/).
Uncertainty: [Phoon & Kulhawy 1999](https://repository.sutd.edu.sg/esploro/outputs/journalArticle/Characterization-of-geotechnical-variability/9911198209846),
[Ching & Phoon 2014](https://www.sciencegate.app/document/10.1139/cgj-2013-0353),
[Wellmann & Caumon 2018](https://hal.univ-lorraine.fr/hal-01921494),
[Wiegel et al. 2024](https://artikeldatenbank.ernst-und-sohn.de/artikel/bt-2024-11-implementierung-von-probabilistischen-baugrundmode-51046).
LLMs: [review of LLMs in geotechnics](https://arxiv.org/pdf/2507.05613).
Further sources and the verification status of each are in [30](30_groundtwin_analysis_research.md).

---

Up: [Index](README.md)

Related: [30 Research log](30_groundtwin_analysis_research.md) · [27 Ground Analysis](27_ground_analysis_gempy.md) ·
[28 Homogenbereiche](28_homogenbereiche.md) · [Architecture](ARCHITECTURE_BAUGRUNDMODELL.md) · [11 Decisions](11_decisions.md)
