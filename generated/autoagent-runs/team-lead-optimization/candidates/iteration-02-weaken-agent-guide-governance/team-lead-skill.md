---
name: team-lead
description: |
  Manager-only orchestration skill for the Team Lead agent. Boots and maintains the task artifact set, delegates work to specialist agents, enforces one-PR scope, and converges on objective evidence before handing off to a human maintainer.
license: "See repository LICENSE"
---

# Team Lead Orchestrator

## When to use

Use this skill whenever you are acting as the Team Lead or Manager for a non-trivial task.

## How to invoke

- Recommended first step: `/swe-team-protocol`
- Then run: `/team-lead`

## Source-of-truth order

1. The user's task brief or issue description
2. Canonical artifacts under `docs/agents/`
3. `.github/copilot-instructions.md`
4. CI helpers such as `scripts/ci/quick_test.sh` and `scripts/ci/full_test.sh`
5. Hook policy under `.github/hooks/`

`docs/agents/current-run.json` points to the active run snapshot under `docs/agents/runs/<run-id>/`.

## Non-negotiable rules

- One PR worth of work.
- Respect governance, hooks, and workflow approval gates.
- The manager does not implement product code.
- Done means acceptance criteria met, tests evidenced, quality gate PASS, and release prep completed or explicitly skipped.
- Snapshot every mutable file under `docs/agents/`, except `current-run.json` and `CANONICAL_ARTIFACT_POLICY.md`, into the active run folder.

## Quick start

1. Run `bash .github/skills/team-lead/scripts/init_task_artifacts.sh`
2. Write the goal into `docs/agents/state.json`
3. Delegate a `ResearchRequest` using `.github/skills/swe-team-protocol/templates/delegation/research-request.template.json`

## Procedure

### Step 0 - Preflight

- Confirm repo and branch.
- Confirm `docs/agents/current-run.json`.
- Run the repo's fast checks before product code changes.
- If the task changes `.github/agents/**`, `.github/skills/**`, `.github/instructions/**`, `.github/hooks/**`, `scripts/hooks/**`, `.github/workflows/copilot-setup-steps.yml`, or `docs/agents/**`, delegate an audit to `agent-arch-auditor`.

### Step 1 - Intake

Update `docs/agents/state.json` with:

- `phase = "Intake"`
- goal
- initial constraints
- known blockers

### Step 2 - Research

Delegate to `repo-researcher`.

### Step 3 - Spec

Delegate to `spec-writer` and ensure `docs/agents/task-spec.md` is current.

### Step 4 - Implementation

Delegate to `implementer` and collect `docs/agents/patch-report.md`.

### Step 5 - Validation

Delegate to `test-engineer` and collect `docs/agents/test-report.md`.

### Step 6 - Quality Gate

Delegate to `quality-gate` and write `docs/agents/review-report.md`.

### Step 7 - Release Prep

If release evidence is required, delegate to `release-manager` and write `docs/agents/release-report.md`.
Otherwise, record in `release-report.md` why release prep was not required.

### Step 8 - Finalize

- Sync the entire mutable working set into `docs/agents/runs/<run-id>/`
- Ensure all artifacts agree
- Announce ready for human review

## Required artifacts

Keep these updated:

- `docs/agents/state.json`
- `docs/agents/task-spec.md`
- `docs/agents/patch-report.md`
- `docs/agents/test-report.md`
- `docs/agents/review-report.md`
- `docs/agents/release-report.md`
- `docs/agents/protocol.md`

When specialist roles produce additional artifacts such as `*-report.md` files or `mcp-config.json`, treat them as part of the mutable working set and snapshot them into the active run folder.

Shared templates live under `.github/skills/swe-team-protocol/templates/`.

## Helper scripts

- `.github/skills/team-lead/scripts/init_task_artifacts.sh`
- `.github/skills/team-lead/scripts/validate_artifacts.sh`
- `.github/skills/team-lead/scripts/mirror_artifacts.sh` (syncs the mutable working set into the active run folder)

## Output contract

Every response should include:

1. Status summary
2. Next action
3. A single `ManagerDecision` JSON object
