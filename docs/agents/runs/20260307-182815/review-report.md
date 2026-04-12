# Quality Gate Review Report

## Summary
- **Status:** PASS / FAIL
- **Goal:** <!-- one sentence -->
- **Reviewed at:** <!-- ISO date/time -->
- **Reviewer:** quality-gate
- **Ready for human review:** true / false

## Governance Notes
- <!-- e.g., GitHub Actions may require maintainer approval to run on Copilot PRs; local/in-session evidence is required. -->

## Acceptance Criteria Review
> For each AC, provide evidence and a clear pass/fail verdict.

### AC1
- **Verdict:** pass / fail
- **Evidence:**
  - <!-- command/test + key result -->
- **Notes:** <!-- brief -->

### AC2
- **Verdict:** pass / fail
- **Evidence:**
  - <!-- -->
- **Notes:** <!-- -->

## Tests & Evidence
| Command / Check | Result | Notes |
|---|---|---|
| <!-- ./scripts/ci/quick_test.sh --> | pass/fail/not_run | <!-- --> |
| <!-- ./scripts/ci/full_test.sh --> | pass/fail/not_run | <!-- --> |

## Security Hygiene
- **Verdict:** pass / fail
- **Checks performed:**
  - <!-- secrets scan (manual grep, etc.) -->
  - <!-- workflow permissions review -->
  - <!-- dependency/license/vuln notes -->
- **Notes:**
  - <!-- high-signal only -->

## Diff Review
- **Scope:** appropriate / too_broad
- **Risk level:** low / medium / high
- **Hotspots:**
  - <!-- file paths / symbols that deserve extra scrutiny -->
- **Notes:**
  - <!-- drive-by refactors? API changes? compatibility concerns? -->

## Blockers (FAIL conditions)
> If **Status = FAIL**, list minimal actionable blockers.

- **B1 — <category>:** <!-- spec_mismatch | missing_evidence | test_failure | flake_risk | security | governance | other -->
  - **Summary:** <!-- -->
  - **Evidence:** <!-- -->
  - **Recommended fix:** <!-- -->

- **B2 — <category>:**
  - **Summary:** <!-- -->
  - **Evidence:** <!-- -->
  - **Recommended fix:** <!-- -->

## Non-blocking Findings
- **N1:** <!-- -->
- **N2:** <!-- -->

---

## Machine-readable ReviewReport (required)
```json
{
  "type": "ReviewReport",
  "status": "PASS",
  "goal": "",
  "specVersion": "",
  "acceptanceReview": [
    { "ac": "AC1", "verdict": "pass", "evidence": [""], "notes": "" }
  ],
  "testsEvidence": [
    { "command": "", "result": "pass", "notes": "" }
  ],
  "securityHygiene": {
    "verdict": "pass",
    "checks": [""],
    "notes": [""]
  },
  "diffReview": {
    "scope": "appropriate",
    "risk": "low",
    "notes": [""],
    "hotspots": [""]
  },
  "blockers": [],
  "nonBlockingFindings": [
    { "id": "N1", "summary": "", "recommendation": "" }
  ],
  "governanceNotes": [
    "Workflows may require maintainer approval to run on Copilot-created PRs."
  ],
  "readyForHumanReview": true
}
```
