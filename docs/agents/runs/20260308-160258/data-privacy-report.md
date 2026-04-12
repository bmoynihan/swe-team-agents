# Data Privacy Report

## Summary
- **Status:** PASS / FAIL
- **Goal:** <!-- one sentence -->
- **Reviewed at:** <!-- ISO date/time -->
- **Reviewer:** data-privacy-reviewer
- **Ready for Quality Gate:** true / false

## Data Inventory
> List any personal/sensitive data touched by the change. If none, explicitly state “none”.

| Element | Classification | Source | Processing | Storage | Retention | Sharing | Notes |
|---|---|---|---|---|---|---|---|
| <!-- --> | none/personal/sensitive/unknown | <!-- --> | <!-- --> | none/transient/persistent/unknown | <!-- --> | none/internal/third-party/unknown | <!-- --> |

## Principles Review
- **Purpose limitation:** pass / fail — Evidence: <!-- -->
- **Data minimization:** pass / fail — Evidence: <!-- -->
- **Storage limitation:** pass / fail / n/a — Evidence: <!-- -->
- **Integrity & confidentiality:** pass / fail — Evidence: <!-- -->
- **Accountability docs:** pass / fail — Evidence: <!-- -->

## Privacy by Default
- **Verdict:** pass / fail
- **Defaults applied:**
  - <!-- minimal collection -->
  - <!-- minimal retention -->
  - <!-- minimal sharing -->
- **Evidence:** <!-- where defaults are set -->

## Logging / Telemetry Hygiene
- **Verdict:** pass / fail
- **Redaction:** present / missing / unknown
- **High-cardinality risk:** low / medium / high
- **Evidence:** <!-- grep/tests/docs -->

## NIST Privacy Framework Notes (optional, structured thinking)
- Identify-P: <!-- -->
- Govern-P: <!-- -->
- Control-P: <!-- -->
- Communicate-P: <!-- -->
- Protect-P: <!-- -->

## Blockers
- **DP1 — <category>:** <!-- minimization | retention | transparency | access-control | logging | third-party-sharing | other -->
  - **Summary:** <!-- -->
  - **Evidence:** <!-- -->
  - **Recommended fix:** <!-- -->

## Non-blocking Findings
- **DPN1:** <!-- -->

## Evidence
| Command / Check | Result | Notes |
|---|---|---|
| <!-- grep for sensitive logging, tests, docs review --> | pass/fail/not_run | <!-- --> |

---

## Machine-readable DataPrivacyReport (required)
```json
{
  "type": "DataPrivacyReport",
  "status": "PASS",
  "goal": "",
  "dataInventory": [
    {
      "element": "",
      "classification": "none",
      "source": "",
      "processing": "",
      "storage": "none",
      "retention": "",
      "sharing": "none",
      "notes": ""
    }
  ],
  "principlesReview": {
    "purposeLimitation": { "verdict": "pass", "evidence": "" },
    "dataMinimization": { "verdict": "pass", "evidence": "" },
    "storageLimitation": { "verdict": "not_applicable", "evidence": "" },
    "integrityConfidentiality": { "verdict": "pass", "evidence": "" },
    "accountabilityDocs": { "verdict": "pass", "evidence": "" }
  },
  "privacyByDefault": {
    "verdict": "pass",
    "defaults": [""],
    "evidence": ""
  },
  "loggingTelemetryHygiene": {
    "verdict": "pass",
    "redaction": "present",
    "highCardinalityRisk": "low",
    "evidence": ""
  },
  "nistPrivacyFrameworkNotes": {
    "identifyP": [""],
    "governP": [""],
    "controlP": [""],
    "communicateP": [""],
    "protectP": [""]
  },
  "blockers": [],
  "nonBlockingFindings": [
    { "id": "DPN1", "summary": "", "recommendation": "" }
  ],
  "evidence": [
    { "commandOrCheck": "", "result": "not_run", "notes": "" }
  ],
  "readyForQualityGate": true
}
```

