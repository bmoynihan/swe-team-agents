# SRE / On-Call Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Produced at:** <!-- ISO date/time -->
- **Author:** sre-oncall

## Runbook Entries
> Keep entries actionable: symptoms → first 5 minutes → triage flow → mitigations → rollback → escalation.

### Runbook: <!-- title -->
- **Location:** <!-- docs/runbooks/... or inline here -->
- **Symptoms:**
  - <!-- what users/on-call see -->
- **First 5 minutes:**
  1. <!-- quick checks -->
  2. <!-- -->
- **Triage flow:**
  - <!-- decision points -->
- **Mitigations:**
  - <!-- reduce impact fast -->
- **Rollback:**
  - <!-- safe rollback steps -->
- **Escalation:**
  - <!-- when to page/escalate -->

## Golden Signal Alerts
| Signal | Name | Condition | Severity | Notes |
|---|---|---|---|---|
| latency | <!-- --> | <!-- --> | low/med/high | <!-- --> |
| errors | <!-- --> | <!-- --> | low/med/high | <!-- --> |
| saturation | <!-- --> | <!-- --> | low/med/high | <!-- --> |
| traffic | <!-- --> | <!-- --> | low/med/high | <!-- --> |

## USE Method Checks
| Resource | Utilization | Saturation | Errors |
|---|---|---|---|
| cpu | <!-- --> | <!-- --> | <!-- --> |
| memory | <!-- --> | <!-- --> | <!-- --> |
| db/queue/etc | <!-- --> | <!-- --> | <!-- --> |

## Incident Scenarios
### Scenario 1 — <!-- -->
- **Detection:**
  - <!-- alert/log/metric -->
- **Diagnosis:**
  - <!-- steps -->
- **Mitigation:**
  - <!-- -->
- **Rollback:**
  - <!-- -->
- **Post-incident follow-ups:**
  - <!-- -->

## Dependencies & Blast Radius
| Dependency | Failure mode | Blast radius | Notes |
|---|---|---|---|
| <!-- --> | <!-- --> | small/medium/large | <!-- --> |

## Known Issues / Blockers
- <!-- missing observability, missing rollback, unclear ownership, etc. -->

## Follow-ups
- **SRE1 (low/med/high):** <!-- -->

## Notes to Team Lead
- <!-- -->

---

## Machine-readable SREReport (required)
```json
{
  "type": "SREReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "runbookEntries": [
    {
      "location": "docs/agents/sre-report.md",
      "title": "",
      "symptoms": [""],
      "firstFiveMinutes": [""],
      "triageFlow": [""],
      "mitigations": [""],
      "rollback": [""],
      "escalation": [""]
    }
  ],
  "goldenSignalAlerts": [
    {
      "signal": "errors",
      "name": "",
      "condition": "",
      "severity": "medium",
      "notes": ""
    }
  ],
  "useMethodChecks": [
    {
      "resource": "cpu",
      "utilization": "",
      "saturation": "",
      "errors": ""
    }
  ],
  "incidentScenarios": [
    {
      "scenario": "",
      "detection": [""],
      "diagnosis": [""],
      "mitigation": [""],
      "rollback": [""],
      "postIncidentFollowUps": [""]
    }
  ],
  "dependenciesAndBlastRadius": [
    {
      "dependency": "",
      "failureMode": "",
      "blastRadius": "small",
      "notes": ""
    }
  ],
  "knownIssues": [],
  "followUps": [
    {
      "id": "SRE1",
      "priority": "low",
      "summary": ""
    }
  ],
  "notesToTeamLead": [""]
}
```


