# Review summary
- Verdict: PASS or FAIL
- Goal: <one-sentence goal>
- Scope: <appropriate|too_broad>
- Risk: <low|medium|high>
- Ready for human review: <true|false>
- Top blocker or confidence note: <short sentence>

```json
{
  "type": "ReviewReport",
  "status": "FAIL",
  "goal": "<copy the task goal or concise summary>",
  "specVersion": "<commit hash, date, or version label>",
  "acceptanceReview": [
    {
      "ac": "AC1",
      "verdict": "fail",
      "evidence": [
        "<test, command output, artifact, or diff observation>"
      ],
      "notes": "<why this AC passes or fails>"
    }
  ],
  "testsEvidence": [
    {
      "command": "<exact command or test invocation>",
      "result": "not_run",
      "notes": "<what happened or why not run>"
    }
  ],
  "securityHygiene": {
    "verdict": "pass",
    "checks": [
      "No committed secrets detected in touched files",
      "No obvious workflow permission escalation",
      "No suspicious exfiltration commands in changed scripts"
    ],
    "notes": [
      "<add any caveats or leave this as a benign note>"
    ]
  },
  "diffReview": {
    "scope": "appropriate",
    "risk": "medium",
    "notes": [
      "<high-level reviewability and scope note>",
      "<compatibility/performance/maintainability note if relevant>"
    ],
    "hotspots": [
      "<path/to/file>",
      "<module.symbol>"
    ]
  },
  "blockers": [
    {
      "id": "B1",
      "category": "missing_evidence",
      "summary": "<single blocker statement>",
      "evidence": "<what proves the blocker exists>",
      "recommendedFix": "<smallest concrete next action>"
    }
  ],
  "nonBlockingFindings": [
    {
      "id": "N1",
      "summary": "<optional improvement that should not block>",
      "recommendation": "<clear follow-up>"
    }
  ],
  "governanceNotes": [
    "Copilot-created PR workflows may require a maintainer to approve and run workflows before GitHub Actions evidence appears.",
    "Pending CI is not sufficient for PASS unless equivalent local or in-session evidence exists."
  ],
  "readyForHumanReview": false
}
```


