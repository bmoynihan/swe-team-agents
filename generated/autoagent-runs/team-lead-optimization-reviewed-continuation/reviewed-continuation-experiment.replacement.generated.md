---
name: team-lead-optimization-reviewed-continuation-replacement-mutation
description: "Generated replacement-mutation experiment for team-lead-optimization-reviewed-continuation. Manual launch only."
optimizationTargets:
  - id: team-lead
    path: "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/.github/agents/team-lead.agent.md"
    kind: agent_profile
    primary: true
    mutableRegions:
      - body
    weight: 1.0
benchmarkPath: "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization-reviewed-continuation/reviewed-benchmark.json"
mutationCatalogPath: "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization-reviewed-continuation/reviewed-mutations-replacement.json"
maxIterations: 1
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
  enabled: false
  mode: manual
  scheduleCron: null
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
  enabled: true
  runsDir: "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs"
  currentFiles:
    - state.json
    - patch-report.md
    - test-report.md
    - review-report.md
  reportFiles:
    - state.json
    - patch-report.md
    - test-report.md
    - review-report.md
    - autoagent-report.md
  includeCurrentArtifacts: true
  includeHookAudit: true
  includeChatHistory: true
  chatHistoryPaths:
    - "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-chat-export.json"
  includeTranscriptHistory: true
  transcriptHistoryPaths:
    - "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-transcript-export.jsonl"
  includeHandoffHistory: true
  handoffHistoryPaths:
    - "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-handoff-export.jsonl"
  includeVsCodeLogs: false
  vsCodeLogPaths: []
  externalLogSources:
    - id: chat-history-1
      kind: chat_transcript
      path: "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-chat-export.json"
      format: json
      optional: true
      includeLinePatterns: []
      excludeLinePatterns: []
      maxRecords: 200
      maxLineLength: 400
    - id: transcript-history-1
      kind: conversation_transcript
      path: "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-transcript-export.jsonl"
      format: jsonl
      optional: true
      includeLinePatterns: []
      excludeLinePatterns: []
      maxRecords: 200
      maxLineLength: 400
    - id: handoff-history-1
      kind: handoff_history
      path: "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/docs/agents/runs/20260308-160258/copilot-handoff-export.jsonl"
      format: jsonl
      optional: true
      includeLinePatterns: []
      excludeLinePatterns: []
      maxRecords: 200
      maxLineLength: 400
  maxRuns: 5
  maxRecordsPerFile: 200
  maxExternalLogLineLength: 400
  redactSensitive: true
  allowExternalPaths: false
reviewedPolicyRuntime:
  enabled: true
  artifactPath: "D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization-reviewed-continuation/reviewed-policies.json"
  preferredSequenceBonus: 0.04
  escalationPenalty: 0.05
---

Generated from an additive replacement mutation catalog. Launch this experiment manually only after confirming the governed artifacts and preserving the historical review manifest at D:/Aon_Projects/00_VSC_Github_Databricks_Coding_Agent/swe_team_agents_template - Rev4/generated/autoagent-runs/team-lead-optimization/manual-learning-review.json.
