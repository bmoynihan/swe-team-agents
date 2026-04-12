#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import time
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.apps import App, AppDeployment
from databricks.sdk.service.workspace import ImportFormat


APP_NAME_DEFAULT = "hello-repo-guide-app"
SUCCESS_STATES = {"ACTIVE", "READY", "RUNNING", "SUCCEEDED", "HEALTHY"}
FAILURE_STATES = {"FAILED", "ERROR", "CANCELED", "CANCELLED"}
EXCLUDED_DIRS = {"node_modules", ".git", ".copilot-state", "__pycache__"}


def _state_text(value) -> str:
    if value is None:
        return ""
    return str(value).split(".")[-1].upper()


def _iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def _workspace_root(client: WorkspaceClient, explicit_root: str | None, package_slug: str) -> str:
    if explicit_root:
        return explicit_root.rstrip("/")

    try:
        user_name = client.current_user.me().user_name
    except Exception:
        user_name = None

    if user_name:
        return f"/Workspace/Users/{user_name}/generated/copilot-agent-packages/{package_slug}"
    return f"/Workspace/Shared/generated/copilot-agent-packages/{package_slug}"


def _upload_folder(client: WorkspaceClient, local_root: Path, workspace_root: str) -> dict:
    client.workspace.mkdirs(workspace_root)
    uploaded = []
    for file_path in _iter_files(local_root):
        relative = file_path.relative_to(local_root).as_posix()
        remote_path = f"{workspace_root}/{relative}"
        parent = remote_path.rsplit("/", 1)[0]
        client.workspace.mkdirs(parent)
        with file_path.open("rb") as handle:
            client.workspace.upload(
                path=remote_path,
                content=io.BytesIO(handle.read()),
                format=ImportFormat.AUTO,
                overwrite=True,
            )
        uploaded.append(remote_path)
    return {
        "localRoot": local_root.as_posix(),
        "workspaceRoot": workspace_root,
        "uploadedFiles": uploaded,
    }


def _ensure_app(client: WorkspaceClient, name: str, description: str) -> dict:
    try:
        app = client.apps.get(name=name)
        created = False
    except Exception:
        app = client.apps.create(app=App(name=name, description=description)).response
        created = True
    return {
        "created": created,
        "name": getattr(app, "name", name),
        "url": getattr(app, "url", None),
    }


def _ensure_started(client: WorkspaceClient, name: str) -> None:
    app = client.apps.get(name=name)
    state = _app_state(app)
    if state in SUCCESS_STATES or state == "STARTING":
        return
    client.apps.start(name=name).result(timeout=dt.timedelta(minutes=20))


def _deployment_state(deployment) -> str:
    if deployment is None:
        return ""
    return _state_text(getattr(getattr(deployment, "status", None), "state", None))


def _app_state(app) -> str:
    if app is None:
        return ""
    compute_status = getattr(app, "compute_status", None)
    if compute_status is not None:
        return _state_text(getattr(compute_status, "state", None))
    return _state_text(getattr(app, "status", None))


def _get_logs(client: WorkspaceClient, app_name: str, deployment_id: str | None):
    if not deployment_id:
        return None
    try:
        response = client.api_client.do(
            "GET",
            f"/api/2.0/apps/{app_name}/deployments/{deployment_id}/logs",
        )
        return response.get("logs")
    except Exception:
        return None


def _wait_for_health(client: WorkspaceClient, name: str, timeout_seconds: int, poll_seconds: int) -> dict:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        app = client.apps.get(name=name)
        active = getattr(app, "active_deployment", None)
        app_state = _app_state(app)
        deployment_state = _deployment_state(active)
        if app_state in FAILURE_STATES or deployment_state in FAILURE_STATES:
            raise RuntimeError(
                f"Deployment failed with app_state={app_state} deployment_state={deployment_state}"
            )
        if app_state in SUCCESS_STATES and (
            not deployment_state or deployment_state in SUCCESS_STATES
        ):
            deployment_id = getattr(active, "deployment_id", None)
            return {
                "appState": app_state,
                "deploymentState": deployment_state,
                "deploymentId": deployment_id,
                "url": getattr(app, "url", None),
            }
        time.sleep(poll_seconds)
    raise TimeoutError(f"App '{name}' did not become healthy within {timeout_seconds}s")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy the generated Copilot agent package as a Databricks App.")
    parser.add_argument("--app-name", default=APP_NAME_DEFAULT)
    parser.add_argument("--profile")
    parser.add_argument("--workspace-root")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--poll-seconds", type=int, default=10)
    args = parser.parse_args()

    package_root = Path(__file__).resolve().parents[1]
    client = WorkspaceClient(profile=args.profile) if args.profile else WorkspaceClient()

    workspace_root = _workspace_root(client, args.workspace_root, package_root.name)
    upload_result = _upload_folder(client, package_root, workspace_root)
    app_result = _ensure_app(
        client,
        name=args.app_name,
        description="Generated by copilot-agent-converter for Databricks App validation.",
    )
    _ensure_started(client, args.app_name)

    deployment = client.apps.deploy(
        app_name=args.app_name,
        app_deployment=AppDeployment(source_code_path=workspace_root),
    ).result(timeout=dt.timedelta(minutes=20))

    deployment_id = getattr(deployment, "deployment_id", None)
    health = _wait_for_health(
        client,
        name=args.app_name,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    logs = _get_logs(client, args.app_name, health.get("deploymentId") or deployment_id)

    result = {
        "app": app_result,
        "upload": upload_result,
        "deployRequest": {
            "deploymentId": deployment_id,
            "sourceCodePath": workspace_root,
        },
        "health": health,
        "logsExcerpt": logs.splitlines()[-20:] if logs else [],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
