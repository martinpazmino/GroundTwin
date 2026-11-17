---
title: "30 GroundTwin Analysis: research log"
date: 2026-11-17
tags: [groundtwin-analysis, research, agsi, daub, tbm, plaxis, interoperability]
aliases: [GroundTwin Analysis research, AGSi research, DAUB TBM tables]
status: in-progress
---

# 30 GroundTwin Analysis: research log

Research for the concept in [29](29_groundtwin_analysis.md). Each section says what was read, how, and what it changes.
Only facts with a source are recorded; claims not checked against the source text are marked as such.

> [!NOTE]
> Summary of the first round (2026-11-17):
> - **AGSi 1.0.1** (June 2024) fits the interpreted part of the package, but every AGSi object forbids additional
>   attributes. Value kind, provenance and σ must go into a separate manifest keyed by AGSi ids (§1).
> - **DAUB Teil 3** splits the ground model into the factual *GeoDocu Model* and four interpreted models; GroundTwin's
>   data map onto them directly (§2).
> - **DAUB TBM selection** names 7 soil parameters and expects the *characteristic values from the geotechnical
>   report* as input. The slurry (SLS) and EPB tables were read from the vector PDF and checked against the rendered
>   page (§3).
> - **Experiment:** from the layer descriptions alone, at most 3 of the 7 DAUB inputs can be estimated, and coverage
>   depends on the Gutachter's writing style (Berlin: fines class for 51 of 69 Schichten; Talheim: consistency for 17
>   of 65; relative density in neither) (§4).
> - **PLAXIS** takes boreholes (PLAXIS Designer: OpenGround, gINT, CSV) and Leapfrog sections; the CSV layout is not
>   publicly documented in what was found (§5).

## 1. AGSi 1.0.1

**Read:** the standard pages (general, scope, rules, data, model, observation, geometry, codes) at
<https://ags-data-format-wg.gitlab.io/agsi/agsi_standard/latest/> and the JSON Schema `AGSi_JSONSchema_v1-0-1_2019-09.json`
from the standard's download (2026-11-17).

| Finding | Source | Consequence for GroundTwin |
|---|---|---|
| Version 1.0.1 published June 2024; 1.0.0 was the first formal release (30 Nov 2022) | Version info | target 1.0.1 |
| AGSi is for **interpreted** data; factual data go in AGS (factual) files referenced as documents | Scope 1.3.1, Data rules 7.2.2 | BoreholeML/AGS4 for Bohrungen; AGSi only for Einheiten, statistics, model |
| *Property* = value from a test (Eurocode 7 measured or derived); *parameter* = interpreted design value, most likely characteristic | Data rules 7.2.1 | GroundTwin writes properties (`agsiDataPropertyValue`, `agsiDataPropertySummary`), never parameters, unless the engineer enters them |
| Parameters shared should be characteristic values, not factored design values | Scope 1.3.1 | consistent with “GroundTwin derives, the engineer decides” |
| Every object of the schema has `additionalProperties: false` (27 of 29 definitions; only `coordinateTuple` and `valueProfile` are open) | JSON Schema | no own fields inside AGSi; value kind, provenance, σ go into the manifest keyed by `dataID`, `elementID`, `holeID` |
| `agsiDataPropertySummary`: min, max, mean, standard deviation, count, summary text | JSON Schema | fits the Kennwerte statistics per Einheit/Bereich |
| Codes: AGSi list recommended; codes not covered are defined with `agsProjectCode`; property codes follow AGS factual headings (e.g. `LLPL_PL`), derived values use parameter-style codes | Codes 9.1, Data rules 7.2.3 | German codes (DIN 4023, DIN 18196, VOB/C ATV, Homogenbereich) as `agsProjectCode` with a code set |
| `caseID` optional on data values (code or text) | Data rules 7.2.4 | candidate for “Ansprache” vs “Labor”, to be decided with the guidance pages |
| `agsiGeometryFromFile` points to external geometry files with `fileFormat` free text | Geometry 6.3.1 | the IFC of the model can be referenced instead of duplicated |
| Identifier cross-checks and uniqueness are not checked by generic JSON Schema validators | Encoding 8.3 | our exporter must check them itself |
| `agsiModelElement` has no required attributes; `elementType` is free text (example *Geological unit*) | JSON Schema | Einheiten as `Geological unit`, Homogenbereiche as their own element type per ATV |

**Mapping (draft):**

| GroundTwin | AGSi |
|---|---|
| project, CRS (ETRS89/UTM, DHHN2016) | `agsProject`, `agsProjectCoordinateSystem` |
| Gutachten PDF, BoreholeML, IFC | `agsProjectDocument` in a document set |
| layer model | `agsiModel` (type observational) |
| Einheit | `agsiModelElement` (`elementType` = Geological unit) + `agsiGeometryFromFile` → IFC |
| Homogenbereich per ATV | `agsiModelElement` in a separate `agsiModel` per ATV |
| Kennwerte statistics | `agsiDataPropertySummary` / `agsiDataPropertyValue` with `dataID` |
| Bohrungen shown in the model | `agsiObservationExpHole` with `agsiObservationColumn` |
| value kind, provenance, σ, completeness | manifest (outside AGSi), keyed by the ids above |

**Open:** the AGSi *guidance* pages (data cases, model types) were not read yet; the AGS validation tool mentioned in
8.3 was not found.

## 2. DAUB Teil 3: Baugrundmodell

**Read:** *Recommendation BIM in Tunnelling – Model requirements – Part 3: Ground Model* (English edition 05/2023,
39 pages), chapters 4.1–4.4, from <https://www.daub-ita.de/fileadmin/documents/daub/gtcrec5/2023-05_DAUB-BIT-Modellanforderungen-T3_EN_fin.pdf>.

- The domain model *Ground* consists of the factual **GeoDocu Model** and the interpreted **Geological**,
  **Geotechnical**, **Hydrogeological** and **Geotechnical Synthesis Model** (Figure 4-1). The strict separation of
  factual and interpretative data follows DIN 4020, SIA 199 and the ÖGG guidelines.
- The GeoDocu Model is “not entirely factual in a strict sense”: allocating borehole lithology to a geological unit is
  already interpretation. This supports a value **kind** per value rather than a hard factual/interpreted file split.
- The Geotechnical Synthesis Model holds the prognosis for the tunnel section: homogeneous areas, discontinuities,
  behaviour types, water ingress, geogenic risks; its content is agreed between modeller, client and designer.
- Information can be modelled as sub-objects with geometry or as properties of a parent object (example: water level
  in a borehole); explicit requirements per project.
- Chapter 4.5 (properties catalogue) and the appendices were not read yet.

**Consequence:** the package's parts map onto the DAUB sub-models one to one (see [29 §2](29_groundtwin_analysis.md#2-terms-en-19972024-daub-dggt)).
The Homogenbereiche of [28](28_homogenbereiche.md) belong to the synthesis side, not to the geological model.

## 3. DAUB TBM selection tables

**Read:** *Recommendations for the Selection of Tunnel Boring Machines* (version January 2022, revised August 2025,
55 pages) from <https://www.daub-ita.de/fileadmin/documents/daub/gtcrec1/2025-08_Selection_of_Tunnel_Borng_Machines.pdf>;
section 7.1 and Appendix 3.

- **Inputs** (7.1.1): “The characteristic values from the geotechnical report and, if necessary, bandwidths and values
  from the reports of the tunnel engineering experts serve as input parameters for the selection tables.” A support
  pressure calculation is required in any case; the table ranges do not replace it.
- **Symbols** (7.1.2–7.1.4): `+` main field of application, `o` extended (needs specific additional measures), `–`
  limited (considerable additional measures; risk analysis and comparison of variants strongly recommended).
- **Soil parameters** (Appendix 3, all machine types): fines content < 0.06 mm (DIN 18196) in 4 classes; permeability k
  (DIN EN ISO 17892-11) in 4 classes; consistency I<sub>c</sub> (DIN EN ISO 17892-12) in 5 classes; relative density (DIN 18126)
  in 3 classes; support pressure in 4 classes; swelling potential in 4 classes; abrasivity as equivalent quartz content
  in 5 classes. Rock: unconfined compressive strength, RQD and further RMR parameters.
- **Tables:** 3.1 GRT, 3.2 DOS, 3.3 OPS, 3.4 SLS (slurry), 3.5 EPB, 3.6 VDS, 3.7 HYS, 3.8 EXS/RHS. A Mixshield is a
  slurry machine with an air cushion; DAUB does not list it as its own type.

**How read:** the tables are vector graphics with the symbols as text. A small script grouped the words by height and
assigned each symbol to the nearest class column (the same technique as the Bohrprofil extraction). For SLS and EPB
every cell was then **checked against the rendered page**; for other machine types the script mis-assigned some
rows, so those values are not recorded here.

**Appendix 3.4 Slurry shield (SLS)** and **3.5 Earth pressure balance shield (EPB)**, soil part:

| Parameter | Class | SLS | EPB |
|---|---|---|---|
| Fines < 0.06 mm | < 5 % · 5–15 % · 15–40 % · > 40 % | + · + · + · o | – · o · o/+ · + |
| Permeability k [m/s] | > 10⁻² · 10⁻²–10⁻⁴ · 10⁻⁴–10⁻⁶ · < 10⁻⁶ | – · o · + · o | – · – · o · + |
| Consistency I<sub>c</sub> | breiig 0–0.5 · weich 0.5–0.75 · steif 0.75–1.0 · halbfest 1.0–1.25 · fest 1.25–1.5 | –/o · o · o · o · o | o · + · + · o · o |
| Relative density | dicht · mitteldicht · locker | + · + · o | + · + · + |
| Support pressure [bar] | 0 · 1–4 · 4–7 · 7–15 | o · + · + · + | + · + · o · – |
| Swelling potential | kein · gering · mittel · hoch | + · + · o · – | + · + · o · – |
| Abrasivity äQu [%] | 0–5 · 5–15 · 15–35 · 35–75 · 75–100 | + · + · + · o · o | + · + · o · o · – |

`a/b` = the class is split in the table into two cells with different symbols. Values reproduced as factual data with
the source; the recommendation itself must be consulted for use.

**Consequence:** a DAUB pre-selection is an **applicability rule** of the catalogue (kind `empirical_range`, authority
guideline) with 7 typed inputs. Its output is a symbol per parameter and machine type, never a choice of machine; the
inputs it expects are characteristic values, which GroundTwin does not set.

## 4. Experiment: DAUB screening from descriptions

**Question:** how many of the 7 DAUB inputs can be estimated from the layer descriptions GroundTwin already reads?
**Method** (scratch script, not part of the product): `normen.deuten` on every Schicht of the two real examples;
fines class from main soil and the stage of a fine-grained secondary fraction (DIN 4023 guide values: *schwach* < 15 %,
without qualifier 15–30 %, *stark* > 30 %); consistency and relative density from the Ansprache.

| Example | Schichten | Fines class | Consistency | Relative density | k, pressure, swelling, abrasivity |
|---|---|---|---|---|---|
| Berlin V-67b | 69 | 51 | 0 | 0 | never |
| Talheim | 65 | 15 | 17 | 0 | never |

- The consistency terms of the Ansprache (breiig, weich, steif, halbfest, fest) are the class names of the DAUB
  consistency row, so a description-based class is direct, though without a measured I<sub>c</sub>.
- “No fine fraction named” was read as fines < 5 %. This is an **assumption**: a short field description (Berlin:
  `Feinsand/grau/Schichtwasser`) may simply not mention fines. Such a class must be shown as assumed.
- Clean sands of Berlin come out as `+` for SLS and `–` for EPB on fines alone, which matches common practice, but
  4 of 7 inputs are always missing. A screening from descriptions is an *indication of what to investigate*, not a
  pre-selection.

**Consequence:** the readiness view (phase A3) is the useful product here: it tells which DAUB inputs exist, which are
assumed and which laboratory tests would fill the rest (grading → fines and k; Atterberg + water content → I<sub>c</sub>;
abrasivity tests).

## 5. PLAXIS interfaces

**Read:** vendor and community pages (2026-11-16/17); no full manual.

- PLAXIS Designer imports boreholes from OpenGround Cloud, gINT and CSV
  ([Wilde Analysis](https://wildeanalysis.co.uk/software/built-environment/plaxis/designer/),
  [Bentley](https://br.bentley.com/pds-plaxis-designer-ltr-en-lr)). The CSV column layout was **not found** publicly.
- PLAXIS 2D imports Leapfrog cross sections through Seequent Central; PLAXIS 3D takes data from a Leapfrog project
  published to Central ([Bentley wiki](https://communities.bentley.com/products/geotech-analysis/w/wiki/64841/import-leapfrog-geological-cross-sections-from-seequent-central-into-plaxis-2d)).
- CPT import exists ([Bentley wiki](https://communities.bentley.com/products/geotech-analysis/w/plaxis-soilvision-wiki/47629/how-to-import-cpt-data-into-plaxis)).
- Scripting: boreholes with groundwater head and layer levels can be set from a CSV through the PLAXIS Python
  interface (forum example, V20 Update 3 onward; [Bentley forum](https://communities.bentley.com/products/geotech-analysis/f/plaxis-soilvision-forum/203925/python---boreholes-and-soil-layers-set-using-information-from-a-csv-file)).
- Leapfrog Works imports AGS 3.1 and 4 ([Seequent help](https://help.seequent.com/Works/4.0/en-GB/Content/drillholes/import-drillholes.htm)).

**Consequence:** the open route to PLAXIS is AGS4 (→ OpenGround/Leapfrog → PLAXIS). A direct PLAXIS Designer CSV needs
a sample file exported from PLAXIS by someone with a licence.

## 6. Next research items

1. AGSi guidance pages (data cases, model types, example files); decide the use of `caseID`.
2. DAUB Teil 3 chapter 4.5 (properties catalogue) and appendices: which properties it expects per sub-model.
3. Remaining DAUB TBM tables (OPS, VDS, HYS) with the same visual check.
4. Correlation sources for phase A4 (CPT SBT, DPH density): read the source texts and collect reference cases.
5. A PLAXIS Designer CSV sample (needs a licence holder).
6. DGGT recommendation 2 (*Entwicklungsstufen und Attribuierung*) for the attribute list of the Fachmodell Baugrund.

---

Up: [Index](README.md)

Related: [29 GroundTwin Analysis](29_groundtwin_analysis.md) · [28 Homogenbereiche](28_homogenbereiche.md) ·
[27 Ground Analysis](27_ground_analysis_gempy.md) · [Architecture](ARCHITECTURE_BAUGRUNDMODELL.md)
