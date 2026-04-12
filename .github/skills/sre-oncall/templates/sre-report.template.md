# SRE Report — Operational Readiness

> **Purpose:** capture on-call-ready guidance and objective readiness evidence for the change defined in `docs/agents/task-spec.md`.

## Summary (≤12 lines)
- **Goal:** <what this change delivers>
- **Status:** READY_FOR_QUALITY_GATE | BLOCKED
- **Top risks:** <1–3 bullets>
- **Runbook coverage:** <where the runbook lives>
- **Rollback confidence:** <high/medium/low + why>
- **Observability gaps:** <0–3 bullets>

```json
{
  "type": "SREReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "<string>",
  "runbookEntries": [
    {
      "location": "docs/runbooks/<...> OR docs/ops/<...> OR docs/agents/sre-report.md",
      "title": "<string>",
      "symptoms": ["<string>"] ,
      "firstFiveMinutes": ["<string>"] ,
      "triageFlow": ["<string>"] ,
      "mitigations": ["<string>"] ,
      "rollback": ["<string>"] ,
      "escalation": ["<string>"]
    }
  ],
  "goldenSignalAlerts": [
    {
      "signal": "latency",
      "name": "<string>",
      "condition": "<string>",
      "severity": "medium",
      "notes": "<string>"
    }
  ],
  "useMethodChecks": [
    {
      "resource": "cpu",
      "utilization": "<string>",
      "saturation": "<string>",
      "errors": "<string>"
    }
  ],
  "incidentScenarios": [
    {
      "scenario": "<string>",
      "detection": ["<string>"],
      "diagnosis": ["<string>"],
      "mitigation": ["<string>"],
      "rollback": ["<string>"],
      "postIncidentFollowUps": ["<string>"]
    }
  ],
  "dependenciesAndBlastRadius": [
    {
      "dependency": "<string>",
      "failureMode": "<string>",
      "blastRadius": "medium",
      "notes": "<string>"
    }
  ],
  "knownIssues": [
    {
      "category": "missing_observability",
      "evidence": "<string>",
      "nextStep": "<string>"
    }
  ],
  "followUps": [
    { "id": "SRE1", "priority": "medium", "summary": "<string>" }
  ],
  "notesToTeamLead": ["<string>"]
}
```


