# Task Spec

## Summary
- **Title:** <!-- short, specific -->
- **Goal:** <!-- one sentence outcome -->
- **Owner:** team-lead
- **Source:** <!-- issue/pr/manual + link/ID -->
- **Last updated:** <!-- ISO date/time -->

## Context
<!--
What is the current behavior and what should change?
Include links, screenshots, logs, or minimal repro notes as needed.
State constraints (no API change, backwards compatibility, etc.).
-->

## Goals
- <!-- G1 -->
- <!-- G2 -->

## Non-goals
- <!-- NG1 -->
- <!-- NG2 -->

## Acceptance Criteria
> Acceptance criteria must be objectively testable. Prefer fewer, stronger ACs.

### AC1 — <!-- name -->
**Statement:** <!-- observable behavior/outcome -->
**Evidence (must provide at least one):**
- <!-- test/command + expected result -->
**Negative / edge coverage:**
- <!-- -->
**Notes:** <!-- optional -->

### AC2 — <!-- name -->
**Statement:** <!-- -->
**Evidence:**
- <!-- -->
**Negative / edge coverage:**
- <!-- -->
**Notes:** <!-- -->

## Validation Plan

### Fast subset (required)
- Command(s):
  - `<!-- e.g., ./scripts/ci/quick_test.sh -->`
- Expected:
  - <!-- what “pass” means -->

### Full suite (recommended)
- Command(s):
  - `<!-- e.g., ./scripts/ci/full_test.sh -->`
- Expected:
  - <!-- -->

### Notes
- <!-- e.g., if CI won’t auto-run on Copilot PRs until approved, record local evidence -->

## Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation | Detection |
|---|---|---|---|---|
| <!-- --> | low/med/high | low/med/high | <!-- --> | <!-- test/metric/log --> |

## Rollback Plan
1. <!-- revert/disable/restore -->
2. <!-- verify rollback -->

## Open Questions
- <!-- -->

## Traceability Matrix
| Acceptance Criterion | Evidence (tests/commands/artifacts) | Owner Agent |
|---|---|---|
| AC1 | <!-- --> | test-engineer |
| AC2 | <!-- --> | implementer |

