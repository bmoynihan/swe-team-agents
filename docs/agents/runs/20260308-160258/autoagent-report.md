# AutoAgent Report

- Status: READY_FOR_QUALITY_GATE
- Report status meaning: artifact_readiness
- Experiment: team-lead-optimization
- Primary target: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/team-lead.agent.md
- Target bundle size: 3
- Evidence records: 26
- Evidence runs: 3
- External log records: 5
- Governed trace export records: 5
- Fixture-backed external log records: 0
- Transcript evidence records: 4
- Handoff evidence records: 1
- Baseline score: 1.0
- Best score: 1.0
- Best candidate: baseline
- Best trajectory score: 0.88
- Best trajectory evidence matches: 12
- Candidate search: current_best (frontier size 1)
- Candidate ranking signals: benchmark_score, complexity, trajectory_score
- Winner decisive signal: benchmark_score
- Winner rationale: baseline beat weaken-agent-guide-governance on benchmark score (1.0 vs 0.848485).
- Winner trajectory contributors: Top trajectory contributors: matchedEvidenceRecords +11, attributedSuccessCount +3, actionEfficiency +0.666667
- Winner evidence rationale: none
- Resume: fresh run
- Resume checkpoint stage: post_mutation_search
- Search ledger nodes: 3
- Checkpoint: 2/2 mutations complete
- Checkpoint storage: 1 inline, 2 snapshot-backed
- Checkpoint manifest: 2 snapshot-backed candidates, 6 files
- Trace events: 8
- Trace trajectories: 3
- Trace candidate episodes: 3
- Trace evidence-backed episodes: 3
- Learning mode: shadow_only
- Learning reasoning-path signal: reasoningPathEfficiencyScore
- Learning source-backed paths: 3
- Learning transcript-backed paths: 2
- Learning handoff-backed paths: 1
- Learning best reasoning-path efficiency: 0.795833
- Learning top observed paths: 3
- Learning benchmark candidates: 3
- Learning mutation seeds: 3
- Learning policy candidates: 2
- Learning benchmark draft fragments: 3
- Learning mutation draft entries: 3
- Learning policy draft entries: 2
- Trace best trajectory score: 0.88
- Trace best trajectory evidence matches: 12
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
- Guarded learning recommended action: Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.
- Learning promotion audit: ready
- Learning promotion audit artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/learning-promotion-audit.json
- Learning promotion audit source mode: manual_review
- Learning promotion audit reviewer overrides: 1
- Learning promotion audit benchmark decisions: reviewed 1, accepted 1, rejected 0, deferred 0
- Learning promotion audit mutation decisions: reviewed 1, accepted 1, rejected 0, deferred 0
- Learning promotion audit policy decisions: reviewed 1, accepted 1, rejected 0, deferred 0
- Learning promotion audit blocked factors: observedCount 1
- Learning promotion audit benchmark blocked factors: none
- Learning promotion audit mutation blocked factors: none
- Learning promotion audit policy blocked factors: observedCount 1
- Reviewed continuation package: ready
- Reviewed continuation bundle artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-continuation-bundle.json
- Reviewed continuation accepted items: benchmark 1, mutations 1, policies 1
- Reviewed continuation trace origins: governed_run_export
- Reviewed continuation governed trace runs: 20260308-160258
- Manual dispatch manifest: ready_for_manual_dispatch
- Manual dispatch blocked reasons: none
- Manual dispatch required action: Review the generated follow-on experiment and launch it manually with the provided command.
- Manual dispatch follow-on experiment: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-continuation-experiment.generated.md
- Manual dispatch launch command: py -3 "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/skills/autoagent-loop/scripts/autoagent_loop.py" --experiment "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-continuation-experiment.generated.md" --output-root "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs" --report "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md" --results "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-results.tsv" --evidence "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-evidence.json"
- Reviewed policy runtime: disabled (0 policies)
- Reviewed policy artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-policies.json
- Continuous mode: manual
- Continuation eligibility: blocked
- Continuation blocked reasons: manual_mode
- Continuation execution: report_only
- Governed task lifecycle: Implement
- Governed task id: manual-autoagent-broaden-governed-bundle-coverage-20260414
- Governed task title: Broaden the checked-in AutoAgent governed bundle to include AGENTS.md
- Governed lifecycle quality gate: PASS
- Governed next action: team-lead - Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.
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
- Reviewed handoff recommended action: Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.
- Orchestration contract: blocked
- Orchestration contract blocked reasons: manual_mode
- Orchestration contract mode: staged_dispatch_simulation
- Orchestration contract scope: bounded_follow_on_slice
- Orchestration contract id: manual-autoagent-broaden-governed-bundle-coverage-20260414::staged_dispatch_simulation
- Orchestration contract summary: Staged dispatch simulation is blocked.
- Orchestration contract recommended action: Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.
- Reviewed dispatch intent: blocked
- Reviewed dispatch blocked reasons: manual_mode
- Reviewed dispatch approval status: blocked
- Reviewed dispatch approval source: governed_artifacts_only
- Reviewed dispatch summary: Reviewed dispatch intent is blocked.
- Reviewed dispatch recommended action: Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.
- Governed approval metadata: blocked
- Governed approval blocked reasons: manual_mode
- Governed approval review pass recorded: True
- Governed approval quality gate: PASS
- Governed approval source: governed_artifacts_only
- Governed approval summary: Governed approval metadata is blocked.
- Governed approval recommended action: Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.
- Phase 4 bounded step: governed_approval_metadata
- Phase 4 execution authority: out_of_scope
- Phase 3 visibility scope: complete
- Phase 3 exit criteria: continuation eligibility, continuation readiness, governed review consensus, governed task lifecycle, and reviewed handoff visibility are all present under manual/report_only semantics
- Phase 3 unattended orchestration: out_of_scope
- Live evaluator: disabled
- Live evaluation status: disabled
- Staged patch: review_bundle (0 targets)
- Staged patch bundle: ready_no_changes
- Staged patch bundle artifact: D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/staged-patch-review-bundle.json
- Staged patch bundle targets: none
- Staged patch bundle required action: Review the staged patch bundle and governed artifacts before choosing the next bounded step.
- Applied best variant: False

```json
{
  "type": "AutoAgentReport",
  "status": "READY_FOR_QUALITY_GATE",
  "reportStatusMeaning": "artifact_readiness",
  "experiment": {
    "name": "team-lead-optimization",
    "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-experiment.md",
    "description": "Conservative first-pass AutoAgent experiment for this repository. It benchmarks a small governed manager bundle anchored on the `team-lead` agent profile, the shared Team Lead orchestration skill, and the repo-level `AGENTS.md` operating guide, tests a small mutation catalog, and keeps only variants that improve score or preserve score with lower complexity while staging review-oriented run metadata.\n",
    "directive": "# AutoAgent Experiment\n\nOptimize the Team Lead agent for clarity and brevity while preserving these requirements:\n\n- retain the sole-coordinator rule\n- retain the `docs/agents/` and `docs/agents/current-run.json` determinism contract\n- retain the manager boundary against product-code edits\n- retain the canonical delegation flow through `quality-gate`\n- retain the `ManagerDecision` output contract\n- preserve the reviewed tool surface in frontmatter\n\nKeep any candidate that improves benchmark score. If two candidates tie on score, keep the simpler one.\n\nThis checked-in Team Lead experiment now starts with a small governed manager bundle instead of a\nsingle target file. The `team-lead` agent profile still carries the highest-signal tool surface and\noutput contract, `.github/skills/team-lead/SKILL.md` carries the shared workflow rules that the\nmanager is expected to preserve across runs, and `AGENTS.md` carries the repo-level operating guide\nfor the canonical artifact root, validation order, and hook-governance expectations. This is still\ndeliberately smaller than the full agent team: it expands the optimization surface beyond one file\nwithout yet widening into specialist profiles, hooks, or broader shared guidance.\n\nIf maintainers later want broader optimization, they can extend `optimizationTargets` further to\ninclude specialist agent profiles or additional shared guidance artifacts after the bundle benchmark\nand mutation catalog have enough evidence-backed coverage to keep the larger search space governed.\n\nIt also opts into the governed evidence collector so the loop can summarize current artifacts, recent\nrun snapshots, and hook-audit records into a redacted evidence dataset without reading arbitrary\nexternal files by default.\n\nThis checked-in experiment now points its chat, transcript, and handoff evidence at sanitized\ngoverned exports stored under the active run snapshot so canonical artifacts exercise the\nrepo-owned continuation path instead of the fixture-only fallback.\n\nThe candidate-search policy is now explicit in the sample schema. This checked-in experiment keeps\nthe default `current_best` search path with a frontier size of `1`, which preserves the historical\nlinear mutation loop. Maintainers can opt into bounded frontier search in reviewed runs by raising\n`candidatePolicy.frontierSize` above `1`, which enables branching from multiple kept candidates and\nrecords parent or depth metadata in the run artifacts.\n\nEach generated AutoAgent run now also emits a dedicated `search-ledger.json` artifact under the run\nroot. That ledger captures candidate nodes, frontier snapshots, and the final best-candidate lineage\nso replay-oriented slices do not have to reconstruct search history from the TSV or embedded report\nJSON alone.\n\nRuns now also emit a dedicated `search-checkpoint.json` artifact under the same generated run root.\nThat checkpoint captures the post-mutation search state needed for guarded resume support: candidate\nrecords, the current frontier, the deterministic best candidate, and the next mutation index. The\ncheckpoint keeps full inline documents only for the active frontier and deterministic best\ncandidate; older candidates restore from the generated candidate snapshots already written under the\nrun root. Checkpoint creation intentionally stops before any optional live-evaluator advisory or\ntie-breaker pass, so resume always re-enters from deterministic mutation-search state rather than\nfrom a post-live winner selection. A maintainer can resume from that checkpoint with `--resume`,\nbut the checked-in canonical experiment still defaults to a fresh run and does not enable any\nbackground or autonomous continuation.\n\nEach run also emits `search-checkpoint-manifest.json`, a smaller companion artifact that lists the\nsnapshot-backed candidate files required for resume. The manifest is additive: it helps maintainers\nand external tooling validate the restore set without opening the full checkpoint, but\n`search-checkpoint.json` remains the source of truth for resumable search state, and both artifacts\ncontinue to describe the same pre-live `post_mutation_search` boundary.\n\nThe current Phase 3 visibility contract still stops at review-gated reporting instead of enabling\nunattended automation. `stagedPatchPolicy` controls the review artifact shape, and\n`continuousPolicy` now reports whether a reviewed continuation would be eligible in the future while\nremaining manual by default in this checked-in experiment. A separate readiness signal now layers\non top of that eligibility and cross-checks the local governed review state in `docs/agents/state.json`\nagainst the machine-readable `ReviewReport` JSON block in `docs/agents/review-report.md`. Matching\nPASS governed artifacts can make an eligible continuation look ready, while mismatch, missing JSON,\nor unreadable governed inputs block readiness deterministically. This remains visibility-only and\ndoes not queue or run anything. Any non-manual continuation mode must still stay stage-only and\nrequire review pass under the repo's deterministic-first guardrails. This sample keeps live\nevaluation disabled and continuation manual by default, so canonical artifacts show blocked\nmanual-mode eligibility, blocked readiness, explicit governed-review consensus, and the current\ngoverned artifact statuses rather than any scheduler, queue, or background follow-on run.\n\nThe canonical AutoAgent report also keeps its top-level `status` as an artifact-readiness signal for\nthe generated report itself. Governed task lifecycle is a separate local visibility signal sourced\nfrom `docs/agents/state.json`, so maintainers can see whether the current bounded slice is still in\nprogress, review-ready, or already closed without mistaking `AutoAgentReport.status` for the slice\nlifecycle.\n\nPhase 3 visibility scope is complete once canonical artifacts expose continuation eligibility,\ncontinuation readiness, governed review consensus, governed task lifecycle, and a reviewed manual\nhandoff summary under the same manual and `report_only` semantics. That completion point still does\nnot authorize unattended orchestration. Any scheduler, queue, background follow-on run, or\nautonomous continuation remains out of scope for Phase 3 and belongs to a later planning track.\n\nThe current bounded Phase 4 implementation step still stops short of execution. It can add an\nadditive governed approval metadata layer derived from the existing reviewed dispatch intent,\ngoverned review consensus, and governed lifecycle signals, but it must remain manual,\nreview-gated, and `report_only`. A governed approval metadata state that is blocked,\nnot-requested, or ready for manual recording only describes what governed approval evidence is\ncurrently visible; it does not authorize approval APIs, schedulers, queues, unattended\ncontinuation, or automatic apply behavior.\n\nIf maintainers want to learn from editor-side debug traces, they must opt in explicitly through\n`includeVsCodeLogs`, `vsCodeLogPaths`, or `externalLogSources`. External logs are still subject to\nthe same secret and path redaction rules as governed run artifacts.",
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
      "taskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
      "taskTitle": "Broaden the checked-in AutoAgent governed bundle to include AGENTS.md",
      "phase": "Implement",
      "qualityGateStatus": "PASS",
      "nextActionSummary": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
      "governedTaskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
      "governedTaskPhase": "Implement",
      "summary": "Not ready for reviewed manual handoff.",
      "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
      "governedTaskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
      "governedTaskPhase": "Implement",
      "contractId": "manual-autoagent-broaden-governed-bundle-coverage-20260414::staged_dispatch_simulation",
      "summary": "Staged dispatch simulation is blocked.",
      "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
      "governedTaskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
      "governedTaskPhase": "Implement",
      "intentId": "manual-autoagent-broaden-governed-bundle-coverage-20260414::staged_dispatch_simulation::reviewed_dispatch_intent",
      "summary": "Reviewed dispatch intent is blocked.",
      "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
      "governedTaskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
      "governedTaskPhase": "Implement",
      "metadataId": "manual-autoagent-broaden-governed-bundle-coverage-20260414::staged_dispatch_simulation::reviewed_dispatch_intent::governed_approval_metadata",
      "summary": "Governed approval metadata is blocked.",
      "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-chat-export.json"
      ],
      "includeTranscriptHistory": true,
      "transcriptHistoryPaths": [
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-transcript-export.jsonl"
      ],
      "includeHandoffHistory": true,
      "handoffHistoryPaths": [
        "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-handoff-export.jsonl"
      ],
      "includeVsCodeLogs": false,
      "vsCodeLogPaths": [],
      "externalLogSources": [
        {
          "id": "chat-history-1",
          "kind": "chat_transcript",
          "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-chat-export.json",
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
          "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-transcript-export.jsonl",
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
          "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-handoff-export.jsonl",
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
    },
    {
      "id": "team-lead-skill",
      "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/skills/team-lead/SKILL.md",
      "kind": "markdown_document",
      "primary": false,
      "mutableRegions": [
        "body"
      ],
      "weight": 1.0
    },
    {
      "id": "agent-operating-guide",
      "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/AGENTS.md",
      "kind": "markdown_document",
      "primary": false,
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
    "completedMutationCount": 2,
    "requestedMutationCount": 2,
    "totalMutationCount": 2,
    "nextMutationIndex": 3,
    "hasRemainingMutations": false,
    "inlineCandidateCount": 1,
    "snapshotBackedCandidateCount": 2,
    "checkpointPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint.json",
    "checkpointManifestPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-checkpoint-manifest.json",
    "manifestSnapshotCandidateCount": 2,
    "manifestRequiredFileCount": 6
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
        "description": "Loosen the manager scope across the manager bundle to prove governance regressions are discarded.",
        "priorityStatus": "neutral",
        "priorityScore": 0.0,
        "bonus": 0.0,
        "penalty": 0.0,
        "matchedPolicyCount": 0,
        "matchedPolicyIds": [],
        "sourceCandidateIds": []
      },
      {
        "plannedIndex": 2,
        "catalogIndex": 2,
        "planToken": "2:weaken-agent-guide-governance",
        "mutationId": "weaken-agent-guide-governance",
        "description": "Weaken the shared AGENTS governance contract to prove the broader governed bundle rejects drift.",
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
    "ledgerNodeCount": 3,
    "searchLedgerPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/search-ledger.json",
    "bestCandidateLineage": [
      "baseline"
    ],
    "finalFrontierCandidateIds": [
      "baseline"
    ],
    "winnerExplanation": {
      "winnerCandidateId": "baseline",
      "comparedCandidateId": "weaken-agent-guide-governance",
      "comparisonMode": "deterministic_ranking",
      "decisiveSignal": "benchmark_score",
      "evidenceBacked": false,
      "summary": "baseline beat weaken-agent-guide-governance on benchmark score (1.0 vs 0.848485).",
      "evidenceSummary": null,
      "rankingComparison": {
        "winnerScore": 1.0,
        "runnerUpScore": 0.848485,
        "scoreDelta": 0.151515,
        "winnerComplexityScore": 8854,
        "runnerUpComplexityScore": 8887,
        "complexityAdvantage": 33,
        "winnerTrajectoryScore": 0.88,
        "runnerUpTrajectoryScore": 0.646429,
        "trajectoryScoreDelta": 0.233571
      },
      "topTrajectorySignals": [
        {
          "signal": "matchedEvidenceRecords",
          "preference": "higher_is_better",
          "winner": 12,
          "runnerUp": 1,
          "advantage": 11.0
        },
        {
          "signal": "attributedSuccessCount",
          "preference": "higher_is_better",
          "winner": 3,
          "runnerUp": 0,
          "advantage": 3.0
        },
        {
          "signal": "actionEfficiency",
          "preference": "higher_is_better",
          "winner": 1.0,
          "runnerUp": 0.333333,
          "advantage": 0.666667
        },
        {
          "signal": "lineageEfficiency",
          "preference": "higher_is_better",
          "winner": 1.0,
          "runnerUp": 0.5,
          "advantage": 0.5
        },
        {
          "signal": "validationBreadth",
          "preference": "higher_is_better",
          "winner": 1.0,
          "runnerUp": 0.857143,
          "advantage": 0.142857
        }
      ],
      "trajectorySummary": "Top trajectory contributors: matchedEvidenceRecords +11, attributedSuccessCount +3, actionEfficiency +0.666667",
      "evidenceComparison": {
        "winnerSourceKinds": {
          "handoff_event": 1,
          "run_report": 7,
          "run_state": 2,
          "transcript_event": 2
        },
        "runnerUpSourceKinds": {
          "run_report": 1
        },
        "winnerStatuses": {
          "done": 1,
          "implement": 1,
          "pass": 2,
          "ready_for_quality_gate": 5,
          "success": 3
        },
        "runnerUpStatuses": {
          "ready_for_quality_gate": 1
        }
      },
      "winner": {
        "candidateId": "baseline",
        "iteration": 0,
        "searchDepth": 0,
        "score": 1.0,
        "complexityScore": 8854,
        "trajectoryScore": 0.88,
        "trajectorySignals": {
          "validationBreadth": 1.0,
          "parentProgress": 0.0,
          "actionEfficiency": 1.0,
          "targetFocus": 1.0,
          "lineageEfficiency": 1.0,
          "matchedEvidenceRecords": 12,
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
          "matchedRecordCount": 12,
          "successCount": 3,
          "warningCount": 0,
          "errorCount": 0,
          "toolErrorCount": 0,
          "externalErrorCount": 0,
          "sourceKindCounts": {
            "handoff_event": 1,
            "run_report": 7,
            "run_state": 2,
            "transcript_event": 2
          },
          "statusCounts": {
            "done": 1,
            "implement": 1,
            "pass": 2,
            "ready_for_quality_gate": 5,
            "success": 3
          }
        }
      },
      "runnerUp": {
        "candidateId": "weaken-agent-guide-governance",
        "iteration": 2,
        "searchDepth": 1,
        "score": 0.848485,
        "complexityScore": 8887,
        "trajectoryScore": 0.646429,
        "trajectorySignals": {
          "validationBreadth": 0.857143,
          "parentProgress": 0.0,
          "actionEfficiency": 0.333333,
          "targetFocus": 1.0,
          "lineageEfficiency": 0.5,
          "matchedEvidenceRecords": 1,
          "attributedSuccessCount": 0,
          "attributedWarningCount": 0,
          "attributedErrorCount": 0,
          "attributedToolErrorCount": 0,
          "attributedExternalErrorCount": 0,
          "evidenceSupport": 0.0,
          "evidenceIssuePenalty": 0.0,
          "reviewedPolicyBonus": 0.0,
          "reviewedPolicyPenalty": 0.0,
          "liveWinnerBoost": 0.0
        },
        "evidence": {
          "matchedRecordCount": 1,
          "successCount": 0,
          "warningCount": 0,
          "errorCount": 0,
          "toolErrorCount": 0,
          "externalErrorCount": 0,
          "sourceKindCounts": {
            "run_report": 1
          },
          "statusCounts": {
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
      "Implement": 1,
      "READY_FOR_QUALITY_GATE": 5,
      "PASS": 3,
      "Done": 1,
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
    "externalSourceCount": 3,
    "governedTraceExportRecordCount": 5,
    "governedTraceExportSourceCount": 3,
    "fixtureExternalLogRecordCount": 0,
    "fixtureExternalSourceCount": 0
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
    "candidatePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/candidates/iteration-00-baseline",
    "changedTargetCount": 0,
    "changedTargets": [],
    "reviewerHints": [],
    "manifestFormat": "candidate_snapshot",
    "includeTargetSnapshots": true,
    "includeDiffSummary": true
  },
  "stagedPatchReviewBundle": {
    "status": "ready_no_changes",
    "bundlePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/staged-patch-review-bundle.json",
    "bundleFound": true,
    "candidateId": "baseline",
    "changedTargetCount": 0,
    "changedTargetIds": [],
    "primaryChangedTargetIds": [],
    "reviewerHints": [],
    "requiredHumanAction": "Review the staged patch bundle and governed artifacts before choosing the next bounded step."
  },
  "provenance": {
    "inputs": {
      "experiment": {
        "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-experiment.md",
        "exists": true,
        "sha256": "135cc204b15cf9388c3a849b431f609395c9774041a21e933c605d9f8c8d0cd5",
        "sizeBytes": 9844
      },
      "benchmark": {
        "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/skills/autoagent-loop/examples/team-lead-benchmark.json",
        "exists": true,
        "sha256": "2664b454cb1b31f700622a347695e91f7adc591965ecea279023f3e0ebd35e15",
        "sizeBytes": 3897
      },
      "mutationCatalog": {
        "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/skills/autoagent-loop/examples/team-lead-mutations.json",
        "exists": true,
        "sha256": "53ce4c8fa10554c264360b4fff3def2eeb2ccd8c9907e132018f50506899d9fe",
        "sizeBytes": 1968
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
          "Implement": 1,
          "READY_FOR_QUALITY_GATE": 5,
          "PASS": 3,
          "Done": 1,
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
        "externalSourceCount": 3,
        "governedTraceExportRecordCount": 5,
        "governedTraceExportSourceCount": 3,
        "fixtureExternalLogRecordCount": 0,
        "fixtureExternalSourceCount": 0
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
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-chat-export.json",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 2,
            "recordKind": "transcript_event"
          },
          {
            "id": "transcript-history-1",
            "kind": "conversation_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-transcript-export.jsonl",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 2,
            "recordKind": "transcript_event"
          },
          {
            "id": "handoff-history-1",
            "kind": "handoff_history",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-handoff-export.jsonl",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 1,
            "recordKind": "handoff_event"
          }
        ],
        "transcriptSources": [
          {
            "id": "chat-history-1",
            "kind": "chat_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-chat-export.json",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 2,
            "recordKind": "transcript_event"
          },
          {
            "id": "transcript-history-1",
            "kind": "conversation_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-transcript-export.jsonl",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 2,
            "recordKind": "transcript_event"
          }
        ],
        "handoffSources": [
          {
            "id": "handoff-history-1",
            "kind": "handoff_history",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-handoff-export.jsonl",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 1,
            "recordKind": "handoff_event"
          }
        ],
        "governedTraceExportSources": [
          {
            "id": "chat-history-1",
            "kind": "chat_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-chat-export.json",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 2,
            "recordKind": "transcript_event"
          },
          {
            "id": "transcript-history-1",
            "kind": "conversation_transcript",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-transcript-export.jsonl",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 2,
            "recordKind": "transcript_event"
          },
          {
            "id": "handoff-history-1",
            "kind": "handoff_history",
            "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-handoff-export.jsonl",
            "sourceOrigin": "governed_run_export",
            "sourceRunId": "20260308-160258",
            "recordCount": 1,
            "recordKind": "handoff_event"
          }
        ],
        "fixtureExternalSources": []
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
        "taskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
        "taskTitle": "Broaden the checked-in AutoAgent governed bundle to include AGENTS.md",
        "phase": "Implement",
        "qualityGateStatus": "PASS",
        "nextActionSummary": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
        "governedTaskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
        "governedTaskPhase": "Implement",
        "summary": "Not ready for reviewed manual handoff.",
        "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
        "governedTaskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
        "governedTaskPhase": "Implement",
        "contractId": "manual-autoagent-broaden-governed-bundle-coverage-20260414::staged_dispatch_simulation",
        "summary": "Staged dispatch simulation is blocked.",
        "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
        "governedTaskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
        "governedTaskPhase": "Implement",
        "intentId": "manual-autoagent-broaden-governed-bundle-coverage-20260414::staged_dispatch_simulation::reviewed_dispatch_intent",
        "summary": "Reviewed dispatch intent is blocked.",
        "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
        "governedTaskId": "manual-autoagent-broaden-governed-bundle-coverage-20260414",
        "governedTaskPhase": "Implement",
        "metadataId": "manual-autoagent-broaden-governed-bundle-coverage-20260414::staged_dispatch_simulation::reviewed_dispatch_intent::governed_approval_metadata",
        "summary": "Governed approval metadata is blocked.",
        "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation.",
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
        "deferredBenchmarkDraftCount": 3,
        "deferredPolicyDraftCount": 2,
        "acceptedBenchmarkDraftIds": [],
        "acceptedPolicyDraftIds": [],
        "summary": "Guarded learning promotion is blocked until continuation and approval gates are ready.",
        "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation."
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
      "stagedPatchBundlePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/staged-patch-review-bundle.json",
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
      "matchedEvidenceRecords": 12,
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
      "matchedRecordCount": 12,
      "errorCount": 0,
      "warningCount": 0,
      "successCount": 3,
      "toolErrorCount": 0,
      "externalErrorCount": 0,
      "sourceKindCounts": {
        "run_state": 2,
        "run_report": 7,
        "transcript_event": 2,
        "handoff_event": 1
      },
      "statusCounts": {
        "implement": 1,
        "ready_for_quality_gate": 5,
        "pass": 2,
        "done": 1,
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
    "passedChecks": 14,
    "totalChecks": 14,
    "complexity": {
      "bodyChars": 8659,
      "toolCount": 6,
      "mcpServerCount": 0,
      "fileCount": 3,
      "score": 8854,
      "perTarget": {
        "team-lead": {
          "bodyChars": 2948,
          "toolCount": 6,
          "mcpServerCount": 0,
          "score": 3098
        },
        "team-lead-skill": {
          "bodyChars": 3535,
          "toolCount": 0,
          "mcpServerCount": 0,
          "score": 3535
        },
        "agent-operating-guide": {
          "bodyChars": 2176,
          "toolCount": 0,
          "mcpServerCount": 0,
          "score": 2176
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
      "matchedEvidenceRecords": 12,
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
      "matchedRecordCount": 12,
      "errorCount": 0,
      "warningCount": 0,
      "successCount": 3,
      "toolErrorCount": 0,
      "externalErrorCount": 0,
      "sourceKindCounts": {
        "run_state": 2,
        "run_report": 7,
        "transcript_event": 2,
        "handoff_event": 1
      },
      "statusCounts": {
        "implement": 1,
        "ready_for_quality_gate": 5,
        "pass": 2,
        "done": 1,
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
    "passedChecks": 14,
    "totalChecks": 14,
    "complexity": {
      "bodyChars": 8659,
      "toolCount": 6,
      "mcpServerCount": 0,
      "fileCount": 3,
      "score": 8854,
      "perTarget": {
        "team-lead": {
          "bodyChars": 2948,
          "toolCount": 6,
          "mcpServerCount": 0,
          "score": 3098
        },
        "team-lead-skill": {
          "bodyChars": 3535,
          "toolCount": 0,
          "mcpServerCount": 0,
          "score": 3535
        },
        "agent-operating-guide": {
          "bodyChars": 2176,
          "toolCount": 0,
          "mcpServerCount": 0,
          "score": 2176
        }
      }
    },
    "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/candidates/iteration-00-baseline"
  },
  "keptCandidates": [
    "baseline"
  ],
  "discardedCandidates": [
    "relax-no-product-code-boundary",
    "weaken-agent-guide-governance"
  ],
  "iterations": [
    {
      "iteration": 0,
      "candidateId": "baseline",
      "parentCandidateId": null,
      "searchDepth": 0,
      "score": 1.0,
      "passedChecks": 14,
      "totalChecks": 14,
      "status": "keep",
      "description": "Baseline target agent",
      "complexity": {
        "bodyChars": 8659,
        "toolCount": 6,
        "mcpServerCount": 0,
        "fileCount": 3,
        "score": 8854,
        "perTarget": {
          "team-lead": {
            "bodyChars": 2948,
            "toolCount": 6,
            "mcpServerCount": 0,
            "score": 3098
          },
          "team-lead-skill": {
            "bodyChars": 3535,
            "toolCount": 0,
            "mcpServerCount": 0,
            "score": 3535
          },
          "agent-operating-guide": {
            "bodyChars": 2176,
            "toolCount": 0,
            "mcpServerCount": 0,
            "score": 2176
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
      "score": 0.818182,
      "trajectoryScore": 0.516429,
      "passedChecks": 12,
      "totalChecks": 14,
      "status": "discard",
      "description": "Loosen the manager scope across the manager bundle to prove governance regressions are discarded.",
      "complexity": {
        "bodyChars": 8646,
        "toolCount": 6,
        "mcpServerCount": 0,
        "fileCount": 3,
        "score": 8841,
        "perTarget": {
          "team-lead": {
            "bodyChars": 2940,
            "toolCount": 6,
            "mcpServerCount": 0,
            "score": 3090
          },
          "team-lead-skill": {
            "bodyChars": 3530,
            "toolCount": 0,
            "mcpServerCount": 0,
            "score": 3530
          },
          "agent-operating-guide": {
            "bodyChars": 2176,
            "toolCount": 0,
            "mcpServerCount": 0,
            "score": 2176
          }
        }
      },
      "touchedTargets": [
        "team-lead",
        "team-lead-skill"
      ]
    },
    {
      "iteration": 2,
      "candidateId": "weaken-agent-guide-governance",
      "parentCandidateId": "baseline",
      "searchDepth": 1,
      "score": 0.848485,
      "trajectoryScore": 0.646429,
      "passedChecks": 12,
      "totalChecks": 14,
      "status": "discard",
      "description": "Weaken the shared AGENTS governance contract to prove the broader governed bundle rejects drift.",
      "complexity": {
        "bodyChars": 8692,
        "toolCount": 6,
        "mcpServerCount": 0,
        "fileCount": 3,
        "score": 8887,
        "perTarget": {
          "team-lead": {
            "bodyChars": 2948,
            "toolCount": 6,
            "mcpServerCount": 0,
            "score": 3098
          },
          "team-lead-skill": {
            "bodyChars": 3535,
            "toolCount": 0,
            "mcpServerCount": 0,
            "score": 3535
          },
          "agent-operating-guide": {
            "bodyChars": 2209,
            "toolCount": 0,
            "mcpServerCount": 0,
            "score": 2209
          }
        }
      },
      "touchedTargets": [
        "agent-operating-guide"
      ]
    }
  ],
  "appliedBestVariant": false,
  "appliedPath": null,
  "appliedPaths": [],
  "traceSummary": {
    "path": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/autoagent-trace.json",
    "eventCount": 8,
    "trajectoryCount": 3,
    "episodeCount": 3,
    "evidenceBackedEpisodeCount": 3,
    "bestTrajectoryScore": 0.88,
    "bestTrajectoryEvidenceMatches": 12,
    "winnerExplanation": {
      "winnerCandidateId": "baseline",
      "comparedCandidateId": "weaken-agent-guide-governance",
      "comparisonMode": "deterministic_ranking",
      "decisiveSignal": "benchmark_score",
      "evidenceBacked": false,
      "summary": "baseline beat weaken-agent-guide-governance on benchmark score (1.0 vs 0.848485).",
      "evidenceSummary": null,
      "rankingComparison": {
        "winnerScore": 1.0,
        "runnerUpScore": 0.848485,
        "scoreDelta": 0.151515,
        "winnerComplexityScore": 8854,
        "runnerUpComplexityScore": 8887,
        "complexityAdvantage": 33,
        "winnerTrajectoryScore": 0.88,
        "runnerUpTrajectoryScore": 0.646429,
        "trajectoryScoreDelta": 0.233571
      },
      "topTrajectorySignals": [
        {
          "signal": "matchedEvidenceRecords",
          "preference": "higher_is_better",
          "winner": 12,
          "runnerUp": 1,
          "advantage": 11.0
        },
        {
          "signal": "attributedSuccessCount",
          "preference": "higher_is_better",
          "winner": 3,
          "runnerUp": 0,
          "advantage": 3.0
        },
        {
          "signal": "actionEfficiency",
          "preference": "higher_is_better",
          "winner": 1.0,
          "runnerUp": 0.333333,
          "advantage": 0.666667
        },
        {
          "signal": "lineageEfficiency",
          "preference": "higher_is_better",
          "winner": 1.0,
          "runnerUp": 0.5,
          "advantage": 0.5
        },
        {
          "signal": "validationBreadth",
          "preference": "higher_is_better",
          "winner": 1.0,
          "runnerUp": 0.857143,
          "advantage": 0.142857
        }
      ],
      "trajectorySummary": "Top trajectory contributors: matchedEvidenceRecords +11, attributedSuccessCount +3, actionEfficiency +0.666667",
      "evidenceComparison": {
        "winnerSourceKinds": {
          "handoff_event": 1,
          "run_report": 7,
          "run_state": 2,
          "transcript_event": 2
        },
        "runnerUpSourceKinds": {
          "run_report": 1
        },
        "winnerStatuses": {
          "done": 1,
          "implement": 1,
          "pass": 2,
          "ready_for_quality_gate": 5,
          "success": 3
        },
        "runnerUpStatuses": {
          "ready_for_quality_gate": 1
        }
      },
      "winner": {
        "candidateId": "baseline",
        "iteration": 0,
        "searchDepth": 0,
        "score": 1.0,
        "complexityScore": 8854,
        "trajectoryScore": 0.88,
        "trajectorySignals": {
          "validationBreadth": 1.0,
          "parentProgress": 0.0,
          "actionEfficiency": 1.0,
          "targetFocus": 1.0,
          "lineageEfficiency": 1.0,
          "matchedEvidenceRecords": 12,
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
          "matchedRecordCount": 12,
          "successCount": 3,
          "warningCount": 0,
          "errorCount": 0,
          "toolErrorCount": 0,
          "externalErrorCount": 0,
          "sourceKindCounts": {
            "handoff_event": 1,
            "run_report": 7,
            "run_state": 2,
            "transcript_event": 2
          },
          "statusCounts": {
            "done": 1,
            "implement": 1,
            "pass": 2,
            "ready_for_quality_gate": 5,
            "success": 3
          }
        }
      },
      "runnerUp": {
        "candidateId": "weaken-agent-guide-governance",
        "iteration": 2,
        "searchDepth": 1,
        "score": 0.848485,
        "complexityScore": 8887,
        "trajectoryScore": 0.646429,
        "trajectorySignals": {
          "validationBreadth": 0.857143,
          "parentProgress": 0.0,
          "actionEfficiency": 0.333333,
          "targetFocus": 1.0,
          "lineageEfficiency": 0.5,
          "matchedEvidenceRecords": 1,
          "attributedSuccessCount": 0,
          "attributedWarningCount": 0,
          "attributedErrorCount": 0,
          "attributedToolErrorCount": 0,
          "attributedExternalErrorCount": 0,
          "evidenceSupport": 0.0,
          "evidenceIssuePenalty": 0.0,
          "reviewedPolicyBonus": 0.0,
          "reviewedPolicyPenalty": 0.0,
          "liveWinnerBoost": 0.0
        },
        "evidence": {
          "matchedRecordCount": 1,
          "successCount": 0,
          "warningCount": 0,
          "errorCount": 0,
          "toolErrorCount": 0,
          "externalErrorCount": 0,
          "sourceKindCounts": {
            "run_report": 1
          },
          "statusCounts": {
            "ready_for_quality_gate": 1
          }
        }
      },
      "liveEvaluation": null
    }
  },
  "learningSummary": {
    "mode": "shadow_only",
    "episodeCount": 3,
    "evidenceBackedEpisodeCount": 3,
    "reasoningPathSignal": {
      "name": "reasoningPathEfficiencyScore",
      "sourceBackedPathCount": 3,
      "transcriptBackedPathCount": 2,
      "handoffBackedPathCount": 1,
      "bestObservedScore": 0.795833
    },
    "topObservedPaths": [
      {
        "episodeId": "candidate-episode-baseline",
        "trajectoryId": "candidate-trajectory-baseline",
        "candidateId": "baseline",
        "classification": "successful_path",
        "learningScore": 0.839583,
        "qualityScore": 0.86875,
        "efficiencyScore": 0.795833,
        "reasoningPathEfficiencyScore": 0.795833,
        "terminalStatus": "success",
        "matchedRecordCount": 12,
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
          "matchedRecordCount": 12,
          "sourceKinds": [
            "handoff_event",
            "run_report",
            "run_state",
            "transcript_event"
          ],
          "sourceOrigins": [
            "governed_run_export"
          ],
          "sourceOriginCounts": {
            "governed_run_export": 3
          },
          "sourceScopes": [
            "current_artifact",
            "run_snapshot",
            "chat_transcript",
            "conversation_transcript",
            "handoff_history"
          ],
          "sourceIds": [
            "chat-history-1",
            "transcript-history-1",
            "handoff-history-1"
          ],
          "governedRunIds": [
            "20260308-160258"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 1,
          "transcriptBacked": true,
          "handoffBacked": true
        },
        "factors": {
          "benchmarkQuality": 1.0,
          "evidenceQuality": 0.625,
          "terminalOutcomeScore": 1.0,
          "actionCount": 0,
          "searchDepth": 0,
          "stepCount": 12,
          "handoffCount": 1,
          "handoffEfficiency": 0.666667,
          "toolSequenceLength": 3,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.795833
        },
        "selectedAsBest": true
      },
      {
        "episodeId": "candidate-episode-weaken-agent-guide-governance",
        "trajectoryId": "candidate-trajectory-weaken-agent-guide-governance",
        "candidateId": "weaken-agent-guide-governance",
        "classification": "observed_path",
        "learningScore": 0.689424,
        "qualityScore": 0.676818,
        "efficiencyScore": 0.708333,
        "reasoningPathEfficiencyScore": 0.708333,
        "terminalStatus": "READY_FOR_QUALITY_GATE",
        "matchedRecordCount": 1,
        "handoffCount": 0,
        "searchDepth": 1,
        "actionCount": 2,
        "sourceKinds": [
          "run_report"
        ],
        "toolNames": [],
        "toolSequence": [],
        "provenance": {
          "matchedRecordCount": 1,
          "sourceKinds": [
            "run_report"
          ],
          "sourceOrigins": [],
          "sourceOriginCounts": {},
          "sourceScopes": [
            "run_snapshot"
          ],
          "sourceIds": [],
          "governedRunIds": [],
          "transcriptRecordCount": 0,
          "handoffRecordCount": 0,
          "transcriptBacked": false,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.848485,
          "evidenceQuality": 0.5,
          "terminalOutcomeScore": 0.6,
          "actionCount": 2,
          "searchDepth": 1,
          "stepCount": 1,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 0,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.708333
        },
        "selectedAsBest": false
      },
      {
        "episodeId": "candidate-episode-relax-no-product-code-boundary",
        "trajectoryId": "candidate-trajectory-relax-no-product-code-boundary",
        "candidateId": "relax-no-product-code-boundary",
        "classification": "failure_path",
        "learningScore": 0.464242,
        "qualityScore": 0.368182,
        "efficiencyScore": 0.608333,
        "reasoningPathEfficiencyScore": 0.608333,
        "terminalStatus": "error",
        "matchedRecordCount": 3,
        "handoffCount": 0,
        "searchDepth": 1,
        "actionCount": 2,
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
          "sourceOrigins": [
            "governed_run_export"
          ],
          "sourceOriginCounts": {
            "governed_run_export": 2
          },
          "sourceScopes": [
            "run_snapshot",
            "chat_transcript",
            "conversation_transcript"
          ],
          "sourceIds": [
            "chat-history-1",
            "transcript-history-1"
          ],
          "governedRunIds": [
            "20260308-160258"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 0,
          "transcriptBacked": true,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.818182,
          "evidenceQuality": 0.0,
          "terminalOutcomeScore": 0.0,
          "actionCount": 2,
          "searchDepth": 1,
          "stepCount": 3,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 2,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.608333
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
        "learningScore": 0.839583,
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
        "reasoningPathEfficiencyScore": 0.795833,
        "provenance": {
          "matchedRecordCount": 12,
          "sourceKinds": [
            "handoff_event",
            "run_report",
            "run_state",
            "transcript_event"
          ],
          "sourceOrigins": [
            "governed_run_export"
          ],
          "sourceOriginCounts": {
            "governed_run_export": 3
          },
          "sourceScopes": [
            "current_artifact",
            "run_snapshot",
            "chat_transcript",
            "conversation_transcript",
            "handoff_history"
          ],
          "sourceIds": [
            "chat-history-1",
            "transcript-history-1",
            "handoff-history-1"
          ],
          "governedRunIds": [
            "20260308-160258"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 1,
          "transcriptBacked": true,
          "handoffBacked": true
        },
        "factors": {
          "benchmarkQuality": 1.0,
          "evidenceQuality": 0.625,
          "terminalOutcomeScore": 1.0,
          "actionCount": 0,
          "searchDepth": 0,
          "stepCount": 12,
          "handoffCount": 1,
          "handoffEfficiency": 0.666667,
          "toolSequenceLength": 3,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.795833
        },
        "rationale": "Preserve the observed successful path pattern."
      },
      {
        "suggestionId": "episode-benchmark-02",
        "kind": "episode_success_guard",
        "classification": "observed_path",
        "observedCount": 1,
        "learningScore": 0.689424,
        "exampleCandidateIds": [
          "weaken-agent-guide-governance"
        ],
        "sourceKinds": [
          "run_report"
        ],
        "handoffCount": 0,
        "toolNames": [],
        "terminalStatus": "READY_FOR_QUALITY_GATE",
        "reasoningPathEfficiencyScore": 0.708333,
        "provenance": {
          "matchedRecordCount": 1,
          "sourceKinds": [
            "run_report"
          ],
          "sourceOrigins": [],
          "sourceOriginCounts": {},
          "sourceScopes": [
            "run_snapshot"
          ],
          "sourceIds": [],
          "governedRunIds": [],
          "transcriptRecordCount": 0,
          "handoffRecordCount": 0,
          "transcriptBacked": false,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.848485,
          "evidenceQuality": 0.5,
          "terminalOutcomeScore": 0.6,
          "actionCount": 2,
          "searchDepth": 1,
          "stepCount": 1,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 0,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.708333
        },
        "rationale": "Preserve the observed successful path pattern."
      },
      {
        "suggestionId": "episode-benchmark-03",
        "kind": "episode_failure_regression",
        "classification": "failure_path",
        "observedCount": 1,
        "learningScore": 0.464242,
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
        "reasoningPathEfficiencyScore": 0.608333,
        "provenance": {
          "matchedRecordCount": 3,
          "sourceKinds": [
            "run_report",
            "transcript_event"
          ],
          "sourceOrigins": [
            "governed_run_export"
          ],
          "sourceOriginCounts": {
            "governed_run_export": 2
          },
          "sourceScopes": [
            "run_snapshot",
            "chat_transcript",
            "conversation_transcript"
          ],
          "sourceIds": [
            "chat-history-1",
            "transcript-history-1"
          ],
          "governedRunIds": [
            "20260308-160258"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 0,
          "transcriptBacked": true,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.818182,
          "evidenceQuality": 0.0,
          "terminalOutcomeScore": 0.0,
          "actionCount": 2,
          "searchDepth": 1,
          "stepCount": 3,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 2,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.608333
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
        "learningScore": 0.839583,
        "reasoningPathEfficiencyScore": 0.795833,
        "provenance": {
          "matchedRecordCount": 12,
          "sourceKinds": [
            "handoff_event",
            "run_report",
            "run_state",
            "transcript_event"
          ],
          "sourceOrigins": [
            "governed_run_export"
          ],
          "sourceOriginCounts": {
            "governed_run_export": 3
          },
          "sourceScopes": [
            "current_artifact",
            "run_snapshot",
            "chat_transcript",
            "conversation_transcript",
            "handoff_history"
          ],
          "sourceIds": [
            "chat-history-1",
            "transcript-history-1",
            "handoff-history-1"
          ],
          "governedRunIds": [
            "20260308-160258"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 1,
          "transcriptBacked": true,
          "handoffBacked": true
        },
        "factors": {
          "benchmarkQuality": 1.0,
          "evidenceQuality": 0.625,
          "terminalOutcomeScore": 1.0,
          "actionCount": 0,
          "searchDepth": 0,
          "stepCount": 12,
          "handoffCount": 1,
          "handoffEfficiency": 0.666667,
          "toolSequenceLength": 3,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.795833
        },
        "rationale": "Promote this observed successful path as a future mutation seed."
      },
      {
        "seedId": "episode-mutation-seed-02",
        "kind": "investigate_observed_path",
        "candidateId": "weaken-agent-guide-governance",
        "episodeId": "candidate-episode-weaken-agent-guide-governance",
        "sourceMutationId": "weaken-agent-guide-governance",
        "sourceKinds": [
          "run_report"
        ],
        "handoffCount": 0,
        "toolNames": [],
        "targetSearchDepth": 1,
        "targetActionCount": 2,
        "learningScore": 0.689424,
        "reasoningPathEfficiencyScore": 0.708333,
        "provenance": {
          "matchedRecordCount": 1,
          "sourceKinds": [
            "run_report"
          ],
          "sourceOrigins": [],
          "sourceOriginCounts": {},
          "sourceScopes": [
            "run_snapshot"
          ],
          "sourceIds": [],
          "governedRunIds": [],
          "transcriptRecordCount": 0,
          "handoffRecordCount": 0,
          "transcriptBacked": false,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.848485,
          "evidenceQuality": 0.5,
          "terminalOutcomeScore": 0.6,
          "actionCount": 2,
          "searchDepth": 1,
          "stepCount": 1,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 0,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.708333
        },
        "rationale": "Investigate this observed path before turning it into a mutation."
      },
      {
        "seedId": "episode-mutation-seed-03",
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
        "targetActionCount": 2,
        "learningScore": 0.464242,
        "reasoningPathEfficiencyScore": 0.608333,
        "provenance": {
          "matchedRecordCount": 3,
          "sourceKinds": [
            "run_report",
            "transcript_event"
          ],
          "sourceOrigins": [
            "governed_run_export"
          ],
          "sourceOriginCounts": {
            "governed_run_export": 2
          },
          "sourceScopes": [
            "run_snapshot",
            "chat_transcript",
            "conversation_transcript"
          ],
          "sourceIds": [
            "chat-history-1",
            "transcript-history-1"
          ],
          "governedRunIds": [
            "20260308-160258"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 0,
          "transcriptBacked": true,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.818182,
          "evidenceQuality": 0.0,
          "terminalOutcomeScore": 0.0,
          "actionCount": 2,
          "searchDepth": 1,
          "stepCount": 3,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 2,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.608333
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
        "learningScore": 0.839583,
        "reasoningPathEfficiencyScore": 0.795833,
        "provenance": {
          "matchedRecordCount": 12,
          "sourceKinds": [
            "handoff_event",
            "run_report",
            "run_state",
            "transcript_event"
          ],
          "sourceOrigins": [
            "governed_run_export"
          ],
          "sourceOriginCounts": {
            "governed_run_export": 3
          },
          "sourceScopes": [
            "current_artifact",
            "run_snapshot",
            "chat_transcript",
            "conversation_transcript",
            "handoff_history"
          ],
          "sourceIds": [
            "chat-history-1",
            "transcript-history-1",
            "handoff-history-1"
          ],
          "governedRunIds": [
            "20260308-160258"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 1,
          "transcriptBacked": true,
          "handoffBacked": true
        },
        "factors": {
          "benchmarkQuality": 1.0,
          "evidenceQuality": 0.625,
          "terminalOutcomeScore": 1.0,
          "actionCount": 0,
          "searchDepth": 0,
          "stepCount": 12,
          "handoffCount": 1,
          "handoffEfficiency": 0.666667,
          "toolSequenceLength": 3,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.795833
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
          "maxActionCount": 2
        },
        "learningScore": 0.464242,
        "reasoningPathEfficiencyScore": 0.608333,
        "provenance": {
          "matchedRecordCount": 3,
          "sourceKinds": [
            "run_report",
            "transcript_event"
          ],
          "sourceOrigins": [
            "governed_run_export"
          ],
          "sourceOriginCounts": {
            "governed_run_export": 2
          },
          "sourceScopes": [
            "run_snapshot",
            "chat_transcript",
            "conversation_transcript"
          ],
          "sourceIds": [
            "chat-history-1",
            "transcript-history-1"
          ],
          "governedRunIds": [
            "20260308-160258"
          ],
          "transcriptRecordCount": 2,
          "handoffRecordCount": 0,
          "transcriptBacked": true,
          "handoffBacked": false
        },
        "factors": {
          "benchmarkQuality": 0.818182,
          "evidenceQuality": 0.0,
          "terminalOutcomeScore": 0.0,
          "actionCount": 2,
          "searchDepth": 1,
          "stepCount": 3,
          "handoffCount": 0,
          "handoffEfficiency": 1.0,
          "toolSequenceLength": 2,
          "repeatedToolCount": 0,
          "toolChurnScore": 1.0,
          "reasoningPathEfficiencyScore": 0.608333
        },
        "rationale": "Escalate or branch away when this observed tool path ends in failure or warning."
      }
    ]
  },
  "learningArtifacts": {
    "mode": "review_only",
    "benchmarkDraftCount": 3,
    "mutationDraftCount": 3,
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
    "deferredBenchmarkDraftCount": 3,
    "deferredPolicyDraftCount": 2,
    "acceptedBenchmarkDraftIds": [],
    "acceptedPolicyDraftIds": [],
    "summary": "Guarded learning promotion is blocked until continuation and approval gates are ready.",
    "recommendedAction": "Open the next bounded AutoAgent slice for broader governed bundle coverage or reviewer workflow polish before considering any unattended continuation."
  },
  "learningPromotionAudit": {
    "status": "ready",
    "artifactPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/learning-promotion-audit.json",
    "artifactFound": true,
    "promotionSourceMode": "manual_review",
    "reviewedBenchmarkDraftCount": 1,
    "acceptedBenchmarkDraftCount": 1,
    "rejectedBenchmarkDraftCount": 0,
    "deferredBenchmarkDraftCount": 0,
    "reviewedMutationDraftCount": 1,
    "acceptedMutationDraftCount": 1,
    "rejectedMutationDraftCount": 0,
    "deferredMutationDraftCount": 0,
    "reviewedPolicyDraftCount": 1,
    "acceptedPolicyDraftCount": 1,
    "rejectedPolicyDraftCount": 0,
    "deferredPolicyDraftCount": 0,
    "reviewerOverrideCount": 1,
    "benchmarkReviewerOverrideCount": 0,
    "mutationReviewerOverrideCount": 0,
    "policyReviewerOverrideCount": 1,
    "blockedFactorCounts": {
      "observedCount": 1
    },
    "benchmarkBlockedFactorCounts": {},
    "mutationBlockedFactorCounts": {},
    "policyBlockedFactorCounts": {
      "observedCount": 1
    }
  },
  "reviewedContinuationPackage": {
    "status": "ready",
    "bundlePath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-continuation-bundle.json",
    "bundleFound": true,
    "acceptedBenchmarkDraftCount": 1,
    "acceptedMutationDraftCount": 1,
    "acceptedPolicyDraftCount": 1,
    "acceptedTotalCount": 3,
    "traceSourceOrigins": [
      "governed_run_export"
    ],
    "governedTraceExportRunIds": [
      "20260308-160258"
    ],
    "manualDispatchStatus": "ready_for_manual_dispatch",
    "manualDispatchPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/manual-dispatch.generated.json",
    "manualDispatchFound": true,
    "manualDispatchBlockedReasons": [],
    "requiredHumanAction": "Review the generated follow-on experiment and launch it manually with the provided command.",
    "followOnExperimentPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-continuation-experiment.generated.md",
    "launchCommand": "py -3 \"D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/skills/autoagent-loop/scripts/autoagent_loop.py\" --experiment \"D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/reviewed-continuation-experiment.generated.md\" --output-root \"D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs\" --report \"D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-report.md\" --results \"D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-results.tsv\" --evidence \"D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/autoagent-evidence.json\""
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
    "stagedPatchBundle": {
      "requestedPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/staged-patch-review-bundle.json",
      "actualPath": "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/staged-patch-review-bundle.json",
      "fallbackUsed": false,
      "warning": null
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
