from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EMITTER_PATH = (
    ROOT / ".github" / "skills" / "copilot-agent-converter" / "scripts" / "emit_target_scaffolds.py"
)
SOURCE_AGENT = ROOT / ".github" / "agents" / "hello-repo-guide.agent.md"


def load_module():
    spec = importlib.util.spec_from_file_location("copilot_agent_emitter", EMITTER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_emit_package_generates_service_and_databricks_app() -> None:
    module = load_module()
    sandbox_root = Path(tempfile.mkdtemp(prefix="emitter-", dir=ROOT / ".tmp"))
    try:
        report_path = sandbox_root / "copilot-agent-conversion-report.md"

        result = module.emit_package(
            source_path=SOURCE_AGENT,
            output_root=sandbox_root,
            targets=["copilot-sdk-service", "databricks-app"],
            report_path=report_path,
            status="READY_FOR_TEST_ENGINEER",
        )

        package_root = Path(result["packageRoot"])
        assert package_root.name == "hello-repo-guide"
        assert (package_root / "normalized-agent-spec.json").exists()
        assert (package_root / "app.yaml").exists()
        assert (package_root / "src" / "server.js").exists()
        assert (package_root / "scripts" / "deploy_databricks_app.py").exists()

        package_json = json.loads((package_root / "package.json").read_text(encoding="utf-8"))
        assert package_json["dependencies"]["@github/copilot-sdk"] == "0.2.0"
        assert package_json["dependencies"]["@github/copilot"] == "1.0.17"

        server_js = (package_root / "src" / "server.js").read_text(encoding="utf-8")
        assert '"/invoke"' in server_js
        assert 'runtimeMode: "mock"' not in server_js

        app_yaml = (package_root / "app.yaml").read_text(encoding="utf-8")
        assert "COPILOT_RUNTIME_MODE" in app_yaml
        assert '"mock"' in app_yaml

        report = report_path.read_text(encoding="utf-8")
        assert SOURCE_AGENT.as_posix() in report
        assert report.count("```json") == 1
        assert result["manualReviewReasons"] == []
    finally:
        shutil.rmtree(sandbox_root, ignore_errors=True)


def test_emit_package_falls_back_when_report_target_is_locked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module()
    sandbox_root = Path(tempfile.mkdtemp(prefix="emitter-", dir=ROOT / ".tmp"))
    fake_root = sandbox_root / "repo"
    docs_agents = fake_root / "docs" / "agents"
    run_root = docs_agents / "runs" / "test-run"
    run_root.mkdir(parents=True)
    (run_root / "hook-audit").mkdir()
    (docs_agents / "current-run.json").write_text(
        json.dumps(
            {
                "currentRunId": "test-run",
                "currentRunPath": "docs/agents/runs/test-run",
            }
        ),
        encoding="utf-8",
    )

    original_write = module._write

    def flaky_write(path: Path, content: str) -> None:
        if path == docs_agents / "copilot-agent-conversion-report.md":
            raise PermissionError("locked for test")
        original_write(path, content)

    monkeypatch.setattr(module, "ROOT", fake_root)
    monkeypatch.setattr(module, "DOCS_AGENTS_DIR", docs_agents)
    monkeypatch.setattr(module, "_write", flaky_write)

    try:
        report_path = docs_agents / "copilot-agent-conversion-report.md"
        result = module.emit_package(
            source_path=SOURCE_AGENT,
            output_root=sandbox_root / "generated",
            targets=["copilot-sdk-service", "databricks-app"],
            report_path=report_path,
            status="READY_FOR_TEST_ENGINEER",
        )

        report = result["report"]
        assert report["fallbackUsed"] is True
        assert report["actualPath"].endswith("copilot-agent-conversion-report.generated.md")

        actual_report = Path(report["actualPath"])
        assert actual_report.exists()

        run_snapshot = report["runSnapshot"]
        assert run_snapshot is not None
        assert run_snapshot["actualPath"].endswith(
            "docs/agents/runs/test-run/copilot-agent-conversion-report.generated.md"
        )
        assert Path(run_snapshot["actualPath"]).exists()
    finally:
        shutil.rmtree(sandbox_root, ignore_errors=True)
