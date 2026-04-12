# UX Review Summary

Status: `PASS|FAIL`  
Goal: `<one-sentence goal>`  
Scope: `<what changed>`  
Primary journeys: `<journey 1>; <journey 2>`  
Key evidence: `<tests/checks/manual review steps>`  
Top blockers: `<none or short list>`  
Non-blocking findings: `<none or short list>`  
Ready for Quality Gate: `<true|false>`

```json
{
  "type": "UXReviewReport",
  "status": "FAIL",
  "goal": "Review the updated settings form flow for usability, accessibility, and design-system consistency.",
  "scope": {
    "summary": "Settings form validation, save feedback, and empty-state copy were changed.",
    "pathsReviewed": [
      "src/routes/settings.tsx",
      "src/components/SettingsForm.tsx",
      "src/components/InlineError.tsx"
    ],
    "userJourneys": [
      "Edit settings and save successfully",
      "Submit invalid data and recover from errors"
    ]
  },
  "specAlignment": [
    {
      "acceptanceCriterion": "Users can save valid settings and receive confirmation.",
      "verdict": "pass",
      "evidence": "Save confirmation banner appears after successful submit in src/components/SettingsForm.tsx."
    },
    {
      "acceptanceCriterion": "Validation errors are shown clearly and are recoverable.",
      "verdict": "fail",
      "evidence": "Inline errors render visually, but focus does not move to the first invalid field and error summary is absent."
    }
  ],
  "heuristicsReview": [
    {
      "heuristic": "visibility",
      "verdict": "pass",
      "evidence": "Saving state is visible with a pending button label and success confirmation.",
      "notes": "No silent submit."
    },
    {
      "heuristic": "error-recovery",
      "verdict": "fail",
      "evidence": "Users receive an error message, but the first corrective action is not highlighted.",
      "notes": "Recovery is slower than necessary."
    }
  ],
  "accessibilityReview": {
    "wcagTarget": "2.2 AA-oriented",
    "keyboard": {"verdict": "pass", "evidence": "Tab order follows field order and submit button is reachable."},
    "focus": {"verdict": "fail", "evidence": "After submit with invalid data, focus remains on the button rather than moving to the first invalid field."},
    "semantics": {"verdict": "pass", "evidence": "Field labels are programmatically associated with inputs."},
    "formsAndErrors": {"verdict": "fail", "evidence": "Errors are visible but not announced clearly for assistive technology users."},
    "contrast": {"verdict": "not_checked", "evidence": "No automated or measured contrast evidence was found in this session."},
    "targetSize": {"verdict": "pass", "evidence": "Primary controls appear comfortably sized and spaced."},
    "statusMessages": {"verdict": "pass", "evidence": "Success banner is persistent long enough to be perceived."}
  },
  "contentReview": [
    {
      "area": "buttons",
      "verdict": "pass",
      "evidence": "Primary action uses the concrete verb 'Save settings'."
    },
    {
      "area": "errors",
      "verdict": "fail",
      "evidence": "Error copy says 'Invalid payload' instead of telling users what field needs correction."
    }
  ],
  "statesReview": [
    {"state": "loading", "verdict": "pass", "notes": "Pending submit is visible."},
    {"state": "validation", "verdict": "fail", "notes": "Validation state is visible but not easy to recover from."},
    {"state": "success", "verdict": "pass", "notes": "Success confirmation is clear."},
    {"state": "error", "verdict": "fail", "notes": "Form-level failure messaging is too technical."}
  ],
  "designSystemConsistency": {
    "verdict": "pass",
    "evidence": "Existing button, field, and banner primitives are reused."
  },
  "blockers": [
    {
      "id": "UX1",
      "category": "accessibility",
      "summary": "Validation failure does not move focus to the first invalid field or expose a clear recovery path.",
      "evidence": "Focus remains on submit after invalid submit; no error summary or linked recovery cue was found.",
      "recommendedFix": "Move focus to the first invalid control or a linked error summary and ensure errors are announced."
    },
    {
      "id": "UX2",
      "category": "copy",
      "summary": "Technical error copy leaks implementation language into the UI.",
      "evidence": "The message 'Invalid payload' does not tell users what to fix.",
      "recommendedFix": "Replace technical wording with field-specific, actionable guidance."
    }
  ],
  "nonBlockingFindings": [
    {
      "id": "UXN1",
      "summary": "Empty-state helper text could mention where defaults come from.",
      "recommendation": "Add one sentence explaining the source of default settings if users commonly arrive here first."
    }
  ],
  "evidence": [
    {
      "commandOrCheck": "Manual code review of updated settings flow",
      "result": "pass",
      "notes": "Reviewed the changed components and submit logic."
    },
    {
      "commandOrCheck": "Existing form tests",
      "result": "not_run",
      "notes": "No session evidence was captured for a focused validation/error test."
    }
  ],
  "readyForQualityGate": false
}
```


