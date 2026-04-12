# Performance Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE / BLOCKED
- **Goal:** <!-- one sentence -->
- **Produced at:** <!-- ISO date/time -->
- **Author:** performance-engineer

## Workloads Measured
> Include baseline and after measurements for each workload.

### Workload 1 — <!-- name -->
- **Kind:** micro / component / integration
- **Command:** `<!-- -->`
- **Dataset/fixture:** <!-- -->
- **Environment:**
  - OS: <!-- -->
  - CPU: <!-- -->
  - Memory: <!-- -->
  - Runtime: <!-- python/node/java etc -->
  - Notes: <!-- -->

#### Baseline
- Metrics:
  - time_ms: <!-- -->
  - throughput: <!-- -->
  - allocations: <!-- -->
- Variance notes: <!-- warmup, outliers, stdev -->

#### After change
- Metrics:
  - time_ms: <!-- -->
  - throughput: <!-- -->
  - allocations: <!-- -->
- Variance notes: <!-- -->

#### Delta
- time_percent: <!-- -->
- throughput_percent: <!-- -->
- allocations_percent: <!-- -->
- Interpretation: improved / regressed / no_material_change / inconclusive

## Regressions
- **P1:** <!-- summary -->
  - Magnitude: small / medium / large
  - Evidence: <!-- -->
  - Suspected cause: <!-- -->
  - Recommended fix: <!-- -->

## Profiling
- Tool: <!-- -->
- Command: `<!-- -->`
- Top findings:
  - <!-- -->
- Notes:
  - <!-- -->

## Benchmarks Added/Updated
- `<!-- path -->`
  - How to run: `<!-- -->`
  - What it covers: <!-- -->

## CI Notes
- <!-- CI variance caveat; do not hard-gate small deltas unless policy exists -->

## Known Issues / Blockers
- <!-- setup failure, benchmark instability, tooling gap, etc. -->

## Notes to Team Lead
- <!-- -->

---

## Machine-readable PerformanceReport (required)
```json
{
  "type": "PerformanceReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "",
  "workloads": [
    {
      "name": "",
      "kind": "micro",
      "command": "",
      "datasetOrFixture": "",
      "environment": {
        "os": "",
        "cpu": "",
        "memory": "",
        "runtime": "",
        "notes": ""
      },
      "baseline": {
        "metrics": { "time_ms": 0, "throughput": 0, "allocations": 0 },
        "varianceNotes": ""
      },
      "after": {
        "metrics": { "time_ms": 0, "throughput": 0, "allocations": 0 },
        "varianceNotes": ""
      },
      "delta": {
        "time_percent": 0,
        "throughput_percent": 0,
        "allocations_percent": 0,
        "interpretation": "no_material_change"
      }
    }
  ],
  "regressions": [],
  "profiling": [],
  "benchmarksAddedOrUpdated": [
    { "path": "", "howToRun": "", "whatItCovers": "" }
  ],
  "ciNotes": [
    "CI runners are noisy; avoid hard-gating small deltas unless repo policy supports it."
  ],
  "knownIssues": [],
  "notesToTeamLead": [""]
}
```

