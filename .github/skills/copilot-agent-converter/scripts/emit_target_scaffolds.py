#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[3]
DOCS_AGENTS_DIR = ROOT / "docs" / "agents"
CONTROL_SINGLETONS = {"current-run.json", "CANONICAL_ARTIFACT_POLICY.md"}
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from normalize_agent_profile import build_normalized_spec


def _json(data: Any) -> str:
    return json.dumps(data, indent=2) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _fallback_path(path: Path) -> Path:
    suffix = path.suffix
    stem = path.stem if suffix else path.name
    fallback_tag = ".generated" if not stem.endswith(".generated") else ".copy"
    return path.with_name(f"{stem}{fallback_tag}{suffix}")


def _write_with_fallback(path: Path, content: str) -> dict[str, Any]:
    try:
        _write(path, content)
        return {
            "requestedPath": path.as_posix(),
            "actualPath": path.as_posix(),
            "fallbackUsed": False,
            "warning": None,
        }
    except OSError as error:
        fallback_path = _fallback_path(path)
        _write(fallback_path, content)
        return {
            "requestedPath": path.as_posix(),
            "actualPath": fallback_path.as_posix(),
            "fallbackUsed": True,
            "warning": str(error),
        }


def _current_run_root() -> Path | None:
    current_run_path = DOCS_AGENTS_DIR / "current-run.json"
    if not current_run_path.exists():
        return None
    try:
        payload = json.loads(current_run_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    run_path = payload.get("currentRunPath")
    if not isinstance(run_path, str) or not run_path:
        return None
    return ROOT / run_path


def _is_root_docs_artifact(path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(DOCS_AGENTS_DIR.resolve())
    except ValueError:
        return False
    if not relative.parts:
        return False
    if relative.parts[0] == "runs":
        return False
    return path.name not in CONTROL_SINGLETONS


def write_docs_artifact(path: Path, content: str) -> dict[str, Any]:
    artifact = _write_with_fallback(path, content)
    run_snapshot = None
    actual_path = Path(artifact["actualPath"])
    if _is_root_docs_artifact(actual_path):
        run_root = _current_run_root()
        if run_root is not None:
            run_snapshot = _write_with_fallback(run_root / actual_path.name, content)
    artifact["runSnapshot"] = run_snapshot
    return artifact


def _package_root(output_root: Path, spec: dict[str, Any]) -> Path:
    return output_root / spec["identity"]["id"]


def _package_name(spec: dict[str, Any]) -> str:
    return f"copilot-agent-{spec['identity']['id']}"


def _app_name(spec: dict[str, Any]) -> str:
    candidate = f"{spec['identity']['id']}-app"
    return candidate[:30].rstrip("-")


def _manual_review_notes(spec: dict[str, Any]) -> list[str]:
    return list(spec["conversionReport"]["manualReviewReasons"])


def _http_mcp_servers(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    servers: dict[str, dict[str, Any]] = {}
    for entry in spec["integrations"]["mcpServers"]:
        if entry["transport"]["input"] != "http":
            continue
        original = entry["originalConfig"]
        url = original.get("url")
        if not url:
            continue
        server: dict[str, Any] = {"type": "http", "url": url}
        headers = original.get("headers")
        if isinstance(headers, dict) and headers:
            server["headers"] = {str(key): str(value) for key, value in headers.items()}
        servers[entry["name"]] = server
    return servers


def _render_gitignore() -> str:
    return "node_modules/\n.copilot-state/\n"


def _render_env_example(spec: dict[str, Any]) -> str:
    return textwrap.dedent(
        f"""\
        COPILOT_RUNTIME_MODE=mock
        PORT=8000
        COPILOT_MODEL=
        COPILOT_CLI_PATH=
        COPILOT_PROVIDER_TYPE=openai
        COPILOT_PROVIDER_BASE_URL=
        COPILOT_PROVIDER_API_KEY=
        COPILOT_PROVIDER_BEARER_TOKEN=
        COPILOT_PROVIDER_WIRE_API=completions
        COPILOT_PROVIDER_AZURE_API_VERSION=
        GENERATED_AGENT_ID={spec["identity"]["id"]}
        """
    )


def _render_package_json(spec: dict[str, Any]) -> str:
    package = {
        "name": _package_name(spec),
        "version": "0.1.0",
        "private": True,
        "type": "module",
        "description": spec["identity"]["description"] or "Generated Copilot agent runtime package.",
        "engines": {"node": ">=22"},
        "scripts": {
            "start": "node ./src/server.js",
            "smoke": "node ./scripts/local_smoke_test.mjs",
        },
        "dependencies": {
            "@github/copilot": "1.0.17",
            "@github/copilot-sdk": "0.2.0",
            "express": "5.2.1",
        },
    }
    return _json(package)


def _render_app_yaml() -> str:
    return textwrap.dedent(
        """\
        command:
          - "node"
          - "src/server.js"

        env:
          - name: NODE_ENV
            value: "production"
          - name: COPILOT_RUNTIME_MODE
            value: "mock"
        """
    )


def _render_readme(source_path: Path, spec: dict[str, Any], targets: list[str], report_location: str) -> str:
    report_line = report_location or "not requested"
    targets_text = ", ".join(targets)
    review_notes = _manual_review_notes(spec)
    review_block = "\n".join(f"- {note}" for note in review_notes) if review_notes else "- None"
    return textwrap.dedent(
        f"""\
        # {spec["identity"]["displayName"]} Package

        This package was generated from `{source_path.as_posix()}` by the repo-native
        `copilot-agent-converter` scaffold emitter.

        ## What it contains

        - A runnable Node service that exposes `GET /health`, `GET /agent`, and `POST /invoke`
        - A `package.json` with the Copilot SDK and Copilot CLI runtime dependencies
        - A Databricks `app.yaml` so the same service can be deployed as a Databricks App
        - A Python deployment helper that uploads the folder to a workspace and triggers an app deploy
        - A deterministic local smoke test script that starts the service in mock mode

        ## Targets emitted

        - {targets_text}

        ## Conversion inputs

        - Source agent: `{source_path.as_posix()}`
        - Normalized spec: `normalized-agent-spec.json`
        - Conversion report: `{report_line}`

        ## Local validation

        ```bash
        npm install
        npm run smoke
        ```

        The generated runtime defaults to `COPILOT_RUNTIME_MODE=mock` so the first validation pass is
        deterministic and does not require GitHub Copilot authentication.

        ## Databricks deployment

        ```bash
        py -3 -m pip install databricks-sdk
        py -3 scripts/deploy_databricks_app.py --profile dev
        ```

        Override `--app-name` if you want a different Databricks App name. The deployment helper uploads this
        folder to the workspace, creates the app if needed, and waits for the deployment to become healthy.

        ## Optional live Copilot mode

        Set `COPILOT_RUNTIME_MODE=copilot` and provide one of these runtime paths:

        - GitHub-authenticated Copilot CLI via the bundled `@github/copilot` package
        - A custom provider using `COPILOT_PROVIDER_BASE_URL`, `COPILOT_MODEL`, and auth variables

        ## Manual review notes

        {review_block}
        """
    )


def _render_config_js() -> str:
    return textwrap.dedent(
        """\
        import { readFile } from "node:fs/promises";
        import path from "node:path";
        import { fileURLToPath } from "node:url";

        const __filename = fileURLToPath(import.meta.url);
        const __dirname = path.dirname(__filename);
        const DEFAULT_SPEC_PATH = path.resolve(__dirname, "..", "normalized-agent-spec.json");

        export async function loadSpec() {
          const specPath = process.env.AGENT_SPEC_PATH || DEFAULT_SPEC_PATH;
          const raw = await readFile(specPath, "utf8");
          return JSON.parse(raw);
        }

        export function loadRuntimeConfig() {
          const runtimeMode = (process.env.COPILOT_RUNTIME_MODE || "mock").toLowerCase();
          return {
            runtimeMode,
            port: Number.parseInt(
              process.env.DATABRICKS_APP_PORT || process.env.PORT || "8000",
              10,
            ),
            copilot: {
              cliPath: process.env.COPILOT_CLI_PATH || undefined,
              model: process.env.COPILOT_MODEL || undefined,
              providerType: process.env.COPILOT_PROVIDER_TYPE || "openai",
              providerBaseUrl: process.env.COPILOT_PROVIDER_BASE_URL || undefined,
              providerApiKey: process.env.COPILOT_PROVIDER_API_KEY || undefined,
              providerBearerToken: process.env.COPILOT_PROVIDER_BEARER_TOKEN || undefined,
              providerWireApi: process.env.COPILOT_PROVIDER_WIRE_API || "completions",
              azureApiVersion: process.env.COPILOT_PROVIDER_AZURE_API_VERSION || undefined,
            },
          };
        }
        """
    )


def _render_mock_runtime_js() -> str:
    return textwrap.dedent(
        """\
        function extractFileHints(systemPrompt) {
          const matches = [...systemPrompt.matchAll(/`([^`]+)`/g)];
          return [...new Set(matches.map((match) => match[1]).filter(Boolean))].slice(0, 4);
        }

        export async function invokeMock(spec, prompt) {
          const hints = extractFileHints(spec.behavior.systemPrompt);
          const guidance = hints.length > 0 ? hints.join(", ") : "AGENTS.md";
          const message = [
            `Hello from ${spec.identity.displayName}.`,
            spec.identity.description || "This is a generated mock runtime for validation.",
            "This response came from the deterministic mock mode of the generated service.",
            `Suggested next docs: ${guidance}.`,
            `Prompt received: ${String(prompt || "").trim() || "(empty prompt)"}`,
          ].join(" ");

          return {
            runtime: {
              mode: "mock",
              usedTools: spec.capabilities.rawTools,
            },
            message,
          };
        }
        """
    )


def _render_copilot_runtime_js(spec: dict[str, Any]) -> str:
    custom_agent = {
        "name": spec["identity"]["id"],
        "displayName": spec["identity"]["displayName"],
        "description": spec["identity"]["description"],
        "tools": spec["capabilities"]["rawTools"],
        "prompt": spec["behavior"]["systemPrompt"],
        "infer": True,
    }
    mcp_servers = _http_mcp_servers(spec)
    return textwrap.dedent(
        f"""\
        import {{ CopilotClient, approveAll }} from "@github/copilot-sdk";

        const CUSTOM_AGENT = {json.dumps(custom_agent, indent=2)};
        const CUSTOM_MCP_SERVERS = {json.dumps(mcp_servers, indent=2)};

        function buildProviderConfig(config) {{
          if (!config.providerBaseUrl) {{
            return undefined;
          }}

          const provider = {{
            type: config.providerType || "openai",
            baseUrl: config.providerBaseUrl,
            wireApi: config.providerWireApi || "completions",
          }};

          if (config.providerBearerToken) {{
            provider.bearerToken = config.providerBearerToken;
          }} else if (config.providerApiKey) {{
            provider.apiKey = config.providerApiKey;
          }}

          if (provider.type === "azure" && config.azureApiVersion) {{
            provider.azure = {{ apiVersion: config.azureApiVersion }};
          }}

          return provider;
        }}

        async function ensureAuthIfNeeded(client, config) {{
          if (config.providerBaseUrl) {{
            if (!config.model) {{
              throw new Error("COPILOT_MODEL is required when using a custom provider.");
            }}
            return;
          }}

          const auth = await client.getAuthStatus();
          if (!auth.isAuthenticated) {{
            throw new Error(
              auth.statusMessage || "GitHub Copilot CLI authentication is required for live mode.",
            );
          }}
        }}

        export async function invokeWithCopilot(spec, config, prompt) {{
          const client = new CopilotClient({{
            ...(config.cliPath ? {{ cliPath: config.cliPath }} : {{}}),
          }});

          try {{
            await ensureAuthIfNeeded(client, config);
            const providerConfig = buildProviderConfig(config);
            const session = await client.createSession({{
              clientName: "copilot-agent-converter-generated-service",
              onPermissionRequest: approveAll,
              ...(config.model ? {{ model: config.model }} : {{}}),
              ...(providerConfig ? {{ provider: providerConfig }} : {{}}),
              customAgents: [
                {{
                  ...CUSTOM_AGENT,
                  ...(Object.keys(CUSTOM_MCP_SERVERS).length > 0
                    ? {{ mcpServers: CUSTOM_MCP_SERVERS }}
                    : {{}}),
                }},
              ],
              agent: CUSTOM_AGENT.name,
              availableTools: [],
            }});

            try {{
              const response = await session.sendAndWait({{ prompt }});
              return {{
                runtime: {{
                  mode: "copilot",
                  model: config.model || null,
                  providerBaseUrl: config.providerBaseUrl || null,
                }},
                message: response?.data?.content || "Copilot session returned no content.",
              }};
            }} finally {{
              await session.disconnect();
            }}
          }} finally {{
            await client.stop();
          }}
        }}
        """
    )


def _render_server_js() -> str:
    return textwrap.dedent(
        """\
        import express from "express";
        import { loadRuntimeConfig, loadSpec } from "./config.js";
        import { invokeWithCopilot } from "./copilot-runtime.js";
        import { invokeMock } from "./mock-runtime.js";

        const app = express();
        app.use(express.json({ limit: "1mb" }));

        const spec = await loadSpec();
        const config = loadRuntimeConfig();

        async function runAgent(prompt) {
          if (config.runtimeMode === "copilot") {
            return invokeWithCopilot(spec, config.copilot, prompt);
          }
          return invokeMock(spec, prompt);
        }

        app.get("/", async (_req, res) => {
          res.json({
            name: spec.identity.displayName,
            id: spec.identity.id,
            runtimeMode: config.runtimeMode,
            endpoints: ["/health", "/agent", "/invoke"],
          });
        });

        app.get("/health", async (_req, res) => {
          res.json({
            status: "ok",
            runtimeMode: config.runtimeMode,
            agent: {
              id: spec.identity.id,
              displayName: spec.identity.displayName,
            },
            determinism: spec.conversionReport.determinism,
            manualReviewReasons: spec.conversionReport.manualReviewReasons,
          });
        });

        app.get("/agent", async (_req, res) => {
          res.json({
            source: spec.source,
            identity: spec.identity,
            behavior: {
              visibility: spec.behavior.visibility,
            },
            packagingHints: spec.packagingHints,
          });
        });

        app.post("/invoke", async (req, res) => {
          try {
            const prompt = typeof req.body?.prompt === "string" ? req.body.prompt : "";
            const result = await runAgent(prompt);
            res.json({
              agent: {
                id: spec.identity.id,
                displayName: spec.identity.displayName,
              },
              ...result,
            });
          } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            res.status(500).json({
              error: message,
              runtimeMode: config.runtimeMode,
              agentId: spec.identity.id,
            });
          }
        });

        app.listen(config.port, "0.0.0.0", () => {
          console.log(`Generated agent service listening on port ${config.port}`);
        });
        """
    )


def _render_smoke_test_js() -> str:
    return textwrap.dedent(
        """\
        import assert from "node:assert/strict";
        import { spawn } from "node:child_process";
        import process from "node:process";
        import { setTimeout as sleep } from "node:timers/promises";

        const port = 8123;
        const baseUrl = `http://127.0.0.1:${port}`;
        const child = spawn(process.execPath, ["src/server.js"], {
          env: {
            ...process.env,
            PORT: String(port),
            COPILOT_RUNTIME_MODE: "mock",
          },
          stdio: ["ignore", "pipe", "pipe"],
        });

        let output = "";
        child.stdout.on("data", (chunk) => {
          output += chunk.toString();
        });
        child.stderr.on("data", (chunk) => {
          output += chunk.toString();
        });

        async function waitForHealth() {
          for (let attempt = 0; attempt < 40; attempt += 1) {
            try {
              const response = await fetch(`${baseUrl}/health`);
              if (response.ok) {
                return response.json();
              }
            } catch (_error) {
              // service not ready yet
            }
            await sleep(250);
          }
          throw new Error(`Service did not become healthy. Output: ${output}`);
        }

        try {
          const health = await waitForHealth();
          assert.equal(health.status, "ok");
          assert.equal(health.runtimeMode, "mock");

          const response = await fetch(`${baseUrl}/invoke`, {
            method: "POST",
            headers: {
              "content-type": "application/json",
            },
            body: JSON.stringify({
              prompt: "Say hello and point me to the repo workflow docs.",
            }),
          });
          assert.equal(response.status, 200);

          const payload = await response.json();
          assert.equal(payload.runtime.mode, "mock");
          assert.match(payload.message, /Hello from/i);

          console.log(JSON.stringify({ health, invoke: payload }, null, 2));
        } finally {
          child.kill("SIGTERM");
        }
        """
    )


def _render_deploy_script(spec: dict[str, Any]) -> str:
    return textwrap.dedent(
        f"""\
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


        APP_NAME_DEFAULT = "{_app_name(spec)}"
        SUCCESS_STATES = {{"ACTIVE", "READY", "RUNNING", "SUCCEEDED", "HEALTHY"}}
        FAILURE_STATES = {{"FAILED", "ERROR", "CANCELED", "CANCELLED"}}
        EXCLUDED_DIRS = {{"node_modules", ".git", ".copilot-state", "__pycache__"}}


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
                return f"/Workspace/Users/{{user_name}}/generated/copilot-agent-packages/{{package_slug}}"
            return f"/Workspace/Shared/generated/copilot-agent-packages/{{package_slug}}"


        def _upload_folder(client: WorkspaceClient, local_root: Path, workspace_root: str) -> dict:
            client.workspace.mkdirs(workspace_root)
            uploaded = []
            for file_path in _iter_files(local_root):
                relative = file_path.relative_to(local_root).as_posix()
                remote_path = f"{{workspace_root}}/{{relative}}"
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
            return {{
                "localRoot": local_root.as_posix(),
                "workspaceRoot": workspace_root,
                "uploadedFiles": uploaded,
            }}


        def _ensure_app(client: WorkspaceClient, name: str, description: str) -> dict:
            try:
                app = client.apps.get(name=name)
                created = False
            except Exception:
                app = client.apps.create(app=App(name=name, description=description)).response
                created = True
            return {{
                "created": created,
                "name": getattr(app, "name", name),
                "url": getattr(app, "url", None),
            }}


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
                    f"/api/2.0/apps/{{app_name}}/deployments/{{deployment_id}}/logs",
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
                        f"Deployment failed with app_state={{app_state}} deployment_state={{deployment_state}}"
                    )
                if app_state in SUCCESS_STATES and (
                    not deployment_state or deployment_state in SUCCESS_STATES
                ):
                    deployment_id = getattr(active, "deployment_id", None)
                    return {{
                        "appState": app_state,
                        "deploymentState": deployment_state,
                        "deploymentId": deployment_id,
                        "url": getattr(app, "url", None),
                    }}
                time.sleep(poll_seconds)
            raise TimeoutError(f"App '{{name}}' did not become healthy within {{timeout_seconds}}s")


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

            result = {{
                "app": app_result,
                "upload": upload_result,
                "deployRequest": {{
                    "deploymentId": deployment_id,
                    "sourceCodePath": workspace_root,
                }},
                "health": health,
                "logsExcerpt": logs.splitlines()[-20:] if logs else [],
            }}
            print(json.dumps(result, indent=2))
            return 0


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    )


def _render_report(
    source_path: Path,
    normalized_spec_path: Path,
    package_root: Path,
    targets: list[str],
    generated_files: list[str],
    spec: dict[str, Any],
    status: str,
) -> str:
    packaging_targets = []
    for target in targets:
        notes: list[str] = []
        if target == "databricks-app":
            notes.append("Generated package includes app.yaml and a Python SDK deployment helper.")
        if target == "copilot-sdk-service":
            notes.append("Generated package defaults to mock mode and can be upgraded to live Copilot mode.")
        if _manual_review_notes(spec):
            notes.extend(_manual_review_notes(spec))
        packaging_targets.append(
            {
                "target": target,
                "status": "ready" if not _manual_review_notes(spec) else "manual_review",
                "artifacts": generated_files,
                "notes": notes,
            }
        )

    report = {
        "type": "CopilotAgentConversionReport",
        "status": status,
        "mode": "conversion",
        "goal": "Convert a real example Copilot custom agent into runnable Copilot SDK and Databricks App scaffolds.",
        "sourceAgent": {
            "path": source_path.as_posix(),
            "name": spec["identity"]["name"],
            "targets": spec["source"]["sourceTargets"],
            "parseStatus": "pass",
        },
        "normalizedSpec": {
            "path": normalized_spec_path.as_posix(),
            "determinism": spec["conversionReport"]["determinism"],
            "manualReviewReasons": spec["conversionReport"]["manualReviewReasons"],
            "lossyTransforms": spec["conversionReport"]["lossyTransforms"],
        },
        "packagingTargets": packaging_targets,
        "generatedFiles": generated_files,
        "validation": [
            {
                "check": "spec-parse",
                "result": "pass",
                "evidence": normalized_spec_path.as_posix(),
            },
            {
                "check": "scaffold-emission",
                "result": "pass",
                "evidence": package_root.as_posix(),
            },
        ],
        "blockers": [],
        "notesToTeamLead": [
            "The generated runtime defaults to mock mode so the first Databricks deployment is deterministic.",
            "Switch to live Copilot mode only after configuring GitHub Copilot CLI auth or a provider-backed model endpoint.",
        ],
    }

    summary = [
        "# Copilot Agent Conversion Report",
        "",
        "## Summary (<=12 lines)",
        f"- Status: {status}",
        "- Mode: conversion",
        "- Goal: Operationalize the first real Copilot-agent conversion with runnable scaffolds.",
        f"- Source agent: {source_path.as_posix()}",
        f"- Determinism: {spec['conversionReport']['determinism']}",
        f"- Targets: {', '.join(targets)}",
        f"- Generated package: {package_root.as_posix()}",
        "- Notes: The emitted service defaults to deterministic mock mode and includes a Databricks deployment helper.",
        "",
        "```json",
        json.dumps(report, indent=2),
        "```",
        "",
    ]
    return "\n".join(summary)


def emit_package(
    source_path: Path,
    output_root: Path,
    targets: list[str],
    report_path: Path | None,
    status: str,
) -> dict[str, Any]:
    spec = build_normalized_spec(source_path)
    package_root = _package_root(output_root, spec)
    package_root.mkdir(parents=True, exist_ok=True)

    normalized_spec_path = package_root / "normalized-agent-spec.json"
    _write(normalized_spec_path, _json(spec))

    files_to_render = {
        package_root / ".gitignore": _render_gitignore(),
        package_root / ".env.example": _render_env_example(spec),
        package_root / "package.json": _render_package_json(spec),
        package_root / "app.yaml": _render_app_yaml(),
        package_root / "src" / "config.js": _render_config_js(),
        package_root / "src" / "mock-runtime.js": _render_mock_runtime_js(),
        package_root / "src" / "copilot-runtime.js": _render_copilot_runtime_js(spec),
        package_root / "src" / "server.js": _render_server_js(),
        package_root / "scripts" / "local_smoke_test.mjs": _render_smoke_test_js(),
        package_root / "scripts" / "deploy_databricks_app.py": _render_deploy_script(spec),
    }

    for path, content in files_to_render.items():
        _write(path, content)

    readme_path = package_root / "README.md"
    generated_files = [path.relative_to(package_root).as_posix() for path in files_to_render]
    generated_files.append(readme_path.relative_to(package_root).as_posix())
    generated_files.insert(0, normalized_spec_path.relative_to(package_root).as_posix())
    absolute_generated_files = [(package_root / entry).as_posix() for entry in generated_files]

    report_result = None
    if report_path:
        report_content = _render_report(
            source_path=source_path,
            normalized_spec_path=normalized_spec_path,
            package_root=package_root,
            targets=targets,
            generated_files=absolute_generated_files,
            spec=spec,
            status=status,
        )
        report_result = write_docs_artifact(report_path, report_content)

    report_location = report_result["actualPath"] if report_result else "not requested"
    _write(readme_path, _render_readme(source_path, spec, targets, report_location))

    return {
        "sourceAgent": source_path.as_posix(),
        "packageRoot": package_root.as_posix(),
        "targets": targets,
        "normalizedSpec": normalized_spec_path.as_posix(),
        "generatedFiles": absolute_generated_files,
        "determinism": spec["conversionReport"]["determinism"],
        "manualReviewReasons": spec["conversionReport"]["manualReviewReasons"],
        "appName": _app_name(spec),
        "report": report_result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit runnable target scaffolds for a normalized Copilot custom agent profile."
    )
    parser.add_argument("--input", required=True, help="Path to the source .agent.md file.")
    parser.add_argument(
        "--output-root",
        default="generated/copilot-agent-packages",
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
        help="Optional path to write docs/agents/copilot-agent-conversion-report.md.",
    )
    parser.add_argument(
        "--status",
        default="READY_FOR_TEST_ENGINEER",
        help="Status string to write into the optional conversion report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path = Path(args.input).resolve()
    output_root = Path(args.output_root).resolve()
    targets = args.targets or ["copilot-sdk-service", "databricks-app"]
    report_path = Path(args.report).resolve() if args.report else None

    result = emit_package(
        source_path=source_path,
        output_root=output_root,
        targets=targets,
        report_path=report_path,
        status=args.status,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
