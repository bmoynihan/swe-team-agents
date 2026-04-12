# Patch Report

## Summary (≤10 lines)
- Goal:
- ACs implemented:
- High-level approach:
- Risk notes:
- What to test next (handoff):

```json
{
  "type": "PatchReport",
  "status": "READY_FOR_TEST_ENGINEER",
  "goal": "<copy from task spec goal>",
  "acceptanceImplemented": ["AC1"],
  "changes": [
    {
      "file": "src/<path>.py",
      "summary": "<what changed and why>",
      "risk": "low"
    }
  ],
  "testsRun": [
    {
      "command": "<fast subset command>",
      "result": "pass",
      "notes": "<key output / runtime / caveats>"
    }
  ],
  "knownIssues": [],
  "handoffToTestEngineer": {
    "focusAreas": ["<edge cases / regressions to probe>"],
    "suggestedTests": ["<test names or commands>"],
    "edgeCases": ["<weird inputs, boundaries, error paths>"]
  },
  "notesToTeamLead": ["<spec ambiguity, follow-ups, tradeoffs>"]
}
```

