---
name: onboarding-bundle-optimization
description: >
  Exercise the Phase 1 AutoAgent target bundle model against a primary agent and a shared guidance
  document.
optimizationTargets:
  - id: primary-agent
    path: onboarding-helper.agent.md
    kind: agent_profile
    primary: true
    mutableRegions:
      - body
      - frontmatter.tools
  - id: shared-guidance
    path: shared-guidance.md
    kind: markdown_document
    mutableRegions:
      - body
benchmarkPath: bundle-benchmark.json
mutationCatalogPath: bundle-mutations.json
maxIterations: 3
applyBestCandidate: false
stageForReview: true
evaluationMode:
  deterministic: true
  live: false
continuousPolicy:
  mode: manual
candidatePolicy:
  keepStrategy: score-then-simpler
---

# AutoAgent Experiment

Optimize the onboarding target bundle while preserving a narrow tool surface.

- the primary onboarding agent should redirect deeper requests to `team-lead`
- the shared guidance document should point to `docs/agents/task-spec.md`
- complexity regressions should be discarded when they lower score
