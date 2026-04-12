---
applyTo: ".github/hooks/**/*.json,.github/workflows/copilot-setup-steps.yml,scripts/hooks/**/*.sh,scripts/hooks/**/*.ps1"
---

When editing Copilot hooks, hook scripts, or the Copilot setup workflow:

## Follow GitHub's supported shape exactly
- Keep hook configuration files under `.github/hooks/*.json` with `version: 1` and a `hooks` object.
- Keep the Copilot setup workflow at `.github/workflows/copilot-setup-steps.yml`.
- The setup workflow must contain exactly one job named `copilot-setup-steps`.
- In that job, only rely on supported keys: `steps`, `permissions`, `runs-on`, `services`, `snapshot`, and `timeout-minutes`.

## Hooks must stay deterministic and safe
- Keep hooks fast, synchronous, and network-free unless there is a strong documented reason.
- Never log secrets, tokens, cookies, or full environment dumps.
- Prefer high-signal audit metadata over raw payloads.
- Keep Bash and PowerShell behavior aligned.
- Use `docs/agents/current-run.json` to resolve the active run, and keep JSON hook configs on the `<current-run>` placeholder pattern.

## Workflow and security expectations
- Use least-privilege permissions.
- If third-party actions are added, pin them to a full commit SHA.
- Keep `timeout-minutes` explicit.
- Do not add broad workflow permissions or unsafe trigger changes without a documented need.

## Operational consistency
- Hook scripts belong under `scripts/hooks/` only.
- If changing hook paths, event names, or audit locations, update the scripts, the JSON config, the related prompts, and the validator together.
