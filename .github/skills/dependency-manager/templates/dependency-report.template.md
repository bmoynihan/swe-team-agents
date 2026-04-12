# Dependency Report

<≤12 lines: what changed, why, and what evidence you collected.>

```json
{
  "type": "DependencyReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "changes": [
    {
      "ecosystem": "pip|poetry|npm|pnpm|yarn|gomod|maven|gradle|docker|github-actions|other",
      "files": [],
      "changeType": "security-fix|maintenance|pin|lockfile-refresh|config",
      "summary": "",
      "risk": "low|medium|high"
    }
  ],
  "lockfilePosture": {
    "present": true,
    "notes": [],
    "transitiveVisibility": "good|partial|unknown"
  },
  "dependabot": {
    "status": "enabled|disabled|not_configured|unknown",
    "configPath": ".github/dependabot.yml",
    "groupingUsed": false,
    "notes": []
  },
  "dependencyReview": {
    "status": "enabled|disabled|not_configured|unknown",
    "workflowPaths": [],
    "notes": []
  },
  "testsRun": [
    { "command": "", "result": "pass|fail|not_run", "notes": "" }
  ],
  "knownIssues": [
    {
      "category": "setup_failure|resolver_conflict|test_or_runtime_failure|network_block|tool_denial|permission_or_governance_block",
      "evidence": "",
      "nextStep": ""
    }
  ],
  "followUps": [
    { "id": "D1", "priority": "low|medium|high", "summary": "" }
  ],
  "notesToTeamLead": []
}
```


