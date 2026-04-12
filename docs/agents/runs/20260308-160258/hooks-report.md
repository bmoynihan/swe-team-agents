# Hooks Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Produced at:** <!-- ISO date/time -->
- **Author:** hooks-engineer

## Hook Configs
- **Primary config:** `.github/hooks/hooks.json`
- **Events wired:**
  - sessionStart
  - preToolUse
  - postToolUse
  - errorOccurred
  - sessionEnd
- **Timeouts:**
  - preToolUse: 10s
  - postToolUse: 10s
  - sessionEnd: 30s

## Scripts
| Path | Purpose |
|---|---|
| `scripts/hooks/pretool_denylist.sh` | deny high-risk tool calls |
| `scripts/hooks/audit_log.sh` | append audit entries |
| `scripts/hooks/session_start.sh` | session start marker + readiness checks |
| `scripts/hooks/session_end.sh` | session summary artifact |
| `scripts/hooks/smoke_test.sh` | local smoke tests |
| `scripts/hooks/pretool_denylist.ps1` | PowerShell denylist |
| `scripts/hooks/audit_log.ps1` | PowerShell audit logger |
| `scripts/hooks/session_start.ps1` | PowerShell session start |
| `scripts/hooks/session_end.ps1` | PowerShell session end |
| `scripts/hooks/smoke_test.ps1` | PowerShell smoke tests |

## Deny Policy
### High-risk patterns blocked
- destructive deletes (e.g., `rm -rf /`, `rm -rf ..`, `.git` nukes)
- credential harvesting (e.g., reading SSH keys, cloud creds, `.env`)
- obvious exfiltration (archive + network upload, curl upload flags, raw sockets)

### False-positive mitigations
- does not block normal downloads (`curl URL`)
- does not block targeted env access (`printenv VAR`)
- deny rules are pattern-based and narrow

## Audit Trail
- **Format:** JSONL
- **Location:** `docs/agents/runs/<run-id>/hook-audit/tool-audit.jsonl`
- **Redaction:** present
  - command output previews are truncated
  - common secret patterns are redacted
  - full payloads are not recorded
- **Session summary:** `docs/agents/runs/<run-id>/hook-audit/session-summary.json`

## Validation
| Check | Result | Evidence |
|---|---|---|
| jq-validate | pass/fail/not_run | <!-- jq . .github/hooks/hooks.json --> |
| deny-smoke | pass/fail/not_run | <!-- scripts/hooks/smoke_test.sh --> |
| audit-smoke | pass/fail/not_run | <!-- confirms JSONL append + summary --> |
| powershell-smoke | pass/fail/not_run | <!-- scripts/hooks/smoke_test.ps1 --> |

## Known Issues / Blockers
- <!-- policy too strict/loose, missing PowerShell on runner, etc. -->

## Notes to Team Lead
- <!-- -->

---

## Machine-readable HooksReport (required)
```json
{
  "type": "HooksReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "hookConfigs": [
    {
      "path": ".github/hooks/hooks.json",
      "events": ["sessionStart", "preToolUse", "postToolUse", "errorOccurred", "sessionEnd"],
      "timeouts": { "preToolUse": 10, "postToolUse": 10, "sessionEnd": 30 },
      "notes": ""
    }
  ],
  "scripts": [
    { "path": "scripts/hooks/pretool_denylist.sh", "purpose": "deny high-risk tool calls" },
    { "path": "scripts/hooks/audit_log.sh", "purpose": "append audit entries" },
    { "path": "scripts/hooks/session_start.sh", "purpose": "session start marker + readiness checks" },
    { "path": "scripts/hooks/session_end.sh", "purpose": "session summary artifact" }
  ],
  "denyPolicy": {
    "highRiskPatterns": ["destructive deletes", "credential harvesting", "exfiltration patterns"],
    "falsePositiveMitigations": ["allow normal curl downloads", "allow targeted printenv VAR", "narrow regex rules"],
    "notes": ""
  },
  "auditTrail": {
    "format": "jsonl",
    "location": "docs/agents/runs/<run-id>/hook-audit/tool-audit.jsonl",
    "redaction": "present",
    "notes": ""
  },
  "validation": [
    { "check": "jq-validate", "result": "not_run", "evidence": "" },
    { "check": "deny-smoke", "result": "not_run", "evidence": "" },
    { "check": "audit-smoke", "result": "not_run", "evidence": "" },
    { "check": "powershell-smoke", "result": "not_run", "evidence": "" }
  ],
  "knownIssues": [],
  "notesToTeamLead": [""]
}
```


