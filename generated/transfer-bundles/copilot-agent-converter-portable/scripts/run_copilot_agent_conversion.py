#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EMITTER_PATH = (
    ROOT
    / ".github"
    / "skills"
    / "copilot-agent-converter"
    / "scripts"
    / "emit_target_scaffolds.py"
)
DEFAULT_REPORT_PATH = ROOT / "docs" / "agents" / "copilot-agent-conversion-report.md"
DEFAULT_OUTPUT_ROOT = ROOT / "generated" / "copilot-agent-packages"


def _json(data: Any) -> str:
    return json.dumps(data, indent=2) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _load_emitter():
    spec = importlib.util.spec_from_file_location("copilot_agent_emitter", EMITTER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _find_command(*candidates: str) -> str:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise FileNotFoundError(f"Required command not found on PATH: {', '.join(candidates)}")


def _run_command(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if completed.returncode != 0:
        details = [f"Command failed with exit code {completed.returncode}: {' '.join(command)}"]
        if stdout:
            details.append(f"stdout:\n{stdout}")
        if stderr:
            details.append(f"stderr:\n{stderr}")
        raise RuntimeError("\n\n".join(details))
    return stdout


def _summarize_deployment(payload: dict[str, Any]) -> dict[str, Any]:
    app = payload.get("app", {})
    health = payload.get("health", {})
    deploy_request = payload.get("deployRequest", {})
    return {
        "appName": app.get("name"),
        "url": health.get("url") or app.get("url"),
        "appState": health.get("appState"),
        "deploymentId": health.get("deploymentId") or deploy_request.get("deploymentId"),
        "deploymentState": health.get("deploymentState"),
        "sourceCodePath": deploy_request.get("sourceCodePath"),
    }


def _render_lock_note(report_artifact: dict[str, Any] | None) -> str:
    lines = ["# Artifact Lock Note", ""]
    if not report_artifact:
        lines.extend(
            [
                "No `docs/agents` report artifact was requested for this run.",
                "",
            ]
        )
        return "\n".join(lines)

    run_snapshot = report_artifact.get("runSnapshot") or {}
    report_fallback = bool(report_artifact.get("fallbackUsed"))
    snapshot_fallback = bool(run_snapshot.get("fallbackUsed"))

    if report_fallback or snapshot_fallback:
        lines.extend(
            [
                "The preferred `docs/agents` report target could not be updated directly, so this run wrote a fallback artifact.",
                "",
                f"- Requested report path: `{report_artifact['requestedPath']}`",
                f"- Actual report path: `{report_artifact['actualPath']}`",
            ]
        )
        if report_artifact.get("warning"):
            lines.append(f"- Root write warning: `{report_artifact['warning']}`")
        if run_snapshot:
            lines.append(f"- Run snapshot path: `{run_snapshot.get('actualPath')}`")
            if run_snapshot.get("warning"):
                lines.append(f"- Run snapshot warning: `{run_snapshot['warning']}`")
    else:
        lines.extend(
            [
                "No `docs/agents` write-lock fallback was required for this run.",
                "",
                f"- Report path: `{report_artifact['actualPath']}`",
            ]
        )
        if run_snapshot:
            lines.append(f"- Run snapshot path: `{run_snapshot.get('actualPath')}`")

    lines.append("")
    return "\n".join(lines)


def run_pipeline(
    source_path: Path,
    output_root: Path,
    targets: list[str],
    report_path: Path | None,
    status: str,
    install_dependencies: bool,
    run_smoke_test: bool,
    deploy_databricks: bool,
    databricks_profile: str | None,
    databricks_app_name: str | None,
    databricks_workspace_root: str | None,
    timeout_seconds: int,
    poll_seconds: int,
) -> dict[str, Any]:
    emitter = _load_emitter()
    emission = emitter.emit_package(
        source_path=source_path,
        output_root=output_root,
        targets=targets,
        report_path=report_path,
        status=status,
    )

    package_root = Path(emission["packageRoot"])
    result: dict[str, Any] = {
        "sourceAgent": emission["sourceAgent"],
        "packageRoot": emission["packageRoot"],
        "targets": emission["targets"],
        "normalizedSpec": emission["normalizedSpec"],
        "determinism": emission["determinism"],
        "manualReviewReasons": emission["manualReviewReasons"],
        "artifacts": {
            "report": emission.get("report"),
        },
        "validation": [],
    }

    lock_note_path = ROOT / "docs" / "agents" / "artifact-lock-note.md"
    lock_note_result = emitter.write_docs_artifact(
        lock_note_path,
        _render_lock_note(emission.get("report")),
    )
    result["artifacts"]["artifactLockNote"] = lock_note_result

    if install_dependencies:
        npm_command = _find_command("npm.cmd", "npm")
        _run_command([npm_command, "install"], cwd=package_root)
        result["validation"].append(
            {
                "check": "npm-install",
                "result": "pass",
                "evidence": package_root.as_posix(),
            }
        )

    if run_smoke_test:
        node_command = _find_command("node.exe", "node")
        smoke_output = _run_command([node_command, "./scripts/local_smoke_test.mjs"], cwd=package_root)
        smoke_payload = json.loads(smoke_output)
        smoke_path = package_root / "smoke-test-result.json"
        _write(smoke_path, _json(smoke_payload))
        result["artifacts"]["smokeTest"] = smoke_path.as_posix()
        result["validation"].append(
            {
                "check": "local-smoke-test",
                "result": "pass",
                "evidence": smoke_path.as_posix(),
            }
        )

    if deploy_databricks:
        deploy_command = [
            sys.executable,
            "scripts/deploy_databricks_app.py",
        ]
        if databricks_profile:
            deploy_command.extend(["--profile", databricks_profile])
        if databricks_app_name:
            deploy_command.extend(["--app-name", databricks_app_name])
        if databricks_workspace_root:
            deploy_command.extend(["--workspace-root", databricks_workspace_root])
        deploy_command.extend(
            [
                "--timeout-seconds",
                str(timeout_seconds),
                "--poll-seconds",
                str(poll_seconds),
            ]
        )
        deploy_output = _run_command(deploy_command, cwd=package_root)
        deploy_payload = json.loads(deploy_output)
        deploy_summary = _summarize_deployment(deploy_payload)
        deploy_path = package_root / "databricks-deploy-result.json"
        _write(deploy_path, _json(deploy_summary))
        result["artifacts"]["databricksDeploy"] = deploy_path.as_posix()
        result["validation"].append(
            {
                "check": "databricks-app-deploy",
                "result": "pass",
                "evidence": deploy_path.as_posix(),
            }
        )

    run_result_path = package_root / "conversion-run-result.json"
    result["artifacts"]["pipelineResult"] = run_result_path.as_posix()
    _write(run_result_path, _json(result))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit, validate, and optionally deploy a converted Copilot agent package."
    )
    parser.add_argument("--input", required=True, help="Path to the source .agent.md file.")
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT.as_posix(),
        help="Folder where generated packages should be written.",
    )
    parser.add_argument(
        "--target",
        action="append",
        choices=["copilot-sdk-service", "databricks-app"],
        dest="targets",
        help="Target package to generate. May be supplied multiple times.",
    )
    parser.add_argument(
        "--report",
        default=DEFAULT_REPORT_PATH.as_posix(),
        help="Preferred docs/agents report path. The runner falls back safely if it is write-locked.",
    )
    parser.add_argument(
        "--status",
        default="READY_FOR_QUALITY_GATE",
        help="Status string to write into the conversion report.",
    )
    parser.add_argument(
        "--skip-npm-install",
        action="store_true",
        help="Skip npm install inside the generated package.",
    )
    parser.add_argument(
        "--skip-smoke-test",
        action="store_true",
        help="Skip the local deterministic smoke test.",
    )
    parser.add_argument(
        "--deploy-databricks",
        action="store_true",
        help="Deploy the generated package as a Databricks App after local validation.",
    )
    parser.add_argument("--profile", help="Optional Databricks auth profile for deployment.")
    parser.add_argument("--app-name", help="Optional Databricks App name override.")
    parser.add_argument("--workspace-root", help="Optional Databricks workspace upload root.")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--poll-seconds", type=int, default=10)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_pipeline(
        source_path=Path(args.input).resolve(),
        output_root=Path(args.output_root).resolve(),
        targets=args.targets or ["copilot-sdk-service", "databricks-app"],
        report_path=Path(args.report).resolve() if args.report else None,
        status=args.status,
        install_dependencies=not args.skip_npm_install,
        run_smoke_test=not args.skip_smoke_test,
        deploy_databricks=args.deploy_databricks,
        databricks_profile=args.profile,
        databricks_app_name=args.app_name,
        databricks_workspace_root=args.workspace_root,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
