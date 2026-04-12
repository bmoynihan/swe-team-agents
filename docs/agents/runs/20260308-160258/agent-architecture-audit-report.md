# Agent Architecture Audit Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Audited at:** <!-- ISO date/time -->
- **Auditor:** agent-arch-auditor
- **Ready for Quality Gate:** true / false

## Inventory
- **Agent files:** <!-- count -->
- **Skill files:** <!-- count -->
- **Instruction files:** <!-- count -->
- **Hook files:** <!-- count -->
- **Workflow files:** <!-- count -->
- **Artifact files:** <!-- count -->

## Canonical Sources
- **Team state:** `docs/agents/state.json`
- **Task spec:** `docs/agents/task-spec.md`
- **Patch report:** `docs/agents/patch-report.md`
- **Test report:** `docs/agents/test-report.md`
- **Quality gate report:** `docs/agents/review-report.md`
- **Release report:** `docs/agents/release-report.md`

## Compatibility Checks
- **Check:** <!-- -->
  - **Result:** pass / fail / not_run
  - **Evidence:** <!-- -->

## Findings
- **AA1 — <severity> / <category>:**
  - **File:** <!-- -->
  - **Evidence:** <!-- -->
  - **Risk:** <!-- -->
  - **Recommended fix:** <!-- -->
  - **Owner:** <!-- -->

## Recommended Patch Plan
- <!-- ordered smallest-safe change -->

## Notes to Team Lead
- <!-- -->

---

## Machine-readable AgentArchitectureAuditReport (required)
```json
{
  "type": "AgentArchitectureAuditReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "inventory": {
    "agentFiles": 0,
    "skillFiles": 0,
    "instructionFiles": 0,
    "hookFiles": 0,
    "workflowFiles": 0,
    "artifactFiles": 0
  },
  "canonicalSources": {
    "teamState": "docs/agents/state.json",
    "taskSpec": "docs/agents/task-spec.md",
    "patchReport": "docs/agents/patch-report.md",
    "testReport": "docs/agents/test-report.md",
    "qualityGateReport": "docs/agents/review-report.md",
    "releaseReport": "docs/agents/release-report.md"
  },
  "compatibilityChecks": [
    {
      "check": "custom-agent-paths",
      "result": "pass",
      "evidence": ""
    }
  ],
  "findings": [
    {
      "id": "AA1",
      "severity": "medium",
      "category": "determinism",
      "file": "",
      "evidence": "",
      "risk": "",
      "recommendedFix": "",
      "owner": ""
    }
  ],
  "recommendedPatchPlan": [""],
  "notesToTeamLead": [""],
  "readyForQualityGate": true
}
```
