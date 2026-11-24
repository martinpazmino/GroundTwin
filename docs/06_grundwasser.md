---
title: "Grundwasser: symbols, text and water lines"
date: 2026-10-23
tags: [geo_agent, extraction, grundwasser]
aliases: [Grundwasser, Grundwasserstand]
---

# Grundwasser: symbols, text and water lines

**Conclusion:** the Grundwasser level is not extracted today. It appears in three forms — a symbol
in the Bohrprofil, text with keywords, and water lines in the Längsschnitt — and all three can be
read deterministically. It is worth combining our own geometric detection (DIN symbol) with
swissgeol's keyword lists and colour detection.

**Status:** symbol tested in the prototype (`groundwater` in
[`prototyp_v2.py`](../services/extractor/prototyp_v2.py)): **17/17** synthetic Bohrungen with
depth within ±5 cm and date. swissgeol unchanged found **0/14** in the 5 layouts it was tested on
(its detector looks for the Swiss two-line symbol;
[08](08_swissgeol_reuse.md#4-test-swissgeol-unchanged-on-our-pdfs)).

**With real PDFs** ([15](15_results_real_pdfs.md)): Talheim **3/4**. The triangle can sit next to
the neighbouring column, and what decides the Bohrung is the end of the **water line**. The
"angebohrt" symbol (two strokes + line) is not read yet. Wachenroth: "kein Grundwasser" detected in
**6/6** and stored as data. swissgeol: 1 false Grundwasser level.

In **Hausham** (DC-Software) the water is written as text `GW 2.53m` (4/4 after adding reading from
text). Three things had to be ruled out as "not water": the series of ▽ on the **elevation ruler**,
the triangles with an **elevation** next to them (`741.00m`) and the ▼ of the **starting
elevation** (depth 0).

## 1. Forms in which it appears

| Form | Where | How it is read |
|---|---|---|
| DIN 4023 symbol (triangle, filled or not, sometimes with lines below) | next to the column | closed path of 3 segments, 3–16 pt, vertex pointing down; the tip is the level |
| Text `GW 3,20 m u. GOK`, `Ruhewasserspiegel …`, date | next to the symbol or in the description | keywords + number + date |
| Text in a minority colour (blue) with a date | next to the column | swissgeol heuristic `groundwater_color_detection.py` |
| HGW / MGW / Bemessungswasserstand lines | Längsschnitt | blue/dashed polylines → `(station, NHN)` ([03 §6](03_laengsschnitt_generalization.md#6-terrain-and-water)) |

The difference between "angetroffen" and "Ruhewasserstand / nach Bohrende" is taken from the
**legend of the document** (fill, number of lines), not from the code.

## 2. Algorithm (symbol)

1. Closed paths with exactly 3 segments and symbol size, less than 30 pt from the column.
2. Exactly one vertex at the bottom → `y_level = y` of the tip → depth with the column's
   regression ([02 §3](02_bohrprofil_generalization.md#3-vertical-scale-by-regression)).
3. Text within 14 pt: date `dd.mm.yy(yy)` and, if present, a labelled depth → it must match the
   geometric one (±5 cm); otherwise, issue.
4. `NHN = GOK − Tiefe` as a check.

## 3. Keywords (German)

Base: swissgeol's `groundwater_keys.de` list (`Grundwasserspiegel`, `GW`, `GWSP`, `Wsp`,
`GW-Spiegel`, `Grundwasser`, …) and its false positives (`Grundwasserfassung`, `GW/`). To add for
Germany: `GW angetroffen`, `Ruhewasserspiegel`, `Wasserstand nach Bohrende`, `GW-Stand`, `HGW`,
`MGW`, `Bemessungswasserstand`, `Schichtenwasser`; units `m u. GOK`, `m NHN`, `m NN`, `mNN`
(swissgeol comes with Swiss units such as `m ü. M.`).

## 4. Data model and IFC

Table `groundwater_obs` in the [architecture §5.2](ARCHITECTURE_BAUGRUNDMODELL.md#52-supabase-schema-draft-migration)
with `kind` ∈ {angetroffen, ruhe, nach_bohrende, bemessung, hgw, mgw}, `depth`, `nhn`,
`observed_on`, provenance. In IFC: `Pset_BoreholeCommon.GroundwaterDepth`; the lines of the
Längsschnitt as a `WATER` stratum or a surface in the model.

**Built (Issue #26, 2026-11-19).** The plan above split in two:

- *Per Bohrung* (`groundwater` of the extraction): `kind` ∈ {`angetroffen`, `Ruhewasser`, `Bohrende`,
  `Schichtenwasser`, `unbestimmt`}, `observed_on` (ISO date) and `evidence` (the text read). The names follow the
  BoreholeML import. Older extractions write `gemessen`, read as `unbestimmt`. Rules: [17 E7](17_extraction_algorithm.md#e7-water)
  points 4–5; vocabulary and precedence: `services/modeler/baugrundmodell/wasser.py`.
- *Per project* (`wasserstaende` of the extraction): Bemessungswasserstand, zeHGW, HHGW, MHGW, HGW, MGW, MNGW from
  the report text with m NHN, page and evidence. They are not levels of a Bohrung and never enter the
  Grundwasserfläche.
- IFC: `Pset_BoreholeCommon.GroundwaterDepth` = the highest level of the kind with precedence (never Schichtenwasser);
  `CPset_Grundwasser` per Bohrung with all levels (`Staende`, kind and date each), `Art_Modell`, `Datum`,
  `Art_offen`.
- BoreholeML: `bml:groundwater/bml:Groundwater` with `entryDepth`/`balancedLevel`/`endLevel` and their
  `…DateTime` for the kinds angetroffen / Ruhewasser / Bohrende; levels without a kind and Schichtenwasser only in
  the text. Valid against the official 3.2 XSD; the import reads the dates back.
- Measured on the training PDFs: Hausham B 2, B 3 Ruhewasser with date (from the Schichtenverzeichnis), RKS 4, RKS 9
  date only (the PDF does not say the kind); Berlin both levels angetroffen (*Wasseranschnitt*), Bemessungswasserstand
  +32.80 and zeHGW +33.50 m NHN; Halle MHGW 75.0 m NHN; Talheim kind open (it is only in the legend, by the
  symbol: W3, #20). Not built: the HGW/MGW lines of the Längsschnitt and the kind from the legend symbol (#20).

**Water level tables in the report** (2026-11-19, `services/extractor/wassertabelle.py`, separate stage).

- **Table:** a page with `Wasserst…` and `m u. GOK`. A row is a Bohrung code followed by a depth, optionally with a
  footnote sign (`3,00*`) and a Wasserart column.
- **Kind**, never guessed, with the same keywords as the profile:
  1. the value's footnote (`*) Grundwasseranschnitt`);
  2. the Wasserart column (`Schichtenwasser`);
  3. the sentence on the table ("… wie folgt nach Bohrende eingemessen").
- **Date:** a period ("vom 01.07. bis 15.10.2020") is no measuring day and stays in the evidence only.
- **Merging** (`einarbeiten`, in `ui/pipeline.py`):
  - same depth ± 3 cm → kind and date are filled where missing;
  - a level the profile lacks is added with evidence "Tabelle S. …" and an issue on the Bohrung;
  - against "kein Grundwasser" in the profile, a second issue.
- **Measured:** Halle gives 26/26 rows, 22 nach Bohrende and 4 Anschnitt (KRB 2, 7, 23, 30, the starred values).
  The other PDFs give no rows (no false ones). Halle's Bohrprofile are not extracted yet, so the rows stay in
  `wassertabelle` of the document until they are.

**Water lines in the Längsschnitt** (2026-11-24, Issue #26 part 2b, rule `ls_wasserlinien`, W6):

- **Rule:** a blue or dashed open polyline (`width ≥ 80 pt`) on a vector Längsschnitt is extracted only when **(a)** an
  unambiguous water-kind label (`Bemessungswasserstand`, `Bauwasserstand`, `zeHGW`, `HHGW`, `MHGW`, `HGW`, `MGW`,
  `MNGW`, `GW <Datum>`, or a legend-defined abbreviation such as `Bau` → `Bauwasserstand`) is attached within `14 pt`,
  **(b)** the vertical NHN elevation axis is calibrated (`≥ 4` decreasing margin labels with `R² ≥ 0.998`, agreeing if
  two axes exist; or `≥ 2` Bohrung GOKs + `H 1:n` agreeing within `0.12 m`), and **(c)** it is neither the GOK terrain
  line nor a Schichtgrenze. Unclear or uncalibrated lines are withheld and reported in `wasserlinien_hinweise`.
- **Merging into `wasserstaende`:** stored alongside text levels with `quelle: "Laengsschnitt"` (constant `nhn` if
  variation `≤ 5 cm`, else `stuetzpunkte` per station or `x_pt`). Same kind and height within `±5 cm` merges into one
  entry (`quelle: "Text+Laengsschnitt"`, both evidences, confidence `0.95`); a contradiction keeps both entries with a
  `hinweis`. Never enters `boreholes[*].groundwater` or the Grundwasserfläche (G5).
- **Measured:** across the 13 real PDFs, only `marl_251.pdf` p. 6 (Anlage 3.1) has a drawn water polyline
  (`Bauwasserstand` `54.17–56.05 m NHN`, 13 vertices, 0.00 m error; `Bem = GOK` sits on the black terrain line and is
  not emitted as a false line); all 12 other real PDFs give **0 false lines**. Synthetic suite
  `services/extractor/synth_laengsschnitt.py` (5 cases: constant, sloped with stations, text merge/contradiction, 4
  traps, uncalibrated): **6/6** right, **0 false**; stress `s29`–`s30`; `tests/test_wasserlinien_laengsschnitt.py`.

Up: [Index](README.md)

Related: [02 Bohrprofil](02_bohrprofil_generalization.md) · [03 Längsschnitt](03_laengsschnitt_generalization.md) · [08 swissgeol](08_swissgeol_reuse.md)
