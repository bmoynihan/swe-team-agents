# Task Spec

## Summary
- **Goal:** Broaden the checked-in AutoAgent governed manager bundle to include `AGENTS.md` and keep the experiment manual, deterministic, and `report_only`.
- **Why now:** The staged review-bundle slice is complete and validated. The next highest-value bounded step is to prove the checked-in target bundle scales across one more repo-level governance artifact before spending another slice on reviewer ergonomics or continuation behavior.
- **User impact:** Maintainers get a more representative checked-in manager bundle that covers the repo-level operating guide as well as the Team Lead profile and skill, while keeping the same review-first execution boundary.
- **Owner:** team-lead
- **Last updated:** 2026-04-14T21:25:00Z

## Context
The current checked-in AutoAgent experiment already supports a small manager bundle:
- `.github/agents/team-lead.agent.md` carries the highest-signal Team Lead tool surface and output contract
- `.github/skills/team-lead/SKILL.md` carries the shared manager workflow rules
- the staged review-bundle slice proved the runtime can serialize and report bundle-level review artifacts without widening execution authority

This slice is deliberately bounded:
- add `AGENTS.md` as one more governed manager-shared target in the checked-in experiment
- add explicit benchmark checks for the AGENTS current-run, shared-root, and hook-governance contract
- add one AGENTS-specific negative regression mutation that weakens the repo-level governance language
- preserve manual and `report_only` semantics in the checked-in experiment and generated artifacts
- refresh the canonical AutoAgent run once after the bundle extension

## Goals
- Add `AGENTS.md` as a third checked-in optimization target in `docs/agents/autoagent-experiment.md`.
- Extend the checked-in Team Lead benchmark with AGENTS-specific governance checks.
- Extend the checked-in mutation catalog with an AGENTS-specific negative governance-regression mutation.
- Update deterministic pytest coverage so the checked-in bundle contract is locked to the expanded governed bundle.
- Refresh the canonical AutoAgent artifacts with one manual rerun of the checked-in experiment.

## Non-goals
- Do not enable unattended continuation, approval APIs, scheduling, queues, watchers, or services.
- Do not auto-apply the best candidate to the checked-in manager bundle.
- Do not widen the checked-in bundle into specialist agent profiles, hooks, or broader non-manager guidance.
- Do not change runtime ranking logic or reviewed-continuation packaging beyond what is needed to extend the checked-in governed bundle inputs.
- Do not weaken redaction, truncation, or external-path guardrails.

## Acceptance Criteria
> Each AC must be objectively testable and mapped to evidence below.

### AC1 — The Checked-In Experiment Includes AGENTS.md As A Governed Bundle Target
**Statement:** The checked-in AutoAgent experiment includes `AGENTS.md` as a third governed manager target alongside the Team Lead profile and Team Lead skill without changing the experiment’s manual or `report_only` posture.
**Evidence:**
- `docs/agents/autoagent-experiment.md`
- `AGENTS.md`
- `tests/test_autoagent_loop_runner.py`
**Negative / edge coverage:**
- The added target must stay within manager-shared guidance rather than specialist profiles or execution-capable assets.
- The experiment must remain manual and `report_only`.

### AC2 — Benchmark And Mutation Inputs Cover The New AGENTS Governance Contract
**Statement:** The checked-in Team Lead benchmark and mutation catalog include AGENTS-specific checks and a negative governance-regression mutation that the bundle search can evaluate deterministically.
**Evidence:**
- `.github/skills/autoagent-loop/examples/team-lead-benchmark.json`
- `.github/skills/autoagent-loop/examples/team-lead-mutations.json`
- `AGENTS.md`
**Negative / edge coverage:**
- The new mutation must stay negative and governance-focused rather than testing unrelated stylistic drift.
- The checked-in bundle must remain manager-only.

### AC3 — Deterministic Coverage Locks The Expanded Governed Bundle Contract
**Statement:** Focused deterministic pytest coverage proves the checked-in experiment now targets the Team Lead profile, Team Lead skill, and `AGENTS.md`, and that the benchmark and mutation catalog contain the expected AGENTS governance assertions.
**Evidence:**
- `tests/test_autoagent_loop_runner.py`
- `docs/agents/autoagent-experiment.md`
- `.github/skills/autoagent-loop/examples/team-lead-benchmark.json`
- `.github/skills/autoagent-loop/examples/team-lead-mutations.json`
**Negative / edge coverage:**
- Validation must stay offline and deterministic.
- The checked-in experiment must remain manual and `report_only`.

### AC4 — Canonical And Governed Artifacts Reflect The Broader Governed Bundle Slice
**Statement:** The canonical AutoAgent outputs plus the governed task, patch, test, review, release, and active run snapshot artifacts are updated for the broader governed bundle slice and remain machine-parseable.
**Evidence:**
- `docs/agents/task-spec.md`
- `docs/agents/state.json`
- `docs/agents/autoagent-report.md`
- `docs/agents/autoagent-results.tsv`
- `docs/agents/autoagent-evidence.json`
- `docs/agents/patch-report.md`
- `docs/agents/test-report.md`
- `docs/agents/review-report.md`
- `docs/agents/release-report.md`
- `docs/agents/runs/20260308-160258/`
**Negative / edge coverage:**
- Root and run-scoped copies of touched governed artifacts must match exactly.
- The slice must not claim unattended or autonomous execution.

## Validation Plan
### Focused staged-bundle regression (required)
- Command(s):
  - `py -3 -m pytest tests/test_autoagent_loop_runner.py::test_autoagent_loop_report_includes_staged_patch_and_provenance tests/test_autoagent_loop_runner.py::test_checked_in_autoagent_experiment_uses_manager_bundle_targets tests/test_autoagent_loop_runner.py::test_autoagent_loop_imports_approved_learning_drafts_with_review_manifest --basetemp ./.tmp/pytest-staged-bundle`
- Expected outcome:
  - The expanded checked-in governed bundle contract and the existing review-bundle and reviewed-learning paths remain deterministic.

### Canonical AutoAgent rerun (required)
- Command(s):
  - `py -3 scripts/run_autoagent_loop.py --experiment docs/agents/autoagent-experiment.md`
- Expected outcome:
  - The canonical AutoAgent report, results, evidence, trace, and generated staged patch review bundle refresh successfully under the expanded governed manager bundle.

### Governed artifact validation (required)
- Command(s):
  - `pwsh -File ./scripts/ci/quick_test.ps1`
  - `py -3 -m json.tool docs/agents/state.json > $null`
  - `py -3 -c "from pathlib import Path; pairs=[('docs/agents/task-spec.md','docs/agents/runs/20260308-160258/task-spec.md'),('docs/agents/state.json','docs/agents/runs/20260308-160258/state.json'),('docs/agents/patch-report.md','docs/agents/runs/20260308-160258/patch-report.md'),('docs/agents/test-report.md','docs/agents/runs/20260308-160258/test-report.md'),('docs/agents/review-report.md','docs/agents/runs/20260308-160258/review-report.md'),('docs/agents/release-report.md','docs/agents/runs/20260308-160258/release-report.md'),('docs/agents/autoagent-experiment.md','docs/agents/runs/20260308-160258/autoagent-experiment.md'),('docs/agents/autoagent-report.md','docs/agents/runs/20260308-160258/autoagent-report.md'),('docs/agents/autoagent-results.tsv','docs/agents/runs/20260308-160258/autoagent-results.tsv'),('docs/agents/autoagent-evidence.json','docs/agents/runs/20260308-160258/autoagent-evidence.json')]; assert all(Path(left).read_text(encoding='utf-8') == Path(right).read_text(encoding='utf-8') for left,right in pairs); print('PARITY_OK')"`
- Expected outcome:
  - The governed docs remain machine-parseable, the repo fast suite passes, and all touched root and run-scoped artifacts remain synchronized.

## Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation | Detection |
|---|---|---|---|---|
| The third target could expand the checked-in bundle into guidance that is too broad or noisy for stable deterministic coverage | high | medium | Limit the new target to `AGENTS.md` and add only governance-specific benchmark checks | focused pytest and canonical rerun |
| The new AGENTS mutation could be too weak to prove a meaningful regression | medium | medium | Target the shared-root and hook-denial language that the benchmark checks explicitly guard | canonical rerun and results review |
| Root and run-scoped governed artifacts could diverge while refreshing this slice | medium | medium | Mirror each touched artifact into the active run snapshot and run parity validation explicitly | parity validation command |

## Rollback Plan
1. Restore `docs/agents/autoagent-experiment.md`, `.github/skills/autoagent-loop/examples/team-lead-benchmark.json`, `.github/skills/autoagent-loop/examples/team-lead-mutations.json`, `tests/test_autoagent_loop_runner.py`, and the touched `docs/agents/` artifacts from the prior snapshot if maintainers do not want to keep the broader governed bundle slice.
2. Restore the matching canonical generated artifacts if maintainers do not want to keep the `AGENTS.md` bundle extension.
3. Restore the matching run-scoped copies under `docs/agents/runs/20260308-160258/`.

## Open Questions
- None. This slice is intentionally limited to one more manager-shared governed target and preserves the current manual/report-only execution boundary.

## Traceability Matrix
| Acceptance Criterion | Evidence (tests/commands/artifacts) | Owner Agent |
|---|---|---|
| AC1 | checked-in experiment target bundle plus focused pytest coverage | implementer |
| AC2 | benchmark and mutation catalog updates for AGENTS governance | implementer |
| AC3 | focused pytest coverage for the expanded bundle contract | implementer |
| AC4 | refreshed governed lifecycle artifacts, JSON validation, and parity validation | quality-gate |
