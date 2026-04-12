#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"\A---\n(?P<front>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)
DEFAULT_SOURCE_TARGETS = ["vscode", "github-copilot"]
TOOL_CATEGORY_MAP = {
    "read": "read",
    "search": "search",
    "edit": "write",
    "write": "write",
    "execute": "shell",
    "shell": "shell",
    "web": "web",
    "agent": "agent",
}


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    if value.startswith(("[", "{", "(", '"', "'")):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return _strip_quotes(value)
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return _strip_quotes(value)


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_block(lines: list[str], start: int, indent: int) -> tuple[Any, int]:
    first_index = start
    while first_index < len(lines) and not lines[first_index].strip():
        first_index += 1
    if first_index >= len(lines):
        return {}, first_index

    current = lines[first_index]
    current_indent = _indent_of(current)
    if current_indent < indent:
        return {}, first_index
    if current[current_indent:].startswith("- "):
        return _parse_list(lines, first_index, current_indent)
    return _parse_dict(lines, first_index, current_indent)


def _parse_dict(lines: list[str], start: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        current_indent = _indent_of(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            break
        stripped = line[indent:]
        if ":" not in stripped:
            break
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value in (">", "|"):
            block_lines: list[str] = []
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if not next_line.strip():
                    block_lines.append("")
                    index += 1
                    continue
                next_indent = _indent_of(next_line)
                if next_indent <= indent:
                    break
                block_lines.append(next_line[indent + 2 :])
                index += 1
            if raw_value == "|":
                value = "\n".join(block_lines).strip()
            else:
                value = " ".join(part.strip() for part in block_lines if part.strip())
            result[key] = value
            continue
        if raw_value == "":
            index += 1
            value, index = _parse_block(lines, index, indent + 2)
            result[key] = value
            continue
        result[key] = _parse_scalar(raw_value)
        index += 1
    return result, index


def _parse_list(lines: list[str], start: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        current_indent = _indent_of(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            break
        stripped = line[indent:]
        if not stripped.startswith("- "):
            break
        item_content = stripped[2:].strip()
        index += 1
        if not item_content:
            nested, index = _parse_block(lines, index, indent + 2)
            result.append(nested)
            continue
        if ":" in item_content and not item_content.startswith(("[", "{", '"', "'")):
            key, raw_value = item_content.split(":", 1)
            item: dict[str, Any] = {key.strip(): _parse_scalar(raw_value.strip())}
            nested, next_index = _parse_block(lines, index, indent + 2)
            if isinstance(nested, dict):
                item.update(nested)
                index = next_index
            result.append(item)
            continue
        result.append(_parse_scalar(item_content))
    return result, index


def parse_frontmatter(frontmatter: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        lines = frontmatter.splitlines()
        data, _ = _parse_block(lines, 0, 0)
        if isinstance(data, dict):
            return data
        return {}
    parsed = yaml.safe_load(frontmatter) or {}
    if isinstance(parsed, dict):
        return parsed
    raise ValueError("Frontmatter must parse to a mapping.")


def load_agent_profile(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError(f"{path.as_posix()} does not contain a valid YAML frontmatter block.")
    frontmatter = parse_frontmatter(match.group("front"))
    body = match.group("body").strip()
    return frontmatter, body


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _target_list(frontmatter: dict[str, Any]) -> list[str]:
    raw_target = frontmatter.get("target")
    if raw_target in (None, ""):
        return list(DEFAULT_SOURCE_TARGETS)
    values = [str(value) for value in _as_list(raw_target)]
    return values or list(DEFAULT_SOURCE_TARGETS)


def _tool_policy(raw_tools: list[str], tools_present: bool) -> tuple[str, list[str]]:
    if not tools_present:
        return "all", ["*"]
    if not raw_tools:
        return "none", []
    if raw_tools == ["*"]:
        return "all", raw_tools
    return "allowlist", raw_tools


def _canonicalize_tools(raw_tools: list[str]) -> tuple[dict[str, list[Any]], list[str]]:
    canonical: dict[str, list[Any]] = {
        "read": [],
        "write": [],
        "shell": [],
        "search": [],
        "web": [],
        "agent": [],
        "mcp": [],
    }
    unresolved: list[str] = []
    for tool in raw_tools:
        category = TOOL_CATEGORY_MAP.get(tool)
        if category:
            canonical[category].append(tool)
            continue
        if "/" in tool and tool != "*":
            server, pattern = tool.split("/", 1)
            canonical["mcp"].append({"server": server, "toolPattern": pattern or "*"})
            continue
        if tool != "*":
            unresolved.append(tool)
    return canonical, unresolved


def _normalize_mcp_servers(frontmatter: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    raw_servers = frontmatter.get("mcpServers")
    if raw_servers is None:
        raw_servers = frontmatter.get("mcp-servers")
    normalized: list[dict[str, Any]] = []
    warnings: list[str] = []
    review_reasons: list[str] = []
    for entry in _as_list(raw_servers):
        if isinstance(entry, str):
            normalized.append(
                {
                    "name": entry,
                    "source": "reference",
                    "originalConfig": {"name": entry},
                    "transport": {"input": "unknown", "servingTargetRequired": "manual-review"},
                    "auth": {"mode": "unknown", "secretRefs": []},
                    "exposure": {"toolScope": "unknown", "allowedTools": []},
                }
            )
            warnings.append(f"MCP server '{entry}' does not declare transport details.")
            continue
        if not isinstance(entry, dict):
            warnings.append("Encountered an MCP server entry that is not a string or mapping.")
            continue
        name = str(entry.get("name") or entry.get("id") or "unnamed-mcp-server")
        if "url" in entry:
            transport_input = "http"
            serving_target = "direct"
        elif "command" in entry or "args" in entry:
            transport_input = "stdio"
            serving_target = "http-bridge"
            review_reasons.append(
                f"MCP server '{name}' uses stdio transport and needs an HTTP bridge for remote serving."
            )
        else:
            transport_input = "unknown"
            serving_target = "manual-review"
            warnings.append(f"MCP server '{name}' has no detectable transport.")
        normalized.append(
            {
                "name": name,
                "source": "inline",
                "originalConfig": entry,
                "transport": {
                    "input": transport_input,
                    "servingTargetRequired": serving_target,
                },
                "auth": {
                    "mode": "secret-ref" if any("secret" in str(key).lower() for key in entry) else "unknown",
                    "secretRefs": [],
                },
                "exposure": {
                    "toolScope": "subset",
                    "allowedTools": [],
                },
            }
        )
    return normalized, warnings, review_reasons


def _mutation_level(canonical_tools: dict[str, list[Any]]) -> str:
    if canonical_tools["shell"]:
        return "shell"
    if canonical_tools["write"]:
        return "write"
    return "read-only"


def _preferred_model(frontmatter: dict[str, Any]) -> list[str]:
    for key in ("model", "model-preference", "modelPreference"):
        value = frontmatter.get(key)
        if value:
            return [str(item) for item in _as_list(value)]
    return []


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "copilot-agent"


def build_normalized_spec(source_path: Path) -> dict[str, Any]:
    frontmatter, body = load_agent_profile(source_path)
    name = str(frontmatter.get("name") or source_path.stem.replace(".agent", ""))
    display_name = str(frontmatter.get("display-name") or name)
    description = str(frontmatter.get("description") or "")
    raw_tools_value = _as_list(frontmatter.get("tools"))
    raw_tools = [str(tool) for tool in raw_tools_value]
    session_tool_policy, raw_tools = _tool_policy(raw_tools, "tools" in frontmatter)
    canonical_tools, unresolved_tools = _canonicalize_tools(raw_tools)
    mcp_servers, parser_warnings, mcp_review_reasons = _normalize_mcp_servers(frontmatter)
    subagents = _as_list(frontmatter.get("agents") or frontmatter.get("subagents"))
    handoffs = _as_list(frontmatter.get("handoffs"))
    hooks = _as_list(frontmatter.get("hooks"))

    manual_review_reasons = list(mcp_review_reasons)
    lossy_transforms: list[str] = []
    if hooks:
        manual_review_reasons.append(
            "VS Code hook configuration is editor-specific and needs manual translation."
        )
    if unresolved_tools:
        manual_review_reasons.append(
            "Some source tools could not be normalized automatically."
        )
    if handoffs:
        lossy_transforms.append("Handoffs are preserved as app-layer metadata, not a deployable runtime primitive.")
    if subagents and "agent" not in raw_tools:
        manual_review_reasons.append(
            "Subagents are declared without the agent tool; review runtime routing expectations."
        )

    determinism_score = 0
    determinism_score += len(unresolved_tools)
    determinism_score += len(hooks) * 2
    determinism_score += len(mcp_review_reasons)
    determinism_score += 1 if handoffs else 0
    if determinism_score == 0:
        determinism = "high"
    elif determinism_score <= 2:
        determinism = "medium"
    else:
        determinism = "low"

    return {
        "specVersion": "0.1",
        "source": {
            "kind": "github-copilot-agent-profile",
            "filePath": source_path.as_posix(),
            "sourceFormat": "agent-md",
            "sourceTargets": _target_list(frontmatter),
            "parserWarnings": parser_warnings,
            "rawFrontmatter": frontmatter,
        },
        "identity": {
            "id": _slugify(name),
            "name": name,
            "displayName": display_name,
            "description": description,
        },
        "behavior": {
            "systemPrompt": body,
            "modelPreferences": {
                "preferred": _preferred_model(frontmatter),
                "fallback": [],
            },
            "visibility": {
                "pickerVisible": bool(frontmatter.get("user-invocable", True)),
                "allowSubagentInvocation": bool(subagents) or "agent" in raw_tools,
            },
            "routing": {
                "subagents": {
                    "allowed": [str(value) for value in subagents],
                },
                "handoffs": handoffs,
            },
        },
        "capabilities": {
            "sessionToolPolicy": session_tool_policy,
            "rawTools": raw_tools,
            "canonicalTools": canonical_tools,
            "unresolvedTools": unresolved_tools,
            "hooks": {
                "vscodeOnly": hooks,
                "unsupported": [],
            },
        },
        "integrations": {
            "mcpServers": mcp_servers,
        },
        "runtimeRequirements": {
            "workspace": {
                "requiresRepoContext": True,
                "requiresFilesystem": True,
            },
            "execution": {
                "mutationLevel": _mutation_level(canonical_tools),
                "needsInteractiveAuth": False,
                "needsBackgroundProcess": False,
                "networkAccess": "optional",
            },
        },
        "packagingHints": {
            "preferredTargets": ["copilot-sdk-service", "databricks-app"],
            "serviceSurfaces": {
                "restApi": True,
                "mcp": True,
            },
            "authProfile": {
                "interactiveUser": "oauth",
                "serviceToService": "token-or-oauth",
            },
            "publicExposure": {
                "anonymousAllowed": False,
            },
        },
        "conversionReport": {
            "determinism": determinism,
            "lossyTransforms": lossy_transforms,
            "manualReviewReasons": manual_review_reasons,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize a GitHub Copilot custom agent profile into a machine-readable spec."
    )
    parser.add_argument("--input", required=True, help="Path to the source .agent.md file.")
    parser.add_argument(
        "--output",
        help="Optional output path. When omitted, JSON is written to stdout.",
    )
    args = parser.parse_args()

    source_path = Path(args.input).resolve()
    spec = build_normalized_spec(source_path)
    rendered = json.dumps(spec, indent=2) + "\n"

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
