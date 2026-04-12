# Task Spec

## Summary
- **Goal:** <!-- one sentence: what outcome are we achieving? -->
- **Why now:** <!-- why this matters -->
- **User impact:** <!-- who is affected and how -->
- **Owner:** team-lead
- **Last updated:** <!-- ISO date/time -->

## Context
<!--
Brief background and current behavior.
Include links to issue/PR if applicable.
State assumptions and constraints you must respect.
-->

## Goals
- <!-- G1 -->
- <!-- G2 -->

## Non-goals
- <!-- NG1 -->
- <!-- NG2 -->

## Acceptance Criteria
> Each AC must be objectively testable and mapped to evidence below.

### AC1 — <!-- short name -->
**Statement:** <!-- observable behavior/outcome -->
**Evidence (must provide at least one):**
- <!-- e.g., pytest -q tests/test_x.py::test_y -->
- <!-- e.g., CLI command output, deterministic log line, artifact path -->
**Negative / edge coverage:**
- <!-- error path / boundary case -->
**Notes:** <!-- optional -->

### AC2 — <!-- short name -->
**Statement:** <!-- observable behavior/outcome -->
**Evidence:**
- <!-- command/test -->
**Negative / edge coverage:**
- <!-- -->
**Notes:** <!-- optional -->

<!-- Add AC3..ACn as needed; prefer fewer strong ACs -->

## Validation Plan
> Prefer deterministic, CI-friendly commands. If “full suite” is too slow, specify a targeted subset and justify.

### Fast subset (required)
- Command(s):
  - `<!-- e.g., ./scripts/ci/quick_test.sh -->`
- Expected outcome:
  - <!-- pass/fail criteria -->

### Full suite (recommended when feasible)
- Command(s):
  - `<!-- e.g., ./scripts/ci/full_test.sh -->`
- Expected outcome:
  - <!-- pass/fail criteria -->

### Notes
- <!-- e.g., GitHub Actions may require maintainer approval to run on Copilot PRs; ensure local evidence is recorded. -->

## Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation | Detection |
|---|---|---|---|---|
| <!-- R1 --> | low/med/high | low/med/high | <!-- --> | <!-- test/metric/log --> |
| <!-- R2 --> | low/med/high | low/med/high | <!-- --> | <!-- --> |

## Rollback Plan
<!--
Keep this concrete and safe. Prefer:
- revert PR
- disable flag / config toggle (if exists)
- restore previous behavior
-->

1. <!-- Step 1 -->
2. <!-- Step 2 -->
3. <!-- Verification step -->

## Open Questions
- <!-- Q1 -->
- <!-- Q2 -->

## Traceability Matrix
> Map every AC to the exact evidence you will produce.

| Acceptance Criterion | Evidence (tests/commands/artifacts) | Owner Agent |
|---|---|---|
| AC1 | <!-- e.g., pytest -q tests/... --> | test-engineer |
| AC2 | <!-- e.g., ./scripts/ci/quick_test.sh --> | implementer |


