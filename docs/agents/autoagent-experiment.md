---
name: team-lead-optimization
description: >
  Conservative first-pass AutoAgent experiment for this repository. It benchmarks the
  `team-lead` agent profile, tests a small mutation catalog, and keeps only variants
  that improve score or preserve score with lower complexity while staging
  review-oriented run metadata.
optimizationTargets:
  - id: team-lead
    path: ../../.github/agents/team-lead.agent.md
    kind: agent_profile
    primary: true
    mutableRegions:
      - body
benchmarkPath: ../../.github/skills/autoagent-loop/examples/team-lead-benchmark.json
mutationCatalogPath: ../../.github/skills/autoagent-loop/examples/team-lead-mutations.json
maxIterations: 4
applyBestCandidate: false
stageForReview: true
evaluationMode:
  deterministic: true
  live: false
  liveEvaluator:
    enabled: false
    strategy: advisory
    provider: github-models
    model: gpt-5.4
    promptArtifactPath: null
    rubricPaths: []
    maxSamples: 0
    recordRawOutputs: false
    requireDeterministicPass: true
    temperature: 0.0
continuousPolicy:
  mode: manual
  triggerOn:
    - review_failure
  minSignalCount: 2
  maxQueuedRuns: 1
  maxRunsPerSweep: 1
  learningWindowDays: 30
  stageOnly: true
  requireReviewPass: true
candidatePolicy:
  keepStrategy: score-then-simpler
  searchStrategy: current_best
  frontierSize: 1
stagedPatchPolicy:
  enabled: true
  mode: review_bundle
  applyOnPass: false
  includeTargetSnapshots: true
  includeDiffSummary: true
  reviewerHints: []
  manifestFormat: candidate_snapshot
evidencePolicy:
  includeCurrentArtifacts: true
  includeHookAudit: true
  includeChatHistory: true
  chatHistoryPaths:
    - ../../tests/fixtures/autoagent-loop/team-lead-chat-history.json
  includeTranscriptHistory: true
  transcriptHistoryPaths:
    - ../../tests/fixtures/autoagent-loop/team-lead-transcript-history.jsonl
  includeHandoffHistory: true
  handoffHistoryPaths:
    - ../../tests/fixtures/autoagent-loop/team-lead-handoff-history.jsonl
  includeVsCodeLogs: false
  vsCodeLogPaths: []
  externalLogSources: []
  maxRuns: 5
  maxRecordsPerFile: 200
  maxExternalLogLineLength: 400
  redactSensitive: true
  allowExternalPaths: false
---

# AutoAgent Experiment

Optimize the Team Lead agent for clarity and brevity while preserving these requirements:

- retain the sole-coordinator rule
- retain the `docs/agents/` and `docs/agents/current-run.json` determinism contract
- retain the manager boundary against product-code edits
- retain the canonical delegation flow through `quality-gate`
- retain the `ManagerDecision` output contract
- preserve the reviewed tool surface in frontmatter

Keep any candidate that improves benchmark score. If two candidates tie on score, keep the simpler one.

This checked-in Team Lead experiment intentionally starts with a single target agent file instead of
a larger orchestration bundle. The agent profile carries the highest-signal manager contract, and
keeping the first pass single-target limits risk while the benchmark and mutation catalog mature.
If maintainers later want broader optimization, they can extend `optimizationTargets` to include
`.github/skills/team-lead/SKILL.md` or other shared guidance artifacts.

It also opts into the governed evidence collector so the loop can summarize current artifacts, recent
run snapshots, and hook-audit records into a redacted evidence dataset without reading arbitrary
external files by default.

This checked-in experiment now also uses repo-local fixture-backed chat, transcript, and handoff
exports so canonical artifacts keep explicit reasoning-trace uptake visible without depending on a
maintainer's private editor history.

The candidate-search policy is now explicit in the sample schema. This checked-in experiment keeps
the default `current_best` search path with a frontier size of `1`, which preserves the historical
linear mutation loop. Maintainers can opt into bounded frontier search in reviewed runs by raising
`candidatePolicy.frontierSize` above `1`, which enables branching from multiple kept candidates and
records parent or depth metadata in the run artifacts.

Each generated AutoAgent run now also emits a dedicated `search-ledger.json` artifact under the run
root. That ledger captures candidate nodes, frontier snapshots, and the final best-candidate lineage
so replay-oriented slices do not have to reconstruct search history from the TSV or embedded report
JSON alone.

Runs now also emit a dedicated `search-checkpoint.json` artifact under the same generated run root.
That checkpoint captures the post-mutation search state needed for guarded resume support: candidate
records, the current frontier, the deterministic best candidate, and the next mutation index. The
checkpoint keeps full inline documents only for the active frontier and deterministic best
candidate; older candidates restore from the generated candidate snapshots already written under the
run root. Checkpoint creation intentionally stops before any optional live-evaluator advisory or
tie-breaker pass, so resume always re-enters from deterministic mutation-search state rather than
from a post-live winner selection. A maintainer can resume from that checkpoint with `--resume`,
but the checked-in canonical experiment still defaults to a fresh run and does not enable any
background or autonomous continuation.

Each run also emits `search-checkpoint-manifest.json`, a smaller companion artifact that lists the
snapshot-backed candidate files required for resume. The manifest is additive: it helps maintainers
and external tooling validate the restore set without opening the full checkpoint, but
`search-checkpoint.json` remains the source of truth for resumable search state, and both artifacts
continue to describe the same pre-live `post_mutation_search` boundary.

The current Phase 3 visibility contract still stops at review-gated reporting instead of enabling
unattended automation. `stagedPatchPolicy` controls the review artifact shape, and
`continuousPolicy` now reports whether a reviewed continuation would be eligible in the future while
remaining manual by default in this checked-in experiment. A separate readiness signal now layers
on top of that eligibility and cross-checks the local governed review state in `docs/agents/state.json`
against the machine-readable `ReviewReport` JSON block in `docs/agents/review-report.md`. Matching
PASS governed artifacts can make an eligible continuation look ready, while mismatch, missing JSON,
or unreadable governed inputs block readiness deterministically. This remains visibility-only and
does not queue or run anything. Any non-manual continuation mode must still stay stage-only and
require review pass under the repo's deterministic-first guardrails. This sample keeps live
evaluation disabled and continuation manual by default, so canonical artifacts show blocked
manual-mode eligibility, blocked readiness, explicit governed-review consensus, and the current
governed artifact statuses rather than any scheduler, queue, or background follow-on run.

The canonical AutoAgent report also keeps its top-level `status` as an artifact-readiness signal for
the generated report itself. Governed task lifecycle is a separate local visibility signal sourced
from `docs/agents/state.json`, so maintainers can see whether the current bounded slice is still in
progress, review-ready, or already closed without mistaking `AutoAgentReport.status` for the slice
lifecycle.

Phase 3 visibility scope is complete once canonical artifacts expose continuation eligibility,
continuation readiness, governed review consensus, governed task lifecycle, and a reviewed manual
handoff summary under the same manual and `report_only` semantics. That completion point still does
not authorize unattended orchestration. Any scheduler, queue, background follow-on run, or
autonomous continuation remains out of scope for Phase 3 and belongs to a later planning track.

The current bounded Phase 4 implementation step still stops short of execution. It can add an
additive governed approval metadata layer derived from the existing reviewed dispatch intent,
governed review consensus, and governed lifecycle signals, but it must remain manual,
review-gated, and `report_only`. A governed approval metadata state that is blocked,
not-requested, or ready for manual recording only describes what governed approval evidence is
currently visible; it does not authorize approval APIs, schedulers, queues, unattended
continuation, or automatic apply behavior.

If maintainers want to learn from editor-side debug traces, they must opt in explicitly through
`includeVsCodeLogs`, `vsCodeLogPaths`, or `externalLogSources`. External logs are still subject to
the same secret and path redaction rules as governed run artifacts.
