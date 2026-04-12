from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_check_agent_system_module():
    script_path = ROOT / "scripts" / "ci" / "check_agent_system.py"
    spec = importlib.util.spec_from_file_location("check_agent_system", script_path)
    if spec is None or spec.loader is None:
        raise AssertionError("Failed to load check_agent_system module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_check_agent_paths(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "ci" / "check_agent_paths.py"),
            "--root",
            str(root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_check_agent_paths_fails_when_forbidden_token_present(tmp_path: Path) -> None:
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "bad.md").write_text("Use docs/agent/report.md\n", encoding="utf-8")

    result = run_check_agent_paths(tmp_path)

    assert result.returncode == 1
    assert "docs/agent/" in result.stdout


def test_check_agent_paths_ignores_generated_and_cache_paths(tmp_path: Path) -> None:
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "good.md").write_text(
        "docs/agents/review-report.md\n", encoding="utf-8"
    )
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "ok.sh").write_text("echo ok\n", encoding="utf-8")
    (tmp_path / "docs" / "agents" / "runs" / "run-1").mkdir(parents=True)
    (tmp_path / "docs" / "agents" / "runs" / "run-1" / "stale.md").write_text(
        "docs/agent/ignored.md\n", encoding="utf-8"
    )
    (tmp_path / "scripts" / "__pycache__").mkdir()
    (tmp_path / "scripts" / "__pycache__" / "ignored.py").write_text(
        "docs/agent/ignored.py\n", encoding="utf-8"
    )
    (tmp_path / "AGENTS.md").write_text("docs/agents/current-run.json\n", encoding="utf-8")

    result = run_check_agent_paths(tmp_path)

    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_check_agent_system_iter_text_files_ignores_generated_and_cache_paths(
    tmp_path: Path,
) -> None:
    module = load_check_agent_system_module()
    module.ROOT = tmp_path

    included = tmp_path / ".github" / "agents" / "good.agent.md"
    included.parent.mkdir(parents=True, exist_ok=True)
    included.write_text("agent body\n", encoding="utf-8")

    generated = tmp_path / "generated" / "autoagent-runs" / "run-1" / "artifact.md"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text("generated artifact\n", encoding="utf-8")

    run_snapshot = tmp_path / "docs" / "agents" / "runs" / "run-1" / "report.md"
    run_snapshot.parent.mkdir(parents=True, exist_ok=True)
    run_snapshot.write_text("run snapshot\n", encoding="utf-8")

    mypy_cache = tmp_path / ".mypy_cache" / "3.11" / "cached.json"
    mypy_cache.parent.mkdir(parents=True, exist_ok=True)
    mypy_cache.write_text("cached\n", encoding="utf-8")

    pycache = tmp_path / "scripts" / "__pycache__" / "cached.py"
    pycache.parent.mkdir(parents=True, exist_ok=True)
    pycache.write_text("cached\n", encoding="utf-8")

    files = {path.relative_to(tmp_path).as_posix() for path in module.iter_text_files()}

    assert ".github/agents/good.agent.md" in files
    assert "generated/autoagent-runs/run-1/artifact.md" not in files
    assert "docs/agents/runs/run-1/report.md" not in files
    assert ".mypy_cache/3.11/cached.json" not in files
    assert "scripts/__pycache__/cached.py" not in files


def test_ci_entrypoints_delegate_to_python_runners() -> None:
    quick_sh = (ROOT / "scripts" / "ci" / "quick_test.sh").read_text(encoding="utf-8")
    full_sh = (ROOT / "scripts" / "ci" / "full_test.sh").read_text(encoding="utf-8")
    quick_ps1 = (ROOT / "scripts" / "ci" / "quick_test.ps1").read_text(encoding="utf-8")
    full_ps1 = (ROOT / "scripts" / "ci" / "full_test.ps1").read_text(encoding="utf-8")

    assert "quick_test.py" in quick_sh
    assert "full_test.py" in full_sh
    assert "quick_test.py" in quick_ps1
    assert "full_test.py" in full_ps1


def test_quick_test_scopes_ci_tools_to_first_party_paths() -> None:
    quick_test = (ROOT / "scripts" / "ci" / "quick_test.py").read_text(encoding="utf-8")
    ci_runner = (ROOT / "scripts" / "ci" / "ci_runner.py").read_text(encoding="utf-8")

    assert "first_party_python_targets" in quick_test
    assert '["ruff", "format", "--check", *python_targets]' in quick_test
    assert '["ruff", "check", *python_targets]' in quick_test
    assert "mypy_targets = [" in quick_test
    assert '["mypy", *mypy_targets]' in quick_test
    assert 'run_optional("ruff", ["ruff", "format", "--check", "."], env=env)' not in quick_test
    assert 'run_optional("ruff", ["ruff", "check", "."], env=env)' not in quick_test
    assert 'run_command(["mypy", "."], env=env)' not in quick_test
    assert 'os.environ.get("RUFF_TARGETS")' in ci_runner
