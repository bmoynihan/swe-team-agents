---
applyTo: "src/**/*.py,scripts/ci/**/*.py"
---

When editing Python source or Python CI utilities in this repository:

## Match the project configuration
- Target Python 3.10+ semantics.
- Keep Ruff compatibility with line length 100.
- Prefer simple standard-library solutions over new dependencies.
- Keep imports clean and deterministic.

## Write maintainable repo code
- Use clear function boundaries and readable names.
- Prefer `pathlib.Path` for repository paths.
- Keep CLI and validation scripts explicit about failure reasons and exit behavior.
- Avoid hidden global state and unnecessary side effects.
- Keep messages concise and useful for maintainers and agents.

## Preserve determinism
- Do not add network access to tests or validators.
- Do not depend on local machine state outside the repository unless the script is explicitly an environment probe.
- When validating the agent system, check supported GitHub conventions and this repo's canonical paths together.

## Be careful with repo-wide scanners
- Skip generated run snapshots when checking for stale text unless the task specifically targets them.
- Ignore compiled caches such as `__pycache__` in text scans.
- If you block on stale-token detection, ensure the validator does not flag its own internal rule strings.
