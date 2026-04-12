# hello-repo-guide Package

This package was generated from `D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/hello-repo-guide.agent.md` by the repo-native
`copilot-agent-converter` scaffold emitter.

## What it contains

- A runnable Node service that exposes `GET /health`, `GET /agent`, and `POST /invoke`
- A `package.json` with the Copilot SDK and Copilot CLI runtime dependencies
- A Databricks `app.yaml` so the same service can be deployed as a Databricks App
- A Python deployment helper that uploads the folder to a workspace and triggers an app deploy
- A deterministic local smoke test script that starts the service in mock mode

## Targets emitted

- copilot-sdk-service, databricks-app

## Conversion inputs

- Source agent: `D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/hello-repo-guide.agent.md`
- Normalized spec: `normalized-agent-spec.json`
- Conversion report: `D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/copilot-agent-conversion-report.generated.md`

## Local validation

```bash
npm install
npm run smoke
```

The generated runtime defaults to `COPILOT_RUNTIME_MODE=mock` so the first validation pass is
deterministic and does not require GitHub Copilot authentication.

## Databricks deployment

```bash
py -3 -m pip install databricks-sdk
py -3 scripts/deploy_databricks_app.py --profile dev
```

Override `--app-name` if you want a different Databricks App name. The deployment helper uploads this
folder to the workspace, creates the app if needed, and waits for the deployment to become healthy.

## Optional live Copilot mode

Set `COPILOT_RUNTIME_MODE=copilot` and provide one of these runtime paths:

- GitHub-authenticated Copilot CLI via the bundled `@github/copilot` package
- A custom provider using `COPILOT_PROVIDER_BASE_URL`, `COPILOT_MODEL`, and auth variables

## Manual review notes

- None
