from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from inspect import cleandoc
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / ".github" / "skills" / "autoagent-loop" / "scripts" / "autoagent_loop.py"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "autoagent-loop"


def load_module():
    spec = importlib.util.spec_from_file_location("repo_autoagent_loop_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def prepare_workspace(tmp_path: Path) -> tuple[Path, Path]:
    docs_agents = tmp_path / "docs" / "agents"
    run_root = docs_agents / "runs" / "test-run"
    docs_agents.mkdir(parents=True, exist_ok=True)
    run_root.mkdir(parents=True, exist_ok=True)
    current_run = {"currentRunPath": "docs/agents/runs/test-run"}
    (docs_agents / "current-run.json").write_text(json.dumps(current_run), encoding="utf-8")

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    for name in [
        "onboarding-helper.agent.md",
        "benchmark.json",
        "mutations.json",
        "experiment.md",
    ]:
        (working_dir / name).write_text(
            (FIXTURE_DIR / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    return docs_agents, working_dir


def prepare_multi_target_workspace(tmp_path: Path) -> tuple[Path, Path]:
    docs_agents, working_dir = prepare_workspace(tmp_path)
    for name in [
        "bundle-benchmark.json",
        "bundle-mutations.json",
        "bundle-experiment.md",
        "shared-guidance.md",
    ]:
        (working_dir / name).write_text(
            (FIXTURE_DIR / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    return docs_agents, working_dir


def prepare_branching_search_workspace(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    docs_agents = tmp_path / "docs" / "agents"
    run_root = docs_agents / "runs" / "test-run"
    docs_agents.mkdir(parents=True, exist_ok=True)
    run_root.mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )

    work_dir = tmp_path / "frontier-work"
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "branching.agent.md").write_text(
        "---\nname: Branching Agent\ntools: []\n---\n\n# Branching Agent\n\nMODE: base\n",
        encoding="utf-8",
    )
    (work_dir / "branching-benchmark.json").write_text(
        json.dumps(
            {
                "id": "branching-benchmark",
                "checks": [
                    {
                        "id": "workflow-mode",
                        "type": "contains_text",
                        "target": "body",
                        "value": "MODE: workflow",
                        "weight": 1.0,
                    },
                    {
                        "id": "docs-mode",
                        "type": "contains_text",
                        "target": "body",
                        "value": "MODE: docs",
                        "weight": 1.0,
                    },
                    {
                        "id": "workflow-finish",
                        "type": "contains_text",
                        "target": "body",
                        "value": "manager-led multi-agent workflow",
                        "weight": 1.0,
                    },
                    {
                        "id": "docs-agents",
                        "type": "contains_text",
                        "target": "body",
                        "value": "`AGENTS.md`",
                        "weight": 1.0,
                    },
                    {
                        "id": "docs-task-spec",
                        "type": "contains_text",
                        "target": "body",
                        "value": "`docs/agents/task-spec.md`",
                        "weight": 1.0,
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (work_dir / "branching-mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "choose-workflow-path",
                        "description": "Open the workflow branch.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "MODE: base",
                                "new": "MODE: workflow",
                            }
                        ],
                    },
                    {
                        "id": "choose-docs-path",
                        "description": "Open the docs branch.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "MODE: base",
                                "new": "MODE: docs",
                            }
                        ],
                    },
                    {
                        "id": "workflow-finisher",
                        "description": "Finish the workflow branch.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "MODE: workflow",
                                "new": "MODE: workflow\nmanager-led multi-agent workflow",
                            }
                        ],
                    },
                    {
                        "id": "docs-finisher",
                        "description": "Finish the docs branch.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "MODE: docs",
                                "new": "MODE: docs\n`AGENTS.md`\n`docs/agents/task-spec.md`",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    linear_experiment = work_dir / "linear-experiment.md"
    write_experiment(
        linear_experiment,
        "\n".join(
            [
                "name: branching-linear",
                "targetAgentPath: branching.agent.md",
                "benchmarkPath: branching-benchmark.json",
                "mutationCatalogPath: branching-mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
            ]
        ),
    )
    frontier_experiment = work_dir / "frontier-experiment.md"
    write_experiment(
        frontier_experiment,
        "\n".join(
            [
                "name: branching-frontier",
                "targetAgentPath: branching.agent.md",
                "benchmarkPath: branching-benchmark.json",
                "mutationCatalogPath: branching-mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 3",
            ]
        ),
    )

    return docs_agents, work_dir, linear_experiment, frontier_experiment


def write_experiment(path: Path, frontmatter: str, body: str = "Bundle experiment body.") -> None:
    path.write_text(f"---\n{cleandoc(frontmatter)}\n---\n\n{body}\n", encoding="utf-8")


def write_markdown_report(path: Path, payload: dict[str, object], title: str = "Report") -> None:
    path.write_text(
        f"# {title}\n\n```json\n{json.dumps(payload, indent=2)}\n```\n",
        encoding="utf-8",
    )


def write_governed_state(
    path: Path,
    quality_gate_status: str,
    *,
    task_id: str = "manual-autoagent-slice",
    task_title: str = "Governed AutoAgent Slice",
    phase: str = "Done",
    next_action_summary: str = "Open the next bounded AutoAgent slice.",
    next_action_owner: str = "team-lead",
) -> None:
    path.write_text(
        json.dumps(
            {
                "task": {"id": task_id, "title": task_title},
                "phase": phase,
                "quality_gate": {"status": quality_gate_status},
                "next_action": {
                    "summary": next_action_summary,
                    "owner": next_action_owner,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_governed_review_report(path: Path, status: str) -> None:
    write_markdown_report(path, {"type": "ReviewReport", "status": status}, title="Review summary")


def write_live_evaluator_experiment(
    path: Path,
    target_name: str,
    *,
    benchmark_name: str = "benchmark.json",
    mutation_catalog_name: str = "mutations.json",
    prompt_name: str | None,
    rubric_names: list[str],
    provider: str = "github-models",
    strategy: str = "advisory",
    max_samples: int = 2,
    record_raw_outputs: bool = False,
    stage_for_review: bool = True,
    staged_apply_on_pass: bool = False,
    continuous_stage_only: bool = True,
) -> None:
    lines = [
        f"name: {path.stem}",
        f"targetAgentPath: {target_name}",
        f"benchmarkPath: {benchmark_name}",
        f"mutationCatalogPath: {mutation_catalog_name}",
        f"stageForReview: {'true' if stage_for_review else 'false'}",
        "evaluationMode:",
        "  deterministic: true",
        "  liveEvaluator:",
        "    enabled: true",
        f"    strategy: {strategy}",
        f"    provider: {provider}",
        "    model: gpt-5.4",
        f"    maxSamples: {max_samples}",
        f"    recordRawOutputs: {'true' if record_raw_outputs else 'false'}",
    ]
    if prompt_name is not None:
        lines.append(f"    promptArtifactPath: {prompt_name}")
    if rubric_names:
        lines.append("    rubricPaths:")
        lines.extend(f"      - {name}" for name in rubric_names)
    lines.extend(
        [
            "stagedPatchPolicy:",
            "  enabled: true",
            "  mode: review_bundle",
            f"  applyOnPass: {'true' if staged_apply_on_pass else 'false'}",
            "continuousPolicy:",
            "  mode: manual",
            f"  stageOnly: {'true' if continuous_stage_only else 'false'}",
        ]
    )
    write_experiment(path, "\n".join(lines))


def write_continuation_policy_experiment(
    path: Path,
    target_name: str,
    *,
    benchmark_name: str = "benchmark.json",
    mutation_catalog_name: str = "mutations.json",
    mode: str = "manual",
    stage_for_review: bool = True,
    staged_apply_on_pass: bool = False,
    continuous_stage_only: bool = True,
    continuous_require_review_pass: bool = True,
    enabled: bool | None = None,
    schedule_cron: str | None = None,
    triggers: list[str] | None = None,
    min_signal_count: int | None = None,
    apply_best_candidate: bool = False,
) -> None:
    lines = [
        f"name: {path.stem}",
        f"targetAgentPath: {target_name}",
        f"benchmarkPath: {benchmark_name}",
        f"mutationCatalogPath: {mutation_catalog_name}",
        f"stageForReview: {'true' if stage_for_review else 'false'}",
        f"applyBestCandidate: {'true' if apply_best_candidate else 'false'}",
        "stagedPatchPolicy:",
        "  enabled: true",
        "  mode: review_bundle",
        f"  applyOnPass: {'true' if staged_apply_on_pass else 'false'}",
        "continuousPolicy:",
        f"  mode: {mode}",
        f"  stageOnly: {'true' if continuous_stage_only else 'false'}",
        f"  requireReviewPass: {'true' if continuous_require_review_pass else 'false'}",
    ]
    if enabled is not None:
        lines.append(f"  enabled: {'true' if enabled else 'false'}")
    if schedule_cron is not None:
        lines.append(f'  scheduleCron: "{schedule_cron}"')
    if triggers:
        lines.append("  triggerOn:")
        lines.extend(f"    - {trigger}" for trigger in triggers)
    if min_signal_count is not None:
        lines.append(f"  minSignalCount: {min_signal_count}")
    write_experiment(path, "\n".join(lines))


def test_load_experiment_normalizes_extended_phase1_schema(tmp_path: Path) -> None:
    module = load_module()

    target = tmp_path / "primary.agent.md"
    target.write_text("---\nname: Primary\n---\n\nPrimary body.\n", encoding="utf-8")
    prompt = tmp_path / "judge-prompt.md"
    prompt.write_text("Judge prompt.\n", encoding="utf-8")
    rubric = tmp_path / "judge-rubric.md"
    rubric.write_text("Judge rubric.\n", encoding="utf-8")

    experiment = tmp_path / "extended-experiment.md"
    write_experiment(
        experiment,
        f"""
name: extended-schema
targetAgentPath: {target.name}
benchmarkPath: benchmark.json
mutationCatalogPath: mutations.json
evaluationMode:
  deterministic: true
  liveEvaluator:
    enabled: true
    strategy: tie_breaker
    provider: github-models
    model: gpt-5.4
    promptArtifactPath: {prompt.name}
    rubricPaths:
      - {rubric.name}
    maxSamples: 3
    recordRawOutputs: true
continuousPolicy:
  mode: usage_driven
  triggerOn:
    - review_failure
    - tool_error_spike
  minSignalCount: 4
  maxQueuedRuns: 2
  learningWindowDays: 14
stagedPatchPolicy:
  enabled: true
  mode: review_bundle
  reviewerHints:
    - Review the candidate before applying it.
  includeTargetSnapshots: true
  includeDiffSummary: true
""".strip(),
    )

    loaded = module.load_experiment(experiment)

    assert loaded["evaluationMode"]["deterministic"] is True
    assert loaded["evaluationMode"]["live"] is True
    assert loaded["evaluationMode"]["liveEvaluator"]["strategy"] == "tie_breaker"
    assert loaded["evaluationMode"]["liveEvaluator"]["model"] == "gpt-5.4"
    assert loaded["evaluationMode"]["liveEvaluator"]["promptArtifactPath"] == prompt.resolve()
    assert loaded["evaluationMode"]["liveEvaluator"]["rubricPaths"] == [rubric.resolve()]
    assert loaded["continuousPolicy"]["mode"] == "usage_driven"
    assert loaded["continuousPolicy"]["triggerOn"] == [
        "review_failure",
        "tool_error_spike",
    ]
    assert loaded["continuousPolicy"]["minSignalCount"] == 4
    assert loaded["continuousPolicy"]["maxQueuedRuns"] == 2
    assert loaded["continuousPolicy"]["learningWindowDays"] == 14
    assert loaded["continuationEligibility"] == {
        "eligible": True,
        "status": "eligible",
        "blockedReasons": [],
        "executionMode": "report_only",
        "reviewGated": True,
    }
    assert loaded["stagedPatchPolicy"]["enabled"] is True
    assert loaded["stagedPatchPolicy"]["mode"] == "review_bundle"
    assert loaded["candidatePolicy"] == {
        "keepStrategy": "score-then-simpler",
        "searchStrategy": "current_best",
        "frontierSize": 1,
    }


def test_checked_in_autoagent_experiment_uses_manager_bundle_targets() -> None:
    module = load_module()

    experiment_path = ROOT / "docs" / "agents" / "autoagent-experiment.md"
    benchmark_path = (
        ROOT / ".github" / "skills" / "autoagent-loop" / "examples" / "team-lead-benchmark.json"
    )
    mutation_path = (
        ROOT / ".github" / "skills" / "autoagent-loop" / "examples" / "team-lead-mutations.json"
    )

    loaded = module.load_experiment(experiment_path)
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    mutations = json.loads(mutation_path.read_text(encoding="utf-8"))

    assert [target["id"] for target in loaded["targets"]] == [
        "team-lead",
        "team-lead-skill",
        "agent-operating-guide",
    ]
    assert loaded["primaryTargetId"] == "team-lead"
    assert loaded["continuousPolicy"]["mode"] == "manual"
    assert loaded["continuousPolicy"]["stageOnly"] is True
    assert loaded["continuousPolicy"]["requireReviewPass"] is True
    assert loaded["evaluationMode"]["liveEvaluator"]["enabled"] is False
    assert loaded["evidencePolicy"]["includeChatHistory"] is True
    assert loaded["evidencePolicy"]["includeTranscriptHistory"] is True
    assert loaded["evidencePolicy"]["includeHandoffHistory"] is True
    assert loaded["evidencePolicy"]["allowExternalPaths"] is False

    checks_by_id = {check["id"]: check for check in benchmark["checks"]}
    assert checks_by_id["skill-current-run-contract"]["targetId"] == "team-lead-skill"
    assert checks_by_id["skill-no-product-code-boundary"]["value"] == (
        "The manager does not implement product code."
    )
    assert checks_by_id["skill-snapshot-contract"]["targetId"] == "team-lead-skill"
    assert checks_by_id["guide-current-run-contract"]["targetId"] == "agent-operating-guide"
    assert checks_by_id["guide-live-shared-root"]["value"] == (
        "`docs/agents/` is the only live shared artifact root."
    )
    assert checks_by_id["guide-no-hook-bypass"]["targetId"] == "agent-operating-guide"

    boundary_operations = mutations["mutations"][0]["operations"]
    assert {operation["targetId"] for operation in boundary_operations} == {
        "team-lead",
        "team-lead-skill",
    }
    assert any(
        operation["old"] == "- The manager does not implement product code."
        and operation["new"] == "- The manager may implement product code."
        for operation in boundary_operations
    )

    guide_operations = mutations["mutations"][1]["operations"]
    assert {operation["targetId"] for operation in guide_operations} == {
        "agent-operating-guide",
    }
    assert any(
        operation["old"] == "- `docs/agents/` is the only live shared artifact root."
        and operation["new"] == "- `docs/agents/` is a preferred live shared artifact root."
        for operation in guide_operations
    )
    assert any(
        operation["old"] == "- Do not bypass hook denials."
        and operation["new"] == "- Do not bypass hook denials when local iteration needs it."
        for operation in guide_operations
    )
    assert loaded["stageForReview"] is True


def test_load_experiment_normalizes_first_class_history_sources(tmp_path: Path) -> None:
    module = load_module()

    target = tmp_path / "primary.agent.md"
    target.write_text("---\nname: Primary\n---\n\nPrimary body.\n", encoding="utf-8")
    chat_export = tmp_path / "history" / "exported-chat.json"
    chat_export.parent.mkdir(parents=True, exist_ok=True)
    chat_export.write_text("[]\n", encoding="utf-8")
    transcript_export = tmp_path / "history" / "conversation.jsonl"
    transcript_export.write_text("", encoding="utf-8")

    experiment = tmp_path / "history-experiment.md"
    write_experiment(
        experiment,
        f"""
name: history-schema
targetAgentPath: {target.name}
benchmarkPath: benchmark.json
mutationCatalogPath: mutations.json
evidencePolicy:
  includeChatHistory: true
  chatHistoryPaths:
        - history/{chat_export.name}
  includeTranscriptHistory: true
  transcriptHistoryPaths:
        - history/{transcript_export.name}
""".strip(),
    )

    loaded = module.load_experiment(experiment)
    evidence_policy = loaded["evidencePolicy"]

    assert evidence_policy["includeChatHistory"] is True
    assert evidence_policy["chatHistoryPaths"] == [chat_export.resolve()]
    assert evidence_policy["includeTranscriptHistory"] is True
    assert evidence_policy["transcriptHistoryPaths"] == [transcript_export.resolve()]
    assert [source["kind"] for source in evidence_policy["externalLogSources"]] == [
        "chat_transcript",
        "conversation_transcript",
    ]
    assert [source["format"] for source in evidence_policy["externalLogSources"]] == [
        "json",
        "jsonl",
    ]


def test_load_experiment_normalizes_first_class_handoff_history_sources(
    tmp_path: Path,
) -> None:
    module = load_module()

    target = tmp_path / "primary.agent.md"
    target.write_text("---\nname: Primary\n---\n\nPrimary body.\n", encoding="utf-8")
    handoff_export = tmp_path / "history" / "handoff-history.jsonl"
    handoff_export.parent.mkdir(parents=True, exist_ok=True)
    handoff_export.write_text("", encoding="utf-8")

    experiment = tmp_path / "handoff-history-experiment.md"
    write_experiment(
        experiment,
        f"""
name: handoff-history-schema
targetAgentPath: {target.name}
benchmarkPath: benchmark.json
mutationCatalogPath: mutations.json
evidencePolicy:
  includeHandoffHistory: true
  handoffHistoryPaths:
        - history/{handoff_export.name}
""".strip(),
    )

    loaded = module.load_experiment(experiment)
    evidence_policy = loaded["evidencePolicy"]

    assert evidence_policy["includeHandoffHistory"] is True
    assert evidence_policy["handoffHistoryPaths"] == [handoff_export.resolve()]
    assert [source["kind"] for source in evidence_policy["externalLogSources"]] == [
        "handoff_history"
    ]
    assert [source["format"] for source in evidence_policy["externalLogSources"]] == ["jsonl"]


def test_load_experiment_normalizes_reviewed_policy_runtime(tmp_path: Path) -> None:
    module = load_module()

    target = tmp_path / "primary.agent.md"
    target.write_text("---\nname: Primary\n---\n\nPrimary body.\n", encoding="utf-8")
    reviewed_policies = tmp_path / "reviewed-policies.json"
    reviewed_policies.write_text('{"policies": []}\n', encoding="utf-8")

    experiment = tmp_path / "reviewed-policy-runtime-experiment.md"
    write_experiment(
        experiment,
        f"""
name: reviewed-policy-runtime
targetAgentPath: {target.name}
benchmarkPath: benchmark.json
mutationCatalogPath: mutations.json
reviewedPolicyRuntime:
  enabled: true
  artifactPath: {reviewed_policies.name}
  preferredSequenceBonus: 0.06
  escalationPenalty: 0.07
""".strip(),
    )

    loaded = module.load_experiment(experiment)

    assert loaded["reviewedPolicyRuntime"] == {
        "enabled": True,
        "artifactPath": reviewed_policies.resolve(),
        "preferredSequenceBonus": 0.06,
        "escalationPenalty": 0.07,
    }


def test_load_experiment_normalizes_frontier_candidate_policy(tmp_path: Path) -> None:
    module = load_module()

    target = tmp_path / "primary.agent.md"
    target.write_text("---\nname: Primary\n---\n\nPrimary body.\n", encoding="utf-8")
    experiment = tmp_path / "frontier-experiment.md"
    write_experiment(
        experiment,
        f"""
name: frontier-schema
targetAgentPath: {target.name}
benchmarkPath: benchmark.json
mutationCatalogPath: mutations.json
candidatePolicy:
  keepStrategy: score-then-simpler
  frontierSize: 3
""".strip(),
    )

    loaded = module.load_experiment(experiment)

    assert loaded["candidatePolicy"] == {
        "keepStrategy": "score-then-simpler",
        "searchStrategy": "frontier",
        "frontierSize": 3,
    }


@pytest.mark.parametrize(
    ("candidate_policy", "match"),
    [
        (
            "candidatePolicy:\n  searchStrategy: unsupported",
            r"Unsupported candidatePolicy\.searchStrategy: unsupported",
        ),
        (
            "candidatePolicy:\n  frontierSize: 0",
            r"candidatePolicy\.frontierSize must be at least 1\.",
        ),
        (
            "candidatePolicy:\n  searchStrategy: current_best\n  frontierSize: 2",
            r"candidatePolicy\.frontierSize must be 1 when searchStrategy is current_best\.",
        ),
    ],
)
def test_load_experiment_rejects_invalid_candidate_policy(
    tmp_path: Path,
    candidate_policy: str,
    match: str,
) -> None:
    module = load_module()

    target = tmp_path / "primary.agent.md"
    target.write_text("---\nname: Primary\n---\n\nPrimary body.\n", encoding="utf-8")
    experiment = tmp_path / "invalid-candidate-policy.md"
    write_experiment(
        experiment,
        f"""
name: invalid-candidate-policy
targetAgentPath: {target.name}
benchmarkPath: benchmark.json
mutationCatalogPath: mutations.json
{candidate_policy}
""".strip(),
    )

    with pytest.raises(ValueError, match=match):
        module.load_experiment(experiment)


@pytest.mark.parametrize(
    ("provider", "prompt_name", "rubric_names", "max_samples", "match"),
    [
        (
            "unsupported-provider",
            "judge-prompt.md",
            ["judge-rubric.md"],
            2,
            r"Unsupported live evaluator provider: unsupported-provider",
        ),
        (
            "github-models",
            None,
            ["judge-rubric.md"],
            2,
            r"Live evaluator requires promptArtifactPath when enabled\.",
        ),
        (
            "github-models",
            "judge-prompt.md",
            [],
            2,
            r"Live evaluator requires at least one rubricPath when enabled\.",
        ),
        (
            "github-models",
            "judge-prompt.md",
            ["judge-rubric.md"],
            0,
            r"Live evaluator maxSamples must be at least 1 when enabled\.",
        ),
    ],
)
def test_run_autoagent_loop_rejects_invalid_live_evaluator_config(
    tmp_path: Path,
    provider: str,
    prompt_name: str | None,
    rubric_names: list[str],
    max_samples: int,
    match: str,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    if prompt_name is not None:
        (working_dir / prompt_name).write_text("Judge prompt.\n", encoding="utf-8")
    for rubric_name in rubric_names:
        (working_dir / rubric_name).write_text("Judge rubric.\n", encoding="utf-8")

    experiment = working_dir / "invalid-live-evaluator.md"
    write_live_evaluator_experiment(
        experiment,
        "onboarding-helper.agent.md",
        prompt_name=prompt_name,
        rubric_names=rubric_names,
        provider=provider,
        max_samples=max_samples,
    )

    with pytest.raises(ValueError, match=match):
        module.run_autoagent_loop(
            experiment_path=experiment.resolve(),
            output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
            report_path=(docs_agents / "autoagent-report.md").resolve(),
            results_path=(docs_agents / "autoagent-results.tsv").resolve(),
            max_iterations=0,
            apply_best=False,
        )


def test_run_autoagent_loop_rejects_live_evaluator_when_apply_best_requested(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    prompt = working_dir / "judge-prompt.md"
    prompt.write_text("Judge prompt.\n", encoding="utf-8")
    rubric = working_dir / "judge-rubric.md"
    rubric.write_text("Judge rubric.\n", encoding="utf-8")

    experiment = working_dir / "unsafe-live-evaluator.md"
    write_live_evaluator_experiment(
        experiment,
        "onboarding-helper.agent.md",
        prompt_name=prompt.name,
        rubric_names=[rubric.name],
    )

    with pytest.raises(
        ValueError,
        match=(
            r"Live evaluator execution requires stage-for-review mode; "
            r"apply-best is not allowed\."
        ),
    ):
        module.run_autoagent_loop(
            experiment_path=experiment.resolve(),
            output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
            report_path=(docs_agents / "autoagent-report.md").resolve(),
            results_path=(docs_agents / "autoagent-results.tsv").resolve(),
            max_iterations=0,
            apply_best=True,
        )


@pytest.mark.parametrize(
    ("stage_for_review", "staged_apply_on_pass", "continuous_stage_only", "match"),
    [
        (
            False,
            False,
            True,
            r"Live evaluator execution requires staged patch review to remain enabled\.",
        ),
        (
            True,
            True,
            True,
            r"Live evaluator execution requires stagedPatchPolicy\.applyOnPass to remain false\.",
        ),
        (
            True,
            False,
            False,
            r"Live evaluator execution requires continuousPolicy\.stageOnly to remain true\.",
        ),
    ],
)
def test_run_autoagent_loop_rejects_unsafe_live_evaluator_stage_settings(
    tmp_path: Path,
    stage_for_review: bool,
    staged_apply_on_pass: bool,
    continuous_stage_only: bool,
    match: str,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    prompt = working_dir / "judge-prompt.md"
    prompt.write_text("Judge prompt.\n", encoding="utf-8")
    rubric = working_dir / "judge-rubric.md"
    rubric.write_text("Judge rubric.\n", encoding="utf-8")

    experiment = working_dir / "unsafe-stage-settings.md"
    write_live_evaluator_experiment(
        experiment,
        "onboarding-helper.agent.md",
        prompt_name=prompt.name,
        rubric_names=[rubric.name],
        stage_for_review=stage_for_review,
        staged_apply_on_pass=staged_apply_on_pass,
        continuous_stage_only=continuous_stage_only,
    )

    with pytest.raises(ValueError, match=match):
        module.run_autoagent_loop(
            experiment_path=experiment.resolve(),
            output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
            report_path=(docs_agents / "autoagent-report.md").resolve(),
            results_path=(docs_agents / "autoagent-results.tsv").resolve(),
            max_iterations=0,
            apply_best=False,
        )


def test_run_autoagent_loop_reports_manual_continuation_eligibility(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_state(docs_agents / "state.json", "PASS")
    write_governed_review_report(docs_agents / "review-report.md", "PASS")

    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    eligibility = result["experiment"]["continuationEligibility"]
    assert eligibility == {
        "eligible": False,
        "status": "blocked",
        "blockedReasons": ["manual_mode"],
        "executionMode": "report_only",
        "reviewGated": True,
    }
    lifecycle = result["experiment"]["governedTaskLifecycle"]
    assert lifecycle == {
        "status": "available",
        "readable": True,
        "sourcePath": (docs_agents / "state.json").as_posix(),
        "taskId": "manual-autoagent-slice",
        "taskTitle": "Governed AutoAgent Slice",
        "phase": "Done",
        "qualityGateStatus": "PASS",
        "nextActionSummary": "Open the next bounded AutoAgent slice.",
        "nextActionOwner": "team-lead",
        "missingFields": [],
    }
    readiness = result["experiment"]["continuationReadiness"]
    assert readiness == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["manual_mode"],
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": False,
        "governedReviewStatus": "PASS",
        "governedReviewReadable": True,
        "governedReviewSourcePath": (docs_agents / "state.json").as_posix(),
    }
    handoff = result["experiment"]["reviewedContinuationHandoff"]
    assert handoff == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["manual_mode"],
        "handoffMode": "reviewed_manual",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": False,
        "continuationReadinessStatus": "blocked",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Done",
        "summary": "Not ready for reviewed manual handoff.",
        "recommendedAction": "Open the next bounded AutoAgent slice.",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
        },
    }
    assert result["provenance"]["policy"]["continuationEligibility"] == eligibility
    consensus = result["experiment"]["governedReviewConsensus"]
    assert consensus == {
        "agrees": True,
        "status": "consistent",
        "blockedReasons": [],
        "stateStatus": "PASS",
        "stateReadable": True,
        "stateSourcePath": (docs_agents / "state.json").as_posix(),
        "reviewReportStatus": "PASS",
        "reviewReportReadable": True,
        "reviewReportSourcePath": (docs_agents / "review-report.md").as_posix(),
    }
    assert result["reportStatusMeaning"] == "artifact_readiness"
    assert result["provenance"]["policy"]["governedTaskLifecycle"] == lifecycle
    assert result["provenance"]["policy"]["governedReviewConsensus"] == consensus
    assert result["provenance"]["policy"]["continuationReadiness"] == readiness
    assert result["provenance"]["policy"]["reviewedContinuationHandoff"] == handoff
    contract = result["experiment"]["orchestrationContract"]
    assert contract == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["manual_mode"],
        "contractMode": "staged_dispatch_simulation",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": False,
        "reviewedHandoffStatus": "blocked",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Done",
        "contractId": "manual-autoagent-slice::staged_dispatch_simulation",
        "summary": "Staged dispatch simulation is blocked.",
        "recommendedAction": "Open the next bounded AutoAgent slice.",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["provenance"]["policy"]["orchestrationContract"] == contract
    intent = result["experiment"]["reviewedDispatchIntent"]
    assert intent == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["manual_mode"],
        "intentMode": "reviewed_dispatch_intent",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": False,
        "requiresExplicitApproval": True,
        "approvalStatus": "blocked",
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "orchestrationContractStatus": "blocked",
        "reviewedHandoffStatus": "blocked",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Done",
        "intentId": "manual-autoagent-slice::staged_dispatch_simulation::reviewed_dispatch_intent",
        "summary": "Reviewed dispatch intent is blocked.",
        "recommendedAction": "Open the next bounded AutoAgent slice.",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["provenance"]["policy"]["reviewedDispatchIntent"] == intent
    approval_metadata = result["experiment"]["governedApprovalMetadata"]
    assert approval_metadata == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["manual_mode"],
        "approvalMode": "governed_approval_metadata",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": False,
        "requiresExplicitApproval": True,
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "readyForRecording": False,
        "reviewPassRecorded": True,
        "reviewPassReadable": True,
        "qualityGateStatus": "PASS",
        "reviewedDispatchIntentStatus": "blocked",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Done",
        "metadataId": (
            "manual-autoagent-slice::staged_dispatch_simulation::"
            "reviewed_dispatch_intent::governed_approval_metadata"
        ),
        "summary": "Governed approval metadata is blocked.",
        "recommendedAction": "Open the next bounded AutoAgent slice.",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["provenance"]["policy"]["governedApprovalMetadata"] == approval_metadata

    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Report status meaning: artifact_readiness" in report_text
    assert "- Governed task lifecycle: Done" in report_text
    assert "- Governed task id: manual-autoagent-slice" in report_text
    assert "- Governed task title: Governed AutoAgent Slice" in report_text
    assert "- Governed lifecycle quality gate: PASS" in report_text
    assert (
        "- Governed next action: team-lead - Open the next bounded AutoAgent slice." in report_text
    )
    assert "- Governed lifecycle missing fields: none" in report_text
    assert "- Continuation eligibility: blocked" in report_text
    assert "- Continuation blocked reasons: manual_mode" in report_text
    assert "- Continuation execution: report_only" in report_text
    assert "- Continuation readiness: blocked" in report_text
    assert "- Continuation readiness blocked reasons: manual_mode" in report_text
    assert "- Governed review consensus: consistent" in report_text
    assert "- Governed review consensus blocked reasons: none" in report_text
    assert "- Governed review status: PASS" in report_text
    assert "- Review report status: PASS" in report_text
    assert "- Transcript evidence records: 0" in report_text
    assert "- Handoff evidence records: 0" in report_text
    assert "- Reviewed continuation handoff: blocked" in report_text
    assert "- Reviewed handoff blocked reasons: manual_mode" in report_text
    assert "- Reviewed handoff mode: reviewed_manual" in report_text
    assert "- Reviewed handoff summary: Not ready for reviewed manual handoff." in report_text
    assert (
        "- Reviewed handoff recommended action: Open the next bounded AutoAgent slice."
        in report_text
    )
    assert "- Orchestration contract: blocked" in report_text
    assert "- Orchestration contract blocked reasons: manual_mode" in report_text
    assert "- Orchestration contract mode: staged_dispatch_simulation" in report_text
    assert "- Orchestration contract summary: Staged dispatch simulation is blocked." in report_text
    assert "- Reviewed dispatch intent: blocked" in report_text
    assert "- Reviewed dispatch blocked reasons: manual_mode" in report_text
    assert "- Reviewed dispatch approval status: blocked" in report_text
    assert "- Reviewed dispatch approval source: governed_artifacts_only" in report_text
    assert "- Reviewed dispatch summary: Reviewed dispatch intent is blocked." in report_text
    assert (
        "- Reviewed dispatch recommended action: Open the next bounded AutoAgent slice."
        in report_text
    )
    assert "- Governed approval metadata: blocked" in report_text
    assert "- Governed approval blocked reasons: manual_mode" in report_text
    assert "- Governed approval review pass recorded: True" in report_text
    assert "- Governed approval quality gate: PASS" in report_text
    assert "- Governed approval source: governed_artifacts_only" in report_text
    assert "- Governed approval summary: Governed approval metadata is blocked." in report_text
    assert (
        "- Governed approval recommended action: Open the next bounded AutoAgent slice."
        in report_text
    )
    assert "- Phase 4 bounded step: governed_approval_metadata" in report_text
    assert "- Phase 4 execution authority: out_of_scope" in report_text
    assert "- Phase 3 visibility scope: complete" in report_text
    assert "- Phase 3 unattended orchestration: out_of_scope" in report_text


def test_run_autoagent_loop_reports_eligible_review_gated_continuation(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_state(docs_agents / "state.json", "PASS")
    write_governed_review_report(docs_agents / "review-report.md", "PASS")

    experiment = working_dir / "scheduled-continuation.md"
    write_continuation_policy_experiment(
        experiment,
        "onboarding-helper.agent.md",
        mode="scheduled",
        schedule_cron="0 2 * * *",
        triggers=["review_failure"],
        min_signal_count=2,
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    eligibility = result["experiment"]["continuationEligibility"]
    assert eligibility == {
        "eligible": True,
        "status": "eligible",
        "blockedReasons": [],
        "executionMode": "report_only",
        "reviewGated": True,
    }
    lifecycle = result["experiment"]["governedTaskLifecycle"]
    assert lifecycle == {
        "status": "available",
        "readable": True,
        "sourcePath": (docs_agents / "state.json").as_posix(),
        "taskId": "manual-autoagent-slice",
        "taskTitle": "Governed AutoAgent Slice",
        "phase": "Done",
        "qualityGateStatus": "PASS",
        "nextActionSummary": "Open the next bounded AutoAgent slice.",
        "nextActionOwner": "team-lead",
        "missingFields": [],
    }
    readiness = result["experiment"]["continuationReadiness"]
    assert readiness == {
        "ready": True,
        "status": "ready",
        "blockedReasons": [],
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "governedReviewStatus": "PASS",
        "governedReviewReadable": True,
        "governedReviewSourcePath": (docs_agents / "state.json").as_posix(),
    }
    handoff = result["experiment"]["reviewedContinuationHandoff"]
    assert handoff == {
        "ready": True,
        "status": "ready",
        "blockedReasons": [],
        "handoffMode": "reviewed_manual",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "continuationReadinessStatus": "ready",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Done",
        "summary": "Ready for reviewed manual handoff.",
        "recommendedAction": (
            "Review the staged patch bundle and governed artifacts before "
            "choosing the next bounded step."
        ),
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
        },
    }
    assert result["provenance"]["policy"]["continuationEligibility"] == eligibility
    consensus = result["experiment"]["governedReviewConsensus"]
    assert consensus == {
        "agrees": True,
        "status": "consistent",
        "blockedReasons": [],
        "stateStatus": "PASS",
        "stateReadable": True,
        "stateSourcePath": (docs_agents / "state.json").as_posix(),
        "reviewReportStatus": "PASS",
        "reviewReportReadable": True,
        "reviewReportSourcePath": (docs_agents / "review-report.md").as_posix(),
    }
    assert result["reportStatusMeaning"] == "artifact_readiness"
    assert result["provenance"]["policy"]["governedTaskLifecycle"] == lifecycle
    assert result["provenance"]["policy"]["governedReviewConsensus"] == consensus
    assert result["provenance"]["policy"]["continuationReadiness"] == readiness
    assert result["provenance"]["policy"]["reviewedContinuationHandoff"] == handoff
    contract = result["experiment"]["orchestrationContract"]
    assert contract == {
        "ready": True,
        "status": "staged",
        "blockedReasons": [],
        "contractMode": "staged_dispatch_simulation",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "reviewedHandoffStatus": "ready",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Done",
        "contractId": "manual-autoagent-slice::staged_dispatch_simulation",
        "summary": "Staged dispatch simulation is ready for manual review.",
        "recommendedAction": (
            "Open the next bounded implementation step but keep execution manual and report_only."
        ),
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["provenance"]["policy"]["orchestrationContract"] == contract
    intent = result["experiment"]["reviewedDispatchIntent"]
    assert intent == {
        "ready": True,
        "status": "approval_pending",
        "blockedReasons": [],
        "intentMode": "reviewed_dispatch_intent",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "requiresExplicitApproval": True,
        "approvalStatus": "pending_explicit_approval",
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "orchestrationContractStatus": "staged",
        "reviewedHandoffStatus": "ready",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Done",
        "intentId": "manual-autoagent-slice::staged_dispatch_simulation::reviewed_dispatch_intent",
        "summary": "Reviewed dispatch intent is awaiting explicit approval metadata.",
        "recommendedAction": (
            "Record explicit approval metadata before opening the next bounded implementation step."
        ),
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["provenance"]["policy"]["reviewedDispatchIntent"] == intent
    approval_metadata = result["experiment"]["governedApprovalMetadata"]
    assert approval_metadata == {
        "ready": True,
        "status": "ready_for_recording",
        "blockedReasons": [],
        "approvalMode": "governed_approval_metadata",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "requiresExplicitApproval": True,
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "readyForRecording": True,
        "reviewPassRecorded": True,
        "reviewPassReadable": True,
        "qualityGateStatus": "PASS",
        "reviewedDispatchIntentStatus": "approval_pending",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Done",
        "metadataId": (
            "manual-autoagent-slice::staged_dispatch_simulation::"
            "reviewed_dispatch_intent::governed_approval_metadata"
        ),
        "summary": "Governed approval metadata is ready for manual approval recording.",
        "recommendedAction": (
            "Record explicit manual approval metadata in governed artifacts "
            "before opening the next bounded implementation step."
        ),
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["provenance"]["policy"]["governedApprovalMetadata"] == approval_metadata

    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Report status meaning: artifact_readiness" in report_text
    assert "- Governed task lifecycle: Done" in report_text
    assert "- Governed lifecycle missing fields: none" in report_text
    assert "- Continuous mode: scheduled" in report_text
    assert "- Continuation eligibility: eligible" in report_text
    assert "- Continuation blocked reasons: none" in report_text
    assert "- Continuation readiness: ready" in report_text
    assert "- Continuation readiness blocked reasons: none" in report_text
    assert "- Governed review consensus: consistent" in report_text
    assert "- Governed review consensus blocked reasons: none" in report_text
    assert "- Governed review status: PASS" in report_text
    assert "- Review report status: PASS" in report_text
    assert "- Reviewed continuation handoff: ready" in report_text
    assert "- Reviewed handoff blocked reasons: none" in report_text
    assert "- Reviewed handoff mode: reviewed_manual" in report_text
    assert "- Reviewed handoff summary: Ready for reviewed manual handoff." in report_text
    assert (
        "- Reviewed handoff recommended action: Review the staged patch bundle "
        "and governed artifacts before choosing the next bounded step." in report_text
    )
    assert "- Orchestration contract: staged" in report_text
    assert "- Orchestration contract blocked reasons: none" in report_text
    assert (
        "- Orchestration contract summary: Staged dispatch simulation is ready for manual review."
        in report_text
    )
    assert (
        "- Orchestration contract recommended action: Open the next bounded "
        "implementation step but keep execution manual and report_only." in report_text
    )
    assert "- Reviewed dispatch intent: approval_pending" in report_text
    assert "- Reviewed dispatch blocked reasons: none" in report_text
    assert "- Reviewed dispatch approval status: pending_explicit_approval" in report_text
    assert (
        "- Reviewed dispatch summary: Reviewed dispatch intent is awaiting "
        "explicit approval metadata." in report_text
    )
    assert (
        "- Reviewed dispatch recommended action: Record explicit approval "
        "metadata before opening the next bounded implementation step." in report_text
    )
    assert "- Governed approval metadata: ready_for_recording" in report_text
    assert "- Governed approval blocked reasons: none" in report_text
    assert "- Governed approval review pass recorded: True" in report_text
    assert "- Governed approval quality gate: PASS" in report_text
    assert "- Governed approval source: governed_artifacts_only" in report_text
    assert (
        "- Governed approval summary: Governed approval metadata is ready for "
        "manual approval recording." in report_text
    )
    assert (
        "- Governed approval recommended action: Record explicit manual "
        "approval metadata in governed artifacts before opening the next "
        "bounded implementation step." in report_text
    )
    assert result["resume"]["resumed"] is False


def test_run_autoagent_loop_reports_staged_reviewed_dispatch_intent_before_done_phase(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_state(docs_agents / "state.json", "PASS", phase="Review")
    write_governed_review_report(docs_agents / "review-report.md", "PASS")

    experiment = working_dir / "scheduled-continuation.md"
    write_continuation_policy_experiment(
        experiment,
        "onboarding-helper.agent.md",
        mode="scheduled",
        schedule_cron="0 2 * * *",
        triggers=["review_failure"],
        min_signal_count=2,
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["experiment"]["orchestrationContract"]["status"] == "staged"
    assert result["experiment"]["reviewedDispatchIntent"] == {
        "ready": True,
        "status": "staged_for_review",
        "blockedReasons": [],
        "intentMode": "reviewed_dispatch_intent",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "requiresExplicitApproval": True,
        "approvalStatus": "not_requested",
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "orchestrationContractStatus": "staged",
        "reviewedHandoffStatus": "ready",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Review",
        "intentId": "manual-autoagent-slice::staged_dispatch_simulation::reviewed_dispatch_intent",
        "summary": "Reviewed dispatch intent is staged for manual review.",
        "recommendedAction": (
            "Review the staged dispatch intent and governed artifacts before "
            "requesting explicit approval metadata."
        ),
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["experiment"]["governedApprovalMetadata"] == {
        "ready": False,
        "status": "not_requested",
        "blockedReasons": [],
        "approvalMode": "governed_approval_metadata",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "requiresExplicitApproval": True,
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "readyForRecording": False,
        "reviewPassRecorded": True,
        "reviewPassReadable": True,
        "qualityGateStatus": "PASS",
        "reviewedDispatchIntentStatus": "staged_for_review",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "available",
        "governedTaskId": "manual-autoagent-slice",
        "governedTaskPhase": "Review",
        "metadataId": (
            "manual-autoagent-slice::staged_dispatch_simulation::"
            "reviewed_dispatch_intent::governed_approval_metadata"
        ),
        "summary": "Governed approval metadata is not yet requested.",
        "recommendedAction": (
            "Advance the governed task to Done/PASS and review the dispatch "
            "intent before recording explicit manual approval metadata."
        ),
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Governed task lifecycle: Review" in report_text
    assert "- Reviewed dispatch intent: staged_for_review" in report_text
    assert "- Reviewed dispatch approval status: not_requested" in report_text
    assert (
        "- Reviewed dispatch summary: Reviewed dispatch intent is staged for manual review."
        in report_text
    )
    assert "- Governed approval metadata: not_requested" in report_text
    assert "- Governed approval review pass recorded: True" in report_text
    assert (
        "- Governed approval summary: Governed approval metadata is not yet requested."
        in report_text
    )


@pytest.mark.parametrize(
    ("quality_gate_status", "expected_review_status"),
    [("PENDING", "PENDING"), ("FAIL", "FAIL")],
)
def test_run_autoagent_loop_blocks_continuation_readiness_when_governed_review_not_pass(
    tmp_path: Path,
    quality_gate_status: str,
    expected_review_status: str,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_state(docs_agents / "state.json", quality_gate_status)
    write_governed_review_report(docs_agents / "review-report.md", quality_gate_status)

    experiment = working_dir / "scheduled-continuation.md"
    write_continuation_policy_experiment(
        experiment,
        "onboarding-helper.agent.md",
        mode="scheduled",
        schedule_cron="0 2 * * *",
        triggers=["review_failure"],
        min_signal_count=2,
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["experiment"]["continuationReadiness"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["governed_review_not_pass"],
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "governedReviewStatus": expected_review_status,
        "governedReviewReadable": True,
        "governedReviewSourcePath": (docs_agents / "state.json").as_posix(),
    }
    assert result["experiment"]["reviewedDispatchIntent"]["status"] == "blocked"
    assert result["experiment"]["reviewedDispatchIntent"]["approvalStatus"] == "blocked"
    assert result["experiment"]["governedApprovalMetadata"]["status"] == "blocked"
    assert result["experiment"]["governedApprovalMetadata"]["reviewPassRecorded"] is False


def test_run_autoagent_loop_blocks_continuation_readiness_when_governed_review_sources_disagree(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_state(docs_agents / "state.json", "PASS")
    write_governed_review_report(docs_agents / "review-report.md", "FAIL")

    experiment = working_dir / "scheduled-continuation.md"
    write_continuation_policy_experiment(
        experiment,
        "onboarding-helper.agent.md",
        mode="scheduled",
        schedule_cron="0 2 * * *",
        triggers=["review_failure"],
        min_signal_count=2,
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["experiment"]["governedReviewConsensus"] == {
        "agrees": False,
        "status": "blocked",
        "blockedReasons": ["governed_review_status_mismatch"],
        "stateStatus": "PASS",
        "stateReadable": True,
        "stateSourcePath": (docs_agents / "state.json").as_posix(),
        "reviewReportStatus": "FAIL",
        "reviewReportReadable": True,
        "reviewReportSourcePath": (docs_agents / "review-report.md").as_posix(),
    }
    assert result["experiment"]["continuationReadiness"]["blockedReasons"] == [
        "governed_review_status_mismatch"
    ]


def test_run_autoagent_loop_blocks_continuation_readiness_when_governed_review_report_missing_json(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_state(docs_agents / "state.json", "PASS")
    (docs_agents / "review-report.md").write_text(
        "# Review summary\n\nNo JSON block.\n", encoding="utf-8"
    )

    experiment = working_dir / "scheduled-continuation.md"
    write_continuation_policy_experiment(
        experiment,
        "onboarding-helper.agent.md",
        mode="scheduled",
        schedule_cron="0 2 * * *",
        triggers=["review_failure"],
        min_signal_count=2,
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["experiment"]["governedReviewConsensus"] == {
        "agrees": False,
        "status": "blocked",
        "blockedReasons": ["governed_review_report_unavailable"],
        "stateStatus": "PASS",
        "stateReadable": True,
        "stateSourcePath": (docs_agents / "state.json").as_posix(),
        "reviewReportStatus": "UNAVAILABLE",
        "reviewReportReadable": False,
        "reviewReportSourcePath": (docs_agents / "review-report.md").as_posix(),
    }
    assert result["experiment"]["continuationReadiness"]["blockedReasons"] == [
        "governed_review_report_unavailable"
    ]


def test_run_autoagent_loop_blocks_continuation_readiness_when_governed_review_state_missing(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_review_report(docs_agents / "review-report.md", "PASS")

    experiment = working_dir / "scheduled-continuation.md"
    write_continuation_policy_experiment(
        experiment,
        "onboarding-helper.agent.md",
        mode="scheduled",
        schedule_cron="0 2 * * *",
        triggers=["review_failure"],
        min_signal_count=2,
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["experiment"]["continuationReadiness"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["governed_review_state_unavailable"],
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "governedReviewStatus": "UNAVAILABLE",
        "governedReviewReadable": False,
        "governedReviewSourcePath": (docs_agents / "state.json").as_posix(),
    }
    assert result["experiment"]["governedTaskLifecycle"] == {
        "status": "unavailable",
        "readable": False,
        "sourcePath": (docs_agents / "state.json").as_posix(),
        "taskId": "UNAVAILABLE",
        "taskTitle": "UNAVAILABLE",
        "phase": "UNAVAILABLE",
        "qualityGateStatus": "UNAVAILABLE",
        "nextActionSummary": "UNAVAILABLE",
        "nextActionOwner": "UNAVAILABLE",
        "missingFields": [
            "task.id",
            "task.title",
            "phase",
            "quality_gate.status",
            "next_action.summary",
            "next_action.owner",
        ],
    }
    assert result["experiment"]["reviewedContinuationHandoff"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": [
            "governed_review_state_unavailable",
            "governed_task_lifecycle_unavailable",
        ],
        "handoffMode": "reviewed_manual",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "continuationReadinessStatus": "blocked",
        "governedReviewConsensusStatus": "blocked",
        "governedTaskLifecycleStatus": "unavailable",
        "governedTaskId": "UNAVAILABLE",
        "governedTaskPhase": "UNAVAILABLE",
        "summary": "Not ready for reviewed manual handoff.",
        "recommendedAction": "UNAVAILABLE",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
        },
    }
    assert result["experiment"]["orchestrationContract"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": [
            "governed_review_state_unavailable",
            "governed_task_lifecycle_unavailable",
        ],
        "contractMode": "staged_dispatch_simulation",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "reviewedHandoffStatus": "blocked",
        "governedTaskLifecycleStatus": "unavailable",
        "governedTaskId": "UNAVAILABLE",
        "governedTaskPhase": "UNAVAILABLE",
        "contractId": "UNAVAILABLE::staged_dispatch_simulation",
        "summary": "Staged dispatch simulation is blocked.",
        "recommendedAction": "UNAVAILABLE",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["experiment"]["reviewedDispatchIntent"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": [
            "governed_review_state_unavailable",
            "governed_task_lifecycle_unavailable",
        ],
        "intentMode": "reviewed_dispatch_intent",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "requiresExplicitApproval": True,
        "approvalStatus": "blocked",
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "orchestrationContractStatus": "blocked",
        "reviewedHandoffStatus": "blocked",
        "governedReviewConsensusStatus": "blocked",
        "governedTaskLifecycleStatus": "unavailable",
        "governedTaskId": "UNAVAILABLE",
        "governedTaskPhase": "UNAVAILABLE",
        "intentId": "UNAVAILABLE::staged_dispatch_simulation::reviewed_dispatch_intent",
        "summary": "Reviewed dispatch intent is blocked.",
        "recommendedAction": "UNAVAILABLE",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["experiment"]["governedApprovalMetadata"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": [
            "governed_review_state_unavailable",
            "governed_task_lifecycle_unavailable",
        ],
        "approvalMode": "governed_approval_metadata",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "requiresExplicitApproval": True,
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "readyForRecording": False,
        "reviewPassRecorded": False,
        "reviewPassReadable": False,
        "qualityGateStatus": "UNAVAILABLE",
        "reviewedDispatchIntentStatus": "blocked",
        "governedReviewConsensusStatus": "blocked",
        "governedTaskLifecycleStatus": "unavailable",
        "governedTaskId": "UNAVAILABLE",
        "governedTaskPhase": "UNAVAILABLE",
        "metadataId": (
            "UNAVAILABLE::staged_dispatch_simulation::reviewed_dispatch_intent::"
            "governed_approval_metadata"
        ),
        "summary": "Governed approval metadata is blocked.",
        "recommendedAction": "UNAVAILABLE",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }


def test_run_autoagent_loop_reports_partial_governed_task_lifecycle_when_state_missing_fields(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    (docs_agents / "state.json").write_text(
        json.dumps({"quality_gate": {"status": "PASS"}}, indent=2) + "\n",
        encoding="utf-8",
    )
    write_governed_review_report(docs_agents / "review-report.md", "PASS")

    experiment = working_dir / "scheduled-continuation.md"
    write_continuation_policy_experiment(
        experiment,
        "onboarding-helper.agent.md",
        mode="scheduled",
        schedule_cron="0 2 * * *",
        triggers=["review_failure"],
        min_signal_count=2,
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["experiment"]["governedTaskLifecycle"] == {
        "status": "partial",
        "readable": True,
        "sourcePath": (docs_agents / "state.json").as_posix(),
        "taskId": "UNKNOWN",
        "taskTitle": "UNKNOWN",
        "phase": "UNKNOWN",
        "qualityGateStatus": "PASS",
        "nextActionSummary": "UNKNOWN",
        "nextActionOwner": "UNKNOWN",
        "missingFields": [
            "phase",
            "task.id",
            "task.title",
            "next_action.summary",
            "next_action.owner",
        ],
    }
    assert result["experiment"]["continuationReadiness"] == {
        "ready": True,
        "status": "ready",
        "blockedReasons": [],
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "governedReviewStatus": "PASS",
        "governedReviewReadable": True,
        "governedReviewSourcePath": (docs_agents / "state.json").as_posix(),
    }
    assert result["experiment"]["reviewedContinuationHandoff"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["governed_task_lifecycle_partial"],
        "handoffMode": "reviewed_manual",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "continuationReadinessStatus": "ready",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "partial",
        "governedTaskId": "UNKNOWN",
        "governedTaskPhase": "UNKNOWN",
        "summary": "Not ready for reviewed manual handoff.",
        "recommendedAction": "UNKNOWN",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
        },
    }
    assert result["experiment"]["orchestrationContract"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["governed_task_lifecycle_partial"],
        "contractMode": "staged_dispatch_simulation",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "reviewedHandoffStatus": "blocked",
        "governedTaskLifecycleStatus": "partial",
        "governedTaskId": "UNKNOWN",
        "governedTaskPhase": "UNKNOWN",
        "contractId": "UNKNOWN::staged_dispatch_simulation",
        "summary": "Staged dispatch simulation is blocked.",
        "recommendedAction": "UNKNOWN",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["experiment"]["reviewedDispatchIntent"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["governed_task_lifecycle_partial"],
        "intentMode": "reviewed_dispatch_intent",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "requiresExplicitApproval": True,
        "approvalStatus": "blocked",
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "orchestrationContractStatus": "blocked",
        "reviewedHandoffStatus": "blocked",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "partial",
        "governedTaskId": "UNKNOWN",
        "governedTaskPhase": "UNKNOWN",
        "intentId": "UNKNOWN::staged_dispatch_simulation::reviewed_dispatch_intent",
        "summary": "Reviewed dispatch intent is blocked.",
        "recommendedAction": "UNKNOWN",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    assert result["experiment"]["governedApprovalMetadata"] == {
        "ready": False,
        "status": "blocked",
        "blockedReasons": ["governed_task_lifecycle_partial"],
        "approvalMode": "governed_approval_metadata",
        "manualOnly": True,
        "executionMode": "report_only",
        "reviewGated": True,
        "policyEligible": True,
        "requiresExplicitApproval": True,
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "readyForRecording": False,
        "reviewPassRecorded": True,
        "reviewPassReadable": True,
        "qualityGateStatus": "PASS",
        "reviewedDispatchIntentStatus": "blocked",
        "governedReviewConsensusStatus": "consistent",
        "governedTaskLifecycleStatus": "partial",
        "governedTaskId": "UNKNOWN",
        "governedTaskPhase": "UNKNOWN",
        "metadataId": (
            "UNKNOWN::staged_dispatch_simulation::reviewed_dispatch_intent::"
            "governed_approval_metadata"
        ),
        "summary": "Governed approval metadata is blocked.",
        "recommendedAction": "UNKNOWN",
        "artifactRefs": {
            "state": (docs_agents / "state.json").as_posix(),
            "reviewReport": (docs_agents / "review-report.md").as_posix(),
            "report": (docs_agents / "autoagent-report.md").as_posix(),
            "adr": (
                module.ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }
    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Governed task lifecycle: UNKNOWN" in report_text
    assert (
        "- Governed lifecycle missing fields: phase, task.id, task.title, "
        "next_action.summary, next_action.owner" in report_text
    )
    assert "- Reviewed continuation handoff: blocked" in report_text
    assert "- Reviewed handoff blocked reasons: governed_task_lifecycle_partial" in report_text
    assert "- Orchestration contract: blocked" in report_text
    assert (
        "- Orchestration contract blocked reasons: governed_task_lifecycle_partial" in report_text
    )


@pytest.mark.parametrize(
    (
        "stage_for_review",
        "staged_apply_on_pass",
        "continuous_stage_only",
        "continuous_require_review_pass",
        "apply_best_candidate",
        "apply_best_requested",
        "match",
    ),
    [
        (
            False,
            False,
            True,
            True,
            False,
            False,
            r"Continuous policy requires staged patch review to remain enabled\.",
        ),
        (
            True,
            True,
            True,
            True,
            False,
            False,
            r"Continuous policy requires stagedPatchPolicy\.applyOnPass to remain false\.",
        ),
        (
            True,
            False,
            False,
            True,
            False,
            False,
            r"Continuous policy requires continuousPolicy\.stageOnly to remain true\.",
        ),
        (
            True,
            False,
            True,
            False,
            False,
            False,
            r"Continuous policy requires continuousPolicy\.requireReviewPass to remain true\.",
        ),
        (
            True,
            False,
            True,
            True,
            True,
            False,
            r"Continuous policy requires stage-for-review mode; apply-best is not allowed\.",
        ),
    ],
)
def test_run_autoagent_loop_rejects_unsafe_continuation_policy_settings(
    tmp_path: Path,
    stage_for_review: bool,
    staged_apply_on_pass: bool,
    continuous_stage_only: bool,
    continuous_require_review_pass: bool,
    apply_best_candidate: bool,
    apply_best_requested: bool,
    match: str,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    experiment = working_dir / "unsafe-continuation-settings.md"
    write_continuation_policy_experiment(
        experiment,
        "onboarding-helper.agent.md",
        mode="scheduled",
        schedule_cron="0 2 * * *",
        triggers=["review_failure"],
        min_signal_count=2,
        stage_for_review=stage_for_review,
        staged_apply_on_pass=staged_apply_on_pass,
        continuous_stage_only=continuous_stage_only,
        continuous_require_review_pass=continuous_require_review_pass,
        apply_best_candidate=apply_best_candidate,
    )

    with pytest.raises(ValueError, match=match):
        module.run_autoagent_loop(
            experiment_path=experiment.resolve(),
            output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
            report_path=(docs_agents / "autoagent-report.md").resolve(),
            results_path=(docs_agents / "autoagent-results.tsv").resolve(),
            max_iterations=0,
            apply_best=apply_best_requested,
        )


def test_autoagent_loop_executes_live_evaluator_in_advisory_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    prompt = working_dir / "judge-prompt.md"
    prompt.write_text("Judge prompt.\n", encoding="utf-8")
    rubric = working_dir / "judge-rubric.md"
    rubric.write_text("Judge rubric.\n", encoding="utf-8")
    experiment = working_dir / "advisory-live-evaluator.md"
    write_live_evaluator_experiment(
        experiment,
        "onboarding-helper.agent.md",
        prompt_name=prompt.name,
        rubric_names=[rubric.name],
        strategy="advisory",
        max_samples=2,
    )

    def fake_runner(
        config: dict[str, object], samples: list[dict[str, object]], _experiment: dict[str, object]
    ) -> dict[str, object]:
        assert config["strategy"] == "advisory"
        assert len(samples) == 2
        return {
            "judgments": [
                {
                    "candidateId": samples[0]["candidateId"],
                    "score": 0.1,
                    "verdict": "neutral",
                    "rationale": "Bearer secret-token C:/Outside/advisory.txt",
                    "rawOutput": "Bearer secret-token C:/Outside/advisory.txt",
                },
                {
                    "candidateId": samples[1]["candidateId"],
                    "score": 0.9,
                    "verdict": "prefer",
                    "rationale": "Keeps the manager-led workflow guidance.",
                },
            ]
        }

    monkeypatch.setitem(module.LIVE_EVALUATOR_RUNNERS, "github-models", fake_runner)

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["bestCandidate"]["candidateId"] == "trim-intro"
    assert result["liveEvaluation"]["status"] == "succeeded"
    assert result["liveEvaluation"]["strategy"] == "advisory"
    assert result["liveEvaluation"]["sampleCount"] == 2
    assert result["liveEvaluation"]["bestCandidateChanged"] is False
    assert result["liveEvaluation"]["winnerCandidateId"] == "trim-intro"

    serialized = json.dumps(result["liveEvaluation"])
    assert "secret-token" not in serialized
    assert "advisory.txt" not in serialized
    assert "rawOutput" not in serialized
    assert "[external-path]" in serialized


def test_autoagent_loop_uses_live_evaluator_for_tie_breaker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "tie-breaker.agent.md"
    target.write_text("---\nname: Tie Breaker\n---\n\nOriginal text.\n", encoding="utf-8")
    prompt = working_dir / "judge-prompt.md"
    prompt.write_text("Judge prompt.\n", encoding="utf-8")
    rubric = working_dir / "judge-rubric.md"
    rubric.write_text("Judge rubric.\n", encoding="utf-8")

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "requirement",
                        "type": "contains_text",
                        "target": "body",
                        "value": "Documented requirement",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First tied candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "Original text.",
                                "new": "Documented requirement A",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second tied candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "Documented requirement A",
                                "new": "Documented requirement B",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "tie-breaker-experiment.md"
    write_live_evaluator_experiment(
        experiment,
        target.name,
        prompt_name=prompt.name,
        rubric_names=[rubric.name],
        strategy="tie_breaker",
        max_samples=2,
        record_raw_outputs=True,
    )

    def fake_runner(
        _config: dict[str, object], samples: list[dict[str, object]], _experiment: dict[str, object]
    ) -> dict[str, object]:
        return {
            "judgments": [
                {
                    "candidateId": sample["candidateId"],
                    "score": 0.95 if sample["candidateId"] == "candidate-b" else 0.1,
                    "verdict": "prefer" if sample["candidateId"] == "candidate-b" else "neutral",
                    "rationale": f"Judge preferred {sample['candidateId']}.",
                    "rawOutput": f"Bearer secret-token C:/Outside/{sample['candidateId']}.txt",
                }
                for sample in samples
            ]
        }

    monkeypatch.setitem(module.LIVE_EVALUATOR_RUNNERS, "github-models", fake_runner)

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    checkpoint = json.loads(
        Path(result["artifacts"]["checkpoint"]["actualPath"]).read_text(encoding="utf-8")
    )
    manifest = json.loads(
        Path(result["artifacts"]["checkpointManifest"]["actualPath"]).read_text(encoding="utf-8")
    )

    assert result["liveEvaluation"]["status"] == "succeeded"
    assert result["liveEvaluation"]["strategy"] == "tie_breaker"
    assert result["liveEvaluation"]["tieBreakerApplied"] is True
    assert result["liveEvaluation"]["bestCandidateChanged"] is True
    assert result["liveEvaluation"]["winnerCandidateId"] == "candidate-b"
    assert result["bestCandidate"]["candidateId"] == "candidate-b"
    assert result["resume"]["checkpointStage"] == "post_mutation_search"
    assert result["provenance"]["artifacts"]["checkpointStage"] == "post_mutation_search"
    assert checkpoint["resumeStage"] == "post_mutation_search"
    assert checkpoint["deterministicBestCandidateId"] == "candidate-a"
    assert manifest["resumeStage"] == "post_mutation_search"
    assert manifest["deterministicBestCandidateId"] == "candidate-a"

    serialized = json.dumps(result["liveEvaluation"])
    assert "secret-token" not in serialized
    assert "candidate-b.txt" not in serialized
    assert "[external-path]" in serialized
    assert "rawOutput" in serialized


def test_autoagent_loop_uses_trajectory_score_to_break_deterministic_ties(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "trajectory-rank.agent.md"
    target.write_text("---\nname: Trajectory Rank\n---\n\nSeed text.\n", encoding="utf-8")

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "heavy",
                        "type": "contains_text",
                        "target": "body",
                        "value": "ABCD EFGH",
                        "weight": 2,
                    },
                    {
                        "id": "breadth-a",
                        "type": "contains_text",
                        "target": "body",
                        "value": "IJKL",
                        "weight": 1,
                    },
                    {
                        "id": "breadth-b",
                        "type": "contains_text",
                        "target": "body",
                        "value": "MNOP",
                        "weight": 1,
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "Hit the high-weight requirement only.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "Seed text.",
                                "new": "ABCD EFGH",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Cover more benchmark checks at the same weighted score.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "ABCD EFGH",
                                "new": "IJKL MNOP",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "trajectory-ranking-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: trajectory-ranking-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    candidate_a = next(row for row in result["iterations"] if row["candidateId"] == "candidate-a")
    candidate_b = next(row for row in result["iterations"] if row["candidateId"] == "candidate-b")
    assert candidate_a["score"] == 0.5
    assert candidate_b["score"] == 0.5
    assert candidate_a["complexity"]["score"] == candidate_b["complexity"]["score"]
    assert candidate_b["trajectoryScore"] > candidate_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-b"
    assert result["bestCandidate"]["trajectoryScore"] == candidate_b["trajectoryScore"]
    assert result["candidateSearch"]["rankingSignals"] == [
        "benchmark_score",
        "complexity",
        "trajectory_score",
    ]
    explanation = result["candidateSearch"]["winnerExplanation"]
    assert explanation["decisiveSignal"] == "trajectory_score"
    assert explanation["evidenceBacked"] is False
    assert explanation["comparedCandidateId"] == "candidate-a"
    assert explanation["rankingComparison"]["trajectoryScoreDelta"] == round(
        candidate_b["trajectoryScore"] - candidate_a["trajectoryScore"],
        6,
    )
    assert explanation["trajectorySummary"].startswith("Top trajectory contributors: ")
    assert explanation["topTrajectorySignals"]
    assert explanation["topTrajectorySignals"][0]["advantage"] > 0
    assert explanation["evidenceComparison"]["winnerSourceKinds"] == {}
    assert explanation["evidenceComparison"]["runnerUpSourceKinds"] == {}

    ledger = json.loads(
        Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    candidate_b_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-b"
    )
    assert candidate_b_node["trajectoryScore"] == candidate_b["trajectoryScore"]

    results_text = Path(result["artifacts"]["results"]["actualPath"]).read_text(encoding="utf-8")
    assert "trajectory_score" in results_text.splitlines()[0]


def test_autoagent_loop_uses_candidate_evidence_to_break_exact_ties(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "evidence-rank.agent.md"
    target.write_text("---\nname: Evidence Rank\n---\n\nBASE\n", encoding="utf-8")

    debug_log = tmp_path / "logs" / "trajectory-evidence.log"
    debug_log.parent.mkdir(parents=True, exist_ok=True)
    debug_log.write_text(
        "ERROR candidate-a tool failure\nSUCCESS candidate-b--from--baseline validated cleanly\n",
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second exact-tie candidate with cleaner evidence.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "trajectory-evidence-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: trajectory-evidence-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeVsCodeLogs: true",
                "  vsCodeLogPaths:",
                f"    - {debug_log.as_posix()}",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    candidate_a = next(row for row in result["iterations"] if row["candidateId"] == "candidate-a")
    candidate_b = next(
        row for row in result["iterations"] if row["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a["score"] == candidate_b["score"] == 1.0
    assert candidate_a["complexity"]["score"] == candidate_b["complexity"]["score"]
    assert candidate_b["trajectoryScore"] > candidate_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-b--from--baseline"
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["matchedRecordCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["successCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["errorCount"] == 0
    explanation = result["candidateSearch"]["winnerExplanation"]
    assert explanation["decisiveSignal"] == "trajectory_score"
    assert explanation["evidenceBacked"] is True
    assert explanation["comparedCandidateId"] == "candidate-a"
    assert explanation["trajectorySummary"].startswith("Top trajectory contributors: ")
    assert explanation["evidenceComparison"]["winnerSourceKinds"] == {"external_log": 1}
    assert explanation["evidenceComparison"]["runnerUpSourceKinds"] == {"external_log": 1}
    assert explanation["evidenceComparison"]["winnerStatuses"] == {"success": 1}
    assert explanation["evidenceComparison"]["runnerUpStatuses"] == {"error": 1}

    ledger = json.loads(
        Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    candidate_a_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-a"
    )
    candidate_b_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a_node["trajectoryEvidenceErrors"] == 1
    assert candidate_b_node["trajectoryEvidenceSuccesses"] == 1


def test_autoagent_loop_uses_session_audit_evidence_to_break_exact_ties(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "session-evidence-rank.agent.md"
    target.write_text("---\nname: Session Evidence Rank\n---\n\nBASE\n", encoding="utf-8")

    historical_run = docs_agents / "runs" / "20260403-030303"
    (historical_run / "hook-audit").mkdir(parents=True, exist_ok=True)
    (historical_run / "hook-audit" / "session.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 1,
                        "event": "toolCall",
                        "status": "error",
                        "toolName": "apply_patch",
                        "candidateId": "candidate-a",
                        "message": "candidate-a failed validation",
                    }
                ),
                json.dumps(
                    {
                        "ts": 2,
                        "event": "toolCall",
                        "status": "success",
                        "toolName": "read_file",
                        "candidateId": "candidate-b--from--baseline",
                        "message": "candidate-b--from--baseline validated cleanly",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (historical_run / "hook-audit" / "session-summary.json").write_text(
        json.dumps(
            {
                "ts": 3,
                "event": "sessionEnd",
                "audit": {
                    "totalEvents": 2,
                    "denies": 0,
                    "errors": 1,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second exact-tie candidate with cleaner session evidence.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "session-trajectory-evidence-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: session-trajectory-evidence-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: true",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    candidate_a = next(row for row in result["iterations"] if row["candidateId"] == "candidate-a")
    candidate_b = next(
        row for row in result["iterations"] if row["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a["score"] == candidate_b["score"] == 1.0
    assert candidate_a["complexity"]["score"] == candidate_b["complexity"]["score"]
    assert candidate_b["trajectoryScore"] > candidate_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-b--from--baseline"
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["matchedRecordCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["successCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["sourceKindCounts"] == {
        "session_event": 1
    }
    explanation = result["candidateSearch"]["winnerExplanation"]
    assert explanation["decisiveSignal"] == "trajectory_score"
    assert explanation["evidenceBacked"] is True
    assert explanation["comparedCandidateId"] == "candidate-a"
    assert explanation["trajectorySummary"].startswith("Top trajectory contributors: ")
    assert explanation["evidenceComparison"]["winnerSourceKinds"] == {"session_event": 1}
    assert explanation["evidenceComparison"]["runnerUpSourceKinds"] == {"session_event": 1}
    assert explanation["evidenceComparison"]["winnerStatuses"] == {"success": 1}
    assert explanation["evidenceComparison"]["runnerUpStatuses"] == {"error": 1}

    evidence = json.loads((docs_agents / "autoagent-evidence.json").read_text(encoding="utf-8"))
    assert evidence["summary"]["sessionRecordCount"] == 3
    assert evidence["summary"]["recordsByKind"]["session_event"] == 2
    assert evidence["summary"]["recordsByKind"]["session_summary"] == 1
    assert any(path.endswith("session.jsonl") for path in evidence["sources"]["sessionArtifacts"])
    assert any(
        path.endswith("session-summary.json") for path in evidence["sources"]["sessionArtifacts"]
    )

    ledger = json.loads(
        Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    candidate_a_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-a"
    )
    candidate_b_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a_node["trajectoryEvidenceErrors"] == 1
    assert candidate_b_node["trajectoryEvidenceSuccesses"] == 1

    trace = json.loads(Path(result["artifacts"]["trace"]["actualPath"]).read_text(encoding="utf-8"))
    best_episode = next(
        episode
        for episode in trace["episodes"]
        if episode["candidateId"] == "candidate-b--from--baseline"
    )
    assert trace["learning"]["mode"] == "shadow_only"
    assert trace["learning"]["episodeCount"] == trace["summary"]["episodeCount"]
    assert trace["learning"]["evidenceBackedEpisodeCount"] == 2
    assert any(
        candidate["kind"] == "episode_success_guard" and candidate["toolNames"] == ["read_file"]
        for candidate in trace["learning"]["benchmarkCandidates"]
    )
    assert any(
        seed["kind"] == "reinforce_success_path"
        and seed["candidateId"] == "candidate-b--from--baseline"
        and seed["toolNames"] == ["read_file"]
        for seed in trace["learning"]["mutationSeedCandidates"]
    )
    assert any(
        candidate["kind"] == "preferred_tool_sequence"
        and candidate["toolSequence"] == ["read_file"]
        for candidate in trace["learning"]["policyCandidates"]
    )
    assert any(
        candidate["kind"] == "escalation_trigger" and candidate["triggerTools"] == ["apply_patch"]
        for candidate in trace["learning"]["policyCandidates"]
    )
    benchmark_drafts_path = Path(result["learningArtifacts"]["benchmarkDraftsPath"])
    mutation_drafts_path = Path(result["learningArtifacts"]["mutationDraftsPath"])
    policy_drafts_path = Path(result["learningArtifacts"]["policyDraftsPath"])
    assert benchmark_drafts_path.exists()
    assert mutation_drafts_path.exists()
    assert policy_drafts_path.exists()
    benchmark_drafts = json.loads(benchmark_drafts_path.read_text(encoding="utf-8"))
    mutation_drafts = json.loads(mutation_drafts_path.read_text(encoding="utf-8"))
    policy_drafts = json.loads(policy_drafts_path.read_text(encoding="utf-8"))
    assert benchmark_drafts["mode"] == "review_only"
    assert benchmark_drafts["draftFragmentCount"] >= 1
    assert any(
        fragment["kind"] == "episode_success_guard"
        and fragment["fragment"]["suggestedChecks"][0]["toolNames"] == ["read_file"]
        for fragment in benchmark_drafts["draftFragments"]
    )
    assert mutation_drafts["mode"] == "review_only"
    assert mutation_drafts["draftEntryCount"] >= 1
    assert any(
        entry["kind"] == "reinforce_success_path"
        and entry["entry"]["sourceMutationId"] == "candidate-b"
        and entry["entry"]["preferredTools"] == ["read_file"]
        for entry in mutation_drafts["draftEntries"]
    )
    assert policy_drafts["mode"] == "review_only"
    assert policy_drafts["draftEntryCount"] >= 1
    assert any(
        entry["kind"] == "preferred_tool_sequence"
        and entry["entry"]["preferredToolSequence"] == ["read_file"]
        for entry in policy_drafts["draftEntries"]
    )
    assert any(
        entry["kind"] == "escalation_trigger" and entry["entry"]["triggerTools"] == ["apply_patch"]
        for entry in policy_drafts["draftEntries"]
    )
    assert trace["summary"]["episodeCount"] == len(trace["episodes"])
    assert trace["summary"]["evidenceBackedEpisodeCount"] == 2
    assert best_episode["summary"]["matchedRecordCount"] == 1
    assert best_episode["summary"]["sourceKindCounts"] == {"session_event": 1}
    assert best_episode["summary"]["toolNames"] == ["read_file"]
    assert best_episode["steps"][0]["status"] == "success"
    assert best_episode["steps"][0]["candidateIds"] == ["candidate-b--from--baseline"]
    assert best_episode["steps"][0]["transcriptText"] is None


def test_autoagent_loop_imports_approved_learning_drafts_with_review_manifest(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    historical_run = docs_agents / "runs" / "historical-run"
    historical_run.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_state(docs_agents / "state.json", "PASS")
    write_governed_review_report(docs_agents / "review-report.md", "PASS")

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "session-learning-import.agent.md"
    target.write_text("---\nname: Session Import\n---\n\nBASE\n", encoding="utf-8")

    (historical_run / "hook-audit").mkdir(parents=True, exist_ok=True)
    (historical_run / "hook-audit" / "session.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 1,
                        "event": "toolCall",
                        "status": "error",
                        "toolName": "apply_patch",
                        "candidateId": "candidate-a",
                        "message": "candidate-a failed validation",
                    }
                ),
                json.dumps(
                    {
                        "ts": 2,
                        "event": "toolCall",
                        "status": "success",
                        "toolName": "read_file",
                        "candidateId": "candidate-b--from--baseline",
                        "message": "candidate-b--from--baseline validated cleanly",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (historical_run / "hook-audit" / "session-summary.json").write_text(
        json.dumps(
            {
                "ts": 3,
                "event": "sessionEnd",
                "audit": {
                    "totalEvents": 2,
                    "denies": 0,
                    "errors": 1,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second exact-tie candidate with cleaner session evidence.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "session-learning-import-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: session-learning-import-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: true",
            ]
        ),
    )

    output_root = (tmp_path / "generated" / "autoagent-runs").resolve()
    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=output_root,
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )
    assert result["reviewedContinuationPackage"] == {
        "status": "artifact_missing",
        "bundlePath": (
            output_root / experiment.stem / "reviewed-continuation-bundle.json"
        ).as_posix(),
        "bundleFound": False,
        "acceptedBenchmarkDraftCount": 0,
        "acceptedMutationDraftCount": 0,
        "acceptedPolicyDraftCount": 0,
        "acceptedTotalCount": 0,
        "traceSourceOrigins": [],
        "governedTraceExportRunIds": [],
        "manualDispatchStatus": "artifact_missing",
        "manualDispatchPath": (
            output_root / experiment.stem / "manual-dispatch.generated.json"
        ).as_posix(),
        "manualDispatchFound": False,
        "manualDispatchBlockedReasons": [],
        "requiredHumanAction": None,
        "followOnExperimentPath": None,
        "launchCommand": None,
    }

    benchmark_drafts = json.loads(
        Path(result["learningArtifacts"]["benchmarkDraftsPath"]).read_text(encoding="utf-8")
    )
    mutation_drafts = json.loads(
        Path(result["learningArtifacts"]["mutationDraftsPath"]).read_text(encoding="utf-8")
    )
    policy_drafts = json.loads(
        Path(result["learningArtifacts"]["policyDraftsPath"]).read_text(encoding="utf-8")
    )
    accepted_benchmark_draft = benchmark_drafts["draftFragments"][0]
    accepted_mutation_draft = next(
        entry for entry in mutation_drafts["draftEntries"] if entry["entry"].get("sourceMutationId")
    )
    accepted_policy_draft = next(
        entry
        for entry in policy_drafts["draftEntries"]
        if entry["kind"] == "preferred_tool_sequence"
    )

    review_manifest = {
        "type": "AutoAgentLearningReview",
        "reviewer": "human-maintainer",
        "reviewedAt": "2026-01-01T00:00:00Z",
        "summary": "Approve one benchmark fragment and one mutation draft.",
        "benchmarkDrafts": [
            {
                "draftId": accepted_benchmark_draft["draftId"],
                "stagedDecision": "accept",
                "decision": "accept",
                "decisionRationale": {
                    "observedCount": 2,
                    "observedCountThreshold": 1,
                    "observedCountPass": True,
                    "observedCountDelta": 1,
                    "blockedByFactors": [],
                    "primaryBlockedFactor": None,
                },
                "notes": "Promote the generated episode observation guard.",
            }
        ],
        "mutationDrafts": [
            {
                "draftId": accepted_mutation_draft["draftId"],
                "stagedDecision": "accept",
                "decision": "accept",
                "decisionRationale": {
                    "sourceMutationId": accepted_mutation_draft["entry"]["sourceMutationId"],
                    "blockedByFactors": [],
                    "primaryBlockedFactor": None,
                },
                "notes": "Promote the successful path as an executable mutation clone.",
            }
        ],
        "policyDrafts": [
            {
                "draftId": accepted_policy_draft["draftId"],
                "stagedDecision": "defer",
                "decision": "accept",
                "decisionRationale": {
                    "observedCount": accepted_policy_draft["entry"]["observedCount"],
                    "observedCountThreshold": accepted_policy_draft["entry"]["observedCount"] + 1,
                    "observedCountPass": False,
                    "observedCountDelta": -1,
                    "learningScore": accepted_policy_draft["entry"]["learningScore"],
                    "learningScoreThreshold": 0.7,
                    "learningScorePass": True,
                    "learningScoreDelta": accepted_policy_draft["entry"]["learningScore"] - 0.7,
                    "blockedByFactors": ["observedCount"],
                    "primaryBlockedFactor": "observedCount",
                },
                "notes": "Promote the reviewed preferred tool sequence policy.",
            }
        ],
    }
    review_path = working_dir / "learning-review.json"
    review_path.write_text(json.dumps(review_manifest, indent=2), encoding="utf-8")

    import_result = module.import_learning_review(
        experiment_path=experiment.resolve(),
        output_root=output_root,
        review_path=review_path.resolve(),
    )

    assert import_result["mode"] == "manual_review_import"
    assert import_result["summary"]["acceptedBenchmarkDraftCount"] == 1
    assert import_result["summary"]["importedBenchmarkCheckCount"] == 1
    assert import_result["summary"]["acceptedMutationDraftCount"] == 1
    assert import_result["summary"]["importedMutationCount"] == 1
    assert import_result["summary"]["acceptedPolicyDraftCount"] == 1
    assert import_result["summary"]["importedPolicyCount"] == 1

    promoted_benchmark = json.loads(
        Path(import_result["artifacts"]["promotedBenchmark"]["actualPath"]).read_text(
            encoding="utf-8"
        )
    )
    imported_check = next(
        check
        for check in promoted_benchmark["checks"]
        if check["id"] == accepted_benchmark_draft["fragment"]["suggestedChecks"][0]["id"]
    )
    assert imported_check == {
        "id": accepted_benchmark_draft["fragment"]["suggestedChecks"][0]["id"],
        "type": "episode_observation_guard",
        "sourceKinds": ["session_event"],
        "toolNames": ["read_file"],
        "terminalStatus": "success",
        "minMatchedRecordCount": 1,
        "weight": 0.25,
        "intent": "Preserve the observed successful path pattern.",
    }
    assert promoted_benchmark["approvedLearningDrafts"] == [
        {
            "draftId": accepted_benchmark_draft["draftId"],
            "sourceSuggestionId": accepted_benchmark_draft["sourceSuggestionId"],
            "reviewer": "human-maintainer",
            "reviewedAt": "2026-01-01T00:00:00Z",
            "notes": "Promote the generated episode observation guard.",
            "addedCheckIds": [accepted_benchmark_draft["fragment"]["suggestedChecks"][0]["id"]],
        }
    ]

    promoted_mutations = json.loads(
        Path(import_result["artifacts"]["promotedMutations"]["actualPath"]).read_text(
            encoding="utf-8"
        )
    )
    source_mutation = next(
        mutation
        for mutation in json.loads((working_dir / "mutations.json").read_text(encoding="utf-8"))[
            "mutations"
        ]
        if mutation["id"] == accepted_mutation_draft["entry"]["sourceMutationId"]
    )
    promoted_mutation = next(
        mutation
        for mutation in promoted_mutations["mutations"]
        if mutation["id"] == accepted_mutation_draft["entry"]["id"]
    )
    assert promoted_mutation["operations"] == source_mutation["operations"]
    assert promoted_mutation["description"] == accepted_mutation_draft["entry"]["description"]
    assert promoted_mutation["learningImportMetadata"] == {
        "draftId": accepted_mutation_draft["draftId"],
        "sourceSeedId": accepted_mutation_draft["sourceSeedId"],
        "sourceMutationId": accepted_mutation_draft["entry"]["sourceMutationId"],
        "sourceCandidateId": accepted_mutation_draft["entry"]["sourceCandidateId"],
        "sourceEpisodeId": accepted_mutation_draft["entry"]["sourceEpisodeId"],
        "reviewer": "human-maintainer",
        "reviewedAt": "2026-01-01T00:00:00Z",
        "notes": "Promote the successful path as an executable mutation clone.",
    }
    assert promoted_mutations["approvedLearningDrafts"] == [
        {
            "draftId": accepted_mutation_draft["draftId"],
            "promotedMutationId": accepted_mutation_draft["entry"]["id"],
            "sourceSeedId": accepted_mutation_draft["sourceSeedId"],
            "sourceMutationId": accepted_mutation_draft["entry"]["sourceMutationId"],
            "reviewer": "human-maintainer",
            "reviewedAt": "2026-01-01T00:00:00Z",
            "notes": "Promote the successful path as an executable mutation clone.",
        }
    ]
    promoted_policies = json.loads(
        Path(import_result["artifacts"]["promotedPolicies"]["actualPath"]).read_text(
            encoding="utf-8"
        )
    )
    promoted_policy = next(
        policy
        for policy in promoted_policies["policies"]
        if policy["id"] == accepted_policy_draft["entry"]["id"]
    )
    assert promoted_policy["preferredToolSequence"] == ["read_file"]
    assert promoted_policy["preferredTools"] == ["read_file"]
    assert promoted_policy["learningImportMetadata"] == {
        "draftId": accepted_policy_draft["draftId"],
        "sourcePolicyId": accepted_policy_draft["sourcePolicyId"],
        "reviewer": "human-maintainer",
        "reviewedAt": "2026-01-01T00:00:00Z",
        "notes": "Promote the reviewed preferred tool sequence policy.",
    }
    assert promoted_policies["approvedLearningDrafts"] == [
        {
            "draftId": accepted_policy_draft["draftId"],
            "promotedPolicyId": accepted_policy_draft["entry"]["id"],
            "sourcePolicyId": accepted_policy_draft["sourcePolicyId"],
            "reviewer": "human-maintainer",
            "reviewedAt": "2026-01-01T00:00:00Z",
            "notes": "Promote the reviewed preferred tool sequence policy.",
        }
    ]
    assert Path(import_result["artifacts"]["importReport"]["actualPath"]).exists()
    assert Path(import_result["artifacts"]["promotionAudit"]["actualPath"]).exists()
    assert Path(import_result["artifacts"]["continuationBundle"]["actualPath"]).exists()
    assert Path(import_result["artifacts"]["manualDispatchManifest"]["actualPath"]).exists()
    assert Path(import_result["artifacts"]["followOnExperiment"]["actualPath"]).exists()

    continuation_bundle = json.loads(
        Path(import_result["artifacts"]["continuationBundle"]["actualPath"]).read_text(
            encoding="utf-8"
        )
    )
    assert continuation_bundle["type"] == "AutoAgentReviewedContinuationBundle"
    assert continuation_bundle["status"] == "ready"
    assert continuation_bundle["summary"] == {
        "acceptedBenchmarkDraftCount": 1,
        "acceptedMutationDraftCount": 1,
        "acceptedPolicyDraftCount": 1,
        "acceptedTotalCount": 3,
        "targetCount": 1,
        "targetIds": ["primary"],
    }
    assert continuation_bundle["experiment"]["primaryTargetId"] == "primary"
    assert continuation_bundle["accepted"]["benchmarkDrafts"][0]["traceProvenance"] == deepcopy(
        accepted_benchmark_draft["fragment"]["traceProvenance"]
    )
    assert continuation_bundle["accepted"]["mutationDrafts"][0]["traceProvenance"] == deepcopy(
        accepted_mutation_draft["entry"]["traceProvenance"]
    )
    assert continuation_bundle["accepted"]["policyDrafts"][0]["traceProvenance"] == deepcopy(
        accepted_policy_draft["entry"]["traceProvenance"]
    )

    manual_dispatch_manifest = json.loads(
        Path(import_result["artifacts"]["manualDispatchManifest"]["actualPath"]).read_text(
            encoding="utf-8"
        )
    )
    assert manual_dispatch_manifest["type"] == "AutoAgentManualDispatchManifest"
    assert manual_dispatch_manifest["status"] == "ready_for_manual_dispatch"
    assert manual_dispatch_manifest["blockedReasons"] == []
    assert manual_dispatch_manifest["manualOnly"] is True
    assert manual_dispatch_manifest["reportOnly"] is True
    assert manual_dispatch_manifest["requiresHumanLaunch"] is True
    assert manual_dispatch_manifest["approvalSource"] == "governed_artifacts_only"
    assert (
        manual_dispatch_manifest["bundlePath"]
        == import_result["artifacts"]["continuationBundle"]["actualPath"]
    )
    assert (
        manual_dispatch_manifest["followOnExperimentPath"]
        == import_result["artifacts"]["followOnExperiment"]["actualPath"]
    )
    assert "--experiment" in str(manual_dispatch_manifest["launchCommand"])

    follow_on_experiment = module.load_experiment(
        Path(import_result["artifacts"]["followOnExperiment"]["actualPath"])
    )
    assert (
        follow_on_experiment["benchmarkPath"].as_posix()
        == import_result["artifacts"]["promotedBenchmark"]["actualPath"]
    )
    assert (
        follow_on_experiment["mutationCatalogPath"].as_posix()
        == import_result["artifacts"]["promotedMutations"]["actualPath"]
    )
    assert follow_on_experiment["reviewedPolicyRuntime"]["enabled"] is True
    assert (
        follow_on_experiment["reviewedPolicyRuntime"]["artifactPath"].as_posix()
        == import_result["artifacts"]["promotedPolicies"]["actualPath"]
    )

    promotion_audit = json.loads(
        Path(import_result["artifacts"]["promotionAudit"]["actualPath"]).read_text(encoding="utf-8")
    )
    assert promotion_audit["type"] == "AutoAgentLearningPromotionAudit"
    assert promotion_audit["guardrails"] == {
        "reviewRequired": True,
        "runtimeEffect": "review_only",
        "autoApplyEnabled": False,
    }
    assert promotion_audit["summary"]["acceptedBenchmarkDraftCount"] == 1
    assert promotion_audit["summary"]["acceptedMutationDraftCount"] == 1
    assert promotion_audit["summary"]["acceptedPolicyDraftCount"] == 1

    benchmark_decision = promotion_audit["decisions"]["benchmarkDrafts"][0]
    assert benchmark_decision["draftId"] == accepted_benchmark_draft["draftId"]
    assert benchmark_decision["stagedDecision"] == "accept"
    assert benchmark_decision["decision"] == "accept"
    assert benchmark_decision["reviewerOverride"] is False
    assert (
        benchmark_decision["sourceSuggestionId"] == accepted_benchmark_draft["sourceSuggestionId"]
    )
    assert benchmark_decision["decisionRationale"] == {
        "observedCount": 2,
        "observedCountThreshold": 1,
        "observedCountPass": True,
        "observedCountDelta": 1,
        "blockedByFactors": [],
        "primaryBlockedFactor": None,
    }

    mutation_decision = promotion_audit["decisions"]["mutationDrafts"][0]
    assert mutation_decision["draftId"] == accepted_mutation_draft["draftId"]
    assert mutation_decision["stagedDecision"] == "accept"
    assert mutation_decision["decision"] == "accept"
    assert mutation_decision["reviewerOverride"] is False
    assert mutation_decision["sourceSeedId"] == accepted_mutation_draft["sourceSeedId"]
    assert (
        mutation_decision["sourceMutationId"]
        == accepted_mutation_draft["entry"]["sourceMutationId"]
    )

    policy_decision = promotion_audit["decisions"]["policyDrafts"][0]
    assert policy_decision["draftId"] == accepted_policy_draft["draftId"]
    assert policy_decision["stagedDecision"] == "defer"
    assert policy_decision["decision"] == "accept"
    assert policy_decision["reviewerOverride"] is True
    assert policy_decision["sourcePolicyId"] == accepted_policy_draft["sourcePolicyId"]
    assert policy_decision["decisionRationale"] == {
        "observedCount": accepted_policy_draft["entry"]["observedCount"],
        "observedCountThreshold": accepted_policy_draft["entry"]["observedCount"] + 1,
        "observedCountPass": False,
        "observedCountDelta": -1,
        "learningScore": accepted_policy_draft["entry"]["learningScore"],
        "learningScoreThreshold": 0.7,
        "learningScorePass": True,
        "learningScoreDelta": accepted_policy_draft["entry"]["learningScore"] - 0.7,
        "blockedByFactors": ["observedCount"],
        "primaryBlockedFactor": "observedCount",
    }

    rerun_result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=output_root,
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert rerun_result["learningPromotionAudit"] == {
        "status": "ready",
        "artifactPath": import_result["artifacts"]["promotionAudit"]["actualPath"],
        "artifactFound": True,
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
        "blockedFactorCounts": {"observedCount": 1},
        "benchmarkBlockedFactorCounts": {},
        "mutationBlockedFactorCounts": {},
        "policyBlockedFactorCounts": {"observedCount": 1},
    }
    assert rerun_result["reviewedContinuationPackage"] == {
        "status": "ready",
        "bundlePath": import_result["artifacts"]["continuationBundle"]["actualPath"],
        "bundleFound": True,
        "acceptedBenchmarkDraftCount": 1,
        "acceptedMutationDraftCount": 1,
        "acceptedPolicyDraftCount": 1,
        "acceptedTotalCount": 3,
        "traceSourceOrigins": [],
        "governedTraceExportRunIds": [],
        "manualDispatchStatus": "ready_for_manual_dispatch",
        "manualDispatchPath": import_result["artifacts"]["manualDispatchManifest"]["actualPath"],
        "manualDispatchFound": True,
        "manualDispatchBlockedReasons": [],
        "requiredHumanAction": (
            "Review the generated follow-on experiment and launch it manually "
            "with the provided command."
        ),
        "followOnExperimentPath": import_result["artifacts"]["followOnExperiment"]["actualPath"],
        "launchCommand": manual_dispatch_manifest["launchCommand"],
    }

    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Learning promotion audit: ready" in report_text
    assert (
        "- Learning promotion audit artifact: "
        f"{import_result['artifacts']['promotionAudit']['actualPath']}"
    ) in report_text
    assert "- Learning promotion audit source mode: manual_review" in report_text
    assert "- Learning promotion audit reviewer overrides: 1" in report_text
    assert (
        "- Learning promotion audit benchmark decisions: "
        "reviewed 1, accepted 1, rejected 0, deferred 0"
    ) in report_text
    assert (
        "- Learning promotion audit mutation decisions: "
        "reviewed 1, accepted 1, rejected 0, deferred 0"
    ) in report_text
    assert (
        "- Learning promotion audit policy decisions: "
        "reviewed 1, accepted 1, rejected 0, deferred 0"
    ) in report_text
    assert "- Learning promotion audit blocked factors: observedCount 1" in report_text
    assert "- Learning promotion audit benchmark blocked factors: none" in report_text
    assert "- Learning promotion audit mutation blocked factors: none" in report_text
    assert "- Reviewed continuation package: ready" in report_text
    assert (
        "- Reviewed continuation bundle artifact: "
        f"{import_result['artifacts']['continuationBundle']['actualPath']}"
    ) in report_text
    assert (
        "- Reviewed continuation accepted items: benchmark 1, mutations 1, policies 1"
        in report_text
    )
    assert "- Reviewed continuation trace origins: none" in report_text
    assert "- Manual dispatch manifest: ready_for_manual_dispatch" in report_text
    assert "- Manual dispatch blocked reasons: none" in report_text
    assert (
        "- Manual dispatch required action: "
        "Review the generated follow-on experiment and launch it manually with the "
        "provided command." in report_text
    )
    assert (
        "- Manual dispatch follow-on experiment: "
        f"{import_result['artifacts']['followOnExperiment']['actualPath']}"
    ) in report_text
    assert "- Manual dispatch launch command: py -3 " in report_text
    assert "- Learning promotion audit policy blocked factors: observedCount 1" in report_text


def test_autoagent_loop_uses_reviewed_preferred_tool_sequence_to_break_success_ties(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    historical_run = docs_agents / "runs" / "20260411-010101"
    (historical_run / "hook-audit").mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "reviewed-policy-rank.agent.md"
    target.write_text("---\nname: Reviewed Policy Rank\n---\n\nBASE\n", encoding="utf-8")

    (historical_run / "hook-audit" / "session.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 1,
                        "event": "toolCall",
                        "status": "success",
                        "toolName": "apply_patch",
                        "candidateId": "candidate-a",
                        "message": "candidate-a completed cleanly",
                    }
                ),
                json.dumps(
                    {
                        "ts": 2,
                        "event": "toolCall",
                        "status": "success",
                        "toolName": "read_file",
                        "candidateId": "candidate-b--from--baseline",
                        "message": "candidate-b--from--baseline completed cleanly",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second exact-tie candidate with reviewed-tool support.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "reviewed-policy-ranking-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: reviewed-policy-ranking-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: true",
                "reviewedPolicyRuntime:",
                "  enabled: true",
                "  preferredSequenceBonus: 0.05",
            ]
        ),
    )

    output_root = (tmp_path / "generated" / "autoagent-runs").resolve()
    run_root = output_root / "reviewed-policy-ranking-experiment"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "reviewed-policies.json").write_text(
        json.dumps(
            {
                "type": "AutoAgentReviewedPolicies",
                "mode": "manual_review_import",
                "source": {"experimentName": "reviewed-policy-ranking-experiment"},
                "policies": [
                    {
                        "id": "prefer-read-file",
                        "intent": "preferred_tool_sequence",
                        "description": "Prefer the observed read_file success path.",
                        "preferredToolSequence": ["read_file"],
                        "preferredTools": ["read_file"],
                        "preferredSourceKinds": ["session_event"],
                        "terminalStatus": "success",
                        "constraints": {"maxSearchDepth": 1, "maxActionCount": 1},
                        "learningScore": 1.0,
                        "observedCount": 3,
                    }
                ],
                "approvedLearningDrafts": [
                    {"draftId": "policy-draft-01", "promotedPolicyId": "prefer-read-file"}
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=output_root,
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    candidate_a = next(row for row in result["iterations"] if row["candidateId"] == "candidate-a")
    candidate_b = next(
        row for row in result["iterations"] if row["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a["score"] == candidate_b["score"] == 1.0
    assert candidate_a["complexity"]["score"] == candidate_b["complexity"]["score"]
    assert candidate_b["trajectoryScore"] > candidate_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-b--from--baseline"
    assert result["experiment"]["reviewedPolicyRuntimeState"]["status"] == "ready"
    assert result["bestCandidate"]["reviewedPolicyContext"]["matchedPolicyIds"] == [
        "prefer-read-file"
    ]
    assert result["bestCandidate"]["reviewedPolicyContext"]["bonus"] > 0

    ledger = json.loads(
        Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    candidate_b_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_b_node["reviewedPolicyMatches"] == 1
    assert candidate_b_node["reviewedPolicyBonus"] > 0


def test_autoagent_loop_uses_reviewed_escalation_trigger_to_break_warning_ties(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    historical_run = docs_agents / "runs" / "20260411-020202"
    (historical_run / "hook-audit").mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "reviewed-escalation-rank.agent.md"
    target.write_text("---\nname: Reviewed Escalation Rank\n---\n\nBASE\n", encoding="utf-8")

    (historical_run / "hook-audit" / "session.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 1,
                        "event": "toolCall",
                        "status": "warning",
                        "toolName": "apply_patch",
                        "candidateId": "candidate-a",
                        "message": "candidate-a hit a warning path",
                    }
                ),
                json.dumps(
                    {
                        "ts": 2,
                        "event": "toolCall",
                        "status": "warning",
                        "toolName": "read_file",
                        "candidateId": "candidate-b--from--baseline",
                        "message": "candidate-b--from--baseline hit a different warning path",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": (
                            "Second exact-tie candidate avoiding the escalation trigger."
                        ),
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "reviewed-escalation-ranking-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: reviewed-escalation-ranking-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: true",
                "reviewedPolicyRuntime:",
                "  enabled: true",
                "  escalationPenalty: 0.05",
            ]
        ),
    )

    output_root = (tmp_path / "generated" / "autoagent-runs").resolve()
    run_root = output_root / "reviewed-escalation-ranking-experiment"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "reviewed-policies.json").write_text(
        json.dumps(
            {
                "type": "AutoAgentReviewedPolicies",
                "mode": "manual_review_import",
                "source": {"experimentName": "reviewed-escalation-ranking-experiment"},
                "policies": [
                    {
                        "id": "escalate-apply-patch-warning",
                        "intent": "escalation_trigger",
                        "description": "Penalize the reviewed apply_patch warning path.",
                        "triggerTools": ["apply_patch"],
                        "preferredSourceKinds": ["session_event"],
                        "terminalStatus": "warning",
                        "constraints": {"maxSearchDepth": 1, "maxActionCount": 1},
                        "learningScore": 1.0,
                        "observedCount": 2,
                    }
                ],
                "approvedLearningDrafts": [
                    {
                        "draftId": "policy-draft-01",
                        "promotedPolicyId": "escalate-apply-patch-warning",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=output_root,
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    candidate_a = next(row for row in result["iterations"] if row["candidateId"] == "candidate-a")
    candidate_b = next(
        row for row in result["iterations"] if row["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a["score"] == candidate_b["score"] == 1.0
    assert candidate_a["complexity"]["score"] == candidate_b["complexity"]["score"]
    assert candidate_b["trajectoryScore"] > candidate_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-b--from--baseline"
    assert result["bestCandidate"]["reviewedPolicyContext"]["matchedPolicyCount"] == 0

    candidate_a_record = next(
        record
        for record in json.loads(
            Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
        )["nodes"]
        if record["candidateId"] == "candidate-a"
    )
    assert candidate_a_record["reviewedPolicyMatches"] == 1
    assert candidate_a_record["reviewedPolicyPenalty"] > 0
    explanation = result["candidateSearch"]["winnerExplanation"]
    assert any(
        signal["signal"] == "reviewedPolicyPenalty"
        for signal in explanation["topTrajectorySignals"]
    )


def test_autoagent_loop_prioritizes_reviewed_policy_source_candidate_mutations(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "reviewed-priority.agent.md"
    target.write_text("---\nname: Reviewed Priority\n---\n\nBASE\n", encoding="utf-8")

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOOD",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "Catalog-first neutral mutation.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "NEUTRAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": (
                            "Reviewed-path mutation promoted from an approved candidate."
                        ),
                        "learningImportMetadata": {
                            "sourceCandidateId": "reviewed-success-path",
                            "sourceMutationId": "candidate-b",
                        },
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOOD",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "reviewed-mutation-priority-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: reviewed-mutation-priority-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "reviewedPolicyRuntime:",
                "  enabled: true",
                "  preferredSequenceBonus: 0.05",
            ]
        ),
    )

    output_root = (tmp_path / "generated" / "autoagent-runs").resolve()
    run_root = output_root / "reviewed-mutation-priority-experiment"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "reviewed-policies.json").write_text(
        json.dumps(
            {
                "type": "AutoAgentReviewedPolicies",
                "mode": "manual_review_import",
                "source": {"experimentName": "reviewed-mutation-priority-experiment"},
                "policies": [
                    {
                        "id": "prefer-reviewed-success-path",
                        "intent": "preferred_tool_sequence",
                        "description": "Prefer mutations promoted from the reviewed success path.",
                        "sourceCandidateIds": ["reviewed-success-path"],
                        "preferredToolSequence": ["read_file"],
                        "preferredTools": ["read_file"],
                        "learningScore": 1.0,
                        "observedCount": 2,
                    }
                ],
                "approvedLearningDrafts": [
                    {
                        "draftId": "policy-draft-01",
                        "promotedPolicyId": "prefer-reviewed-success-path",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=output_root,
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=1,
        apply_best=False,
    )

    assert result["bestCandidate"]["candidateId"] == "candidate-b"
    assert result["iterations"][1]["candidateId"] == "candidate-b"
    mutation_plan = result["candidateSearch"]["mutationExecutionPlan"]
    assert mutation_plan[0]["mutationId"] == "candidate-b"
    assert mutation_plan[0]["priorityStatus"] == "prioritized"
    assert mutation_plan[0]["matchedPolicyIds"] == ["prefer-reviewed-success-path"]
    assert mutation_plan[1]["mutationId"] == "candidate-a"

    ledger = json.loads(
        Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    assert ledger["mutationExecutionPlan"][0]["mutationId"] == "candidate-b"

    checkpoint = json.loads(
        Path(result["artifacts"]["checkpoint"]["actualPath"]).read_text(encoding="utf-8")
    )
    assert checkpoint["mutationExecutionPlan"][0]["mutationId"] == "candidate-b"
    assert checkpoint["mutationExecutionPlanTokens"][0] == "2:candidate-b"


def test_autoagent_loop_preserves_catalog_order_without_reviewed_policy_source_match(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "reviewed-no-match.agent.md"
    target.write_text("---\nname: Reviewed No Match\n---\n\nBASE\n", encoding="utf-8")

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": (
                            "Catalog-first mutation remains first without a reviewed match."
                        ),
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": (
                            "Reviewed metadata exists, but it does not match the active policy."
                        ),
                        "learningImportMetadata": {
                            "sourceCandidateId": "unmatched-reviewed-path",
                            "sourceMutationId": "candidate-b",
                        },
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "reviewed-mutation-no-match-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: reviewed-mutation-no-match-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "reviewedPolicyRuntime:",
                "  enabled: true",
                "  preferredSequenceBonus: 0.05",
            ]
        ),
    )

    output_root = (tmp_path / "generated" / "autoagent-runs").resolve()
    run_root = output_root / "reviewed-mutation-no-match-experiment"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "reviewed-policies.json").write_text(
        json.dumps(
            {
                "type": "AutoAgentReviewedPolicies",
                "mode": "manual_review_import",
                "source": {"experimentName": "reviewed-mutation-no-match-experiment"},
                "policies": [
                    {
                        "id": "prefer-different-reviewed-path",
                        "intent": "preferred_tool_sequence",
                        "description": (
                            "Active reviewed policy references a different source candidate."
                        ),
                        "sourceCandidateIds": ["different-reviewed-path"],
                        "preferredToolSequence": ["read_file"],
                        "preferredTools": ["read_file"],
                        "learningScore": 1.0,
                        "observedCount": 2,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=output_root,
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=1,
        apply_best=False,
    )

    assert result["bestCandidate"]["candidateId"] == "candidate-a"
    assert result["iterations"][1]["candidateId"] == "candidate-a"
    mutation_plan = result["candidateSearch"]["mutationExecutionPlan"]
    assert mutation_plan[0]["mutationId"] == "candidate-a"
    assert mutation_plan[0]["priorityStatus"] == "neutral"
    assert mutation_plan[1]["mutationId"] == "candidate-b"
    assert mutation_plan[1]["matchedPolicyIds"] == []


def test_episode_observation_guard_matches_candidate_evidence() -> None:
    module = load_module()
    documents = {
        "agent": {
            "path": Path("agent.md"),
            "frontmatter": {"name": "Episode Guard"},
            "body": "GOAL\n",
        }
    }
    benchmark = {
        "checks": [
            {
                "id": "observed-success-path",
                "type": "episode_observation_guard",
                "sourceKinds": ["session_event"],
                "toolNames": ["read_file"],
                "terminalStatus": "success",
                "weight": 0.25,
            }
        ]
    }
    evidence_dataset = {
        "records": [
            {
                "sourceKind": "session_event",
                "status": "success",
                "toolName": "read_file",
                "candidateIds": ["candidate-b--from--baseline"],
            }
        ]
    }

    passing_eval = module.evaluate_candidate(
        documents,
        benchmark,
        "agent",
        candidate_record={
            "candidateId": "candidate-b--from--baseline",
            "parentCandidateId": "baseline",
            "mutationId": "candidate-b",
            "status": "keep",
        },
        evidence_dataset=evidence_dataset,
    )
    failing_eval = module.evaluate_candidate(
        documents,
        benchmark,
        "agent",
        candidate_record={
            "candidateId": "candidate-a",
            "parentCandidateId": "baseline",
            "mutationId": "candidate-a",
            "status": "discard",
        },
        evidence_dataset=evidence_dataset,
    )

    assert passing_eval["score"] == 1.0
    assert passing_eval["checks"][0]["passed"] is True
    assert passing_eval["checks"][0]["observed"]["matchedRecordCount"] == 1
    assert passing_eval["checks"][0]["observed"]["toolNames"] == ["read_file"]

    assert failing_eval["score"] == 0.0
    assert failing_eval["checks"][0]["passed"] is False
    assert failing_eval["checks"][0]["observed"]["matchedRecordCount"] == 0


def test_episode_shadow_learning_scores_keep_benchmark_only_quality_stable() -> None:
    module = load_module()

    scores = module._episode_shadow_learning_scores(
        {"evaluation": {"score": 0.82}},
        {"actionSequence": [], "searchDepth": 0},
        {
            "summary": {
                "matchedRecordCount": 0,
                "stepCount": 0,
                "statusCounts": {},
                "terminalStatus": "unknown",
                "handoffCount": 0,
                "toolSequence": [],
            }
        },
    )

    assert scores["classification"] == "benchmark_only"
    assert scores["qualityScore"] == pytest.approx(0.82)
    assert scores["factors"]["terminalOutcomeScore"] == pytest.approx(0.82)
    assert scores["factors"]["handoffEfficiency"] == pytest.approx(1.0)
    assert scores["factors"]["toolChurnScore"] == pytest.approx(1.0)
    assert scores["factors"]["repeatedToolCount"] == 0


def test_episode_shadow_learning_scores_penalize_terminal_handoff_and_tool_churn() -> None:
    module = load_module()

    success_scores = module._episode_shadow_learning_scores(
        {"evaluation": {"score": 1.0}},
        {"actionSequence": ["read_file", "apply_patch"], "searchDepth": 1},
        {
            "summary": {
                "matchedRecordCount": 2,
                "stepCount": 2,
                "statusCounts": {"success": 2},
                "terminalStatus": "success",
                "handoffCount": 0,
                "toolSequence": ["read_file", "apply_patch"],
            }
        },
    )
    degraded_scores = module._episode_shadow_learning_scores(
        {"evaluation": {"score": 1.0}},
        {"actionSequence": ["read_file", "apply_patch"], "searchDepth": 1},
        {
            "summary": {
                "matchedRecordCount": 2,
                "stepCount": 2,
                "statusCounts": {"warning": 2},
                "terminalStatus": "warning",
                "handoffCount": 2,
                "toolSequence": ["read_file", "read_file", "read_file"],
            }
        },
    )

    assert success_scores["qualityScore"] > degraded_scores["qualityScore"]
    assert success_scores["efficiencyScore"] > degraded_scores["efficiencyScore"]
    assert success_scores["learningScore"] > degraded_scores["learningScore"]
    assert success_scores["factors"]["terminalOutcomeScore"] == pytest.approx(1.0)
    assert degraded_scores["factors"]["terminalOutcomeScore"] == pytest.approx(0.35)
    assert degraded_scores["factors"]["handoffCount"] == 2
    assert (
        degraded_scores["factors"]["handoffEfficiency"]
        < success_scores["factors"]["handoffEfficiency"]
    )
    assert degraded_scores["factors"]["repeatedToolCount"] == 2
    assert (
        degraded_scores["factors"]["toolChurnScore"] < success_scores["factors"]["toolChurnScore"]
    )


def test_learning_review_template_manifest_is_valid() -> None:
    module = load_module()
    template_path = (
        ROOT
        / ".github"
        / "skills"
        / "autoagent-loop"
        / "examples"
        / "learning-review-template.json"
    )

    manifest = module._load_learning_review_manifest(template_path)

    assert manifest["type"] == "AutoAgentLearningReview"
    assert manifest["benchmarkDrafts"][0]["decision"] == "accept"
    assert manifest["mutationDrafts"][0]["decision"] == "accept"
    assert manifest["policyDrafts"][0]["decision"] == "accept"


def test_autoagent_loop_stages_guarded_learning_review_when_governance_is_ready(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents
    write_governed_state(docs_agents / "state.json", "PASS")
    write_governed_review_report(docs_agents / "review-report.md", "PASS")

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "session-evidence-rank.agent.md"
    target.write_text("---\nname: Session Evidence Rank\n---\n\nBASE\n", encoding="utf-8")

    historical_run = docs_agents / "runs" / "20260403-030303"
    (historical_run / "hook-audit").mkdir(parents=True, exist_ok=True)
    (historical_run / "hook-audit" / "session.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 1,
                        "event": "toolCall",
                        "status": "error",
                        "toolName": "apply_patch",
                        "candidateId": "candidate-a",
                        "message": "candidate-a failed validation",
                    }
                ),
                json.dumps(
                    {
                        "ts": 2,
                        "event": "toolCall",
                        "status": "success",
                        "toolName": "read_file",
                        "candidateId": "candidate-b--from--baseline",
                        "message": "candidate-b--from--baseline validated cleanly",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (historical_run / "hook-audit" / "session-summary.json").write_text(
        json.dumps(
            {
                "ts": 3,
                "event": "sessionEnd",
                "audit": {
                    "totalEvents": 2,
                    "denies": 0,
                    "errors": 1,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second exact-tie candidate with cleaner session evidence.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "guarded-learning-review-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: guarded-learning-review-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "continuousPolicy:",
                "  mode: scheduled",
                '  scheduleCron: "0 2 * * *"',
                "  triggerOn:",
                "    - review_failure",
                "  minSignalCount: 1",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: true",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    guarded = result["guardedLearningPromotion"]
    assert guarded["ready"] is True
    assert guarded["status"] == "staged_for_review"
    assert guarded["acceptedBenchmarkDraftCount"] >= 1
    assert guarded["acceptedPolicyDraftCount"] >= 1
    assert guarded["artifactPath"] == result["artifacts"]["guardedLearningReview"]["actualPath"]

    guarded_manifest_path = Path(guarded["artifactPath"])
    assert guarded_manifest_path.exists()
    guarded_manifest = json.loads(guarded_manifest_path.read_text(encoding="utf-8"))
    assert guarded_manifest["type"] == "AutoAgentLearningReview"
    assert guarded_manifest["mode"] == "guarded_auto_promotion"
    assert guarded_manifest["reviewer"] == "autoagent-guarded-promotion"
    assert guarded_manifest["guardrails"] == {
        "continuationEligibilityStatus": "eligible",
        "continuationReadinessStatus": "ready",
        "governedApprovalStatus": "ready_for_recording",
        "minObservedCount": 1,
        "minPolicyLearningScore": 0.7,
        "reviewRequired": True,
    }
    assert guarded_manifest["mutationDrafts"] == []
    assert any(entry["decision"] == "accept" for entry in guarded_manifest["benchmarkDrafts"])
    assert any(entry["decision"] == "accept" for entry in guarded_manifest["policyDrafts"])

    accepted_benchmark_review = next(
        entry for entry in guarded_manifest["benchmarkDrafts"] if entry["decision"] == "accept"
    )
    assert accepted_benchmark_review["stagedDecision"] == "accept"
    assert accepted_benchmark_review["decisionRationale"]["observedCountPass"] is True
    assert accepted_benchmark_review["decisionRationale"]["blockedByFactors"] == []
    assert accepted_benchmark_review["decisionRationale"]["primaryBlockedFactor"] is None

    accepted_policy_review = next(
        entry for entry in guarded_manifest["policyDrafts"] if entry["decision"] == "accept"
    )
    assert accepted_policy_review["stagedDecision"] == "accept"
    assert accepted_policy_review["decisionRationale"]["observedCountPass"] is True
    assert accepted_policy_review["decisionRationale"]["learningScorePass"] is True
    assert accepted_policy_review["decisionRationale"]["blockedByFactors"] == []
    assert accepted_policy_review["decisionRationale"]["primaryBlockedFactor"] is None

    deferred_policy_review = next(
        (entry for entry in guarded_manifest["policyDrafts"] if entry["decision"] == "defer"),
        None,
    )
    if deferred_policy_review is not None:
        assert deferred_policy_review["stagedDecision"] == "defer"
        assert deferred_policy_review["decisionRationale"]["blockedByFactors"]
        assert deferred_policy_review["decisionRationale"]["primaryBlockedFactor"] in {
            "observedCount",
            "learningScore",
        }

    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Guarded learning promotion: staged_for_review" in report_text
    assert "- Guarded learning blocked reasons: none" in report_text
    assert "- Guarded learning benchmark accepts: " in report_text
    assert "- Guarded learning policy accepts: " in report_text
    assert f"- Guarded learning review artifact: {guarded['artifactPath']}" in report_text


def test_autoagent_loop_uses_external_transcript_evidence_to_break_exact_ties(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "transcript-evidence-rank.agent.md"
    target.write_text("---\nname: Transcript Evidence Rank\n---\n\nBASE\n", encoding="utf-8")

    transcript_path = tmp_path / "transcripts" / "copilot-session.jsonl"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 1,
                        "role": "tool",
                        "tool": {"name": "apply_patch"},
                        "status": "error",
                        "candidate": {"id": "candidate-a"},
                        "content": [
                            {
                                "type": "text",
                                "text": "candidate-a patch failed validation",
                            }
                        ],
                    }
                ),
                json.dumps(
                    {
                        "ts": 2,
                        "role": "assistant",
                        "status": "success",
                        "candidate": {"id": "candidate-b--from--baseline"},
                        "toolCall": {"name": "read_file"},
                        "response": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "candidate-b--from--baseline validated cleanly "
                                        "after transcript review"
                                    ),
                                }
                            ]
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": (
                            "Second exact-tie candidate with cleaner transcript evidence."
                        ),
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "transcript-trajectory-evidence-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: transcript-trajectory-evidence-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: false",
                "  externalLogSources:",
                "    - id: transcript-source",
                "      kind: copilot_chat_transcript",
                f"      path: {transcript_path.as_posix()}",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    candidate_a = next(row for row in result["iterations"] if row["candidateId"] == "candidate-a")
    candidate_b = next(
        row for row in result["iterations"] if row["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a["score"] == candidate_b["score"] == 1.0
    assert candidate_a["complexity"]["score"] == candidate_b["complexity"]["score"]
    assert candidate_b["trajectoryScore"] > candidate_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-b--from--baseline"
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["matchedRecordCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["successCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["sourceKindCounts"] == {
        "transcript_event": 1
    }
    explanation = result["candidateSearch"]["winnerExplanation"]
    assert explanation["decisiveSignal"] == "trajectory_score"
    assert explanation["evidenceBacked"] is True
    assert explanation["trajectorySummary"].startswith("Top trajectory contributors: ")
    assert explanation["evidenceComparison"]["winnerSourceKinds"] == {"transcript_event": 1}
    assert explanation["evidenceComparison"]["runnerUpSourceKinds"] == {"transcript_event": 1}
    assert explanation["evidenceComparison"]["winnerStatuses"] == {"success": 1}
    assert explanation["evidenceComparison"]["runnerUpStatuses"] == {"error": 1}

    evidence = json.loads((docs_agents / "autoagent-evidence.json").read_text(encoding="utf-8"))
    assert evidence["summary"]["transcriptRecordCount"] == 2
    assert evidence["summary"]["externalLogRecordCount"] == 2
    assert evidence["summary"]["externalSourceCount"] == 1
    assert evidence["summary"]["recordsByKind"]["transcript_event"] == 2
    assert evidence["sources"]["transcriptSources"][0]["kind"] == "copilot_chat_transcript"
    assert evidence["sources"]["transcriptSources"][0]["recordKind"] == "transcript_event"

    ledger = json.loads(
        Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    candidate_a_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-a"
    )
    candidate_b_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a_node["trajectoryEvidenceErrors"] == 1
    assert candidate_b_node["trajectoryEvidenceSuccesses"] == 1


def test_autoagent_loop_uses_first_class_chat_history_json_exports_to_break_exact_ties(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "chat-history-evidence-rank.agent.md"
    target.write_text("---\nname: Chat History Evidence Rank\n---\n\nBASE\n", encoding="utf-8")

    chat_export_path = docs_agents / "runs" / "20260411-010101" / "copilot-chat-export.json"
    chat_export_path.parent.mkdir(parents=True, exist_ok=True)
    chat_export_path.write_text(
        json.dumps(
            {
                "conversationId": "session-1",
                "messages": [
                    {
                        "ts": 1,
                        "message": {
                            "author": {"role": "assistant"},
                            "content": [
                                {
                                    "type": "text",
                                    "text": "candidate-a chat history path hit an error",
                                }
                            ],
                            "metadata": {"candidate": {"id": "candidate-a"}},
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "type": "function",
                                    "function": {"name": "apply_patch"},
                                }
                            ],
                        },
                        "result": {"status": "failed"},
                    },
                    {
                        "ts": 2,
                        "message": {
                            "author": {"role": "assistant"},
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "candidate-b--from--baseline chat history path "
                                        "validated cleanly"
                                    ),
                                }
                            ],
                            "metadata": {
                                "selectedCandidate": {"id": "candidate-b--from--baseline"}
                            },
                            "tool_calls": [
                                {
                                    "id": "call-2",
                                    "type": "function",
                                    "function": {"name": "read_file"},
                                }
                            ],
                        },
                        "result": {"status": "completed"},
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": (
                            "Second exact-tie candidate with cleaner chat history evidence."
                        ),
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "chat-history-trajectory-evidence-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: chat-history-trajectory-evidence-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: false",
                "  includeChatHistory: true",
                "  chatHistoryPaths:",
                f"    - {chat_export_path.as_posix()}",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    candidate_a = next(row for row in result["iterations"] if row["candidateId"] == "candidate-a")
    candidate_b = next(
        row for row in result["iterations"] if row["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a["score"] == candidate_b["score"] == 1.0
    assert candidate_a["complexity"]["score"] == candidate_b["complexity"]["score"]
    assert candidate_b["trajectoryScore"] > candidate_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-b--from--baseline"
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["matchedRecordCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["successCount"] == 1

    evidence = json.loads((docs_agents / "autoagent-evidence.json").read_text(encoding="utf-8"))
    assert evidence["summary"]["transcriptRecordCount"] == 2
    assert evidence["summary"]["externalSourceCount"] == 1
    assert evidence["summary"]["governedTraceExportRecordCount"] == 2
    assert evidence["summary"]["governedTraceExportSourceCount"] == 1
    assert evidence["summary"]["fixtureExternalLogRecordCount"] == 0
    assert evidence["summary"]["recordsByKind"]["transcript_event"] == 2
    assert evidence["sources"]["transcriptSources"][0]["kind"] == "chat_transcript"
    assert evidence["sources"]["transcriptSources"][0]["recordKind"] == "transcript_event"
    assert evidence["sources"]["transcriptSources"][0]["sourceOrigin"] == "governed_run_export"
    assert evidence["sources"]["transcriptSources"][0]["sourceRunId"] == "20260411-010101"

    transcript_records = [
        record for record in evidence["records"] if record["sourceKind"] == "transcript_event"
    ]
    assert transcript_records[0]["sourceOrigin"] == "governed_run_export"
    assert transcript_records[0]["sourceRunId"] == "20260411-010101"
    assert transcript_records[0]["toolName"] == "apply_patch"
    assert transcript_records[0]["status"] == "error"
    assert transcript_records[1]["toolName"] == "read_file"
    assert transcript_records[1]["status"] == "success"

    learning_summary = result["learningSummary"]
    top_observed_path = learning_summary["topObservedPaths"][0]
    assert learning_summary["reasoningPathSignal"]["name"] == "reasoningPathEfficiencyScore"
    assert learning_summary["reasoningPathSignal"]["transcriptBackedPathCount"] == 2
    assert learning_summary["reasoningPathSignal"]["handoffBackedPathCount"] == 0
    assert top_observed_path["provenance"]["transcriptBacked"] is True
    assert top_observed_path["provenance"]["handoffBacked"] is False
    assert top_observed_path["provenance"]["sourceOrigins"] == ["governed_run_export"]
    assert top_observed_path["provenance"]["governedRunIds"] == ["20260411-010101"]
    assert top_observed_path["reasoningPathEfficiencyScore"] == pytest.approx(
        top_observed_path["factors"]["reasoningPathEfficiencyScore"]
    )

    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Governed trace export records: 2" in report_text
    assert "- Fixture-backed external log records: 0" in report_text
    assert "- Transcript evidence records: 2" in report_text
    assert "- Handoff evidence records: 0" in report_text
    assert "- Learning reasoning-path signal: reasoningPathEfficiencyScore" in report_text
    assert "- Learning transcript-backed paths: 2" in report_text
    assert "- Learning handoff-backed paths: 0" in report_text


def test_autoagent_loop_uses_nested_transcript_metadata_to_break_exact_ties(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "nested-transcript-evidence-rank.agent.md"
    target.write_text("---\nname: Nested Transcript Evidence Rank\n---\n\nBASE\n", encoding="utf-8")

    transcript_path = tmp_path / "transcripts" / "copilot-session-nested.jsonl"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 1,
                        "candidate": {"id": "candidate-a"},
                        "message": {
                            "author": {"role": "assistant"},
                            "content": [
                                {
                                    "type": "text",
                                    "text": "candidate-a nested transcript review entry",
                                }
                            ],
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "type": "function",
                                    "function": {"name": "apply_patch"},
                                }
                            ],
                        },
                        "result": {"status": "failed"},
                    }
                ),
                json.dumps(
                    {
                        "ts": 2,
                        "candidate": {"id": "candidate-b--from--baseline"},
                        "message": {
                            "author": {"role": "assistant"},
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "candidate-b--from--baseline nested transcript review entry"
                                    ),
                                }
                            ],
                            "tool_calls": [
                                {
                                    "id": "call-2",
                                    "type": "function",
                                    "function": {"name": "read_file"},
                                }
                            ],
                        },
                        "result": {"status": "completed"},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First exact-tie candidate.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second exact-tie candidate with nested transcript success.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "nested-transcript-trajectory-evidence-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: nested-transcript-trajectory-evidence-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: false",
                "  externalLogSources:",
                "    - id: nested-transcript-source",
                "      kind: copilot_chat_transcript",
                f"      path: {transcript_path.as_posix()}",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    candidate_a = next(row for row in result["iterations"] if row["candidateId"] == "candidate-a")
    candidate_b = next(
        row for row in result["iterations"] if row["candidateId"] == "candidate-b--from--baseline"
    )
    assert candidate_a["score"] == candidate_b["score"] == 1.0
    assert candidate_a["complexity"]["score"] == candidate_b["complexity"]["score"]
    assert candidate_b["trajectoryScore"] > candidate_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-b--from--baseline"
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["matchedRecordCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["successCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["statusCounts"] == {"success": 1}

    evidence = json.loads((docs_agents / "autoagent-evidence.json").read_text(encoding="utf-8"))
    transcript_records = [
        record for record in evidence["records"] if record["sourceKind"] == "transcript_event"
    ]
    assert evidence["summary"]["statuses"] == {"error": 1, "success": 1}
    assert transcript_records[0]["role"] == "assistant"
    assert transcript_records[0]["toolName"] == "apply_patch"
    assert transcript_records[0]["status"] == "error"
    assert transcript_records[1]["role"] == "assistant"
    assert transcript_records[1]["toolName"] == "read_file"
    assert transcript_records[1]["status"] == "success"


def test_autoagent_loop_prefers_exact_nested_candidate_ids_for_branched_transcripts(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "branched-transcript-candidate-attribution.agent.md"
    target.write_text(
        "---\nname: Branched Transcript Candidate Attribution\n---\n\nBASE\n",
        encoding="utf-8",
    )

    transcript_path = tmp_path / "transcripts" / "branched-copilot-session.jsonl"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(
        json.dumps(
            {
                "ts": 1,
                "message": {
                    "author": {"role": "assistant"},
                    "content": [
                        {
                            "type": "text",
                            "text": "Branched transcript review selected the cleaner candidate.",
                        }
                    ],
                    "metadata": {
                        "candidate": {"id": "candidate-c--from--candidate-b-from-baseline"}
                    },
                },
                "result": {
                    "status": "completed",
                    "selectedCandidate": {"id": "candidate-c--from--candidate-b-from-baseline"},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    },
                    {
                        "id": "follow-up",
                        "type": "contains_text",
                        "target": "body",
                        "value": "SECOND",
                        "weight": 1,
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First parent candidate for the branched transcript test.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL\nBASE2",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second parent candidate for the branched transcript test.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL\nBASE2",
                            }
                        ],
                    },
                    {
                        "id": "candidate-c",
                        "description": (
                            "Shared follow-up mutation that creates two branched candidates."
                        ),
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE2",
                                "new": "SECOND",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "branched-transcript-candidate-attribution-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: branched-transcript-candidate-attribution-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  searchStrategy: frontier",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: false",
                "  externalLogSources:",
                "    - id: branched-transcript-source",
                "      kind: copilot_chat_transcript",
                f"      path: {transcript_path.as_posix()}",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    branch_a = next(
        row
        for row in result["iterations"]
        if row["candidateId"] == "candidate-c--from--candidate-a"
    )
    branch_b = next(
        row
        for row in result["iterations"]
        if row["candidateId"] == "candidate-c--from--candidate-b-from-baseline"
    )
    assert branch_a["score"] == branch_b["score"] == 1.0
    assert branch_a["complexity"]["score"] == branch_b["complexity"]["score"]
    assert branch_b["trajectoryScore"] > branch_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-c--from--candidate-b-from-baseline"
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["matchedRecordCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["successCount"] == 1
    explanation = result["candidateSearch"]["winnerExplanation"]
    assert explanation["decisiveSignal"] == "trajectory_score"
    assert explanation["evidenceBacked"] is True

    evidence = json.loads((docs_agents / "autoagent-evidence.json").read_text(encoding="utf-8"))
    transcript_record = next(
        record for record in evidence["records"] if record["sourceKind"] == "transcript_event"
    )
    assert transcript_record["candidateIds"] == ["candidate-c--from--candidate-b-from-baseline"]
    assert transcript_record["status"] == "success"

    ledger = json.loads(
        Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    branch_a_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-c--from--candidate-a"
    )
    branch_b_node = next(
        node
        for node in ledger["nodes"]
        if node["candidateId"] == "candidate-c--from--candidate-b-from-baseline"
    )
    assert branch_a_node["trajectoryEvidenceMatches"] == 0
    assert branch_a_node["trajectoryEvidenceSuccesses"] == 0
    assert branch_b_node["trajectoryEvidenceMatches"] == 1
    assert branch_b_node["trajectoryEvidenceSuccesses"] == 1


def test_autoagent_loop_uses_handoff_history_to_attribute_branched_candidates(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents = tmp_path / "docs" / "agents"
    docs_agents.mkdir(parents=True, exist_ok=True)
    (docs_agents / "runs" / "test-run").mkdir(parents=True, exist_ok=True)
    (docs_agents / "current-run.json").write_text(
        json.dumps({"currentRunPath": "docs/agents/runs/test-run"}),
        encoding="utf-8",
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    working_dir = tmp_path / "work"
    working_dir.mkdir(parents=True, exist_ok=True)
    target = working_dir / "branched-handoff-candidate-attribution.agent.md"
    target.write_text(
        "---\nname: Branched Handoff Candidate Attribution\n---\n\nBASE\n",
        encoding="utf-8",
    )

    handoff_path = tmp_path / "transcripts" / "branched-handoff-session.jsonl"
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        json.dumps(
            {
                "ts": 1,
                "event": "handoff",
                "message": {
                    "author": {"role": "assistant"},
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "candidate-c--from--candidate-a appears in text, but explicit "
                                "handoff routing selected the other branch."
                            ),
                        }
                    ],
                },
                "handoff": {"targetCandidateId": "candidate-c--from--candidate-b-from-baseline"},
                "tool": {"name": "read_file"},
                "result": {"status": "completed"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    (working_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "id": "goal",
                        "type": "contains_text",
                        "target": "body",
                        "value": "GOAL",
                        "weight": 1,
                    },
                    {
                        "id": "follow-up",
                        "type": "contains_text",
                        "target": "body",
                        "value": "SECOND",
                        "weight": 1,
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (working_dir / "mutations.json").write_text(
        json.dumps(
            {
                "mutations": [
                    {
                        "id": "candidate-a",
                        "description": "First parent candidate for the branched handoff test.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL\nBASE2",
                            }
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "description": "Second parent candidate for the branched handoff test.",
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE",
                                "new": "GOAL\nBASE2",
                            }
                        ],
                    },
                    {
                        "id": "candidate-c",
                        "description": (
                            "Shared follow-up mutation that creates two branched candidates."
                        ),
                        "operations": [
                            {
                                "type": "replace_text",
                                "target": "body",
                                "old": "BASE2",
                                "new": "SECOND",
                            }
                        ],
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    experiment = working_dir / "branched-handoff-candidate-attribution-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: branched-handoff-candidate-attribution-experiment",
                f"targetAgentPath: {target.name}",
                "benchmarkPath: benchmark.json",
                "mutationCatalogPath: mutations.json",
                "candidatePolicy:",
                "  keepStrategy: score-then-simpler",
                "  searchStrategy: frontier",
                "  frontierSize: 2",
                "evidencePolicy:",
                "  includeCurrentArtifacts: false",
                "  includeHookAudit: false",
                "  includeHandoffHistory: true",
                "  handoffHistoryPaths:",
                f"    - {handoff_path.as_posix()}",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    branch_a = next(
        row
        for row in result["iterations"]
        if row["candidateId"] == "candidate-c--from--candidate-a"
    )
    branch_b = next(
        row
        for row in result["iterations"]
        if row["candidateId"] == "candidate-c--from--candidate-b-from-baseline"
    )
    assert branch_a["score"] == branch_b["score"] == 1.0
    assert branch_a["complexity"]["score"] == branch_b["complexity"]["score"]
    assert branch_b["trajectoryScore"] > branch_a["trajectoryScore"]
    assert result["bestCandidate"]["candidateId"] == "candidate-c--from--candidate-b-from-baseline"
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["matchedRecordCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["successCount"] == 1
    assert result["bestCandidate"]["trajectoryEvidenceContext"]["sourceKindCounts"] == {
        "handoff_event": 1
    }

    evidence = json.loads((docs_agents / "autoagent-evidence.json").read_text(encoding="utf-8"))
    assert evidence["summary"]["handoffRecordCount"] == 1
    assert evidence["summary"]["externalLogRecordCount"] == 1
    assert evidence["summary"]["externalSourceCount"] == 1
    assert evidence["summary"]["recordsByKind"]["handoff_event"] == 1
    assert evidence["sources"]["handoffSources"][0]["kind"] == "handoff_history"
    assert evidence["sources"]["handoffSources"][0]["recordKind"] == "handoff_event"

    handoff_record = next(
        record for record in evidence["records"] if record["sourceKind"] == "handoff_event"
    )
    assert handoff_record["candidateIds"] == []
    assert handoff_record["handoffRefs"] == ["candidate-c--from--candidate-b-from-baseline"]
    assert handoff_record["status"] == "success"

    trace = json.loads(Path(result["artifacts"]["trace"]["actualPath"]).read_text(encoding="utf-8"))
    best_episode = next(
        episode
        for episode in trace["episodes"]
        if episode["candidateId"] == "candidate-c--from--candidate-b-from-baseline"
    )
    top_observed_path = trace["learning"]["topObservedPaths"][0]
    assert best_episode["summary"]["matchedRecordCount"] == 1
    assert best_episode["summary"]["handoffCount"] == 1
    assert best_episode["summary"]["sourceKindCounts"] == {"handoff_event": 1}
    assert best_episode["steps"][0]["handoffRefs"] == [
        "candidate-c--from--candidate-b-from-baseline"
    ]
    assert top_observed_path["handoffCount"] == 1
    assert top_observed_path["provenance"]["transcriptBacked"] is False
    assert top_observed_path["provenance"]["handoffBacked"] is True
    assert top_observed_path["factors"]["handoffCount"] == 1
    assert top_observed_path["factors"]["terminalOutcomeScore"] == pytest.approx(1.0)
    assert top_observed_path["factors"]["handoffEfficiency"] < 1.0
    assert top_observed_path["factors"]["toolChurnScore"] == pytest.approx(1.0)
    assert top_observed_path["reasoningPathEfficiencyScore"] == pytest.approx(
        top_observed_path["factors"]["reasoningPathEfficiencyScore"]
    )
    assert trace["learning"]["reasoningPathSignal"]["name"] == "reasoningPathEfficiencyScore"
    assert trace["learning"]["reasoningPathSignal"]["sourceBackedPathCount"] == 1
    assert trace["learning"]["reasoningPathSignal"]["transcriptBackedPathCount"] == 0
    assert trace["learning"]["reasoningPathSignal"]["handoffBackedPathCount"] == 1
    assert trace["learning"]["reasoningPathSignal"]["bestObservedScore"] == pytest.approx(
        top_observed_path["reasoningPathEfficiencyScore"]
    )
    assert any(
        candidate["kind"] == "episode_success_guard" and candidate["handoffCount"] == 1
        for candidate in trace["learning"]["benchmarkCandidates"]
    )
    assert any(
        seed["kind"] == "reinforce_success_path"
        and seed["candidateId"] == "candidate-c--from--candidate-b-from-baseline"
        and seed["handoffCount"] == 1
        for seed in trace["learning"]["mutationSeedCandidates"]
    )
    assert any(
        candidate["kind"] == "preferred_tool_sequence"
        and candidate["handoffCount"] == 1
        and candidate["toolSequence"] == ["read_file"]
        for candidate in trace["learning"]["policyCandidates"]
    )

    benchmark_drafts = json.loads(
        Path(result["learningArtifacts"]["benchmarkDraftsPath"]).read_text(encoding="utf-8")
    )
    mutation_drafts = json.loads(
        Path(result["learningArtifacts"]["mutationDraftsPath"]).read_text(encoding="utf-8")
    )
    policy_drafts = json.loads(
        Path(result["learningArtifacts"]["policyDraftsPath"]).read_text(encoding="utf-8")
    )
    assert benchmark_drafts["mode"] == "review_only"
    assert mutation_drafts["mode"] == "review_only"
    assert policy_drafts["mode"] == "review_only"
    assert any(
        fragment["kind"] == "episode_success_guard"
        and fragment["fragment"]["handoffCount"] == 1
        and fragment["fragment"]["traceProvenance"]["handoffBacked"] is True
        and fragment["fragment"]["reasoningPathEfficiencyScore"]
        == pytest.approx(top_observed_path["reasoningPathEfficiencyScore"])
        and fragment["fragment"]["factorSummary"]["handoffCount"] == 1
        and fragment["fragment"]["factorSummary"]["terminalOutcomeScore"] == pytest.approx(1.0)
        and fragment["fragment"]["factorSummary"]["reasoningPathEfficiencyScore"]
        == pytest.approx(top_observed_path["reasoningPathEfficiencyScore"])
        and fragment["fragment"]["suggestedChecks"][0]["handoffCount"] == 1
        and fragment["fragment"]["suggestedChecks"][0]["traceProvenance"]["handoffBacked"] is True
        for fragment in benchmark_drafts["draftFragments"]
    )
    assert any(
        entry["kind"] == "reinforce_success_path"
        and entry["entry"]["handoffCount"] == 1
        and entry["entry"]["traceProvenance"]["handoffBacked"] is True
        and entry["entry"]["reasoningPathEfficiencyScore"]
        == pytest.approx(top_observed_path["reasoningPathEfficiencyScore"])
        and entry["entry"]["factorSummary"]["handoffCount"] == 1
        and entry["entry"]["factorSummary"]["reasoningPathEfficiencyScore"]
        == pytest.approx(top_observed_path["reasoningPathEfficiencyScore"])
        for entry in mutation_drafts["draftEntries"]
    )
    assert any(
        entry["kind"] == "preferred_tool_sequence"
        and entry["entry"]["handoffCount"] == 1
        and entry["entry"]["traceProvenance"]["handoffBacked"] is True
        and entry["entry"]["reasoningPathEfficiencyScore"]
        == pytest.approx(top_observed_path["reasoningPathEfficiencyScore"])
        and entry["entry"]["factorSummary"]["handoffCount"] == 1
        and entry["entry"]["factorSummary"]["reasoningPathEfficiencyScore"]
        == pytest.approx(top_observed_path["reasoningPathEfficiencyScore"])
        and entry["entry"]["preferredToolSequence"] == ["read_file"]
        for entry in policy_drafts["draftEntries"]
    )

    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Transcript evidence records: 0" in report_text
    assert "- Handoff evidence records: 1" in report_text
    assert "- Learning reasoning-path signal: reasoningPathEfficiencyScore" in report_text
    assert "- Learning transcript-backed paths: 0" in report_text
    assert "- Learning handoff-backed paths: 1" in report_text

    ledger = json.loads(
        Path(result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    branch_a_node = next(
        node for node in ledger["nodes"] if node["candidateId"] == "candidate-c--from--candidate-a"
    )
    branch_b_node = next(
        node
        for node in ledger["nodes"]
        if node["candidateId"] == "candidate-c--from--candidate-b-from-baseline"
    )
    assert branch_a_node["trajectoryEvidenceMatches"] == 0
    assert branch_a_node["trajectoryEvidenceSuccesses"] == 0
    assert branch_b_node["trajectoryEvidenceMatches"] == 1
    assert branch_b_node["trajectoryEvidenceSuccesses"] == 1


def test_autoagent_loop_falls_back_when_live_evaluator_runner_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    prompt = working_dir / "judge-prompt.md"
    prompt.write_text("Judge prompt.\n", encoding="utf-8")
    rubric = working_dir / "judge-rubric.md"
    rubric.write_text("Judge rubric.\n", encoding="utf-8")
    experiment = working_dir / "failing-live-evaluator.md"
    write_live_evaluator_experiment(
        experiment,
        "onboarding-helper.agent.md",
        prompt_name=prompt.name,
        rubric_names=[rubric.name],
    )

    def failing_runner(
        _config: dict[str, object],
        _samples: list[dict[str, object]],
        _experiment: dict[str, object],
    ) -> dict[str, object]:
        raise RuntimeError("Bearer secret-token C:/Outside/failing-runner.txt")

    monkeypatch.setitem(module.LIVE_EVALUATOR_RUNNERS, "github-models", failing_runner)

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["bestCandidate"]["candidateId"] == "trim-intro"
    assert result["liveEvaluation"]["status"] == "failed"
    assert result["liveEvaluation"]["fallbackToDeterministic"] is True
    assert result["liveEvaluation"]["winnerCandidateId"] == "trim-intro"

    serialized = json.dumps(result["liveEvaluation"])
    assert "secret-token" not in serialized
    assert "failing-runner.txt" not in serialized
    assert "[external-path]" in serialized


def test_autoagent_loop_keeps_better_and_simpler_candidates(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["baseline"]["score"] < result["bestCandidate"]["score"]
    assert result["bestCandidate"]["candidateId"] == "trim-intro"
    assert "add-read-tool" in result["discardedCandidates"]
    assert (docs_agents / "autoagent-report.md").exists()
    assert (docs_agents / "runs" / "test-run" / "autoagent-report.md").exists()
    assert (docs_agents / "autoagent-results.tsv").exists()
    assert (docs_agents / "runs" / "test-run" / "autoagent-results.tsv").exists()


def test_autoagent_loop_writes_search_ledger_artifact(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    ledger_path = Path(result["artifacts"]["searchLedger"]["actualPath"])
    assert ledger_path.exists()
    assert result["candidateSearch"]["searchLedgerPath"] == ledger_path.as_posix()
    assert result["provenance"]["artifacts"]["searchLedgerPath"] == ledger_path.as_posix()

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["type"] == "AutoAgentSearchLedger"
    assert ledger["baselineCandidateId"] == "baseline"
    assert ledger["bestCandidateId"] == result["bestCandidate"]["candidateId"]
    assert ledger["bestCandidateLineage"][0] == "baseline"
    assert ledger["bestCandidateLineage"][-1] == result["bestCandidate"]["candidateId"]
    assert ledger["candidateCount"] == len(result["iterations"])
    assert ledger["winnerExplanation"] == result["candidateSearch"]["winnerExplanation"]
    assert ledger["frontierSnapshots"][0]["frontierCandidateIds"] == ["baseline"]
    assert (
        ledger["frontierSnapshots"][-1]["bestCandidateId"] == result["bestCandidate"]["candidateId"]
    )


def test_autoagent_loop_writes_trace_artifact(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    trace_path = Path(result["artifacts"]["trace"]["actualPath"])
    assert trace_path.exists()
    assert result["traceSummary"]["path"] == trace_path.as_posix()
    assert result["traceSummary"]["eventCount"] > 0
    assert result["traceSummary"]["trajectoryCount"] > 0
    assert result["provenance"]["artifacts"]["tracePath"] == trace_path.as_posix()

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["type"] == "AutoAgentTrace"
    assert trace["version"] == 1
    assert trace["traceKind"] == "optimization_run"
    assert trace["artifacts"]["tracePath"] == trace_path.as_posix()
    assert (
        trace["artifacts"]["benchmarkDraftsPath"]
        == result["learningArtifacts"]["benchmarkDraftsPath"]
    )
    assert (
        trace["artifacts"]["mutationDraftsPath"]
        == result["learningArtifacts"]["mutationDraftsPath"]
    )
    assert trace["summary"]["outcomeLabel"] == "improved"
    assert trace["summary"]["trajectoryCount"] == result["traceSummary"]["trajectoryCount"]
    assert trace["summary"]["episodeCount"] == result["traceSummary"]["episodeCount"]
    assert (
        trace["summary"]["evidenceBackedEpisodeCount"]
        == result["traceSummary"]["evidenceBackedEpisodeCount"]
    )
    assert trace["learning"]["mode"] == "shadow_only"
    assert result["learningSummary"] == trace["learning"]
    assert result["learningArtifacts"]["mode"] == "review_only"
    assert trace["learning"]["benchmarkCandidates"] == []
    assert trace["learning"]["mutationSeedCandidates"] == []
    benchmark_drafts = json.loads(
        Path(result["learningArtifacts"]["benchmarkDraftsPath"]).read_text(encoding="utf-8")
    )
    mutation_drafts = json.loads(
        Path(result["learningArtifacts"]["mutationDraftsPath"]).read_text(encoding="utf-8")
    )
    assert benchmark_drafts["draftFragmentCount"] == 0
    assert mutation_drafts["draftEntryCount"] == 0
    assert trace["summary"]["bestTrajectoryId"] == (
        f"candidate-trajectory-{result['bestCandidate']['candidateId']}"
    )
    assert trace["summary"]["bestTrajectoryScore"] == result["traceSummary"]["bestTrajectoryScore"]
    assert (
        trace["summary"]["bestTrajectoryEvidenceMatches"]
        == (result["traceSummary"]["bestTrajectoryEvidenceMatches"])
    )
    assert trace["summary"]["rankingSignals"] == result["candidateSearch"]["rankingSignals"]
    assert trace["summary"]["winnerExplanation"] == result["candidateSearch"]["winnerExplanation"]
    assert trace["summary"]["improvementDelta"] == round(
        result["bestCandidate"]["score"] - result["baseline"]["score"],
        6,
    )
    assert result["bestCandidate"]["trajectoryScore"] >= result["baseline"]["trajectoryScore"]

    candidate_events = [
        event for event in trace["events"] if event["kind"] == "candidate_evaluation"
    ]
    episodes = trace["episodes"]
    assert candidate_events[0]["candidateId"] == "baseline"
    assert candidate_events[0]["trajectoryScore"] == result["baseline"]["trajectoryScore"]
    assert len(episodes) == result["traceSummary"]["episodeCount"]
    assert any(
        event["candidateId"] == result["bestCandidate"]["candidateId"]
        and event["selectedAsBest"] is True
        for event in candidate_events
    )
    trajectories = trace["trajectories"]
    assert len(trajectories) == result["traceSummary"]["trajectoryCount"]

    baseline_trajectory = trajectories[0]
    baseline_episode = next(episode for episode in episodes if episode["candidateId"] == "baseline")
    assert baseline_trajectory["candidateId"] == "baseline"
    assert baseline_trajectory["actionSequence"] == []
    assert baseline_trajectory["validationAttempts"][0]["attemptType"] == "deterministic_benchmark"
    assert baseline_trajectory["validationAttempts"][0]["checks"][0]["expected"] is not None
    assert candidate_events[0]["trajectoryId"] == baseline_trajectory["trajectoryId"]
    assert baseline_trajectory["context"]["evidence"]["matchedRecordCount"] == 0
    assert baseline_episode["summary"]["matchedRecordCount"] == 0
    assert baseline_episode["summary"]["observedPattern"] == "benchmark_only"
    assert (
        baseline_trajectory["ranking"]["trajectoryScore"] == result["baseline"]["trajectoryScore"]
    )

    mutated_trajectory = next(
        trajectory for trajectory in trajectories if trajectory["candidateId"] != "baseline"
    )
    assert mutated_trajectory["context"]["mutation"]["id"] == mutated_trajectory["mutationId"]
    assert mutated_trajectory["context"]["lineageCandidateIds"][0] == "baseline"
    assert mutated_trajectory["actionSequence"][0]["actionType"] == "mutation_operation"
    assert mutated_trajectory["validationAttempts"][0]["checks"][0]["observed"] is not None
    assert mutated_trajectory["ranking"]["signals"]["validationBreadth"] >= 0.0

    best_trajectory = next(
        trajectory
        for trajectory in trajectories
        if trajectory["candidateId"] == result["bestCandidate"]["candidateId"]
    )
    assert best_trajectory["outcome"]["selectedAsBest"] is True
    assert (
        best_trajectory["ranking"]["trajectoryScore"] == result["bestCandidate"]["trajectoryScore"]
    )

    live_event = next(event for event in trace["events"] if event["kind"] == "live_evaluation")
    assert live_event["winnerCandidateId"] == result["bestCandidate"]["candidateId"]

    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert f"- Trace events: {result['traceSummary']['eventCount']}" in report_text
    assert f"- Trace trajectories: {result['traceSummary']['trajectoryCount']}" in report_text
    assert (
        f"- Trace best trajectory score: {result['traceSummary']['bestTrajectoryScore']}"
        in report_text
    )
    assert f"- Trace candidate episodes: {result['traceSummary']['episodeCount']}" in report_text
    assert (
        "- Trace evidence-backed episodes: "
        f"{result['traceSummary']['evidenceBackedEpisodeCount']}" in report_text
    )
    assert f"- Learning mode: {result['learningSummary']['mode']}" in report_text
    assert (
        "- Learning benchmark candidates: "
        f"{len(result['learningSummary']['benchmarkCandidates'])}" in report_text
    )
    assert (
        "- Learning mutation seeds: "
        f"{len(result['learningSummary']['mutationSeedCandidates'])}" in report_text
    )
    assert (
        "- Learning benchmark draft fragments: "
        f"{result['learningArtifacts']['benchmarkDraftCount']}" in report_text
    )
    assert (
        "- Learning mutation draft entries: "
        f"{result['learningArtifacts']['mutationDraftCount']}" in report_text
    )
    assert (
        "- Learning benchmark drafts artifact: "
        f"{result['learningArtifacts']['benchmarkDraftsPath']}" in report_text
    )
    assert (
        "- Learning mutation drafts artifact: "
        f"{result['learningArtifacts']['mutationDraftsPath']}" in report_text
    )
    assert (
        "- Trace best trajectory evidence matches: "
        f"{result['traceSummary']['bestTrajectoryEvidenceMatches']}" in report_text
    )
    assert (
        f"- Winner rationale: {result['candidateSearch']['winnerExplanation']['summary']}"
        in report_text
    )
    assert (
        "- Winner trajectory contributors: "
        f"{result['candidateSearch']['winnerExplanation']['trajectorySummary'] or 'none'}"
        in report_text
    )
    assert f"- Trace artifact: {trace_path.as_posix()}" in report_text


def test_autoagent_loop_writes_resume_checkpoint_artifact(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=1,
        apply_best=False,
    )

    checkpoint_path = Path(result["artifacts"]["checkpoint"]["actualPath"])
    manifest_path = Path(result["artifacts"]["checkpointManifest"]["actualPath"])
    assert checkpoint_path.exists()
    assert manifest_path.exists()
    assert result["resume"]["resumed"] is False
    assert result["resume"]["completedMutationCount"] == 1
    assert result["provenance"]["artifacts"]["checkpointPath"] == checkpoint_path.as_posix()
    assert result["provenance"]["artifacts"]["checkpointManifestPath"] == manifest_path.as_posix()

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert checkpoint["type"] == "AutoAgentCheckpoint"
    assert checkpoint["version"] == 2
    assert manifest["type"] == "AutoAgentCheckpointManifest"
    assert manifest["version"] == 1
    assert checkpoint["completedMutationCount"] == 1
    assert checkpoint["nextMutationIndex"] == 2
    assert checkpoint["deterministicBestCandidateId"] == result["bestCandidate"]["candidateId"]
    assert checkpoint["inlineCandidateCount"] == 1
    assert checkpoint["snapshotBackedCandidateCount"] == 1
    assert result["resume"]["manifestSnapshotCandidateCount"] == 1
    assert result["resume"]["manifestRequiredFileCount"] == 1
    assert checkpoint["candidateRecords"][0]["candidateId"] == "baseline"
    assert checkpoint["candidateRecords"][0]["documentStorage"] == "candidate_snapshot"
    assert "documents" not in checkpoint["candidateRecords"][0]
    assert checkpoint["currentFrontierCandidateIds"] == [result["bestCandidate"]["candidateId"]]
    assert manifest["checkpointPath"] == checkpoint_path.as_posix()
    assert manifest["snapshotCandidateCount"] == 1
    assert manifest["requiredFileCount"] == 1

    manifest_entry = manifest["snapshotCandidates"][0]
    assert manifest_entry["candidateId"] == "baseline"
    assert manifest_entry["requiredFiles"][0]["path"] == checkpoint["candidateRecords"][0]["path"]
    assert Path(manifest_entry["requiredFiles"][0]["path"]).exists()

    best_record = next(
        record
        for record in checkpoint["candidateRecords"]
        if record["candidateId"] == result["bestCandidate"]["candidateId"]
    )
    assert best_record["documentStorage"] == "inline"
    assert next(iter(best_record["documents"].values()))["body"]


def test_autoagent_loop_resume_checkpoint_matches_fresh_current_best_run(tmp_path: Path) -> None:
    module = load_module()

    resumable_root = tmp_path / "resumable"
    docs_agents, working_dir = prepare_workspace(resumable_root)
    module.ROOT = resumable_root
    module.DOCS_AGENTS_DIR = docs_agents

    partial = module.run_autoagent_loop(
        experiment_path=(working_dir / "experiment.md").resolve(),
        output_root=(resumable_root / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=1,
        apply_best=False,
    )
    resumed = module.run_autoagent_loop(
        experiment_path=(working_dir / "experiment.md").resolve(),
        output_root=(resumable_root / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
        resume=True,
    )

    fresh_root = tmp_path / "fresh"
    fresh_docs_agents, fresh_working_dir = prepare_workspace(fresh_root)
    module.ROOT = fresh_root
    module.DOCS_AGENTS_DIR = fresh_docs_agents
    fresh = module.run_autoagent_loop(
        experiment_path=(fresh_working_dir / "experiment.md").resolve(),
        output_root=(fresh_root / "generated" / "autoagent-runs").resolve(),
        report_path=(fresh_docs_agents / "autoagent-report.md").resolve(),
        results_path=(fresh_docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert partial["resume"]["hasRemainingMutations"] is True
    assert resumed["resume"]["resumed"] is True
    assert resumed["resume"]["startingMutationIndex"] == 2
    assert resumed["bestCandidate"]["candidateId"] == fresh["bestCandidate"]["candidateId"]
    assert resumed["bestCandidate"]["score"] == fresh["bestCandidate"]["score"]
    assert (
        resumed["candidateSearch"]["bestCandidateLineage"]
        == fresh["candidateSearch"]["bestCandidateLineage"]
    )
    assert [row["candidateId"] for row in resumed["iterations"]] == [
        row["candidateId"] for row in fresh["iterations"]
    ]


def test_autoagent_loop_frontier_search_branches_from_multiple_kept_candidates(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents, _, linear_experiment, frontier_experiment = prepare_branching_search_workspace(
        tmp_path
    )
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    linear_result = module.run_autoagent_loop(
        experiment_path=linear_experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )
    frontier_result = module.run_autoagent_loop(
        experiment_path=frontier_experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert linear_result["candidateSearch"]["strategy"] == "current_best"
    assert linear_result["bestCandidate"]["candidateId"] == "workflow-finisher"
    assert linear_result["bestCandidate"]["score"] == 0.4

    assert frontier_result["candidateSearch"]["strategy"] == "frontier"
    assert frontier_result["candidateSearch"]["frontierSize"] == 3
    assert frontier_result["bestCandidate"]["score"] == 0.6
    assert frontier_result["bestCandidate"]["candidateId"].startswith("docs-finisher--from--")
    assert frontier_result["candidateSearch"]["maxSearchDepth"] >= 2
    assert (
        frontier_result["bestCandidate"]["candidateId"]
        in frontier_result["candidateSearch"]["finalFrontierCandidateIds"]
    )

    branched_rows = [
        row for row in frontier_result["iterations"] if row.get("parentCandidateId") == "baseline"
    ]
    assert any(row["candidateId"] == "choose-docs-path--from--baseline" for row in branched_rows)

    ledger = json.loads(
        Path(frontier_result["artifacts"]["searchLedger"]["actualPath"]).read_text(encoding="utf-8")
    )
    assert ledger["bestCandidateId"] == frontier_result["bestCandidate"]["candidateId"]
    assert ledger["bestCandidateLineage"][0] == "baseline"
    assert ledger["bestCandidateLineage"][-1] == frontier_result["bestCandidate"]["candidateId"]
    assert any(
        len(snapshot["frontierCandidateIds"]) > 1 for snapshot in ledger["frontierSnapshots"]
    )
    assert (
        ledger["frontierSnapshots"][-1]["bestCandidateId"]
        == frontier_result["bestCandidate"]["candidateId"]
    )


def test_autoagent_loop_resume_frontier_checkpoint_preserves_branching_outcome(
    tmp_path: Path,
) -> None:
    module = load_module()

    resumable_root = tmp_path / "resumable-frontier"
    docs_agents, _, _, frontier_experiment = prepare_branching_search_workspace(resumable_root)
    module.ROOT = resumable_root
    module.DOCS_AGENTS_DIR = docs_agents

    partial = module.run_autoagent_loop(
        experiment_path=frontier_experiment.resolve(),
        output_root=(resumable_root / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=2,
        apply_best=False,
    )
    partial_checkpoint = json.loads(
        Path(partial["artifacts"]["checkpoint"]["actualPath"]).read_text(encoding="utf-8")
    )
    resumed = module.run_autoagent_loop(
        experiment_path=frontier_experiment.resolve(),
        output_root=(resumable_root / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
        resume=True,
    )

    fresh_root = tmp_path / "fresh-frontier"
    fresh_docs_agents, _, _, fresh_frontier_experiment = prepare_branching_search_workspace(
        fresh_root
    )
    module.ROOT = fresh_root
    module.DOCS_AGENTS_DIR = fresh_docs_agents
    fresh = module.run_autoagent_loop(
        experiment_path=fresh_frontier_experiment.resolve(),
        output_root=(fresh_root / "generated" / "autoagent-runs").resolve(),
        report_path=(fresh_docs_agents / "autoagent-report.md").resolve(),
        results_path=(fresh_docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert partial_checkpoint["completedMutationCount"] == 2
    assert partial_checkpoint["hasRemainingMutations"] is True
    assert len(partial_checkpoint["currentFrontierCandidateIds"]) > 1

    assert resumed["resume"]["resumed"] is True
    assert resumed["resume"]["startingMutationIndex"] == 3
    assert resumed["bestCandidate"]["candidateId"] == fresh["bestCandidate"]["candidateId"]
    assert resumed["bestCandidate"]["score"] == fresh["bestCandidate"]["score"]
    assert (
        resumed["candidateSearch"]["bestCandidateLineage"]
        == fresh["candidateSearch"]["bestCandidateLineage"]
    )


def test_autoagent_loop_resume_requires_existing_checkpoint(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    with pytest.raises(ValueError, match=r"Resume checkpoint does not exist"):
        module.run_autoagent_loop(
            experiment_path=(working_dir / "experiment.md").resolve(),
            output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
            report_path=(docs_agents / "autoagent-report.md").resolve(),
            results_path=(docs_agents / "autoagent-results.tsv").resolve(),
            max_iterations=0,
            apply_best=False,
            resume=True,
        )


def test_autoagent_loop_resume_requires_snapshot_backed_candidate_files(tmp_path: Path) -> None:
    module = load_module()

    resumable_root = tmp_path / "resumable-missing-snapshot"
    docs_agents, _, _, frontier_experiment = prepare_branching_search_workspace(resumable_root)
    module.ROOT = resumable_root
    module.DOCS_AGENTS_DIR = docs_agents

    partial = module.run_autoagent_loop(
        experiment_path=frontier_experiment.resolve(),
        output_root=(resumable_root / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=2,
        apply_best=False,
    )
    checkpoint = json.loads(
        Path(partial["artifacts"]["checkpoint"]["actualPath"]).read_text(encoding="utf-8")
    )
    snapshot_backed_record = next(
        record
        for record in checkpoint["candidateRecords"]
        if record["documentStorage"] == "candidate_snapshot" and record["iteration"] > 0
    )
    Path(snapshot_backed_record["path"]).unlink()

    with pytest.raises(ValueError, match=r"Resume checkpoint candidate snapshot does not exist"):
        module.run_autoagent_loop(
            experiment_path=frontier_experiment.resolve(),
            output_root=(resumable_root / "generated" / "autoagent-runs").resolve(),
            report_path=(docs_agents / "autoagent-report.md").resolve(),
            results_path=(docs_agents / "autoagent-results.tsv").resolve(),
            max_iterations=0,
            apply_best=False,
            resume=True,
        )


def test_autoagent_loop_apply_best_updates_target_agent(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    target_agent = working_dir / "onboarding-helper.agent.md"
    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=4,
        apply_best=True,
    )

    target_content = target_agent.read_text(encoding="utf-8")
    assert result["appliedBestVariant"] is True
    assert result["appliedPath"] == target_agent.as_posix()
    assert "manager-led multi-agent workflow" in target_content
    assert "`docs/agents/task-spec.md`" in target_content
    assert "`team-lead`" in target_content


def test_runner_main_loads_core_module(monkeypatch, tmp_path: Path) -> None:
    runner_path = ROOT / "scripts" / "run_autoagent_loop.py"
    spec = importlib.util.spec_from_file_location("repo_autoagent_runner_test", runner_path)
    assert spec is not None and spec.loader is not None
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)

    class StubModule:
        @staticmethod
        def main() -> int:
            return 7

    monkeypatch.setattr(runner, "_load_module", lambda: StubModule())
    assert runner.main() == 7


def test_autoagent_loop_supports_multi_target_experiments(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "bundle-experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert len(result["targetBundle"]) == 2
    assert result["primaryTargetId"] == "primary-agent"
    assert result["bestCandidate"]["candidateId"] == "add-shared-task-spec-reference"
    assert result["baseline"]["score"] < result["bestCandidate"]["score"]
    assert "add-read-tool" in result["discardedCandidates"]

    candidate_bundle = Path(result["bestCandidate"]["path"])
    assert candidate_bundle.is_dir()
    assert (candidate_bundle / "primary-agent.agent.md").exists()
    assert (candidate_bundle / "shared-guidance.md").exists()


def test_autoagent_loop_checkpoint_manifest_records_bundle_snapshot_files(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "bundle-experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=1,
        apply_best=False,
    )

    manifest = json.loads(
        Path(result["artifacts"]["checkpointManifest"]["actualPath"]).read_text(encoding="utf-8")
    )

    assert manifest["snapshotCandidateCount"] == 1
    assert manifest["requiredFileCount"] == 2
    snapshot_entry = manifest["snapshotCandidates"][0]
    assert snapshot_entry["candidateId"] == "baseline"
    assert {item["targetId"] for item in snapshot_entry["requiredFiles"]} == {
        "primary-agent",
        "shared-guidance",
    }
    assert all(Path(item["path"]).exists() for item in snapshot_entry["requiredFiles"])


def test_autoagent_loop_apply_best_updates_all_targets_in_bundle(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    primary_target = working_dir / "onboarding-helper.agent.md"
    secondary_target = working_dir / "shared-guidance.md"
    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "bundle-experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=3,
        apply_best=True,
    )

    assert result["appliedBestVariant"] is True
    assert result["appliedPath"] == primary_target.as_posix()
    assert result["appliedPaths"] == [primary_target.as_posix(), secondary_target.as_posix()]
    assert "`team-lead`" in primary_target.read_text(encoding="utf-8")
    assert "`docs/agents/task-spec.md`" in secondary_target.read_text(encoding="utf-8")


def test_load_experiment_rejects_bundle_targets_without_paths(tmp_path: Path) -> None:
    module = load_module()
    experiment = tmp_path / "invalid-experiment.md"
    write_experiment(
        experiment,
        """
name: invalid-bundle
optimizationTargets:
  - id: primary-agent
benchmarkPath: benchmark.json
mutationCatalogPath: mutations.json
""".strip(),
    )

    with pytest.raises(ValueError, match=r"Optimization target #1 is missing a path\."):
        module.load_experiment(experiment)


def test_load_experiment_rejects_duplicate_bundle_target_ids(tmp_path: Path) -> None:
    module = load_module()
    target_one = tmp_path / "primary.agent.md"
    target_two = tmp_path / "secondary.md"
    target_one.write_text("---\nname: Primary\n---\n\nPrimary body.\n", encoding="utf-8")
    target_two.write_text("---\nname: Secondary\n---\n\nSecondary body.\n", encoding="utf-8")
    experiment = tmp_path / "duplicate-targets.md"
    write_experiment(
        experiment,
        f"""
name: duplicate-targets
optimizationTargets:
  - id: shared-target
    path: {target_one.name}
  - id: shared-target
    path: {target_two.name}
benchmarkPath: benchmark.json
mutationCatalogPath: mutations.json
""".strip(),
    )

    with pytest.raises(ValueError, match=r"Duplicate optimization target id: shared-target"):
        module.load_experiment(experiment)


def test_autoagent_loop_rejects_unknown_mutation_target_ids(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    invalid_mutations = [
        {
            "id": "unknown-target-mutation",
            "description": "Mutation points at a missing bundle target.",
            "operations": [
                {
                    "type": "ensure_contains",
                    "targetId": "missing-target",
                    "region": "body",
                    "text": "This should fail.",
                }
            ],
        }
    ]
    (working_dir / "bundle-mutations.json").write_text(
        json.dumps({"mutations": invalid_mutations}, indent=2),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match=r"Mutation 'unknown-target-mutation' references unknown targetId 'missing-target'\.",
    ):
        module.run_autoagent_loop(
            experiment_path=(working_dir / "bundle-experiment.md").resolve(),
            output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
            report_path=(docs_agents / "autoagent-report.md").resolve(),
            results_path=(docs_agents / "autoagent-results.tsv").resolve(),
            max_iterations=0,
            apply_best=False,
        )


def test_autoagent_loop_rejects_unknown_benchmark_target_ids(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    benchmark = json.loads((working_dir / "bundle-benchmark.json").read_text(encoding="utf-8"))
    benchmark["checks"].append(
        {
            "id": "missing-target-check",
            "targetId": "missing-target",
            "type": "contains",
            "pattern": "This should fail.",
            "weight": 1,
        }
    )
    (working_dir / "bundle-benchmark.json").write_text(
        json.dumps(benchmark, indent=2),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match=(
            r"Benchmark check 'missing-target-check' references unknown targetId "
            r"'missing-target'\."
        ),
    ):
        module.run_autoagent_loop(
            experiment_path=(working_dir / "bundle-experiment.md").resolve(),
            output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
            report_path=(docs_agents / "autoagent-report.md").resolve(),
            results_path=(docs_agents / "autoagent-results.tsv").resolve(),
            max_iterations=0,
            apply_best=False,
        )


def test_autoagent_loop_collects_evidence_dataset_and_redacts_sensitive_values(
    tmp_path: Path,
) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    write_markdown_report(
        docs_agents / "review-report.md",
        {
            "type": "ReviewReport",
            "status": "PASS",
            "goal": "Current governed review state.",
        },
        title="Review summary",
    )

    historical_run = docs_agents / "runs" / "20260401-010101"
    (historical_run / "hook-audit").mkdir(parents=True, exist_ok=True)
    (historical_run / "state.json").write_text(
        json.dumps(
            {
                "protocol": "swe-team-v1",
                "phase": "Review",
                "task": {"id": "phase1-evidence"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown_report(
        historical_run / "review-report.md",
        {
            "type": "ReviewReport",
            "status": "FAIL",
            "goal": "Historical failed review.",
            "notes": [
                "Bearer secret-token",
                "C:/Outside/secret.txt",
                "/tmp/secret.txt",
            ],
        },
        title="Review summary",
    )
    (historical_run / "hook-audit" / "tool-audit.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": 1,
                        "event": "preToolUse",
                        "status": "error",
                        "toolName": "bash",
                        "commandPreview": "Bearer secret-token token=abc123 C:/Outside/secret.txt",
                    }
                ),
                json.dumps(
                    {
                        "ts": 2,
                        "event": "postToolUse",
                        "status": "success",
                        "toolName": "read_file",
                        "commandPreview": str(tmp_path / "docs" / "agents" / "task-spec.md"),
                    }
                ),
                json.dumps(
                    {
                        "ts": 3,
                        "event": "postToolUse",
                        "status": "success",
                        "toolName": "bash",
                        "commandPreview": "bash ./scripts/ci/quick_test.sh",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = module.run_autoagent_loop(
        experiment_path=(working_dir / "bundle-experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    evidence_path = docs_agents / "autoagent-evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert result["evidenceSummary"]["recordCount"] == evidence["summary"]["recordCount"]
    assert evidence["summary"]["runCount"] >= 2
    assert evidence["summary"]["reportFailureCount"] >= 1
    assert evidence["summary"]["toolErrorCount"] >= 1
    assert (docs_agents / "runs" / "test-run" / "autoagent-evidence.json").exists()

    serialized = json.dumps(evidence)
    assert "secret-token" not in serialized
    assert "abc123" not in serialized
    assert "/tmp/secret.txt" not in serialized
    assert "[external-path]" in serialized
    assert "bash ./scripts/ci/quick_test.sh" in serialized
    assert "<repo>/docs/agents/task-spec.md" in serialized


def test_autoagent_loop_records_hook_audit_parse_errors(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    historical_run = docs_agents / "runs" / "20260402-020202"
    (historical_run / "hook-audit").mkdir(parents=True, exist_ok=True)
    (historical_run / "hook-audit" / "tool-audit.jsonl").write_text(
        "not-json\n"
        + json.dumps(
            {
                "ts": 3,
                "event": "postToolUse",
                "status": "success",
                "toolName": "read_file",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    module.run_autoagent_loop(
        experiment_path=(working_dir / "bundle-experiment.md").resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    evidence = json.loads((docs_agents / "autoagent-evidence.json").read_text(encoding="utf-8"))
    assert evidence["summary"]["parseErrorCount"] == 1
    assert evidence["parseErrors"][0]["file"].endswith("tool-audit.jsonl")


def test_autoagent_loop_report_includes_staged_patch_and_provenance(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    prompt = working_dir / "judge-prompt.md"
    prompt.write_text("Judge prompt.\n", encoding="utf-8")
    rubric = working_dir / "judge-rubric.md"
    rubric.write_text("Judge rubric.\n", encoding="utf-8")
    experiment = working_dir / "bundle-extended-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: bundle-extended",
                "optimizationTargets:",
                "  - id: primary-agent",
                "    path: onboarding-helper.agent.md",
                "    kind: agent_profile",
                "    primary: true",
                "    mutableRegions:",
                "      - body",
                "      - frontmatter.tools",
                "  - id: shared-guidance",
                "    path: shared-guidance.md",
                "    kind: markdown_document",
                "    mutableRegions:",
                "      - body",
                "benchmarkPath: bundle-benchmark.json",
                "mutationCatalogPath: bundle-mutations.json",
                "evaluationMode:",
                "  deterministic: true",
                "  liveEvaluator:",
                "    enabled: true",
                "    strategy: advisory",
                "    provider: github-models",
                "    model: gpt-5.4",
                f"    promptArtifactPath: {prompt.name}",
                "    rubricPaths:",
                f"      - {rubric.name}",
                "continuousPolicy:",
                "  mode: scheduled",
                '  scheduleCron: "0 2 * * *"',
                "  triggerOn:",
                "    - review_failure",
                "  minSignalCount: 2",
                "stagedPatchPolicy:",
                "  enabled: true",
                "  mode: review_bundle",
                "  reviewerHints:",
                "    - Review both bundle targets before apply-best.",
            ]
        ),
    )

    result = module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    assert result["stagedPatch"]["enabled"] is True
    assert result["stagedPatch"]["mode"] == "review_bundle"
    assert result["stagedPatch"]["changedTargetCount"] == 2
    changed_ids = {target["targetId"] for target in result["stagedPatch"]["changedTargets"]}
    assert changed_ids == {"primary-agent", "shared-guidance"}
    assert result["stagedPatchReviewBundle"] == {
        "status": "ready",
        "bundlePath": result["artifacts"]["stagedPatchBundle"]["actualPath"],
        "bundleFound": True,
        "candidateId": result["stagedPatch"]["candidateId"],
        "changedTargetCount": 2,
        "changedTargetIds": ["primary-agent", "shared-guidance"],
        "primaryChangedTargetIds": ["primary-agent"],
        "reviewerHints": ["Review both bundle targets before apply-best."],
        "requiredHumanAction": (
            "Review the staged patch bundle and governed artifacts before choosing the next "
            "bounded step."
        ),
    }
    staged_patch_bundle = json.loads(
        Path(result["artifacts"]["stagedPatchBundle"]["actualPath"]).read_text(encoding="utf-8")
    )
    assert staged_patch_bundle["type"] == "AutoAgentStagedPatchReviewBundle"
    assert staged_patch_bundle["status"] == "ready"
    assert staged_patch_bundle["summary"] == {
        "changedTargetCount": 2,
        "changedTargetIds": ["primary-agent", "shared-guidance"],
        "primaryChangedTargetIds": ["primary-agent"],
        "hasChanges": True,
    }
    assert staged_patch_bundle["candidate"] == {
        "candidateId": result["stagedPatch"]["candidateId"],
        "candidatePath": result["stagedPatch"]["candidatePath"],
        "changedTargetCount": 2,
    }
    assert staged_patch_bundle["changedTargets"] == [
        {
            "targetId": "primary-agent",
            "sourcePath": (working_dir / "onboarding-helper.agent.md").as_posix(),
            "primary": True,
            "kind": "agent_profile",
            "mutableRegions": ["body", "frontmatter.tools"],
            "candidateSnapshotPath": result["stagedPatch"]["changedTargets"][0][
                "candidateSnapshotPath"
            ],
            "changedRegions": ["body"],
            "frontmatterChangedKeys": [],
        },
        {
            "targetId": "shared-guidance",
            "sourcePath": (working_dir / "shared-guidance.md").as_posix(),
            "primary": False,
            "kind": "markdown_document",
            "mutableRegions": ["body"],
            "candidateSnapshotPath": result["stagedPatch"]["changedTargets"][1][
                "candidateSnapshotPath"
            ],
            "changedRegions": ["body"],
            "frontmatterChangedKeys": [],
        },
    ]
    assert result["provenance"]["inputs"]["experiment"]["path"].endswith(
        "bundle-extended-experiment.md"
    )
    assert len(result["provenance"]["inputs"]["experiment"]["sha256"]) == 64
    assert result["provenance"]["inputs"]["liveEvaluatorPrompt"]["path"].endswith("judge-prompt.md")
    assert result["provenance"]["evidence"]["sources"]["runSnapshots"] == ["test-run"]
    assert result["provenance"]["artifacts"]["stagedPatchBundlePath"].endswith(
        "staged-patch-review-bundle.json"
    )
    assert result["provenance"]["artifacts"]["reportPath"].endswith("autoagent-report.md")

    report_text = (docs_agents / "autoagent-report.md").read_text(encoding="utf-8")
    assert "- Staged patch bundle: ready" in report_text
    assert (
        f"- Staged patch bundle artifact: {result['artifacts']['stagedPatchBundle']['actualPath']}"
    ) in report_text
    assert "- Staged patch bundle targets: primary-agent, shared-guidance" in report_text
    assert (
        "- Staged patch bundle required action: Review the staged patch bundle and governed "
        "artifacts before choosing the next bounded step."
    ) in report_text


def test_autoagent_loop_collects_optional_debug_logs(tmp_path: Path) -> None:
    module = load_module()
    docs_agents, working_dir = prepare_multi_target_workspace(tmp_path)
    module.ROOT = tmp_path
    module.DOCS_AGENTS_DIR = docs_agents

    debug_log = tmp_path / "logs" / "copilot-debug.log"
    debug_log.parent.mkdir(parents=True, exist_ok=True)
    debug_log.write_text(
        "INFO startup complete\n"
        "WARN review blocker for candidate\n"
        "ERROR Bearer secret-token C:/Outside/secret.txt\n",
        encoding="utf-8",
    )

    experiment = working_dir / "bundle-debug-log-experiment.md"
    write_experiment(
        experiment,
        "\n".join(
            [
                "name: bundle-debug-log",
                "optimizationTargets:",
                "  - id: primary-agent",
                "    path: onboarding-helper.agent.md",
                "    kind: agent_profile",
                "    primary: true",
                "    mutableRegions:",
                "      - body",
                "      - frontmatter.tools",
                "  - id: shared-guidance",
                "    path: shared-guidance.md",
                "    kind: markdown_document",
                "    mutableRegions:",
                "      - body",
                "benchmarkPath: bundle-benchmark.json",
                "mutationCatalogPath: bundle-mutations.json",
                "evidencePolicy:",
                "  includeCurrentArtifacts: true",
                "  includeHookAudit: true",
                "  includeVsCodeLogs: true",
                "  vsCodeLogPaths:",
                f"    - {debug_log.as_posix()}",
            ]
        ),
    )

    module.run_autoagent_loop(
        experiment_path=experiment.resolve(),
        output_root=(tmp_path / "generated" / "autoagent-runs").resolve(),
        report_path=(docs_agents / "autoagent-report.md").resolve(),
        results_path=(docs_agents / "autoagent-results.tsv").resolve(),
        max_iterations=0,
        apply_best=False,
    )

    evidence = json.loads((docs_agents / "autoagent-evidence.json").read_text(encoding="utf-8"))
    assert evidence["summary"]["externalLogRecordCount"] == 2
    assert evidence["summary"]["externalSourceCount"] == 1
    assert evidence["sources"]["externalLogs"][0]["kind"] == "vscode_debug_log"

    serialized = json.dumps(evidence)
    assert "secret-token" not in serialized
    assert "C:/Outside/secret.txt" not in serialized
    assert "[external-path]" in serialized
