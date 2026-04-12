# Security Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Produced at:** <!-- ISO date/time -->
- **Author:** security-engineer

## Checks Performed
| Check | Result | Evidence |
|---|---|---|
| secrets_hygiene | pass/fail/not_run | <!-- grep/search notes --> |
| actions_least_privilege | pass/fail/not_run | <!-- workflow permissions review --> |
| dependency_supply_chain | pass/fail/not_run | <!-- dependency diff, advisories --> |
| code_scanning_codeql | pass/fail/not_run | <!-- CodeQL workflow/config --> |
| agent_controls_hooks_mcp | pass/fail/not_run | <!-- hooks + MCP review --> |

## Blockers (must fix before Quality Gate)
- **S1 — <category>:** <!-- secrets | actions-permissions | dependency-risk | code-scanning | exfiltration-risk | other -->
  - **Summary:** <!-- -->
  - **Evidence:** <!-- -->
  - **Recommended fix:** <!-- -->

## Recommendations
- **R1 (low/medium/high):** <!-- -->
  - **Rationale:** <!-- -->
  - **Suggested change:** <!-- -->

## Workflow Notes
- <!-- e.g., Copilot PR workflows may require maintainer approval to run; record local evidence. -->

## MCP & Setup Steps Notes
- <!-- call out least privilege, allowlists, firewall scope gap, secret handling -->

## Files Reviewed
- <!-- list key files (workflows, manifests, etc.) -->

## Commands Run
| Command | Result | Notes |
|---|---|---|
| <!-- --> | pass/fail/not_run | <!-- --> |

## Notes to Team Lead
- <!-- -->

---

## Machine-readable SecurityReport (required)
```json
{
  "type": "SecurityReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "checksPerformed": [
    { "name": "secrets_hygiene", "result": "pass", "evidence": "" },
    { "name": "actions_least_privilege", "result": "pass", "evidence": "" },
    { "name": "dependency_supply_chain", "result": "pass", "evidence": "" },
    { "name": "code_scanning_codeql", "result": "not_run", "evidence": "" },
    { "name": "agent_controls_hooks_mcp", "result": "pass", "evidence": "" }
  ],
  "blockers": [],
  "recommendations": [
    {
      "id": "R1",
      "priority": "low",
      "summary": "",
      "rationale": "",
      "suggestedChange": ""
    }
  ],
  "workflowNotes": [
    "Workflows may require maintainer approval to run on Copilot-created PRs."
  ],
  "mcpAndSetupStepsNotes": [
    "Treat MCP servers and setup steps as privileged; enforce least-privilege tool allowlists and secret handling."
  ],
  "filesReviewed": [],
  "commandsRun": [
    { "command": "", "result": "not_run", "notes": "" }
  ],
  "notesToTeamLead": [""]
}
```

