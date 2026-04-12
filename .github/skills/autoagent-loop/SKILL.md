---
name: autoagent-loop
description: >
  Repo-native AutoAgent loop for optimizing GitHub Copilot agent-system targets with deterministic
  benchmarks, mutation catalogs, keep-or-discard scoring, and governed docs artifacts. Use when the
  user wants self-optimization, harness benchmarking, or an AutoAgent-style overnight loop adapted
  to this repository.
license: See repository LICENSE
metadata:
  owner: "multi-agent-swe-team"
  version: "0.1"
  spec: "agentskills.io"
---

# AutoAgent Loop

## When to use
- A user wants AutoAgent-style harness optimization for `.github/agents/*.agent.md` files or closely related markdown-based agent-system targets in this repo.
- You need a deterministic benchmark loop instead of ad hoc prompt edits.
- You want a run ledger, keep/discard history, and a report artifact that mirrors into the active run.
- You want to benchmark prompt, tool, routing, or shared-guidance mutations without rewriting the whole repo manually.

## When NOT to use
- Implementing unrelated product features.
- Running live cloud deployments or remote experiments with real secrets.
- Pretending this loop is a free-form code-editing model trainer. In this phase it optimizes governed markdown agent-system targets.
- Replacing the repo's existing Team Lead or quality-gate workflow.

## Inputs (source-of-truth order)
1. `docs/agents/autoagent-experiment.md`
2. The target bundle referenced by the experiment (`optimizationTargets`, or the legacy `targetAgentPath` fallback)
3. The benchmark JSON and mutation catalog JSON referenced by the experiment
4. `AGENTS.md`
5. `.github/copilot-instructions.md`

## Outputs
- `docs/agents/autoagent-report.md`
- `docs/agents/autoagent-results.tsv`
- `generated/autoagent-runs/<experiment>/autoagent-trace.json`
- candidate artifacts under `generated/autoagent-runs/`
- winner-selection rationale in the report, trace summary, and search ledger

## Non-negotiable rules
- The experiment markdown is the equivalent of AutoAgent's `program.md`; humans edit direction there.
- The target bundle is the harness under test. In the legacy schema, the harness is a single `.agent.md` file.
- Keep if weighted benchmark score improves.
- If weighted benchmark score ties, prefer the lower complexity candidate.
- If score and complexity both tie, prefer the higher trajectory score derived from benchmark breadth, mutation efficiency, lineage depth, and any candidate-specific hook, session-audit, transcript, or external-log evidence captured by the evidence policy.
- When trajectory signals decide the winner, emit the exact contributing signal deltas plus evidence-source and status comparisons in the winner rationale artifacts.
- Transcript evidence should normalize both direct and nested `message`, `result`, and `tool_calls` metadata so Copilot-style JSONL exports can contribute tool and status signals during tie-breaking.
- Use `evidencePolicy.includeChatHistory` with `chatHistoryPaths` for exported chat-history files and `includeTranscriptHistory` with `transcriptHistoryPaths` for exported transcript files. These aliases feed the same governed evidence path as `externalLogSources` while accepting routine `.json` and `.jsonl` conversation exports.
- When transcript records expose explicit nested candidate ids, use those exact ids for evidence attribution before falling back to broader text matching so branched candidates are not conflated by shared mutation ids.
- Prefer deterministic checks over live-model calls.
- Do not mutate the source agent unless the user requests `--apply-best`.
- Mirror any `docs/agents/` artifacts into the current run snapshot.
- Never write secrets or real environment values into experiments, benchmarks, or reports.
- Guarded auto-promotion in this phase may only stage a generated review manifest for benchmark or policy drafts after continuation eligibility, reviewed handoff, and governed approval metadata all say the run is still manual and ready for review.
- Phase 1 only supports markdown documents that use the repo's existing frontmatter-plus-body contract.

## Procedure
### Step 1 - Preflight
1. Confirm the experiment path and target agent.
2. Run the baseline candidate first.
3. Create a generated run folder under `generated/autoagent-runs/`.

### Step 2 - Evaluate the baseline
1. Load the target bundle.
2. Evaluate it against the deterministic benchmark.
3. Record iteration `0` as the baseline in `docs/agents/autoagent-results.tsv`, including the computed trajectory score.

### Step 3 - Iterate through candidate mutations
1. Apply one mutation at a time to the current best candidate bundle.
2. Re-evaluate the mutated candidate.
3. Mark the mutation as `keep`, `discard`, or `skip`.
4. Persist the candidate target bundle and evaluation JSON into the generated run folder.

### Step 4 - Finalize
1. Optionally apply the best candidate with `--apply-best`.
2. Emit `autoagent-trace.json` under the generated run root with the optimization trajectory, per-candidate action sequences, validation attempts, evidence-backed ranking signals, session-audit or transcript context when available, explicit winner rationale with top trajectory contributors, and artifact refs.
  The trace should also preserve a candidate-scoped episode view derived from attributed session or transcript evidence so future learning slices can mine observable action patterns instead of only aggregate counts.
  Any benchmark, mutation, or policy candidates mined from those episodes must remain advisory in shadow mode until a later reviewed automation slice explicitly promotes them.
  Review-only slices may persist those advisory suggestions as generated draft benchmark fragments, draft mutation catalog entries, or draft policy catalog entries under the run root, but the active experiment must never consume those generated drafts automatically.
  When the continuation and approval gates are fully ready, the loop may also stage a generated `guarded-learning-review.generated.json` manifest that pre-fills benchmark and policy draft decisions for maintainer review; this artifact is still advisory and must not be imported automatically.
  Promotion of generated drafts is a separate governed step. Use `--import-learning-review <review.json>` to merge accepted drafts, allow accepted benchmark fragments to either carry reviewer-supplied executable checks or import a generated `episode_observation_guard` suggestion directly, and only clone mutation drafts automatically when the draft carries a source mutation reference or the review manifest supplies a full mutation payload.
  Accepted policy drafts merge into a separate `reviewed-policies.json` artifact and remain review artifacts only; the active experiment still does not consume them automatically.
  Start from `.github/skills/autoagent-loop/examples/learning-review-template.json` when preparing that review manifest.
3. Write `docs/agents/autoagent-report.md` with one `AutoAgentReport` JSON block and a concise winner rationale section that includes the top trajectory contributors when available.
4. Snapshot the report and results into the active run folder.

## Failure handling
Blocker categories:
- `missing_experiment`
- `missing_target_agent`
- `invalid_benchmark`
- `invalid_mutation_catalog`
- `artifact_write_failure`

Retry budget:
- 1 pass for parseable experiment or benchmark issues
- 1 pass for docs artifact fallback
- otherwise `BLOCKED` with concrete next steps

## Required commands
- Deterministic run:
  `py -3 scripts/run_autoagent_loop.py --experiment docs/agents/autoagent-experiment.md`

## Required output artifact
### Write/update: `docs/agents/autoagent-report.md`
- Short human summary
- Exactly one fenced JSON object of type `AutoAgentReport`
