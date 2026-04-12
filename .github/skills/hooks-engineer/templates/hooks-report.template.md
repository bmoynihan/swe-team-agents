# Hooks Report

(≤12 lines) What changed, why, and the safety/traceability impact. Mention any deny policy changes and the validation evidence.

```json
{
  "type": "HooksReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "Add/tune Copilot hooks for denylist enforcement + audit logging",
  "hookConfigs": [
    {
      "path": ".github/hooks/hooks.json",
      "events": ["sessionStart", "preToolUse", "postToolUse", "errorOccurred", "sessionEnd"],
      "timeouts": { "preToolUse": 10, "postToolUse": 10, "sessionEnd": 30 },
      "notes": "Describe wiring and any notable constraints."
    }
  ],
  "scripts": [
    { "path": "scripts/hooks/pretool_denylist.sh", "purpose": "deny high-risk tool calls" },
    { "path": "scripts/hooks/audit_log.sh", "purpose": "append audit entries as JSONL" },
    { "path": "scripts/hooks/session_start.sh", "purpose": "session start marker + lightweight checks" },
    { "path": "scripts/hooks/session_end.sh", "purpose": "session summary artifact" },
    { "path": "scripts/hooks/smoke_test.sh", "purpose": "deterministic validation (jq + pipe tests)" }
  ],
  "denyPolicy": {
    "highRiskPatterns": [
      "rm -rf /( |$)",
      "rm -rf ~(/|$)",
      "rm -rf \\.\\.( |/|$)",
      "cat .*id_rsa",
      "(tar|zip).*(curl|wget|nc)"
    ],
    "falsePositiveMitigations": [
      "Only apply destructive patterns to shell-like tools",
      "Hash toolArgs; don't store raw args",
      "Prefer allow-by-default with narrow denies"
    ],
    "notes": "Keep policy precise; explain any scope exceptions."
  },
  "auditTrail": {
    "format": "jsonl",
    "location": "docs/agents/runs/<run-id>/hook-audit/tool-audit.jsonl",
    "redaction": "present",
    "notes": "Args are hashed; sensitive fields are redacted."
  },
  "validation": [
    { "check": "jq-validate", "result": "pass", "evidence": "jq . .github/hooks/hooks.json" },
    { "check": "deny-smoke", "result": "pass", "evidence": "fixtures/deny_rm_rf.json piped into pretool_denylist.sh" },
    { "check": "audit-smoke", "result": "pass", "evidence": "fixtures/audit_sample.json piped into audit_log.sh" }
  ],
  "knownIssues": [],
  "notesToTeamLead": [
    "If repeated denies occur for the same command signature, treat as mis-scoping or prompt injection and escalate."
  ]
}
```

