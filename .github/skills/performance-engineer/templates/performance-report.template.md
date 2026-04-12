# Performance Report

> Keep the human summary short (≤ 12 lines). Then include exactly one JSON object in a fenced code block.

## Human summary (≤ 12 lines)
- Goal:
- Workloads measured:
- Headline result:
- Any regressions:
- Any benchmarks added/updated:
- Notes on variance / CI runner noise:
- Recommendation:

```json
{
  "type": "PerformanceReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "What performance goal(s) or regression check was requested by the Task Spec?",
  "workloads": [
    {
      "name": "workload-name",
      "kind": "micro",
      "command": "exact command used (include args/flags)",
      "datasetOrFixture": "fixture path / dataset description (or 'none')",
      "environment": {
        "os": "e.g. ubuntu-22.04",
        "cpu": "e.g. 2 vCPU Intel/AMD (or local machine model)",
        "memory": "e.g. 7GB",
        "runtime": "e.g. node 20.11 / python 3.11 / go 1.22 / java 21",
        "notes": "warmups, iteration count, pinned deps, turbo disabled, etc."
      },
      "baseline": {
        "metrics": {
          "time_ms": 0,
          "throughput": 0,
          "allocations": 0
        },
        "varianceNotes": "min/mean/stdev or p50/p95; runner variance notes; cache/JIT warmup notes"
      },
      "after": {
        "metrics": {
          "time_ms": 0,
          "throughput": 0,
          "allocations": 0
        },
        "varianceNotes": "same methodology as baseline; note anything different"
      },
      "delta": {
        "time_percent": 0,
        "throughput_percent": 0,
        "allocations_percent": 0,
        "interpretation": "no_material_change"
      }
    }
  ],
  "regressions": [
    {
      "id": "P1",
      "summary": "What regressed and for which workload/metric?",
      "magnitude": "small",
      "evidence": "Paste the key numbers (before/after) and the command that produced them.",
      "suspectedCause": "Tie the cause to the patch (file/function/behavior). If unknown, say so.",
      "recommendedFix": "Smallest scoped fix; or 'out-of-scope' + recommended next PR plan."
    }
  ],
  "profiling": [
    {
      "tool": "e.g. pprof / perf / py-spy / node --prof / jfr / heap profiler",
      "command": "exact command used",
      "topFindings": [
        "finding 1",
        "finding 2"
      ],
      "notes": "how to reproduce / where artifacts were saved (if any)"
    }
  ],
  "benchmarksAddedOrUpdated": [
    {
      "path": "path/to/benchmark/file/or/suite",
      "howToRun": "exact command",
      "whatItCovers": "what user-facing operation or hotspot this benchmark represents"
    }
  ],
  "ciNotes": [
    "If run on GitHub-hosted runners: note expected variance; avoid hard-gating small deltas unless repo policy says otherwise."
  ],
  "knownIssues": [
    {
      "category": "benchmark_instability",
      "evidence": "What showed instability (numbers, logs)?",
      "nextStep": "How to stabilize (pin CPU governor, increase iterations, isolate IO, use fixtures, etc.)"
    }
  ],
  "notesToTeamLead": [
    "Anything the Team Lead should decide (e.g., accept small regression due to correctness/security fix; plan follow-up PR)."
  ]
}
```

