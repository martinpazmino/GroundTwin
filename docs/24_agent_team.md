---
title: "24 Agent team: Claude as orchestrator, Gemini as specialists (proposal)"
date: 2026-11-05
tags: [agents, orchestration, gemini, claude-code, tokens, automation, proposal]
aliases: [Agent team, Multi-agent system, Gemini agents]
status: proposed
---

# 24 Agent team: Claude as orchestrator, Gemini as specialists (proposal)

Phases 1 and 2 of the mission "an autonomous multi-agent engineering system for GroundTwin": what the repository and the
Google offering really allow, and the smallest architecture that saves Claude tokens without lowering the bar of
[16](16_lessons_learned.md). **Nothing of §5 is built yet**; §8 lists what needs your decision first.

> [!NOTE]
> Summary:
> - **Claude's cost is turns × context, not output.** In this project's longest session (measured, §2): 4,844 calls,
>   a median context of 487 k tokens per call, 2.3 billion cached tokens re-read. Every extra round trip re-reads
>   about half a million tokens. The saving comes from fewer Claude round trips and compact reports, not from
>   shorter answers.
> - **Your Google AI Pro subscription cannot be driven through its CLI.** Gemini CLI no longer serves AI Pro since
>   2026-06-18. The successor, Antigravity CLI, may be run from your own local script. Google staff call wrapping it
>   in a third-party agent (Claude Code) a breach of its terms. Unattended runs risk an account lockout (§4.2).
> - **The subscription still pays its way, through official APIs** (§4.5):
>   - **Jules** (Google's asynchronous coding agent): AI Pro raises it to 100 tasks a day and 15 at once. It has a
>     documented API for automation and works in Google's VMs on a branch of the GitHub repository. It becomes the
>     implementing agent, at no Claude tokens while it works.
>   - **$10 a month of Google Cloud credit** (Developer Program, included since 2026-01-27). It pays for paid Gemini
>     API calls, including `gemini-4-argon`, once a Cloud project with billing is linked.
>   - The subscription does **not** raise the limits of an API key; its higher quotas apply in the AI Studio web
>     interface only.
> - **The reviewing and analysing agents use the Gemini API with an AI Studio key**, called from a thin Python package
>   in the repo. Its free tier needs no billing and covers `gemini-3.8-flash` and `gemini-3.5-flash-lite`. "Argon" is
>   real: `gemini-4-argon`, Google's flagship, paid only (§4.3), so it runs on the monthly credit.
> - **Deterministic scripts first, agents second.** A suite runner with a ten-line verdict and a docs consistency
>   check save more Claude turns than any model. Agents get the loops that need judgement: diagnose a failure,
>   review a diff, draft the docs of a change, write tests (§3).
> - **Four roles, not twenty.** Roles are prompts instantiated per task, with a model policy, a context recipe and
>   an output schema. Gemini agents get no shell and no write access. They return text (findings, a patch). The
>   orchestrator applies patches in a git worktree, and Claude approves what enters the branch (§5).

## 1. What the repository already has

| Layer | Today | Gap for agents |
|---|---|---|
| Rules | `CLAUDE.md` (134 lines), `CONTRIBUTING.md`, [16](16_lessons_learned.md) (P1–P21 …), [11](11_decisions.md) (D1–D99) | No concise spec for a non-Claude agent; CLAUDE.md is Claude-specific and long |
| Tests | pytest app 173 (~2 min), modeler 63, viewer check 19 (~3 min), end-to-end 54 (~15 min, partly network), regression on real/stress/synthetic PDFs with a baseline, ablation, perturbation, blind protocol | Outputs are long logs; no single compact verdict |
| CI | `.github/workflows/pruefungen.yml`: pytest, web build, container image; end-to-end on demand | No lint (`ruff` passes locally, not in CI), no review step |
| Claude Code config | none (`.claude/` does not exist) | No commands, skills, hooks or subagent definitions |
| Docs | 26 notes, 5.7 k lines, linked; every feature touches 6–9 files (21, 11, 16, CHANGELOG, CLAUDE.md, README, THIRD_PARTY_LICENSES, a README) | Kept in sync by hand; link and anchor checks ad hoc |
| Size | Python/TypeScript/docs about 30 k lines: extractor 2.4 k, modeler 3.1 k, geodaten 3.0 k, server 1.4 k, ui 1.5 k, web 6.6 k, tests 3.2 k | Small enough that a 1 M-token model can hold any one area whole |

## 2. Where Claude's tokens go (measured)

Measured from this session's transcript (`~/.claude/projects/…/<session>.jsonl`, the `usage` record of every
response: **actual**, not estimated), 2026-10-28 to 2026-11-05:

| Quantity | Value |
|---|---|
| Claude calls | 4,844 (506–1,066 per working day) |
| Context per call | median 487 k tokens, p10 193 k, p90 778 k |
| Cached input re-read | 2,328 M tokens; cache creation 37.6 M; uncached input 9.8 k |
| Output | 8.3 M tokens (median 877 per call) |
| Tool results fed back | 4.7 M characters (~1.2 M tokens): Bash 69 %, Read 16.5 %, web search 6.5 % |
| Tool calls | Bash 1,893; Write 158; Read 152; web search 79; GitHub/CI 61 |

What it means:

1. **One extra round trip costs about 0.5 M context tokens** (cached, so cheap per token, but 2.3 billion of them).
   A task that takes 20 small turns re-reads ~10 M tokens. Example from 2026-11-05: diagnosing the repeated Standort
   failure (lesson M42) took about 20 turns: reproduce, compare with the previous version, trace. Delegated, it would
   have been two turns, the order and the reading of the report.
2. **Logs are the largest input**: 69 % of what came back was command output (test logs, greps, page extractions).
   A runner that returns a ten-line verdict removes most of it.
3. **Long sessions grow the context**: the p90 of 778 k is the end of a long session. A compact state handoff
   (branch, last commit, open tasks, last verdict) lets a new session start small. This is the cheapest lever of all.
4. **Output went largely into docs**: the doc updates of a feature (6–9 files) are a natural draft for an agent,
   reviewed by Claude as a diff.

## 3. Repetitive work worth automating

| Work (evidence in this repository) | Better as | Why |
|---|---|---|
| Run pytest / modeler / viewer / end-to-end, wait, read logs, find the failure | **Script** `pruefen`: suites in parallel where independent, one JSON verdict, failures with their first lines | No judgement needed; removes most Bash output from Claude's context |
| Check docs after a change: links and anchors, ranges (D1–D99, P1–P21, "54 checks"), the index | **Script** `doku-pruefen` | Deterministic; Claude wrote the same link checker twice by hand |
| Session start and end: state of branch, tests, open tasks | **Script** `stand` (+ an optional SessionStart hook) | Enables short sessions (§2, point 3) |
| Diagnose a failing test or check from its log and the code it names | **Agent** Testanalyst | A loop of reading and hypothesising; a 1 M-token model reads the whole area |
| Review a diff against the project rules (no PDF-specific rule, marked not hidden, IFC in metres …) | **Agent** Prüfer | Independent second opinion; findings with evidence |
| Draft the doc updates of a change (CHANGELOG, docs/21 section, decision and lesson stubs) | **Agent** Dokumentar | High Claude output today; a draft diff is easy to review |
| Write tests for a changed module | **Agent** Testautor | Kept only if they pass and catch an injected fault |
| Review screenshots of the app (two CSS collisions were found by eye on 2026-11-05) | **Agent** later (Gemini reads images) | Multimodal; low risk |
| Research (79 web searches in this session) | **Agent** later, with Google Search grounding | Paid per grounded query outside the free allowance; only on demand |

Not worth automating now: background agents on every save, CI calls to a model on every push (cost and noise),
agents that talk freely.

## 4. Google integration audit

### 4.1 The options

| Interface | State (2026-11-05) | Your subscription usable? | For this system |
|---|---|---|---|
| **Gemini CLI** (open source, npm 0.67.0) | Stopped serving the individual, AI Pro and Ultra tiers on 2026-06-18; "Login with Google" no longer works. API key, Vertex AI and Code Assist Standard/Enterprise still work | No | Possible with an API key, but it is an agent with a shell: more to sandbox than we need |
| **Antigravity CLI** (`agy`, closed source, since 2026-05-19) | Headless `agy -p`, `--output-format json`/`stream-json`, `--json-schema`; the JSON reports `usage` (input, output, thinking, cached tokens) and `num_turns`; login once interactively | Only for **your own local scripts, started by hand**. Google staff: Section 6 of the Antigravity Additional Terms prohibits wrapping `agy` inside third-party agents or apps; unattended or automatic requests are not supported on consumer plans and can trigger enforcement and lockouts | **Not as an agent of Claude Code.** Fine for you to use interactively next to it |
| **Gemini API** (AI Studio key; SDK `google-genai` 2.34.0) | Supported path for automation; per-call model choice, structured output, parallel calls within the rate limits, token counts in every response | Not the subscription: a separate key. Free tier without billing | **Recommended** |
| **Jules API** (`jules.googleapis.com/v1alpha`, alpha) | Google's asynchronous coding agent; sessions on a connected GitHub repository; key from the Jules settings (at most 3); plan approval optional; result as a pull request or in the session | **Yes**: "Jules in Pro" is a benefit of Google AI Pro (100 tasks per rolling 24 h, 15 concurrent; free: 15 and 3). The API is documented for automation ("automate tasks like bug fixing and code reviews") | **Recommended** as the implementing agent (§4.5) |
| Developer Program credits | $10 per month in Google Cloud credits for Google AI Pro ($100 for Ultra), activated at the Google Developer Program, applied to a Cloud project with billing; usable for the Gemini API | **Yes**, as money for paid API calls; with prepay billing a paid balance above $0 is needed to activate them | Pays for Argon escalations (§5.4) |
| Vertex AI | Paid Google Cloud project | No | Only if a company account and contract are wanted |
| MCP server around Gemini | Possible | – | Unnecessary: a command called by Claude through Bash costs the same and is simpler |

The cloud container reaches `generativelanguage.googleapis.com`, npm and pypi. No Gemini credential is present. A key
would come as an environment secret, never pasted into the chat.

### 4.2 Your Google AI Pro subscription, answered

1. **Programmatic access?**
   - Through `agy`: only when run by hand from your own script. Its quota works inside Google's own apps and cannot
     be called as a backend API (Google staff, 2026-10-28).
   - Through **Jules**: yes, with its official API and the higher limits of *Jules in Pro*.
   - Through the **Gemini API**: with the monthly Cloud credit (§4.5).
2. **Reuse the authentication?** No. Extracting or reusing the OAuth tokens is explicitly prohibited, and a cloud
   session could not hold your login safely anyway.
3. **Separate API billing?** Not for the free tier of the API (an AI Studio key, no billing). Paid models
   (`gemini-4-argon`) and higher limits need Cloud Billing on the project. Your $10 monthly credit is applied first,
   and with prepay billing nothing beyond the prepaid balance can be spent. Only with your approval.
4. **Models**: see §4.3.
5. **Parallel execution?** Yes, through the API, within the per-project rate limits.
6. **Limits**: the free-tier rate limits are no longer published; AI Studio shows them per project. Argon and 3.1 Pro
   have no free tier. Preview models are limited more tightly.
7. **Without extra cost?** Yes: the free tier of the API with an AI Studio key, and the agent package of §5.

The forum guidance is not consistent: a reply of 2026-09-15 called orchestration of `agy` supported, while the FAQ (as
quoted on 2026-10-27) and the staff reply of 2026-10-28 say otherwise. A lockout would hit your whole Google account.
The proposal therefore does not depend on the subscription at all.

### 4.3 Models and prices (Gemini API pricing page, read 2026-11-05)

| Model | Free tier | Paid, per 1 M tokens in / out | Use here |
|---|---|---|---|
| `gemini-3.5-flash-lite` | yes | $0.30 / $2.50 | Summaries of logs, classification, consistency checks |
| `gemini-3.8-flash` | yes | $0.75 / $3.75 until 2026-12-31 | **Default**: review, diagnosis, docs, tests |
| `gemini-3.1-flash-lite` | yes | $0.25 / $1.50 | Fallback for Flash-Lite |
| `gemini-4-argon` ("Argon") | **no** | $2 / $10 until 2026-11-30, then about double; Batch/Flex $1 / $5 | Escalation for high-risk reviews (extraction, modeler, IFC), only with a budget |
| `gemini-3.1-pro-preview` | no | $2 / $12 | Not needed next to Argon |
| Gemma 4 | yes (open weights) | – | Later: locally, for anything near confidential data |

"Argon" was checked, not assumed. It is the codename of Gemini 4, published as `gemini-4-argon` (Google's model page).
It has a 1,048,576-token unified context, at most 65,536 output tokens (up to 1 M with long decode), implicit caching
only, and Batch and Flex. It is a valid model, but it costs money from the first token.

### 4.4 Data and terms

- **The free tier can be read by people**: "human reviewers may read, annotate, and process your API input and output
  … Do not submit sensitive, confidential, or personal information to the Unpaid Services" (Gemini API Additional
  Terms).
- **In the EEA**, the data-use terms of the paid services apply to all services, including the unpaid ones (same
  terms). That covers you in Germany, but it is still processing by a third party.
- **For end users in the EEA**, Switzerland or the UK, an API client must use paid services only. That matters for a
  later product feature, not for development tools.
- **What may be sent:** files tracked in git. GroundTwin is published under the AGPL, so these are public anyway.
- **What is never sent:**
  - third-party PDFs and client Gutachten;
  - project folders (`ARBEIT`) and secrets;
  - **any blind-test PDF before its predictions are frozen and pushed** (the blind protocol of
    [CONTRIBUTING](../CONTRIBUTING.md)).

### 4.5 What the subscription does give, and how the system uses it

| Benefit of Google AI Pro | Programmatic? | Use in this system |
|---|---|---|
| **Jules in Pro**: 100 tasks per rolling 24 h, 15 concurrent, the latest Gemini Pro model | Yes, with the Jules API | **Umsetzer** (implementer): a task with a clear goal → Jules works on its own branch → a pull request. Claude reviews, CI runs, nothing is merged without Claude |
| **$10 per month in Google Cloud credits** (Developer Program; each grant valid one year) | Yes, as payment for Gemini API calls | Argon for high-risk reviews and hard diagnoses, capped by the orchestrator at the credit (for example $9 per month) |
| Higher quotas and Argon in the **AI Studio web interface** | No (web only) | For you, by hand: a second opinion on a module |
| **Antigravity** with the AI Pro quota (refresh every 5 hours, weekly cap) | Only scripted by hand | For you, interactively; never wrapped by Claude Code |
| **NotebookLM**, Deep Research | No | For you and the team: the docs of GroundTwin as a notebook (questions, audio overviews for the manager) |
| Colab compute units | No | Later, by hand: a GPU for OCR experiments or a local model |

Conditions:

- Paid Jules plans exist only for personal Google accounts ending in @gmail.com. These benefits belong to Google
  AI Pro (formerly Google One AI Premium); a Google AI Plus plan may not include them, so check the plan name in
  your Google One settings.
- Jules needs its GitHub app on the repository. It writes branches and pull requests; branch protection on `main`
  keeps every merge with a reviewed pull request.
- The Jules API is alpha: names may change. The adapter is small, so a change costs one file.

## 5. Recommended architecture

### 5.1 Principles

1. **Claude decides, agents propose.** Agents return findings and patches as text; nothing they write reaches the
   branch without Claude.
2. **Deterministic before generative.** Scripts for everything that needs no judgement (§3).
3. **Context is packed, not explored.** The orchestrator chooses the files for each task (cheap, auditable, no repo
   tools for the model). An agent may ask once for more files by path; the orchestrator serves them if they are
   allowed.
4. **Bounded exchanges.** Agents talk through a task's message log under a workflow with a fixed number of rounds.
   No free conversation, no agent starting agents.
5. **Measure, then grow.** Every model call and every delegating Claude turn is logged; a role stays only if it
   saves Claude tokens at equal quality.

### 5.2 Components and where they live

Code in German, like the rest of the repository; the docs in English.

```text
AGENTS.md                     shared spec for non-Claude agents (≤ 80 lines): the invariants of 16, the output protocol,
                              pointers into CLAUDE.md, 16, 17, 18, 21 – no copy of CLAUDE.md
agenten/                      Python package, development tool only (the product does not import it)
  __main__.py                 python -m agenten pruefen | doku-pruefen | stand | review | diagnose | doku | tests |
                              uebernehmen | kosten
  modelle.json                model registry: provider, id, tier, prices, limits, strengths, status
  anbieter/                   provider adapters behind one interface: gemini.py (google-genai), later anthropic,
                              openai, ollama (local Gemma)
  rollen/*.md                 roles: frontmatter (model policy, context recipe, output schema, permissions) + text
  ablaeufe/*.json             workflows: steps, parallel groups, peer rounds, stop rules
  kontext.py                  context packer: diff, traceback or symbol → files; budgets; allowlist (git ls-files),
                              denylist, secret scan
  ablauf.py                   runner: DAG with parallel steps, file ownership, worktrees, message log
  protokoll.py                metrics JSONL; Claude tokens from the transcript; cost estimate from the registry
  pruefen.py, doku.py         the deterministic runners of §3
.agenten/  (gitignored)       tasks, messages, reports, patches, worktrees, metrics
.claude/commands/             /pruefen, /review, /diagnose, /doku: one line each, calling python -m agenten
tests/test_agenten.py         offline tests with a fake provider (no network, no key)
```

The proposed `.google/` and `orchestration/` folders are not needed. With the API, Google reads nothing from the
repository, and the repository names its packages in German.

### 5.3 Roles

Dynamic: a role is instantiated per task, and several of the proposed roles share one.

| Role | Covers | Model policy | Context recipe | Output | Writes |
|---|---|---|---|---|---|
| **Prüfer** | code reviewer, security reviewer, IFC and geotechnics rules | 3.8 Flash; Argon for diffs in extractor, modeler, IFC or benchmark if a budget is set | the diff, the changed files whole, their tests, the relevant rules of 16 | findings: severity, file:line, claim, evidence, confidence | nothing |
| **Testanalyst** | test-failure analyst, regression analyst | 3.8 Flash; escalate on low confidence | the compressed log, files and lines of the traceback, recent diff of those files | cause, evidence, a minimal patch, confidence | patch as text |
| **Dokumentar** | documentation engineer, consistency | 3.5 Flash-Lite for checks, 3.8 Flash for drafts | the diff, the doc map (which notes name which modules), the style rules (English, German terms, links) | a doc patch + the list of claims it could not verify | patch as text |
| **Testautor** | test generation, QA | 3.8 Flash | the module, its existing tests, the fixtures | new tests as a patch | patch as text |
| **Umsetzer (Jules)** | backend, frontend and full-stack developer, refactoring | Jules (subscription, latest Gemini Pro), up to 15 at once | the task text, the files to touch, the tests that must pass, the protected files; Jules reads the repository itself in its VM | a pull request on its own branch | its branch only |
| later: UX-Prüfer, IFC-Fachmann, Rechercheur | UX, IFC 4.3/BIM, research | Flash (images), Argon (IFC), grounding | screenshots; IFC validation output; a question | findings | nothing |

### 5.4 Model selection

`modelle.json` holds every model with its tier, prices, context limit, strengths and status. `waehlen(rolle, auftrag)`
picks one per call:

1. Start from the role's default (§5.3).
2. Down to Flash-Lite when the input is a log summary or a check.
3. Up to Argon only when the task is high-risk (extractor, modeler, IFC, benchmark) **and** budget is left on the
   monthly Cloud credit, or after a Flash result with low confidence.
4. Implementation work goes to **Jules** when it is well specified (goal, files, tests), and to Claude when it needs
   the architecture in Claude's head.
5. Never a preview model by default. A retired model (for example 3.6 Flash on Vertex after 2026-11-19) falls back
   to its successor named in the registry.

A new provider is one adapter and a few registry lines. The Claude side stays Claude Code: Claude subagents save
main-thread context but are still Claude tokens, so they are not the default for delegable work.

### 5.5 Communication protocol

1. **Order.** Claude (or a script) writes one task: `{id, rolle, ziel, eingaben, schreibmenge, budget, ablauf}`.
   `schreibmenge` (the files a patch may touch) is locked; a second task with an overlapping set waits.
2. **Exchange.** Agents write messages to `.agenten/<id>/nachrichten.jsonl`:
   `{von, an, typ: befund|frage|antwort|patch|urteil, text ≤ 400 tokens, belege: [file:line], vertrauen}`.
   The workflow says who may answer whom and how often. Example *diagnose*:
   1. Testanalyst: cause + patch.
   2. Patch applied in a worktree, the named tests run.
   3. Prüfer: review of patch and test result.
   4. One revision round if the Prüfer objects.
   5. Stop.
   Example *umsetzen* (with Jules):
   1. Claude writes the task.
   2. Jules plans and implements on its branch.
   3. CI and the Prüfer (Gemini API) check the pull request.
   4. The Prüfer's findings go back to the Jules session as a message, at most twice.
   5. Claude reviews the final diff and merges or rejects it.
3. **Report.** Claude reads only `bericht.json` (≤ 2 KB): verdict, the merged findings, the patch path with its
   `--stat`, the tests run and their result, confidence, open questions, and the tokens and cost of the task.
4. **Decision.** Claude approves (`python -m agenten uebernehmen <id>` applies the patch to the working tree after
   Claude has seen it), asks for one revision, or orders an independent second review by another model.

### 5.6 Context management

- **Recipes per role** (§5.3) and a **budget per call** (for example 60 k tokens for Flash). The packer fills the
   budget by priority: the changed lines, the whole changed files, the callers, the tests, then the rules.
- **Allowed universe**: `git ls-files`, minus a denylist:
  - `benchmark/groundtruth/` of blind sets before release;
  - anything matching `*.pdf` outside synthetic test plans;
  - `.env*` and secrets;
  - `apps/web/dist`;
  - vendor files.
- **Secret scan** of every pack before it leaves (keys, tokens, passwords).
- **No repeated exploration**: a small index (module → files, tests, docs that name it) is rebuilt from git when it
  changes, so neither Claude nor an agent searches the repository again.
- The spec of every agent is `AGENTS.md` plus the rule lines its role names, not the whole of CLAUDE.md.

### 5.7 Security and permissions

| Risk | Answer |
|---|---|
| An agent changes production code | Gemini agents have no tools; patches are applied by the orchestrator in `git worktree` on a scratch branch only. Jules writes only its own branch; branch protection keeps `main` behind a reviewed pull request |
| Two agents on the same file | Write sets are locked per task; overlapping tasks wait |
| Critical files | **Protected**: `services/extractor/prototyp_v4.py`, `benchmark/baseline_v4.json`, `benchmark/groundtruth/**`, `constraints.txt`, CI workflows, `CLAUDE.md`, `LICENSE`. A patch touching one is refused unless Claude allows it explicitly for that task |
| Weakened tests | A patch that deletes or skips a test, or lowers a baseline, is refused automatically |
| Generated code accepted blindly | Claude reviews every patch; high-risk patches get an independent review by a second model |
| Costs | Paid models off by default; a daily and a per-task budget in the config; over budget → stop, not fallback to paid |
| Data | §4.4; the packer enforces it, not the prompt |

### 5.8 Observability

One JSON line per model call in `.agenten/metriken.jsonl`:
`{zeit, auftrag, rolle, anbieter, modell, tokens_ein, tokens_aus, tokens_denken, tokens_cache, dauer_ms, versuche,
erfolg, kosten_usd, kosten_art}`.

- Tokens are **actual** (the `usageMetadata` of each response).
- Costs are **estimates** from the registry prices, marked `kosten_art: "geschätzt"`.
- Claude's side is measured from the transcript, also actual: `python -m agenten kosten --seit <zeit>` sums the
  `usage` of the Claude calls in the window of a task.
- Delegation overhead is then visible per task: the Claude tokens of order plus review, against the turns the
  task would have taken.
- No dashboard: the JSONL is the interface for a later one.

### 5.9 Claude Code integration and the rule for delegating

- Commands in `.claude/commands/` (one line each). A short section in CLAUDE.md: when to delegate, how to read a
  report.
- **Delegate** when a task is expected to take three or more Claude turns or more than ~20 k tokens of reading (logs,
  large files). Do it inline when it is a single edit or needs project judgement Claude already holds.
- Later hooks:
  - SessionStart: print the `stand` (a few lines);
  - pre-commit: `doku-pruefen` and the fast tests.
  
  No background model calls.

## 6. Trade-offs

| Choice | Alternative | Why this one |
|---|---|---|
| Gemini API with packed context | `agy` or Gemini CLI as tool-using agents | Allowed by the terms; no shell to sandbox; exact token counts; the context we choose is the context we can audit. Cost: the agent cannot roam the repo. Mitigation: one "more files" round |
| Free tier first | Paid tier from the start | No cost without your approval; Flash suffices for review, diagnosis and docs. Cost: unpublished limits, no Argon |
| Four roles | One agent per proposed role | Fewer prompts to maintain; roles merge where the context and the output are the same |
| Scripts for checks | Agents for everything | Determinism; no tokens; the biggest measured saving (§2) |
| Bounded workflows | Free agent chat | Predictable cost and time; no recursive delegation |
| Logs in JSONL | A dashboard | Enough to decide whether delegation pays; a dashboard can read the same file later |

## 7. Roadmap

| Phase | Content | Accepted when |
|---|---|---|
| 3a, no model | `pruefen`, `doku-pruefen`, `stand`, metrics of the Claude side; `/pruefen` | The full check returns one verdict ≤ 15 lines; a known doc inconsistency is found; tests offline |
| 3b, MVP agents | `google-genai` adapter, registry, packer with denylist and secret scan, Prüfer and Testanalyst, the *diagnose* workflow with a worktree, `bericht.json`, `uebernehmen` | A fake-provider test suite; one real *diagnose* on a deliberately broken test (§7 Phase 4); no write outside the worktree; tokens logged |
| 3c, Jules | Jules adapter (sessions, plan, messages, pull request), the *umsetzen* workflow with the Prüfer, one GitHub app install and branch protection (your action) | One real small task (for example a test for `geodaten/laender.py`) done by Jules, reviewed, merged by Claude; Jules tasks and Claude tokens logged |
| 4, validation | Four real tasks, each once delegated and once inline, Claude tokens from the transcript: (1) diagnose a reintroduced bug (the radius of the LoD2 cut-out); (2) review commit `a7523cb`; (3) the docs of a small feature against the docs written by hand; (4) tests for `geodaten/laender.py` kept only if they catch an injected fault | A table of Claude tokens, Gemini tokens, time and quality per task; a role stays only where it saves |
| 5 | Dokumentar and Testautor if Phase 4 shows savings; UX-Prüfer for screenshots; hooks; Argon for high-risk reviews if you approve a budget | Each addition justified by the Phase 4 numbers |

## 8. Decisions needed from you

1. **Integration**:
   - the Gemini API with an AI Studio key for the reviewing and analysing roles;
   - **Jules** with your subscription for the implementing role;
   - not the subscription through `agy`.
2. **The keys**: create them without billing:
   - the Gemini key in Google AI Studio;
   - the Jules key in the Jules settings.
   
   Add them as `GEMINI_API_KEY` and `JULES_API_KEY`:
   - for cloud sessions, as an environment secret;
   - on your PC, in a git-ignored `.env`.
   
   Never in the repository or the chat.
3. **Data policy** of §4.4: only tracked files of the (public) repository, never client Gutachten, never blind PDFs.
4. **The monthly $10 credit**: activate it at the Google Developer Program and link a Cloud project with prepay
   billing. With prepay, the spend can never exceed what you deposited. Until then, paid models stay off.
5. **Jules on the repository**: install its GitHub app on `martinpazmino/GroundTwin`, and protect `main` (merge only
   with a reviewed pull request).
6. **Go for Phase 3a**: it needs no key and no decision above, and is useful on its own.

## 9. Sources (read 2026-11-05)

- [Gemini Code Assist for individuals: deprecation](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals), and the [Gemini CLI discussion #28017](https://github.com/google-gemini/gemini-cli/discussions/28017)
- [Antigravity CLI: headless mode](https://antigravity.google/docs/cli/headless/) and the [announcement](https://antigravity.google/blog/introducing-google-antigravity-cli/)
- Google AI Developers Forum: [policy clarification on subscription quota](https://discuss.ai.google.dev/t/policy-clarification-private-monitoring-app-using-official-antigravity-cli-and-subscription-quota/190756) (staff reply 2026-10-28) and [external orchestration of headless mode](https://discuss.ai.google.dev/t/is-external-orchestration-of-antigravity-cli-headless-mode-supported-with-account-based-usage/183051)
- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms), [Gemini 4 Argon](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon)
- [Gemini CLI headless mode](https://geminicli.com/docs/cli/headless/) (JSON statistics, for API-key use)
- [Google AI plans in the Gemini API docs](https://ai.google.dev/gemini-api/docs/google-ai-plans) (subscription benefits in the AI Studio UI only; Developer Program credits for the API), [Google blog: Developer Program premium in AI Pro and Ultra](https://blog.google/innovation-and-ai/technology/developers-tools/gdp-premium-ai-pro-ultra/) ($10 / $100 per month), [Google AI plans](https://one.google.com/about/google-ai-plans/)
- [Jules: limits and plans](https://jules.google/docs/usage-limits), [Jules API](https://developers.google.com/jules/api)
- Claude side: the `usage` records of the session transcript, measured with a script (§2)

Up: [Index](README.md)

Related: [16 Lessons](16_lessons_learned.md) · [11 Decisions](11_decisions.md) · [21 Step app](21_app_schritte_normen.md) · [22 Online](22_deployment.md) · [CONTRIBUTING](../CONTRIBUTING.md)
