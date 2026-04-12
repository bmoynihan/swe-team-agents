# Docs Report

## Summary (≤ 12 lines)
- Goal:
- What changed (doc-visible):
- Docs updated:
- Examples added:
- Troubleshooting added:
- Validation steps included:
- Open questions / known issues (if any):

```json
{
  "type": "DocsReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "<one sentence from task spec>",
  "docsUpdated": [
    {
      "path": "README.md",
      "changeType": "update",
      "summary": "<what changed>"
    }
  ],
  "acceptanceDocsMapping": [
    {
      "ac": "AC1",
      "docEvidence": [
        "README.md#<section> or docs/<path>#<section>"
      ],
      "validationStepsIncluded": [
        "<command or step included in docs>"
      ]
    }
  ],
  "examplesAdded": [
    {
      "location": "README.md#<section>",
      "whatItDemonstrates": "<happy path usage>",
      "notes": "<placeholders used / assumptions>"
    }
  ],
  "troubleshootingAdded": [
    {
      "symptom": "<what the user sees>",
      "cause": "<likely cause>",
      "fix": "<actionable fix>",
      "location": "docs/<path>#<section>"
    }
  ],
  "knownIssues": [
    {
      "category": "spec_ambiguity",
      "evidence": "<what is missing/unclear>",
      "nextStep": "<what the Team Lead should clarify>"
    }
  ],
  "notesToTeamLead": [
    "<review focus areas, doc gaps, follow-ups>"
  ]
}
```


