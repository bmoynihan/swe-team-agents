# Copilot Agent Converter Portable Bundle

This bundle is the minimal repo-safe package for moving `copilot-agent-converter` into another VS Code / GitHub Copilot custom-agent repository.

## What to copy into the target repo

- `.github/agents/copilot-agent-converter.agent.md`
- `.github/prompts/convert-agent-to-databricks-app.prompt.md`
- `.github/skills/copilot-agent-converter/`
- `scripts/run_copilot_agent_conversion.py`

## Optional extras included in this bundle

- `.github/agents/hello-repo-guide.agent.md`
- `tests/test_copilot_agent_converter.py`
- `tests/test_copilot_agent_scaffold_emitter.py`
- `tests/test_copilot_agent_conversion_runner.py`
- `tests/fixtures/copilot-agent-converter/planner.agent.md`
- `tests/fixtures/copilot-agent-converter/db-helper.agent.md`

## Install steps in the work repo

1. Copy the `.github/agents/`, `.github/prompts/`, `.github/skills/`, and `scripts/` paths from this bundle into the target repo.
2. Ensure the workspace has `"chat.promptFiles": true` in `.vscode/settings.json`.
3. If the target repo does not already have `docs/agents/`, allow the converter to create it on first run.
4. Do not copy personal auth files such as `.databrickscfg`, `.env`, `.databricks.env`, or any tokens.
5. Recreate Databricks auth on the work machine using the work profile and workspace.
6. Open the prompt file from `.github/prompts/` in VS Code or paste its contents into Copilot Chat.
7. Validate from the target repo with:

```bash
py -3 scripts/run_copilot_agent_conversion.py --input .github/agents/hello-repo-guide.agent.md --skip-smoke-test
```

8. For full validation after Node and Databricks auth are ready:

```bash
py -3 scripts/run_copilot_agent_conversion.py --input .github/agents/hello-repo-guide.agent.md --deploy-databricks --profile <work-profile>
```

## Notes

- This bundle is repo-level, not account-level. It is meant to be copied into another repository.
- The converter can write `docs/agents/copilot-agent-conversion-report.generated.md` if the canonical report file is locked.
- The generated service validates in deterministic `mock` mode first; live Copilot mode still needs GitHub Copilot CLI auth or provider env vars.
