# Dependency Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Produced at:** <!-- ISO date/time -->
- **Author:** dependency-manager

## Changes
> Dependency changes should be dependency-only unless the task spec explicitly requires code changes.

- **Ecosystem:** <!-- pip/poetry/npm/pnpm/yarn/gomod/docker/github-actions/other -->
- **Files:** <!-- manifest + lockfile paths -->
- **Change type:** security-fix / maintenance / pin / lockfile-refresh / config
- **Summary:** <!-- -->
- **Risk:** low / medium / high

## Lockfile Posture
- **Lockfiles present:** true / false
- **Notes:** <!-- -->
- **Transitive visibility:** good / partial / unknown

## Dependabot
- **Status:** enabled / disabled / not_configured / unknown
- **Config path:** `.github/dependabot.yml`
- **Grouping used:** true / false
- **Notes:** <!-- -->

## Dependency Review Gate
- **Status:** enabled / disabled / not_configured / unknown
- **Workflow paths:** <!-- .github/workflows/... -->
- **Notes:** <!-- -->

## Tests Run (evidence)
| Command | Result | Notes |
|---|---|---|
| <!-- ./scripts/ci/quick_test.sh --> | pass/fail/not_run | <!-- --> |
| <!-- ./scripts/ci/full_test.sh --> | pass/fail/not_run | <!-- --> |

## Known Issues / Blockers
- <!-- setup failure, resolver conflict, test failure, network block, etc. -->

## Follow-ups
- **D1 (low/med/high):** <!-- -->

## Notes to Team Lead
- <!-- -->

---

## Machine-readable DependencyReport (required)
```json
{
  "type": "DependencyReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "changes": [
    {
      "ecosystem": "pip",
      "files": [""],
      "changeType": "maintenance",
      "summary": "",
      "risk": "low"
    }
  ],
  "lockfilePosture": {
    "present": true,
    "notes": [""],
    "transitiveVisibility": "good"
  },
  "dependabot": {
    "status": "unknown",
    "configPath": ".github/dependabot.yml",
    "groupingUsed": false,
    "notes": [""]
  },
  "dependencyReview": {
    "status": "unknown",
    "workflowPaths": [""],
    "notes": [""]
  },
  "testsRun": [
    {
      "command": "",
      "result": "not_run",
      "notes": ""
    }
  ],
  "knownIssues": [],
  "followUps": [
    {
      "id": "D1",
      "priority": "low",
      "summary": ""
    }
  ],
  "notesToTeamLead": [""]
}
```

