# Change Plan (Implementer)

## Human summary (≤10 lines)
- Goal:
- ACs in scope:
- Expected files:
- Test plan (fast subset + targeted/full):
- Risk & rollback:

```json
{
  "type": "ChangePlan",
  "goal": "<copy from task spec>",
  "acceptanceInScope": ["AC1", "AC2"],
  "approach": [
    "<step 1: smallest code change>",
    "<step 2: add/adjust minimal test>",
    "<step 3: run validation>"
  ],
  "expectedFiles": ["src/<path>.py", "tests/<path>_test.py"],
  "validationPlan": {
    "fastSubset": ["<command>"],
    "fullOrTargeted": ["<command>"]
  },
  "risks": [
    {
      "risk": "<what could go wrong>",
      "severity": "low|medium|high",
      "mitigation": "<how you’ll reduce risk>",
      "rollback": "<how to revert safely>"
    }
  ]
}
```

