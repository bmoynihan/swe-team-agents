# Research Report

- Phase 5A already provided the evidence boundary required for bounded learning work: explicit handoff-history ingestion, deterministic attribution, and review-only episode summaries with `handoffCount`.
- The smallest safe Phase 5B implementation slice was therefore not new evidence ingestion but explicit advisory weighting: terminal outcome, handoff efficiency, and repeated-tool churn, all derived from the existing episode summaries and trajectory metadata.
- The runtime now exposes those factor terms in the shadow-learning score and carries them forward into review-only learning artifacts so maintainers can inspect why a path scored the way it did.
- Deterministic direct tests and full runner-file coverage show the refinement stays shadow-only, offline, and review-only, so the next roadmap step can move toward review-only promotion rather than reopening this metric baseline.

```json
{
	"type": "ResearchReport",
	"status": "COMPLETE",
	"goal": "Confirm that the Phase 5B planning contract could be implemented as a bounded advisory scoring refinement without widening evidence sources or runtime authority.",
	"question": "Once the bounded path-quality planning contract exists, what is the next smallest safe implementation slice that moves AutoAgent toward straighter reasoning-path review without skipping governance?",
	"findings": [
		{
			"id": "F1",
			"summary": "Phase 5A already supplied the evidence boundary needed for bounded path-quality refinement.",
			"evidence": [
				"Candidate episodes already expose matchedRecordCount, stepCount, statusCounts, terminalStatus, handoffCount, and toolSequence.",
				"Trajectories already expose actionSequence and searchDepth.",
				"Review-only learning artifacts already serialize advisory scores without changing live authority."
			]
		},
		{
			"id": "F2",
			"summary": "The smallest safe runtime change was to refine advisory scoring with explicit factor terms, not to add new evidence inputs.",
			"evidence": [
				"The runtime now derives terminalOutcomeScore from episode classification, handoffEfficiency from handoffCount, and toolChurnScore from repeated adjacent tool usage.",
				"The updated qualityScore and efficiencyScore formulas still rely only on bounded, deterministic episode and trajectory summaries.",
				"Benchmark-only episodes keep benchmark quality stable when no matched evidence exists."
			]
		},
		{
			"id": "F3",
			"summary": "Review-only learning artifacts can now explain advisory path-quality decisions at the factor level.",
			"evidence": [
				"topObservedPaths now carries factor summaries alongside learningScore, qualityScore, and efficiencyScore.",
				"Benchmark, mutation, and policy candidates now retain the same factor summaries.",
				"Generated review-only draft payloads now serialize factorSummary fields for maintainer inspection."
			]
		},
		{
			"id": "F4",
			"summary": "The refinement remains bounded enough to keep the broader roadmap unchanged.",
			"evidence": [
				"The implementation does not change live ranking authority, mutation ordering authority, reviewed-policy runtime loading, apply-best, or continuation readiness.",
				"Validation stayed deterministic and offline via targeted pytest coverage and the full runner file.",
				"Later roadmap phases still begin with review-only promotion and provenance-backed learning review before any broader runtime expansion."
			]
		}
	],
	"roadmap": [
		{
			"id": "Phase5A",
			"title": "Handoff-Aware Trace Source Contract",
			"goal": "Add explicit handoff-history evidence inputs and deterministic candidate attribution across chat, tool, and handoff records.",
			"status": "completed",
			"scope": [
				"Explicit handoff-history source family under evidencePolicy",
				"Deterministic attribution hierarchy favoring explicit candidate ids and lineage refs",
				"Review-only path summaries with handoff count, tool sequence, and terminal status"
			],
			"entryCriteria": [
				"Current evidence redaction and opt-in controls stay unchanged",
				"No autonomous behavior is introduced"
			],
			"exitCriteria": [
				"Focused and full deterministic runner tests pass",
				"Handoff-aware traces remain advisory only"
			],
			"stillOutOfScope": [
				"Auto-import",
				"Dynamic replanning",
				"Autonomous execution"
			]
		},
		{
			"id": "Phase5B",
			"title": "Bounded Advisory Path-Quality Factors",
			"goal": "Implement bounded advisory path-quality factors from existing episode summaries so straighter reasoning paths can be reviewed without widening authority.",
			"status": "completed",
			"scope": [
				"Explicit terminal-outcome scoring for advisory qualityScore",
				"Explicit handoff-efficiency and repeated-tool-churn terms for advisory efficiencyScore",
				"Review-only factor summaries across learning summaries and draft payloads"
			],
			"entryCriteria": [
				"Phase5A attribution is reliable for branched candidates",
				"The runtime already exposes bounded episode summaries and advisory score fields"
			],
			"exitCriteria": [
				"Direct score tests prove benchmark-only stability and degraded warning or handoff-tool-churn behavior",
				"The full deterministic runner file passes with factor-summary serialization coverage",
				"The implementation remains shadow-only and review-only"
			],
			"stillOutOfScope": [
				"New evidence sources",
				"Live ranking authority changes",
				"Automatic policy activation",
				"Autonomous continuation"
			]
		},
		{
			"id": "Phase5C",
			"title": "Review-Only Learning Promotion",
			"goal": "Promote high-signal trace patterns into benchmark or policy draft suggestions with stronger provenance and maintainer review guidance.",
			"status": "next",
			"scope": [
				"Richer guarded learning review manifests",
				"Explicit provenance linking from episodes to draft suggestions",
				"Maintainer-facing rationale for accepted versus deferred drafts"
			],
			"entryCriteria": [
				"Phase5B advisory factor semantics are stable and reviewable"
			],
			"exitCriteria": [
				"Draft suggestions remain review-only and provenance-backed",
				"Generated guidance is deterministic enough for repeatable review"
			],
			"stillOutOfScope": [
				"Auto-merge of drafts",
				"Automatic runtime consumption"
			]
		},
		{
			"id": "Phase5D",
			"title": "Bounded Reviewed-Learning Runtime Expansion",
			"goal": "Allow approved, reviewed trace-derived learning to influence more of the bounded runtime while staying explicit, static, and reversible.",
			"status": "future",
			"scope": [
				"Static reviewed-learning effects on ranking or planning",
				"Checkpoint-safe and replay-safe runtime use",
				"Artifact-backed rollout controls"
			],
			"entryCriteria": [
				"Phase5C review manifests and provenance are trusted by maintainers"
			],
			"exitCriteria": [
				"Runtime influence is explicit and reversible",
				"No raw trace is consumed directly at runtime"
			],
			"stillOutOfScope": [
				"Live online learning",
				"Execution-capable orchestration"
			]
		},
		{
			"id": "Phase6A",
			"title": "Team-Level Handoff Optimization",
			"goal": "Expand optimization targets from single-agent guidance toward multi-agent delegation and handoff contracts.",
			"status": "future",
			"scope": [
				"Shared handoff conventions across Team Lead and specialist agents",
				"Delegation-path benchmarks",
				"Comparison of shorter versus longer agent routes"
			],
			"entryCriteria": [
				"Trace-backed path summaries are reliable across multi-step episodes"
			],
			"exitCriteria": [
				"Agent-team handoff quality is observable and benchmarked",
				"Optimization still remains review-gated"
			],
			"stillOutOfScope": [
				"Unattended dispatch",
				"Background self-modification"
			]
		},
		{
			"id": "Phase6B",
			"title": "Guarded Semi-Autonomous Execution",
			"goal": "Introduce bounded, stage-only automation for approved follow-on work while keeping human review and rollback mandatory.",
			"status": "future",
			"scope": [
				"Stage-only dispatch preparation",
				"Explicit approval checkpoints",
				"Budgets, kill switches, and rollback markers"
			],
			"entryCriteria": [
				"Earlier phases show high-confidence attribution and reviewed learning quality",
				"Governance artifacts clearly define authority boundaries"
			],
			"exitCriteria": [
				"Any automation remains bounded, logged, and reversible",
				"Human approval remains mandatory before execution"
			],
			"stillOutOfScope": [
				"Continuous unattended operation",
				"Self-approved code changes"
			]
		},
		{
			"id": "Phase7",
			"title": "Safely Autonomous Self-Improving Agent Team",
			"goal": "Reach limited autonomy only after trace quality, review promotion, team optimization, and guarded semi-autonomy have all been proven stable.",
			"status": "future",
			"scope": [
				"Strict bounded autonomy in approved workflows only",
				"Persistent governance, rollback, and observability requirements",
				"Continuous learning from reviewed traces rather than raw unreviewed behavior"
			],
			"entryCriteria": [
				"All prior phases are complete and governance approves autonomy for a specific surface"
			],
			"exitCriteria": [
				"Autonomy is auditable, bounded, and reversible",
				"The system can improve within policy without bypassing human control"
			],
			"stillOutOfScope": [
				"Unbounded autonomous operation",
				"Hidden learning channels",
				"Self-widening authority"
			]
		}
	],
	"commands": [
		{
			"command": "read_file docs/agents/task-spec.md, docs/agents/research-report.md, docs/agents/state.json, docs/agents/review-report.md, docs/agents/release-report.md",
			"result": "pass",
			"notes": "Confirmed the active governed artifacts still described the planning-only slice and needed to be advanced to the implemented Phase 5B task."
		},
		{
			"command": "read_file .github/skills/autoagent-loop/scripts/autoagent_loop.py around _episode_shadow_learning_scores(), _episode_learning_summary(), and review-only draft payload builders",
			"result": "pass",
			"notes": "Confirmed the runtime already exposed the bounded episode summaries required for a factor-only scoring refinement and identified the exact review-only serialization seams."
		},
		{
			"command": "py -3 -m pytest tests/test_autoagent_loop_runner.py --basetemp .\\.tmp\\pytest-shadow-learning -k \"test_episode_shadow_learning_scores_keep_benchmark_only_quality_stable or test_episode_shadow_learning_scores_penalize_terminal_handoff_and_tool_churn\"",
			"result": "pass",
			"notes": "Focused direct score coverage passed with 2 selected tests and 71 deselected."
		},
		{
			"command": "py -3 -m pytest tests/test_autoagent_loop_runner.py --basetemp .\\.tmp\\pytest-autoagent-loop-runner",
			"result": "pass",
			"notes": "The full deterministic runner file passed with 73 tests, confirming factor-summary serialization through review-only learning artifacts."
		}
	],
	"conclusion": {
		"verdict": "phase5b_bounded_advisory_factors_implemented_and_validated",
		"summary": "The bounded Phase 5B scoring refinement is now implemented, validated, and still shadow-only: terminal outcome, handoff burden, and repeated-tool churn are explicit factors, and maintainers can inspect them through review-only learning artifacts.",
		"recommendedNextAction": "Refresh the governed artifacts around the implemented slice and queue either Phase 5C review-only promotion or a narrower factor-calibration follow-on as the next bounded step."
	},
	"artifactsReviewed": [
		"docs/agents/task-spec.md",
		"docs/agents/research-report.md",
		"docs/agents/state.json",
		"docs/agents/patch-report.md",
		"docs/agents/test-report.md",
		"docs/agents/review-report.md",
		"docs/agents/release-report.md",
		".github/skills/autoagent-loop/scripts/autoagent_loop.py",
		"tests/test_autoagent_loop_runner.py"
	]
}
```


