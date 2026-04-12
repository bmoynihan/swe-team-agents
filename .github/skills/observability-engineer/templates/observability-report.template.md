# Observability Report

<!--
Copy this file to:
- docs/agents/observability-report.md
Then fill in the summary and JSON.
-->

## Summary (≤ 12 lines)
- Goal:
- What changed (high level):
- What’s now observable (logs/metrics/traces):
- Correlation method:
- How to validate quickly:
- Any known gaps / risks:

```json
{
  "type": "ObservabilityReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "<one sentence goal tied to task-spec>",
  "acceptanceSignalMapping": [
    {
      "ac": "AC1",
      "logs": [
        "event=<name> fields=[...] (no sensitive data)"
      ],
      "metrics": [
        "<metric_name> - what it measures"
      ],
      "traces": [
        "<span_name> - key events/errors"
      ],
      "correlation": "trace_id/span_id in logs: yes/no; how obtained"
    }
  ],
  "goldenSignals": {
    "latency": [
      "<p95/p99 metric or trace-derived latency, where>"
    ],
    "traffic": [
      "<request/job count metric>"
    ],
    "errors": [
      "<error counter and/or exception log event>"
    ],
    "saturation": [
      "<queue depth, worker utilization, db pool saturation, etc.>"
    ]
  },
  "useMethodChecks": [
    {
      "resource": "cpu|memory|disk|network|db|queue|other",
      "utilization": "<what to check>",
      "saturation": "<what to check>",
      "errors": "<what to check>"
    }
  ],
  "semanticConventions": [
    {
      "area": "http|db|messaging|system|other",
      "notes": "Used existing library constants / semantic conventions; avoided inventing attribute keys"
    }
  ],
  "dashboardsProposed": [
    {
      "name": "<dashboard name>",
      "panels": [
        "<panel 1>",
        "<panel 2>"
      ]
    }
  ],
  "alertsProposed": [
    {
      "name": "<alert name>",
      "signal": "latency|errors|saturation|other",
      "condition": "<threshold/burn-rate>",
      "severity": "low|medium|high",
      "notes": "<assumptions + runbook link/steps>"
    }
  ],
  "runbookNotes": [
    {
      "symptom": "<what the on-caller sees>",
      "checkFirst": [
        "<fast check 1>",
        "<fast check 2>"
      ],
      "thenCheck": [
        "<deeper check 1>",
        "<deeper check 2>"
      ],
      "likelyCause": "<most likely cause>",
      "fixOrMitigation": "<rollback/flag/limit/retry/backoff/etc.>"
    }
  ],
  "evidence": [
    {
      "command": "<command(s) you ran or query you executed>",
      "result": "pass|fail|not_run",
      "notes": "<what you observed that proves signals emit correctly>"
    }
  ],
  "knownIssues": [
    {
      "category": "missing_context|high_cardinality_risk|sensitive_data_risk|tooling_gap|other",
      "evidence": "<what shows the problem>",
      "nextStep": "<what the Team Lead / repo owner should do>"
    }
  ],
  "notesToTeamLead": [
    "<anything important for merging/release/ops>"
  ]
}
```


