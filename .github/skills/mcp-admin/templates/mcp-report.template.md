# MCP Report

status: READY_FOR_QUALITY_GATE|BLOCKED
date: YYYY-MM-DD
owner: mcp-admin
scope:
  github_coding_agent: true|false
  vscode_agent_mode: true|false

## Summary (≤ 12 lines)
- Goal:
- What changed:
- Why:
- Tool exposure delta:
- Secrets handling:
- Verification outcome:
- Rollback:

## Config artifacts
- GitHub Copilot coding agent source-of-truth: `docs/agents/mcp-config.json`
- VS Code workspace config: `.vscode/mcp.json`

## Tool allowlists (explicit)
### GitHub Copilot coding agent
- server: <name>
  - type: local|stdio|http|sse
  - tools allowlisted: [...]
  - write tools enabled: yes/no (justify)

### VS Code
- server: <name>
  - type: stdio|http|sse
  - expected tools: [...]
  - secrets handling: inputs|env|envFile|none

## Secrets plan (no secrets committed)
### GitHub Copilot environment (must be COPILOT_MCP_*)
- COPILOT_MCP_<NAME>: purpose, scope, rotation notes

### VS Code
- inputs:
  - id: <id>, purpose
- env:
  - VAR: purpose
- envFile:
  - path: <path> (must be gitignored)

## Verification evidence
- JSON validation:
  - mcp-config.json: pass/fail (evidence)
  - .vscode/mcp.json: pass/fail (evidence)
- VS Code tool discovery: pass/fail (evidence)
- GitHub config validation: pass/fail (evidence)
- No-secrets check: pass/fail (evidence)

## Risk assessment
risk: low|medium|high
notes:
- <risk note>
rollback:
- <rollback step>

---

```json
{
  "type": "MCPReport",
  "status": "READY_FOR_QUALITY_GATE|BLOCKED",
  "goal": "REPLACE_ME",
  "githubCodingAgentMcp": {
    "changed": true,
    "sourceOfTruthPath": "docs/agents/mcp-config.json",
    "servers": [
      {
        "name": "REPLACE_ME",
        "type": "local|stdio|http|sse",
        "toolsAllowlisted": ["REPLACE_ME"],
        "writeToolsEnabled": false,
        "secretsUsed": ["COPILOT_MCP_REPLACE_ME"],
        "notes": "REPLACE_ME"
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
        "name": "REPLACE_ME",
        "type": "stdio|http|sse",
        "commandOrUrl": "REPLACE_ME",
        "secretsHandling": "inputs|env|envFile|none",
        "notes": "REPLACE_ME"
      }
    ]
  },
  "verification": [
    {
      "check": "json-validate|tool-discovery|smoke-call|no-secrets-scan",
      "result": "pass|fail|not_run",
      "evidence": "REPLACE_ME"
    }
  ],
  "riskAssessment": {
    "risk": "low|medium|high",
    "notes": ["REPLACE_ME"],
    "rollback": ["REPLACE_ME"]
  },
  "blockers": [],
  "notesToTeamLead": ["REPLACE_ME"]
}
```


