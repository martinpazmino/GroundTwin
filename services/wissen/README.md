---
title: "services/wissen: knowledge catalogue and package manifest (schemas)"
tags: [groundtwin-analysis, schema, catalogue, manifest]
---

# services/wissen

Schemas of GroundTwin Analysis (D108, accepted 2026-11-22; [docs/29](../../docs/29_groundtwin_analysis.md)), no
runtime code yet (A1/A2 build on them):

- `schemas/katalog_eintrag.schema.json`: one entry of the knowledge catalogue (rule, correlation, empirical range,
  analysis, requirement) with source (`verified` only after the source text was read), inputs, outputs, validity,
  uncertainty, `when_missing` and tests (docs/29 §3).
- `schemas/manifest.schema.json`: the manifest of the information package. Value kind per value (`observed`,
  `interpreted`, `derived`, `modelled`, `assumed`, `missing`), provenance (sources, catalogue entry and version, inputs),
  uncertainty by component, open items. `charakteristisch: true` only with `eingegeben_von`: GroundTwin derives, the
  engineer sets characteristic values (docs/29 §4–5).

Tests: `tests/test_wissen_schemas.py` (skip without `jsonschema`).

Up: [Documentation index](../../docs/README.md)
