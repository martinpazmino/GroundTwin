---
title: "Sondierungen: digitising DPH/CPT curves"
date: 2026-10-23
tags: [geo_agent, extraction, sondierungen, dph, cpt]
aliases: [Sondierungen, Rammsondierung, Drucksondierung]
---

# Sondierungen: digitising DPH/CPT curves

**Conclusion:** the Sondierungen (Rammsondierung DPH/DPL/DPM, Drucksondierung CPT) are discarded
today (`geo_agent/bohrprofil.py:32`, README: "CPT-/Sonden-Spalten bewusst weggelassen"), but in a
vector PDF their curves are **exact polylines**. With the axes calibrated by regression (the same
technique as in the Längsschnitt) they can be digitised without loss.

**Status:** a stage of its own reads DPH tables, diagrams and Längsschnitte and CPT diagrams from real Gutachten (§5, 2026-11-21). Before: tested for DPH in the synthetic layout B (`soundings` in
[`prototyp_v2.py`](../services/extractor/prototyp_v2.py)): **32 steps**, maximum error
**0.4 blows N10** (rounding of the regression on the centre of the labels). CPT: design.

## 1. What they contain

| Type | Standard | Curve | Value |
|---|---|---|---|
| DPL / DPM / DPH / DPSH | DIN EN ISO 22476-2 | steps every 10 cm | `N10` (blows / 10 cm) |
| CPT / CPTu | DIN EN ISO 22476-1 | continuous | `q_c` [MN/m²], `f_s`, `R_f`, (`u_2`) |
| SPT (in the Bohrprofil) | DIN EN ISO 22476-3 | single numbers | `N30` |

Later use (Lagerungsdichte, consistency, model parameters): standardised correlations, done by the
geotechnical engineer; the app only delivers the data with its provenance.

## 2. Algorithm

1. **Find the diagram**: title with the regex `^(DPH|DPL|DPM|DS|CPT|SRS)\s*\d+…` and the frame
   (tall rectangle without fill) below it.
2. **Value axis**: integers in a row below the title (`0 10 20 30`) → fit `N10 = a·x + b`. Accept
   only if they form an arithmetic progression (≥ 3).
3. **Depth axis**: ruler of integers to the left of the frame (`1 2 3 …`) → `Tiefe = c·y + d`; if
   the diagram shares the axis with the Bohrprofil, reuse its regression
   ([02 §3](02_bohrprofil_generalization.md#3-vertical-scale-by-regression)).
4. **Curve**: the path without fill with ≥ 6 segments inside the frame. DPH: each vertical segment
   is a step `(Tiefe_oben, Tiefe_unten, N10)`. CPT: sample the polyline every 2 cm.
5. **Several curves** (CPT: `q_c` and `R_f`): separate them by colour, line width, dash pattern or
   OCG layer, and assign each one to its axis (a CPT usually has two horizontal scales).
6. **Validate**: monotonic depth, values inside the axis, last depth = the labelled Endtiefe.

## 3. Special cases

- Values beyond the axis are written as text at the edge (`N10 > 50`, `76`) → read the text instead
  of the curve and mark it `censored`.
- Logarithmic axes (some CPTs): fit on `log10(value)`.
- Diagram split over several pages → concatenate by depth.
- Scans: raster only → Fast Line Detector / vectorisation (swissgeol has line detection in raster,
  [08](08_swissgeol_reuse.md)); lower confidence.

## 4. Data model

```sql
create table soundings (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects on delete cascade,
  code text not null,                      -- 'DPH 1', 'CPT 3'
  kind text not null,                      -- 'DPH' | 'DPL' | 'CPT' ...
  collar geometry(PointZ),
  provenance jsonb not null default '[]',
  unique (project_id, code)
);
create table sounding_values (
  sounding_id uuid references soundings on delete cascade,
  depth_top numeric(7,2), depth_bottom numeric(7,2),
  quantity text not null,                  -- 'N10' | 'qc' | 'fs' | 'Rf'
  value real, censored boolean default false
);
```

It fits next to `boreholes` in the schema of the
[architecture §5.2](ARCHITECTURE_BAUGRUNDMODELL.md#52-supabase-schema-draft-migration); in IFC,
`Pset_SolidStratumCapacity.NValue` can take values aggregated per stratum.

## 5. Measured stage on real Gutachten (2026-11-21, Issue #27 part 1)

`services/extractor/sondierungen.py` is a stage of its own like `kennwerte.py` (prototyp_v4 untouched):
`lesen(pdf, doc=None, ocr=True)` gives per Sondierung `code`, `art` (DPH/DPL/DPM/DPSH/SRS, CPT/CPTu), `seite`, `form`
(`diagramm`, `tabelle`, `laengsschnitt`), `werte` (DPH: `[oben, unten, N10]`; CPT: `[tiefe, q_c, f_s, R_f]`), `endtiefe`,
`ansatzhoehe`, `konfidenz`, `hinweise`, `beleg` (pages, bbox, method, axis fit) and `quelle` (Text/OCR). Built by
Antigravity (task `agy-20261120-133350`), finished and checked by Claude. Not wired into the model, IFC, BoreholeML or the
app yet (parts 2–4 of #27).

### 5.1 Ground truth (training, never blind)

`benchmark/groundtruth_sondierungen/<pdf>.json`, transcribed by the agent with a sample of 10 values per Sondierung
(page and position) and the values it could not read listed as `unsicher`: 5 PDFs, **32 Sondierungen** (26 DPH/DPL,
6 CPT). Checked independently: Triefenstein, all 160 table rows read from the text layer, 0 differences; Hausham
DPH 1, the first 20 steps against the drawing, 0 differences; sha256 of all five PDFs.

### 5.2 Results (`benchmark/sondierungen_eval.py`, baseline `benchmark/baseline_sondierungen.json`)

| Set | Before (prototyp_v4 `soundings`) | After |
|---|---|---|
| Real, 5 PDFs | 0/22 on the three vector PDFs (scans not run) | 32/32 Sondierungen, 0 false; DPH steps **1281/1564**, 0 false values |
| – Hausham (vector diagram) | 0/378 | 378/378 |
| – Marl (vector diagram + Längsschnitt) | 0/506 | 506/506 |
| – Triefenstein (table + bars) | 0/180 | 180/180 |
| – Rednitzhembach (scan) | | 217/220 |
| – Berlin (scan, 2 DPH + 4 CPT) | | found 6/6, values withheld (`konfidenz` 0.35, hint) |
| Stress, 8 cases (2 traps) | 0/6 found | 6/6, 277/277 steps, CPT 41/41 (q_c error 0.0 %), traps 0 |
| Synthetic, 6 layouts | 2/2, 32/32 | 2/2, 32/32 |
| Time per page (vector, no OCR) | 270–950 ms (whole v4) | 40–160 ms |
| rot90 / scale70 (vector PDFs) | | 1064/1064 each, 0 false |
| raster150 (the three vector PDFs as 150 dpi images, no text) | | 19/22 found, **0 values**, 0 false (3.5 s/page with OCR) |
| PDFs without Sondierungen (Halle, Talheim, Wachenroth) | | 0 found (Halle has water-level and Kennwert tables with depths) |

### 5.3 Independent probes and the fix they forced

The stress cases were written by the same agent as the stage, so Claude drew its own layout (axis 0–40 or 0–50,
grid or none, title variants, DPM, scales 1:50 and 1:100): 40/40 steps, 0 false in every variant, **except a curve drawn
as single strokes** (one path per segment, as some CAD exports do): nothing found. Cause: the hull of a vertical or
horizontal stroke has width or height 0 and counts as empty in pymupdf, so every intersection test dropped it. Fixed
generally (`_rechteck`: hull widened by 0.5 pt) plus a rule `einzelstriche_verketten` (strokes of the same colour and
width that join end to end form one path, ≥ 6 links). Now 40/40, and without the rule the case gives no values, never
false ones (`tests/test_sondierungen_extraktion.py`).

### 5.4 Which rule protects which case (ablation)

Each rule switched off on the three vector PDFs, the stress and the synthetic cases (`--disable`, no OCR):

| Rule off | What breaks |
|---|---|
| `tabelle_kopf_schlagzahl` | laboratory table taken for N10 (trap s08: 1 false Sondierung, 10 false values); s01 and CPT s04 get false values (19 in all) |
| `achse_arithmetisch_und_rahmen` | Hausham 283/378, 12 false values; the second page of s06 loses its axis |
| `tiefe_nicht_bohrungscode` | **Marl: 1 false Sondierung, 52 false values** (the L14 failure again) |
| `laengsschnitt_hoehenmassstab` | Marl: 1 false Sondierung, 52 false values; Längsschnitt case s03 not found |
| `mehrseitig_verbinden` | s06 (diagram over two pages): 1 false Sondierung, 40 false values |
| `cpt_kurven_trennen` | CPT s04: q_c error 0 % → 20.6 % mean, 43.3 % max (q_c and f_s mixed) |
| `zensierte_randwerte` | 9 real and 4 stress steps lost (values beyond the axis) |
| `einzelstriche_verketten` | none here; the single-stroke probe gives no values (§5.3) |
| `scan_konservativ` | none without OCR; it withholds the Berlin CPT values |
| `tabelle_luecken_melden`, `cpt_log_achse`, `endpruefung_monoton_und_achse` | none on these cases (they mark or check; kept, measured again with the next real case) |

The tests hold the strongest ones: rule off → case fails (`tests/test_sondierungen_extraktion.py`).

### 5.5 Limits

- **CPT in scans** (Berlin): codes, pages and depth axis are found, values are withheld (several axes, hatching,
  uncertain OCR of the axes); the end depth is right for 2 of 6. A Berlin CPT needs the vector original or a person.
- **Scans at 150 dpi**: the Sondierungen are found by their OCR header, but the steps are withheld; the 300 dpi scan
  of Rednitzhembach gives 217/220. Reading 150 dpi curves would need a vectorisation of the raster (docs/05 §3).
- **Log axes**: built (`cpt_log_achse`) but no real or stress case depends on it yet; it stays switched on until a
  real log-scale CPT measures it.
- **Units of CPT** that the PDF does not print are not guessed (`hinweise`).
- Figures are training figures. A blind test needs a new Gutachten with Sondierungen (#16).


Up: [Index](README.md)

Related: [02 Bohrprofil](02_bohrprofil_generalization.md) · [09 Validation](09_validation_benchmark.md) · [Architecture](ARCHITECTURE_BAUGRUNDMODELL.md)
