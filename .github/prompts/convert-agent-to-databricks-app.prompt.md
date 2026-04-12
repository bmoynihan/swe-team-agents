# Reusable Prompt: Convert Any Workspace Agent To A Databricks App

Use this prompt with `/copilot-agent-converter` in a repository that already contains the
`copilot-agent-converter.agent.md` agent and the `copilot-agent-converter` skill.

## Prompt Template

```text
/copilot-agent-converter

Convert the source agent at `<SOURCE_AGENT_PATH>` into a Databricks App target.

Requirements:
- Treat the source `.agent.md` file as the semantic source of truth.
- Target only `databricks-app` unless the source needs `copilot-sdk-service` scaffolding as an implementation dependency.
- Prefer the repo-native runner:
  `py -3 scripts/run_copilot_agent_conversion.py --input <SOURCE_AGENT_PATH> --target databricks-app`
- If Node dependencies and Databricks auth are available, run the full flow with deployment validation using:
  `py -3 scripts/run_copilot_agent_conversion.py --input <SOURCE_AGENT_PATH> --target databricks-app --deploy-databricks --profile <DATABRICKS_PROFILE>`
- If deployment is not possible, still emit the Databricks App scaffold and explain the blocker precisely.
- Write or update the conversion report under `docs/agents/`.
- If `docs/agents/copilot-agent-conversion-report.md` is write-locked, use the generated fallback path and record that fallback explicitly.
- Return:
  1. the package output path
  2. the conversion report path
  3. the Databricks app name
  4. whether deploy validation ran successfully
  5. any remaining prerequisites for live use

Parameters:
- Source agent path: `<SOURCE_AGENT_PATH>`
- Databricks profile: `<DATABRICKS_PROFILE>`
- Optional Databricks app name override: `<APP_NAME_OVERRIDE_OR_BLANK>`
- Optional workspace upload root: `<WORKSPACE_ROOT_OR_BLANK>`

Constraints:
- Never use or print secrets.
- Never claim the app is publicly anonymous.
- If the source agent uses stdio MCP servers, call out the required HTTP bridge.
```

## Fast Example

```text
/copilot-agent-converter

Convert the source agent at `.github/agents/hello-repo-guide.agent.md` into a Databricks App target.

Requirements:
- Treat the source `.agent.md` file as the semantic source of truth.
- Target only `databricks-app`.
- Prefer the repo-native runner:
  `py -3 scripts/run_copilot_agent_conversion.py --input .github/agents/hello-repo-guide.agent.md --target databricks-app`
- If Databricks auth is available, run deploy validation using:
  `py -3 scripts/run_copilot_agent_conversion.py --input .github/agents/hello-repo-guide.agent.md --target databricks-app --deploy-databricks --profile dev`
- Write or update the conversion report under `docs/agents/`.
- Return the package path, report path, app name, deploy result, and any blockers.
```

## Placeholder Guide

- `<SOURCE_AGENT_PATH>`: repo-relative path like `.github/agents/my-agent.agent.md`
- `<DATABRICKS_PROFILE>`: local profile name like `dev`, `work`, or `prod`
- `<APP_NAME_OVERRIDE_OR_BLANK>`: optional override if you do not want the default generated app name
- `<WORKSPACE_ROOT_OR_BLANK>`: optional Databricks workspace upload folder
