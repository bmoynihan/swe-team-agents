---
applyTo: "docs/agents/**/*.md,docs/agents/**/*.json,docs/agents/**/*.jsonl"
excludeAgent: "code-review"
---

When editing operational artifacts under `docs/agents/`:

## Treat these files as machine-readable working state
- Preserve required filenames and stable keys.
- Keep report schemas consistent with the owning agent or template.
- Do not add commentary outside the expected human summary and schema block structure.

## Respect run-scoped ownership
- Root files under `docs/agents/` are the current shared working set.
- Mutable root artifacts must also exist in the active run folder from `docs/agents/current-run.json`.
- Hook audit data belongs only under `docs/agents/runs/<run-id>/hook-audit/`.
- Do not create parallel singleton logs or duplicate canonical reports elsewhere.

## Preserve artifact quality
- Keep JSON valid and machine-parseable.
- Keep Markdown summaries short and factual.
- When a file requires one schema object, emit exactly one schema object.
- Do not embed secrets, tokens, or environment dumps in any artifact.
- Use exact artifact paths when cross-referencing other reports.

## Avoid path drift
- Use `docs/agents/`, never `docs/agent/`.
- Do not reference any duplicate artifact root under `.github/docs/`.
- Do not revive removed artifact owners or obsolete role names.
