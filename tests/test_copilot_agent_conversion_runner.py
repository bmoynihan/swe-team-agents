from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_copilot_agent_conversion.py"
SOURCE_AGENT = ROOT / ".github" / "agents" / "hello-repo-guide.agent.md"


def load_module():
    spec = importlib.util.spec_from_file_location("copilot_agent_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_run_pipeline_writes_validation_artifacts(monkeypatch) -> None:
    module = load_module()
    sandbox_root = Path(tempfile.mkdtemp(prefix="runner-", dir=ROOT / ".tmp"))

    class FakeEmitter:
        def emit_package(self, source_path, output_root, targets, report_path, status):
            package_root = output_root / "hello-repo-guide"
            (package_root / "scripts").mkdir(parents=True)
            (package_root / "normalized-agent-spec.json").write_text("{}", encoding="utf-8")
            return {
                "sourceAgent": source_path.as_posix(),
                "packageRoot": package_root.as_posix(),
                "targets": targets,
                "normalizedSpec": (package_root / "normalized-agent-spec.json").as_posix(),
                "generatedFiles": [],
                "determinism": "high",
                "manualReviewReasons": [],
                "appName": "hello-repo-guide-app",
                "report": {
                    "requestedPath": report_path.as_posix(),
                    "actualPath": report_path.as_posix(),
                    "fallbackUsed": False,
                    "warning": None,
                    "runSnapshot": None,
                },
            }

        def write_docs_artifact(self, path, content):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {
                "requestedPath": path.as_posix(),
                "actualPath": path.as_posix(),
                "fallbackUsed": False,
                "warning": None,
                "runSnapshot": None,
            }

    def fake_run_command(command, cwd):
        if "local_smoke_test.mjs" in " ".join(command):
            return json.dumps(
                {
                    "health": {"status": "ok", "runtimeMode": "mock"},
                    "invoke": {"runtime": {"mode": "mock"}, "message": "Hello from test."},
                }
            )
        return ""

    monkeypatch.setattr(module, "_load_emitter", lambda: FakeEmitter())
    monkeypatch.setattr(module, "_find_command", lambda *candidates: candidates[0])
    monkeypatch.setattr(module, "_run_command", fake_run_command)

    try:
        result = module.run_pipeline(
            source_path=SOURCE_AGENT,
            output_root=sandbox_root / "generated",
            targets=["copilot-sdk-service", "databricks-app"],
            report_path=sandbox_root / "docs" / "agents" / "copilot-agent-conversion-report.md",
            status="READY_FOR_QUALITY_GATE",
            install_dependencies=True,
            run_smoke_test=True,
            deploy_databricks=False,
            databricks_profile=None,
            databricks_app_name=None,
            databricks_workspace_root=None,
            timeout_seconds=600,
            poll_seconds=10,
        )

        package_root = Path(result["packageRoot"])
        smoke_path = Path(result["artifacts"]["smokeTest"])
        pipeline_result_path = package_root / "conversion-run-result.json"

        assert smoke_path.exists()
        assert json.loads(smoke_path.read_text(encoding="utf-8"))["health"]["status"] == "ok"
        assert pipeline_result_path.exists()
        pipeline_result = json.loads(pipeline_result_path.read_text(encoding="utf-8"))
        assert len(pipeline_result["validation"]) == 2
        assert pipeline_result["validation"][0]["check"] == "npm-install"
        assert pipeline_result["validation"][1]["check"] == "local-smoke-test"
    finally:
        shutil.rmtree(sandbox_root, ignore_errors=True)
