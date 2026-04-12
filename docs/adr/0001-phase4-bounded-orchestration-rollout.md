# ADR 0001: Bounded Orchestration Rollout After Phase 3

- Status: Accepted
- Date: 2026-04-09
- Deciders: team-lead, architecture-reviewer, quality-gate
- Related artifacts:
  - `docs/agents/task-spec.md`
  - `docs/agents/state.json`
  - `docs/agents/architecture-review-report.md`

## Context

Phase 3 completed the visibility-only continuation work. The repository now exposes continuation eligibility, review-aware readiness, governed review consensus, governed task lifecycle, and reviewed manual handoff visibility while keeping execution manual and `report_only`.

That creates a new risk: future orchestration work could jump directly from visibility to execution without an agreed prerequisite checklist, rollout order, or rollback posture. The next step must therefore stay in planning until the repository defines exactly what later orchestration slices may and may not do.

## Decision

The repository will treat post-Phase-3 orchestration as a bounded multi-slice rollout rather than a single feature switch.

### Prerequisites for any later orchestration implementation slice

1. Phase 3 visibility signals remain the required baseline:
   - `continuationEligibility`
   - `continuationReadiness`
   - `governedReviewConsensus`
   - `governedTaskLifecycle`
   - `reviewedContinuationHandoff`
2. Any later orchestration slice must preserve deterministic-first ranking and must not allow live or external signals to bypass existing guardrails.
3. Any later orchestration slice must keep rollback explicit and reversible through governed artifacts and generated run artifacts.
4. Any later orchestration slice must remain review-gated and must not assume unattended execution authority from Phase 3 completion alone.

### Hard non-goals for the planning slice

This planning slice does not:

- enable schedulers, queues, daemons, watchers, or background continuation
- enable autonomous apply, autonomous resume, or unattended continuation
- integrate GitHub review APIs, CI status APIs, or external dispatch systems
- change the current manual or `report_only` runtime behavior

### Rollout order

The rollout after this planning slice must remain bounded and reviewable:

1. First bounded implementation slice:
   add orchestration contract metadata or staged dispatch simulation only, while preserving manual and `report_only` execution semantics.
2. Later slice, only if the first slice is complete and reviewed:
   add a reviewed dispatch intent that still does not execute automatically.
3. Any execution-capable orchestration work:
   requires a separate future planning and approval step and is not authorized by this ADR.

### Rollback posture

If a later orchestration slice creates ambiguity about execution authority, rollback must restore the prior manual and `report_only` semantics and remove any new orchestration metadata that implies dispatch readiness beyond reviewed manual handoff.

## Consequences

### Positive

- Prevents scope creep from Phase 3 visibility into accidental execution behavior.
- Gives later implementation slices a concrete checklist and rollout order.
- Keeps planning and implementation boundaries explicit in governed artifacts.

### Negative

- Adds one more planning step before implementation can continue.
- Requires future slices to stay smaller and more incremental than an all-at-once orchestration feature.

### Follow-on work

The next bounded implementation slice should define an orchestration contract layer or staged dispatch simulation that remains manual, `report_only`, reversible, and review-gated.
