# Canonical Artifact Policy

Canonical shared root for team workflow artifacts is `docs/agents/`.

Shared singleton control files:

- `docs/agents/current-run.json`
- `docs/agents/CANONICAL_ARTIFACT_POLICY.md`

Core required working artifacts:

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

Specialist working artifacts:

- Any role-owned report under `docs/agents/*-report.md`
- Typical examples include `ci-report.md`, `security-report.md`, `observability-report.md`, `performance-report.md`, `dependency-report.md`, `backlog-report.md`, `architecture-review-report.md`, `sre-report.md`, `ux-review-report.md`, `data-privacy-report.md`, `compliance-report.md`, `mcp-report.md`, and `hooks-report.md`
- When present, specialist reports are mutable run outputs and must be snapshotted into the active run folder

Run-scoped ownership policy:

- The active run folder lives under `docs/agents/runs/<run-id>/`.
- `docs/agents/current-run.json` points to the active run id and path.
- The active run folder owns the mutable run snapshot and hook audit logs.
- Hook audit logs must live only under `docs/agents/runs/<run-id>/hook-audit/`.
- Every mutable file under `docs/agents/`, except the singleton control files above, must be copied into the active run folder.
- Root copies under `docs/agents/` are the latest shared working set and must stay in sync with the active run snapshot.

Unsupported paths:

- No generated mirror tree is used in this repository.
- `.github/scripts/hooks/` is not used in this repository.
