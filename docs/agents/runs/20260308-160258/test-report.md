# Test Report

## Summary
- **Status:** READY_FOR_QUALITY_GATE
- **Goal:** Record deterministic validation evidence for the broader governed bundle slice that adds `AGENTS.md` to the checked-in manager bundle.
- **Produced at:** 2026-04-14T22:18:00Z
- **Author:** test-engineer

## Current posture
- Focused deterministic validation passed for the expanded three-target governed bundle contract.
- The first canonical rerun exposed a real contract failure: `AGENTS.md` lacked the YAML frontmatter required by the markdown target loader. Adding minimal frontmatter fixed the failure at the root cause.
- The final canonical rerun refreshed the report, results, evidence, and trace for the new three-target bundle while keeping the experiment manual and `report_only`.
- The canonical run kept baseline at `1.0`, so both negative mutations were discarded and the staged review bundle remained `ready_no_changes`.

## Validation evidence
- Ran focused deterministic pytest coverage for staged patch reporting, the checked-in bundle contract, and reviewed-learning imports before and after the AGENTS compatibility fix.
- Re-ran the canonical AutoAgent experiment through [docs/agents/autoagent-experiment.md](docs/agents/autoagent-experiment.md) after adding frontmatter to [AGENTS.md](AGENTS.md).
- Confirmed the refreshed canonical report, results, and trace now show a three-target bundle, `14/14` passing checks for baseline, and a second discarded mutation `weaken-agent-guide-governance`.
- Confirmed the captured `quick_test.ps1` transcript shows `check_agent_paths`, `check_agent_system`, Ruff format, Ruff check, mypy, and the quick pytest subset all passing.
- Verified machine-parseable governed state with `JSON_OK` and root/run parity with `PARITY_OK` after refreshing the report layer and resynchronizing the active run snapshot.

## Flake posture
- **Risk:** low
- **Notes:**
  - Validation stayed offline and deterministic.
  - The checked-in experiment remained manual and `report_only`.
  - The Windows shell transcript is still noisy for longer PowerShell commands, so fast-suite evidence was taken from the captured transcript rather than the inline terminal stream.

## Known issues / blockers
- No slice-specific validation blockers remain.
- The Windows host still prints benign `compileall` warnings for temp directories, but the fast suite completed successfully.

## Handoff to Quality Gate
- **Current posture:** ready for quality gate.
- **Why:** the expanded governed bundle contract is locked by focused tests, the canonical rerun passed after the root-cause fix, the fast suite passed, and the governed artifacts are resynchronized.
- **Focus areas:**
  - AGENTS loader compatibility and the minimal frontmatter fix
  - three-target bundle correctness in the canonical AutoAgent outputs
  - refreshed governed task/report parity after closing the slice

```json
{
  "type": "TestReport",
  "status": "READY_FOR_QUALITY_GATE",
  "goal": "Record deterministic validation evidence for the broader governed bundle slice that adds AGENTS.md to the checked-in manager bundle.",
  "acceptanceCovered": [
    "AC1",
    "AC2",
    "AC3",
    "AC4"
  ],
  "testsRun": [
    {
      "command": "py -3 -m pytest tests/test_autoagent_loop_runner.py::test_autoagent_loop_report_includes_staged_patch_and_provenance tests/test_autoagent_loop_runner.py::test_checked_in_autoagent_experiment_uses_manager_bundle_targets tests/test_autoagent_loop_runner.py::test_autoagent_loop_imports_approved_learning_drafts_with_review_manifest --basetemp ./.tmp/pytest-broader-bundle-rerun",
      "result": "pass",
      "notes": "Focused deterministic coverage passed after the AGENTS frontmatter fix and locked the expanded governed bundle contract."
    },
    {
      "command": "py -3 scripts/run_autoagent_loop.py --experiment docs/agents/autoagent-experiment.md",
      "result": "pass",
      "notes": "The final canonical AutoAgent rerun refreshed the report, results, evidence, and trace for the three-target bundle. Baseline remained best at 1.0, while the negative mutations were discarded at 0.818182 and 0.848485."
    },
    {
      "command": "pwsh -File ./scripts/ci/quick_test.ps1",
      "result": "pass",
      "notes": "The captured quick-suite transcript shows check_agent_paths PASS, agent-system-consistency PASS, Ruff format PASS, Ruff check PASS, mypy success on 19 source files, the quick pytest subset PASS, and quick_test PASS."
    },
    {
      "command": "py -3 -m json.tool docs/agents/state.json > $null",
      "result": "pass",
      "notes": "The governed lifecycle state remained valid JSON after closing the broader governed bundle slice."
    },
    {
      "command": "py -3 -c \"from pathlib import Path; pairs=[('docs/agents/task-spec.md','docs/agents/runs/20260308-160258/task-spec.md'),('docs/agents/state.json','docs/agents/runs/20260308-160258/state.json'),('docs/agents/patch-report.md','docs/agents/runs/20260308-160258/patch-report.md'),('docs/agents/test-report.md','docs/agents/runs/20260308-160258/test-report.md'),('docs/agents/review-report.md','docs/agents/runs/20260308-160258/review-report.md'),('docs/agents/release-report.md','docs/agents/runs/20260308-160258/release-report.md'),('docs/agents/autoagent-experiment.md','docs/agents/runs/20260308-160258/autoagent-experiment.md'),('docs/agents/autoagent-report.md','docs/agents/runs/20260308-160258/autoagent-report.md'),('docs/agents/autoagent-results.tsv','docs/agents/runs/20260308-160258/autoagent-results.tsv'),('docs/agents/autoagent-evidence.json','docs/agents/runs/20260308-160258/autoagent-evidence.json')]; assert all(Path(left).read_text(encoding='utf-8') == Path(right).read_text(encoding='utf-8') for left,right in pairs); print('PARITY_OK')\"",
      "result": "pass",
      "notes": "Root and active-run governed artifacts matched after the refreshed report layer was mirrored into the active run snapshot."
    }
  ],
  "plannedTests": [],
  "flakeAssessment": {
    "risk": "low",
    "notes": [
      "Validation stayed offline and deterministic.",
      "The checked-in experiment still runs under manual and report_only semantics.",
      "The Windows shell transcript is noisy for longer PowerShell commands on this host."
    ],
    "mitigationsApplied": [
      "Fixed the AGENTS loader failure by adding minimal frontmatter instead of changing runtime behavior.",
      "Used the repo-standard quick suite and captured its verdict from the transcript that completed successfully.",
      "Re-ran the canonical experiment and rechecked governed artifact parity after refreshing the report layer."
    ]
  },
  "coverageNotes": [
    "The canonical AutoAgent outputs now show a three-target governed manager bundle and 14 benchmark checks for baseline.",
    "The canonical results table now includes two discarded negative mutations: relax-no-product-code-boundary and weaken-agent-guide-governance.",
    "The generated trace now records agent-operating-guide as part of the target bundle and the AGENTS-specific benchmark checks.",
    "The checked-in experiment remains manual and report_only.",
    "The next bounded step should focus on reviewer workflow polish or another manager-shared governed artifact, not unattended continuation."
  ],
  "knownIssues": [
    {
      "category": "environment",
      "evidence": "The fast-suite transcript still prints benign compileall warnings for temp directories on this host.",
      "nextStep": "Treat the warnings as environment noise unless they start masking a real compile failure."
    }
  ],
  "handoffToQualityGate": {
    "focusAreas": [
      "AGENTS loader compatibility and the minimal frontmatter fix",
      "Three-target bundle correctness in canonical outputs",
      "Refreshed governed task/report parity"
    ],
    "commandsToReRun": [
      "py -3 -m pytest tests/test_autoagent_loop_runner.py::test_autoagent_loop_report_includes_staged_patch_and_provenance tests/test_autoagent_loop_runner.py::test_checked_in_autoagent_experiment_uses_manager_bundle_targets tests/test_autoagent_loop_runner.py::test_autoagent_loop_imports_approved_learning_drafts_with_review_manifest --basetemp ./.tmp/pytest-broader-bundle-rerun",
      "py -3 scripts/run_autoagent_loop.py --experiment docs/agents/autoagent-experiment.md",
      "pwsh -File ./scripts/ci/quick_test.ps1",
      "py -3 -m json.tool docs/agents/state.json > $null"
    ],
    "riskHotspots": [
      "docs/agents/autoagent-experiment.md",
      ".github/skills/autoagent-loop/examples/team-lead-benchmark.json",
      ".github/skills/autoagent-loop/examples/team-lead-mutations.json",
      "AGENTS.md",
      "tests/test_autoagent_loop_runner.py"
    ]
  }
}
```
