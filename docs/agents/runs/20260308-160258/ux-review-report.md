# UX Review Report

## Summary
- **Status:** PASS / FAIL
- **Goal:** <!-- one sentence -->
- **Reviewed at:** <!-- ISO date/time -->
- **Reviewer:** ux-reviewer
- **Ready for Quality Gate:** true / false

## Heuristics Review (high-signal)
> Keep notes concise and evidence-based.

| Heuristic | Verdict | Evidence | Notes |
|---|---|---|---|
| visibility | pass/fail | <!-- --> | <!-- --> |
| match | pass/fail | <!-- --> | <!-- --> |
| control | pass/fail | <!-- --> | <!-- --> |
| consistency | pass/fail | <!-- --> | <!-- --> |
| error-prevention | pass/fail | <!-- --> | <!-- --> |
| recognition | pass/fail | <!-- --> | <!-- --> |
| efficiency | pass/fail | <!-- --> | <!-- --> |
| minimalism | pass/fail | <!-- --> | <!-- --> |
| error-recovery | pass/fail | <!-- --> | <!-- --> |
| help | pass/fail | <!-- --> | <!-- --> |

## Accessibility Review (WCAG 2.2 AA-oriented)
- **Keyboard:** pass / fail — Evidence: <!-- -->
- **Focus visibility / not obscured:** pass / fail — Evidence: <!-- -->
- **Semantics (labels/headings/roles):** pass / fail — Evidence: <!-- -->
- **Contrast:** pass / fail / not_checked — Evidence: <!-- -->
- **Target size:** pass / fail / not_checked — Evidence: <!-- -->

## States Review
| State | Verdict | Notes |
|---|---|---|
| loading | pass/fail | <!-- --> |
| empty | pass/fail | <!-- --> |
| error | pass/fail | <!-- --> |
| success | pass/fail | <!-- --> |
| partial | pass/fail | <!-- --> |

## Blockers
- **UX1 — <category>:** <!-- accessibility | usability | copy | consistency | edge-case -->
  - **Summary:** <!-- -->
  - **Evidence:** <!-- -->
  - **Recommended fix:** <!-- -->

## Non-blocking Findings
- **UXN1:** <!-- -->

## Evidence
| Command / Check | Result | Notes |
|---|---|---|
| <!-- unit/e2e/a11y check if exists --> | pass/fail/not_run | <!-- --> |

---

## Machine-readable UXReviewReport (required)
```json
{
  "type": "UXReviewReport",
  "status": "PASS",
  "goal": "",
  "heuristicsReview": [
    { "heuristic": "visibility", "verdict": "pass", "evidence": "", "notes": "" }
  ],
  "accessibilityReview": {
    "wcagTarget": "2.2 AA-oriented",
    "keyboard": { "verdict": "pass", "evidence": "" },
    "focus": { "verdict": "pass", "evidence": "" },
    "semantics": { "verdict": "pass", "evidence": "" },
    "contrast": { "verdict": "not_checked", "evidence": "" },
    "targetSize": { "verdict": "not_checked", "evidence": "" }
  },
  "statesReview": [
    { "state": "loading", "verdict": "pass", "notes": "" }
  ],
  "blockers": [],
  "nonBlockingFindings": [
    { "id": "UXN1", "summary": "", "recommendation": "" }
  ],
  "evidence": [
    { "commandOrCheck": "", "result": "not_run", "notes": "" }
  ],
  "readyForQualityGate": true
}
```

