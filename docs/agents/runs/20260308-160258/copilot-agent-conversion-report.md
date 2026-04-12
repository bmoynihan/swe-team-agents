# Copilot Agent Conversion Report

## Summary (<=12 lines)
- Status: READY_FOR_QUALITY_GATE
- Mode: bootstrap
- Goal: Add a deterministic converter agent and supporting skill to this repository.
- Source agent: none yet; this change bootstraps the converter for later use.
- Determinism: high for the bootstrap artifacts, medium for future source-agent conversions with MCP or hook translation.
- Targets: copilot-sdk-service, databricks-app, maf-foundry
- Notes: stdio MCP transport is explicitly flagged as requiring an HTTP bridge for remote serving.

```json
{
  "type": "CopilotAgentConversionReport",
  "status": "READY_FOR_QUALITY_GATE",
  "mode": "bootstrap",
  "goal": "Add a user-invocable converter agent that normalizes GitHub Copilot custom agents and guides deterministic packaging decisions.",
  "sourceAgent": {
    "path": "",
    "name": "",
    "targets": [],
    "parseStatus": "not_run"
  },
  "normalizedSpec": {
    "path": ".github/skills/copilot-agent-converter/templates/normalized-agent-spec.template.json",
    "determinism": "medium",
    "manualReviewReasons": [
      "VS Code-only hooks still require manual translation.",
      "stdio MCP transport still requires an HTTP bridge before remote serving."
    ],
    "lossyTransforms": [
      "Handoffs are preserved as app-layer metadata rather than a universal deployed runtime primitive."
    ]
  },
  "packagingTargets": [
    {
      "target": "copilot-sdk-service",
      "status": "ready",
      "artifacts": [
        ".github/skills/copilot-agent-converter/SKILL.md",
        ".github/skills/copilot-agent-converter/templates/normalized-agent-spec.template.json"
      ],
      "notes": [
        "This remains the semantic first target for deterministic conversion."
      ]
    },
    {
      "target": "databricks-app",
      "status": "ready",
      "artifacts": [
        ".github/skills/copilot-agent-converter/SKILL.md"
      ],
      "notes": [
        "Treat Databricks Apps as an authenticated enterprise packaging target, not a public endpoint default."
      ]
    },
    {
      "target": "maf-foundry",
      "status": "manual_review",
      "artifacts": [],
      "notes": [
        "Keep MAF/Foundry as a packaging wrapper rather than the semantic source of truth."
      ]
    }
  ],
  "generatedFiles": [
    ".github/agents/copilot-agent-converter.agent.md",
    ".github/skills/copilot-agent-converter/SKILL.md",
    ".github/skills/copilot-agent-converter/scripts/normalize_agent_profile.py",
    ".github/skills/copilot-agent-converter/templates/copilot-agent-conversion-report.template.md",
    ".github/skills/copilot-agent-converter/templates/normalized-agent-spec.template.json",
    "tests/test_copilot_agent_converter.py"
  ],
  "validation": [
    {
      "check": "spec-parse",
      "result": "not_run",
      "evidence": "Bootstrap mode did not run the converter against a specific source agent."
    },
    {
      "check": "template-sync",
      "result": "pass",
      "evidence": "The new agent points to its skill and report artifact, and the skill points to its templates and helper script."
    }
  ],
  "blockers": [],
  "notesToTeamLead": [
    "Use the new converter on an existing .agent.md next to validate the first real conversion flow.",
    "Keep packaging decisions downstream from the normalized intermediate spec to minimize semantic drift."
  ]
}
```
