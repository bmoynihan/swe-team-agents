# Research Report

> Owner: Repo Researcher  
> Status: draft (update to final when ready)  
> Output contract: ≤10 lines summary + exactly one `ResearchReport` JSON object.

## Human summary (≤10 lines)
- Goal:
- Repro status:
- Primary suspect area:
- Top hypothesis:
- Biggest risk:
- Blocker (if any):

```json
{
  "type": "ResearchReport",
  "goal": "<one sentence>",
  "constraints": ["<constraint 1>", "<constraint 2>"],
  "repro": {
    "status": "reproduced",
    "steps": [
      "<command(s) or steps to reproduce>"
    ],
    "expected": "<expected behavior>",
    "actual": "<actual behavior / error>",
    "notes": "<env notes, flakiness, required setup>"
  },
  "hypotheses": [
    {
      "id": "H1",
      "statement": "<most likely root cause>",
      "confidence": 0.7,
      "evidence": {
        "files": [
          "<path:line-range>",
          "<path#symbol>"
        ],
        "observations": [
          "<stack trace excerpt summary>",
          "<why this supports H1>"
        ]
      },
      "falsification": [
        "<quick experiment to disprove H1>"
      ]
    }
  ],
  "suspectAreas": [
    {
      "file": "<path>",
      "symbols": ["<symbol()>", "<Class.method>"],
      "why": "<why this is relevant>"
    }
  ],
  "acceptanceCriteriaSeeds": [
    {
      "id": "AC1",
      "statement": "<what must be true after the fix>",
      "suggestedTests": ["<test name or command>"]
    }
  ],
  "validationPlanSeed": {
    "fastSubset": ["<fast command(s)>"],
    "fullSuite": ["<full suite command(s)>"],
    "notes": "<what to watch for>"
  },
  "risks": [
    { "risk": "<risk>", "mitigation": "<mitigation>" }
  ],
  "blockers": [
    {
      "category": "setup_failure",
      "evidence": "<1–2 lines of evidence>",
      "nextStep": "<smallest unblocking step>"
    }
  ]
}
```


