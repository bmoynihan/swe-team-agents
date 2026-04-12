# Agent System Audit

## Executive summary

This repo has the right broad components for a GitHub Copilot agent system, but it is not deterministic today.

Inventory:
- 23 custom agent files under `.github/agents/`
- 134 files under `.github/skills/`
- 1 root `AGENTS.md`
- 1 `.github/copilot-instructions.md`
- 0 files under `.github/instructions/`
- 1 hooks config under `.github/hooks/`
- 10 hook wrapper scripts under `.github/scripts/hooks/`
- 1 `.github/workflows/copilot-setup-steps.yml`
- 32 files under `docs/agents/`
- 24 files under `.github/docs/agents/`

GitHub convention check:
- `.github/hooks/*.json`: PASS
- `.github/workflows/copilot-setup-steps.yml`: PASS
- single job named `copilot-setup-steps`: PASS
- `.github/copilot-instructions.md`: PASS
- `.github/instructions/**`: none present
- live `docs/agent/` singular drift: none found outside the intentional guard/test checks

High-severity findings:
- Unsupported custom-agent filenames: every agent file uses `.github/agents/*.agent`, but GitHub custom agents use `.github/agents/*.agent.md`. This appears both in the file inventory and in repo guidance at `AGENTS.md` and `.github/copilot-instructions.md`. If left unchanged, GitHub will not load the custom agent catalog.
- Competing source-of-truth contracts: `AGENTS.md`, `.github/copilot-instructions.md`, `.github/skills/team-lead/SKILL.md`, and `.github/skills/swe-team-protocol/SKILL.md` treat `state.json`, `task-spec.md`, and `review-report.md` as the core contract, while `docs/agents/CANONICAL_ARTIFACT_POLICY.md` declares six required canonical files plus five supporting canonicals. Ownership and “done” criteria are therefore ambiguous.
- Duplicate canonical artifact roots: `docs/agents/` is declared canonical, but `.github/docs/agents/` contains 24 duplicate artifacts and 11 of those duplicates already drift. Examples include `docs/agents/security-report.md` vs `.github/docs/agents/security-report.md`, `docs/agents/sre-report.md` vs `.github/docs/agents/sre-report.md`, and `docs/agents/ux-review-report.md` vs `.github/docs/agents/ux-review-report.md`.
- Release artifact ownership conflict: `.github/agents/release-engineer.agent` and `.github/agents/release-manager.agent` both target `docs/agents/release-report.md`, but one emits `ReleasePlan` and the other emits `ReleaseReport`. The primary Team Lead loop does not invoke either release role, so the release stage is both duplicated and orphaned.
- Run-scoped policy is only partially implemented: `docs/agents/current-run.json` points to `docs/agents/runs/20260307-182815`, but only `state.json`, `task-spec.md`, `review-report.md`, and `protocol.md` are snapshotted there. `patch-report.md`, `test-report.md`, `release-report.md`, and hook audit logs remain shared singleton files under `docs/agents/`.

Medium-severity findings:
- Prompt corruption/stale citation debris: 111 `:contentReference[...]` markers remain across 19 files. Some are harmless comments, but others corrupt words and JSON examples, including `.github/skills/mcp-admin/SKILL.md` and `.github/agents/security-engineer.agent`.
- Duplicate protocol packages drift: `.github/skills/team-lead/**` and `.github/skills/swe-team-protocol/**` both define the team contract, but their schemas and templates differ. Example: `team-lead/templates/task-spec.template.md` starts with `## Summary`, while `swe-team-protocol/templates/task-spec.template.md` starts with `## Objective`.
- Unclosed fenced JSON blocks: many agent prompts and report templates end with an opening ```json block but no closing fence. This affects `docs/agents/patch-report.md`, `docs/agents/review-report.md`, `docs/agents/release-report.md`, and all 23 `.github/agents/*.agent` files.
- Validator blind spots: `scripts/ci/check_agent_system.py` passes, but it validates the repo’s wrong `.agent` convention, checks `.github/workflows/copilot-setup-steps.md` instead of the real `.yml`, and does not detect mirror drift, duplicate release roles, or broken markdown fences.
- Hook layout drift: `.github/hooks/hooks.json` executes `scripts/hooks/*`, while `.github/scripts/hooks/*` contains wrapper duplicates. That creates two maintenance roots for the same hook behavior.
- Extra packaged artifact copies: `.github/skills/ux-reviewer-skill-package/ux-reviewer-skill-package/docs/agents/ux-review-report.md` introduces a third in-repo copy of a report artifact, and the adjacent zip embeds even more copies.

Canonical source-of-truth assessment:
- team state: `docs/agents/state.json`
  Competing locations: `.github/docs/agents/state.json`, `docs/agents/runs/20260307-182815/state.json`
- task specification: `docs/agents/task-spec.md`
  Competing locations: `.github/docs/agents/task-spec.md`, `docs/agents/runs/20260307-182815/task-spec.md`
- patch report: `docs/agents/patch-report.md`
  Competing locations: `.github/docs/agents/patch-report.md`
- test report: `docs/agents/test-report.md`
  Competing locations: `.github/docs/agents/test-report.md`
- quality gate report: `docs/agents/review-report.md`
  Competing locations: `.github/docs/agents/review-report.md`, `docs/agents/runs/20260307-182815/review-report.md`
- release report: `docs/agents/release-report.md`
  Competing locations: `.github/docs/agents/release-report.md`
  Additional ownership conflict: `release-engineer` and `release-manager` both claim it

Why this matters:
- GitHub compatibility issues stop the agent system from loading at all.
- Duplicate mutable artifacts create nondeterministic handoffs.
- Conflicting schemas and role ownership make machine-parseable outputs unreliable.
- Shared singleton runtime files make parallel or repeated runs overwrite each other.
- Prompt corruption and malformed templates increase model confusion even when the high-level process is sound.
