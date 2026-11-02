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
| [`prototyp_v4.py`](prototyp_v4.py) | **Used by the app.** Algorithm by stages E0–E9: page class, OCR, generic headers, labels as the final value, "label first" mode, Schicht tables, Schichtenverzeichnis, coordinates, confidence and canonical JSON; switchable rules in `RULES` |
| [`prototyp_v2.py`](prototyp_v2.py) | First layout-independent extractor (columns, header/GOK, scale by regression, Schraffur, water, DPH, coordinates); v4 imports its basic functions |
| [`stress_cases.py`](stress_cases.py) | 17 stress cases, one per lesson, with ground truth |
| [`synth_bohrprofil.py`](synth_bohrprofil.py) | Generates 6 simplified DIN 4023 layouts (A, A2, A3, A4, A5, B) + JSON with the ground truth |

## Run

From the repository root, with the dependencies of `requirements-server.txt` (OCR:
`requirements-ocr.txt`):

```bash
python services/extractor/synth_bohrprofil.py /tmp/synth     # 6 synthetic layouts + ground truth
python services/extractor/stress_cases.py /tmp/stress        # 17 stress cases + ground truth
python benchmark/regression.py --module services/extractor/prototyp_v4.py \
  --real <pdfs> --stress /tmp/stress --synth /tmp/synth --baseline benchmark/baseline_v4.json
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
