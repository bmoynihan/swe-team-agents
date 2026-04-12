---
name: agent-arch-auditor
description: >
  Use when adding, auditing, or repairing the GitHub Copilot agent system in this repository.
  Covers custom agents, skills, instructions, hooks, setup workflow, artifact ownership, and deterministic run behavior.
---

# Agent Architecture Auditor

## When to use
Use this skill when a task changes or audits any of:
- `.github/agents/**`
- `.github/skills/**`
- `.github/instructions/**`
- `.github/hooks/**`
- `scripts/hooks/**`
- `.github/workflows/copilot-setup-steps.yml`
- `docs/agents/**`
- `scripts/ci/check_agent_system.py`

Use it for both read-only audits and smallest-safe remediation of the Copilot agent substrate.

## How to invoke
- In Copilot prompt: `/agent-arch-auditor`
- In a multi-agent team: have the Team Lead ask the Agent Architecture Auditor to use `/agent-arch-auditor` and write the report.

## Inputs (source-of-truth order)
1. `docs/agents/CANONICAL_ARTIFACT_POLICY.md`
2. `docs/agents/current-run.json`
3. `AGENTS.md`
4. `.github/copilot-instructions.md`
5. `.github/instructions/**`
6. `.github/agents/**`
7. `.github/skills/**`
8. `.github/hooks/**` and `scripts/hooks/**`
9. `.github/workflows/copilot-setup-steps.yml`
10. `docs/agents/**`

## Non-negotiable rules
- Use only supported GitHub conventions.
- Keep findings evidence-first, with exact paths.
- Treat duplicate canonical artifacts and competing owners as real defects.
- Prefer the smallest safe patch set when asked to remediate.
- Do not modify product code unless the task explicitly includes it.

## Procedure

### Step 1 - Inventory the agent-system surface
- Run `bash .github/skills/agent-arch-auditor/scripts/inventory_agent_surface.sh` when a quick inventory helps.
- Count the active agents, skills, instructions, hook files, workflow files, and artifact files.
- Confirm the active run folder from `docs/agents/current-run.json`.

### Step 2 - Verify GitHub compatibility
Check:
- custom agents use `.github/agents/*.agent.md`
- instructions use `.github/instructions/**/*.instructions.md`
- hooks live only under `.github/hooks/*.json`
- hook scripts live only under `scripts/hooks/`
- Copilot setup workflow is `.github/workflows/copilot-setup-steps.yml`
- that workflow contains exactly one job named `copilot-setup-steps`

### Step 3 - Verify canonical ownership and determinism
Check:
- canonical sources of truth for `state.json`, `task-spec.md`, `patch-report.md`, `test-report.md`, `review-report.md`, and `release-report.md`
- specialist report ownership and path stability
- run-scoped snapshot completeness under `docs/agents/runs/<run-id>/`
- hook audit logs stay under the active run only

### Step 4 - Compare prompts, skills, instructions, templates, and scripts
Look for:
- contradictory instructions
- stale paths and obsolete role names
- broken JSON examples and unbalanced fences
- excessive tool scopes
- duplicated or competing templates for the same artifact

### Step 5 - Patch only when requested
If the task includes remediation:
- update the smallest set of files that removes the inconsistency
- keep related prompts, templates, helper scripts, and validator logic aligned
- resync mutable `docs/agents/` artifacts into the active run folder if artifact paths change

### Step 6 - Write the audit artifact
Write `docs/agents/agent-architecture-audit-report.md` using:
- `templates/agent-architecture-audit-report.template.md`

Required structure:
1. short human summary
2. exactly one `AgentArchitectureAuditReport` JSON object in a fenced code block

## Default findings categories
- `github-compatibility`
- `ownership`
- `instructions`
- `tool-scope`
- `hooks`
- `workflow`
- `schema`
- `determinism`
- `other`
