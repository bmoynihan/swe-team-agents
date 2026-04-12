# MCP Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Produced at:** <!-- ISO date/time -->
- **Author:** mcp-admin

## GitHub Coding Agent MCP
> GitHub coding agent MCP is configured in **repo settings**, but we keep a version-controlled source-of-truth copy in-repo.

- **Source of truth:** `docs/agents/mcp-config.json`
- **Changed:** true / false

### Servers
| Name | Type | Tools allowlisted | Write tools enabled | Secrets used | Notes |
|---|---|---|---|---|---|
| <!-- --> | stdio/http/sse/etc | <!-- --> | true/false | <!-- COPILOT_MCP_* --> | <!-- --> |

### Limitations noted
- tools-only (no prompts/resources)
- remote OAuth-based auth not supported (avoid OAuth-required servers)

## VS Code MCP
- **Path:** `.vscode/mcp.json`
- **Changed:** true / false

### Servers
| Name | Type | Command/URL | Secrets handling | Notes |
|---|---|---|---|---|
| <!-- --> | stdio/http/sse | <!-- --> | inputs/env/envfile/none | <!-- --> |

## Verification
| Check | Result | Evidence |
|---|---|---|
| json-validate | pass/fail/not_run | <!-- jq/python parse result --> |
| tool-discovery | pass/fail/not_run | <!-- VS Code MCP server list/logs --> |
| smoke-call | pass/fail/not_run | <!-- a safe read-only tool call --> |
| no-secrets-scan | pass/fail/not_run | <!-- grep for COPILOT_MCP_ or tokens committed --> |

## Risk Assessment
- **Risk:** low / medium / high
- **Notes:** <!-- why -->
- **Rollback:**
  1. <!-- revert config change -->
  2. <!-- remove server / reduce tool allowlist -->
  3. <!-- verify -->

## Blockers
- <!-- invalid JSON, tool too broad, secret risk, untrusted server, etc. -->

## Notes to Team Lead
- <!-- -->

---

## Machine-readable MCPReport (required)
```json
{
  "type": "MCPReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "githubCodingAgentMcp": {
    "changed": false,
    "sourceOfTruthPath": "docs/agents/mcp-config.json",
    "servers": [
      {
        "name": "",
        "type": "stdio",
        "toolsAllowlisted": [""],
        "writeToolsEnabled": false,
        "secretsUsed": ["COPILOT_MCP_EXAMPLE_TOKEN"],
        "notes": ""
      }
    ],
    "limitationsNoted": [
      "tools-only (no prompts/resources)",
      "no OAuth-based remote auth"
    ]
  },
  "vscodeMcp": {
    "changed": false,
    "path": ".vscode/mcp.json",
    "servers": [
      {
        "name": "",
        "type": "stdio",
        "commandOrUrl": "",
        "secretsHandling": "env",
        "notes": ""
      }
    ]
  },
  "verification": [
    {
      "check": "json-validate",
      "result": "not_run",
      "evidence": ""
    }
  ],
  "riskAssessment": {
    "risk": "low",
    "notes": [""],
    "rollback": [""]
  },
  "blockers": [],
  "notesToTeamLead": [""]
}
```


