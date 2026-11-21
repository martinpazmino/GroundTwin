---
title: "Extractor: Bohrprofile from the PDF"
date: 2026-11-02
tags: [extraction, benchmark]
aliases: [Extractor, Extraction v2 spike]
---

# Extractor: Bohrprofile from the PDF

The extraction that the app uses ([`ui/pipeline.py`](../../ui/pipeline.py) loads `prototyp_v4.py`
without changing it) and the reference of the regression. Specification:
[17 Algorithm](../../docs/17_extraction_algorithm.md); rules: [16 Lessons](../../docs/16_lessons_learned.md).
Every change passes the regression of the [benchmark](../../benchmark/README.md).

| File | What it does |
|---|---|
| [`prototyp_v4.py`](prototyp_v4.py) | **Used by the app.** Algorithm by stages E0–E9: page class, OCR, generic headers, labels as the final value, "label first" mode, Schicht tables, Schichtenverzeichnis, coordinates, water symbols in vector and scan (W3, W4), confidence and canonical JSON; switchable rules in `RULES` |
| [`prototyp_v2.py`](prototyp_v2.py) | First layout-independent extractor (columns, header/GOK, scale by regression, Schraffur, water, DPH, coordinates); v4 imports its basic functions |
| [`textebene.py`](textebene.py) | Shared page text / OCR reader for the additional report and annex stages, marking `quelle: Text` or `OCR` |
| [`kennwerte.py`](kennwerte.py) | Bodenkennwerte (Wichte, Reibungswinkel, Kohäsion, Steifemodul …) from report tables and lists ([28 §9](../../docs/28_homogenbereiche.md#9-kennwerte-from-the-report-tables-issue-18-2026-11-19-training-pdfs-not-blind)) |
| [`labor.py`](labor.py) | Bodenmechanische Laborversuche (Wassergehalt, Zustandsgrenzen, Korngröße, Glühverlust, Kalkgehalt, Durchlässigkeit, Proctor, CBR) from annex sheets ([28 §9b](../../docs/28_homogenbereiche.md#9b-laboratory-sheets-of-the-annexes-issue-18-2026-11-19-training-pdfs-not-blind)) |
| [`homogenbereiche_text.py`](homogenbereiche_text.py) | Homogenbereiche defined by the Gutachter in the report (tables, sections, sentences) ([28 §10](../../docs/28_homogenbereiche.md#10-the-gutachters-own-homogenbereiche-issue-21-2026-11-19-training-pdfs-not-blind)) |
| [`wassertabelle.py`](wassertabelle.py) | Water level tables in the report (Aufschluss \| Wasserstand \| Wasserart) with water kind and footnote evidence ([06 §4](../../docs/06_grundwasser.md#4-data-model-and-ifc)) |
| [`sondierungen.py`](sondierungen.py) | Sondierungen (DPH/DPL/DPM/DPSH `N10`, CPT/CPTu `q_c`/`f_s`/`R_f`) from tables, vector diagrams, Längsschnitte and scans; switchable rules in `REGELN` ([05 §5](../../docs/05_sondierungen.md#5-measured-stage-on-real-gutachten-2026-11-21-issue-27-part-1)) |
| [`stress_cases.py`](stress_cases.py) | 23 stress cases (`s01`–`s23`), one per lesson, with ground truth |
| [`stress_sondierungen.py`](stress_sondierungen.py) | 8 synthetic stress cases (`s01`–`s08`, including two traps) with ground truth for Sondierungen |
| [`synth_bohrprofil.py`](synth_bohrprofil.py) | Generates 6 simplified DIN 4023 layouts (A, A2, A3, A4, A5, B) + JSON with the ground truth |

## Run

From the repository root, with the dependencies of `requirements-server.txt` (OCR:
`requirements-ocr.txt`):

```bash
python services/extractor/synth_bohrprofil.py /tmp/synth          # 6 synthetic layouts + ground truth
python services/extractor/stress_cases.py /tmp/stress             # 23 stress cases + ground truth
python services/extractor/stress_sondierungen.py /tmp/stress_sond # 8 sounding stress cases + ground truth
python benchmark/regression.py --module services/extractor/prototyp_v4.py \
  --real <pdfs> --stress /tmp/stress --synth /tmp/synth --baseline benchmark/baseline_v4.json
python benchmark/sondierungen_eval.py --real <pdfs> --stress /tmp/stress_sond --synth /tmp/synth \
  --baseline benchmark/baseline_sondierungen.json
```

## History

The folder started as the spike `spikes/extraktion_v2` (2026-10-23). Files that are no longer needed
remain in the git history at commit `03be932`:

- [`prototyp_v3.py`](https://github.com/martinpazmino/GroundTwin/blob/03be932/spikes/extraktion_v2/prototyp_v3.py):
  the iteration after the first real PDFs ([15](../../docs/15_results_real_pdfs.md)), replaced by v4.
- The runners of the first comparison v1 / v2 / swissgeol on the synthetic PDFs
  ([`run_geo_agent_v1.py`](https://github.com/martinpazmino/GroundTwin/blob/03be932/spikes/extraktion_v2/run_geo_agent_v1.py),
  [`run_prototyp_v2.py`](https://github.com/martinpazmino/GroundTwin/blob/03be932/spikes/extraktion_v2/run_prototyp_v2.py),
  [`score_swissgeol.py`](https://github.com/martinpazmino/GroundTwin/blob/03be932/spikes/extraktion_v2/score_swissgeol.py),
  [`eval_utils.py`](https://github.com/martinpazmino/GroundTwin/blob/03be932/spikes/extraktion_v2/eval_utils.py)).

Result of that comparison (2026-10-23; table: [09 Validation](../../docs/09_validation_benchmark.md#1-current-results-spike-synthetic-pdfs)):

- v1: correct on A/A2; A3 6/18 Bodenarten (7 wrong ones in green); A4 and B 0 %; it does not detect
  the contradiction of A5.
- v2: 102/102 Schichten, Schraffur 101/102 (the remaining one is the contradiction of A5, reported as
  an issue), GOK/water/coordinates 17/17, DPH max. error 0.4 N10, scale 1:100/1:50 detected.
- swissgeol (unchanged, commit `776ea39`): boundaries and descriptions 18/18 on A–A3, 12/18 on A4; on
  B correct data under wrong names; 0 water, 0 elevations, 0 coordinates; false Schichten from the
  legend.

Up: [Documentation index](../../docs/README.md)

Related: [17 Algorithm](../../docs/17_extraction_algorithm.md) · [Benchmark](../../benchmark/README.md) · [01 Diagnosis](../../docs/01_diagnosis_fixed_layout.md) · [08 swissgeol](../../docs/08_swissgeol_reuse.md) · [09 Validation](../../docs/09_validation_benchmark.md)
