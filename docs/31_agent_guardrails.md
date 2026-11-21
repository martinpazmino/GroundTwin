---
title: "31 Agent guardrails: rules as checks, feature map, verification"
date: 2026-11-20
tags: [agents, verification, static-analysis, architecture, feature-map, ci, guardrails]
aliases: [Hausregeln, Funktionskarte, Agent guardrails]
status: proposed
---

# 31 Agent guardrails: rules as checks, feature map, verification

GroundTwin is written mostly by agents (Claude, Gemini agents, Antigravity; [24](24_agent_team.md)). Agents copy what
the repository shows them, and they skip prose when a shortcut looks cheaper. This note takes the practice described by
Lauren Tan (talk *All Code Is Slop (Except Mine)*, AI Engineer Code Summit, 2026-11-14, and a summary of her interview,
ConquerAI, 2026-11-16; both summaries were machine-made and are not verified) and applies to GroundTwin what fits.

## 1. The idea in five lines

1. **Code is the agent's memory.** A workaround in the repository is copied; so the repository must show only the
   right way.
2. **Order of investment** (her "pyramid"): architecture of the code > static checks > runtime and formal
   verification > prose (rules, skills, AGENTS.md/CLAUDE.md) > human review.
3. **Every correction of an agent becomes a deterministic check**, not one more line of prose.
4. **Verification first:** the agent must be able to prove its own change (tests, a feature map, a driver for the
   app), so that a person does not have to.
5. **Inner loop before outer loop:** automating a loop that produces slop only produces more slop.

## 2. What GroundTwin already had

| Practice | Already in GroundTwin |
|---|---|
| Verification of the extraction | Regression on real, stress and synthetic PDFs with a baseline; ablation; perturbations ([09](09_validation_benchmark.md)) |
| Runtime verification of the app | `scripts/check_app.mjs` (Playwright, 58 checks), `apps/web/scripts/check.mjs`, `scripts/testplan.py` |
| One verdict instead of logs | `python -m agenten pruefen` ([24 §3](24_agent_team.md)) |
| Tests that must kill mutants | `python -m agenten tests` |
| Prose rules | CLAUDE.md, AGENTS.md, [16 lessons learned](16_lessons_learned.md) (P, E, G, L, W … rules) |

What was missing: most rules of CLAUDE.md were prose only. Nothing failed when an agent broke them.

## 3. Built (2026-11-20)

### 3.1 House rules as tests (`tests/test_hausregeln.py`)

Each rule had been prose; now `pytest` fails with a message that says how to do it right. `BESTAND` lists old places
that may break a rule; the list may only get shorter.

| Rule | Check | Was prose in |
|---|---|---|
| Layers of the code | Imports between areas only as allowed: extractor and modeler import no app code; analysis and geodata only the modeler; `ui` no `server`; v1 (`geo_agent`) only from two old files | Architecture, CLAUDE.md |
| Network | `urllib.request`, `http.client`, `requests`, `httpx`, `socket` only in `geodaten/netz.py` (and the agent team's `anbieter.py`; hand tools in `werkzeuge/`) | X33 |
| Nothing hidden | No broad `except` that swallows silently | "a doubtful value is marked, never hidden" |
| `# noqa` names its rule | No bare `# noqa` | — (from the talk: workarounds multiply) |
| No third-party Gutachten | No PDF in the repository except own synthetic ones; images only in `docs/img` and the web app | "Third-party PDFs are not pushed" |
| Ground truth is checkable | Every `benchmark/groundtruth/*.json` has `source` and `sha256` | Blind-test rules |
| No model identifiers | No Claude model id in tracked files | Session rule |
| No secrets | No `.env`, no key patterns | SECURITY.md |
| Characteristic values stay with the engineer | No `_char` key in the modeler | D108, docs/28 §9 |
| **Extraction changes pass the regression** | `benchmark/baseline_v4.modul.json` holds the sha256 of `prototyp_v4.py` the baseline was computed with; `regression.py --write` writes it; a changed module without a new baseline fails | CLAUDE.md working rules |
| Sondierungen are measured again | `benchmark/baseline_sondierungen.json` carries the hash of `sondierungen.py` (`sondierungen_eval.py --write`) | docs/05 §5 |
| No paths that differ only in case | Two such files overwrite each other on Windows and macOS (seen: `agenten/routinen/README.md` and `readme.md`) | — |

Each check was mutation-tested: an import of `server` in the modeler, a `urllib.request` in `ui`, a silent `except`,
a renamed route and a changed `prototyp_v4.py` each made the suite fail.

### 3.2 `apps/web/dist` matches the source (CI)

The web job builds and then fails if `git status -- apps/web/dist` is not empty ("after changing anything
`npm run build` and commit `apps/web/dist`"). The build is reproducible: a rebuild with Node 22 and `npm ci` gives
byte-identical files.

### 3.3 Feature map (`docs/feature_map.json`, `tests/test_funktionskarte.py`)

The feature map is the shared vocabulary between agents and people: per function its Schritt, whether it sits under
*Erweitert*, its API routes and project operations (`ui/projekt.aendern`), the doc, and the **proof** (unit tests,
checks of `check_app.mjs`). The test fails when:

- a route of `server/api.py` or an operation of `aendern` is not in the map (a new function must say where it lives
  and what proves it);
- the map names a route or operation that is gone (D99: never delete a function, fold it; removing one is now a
  visible decision);
- a named test or end-to-end check does not exist.

Building the map found three operations without any test (`erzeugen`, `auto`, `ueberhoehung`) and one without bounds:
`ueberhoehung` accepted 0 or negative factors. It now takes integers 1–50 and a test covers all four.

### 3.4 Two commands for agents (`.claude/commands`)

- `/regel`: when you correct an agent, turn the correction into a check (test or lint), clean up the existing
  places, and record it in §3.1.
- `/verifizieren`: before saying "done", find the touched functions in the feature map and run their proofs.

## 4. Not adopted, with reasons

| From the talk | Decision for GroundTwin |
|---|---|
| Ban (almost) all comments | **No.** Here comments and docstrings carry the evidence of a domain rule (norm, paragraph, measured case) and are part of "a doubtful value is marked". The failure mode the ban targets (a comment that justifies a workaround) is addressed by the silent-`except` and `# noqa` checks; more can follow per case through `/regel`. |
| Ban nuanced framework APIs (React `useEffect`) | Not applicable in this form; the web app uses lit. Candidate later: a lint for the viewer (e.g. no direct `three` scene changes outside the viewer module). |
| Formal verification (TLA+, Lean) | Not now. Candidates where it would pay: the project state machine (`aendern`, lock of the plan, Standort → Gutachten) and the closed-solid invariant of the modeler (property-based tests first). |
| Auto-merge of agent PRs, fuzzing release builds | Not before the inner loop is trusted; main requires a squash merge by a person. |

## 5. Next steps (proposed)

1. **App driver for agents** (runtime verification): a small CLI over the API (`python -m agenten app <funktion>`)
   that runs one feature-map entry against a running server and writes proof (JSON, screenshot), so an agent can show
   a change works without the full 15-minute end-to-end run.
2. **Property tests** for the modeler invariants (exact contacts, closed solids, unit METRE) on random layer-cake
   data.
3. **Evals of the skills/commands**: run the same task with and without a command in parallel worktrees and score
   the result against the checks (the agent team already scores tests by mutants, [24](24_agent_team.md)).
4. **Ratchet the prose**: go through CLAUDE.md and docs/16 and mark each rule as *check* (with its test) or *prose
   only*; move every rule that can be checked into §3.1.
5. **Outer loop** (later): a scheduled run of the regression and of `check_app.mjs` that opens an issue on a
   regression. Only after 1–4.

## 6. Scheduled routines for Antigravity

The user schedules them in Antigravity on their own machine (it has the real PDFs and the network to the Länder).
The instruction there is one line, *read `agenten/routinen/README.md` and run `agenten/routinen/<name>.md`*; the task
itself is versioned in the repository. Each routine works in its own worktree from `origin/main`, may touch only its
listed files, must pass the house rules and the feature map before a push, and pushes only to its own branch
`agy/routine-<name>` (never `main`, never `--force`); Claude reviews and squash-merges. Routines with *report only*
never change data (`dienste.json`, baselines, constraints).

| Routine | Rhythm | Push |
|---|---|---|
| README and doc index | weekly | docs |
| Doc upkeep (CHANGELOG, links, doc ↔ code) | weekly | docs |
| Dienste der Länder from the user's machine | weekly | report |
| Regression on the real PDFs (+ raster150) | weekly | report |
| Rule audit (prose → check), table below | every two weeks | docs |
| Dependencies (outdated, audit, licences) | monthly | report |
| One test gap of the feature map closed | weekly | tests |

## 7. Rule audit

Filled by the routine `regeln_audit` (rule, source, check or proposal).

| Rule | Source | Status | Check or proposal |
|---|---|---|---|

---

Up: [Index](README.md)

Related: [24 Agent team](24_agent_team.md) · [16 Lessons learned](16_lessons_learned.md) ·
[09 Validation](09_validation_benchmark.md) · [11 Decisions](11_decisions.md) · [21 Step app](21_app_schritte_normen.md)
