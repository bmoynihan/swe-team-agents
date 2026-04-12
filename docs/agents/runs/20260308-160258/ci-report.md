# CI Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Produced at:** <!-- ISO date/time -->
- **Author:** ci-engineer

## Workflows Touched
- `<!-- .github/workflows/....yml -->` — <!-- add/update/fix/tighten-permissions + why -->

## Permissions Review
> Least privilege by default; job-level overrides only when needed.

- **Default workflow permissions:** <!-- e.g., contents: read -->
- **Job overrides:**
  - <!-- job: perms + justification -->

## Action Supply Chain Notes
> Prefer trusted actions; pin immutably when policy requires; avoid broad permissions.

- `<!-- owner/action@ref -->` — pinning: sha/tag/none — risk: low/med/high — notes: <!-- -->

## Caching
> Use caching only when it improves runtime and remains correct.

- **Used:** true / false
- **Paths cached:** <!-- -->
- **Key strategy:** <!-- based on lockfiles -->
- **Restore keys:** <!-- -->
- **Notes:** <!-- -->

## Commands Aligned to Task Spec
- **Fast subset:**
  - `<!-- -->`
- **Full suite:**
  - `<!-- -->`
- **Notes:**
  - <!-- -->

## Evidence
| Command / Run | Result | Notes |
|---|---|---|
| <!-- ./scripts/ci/quick_test.sh --> | pass/fail/not_run | <!-- --> |
| <!-- ./scripts/ci/full_test.sh --> | pass/fail/not_run | <!-- --> |

## Known Issues / Blockers
- <!-- category + evidence + next step -->

## Notes to Team Lead
- <!-- -->

---

## Machine-readable CIReport (required)
```json
{
  "type": "CIReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "workflowsTouched": [
    {
      "path": ".github/workflows/ci.yml",
      "changeType": "add",
      "summary": ""
    }
  ],
  "permissionsReview": {
    "defaultPermissions": "",
    "jobOverrides": [
      {
        "job": "",
        "permissions": "",
        "justification": ""
      }
    ],
    "notes": [""]
  },
  "actionSupplyChainNotes": [
    {
      "action": "actions/checkout@v5",
      "pinning": "tag",
      "risk": "low",
      "notes": ""
    }
  ],
  "caching": [
    {
      "used": false,
      "action": "actions/cache",
      "paths": [""],
      "keyStrategy": "",
      "restoreKeys": [""],
      "notes": ""
    }
  ],
  "commandsAlignedToSpec": {
    "fastSubset": [""],
    "fullSuite": [""],
    "notes": [""]
  },
  "evidence": [
    {
      "commandOrRun": "",
      "result": "pass",
      "notes": ""
    }
  ],
  "knownIssues": [],
  "notesToTeamLead": [""]
}
```

