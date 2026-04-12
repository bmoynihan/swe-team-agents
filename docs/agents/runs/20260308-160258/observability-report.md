# Observability Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Produced at:** <!-- ISO date/time -->
- **Author:** observability-engineer

## Acceptance Criteria → Signals Mapping
> For each AC, define what proves success/failure in logs/metrics/traces and how correlation works.

### AC1
- **Logs:** <!-- event name + fields; redaction notes -->
- **Metrics:** <!-- names + meaning; low-cardinality labels -->
- **Traces:** <!-- span names/events/attributes -->
- **Correlation:** <!-- trace_id/span_id or request_id -->

### AC2
- **Logs:** <!-- -->
- **Metrics:** <!-- -->
- **Traces:** <!-- -->
- **Correlation:** <!-- -->

## Golden Signals
- **Latency:** <!-- e.g., p95 latency metric; endpoint scope -->
- **Traffic:** <!-- request rate -->
- **Errors:** <!-- error rate; class of errors -->
- **Saturation:** <!-- CPU/memory/queue depth -->

## USE Method Checks (resource triage)
| Resource | Utilization | Saturation | Errors |
|---|---|---|---|
| cpu | <!-- --> | <!-- --> | <!-- --> |
| memory | <!-- --> | <!-- --> | <!-- --> |
| db/queue/etc | <!-- --> | <!-- --> | <!-- --> |

## Semantic Conventions
- <!-- note which OTel semantic conventions/attributes were applied -->

## Dashboards Proposed
- **Dashboard:** <!-- name -->
  - Panels:
    - <!-- panel 1 -->
    - <!-- panel 2 -->

## Alerts Proposed
| Name | Signal | Condition | Severity | Notes |
|---|---|---|---|---|
| <!-- --> | latency/errors/saturation | <!-- --> | low/med/high | <!-- --> |

## Runbook Notes
- **Symptom:** <!-- -->
  - Check first: <!-- -->
  - Then check: <!-- -->
  - Likely cause: <!-- -->
  - Fix/mitigation: <!-- -->

## Evidence
| Command / Check | Result | Notes |
|---|---|---|
| <!-- run a fast subset and demonstrate signal emission --> | pass/fail/not_run | <!-- --> |

## Known Issues / Blockers
- <!-- missing context, high-cardinality risk, sensitive-data risk, tooling gap -->

## Notes to Team Lead
- <!-- -->

---

## Machine-readable ObservabilityReport (required)
```json
{
  "type": "ObservabilityReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "acceptanceSignalMapping": [
    {
      "ac": "AC1",
      "logs": [""],
      "metrics": [""],
      "traces": [""],
      "correlation": "trace_id/span_id present? yes/no + how"
    }
  ],
  "goldenSignals": {
    "latency": [""],
    "traffic": [""],
    "errors": [""],
    "saturation": [""]
  },
  "useMethodChecks": [
    {
      "resource": "cpu",
      "utilization": "",
      "saturation": "",
      "errors": ""
    }
  ],
  "semanticConventions": [
    {
      "area": "http",
      "notes": ""
    }
  ],
  "dashboardsProposed": [
    {
      "name": "",
      "panels": [""]
    }
  ],
  "alertsProposed": [
    {
      "name": "",
      "signal": "errors",
      "condition": "",
      "severity": "medium",
      "notes": ""
    }
  ],
  "runbookNotes": [
    {
      "symptom": "",
      "checkFirst": [""],
      "thenCheck": [""],
      "likelyCause": "",
      "fixOrMitigation": ""
    }
  ],
  "evidence": [
    {
      "command": "",
      "result": "not_run",
      "notes": ""
    }
  ],
  "knownIssues": [],
  "notesToTeamLead": [""]
}
```

