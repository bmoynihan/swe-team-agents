# Agent System Remediation Plan

## Ordered patch plan

1. Rename every custom agent from `.github/agents/*.agent` to `.github/agents/*.agent.md`.
2. Update all references to agent paths and globs in `AGENTS.md`, `.github/copilot-instructions.md`, and `scripts/ci/check_agent_system.py`.
3. Choose one release role.
4. Standardize `docs/agents/release-report.md` on one JSON type and one owner.
5. Merge the Team Lead protocol assets into one package: keep either `.github/skills/swe-team-protocol/**` or `.github/skills/team-lead/**` as the shared contract, not both.
6. Rewrite the canonical artifact policy once and propagate it to `AGENTS.md`, `.github/copilot-instructions.md`, Team Lead, and `swe-team-protocol`.
7. Make mutable artifacts run-scoped under `docs/agents/runs/<run-id>/`: `state.json`, `task-spec.md`, `patch-report.md`, `test-report.md`, `review-report.md`, `release-report.md`, and hook audit logs.
8. Freeze or remove `.github/docs/agents/**` as a committed editable tree. If a mirror is still needed, generate it from the canonical run output only.
9. Remove every stale `:contentReference[...]` fragment and repair the corrupted lines.
10. Close every open fenced code block in prompts and templates.
11. Collapse hook scripts to one root and point hooks only at that root.
12. Strengthen `scripts/ci/check_agent_system.py` so it validates the real GitHub contract instead of the repo’s current local conventions.

## Quick wins

- Rename `.agent` files to `.agent.md`.
- Fix `scripts/ci/check_agent_system.py` to inspect `.github/workflows/copilot-setup-steps.yml`, not `.md`.
- Delete stale `:contentReference[...]` tokens.
- Close unclosed JSON fences.
- Remove one of `release-engineer` or `release-manager`.

## Breaking changes

- Moving canonical mutable artifacts from shared singleton files to run-scoped folders.
- Deleting or de-committing `.github/docs/agents/**` as a live mirror.
- Removing one release role and one release JSON schema.
- Merging `team-lead` and `swe-team-protocol` shared contract files.

## Files to add

- `docs/agents/runs/<run-id>/patch-report.md`
- `docs/agents/runs/<run-id>/test-report.md`
- `docs/agents/runs/<run-id>/release-report.md`
- `docs/agents/runs/<run-id>/hook-audit/session.jsonl`
- `docs/agents/runs/<run-id>/hook-audit/tool-audit.jsonl`

## Files to delete

- `.github/agents/release-engineer.agent` or `.github/agents/release-manager.agent`
- `.github/skills/release-engineer/**` or `.github/skills/release-manager/**`
- `.github/scripts/hooks/*` if `scripts/hooks/*` remains canonical
- `.github/workflows/copilot-setup-steps.md`
- `.github/skills/ux-reviewer-skill-package.zip`
- `.github/skills/ux-reviewer-skill-package/**`
- `.github/docs/agents/**` after migration if mirror commits are removed

## Files to rename

- every file currently matching `.github/agents/*.agent` to `.github/agents/*.agent.md`

## Files to merge

- `.github/skills/team-lead/**` with `.github/skills/swe-team-protocol/**`
- `.github/agents/release-engineer.agent` with `.github/agents/release-manager.agent`
- `docs/agents/*` with `.github/docs/agents/*` by choosing one canonical owner and one generated mirror policy

## Hooks or templates to add

- a run-aware hook audit path convention: `docs/agents/runs/<run-id>/hook-audit/`
- a fence-balance check in `scripts/ci/check_agent_system.py`
- a mirror-drift check that fails if `.github/docs/agents/**` differs from the canonical source
- a release-role uniqueness check so only one agent owns `docs/agents/release-report.md`
