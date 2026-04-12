# Security Report

> Keep this ≤12 lines. State: what you reviewed, what you ran, and the ship/no-ship security status.

```json
{
  "type": "SecurityReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "<short goal from task-spec>",
  "checksPerformed": [
    {"name": "secrets_hygiene", "result": "pass", "evidence": "<command/snippet>"},
    {"name": "actions_least_privilege", "result": "not_run", "evidence": "<why>"},
    {"name": "dependency_supply_chain", "result": "not_run", "evidence": "<why>"},
    {"name": "code_scanning_codeql", "result": "not_run", "evidence": "<why>"},
    {"name": "agent_controls_hooks_mcp", "result": "not_run", "evidence": "<why>"}
  ],
  "blockers": [],
  "recommendations": [],
  "workflowNotes": [],
  "mcpAndSetupStepsNotes": [],
  "filesReviewed": [],
  "commandsRun": [],
  "notesToTeamLead": []
}
```


