# Task Spec: <short title>

> Owner: Spec Writer  
> Status: DRAFT | FINAL  
> Source inputs: <links to ResearchReport / issue / PR / chat>  
> Target branch/PR: <branch or PR link if known>

## Summary
One paragraph: problem statement + intended user-visible outcome.

## Context
- Why this matters (user impact / bug impact / operational impact)
- Current behavior (include repro summary)
- Constraints from manager (no API change, keep diff minimal, etc.)

## Goals
- G1: …
- G2: …

## Non-goals
- NG1: …
- NG2: …

## Acceptance Criteria
Use **AC1..ACn**. Each AC must be objectively testable.

| ID | Statement (observable) | Evidence (tests/commands) | Negative / edge cases |
|---|---|---|---|
| AC1 | … | `…` | … |
| AC2 | … | `…` | … |

## Validation Plan
### Fast subset (CI-friendly)
```bash
# smallest set of commands covering all ACs
…
```

### Full suite (full confidence)
```bash
…
```

### Notes
- Setup prerequisites (only if required):
  - …

## Risks & Mitigations
| Risk | Detection | Mitigation |
|---|---|---|
| … | … | … |

## Rollback Plan
Concrete steps to undo safely:
1. …
2. …

## Open Questions
If anything is ambiguous or conflicting:
- Q1: …
- Q2: …

## Traceability Matrix
Map each AC to tests/commands and expected evidence.

| AC | Tests/commands | Expected evidence |
|---|---|---|
| AC1 | `…` | exit 0; log contains … |
| AC2 | `…` | … |


