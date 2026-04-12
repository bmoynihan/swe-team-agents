# AutoAgent Report

- Status: READY_FOR_QUALITY_GATE
- Report status meaning: artifact_readiness
- Experiment: team-lead-optimization
- Primary target: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/team-lead.agent.md
- Target bundle size: 1
- Evidence records: 26
- Evidence runs: 3
- External log records: 5
- Transcript evidence records: 4
- Handoff evidence records: 1
- Baseline score: 1.0
- Best score: 1.0
- Best candidate: baseline
- Best trajectory score: 0.88
- Best trajectory evidence matches: 6
- Candidate search: current_best (frontier size 1)
- Candidate ranking signals: benchmark_score, complexity, trajectory_score
- Winner decisive signal: benchmark_score
- Winner rationale: baseline beat relax-no-product-code-boundary on benchmark score (1.0 vs 0.842105).
- Winner trajectory contributors: Top trajectory contributors: attributedSuccessCount +3, matchedEvidenceRecords +3, attributedErrorCount lower by 2
- Winner evidence rationale: none
- Resume: fresh run
- Resume checkpoint stage: post_mutation_search
- Search ledger nodes: 2
- Checkpoint: 1/1 mutations complete
- Checkpoint storage: 1 inline, 1 snapshot-backed
- Checkpoint manifest: 1 snapshot-backed candidates, 1 files
- Trace events: 6
- Trace trajectories: 2
- Trace candidate episodes: 2
- Trace evidence-backed episodes: 2
- Learning mode: shadow_only
- Learning reasoning-path signal: reasoningPathEfficiencyScore
- Learning source-backed paths: 2
- Learning transcript-backed paths: 2
- Learning handoff-backed paths: 1
- Learning best reasoning-path efficiency: 0.808333
- Learning top observed paths: 2
- Learning benchmark candidates: 2
- Learning mutation seeds: 2
- Learning policy candidates: 2
- Learning benchmark draft fragments: 2
- Learning mutation draft entries: 2
- Learning policy draft entries: 2
- Trace best trajectory score: 0.88
- Trace best trajectory evidence matches: 6
- Trace artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/autoagent-trace.json
- Learning benchmark drafts artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-benchmark-fragments.json
- Learning mutation drafts artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-mutation-catalog.json
- Learning policy drafts artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-policy-catalog.json
- Guarded learning promotion: blocked
- Guarded learning blocked reasons: manual_mode
- Guarded learning benchmark accepts: 0
- Guarded learning policy accepts: 0
- Guarded learning review artifact: none
- Guarded learning summary: Guarded learning promotion is blocked until continuation and approval gates are ready.
- Guarded learning recommended action: Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.
- Learning promotion audit: artifact_missing
- Learning promotion audit artifact: none
- Learning promotion audit source mode: none
- Learning promotion audit reviewer overrides: 0
- Learning promotion audit benchmark decisions: reviewed 0, accepted 0, rejected 0, deferred 0
- Learning promotion audit mutation decisions: reviewed 0, accepted 0, rejected 0, deferred 0
- Learning promotion audit policy decisions: reviewed 0, accepted 0, rejected 0, deferred 0
- Learning promotion audit blocked factors: none
- Learning promotion audit benchmark blocked factors: none
- Learning promotion audit mutation blocked factors: none
- Learning promotion audit policy blocked factors: none
- Reviewed policy runtime: disabled (0 policies)
- Reviewed policy artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-policies.json
- Continuous mode: manual
- Continuation eligibility: blocked
- Continuation blocked reasons: manual_mode
- Continuation execution: report_only
- Governed task lifecycle: Review
- Governed task id: manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412
- Governed task title: Implement transcript-backed reasoning-path efficiency learning for AutoAgent
- Governed lifecycle quality gate: PASS
- Governed next action: team-lead - Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.
- Governed lifecycle missing fields: none
- Continuation readiness: blocked
- Continuation readiness blocked reasons: manual_mode
- Governed review consensus: consistent
- Governed review consensus blocked reasons: none
- Governed review status: PASS
- Review report status: PASS
- Reviewed continuation handoff: blocked
- Reviewed handoff blocked reasons: manual_mode
- Reviewed handoff mode: reviewed_manual
- Reviewed handoff summary: Not ready for reviewed manual handoff.
- Reviewed handoff recommended action: Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.
- Orchestration contract: blocked
- Orchestration contract blocked reasons: manual_mode
- Orchestration contract mode: staged_dispatch_simulation
- Orchestration contract scope: bounded_follow_on_slice
- Orchestration contract id: manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412::staged_dispatch_simulation
- Orchestration contract summary: Staged dispatch simulation is blocked.
- Orchestration contract recommended action: Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.
- Reviewed dispatch intent: blocked
- Reviewed dispatch blocked reasons: manual_mode
- Reviewed dispatch approval status: blocked
- Reviewed dispatch approval source: governed_artifacts_only
- Reviewed dispatch summary: Reviewed dispatch intent is blocked.
- Reviewed dispatch recommended action: Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.
- Governed approval metadata: blocked
- Governed approval blocked reasons: manual_mode
- Governed approval review pass recorded: True
- Governed approval quality gate: PASS
- Governed approval source: governed_artifacts_only
- Governed approval summary: Governed approval metadata is blocked.
- Governed approval recommended action: Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.
- Phase 4 bounded step: governed_approval_metadata
- Phase 4 execution authority: out_of_scope
- Phase 3 visibility scope: complete
- Phase 3 exit criteria: continuation eligibility, continuation readiness, governed review consensus, governed task lifecycle, and reviewed handoff visibility are all present under manual/report_only semantics
- Phase 3 unattended orchestration: out_of_scope
- Live evaluator: disabled
- Live evaluation status: disabled
- Staged patch: review_bundle (0 targets)
- Applied best variant: False

```json
{
  "type": "AutoAgentReport",
  "status": "READY_FOR_QUALITY_GATE",
  "reportStatusMeaning": "artifact_readiness",
  "experiment": {
    "name": "team-lead-optimization",
    "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-experiment.md",
    "description": "Conservative first-pass AutoAgent experiment for this repository. It benchmarks the `team-lead` agent profile, tests a small mutation catalog, and keeps only variants that improve score or preserve score with lower complexity while staging review-oriented run metadata.\n",
    "directive": "# AutoAgent Experiment\n\nOptimize the Team Lead agent for clarity and brevity while preserving these requirements:\n\n- retain the sole-coordinator rule\n- retain the `docs/agents/` and `docs/agents/current-run.json` determinism contract\n- retain the manager boundary against product-code edits\n- retain the canonical delegation flow through `quality-gate`\n- retain the `ManagerDecision` output contract\n- preserve the reviewed tool surface in frontmatter\n\nKeep any candidate that improves benchmark score. If two candidates tie on score, keep the simpler one.\n\nThis checked-in Team Lead experiment intentionally starts with a single target agent file instead of\na larger orchestration bundle. The agent profile carries the highest-signal manager contract, and\nkeeping the first pass single-target limits risk while the benchmark and mutation catalog mature.\nIf maintainers later want broader optimization, they can extend `optimizationTargets` to include\n`.github/skills/team-lead/SKILL.md` or other shared guidance artifacts.\n\nIt also opts into the governed evidence collector so the loop can summarize current artifacts, recent\nrun snapshots, and hook-audit records into a redacted evidence dataset without reading arbitrary\nexternal files by default.\n\nThis checked-in experiment now also uses repo-local fixture-backed chat, transcript, and handoff\nexports so canonical artifacts keep explicit reasoning-trace uptake visible without depending on a\nmaintainer's private editor history.\n\nThe candidate-search policy is now explicit in the sample schema. This checked-in experiment keeps\nthe default `current_best` search path with a frontier size of `1`, which preserves the historical\nlinear mutation loop. Maintainers can opt into bounded frontier search in reviewed runs by raising\n`candidatePolicy.frontierSize` above `1`, which enables branching from multiple kept candidates and\nrecords parent or depth metadata in the run artifacts.\n\nEach generated AutoAgent run now also emits a dedicated `search-ledger.json` artifact under the run\nroot. That ledger captures candidate nodes, frontier snapshots, and the final best-candidate lineage\nso replay-oriented slices do not have to reconstruct search history from the TSV or embedded report\nJSON alone.\n\nRuns now also emit a dedicated `search-checkpoint.json` artifact under the same generated run root.\nThat checkpoint captures the post-mutation search state needed for guarded resume support: candidate\nrecords, the current frontier, the deterministic best candidate, and the next mutation index. The\ncheckpoint keeps full inline documents only for the active frontier and deterministic best\ncandidate; older candidates restore from the generated candidate snapshots already written under the\nrun root. Checkpoint creation intentionally stops before any optional live-evaluator advisory or\ntie-breaker pass, so resume always re-enters from deterministic mutation-search state rather than\nfrom a post-live winner selection. A maintainer can resume from that checkpoint with `--resume`,\nbut the checked-in canonical experiment still defaults to a fresh run and does not enable any\nbackground or autonomous continuation.\n\nEach run also emits `search-checkpoint-manifest.json`, a smaller companion artifact that lists the\nsnapshot-backed candidate files required for resume. The manifest is additive: it helps maintainers\nand external tooling validate the restore set without opening the full checkpoint, but\n`search-checkpoint.json` remains the source of truth for resumable search state, and both artifacts\ncontinue to describe the same pre-live `post_mutation_search` boundary.\n\nThe current Phase 3 visibility contract still stops at review-gated reporting instead of enabling\nunattended automation. `stagedPatchPolicy` controls the review artifact shape, and\n`continuousPolicy` now reports whether a reviewed continuation would be eligible in the future while\nremaining manual by default in this checked-in experiment. A separate readiness signal now layers\non top of that eligibility and cross-checks the local governed review state in `docs/agents/state.json`\nagainst the machine-readable `ReviewReport` JSON block in `docs/agents/review-report.md`. Matching\nPASS governed artifacts can make an eligible continuation look ready, while mismatch, missing JSON,\nor unreadable governed inputs block readiness deterministically. This remains visibility-only and\ndoes not queue or run anything. Any non-manual continuation mode must still stay stage-only and\nrequire review pass under the repo's deterministic-first guardrails. This sample keeps live\nevaluation disabled and continuation manual by default, so canonical artifacts show blocked\nmanual-mode eligibility, blocked readiness, explicit governed-review consensus, and the current\ngoverned artifact statuses rather than any scheduler, queue, or background follow-on run.\n\nThe canonical AutoAgent report also keeps its top-level `status` as an artifact-readiness signal for\nthe generated report itself. Governed task lifecycle is a separate local visibility signal sourced\nfrom `docs/agents/state.json`, so maintainers can see whether the current bounded slice is still in\nprogress, review-ready, or already closed without mistaking `AutoAgentReport.status` for the slice\nlifecycle.\n\nPhase 3 visibility scope is complete once canonical artifacts expose continuation eligibility,\ncontinuation readiness, governed review consensus, governed task lifecycle, and a reviewed manual\nhandoff summary under the same manual and `report_only` semantics. That completion point still does\nnot authorize unattended orchestration. Any scheduler, queue, background follow-on run, or\nautonomous continuation remains out of scope for Phase 3 and belongs to a later planning track.\n\nThe current bounded Phase 4 implementation step still stops short of execution. It can add an\nadditive governed approval metadata layer derived from the existing reviewed dispatch intent,\ngoverned review consensus, and governed lifecycle signals, but it must remain manual,\nreview-gated, and `report_only`. A governed approval metadata state that is blocked,\nnot-requested, or ready for manual recording only describes what governed approval evidence is\ncurrently visible; it does not authorize approval APIs, schedulers, queues, unattended\ncontinuation, or automatic apply behavior.\n\nIf maintainers want to learn from editor-side debug traces, they must opt in explicitly through\n`includeVsCodeLogs`, `vsCodeLogPaths`, or `externalLogSources`. External logs are still subject to\nthe same secret and path redaction rules as governed run artifacts.",
    "candidatePolicy": {
      "keepStrategy": "score-then-simpler",
      "searchStrategy": "current_best",
      "frontierSize": 1
    },
    "evaluationMode": {
      "deterministic": true,
      "live": false,
      "liveEvaluator": {
        "enabled": false,
        "strategy": "advisory",
        "provider": "github-models",
        "model": "gpt-5.4",
        "promptArtifactPath": null,
        "rubricPaths": [],
        "maxSamples": 0,
        "recordRawOutputs": false,
        "requireDeterministicPass": true,
        "temperature": 0.0
      }
    },
    "continuousPolicy": {
      "enabled": false,
      "mode": "manual",
      "scheduleCron": null,
      "triggerOn": [
        "review_failure"
      ],
      "minSignalCount": 2,
      "maxQueuedRuns": 1,
      "maxRunsPerSweep": 1,
      "learningWindowDays": 30,
      "stageOnly": true,
      "requireReviewPass": true
    },
    "continuationEligibility": {
      "eligible": false,
      "status": "blocked",
      "blockedReasons": [
        "manual_mode"
      ],
      "executionMode": "report_only",
      "reviewGated": true
    },
    "governedTaskLifecycle": {
      "status": "available",
      "readable": true,
      "sourcePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
      "taskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
      "taskTitle": "Implement transcript-backed reasoning-path efficiency learning for AutoAgent",
      "phase": "Review",
      "qualityGateStatus": "PASS",
      "nextActionSummary": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
      "nextActionOwner": "team-lead",
      "missingFields": []
    },
    "governedReviewConsensus": {
      "agrees": true,
      "status": "consistent",
      "blockedReasons": [],
      "stateStatus": "PASS",
      "stateReadable": true,
      "stateSourcePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
      "reviewReportStatus": "PASS",
      "reviewReportReadable": true,
      "reviewReportSourcePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md"
    },
    "continuationReadiness": {
      "ready": false,
      "status": "blocked",
      "blockedReasons": [
        "manual_mode"
      ],
      "executionMode": "report_only",
      "reviewGated": true,
      "policyEligible": false,
      "governedReviewStatus": "PASS",
      "governedReviewReadable": true,
      "governedReviewSourcePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json"
    },
    "reviewedContinuationHandoff": {
      "ready": false,
      "status": "blocked",
      "blockedReasons": [
        "manual_mode"
      ],
      "handoffMode": "reviewed_manual",
      "manualOnly": true,
      "executionMode": "report_only",
      "reviewGated": true,
      "policyEligible": false,
      "continuationReadinessStatus": "blocked",
      "governedReviewConsensusStatus": "consistent",
      "governedTaskLifecycleStatus": "available",
      "governedTaskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
      "governedTaskPhase": "Review",
      "summary": "Not ready for reviewed manual handoff.",
      "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
      "artifactRefs": {
        "state": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
        "reviewReport": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md",
        "report": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md"
      }
    },
    "orchestrationContract": {
      "ready": false,
      "status": "blocked",
      "blockedReasons": [
        "manual_mode"
      ],
      "contractMode": "staged_dispatch_simulation",
      "dispatchScope": "bounded_follow_on_slice",
      "manualOnly": true,
      "executionMode": "report_only",
      "reviewGated": true,
      "policyEligible": false,
      "reviewedHandoffStatus": "blocked",
      "governedTaskLifecycleStatus": "available",
      "governedTaskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
      "governedTaskPhase": "Review",
      "contractId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412::staged_dispatch_simulation",
      "summary": "Staged dispatch simulation is blocked.",
      "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
      "artifactRefs": {
        "state": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
        "reviewReport": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md",
        "report": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md",
        "adr": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/adr/0001-phase4-bounded-orchestration-rollout.md"
      }
    },
    "reviewedDispatchIntent": {
      "ready": false,
      "status": "blocked",
      "blockedReasons": [
        "manual_mode"
      ],
      "intentMode": "reviewed_dispatch_intent",
      "dispatchScope": "bounded_follow_on_slice",
      "manualOnly": true,
      "executionMode": "report_only",
      "reviewGated": true,
      "policyEligible": false,
      "requiresExplicitApproval": true,
      "approvalStatus": "blocked",
      "approvalMetadataPresent": false,
      "approvalSource": "governed_artifacts_only",
      "orchestrationContractStatus": "blocked",
      "reviewedHandoffStatus": "blocked",
      "governedReviewConsensusStatus": "consistent",
      "governedTaskLifecycleStatus": "available",
      "governedTaskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
      "governedTaskPhase": "Review",
      "intentId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412::staged_dispatch_simulation::reviewed_dispatch_intent",
      "summary": "Reviewed dispatch intent is blocked.",
      "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
      "artifactRefs": {
        "state": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
        "reviewReport": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md",
        "report": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md",
        "adr": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/adr/0001-phase4-bounded-orchestration-rollout.md"
      }
    },
    "governedApprovalMetadata": {
      "ready": false,
      "status": "blocked",
      "blockedReasons": [
        "manual_mode"
      ],
      "approvalMode": "governed_approval_metadata",
      "manualOnly": true,
      "executionMode": "report_only",
      "reviewGated": true,
      "policyEligible": false,
      "requiresExplicitApproval": true,
      "approvalMetadataPresent": false,
      "approvalSource": "governed_artifacts_only",
      "readyForRecording": false,
      "reviewPassRecorded": true,
      "reviewPassReadable": true,
      "qualityGateStatus": "PASS",
      "reviewedDispatchIntentStatus": "blocked",
      "governedReviewConsensusStatus": "consistent",
      "governedTaskLifecycleStatus": "available",
      "governedTaskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
      "governedTaskPhase": "Review",
      "metadataId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412::staged_dispatch_simulation::reviewed_dispatch_intent::governed_approval_metadata",
      "summary": "Governed approval metadata is blocked.",
      "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
      "artifactRefs": {
        "state": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
        "reviewReport": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md",
        "report": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md",
        "adr": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/adr/0001-phase4-bounded-orchestration-rollout.md"
      }
    },
    "stagedPatchPolicy": {
      "enabled": true,
      "mode": "review_bundle",
      "applyOnPass": false,
      "includeTargetSnapshots": true,
      "includeDiffSummary": true,
      "reviewerHints": [],
      "manifestFormat": "candidate_snapshot"
    },
    "evidencePolicy": {
      "enabled": true,
      "runsDir": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs",
      "currentFiles": [
        "state.json",
        "patch-report.md",
        "test-report.md",
        "review-report.md"
      ],
      "reportFiles": [
        "state.json",
        "patch-report.md",
        "test-report.md",
        "review-report.md",
        "autoagent-report.md"
      ],
      "includeCurrentArtifacts": true,
      "includeHookAudit": true,
      "includeChatHistory": true,
      "chatHistoryPaths": [
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-chat-history.json"
      ],
      "includeTranscriptHistory": true,
      "transcriptHistoryPaths": [
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-transcript-history.jsonl"
      ],
      "includeHandoffHistory": true,
      "handoffHistoryPaths": [
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-handoff-history.jsonl"
      ],
      "includeVsCodeLogs": false,
      "vsCodeLogPaths": [],
      "externalLogSources": [
        {
          "id": "chat-history-1",
          "kind": "chat_transcript",
          "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-chat-history.json",
          "format": "json",
          "optional": true,
          "includeLinePatterns": [],
          "excludeLinePatterns": [],
          "maxRecords": 200,
          "maxLineLength": 400
        },
        {
          "id": "transcript-history-1",
          "kind": "conversation_transcript",
          "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-transcript-history.jsonl",
          "format": "jsonl",
          "optional": true,
          "includeLinePatterns": [],
          "excludeLinePatterns": [],
          "maxRecords": 200,
          "maxLineLength": 400
        },
        {
          "id": "handoff-history-1",
          "kind": "handoff_history",
          "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-handoff-history.jsonl",
          "format": "jsonl",
          "optional": true,
          "includeLinePatterns": [],
          "excludeLinePatterns": [],
          "maxRecords": 200,
          "maxLineLength": 400
        }
      ],
      "maxRuns": 5,
      "maxRecordsPerFile": 200,
      "maxExternalLogLineLength": 400,
      "redactSensitive": true,
      "allowExternalPaths": false
    },
    "reviewedPolicyRuntime": {
      "enabled": false,
      "artifactPath": null,
      "preferredSequenceBonus": 0.04,
      "escalationPenalty": 0.05
    },
    "reviewedPolicyRuntimeState": {
      "enabled": false,
      "status": "disabled",
      "artifactPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-policies.json",
      "artifactFound": false,
      "policyCount": 0,
      "activePolicyCount": 0,
      "approvedLearningDraftCount": 0
    },
    "stageForReview": true
  },
  "targetBundle": [
    {
      "id": "team-lead",
      "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/team-lead.agent.md",
      "kind": "agent_profile",
      "primary": true,
      "mutableRegions": [
        "body"
      ],
      "weight": 1.0
    }
  ],
  "primaryTargetId": "team-lead",
  "targetAgent": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/team-lead.agent.md",
  "resume": {
    "requested": false,
    "resumed": false,
    "checkpointStage": "post_mutation_search",
    "startingMutationIndex": 1,
    "completedMutationCount": 1,
    "requestedMutationCount": 1,
    "totalMutationCount": 1,
    "nextMutationIndex": 2,
    "hasRemainingMutations": false,
    "inlineCandidateCount": 1,
    "snapshotBackedCandidateCount": 1,
    "checkpointPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint.json",
    "checkpointManifestPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint-manifest.json",
    "manifestSnapshotCandidateCount": 1,
    "manifestRequiredFileCount": 1
  },
  "candidateSearch": {
    "strategy": "current_best",
    "frontierSize": 1,
    "keepStrategy": "score-then-simpler",
    "rankingSignals": [
      "benchmark_score",
      "complexity",
      "trajectory_score"
    ],
    "mutationExecutionPlan": [
      {
        "plannedIndex": 1,
        "catalogIndex": 1,
        "planToken": "1:relax-no-product-code-boundary",
        "mutationId": "relax-no-product-code-boundary",
        "description": "Loosen the manager scope to prove governance regressions are discarded.",
        "priorityStatus": "neutral",
        "priorityScore": 0.0,
        "bonus": 0.0,
        "penalty": 0.0,
        "matchedPolicyCount": 0,
        "matchedPolicyIds": [],
        "sourceCandidateIds": []
      }
    ],
    "maxSearchDepth": 1,
    "ledgerNodeCount": 2,
    "searchLedgerPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-ledger.json",
    "bestCandidateLineage": [
      "baseline"
    ],
    "finalFrontierCandidateIds": [
      "baseline"
    ],
    "winnerExplanation": {
      "winnerCandidateId": "baseline",
      "comparedCandidateId": "relax-no-product-code-boundary",
      "comparisonMode": "deterministic_ranking",
      "decisiveSignal": "benchmark_score",
      "evidenceBacked": false,
      "summary": "baseline beat relax-no-product-code-boundary on benchmark score (1.0 vs 0.842105).",
      "evidenceSummary": null,
      "rankingComparison": {
        "winnerScore": 1.0,
        "runnerUpScore": 0.842105,
        "scoreDelta": 0.157895,
        "winnerComplexityScore": 3113,
        "runnerUpComplexityScore": 3105,
        "complexityAdvantage": -8,
        "winnerTrajectoryScore": 0.88,
        "runnerUpTrajectoryScore": 0.60125,
        "trajectoryScoreDelta": 0.27875
      },
      "topTrajectorySignals": [
        {
          "signal": "attributedSuccessCount",
          "preference": "higher_is_better",
          "winner": 3,
          "runnerUp": 0,
          "advantage": 3.0
        },
        {
          "signal": "matchedEvidenceRecords",
          "preference": "higher_is_better",
          "winner": 6,
          "runnerUp": 3,
          "advantage": 3.0
        },
        {
          "signal": "attributedErrorCount",
          "preference": "lower_is_better",
          "winner": 0,
          "runnerUp": 2,
          "advantage": 2.0
        },
        {
          "signal": "attributedToolErrorCount",
          "preference": "lower_is_better",
          "winner": 0,
          "runnerUp": 2,
          "advantage": 2.0
        },
        {
          "signal": "actionEfficiency",
          "preference": "higher_is_better",
          "winner": 1.0,
          "runnerUp": 0.5,
          "advantage": 0.5
        }
      ],
      "trajectorySummary": "Top trajectory contributors: attributedSuccessCount +3, matchedEvidenceRecords +3, attributedErrorCount lower by 2",
      "evidenceComparison": {
        "winnerSourceKinds": {
          "handoff_event": 1,
          "run_report": 1,
          "run_state": 2,
          "transcript_event": 2
        },
        "runnerUpSourceKinds": {
          "run_report": 1,
          "transcript_event": 2
        },
        "winnerStatuses": {
          "ready_for_quality_gate": 1,
          "review": 1,
          "spec": 1,
          "success": 3
        },
        "runnerUpStatuses": {
          "error": 2,
          "ready_for_quality_gate": 1
        }
      },
      "winner": {
        "candidateId": "baseline",
        "iteration": 0,
        "searchDepth": 0,
        "score": 1.0,
        "complexityScore": 3113,
        "trajectoryScore": 0.88,
        "trajectorySignals": {
          "validationBreadth": 1.0,
          "parentProgress": 0.0,
          "actionEfficiency": 1.0,
          "targetFocus": 1.0,
          "lineageEfficiency": 1.0,
          "matchedEvidenceRecords": 6,
          "attributedSuccessCount": 3,
          "attributedWarningCount": 0,
          "attributedErrorCount": 0,
          "attributedToolErrorCount": 0,
          "attributedExternalErrorCount": 0,
          "evidenceSupport": 0.03,
          "evidenceIssuePenalty": 0.0,
          "reviewedPolicyBonus": 0.0,
          "reviewedPolicyPenalty": 0.0,
          "liveWinnerBoost": 0.0
        },
        "evidence": {
          "matchedRecordCount": 6,
          "successCount": 3,
          "warningCount": 0,
          "errorCount": 0,
          "toolErrorCount": 0,
          "externalErrorCount": 0,
          "sourceKindCounts": {
            "handoff_event": 1,
            "run_report": 1,
            "run_state": 2,
            "transcript_event": 2
          },
          "statusCounts": {
            "ready_for_quality_gate": 1,
            "review": 1,
            "spec": 1,
            "success": 3
          }
        }
      },
      "runnerUp": {
        "candidateId": "relax-no-product-code-boundary",
        "iteration": 1,
        "searchDepth": 1,
        "score": 0.842105,
        "complexityScore": 3105,
        "trajectoryScore": 0.60125,
        "trajectorySignals": {
          "validationBreadth": 0.875,
          "parentProgress": 0.0,
          "actionEfficiency": 0.5,
          "targetFocus": 1.0,
          "lineageEfficiency": 0.5,
          "matchedEvidenceRecords": 3,
          "attributedSuccessCount": 0,
          "attributedWarningCount": 0,
          "attributedErrorCount": 2,
          "attributedToolErrorCount": 2,
          "attributedExternalErrorCount": 0,
          "evidenceSupport": 0.0,
          "evidenceIssuePenalty": 0.08,
          "reviewedPolicyBonus": 0.0,
          "reviewedPolicyPenalty": 0.0,
          "liveWinnerBoost": 0.0
        },
        "evidence": {
          "matchedRecordCount": 3,
          "successCount": 0,
          "warningCount": 0,
          "errorCount": 2,
          "toolErrorCount": 2,
          "externalErrorCount": 0,
          "sourceKindCounts": {
            "run_report": 1,
            "transcript_event": 2
          },
          "statusCounts": {
            "error": 2,
            "ready_for_quality_gate": 1
          }
        }
      },
      "liveEvaluation": null
    }
  },
  "evidenceSummary": {
    "recordCount": 26,
    "runCount": 3,
    "recordsByKind": {
      "run_state": 3,
      "run_report": 8,
      "hook_event": 5,
      "session_event": 5,
      "transcript_event": 4,
      "handoff_event": 1
    },
    "statuses": {
      "Review": 1,
      "READY_FOR_QUALITY_GATE": 5,
      "PASS": 3,
      "Spec": 1,
      "Intake": 1,
      "success": 3,
      "error": 2
    },
    "reportFailureCount": 0,
    "toolErrorCount": 0,
    "parseErrorCount": 0,
    "sessionRecordCount": 5,
    "transcriptRecordCount": 4,
    "handoffRecordCount": 1,
    "externalLogRecordCount": 5,
    "externalSourceCount": 3
  },
  "liveEvaluation": {
    "enabled": false,
    "status": "disabled",
    "strategy": "advisory",
    "provider": "github-models",
    "model": "gpt-5.4",
    "sampleCount": 0,
    "evaluatedCandidateIds": [],
    "winnerCandidateId": "baseline",
    "bestCandidateChanged": false,
    "tieBreakerApplied": false,
    "fallbackToDeterministic": false,
    "reason": "live_evaluator_disabled",
    "verdictCounts": {},
    "judgments": []
  },
  "stagedPatch": {
    "enabled": true,
    "mode": "review_bundle",
    "applyOnPass": false,
    "candidateId": "baseline",
    "candidatePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/candidates/iteration-00-baseline.agent.md",
    "changedTargetCount": 0,
    "changedTargets": [],
    "reviewerHints": [],
    "manifestFormat": "candidate_snapshot",
    "includeTargetSnapshots": true,
    "includeDiffSummary": true
  },
  "provenance": {
    "inputs": {
      "experiment": {
        "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-experiment.md",
        "exists": true,
        "sha256": "4fdfba58c95ea72fac6e4e6aa0c82dc34e1d3eb934735dddfe9a6869e4052c15",
        "sizeBytes": 8968
      },
      "benchmark": {
        "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/skills/autoagent-loop/examples/team-lead-benchmark.json",
        "exists": true,
        "sha256": "e6317b46662d050f5b108fcadd61a64cf81b4734de11efb69661cc26d39ce71d",
        "sizeBytes": 1924
      },
      "mutationCatalog": {
        "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/skills/autoagent-loop/examples/team-lead-mutations.json",
        "exists": true,
        "sha256": "b0bb3b075af0d678d4029ab6d401a2c4915b7e5bd51f75008499ce2984e71c4b",
        "sizeBytes": 636
      },
      "liveEvaluatorPrompt": null,
      "liveEvaluatorRubrics": [],
      "resumeCheckpoint": null
    },
    "evidence": {
      "datasetPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-evidence.json",
      "summary": {
        "recordCount": 26,
        "runCount": 3,
        "recordsByKind": {
          "run_state": 3,
          "run_report": 8,
          "hook_event": 5,
          "session_event": 5,
          "transcript_event": 4,
          "handoff_event": 1
        },
        "statuses": {
          "Review": 1,
          "READY_FOR_QUALITY_GATE": 5,
          "PASS": 3,
          "Spec": 1,
          "Intake": 1,
          "success": 3,
          "error": 2
        },
        "reportFailureCount": 0,
        "toolErrorCount": 0,
        "parseErrorCount": 0,
        "sessionRecordCount": 5,
        "transcriptRecordCount": 4,
        "handoffRecordCount": 1,
        "externalLogRecordCount": 5,
        "externalSourceCount": 3
      },
      "sources": {
        "currentArtifacts": [
          "docs/agents/state.json",
          "docs/agents/patch-report.md",
          "docs/agents/test-report.md",
          "docs/agents/review-report.md"
        ],
        "runSnapshots": [
          "20260307-182815",
          "20260308-151009",
          "20260308-160258"
        ],
        "hookAuditFiles": [
          "docs/agents/runs/20260308-160258/hook-audit/tool-audit.jsonl",
          "docs/agents/runs/20260307-182815/hook-audit/tool-audit.jsonl"
        ],
        "sessionArtifacts": [
          "docs/agents/runs/20260308-160258/hook-audit/session.jsonl",
          "docs/agents/runs/20260307-182815/hook-audit/session.jsonl"
        ],
        "externalLogs": [
          {
            "id": "chat-history-1",
            "kind": "chat_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-chat-history.json",
            "recordCount": 2,
            "recordKind": "transcript_event"
          },
          {
            "id": "transcript-history-1",
            "kind": "conversation_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-transcript-history.jsonl",
            "recordCount": 2,
            "recordKind": "transcript_event"
          },
          {
            "id": "handoff-history-1",
            "kind": "handoff_history",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-handoff-history.jsonl",
            "recordCount": 1,
            "recordKind": "handoff_event"
          }
        ],
        "transcriptSources": [
          {
            "id": "chat-history-1",
            "kind": "chat_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-chat-history.json",
            "recordCount": 2,
            "recordKind": "transcript_event"
          },
          {
            "id": "transcript-history-1",
            "kind": "conversation_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-transcript-history.jsonl",
            "recordCount": 2,
            "recordKind": "transcript_event"
          }
        ],
        "handoffSources": [
          {
            "id": "handoff-history-1",
            "kind": "handoff_history",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/tests/fixtures/autoagent-loop/team-lead-handoff-history.jsonl",
            "recordCount": 1,
            "recordKind": "handoff_event"
          }
        ]
      }
    },
    "policy": {
      "continuousPolicy": {
        "enabled": false,
        "mode": "manual",
        "scheduleCron": null,
        "triggerOn": [
          "review_failure"
        ],
        "minSignalCount": 2,
        "maxQueuedRuns": 1,
        "maxRunsPerSweep": 1,
        "learningWindowDays": 30,
        "stageOnly": true,
        "requireReviewPass": true
      },
      "continuationEligibility": {
        "eligible": false,
        "status": "blocked",
        "blockedReasons": [
          "manual_mode"
        ],
        "executionMode": "report_only",
        "reviewGated": true
      },
      "governedTaskLifecycle": {
        "status": "available",
        "readable": true,
        "sourcePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
        "taskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
        "taskTitle": "Implement transcript-backed reasoning-path efficiency learning for AutoAgent",
        "phase": "Review",
        "qualityGateStatus": "PASS",
        "nextActionSummary": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
        "nextActionOwner": "team-lead",
        "missingFields": []
      },
      "governedReviewConsensus": {
        "agrees": true,
        "status": "consistent",
        "blockedReasons": [],
        "stateStatus": "PASS",
        "stateReadable": true,
        "stateSourcePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
        "reviewReportStatus": "PASS",
        "reviewReportReadable": true,
        "reviewReportSourcePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md"
      },
      "continuationReadiness": {
        "ready": false,
        "status": "blocked",
        "blockedReasons": [
          "manual_mode"
        ],
        "executionMode": "report_only",
        "reviewGated": true,
        "policyEligible": false,
        "governedReviewStatus": "PASS",
        "governedReviewReadable": true,
        "governedReviewSourcePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json"
      },
      "reviewedContinuationHandoff": {
        "ready": false,
        "status": "blocked",
        "blockedReasons": [
          "manual_mode"
        ],
        "handoffMode": "reviewed_manual",
        "manualOnly": true,
        "executionMode": "report_only",
        "reviewGated": true,
        "policyEligible": false,
        "continuationReadinessStatus": "blocked",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
        "governedTaskPhase": "Review",
        "summary": "Not ready for reviewed manual handoff.",
        "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
        "artifactRefs": {
          "state": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
          "reviewReport": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md",
          "report": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md"
        }
      },
      "orchestrationContract": {
        "ready": false,
        "status": "blocked",
        "blockedReasons": [
          "manual_mode"
        ],
        "contractMode": "staged_dispatch_simulation",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": true,
        "executionMode": "report_only",
        "reviewGated": true,
        "policyEligible": false,
        "reviewedHandoffStatus": "blocked",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
        "governedTaskPhase": "Review",
        "contractId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412::staged_dispatch_simulation",
        "summary": "Staged dispatch simulation is blocked.",
        "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
        "artifactRefs": {
          "state": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
          "reviewReport": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md",
          "report": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md",
          "adr": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/adr/0001-phase4-bounded-orchestration-rollout.md"
        }
      },
      "reviewedDispatchIntent": {
        "ready": false,
        "status": "blocked",
        "blockedReasons": [
          "manual_mode"
        ],
        "intentMode": "reviewed_dispatch_intent",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": true,
        "executionMode": "report_only",
        "reviewGated": true,
        "policyEligible": false,
        "requiresExplicitApproval": true,
        "approvalStatus": "blocked",
        "approvalMetadataPresent": false,
        "approvalSource": "governed_artifacts_only",
        "orchestrationContractStatus": "blocked",
        "reviewedHandoffStatus": "blocked",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
        "governedTaskPhase": "Review",
        "intentId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412::staged_dispatch_simulation::reviewed_dispatch_intent",
        "summary": "Reviewed dispatch intent is blocked.",
        "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
        "artifactRefs": {
          "state": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
          "reviewReport": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md",
          "report": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md",
          "adr": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/adr/0001-phase4-bounded-orchestration-rollout.md"
        }
      },
      "governedApprovalMetadata": {
        "ready": false,
        "status": "blocked",
        "blockedReasons": [
          "manual_mode"
        ],
        "approvalMode": "governed_approval_metadata",
        "manualOnly": true,
        "executionMode": "report_only",
        "reviewGated": true,
        "policyEligible": false,
        "requiresExplicitApproval": true,
        "approvalMetadataPresent": false,
        "approvalSource": "governed_artifacts_only",
        "readyForRecording": false,
        "reviewPassRecorded": true,
        "reviewPassReadable": true,
        "qualityGateStatus": "PASS",
        "reviewedDispatchIntentStatus": "blocked",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412",
        "governedTaskPhase": "Review",
        "metadataId": "manual-autoagent-phase5f-trace-backed-reasoning-path-efficiency-20260412::staged_dispatch_simulation::reviewed_dispatch_intent::governed_approval_metadata",
        "summary": "Governed approval metadata is blocked.",
        "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice.",
        "artifactRefs": {
          "state": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/state.json",
          "reviewReport": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/review-report.md",
          "report": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md",
          "adr": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/adr/0001-phase4-bounded-orchestration-rollout.md"
        }
      },
      "reviewedPolicyRuntime": {
        "enabled": false,
        "artifactPath": null,
        "preferredSequenceBonus": 0.04,
        "escalationPenalty": 0.05
      },
      "reviewedPolicyRuntimeState": {
        "enabled": false,
        "status": "disabled",
        "artifactPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-policies.json",
        "artifactFound": false,
        "policyCount": 0,
        "activePolicyCount": 0,
        "approvedLearningDraftCount": 0
      },
      "guardedLearningPromotion": {
        "ready": false,
        "status": "blocked",
        "blockedReasons": [
          "manual_mode"
        ],
        "mode": "generated_review_manifest",
        "reviewRequired": true,
        "artifactPath": null,
        "minObservedCount": 2,
        "minPolicyLearningScore": 0.7,
        "acceptedBenchmarkDraftCount": 0,
        "acceptedPolicyDraftCount": 0,
        "deferredBenchmarkDraftCount": 2,
        "deferredPolicyDraftCount": 2,
        "acceptedBenchmarkDraftIds": [],
        "acceptedPolicyDraftIds": [],
        "summary": "Guarded learning promotion is blocked until continuation and approval gates are ready.",
        "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice."
      }
    },
    "artifacts": {
      "resultsPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-results.tsv",
      "checkpointPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint.json",
      "checkpointStage": "post_mutation_search",
      "checkpointManifestPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint-manifest.json",
      "searchLedgerPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-ledger.json",
      "benchmarkDraftsPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-benchmark-fragments.json",
      "mutationDraftsPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-mutation-catalog.json",
      "policyDraftsPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-policy-catalog.json",
      "tracePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/autoagent-trace.json",
      "currentRunRoot": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258",
      "guardedLearningReviewPath": null
    }
  },
  "baseline": {
    "candidateId": "baseline",
    "score": 1.0,
    "trajectoryScore": 0.88,
    "trajectoryScoreBreakdown": {
      "validationBreadth": 1.0,
      "parentProgress": 0.0,
      "actionEfficiency": 1.0,
      "targetFocus": 1.0,
      "lineageEfficiency": 1.0,
      "matchedEvidenceRecords": 6,
      "attributedSuccessCount": 3,
      "attributedWarningCount": 0,
      "attributedErrorCount": 0,
      "attributedToolErrorCount": 0,
      "attributedExternalErrorCount": 0,
      "evidenceSupport": 0.03,
      "evidenceIssuePenalty": 0.0,
      "reviewedPolicyBonus": 0.0,
      "reviewedPolicyPenalty": 0.0,
      "liveWinnerBoost": 0.0
    },
    "trajectoryEvidenceContext": {
      "aliases": [
        "baseline",
        "candidate-trajectory-baseline"
      ],
      "matchedRecordCount": 6,
      "errorCount": 0,
      "warningCount": 0,
      "successCount": 3,
      "toolErrorCount": 0,
      "externalErrorCount": 0,
      "sourceKindCounts": {
        "run_state": 2,
        "run_report": 1,
        "transcript_event": 2,
        "handoff_event": 1
      },
      "statusCounts": {
        "review": 1,
        "spec": 1,
        "ready_for_quality_gate": 1,
        "success": 3
      }
    },
    "reviewedPolicyContext": {
      "enabled": false,
      "status": "disabled",
      "artifactPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-policies.json",
      "policyCount": 0,
      "matchedPolicyCount": 0,
      "preferredSequenceMatchCount": 0,
      "escalationMatchCount": 0,
      "bonus": 0.0,
      "penalty": 0.0,
      "matchedPolicyIds": [],
      "matchedPolicies": []
    },
    "passedChecks": 8,
    "totalChecks": 8,
    "complexity": {
      "bodyChars": 2948,
      "toolCount": 6,
      "mcpServerCount": 0,
      "fileCount": 1,
      "score": 3113,
      "perTarget": {
        "team-lead": {
          "bodyChars": 2948,
          "toolCount": 6,
          "mcpServerCount": 0,
          "score": 3098
        }
      }
    }
  },
  "bestCandidate": {
    "candidateId": "baseline",
    "score": 1.0,
    "trajectoryScore": 0.88,
    "trajectoryScoreBreakdown": {
      "validationBreadth": 1.0,
      "parentProgress": 0.0,
      "actionEfficiency": 1.0,
      "targetFocus": 1.0,
      "lineageEfficiency": 1.0,
      "matchedEvidenceRecords": 6,
      "attributedSuccessCount": 3,
      "attributedWarningCount": 0,
      "attributedErrorCount": 0,
      "attributedToolErrorCount": 0,
      "attributedExternalErrorCount": 0,
      "evidenceSupport": 0.03,
      "evidenceIssuePenalty": 0.0,
      "reviewedPolicyBonus": 0.0,
      "reviewedPolicyPenalty": 0.0,
      "liveWinnerBoost": 0.0
    },
    "trajectoryEvidenceContext": {
      "aliases": [
        "baseline",
        "candidate-trajectory-baseline"
      ],
      "matchedRecordCount": 6,
      "errorCount": 0,
      "warningCount": 0,
      "successCount": 3,
      "toolErrorCount": 0,
      "externalErrorCount": 0,
      "sourceKindCounts": {
        "run_state": 2,
        "run_report": 1,
        "transcript_event": 2,
        "handoff_event": 1
      },
      "statusCounts": {
        "review": 1,
        "spec": 1,
        "ready_for_quality_gate": 1,
        "success": 3
      }
    },
    "reviewedPolicyContext": {
      "enabled": false,
      "status": "disabled",
      "artifactPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-policies.json",
      "policyCount": 0,
      "matchedPolicyCount": 0,
      "preferredSequenceMatchCount": 0,
      "escalationMatchCount": 0,
      "bonus": 0.0,
      "penalty": 0.0,
      "matchedPolicyIds": [],
      "matchedPolicies": []
    },
    "passedChecks": 8,
    "totalChecks": 8,
    "complexity": {
      "bodyChars": 2948,
      "toolCount": 6,
      "mcpServerCount": 0,
      "fileCount": 1,
      "score": 3113,
      "perTarget": {
        "team-lead": {
          "bodyChars": 2948,
          "toolCount": 6,
          "mcpServerCount": 0,
          "score": 3098
        }
      }
    },
    "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/candidates/iteration-00-baseline.agent.md"
  },
  "keptCandidates": [
    "baseline"
  ],
  "discardedCandidates": [
    "relax-no-product-code-boundary"
  ],
  "iterations": [
    {
      "iteration": 0,
      "candidateId": "baseline",
      "parentCandidateId": null,
      "searchDepth": 0,
      "score": 1.0,
      "passedChecks": 8,
      "totalChecks": 8,
      "status": "keep",
      "description": "Baseline target agent",
      "complexity": {
        "bodyChars": 2948,
        "toolCount": 6,
        "mcpServerCount": 0,
        "fileCount": 1,
        "score": 3113,
        "perTarget": {
          "team-lead": {
            "bodyChars": 2948,
            "toolCount": 6,
            "mcpServerCount": 0,
            "score": 3098
          }
        }
      },
      "trajectoryScore": 0.88
    },
    {
      "iteration": 1,
      "candidateId": "relax-no-product-code-boundary",
      "parentCandidateId": "baseline",
      "searchDepth": 1,
      "score": 0.842105,
      "trajectoryScore": 0.60125,
      "passedChecks": 7,
      "totalChecks": 8,
      "status": "discard",
      "description": "Loosen the manager scope to prove governance regressions are discarded.",
      "complexity": {
        "bodyChars": 2940,
        "toolCount": 6,
        "mcpServerCount": 0,
        "fileCount": 1,
        "score": 3105,
        "perTarget": {
          "team-lead": {
            "bodyChars": 2940,
            "toolCount": 6,
            "mcpServerCount": 0,
            "score": 3090
          }
        }
      },
      "touchedTargets": [
        "team-lead"
      ]
    }
  ],
  "appliedBestVariant": false,
  "appliedPath": null,
  "appliedPaths": [],
  "traceSummary": {
    "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/autoagent-trace.json",
    "eventCount": 6,
    "trajectoryCount": 2,
    "episodeCount": 2,
    "evidenceBackedEpisodeCount": 2,
    "bestTrajectoryScore": 0.88,
    "bestTrajectoryEvidenceMatches": 6,
    "winnerExplanation": {
      "winnerCandidateId": "baseline",
      "comparedCandidateId": "relax-no-product-code-boundary",
      "comparisonMode": "deterministic_ranking",
      "decisiveSignal": "benchmark_score",
      "evidenceBacked": false,
      "summary": "baseline beat relax-no-product-code-boundary on benchmark score (1.0 vs 0.842105).",
      "evidenceSummary": null,
      "rankingComparison": {
        "winnerScore": 1.0,
        "runnerUpScore": 0.842105,
        "scoreDelta": 0.157895,
        "winnerComplexityScore": 3113,
        "runnerUpComplexityScore": 3105,
        "complexityAdvantage": -8,
        "winnerTrajectoryScore": 0.88,
        "runnerUpTrajectoryScore": 0.60125,
        "trajectoryScoreDelta": 0.27875
      },
      "topTrajectorySignals": [
        {
          "signal": "attributedSuccessCount",
          "preference": "higher_is_better",
          "winner": 3,
          "runnerUp": 0,
          "advantage": 3.0
        },
        {
          "signal": "matchedEvidenceRecords",
          "preference": "higher_is_better",
          "winner": 6,
          "runnerUp": 3,
          "advantage": 3.0
        },
        {
          "signal": "attributedErrorCount",
          "preference": "lower_is_better",
          "winner": 0,
          "runnerUp": 2,
          "advantage": 2.0
        },
        {
          "signal": "attributedToolErrorCount",
          "preference": "lower_is_better",
          "winner": 0,
          "runnerUp": 2,
          "advantage": 2.0
        },
        {
          "signal": "actionEfficiency",
          "preference": "higher_is_better",
          "winner": 1.0,
          "runnerUp": 0.5,
          "advantage": 0.5
        }
      ],
      "trajectorySummary": "Top trajectory contributors: attributedSuccessCount +3, matchedEvidenceRecords +3, attributedErrorCount lower by 2",
      "evidenceComparison": {
        "winnerSourceKinds": {
          "handoff_event": 1,
          "run_report": 1,
          "run_state": 2,
          "transcript_event": 2
        },
        "runnerUpSourceKinds": {
          "run_report": 1,
          "transcript_event": 2
        },
        "winnerStatuses": {
          "ready_for_quality_gate": 1,
          "review": 1,
          "spec": 1,
          "success": 3
        },
        "runnerUpStatuses": {
          "error": 2,
          "ready_for_quality_gate": 1
        }
      },
      "winner": {
        "candidateId": "baseline",
        "iteration": 0,
        "searchDepth": 0,
        "score": 1.0,
        "complexityScore": 3113,
        "trajectoryScore": 0.88,
        "trajectorySignals": {
          "validationBreadth": 1.0,
          "parentProgress": 0.0,
          "actionEfficiency": 1.0,
          "targetFocus": 1.0,
          "lineageEfficiency": 1.0,
          "matchedEvidenceRecords": 6,
          "attributedSuccessCount": 3,
          "attributedWarningCount": 0,
          "attributedErrorCount": 0,
          "attributedToolErrorCount": 0,
          "attributedExternalErrorCount": 0,
          "evidenceSupport": 0.03,
          "evidenceIssuePenalty": 0.0,
          "reviewedPolicyBonus": 0.0,
          "reviewedPolicyPenalty": 0.0,
          "liveWinnerBoost": 0.0
        },
        "evidence": {
          "matchedRecordCount": 6,
          "successCount": 3,
          "warningCount": 0,
          "errorCount": 0,
          "toolErrorCount": 0,
          "externalErrorCount": 0,
          "sourceKindCounts": {
            "handoff_event": 1,
            "run_report": 1,
            "run_state": 2,
            "transcript_event": 2
          },
          "statusCounts": {
            "ready_for_quality_gate": 1,
            "review": 1,
            "spec": 1,
            "success": 3
          }
        }
      },
      "runnerUp": {
        "candidateId": "relax-no-product-code-boundary",
        "iteration": 1,
        "searchDepth": 1,
        "score": 0.842105,
        "complexityScore": 3105,
        "trajectoryScore": 0.60125,
        "trajectorySignals": {
          "validationBreadth": 0.875,
          "parentProgress": 0.0,
          "actionEfficiency": 0.5,
          "targetFocus": 1.0,
          "lineageEfficiency": 0.5,
          "matchedEvidenceRecords": 3,
          "attributedSuccessCount": 0,
          "attributedWarningCount": 0,
          "attributedErrorCount": 2,
          "attributedToolErrorCount": 2,
          "attributedExternalErrorCount": 0,
          "evidenceSupport": 0.0,
          "evidenceIssuePenalty": 0.08,
          "reviewedPolicyBonus": 0.0,
          "reviewedPolicyPenalty": 0.0,
          "liveWinnerBoost": 0.0
        },
        "evidence": {
          "matchedRecordCount": 3,
          "successCount": 0,
          "warningCount": 0,
          "errorCount": 2,
          "toolErrorCount": 2,
          "externalErrorCount": 0,
          "sourceKindCounts": {
            "run_report": 1,
            "transcript_event": 2
          },
          "statusCounts": {
            "error": 2,
            "ready_for_quality_gate": 1
          }
        }
      },
      "liveEvaluation": null
    }
  },
  "learningSummary": {
    "mode": "shadow_only",
    "episodeCount": 2,
    "evidenceBackedEpisodeCount": 2,
    "reasoningPathSignal": {
      "name": "reasoningPathEfficiencyScore",
      "sourceBackedPathCount": 2,
      "transcriptBackedPathCount": 2,
      "handoffBackedPathCount": 1,
      "bestObservedScore": 0.808333
    },
    "topObservedPaths": [
      {
        "episodeId": "candidate-episode-baseline",
        "trajectoryId": "candidate-trajectory-baseline",
        "candidateId": "baseline",
        "classification": "successful_path",
        "learningScore": 0.870833,
        "qualityScore": 0.9125,
        "efficiencyScore": 0.808333,
        "reasoningPathEfficiencyScore": 0.808333,
        "terminalStatus": "success",
        "matchedRecordCount": 6,
        "handoffCount": 1,
        "searchDepth": 0,
        "actionCount": 0,
        "sourceKinds": [
          "handoff_event",
          "run_report",
          "run_state",
          "transcript_event"
        ],
        "toolNames": [
          "read_file",
          "grep_search"
        ],
        "toolSequence": [
          "read_file",
          "grep_search",
          "read_file"
        ],
        "provenance": {
          "matchedRecordCount": 6,
          "sourceKinds": [
            "handoff_event",
            "run_report",
            "run_state",
            "transcript_event"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 1,
          "transcriptBacked": true,
          "handoffBacked": true
        },
        "factors": {
          "benchmarkQuality": 1.0,
          "evidenceQuality": 0.75,
          "terminalOutcomeScore": 1.0,
          "actionCount": 0,
          "searchDepth": 0,
          "stepCount": 6,
          "handoffCount": 1,
          "handoffEfficiency": 0.666667,
          "toolSequenceLength": 3,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.808333
        },
        "selectedAsBest": true
      },
      {
        "episodeId": "candidate-episode-relax-no-product-code-boundary",
        "trajectoryId": "candidate-trajectory-relax-no-product-code-boundary",
        "candidateId": "relax-no-product-code-boundary",
        "classification": "failure_path",
        "learningScore": 0.487368,
        "qualityScore": 0.378947,
        "efficiencyScore": 0.65,
        "reasoningPathEfficiencyScore": 0.65,
        "terminalStatus": "error",
        "matchedRecordCount": 3,
        "handoffCount": 0,
        "searchDepth": 1,
        "actionCount": 1,
        "sourceKinds": [
          "run_report",
          "transcript_event"
        ],
        "toolNames": [
          "apply_patch",
          "read_file"
        ],
        "toolSequence": [
          "apply_patch",
          "read_file"
        ],
        "provenance": {
          "matchedRecordCount": 3,
          "sourceKinds": [
            "run_report",
            "transcript_event"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 0,
          "transcriptBacked": true,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.842105,
          "evidenceQuality": 0.0,
          "terminalOutcomeScore": 0.0,
          "actionCount": 1,
          "searchDepth": 1,
          "stepCount": 3,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 2,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.65
        },
        "selectedAsBest": false
      }
    ],
    "benchmarkCandidates": [
      {
        "suggestionId": "episode-benchmark-01",
        "kind": "episode_success_guard",
        "classification": "successful_path",
        "observedCount": 1,
        "learningScore": 0.870833,
        "exampleCandidateIds": [
          "baseline"
        ],
        "sourceKinds": [
          "handoff_event",
          "run_report",
          "run_state",
          "transcript_event"
        ],
        "handoffCount": 1,
        "toolNames": [
          "read_file",
          "grep_search"
        ],
        "terminalStatus": "success",
        "reasoningPathEfficiencyScore": 0.808333,
        "provenance": {
          "matchedRecordCount": 6,
          "sourceKinds": [
            "handoff_event",
            "run_report",
            "run_state",
            "transcript_event"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 1,
          "transcriptBacked": true,
          "handoffBacked": true
        },
        "factors": {
          "benchmarkQuality": 1.0,
          "evidenceQuality": 0.75,
          "terminalOutcomeScore": 1.0,
          "actionCount": 0,
          "searchDepth": 0,
          "stepCount": 6,
          "handoffCount": 1,
          "handoffEfficiency": 0.666667,
          "toolSequenceLength": 3,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.808333
        },
        "rationale": "Preserve the observed successful path pattern."
      },
      {
        "suggestionId": "episode-benchmark-02",
        "kind": "episode_failure_regression",
        "classification": "failure_path",
        "observedCount": 1,
        "learningScore": 0.487368,
        "exampleCandidateIds": [
          "relax-no-product-code-boundary"
        ],
        "sourceKinds": [
          "run_report",
          "transcript_event"
        ],
        "handoffCount": 0,
        "toolNames": [
          "apply_patch",
          "read_file"
        ],
        "terminalStatus": "error",
        "reasoningPathEfficiencyScore": 0.65,
        "provenance": {
          "matchedRecordCount": 3,
          "sourceKinds": [
            "run_report",
            "transcript_event"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 0,
          "transcriptBacked": true,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.842105,
          "evidenceQuality": 0.0,
          "terminalOutcomeScore": 0.0,
          "actionCount": 1,
          "searchDepth": 1,
          "stepCount": 3,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 2,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.65
        },
        "rationale": "Add a regression guard for the observed failing path pattern."
      }
    ],
    "mutationSeedCandidates": [
      {
        "seedId": "episode-mutation-seed-01",
        "kind": "reinforce_success_path",
        "candidateId": "baseline",
        "episodeId": "candidate-episode-baseline",
        "sourceMutationId": null,
        "sourceKinds": [
          "handoff_event",
          "run_report",
          "run_state",
          "transcript_event"
        ],
        "handoffCount": 1,
        "toolNames": [
          "read_file",
          "grep_search"
        ],
        "targetSearchDepth": 0,
        "targetActionCount": 0,
        "learningScore": 0.870833,
        "reasoningPathEfficiencyScore": 0.808333,
        "provenance": {
          "matchedRecordCount": 6,
          "sourceKinds": [
            "handoff_event",
            "run_report",
            "run_state",
            "transcript_event"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 1,
          "transcriptBacked": true,
          "handoffBacked": true
        },
        "factors": {
          "benchmarkQuality": 1.0,
          "evidenceQuality": 0.75,
          "terminalOutcomeScore": 1.0,
          "actionCount": 0,
          "searchDepth": 0,
          "stepCount": 6,
          "handoffCount": 1,
          "handoffEfficiency": 0.666667,
          "toolSequenceLength": 3,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.808333
        },
        "rationale": "Promote this observed successful path as a future mutation seed."
      },
      {
        "seedId": "episode-mutation-seed-02",
        "kind": "avoid_failure_path",
        "candidateId": "relax-no-product-code-boundary",
        "episodeId": "candidate-episode-relax-no-product-code-boundary",
        "sourceMutationId": "relax-no-product-code-boundary",
        "sourceKinds": [
          "run_report",
          "transcript_event"
        ],
        "handoffCount": 0,
        "toolNames": [
          "apply_patch",
          "read_file"
        ],
        "targetSearchDepth": 1,
        "targetActionCount": 1,
        "learningScore": 0.487368,
        "reasoningPathEfficiencyScore": 0.65,
        "provenance": {
          "matchedRecordCount": 3,
          "sourceKinds": [
            "run_report",
            "transcript_event"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 0,
          "transcriptBacked": true,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.842105,
          "evidenceQuality": 0.0,
          "terminalOutcomeScore": 0.0,
          "actionCount": 1,
          "searchDepth": 1,
          "stepCount": 3,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 2,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.65
        },
        "rationale": "Use this observed failing path to shape a future avoidance mutation."
      }
    ],
    "policyCandidates": [
      {
        "policyId": "episode-policy-01",
        "kind": "preferred_tool_sequence",
        "classification": "successful_path",
        "observedCount": 1,
        "exampleCandidateIds": [
          "baseline"
        ],
        "sourceKinds": [
          "handoff_event",
          "run_report",
          "run_state",
          "transcript_event"
        ],
        "handoffCount": 1,
        "toolNames": [
          "read_file",
          "grep_search"
        ],
        "toolSequence": [
          "read_file",
          "grep_search",
          "read_file"
        ],
        "terminalStatus": "success",
        "constraints": {
          "maxSearchDepth": 0,
          "maxActionCount": 0
        },
        "learningScore": 0.870833,
        "reasoningPathEfficiencyScore": 0.808333,
        "provenance": {
          "matchedRecordCount": 6,
          "sourceKinds": [
            "handoff_event",
            "run_report",
            "run_state",
            "transcript_event"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 1,
          "transcriptBacked": true,
          "handoffBacked": true
        },
        "factors": {
          "benchmarkQuality": 1.0,
          "evidenceQuality": 0.75,
          "terminalOutcomeScore": 1.0,
          "actionCount": 0,
          "searchDepth": 0,
          "stepCount": 6,
          "handoffCount": 1,
          "handoffEfficiency": 0.666667,
          "toolSequenceLength": 3,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.808333
        },
        "rationale": "Prefer the observed successful tool sequence for similar paths."
      },
      {
        "policyId": "episode-policy-02",
        "kind": "escalation_trigger",
        "classification": "failure_path",
        "observedCount": 1,
        "exampleCandidateIds": [
          "relax-no-product-code-boundary"
        ],
        "sourceKinds": [
          "run_report",
          "transcript_event"
        ],
        "handoffCount": 0,
        "triggerTools": [
          "apply_patch",
          "read_file"
        ],
        "terminalStatus": "error",
        "constraints": {
          "maxSearchDepth": 1,
          "maxActionCount": 1
        },
        "learningScore": 0.487368,
        "reasoningPathEfficiencyScore": 0.65,
        "provenance": {
          "matchedRecordCount": 3,
          "sourceKinds": [
            "run_report",
            "transcript_event"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 0,
          "transcriptBacked": true,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.842105,
          "evidenceQuality": 0.0,
          "terminalOutcomeScore": 0.0,
          "actionCount": 1,
          "searchDepth": 1,
          "stepCount": 3,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 2,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.65
        },
        "rationale": "Escalate or branch away when this observed tool path ends in failure or warning."
      }
    ]
  },
  "learningArtifacts": {
    "mode": "review_only",
    "benchmarkDraftCount": 2,
    "mutationDraftCount": 2,
    "policyDraftCount": 2,
    "benchmarkDraftsPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-benchmark-fragments.json",
    "mutationDraftsPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-mutation-catalog.json",
    "policyDraftsPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-policy-catalog.json"
  },
  "guardedLearningPromotion": {
    "ready": false,
    "status": "blocked",
    "blockedReasons": [
      "manual_mode"
    ],
    "mode": "generated_review_manifest",
    "reviewRequired": true,
    "artifactPath": null,
    "minObservedCount": 2,
    "minPolicyLearningScore": 0.7,
    "acceptedBenchmarkDraftCount": 0,
    "acceptedPolicyDraftCount": 0,
    "deferredBenchmarkDraftCount": 2,
    "deferredPolicyDraftCount": 2,
    "acceptedBenchmarkDraftIds": [],
    "acceptedPolicyDraftIds": [],
    "summary": "Guarded learning promotion is blocked until continuation and approval gates are ready.",
    "recommendedAction": "Present the implemented Phase 5F transcript-backed reasoning-path slice for maintainer review, then decide whether the next bounded follow-on should refine reviewer-facing learning summaries or open a separate autonomy-planning slice."
  },
  "learningPromotionAudit": {
    "status": "artifact_missing",
    "artifactPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/learning-promotion-audit.json",
    "artifactFound": false,
    "promotionSourceMode": null,
    "reviewedBenchmarkDraftCount": 0,
    "acceptedBenchmarkDraftCount": 0,
    "rejectedBenchmarkDraftCount": 0,
    "deferredBenchmarkDraftCount": 0,
    "reviewedMutationDraftCount": 0,
    "acceptedMutationDraftCount": 0,
    "rejectedMutationDraftCount": 0,
    "deferredMutationDraftCount": 0,
    "reviewedPolicyDraftCount": 0,
    "acceptedPolicyDraftCount": 0,
    "rejectedPolicyDraftCount": 0,
    "deferredPolicyDraftCount": 0,
    "reviewerOverrideCount": 0,
    "benchmarkReviewerOverrideCount": 0,
    "mutationReviewerOverrideCount": 0,
    "policyReviewerOverrideCount": 0,
    "blockedFactorCounts": {},
    "benchmarkBlockedFactorCounts": {},
    "mutationBlockedFactorCounts": {},
    "policyBlockedFactorCounts": {}
  },
  "artifacts": {
    "report": null,
    "results": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-results.tsv",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-results.tsv",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": {
        "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/autoagent-results.tsv",
        "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/autoagent-results.tsv",
        "fallbackUsed": false,
        "warning": null
      }
    },
    "evidence": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-evidence.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-evidence.json",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": {
        "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/autoagent-evidence.json",
        "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/autoagent-evidence.json",
        "fallbackUsed": false,
        "warning": null
      }
    },
    "checkpoint": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint.json",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": null
    },
    "checkpointManifest": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint-manifest.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint-manifest.json",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": null
    },
    "searchLedger": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-ledger.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-ledger.json",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": null
    },
    "benchmarkDrafts": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-benchmark-fragments.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-benchmark-fragments.json",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": null
    },
    "mutationDrafts": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-mutation-catalog.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-mutation-catalog.json",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": null
    },
    "policyDrafts": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-policy-catalog.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/draft-policy-catalog.json",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": null
    },
    "guardedLearningReview": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/guarded-learning-review.generated.json",
      "actualPath": null,
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": null
    },
    "trace": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/autoagent-trace.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/autoagent-trace.json",
      "fallbackUsed": false,
      "warning": null,
      "runSnapshot": null
    },
    "runRoot": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization"
  }
}
```
