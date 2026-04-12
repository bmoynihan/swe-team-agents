---
applyTo: "AGENTS.md,.github/copilot-instructions.md,.github/agents/**/*.agent.md,.github/skills/**/SKILL.md,.github/skills/**/templates/**/*,.github/skills/**/docs/**/*.md"
---

When editing the agent system and prompt assets in this repository:

## Keep the contract stable
- Treat `docs/agents/` as the only live shared artifact root.
- Do not introduce alternate mutable roots under `.github/docs/` or `.github/scripts/hooks/`.
- Preserve the canonical artifact set in `docs/agents/CANONICAL_ARTIFACT_POLICY.md`.
- Keep `docs/agents/current-run.json` as the pointer to the active run snapshot.

## Use supported GitHub conventions only
- Custom agent files must stay under `.github/agents/*.agent.md`.
- Path-specific instructions must stay under `.github/instructions/**/*.instructions.md`.
- Hook configs must stay under `.github/hooks/*.json`.
- Copilot setup steps must stay in `.github/workflows/copilot-setup-steps.yml`.

## Minimize model confusion
- Give each canonical artifact exactly one owner.
- Avoid overlapping role responsibilities unless the prompt explicitly frames one role as advisory only.
- Keep schemas, examples, templates, scripts, and prose aligned when paths or artifact names change.
- Close every fenced code block and keep JSON examples valid.
- Remove stale placeholders, path drift, and obsolete tokens rather than documenting around them.

## Prefer precise tool scope
- Grant tools conservatively.
- Do not add write or execute capability to roles that only review, analyze, or summarize.
- If a role owns a report artifact, state that artifact path explicitly in metadata and body text.

## Preserve determinism
- Keep prompts short, specific, and path-accurate.
- Prefer acceptance-criteria decomposition over file-ownership decomposition.
- When changing artifact or workflow behavior, update the validator and helper scripts in the same change.
