# Test Report

Status: `BLOCKED`
Goal: `<concise goal>`
Scope: `<files / behavior / AC slice>`
Date: `<YYYY-MM-DD>`
Author: `test-engineer`

Summary:
- `<1 short summary line>`
- `<1 short summary line>`
- `<1 short summary line>`
- `<1 short summary line>`
- `<1 short summary line>`

```json
{
  "type": "TestReport",
  "status": "BLOCKED",
  "goal": "<goal>",
  "acceptanceCovered": [
    {
      "ac": "AC1",
      "testsAddedOrUpdated": [
        "<path-or-test-name>"
      ],
      "evidence": [
        "<command + key outcome>"
      ],
      "negativeCoverage": [
        "<edge or negative case>"
      ]
    }
  ],
  "testsRun": [
    {
      "command": "<command>",
      "result": "not_run",
      "notes": "<why>"
    }
  ],
  "flakeAssessment": {
    "risk": "medium",
    "notes": [
      "<flake risk note>"
    ],
    "mitigationsApplied": [
      "<mitigation>"
    ]
  },
  "coverageNotes": [
    "<what is covered and what is intentionally out of scope>"
  ],
  "knownIssues": [
    {
      "category": "missing_task_spec",
      "evidence": "<evidence>",
      "nextStep": "<next step>"
    }
  ],
  "handoffToQualityGate": {
    "focusAreas": [
      "<focus area>"
    ],
    "commandsToReRun": [
      "<command>"
    ],
    "riskHotspots": [
      "<risk hotspot>"
    ]
  }
}
```


