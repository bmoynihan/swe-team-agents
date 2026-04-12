# Copilot Agent Conversion Report

<!--
Keep the human summary short and the JSON machine-parseable.
Use this report both for bootstrap work and for actual source-agent conversions.
-->

## Summary (<=12 lines)
- Status: <READY_FOR_QUALITY_GATE|BLOCKED>
- Mode: <bootstrap|conversion>
- Goal: <one sentence>
- Source agent: <path or none>
- Determinism: <high|medium|low|not_run>
- Targets: <comma-separated list>
- Notes: <highest-signal caveats only>

```json
{
  "type": "CopilotAgentConversionReport",
  "status": "READY_FOR_QUALITY_GATE",
  "mode": "bootstrap",
  "goal": "Add a deterministic converter agent and supporting skill.",
  "sourceAgent": {
    "path": "",
    "name": "",
    "targets": [],
    "parseStatus": "not_run"
  },
  "normalizedSpec": {
    "path": "",
    "determinism": "not_run",
    "manualReviewReasons": [],
    "lossyTransforms": []
  },
  "packagingTargets": [
    {
      "target": "copilot-sdk-service",
      "status": "ready",
      "artifacts": [],
      "notes": []
    }
  ],
  "generatedFiles": [],
  "validation": [
    {
      "check": "spec-parse",
      "result": "not_run",
      "evidence": ""
    }
  ],
  "blockers": [],
  "notesToTeamLead": [""]
}
```
