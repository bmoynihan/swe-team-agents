# Copilot Agent Conversion Report

## Summary (<=12 lines)
- Status: READY_FOR_QUALITY_GATE
- Mode: conversion
- Goal: Operationalize the first real Copilot-agent conversion with runnable scaffolds.
- Source agent: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/hello-repo-guide.agent.md
- Determinism: high
- Targets: copilot-sdk-service, databricks-app
- Generated package: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide
- Notes: The emitted service defaults to deterministic mock mode and includes a Databricks deployment helper.

```json
{
  "type": "CopilotAgentConversionReport",
  "status": "READY_FOR_QUALITY_GATE",
  "mode": "conversion",
  "goal": "Convert a real example Copilot custom agent into runnable Copilot SDK and Databricks App scaffolds.",
  "sourceAgent": {
    "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/hello-repo-guide.agent.md",
    "name": "hello-repo-guide",
    "targets": [
      "vscode",
      "github-copilot"
    ],
    "parseStatus": "pass"
  },
  "normalizedSpec": {
    "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/normalized-agent-spec.json",
    "determinism": "high",
    "manualReviewReasons": [],
    "lossyTransforms": []
  },
  "packagingTargets": [
    {
      "target": "copilot-sdk-service",
      "status": "ready",
      "artifacts": [
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/normalized-agent-spec.json",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/.gitignore",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/.env.example",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/package.json",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/app.yaml",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/config.js",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/mock-runtime.js",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/copilot-runtime.js",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/server.js",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/scripts/local_smoke_test.mjs",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/scripts/deploy_databricks_app.py",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/README.md"
      ],
      "notes": [
        "Generated package defaults to mock mode and can be upgraded to live Copilot mode."
      ]
    },
    {
      "target": "databricks-app",
      "status": "ready",
      "artifacts": [
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/normalized-agent-spec.json",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/.gitignore",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/.env.example",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/package.json",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/app.yaml",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/config.js",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/mock-runtime.js",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/copilot-runtime.js",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/server.js",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/scripts/local_smoke_test.mjs",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/scripts/deploy_databricks_app.py",
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/README.md"
      ],
      "notes": [
        "Generated package includes app.yaml and a Python SDK deployment helper."
      ]
    }
  ],
  "generatedFiles": [
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/normalized-agent-spec.json",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/.gitignore",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/.env.example",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/package.json",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/app.yaml",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/config.js",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/mock-runtime.js",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/copilot-runtime.js",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/src/server.js",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/scripts/local_smoke_test.mjs",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/scripts/deploy_databricks_app.py",
    "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/README.md"
  ],
  "validation": [
    {
      "check": "spec-parse",
      "result": "pass",
      "evidence": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide/normalized-agent-spec.json"
    },
    {
      "check": "scaffold-emission",
      "result": "pass",
      "evidence": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/copilot-agent-packages/hello-repo-guide"
    }
  ],
  "blockers": [],
  "notesToTeamLead": [
    "The generated runtime defaults to mock mode so the first Databricks deployment is deterministic.",
    "Switch to live Copilot mode only after configuring GitHub Copilot CLI auth or a provider-backed model endpoint."
  ]
}
```
