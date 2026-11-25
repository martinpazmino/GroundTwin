---
title: "services/wissen: knowledge catalogue and package manifest (schemas)"
tags: [groundtwin-analysis, schema, catalogue, manifest]
---

# services/wissen

Knowledge catalogue and schemas of GroundTwin Analysis (D108, accepted 2026-11-22;
[docs/29](../../docs/29_groundtwin_analysis.md)). **A2 built** (Issue #34): package `wissen` (no imports of other
parts; existing code is only referenced):

- `wissen/groessen.json`: the vocabulary. Every input and output is named here, with `liefert` (which test or document
  provides it) and `eingabe` (set by a person, never derived).
- `wissen/katalog/*.json`: one entry per rule, correlation, range or analysis (14 in v0). The existing knowledge is
  migrated as entries that point to the code and data that already compute it (`implementierung`, `daten_datei`), so
  behaviour is unchanged. The first new entry is the DAUB TBM pre-selection for SLS and EPB (data only, docs/30 §3).
- `wissen.planen(verfuegbar)`: per entry `moeglich` / `hinweisend` / `blockiert`, with assumed, missing and optional
  inputs. Per missing base quantity: what provides it, what it unlocks on its own, and which entries need it.
  `ungenutzt` lists quantities no entry uses yet (CPT, DPH → A4).
- `wissen.abhaengigkeiten()`: the graph computed from the signatures. `wissen.pruefen()` checks structure, known
  quantities, a single producer per quantity and the absence of cycles.
- `wissen.protokoll(...)`: the record of a derived value (entry id + version, inputs), in the manifest format of A1.
- `wissen.verfuegbar_aus_dokumenten(docs)`: the base quantities a project's extraction provides.
- CLI: `python -m wissen bohrung.schichten boden.beschreibung …` (run with `PYTHONPATH=services/wissen`).

Schemas (A0):

- `schemas/katalog_eintrag.schema.json`: one entry of the knowledge catalogue (rule, correlation, empirical range,
  analysis, requirement) with source (`verified` only after the source text was read), inputs, outputs, validity,
  uncertainty, `when_missing` and tests (docs/29 §3).
- `schemas/manifest.schema.json`: the manifest of the information package. Value kind per value (`observed`,
  `interpreted`, `derived`, `modelled`, `assumed`, `missing`), provenance (sources, catalogue entry and version, inputs),
  uncertainty by component, open items. `charakteristisch: true` only with `eingegeben_von`: GroundTwin derives, the
  engineer sets characteristic values (docs/29 §4–5).

Tests: `tests/test_wissen.py` (catalogue and planner on synthetic projects: only Bohrprofile, + Labor, + CPT) and
`tests/test_wissen_schemas.py` (skip without `jsonschema`).

Up: [Documentation index](../../docs/README.md)
