# swe-team-agents-template

Production-ready starter template for a manager-led software engineering team using agent coordination artifacts.

## What this repository provides

- Python package layout under `src/`
- Deterministic validation scripts under `scripts/ci/`
- Agent role profiles under `.github/agents/`
- Team state and reporting artifacts under `docs/agents/`

## Quick start

1. Create and activate a virtual environment.
2. Install the package in editable mode:

   ```bash
   python -m pip install -e .
   ```

3. Run fast checks:

   ```bash
   ./scripts/ci/quick_test.sh
   ```

   On Windows without native bash:

   ```powershell
   pwsh -File ./scripts/ci/quick_test.ps1
   ```

4. Run full checks:

   ```bash
   ./scripts/ci/full_test.sh
   ```

   On Windows without native bash:

   ```powershell
   pwsh -File ./scripts/ci/full_test.ps1
   ```

## Project layout

- `src/swe_team_agents/` — application package
- `tests/` — automated tests
- `docs/agents/` — task and quality artifacts
- `.github/` — workflows, hooks, skills, and agent profiles
- `generated/copilot-agent-packages/` — emitted runnable Copilot SDK and Databricks App packages

## Copilot Agent Conversion

Use the repo-native runner to convert a source `.agent.md` profile into a runnable Copilot SDK service package,
smoke test it locally, and optionally deploy it as a Databricks App:

```bash
py -3 scripts/run_copilot_agent_conversion.py --input .github/agents/hello-repo-guide.agent.md
```

To include Databricks deployment validation:

```bash
py -3 scripts/run_copilot_agent_conversion.py --input .github/agents/hello-repo-guide.agent.md --deploy-databricks --profile dev
```

The runner writes the generated package under `generated/copilot-agent-packages/<agent-id>/`, records the pipeline
result in `conversion-run-result.json`, and falls back to `docs/agents/copilot-agent-conversion-report.generated.md`
if the canonical report file is write-locked.

To create a portable, work-safe transfer bundle for the converter itself:

```bash
py -3 scripts/package_copilot_agent_converter_portable.py
```

That writes a copyable bundle plus zip under `generated/transfer-bundles/copilot-agent-converter-portable/`.
The bundle also includes a reusable prompt file at
`.github/prompts/convert-agent-to-databricks-app.prompt.md` and enables prompt files in `.vscode/settings.json`.

## Repo-native AutoAgent

This repository also includes a repo-native AutoAgent loop for optimizing GitHub Copilot custom-agent
profiles with deterministic benchmarks, mutation catalogs, and keep-or-discard scoring.

Run the example experiment:

```bash
py -3 scripts/run_autoagent_loop.py --experiment docs/agents/autoagent-experiment.md
```

That writes:

- `docs/agents/autoagent-report.md`
- `docs/agents/autoagent-results.tsv`
- candidate artifacts under `generated/autoagent-runs/`

The experiment markdown plays the same role as AutoAgent's `program.md`: it is the human-authored
directive for what to optimize, while the target `.agent.md` profile is the harness under test.

## Entrypoint

Run as a module:

```bash
python -m swe_team_agents
```

## License

MIT License. See `LICENSE`.


