# Task Spec

## Summary
- **Goal:** Implement the smallest Phase 5F runtime slice that keeps AutoAgent manual and `report_only` while enabling explicit chat, transcript, and handoff evidence ingestion plus deterministic reasoning-path efficiency scoring in learning artifacts.
- **Why now:** The runtime already supports opt-in chat, transcript, and handoff history parsing, but the active experiment still runs with zero external log records and no explicit named signal for the shortest successful reasoning path. Your intention is to learn from actual reasoning traces, so the next bounded step is to make that path signal real and reviewer-visible.
- **User impact:** Maintainers can point AutoAgent at governed repo-local chat, transcript, and handoff logs, see transcript and handoff uptake in the evidence dataset and canonical report, and evaluate the straightest successful reasoning paths through an explicit deterministic efficiency signal without widening execution authority.
- **Owner:** team-lead
- **Last updated:** 2026-04-12T18:44:48.0272715-04:00

## Context
Phase 5A through Phase 5E are complete:
- explicit handoff-aware evidence attribution exists and remains review-only
- advisory shadow-learning factors already surface deterministic rationale in learning payloads
- guarded learning review manifests can stage benchmark and policy drafts for human review
- manual `import_learning_review()` emits `learning-promotion-audit.json` with staged decisions, reviewer overrides, and per-entry `decisionRationale`
- reruns already expose reviewer-facing promotion-audit summaries and blocked-factor aggregation in canonical reporting

The current runtime already has the raw mechanics needed for your goal, but they are not yet active as a coherent learning slice:
- the evidence policy already supports `includeChatHistory`, `includeTranscriptHistory`, `includeHandoffHistory`, and explicit external log sources
- transcript and handoff parsing already extracts candidate ids, lineage candidate ids, handoff references, tool names, transcript text, and derived statuses
- the current checked-in report still shows zero external log records, zero transcript records, and zero handoff records in the active experiment output
- the current shadow-learning score already considers action count, search depth, handoff count, handoff efficiency, and tool churn, but it does not expose an explicit reviewer-facing reasoning-path-efficiency signal

This implementation slice stays intentionally narrow:
- wire explicit repo-local chat, transcript, and handoff evidence into the experiment contract and deterministic tests
- surface transcript and handoff uptake in the evidence dataset, learning summary, and canonical report
- add an explicit deterministic reasoning-path-efficiency signal for observed-path learning and derivative review-only draft artifacts
- keep learning promotion manual and review-only with no auto-apply, auto-import, or unattended execution behavior

Constraints:
- Keep execution manual and `report_only`; do not enable schedulers, queues, watchers, autonomous continuation, autonomous apply-best, approval APIs, or execution-capable orchestration.
- Keep guarded learning promotion review-only; do not auto-import, auto-apply, or auto-activate benchmark, mutation, or policy drafts.
- Preserve explicit opt-in evidence controls, redaction, truncation, and the default external-path restrictions; do not broaden evidence collection into uncontrolled editor or filesystem harvesting.
- Keep the reasoning-path signal deterministic and implementation-local; do not introduce semantic LLM judging, opaque classifiers, network calls, or non-replayable heuristics.
- Preserve existing benchmark quality, terminal outcome, and reviewed-policy boundaries; any new reasoning-path signal must remain bounded and explainable.
- Keep validation deterministic and offline, using repo-local fixtures or governed artifacts rather than live personal chat history.
- Keep governed artifacts under `docs/agents/` mirrored into the active run snapshot.

## Goals
- Enable explicit repo-local chat, transcript, and handoff evidence ingestion in the active AutoAgent contract.
- Surface transcript and handoff evidence uptake in the evidence dataset, learning summary, and canonical report.
- Expose a named deterministic reasoning-path-efficiency signal so reviewers can see and compare the straightest successful paths.
- Preserve manual, review-only learning boundaries while aligning the implementation more directly with your autonomy roadmap.

## Non-goals
- Do not enable unattended execution, schedulers, approval workflows, or autonomous continuation.
- Do not auto-import, auto-apply, or auto-activate trace-derived drafts.
- Do not ingest arbitrary user-private logs by default or disable redaction or external-path controls.
- Do not introduce semantic free-text judging of transcript content through a model or remote service.
- Do not replace benchmark quality or terminal outcome as the primary truth source for success versus failure classification.

## Acceptance Criteria
> Each AC must be objectively testable and mapped to evidence below.

### AC1 — Explicit Transcript And Handoff Evidence Ingestion Works Under Opt-In Control
**Statement:** When repo-local evidence-policy paths are explicitly configured, `run_autoagent_loop()` ingests chat, transcript, and handoff records into the evidence dataset and surfaces non-zero transcript and handoff record counts plus source summaries in generated artifacts.
**Evidence:**
- `.github/skills/autoagent-loop/scripts/autoagent_loop.py`
- `docs/agents/autoagent-experiment.md`
- `tests/test_autoagent_loop_runner.py`
**Negative / edge coverage:**
- Missing optional transcript or handoff sources must remain non-fatal.
- With opt-in flags disabled, transcript and handoff counts must remain zero.
- Redaction and external-path restrictions must remain in force unless explicitly allowed.

### AC2 — Learning Exposes A Deterministic Reasoning-Path Efficiency Signal
**Statement:** Trace-backed learning surfaces a named deterministic reasoning-path-efficiency signal for observed paths and derived suggestions, rewarding shorter successful paths with fewer unnecessary handoffs and lower tool churn when outcome quality is otherwise equal.
**Evidence:**
- `.github/skills/autoagent-loop/scripts/autoagent_loop.py`
- `tests/test_autoagent_loop_runner.py`
- `docs/agents/patch-report.md`
**Negative / edge coverage:**
- The new signal must remain deterministic and explainable.
- The implementation must not rely on semantic LLM judgment of transcript text.
- Benchmark quality and terminal outcome must continue to dominate clearly worse paths.

### AC3 — Source-Backed Reasoning Metrics Are Visible In Learning Artifacts And Canonical Reporting
**Statement:** The canonical AutoAgent report and review-only learning draft artifacts surface transcript or handoff provenance and the new reasoning-path-efficiency signal so reviewers can see which traces drove each learned suggestion.
**Evidence:**
- `.github/skills/autoagent-loop/scripts/autoagent_loop.py`
- `tests/test_autoagent_loop_runner.py`
- `docs/agents/autoagent-report.md`
**Negative / edge coverage:**
- Absent transcript or handoff evidence must render explicit zero or `none` visibility rather than implying hidden trace inputs.
- Draft artifacts must remain review-only and human-auditable.

### AC4 — Manual And Review-Only Boundaries Remain Intact While Governed Artifacts Stay In Sync
**Statement:** Even with transcript or handoff evidence and explicit reasoning-path-efficiency metrics, execution remains manual and `report_only`, guarded learning promotion remains review-only, and the touched governed root and run-scoped artifacts reflect the active Phase 5F slice and validation evidence.
**Evidence:**
- `docs/agents/state.json`
- `docs/agents/task-spec.md`
- `docs/agents/autoagent-report.md`
- `docs/agents/runs/20260308-160258/`
**Negative / edge coverage:**
- No auto-import, auto-apply, auto-activate, approval-authority, or execution-authority expansion is permitted.
- Root and run-scoped copies for touched governed artifacts must match exactly.

## Validation Plan
### Fast subset (required)
- Command(s):
  - `New-Item -ItemType Directory -Force .tmp-pytest | Out-Null; $env:TMP = (Resolve-Path .tmp-pytest).Path; $env:TEMP = $env:TMP; py -3 -m pytest tests/test_autoagent_loop_runner.py -k "transcript or handoff or reasoning_path"`
- Expected outcome:
  - Focused runner coverage proves repo-local transcript or handoff ingestion and the deterministic reasoning-path-efficiency signal on representative fixture-backed paths.

### Full targeted suite (required)
- Command(s):
  - `New-Item -ItemType Directory -Force .tmp-pytest | Out-Null; $env:TMP = (Resolve-Path .tmp-pytest).Path; $env:TEMP = $env:TMP; py -3 -m pytest tests/test_autoagent_loop_runner.py`
- Expected outcome:
  - The full deterministic AutoAgent runner file passes, confirming the new evidence-ingestion and reasoning-efficiency fields do not regress broader loop behavior.

### Governed artifact validation (required)
- Command(s):
  - `py -3 .github/skills/autoagent-loop/scripts/autoagent_loop.py --experiment docs/agents/autoagent-experiment.md --output-root generated/autoagent-runs --report docs/agents/autoagent-report.md --results docs/agents/autoagent-results.tsv --evidence docs/agents/autoagent-evidence.json`
  - `py -3 -m json.tool docs/agents/state.json > $null`
  - `py -3 -c "from pathlib import Path; pairs=[('docs/agents/task-spec.md','docs/agents/runs/20260308-160258/task-spec.md'),('docs/agents/state.json','docs/agents/runs/20260308-160258/state.json'),('docs/agents/autoagent-report.md','docs/agents/runs/20260308-160258/autoagent-report.md'),('docs/agents/autoagent-results.tsv','docs/agents/runs/20260308-160258/autoagent-results.tsv'),('docs/agents/autoagent-evidence.json','docs/agents/runs/20260308-160258/autoagent-evidence.json')];\nfor left,right in pairs:\n    assert Path(left).read_text(encoding='utf-8') == Path(right).read_text(encoding='utf-8')"`
- Expected outcome:
  - The canonical AutoAgent artifacts regenerate successfully, the governed state remains machine-parseable, and the touched root and run artifacts stay synchronized.

## Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation | Detection |
|---|---|---|---|---|
| Transcript or handoff logs could expose sensitive content or private local paths | high | medium | Preserve redaction, truncation, and external-path restrictions by default and keep tests on repo-local fixtures only | evidence dataset inspection and focused regression coverage |
| Real trace ingestion could make results non-deterministic if the slice depends on live editor history | high | medium | Keep validation fixture-backed and offline; do not require live user chat logs for tests or canonical regeneration | focused and full runner regression |
| A new reasoning-path metric could become subjective or opaque | high | low | Keep the signal deterministic, bounded, and derived from explicit structural factors like actions, handoffs, depth, and tool churn | code review and exact-factor test assertions |
| The new signal could overwhelm benchmark quality and promote superficially short but low-quality paths | high | medium | Bound the signal so benchmark quality and terminal outcome remain primary and require deterministic negative coverage on lower-quality paths | focused ranking assertions and full runner regression |
| Root and run-scoped artifacts could diverge while the slice is being closed out | medium | medium | Mirror all touched governed artifacts into the active run snapshot and validate parity explicitly | parity validation command |

## Rollback Plan
1. Restore `.github/skills/autoagent-loop/scripts/autoagent_loop.py`, `tests/test_autoagent_loop_runner.py`, and `docs/agents/autoagent-experiment.md` to the prior Phase 5E baseline if maintainers do not want to keep transcript-backed reasoning-path learning.
2. Restore `docs/agents/task-spec.md`, `docs/agents/state.json`, `docs/agents/autoagent-report.md`, `docs/agents/autoagent-results.tsv`, and `docs/agents/autoagent-evidence.json` from the prior snapshot.
3. Restore the matching run-scoped copies under `docs/agents/runs/20260308-160258/`.
4. Leave execution manual and `report_only`; no migration or release rollback step is required because this slice does not widen shipped execution authority.

## Open Questions
- None. This slice intentionally chooses deterministic structural reasoning-path signals over semantic transcript judging.

## Traceability Matrix
| Acceptance Criterion | Evidence (tests/commands/artifacts) | Owner Agent |
|---|---|---|
| AC1 | explicit transcript and handoff evidence-policy ingestion plus fixture-backed runner assertions | implementer |
| AC2 | deterministic reasoning-path-efficiency signal wiring and focused ranking assertions | implementer |
| AC3 | canonical report and review-only learning draft visibility for source-backed reasoning metrics | implementer |
| AC4 | refreshed governed state, regenerated canonical artifacts, and root-run parity validation | team-lead |
