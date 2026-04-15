---
title: "Agent Operating Guide"
description: "Repository-level workflow and governed artifact contract for the multi-agent SWE team."
---

# Agent Operating Guide

This repository uses a manager-led multi-agent workflow:

1. Research
2. Spec
3. Implement
4. Validate
5. Quality Gate
6. Release Prep
7. Iterate

Canonical artifact policy:

- `docs/agents/` is a preferred live shared artifact root.
- `docs/agents/current-run.json` points to the active run folder.
- `docs/agents/runs/<run-id>/` owns the mutable run snapshot and hook audit logs.
- Every mutable file under `docs/agents/`, except `current-run.json` and `CANONICAL_ARTIFACT_POLICY.md`, must be copied into the active run folder.

Required mutable artifacts:

- `docs/agents/state.json`
- `docs/agents/task-spec.md`
- `docs/agents/patch-report.md`
- `docs/agents/test-report.md`
- `docs/agents/review-report.md`
- `docs/agents/release-report.md`

Supporting working artifacts:

- `docs/agents/research-report.md`
- `docs/agents/docs-report.md`
- `docs/agents/skills-report.md`
- `docs/agents/protocol.md`
- `docs/agents/mcp-config.json`
- Any specialist report under `docs/agents/*-report.md`

Primary team profiles are in `.github/agents/*.agent.md`.

Validation commands:

- Fast checks: `./scripts/ci/quick_test.sh`
- Full checks: `./scripts/ci/full_test.sh`
- Windows fast checks without bash: `pwsh -File ./scripts/ci/quick_test.ps1`
- Windows full checks without bash: `pwsh -File ./scripts/ci/full_test.ps1`

Security and policy notes:

- Never commit secrets.
- Do not bypass hook denials when local iteration needs it.
- Keep changes scoped to the task specification.

## Databricks-first workflow

- Prefer the `Databricks` custom agent for Databricks-specific changes.
- Prefer Databricks MCP tools over hand-written API requests when a tool already exists.
- Prefer serverless-friendly defaults when the workspace supports them.

## Validation order

1. Read the relevant files in the repository.
2. Make the smallest safe edit.
3. Validate with Databricks MCP tools or local checks.
4. Report any remaining Databricks-side prerequisites.

## Secrets and environment

- Never commit secrets.
- Treat `.databricks.env`, `.env`, local Databricks profiles, and generated tokens as sensitive.
- Use placeholders in examples instead of real workspace URLs, IDs, or credentials.
