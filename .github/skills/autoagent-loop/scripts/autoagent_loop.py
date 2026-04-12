#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[4]
DOCS_AGENTS_DIR = ROOT / "docs" / "agents"
CONTROL_SINGLETONS = {"current-run.json", "CANONICAL_ARTIFACT_POLICY.md"}
FRONTMATTER_RE = re.compile(r"\A---\n(?P<front>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)
JSON_BLOCK_RE = re.compile(r"```json\s*(?P<payload>\{.*?\})\s*```", re.DOTALL)
WINDOWS_ABSOLUTE_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"']+")
POSIX_ABSOLUTE_PATH_RE = re.compile(r"(?<!<repo>)(?<![A-Za-z0-9_.:-])/(?:[^\s\"']+)")
DEFAULT_DEBUG_LOG_INCLUDE_PATTERNS = [
    r"\berror\b",
    r"\bwarn(?:ing)?\b",
    r"\bfail(?:ed|ure)?\b",
    r"\bdeny(?:ing|ied)?\b",
    r"\bbenchmark\b",
    r"\bcandidate\b",
    r"\breview\b",
    r"\bpatch\b",
    r"\btool\b",
    r"\bautoagent\b",
]
LOG_ERROR_RE = re.compile(
    r"\berror\b|\bexception\b|\btraceback\b|\bfail(?:ed|ure)?\b|\bfatal\b", re.IGNORECASE
)
LOG_WARNING_RE = re.compile(
    r"\bwarn(?:ing)?\b|\bdeny(?:ing|ied)?\b|\bblock(?:ed|ing)?\b", re.IGNORECASE
)
LOG_SUCCESS_RE = re.compile(r"\bsuccess\b|\bpassed\b|\bready\b|\bonline\b", re.IGNORECASE)
SUPPORTED_LIVE_EVALUATOR_PROVIDERS = {"github-models"}
SUPPORTED_LIVE_EVALUATOR_STRATEGIES = {"advisory", "tie_breaker"}
SUPPORTED_CANDIDATE_KEEP_STRATEGIES = {"score-then-simpler"}
SUPPORTED_CANDIDATE_SEARCH_STRATEGIES = {"current_best", "frontier"}
SUPPORTED_BENCHMARK_CHECK_TYPES = {
    "contains_text",
    "episode_observation_guard",
    "frontmatter_equals",
    "frontmatter_includes",
    "max_body_chars",
}
SUPPORTED_LEARNING_REVIEW_DECISIONS = {"accept", "reject", "defer"}
MAX_RECORDED_LIVE_EVALUATOR_OUTPUT_CHARS = 1200
GUARDED_AUTO_PROMOTION_REVIEWER = "autoagent-guarded-promotion"
GUARDED_AUTO_PROMOTION_MIN_POLICY_LEARNING_SCORE = 0.7
DEFAULT_REVIEWED_POLICY_PREFERRED_SEQUENCE_BONUS = 0.04
DEFAULT_REVIEWED_POLICY_ESCALATION_PENALTY = 0.05
REASONING_PATH_EFFICIENCY_SIGNAL_NAME = "reasoningPathEfficiencyScore"


def _github_models_live_evaluator_runner(
    config: dict[str, Any],
    samples: list[dict[str, Any]],
    experiment: dict[str, Any],
) -> dict[str, Any]:
    raise RuntimeError("No github-models live evaluator runner is configured for this environment.")


LIVE_EVALUATOR_RUNNERS: dict[
    str,
    Callable[[dict[str, Any], list[dict[str, Any]], dict[str, Any]], Any],
] = {"github-models": _github_models_live_evaluator_runner}


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
    if _is_root_docs_artifact(actual_path) and actual_path.name != "current-run.json":
        run_root = _current_run_root()
        if run_root is not None:
            run_snapshot = _write_with_fallback(run_root / actual_path.name, content)
    artifact["runSnapshot"] = run_snapshot
    return artifact


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


def load_markdown_document(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError(f"{path.as_posix()} does not contain a valid YAML frontmatter block.")
    frontmatter = parse_frontmatter(match.group("front"))
    body = match.group("body").strip()
    return frontmatter, body


def _dump_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if "\n" in value:
            return "|"
        if re.fullmatch(r"[A-Za-z0-9_./:-]+", value):
            return value
        return json.dumps(value)
    return json.dumps(value)


def _dump_mapping(data: dict[str, Any], indent: int = 0) -> list[str]:
    lines: list[str] = []
    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.extend(_dump_mapping(value, indent + 2))
        elif isinstance(value, list):
            if not value:
                lines.append(f"{prefix}{key}: []")
            else:
                lines.append(f"{prefix}{key}:")
                lines.extend(_dump_list(value, indent + 2))
        else:
            dumped = _dump_scalar(value)
            if dumped == "|":
                lines.append(f"{prefix}{key}: |")
                for line in str(value).splitlines():
                    lines.append(f"{prefix}  {line}")
            else:
                lines.append(f"{prefix}{key}: {dumped}")
    return lines


def _dump_list(items: list[Any], indent: int = 0) -> list[str]:
    lines: list[str] = []
    prefix = " " * indent
    for item in items:
        if isinstance(item, dict):
            nested = _dump_mapping(item, indent + 2)
            if nested:
                first = nested[0].lstrip()
                lines.append(f"{prefix}- {first}")
                lines.extend(nested[1:])
            else:
                lines.append(f"{prefix}- {{}}")
        elif isinstance(item, list):
            if not item:
                lines.append(f"{prefix}- []")
            else:
                lines.append(f"{prefix}-")
                lines.extend(_dump_list(item, indent + 2))
        else:
            dumped = _dump_scalar(item)
            lines.append(f"{prefix}- {dumped}")
    return lines


def render_markdown_document(frontmatter: dict[str, Any], body: str) -> str:
    lines = ["---"]
    lines.extend(_dump_mapping(frontmatter))
    lines.append("---")
    lines.append("")
    lines.append(body.rstrip())
    lines.append("")
    return "\n".join(lines)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _resolve_path(base_dir: Path, candidate: str | None) -> Path | None:
    if not candidate:
        return None
    path = Path(candidate)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _normalized_id(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return normalized or "item"


def _normalized_strings(values: Any) -> list[str]:
    normalized: list[str] = []
    for value in _as_list(values):
        text = str(value).strip()
        if text:
            normalized.append(text)
    return normalized


def _optional_str(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip()
    return text or None


def _coerce_int(value: Any, default: int) -> int:
    if value is None or isinstance(value, bool):
        return default
    return int(value)


def _coerce_float(value: Any, default: float) -> float:
    if value is None or isinstance(value, bool):
        return default
    return float(value)


def _sha256_for_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _path_provenance(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    exists = path.exists()
    return {
        "path": path.as_posix(),
        "exists": exists,
        "sha256": _sha256_for_path(path) if exists else None,
        "sizeBytes": path.stat().st_size if exists and path.is_file() else None,
    }


def _default_live_evaluator() -> dict[str, Any]:
    return {
        "enabled": False,
        "strategy": "disabled",
        "provider": None,
        "model": None,
        "promptArtifactPath": None,
        "rubricPaths": [],
        "maxSamples": 0,
        "recordRawOutputs": False,
        "requireDeterministicPass": True,
        "temperature": 0.0,
    }


def _resolve_live_evaluator(
    base_dir: Path,
    frontmatter: dict[str, Any],
    evaluation_mode: dict[str, Any],
) -> dict[str, Any]:
    defaults = _default_live_evaluator()
    raw_live = evaluation_mode.get("liveEvaluator") or frontmatter.get("liveEvaluator") or {}
    if isinstance(raw_live, bool):
        raw_live = {"enabled": raw_live}
    if not isinstance(raw_live, dict):
        raw_live = {}

    prompt_path = _resolve_path(base_dir, _optional_str(raw_live.get("promptArtifactPath")))
    rubric_paths = [
        resolved
        for resolved in (
            _resolve_path(base_dir, value)
            for value in _normalized_strings(raw_live.get("rubricPaths"))
        )
        if resolved is not None
    ]
    enabled = bool(raw_live.get("enabled", evaluation_mode.get("live", defaults["enabled"])))
    strategy = str(raw_live.get("strategy") or ("advisory" if enabled else defaults["strategy"]))
    default_max_samples = 1 if enabled else defaults["maxSamples"]

    return {
        "enabled": enabled,
        "strategy": strategy,
        "provider": raw_live.get("provider") or defaults["provider"],
        "model": raw_live.get("model") or defaults["model"],
        "promptArtifactPath": prompt_path,
        "rubricPaths": rubric_paths,
        "maxSamples": _coerce_int(raw_live.get("maxSamples"), default_max_samples),
        "recordRawOutputs": bool(raw_live.get("recordRawOutputs", defaults["recordRawOutputs"])),
        "requireDeterministicPass": bool(
            raw_live.get(
                "requireDeterministicPass",
                defaults["requireDeterministicPass"],
            )
        ),
        "temperature": _coerce_float(
            raw_live.get("temperature"),
            defaults["temperature"],
        ),
    }


def _resolve_evaluation_mode(base_dir: Path, frontmatter: dict[str, Any]) -> dict[str, Any]:
    raw_mode = frontmatter.get("evaluationMode") or {}
    if not isinstance(raw_mode, dict):
        raw_mode = {}
    deterministic = bool(raw_mode.get("deterministic", True))
    live_evaluator = _resolve_live_evaluator(base_dir, frontmatter, raw_mode)
    return {
        "deterministic": deterministic,
        "live": bool(raw_mode.get("live", live_evaluator["enabled"])),
        "liveEvaluator": live_evaluator,
    }


def _serialize_live_evaluator(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "enabled": config["enabled"],
        "strategy": config["strategy"],
        "provider": config["provider"],
        "model": config["model"],
        "promptArtifactPath": (
            config["promptArtifactPath"].as_posix()
            if config["promptArtifactPath"] is not None
            else None
        ),
        "rubricPaths": [path.as_posix() for path in config["rubricPaths"]],
        "maxSamples": config["maxSamples"],
        "recordRawOutputs": config["recordRawOutputs"],
        "requireDeterministicPass": config["requireDeterministicPass"],
        "temperature": config["temperature"],
    }


def _serialize_evaluation_mode(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "deterministic": config["deterministic"],
        "live": config["live"],
        "liveEvaluator": _serialize_live_evaluator(config["liveEvaluator"]),
    }


def _default_continuous_policy() -> dict[str, Any]:
    return {
        "enabled": False,
        "mode": "manual",
        "scheduleCron": None,
        "triggerOn": [],
        "minSignalCount": 0,
        "maxQueuedRuns": 1,
        "maxRunsPerSweep": 1,
        "learningWindowDays": 30,
        "stageOnly": True,
        "requireReviewPass": True,
    }


def _resolve_continuous_policy(frontmatter: dict[str, Any]) -> dict[str, Any]:
    defaults = _default_continuous_policy()
    raw_policy = frontmatter.get("continuousPolicy") or {}
    if isinstance(raw_policy, str):
        raw_policy = {"mode": raw_policy}
    if not isinstance(raw_policy, dict):
        raw_policy = {}

    mode = str(raw_policy.get("mode") or defaults["mode"])
    enabled = bool(raw_policy.get("enabled", mode not in {"manual", "disabled"}))

    return {
        "enabled": enabled,
        "mode": mode,
        "scheduleCron": raw_policy.get("scheduleCron") or raw_policy.get("cron"),
        "triggerOn": _normalized_strings(
            raw_policy.get("triggerOn")
            or raw_policy.get("triggerSources")
            or raw_policy.get("triggers")
        ),
        "minSignalCount": _coerce_int(
            raw_policy.get("minSignalCount"),
            defaults["minSignalCount"],
        ),
        "maxQueuedRuns": _coerce_int(
            raw_policy.get("maxQueuedRuns"),
            defaults["maxQueuedRuns"],
        ),
        "maxRunsPerSweep": _coerce_int(
            raw_policy.get("maxRunsPerSweep"),
            defaults["maxRunsPerSweep"],
        ),
        "learningWindowDays": _coerce_int(
            raw_policy.get("learningWindowDays"),
            defaults["learningWindowDays"],
        ),
        "stageOnly": bool(raw_policy.get("stageOnly", defaults["stageOnly"])),
        "requireReviewPass": bool(
            raw_policy.get("requireReviewPass", defaults["requireReviewPass"])
        ),
    }


def _serialize_continuous_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "enabled": policy["enabled"],
        "mode": policy["mode"],
        "scheduleCron": policy["scheduleCron"],
        "triggerOn": list(policy["triggerOn"]),
        "minSignalCount": policy["minSignalCount"],
        "maxQueuedRuns": policy["maxQueuedRuns"],
        "maxRunsPerSweep": policy["maxRunsPerSweep"],
        "learningWindowDays": policy["learningWindowDays"],
        "stageOnly": policy["stageOnly"],
        "requireReviewPass": policy["requireReviewPass"],
    }


def _derive_continuation_eligibility(experiment: dict[str, Any]) -> dict[str, Any]:
    policy = experiment["continuousPolicy"]
    blocked_reasons: list[str] = []
    mode = policy["mode"]

    if mode == "manual":
        blocked_reasons.append("manual_mode")
    elif mode == "disabled":
        blocked_reasons.append("disabled_mode")
    elif not policy["enabled"]:
        blocked_reasons.append("policy_disabled")
    elif mode == "scheduled" and not policy["scheduleCron"]:
        blocked_reasons.append("missing_schedule_cron")
    elif mode == "usage_driven" and not policy["triggerOn"]:
        blocked_reasons.append("missing_trigger_sources")

    return {
        "eligible": not blocked_reasons,
        "status": "eligible" if not blocked_reasons else "blocked",
        "blockedReasons": blocked_reasons,
        "executionMode": "report_only",
        "reviewGated": True,
    }


def _serialize_continuation_eligibility(eligibility: dict[str, Any]) -> dict[str, Any]:
    return {
        "eligible": eligibility["eligible"],
        "status": eligibility["status"],
        "blockedReasons": list(eligibility["blockedReasons"]),
        "executionMode": eligibility["executionMode"],
        "reviewGated": eligibility["reviewGated"],
    }


def _load_governed_state_payload() -> tuple[Path, dict[str, Any] | None]:
    state_path = DOCS_AGENTS_DIR / "state.json"
    try:
        payload = load_json(state_path)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return state_path, None
    if not isinstance(payload, dict):
        return state_path, None
    return state_path, payload


def _load_governed_review_state() -> dict[str, Any]:
    state_path, payload = _load_governed_state_payload()
    review_state = {
        "status": "UNAVAILABLE",
        "sourcePath": state_path.as_posix(),
        "readable": False,
    }
    if payload is None:
        return review_state
    quality_gate = payload.get("quality_gate")
    if not isinstance(quality_gate, dict):
        return review_state
    status = quality_gate.get("status")
    if not isinstance(status, str) or not status.strip():
        return review_state
    review_state["status"] = status.strip().upper()
    review_state["readable"] = True
    return review_state


def _derive_governed_task_lifecycle() -> dict[str, Any]:
    state_path, payload = _load_governed_state_payload()
    lifecycle = {
        "status": "unavailable",
        "readable": False,
        "sourcePath": state_path.as_posix(),
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
    if payload is None:
        return lifecycle

    missing_fields: list[str] = []

    def _object_dict(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        return {str(key): item for key, item in value.items()}

    task = _object_dict(payload.get("task"))
    quality_gate = _object_dict(payload.get("quality_gate"))
    next_action = _object_dict(payload.get("next_action"))

    def _required_string(source: dict[str, Any], key: str, field_name: str) -> str:
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        missing_fields.append(field_name)
        return "UNKNOWN"

    phase = payload.get("phase")
    if isinstance(phase, str) and phase.strip():
        lifecycle["phase"] = phase.strip()
    else:
        missing_fields.append("phase")
        lifecycle["phase"] = "UNKNOWN"

    lifecycle["taskId"] = _required_string(task, "id", "task.id")
    lifecycle["taskTitle"] = _required_string(task, "title", "task.title")
    lifecycle["qualityGateStatus"] = _required_string(
        quality_gate, "status", "quality_gate.status"
    ).upper()
    lifecycle["nextActionSummary"] = _required_string(next_action, "summary", "next_action.summary")
    lifecycle["nextActionOwner"] = _required_string(next_action, "owner", "next_action.owner")
    lifecycle["missingFields"] = missing_fields
    lifecycle["readable"] = True
    lifecycle["status"] = "available" if not missing_fields else "partial"
    return lifecycle


def _load_governed_review_report() -> dict[str, Any]:
    review_report_path = DOCS_AGENTS_DIR / "review-report.md"
    review_report = {
        "status": "UNAVAILABLE",
        "sourcePath": review_report_path.as_posix(),
        "readable": False,
    }
    try:
        raw = review_report_path.read_text(encoding="utf-8")
    except OSError:
        return review_report
    try:
        payload = _extract_json_block(raw)
    except (json.JSONDecodeError, TypeError, ValueError):
        return review_report
    if not isinstance(payload, dict):
        return review_report
    status = payload.get("status")
    if not isinstance(status, str) or not status.strip():
        return review_report
    review_report["status"] = status.strip().upper()
    review_report["readable"] = True
    return review_report


def _derive_governed_review_consensus() -> dict[str, Any]:
    state_review = _load_governed_review_state()
    report_review = _load_governed_review_report()
    blocked_reasons: list[str] = []

    if not state_review["readable"]:
        blocked_reasons.append("governed_review_state_unavailable")
    if not report_review["readable"]:
        blocked_reasons.append("governed_review_report_unavailable")
    if state_review["readable"] and report_review["readable"]:
        if state_review["status"] != report_review["status"]:
            blocked_reasons.append("governed_review_status_mismatch")
        elif state_review["status"] != "PASS":
            blocked_reasons.append("governed_review_not_pass")

    agrees = (
        state_review["readable"]
        and report_review["readable"]
        and state_review["status"] == report_review["status"]
    )

    return {
        "agrees": agrees,
        "status": "consistent" if not blocked_reasons else "blocked",
        "blockedReasons": blocked_reasons,
        "stateStatus": state_review["status"],
        "stateReadable": state_review["readable"],
        "stateSourcePath": state_review["sourcePath"],
        "reviewReportStatus": report_review["status"],
        "reviewReportReadable": report_review["readable"],
        "reviewReportSourcePath": report_review["sourcePath"],
    }


def _derive_continuation_readiness(
    eligibility: dict[str, Any], governed_review_consensus: dict[str, Any]
) -> dict[str, Any]:
    blocked_reasons = list(eligibility["blockedReasons"])
    consensus_reasons = list(governed_review_consensus["blockedReasons"])

    if not blocked_reasons:
        blocked_reasons.extend(consensus_reasons)

    return {
        "ready": not blocked_reasons,
        "status": "ready" if not blocked_reasons else "blocked",
        "blockedReasons": blocked_reasons,
        "executionMode": eligibility["executionMode"],
        "reviewGated": eligibility["reviewGated"],
        "policyEligible": eligibility["eligible"],
        "governedReviewStatus": governed_review_consensus["stateStatus"],
        "governedReviewReadable": governed_review_consensus["stateReadable"],
        "governedReviewSourcePath": governed_review_consensus["stateSourcePath"],
    }


def _serialize_continuation_readiness(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "ready": readiness["ready"],
        "status": readiness["status"],
        "blockedReasons": list(readiness["blockedReasons"]),
        "executionMode": readiness["executionMode"],
        "reviewGated": readiness["reviewGated"],
        "policyEligible": readiness["policyEligible"],
        "governedReviewStatus": readiness["governedReviewStatus"],
        "governedReviewReadable": readiness["governedReviewReadable"],
        "governedReviewSourcePath": readiness["governedReviewSourcePath"],
    }


def _serialize_governed_review_consensus(consensus: dict[str, Any]) -> dict[str, Any]:
    return {
        "agrees": consensus["agrees"],
        "status": consensus["status"],
        "blockedReasons": list(consensus["blockedReasons"]),
        "stateStatus": consensus["stateStatus"],
        "stateReadable": consensus["stateReadable"],
        "stateSourcePath": consensus["stateSourcePath"],
        "reviewReportStatus": consensus["reviewReportStatus"],
        "reviewReportReadable": consensus["reviewReportReadable"],
        "reviewReportSourcePath": consensus["reviewReportSourcePath"],
    }


def _serialize_governed_task_lifecycle(lifecycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": lifecycle["status"],
        "readable": lifecycle["readable"],
        "sourcePath": lifecycle["sourcePath"],
        "taskId": lifecycle["taskId"],
        "taskTitle": lifecycle["taskTitle"],
        "phase": lifecycle["phase"],
        "qualityGateStatus": lifecycle["qualityGateStatus"],
        "nextActionSummary": lifecycle["nextActionSummary"],
        "nextActionOwner": lifecycle["nextActionOwner"],
        "missingFields": list(lifecycle["missingFields"]),
    }


def _derive_reviewed_continuation_handoff(
    eligibility: dict[str, Any],
    lifecycle: dict[str, Any],
    governed_review_consensus: dict[str, Any],
    readiness: dict[str, Any],
) -> dict[str, Any]:
    blocked_reasons = list(readiness["blockedReasons"])
    if lifecycle["status"] == "unavailable":
        blocked_reasons.append("governed_task_lifecycle_unavailable")
    elif lifecycle["status"] == "partial":
        blocked_reasons.append("governed_task_lifecycle_partial")
    blocked_reasons = list(dict.fromkeys(blocked_reasons))

    ready = not blocked_reasons
    return {
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "blockedReasons": blocked_reasons,
        "handoffMode": "reviewed_manual",
        "manualOnly": True,
        "executionMode": eligibility["executionMode"],
        "reviewGated": eligibility["reviewGated"],
        "policyEligible": eligibility["eligible"],
        "continuationReadinessStatus": readiness["status"],
        "governedReviewConsensusStatus": governed_review_consensus["status"],
        "governedTaskLifecycleStatus": lifecycle["status"],
        "governedTaskId": lifecycle["taskId"],
        "governedTaskPhase": lifecycle["phase"],
        "summary": (
            "Ready for reviewed manual handoff."
            if ready
            else "Not ready for reviewed manual handoff."
        ),
        "recommendedAction": (
            "Review the staged patch bundle and governed artifacts before choosing the "
            "next bounded step."
            if ready
            else lifecycle["nextActionSummary"]
        ),
        "artifactRefs": {
            "state": lifecycle["sourcePath"],
            "reviewReport": governed_review_consensus["reviewReportSourcePath"],
            "report": (DOCS_AGENTS_DIR / "autoagent-report.md").as_posix(),
        },
    }


def _serialize_reviewed_continuation_handoff(handoff: dict[str, Any]) -> dict[str, Any]:
    return {
        "ready": handoff["ready"],
        "status": handoff["status"],
        "blockedReasons": list(handoff["blockedReasons"]),
        "handoffMode": handoff["handoffMode"],
        "manualOnly": handoff["manualOnly"],
        "executionMode": handoff["executionMode"],
        "reviewGated": handoff["reviewGated"],
        "policyEligible": handoff["policyEligible"],
        "continuationReadinessStatus": handoff["continuationReadinessStatus"],
        "governedReviewConsensusStatus": handoff["governedReviewConsensusStatus"],
        "governedTaskLifecycleStatus": handoff["governedTaskLifecycleStatus"],
        "governedTaskId": handoff["governedTaskId"],
        "governedTaskPhase": handoff["governedTaskPhase"],
        "summary": handoff["summary"],
        "recommendedAction": handoff["recommendedAction"],
        "artifactRefs": dict(handoff["artifactRefs"]),
    }


def _derive_orchestration_contract(
    handoff: dict[str, Any],
    lifecycle: dict[str, Any],
) -> dict[str, Any]:
    blocked_reasons = list(handoff["blockedReasons"])
    ready = not blocked_reasons
    task_id = lifecycle["taskId"]
    return {
        "ready": ready,
        "status": "staged" if ready else "blocked",
        "blockedReasons": blocked_reasons,
        "contractMode": "staged_dispatch_simulation",
        "dispatchScope": "bounded_follow_on_slice",
        "manualOnly": handoff["manualOnly"],
        "executionMode": handoff["executionMode"],
        "reviewGated": handoff["reviewGated"],
        "policyEligible": handoff["policyEligible"],
        "reviewedHandoffStatus": handoff["status"],
        "governedTaskLifecycleStatus": lifecycle["status"],
        "governedTaskId": task_id,
        "governedTaskPhase": lifecycle["phase"],
        "contractId": f"{task_id}::staged_dispatch_simulation",
        "summary": (
            "Staged dispatch simulation is ready for manual review."
            if ready
            else "Staged dispatch simulation is blocked."
        ),
        "recommendedAction": (
            "Open the next bounded implementation step but keep execution manual and report_only."
            if ready
            else handoff["recommendedAction"]
        ),
        "artifactRefs": {
            "state": lifecycle["sourcePath"],
            "reviewReport": handoff["artifactRefs"]["reviewReport"],
            "report": handoff["artifactRefs"]["report"],
            "adr": (
                ROOT / "docs" / "adr" / "0001-phase4-bounded-orchestration-rollout.md"
            ).as_posix(),
        },
    }


def _serialize_orchestration_contract(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "ready": contract["ready"],
        "status": contract["status"],
        "blockedReasons": list(contract["blockedReasons"]),
        "contractMode": contract["contractMode"],
        "dispatchScope": contract["dispatchScope"],
        "manualOnly": contract["manualOnly"],
        "executionMode": contract["executionMode"],
        "reviewGated": contract["reviewGated"],
        "policyEligible": contract["policyEligible"],
        "reviewedHandoffStatus": contract["reviewedHandoffStatus"],
        "governedTaskLifecycleStatus": contract["governedTaskLifecycleStatus"],
        "governedTaskId": contract["governedTaskId"],
        "governedTaskPhase": contract["governedTaskPhase"],
        "contractId": contract["contractId"],
        "summary": contract["summary"],
        "recommendedAction": contract["recommendedAction"],
        "artifactRefs": dict(contract["artifactRefs"]),
    }


def _derive_reviewed_dispatch_intent(
    contract: dict[str, Any],
    handoff: dict[str, Any],
    lifecycle: dict[str, Any],
) -> dict[str, Any]:
    blocked_reasons = list(contract["blockedReasons"])
    ready = not blocked_reasons

    if not ready:
        status = "blocked"
        approval_status = "blocked"
        summary = "Reviewed dispatch intent is blocked."
        recommended_action = contract["recommendedAction"]
    elif lifecycle["phase"] == "Done":
        status = "approval_pending"
        approval_status = "pending_explicit_approval"
        summary = "Reviewed dispatch intent is awaiting explicit approval metadata."
        recommended_action = (
            "Record explicit approval metadata before opening the next bounded implementation step."
        )
    else:
        status = "staged_for_review"
        approval_status = "not_requested"
        summary = "Reviewed dispatch intent is staged for manual review."
        recommended_action = (
            "Review the staged dispatch intent and governed artifacts before requesting "
            "explicit approval metadata."
        )

    return {
        "ready": ready,
        "status": status,
        "blockedReasons": blocked_reasons,
        "intentMode": "reviewed_dispatch_intent",
        "dispatchScope": contract["dispatchScope"],
        "manualOnly": contract["manualOnly"],
        "executionMode": contract["executionMode"],
        "reviewGated": contract["reviewGated"],
        "policyEligible": contract["policyEligible"],
        "requiresExplicitApproval": True,
        "approvalStatus": approval_status,
        "approvalMetadataPresent": False,
        "approvalSource": "governed_artifacts_only",
        "orchestrationContractStatus": contract["status"],
        "reviewedHandoffStatus": handoff["status"],
        "governedReviewConsensusStatus": handoff["governedReviewConsensusStatus"],
        "governedTaskLifecycleStatus": lifecycle["status"],
        "governedTaskId": lifecycle["taskId"],
        "governedTaskPhase": lifecycle["phase"],
        "intentId": f"{contract['contractId']}::reviewed_dispatch_intent",
        "summary": summary,
        "recommendedAction": recommended_action,
        "artifactRefs": dict(contract["artifactRefs"]),
    }


def _serialize_reviewed_dispatch_intent(intent: dict[str, Any]) -> dict[str, Any]:
    return {
        "ready": intent["ready"],
        "status": intent["status"],
        "blockedReasons": list(intent["blockedReasons"]),
        "intentMode": intent["intentMode"],
        "dispatchScope": intent["dispatchScope"],
        "manualOnly": intent["manualOnly"],
        "executionMode": intent["executionMode"],
        "reviewGated": intent["reviewGated"],
        "policyEligible": intent["policyEligible"],
        "requiresExplicitApproval": intent["requiresExplicitApproval"],
        "approvalStatus": intent["approvalStatus"],
        "approvalMetadataPresent": intent["approvalMetadataPresent"],
        "approvalSource": intent["approvalSource"],
        "orchestrationContractStatus": intent["orchestrationContractStatus"],
        "reviewedHandoffStatus": intent["reviewedHandoffStatus"],
        "governedReviewConsensusStatus": intent["governedReviewConsensusStatus"],
        "governedTaskLifecycleStatus": intent["governedTaskLifecycleStatus"],
        "governedTaskId": intent["governedTaskId"],
        "governedTaskPhase": intent["governedTaskPhase"],
        "intentId": intent["intentId"],
        "summary": intent["summary"],
        "recommendedAction": intent["recommendedAction"],
        "artifactRefs": dict(intent["artifactRefs"]),
    }


def _derive_governed_approval_metadata(
    intent: dict[str, Any],
    governed_review_consensus: dict[str, Any],
    lifecycle: dict[str, Any],
) -> dict[str, Any]:
    blocked_reasons = list(intent["blockedReasons"])
    review_pass_recorded = (
        governed_review_consensus["status"] == "consistent"
        and governed_review_consensus["stateStatus"] == "PASS"
        and governed_review_consensus["reviewReportStatus"] == "PASS"
    )
    review_pass_readable = (
        governed_review_consensus["stateReadable"]
        and governed_review_consensus["reviewReportReadable"]
    )

    if blocked_reasons:
        status = "blocked"
        ready_for_recording = False
        summary = "Governed approval metadata is blocked."
        recommended_action = intent["recommendedAction"]
    elif lifecycle["phase"] == "Done":
        status = "ready_for_recording"
        ready_for_recording = True
        summary = "Governed approval metadata is ready for manual approval recording."
        recommended_action = (
            "Record explicit manual approval metadata in governed artifacts before opening "
            "the next bounded implementation step."
        )
    else:
        status = "not_requested"
        ready_for_recording = False
        summary = "Governed approval metadata is not yet requested."
        recommended_action = (
            "Advance the governed task to Done/PASS and review the dispatch intent before "
            "recording explicit manual approval metadata."
        )

    return {
        "ready": ready_for_recording,
        "status": status,
        "blockedReasons": blocked_reasons,
        "approvalMode": "governed_approval_metadata",
        "manualOnly": intent["manualOnly"],
        "executionMode": intent["executionMode"],
        "reviewGated": intent["reviewGated"],
        "policyEligible": intent["policyEligible"],
        "requiresExplicitApproval": intent["requiresExplicitApproval"],
        "approvalMetadataPresent": False,
        "approvalSource": intent["approvalSource"],
        "readyForRecording": ready_for_recording,
        "reviewPassRecorded": review_pass_recorded,
        "reviewPassReadable": review_pass_readable,
        "qualityGateStatus": lifecycle["qualityGateStatus"],
        "reviewedDispatchIntentStatus": intent["status"],
        "governedReviewConsensusStatus": governed_review_consensus["status"],
        "governedTaskLifecycleStatus": lifecycle["status"],
        "governedTaskId": lifecycle["taskId"],
        "governedTaskPhase": lifecycle["phase"],
        "metadataId": f"{intent['intentId']}::governed_approval_metadata",
        "summary": summary,
        "recommendedAction": recommended_action,
        "artifactRefs": dict(intent["artifactRefs"]),
    }


def _serialize_governed_approval_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "ready": metadata["ready"],
        "status": metadata["status"],
        "blockedReasons": list(metadata["blockedReasons"]),
        "approvalMode": metadata["approvalMode"],
        "manualOnly": metadata["manualOnly"],
        "executionMode": metadata["executionMode"],
        "reviewGated": metadata["reviewGated"],
        "policyEligible": metadata["policyEligible"],
        "requiresExplicitApproval": metadata["requiresExplicitApproval"],
        "approvalMetadataPresent": metadata["approvalMetadataPresent"],
        "approvalSource": metadata["approvalSource"],
        "readyForRecording": metadata["readyForRecording"],
        "reviewPassRecorded": metadata["reviewPassRecorded"],
        "reviewPassReadable": metadata["reviewPassReadable"],
        "qualityGateStatus": metadata["qualityGateStatus"],
        "reviewedDispatchIntentStatus": metadata["reviewedDispatchIntentStatus"],
        "governedReviewConsensusStatus": metadata["governedReviewConsensusStatus"],
        "governedTaskLifecycleStatus": metadata["governedTaskLifecycleStatus"],
        "governedTaskId": metadata["governedTaskId"],
        "governedTaskPhase": metadata["governedTaskPhase"],
        "metadataId": metadata["metadataId"],
        "summary": metadata["summary"],
        "recommendedAction": metadata["recommendedAction"],
        "artifactRefs": dict(metadata["artifactRefs"]),
    }


def _default_staged_patch_policy() -> dict[str, Any]:
    return {
        "enabled": True,
        "mode": "review_bundle",
        "applyOnPass": False,
        "includeTargetSnapshots": True,
        "includeDiffSummary": True,
        "reviewerHints": [],
        "manifestFormat": "candidate_snapshot",
    }


def _resolve_staged_patch_policy(frontmatter: dict[str, Any]) -> dict[str, Any]:
    defaults = _default_staged_patch_policy()
    raw_policy = frontmatter.get("stagedPatchPolicy") or frontmatter.get("patchStaging") or {}
    if isinstance(raw_policy, str):
        raw_policy = {"mode": raw_policy}
    if not isinstance(raw_policy, dict):
        raw_policy = {}

    legacy_stage = bool(frontmatter.get("stageForReview", defaults["enabled"]))
    enabled = bool(raw_policy.get("enabled", legacy_stage))
    mode = str(raw_policy.get("mode") or (defaults["mode"] if enabled else "disabled"))

    return {
        "enabled": enabled,
        "mode": mode,
        "applyOnPass": bool(raw_policy.get("applyOnPass", defaults["applyOnPass"])),
        "includeTargetSnapshots": bool(
            raw_policy.get("includeTargetSnapshots", defaults["includeTargetSnapshots"])
        ),
        "includeDiffSummary": bool(
            raw_policy.get("includeDiffSummary", defaults["includeDiffSummary"])
        ),
        "reviewerHints": _normalized_strings(
            raw_policy.get("reviewerHints") or defaults["reviewerHints"]
        ),
        "manifestFormat": str(raw_policy.get("manifestFormat") or defaults["manifestFormat"]),
    }


def _serialize_staged_patch_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "enabled": policy["enabled"],
        "mode": policy["mode"],
        "applyOnPass": policy["applyOnPass"],
        "includeTargetSnapshots": policy["includeTargetSnapshots"],
        "includeDiffSummary": policy["includeDiffSummary"],
        "reviewerHints": list(policy["reviewerHints"]),
        "manifestFormat": policy["manifestFormat"],
    }


def _infer_external_log_format(source_path: Path) -> str:
    suffix = source_path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    if suffix == ".json":
        return "json"
    return "text"


def _normalize_external_log_sources(
    base_dir: Path,
    raw_sources: Any,
    max_records_default: int,
    max_line_length_default: int,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, raw_source in enumerate(_as_list(raw_sources), start=1):
        if isinstance(raw_source, str):
            raw_source = {"path": raw_source}
        if not isinstance(raw_source, dict):
            raise ValueError("Each external log source must be a string path or mapping.")
        source_path = _resolve_path(base_dir, raw_source.get("path"))
        if source_path is None:
            raise ValueError(f"External log source #{index} is missing a path.")
        source_id = str(
            raw_source.get("id") or raw_source.get("sourceId") or _normalized_id(source_path.stem)
        )
        kind = str(raw_source.get("kind") or raw_source.get("type") or "external_debug_log")
        include_patterns = _normalized_strings(raw_source.get("includeLinePatterns"))
        if not include_patterns and kind in {"vscode_debug_log", "copilot_debug_log"}:
            include_patterns = list(DEFAULT_DEBUG_LOG_INCLUDE_PATTERNS)
        normalized.append(
            {
                "id": source_id,
                "kind": kind,
                "path": source_path,
                "format": str(raw_source.get("format") or _infer_external_log_format(source_path)),
                "optional": bool(raw_source.get("optional", True)),
                "includeLinePatterns": include_patterns,
                "excludeLinePatterns": _normalized_strings(raw_source.get("excludeLinePatterns")),
                "maxRecords": int(raw_source.get("maxRecords", max_records_default)),
                "maxLineLength": int(raw_source.get("maxLineLength", max_line_length_default)),
            }
        )
    return normalized


def _append_derived_external_log_sources(
    existing_sources: list[dict[str, Any]],
    *,
    base_dir: Path,
    raw_paths: list[str],
    kind: str,
    id_prefix: str,
    max_records_default: int,
    max_line_length_default: int,
) -> None:
    derived_sources = _normalize_external_log_sources(
        base_dir,
        [
            {
                "id": f"{id_prefix}-{index}",
                "kind": kind,
                "path": value,
            }
            for index, value in enumerate(raw_paths, start=1)
        ],
        max_records_default,
        max_line_length_default,
    )
    existing_paths = {source["path"].as_posix() for source in existing_sources}
    for source in derived_sources:
        source_path = source["path"].as_posix()
        if source_path in existing_paths:
            continue
        existing_paths.add(source_path)
        existing_sources.append(source)


def _merge_external_log_sources(
    base_dir: Path,
    raw_policy: dict[str, Any],
    defaults: dict[str, Any],
) -> list[dict[str, Any]]:
    sources = _normalize_external_log_sources(
        base_dir,
        raw_policy.get("externalLogSources"),
        defaults["maxRecordsPerFile"],
        defaults["maxExternalLogLineLength"],
    )

    if bool(raw_policy.get("includeChatHistory", defaults["includeChatHistory"])):
        _append_derived_external_log_sources(
            sources,
            base_dir=base_dir,
            raw_paths=_normalized_strings(raw_policy.get("chatHistoryPaths")),
            kind="chat_transcript",
            id_prefix="chat-history",
            max_records_default=defaults["maxRecordsPerFile"],
            max_line_length_default=defaults["maxExternalLogLineLength"],
        )

    if bool(raw_policy.get("includeTranscriptHistory", defaults["includeTranscriptHistory"])):
        _append_derived_external_log_sources(
            sources,
            base_dir=base_dir,
            raw_paths=_normalized_strings(raw_policy.get("transcriptHistoryPaths")),
            kind="conversation_transcript",
            id_prefix="transcript-history",
            max_records_default=defaults["maxRecordsPerFile"],
            max_line_length_default=defaults["maxExternalLogLineLength"],
        )

    if bool(raw_policy.get("includeHandoffHistory", defaults["includeHandoffHistory"])):
        _append_derived_external_log_sources(
            sources,
            base_dir=base_dir,
            raw_paths=_normalized_strings(raw_policy.get("handoffHistoryPaths")),
            kind="handoff_history",
            id_prefix="handoff-history",
            max_records_default=defaults["maxRecordsPerFile"],
            max_line_length_default=defaults["maxExternalLogLineLength"],
        )

    if bool(raw_policy.get("includeVsCodeLogs", defaults["includeVsCodeLogs"])):
        _append_derived_external_log_sources(
            sources,
            base_dir=base_dir,
            raw_paths=_normalized_strings(raw_policy.get("vsCodeLogPaths")),
            kind="vscode_debug_log",
            id_prefix="vscode-log",
            max_records_default=defaults["maxRecordsPerFile"],
            max_line_length_default=defaults["maxExternalLogLineLength"],
        )
    return sources


def _serialize_external_log_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": source["id"],
            "kind": source["kind"],
            "path": source["path"].as_posix(),
            "format": source["format"],
            "optional": source["optional"],
            "includeLinePatterns": list(source["includeLinePatterns"]),
            "excludeLinePatterns": list(source["excludeLinePatterns"]),
            "maxRecords": source["maxRecords"],
            "maxLineLength": source["maxLineLength"],
        }
        for source in sources
    ]


def _is_transcript_source_kind(kind: str) -> bool:
    return kind in {
        "agent_transcript",
        "chat_transcript",
        "conversation_transcript",
        "copilot_chat_transcript",
        "tool_transcript",
    }


def _is_handoff_source_kind(kind: str) -> bool:
    return kind in {
        "handoff_history",
        "handoff_transcript",
        "agent_handoff_history",
        "delegation_history",
    }


def _external_log_record_kind(kind: str) -> str:
    if _is_handoff_source_kind(kind):
        return "handoff_event"
    if _is_transcript_source_kind(kind):
        return "transcript_event"
    return "external_log"


def _flatten_external_json_payloads(value: Any, *, depth: int = 0) -> list[Any]:
    if depth > 6 or value is None:
        return []
    if isinstance(value, list):
        payloads: list[Any] = []
        for item in value:
            payloads.extend(_flatten_external_json_payloads(item, depth=depth + 1))
        return payloads
    if isinstance(value, dict):
        payloads: list[Any] = []
        for key in (
            "messages",
            "events",
            "entries",
            "items",
            "records",
            "history",
            "transcript",
            "conversation",
            "sessions",
            "turns",
        ):
            nested_value = value.get(key)
            if isinstance(nested_value, (list, dict)):
                payloads.extend(_flatten_external_json_payloads(nested_value, depth=depth + 1))
        return payloads or [value]
    return [value]


def _pattern_matches(value: str, pattern: str) -> bool:
    try:
        return re.search(pattern, value, re.IGNORECASE) is not None
    except re.error:
        return pattern.lower() in value.lower()


def _log_status(value: str) -> str:
    if LOG_ERROR_RE.search(value):
        return "error"
    if LOG_WARNING_RE.search(value):
        return "warning"
    if LOG_SUCCESS_RE.search(value):
        return "success"
    return "info"


def _truncate_text(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[: max(0, max_length - 3)] + "..."


def _transcript_text_fragments(value: Any, *, depth: int = 0) -> list[str]:
    if depth > 4:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        fragments: list[str] = []
        for item in value:
            fragments.extend(_transcript_text_fragments(item, depth=depth + 1))
        return fragments
    if isinstance(value, dict):
        preferred_fragments: list[str] = []
        for key in (
            "text",
            "message",
            "content",
            "prompt",
            "response",
            "output",
            "summary",
            "result",
            "name",
            "id",
        ):
            if key in value:
                preferred_fragments.extend(_transcript_text_fragments(value[key], depth=depth + 1))
        if preferred_fragments:
            return preferred_fragments

        fragments: list[str] = []
        for key, nested_value in value.items():
            if key in {"ts", "timestamp", "type", "kind", "status", "role", "speaker"}:
                continue
            fragments.extend(_transcript_text_fragments(nested_value, depth=depth + 1))
        return fragments
    return []


def _transcript_payload_text(payload: dict[str, Any]) -> str:
    fragments = _transcript_text_fragments(payload)
    return " ".join(fragment.strip() for fragment in fragments if fragment and fragment.strip())


def _transcript_path_values(value: Any, *paths: tuple[str, ...], depth: int = 0) -> list[Any]:
    if depth > 6:
        return []
    matches: list[Any] = []
    for path in paths:
        matches.extend(_transcript_path_value(value, path, depth=depth))
    return matches


def _transcript_path_value(value: Any, path: tuple[str, ...], *, depth: int = 0) -> list[Any]:
    if depth > 6:
        return []
    if not path:
        return [value]
    if isinstance(value, list):
        matches: list[Any] = []
        for item in value:
            matches.extend(_transcript_path_value(item, path, depth=depth + 1))
        return matches
    if not isinstance(value, dict):
        return []
    head, *tail = path
    if head not in value:
        return []
    return _transcript_path_value(value[head], tuple(tail), depth=depth + 1)


def _non_empty_scalar_texts(values: list[Any]) -> list[str]:
    texts: list[str] = []

    def _collect(value: Any) -> None:
        if value is None or isinstance(value, dict):
            return
        if isinstance(value, list):
            for item in value:
                _collect(item)
            return
        text = str(value).strip()
        if text:
            texts.append(text)

    for value in values:
        _collect(value)
    return texts


def _first_non_empty_scalar(values: list[Any]) -> str | None:
    texts = _non_empty_scalar_texts(values)
    return texts[0] if texts else None


def _unique_non_empty_scalar_texts(values: list[Any]) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()
    for text in _non_empty_scalar_texts(values):
        normalized = text.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        texts.append(text)
    return texts


def _transcript_candidate_ids(payload: dict[str, Any]) -> list[str]:
    container_prefixes = [
        (),
        ("metadata",),
        ("context",),
        ("message",),
        ("message", "metadata"),
        ("response",),
        ("response", "metadata"),
        ("result",),
        ("result", "metadata"),
    ]
    candidate_suffixes = [
        ("candidateId",),
        ("candidate", "id"),
        ("candidate", "candidateId"),
        ("selectedCandidateId",),
        ("selectedCandidate", "id"),
        ("selectedCandidate", "candidateId"),
        ("winnerCandidateId",),
        ("winnerCandidate", "id"),
        ("winnerCandidate", "candidateId"),
        ("winningCandidateId",),
        ("winningCandidate", "id"),
        ("winningCandidate", "candidateId"),
        ("bestCandidateId",),
        ("bestCandidate", "id"),
        ("bestCandidate", "candidateId"),
        ("comparedCandidateId",),
        ("comparedCandidate", "id"),
        ("comparedCandidate", "candidateId"),
    ]
    path_values = _transcript_path_values(
        payload,
        *(prefix + suffix for prefix in container_prefixes for suffix in candidate_suffixes),
    )
    return _unique_non_empty_scalar_texts(path_values)


def _transcript_lineage_candidate_ids(payload: dict[str, Any]) -> list[str]:
    container_prefixes = [
        (),
        ("metadata",),
        ("context",),
        ("message",),
        ("message", "metadata"),
        ("response",),
        ("response", "metadata"),
        ("result",),
        ("result", "metadata"),
    ]
    lineage_suffixes = [
        ("lineageCandidateIds",),
        ("lineage", "candidateIds"),
        ("candidateLineageIds",),
        ("candidateLineage", "candidateIds"),
        ("candidateLineage",),
    ]
    path_values = _transcript_path_values(
        payload,
        *(prefix + suffix for prefix in container_prefixes for suffix in lineage_suffixes),
    )
    return _unique_non_empty_scalar_texts(path_values)


def _transcript_handoff_refs(payload: dict[str, Any]) -> list[str]:
    handoff_paths = [
        ("handoffCandidateId",),
        ("handoffCandidate", "id"),
        ("nextCandidateId",),
        ("nextCandidate", "id"),
        ("assignedCandidateId",),
        ("assignedCandidate", "id"),
        ("delegateCandidateId",),
        ("handoff", "targetCandidateId"),
        ("handoff", "targetCandidate", "id"),
        ("handoff", "candidateId"),
        ("handoff", "candidate", "id"),
        ("handoff", "recipientCandidateId"),
        ("handoff", "recipientCandidate", "id"),
        ("delegation", "targetCandidateId"),
        ("delegation", "targetCandidate", "id"),
        ("delegation", "candidateId"),
        ("delegation", "candidate", "id"),
        ("delegation", "recipientCandidateId"),
        ("delegation", "recipientCandidate", "id"),
        ("message", "handoff", "targetCandidateId"),
        ("message", "handoff", "candidateId"),
        ("message", "metadata", "handoff", "targetCandidateId"),
        ("message", "metadata", "handoff", "candidateId"),
        ("result", "handoff", "targetCandidateId"),
        ("response", "handoff", "targetCandidateId"),
    ]
    return _unique_non_empty_scalar_texts(_transcript_path_values(payload, *handoff_paths))


def _transcript_role(payload: dict[str, Any]) -> str | None:
    return _first_non_empty_scalar(
        _transcript_path_values(
            payload,
            ("role",),
            ("speaker",),
            ("actor",),
            ("participant",),
            ("author",),
            ("sender",),
            ("author", "role"),
            ("sender", "role"),
            ("message", "role"),
            ("message", "speaker"),
            ("message", "actor"),
            ("message", "participant"),
            ("message", "author"),
            ("message", "sender"),
            ("message", "author", "role"),
            ("message", "sender", "role"),
        )
    )


def _transcript_tool_name(payload: dict[str, Any]) -> str | None:
    return _first_non_empty_scalar(
        _transcript_path_values(
            payload,
            ("toolName",),
            ("tool", "toolName"),
            ("tool", "name"),
            ("toolCall", "toolName"),
            ("toolCall", "name"),
            ("toolCall", "function", "name"),
            ("function", "toolName"),
            ("function", "name"),
            ("toolCalls", "toolName"),
            ("toolCalls", "name"),
            ("toolCalls", "function", "name"),
            ("tool_calls", "toolName"),
            ("tool_calls", "name"),
            ("tool_calls", "function", "name"),
            ("message", "toolName"),
            ("message", "tool", "toolName"),
            ("message", "tool", "name"),
            ("message", "toolCall", "toolName"),
            ("message", "toolCall", "name"),
            ("message", "toolCall", "function", "name"),
            ("message", "function", "toolName"),
            ("message", "function", "name"),
            ("message", "toolCalls", "toolName"),
            ("message", "toolCalls", "name"),
            ("message", "toolCalls", "function", "name"),
            ("message", "tool_calls", "toolName"),
            ("message", "tool_calls", "name"),
            ("message", "tool_calls", "function", "name"),
        )
    )


def _transcript_record_status(payload: dict[str, Any]) -> str | None:
    raw_status = _first_non_empty_scalar(
        _transcript_path_values(
            payload,
            ("status",),
            ("outcome",),
            ("state",),
            ("result",),
            ("result", "status"),
            ("result", "outcome"),
            ("result", "state"),
            ("response", "status"),
            ("response", "outcome"),
            ("response", "state"),
            ("message", "status"),
            ("message", "outcome"),
            ("message", "state"),
        )
    )
    if raw_status is not None:
        derived_status = _log_status(raw_status)
        if derived_status != "info":
            return derived_status
        lowered_status = raw_status.strip().lower()
        if lowered_status in {
            "ok",
            "completed",
            "done",
            "pass",
            "passed",
            "ready",
            "success",
            "successful",
            "succeeded",
        }:
            return "success"
        return lowered_status

    if any(
        value is not None
        for value in _transcript_path_values(
            payload,
            ("error",),
            ("exception",),
            ("result", "error"),
            ("result", "exception"),
            ("response", "error"),
            ("response", "exception"),
            ("message", "error"),
            ("message", "exception"),
        )
    ):
        return "error"
    if any(
        value is True
        for value in _transcript_path_values(
            payload,
            ("success",),
            ("result", "success"),
            ("response", "success"),
            ("message", "success"),
        )
    ):
        return "success"

    transcript_text = _transcript_payload_text(payload)
    if not transcript_text:
        return None
    derived_status = _log_status(transcript_text)
    return derived_status if derived_status != "info" else None


def _default_target_id(path: Path, index: int) -> str:
    suffixes = "".join(path.suffixes)
    stem = path.name[: -len(suffixes)] if suffixes and path.name.endswith(suffixes) else path.stem
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return normalized or f"target-{index}"


def _infer_target_kind(path: Path) -> str:
    name = path.name
    if name.endswith(".agent.md"):
        return "agent_profile"
    if name.endswith(".instructions.md"):
        return "instruction_document"
    if name == "SKILL.md":
        return "skill_document"
    return "markdown_document"


def _normalize_targets(base_dir: Path, frontmatter: dict[str, Any]) -> list[dict[str, Any]]:
    raw_targets = frontmatter.get("optimizationTargets")
    if raw_targets is None:
        legacy_target = frontmatter.get("targetAgentPath")
        target_path = _resolve_path(base_dir, legacy_target)
        if target_path is None:
            raise ValueError("Experiment is missing targetAgentPath or optimizationTargets.")
        raw_targets = [
            {
                "id": "primary",
                "path": legacy_target,
                "kind": _infer_target_kind(target_path),
                "primary": True,
                "mutableRegions": ["frontmatter", "body"],
            }
        ]

    if not isinstance(raw_targets, list) or not raw_targets:
        raise ValueError("optimizationTargets must be a non-empty list when provided.")

    targets: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw_target in enumerate(raw_targets, start=1):
        if isinstance(raw_target, str):
            raw_target = {"path": raw_target}
        if not isinstance(raw_target, dict):
            raise ValueError("Each optimization target must be a string path or mapping.")

        raw_path = raw_target.get("path") or raw_target.get("targetPath")
        target_path = _resolve_path(base_dir, raw_path)
        if target_path is None:
            raise ValueError(f"Optimization target #{index} is missing a path.")

        target_id = str(
            raw_target.get("id")
            or raw_target.get("targetId")
            or _default_target_id(target_path, index)
        )
        if target_id in seen_ids:
            raise ValueError(f"Duplicate optimization target id: {target_id}")
        seen_ids.add(target_id)

        targets.append(
            {
                "id": target_id,
                "path": target_path,
                "kind": str(
                    raw_target.get("kind")
                    or raw_target.get("type")
                    or _infer_target_kind(target_path)
                ),
                "primary": bool(raw_target.get("primary", False)),
                "mutableRegions": [
                    str(value)
                    for value in _as_list(
                        raw_target.get("mutableRegions") or ["frontmatter", "body"]
                    )
                ],
                "weight": float(raw_target.get("weight", 1.0)),
            }
        )

    if not any(target["primary"] for target in targets):
        targets[0]["primary"] = True
    return targets


def _primary_target(targets: list[dict[str, Any]]) -> dict[str, Any]:
    for target in targets:
        if target.get("primary"):
            return target
    return targets[0]


def _serialize_targets(targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": target["id"],
            "path": target["path"].as_posix(),
            "kind": target["kind"],
            "primary": target["primary"],
            "mutableRegions": target["mutableRegions"],
            "weight": target["weight"],
        }
        for target in targets
    ]


def _resolve_candidate_policy(frontmatter: dict[str, Any]) -> dict[str, Any]:
    raw_policy = dict(frontmatter.get("candidatePolicy") or {})
    keep_strategy = str(raw_policy.get("keepStrategy") or "score-then-simpler").strip()
    raw_frontier_size = raw_policy.get("frontierSize")
    frontier_size = 1 if raw_frontier_size is None else int(raw_frontier_size)
    search_strategy = str(
        raw_policy.get("searchStrategy") or ("frontier" if frontier_size > 1 else "current_best")
    ).strip()

    if keep_strategy not in SUPPORTED_CANDIDATE_KEEP_STRATEGIES:
        raise ValueError(f"Unsupported candidatePolicy.keepStrategy: {keep_strategy}")
    if search_strategy not in SUPPORTED_CANDIDATE_SEARCH_STRATEGIES:
        raise ValueError(f"Unsupported candidatePolicy.searchStrategy: {search_strategy}")
    if frontier_size < 1:
        raise ValueError("candidatePolicy.frontierSize must be at least 1.")
    if search_strategy == "current_best" and frontier_size != 1:
        raise ValueError(
            "candidatePolicy.frontierSize must be 1 when searchStrategy is current_best."
        )

    return {
        "keepStrategy": keep_strategy,
        "searchStrategy": search_strategy,
        "frontierSize": frontier_size,
    }


def _document_suffix(path: Path) -> str:
    suffixes = "".join(path.suffixes)
    return suffixes or ".md"


def _candidate_output_path(
    candidates_root: Path,
    iteration: int,
    candidate_id: str,
    documents: dict[str, dict[str, Any]],
    primary_target_id: str,
) -> Path:
    if len(documents) == 1:
        target_path = documents[primary_target_id]["target"]["path"]
        return (
            candidates_root
            / f"iteration-{iteration:02d}-{candidate_id}{_document_suffix(target_path)}"
        )
    return candidates_root / f"iteration-{iteration:02d}-{candidate_id}"


def _write_candidate_documents(
    candidate_path: Path,
    documents: dict[str, dict[str, Any]],
    primary_target_id: str,
) -> None:
    if candidate_path.suffix:
        document = documents[primary_target_id]
        _write(
            candidate_path,
            render_markdown_document(document["frontmatter"], document["body"]),
        )
        return

    candidate_path.mkdir(parents=True, exist_ok=True)
    for target_id, document in documents.items():
        target_path = document["target"]["path"]
        bundle_path = candidate_path / f"{target_id}{_document_suffix(target_path)}"
        _write(bundle_path, render_markdown_document(document["frontmatter"], document["body"]))


def load_target_documents(targets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for target in targets:
        frontmatter, body = load_markdown_document(target["path"])
        documents[target["id"]] = {
            "target": deepcopy(target),
            "frontmatter": frontmatter,
            "body": body,
        }
    return documents


def _document_or_error(
    documents: dict[str, dict[str, Any]],
    target_id: str,
    context: str,
) -> dict[str, Any]:
    if target_id not in documents:
        raise ValueError(f"{context} references unknown targetId '{target_id}'.")
    return documents[target_id]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_experiment(path: Path) -> dict[str, Any]:
    frontmatter, body = load_markdown_document(path)
    base_dir = path.parent
    targets = _normalize_targets(base_dir, frontmatter)
    primary_target = _primary_target(targets)
    candidate_policy = _resolve_candidate_policy(frontmatter)
    evaluation_mode = _resolve_evaluation_mode(base_dir, frontmatter)
    continuous_policy = _resolve_continuous_policy(frontmatter)
    staged_patch_policy = _resolve_staged_patch_policy(frontmatter)
    evidence_policy = _resolve_evidence_policy(base_dir, frontmatter)
    reviewed_policy_runtime = _resolve_reviewed_policy_runtime(base_dir, frontmatter)
    stage_for_review = bool(frontmatter.get("stageForReview", staged_patch_policy["enabled"]))
    experiment = {
        "path": path,
        "name": frontmatter.get("name") or path.stem,
        "description": frontmatter.get("description") or "",
        "body": body,
        "maxIterations": int(frontmatter.get("maxIterations") or 0),
        "applyBestCandidate": bool(frontmatter.get("applyBestCandidate", False)),
        "targets": targets,
        "primaryTargetId": primary_target["id"],
        "targetAgentPath": primary_target["path"],
        "benchmarkPath": _resolve_path(base_dir, frontmatter.get("benchmarkPath")),
        "mutationCatalogPath": _resolve_path(base_dir, frontmatter.get("mutationCatalogPath")),
        "candidatePolicy": candidate_policy,
        "evaluationMode": evaluation_mode,
        "continuousPolicy": continuous_policy,
        "stagedPatchPolicy": staged_patch_policy,
        "evidencePolicy": evidence_policy,
        "reviewedPolicyRuntime": reviewed_policy_runtime,
        "stageForReview": stage_for_review,
    }
    experiment["continuationEligibility"] = _derive_continuation_eligibility(experiment)
    if experiment["benchmarkPath"] is None:
        raise ValueError("Experiment is missing benchmarkPath.")
    if experiment["mutationCatalogPath"] is None:
        raise ValueError("Experiment is missing mutationCatalogPath.")
    return experiment


def load_benchmark(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    checks = payload.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError(f"{path.as_posix()} must contain a non-empty 'checks' list.")
    return payload


def load_mutations(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    if isinstance(payload, list):
        mutations = payload
    else:
        mutations = payload.get("mutations")
    if not isinstance(mutations, list) or not mutations:
        raise ValueError(f"{path.as_posix()} must contain a non-empty mutation list.")
    return mutations


def _load_learning_review_manifest(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path.as_posix()} must contain a JSON object.")
    for key in ("benchmarkDrafts", "mutationDrafts", "policyDrafts"):
        entries = payload.get(key) or []
        if not isinstance(entries, list):
            raise ValueError(f"Learning review manifest field '{key}' must be a list.")
        seen_draft_ids: set[str] = set()
        for index, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                raise ValueError(
                    f"Learning review manifest field '{key}' entry {index} must be an object."
                )
            draft_id = entry.get("draftId")
            if not isinstance(draft_id, str) or not draft_id:
                raise ValueError(
                    f"Learning review manifest field '{key}' entry {index} is missing draftId."
                )
            if draft_id in seen_draft_ids:
                raise ValueError(
                    "Learning review manifest field "
                    f"'{key}' contains duplicate draftId '{draft_id}'."
                )
            seen_draft_ids.add(draft_id)
            decision = str(entry.get("decision") or "defer")
            if decision not in SUPPORTED_LEARNING_REVIEW_DECISIONS:
                raise ValueError(
                    "Learning review manifest entry "
                    f"'{draft_id}' uses unsupported decision '{decision}'."
                )
    return payload


def _index_learning_drafts(
    entries: list[dict[str, Any]],
    *,
    key: str,
    context: str,
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries, start=1):
        draft_id = entry.get(key)
        if not isinstance(draft_id, str) or not draft_id:
            raise ValueError(f"{context} entry {index} is missing '{key}'.")
        if draft_id in indexed:
            raise ValueError(f"{context} contains duplicate draft id '{draft_id}'.")
        indexed[draft_id] = entry
    return indexed


def _materialize_review_benchmark_checks(
    review_entry: dict[str, Any],
    *,
    draft_entry: dict[str, Any],
    draft_id: str,
    existing_check_ids: set[str],
) -> list[dict[str, Any]]:
    raw_checks = review_entry.get("checks")
    if raw_checks is None:
        raw_checks = _materialize_draft_suggested_benchmark_checks(
            draft_entry,
            draft_id=draft_id,
        )
    if not isinstance(raw_checks, list) or not raw_checks:
        raise ValueError(
            f"Accepted benchmark draft '{draft_id}' requires a non-empty 'checks' list."
        )

    materialized_checks: list[dict[str, Any]] = []
    for index, raw_check in enumerate(raw_checks, start=1):
        if not isinstance(raw_check, dict):
            raise ValueError(
                f"Accepted benchmark draft '{draft_id}' check {index} must be an object."
            )
        check = deepcopy(raw_check)
        check_type = str(check.get("type") or "")
        if check_type not in SUPPORTED_BENCHMARK_CHECK_TYPES:
            raise ValueError(
                "Accepted benchmark draft "
                f"'{draft_id}' uses unsupported benchmark check type '{check_type}'."
            )
        check_id = str(check.get("id") or f"{draft_id}-check-{index:02d}")
        if check_id in existing_check_ids:
            raise ValueError(
                "Accepted benchmark draft "
                f"'{draft_id}' would duplicate benchmark check id '{check_id}'."
            )
        check["id"] = check_id
        materialized_checks.append(check)
        existing_check_ids.add(check_id)
    return materialized_checks


def _materialize_draft_suggested_benchmark_checks(
    draft_entry: dict[str, Any],
    *,
    draft_id: str,
) -> list[dict[str, Any]]:
    fragment = draft_entry.get("fragment")
    suggested_checks = fragment.get("suggestedChecks") if isinstance(fragment, dict) else None
    if not isinstance(suggested_checks, list) or not suggested_checks:
        raise ValueError(
            "Accepted benchmark draft '"
            f"{draft_id}' requires reviewer-supplied 'checks' or supported draft "
            "'suggestedChecks'."
        )

    materialized_checks: list[dict[str, Any]] = []
    for index, suggested_check in enumerate(suggested_checks, start=1):
        if not isinstance(suggested_check, dict):
            raise ValueError(
                f"Accepted benchmark draft '{draft_id}' suggested check {index} must be an object."
            )
        suggested_kind = str(suggested_check.get("kind") or "")
        if suggested_kind != "episode_observation_guard":
            raise ValueError(
                "Accepted benchmark draft '"
                f"{draft_id}' uses unsupported suggested check kind '{suggested_kind}'."
            )
        materialized_checks.append(
            {
                "id": suggested_check.get("id") or f"{draft_id}-check-{index:02d}",
                "type": "episode_observation_guard",
                "sourceKinds": _non_empty_scalar_texts(
                    _as_list(suggested_check.get("sourceKinds"))
                ),
                "toolNames": _non_empty_scalar_texts(_as_list(suggested_check.get("toolNames"))),
                "terminalStatus": _first_non_empty_scalar([suggested_check.get("terminalStatus")]),
                "minMatchedRecordCount": int(suggested_check.get("minMatchedRecordCount", 1)),
                "weight": float(suggested_check.get("weight", 0.25)),
                "intent": suggested_check.get("intent"),
            }
        )
    return materialized_checks


def _materialize_review_mutation(
    review_entry: dict[str, Any],
    draft_entry: dict[str, Any],
    *,
    base_mutations_by_id: dict[str, dict[str, Any]],
    existing_mutation_ids: set[str],
    reviewer: str | None,
    reviewed_at: str | None,
) -> dict[str, Any]:
    draft_id = str(draft_entry["draftId"])
    draft_payload = draft_entry.get("entry") or {}
    explicit_mutation = review_entry.get("mutation")
    source_mutation_id = draft_payload.get("sourceMutationId")

    if explicit_mutation is not None:
        if not isinstance(explicit_mutation, dict):
            raise ValueError(
                f"Accepted mutation draft '{draft_id}' must use an object for 'mutation'."
            )
        mutation = deepcopy(explicit_mutation)
    else:
        if not isinstance(source_mutation_id, str) or not source_mutation_id:
            raise ValueError(
                "Accepted mutation draft "
                f"'{draft_id}' requires either 'mutation' or a source mutation id."
            )
        source_mutation = base_mutations_by_id.get(source_mutation_id)
        if source_mutation is None:
            raise ValueError(
                "Accepted mutation draft "
                f"'{draft_id}' references unknown source mutation '{source_mutation_id}'."
            )
        mutation = deepcopy(source_mutation)

    mutation_id = str(
        review_entry.get("mutationId") or draft_payload.get("id") or mutation.get("id") or draft_id
    )
    if mutation_id in existing_mutation_ids:
        raise ValueError(
            f"Accepted mutation draft '{draft_id}' would duplicate mutation id '{mutation_id}'."
        )
    mutation["id"] = mutation_id

    if "description" in review_entry:
        mutation["description"] = str(review_entry["description"])
    elif explicit_mutation is None and draft_payload.get("description"):
        mutation["description"] = str(draft_payload["description"])

    operations = mutation.get("operations")
    if not isinstance(operations, list) or not operations:
        raise ValueError(
            f"Accepted mutation draft '{draft_id}' must resolve to a mutation with operations."
        )

    mutation["learningImportMetadata"] = {
        key: value
        for key, value in {
            "draftId": draft_id,
            "sourceSeedId": draft_entry.get("sourceSeedId"),
            "sourceMutationId": source_mutation_id,
            "sourceCandidateId": draft_payload.get("sourceCandidateId"),
            "sourceEpisodeId": draft_payload.get("sourceEpisodeId"),
            "reviewer": reviewer,
            "reviewedAt": reviewed_at,
            "notes": review_entry.get("notes"),
        }.items()
        if value not in (None, "")
    }
    existing_mutation_ids.add(mutation_id)
    return mutation


def _load_or_initialize_reviewed_policies_payload(
    path: Path,
    *,
    experiment: dict[str, Any],
    policy_drafts_path: Path,
) -> dict[str, Any]:
    if path.exists():
        payload = load_json(path)
        if not isinstance(payload, dict):
            raise ValueError(f"{path.as_posix()} must contain a JSON object.")
    else:
        payload = {}

    policies = payload.get("policies") or []
    approved_learning_drafts = payload.get("approvedLearningDrafts") or []
    if not isinstance(policies, list):
        raise ValueError(f"{path.as_posix()} field 'policies' must be a list.")
    if not isinstance(approved_learning_drafts, list):
        raise ValueError(f"{path.as_posix()} field 'approvedLearningDrafts' must be a list.")

    return {
        "type": "AutoAgentReviewedPolicies",
        "mode": "manual_review_import",
        "source": {
            "experimentName": experiment["name"],
            "policyDraftsPath": policy_drafts_path.as_posix(),
        },
        "policies": list(policies),
        "approvedLearningDrafts": list(approved_learning_drafts),
    }


def _materialize_review_policy(
    review_entry: dict[str, Any],
    draft_entry: dict[str, Any],
    *,
    existing_policy_ids: set[str],
    reviewer: str | None,
    reviewed_at: str | None,
) -> dict[str, Any]:
    draft_id = str(draft_entry["draftId"])
    draft_payload = draft_entry.get("entry") or {}
    explicit_policy = review_entry.get("policy")

    if explicit_policy is not None:
        if not isinstance(explicit_policy, dict):
            raise ValueError(f"Accepted policy draft '{draft_id}' must use an object for 'policy'.")
        policy = deepcopy(explicit_policy)
    else:
        if not isinstance(draft_payload, dict) or not draft_payload:
            raise ValueError(f"Accepted policy draft '{draft_id}' must resolve to a policy object.")
        policy = deepcopy(draft_payload)

    policy_id = str(
        review_entry.get("policyId") or draft_payload.get("id") or policy.get("id") or draft_id
    )
    if policy_id in existing_policy_ids:
        raise ValueError(
            f"Accepted policy draft '{draft_id}' would duplicate policy id '{policy_id}'."
        )
    policy["id"] = policy_id

    if "description" in review_entry:
        policy["description"] = str(review_entry["description"])

    policy["learningImportMetadata"] = {
        key: value
        for key, value in {
            "draftId": draft_id,
            "sourcePolicyId": draft_entry.get("sourcePolicyId"),
            "reviewer": reviewer,
            "reviewedAt": reviewed_at,
            "notes": review_entry.get("notes"),
        }.items()
        if value not in (None, "")
    }
    existing_policy_ids.add(policy_id)
    return policy


def _default_evidence_policy() -> dict[str, Any]:
    return {
        "enabled": True,
        "runsDir": DOCS_AGENTS_DIR / "runs",
        "currentFiles": ["state.json", "patch-report.md", "test-report.md", "review-report.md"],
        "reportFiles": [
            "state.json",
            "patch-report.md",
            "test-report.md",
            "review-report.md",
            "autoagent-report.md",
        ],
        "includeCurrentArtifacts": True,
        "includeHookAudit": True,
        "includeChatHistory": False,
        "chatHistoryPaths": [],
        "includeTranscriptHistory": False,
        "transcriptHistoryPaths": [],
        "includeHandoffHistory": False,
        "handoffHistoryPaths": [],
        "includeVsCodeLogs": False,
        "vsCodeLogPaths": [],
        "externalLogSources": [],
        "maxRuns": 5,
        "maxRecordsPerFile": 200,
        "maxExternalLogLineLength": 400,
        "redactSensitive": True,
        "allowExternalPaths": False,
    }


def _resolve_evidence_policy(base_dir: Path, frontmatter: dict[str, Any]) -> dict[str, Any]:
    defaults = _default_evidence_policy()
    raw_policy = dict(frontmatter.get("evidencePolicy") or frontmatter.get("evidenceSources") or {})
    chat_history_paths = [
        resolved
        for resolved in (
            _resolve_path(base_dir, str(value))
            for value in _as_list(raw_policy.get("chatHistoryPaths"))
        )
        if resolved is not None
    ]
    transcript_history_paths = [
        resolved
        for resolved in (
            _resolve_path(base_dir, str(value))
            for value in _as_list(raw_policy.get("transcriptHistoryPaths"))
        )
        if resolved is not None
    ]
    handoff_history_paths = [
        resolved
        for resolved in (
            _resolve_path(base_dir, str(value))
            for value in _as_list(raw_policy.get("handoffHistoryPaths"))
        )
        if resolved is not None
    ]
    external_log_sources = _merge_external_log_sources(base_dir, raw_policy, defaults)

    return {
        "enabled": bool(raw_policy.get("enabled", defaults["enabled"])),
        "runsDir": _resolve_path(base_dir, raw_policy.get("runsDir")) or defaults["runsDir"],
        "currentFiles": [
            str(value)
            for value in _as_list(raw_policy.get("currentFiles") or defaults["currentFiles"])
        ],
        "reportFiles": [
            str(value)
            for value in _as_list(raw_policy.get("reportFiles") or defaults["reportFiles"])
        ],
        "includeCurrentArtifacts": bool(
            raw_policy.get("includeCurrentArtifacts", defaults["includeCurrentArtifacts"])
        ),
        "includeHookAudit": bool(raw_policy.get("includeHookAudit", defaults["includeHookAudit"])),
        "includeChatHistory": bool(
            raw_policy.get("includeChatHistory", defaults["includeChatHistory"])
        ),
        "chatHistoryPaths": chat_history_paths,
        "includeTranscriptHistory": bool(
            raw_policy.get(
                "includeTranscriptHistory",
                defaults["includeTranscriptHistory"],
            )
        ),
        "transcriptHistoryPaths": transcript_history_paths,
        "includeHandoffHistory": bool(
            raw_policy.get("includeHandoffHistory", defaults["includeHandoffHistory"])
        ),
        "handoffHistoryPaths": handoff_history_paths,
        "includeVsCodeLogs": bool(
            raw_policy.get("includeVsCodeLogs", defaults["includeVsCodeLogs"])
        ),
        "vsCodeLogPaths": [
            resolved
            for resolved in (
                _resolve_path(base_dir, str(value))
                for value in _as_list(raw_policy.get("vsCodeLogPaths"))
            )
            if resolved is not None
        ],
        "externalLogSources": external_log_sources,
        "maxRuns": int(raw_policy.get("maxRuns", defaults["maxRuns"])),
        "maxRecordsPerFile": int(
            raw_policy.get("maxRecordsPerFile", defaults["maxRecordsPerFile"])
        ),
        "maxExternalLogLineLength": int(
            raw_policy.get(
                "maxExternalLogLineLength",
                defaults["maxExternalLogLineLength"],
            )
        ),
        "redactSensitive": bool(raw_policy.get("redactSensitive", defaults["redactSensitive"])),
        "allowExternalPaths": bool(
            raw_policy.get("allowExternalPaths", defaults["allowExternalPaths"])
        ),
    }


def _serialize_evidence_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "enabled": policy["enabled"],
        "runsDir": policy["runsDir"].as_posix(),
        "currentFiles": list(policy["currentFiles"]),
        "reportFiles": list(policy["reportFiles"]),
        "includeCurrentArtifacts": policy["includeCurrentArtifacts"],
        "includeHookAudit": policy["includeHookAudit"],
        "includeChatHistory": policy["includeChatHistory"],
        "chatHistoryPaths": [path.as_posix() for path in policy["chatHistoryPaths"]],
        "includeTranscriptHistory": policy["includeTranscriptHistory"],
        "transcriptHistoryPaths": [path.as_posix() for path in policy["transcriptHistoryPaths"]],
        "includeHandoffHistory": policy["includeHandoffHistory"],
        "handoffHistoryPaths": [path.as_posix() for path in policy["handoffHistoryPaths"]],
        "includeVsCodeLogs": policy["includeVsCodeLogs"],
        "vsCodeLogPaths": [path.as_posix() for path in policy["vsCodeLogPaths"]],
        "externalLogSources": _serialize_external_log_sources(policy["externalLogSources"]),
        "maxRuns": policy["maxRuns"],
        "maxRecordsPerFile": policy["maxRecordsPerFile"],
        "maxExternalLogLineLength": policy["maxExternalLogLineLength"],
        "redactSensitive": policy["redactSensitive"],
        "allowExternalPaths": policy["allowExternalPaths"],
    }


def _default_reviewed_policy_runtime() -> dict[str, Any]:
    return {
        "enabled": False,
        "artifactPath": None,
        "preferredSequenceBonus": DEFAULT_REVIEWED_POLICY_PREFERRED_SEQUENCE_BONUS,
        "escalationPenalty": DEFAULT_REVIEWED_POLICY_ESCALATION_PENALTY,
    }


def _resolve_reviewed_policy_runtime(base_dir: Path, frontmatter: dict[str, Any]) -> dict[str, Any]:
    defaults = _default_reviewed_policy_runtime()
    raw_policy = (
        frontmatter.get("reviewedPolicyRuntime") or frontmatter.get("reviewedPolicies") or {}
    )
    if isinstance(raw_policy, bool):
        raw_policy = {"enabled": raw_policy}
    elif isinstance(raw_policy, str):
        raw_policy = {"enabled": True, "artifactPath": raw_policy}
    elif not isinstance(raw_policy, dict):
        raw_policy = {}

    raw_preferred_sequence_bonus = raw_policy.get("preferredSequenceBonus")
    if raw_preferred_sequence_bonus in (None, True, False):
        preferred_sequence_bonus = float(defaults["preferredSequenceBonus"])
    else:
        preferred_sequence_bonus = float(raw_preferred_sequence_bonus)

    raw_escalation_penalty = raw_policy.get("escalationPenalty")
    if raw_escalation_penalty in (None, True, False):
        escalation_penalty = float(defaults["escalationPenalty"])
    else:
        escalation_penalty = float(raw_escalation_penalty)

    if preferred_sequence_bonus < 0:
        raise ValueError("reviewedPolicyRuntime.preferredSequenceBonus must be non-negative.")
    if escalation_penalty < 0:
        raise ValueError("reviewedPolicyRuntime.escalationPenalty must be non-negative.")

    raw_artifact_path = raw_policy.get("artifactPath")
    artifact_path = (
        _resolve_path(base_dir, raw_artifact_path) if isinstance(raw_artifact_path, str) else None
    )

    return {
        "enabled": bool(raw_policy.get("enabled", defaults["enabled"])),
        "artifactPath": artifact_path,
        "preferredSequenceBonus": preferred_sequence_bonus,
        "escalationPenalty": escalation_penalty,
    }


def _serialize_reviewed_policy_runtime(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "enabled": policy["enabled"],
        "artifactPath": policy["artifactPath"].as_posix()
        if isinstance(policy.get("artifactPath"), Path)
        else None,
        "preferredSequenceBonus": round(float(policy["preferredSequenceBonus"]), 6),
        "escalationPenalty": round(float(policy["escalationPenalty"]), 6),
    }


def _serialize_reviewed_policy_runtime_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "enabled": bool(state.get("enabled")),
        "status": str(state.get("status") or "disabled"),
        "artifactPath": state.get("artifactPath"),
        "artifactFound": bool(state.get("artifactFound")),
        "policyCount": int(state.get("policyCount") or 0),
        "activePolicyCount": int(state.get("activePolicyCount") or 0),
        "approvedLearningDraftCount": int(state.get("approvedLearningDraftCount") or 0),
    }


def _normalize_named_count_map(raw_counts: Any) -> dict[str, int]:
    if not isinstance(raw_counts, dict):
        return {}

    normalized: dict[str, int] = {}
    for key in sorted(raw_counts):
        if not isinstance(key, str):
            continue
        name = key.strip()
        if not name:
            continue
        value = raw_counts.get(key)
        try:
            count = int(value or 0)
        except (TypeError, ValueError):
            continue
        if count > 0:
            normalized[name] = count
    return normalized


def _aggregate_blocked_factors(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        rationale = entry.get("decisionRationale") or {}
        if not isinstance(rationale, dict):
            continue
        blocked_by_factors = rationale.get("blockedByFactors") or []
        if not isinstance(blocked_by_factors, list):
            continue
        seen_factors: set[str] = set()
        for factor in blocked_by_factors:
            if not isinstance(factor, str):
                continue
            normalized_factor = factor.strip()
            if not normalized_factor or normalized_factor in seen_factors:
                continue
            seen_factors.add(normalized_factor)
            counts[normalized_factor] = counts.get(normalized_factor, 0) + 1
    return _normalize_named_count_map(counts)


def _load_reviewed_policy_runtime_state(
    experiment: dict[str, Any], run_root: Path
) -> dict[str, Any]:
    config = experiment["reviewedPolicyRuntime"]
    artifact_path = config.get("artifactPath") or (run_root / "reviewed-policies.json")
    state = {
        "enabled": bool(config["enabled"]),
        "status": "disabled",
        "artifactPath": artifact_path.as_posix(),
        "artifactFound": False,
        "policyCount": 0,
        "activePolicyCount": 0,
        "approvedLearningDraftCount": 0,
        "policies": [],
    }
    if not config["enabled"]:
        return state
    if not artifact_path.exists():
        state["status"] = "artifact_missing"
        return state

    payload = load_json(artifact_path)
    if not isinstance(payload, dict):
        raise ValueError(f"{artifact_path.as_posix()} must contain a JSON object.")
    raw_policies = payload.get("policies") or []
    approved_learning_drafts = payload.get("approvedLearningDrafts") or []
    if not isinstance(raw_policies, list):
        raise ValueError(f"{artifact_path.as_posix()} field 'policies' must be a list.")
    if not isinstance(approved_learning_drafts, list):
        raise ValueError(
            f"{artifact_path.as_posix()} field 'approvedLearningDrafts' must be a list."
        )

    policies = [
        deepcopy(policy)
        for policy in raw_policies
        if isinstance(policy, dict)
        and isinstance(policy.get("id"), str)
        and str(policy.get("id") or "").strip()
    ]
    state.update(
        {
            "status": "ready" if policies else "ready_empty",
            "artifactFound": True,
            "policyCount": len(raw_policies),
            "activePolicyCount": len(policies),
            "approvedLearningDraftCount": len(approved_learning_drafts),
            "policies": policies,
        }
    )
    return state


def _serialize_learning_promotion_audit_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": str(state.get("status") or "artifact_missing"),
        "artifactPath": state.get("artifactPath"),
        "artifactFound": bool(state.get("artifactFound")),
        "promotionSourceMode": state.get("promotionSourceMode"),
        "reviewedBenchmarkDraftCount": int(state.get("reviewedBenchmarkDraftCount") or 0),
        "acceptedBenchmarkDraftCount": int(state.get("acceptedBenchmarkDraftCount") or 0),
        "rejectedBenchmarkDraftCount": int(state.get("rejectedBenchmarkDraftCount") or 0),
        "deferredBenchmarkDraftCount": int(state.get("deferredBenchmarkDraftCount") or 0),
        "reviewedMutationDraftCount": int(state.get("reviewedMutationDraftCount") or 0),
        "acceptedMutationDraftCount": int(state.get("acceptedMutationDraftCount") or 0),
        "rejectedMutationDraftCount": int(state.get("rejectedMutationDraftCount") or 0),
        "deferredMutationDraftCount": int(state.get("deferredMutationDraftCount") or 0),
        "reviewedPolicyDraftCount": int(state.get("reviewedPolicyDraftCount") or 0),
        "acceptedPolicyDraftCount": int(state.get("acceptedPolicyDraftCount") or 0),
        "rejectedPolicyDraftCount": int(state.get("rejectedPolicyDraftCount") or 0),
        "deferredPolicyDraftCount": int(state.get("deferredPolicyDraftCount") or 0),
        "reviewerOverrideCount": int(state.get("reviewerOverrideCount") or 0),
        "benchmarkReviewerOverrideCount": int(
            state.get("benchmarkReviewerOverrideCount") or 0
        ),
        "mutationReviewerOverrideCount": int(state.get("mutationReviewerOverrideCount") or 0),
        "policyReviewerOverrideCount": int(state.get("policyReviewerOverrideCount") or 0),
        "blockedFactorCounts": _normalize_named_count_map(state.get("blockedFactorCounts")),
        "benchmarkBlockedFactorCounts": _normalize_named_count_map(
            state.get("benchmarkBlockedFactorCounts")
        ),
        "mutationBlockedFactorCounts": _normalize_named_count_map(
            state.get("mutationBlockedFactorCounts")
        ),
        "policyBlockedFactorCounts": _normalize_named_count_map(
            state.get("policyBlockedFactorCounts")
        ),
    }


def _load_learning_promotion_audit_state(run_root: Path) -> dict[str, Any]:
    artifact_path = run_root / "learning-promotion-audit.json"
    state = {
        "status": "artifact_missing",
        "artifactPath": artifact_path.as_posix(),
        "artifactFound": False,
        "promotionSourceMode": None,
        "reviewedBenchmarkDraftCount": 0,
        "acceptedBenchmarkDraftCount": 0,
        "rejectedBenchmarkDraftCount": 0,
        "deferredBenchmarkDraftCount": 0,
        "reviewedMutationDraftCount": 0,
        "acceptedMutationDraftCount": 0,
        "rejectedMutationDraftCount": 0,
        "deferredMutationDraftCount": 0,
        "reviewedPolicyDraftCount": 0,
        "acceptedPolicyDraftCount": 0,
        "rejectedPolicyDraftCount": 0,
        "deferredPolicyDraftCount": 0,
        "reviewerOverrideCount": 0,
        "benchmarkReviewerOverrideCount": 0,
        "mutationReviewerOverrideCount": 0,
        "policyReviewerOverrideCount": 0,
        "blockedFactorCounts": {},
        "benchmarkBlockedFactorCounts": {},
        "mutationBlockedFactorCounts": {},
        "policyBlockedFactorCounts": {},
    }
    if not artifact_path.exists():
        return state

    payload = load_json(artifact_path)
    if not isinstance(payload, dict):
        raise ValueError(f"{artifact_path.as_posix()} must contain a JSON object.")
    if payload.get("type") != "AutoAgentLearningPromotionAudit":
        raise ValueError(f"Unsupported promotion audit type in {artifact_path.as_posix()}.")

    summary = payload.get("summary") or {}
    decisions = payload.get("decisions") or {}
    if not isinstance(summary, dict):
        raise ValueError(f"{artifact_path.as_posix()} field 'summary' must be an object.")
    if not isinstance(decisions, dict):
        raise ValueError(f"{artifact_path.as_posix()} field 'decisions' must be an object.")

    def _decision_entries(key: str) -> list[dict[str, Any]]:
        raw_entries = decisions.get(key) or []
        if not isinstance(raw_entries, list):
            raise ValueError(f"{artifact_path.as_posix()} field 'decisions.{key}' must be a list.")
        return [entry for entry in raw_entries if isinstance(entry, dict)]

    def _override_count(entries: list[dict[str, Any]]) -> int:
        return sum(1 for entry in entries if bool(entry.get("reviewerOverride")))

    benchmark_decisions = _decision_entries("benchmarkDrafts")
    mutation_decisions = _decision_entries("mutationDrafts")
    policy_decisions = _decision_entries("policyDrafts")

    reviewed_benchmark_draft_count = int(
        summary.get("reviewedBenchmarkDraftCount") or len(benchmark_decisions)
    )
    reviewed_mutation_draft_count = int(
        summary.get("reviewedMutationDraftCount") or len(mutation_decisions)
    )
    reviewed_policy_draft_count = int(
        summary.get("reviewedPolicyDraftCount") or len(policy_decisions)
    )
    benchmark_blocked_factor_counts = _aggregate_blocked_factors(benchmark_decisions)
    mutation_blocked_factor_counts = _aggregate_blocked_factors(mutation_decisions)
    policy_blocked_factor_counts = _aggregate_blocked_factors(policy_decisions)
    blocked_factor_counts: dict[str, int] = {}
    for counts in (
        benchmark_blocked_factor_counts,
        mutation_blocked_factor_counts,
        policy_blocked_factor_counts,
    ):
        for factor_name, factor_count in counts.items():
            blocked_factor_counts[factor_name] = blocked_factor_counts.get(factor_name, 0) + factor_count
    blocked_factor_counts = _normalize_named_count_map(blocked_factor_counts)

    state.update(
        {
            "status": (
                "ready"
                if any(
                    (
                        reviewed_benchmark_draft_count,
                        reviewed_mutation_draft_count,
                        reviewed_policy_draft_count,
                    )
                )
                else "ready_empty"
            ),
            "artifactFound": True,
            "promotionSourceMode": payload.get("promotionSourceMode"),
            "reviewedBenchmarkDraftCount": reviewed_benchmark_draft_count,
            "acceptedBenchmarkDraftCount": int(summary.get("acceptedBenchmarkDraftCount") or 0),
            "rejectedBenchmarkDraftCount": int(summary.get("rejectedBenchmarkDraftCount") or 0),
            "deferredBenchmarkDraftCount": int(summary.get("deferredBenchmarkDraftCount") or 0),
            "reviewedMutationDraftCount": reviewed_mutation_draft_count,
            "acceptedMutationDraftCount": int(summary.get("acceptedMutationDraftCount") or 0),
            "rejectedMutationDraftCount": int(summary.get("rejectedMutationDraftCount") or 0),
            "deferredMutationDraftCount": int(summary.get("deferredMutationDraftCount") or 0),
            "reviewedPolicyDraftCount": reviewed_policy_draft_count,
            "acceptedPolicyDraftCount": int(summary.get("acceptedPolicyDraftCount") or 0),
            "rejectedPolicyDraftCount": int(summary.get("rejectedPolicyDraftCount") or 0),
            "deferredPolicyDraftCount": int(summary.get("deferredPolicyDraftCount") or 0),
            "reviewerOverrideCount": (
                _override_count(benchmark_decisions)
                + _override_count(mutation_decisions)
                + _override_count(policy_decisions)
            ),
            "benchmarkReviewerOverrideCount": _override_count(benchmark_decisions),
            "mutationReviewerOverrideCount": _override_count(mutation_decisions),
            "policyReviewerOverrideCount": _override_count(policy_decisions),
            "blockedFactorCounts": blocked_factor_counts,
            "benchmarkBlockedFactorCounts": benchmark_blocked_factor_counts,
            "mutationBlockedFactorCounts": mutation_blocked_factor_counts,
            "policyBlockedFactorCounts": policy_blocked_factor_counts,
        }
    )
    return state


def _extract_json_block(raw: str) -> dict[str, Any] | None:
    match = JSON_BLOCK_RE.search(raw)
    if not match:
        return None
    payload = json.loads(match.group("payload"))
    return payload if isinstance(payload, dict) else None


def _normalize_path_text(value: str, allow_external_paths: bool) -> str:
    normalized = value.replace(ROOT.as_posix(), "<repo>").replace(str(ROOT), "<repo>")
    normalized = normalized.replace("\\", "/")
    if allow_external_paths:
        return normalized

    def replace_match(match: re.Match[str]) -> str:
        raw_path = match.group(0)
        try:
            relative = Path(raw_path).resolve().relative_to(ROOT.resolve())
        except (OSError, ValueError):
            return "[external-path]"
        return f"<repo>/{relative.as_posix()}"

    normalized = WINDOWS_ABSOLUTE_PATH_RE.sub(replace_match, normalized)
    return POSIX_ABSOLUTE_PATH_RE.sub(replace_match, normalized)


def _sanitize_text(value: str, allow_external_paths: bool) -> str:
    sanitized = re.sub(
        r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|key)=\S+",
        r"\1=[REDACTED]",
        value,
    )
    sanitized = re.sub(r"(?i)\bAuthorization:\s*\S+", "Authorization: [REDACTED]", sanitized)
    sanitized = re.sub(r"(?i)\bBearer\s+\S+", "Bearer [REDACTED]", sanitized)
    return _normalize_path_text(sanitized, allow_external_paths)


def _sanitize_value(value: Any, redact_sensitive: bool, allow_external_paths: bool) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _sanitize_value(inner, redact_sensitive, allow_external_paths)
            for key, inner in value.items()
        }
    if isinstance(value, list):
        return [_sanitize_value(item, redact_sensitive, allow_external_paths) for item in value]
    if isinstance(value, str):
        if redact_sensitive:
            return _sanitize_text(value, allow_external_paths)
        return _normalize_path_text(value, allow_external_paths)
    return value


def _safe_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _collect_json_artifact_record(
    path: Path,
    run_id: str,
    source_scope: str,
    policy: dict[str, Any],
) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = load_json(path)
    if not isinstance(payload, dict):
        return None
    sanitized = _sanitize_value(payload, policy["redactSensitive"], policy["allowExternalPaths"])
    return {
        "sourceKind": "run_state" if path.name == "state.json" else "json_artifact",
        "sourceScope": source_scope,
        "runId": run_id,
        "file": _safe_path(path),
        "recordType": str(sanitized.get("type") or path.name),
        "status": sanitized.get("status") or sanitized.get("phase"),
        "payload": sanitized,
    }


def _collect_markdown_artifact_record(
    path: Path,
    run_id: str,
    source_scope: str,
    policy: dict[str, Any],
) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = _extract_json_block(path.read_text(encoding="utf-8"))
    if payload is None:
        return None
    sanitized = _sanitize_value(payload, policy["redactSensitive"], policy["allowExternalPaths"])
    return {
        "sourceKind": "run_report",
        "sourceScope": source_scope,
        "runId": run_id,
        "file": _safe_path(path),
        "recordType": str(sanitized.get("type") or path.name),
        "status": sanitized.get("status"),
        "payload": sanitized,
    }


def _session_record_status(payload: dict[str, Any]) -> str | None:
    raw_status = payload.get("status")
    if raw_status is not None and str(raw_status).strip():
        return str(raw_status)

    if str(payload.get("decision") or "").lower() == "deny":
        return "warning"

    audit = payload.get("audit")
    if isinstance(audit, dict):
        try:
            error_count = int(audit.get("errors") or 0)
        except (TypeError, ValueError):
            error_count = 0
        try:
            deny_count = int(audit.get("denies") or 0)
        except (TypeError, ValueError):
            deny_count = 0
        try:
            total_events = int(audit.get("totalEvents") or 0)
        except (TypeError, ValueError):
            total_events = 0
        if error_count > 0:
            return "error"
        if deny_count > 0:
            return "warning"
        if total_events > 0:
            return "success"

    if payload.get("success") is True:
        return "success"

    hint_text = " ".join(
        str(value)
        for value in [
            payload.get("event"),
            payload.get("message"),
            payload.get("summary"),
            payload.get("content"),
            payload.get("result"),
            payload.get("outcome"),
        ]
        if value is not None and str(value)
    )
    if not hint_text:
        return None

    derived_status = _log_status(hint_text)
    return derived_status if derived_status != "info" else None


def _collect_hook_audit_records(
    run_dir: Path,
    run_id: str,
    policy: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []
    files_seen: list[str] = []
    if not policy["includeHookAudit"]:
        return records, parse_errors, files_seen

    hook_dir = run_dir / "hook-audit"
    if not hook_dir.exists():
        return records, parse_errors, files_seen

    for jsonl_path in sorted(
        path for path in hook_dir.glob("*.jsonl") if path.name != "session.jsonl"
    ):
        files_seen.append(_safe_path(jsonl_path))
        for line_number, raw_line in enumerate(
            jsonl_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not raw_line.strip():
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError as error:
                parse_errors.append(
                    {
                        "runId": run_id,
                        "file": _safe_path(jsonl_path),
                        "line": line_number,
                        "error": str(error),
                    }
                )
                continue
            sanitized = _sanitize_value(
                payload,
                policy["redactSensitive"],
                policy["allowExternalPaths"],
            )
            if not isinstance(sanitized, dict):
                continue
            records.append(
                {
                    "sourceKind": "hook_event",
                    "sourceScope": "run_snapshot",
                    "runId": run_id,
                    "file": _safe_path(jsonl_path),
                    "recordType": str(sanitized.get("event") or jsonl_path.name),
                    "status": sanitized.get("status"),
                    "toolName": sanitized.get("toolName"),
                    "payload": sanitized,
                }
            )
            if len(records) >= policy["maxRecordsPerFile"]:
                break
    return records, parse_errors, files_seen


def _collect_session_audit_records(
    run_dir: Path,
    run_id: str,
    policy: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []
    files_seen: list[str] = []
    if not policy["includeHookAudit"]:
        return records, parse_errors, files_seen

    hook_dir = run_dir / "hook-audit"
    if not hook_dir.exists():
        return records, parse_errors, files_seen

    session_jsonl_path = hook_dir / "session.jsonl"
    if session_jsonl_path.exists():
        files_seen.append(_safe_path(session_jsonl_path))
        source_count = 0
        for line_number, raw_line in enumerate(
            session_jsonl_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not raw_line.strip():
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError as error:
                parse_errors.append(
                    {
                        "runId": run_id,
                        "file": _safe_path(session_jsonl_path),
                        "line": line_number,
                        "error": str(error),
                    }
                )
                continue
            sanitized = _sanitize_value(
                payload,
                policy["redactSensitive"],
                policy["allowExternalPaths"],
            )
            if not isinstance(sanitized, dict):
                continue
            candidate_ids = _transcript_candidate_ids(sanitized)
            records.append(
                {
                    "sourceKind": "session_event",
                    "sourceScope": "run_snapshot",
                    "runId": run_id,
                    "file": _safe_path(session_jsonl_path),
                    "recordType": str(
                        sanitized.get("event") or sanitized.get("type") or session_jsonl_path.name
                    ),
                    "status": _session_record_status(sanitized),
                    "candidateIds": candidate_ids,
                    "toolName": sanitized.get("toolName"),
                    "payload": sanitized,
                }
            )
            source_count += 1
            if source_count >= policy["maxRecordsPerFile"]:
                break

    summary_path = hook_dir / "session-summary.json"
    if summary_path.exists():
        files_seen.append(_safe_path(summary_path))
        try:
            payload = load_json(summary_path)
        except (OSError, json.JSONDecodeError) as error:
            parse_errors.append(
                {
                    "runId": run_id,
                    "file": _safe_path(summary_path),
                    "line": 1,
                    "error": str(error),
                }
            )
        else:
            sanitized = _sanitize_value(
                payload,
                policy["redactSensitive"],
                policy["allowExternalPaths"],
            )
            if isinstance(sanitized, dict):
                records.append(
                    {
                        "sourceKind": "session_summary",
                        "sourceScope": "run_snapshot",
                        "runId": run_id,
                        "file": _safe_path(summary_path),
                        "recordType": str(sanitized.get("event") or summary_path.name),
                        "status": _session_record_status(sanitized),
                        "payload": sanitized,
                    }
                )

    return records, parse_errors, files_seen


def _collect_external_log_records(
    policy: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []

    for source in policy["externalLogSources"]:
        source_path = source["path"]
        if not source_path.exists():
            if not source["optional"]:
                parse_errors.append(
                    {
                        "runId": f"external:{source['id']}",
                        "file": source_path.as_posix(),
                        "line": 0,
                        "error": "External log source not found.",
                    }
                )
            continue

        source_count = 0
        if source["format"] in {"json", "jsonl"}:
            record_kind = _external_log_record_kind(source["kind"])
            raw_entries: list[tuple[int, Any]] = []
            if source["format"] == "jsonl":
                for line_number, raw_line in enumerate(
                    source_path.read_text(encoding="utf-8").splitlines(),
                    start=1,
                ):
                    if not raw_line.strip():
                        continue
                    try:
                        payload = json.loads(raw_line)
                    except json.JSONDecodeError as error:
                        parse_errors.append(
                            {
                                "runId": f"external:{source['id']}",
                                "file": source_path.as_posix(),
                                "line": line_number,
                                "error": str(error),
                            }
                        )
                        continue
                    raw_entries.append((line_number, payload))
            else:
                try:
                    payload = json.loads(source_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as error:
                    parse_errors.append(
                        {
                            "runId": f"external:{source['id']}",
                            "file": source_path.as_posix(),
                            "line": 0,
                            "error": str(error),
                        }
                    )
                    payload = None
                if payload is not None:
                    raw_entries.extend(enumerate(_flatten_external_json_payloads(payload), start=1))

            for _entry_number, payload in raw_entries:
                sanitized = _sanitize_value(
                    payload,
                    policy["redactSensitive"],
                    policy["allowExternalPaths"],
                )
                is_mapping = isinstance(sanitized, dict)
                role = _transcript_role(sanitized) if is_mapping else None
                tool_name = _transcript_tool_name(sanitized) if is_mapping else None
                candidate_ids = (
                    _transcript_candidate_ids(sanitized)
                    if record_kind in {"transcript_event", "handoff_event"} and is_mapping
                    else []
                )
                lineage_candidate_ids = (
                    _transcript_lineage_candidate_ids(sanitized)
                    if record_kind in {"transcript_event", "handoff_event"} and is_mapping
                    else []
                )
                handoff_refs = (
                    _transcript_handoff_refs(sanitized)
                    if record_kind in {"transcript_event", "handoff_event"} and is_mapping
                    else []
                )
                raw_transcript_text = (
                    _transcript_payload_text(sanitized) if is_mapping else str(sanitized).strip()
                )
                transcript_text = None
                if record_kind in {"transcript_event", "handoff_event"} and raw_transcript_text:
                    transcript_text = _truncate_text(
                        raw_transcript_text,
                        source["maxLineLength"],
                    )
                if record_kind in {"transcript_event", "handoff_event"}:
                    status = _transcript_record_status(sanitized) if is_mapping else None
                    if status is None and raw_transcript_text:
                        derived_status = _log_status(raw_transcript_text)
                        status = derived_status if derived_status != "info" else None
                else:
                    status = sanitized.get("status") if is_mapping else None
                    if status is None and raw_transcript_text:
                        derived_status = _log_status(raw_transcript_text)
                        status = derived_status if derived_status != "info" else None
                records.append(
                    {
                        "sourceKind": record_kind,
                        "sourceScope": source["kind"],
                        "runId": f"external:{source['id']}",
                        "file": source_path.as_posix(),
                        "recordType": (
                            str(
                                sanitized.get("event")
                                or sanitized.get("type")
                                or role
                                or source["kind"]
                            )
                            if is_mapping
                            else source["kind"]
                        ),
                        "status": status,
                        "candidateIds": candidate_ids,
                        "lineageCandidateIds": lineage_candidate_ids,
                        "handoffRefs": handoff_refs,
                        "sourceId": source["id"],
                        "role": role,
                        "toolName": tool_name,
                        "transcriptText": transcript_text,
                        "payload": sanitized,
                    }
                )
                source_count += 1
                if source_count >= source["maxRecords"]:
                    break
        else:
            for line_number, raw_line in enumerate(
                source_path.read_text(encoding="utf-8").splitlines(),
                start=1,
            ):
                stripped = raw_line.strip()
                if not stripped:
                    continue
                include_patterns = source["includeLinePatterns"]
                if include_patterns and not any(
                    _pattern_matches(stripped, pattern) for pattern in include_patterns
                ):
                    continue
                if any(
                    _pattern_matches(stripped, pattern) for pattern in source["excludeLinePatterns"]
                ):
                    continue
                sanitized = _sanitize_value(
                    stripped,
                    policy["redactSensitive"],
                    policy["allowExternalPaths"],
                )
                records.append(
                    {
                        "sourceKind": "external_log",
                        "sourceScope": source["kind"],
                        "runId": f"external:{source['id']}",
                        "file": source_path.as_posix(),
                        "recordType": source["kind"],
                        "status": _log_status(stripped),
                        "sourceId": source["id"],
                        "payload": {
                            "lineNumber": line_number,
                            "message": _truncate_text(str(sanitized), source["maxLineLength"]),
                            "matchedPatterns": list(include_patterns),
                        },
                    }
                )
                source_count += 1
                if source_count >= source["maxRecords"]:
                    break

        source_summaries.append(
            {
                "id": source["id"],
                "kind": source["kind"],
                "path": source_path.as_posix(),
                "recordCount": source_count,
                "recordKind": (
                    _external_log_record_kind(source["kind"])
                    if source["format"] in {"json", "jsonl"}
                    else "external_log"
                ),
            }
        )

    return records, parse_errors, source_summaries


def build_evidence_dataset(policy: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []
    discovered_runs: set[str] = set()
    current_artifacts: list[str] = []
    hook_audit_files: list[str] = []
    session_artifacts: list[str] = []
    external_log_sources: list[dict[str, Any]] = []
    session_record_count = 0
    transcript_record_count = 0

    if policy["includeCurrentArtifacts"]:
        current_run_root = _current_run_root()
        current_run_id = current_run_root.name if current_run_root is not None else "current"
        for name in policy["currentFiles"]:
            path = DOCS_AGENTS_DIR / name
            record = (
                _collect_json_artifact_record(path, current_run_id, "current_artifact", policy)
                if path.suffix == ".json"
                else _collect_markdown_artifact_record(
                    path,
                    current_run_id,
                    "current_artifact",
                    policy,
                )
            )
            if record is not None:
                records.append(record)
                current_artifacts.append(record["file"])

    runs_dir = policy["runsDir"]
    run_dirs = (
        sorted(
            [path for path in runs_dir.iterdir() if path.is_dir()],
            key=lambda item: item.name,
            reverse=True,
        )
        if runs_dir.exists()
        else []
    )
    for run_dir in run_dirs[: policy["maxRuns"]]:
        run_id = run_dir.name
        discovered_runs.add(run_id)
        for name in policy["reportFiles"]:
            path = run_dir / name
            record = (
                _collect_json_artifact_record(path, run_id, "run_snapshot", policy)
                if path.suffix == ".json"
                else _collect_markdown_artifact_record(path, run_id, "run_snapshot", policy)
            )
            if record is not None:
                records.append(record)
        hook_records, hook_parse_errors, hook_files = _collect_hook_audit_records(
            run_dir,
            run_id,
            policy,
        )
        records.extend(hook_records)
        parse_errors.extend(hook_parse_errors)
        hook_audit_files.extend(hook_files)
        session_records, session_parse_errors, session_files = _collect_session_audit_records(
            run_dir,
            run_id,
            policy,
        )
        records.extend(session_records)
        parse_errors.extend(session_parse_errors)
        session_artifacts.extend(session_files)
        session_record_count += len(session_records)

    external_records, external_parse_errors, external_log_sources = _collect_external_log_records(
        policy
    )
    records.extend(external_records)
    parse_errors.extend(external_parse_errors)
    transcript_record_count = sum(
        1 for record in external_records if record.get("sourceKind") == "transcript_event"
    )
    handoff_record_count = sum(
        1 for record in external_records if record.get("sourceKind") == "handoff_event"
    )
    transcript_sources = [
        summary
        for summary in external_log_sources
        if summary.get("recordKind") == "transcript_event"
    ]
    handoff_sources = [
        summary for summary in external_log_sources if summary.get("recordKind") == "handoff_event"
    ]

    records_by_kind: dict[str, int] = {}
    statuses: dict[str, int] = {}
    report_failures = 0
    tool_errors = 0
    for record in records:
        kind = record["sourceKind"]
        records_by_kind[kind] = records_by_kind.get(kind, 0) + 1
        status = record.get("status")
        if status is not None:
            status_key = str(status)
            statuses[status_key] = statuses.get(status_key, 0) + 1
            if kind in {"run_report", "json_artifact", "run_state"} and status_key.upper() in {
                "FAIL",
                "BLOCKED",
                "ERROR",
            }:
                report_failures += 1
            if kind == "hook_event" and status_key.lower() == "error":
                tool_errors += 1

    return {
        "type": "AutoAgentEvidenceDataset",
        "policy": _serialize_evidence_policy(policy),
        "sources": {
            "currentArtifacts": current_artifacts,
            "runSnapshots": sorted(discovered_runs),
            "hookAuditFiles": hook_audit_files,
            "sessionArtifacts": session_artifacts,
            "externalLogs": external_log_sources,
            "transcriptSources": transcript_sources,
            "handoffSources": handoff_sources,
        },
        "records": records,
        "summary": {
            "recordCount": len(records),
            "runCount": len(discovered_runs),
            "recordsByKind": records_by_kind,
            "statuses": statuses,
            "reportFailureCount": report_failures,
            "toolErrorCount": tool_errors,
            "parseErrorCount": len(parse_errors),
            "sessionRecordCount": session_record_count,
            "transcriptRecordCount": transcript_record_count,
            "handoffRecordCount": handoff_record_count,
            "externalLogRecordCount": len(external_records),
            "externalSourceCount": len(external_log_sources),
        },
        "parseErrors": parse_errors,
    }


def _replace_section(section_title: str, body: str, update: str) -> str:
    pattern = re.compile(
        rf"(?ms)(^##\s+{re.escape(section_title)}\s*$)(.*?)(?=^##\s+|\Z)",
    )
    match = pattern.search(body)
    if not match:
        addition = f"\n\n## {section_title}\n\n{update.strip()}"
        return (body.rstrip() + addition).strip()
    replacement = f"{match.group(1)}\n\n{update.strip()}\n"
    return (body[: match.start()] + replacement + body[match.end() :]).strip()


def _append_bullet(section_title: str, bullet_text: str, body: str) -> str:
    pattern = re.compile(
        rf"(?ms)(^##\s+{re.escape(section_title)}\s*$)(.*?)(?=^##\s+|\Z)",
    )
    match = pattern.search(body)
    if not match:
        addition = f"\n\n## {section_title}\n\n- {bullet_text}"
        return (body.rstrip() + addition).strip()
    section_body = match.group(2).strip()
    bullet_line = f"- {bullet_text}"
    if bullet_line in section_body.splitlines():
        return body
    updated_section = section_body.rstrip()
    if updated_section:
        updated_section = f"{updated_section}\n{bullet_line}"
    else:
        updated_section = bullet_line
    replacement = f"{match.group(1)}\n\n{updated_section}\n"
    return (body[: match.start()] + replacement + body[match.end() :]).strip()


def apply_mutation(
    documents: dict[str, dict[str, Any]],
    mutation: dict[str, Any],
    default_target_id: str,
) -> tuple[dict[str, dict[str, Any]], bool, list[str]]:
    updated_documents = deepcopy(documents)
    changed = False
    touched_targets: set[str] = set()
    for operation in mutation.get("operations", []):
        op_type = operation.get("type")
        target_id = str(
            operation.get("targetId") or operation.get("documentId") or default_target_id
        )
        document = _document_or_error(
            updated_documents,
            target_id,
            f"Mutation '{mutation.get('id') or 'candidate'}'",
        )
        updated_frontmatter = deepcopy(document["frontmatter"])
        updated_body = document["body"]
        local_change = False
        if op_type == "replace_text":
            target = operation.get("target", "body")
            old = operation.get("old", "")
            new = operation.get("new", "")
            if target == "body":
                replaced = updated_body.replace(old, new)
                if replaced != updated_body:
                    updated_body = replaced
                    local_change = True
            elif isinstance(target, str) and target.startswith("frontmatter."):
                key = target.split(".", 1)[1]
                current_value = str(updated_frontmatter.get(key, ""))
                replaced = current_value.replace(old, new)
                if replaced != current_value:
                    updated_frontmatter[key] = replaced
                    local_change = True
        elif op_type == "ensure_contains":
            target = operation.get("target", "body")
            value = operation.get("value", "")
            if target == "body":
                if value not in updated_body:
                    updated_body = f"{updated_body.rstrip()}\n\n{value}".strip()
                    local_change = True
            elif isinstance(target, str) and target.startswith("frontmatter."):
                key = target.split(".", 1)[1]
                current_value = str(updated_frontmatter.get(key, ""))
                if value not in current_value:
                    joined = f"{current_value.rstrip()} {value}".strip()
                    updated_frontmatter[key] = joined
                    local_change = True
        elif op_type == "ensure_bullet":
            section = operation.get("section") or "Responsibilities"
            value = operation.get("value", "")
            replaced = _append_bullet(section, value, updated_body)
            if replaced != updated_body:
                updated_body = replaced
                local_change = True
        elif op_type == "replace_section":
            section = operation.get("section") or "Responsibilities"
            value = operation.get("value", "")
            replaced = _replace_section(section, updated_body, value)
            if replaced != updated_body:
                updated_body = replaced
                local_change = True
        elif op_type == "merge_list":
            key = operation.get("key")
            values = [str(value) for value in _as_list(operation.get("values"))]
            current_values = [str(value) for value in _as_list(updated_frontmatter.get(key))]
            merged = list(current_values)
            for value in values:
                if value not in merged:
                    merged.append(value)
                    local_change = True
            updated_frontmatter[key] = merged
        elif op_type == "set_value":
            key = operation.get("key")
            value = operation.get("value")
            if updated_frontmatter.get(key) != value:
                updated_frontmatter[key] = value
                local_change = True
        if local_change:
            document["frontmatter"] = updated_frontmatter
            document["body"] = updated_body
            changed = True
            touched_targets.add(target_id)
    return updated_documents, changed, sorted(touched_targets)


def _document_complexity(frontmatter: dict[str, Any], body: str) -> dict[str, int]:
    tools = len(_as_list(frontmatter.get("tools")))
    mcp_servers = len(_as_list(frontmatter.get("mcpServers")))
    body_chars = len(body.strip())
    return {
        "bodyChars": body_chars,
        "toolCount": tools,
        "mcpServerCount": mcp_servers,
        "score": body_chars + (tools * 25) + (mcp_servers * 40),
    }


def _complexity(documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
    per_target: dict[str, dict[str, int]] = {}
    body_chars = 0
    tool_count = 0
    mcp_server_count = 0
    for target_id, document in documents.items():
        metrics = _document_complexity(document["frontmatter"], document["body"])
        per_target[target_id] = metrics
        body_chars += metrics["bodyChars"]
        tool_count += metrics["toolCount"]
        mcp_server_count += metrics["mcpServerCount"]
    file_count = len(documents)
    return {
        "bodyChars": body_chars,
        "toolCount": tool_count,
        "mcpServerCount": mcp_server_count,
        "fileCount": file_count,
        "score": body_chars + (tool_count * 25) + (mcp_server_count * 40) + (file_count * 15),
        "perTarget": per_target,
    }


def evaluate_candidate(
    documents: dict[str, dict[str, Any]],
    benchmark: dict[str, Any],
    default_target_id: str,
    *,
    candidate_record: dict[str, Any] | None = None,
    evidence_dataset: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checks = []
    total_weight = 0.0
    earned_weight = 0.0
    for raw_check in benchmark["checks"]:
        check = dict(raw_check)
        check_id = check.get("id") or check.get("type") or "check"
        check_type = check.get("type")
        target_id = str(check.get("targetId") or check.get("documentId") or default_target_id)
        if check.get("targetId") is not None or check.get("documentId") is not None:
            _document_or_error(documents, target_id, f"Benchmark check '{check_id}'")
        weight = float(check.get("weight", 1.0))
        total_weight += weight
        passed = False
        expected: Any = None
        observed: Any = None
        comparator: str | None = None
        if check_type == "contains_text":
            document = _document_or_error(documents, target_id, f"Benchmark check '{check_id}'")
            target = check.get("target", "body")
            if target == "body":
                actual_text = document["body"]
            elif target == "frontmatter":
                actual_text = _json(document["frontmatter"])
            else:
                actual_text = render_markdown_document(document["frontmatter"], document["body"])
            expected = str(check.get("value", ""))
            comparator = "contains"
            passed = expected in actual_text
            observed = {
                "containsExpected": passed,
                "targetLength": len(actual_text),
            }
        elif check_type == "episode_observation_guard":
            comparator = "episode_matches"
            expected, observed, passed = _evaluate_episode_observation_guard(
                check,
                candidate_record=candidate_record,
                evidence_dataset=evidence_dataset,
            )
        elif check_type == "frontmatter_equals":
            document = _document_or_error(documents, target_id, f"Benchmark check '{check_id}'")
            key = check.get("key")
            expected = check.get("value")
            observed = document["frontmatter"].get(key)
            comparator = "equals"
            passed = observed == expected
        elif check_type == "frontmatter_includes":
            document = _document_or_error(documents, target_id, f"Benchmark check '{check_id}'")
            key = check.get("key")
            expected = [str(value) for value in _as_list(check.get("values"))]
            actual_list = [str(value) for value in _as_list(document["frontmatter"].get(key))]
            observed = actual_list
            comparator = "includes_all"
            passed = all(value in actual_list for value in expected)
        elif check_type == "max_body_chars":
            document = _document_or_error(documents, target_id, f"Benchmark check '{check_id}'")
            expected = int(check.get("value", 0))
            observed = len(document["body"].strip())
            comparator = "less_than_or_equal"
            passed = observed <= expected
        else:
            raise ValueError(f"Unsupported benchmark check type: {check_type}")
        if passed:
            earned_weight += weight
        checks.append(
            {
                "id": check_id,
                "type": check_type,
                "targetId": target_id,
                "target": check.get("target"),
                "key": check.get("key"),
                "comparator": comparator,
                "weight": weight,
                "passed": passed,
                "expected": expected,
                "observed": observed,
                "actual": observed,
            }
        )
    complexity = _complexity(documents)
    total_checks = len(checks)
    passed_checks = sum(1 for check in checks if check["passed"])
    score = earned_weight / total_weight if total_weight else 0.0
    return {
        "score": round(score, 6),
        "passedChecks": passed_checks,
        "totalChecks": total_checks,
        "checks": checks,
        "complexity": complexity,
    }


def _evaluate_episode_observation_guard(
    check: dict[str, Any],
    *,
    candidate_record: dict[str, Any] | None,
    evidence_dataset: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    if candidate_record is None:
        raise ValueError(
            "Benchmark check type 'episode_observation_guard' requires candidate context."
        )

    min_matched_record_count = int(check.get("minMatchedRecordCount", 1))
    if min_matched_record_count < 1:
        raise ValueError(
            "Benchmark check type 'episode_observation_guard' requires minMatchedRecordCount >= 1."
        )

    episode = _candidate_trajectory_episode(
        candidate_record,
        candidate_records_by_id={str(candidate_record["candidateId"]): candidate_record},
        evidence_dataset=evidence_dataset,
    )
    summary = episode["summary"]

    expected_source_kinds = _non_empty_scalar_texts(_as_list(check.get("sourceKinds")))
    expected_tool_names = _non_empty_scalar_texts(_as_list(check.get("toolNames")))
    expected_terminal_status = _first_non_empty_scalar([check.get("terminalStatus")])

    observed_source_kinds = sorted(
        str(key) for key in (summary.get("sourceKindCounts") or {}).keys() if str(key)
    )
    observed_tool_names = [str(tool_name) for tool_name in (summary.get("toolNames") or [])]
    observed_terminal_status = summary.get("terminalStatus")
    matched_record_count = int(summary.get("matchedRecordCount") or 0)

    observed_source_kind_set = {value.casefold() for value in observed_source_kinds}
    observed_tool_name_set = {value.casefold() for value in observed_tool_names}
    source_kinds_match = all(
        value.casefold() in observed_source_kind_set for value in expected_source_kinds
    )
    tool_names_match = all(
        value.casefold() in observed_tool_name_set for value in expected_tool_names
    )
    terminal_status_match = True
    if expected_terminal_status is not None:
        terminal_status_match = (
            str(observed_terminal_status or "").casefold()
            == str(expected_terminal_status).casefold()
        )

    passed = (
        matched_record_count >= min_matched_record_count
        and source_kinds_match
        and tool_names_match
        and terminal_status_match
    )
    expected = {
        "minMatchedRecordCount": min_matched_record_count,
        "sourceKinds": expected_source_kinds,
        "toolNames": expected_tool_names,
        "terminalStatus": expected_terminal_status,
    }
    observed = {
        "episodeId": episode["episodeId"],
        "matchedRecordCount": matched_record_count,
        "sourceKinds": observed_source_kinds,
        "toolNames": observed_tool_names,
        "terminalStatus": observed_terminal_status,
        "sourceKindCounts": deepcopy(summary.get("sourceKindCounts") or {}),
        "statusCounts": deepcopy(summary.get("statusCounts") or {}),
        "sourceKindsMatch": source_kinds_match,
        "toolNamesMatch": tool_names_match,
        "terminalStatusMatch": terminal_status_match,
    }
    return expected, observed, passed


def _live_evaluator_text_limit(experiment: dict[str, Any]) -> int:
    return min(
        MAX_RECORDED_LIVE_EVALUATOR_OUTPUT_CHARS,
        int(experiment["evidencePolicy"]["maxExternalLogLineLength"]),
    )


def _sanitize_live_evaluator_text(value: Any, experiment: dict[str, Any]) -> str:
    text = _sanitize_text(
        str(value),
        allow_external_paths=bool(experiment["evidencePolicy"]["allowExternalPaths"]),
    )
    return _truncate_text(text, _live_evaluator_text_limit(experiment))


def _validate_live_evaluator_config(experiment: dict[str, Any], apply_best_requested: bool) -> None:
    config = experiment["evaluationMode"]["liveEvaluator"]
    if not config["enabled"]:
        return
    if not experiment["evaluationMode"]["deterministic"]:
        raise ValueError(
            "Live evaluator execution requires deterministic scoring to remain enabled."
        )
    if config["provider"] not in SUPPORTED_LIVE_EVALUATOR_PROVIDERS:
        raise ValueError(f"Unsupported live evaluator provider: {config['provider']}")
    if config["strategy"] not in SUPPORTED_LIVE_EVALUATOR_STRATEGIES:
        raise ValueError(f"Unsupported live evaluator strategy: {config['strategy']}")
    if config["promptArtifactPath"] is None:
        raise ValueError("Live evaluator requires promptArtifactPath when enabled.")
    if not config["promptArtifactPath"].exists():
        raise ValueError(
            "Live evaluator prompt artifact does not exist: "
            f"{config['promptArtifactPath'].as_posix()}"
        )
    if not config["rubricPaths"]:
        raise ValueError("Live evaluator requires at least one rubricPath when enabled.")
    missing_rubrics = [path for path in config["rubricPaths"] if not path.exists()]
    if missing_rubrics:
        raise ValueError(f"Live evaluator rubric does not exist: {missing_rubrics[0].as_posix()}")
    if config["maxSamples"] < 1:
        raise ValueError("Live evaluator maxSamples must be at least 1 when enabled.")
    if config["strategy"] == "tie_breaker" and config["maxSamples"] < 2:
        raise ValueError("Tie-breaker live evaluator requires maxSamples of at least 2.")
    if apply_best_requested or experiment["applyBestCandidate"]:
        raise ValueError(
            "Live evaluator execution requires stage-for-review mode; apply-best is not allowed."
        )
    if not experiment["stageForReview"] or not experiment["stagedPatchPolicy"]["enabled"]:
        raise ValueError("Live evaluator execution requires staged patch review to remain enabled.")
    if experiment["stagedPatchPolicy"]["applyOnPass"]:
        raise ValueError(
            "Live evaluator execution requires stagedPatchPolicy.applyOnPass to remain false."
        )
    if not experiment["continuousPolicy"]["stageOnly"]:
        raise ValueError(
            "Live evaluator execution requires continuousPolicy.stageOnly to remain true."
        )


def _validate_continuation_policy_config(
    experiment: dict[str, Any], apply_best_requested: bool
) -> None:
    policy = experiment["continuousPolicy"]
    continuation_requested = policy["enabled"] and policy["mode"] not in {"manual", "disabled"}
    if not continuation_requested:
        return
    if apply_best_requested or experiment["applyBestCandidate"]:
        raise ValueError(
            "Continuous policy requires stage-for-review mode; apply-best is not allowed."
        )
    if not experiment["stageForReview"] or not experiment["stagedPatchPolicy"]["enabled"]:
        raise ValueError("Continuous policy requires staged patch review to remain enabled.")
    if experiment["stagedPatchPolicy"]["applyOnPass"]:
        raise ValueError(
            "Continuous policy requires stagedPatchPolicy.applyOnPass to remain false."
        )
    if not policy["stageOnly"]:
        raise ValueError("Continuous policy requires continuousPolicy.stageOnly to remain true.")
    if not policy["requireReviewPass"]:
        raise ValueError(
            "Continuous policy requires continuousPolicy.requireReviewPass to remain true."
        )


def _evaluation_trajectory_score(evaluation: dict[str, Any]) -> float:
    return round(float(evaluation.get("trajectoryScore", 0.0)), 6)


def _candidate_sort_key(candidate_record: dict[str, Any]) -> tuple[float, int, float, int]:
    evaluation = candidate_record["evaluation"]
    return (
        -float(evaluation["score"]),
        int(evaluation["complexity"]["score"]),
        -_evaluation_trajectory_score(evaluation),
        int(candidate_record["iteration"]),
    )


def _candidate_id_slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return normalized or "candidate"


def _derived_candidate_id(base_candidate_id: str, parent_candidate_id: str, branched: bool) -> str:
    if not branched:
        return base_candidate_id
    return f"{base_candidate_id}--from--{_candidate_id_slug(parent_candidate_id)}"


def _select_frontier_records(
    candidate_records: list[dict[str, Any]],
    frontier_size: int,
) -> list[dict[str, Any]]:
    eligible = [record for record in candidate_records if record["status"] == "keep"]
    ordered = sorted(eligible, key=_candidate_sort_key)
    return ordered[:frontier_size]


def _search_ledger_node(candidate_record: dict[str, Any]) -> dict[str, Any]:
    evaluation = candidate_record["evaluation"]
    evidence_context = evaluation.get("trajectoryEvidenceContext") or {}
    reviewed_policy_context = evaluation.get("reviewedPolicyContext") or {}
    return {
        "candidateId": candidate_record["candidateId"],
        "parentCandidateId": candidate_record.get("parentCandidateId"),
        "mutationId": candidate_record.get("mutationId"),
        "iteration": candidate_record["iteration"],
        "searchDepth": candidate_record.get("searchDepth", 0),
        "status": candidate_record["status"],
        "description": candidate_record["description"],
        "score": evaluation["score"],
        "trajectoryScore": _evaluation_trajectory_score(evaluation),
        "trajectoryEvidenceMatches": int(evidence_context.get("matchedRecordCount") or 0),
        "trajectoryEvidenceErrors": int(evidence_context.get("errorCount") or 0),
        "trajectoryEvidenceWarnings": int(evidence_context.get("warningCount") or 0),
        "trajectoryEvidenceSuccesses": int(evidence_context.get("successCount") or 0),
        "reviewedPolicyMatches": int(reviewed_policy_context.get("matchedPolicyCount") or 0),
        "reviewedPolicyBonus": round(float(reviewed_policy_context.get("bonus") or 0.0), 6),
        "reviewedPolicyPenalty": round(
            float(reviewed_policy_context.get("penalty") or 0.0),
            6,
        ),
        "passedChecks": evaluation["passedChecks"],
        "totalChecks": evaluation["totalChecks"],
        "complexity": deepcopy(evaluation["complexity"]),
        "path": candidate_record["path"].as_posix(),
        "touchedTargets": list(candidate_record.get("touchedTargets") or []),
    }


def _candidate_ranking_snapshot(candidate_record: dict[str, Any]) -> dict[str, Any]:
    evaluation = candidate_record["evaluation"]
    evidence_context = evaluation.get("trajectoryEvidenceContext") or {}
    source_kind_counts = {
        str(key): int(value)
        for key, value in sorted((evidence_context.get("sourceKindCounts") or {}).items())
        if int(value)
    }
    status_counts = {
        str(key): int(value)
        for key, value in sorted((evidence_context.get("statusCounts") or {}).items())
        if int(value)
    }
    return {
        "candidateId": candidate_record["candidateId"],
        "iteration": int(candidate_record["iteration"]),
        "searchDepth": int(candidate_record.get("searchDepth", 0)),
        "score": float(evaluation["score"]),
        "complexityScore": int(evaluation["complexity"]["score"]),
        "trajectoryScore": _evaluation_trajectory_score(evaluation),
        "trajectorySignals": deepcopy(evaluation.get("trajectoryScoreBreakdown") or {}),
        "evidence": {
            "matchedRecordCount": int(evidence_context.get("matchedRecordCount") or 0),
            "successCount": int(evidence_context.get("successCount") or 0),
            "warningCount": int(evidence_context.get("warningCount") or 0),
            "errorCount": int(evidence_context.get("errorCount") or 0),
            "toolErrorCount": int(evidence_context.get("toolErrorCount") or 0),
            "externalErrorCount": int(evidence_context.get("externalErrorCount") or 0),
            "sourceKindCounts": source_kind_counts,
            "statusCounts": status_counts,
        },
    }


def _count_summary(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def _ranking_comparison(
    winner_snapshot: dict[str, Any],
    runner_up_snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "winnerScore": winner_snapshot["score"],
        "runnerUpScore": runner_up_snapshot["score"],
        "scoreDelta": round(winner_snapshot["score"] - runner_up_snapshot["score"], 6),
        "winnerComplexityScore": winner_snapshot["complexityScore"],
        "runnerUpComplexityScore": runner_up_snapshot["complexityScore"],
        "complexityAdvantage": int(
            runner_up_snapshot["complexityScore"] - winner_snapshot["complexityScore"]
        ),
        "winnerTrajectoryScore": winner_snapshot["trajectoryScore"],
        "runnerUpTrajectoryScore": runner_up_snapshot["trajectoryScore"],
        "trajectoryScoreDelta": round(
            winner_snapshot["trajectoryScore"] - runner_up_snapshot["trajectoryScore"],
            6,
        ),
    }


def _trajectory_signal_preference(signal: str) -> str:
    if signal in {
        "attributedWarningCount",
        "attributedErrorCount",
        "attributedToolErrorCount",
        "attributedExternalErrorCount",
        "evidenceIssuePenalty",
        "reviewedPolicyPenalty",
    }:
        return "lower_is_better"
    return "higher_is_better"


def _trajectory_signal_advantages(
    winner_snapshot: dict[str, Any],
    runner_up_snapshot: dict[str, Any],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    winner_signals = winner_snapshot.get("trajectorySignals") or {}
    runner_up_signals = runner_up_snapshot.get("trajectorySignals") or {}
    advantages: list[dict[str, Any]] = []
    for signal in sorted(set(winner_signals) | set(runner_up_signals)):
        winner_value = winner_signals.get(signal)
        runner_up_value = runner_up_signals.get(signal)
        if not isinstance(winner_value, (int, float)) or not isinstance(
            runner_up_value, (int, float)
        ):
            continue
        preference = _trajectory_signal_preference(signal)
        if preference == "lower_is_better":
            advantage = round(float(runner_up_value) - float(winner_value), 6)
        else:
            advantage = round(float(winner_value) - float(runner_up_value), 6)
        if advantage <= 0:
            continue
        advantages.append(
            {
                "signal": signal,
                "preference": preference,
                "winner": winner_value,
                "runnerUp": runner_up_value,
                "advantage": advantage,
            }
        )
    return sorted(advantages, key=lambda item: (-float(item["advantage"]), item["signal"]))[:limit]


def _trajectory_signal_summary(advantages: list[dict[str, Any]]) -> str | None:
    if not advantages:
        return None
    terms: list[str] = []
    for item in advantages[:3]:
        if item["preference"] == "lower_is_better":
            terms.append(f"{item['signal']} lower by {float(item['advantage']):g}")
        else:
            terms.append(f"{item['signal']} +{float(item['advantage']):g}")
    return "Top trajectory contributors: " + ", ".join(terms)


def _evidence_comparison(
    winner_snapshot: dict[str, Any],
    runner_up_snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "winnerSourceKinds": deepcopy(winner_snapshot["evidence"].get("sourceKindCounts") or {}),
        "runnerUpSourceKinds": deepcopy(
            runner_up_snapshot["evidence"].get("sourceKindCounts") or {}
        ),
        "winnerStatuses": deepcopy(winner_snapshot["evidence"].get("statusCounts") or {}),
        "runnerUpStatuses": deepcopy(runner_up_snapshot["evidence"].get("statusCounts") or {}),
    }


def _evidence_backed_tie_breaker(
    winner_snapshot: dict[str, Any],
    runner_up_snapshot: dict[str, Any],
) -> bool:
    evidence_keys = [
        "matchedRecordCount",
        "successCount",
        "warningCount",
        "errorCount",
        "toolErrorCount",
        "externalErrorCount",
    ]
    return any(
        winner_snapshot["evidence"][key] != runner_up_snapshot["evidence"][key]
        for key in evidence_keys
    )


def _trajectory_evidence_summary(
    winner_snapshot: dict[str, Any],
    runner_up_snapshot: dict[str, Any],
) -> str | None:
    if not _evidence_backed_tie_breaker(winner_snapshot, runner_up_snapshot):
        return None
    winner_sources = _count_summary(winner_snapshot["evidence"].get("sourceKindCounts") or {})
    runner_sources = _count_summary(runner_up_snapshot["evidence"].get("sourceKindCounts") or {})
    return (
        "Evidence favored "
        f"{winner_snapshot['candidateId']} "
        f"({winner_snapshot['evidence']['matchedRecordCount']} matches, "
        f"{winner_snapshot['evidence']['successCount']} successes, "
        f"{winner_snapshot['evidence']['errorCount']} errors; sources {winner_sources}) over "
        f"{runner_up_snapshot['candidateId']} "
        f"({runner_up_snapshot['evidence']['matchedRecordCount']} matches, "
        f"{runner_up_snapshot['evidence']['successCount']} successes, "
        f"{runner_up_snapshot['evidence']['errorCount']} errors; sources {runner_sources})."
    )


def _winner_explanation(
    candidate_records: list[dict[str, Any]],
    *,
    best_candidate_id: str,
    deterministic_best_candidate_id: str,
    live_evaluation: dict[str, Any],
) -> dict[str, Any]:
    by_id = {record["candidateId"]: record for record in candidate_records}
    best_record = by_id.get(best_candidate_id)
    if best_record is None:
        raise ValueError(
            f"Winner explanation references unknown candidateId '{best_candidate_id}'."
        )

    winner_snapshot = _candidate_ranking_snapshot(best_record)
    ordered = sorted(candidate_records, key=_candidate_sort_key)
    live_override = (
        bool(live_evaluation.get("bestCandidateChanged"))
        and str(live_evaluation.get("winnerCandidateId") or "") == best_candidate_id
        and deterministic_best_candidate_id != best_candidate_id
    )
    if live_override:
        runner_up_record = by_id.get(deterministic_best_candidate_id)
        runner_up_snapshot = (
            _candidate_ranking_snapshot(runner_up_record) if runner_up_record is not None else None
        )
        ranking_comparison = (
            _ranking_comparison(winner_snapshot, runner_up_snapshot)
            if runner_up_snapshot is not None
            else None
        )
        top_trajectory_signals = (
            _trajectory_signal_advantages(winner_snapshot, runner_up_snapshot)
            if runner_up_snapshot is not None
            else []
        )
        provider = str(live_evaluation.get("provider") or "unknown")
        strategy = str(live_evaluation.get("strategy") or "unknown")
        return {
            "winnerCandidateId": best_candidate_id,
            "comparedCandidateId": deterministic_best_candidate_id,
            "comparisonMode": "live_evaluator_override",
            "decisiveSignal": "live_evaluator",
            "evidenceBacked": False,
            "summary": (
                f"{best_candidate_id} replaced deterministic best "
                f"{deterministic_best_candidate_id} via live evaluator "
                f"({strategy}, {provider})."
            ),
            "evidenceSummary": None,
            "rankingComparison": ranking_comparison,
            "topTrajectorySignals": top_trajectory_signals,
            "trajectorySummary": _trajectory_signal_summary(top_trajectory_signals),
            "evidenceComparison": (
                _evidence_comparison(winner_snapshot, runner_up_snapshot)
                if runner_up_snapshot is not None
                else None
            ),
            "winner": winner_snapshot,
            "runnerUp": runner_up_snapshot,
            "liveEvaluation": {
                "status": live_evaluation.get("status"),
                "provider": live_evaluation.get("provider"),
                "strategy": live_evaluation.get("strategy"),
                "winnerCandidateId": live_evaluation.get("winnerCandidateId"),
            },
        }

    runner_up_record = next(
        (record for record in ordered if record["candidateId"] != best_candidate_id),
        None,
    )
    if runner_up_record is None:
        return {
            "winnerCandidateId": best_candidate_id,
            "comparedCandidateId": None,
            "comparisonMode": "single_candidate",
            "decisiveSignal": "single_candidate",
            "evidenceBacked": False,
            "summary": f"{best_candidate_id} remained the only candidate under consideration.",
            "evidenceSummary": None,
            "rankingComparison": None,
            "topTrajectorySignals": [],
            "trajectorySummary": None,
            "evidenceComparison": None,
            "winner": winner_snapshot,
            "runnerUp": None,
            "liveEvaluation": None,
        }

    runner_up_snapshot = _candidate_ranking_snapshot(runner_up_record)
    winner_score = winner_snapshot["score"]
    runner_up_score = runner_up_snapshot["score"]
    winner_complexity = winner_snapshot["complexityScore"]
    runner_up_complexity = runner_up_snapshot["complexityScore"]
    winner_trajectory = winner_snapshot["trajectoryScore"]
    runner_up_trajectory = runner_up_snapshot["trajectoryScore"]
    evidence_summary = None
    evidence_backed = False
    ranking_comparison = _ranking_comparison(winner_snapshot, runner_up_snapshot)
    top_trajectory_signals = _trajectory_signal_advantages(winner_snapshot, runner_up_snapshot)

    if winner_score > runner_up_score:
        decisive_signal = "benchmark_score"
        summary = (
            f"{best_candidate_id} beat {runner_up_snapshot['candidateId']} on benchmark score "
            f"({winner_score} vs {runner_up_score})."
        )
    elif winner_complexity < runner_up_complexity:
        decisive_signal = "complexity"
        summary = (
            f"{best_candidate_id} tied {runner_up_snapshot['candidateId']} on benchmark score "
            f"({winner_score}) and won on lower complexity "
            f"({winner_complexity} vs {runner_up_complexity})."
        )
    elif winner_trajectory > runner_up_trajectory:
        decisive_signal = "trajectory_score"
        evidence_summary = _trajectory_evidence_summary(winner_snapshot, runner_up_snapshot)
        evidence_backed = evidence_summary is not None
        summary = (
            f"{best_candidate_id} tied {runner_up_snapshot['candidateId']} on benchmark score "
            f"({winner_score}) and complexity ({winner_complexity}) and won on trajectory score "
            f"({winner_trajectory} vs {runner_up_trajectory})."
        )
        if evidence_summary is not None:
            summary = f"{summary} {evidence_summary}"
    else:
        decisive_signal = "iteration_order"
        summary = (
            f"{best_candidate_id} remained ahead of {runner_up_snapshot['candidateId']} after "
            "score, complexity, and trajectory score all tied; iteration order kept it first."
        )

    return {
        "winnerCandidateId": best_candidate_id,
        "comparedCandidateId": runner_up_snapshot["candidateId"],
        "comparisonMode": "deterministic_ranking",
        "decisiveSignal": decisive_signal,
        "evidenceBacked": evidence_backed,
        "summary": summary,
        "evidenceSummary": evidence_summary,
        "rankingComparison": ranking_comparison,
        "topTrajectorySignals": top_trajectory_signals,
        "trajectorySummary": _trajectory_signal_summary(top_trajectory_signals),
        "evidenceComparison": _evidence_comparison(winner_snapshot, runner_up_snapshot),
        "winner": winner_snapshot,
        "runnerUp": runner_up_snapshot,
        "liveEvaluation": None,
    }


def _best_candidate_lineage(
    candidate_records: list[dict[str, Any]],
    best_candidate_id: str,
) -> list[str]:
    by_id = {record["candidateId"]: record for record in candidate_records}
    lineage: list[str] = []
    current_id: str | None = best_candidate_id
    while current_id is not None:
        record = by_id.get(current_id)
        if record is None:
            break
        lineage.append(record["candidateId"])
        current_id = record.get("parentCandidateId")
    return list(reversed(lineage))


def _build_search_ledger(
    experiment: dict[str, Any],
    candidate_records: list[dict[str, Any]],
    frontier_snapshots: list[dict[str, Any]],
    mutation_execution_plan: list[dict[str, Any]],
    best_candidate_id: str,
    live_evaluation: dict[str, Any],
    winner_explanation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "AutoAgentSearchLedger",
        "experiment": {
            "name": experiment["name"],
            "path": experiment["path"].as_posix(),
        },
        "candidatePolicy": deepcopy(experiment["candidatePolicy"]),
        "baselineCandidateId": "baseline",
        "bestCandidateId": best_candidate_id,
        "bestCandidateLineage": _best_candidate_lineage(candidate_records, best_candidate_id),
        "maxSearchDepth": max(int(record.get("searchDepth", 0)) for record in candidate_records),
        "candidateCount": len(candidate_records),
        "frontierSnapshotCount": len(frontier_snapshots),
        "mutationExecutionPlan": deepcopy(mutation_execution_plan),
        "liveEvaluation": {
            "enabled": bool(live_evaluation.get("enabled")),
            "status": live_evaluation.get("status"),
            "winnerCandidateId": live_evaluation.get("winnerCandidateId"),
            "bestCandidateChanged": bool(live_evaluation.get("bestCandidateChanged")),
        },
        "winnerExplanation": deepcopy(winner_explanation),
        "nodes": [_search_ledger_node(record) for record in candidate_records],
        "frontierSnapshots": deepcopy(frontier_snapshots),
    }


def _serialize_checkpoint_documents(
    documents: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    serialized: dict[str, dict[str, Any]] = {}
    for target_id, document in documents.items():
        serialized[target_id] = {
            "frontmatter": deepcopy(document["frontmatter"]),
            "body": document["body"],
        }
    return serialized


def _serialize_checkpoint_candidate_record(
    record: dict[str, Any],
    *,
    inline_documents: bool,
) -> dict[str, Any]:
    payload = {
        "iteration": int(record["iteration"]),
        "candidateId": str(record["candidateId"]),
        "parentCandidateId": record.get("parentCandidateId"),
        "description": str(record.get("description") or "candidate mutation"),
        "status": str(record.get("status") or "discard"),
        "evaluation": deepcopy(record["evaluation"]),
        "path": record["path"].as_posix(),
        "documentStorage": "inline" if inline_documents else "candidate_snapshot",
        "searchDepth": int(record.get("searchDepth", 0)),
        "mutationId": record.get("mutationId"),
        "touchedTargets": list(record.get("touchedTargets") or []),
    }
    if inline_documents:
        payload["documents"] = _serialize_checkpoint_documents(record["documents"])
    return payload


def _restore_checkpoint_documents_from_snapshot(
    candidate_path: Path,
    targets_by_id: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    bundle_mode = len(targets_by_id) > 1
    for target_id, target in targets_by_id.items():
        snapshot_path = _candidate_snapshot_path(
            candidate_path, target_id, target["path"], bundle_mode
        )
        if not snapshot_path.exists():
            raise ValueError(
                f"Resume checkpoint candidate snapshot does not exist: {snapshot_path.as_posix()}"
            )
        frontmatter, body = load_markdown_document(snapshot_path)
        documents[target_id] = {
            "target": deepcopy(target),
            "frontmatter": frontmatter,
            "body": body,
        }
    return documents


def _checkpoint_inline_candidate_ids(
    frontier_records: list[dict[str, Any]],
    deterministic_best_candidate_id: str,
) -> set[str]:
    inline_candidate_ids = {deterministic_best_candidate_id}
    inline_candidate_ids.update(record["candidateId"] for record in frontier_records)
    return inline_candidate_ids


def _restore_checkpoint_documents(
    payload: dict[str, dict[str, Any]],
    targets_by_id: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for target_id, target in targets_by_id.items():
        document_payload = payload.get(target_id)
        if not isinstance(document_payload, dict):
            raise ValueError(
                f"Resume checkpoint inline documents are missing target '{target_id}'."
            )
        documents[target_id] = {
            "target": deepcopy(target),
            "frontmatter": deepcopy(document_payload.get("frontmatter") or {}),
            "body": str(document_payload.get("body") or ""),
        }
    return documents


def _restore_checkpoint_candidate_record(
    payload: dict[str, Any],
    targets_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    candidate_path = Path(str(payload["path"]))
    if payload.get("documents"):
        documents = _restore_checkpoint_documents(payload.get("documents") or {}, targets_by_id)
    else:
        documents = _restore_checkpoint_documents_from_snapshot(candidate_path, targets_by_id)
    return {
        "iteration": int(payload["iteration"]),
        "candidateId": str(payload["candidateId"]),
        "parentCandidateId": payload.get("parentCandidateId"),
        "description": str(payload.get("description") or "candidate mutation"),
        "status": str(payload.get("status") or "discard"),
        "evaluation": deepcopy(payload["evaluation"]),
        "documents": documents,
        "path": candidate_path,
        "searchDepth": int(payload.get("searchDepth", 0)),
        "mutationId": payload.get("mutationId"),
        "touchedTargets": list(payload.get("touchedTargets") or []),
    }


def _build_search_checkpoint(
    experiment: dict[str, Any],
    mutations: list[dict[str, Any]],
    mutation_execution_plan: list[dict[str, Any]],
    requested_mutation_count: int,
    candidate_records: list[dict[str, Any]],
    frontier_records: list[dict[str, Any]],
    frontier_snapshots: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    kept_candidates: list[str],
    discarded_candidates: list[str],
    evaluation_iteration: int,
    deterministic_best_candidate_id: str,
) -> dict[str, Any]:
    completed_mutation_count = max(0, min(requested_mutation_count, len(mutations)))
    next_mutation_index = completed_mutation_count + 1
    inline_candidate_ids = _checkpoint_inline_candidate_ids(
        frontier_records,
        deterministic_best_candidate_id,
    )
    return {
        "type": "AutoAgentCheckpoint",
        "version": 2,
        "resumeStage": "post_mutation_search",
        "experiment": _path_provenance(experiment["path"]),
        "benchmark": _path_provenance(experiment["benchmarkPath"]),
        "mutationCatalog": _path_provenance(experiment["mutationCatalogPath"]),
        "candidatePolicy": deepcopy(experiment["candidatePolicy"]),
        "requestedMutationCount": requested_mutation_count,
        "totalMutationCount": len(mutations),
        "completedMutationCount": completed_mutation_count,
        "nextMutationIndex": next_mutation_index,
        "hasRemainingMutations": completed_mutation_count < len(mutations),
        "mutationExecutionPlan": deepcopy(mutation_execution_plan),
        "mutationExecutionPlanTokens": [
            str(entry["planToken"]) for entry in mutation_execution_plan
        ],
        "evaluationIteration": evaluation_iteration,
        "deterministicBestCandidateId": deterministic_best_candidate_id,
        "currentFrontierCandidateIds": [record["candidateId"] for record in frontier_records],
        "inlineCandidateIds": sorted(inline_candidate_ids),
        "inlineCandidateCount": len(inline_candidate_ids),
        "snapshotBackedCandidateCount": max(0, len(candidate_records) - len(inline_candidate_ids)),
        "keptCandidates": list(kept_candidates),
        "discardedCandidates": list(discarded_candidates),
        "rows": deepcopy(rows),
        "candidateRecords": [
            _serialize_checkpoint_candidate_record(
                record,
                inline_documents=record["candidateId"] in inline_candidate_ids,
            )
            for record in candidate_records
        ],
        "frontierSnapshots": deepcopy(frontier_snapshots),
    }


def _build_search_checkpoint_manifest(
    experiment: dict[str, Any],
    checkpoint_path: Path,
    checkpoint_payload: dict[str, Any],
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    inline_candidate_ids = set(checkpoint_payload.get("inlineCandidateIds") or [])
    snapshot_candidates: list[dict[str, Any]] = []
    required_file_count = 0

    for candidate_record in candidate_records:
        if candidate_record["candidateId"] in inline_candidate_ids:
            continue
        candidate_path = candidate_record["path"]
        bundle_mode = not candidate_path.suffix
        required_files: list[dict[str, Any]] = []
        for target_id, document in candidate_record["documents"].items():
            target = document["target"]
            snapshot_path = _candidate_snapshot_path(
                candidate_path,
                target_id,
                target["path"],
                bundle_mode,
            )
            required_files.append(
                {
                    "targetId": target_id,
                    "path": snapshot_path.as_posix(),
                    "kind": target["kind"],
                    "primary": bool(target["primary"]),
                }
            )
        required_file_count += len(required_files)
        snapshot_candidates.append(
            {
                "candidateId": candidate_record["candidateId"],
                "iteration": candidate_record["iteration"],
                "parentCandidateId": candidate_record.get("parentCandidateId"),
                "searchDepth": int(candidate_record.get("searchDepth", 0)),
                "candidatePath": candidate_path.as_posix(),
                "requiredFiles": required_files,
            }
        )

    return {
        "type": "AutoAgentCheckpointManifest",
        "version": 1,
        "experiment": {
            "name": experiment["name"],
            "path": experiment["path"].as_posix(),
        },
        "checkpointPath": checkpoint_path.as_posix(),
        "checkpointVersion": int(checkpoint_payload.get("version") or 1),
        "resumeStage": checkpoint_payload.get("resumeStage"),
        "candidatePolicy": deepcopy(experiment["candidatePolicy"]),
        "currentFrontierCandidateIds": list(
            checkpoint_payload.get("currentFrontierCandidateIds") or []
        ),
        "deterministicBestCandidateId": checkpoint_payload.get("deterministicBestCandidateId"),
        "inlineCandidateIds": sorted(inline_candidate_ids),
        "snapshotCandidateCount": len(snapshot_candidates),
        "requiredFileCount": required_file_count,
        "snapshotCandidates": snapshot_candidates,
    }


def _load_search_checkpoint(
    checkpoint_path: Path,
    experiment: dict[str, Any],
    mutations: list[dict[str, Any]],
    mutation_execution_plan: list[dict[str, Any]],
    planned_mutation_count: int,
) -> dict[str, Any]:
    if not checkpoint_path.exists():
        raise ValueError(f"Resume checkpoint does not exist: {checkpoint_path.as_posix()}")
    try:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Resume checkpoint is not valid JSON: {checkpoint_path.as_posix()}"
        ) from error
    if checkpoint.get("type") != "AutoAgentCheckpoint":
        raise ValueError(f"Unsupported resume checkpoint type: {checkpoint.get('type')!r}.")
    if int(checkpoint.get("version") or 1) not in {1, 2}:
        raise ValueError(f"Unsupported resume checkpoint version: {checkpoint.get('version')!r}.")
    experiment_meta = checkpoint.get("experiment") or {}
    if experiment_meta.get("path") != experiment["path"].as_posix():
        raise ValueError("Resume checkpoint does not match the requested experiment path.")
    if experiment_meta.get("sha256") != _sha256_for_path(experiment["path"]):
        raise ValueError(
            "Resume checkpoint experiment fingerprint does not match the current file."
        )
    if (checkpoint.get("mutationCatalog") or {}).get("sha256") != _sha256_for_path(
        experiment["mutationCatalogPath"]
    ):
        raise ValueError("Resume checkpoint mutation catalog fingerprint does not match.")
    if (checkpoint.get("benchmark") or {}).get("sha256") != _sha256_for_path(
        experiment["benchmarkPath"]
    ):
        raise ValueError("Resume checkpoint benchmark fingerprint does not match.")
    if checkpoint.get("candidatePolicy") != experiment["candidatePolicy"]:
        raise ValueError("Resume checkpoint candidatePolicy does not match the current experiment.")

    checkpoint_plan_tokens = [
        str(value) for value in (checkpoint.get("mutationExecutionPlanTokens") or []) if str(value)
    ]
    current_plan_tokens = [str(entry["planToken"]) for entry in mutation_execution_plan]
    default_plan_tokens = [
        _mutation_plan_token(mutation, catalog_index)
        for catalog_index, mutation in enumerate(mutations, start=1)
    ]
    if checkpoint_plan_tokens:
        if checkpoint_plan_tokens != current_plan_tokens:
            raise ValueError(
                "Resume checkpoint mutation execution plan does not match the current run."
            )
    elif current_plan_tokens != default_plan_tokens:
        raise ValueError(
            "Resume checkpoint predates reviewed-policy mutation prioritization support."
        )

    completed_mutation_count = int(checkpoint.get("completedMutationCount") or 0)
    if completed_mutation_count < 0:
        raise ValueError("Resume checkpoint completedMutationCount must be non-negative.")
    if completed_mutation_count > len(mutations):
        raise ValueError("Resume checkpoint completedMutationCount exceeds the mutation catalog.")
    if completed_mutation_count > planned_mutation_count:
        raise ValueError(
            "Resume checkpoint has already progressed past the requested max iteration count."
        )
    if not checkpoint.get("candidateRecords"):
        raise ValueError("Resume checkpoint must contain candidateRecords.")
    return checkpoint


def _serialize_candidate_for_live_evaluator(candidate_record: dict[str, Any]) -> dict[str, Any]:
    documents: dict[str, Any] = {}
    for target_id, document in candidate_record["documents"].items():
        documents[target_id] = {
            "targetId": target_id,
            "path": document["target"]["path"].as_posix(),
            "kind": document["target"]["kind"],
            "primary": bool(document["target"]["primary"]),
            "frontmatter": deepcopy(document["frontmatter"]),
            "body": document["body"],
            "rendered": render_markdown_document(document["frontmatter"], document["body"]),
        }
    evaluation = candidate_record["evaluation"]
    return {
        "candidateId": candidate_record["candidateId"],
        "parentCandidateId": candidate_record.get("parentCandidateId"),
        "iteration": candidate_record["iteration"],
        "searchDepth": candidate_record.get("searchDepth", 0),
        "description": candidate_record["description"],
        "status": candidate_record["status"],
        "score": evaluation["score"],
        "trajectoryScore": _evaluation_trajectory_score(evaluation),
        "trajectoryScoreBreakdown": deepcopy(evaluation.get("trajectoryScoreBreakdown") or {}),
        "passedChecks": evaluation["passedChecks"],
        "totalChecks": evaluation["totalChecks"],
        "complexity": deepcopy(evaluation["complexity"]),
        "path": candidate_record["path"].as_posix(),
        "documents": documents,
    }


def _select_live_evaluator_samples(
    experiment: dict[str, Any],
    candidate_records: list[dict[str, Any]],
    best_record: dict[str, Any],
) -> tuple[list[dict[str, Any]], str | None]:
    config = experiment["evaluationMode"]["liveEvaluator"]
    ordered = sorted(candidate_records, key=_candidate_sort_key)
    if config["strategy"] == "tie_breaker":
        best_score = float(best_record["evaluation"]["score"])
        best_complexity = int(best_record["evaluation"]["complexity"]["score"])
        tied = [
            record
            for record in ordered
            if float(record["evaluation"]["score"]) == best_score
            and int(record["evaluation"]["complexity"]["score"]) == best_complexity
        ]
        if len(tied) < 2:
            return [], "no_tie_candidates"
        ordered = tied
    samples = ordered[: int(config["maxSamples"])]
    if not samples:
        return [], "no_candidates_selected"
    return samples, None


def _normalize_live_evaluator_judgments(
    raw_result: Any,
    samples: list[dict[str, Any]],
    experiment: dict[str, Any],
) -> list[dict[str, Any]]:
    config = experiment["evaluationMode"]["liveEvaluator"]
    if isinstance(raw_result, dict):
        raw_judgments = raw_result.get("judgments") or raw_result.get("results") or []
    elif isinstance(raw_result, list):
        raw_judgments = raw_result
    else:
        raise ValueError("Live evaluator runner must return a list or mapping of judgments.")

    sample_ids = {sample["candidateId"] for sample in samples}
    judgments: list[dict[str, Any]] = []
    for raw_judgment in raw_judgments:
        if not isinstance(raw_judgment, dict):
            continue
        candidate_id = str(raw_judgment.get("candidateId") or "").strip()
        if candidate_id not in sample_ids:
            continue
        try:
            score = float(raw_judgment.get("score", 0.0))
        except (TypeError, ValueError):
            score = 0.0
        normalized = {
            "candidateId": candidate_id,
            "score": round(score, 6),
            "verdict": str(raw_judgment.get("verdict") or "neutral"),
        }
        rationale = raw_judgment.get("rationale") or raw_judgment.get("reason")
        if rationale:
            normalized["rationale"] = _sanitize_live_evaluator_text(rationale, experiment)
        if config["recordRawOutputs"] and raw_judgment.get("rawOutput") is not None:
            normalized["rawOutput"] = _sanitize_live_evaluator_text(
                raw_judgment["rawOutput"],
                experiment,
            )
        judgments.append(normalized)
    return judgments


def _verdict_counts(judgments: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for judgment in judgments:
        verdict = str(judgment.get("verdict") or "neutral")
        counts[verdict] = counts.get(verdict, 0) + 1
    return counts


def _choose_tie_breaker_winner(
    best_record: dict[str, Any],
    sample_records: list[dict[str, Any]],
    judgments: list[dict[str, Any]],
) -> tuple[dict[str, Any], bool]:
    judgment_scores = {
        str(judgment["candidateId"]): float(judgment.get("score", 0.0)) for judgment in judgments
    }
    winner = best_record
    winner_score = judgment_scores.get(best_record["candidateId"], float("-inf"))
    for record in sample_records:
        score = judgment_scores.get(record["candidateId"], float("-inf"))
        if score > winner_score:
            winner = record
            winner_score = score
    return winner, winner["candidateId"] != best_record["candidateId"]


def _execute_live_evaluator(
    experiment: dict[str, Any],
    candidate_records: list[dict[str, Any]],
    best_record: dict[str, Any],
    apply_best_requested: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    config = experiment["evaluationMode"]["liveEvaluator"]
    result = {
        "enabled": config["enabled"],
        "status": "disabled",
        "strategy": config["strategy"],
        "provider": config["provider"],
        "model": config["model"],
        "sampleCount": 0,
        "evaluatedCandidateIds": [],
        "winnerCandidateId": best_record["candidateId"],
        "bestCandidateChanged": False,
        "tieBreakerApplied": False,
        "fallbackToDeterministic": False,
        "reason": "live_evaluator_disabled",
        "verdictCounts": {},
        "judgments": [],
    }
    if not config["enabled"]:
        return result, best_record

    _validate_live_evaluator_config(experiment, apply_best_requested)

    if config["requireDeterministicPass"] and (
        best_record["evaluation"]["passedChecks"] < best_record["evaluation"]["totalChecks"]
    ):
        result.update(
            {
                "status": "skipped",
                "reason": "deterministic_checks_failed",
            }
        )
        return result, best_record

    sample_records, skip_reason = _select_live_evaluator_samples(
        experiment,
        candidate_records,
        best_record,
    )
    if skip_reason is not None:
        result.update(
            {
                "status": "skipped",
                "reason": skip_reason,
            }
        )
        return result, best_record

    samples = [
        _serialize_candidate_for_live_evaluator(candidate_record)
        for candidate_record in sample_records
    ]
    result["sampleCount"] = len(samples)
    result["evaluatedCandidateIds"] = [sample["candidateId"] for sample in samples]

    runner = LIVE_EVALUATOR_RUNNERS.get(str(config["provider"]))
    if runner is None:
        result.update(
            {
                "status": "failed",
                "reason": f"no_runner_registered_for_provider:{config['provider']}",
                "fallbackToDeterministic": True,
            }
        )
        return result, best_record

    try:
        raw_result = runner(config, deepcopy(samples), experiment)
        judgments = _normalize_live_evaluator_judgments(raw_result, samples, experiment)
    except Exception as error:
        result.update(
            {
                "status": "failed",
                "reason": _sanitize_live_evaluator_text(error, experiment),
                "fallbackToDeterministic": True,
            }
        )
        return result, best_record

    if not judgments:
        result.update(
            {
                "status": "skipped",
                "reason": "no_judgments_returned",
            }
        )
        return result, best_record

    winner = best_record
    tie_breaker_applied = False
    if config["strategy"] == "tie_breaker":
        winner, tie_breaker_applied = _choose_tie_breaker_winner(
            best_record,
            sample_records,
            judgments,
        )

    result.update(
        {
            "status": "succeeded",
            "reason": None,
            "winnerCandidateId": winner["candidateId"],
            "bestCandidateChanged": winner["candidateId"] != best_record["candidateId"],
            "tieBreakerApplied": tie_breaker_applied,
            "verdictCounts": _verdict_counts(judgments),
            "judgments": judgments,
        }
    )
    return result, winner


def _is_better(candidate: dict[str, Any], best: dict[str, Any]) -> bool:
    if candidate["score"] > best["score"]:
        return True
    if candidate["score"] == best["score"]:
        candidate_complexity = candidate["complexity"]["score"]
        best_complexity = best["complexity"]["score"]
        if candidate_complexity < best_complexity:
            return True
        if candidate_complexity > best_complexity:
            return False
        return _evaluation_trajectory_score(candidate) > _evaluation_trajectory_score(best)
    return False


def _frontmatter_changed_keys(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    keys = set(before) | set(after)
    return sorted(key for key in keys if before.get(key) != after.get(key))


def _candidate_snapshot_path(
    candidate_path: Path,
    target_id: str,
    target_path: Path,
    bundle_mode: bool,
) -> Path:
    if not bundle_mode:
        return candidate_path
    return candidate_path / f"{target_id}{_document_suffix(target_path)}"


def _staged_patch_metadata(
    baseline_documents: dict[str, dict[str, Any]],
    best_documents: dict[str, dict[str, Any]],
    targets: list[dict[str, Any]],
    primary_target_id: str,
    best_candidate_id: str,
    best_candidate_path: Path,
    staged_patch_policy: dict[str, Any],
) -> dict[str, Any]:
    changed_targets: list[dict[str, Any]] = []
    bundle_mode = len(targets) > 1
    for target in targets:
        target_id = target["id"]
        baseline = baseline_documents[target_id]
        best = best_documents[target_id]
        changed_regions: list[str] = []
        frontmatter_keys = _frontmatter_changed_keys(baseline["frontmatter"], best["frontmatter"])
        if frontmatter_keys:
            changed_regions.append("frontmatter")
        if baseline["body"] != best["body"]:
            changed_regions.append("body")
        if not changed_regions:
            continue
        changed_targets.append(
            {
                "targetId": target_id,
                "sourcePath": target["path"].as_posix(),
                "candidateSnapshotPath": _candidate_snapshot_path(
                    best_candidate_path,
                    target_id,
                    target["path"],
                    bundle_mode,
                ).as_posix(),
                "primary": target_id == primary_target_id,
                "kind": target["kind"],
                "mutableRegions": list(target["mutableRegions"]),
                "changedRegions": changed_regions,
                "frontmatterChangedKeys": frontmatter_keys,
            }
        )
    return {
        "enabled": staged_patch_policy["enabled"],
        "mode": staged_patch_policy["mode"],
        "applyOnPass": staged_patch_policy["applyOnPass"],
        "candidateId": best_candidate_id,
        "candidatePath": best_candidate_path.as_posix(),
        "changedTargetCount": len(changed_targets),
        "changedTargets": changed_targets,
        "reviewerHints": list(staged_patch_policy["reviewerHints"]),
        "manifestFormat": staged_patch_policy["manifestFormat"],
        "includeTargetSnapshots": staged_patch_policy["includeTargetSnapshots"],
        "includeDiffSummary": staged_patch_policy["includeDiffSummary"],
    }


def _provenance_summary(
    experiment_path: Path,
    experiment: dict[str, Any],
    evidence_dataset: dict[str, Any],
    evidence_artifact: dict[str, Any],
    results_artifact: dict[str, Any],
    resume_checkpoint_input: Path | None,
    checkpoint_artifact: dict[str, Any],
    checkpoint_stage: str | None,
    checkpoint_manifest_artifact: dict[str, Any],
    search_ledger_artifact: dict[str, Any],
    benchmark_drafts_artifact: dict[str, Any],
    mutation_drafts_artifact: dict[str, Any],
    policy_drafts_artifact: dict[str, Any],
    trace_artifact: dict[str, Any],
) -> dict[str, Any]:
    current_run_root = _current_run_root()
    return {
        "inputs": {
            "experiment": _path_provenance(experiment_path),
            "benchmark": _path_provenance(experiment["benchmarkPath"]),
            "mutationCatalog": _path_provenance(experiment["mutationCatalogPath"]),
            "liveEvaluatorPrompt": _path_provenance(
                experiment["evaluationMode"]["liveEvaluator"]["promptArtifactPath"]
            ),
            "liveEvaluatorRubrics": [
                _path_provenance(path)
                for path in experiment["evaluationMode"]["liveEvaluator"]["rubricPaths"]
            ],
            "resumeCheckpoint": _path_provenance(resume_checkpoint_input),
        },
        "evidence": {
            "datasetPath": evidence_artifact["actualPath"],
            "summary": evidence_dataset["summary"],
            "sources": evidence_dataset["sources"],
        },
        "policy": {
            "continuousPolicy": _serialize_continuous_policy(experiment["continuousPolicy"]),
            "continuationEligibility": _serialize_continuation_eligibility(
                experiment["continuationEligibility"]
            ),
            "governedTaskLifecycle": _serialize_governed_task_lifecycle(
                experiment["governedTaskLifecycle"]
            ),
            "governedReviewConsensus": _serialize_governed_review_consensus(
                experiment["governedReviewConsensus"]
            ),
            "continuationReadiness": _serialize_continuation_readiness(
                experiment["continuationReadiness"]
            ),
            "reviewedContinuationHandoff": _serialize_reviewed_continuation_handoff(
                experiment["reviewedContinuationHandoff"]
            ),
            "orchestrationContract": _serialize_orchestration_contract(
                experiment["orchestrationContract"]
            ),
            "reviewedDispatchIntent": _serialize_reviewed_dispatch_intent(
                experiment["reviewedDispatchIntent"]
            ),
            "governedApprovalMetadata": _serialize_governed_approval_metadata(
                experiment["governedApprovalMetadata"]
            ),
            "reviewedPolicyRuntime": _serialize_reviewed_policy_runtime(
                experiment["reviewedPolicyRuntime"]
            ),
            "reviewedPolicyRuntimeState": _serialize_reviewed_policy_runtime_state(
                experiment.get("reviewedPolicyRuntimeState") or {}
            ),
        },
        "artifacts": {
            "resultsPath": results_artifact["actualPath"],
            "checkpointPath": checkpoint_artifact["actualPath"],
            "checkpointStage": checkpoint_stage,
            "checkpointManifestPath": checkpoint_manifest_artifact["actualPath"],
            "searchLedgerPath": search_ledger_artifact["actualPath"],
            "benchmarkDraftsPath": benchmark_drafts_artifact["actualPath"],
            "mutationDraftsPath": mutation_drafts_artifact["actualPath"],
            "policyDraftsPath": policy_drafts_artifact["actualPath"],
            "tracePath": trace_artifact["actualPath"],
            "currentRunRoot": current_run_root.as_posix() if current_run_root is not None else None,
        },
    }


def _candidate_trace_event(
    row: dict[str, Any],
    candidate_record: dict[str, Any] | None,
    *,
    baseline_score: float,
    parent_score: float | None,
    best_candidate_id: str,
) -> dict[str, Any]:
    score = float(row["score"])
    event = {
        "eventId": f"candidate-evaluation-{int(row['iteration']):02d}-{row['candidateId']}",
        "kind": "candidate_evaluation",
        "trajectoryId": _trace_trajectory_id(row["candidateId"]),
        "iteration": int(row["iteration"]),
        "candidateId": row["candidateId"],
        "parentCandidateId": row.get("parentCandidateId"),
        "mutationId": candidate_record.get("mutationId") if candidate_record else None,
        "searchDepth": int(row.get("searchDepth", 0)),
        "status": row["status"],
        "description": row["description"],
        "score": score,
        "trajectoryScore": float(row.get("trajectoryScore") or 0.0),
        "deltaFromBaseline": round(score - baseline_score, 6),
        "passedChecks": int(row["passedChecks"]),
        "totalChecks": int(row["totalChecks"]),
        "complexity": deepcopy(row["complexity"]),
        "touchedTargets": list(row.get("touchedTargets") or []),
        "candidatePath": candidate_record["path"].as_posix() if candidate_record else None,
        "selectedAsBest": row["candidateId"] == best_candidate_id,
    }
    if parent_score is not None:
        event["deltaFromParent"] = round(score - parent_score, 6)
    return event


def _frontier_trace_event(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "eventId": f"frontier-snapshot-{int(snapshot['mutationIndex']):02d}",
        "kind": "frontier_snapshot",
        "mutationIndex": int(snapshot["mutationIndex"]),
        "mutationId": snapshot.get("mutationId"),
        "evaluatedCandidateIds": list(snapshot.get("evaluatedCandidateIds") or []),
        "frontierCandidateIds": list(snapshot.get("frontierCandidateIds") or []),
        "bestCandidateId": snapshot.get("bestCandidateId"),
    }


def _trace_outcome_label(best_score: float, baseline_score: float) -> str:
    if best_score > baseline_score:
        return "improved"
    return "unchanged"


def _trace_trajectory_id(candidate_id: str) -> str:
    return f"candidate-trajectory-{candidate_id}"


def _mutation_catalog_by_id(mutations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(mutation.get("id")): mutation
        for mutation in mutations
        if mutation.get("id") is not None
    }


def _candidate_lineage_ids(
    candidate_records_by_id: dict[str, dict[str, Any]],
    candidate_id: str,
) -> list[str]:
    lineage: list[str] = []
    current_id: str | None = candidate_id
    while current_id is not None:
        record = candidate_records_by_id.get(current_id)
        if record is None:
            break
        lineage.append(record["candidateId"])
        current_id = record.get("parentCandidateId")
    return list(reversed(lineage))


def _trajectory_action_sequence(
    mutation: dict[str, Any] | None,
    *,
    primary_target_id: str,
) -> list[dict[str, Any]]:
    if not mutation:
        return []

    actions: list[dict[str, Any]] = []
    for operation_index, raw_operation in enumerate(mutation.get("operations") or [], start=1):
        operation = deepcopy(raw_operation)
        resolved_target_id = operation.get("targetId") or operation.get("documentId")
        if resolved_target_id is None:
            operation["targetId"] = primary_target_id
        actions.append(
            {
                "actionId": f"mutation-operation-{operation_index:02d}",
                "actionType": "mutation_operation",
                "operationIndex": operation_index,
                "operation": operation,
            }
        )
    return actions


def _trajectory_validation_attempts(
    candidate_id: str,
    evaluation: dict[str, Any],
    benchmark: dict[str, Any],
    live_evaluation: dict[str, Any],
) -> list[dict[str, Any]]:
    attempts = [
        {
            "attemptType": "deterministic_benchmark",
            "attemptIndex": 1,
            "benchmarkId": benchmark.get("id"),
            "passedChecks": int(evaluation["passedChecks"]),
            "totalChecks": int(evaluation["totalChecks"]),
            "checks": [deepcopy(check) for check in evaluation["checks"]],
        }
    ]

    evaluated_candidate_ids = {
        str(candidate) for candidate in live_evaluation.get("evaluatedCandidateIds") or []
    }
    if candidate_id in evaluated_candidate_ids:
        attempts.append(
            {
                "attemptType": "live_evaluator",
                "attemptIndex": len(attempts) + 1,
                "status": live_evaluation.get("status"),
                "strategy": live_evaluation.get("strategy"),
                "provider": live_evaluation.get("provider"),
                "model": live_evaluation.get("model"),
                "sampleCount": int(live_evaluation.get("sampleCount") or 0),
                "winnerCandidateId": live_evaluation.get("winnerCandidateId"),
                "selectedWinner": candidate_id == live_evaluation.get("winnerCandidateId"),
                "bestCandidateChanged": bool(live_evaluation.get("bestCandidateChanged")),
            }
        )
    return attempts


def _score_candidate_trajectory(trajectory: dict[str, Any]) -> dict[str, Any]:
    outcome = trajectory["outcome"]
    context = trajectory["context"]
    evidence = context.get("evidence") or {}
    reviewed_policies = context.get("reviewedPolicies") or {}
    total_checks = int(outcome.get("totalChecks") or 0)
    passed_checks = int(outcome.get("passedChecks") or 0)
    validation_breadth = passed_checks / total_checks if total_checks else 0.0

    raw_delta_from_parent = outcome.get("deltaFromParent")
    parent_progress = (
        max(float(raw_delta_from_parent), 0.0) if raw_delta_from_parent is not None else 0.0
    )
    action_count = len(trajectory.get("actionSequence") or [])
    action_efficiency = 1.0 if action_count == 0 else 1.0 / (1.0 + action_count)
    touched_target_count = len(context.get("touchedTargets") or [])
    target_focus = 1.0 if touched_target_count <= 1 else 1.0 / float(touched_target_count)
    lineage_efficiency = 1.0 / (1.0 + float(trajectory.get("searchDepth") or 0))
    matched_evidence_records = int(evidence.get("matchedRecordCount") or 0)
    evidence_success_count = int(evidence.get("successCount") or 0)
    evidence_warning_count = int(evidence.get("warningCount") or 0)
    evidence_error_count = int(evidence.get("errorCount") or 0)
    evidence_tool_error_count = int(evidence.get("toolErrorCount") or 0)
    evidence_external_error_count = int(evidence.get("externalErrorCount") or 0)
    evidence_support = min(0.03, evidence_success_count * 0.015)
    evidence_issue_penalty = min(
        0.08,
        (evidence_error_count * 0.04) + (evidence_warning_count * 0.015),
    )
    reviewed_policy_bonus = max(0.0, float(reviewed_policies.get("bonus") or 0.0))
    reviewed_policy_penalty = max(0.0, float(reviewed_policies.get("penalty") or 0.0))
    live_winner_boost = 0.0
    for attempt in trajectory.get("validationAttempts") or []:
        if attempt.get("attemptType") == "live_evaluator" and attempt.get("selectedWinner"):
            live_winner_boost = 0.02
            break

    components = {
        "validationBreadth": round(validation_breadth, 6),
        "parentProgress": round(parent_progress, 6),
        "actionEfficiency": round(action_efficiency, 6),
        "targetFocus": round(target_focus, 6),
        "lineageEfficiency": round(lineage_efficiency, 6),
        "matchedEvidenceRecords": matched_evidence_records,
        "attributedSuccessCount": evidence_success_count,
        "attributedWarningCount": evidence_warning_count,
        "attributedErrorCount": evidence_error_count,
        "attributedToolErrorCount": evidence_tool_error_count,
        "attributedExternalErrorCount": evidence_external_error_count,
        "evidenceSupport": round(evidence_support, 6),
        "evidenceIssuePenalty": round(evidence_issue_penalty, 6),
        "reviewedPolicyBonus": round(reviewed_policy_bonus, 6),
        "reviewedPolicyPenalty": round(reviewed_policy_penalty, 6),
        "liveWinnerBoost": round(live_winner_boost, 6),
    }
    score = round(
        (validation_breadth * 0.55)
        + (parent_progress * 0.15)
        + (action_efficiency * 0.15)
        + (target_focus * 0.1)
        + (lineage_efficiency * 0.05)
        + evidence_support
        - evidence_issue_penalty
        + reviewed_policy_bonus
        - reviewed_policy_penalty
        + live_winner_boost,
        6,
    )
    return {
        "score": score,
        "components": components,
    }


def _evidence_record_search_text(record: dict[str, Any]) -> str:
    payload = record.get("payload")
    if isinstance(payload, (dict, list)):
        payload_text = _json(payload)
    elif payload is None:
        payload_text = ""
    else:
        payload_text = str(payload)
    raw_candidate_ids = record.get("candidateIds")
    if isinstance(raw_candidate_ids, list):
        candidate_ids_text = "\n".join(_non_empty_scalar_texts(raw_candidate_ids))
    elif raw_candidate_ids is None:
        candidate_ids_text = ""
    else:
        candidate_ids_text = "\n".join(_non_empty_scalar_texts([raw_candidate_ids]))
    return "\n".join(
        str(value)
        for value in [
            record.get("file"),
            record.get("recordType"),
            candidate_ids_text,
            record.get("role"),
            record.get("toolName"),
            record.get("sourceId"),
            record.get("transcriptText"),
            payload_text,
        ]
        if value is not None and str(value)
    ).lower()


def _candidate_evidence_aliases(candidate_record: dict[str, Any]) -> list[str]:
    aliases = {
        str(candidate_record["candidateId"]).lower(),
        _trace_trajectory_id(candidate_record["candidateId"]).lower(),
    }
    mutation_id = candidate_record.get("mutationId")
    if mutation_id is not None:
        aliases.add(str(mutation_id).lower())
    return sorted(alias for alias in aliases if alias)


def _candidate_evidence_reference_aliases(
    candidate_record: dict[str, Any],
    candidate_records_by_id: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    aliases = set(_candidate_evidence_aliases(candidate_record))
    candidate_id = str(candidate_record["candidateId"])

    normalized = candidate_id.strip()
    if normalized:
        aliases.add(normalized.casefold())
        aliases.add(_trace_trajectory_id(normalized).casefold())

    return sorted(alias for alias in aliases if alias)


def _evidence_record_candidate_ids(record: dict[str, Any]) -> set[str]:
    raw_candidate_ids = record.get("candidateIds")
    if raw_candidate_ids is None:
        return set()
    values = (
        _non_empty_scalar_texts(raw_candidate_ids)
        if isinstance(raw_candidate_ids, list)
        else _non_empty_scalar_texts([raw_candidate_ids])
    )
    return {value.casefold() for value in values}


def _evidence_record_explicit_candidate_refs(record: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    for field_name in ("candidateIds", "lineageCandidateIds", "handoffRefs"):
        raw_values = record.get(field_name)
        if raw_values is None:
            continue
        values = (
            _non_empty_scalar_texts(raw_values)
            if isinstance(raw_values, list)
            else _non_empty_scalar_texts([raw_values])
        )
        refs.update(value.casefold() for value in values)
    return refs


def _record_matches_candidate_aliases(record: dict[str, Any], aliases: list[str]) -> bool:
    explicit_refs = _evidence_record_explicit_candidate_refs(record)
    if explicit_refs:
        return any(alias in explicit_refs for alias in aliases)

    search_text = _evidence_record_search_text(record)
    return bool(
        search_text
        and any(
            re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", search_text)
            for alias in aliases
        )
    )


def _matched_candidate_evidence_records(
    candidate_record: dict[str, Any],
    evidence_dataset: dict[str, Any] | None,
    *,
    candidate_records_by_id: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    aliases = _candidate_evidence_reference_aliases(
        candidate_record,
        candidate_records_by_id=candidate_records_by_id,
    )
    return [
        record
        for record in (evidence_dataset or {}).get("records") or []
        if _record_matches_candidate_aliases(record, aliases)
    ]


def _candidate_evidence_context(
    candidate_record: dict[str, Any],
    evidence_dataset: dict[str, Any] | None,
    *,
    candidate_records_by_id: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    aliases = _candidate_evidence_reference_aliases(
        candidate_record,
        candidate_records_by_id=candidate_records_by_id,
    )
    matched_record_count = 0
    error_count = 0
    warning_count = 0
    success_count = 0
    tool_error_count = 0
    external_error_count = 0
    source_kind_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}

    for record in (evidence_dataset or {}).get("records") or []:
        if not _record_matches_candidate_aliases(record, aliases):
            continue

        matched_record_count += 1
        source_kind = str(record.get("sourceKind") or "unknown")
        source_kind_counts[source_kind] = source_kind_counts.get(source_kind, 0) + 1

        raw_status = record.get("status")
        status = str(raw_status).lower() if raw_status is not None else "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        if status == "error":
            error_count += 1
            if source_kind == "hook_event":
                tool_error_count += 1
            if source_kind == "session_event" and record.get("toolName") is not None:
                tool_error_count += 1
            if (
                source_kind in {"transcript_event", "handoff_event"}
                and record.get("toolName") is not None
            ):
                tool_error_count += 1
            if source_kind == "external_log":
                external_error_count += 1
        elif status == "warning":
            warning_count += 1
        elif status == "success":
            success_count += 1

    return {
        "aliases": aliases,
        "matchedRecordCount": matched_record_count,
        "errorCount": error_count,
        "warningCount": warning_count,
        "successCount": success_count,
        "toolErrorCount": tool_error_count,
        "externalErrorCount": external_error_count,
        "sourceKindCounts": source_kind_counts,
        "statusCounts": status_counts,
    }


def _candidate_episode_step(
    record: dict[str, Any],
    *,
    episode_id: str,
    step_index: int,
) -> dict[str, Any]:
    raw_candidate_ids = record.get("candidateIds")
    candidate_ids = (
        _non_empty_scalar_texts(raw_candidate_ids)
        if isinstance(raw_candidate_ids, list)
        else _non_empty_scalar_texts([raw_candidate_ids])
        if raw_candidate_ids is not None
        else []
    )
    raw_lineage_candidate_ids = record.get("lineageCandidateIds")
    lineage_candidate_ids = (
        _non_empty_scalar_texts(raw_lineage_candidate_ids)
        if isinstance(raw_lineage_candidate_ids, list)
        else _non_empty_scalar_texts([raw_lineage_candidate_ids])
        if raw_lineage_candidate_ids is not None
        else []
    )
    raw_handoff_refs = record.get("handoffRefs")
    handoff_refs = (
        _non_empty_scalar_texts(raw_handoff_refs)
        if isinstance(raw_handoff_refs, list)
        else _non_empty_scalar_texts([raw_handoff_refs])
        if raw_handoff_refs is not None
        else []
    )
    return {
        "stepId": f"{episode_id}-step-{step_index:02d}",
        "sequence": step_index,
        "sourceKind": str(record.get("sourceKind") or "unknown"),
        "sourceScope": record.get("sourceScope"),
        "file": record.get("file"),
        "recordType": record.get("recordType"),
        "status": record.get("status"),
        "role": record.get("role"),
        "toolName": record.get("toolName"),
        "sourceId": record.get("sourceId"),
        "candidateIds": candidate_ids,
        "lineageCandidateIds": lineage_candidate_ids,
        "handoffRefs": handoff_refs,
        "transcriptText": record.get("transcriptText"),
    }


def _candidate_trajectory_episode(
    candidate_record: dict[str, Any],
    *,
    candidate_records_by_id: dict[str, dict[str, Any]],
    evidence_dataset: dict[str, Any] | None,
) -> dict[str, Any]:
    candidate_id = candidate_record["candidateId"]
    episode_id = f"candidate-episode-{candidate_id}"
    matched_records = _matched_candidate_evidence_records(
        candidate_record,
        evidence_dataset,
        candidate_records_by_id=candidate_records_by_id,
    )
    steps = [
        _candidate_episode_step(record, episode_id=episode_id, step_index=index)
        for index, record in enumerate(matched_records, start=1)
    ]
    source_kind_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    tool_names: list[str] = []
    tool_sequence: list[str] = []
    tool_counts: dict[str, int] = {}
    seen_tool_names: set[str] = set()
    handoff_count = 0
    for step in steps:
        source_kind = step["sourceKind"]
        source_kind_counts[source_kind] = source_kind_counts.get(source_kind, 0) + 1
        status = str(step.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        if source_kind == "handoff_event" or step.get("handoffRefs"):
            handoff_count += 1
        tool_name = step.get("toolName")
        if tool_name is None:
            continue
        normalized_tool_name = str(tool_name)
        tool_sequence.append(normalized_tool_name)
        tool_counts[normalized_tool_name] = tool_counts.get(normalized_tool_name, 0) + 1
        if normalized_tool_name in seen_tool_names:
            continue
        seen_tool_names.add(normalized_tool_name)
        tool_names.append(normalized_tool_name)

    terminal_status = steps[-1].get("status") if steps else None
    if terminal_status is None:
        terminal_status = candidate_record.get("status")

    return {
        "episodeId": episode_id,
        "kind": "candidate_observation_episode",
        "trajectoryId": _trace_trajectory_id(candidate_id),
        "candidateId": candidate_id,
        "parentCandidateId": candidate_record.get("parentCandidateId"),
        "status": candidate_record.get("status"),
        "lineageCandidateIds": _candidate_lineage_ids(candidate_records_by_id, candidate_id),
        "summary": {
            "matchedRecordCount": len(steps),
            "stepCount": len(steps),
            "sourceKindCounts": source_kind_counts,
            "statusCounts": status_counts,
            "toolNames": tool_names,
            "toolSequence": tool_sequence,
            "toolCounts": tool_counts,
            "handoffCount": handoff_count,
            "observedPattern": "evidence_backed" if steps else "benchmark_only",
            "terminalStatus": terminal_status,
        },
        "steps": steps,
    }


def _episode_learning_classification(episode: dict[str, Any]) -> str:
    summary = episode["summary"]
    matched_record_count = int(summary.get("matchedRecordCount") or 0)
    if matched_record_count == 0:
        return "benchmark_only"

    status_counts = summary.get("statusCounts") or {}
    terminal_status = str(summary.get("terminalStatus") or "").lower()
    if int(status_counts.get("error") or 0) > 0 or terminal_status in {
        "error",
        "failed",
        "failure",
    }:
        return "failure_path"
    if int(status_counts.get("warning") or 0) > 0 or terminal_status == "warning":
        return "warning_path"
    if int(status_counts.get("success") or 0) > 0 or terminal_status in {
        "success",
        "completed",
        "done",
        "ok",
        "passed",
    }:
        return "successful_path"
    return "observed_path"


def _episode_terminal_outcome_score(classification: str, benchmark_quality: float) -> float:
    if classification == "benchmark_only":
        return benchmark_quality
    if classification == "successful_path":
        return 1.0
    if classification == "warning_path":
        return 0.35
    if classification == "failure_path":
        return 0.0
    return 0.6


def _episode_tool_churn_score(tool_sequence: list[str]) -> tuple[int, float]:
    repeated_tool_count = sum(
        1
        for index in range(1, len(tool_sequence))
        if tool_sequence[index] == tool_sequence[index - 1]
    )
    if len(tool_sequence) <= 1:
        return repeated_tool_count, 1.0
    return repeated_tool_count, 1.0 / (1.0 + repeated_tool_count)


def _episode_handoff_efficiency(handoff_count: int) -> float:
    return 1.0 / (1.0 + (0.5 * handoff_count))


def _episode_trace_provenance(summary: dict[str, Any]) -> dict[str, Any]:
    source_kind_counts = summary.get("sourceKindCounts") or {}
    transcript_record_count = int(source_kind_counts.get("transcript_event") or 0)
    handoff_record_count = int(source_kind_counts.get("handoff_event") or 0)
    return {
        "matchedRecordCount": int(summary.get("matchedRecordCount") or 0),
        "sourceKinds": sorted(str(key) for key in source_kind_counts.keys()),
        "transcriptRecordCount": transcript_record_count,
        "handoffRecordCount": handoff_record_count,
        "transcriptBacked": transcript_record_count > 0,
        "handoffBacked": handoff_record_count > 0,
    }


def _episode_shadow_learning_scores(
    candidate_record: dict[str, Any],
    trajectory: dict[str, Any],
    episode: dict[str, Any],
) -> dict[str, Any]:
    evaluation = candidate_record["evaluation"]
    benchmark_quality = max(0.0, min(1.0, float(evaluation.get("score") or 0.0)))
    summary = episode["summary"]
    matched_record_count = int(summary.get("matchedRecordCount") or 0)
    step_count = int(summary.get("stepCount") or matched_record_count)
    status_counts = summary.get("statusCounts") or {}
    success_count = int(status_counts.get("success") or 0)
    warning_count = int(status_counts.get("warning") or 0)
    error_count = int(status_counts.get("error") or 0)
    neutral_count = max(
        matched_record_count - success_count - warning_count - error_count,
        0,
    )
    if matched_record_count > 0:
        evidence_quality = max(
            0.0,
            min(
                1.0,
                (success_count + (0.5 * neutral_count) - error_count - (0.5 * warning_count))
                / float(matched_record_count),
            ),
        )
    else:
        evidence_quality = benchmark_quality

    classification = _episode_learning_classification(episode)
    action_count = len(trajectory.get("actionSequence") or [])
    search_depth = int(trajectory.get("searchDepth") or 0)
    handoff_count = int(summary.get("handoffCount") or 0)
    tool_sequence = [str(tool_name) for tool_name in (summary.get("toolSequence") or [])]
    terminal_outcome_score = _episode_terminal_outcome_score(classification, benchmark_quality)
    repeated_tool_count, tool_churn_score = _episode_tool_churn_score(tool_sequence)
    handoff_efficiency = _episode_handoff_efficiency(handoff_count)
    action_efficiency = 1.0 / (1.0 + action_count)
    search_efficiency = 1.0 / (1.0 + search_depth)
    step_efficiency = 1.0 if step_count <= 1 else 1.0 / float(step_count)
    quality_score = round(
        (benchmark_quality * 0.45) + (evidence_quality * 0.35) + (terminal_outcome_score * 0.2),
        6,
    )
    efficiency_score = round(
        (action_efficiency * 0.25)
        + (search_efficiency * 0.25)
        + (step_efficiency * 0.15)
        + (handoff_efficiency * 0.2)
        + (tool_churn_score * 0.15),
        6,
    )
    reasoning_path_efficiency_score = efficiency_score
    learning_score = round((quality_score * 0.6) + (efficiency_score * 0.4), 6)
    return {
        "classification": classification,
        "qualityScore": quality_score,
        "efficiencyScore": efficiency_score,
        REASONING_PATH_EFFICIENCY_SIGNAL_NAME: reasoning_path_efficiency_score,
        "learningScore": learning_score,
        "factors": {
            "benchmarkQuality": round(benchmark_quality, 6),
            "evidenceQuality": round(evidence_quality, 6),
            "terminalOutcomeScore": round(terminal_outcome_score, 6),
            "actionCount": action_count,
            "searchDepth": search_depth,
            "stepCount": step_count,
            "handoffCount": handoff_count,
            "handoffEfficiency": round(handoff_efficiency, 6),
            "toolSequenceLength": len(tool_sequence),
            "repeatedToolCount": repeated_tool_count,
            "toolChurnScore": round(tool_churn_score, 6),
            REASONING_PATH_EFFICIENCY_SIGNAL_NAME: reasoning_path_efficiency_score,
        },
    }


def _episode_pattern_signature(
    episode: dict[str, Any],
    classification: str,
) -> tuple[str, str, int, tuple[str, ...], tuple[str, ...]]:
    summary = episode["summary"]
    source_kinds = tuple(sorted(str(key) for key in (summary.get("sourceKindCounts") or {}).keys()))
    tool_names = tuple(str(tool_name) for tool_name in (summary.get("toolSequence") or []))
    terminal_status = str(summary.get("terminalStatus") or "unknown")
    handoff_count = int(summary.get("handoffCount") or 0)
    return classification, terminal_status, handoff_count, source_kinds, tool_names


def _episode_policy_candidates(
    ranked_patterns: list[
        tuple[
            tuple[str, str, int, tuple[str, ...], tuple[str, ...]],
            list[dict[str, Any]],
        ]
    ],
) -> list[dict[str, Any]]:
    policy_candidates: list[dict[str, Any]] = []
    policy_index = 1

    for _signature, entries in ranked_patterns:
        sample = entries[0]
        observed_count = len(entries)
        example_candidate_ids = sorted({str(entry["candidateId"]) for entry in entries})
        constraints = {
            "maxSearchDepth": int(sample["searchDepth"]),
            "maxActionCount": int(sample["actionCount"]),
        }
        learning_score = max(float(entry["learningScore"]) for entry in entries)
        tool_sequence = [str(tool_name) for tool_name in (sample.get("toolSequence") or [])]
        tool_names = [str(tool_name) for tool_name in (sample.get("toolNames") or [])]
        classification = str(sample["classification"])

        if classification == "successful_path" and tool_sequence:
            policy_candidates.append(
                {
                    "policyId": f"episode-policy-{policy_index:02d}",
                    "kind": "preferred_tool_sequence",
                    "classification": classification,
                    "observedCount": observed_count,
                    "exampleCandidateIds": example_candidate_ids,
                    "sourceKinds": list(sample["sourceKinds"]),
                    "handoffCount": int(sample.get("handoffCount") or 0),
                    "toolNames": tool_names,
                    "toolSequence": tool_sequence,
                    "terminalStatus": sample["terminalStatus"],
                    "constraints": constraints,
                    "learningScore": learning_score,
                    REASONING_PATH_EFFICIENCY_SIGNAL_NAME: float(
                        sample.get(REASONING_PATH_EFFICIENCY_SIGNAL_NAME) or 0.0
                    ),
                    "provenance": deepcopy(sample.get("provenance") or {}),
                    "factors": deepcopy(sample.get("factors") or {}),
                    "rationale": "Prefer the observed successful tool sequence for similar paths.",
                }
            )
            policy_index += 1
            continue

        if classification in {"failure_path", "warning_path"} and tool_names:
            policy_candidates.append(
                {
                    "policyId": f"episode-policy-{policy_index:02d}",
                    "kind": "escalation_trigger",
                    "classification": classification,
                    "observedCount": observed_count,
                    "exampleCandidateIds": example_candidate_ids,
                    "sourceKinds": list(sample["sourceKinds"]),
                    "handoffCount": int(sample.get("handoffCount") or 0),
                    "triggerTools": tool_names,
                    "terminalStatus": sample["terminalStatus"],
                    "constraints": constraints,
                    "learningScore": learning_score,
                    REASONING_PATH_EFFICIENCY_SIGNAL_NAME: float(
                        sample.get(REASONING_PATH_EFFICIENCY_SIGNAL_NAME) or 0.0
                    ),
                    "provenance": deepcopy(sample.get("provenance") or {}),
                    "factors": deepcopy(sample.get("factors") or {}),
                    "rationale": (
                        "Escalate or branch away when this observed tool path ends in failure "
                        "or warning."
                    ),
                }
            )
            policy_index += 1

        if len(policy_candidates) >= 5:
            break

    return policy_candidates


def _episode_learning_summary(
    episodes: list[dict[str, Any]],
    trajectories: list[dict[str, Any]],
    candidate_records_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    trajectory_by_candidate_id = {
        trajectory["candidateId"]: trajectory for trajectory in trajectories
    }
    scored_paths: list[dict[str, Any]] = []
    pattern_buckets: dict[
        tuple[str, str, int, tuple[str, ...], tuple[str, ...]],
        list[dict[str, Any]],
    ] = {}

    for episode in episodes:
        candidate_id = episode["candidateId"]
        candidate_record = candidate_records_by_id.get(candidate_id)
        trajectory = trajectory_by_candidate_id.get(candidate_id)
        if candidate_record is None or trajectory is None:
            continue

        shadow_scores = _episode_shadow_learning_scores(
            candidate_record,
            trajectory,
            episode,
        )
        summary = episode["summary"]
        provenance = _episode_trace_provenance(summary)
        path_summary = {
            "episodeId": episode["episodeId"],
            "trajectoryId": episode["trajectoryId"],
            "candidateId": candidate_id,
            "classification": shadow_scores["classification"],
            "learningScore": shadow_scores["learningScore"],
            "qualityScore": shadow_scores["qualityScore"],
            "efficiencyScore": shadow_scores["efficiencyScore"],
            REASONING_PATH_EFFICIENCY_SIGNAL_NAME: shadow_scores[
                REASONING_PATH_EFFICIENCY_SIGNAL_NAME
            ],
            "terminalStatus": summary.get("terminalStatus"),
            "matchedRecordCount": int(summary.get("matchedRecordCount") or 0),
            "handoffCount": int(summary.get("handoffCount") or 0),
            "searchDepth": int(trajectory.get("searchDepth") or 0),
            "actionCount": len(trajectory.get("actionSequence") or []),
            "sourceKinds": sorted(
                str(key) for key in (summary.get("sourceKindCounts") or {}).keys()
            ),
            "toolNames": [str(tool_name) for tool_name in (summary.get("toolNames") or [])],
            "toolSequence": [str(tool_name) for tool_name in (summary.get("toolSequence") or [])],
            "provenance": provenance,
            "factors": deepcopy(shadow_scores["factors"]),
            "selectedAsBest": bool(trajectory["outcome"].get("selectedAsBest")),
        }
        scored_paths.append(path_summary)

        if path_summary["matchedRecordCount"] == 0:
            continue
        signature = _episode_pattern_signature(episode, path_summary["classification"])
        pattern_buckets.setdefault(signature, []).append(path_summary)

    ranked_paths = sorted(
        scored_paths,
        key=lambda path: (
            -int(path["matchedRecordCount"] > 0),
            -float(path["learningScore"]),
            -float(path["qualityScore"]),
            -float(path["efficiencyScore"]),
            int(path["searchDepth"]),
            int(path["actionCount"]),
            str(path["candidateId"]),
        ),
    )
    top_observed_paths = ranked_paths[:5]

    ranked_patterns = sorted(
        pattern_buckets.items(),
        key=lambda item: (
            -len(item[1]),
            -max(float(entry["learningScore"]) for entry in item[1]),
            item[0],
        ),
    )
    benchmark_candidates: list[dict[str, Any]] = []
    for index, (_signature, entries) in enumerate(ranked_patterns[:5], start=1):
        sample = entries[0]
        kind = (
            "episode_failure_regression"
            if sample["classification"] in {"failure_path", "warning_path"}
            else "episode_success_guard"
        )
        benchmark_candidates.append(
            {
                "suggestionId": f"episode-benchmark-{index:02d}",
                "kind": kind,
                "classification": sample["classification"],
                "observedCount": len(entries),
                "learningScore": max(float(entry["learningScore"]) for entry in entries),
                "exampleCandidateIds": sorted({str(entry["candidateId"]) for entry in entries}),
                "sourceKinds": list(sample["sourceKinds"]),
                "handoffCount": int(sample.get("handoffCount") or 0),
                "toolNames": list(sample["toolNames"]),
                "terminalStatus": sample["terminalStatus"],
                REASONING_PATH_EFFICIENCY_SIGNAL_NAME: float(
                    sample.get(REASONING_PATH_EFFICIENCY_SIGNAL_NAME) or 0.0
                ),
                "provenance": deepcopy(sample.get("provenance") or {}),
                "factors": deepcopy(sample.get("factors") or {}),
                "rationale": (
                    "Preserve the observed successful path pattern."
                    if kind == "episode_success_guard"
                    else "Add a regression guard for the observed failing path pattern."
                ),
            }
        )

    evidence_backed_paths = [path for path in ranked_paths if int(path["matchedRecordCount"]) > 0]
    mutation_seed_candidates: list[dict[str, Any]] = []
    for index, path in enumerate(evidence_backed_paths[:5], start=1):
        source_candidate_record = candidate_records_by_id.get(path["candidateId"])
        if path["classification"] == "successful_path":
            kind = "reinforce_success_path"
            rationale = "Promote this observed successful path as a future mutation seed."
        elif path["classification"] in {"failure_path", "warning_path"}:
            kind = "avoid_failure_path"
            rationale = "Use this observed failing path to shape a future avoidance mutation."
        else:
            kind = "investigate_observed_path"
            rationale = "Investigate this observed path before turning it into a mutation."
        mutation_seed_candidates.append(
            {
                "seedId": f"episode-mutation-seed-{index:02d}",
                "kind": kind,
                "candidateId": path["candidateId"],
                "episodeId": path["episodeId"],
                "sourceMutationId": (
                    source_candidate_record.get("mutationId")
                    if source_candidate_record is not None
                    else None
                ),
                "sourceKinds": list(path["sourceKinds"]),
                "handoffCount": int(path.get("handoffCount") or 0),
                "toolNames": list(path["toolNames"]),
                "targetSearchDepth": int(path["searchDepth"]),
                "targetActionCount": int(path["actionCount"]),
                "learningScore": float(path["learningScore"]),
                REASONING_PATH_EFFICIENCY_SIGNAL_NAME: float(
                    path.get(REASONING_PATH_EFFICIENCY_SIGNAL_NAME) or 0.0
                ),
                "provenance": deepcopy(path.get("provenance") or {}),
                "factors": deepcopy(path.get("factors") or {}),
                "rationale": rationale,
            }
        )

    policy_candidates = _episode_policy_candidates(ranked_patterns)

    transcript_backed_path_count = sum(
        1
        for path in evidence_backed_paths
        if bool((path.get("provenance") or {}).get("transcriptBacked"))
    )
    handoff_backed_path_count = sum(
        1
        for path in evidence_backed_paths
        if bool((path.get("provenance") or {}).get("handoffBacked"))
    )
    best_reasoning_path_efficiency = max(
        (
            float(path.get(REASONING_PATH_EFFICIENCY_SIGNAL_NAME) or 0.0)
            for path in evidence_backed_paths
        ),
        default=0.0,
    )

    return {
        "mode": "shadow_only",
        "episodeCount": len(episodes),
        "evidenceBackedEpisodeCount": len(evidence_backed_paths),
        "reasoningPathSignal": {
            "name": REASONING_PATH_EFFICIENCY_SIGNAL_NAME,
            "sourceBackedPathCount": len(evidence_backed_paths),
            "transcriptBackedPathCount": transcript_backed_path_count,
            "handoffBackedPathCount": handoff_backed_path_count,
            "bestObservedScore": round(best_reasoning_path_efficiency, 6),
        },
        "topObservedPaths": top_observed_paths,
        "benchmarkCandidates": benchmark_candidates,
        "mutationSeedCandidates": mutation_seed_candidates,
        "policyCandidates": policy_candidates,
    }


def _learning_benchmark_drafts_payload(
    learning_summary: dict[str, Any],
    *,
    experiment: dict[str, Any],
    trace_artifact: dict[str, Any],
) -> dict[str, Any]:
    draft_fragments: list[dict[str, Any]] = []
    for index, candidate in enumerate(learning_summary.get("benchmarkCandidates") or [], start=1):
        fragment_name = f"episode-{_candidate_id_slug(candidate['kind'])}-{index:02d}"
        draft_fragments.append(
            {
                "draftId": f"benchmark-fragment-{index:02d}",
                "status": "draft",
                "reviewRequired": True,
                "sourceSuggestionId": candidate["suggestionId"],
                "kind": candidate["kind"],
                "classification": candidate["classification"],
                "fragment": {
                    "name": fragment_name,
                    "title": f"Episode-derived benchmark fragment {index}",
                    "goal": candidate["rationale"],
                    "observedCount": int(candidate["observedCount"]),
                    "learningScore": float(candidate["learningScore"]),
                    REASONING_PATH_EFFICIENCY_SIGNAL_NAME: float(
                        candidate.get(REASONING_PATH_EFFICIENCY_SIGNAL_NAME) or 0.0
                    ),
                    "exampleCandidateIds": list(candidate["exampleCandidateIds"]),
                    "handoffCount": int(candidate.get("handoffCount") or 0),
                    "traceProvenance": deepcopy(candidate.get("provenance") or {}),
                    "factorSummary": deepcopy(candidate.get("factors") or {}),
                    "suggestedChecks": [
                        {
                            "id": f"{fragment_name}-check",
                            "kind": "episode_observation_guard",
                            "intent": candidate["rationale"],
                            "sourceKinds": list(candidate["sourceKinds"]),
                            "toolNames": list(candidate["toolNames"]),
                            "handoffCount": int(candidate.get("handoffCount") or 0),
                            "terminalStatus": candidate["terminalStatus"],
                            "traceProvenance": deepcopy(candidate.get("provenance") or {}),
                        }
                    ],
                },
            }
        )

    return {
        "type": "AutoAgentBenchmarkDrafts",
        "mode": "review_only",
        "shadowMode": True,
        "source": {
            "experimentName": experiment["name"],
            "benchmarkPath": experiment["benchmarkPath"].as_posix(),
            "tracePath": trace_artifact["actualPath"],
        },
        "draftFragmentCount": len(draft_fragments),
        "draftFragments": draft_fragments,
    }


def _learning_mutation_drafts_payload(
    learning_summary: dict[str, Any],
    *,
    experiment: dict[str, Any],
    trace_artifact: dict[str, Any],
) -> dict[str, Any]:
    draft_entries: list[dict[str, Any]] = []
    for index, seed in enumerate(learning_summary.get("mutationSeedCandidates") or [], start=1):
        entry_id = f"episode-{_candidate_id_slug(seed['kind'])}-{index:02d}"
        draft_entries.append(
            {
                "draftId": f"mutation-draft-{index:02d}",
                "status": "draft",
                "reviewRequired": True,
                "sourceSeedId": seed["seedId"],
                "kind": seed["kind"],
                "entry": {
                    "id": entry_id,
                    "description": seed["rationale"],
                    "intent": seed["kind"],
                    "sourceCandidateId": seed["candidateId"],
                    "sourceEpisodeId": seed["episodeId"],
                    "sourceMutationId": seed.get("sourceMutationId"),
                    "preferredSourceKinds": list(seed["sourceKinds"]),
                    "preferredTools": list(seed["toolNames"]),
                    "handoffCount": int(seed.get("handoffCount") or 0),
                    "constraints": {
                        "maxSearchDepth": int(seed["targetSearchDepth"]),
                        "maxActionCount": int(seed["targetActionCount"]),
                    },
                    "learningScore": float(seed["learningScore"]),
                    REASONING_PATH_EFFICIENCY_SIGNAL_NAME: float(
                        seed.get(REASONING_PATH_EFFICIENCY_SIGNAL_NAME) or 0.0
                    ),
                    "traceProvenance": deepcopy(seed.get("provenance") or {}),
                    "factorSummary": deepcopy(seed.get("factors") or {}),
                },
            }
        )

    return {
        "type": "AutoAgentMutationDrafts",
        "mode": "review_only",
        "shadowMode": True,
        "source": {
            "experimentName": experiment["name"],
            "mutationCatalogPath": experiment["mutationCatalogPath"].as_posix(),
            "tracePath": trace_artifact["actualPath"],
        },
        "draftEntryCount": len(draft_entries),
        "draftEntries": draft_entries,
    }


def _guarded_learning_min_observed_count(experiment: dict[str, Any]) -> int:
    return max(1, int(experiment["continuousPolicy"].get("minSignalCount") or 0))


def _guarded_benchmark_review_entries(
    benchmark_drafts_payload: dict[str, Any],
    *,
    min_observed_count: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    review_entries: list[dict[str, Any]] = []
    accepted_draft_ids: list[str] = []

    for draft in benchmark_drafts_payload.get("draftFragments") or []:
        if not isinstance(draft, dict):
            continue
        draft_id = str(draft.get("draftId") or "")
        fragment: dict[str, Any] = {}
        raw_fragment = draft.get("fragment")
        if isinstance(raw_fragment, dict):
            fragment = raw_fragment
        observed_count = int(fragment.get("observedCount") or 0)
        observed_count_pass = observed_count >= min_observed_count
        decision_rationale = {
            "observedCount": observed_count,
            "observedCountThreshold": min_observed_count,
            "observedCountPass": observed_count_pass,
            "observedCountDelta": observed_count - min_observed_count,
            "blockedByFactors": [] if observed_count_pass else ["observedCount"],
            "primaryBlockedFactor": None if observed_count_pass else "observedCount",
        }
        if observed_count_pass:
            decision = "accept"
            accepted_draft_ids.append(draft_id)
            notes = (
                "Auto-staged by guarded promotion because observedCount "
                f"{observed_count} met the threshold {min_observed_count}."
            )
        else:
            decision = "defer"
            notes = (
                "Deferred by guarded promotion because observedCount "
                f"{observed_count} is below the threshold {min_observed_count}."
            )
        review_entries.append(
            {
                "draftId": draft_id,
                "stagedDecision": decision,
                "decision": decision,
                "decisionRationale": decision_rationale,
                "notes": notes,
            }
        )

    return review_entries, accepted_draft_ids


def _guarded_policy_review_entries(
    policy_drafts_payload: dict[str, Any],
    *,
    min_observed_count: int,
    min_learning_score: float,
) -> tuple[list[dict[str, Any]], list[str]]:
    review_entries: list[dict[str, Any]] = []
    accepted_draft_ids: list[str] = []

    for draft in policy_drafts_payload.get("draftEntries") or []:
        if not isinstance(draft, dict):
            continue
        draft_id = str(draft.get("draftId") or "")
        entry: dict[str, Any] = {}
        raw_entry = draft.get("entry")
        if isinstance(raw_entry, dict):
            entry = raw_entry
        observed_count = int(entry.get("observedCount") or 0)
        learning_score = float(entry.get("learningScore") or 0.0)
        observed_count_pass = observed_count >= min_observed_count
        learning_score_pass = learning_score >= min_learning_score
        blocked_by_factors: list[str] = []
        if not observed_count_pass:
            blocked_by_factors.append("observedCount")
        if not learning_score_pass:
            blocked_by_factors.append("learningScore")
        accepted = observed_count_pass and learning_score_pass
        decision_rationale = {
            "observedCount": observed_count,
            "observedCountThreshold": min_observed_count,
            "observedCountPass": observed_count_pass,
            "observedCountDelta": observed_count - min_observed_count,
            "learningScore": learning_score,
            "learningScoreThreshold": min_learning_score,
            "learningScorePass": learning_score_pass,
            "learningScoreDelta": learning_score - min_learning_score,
            "blockedByFactors": blocked_by_factors,
            "primaryBlockedFactor": blocked_by_factors[0] if blocked_by_factors else None,
        }
        if accepted:
            decision = "accept"
            accepted_draft_ids.append(draft_id)
            notes = (
                "Auto-staged by guarded promotion because observedCount "
                f"{observed_count} met the threshold {min_observed_count} and "
                f"learningScore {learning_score:.3f} met the threshold "
                f"{min_learning_score:.3f}."
            )
        else:
            decision = "defer"
            failure_reasons: list[str] = []
            if not observed_count_pass:
                failure_reasons.append(
                    "observedCount "
                    f"{observed_count} is below the threshold {min_observed_count}"
                )
            if not learning_score_pass:
                failure_reasons.append(
                    "learningScore "
                    f"{learning_score:.3f} is below the threshold {min_learning_score:.3f}"
                )
            notes = "Deferred by guarded promotion because " + " and ".join(failure_reasons) + "."
        review_entries.append(
            {
                "draftId": draft_id,
                "stagedDecision": decision,
                "decision": decision,
                "decisionRationale": decision_rationale,
                "notes": notes,
            }
        )

    return review_entries, accepted_draft_ids


def _guarded_learning_promotion(
    experiment: dict[str, Any],
    benchmark_drafts_payload: dict[str, Any],
    policy_drafts_payload: dict[str, Any],
    *,
    run_root: Path,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    min_observed_count = _guarded_learning_min_observed_count(experiment)
    min_policy_learning_score = GUARDED_AUTO_PROMOTION_MIN_POLICY_LEARNING_SCORE
    benchmark_review_entries, accepted_benchmark_draft_ids = _guarded_benchmark_review_entries(
        benchmark_drafts_payload,
        min_observed_count=min_observed_count,
    )
    policy_review_entries, accepted_policy_draft_ids = _guarded_policy_review_entries(
        policy_drafts_payload,
        min_observed_count=min_observed_count,
        min_learning_score=min_policy_learning_score,
    )

    blocked_reasons: list[str] = []
    if not experiment["continuationEligibility"]["eligible"]:
        blocked_reasons.extend(experiment["continuationEligibility"]["blockedReasons"])
    if not experiment["continuationReadiness"]["ready"]:
        blocked_reasons.extend(experiment["continuationReadiness"]["blockedReasons"])
    if not experiment["governedApprovalMetadata"]["ready"]:
        if experiment["governedApprovalMetadata"]["blockedReasons"]:
            blocked_reasons.extend(experiment["governedApprovalMetadata"]["blockedReasons"])
        else:
            blocked_reasons.append("approval_metadata_not_ready")
    if not benchmark_review_entries and not policy_review_entries:
        blocked_reasons.append("no_benchmark_or_policy_drafts")
    blocked_reasons = list(dict.fromkeys(blocked_reasons))

    artifact_path = run_root / "guarded-learning-review.generated.json"
    summary = (
        "Guarded learning promotion is blocked until continuation and approval gates are ready."
        if blocked_reasons
        else "Generated a guarded learning review manifest for benchmark and policy drafts."
    )
    recommended_action = (
        experiment["governedApprovalMetadata"]["recommendedAction"]
        if blocked_reasons
        else (
            "Review the generated learning review manifest and run "
            "--import-learning-review only after a maintainer confirms the staged decisions."
        )
    )

    promotion_summary = {
        "ready": not blocked_reasons,
        "status": "staged_for_review" if not blocked_reasons else "blocked",
        "blockedReasons": blocked_reasons,
        "mode": "generated_review_manifest",
        "reviewRequired": True,
        "artifactPath": artifact_path.as_posix() if not blocked_reasons else None,
        "minObservedCount": min_observed_count,
        "minPolicyLearningScore": min_policy_learning_score,
        "acceptedBenchmarkDraftCount": len(accepted_benchmark_draft_ids),
        "acceptedPolicyDraftCount": len(accepted_policy_draft_ids),
        "deferredBenchmarkDraftCount": (
            len(benchmark_review_entries) - len(accepted_benchmark_draft_ids)
        ),
        "deferredPolicyDraftCount": len(policy_review_entries) - len(accepted_policy_draft_ids),
        "acceptedBenchmarkDraftIds": accepted_benchmark_draft_ids,
        "acceptedPolicyDraftIds": accepted_policy_draft_ids,
        "summary": summary,
        "recommendedAction": recommended_action,
    }
    if blocked_reasons:
        return promotion_summary, None

    manifest = {
        "type": "AutoAgentLearningReview",
        "mode": "guarded_auto_promotion",
        "reviewer": GUARDED_AUTO_PROMOTION_REVIEWER,
        "reviewedAt": None,
        "summary": (
            "Auto-generated guarded learning review. Human approval is still required before "
            "importing any staged decisions."
        ),
        "guardrails": {
            "continuationEligibilityStatus": experiment["continuationEligibility"]["status"],
            "continuationReadinessStatus": experiment["continuationReadiness"]["status"],
            "governedApprovalStatus": experiment["governedApprovalMetadata"]["status"],
            "minObservedCount": min_observed_count,
            "minPolicyLearningScore": min_policy_learning_score,
            "reviewRequired": True,
        },
        "benchmarkDrafts": benchmark_review_entries,
        "mutationDrafts": [],
        "policyDrafts": policy_review_entries,
    }
    return promotion_summary, manifest


def _learning_policy_drafts_payload(
    learning_summary: dict[str, Any],
    *,
    experiment: dict[str, Any],
    trace_artifact: dict[str, Any],
) -> dict[str, Any]:
    draft_entries: list[dict[str, Any]] = []
    for index, candidate in enumerate(learning_summary.get("policyCandidates") or [], start=1):
        entry_id = f"episode-policy-{_candidate_id_slug(candidate['kind'])}-{index:02d}"
        entry: dict[str, Any] = {
            "id": entry_id,
            "description": candidate["rationale"],
            "intent": candidate["kind"],
            "classification": candidate["classification"],
            "sourceCandidateIds": list(candidate["exampleCandidateIds"]),
            "preferredSourceKinds": list(candidate["sourceKinds"]),
            "handoffCount": int(candidate.get("handoffCount") or 0),
            "terminalStatus": candidate["terminalStatus"],
            "constraints": deepcopy(candidate["constraints"]),
            "learningScore": float(candidate["learningScore"]),
            REASONING_PATH_EFFICIENCY_SIGNAL_NAME: float(
                candidate.get(REASONING_PATH_EFFICIENCY_SIGNAL_NAME) or 0.0
            ),
            "observedCount": int(candidate["observedCount"]),
            "traceProvenance": deepcopy(candidate.get("provenance") or {}),
            "factorSummary": deepcopy(candidate.get("factors") or {}),
        }
        if candidate["kind"] == "preferred_tool_sequence":
            entry["preferredToolSequence"] = list(candidate["toolSequence"])
            entry["preferredTools"] = list(candidate["toolNames"])
        elif candidate["kind"] == "escalation_trigger":
            entry["triggerTools"] = list(candidate["triggerTools"])

        draft_entries.append(
            {
                "draftId": f"policy-draft-{index:02d}",
                "status": "draft",
                "reviewRequired": True,
                "sourcePolicyId": candidate["policyId"],
                "kind": candidate["kind"],
                "entry": entry,
            }
        )

    return {
        "type": "AutoAgentPolicyDrafts",
        "mode": "review_only",
        "shadowMode": True,
        "source": {
            "experimentName": experiment["name"],
            "tracePath": trace_artifact["actualPath"],
        },
        "draftEntryCount": len(draft_entries),
        "draftEntries": draft_entries,
    }


def _ordered_tool_sequence_match(
    observed_tool_sequence: list[str],
    expected_tool_sequence: list[str],
) -> bool:
    if not expected_tool_sequence:
        return False
    expected = [tool_name.casefold() for tool_name in expected_tool_sequence]
    observed = [tool_name.casefold() for tool_name in observed_tool_sequence]
    expected_index = 0
    for tool_name in observed:
        if tool_name != expected[expected_index]:
            continue
        expected_index += 1
        if expected_index == len(expected):
            return True
    return False


def _reviewed_policy_constraints_match(
    policy: dict[str, Any],
    *,
    trajectory: dict[str, Any],
    episode: dict[str, Any],
) -> bool:
    raw_constraints = policy.get("constraints")
    constraints = raw_constraints if isinstance(raw_constraints, dict) else {}
    max_search_depth = constraints.get("maxSearchDepth")
    if max_search_depth is not None and int(trajectory.get("searchDepth") or 0) > int(
        max_search_depth
    ):
        return False
    max_action_count = constraints.get("maxActionCount")
    if max_action_count is not None and len(trajectory.get("actionSequence") or []) > int(
        max_action_count
    ):
        return False

    summary = episode["summary"]
    expected_source_kinds = _non_empty_scalar_texts(
        _as_list(policy.get("preferredSourceKinds") or policy.get("sourceKinds"))
    )
    observed_source_kinds = {
        str(key).casefold() for key in (summary.get("sourceKindCounts") or {}).keys() if str(key)
    }
    if expected_source_kinds and not all(
        source_kind.casefold() in observed_source_kinds for source_kind in expected_source_kinds
    ):
        return False

    expected_terminal_status = _first_non_empty_scalar([policy.get("terminalStatus")])
    if expected_terminal_status is None:
        return True
    return (
        str(summary.get("terminalStatus") or "").casefold()
        == str(expected_terminal_status).casefold()
    )


def _reviewed_policy_learning_score(policy: dict[str, Any]) -> float:
    try:
        return max(0.0, min(1.0, float(policy.get("learningScore") or 0.0)))
    except (TypeError, ValueError):
        return 0.0


def _mutation_identity(mutation: dict[str, Any], catalog_index: int) -> str:
    return str(mutation.get("id") or f"candidate-{catalog_index}")


def _mutation_plan_token(mutation: dict[str, Any], catalog_index: int) -> str:
    return f"{catalog_index}:{_mutation_identity(mutation, catalog_index)}"


def _policy_source_candidate_ids(policy: dict[str, Any]) -> list[str]:
    source_candidate_ids: list[str] = []
    source_candidate_ids.extend(_non_empty_scalar_texts(_as_list(policy.get("sourceCandidateIds"))))
    source_candidate_id = _first_non_empty_scalar([policy.get("sourceCandidateId")])
    if source_candidate_id is not None:
        source_candidate_ids.append(str(source_candidate_id))
    return sorted(dict.fromkeys(source_candidate_ids))


def _mutation_source_candidate_ids(mutation: dict[str, Any]) -> list[str]:
    source_candidate_ids: list[str] = []
    source_candidate_ids.extend(
        _non_empty_scalar_texts(_as_list(mutation.get("sourceCandidateIds")))
    )
    source_candidate_id = _first_non_empty_scalar([mutation.get("sourceCandidateId")])
    if source_candidate_id is not None:
        source_candidate_ids.append(str(source_candidate_id))

    learning_import = mutation.get("learningImportMetadata")
    if isinstance(learning_import, dict):
        source_candidate_ids.extend(
            _non_empty_scalar_texts(_as_list(learning_import.get("sourceCandidateIds")))
        )
        imported_source_candidate_id = _first_non_empty_scalar(
            [learning_import.get("sourceCandidateId")]
        )
        if imported_source_candidate_id is not None:
            source_candidate_ids.append(str(imported_source_candidate_id))

    return sorted(dict.fromkeys(source_candidate_ids))


def _mutation_reviewed_policy_priority_context(
    mutation: dict[str, Any],
    *,
    reviewed_policy_runtime_state: dict[str, Any],
    reviewed_policy_runtime: dict[str, Any],
) -> dict[str, Any]:
    source_candidate_ids = _mutation_source_candidate_ids(mutation)
    context = {
        "enabled": bool(reviewed_policy_runtime_state.get("enabled")),
        "status": str(reviewed_policy_runtime_state.get("status") or "disabled"),
        "artifactPath": reviewed_policy_runtime_state.get("artifactPath"),
        "policyCount": int(reviewed_policy_runtime_state.get("activePolicyCount") or 0),
        "sourceCandidateIds": list(source_candidate_ids),
        "matchedPolicyCount": 0,
        "preferredSequenceMatchCount": 0,
        "escalationMatchCount": 0,
        "bonus": 0.0,
        "penalty": 0.0,
        "priorityScore": 0.0,
        "priorityStatus": "neutral",
        "matchedPolicyIds": [],
        "matchedPolicies": [],
    }
    if reviewed_policy_runtime_state.get("status") not in {"ready", "ready_empty"}:
        return context
    if not reviewed_policy_runtime_state.get("policies") or not source_candidate_ids:
        return context

    mutation_source_candidate_ids = {
        candidate_id.casefold() for candidate_id in source_candidate_ids if candidate_id
    }
    matched_policies: list[dict[str, Any]] = []
    preferred_bonus = 0.0
    escalation_penalty = 0.0
    preferred_sequence_match_count = 0
    escalation_match_count = 0

    for policy in reviewed_policy_runtime_state.get("policies") or []:
        if not isinstance(policy, dict):
            continue
        policy_id = str(policy.get("id") or "").strip()
        if not policy_id:
            continue
        policy_source_candidate_ids = _policy_source_candidate_ids(policy)
        if not policy_source_candidate_ids:
            continue
        matched_source_candidate_ids = [
            candidate_id
            for candidate_id in policy_source_candidate_ids
            if candidate_id.casefold() in mutation_source_candidate_ids
        ]
        if not matched_source_candidate_ids:
            continue

        policy_intent = str(policy.get("intent") or policy.get("kind") or "").strip()
        learning_score = _reviewed_policy_learning_score(policy)
        if policy_intent == "preferred_tool_sequence":
            effect = round(
                float(reviewed_policy_runtime["preferredSequenceBonus"]) * learning_score,
                6,
            )
            if effect <= 0:
                continue
            preferred_bonus = max(preferred_bonus, effect)
            preferred_sequence_match_count += 1
            matched_policies.append(
                {
                    "policyId": policy_id,
                    "intent": policy_intent,
                    "effectType": "bonus",
                    "effect": effect,
                    "learningScore": learning_score,
                    "matchedSourceCandidateIds": matched_source_candidate_ids,
                }
            )
        elif policy_intent == "escalation_trigger":
            effect = round(
                float(reviewed_policy_runtime["escalationPenalty"]) * learning_score,
                6,
            )
            if effect <= 0:
                continue
            escalation_penalty = max(escalation_penalty, effect)
            escalation_match_count += 1
            matched_policies.append(
                {
                    "policyId": policy_id,
                    "intent": policy_intent,
                    "effectType": "penalty",
                    "effect": effect,
                    "learningScore": learning_score,
                    "matchedSourceCandidateIds": matched_source_candidate_ids,
                }
            )

    priority_score = round(preferred_bonus - escalation_penalty, 6)
    if priority_score > 0:
        priority_status = "prioritized"
    elif priority_score < 0:
        priority_status = "deprioritized"
    else:
        priority_status = "neutral"

    context.update(
        {
            "matchedPolicyCount": len(matched_policies),
            "preferredSequenceMatchCount": preferred_sequence_match_count,
            "escalationMatchCount": escalation_match_count,
            "bonus": round(preferred_bonus, 6),
            "penalty": round(escalation_penalty, 6),
            "priorityScore": priority_score,
            "priorityStatus": priority_status,
            "matchedPolicyIds": [entry["policyId"] for entry in matched_policies],
            "matchedPolicies": matched_policies,
        }
    )
    return context


def _mutation_priority_sort_key(entry: dict[str, Any]) -> tuple[int, float, float, int, str]:
    context = entry["priorityContext"]
    priority_score = float(context.get("priorityScore") or 0.0)
    if priority_score > 0:
        category = 0
    elif priority_score < 0:
        category = 2
    else:
        category = 1
    return (
        category,
        -float(context.get("bonus") or 0.0),
        float(context.get("penalty") or 0.0),
        int(entry["catalogIndex"]),
        str(entry["mutationId"]),
    )


def _prioritized_mutation_plan(
    mutations: list[dict[str, Any]],
    *,
    reviewed_policy_runtime_state: dict[str, Any],
    reviewed_policy_runtime: dict[str, Any],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for catalog_index, mutation in enumerate(mutations, start=1):
        mutation_id = _mutation_identity(mutation, catalog_index)
        priority_context = _mutation_reviewed_policy_priority_context(
            mutation,
            reviewed_policy_runtime_state=reviewed_policy_runtime_state,
            reviewed_policy_runtime=reviewed_policy_runtime,
        )
        entries.append(
            {
                "catalogIndex": catalog_index,
                "planToken": _mutation_plan_token(mutation, catalog_index),
                "mutationId": mutation_id,
                "description": str(mutation.get("description") or "candidate mutation"),
                "priorityContext": priority_context,
                "mutation": mutation,
            }
        )

    ordered_entries = sorted(entries, key=_mutation_priority_sort_key)
    mutation_plan: list[dict[str, Any]] = []
    for planned_index, entry in enumerate(ordered_entries, start=1):
        priority_context = entry["priorityContext"]
        mutation_plan.append(
            {
                "plannedIndex": planned_index,
                "catalogIndex": int(entry["catalogIndex"]),
                "planToken": entry["planToken"],
                "mutationId": entry["mutationId"],
                "description": entry["description"],
                "priorityStatus": priority_context["priorityStatus"],
                "priorityScore": float(priority_context["priorityScore"]),
                "bonus": float(priority_context["bonus"]),
                "penalty": float(priority_context["penalty"]),
                "matchedPolicyCount": int(priority_context["matchedPolicyCount"]),
                "matchedPolicyIds": list(priority_context["matchedPolicyIds"]),
                "sourceCandidateIds": list(priority_context["sourceCandidateIds"]),
            }
        )
    return mutation_plan


def _candidate_reviewed_policy_context(
    candidate_record: dict[str, Any],
    *,
    candidate_records_by_id: dict[str, dict[str, Any]],
    evidence_dataset: dict[str, Any] | None,
    trajectory: dict[str, Any],
    reviewed_policy_runtime_state: dict[str, Any],
    reviewed_policy_runtime: dict[str, Any],
) -> dict[str, Any]:
    context = {
        "enabled": bool(reviewed_policy_runtime_state.get("enabled")),
        "status": str(reviewed_policy_runtime_state.get("status") or "disabled"),
        "artifactPath": reviewed_policy_runtime_state.get("artifactPath"),
        "policyCount": int(reviewed_policy_runtime_state.get("activePolicyCount") or 0),
        "matchedPolicyCount": 0,
        "preferredSequenceMatchCount": 0,
        "escalationMatchCount": 0,
        "bonus": 0.0,
        "penalty": 0.0,
        "matchedPolicyIds": [],
        "matchedPolicies": [],
    }
    if reviewed_policy_runtime_state.get("status") not in {"ready", "ready_empty"}:
        return context
    if not reviewed_policy_runtime_state.get("policies"):
        return context

    episode = _candidate_trajectory_episode(
        candidate_record,
        candidate_records_by_id=candidate_records_by_id,
        evidence_dataset=evidence_dataset,
    )
    summary = episode["summary"]
    if int(summary.get("matchedRecordCount") or 0) < 1:
        return context

    observed_tool_sequence = [str(tool_name) for tool_name in (summary.get("toolSequence") or [])]
    observed_tool_names = [str(tool_name) for tool_name in (summary.get("toolNames") or [])]
    observed_tool_name_set = {tool_name.casefold() for tool_name in observed_tool_names}

    matched_policies: list[dict[str, Any]] = []
    preferred_bonus = 0.0
    escalation_penalty = 0.0
    preferred_sequence_match_count = 0
    escalation_match_count = 0

    for policy in reviewed_policy_runtime_state.get("policies") or []:
        if not isinstance(policy, dict):
            continue
        policy_id = str(policy.get("id") or "").strip()
        if not policy_id or not _reviewed_policy_constraints_match(
            policy,
            trajectory=trajectory,
            episode=episode,
        ):
            continue
        policy_intent = str(policy.get("intent") or policy.get("kind") or "").strip()
        learning_score = _reviewed_policy_learning_score(policy)
        if policy_intent == "preferred_tool_sequence":
            expected_tool_sequence = _non_empty_scalar_texts(
                _as_list(policy.get("preferredToolSequence") or policy.get("preferredTools"))
            )
            if not expected_tool_sequence or not _ordered_tool_sequence_match(
                observed_tool_sequence,
                expected_tool_sequence,
            ):
                continue
            effect = round(
                float(reviewed_policy_runtime["preferredSequenceBonus"]) * learning_score,
                6,
            )
            if effect <= 0:
                continue
            preferred_bonus = max(preferred_bonus, effect)
            preferred_sequence_match_count += 1
            matched_policies.append(
                {
                    "policyId": policy_id,
                    "intent": policy_intent,
                    "effectType": "bonus",
                    "effect": effect,
                    "learningScore": learning_score,
                }
            )
        elif policy_intent == "escalation_trigger":
            trigger_tools = {
                tool_name.casefold()
                for tool_name in _non_empty_scalar_texts(_as_list(policy.get("triggerTools")))
            }
            if not trigger_tools or not any(
                tool_name in observed_tool_name_set for tool_name in trigger_tools
            ):
                continue
            effect = round(
                float(reviewed_policy_runtime["escalationPenalty"]) * learning_score,
                6,
            )
            if effect <= 0:
                continue
            escalation_penalty = max(escalation_penalty, effect)
            escalation_match_count += 1
            matched_policies.append(
                {
                    "policyId": policy_id,
                    "intent": policy_intent,
                    "effectType": "penalty",
                    "effect": effect,
                    "learningScore": learning_score,
                }
            )

    context.update(
        {
            "matchedPolicyCount": len(matched_policies),
            "preferredSequenceMatchCount": preferred_sequence_match_count,
            "escalationMatchCount": escalation_match_count,
            "bonus": round(preferred_bonus, 6),
            "penalty": round(escalation_penalty, 6),
            "matchedPolicyIds": [entry["policyId"] for entry in matched_policies],
            "matchedPolicies": matched_policies,
        }
    )
    return context


def _annotate_candidate_trajectory_score(
    candidate_record: dict[str, Any],
    *,
    candidate_records_by_id: dict[str, dict[str, Any]],
    mutation_by_id: dict[str, dict[str, Any]],
    experiment: dict[str, Any],
    benchmark: dict[str, Any],
    evidence_dataset: dict[str, Any] | None,
    baseline_score: float,
    live_evaluation: dict[str, Any] | None = None,
    best_candidate_id: str | None = None,
    applied_best_variant: bool = False,
) -> None:
    evidence_context = _candidate_evidence_context(
        candidate_record,
        evidence_dataset,
        candidate_records_by_id=candidate_records_by_id,
    )
    trajectory = _candidate_trajectory(
        candidate_record,
        candidate_records_by_id=candidate_records_by_id,
        mutation_by_id=mutation_by_id,
        experiment=experiment,
        benchmark=benchmark,
        evidence_context=evidence_context,
        baseline_score=baseline_score,
        live_evaluation=live_evaluation or {"evaluatedCandidateIds": []},
        best_candidate_id=best_candidate_id,
        applied_best_variant=applied_best_variant,
    )
    reviewed_policy_context = _candidate_reviewed_policy_context(
        candidate_record,
        candidate_records_by_id=candidate_records_by_id,
        evidence_dataset=evidence_dataset,
        trajectory=trajectory,
        reviewed_policy_runtime_state=experiment.get("reviewedPolicyRuntimeState") or {},
        reviewed_policy_runtime=experiment["reviewedPolicyRuntime"],
    )
    trajectory["context"]["reviewedPolicies"] = deepcopy(reviewed_policy_context)
    ranking = _score_candidate_trajectory(trajectory)
    candidate_record["evaluation"]["trajectoryScore"] = ranking["score"]
    candidate_record["evaluation"]["trajectoryScoreBreakdown"] = ranking["components"]
    candidate_record["evaluation"]["trajectoryEvidenceContext"] = evidence_context
    candidate_record["evaluation"]["reviewedPolicyContext"] = reviewed_policy_context


def _refresh_candidate_rankings(
    candidate_records: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    *,
    mutation_by_id: dict[str, dict[str, Any]],
    experiment: dict[str, Any],
    benchmark: dict[str, Any],
    evidence_dataset: dict[str, Any] | None,
    baseline_score: float,
    live_evaluation: dict[str, Any] | None = None,
    best_candidate_id: str | None = None,
    applied_best_variant: bool = False,
) -> None:
    candidate_records_by_id = {record["candidateId"]: record for record in candidate_records}
    for record in candidate_records:
        _annotate_candidate_trajectory_score(
            record,
            candidate_records_by_id=candidate_records_by_id,
            mutation_by_id=mutation_by_id,
            experiment=experiment,
            benchmark=benchmark,
            evidence_dataset=evidence_dataset,
            baseline_score=baseline_score,
            live_evaluation=live_evaluation,
            best_candidate_id=best_candidate_id,
            applied_best_variant=applied_best_variant,
        )

    rows_by_candidate_id = {row["candidateId"]: row for row in rows}
    for record in candidate_records:
        row = rows_by_candidate_id.get(record["candidateId"])
        if row is None:
            continue
        row["trajectoryScore"] = _evaluation_trajectory_score(record["evaluation"])


def _candidate_trajectory(
    candidate_record: dict[str, Any],
    *,
    candidate_records_by_id: dict[str, dict[str, Any]],
    mutation_by_id: dict[str, dict[str, Any]],
    experiment: dict[str, Any],
    benchmark: dict[str, Any],
    evidence_context: dict[str, Any] | None,
    baseline_score: float,
    live_evaluation: dict[str, Any],
    best_candidate_id: str | None,
    applied_best_variant: bool,
) -> dict[str, Any]:
    candidate_id = candidate_record["candidateId"]
    parent_candidate_id = candidate_record.get("parentCandidateId")
    mutation_id = candidate_record.get("mutationId")
    mutation = mutation_by_id.get(str(mutation_id)) if mutation_id is not None else None
    evaluation = candidate_record["evaluation"]
    score = float(evaluation["score"])
    parent_score = None
    if parent_candidate_id is not None:
        parent_record = candidate_records_by_id.get(parent_candidate_id)
        if parent_record is not None:
            parent_score = float(parent_record["evaluation"]["score"])

    return {
        "trajectoryId": _trace_trajectory_id(candidate_id),
        "kind": "candidate_journey",
        "candidateId": candidate_id,
        "parentCandidateId": parent_candidate_id,
        "mutationId": candidate_record.get("mutationId"),
        "description": candidate_record["description"],
        "searchDepth": int(candidate_record.get("searchDepth", 0)),
        "status": candidate_record["status"],
        "context": {
            "experimentName": experiment["name"],
            "experimentDescription": experiment["description"],
            "benchmarkId": benchmark.get("id"),
            "primaryTargetId": experiment["primaryTargetId"],
            "candidatePath": candidate_record["path"].as_posix(),
            "touchedTargets": list(candidate_record.get("touchedTargets") or []),
            "lineageCandidateIds": _candidate_lineage_ids(candidate_records_by_id, candidate_id),
            "evidence": deepcopy(
                evidence_context
                if evidence_context is not None
                else evaluation.get("trajectoryEvidenceContext") or {}
            ),
            "reviewedPolicies": deepcopy(evaluation.get("reviewedPolicyContext") or {}),
            "mutation": (
                {
                    "id": mutation.get("id"),
                    "description": mutation.get("description"),
                    "operationCount": len(mutation.get("operations") or []),
                }
                if mutation is not None
                else None
            ),
        },
        "actionSequence": _trajectory_action_sequence(
            mutation,
            primary_target_id=experiment["primaryTargetId"],
        ),
        "validationAttempts": _trajectory_validation_attempts(
            candidate_id,
            evaluation,
            benchmark,
            live_evaluation,
        ),
        "ranking": {
            "trajectoryScore": _evaluation_trajectory_score(evaluation),
            "signals": deepcopy(evaluation.get("trajectoryScoreBreakdown") or {}),
        },
        "outcome": {
            "status": candidate_record["status"],
            "score": score,
            "deltaFromBaseline": round(score - baseline_score, 6),
            "deltaFromParent": round(score - parent_score, 6) if parent_score is not None else None,
            "passedChecks": int(evaluation["passedChecks"]),
            "totalChecks": int(evaluation["totalChecks"]),
            "complexity": deepcopy(evaluation["complexity"]),
            "selectedAsBest": best_candidate_id is not None and candidate_id == best_candidate_id,
            "appliedBestVariant": bool(applied_best_variant)
            and best_candidate_id is not None
            and candidate_id == best_candidate_id,
        },
    }


def _build_autoagent_trace(
    experiment_path: Path,
    experiment: dict[str, Any],
    benchmark: dict[str, Any],
    mutations: list[dict[str, Any]],
    result: dict[str, Any],
    candidate_records: list[dict[str, Any]],
    frontier_snapshots: list[dict[str, Any]],
    evidence_dataset: dict[str, Any],
    benchmark_drafts_artifact: dict[str, Any],
    mutation_drafts_artifact: dict[str, Any],
    policy_drafts_artifact: dict[str, Any],
    trace_artifact: dict[str, Any],
) -> dict[str, Any]:
    candidate_records_by_id = {record["candidateId"]: record for record in candidate_records}
    mutation_by_id = _mutation_catalog_by_id(mutations)
    baseline_score = float(result["baseline"]["score"])
    best_score = float(result["bestCandidate"]["score"])
    best_candidate_id = str(result["bestCandidate"]["candidateId"])
    events: list[dict[str, Any]] = []
    trajectories = [
        _candidate_trajectory(
            record,
            candidate_records_by_id=candidate_records_by_id,
            mutation_by_id=mutation_by_id,
            experiment=experiment,
            benchmark=benchmark,
            evidence_context=None,
            baseline_score=baseline_score,
            live_evaluation=result["liveEvaluation"],
            best_candidate_id=best_candidate_id,
            applied_best_variant=bool(result["appliedBestVariant"]),
        )
        for record in candidate_records
    ]
    episodes = [
        _candidate_trajectory_episode(
            record,
            candidate_records_by_id=candidate_records_by_id,
            evidence_dataset=evidence_dataset,
        )
        for record in candidate_records
    ]
    learning_summary = _episode_learning_summary(
        episodes,
        trajectories,
        candidate_records_by_id,
    )

    for row in result["iterations"]:
        candidate_record = candidate_records_by_id.get(row["candidateId"])
        parent_candidate_id = row.get("parentCandidateId")
        parent_record = (
            candidate_records_by_id.get(parent_candidate_id) if parent_candidate_id else None
        )
        parent_score = (
            float(parent_record["evaluation"]["score"]) if parent_record is not None else None
        )
        events.append(
            _candidate_trace_event(
                row,
                candidate_record,
                baseline_score=baseline_score,
                parent_score=parent_score,
                best_candidate_id=best_candidate_id,
            )
        )

    events.extend(_frontier_trace_event(snapshot) for snapshot in frontier_snapshots)
    events.append(
        {
            "eventId": "live-evaluation",
            "kind": "live_evaluation",
            "status": result["liveEvaluation"]["status"],
            "strategy": result["liveEvaluation"]["strategy"],
            "provider": result["liveEvaluation"]["provider"],
            "model": result["liveEvaluation"]["model"],
            "sampleCount": int(result["liveEvaluation"]["sampleCount"]),
            "evaluatedCandidateIds": list(result["liveEvaluation"]["evaluatedCandidateIds"]),
            "winnerCandidateId": result["liveEvaluation"]["winnerCandidateId"],
            "bestCandidateChanged": bool(result["liveEvaluation"]["bestCandidateChanged"]),
            "fallbackToDeterministic": bool(result["liveEvaluation"]["fallbackToDeterministic"]),
            "reason": result["liveEvaluation"].get("reason"),
            "verdictCounts": deepcopy(result["liveEvaluation"].get("verdictCounts") or {}),
        }
    )
    events.append(
        {
            "eventId": "run-outcome",
            "kind": "run_outcome",
            "baselineCandidateId": result["baseline"]["candidateId"],
            "bestCandidateId": best_candidate_id,
            "outcomeLabel": _trace_outcome_label(best_score, baseline_score),
            "improvementDelta": round(best_score - baseline_score, 6),
            "appliedBestVariant": bool(result["appliedBestVariant"]),
            "keptCandidateCount": len(result["keptCandidates"]),
            "discardedCandidateCount": len(result["discardedCandidates"]),
            "winnerExplanation": deepcopy(result["candidateSearch"]["winnerExplanation"]),
        }
    )

    return {
        "type": "AutoAgentTrace",
        "version": 1,
        "traceKind": "optimization_run",
        "experiment": {
            "name": experiment["name"],
            "path": experiment_path.as_posix(),
            "description": experiment["description"],
            "primaryTargetId": experiment["primaryTargetId"],
            "targetBundle": deepcopy(result["targetBundle"]),
            "benchmark": {
                "id": benchmark.get("id"),
                "path": experiment["benchmarkPath"].as_posix(),
                "checkCount": len(benchmark["checks"]),
            },
            "mutationCatalog": {
                "path": experiment["mutationCatalogPath"].as_posix(),
                "mutationCount": len(mutations),
            },
        },
        "inputs": {
            "experiment": deepcopy(result["provenance"]["inputs"]["experiment"]),
            "resumeCheckpoint": deepcopy(result["provenance"]["inputs"]["resumeCheckpoint"]),
            "liveEvaluatorPrompt": deepcopy(result["provenance"]["inputs"]["liveEvaluatorPrompt"]),
            "liveEvaluatorRubrics": deepcopy(
                result["provenance"]["inputs"]["liveEvaluatorRubrics"]
            ),
        },
        "policies": {
            "candidatePolicy": deepcopy(result["experiment"]["candidatePolicy"]),
            "evaluationMode": deepcopy(result["experiment"]["evaluationMode"]),
            "continuousPolicy": deepcopy(result["experiment"]["continuousPolicy"]),
            "stagedPatchPolicy": deepcopy(result["experiment"]["stagedPatchPolicy"]),
            "evidencePolicy": deepcopy(result["experiment"]["evidencePolicy"]),
            "reviewedPolicyRuntime": deepcopy(result["experiment"]["reviewedPolicyRuntime"]),
            "reviewedPolicyRuntimeState": deepcopy(
                result["experiment"]["reviewedPolicyRuntimeState"]
            ),
        },
        "summary": {
            "baseline": deepcopy(result["baseline"]),
            "bestCandidate": deepcopy(result["bestCandidate"]),
            "liveEvaluation": deepcopy(result["liveEvaluation"]),
            "resume": deepcopy(result["resume"]),
            "candidateSearch": deepcopy(result["candidateSearch"]),
            "evidenceSummary": deepcopy(result["evidenceSummary"]),
            "stagedPatch": deepcopy(result["stagedPatch"]),
            "outcomeLabel": _trace_outcome_label(best_score, baseline_score),
            "improvementDelta": round(best_score - baseline_score, 6),
            "appliedBestVariant": bool(result["appliedBestVariant"]),
            "appliedPaths": list(result["appliedPaths"]),
            "keptCandidateCount": len(result["keptCandidates"]),
            "discardedCandidateCount": len(result["discardedCandidates"]),
            "trajectoryCount": len(trajectories),
            "episodeCount": len(episodes),
            "evidenceBackedEpisodeCount": sum(
                1 for episode in episodes if int(episode["summary"]["matchedRecordCount"]) > 0
            ),
            "bestTrajectoryId": _trace_trajectory_id(best_candidate_id),
            "bestTrajectoryScore": result["bestCandidate"].get("trajectoryScore"),
            "bestTrajectoryEvidenceMatches": int(
                result["bestCandidate"]["trajectoryEvidenceContext"].get(
                    "matchedRecordCount",
                    0,
                )
            ),
            "rankingSignals": ["benchmark_score", "complexity", "trajectory_score"],
            "winnerExplanation": deepcopy(result["candidateSearch"]["winnerExplanation"]),
        },
        "artifacts": {
            "tracePath": trace_artifact["actualPath"],
            "runRoot": result["artifacts"]["runRoot"],
            "resultsPath": result["artifacts"]["results"]["actualPath"],
            "evidencePath": result["artifacts"]["evidence"]["actualPath"],
            "checkpointPath": result["artifacts"]["checkpoint"]["actualPath"],
            "checkpointManifestPath": result["artifacts"]["checkpointManifest"]["actualPath"],
            "searchLedgerPath": result["artifacts"]["searchLedger"]["actualPath"],
            "benchmarkDraftsPath": benchmark_drafts_artifact["actualPath"],
            "mutationDraftsPath": mutation_drafts_artifact["actualPath"],
            "policyDraftsPath": policy_drafts_artifact["actualPath"],
        },
        "trajectories": trajectories,
        "episodes": episodes,
        "learning": learning_summary,
        "events": events,
    }


def _tsv_row(values: list[Any]) -> str:
    return "\t".join(str(value) for value in values)


def _render_results_tsv(rows: list[dict[str, Any]]) -> str:
    header = _tsv_row(
        [
            "iteration",
            "candidate_id",
            "parent_candidate_id",
            "search_depth",
            "avg_score",
            "trajectory_score",
            "passed",
            "status",
            "description",
            "complexity_score",
            "body_chars",
            "tool_count",
        ]
    )
    lines = [header]
    for row in rows:
        lines.append(
            _tsv_row(
                [
                    row["iteration"],
                    row["candidateId"],
                    row.get("parentCandidateId") or "",
                    row.get("searchDepth", 0),
                    row["score"],
                    row.get("trajectoryScore", 0.0),
                    f"{row['passedChecks']}/{row['totalChecks']}",
                    row["status"],
                    row["description"],
                    row["complexity"]["score"],
                    row["complexity"]["bodyChars"],
                    row["complexity"]["toolCount"],
                ]
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_report(result: dict[str, Any]) -> str:
    winner_explanation = result["candidateSearch"]["winnerExplanation"]

    def _format_named_counts_for_report(counts: dict[str, int]) -> str:
        if not counts:
            return "none"
        return ", ".join(f"{name} {count}" for name, count in counts.items())

    summary_lines = [
        "# AutoAgent Report",
        "",
        f"- Status: {result['status']}",
        f"- Report status meaning: {result['reportStatusMeaning']}",
        f"- Experiment: {result['experiment']['name']}",
        f"- Primary target: {result['targetAgent']}",
        f"- Target bundle size: {len(result['targetBundle'])}",
        f"- Evidence records: {result['evidenceSummary']['recordCount']}",
        f"- Evidence runs: {result['evidenceSummary']['runCount']}",
        f"- External log records: {result['evidenceSummary']['externalLogRecordCount']}",
        f"- Transcript evidence records: {result['evidenceSummary']['transcriptRecordCount']}",
        f"- Handoff evidence records: {result['evidenceSummary']['handoffRecordCount']}",
        f"- Baseline score: {result['baseline']['score']}",
        f"- Best score: {result['bestCandidate']['score']}",
        f"- Best candidate: {result['bestCandidate']['candidateId']}",
        f"- Best trajectory score: {result['bestCandidate']['trajectoryScore']}",
        (
            "- Best trajectory evidence matches: "
            f"{result['bestCandidate']['trajectoryEvidenceContext'].get('matchedRecordCount', 0)}"
        ),
        (
            "- Candidate search: "
            f"{result['candidateSearch']['strategy']} "
            f"(frontier size {result['candidateSearch']['frontierSize']})"
        ),
        ("- Candidate ranking signals: " + ", ".join(result["candidateSearch"]["rankingSignals"])),
        f"- Winner decisive signal: {winner_explanation['decisiveSignal']}",
        f"- Winner rationale: {winner_explanation['summary']}",
        (
            f"- Winner trajectory contributors: {winner_explanation['trajectorySummary']}"
            if winner_explanation.get("trajectorySummary")
            else "- Winner trajectory contributors: none"
        ),
        (
            f"- Winner evidence rationale: {winner_explanation['evidenceSummary']}"
            if winner_explanation.get("evidenceSummary")
            else "- Winner evidence rationale: none"
        ),
        (
            f"- Resume: resumed from mutation {result['resume']['startingMutationIndex']}"
            if result["resume"]["resumed"]
            else "- Resume: fresh run"
        ),
        f"- Resume checkpoint stage: {result['resume']['checkpointStage']}",
        f"- Search ledger nodes: {result['candidateSearch']['ledgerNodeCount']}",
        (
            "- Checkpoint: "
            f"{result['resume']['completedMutationCount']}/"
            f"{result['resume']['totalMutationCount']} mutations complete"
        ),
        (
            "- Checkpoint storage: "
            f"{result['resume']['inlineCandidateCount']} inline, "
            f"{result['resume']['snapshotBackedCandidateCount']} snapshot-backed"
        ),
        (
            "- Checkpoint manifest: "
            f"{result['resume']['manifestSnapshotCandidateCount']} snapshot-backed candidates, "
            f"{result['resume']['manifestRequiredFileCount']} files"
        ),
        f"- Trace events: {result['traceSummary']['eventCount']}",
        f"- Trace trajectories: {result['traceSummary']['trajectoryCount']}",
        f"- Trace candidate episodes: {result['traceSummary']['episodeCount']}",
        (
            "- Trace evidence-backed episodes: "
            f"{result['traceSummary']['evidenceBackedEpisodeCount']}"
        ),
        f"- Learning mode: {result['learningSummary']['mode']}",
        (
            "- Learning reasoning-path signal: "
            f"{result['learningSummary']['reasoningPathSignal']['name']}"
        ),
        (
            "- Learning source-backed paths: "
            f"{result['learningSummary']['reasoningPathSignal']['sourceBackedPathCount']}"
        ),
        (
            "- Learning transcript-backed paths: "
            f"{result['learningSummary']['reasoningPathSignal']['transcriptBackedPathCount']}"
        ),
        (
            "- Learning handoff-backed paths: "
            f"{result['learningSummary']['reasoningPathSignal']['handoffBackedPathCount']}"
        ),
        (
            "- Learning best reasoning-path efficiency: "
            f"{result['learningSummary']['reasoningPathSignal']['bestObservedScore']}"
        ),
        (f"- Learning top observed paths: {len(result['learningSummary']['topObservedPaths'])}"),
        (
            "- Learning benchmark candidates: "
            f"{len(result['learningSummary']['benchmarkCandidates'])}"
        ),
        (f"- Learning mutation seeds: {len(result['learningSummary']['mutationSeedCandidates'])}"),
        (f"- Learning policy candidates: {len(result['learningSummary']['policyCandidates'])}"),
        (
            "- Learning benchmark draft fragments: "
            f"{result['learningArtifacts']['benchmarkDraftCount']}"
        ),
        (f"- Learning mutation draft entries: {result['learningArtifacts']['mutationDraftCount']}"),
        (f"- Learning policy draft entries: {result['learningArtifacts']['policyDraftCount']}"),
        f"- Trace best trajectory score: {result['traceSummary']['bestTrajectoryScore']}",
        (
            "- Trace best trajectory evidence matches: "
            f"{result['traceSummary']['bestTrajectoryEvidenceMatches']}"
        ),
        f"- Trace artifact: {result['traceSummary']['path']}",
        (
            "- Learning benchmark drafts artifact: "
            f"{result['learningArtifacts']['benchmarkDraftsPath']}"
        ),
        (
            "- Learning mutation drafts artifact: "
            f"{result['learningArtifacts']['mutationDraftsPath']}"
        ),
        (f"- Learning policy drafts artifact: {result['learningArtifacts']['policyDraftsPath']}"),
        (f"- Guarded learning promotion: {result['guardedLearningPromotion']['status']}"),
        (
            "- Guarded learning blocked reasons: "
            + ", ".join(result["guardedLearningPromotion"]["blockedReasons"])
            if result["guardedLearningPromotion"]["blockedReasons"]
            else "- Guarded learning blocked reasons: none"
        ),
        (
            "- Guarded learning benchmark accepts: "
            f"{result['guardedLearningPromotion']['acceptedBenchmarkDraftCount']}"
        ),
        (
            "- Guarded learning policy accepts: "
            f"{result['guardedLearningPromotion']['acceptedPolicyDraftCount']}"
        ),
        (
            "- Guarded learning review artifact: "
            f"{result['guardedLearningPromotion']['artifactPath']}"
            if result["guardedLearningPromotion"]["artifactPath"]
            else "- Guarded learning review artifact: none"
        ),
        (f"- Guarded learning summary: {result['guardedLearningPromotion']['summary']}"),
        (
            "- Guarded learning recommended action: "
            f"{result['guardedLearningPromotion']['recommendedAction']}"
        ),
        (f"- Learning promotion audit: {result['learningPromotionAudit']['status']}"),
        (
            "- Learning promotion audit artifact: "
            f"{result['learningPromotionAudit']['artifactPath']}"
            if result["learningPromotionAudit"]["artifactFound"]
            else "- Learning promotion audit artifact: none"
        ),
        (
            "- Learning promotion audit source mode: "
            f"{result['learningPromotionAudit']['promotionSourceMode']}"
            if result["learningPromotionAudit"]["artifactFound"]
            else "- Learning promotion audit source mode: none"
        ),
        (
            "- Learning promotion audit reviewer overrides: "
            f"{result['learningPromotionAudit']['reviewerOverrideCount']}"
        ),
        (
            "- Learning promotion audit benchmark decisions: "
            "reviewed "
            f"{result['learningPromotionAudit']['reviewedBenchmarkDraftCount']}, "
            "accepted "
            f"{result['learningPromotionAudit']['acceptedBenchmarkDraftCount']}, "
            "rejected "
            f"{result['learningPromotionAudit']['rejectedBenchmarkDraftCount']}, "
            "deferred "
            f"{result['learningPromotionAudit']['deferredBenchmarkDraftCount']}"
        ),
        (
            "- Learning promotion audit mutation decisions: "
            "reviewed "
            f"{result['learningPromotionAudit']['reviewedMutationDraftCount']}, "
            "accepted "
            f"{result['learningPromotionAudit']['acceptedMutationDraftCount']}, "
            "rejected "
            f"{result['learningPromotionAudit']['rejectedMutationDraftCount']}, "
            "deferred "
            f"{result['learningPromotionAudit']['deferredMutationDraftCount']}"
        ),
        (
            "- Learning promotion audit policy decisions: "
            "reviewed "
            f"{result['learningPromotionAudit']['reviewedPolicyDraftCount']}, "
            "accepted "
            f"{result['learningPromotionAudit']['acceptedPolicyDraftCount']}, "
            "rejected "
            f"{result['learningPromotionAudit']['rejectedPolicyDraftCount']}, "
            "deferred "
            f"{result['learningPromotionAudit']['deferredPolicyDraftCount']}"
        ),
        (
            "- Learning promotion audit blocked factors: "
            f"{_format_named_counts_for_report(result['learningPromotionAudit']['blockedFactorCounts'])}"
        ),
        (
            "- Learning promotion audit benchmark blocked factors: "
            f"{_format_named_counts_for_report(result['learningPromotionAudit']['benchmarkBlockedFactorCounts'])}"
        ),
        (
            "- Learning promotion audit mutation blocked factors: "
            f"{_format_named_counts_for_report(result['learningPromotionAudit']['mutationBlockedFactorCounts'])}"
        ),
        (
            "- Learning promotion audit policy blocked factors: "
            f"{_format_named_counts_for_report(result['learningPromotionAudit']['policyBlockedFactorCounts'])}"
        ),
        (
            "- Reviewed policy runtime: "
            f"{result['experiment']['reviewedPolicyRuntimeState']['status']} "
            f"({result['experiment']['reviewedPolicyRuntimeState']['activePolicyCount']} policies)"
        ),
        (
            "- Reviewed policy artifact: "
            f"{result['experiment']['reviewedPolicyRuntimeState']['artifactPath']}"
        ),
        f"- Continuous mode: {result['experiment']['continuousPolicy']['mode']}",
        (
            "- Continuation eligibility: "
            f"{result['experiment']['continuationEligibility']['status']}"
        ),
        (
            "- Continuation blocked reasons: "
            + ", ".join(result["experiment"]["continuationEligibility"]["blockedReasons"])
            if result["experiment"]["continuationEligibility"]["blockedReasons"]
            else "- Continuation blocked reasons: none"
        ),
        (
            "- Continuation execution: "
            f"{result['experiment']['continuationEligibility']['executionMode']}"
        ),
        (f"- Governed task lifecycle: {result['experiment']['governedTaskLifecycle']['phase']}"),
        (f"- Governed task id: {result['experiment']['governedTaskLifecycle']['taskId']}"),
        (f"- Governed task title: {result['experiment']['governedTaskLifecycle']['taskTitle']}"),
        (
            "- Governed lifecycle quality gate: "
            f"{result['experiment']['governedTaskLifecycle']['qualityGateStatus']}"
        ),
        (
            "- Governed next action: "
            f"{result['experiment']['governedTaskLifecycle']['nextActionOwner']}"
            f" - {result['experiment']['governedTaskLifecycle']['nextActionSummary']}"
        ),
        (
            "- Governed lifecycle missing fields: "
            + ", ".join(result["experiment"]["governedTaskLifecycle"]["missingFields"])
            if result["experiment"]["governedTaskLifecycle"]["missingFields"]
            else "- Governed lifecycle missing fields: none"
        ),
        (f"- Continuation readiness: {result['experiment']['continuationReadiness']['status']}"),
        (
            "- Continuation readiness blocked reasons: "
            + ", ".join(result["experiment"]["continuationReadiness"]["blockedReasons"])
            if result["experiment"]["continuationReadiness"]["blockedReasons"]
            else "- Continuation readiness blocked reasons: none"
        ),
        (
            "- Governed review consensus: "
            f"{result['experiment']['governedReviewConsensus']['status']}"
        ),
        (
            "- Governed review consensus blocked reasons: "
            + ", ".join(result["experiment"]["governedReviewConsensus"]["blockedReasons"])
            if result["experiment"]["governedReviewConsensus"]["blockedReasons"]
            else "- Governed review consensus blocked reasons: none"
        ),
        (
            "- Governed review status: "
            f"{result['experiment']['continuationReadiness']['governedReviewStatus']}"
        ),
        (
            "- Review report status: "
            f"{result['experiment']['governedReviewConsensus']['reviewReportStatus']}"
        ),
        (
            "- Reviewed continuation handoff: "
            f"{result['experiment']['reviewedContinuationHandoff']['status']}"
        ),
        (
            "- Reviewed handoff blocked reasons: "
            + ", ".join(result["experiment"]["reviewedContinuationHandoff"]["blockedReasons"])
            if result["experiment"]["reviewedContinuationHandoff"]["blockedReasons"]
            else "- Reviewed handoff blocked reasons: none"
        ),
        (
            "- Reviewed handoff mode: "
            f"{result['experiment']['reviewedContinuationHandoff']['handoffMode']}"
        ),
        (
            "- Reviewed handoff summary: "
            f"{result['experiment']['reviewedContinuationHandoff']['summary']}"
        ),
        (
            "- Reviewed handoff recommended action: "
            f"{result['experiment']['reviewedContinuationHandoff']['recommendedAction']}"
        ),
        (f"- Orchestration contract: {result['experiment']['orchestrationContract']['status']}"),
        (
            "- Orchestration contract blocked reasons: "
            + ", ".join(result["experiment"]["orchestrationContract"]["blockedReasons"])
            if result["experiment"]["orchestrationContract"]["blockedReasons"]
            else "- Orchestration contract blocked reasons: none"
        ),
        (
            "- Orchestration contract mode: "
            f"{result['experiment']['orchestrationContract']['contractMode']}"
        ),
        (
            "- Orchestration contract scope: "
            f"{result['experiment']['orchestrationContract']['dispatchScope']}"
        ),
        (
            "- Orchestration contract id: "
            f"{result['experiment']['orchestrationContract']['contractId']}"
        ),
        (
            "- Orchestration contract summary: "
            f"{result['experiment']['orchestrationContract']['summary']}"
        ),
        (
            "- Orchestration contract recommended action: "
            f"{result['experiment']['orchestrationContract']['recommendedAction']}"
        ),
        (f"- Reviewed dispatch intent: {result['experiment']['reviewedDispatchIntent']['status']}"),
        (
            "- Reviewed dispatch blocked reasons: "
            + ", ".join(result["experiment"]["reviewedDispatchIntent"]["blockedReasons"])
            if result["experiment"]["reviewedDispatchIntent"]["blockedReasons"]
            else "- Reviewed dispatch blocked reasons: none"
        ),
        (
            "- Reviewed dispatch approval status: "
            f"{result['experiment']['reviewedDispatchIntent']['approvalStatus']}"
        ),
        (
            "- Reviewed dispatch approval source: "
            f"{result['experiment']['reviewedDispatchIntent']['approvalSource']}"
        ),
        (
            "- Reviewed dispatch summary: "
            f"{result['experiment']['reviewedDispatchIntent']['summary']}"
        ),
        (
            "- Reviewed dispatch recommended action: "
            f"{result['experiment']['reviewedDispatchIntent']['recommendedAction']}"
        ),
        (
            "- Governed approval metadata: "
            f"{result['experiment']['governedApprovalMetadata']['status']}"
        ),
        (
            "- Governed approval blocked reasons: "
            + ", ".join(result["experiment"]["governedApprovalMetadata"]["blockedReasons"])
            if result["experiment"]["governedApprovalMetadata"]["blockedReasons"]
            else "- Governed approval blocked reasons: none"
        ),
        (
            "- Governed approval review pass recorded: "
            f"{result['experiment']['governedApprovalMetadata']['reviewPassRecorded']}"
        ),
        (
            "- Governed approval quality gate: "
            f"{result['experiment']['governedApprovalMetadata']['qualityGateStatus']}"
        ),
        (
            "- Governed approval source: "
            f"{result['experiment']['governedApprovalMetadata']['approvalSource']}"
        ),
        (
            "- Governed approval summary: "
            f"{result['experiment']['governedApprovalMetadata']['summary']}"
        ),
        (
            "- Governed approval recommended action: "
            f"{result['experiment']['governedApprovalMetadata']['recommendedAction']}"
        ),
        "- Phase 4 bounded step: governed_approval_metadata",
        "- Phase 4 execution authority: out_of_scope",
        "- Phase 3 visibility scope: complete",
        (
            "- Phase 3 exit criteria: continuation eligibility, continuation readiness, "
            "governed review consensus, governed task lifecycle, and reviewed handoff visibility "
            "are all present under manual/report_only semantics"
        ),
        "- Phase 3 unattended orchestration: out_of_scope",
        (
            "- Live evaluator: "
            f"{result['experiment']['evaluationMode']['liveEvaluator']['strategy']}"
            if result["experiment"]["evaluationMode"]["liveEvaluator"]["enabled"]
            else "- Live evaluator: disabled"
        ),
        f"- Live evaluation status: {result['liveEvaluation']['status']}",
        (
            "- Staged patch: "
            f"{result['stagedPatch']['mode']} "
            f"({result['stagedPatch']['changedTargetCount']} targets)"
        ),
        f"- Applied best variant: {result['appliedBestVariant']}",
        "",
        "```json",
        json.dumps(result, indent=2),
        "```",
        "",
    ]
    return "\n".join(summary_lines)


def run_autoagent_loop(
    experiment_path: Path,
    output_root: Path,
    report_path: Path,
    results_path: Path,
    max_iterations: int | None,
    apply_best: bool,
    evidence_path: Path | None = None,
    resume: bool = False,
) -> dict[str, Any]:
    experiment = load_experiment(experiment_path)
    _validate_continuation_policy_config(experiment, apply_best or experiment["applyBestCandidate"])
    _validate_live_evaluator_config(experiment, apply_best or experiment["applyBestCandidate"])
    experiment["governedTaskLifecycle"] = _derive_governed_task_lifecycle()
    experiment["governedReviewConsensus"] = _derive_governed_review_consensus()
    experiment["continuationReadiness"] = _derive_continuation_readiness(
        experiment["continuationEligibility"],
        experiment["governedReviewConsensus"],
    )
    experiment["reviewedContinuationHandoff"] = _derive_reviewed_continuation_handoff(
        experiment["continuationEligibility"],
        experiment["governedTaskLifecycle"],
        experiment["governedReviewConsensus"],
        experiment["continuationReadiness"],
    )
    experiment["orchestrationContract"] = _derive_orchestration_contract(
        experiment["reviewedContinuationHandoff"],
        experiment["governedTaskLifecycle"],
    )
    experiment["reviewedDispatchIntent"] = _derive_reviewed_dispatch_intent(
        experiment["orchestrationContract"],
        experiment["reviewedContinuationHandoff"],
        experiment["governedTaskLifecycle"],
    )
    experiment["governedApprovalMetadata"] = _derive_governed_approval_metadata(
        experiment["reviewedDispatchIntent"],
        experiment["governedReviewConsensus"],
        experiment["governedTaskLifecycle"],
    )
    benchmark = load_benchmark(experiment["benchmarkPath"])
    mutations = load_mutations(experiment["mutationCatalogPath"])
    mutation_by_id = _mutation_catalog_by_id(mutations)
    if max_iterations is None or max_iterations <= 0:
        max_iterations = experiment["maxIterations"] or len(mutations)
    assert max_iterations is not None
    planned_mutation_count = min(max_iterations, len(mutations))
    if evidence_path is None:
        evidence_path = DOCS_AGENTS_DIR / "autoagent-evidence.json"

    targets = experiment["targets"]
    primary_target_id = experiment["primaryTargetId"]
    target_agent_path = experiment["targetAgentPath"]
    assert isinstance(target_agent_path, Path)
    evidence_dataset = build_evidence_dataset(experiment["evidencePolicy"])
    target_documents = load_target_documents(targets)
    baseline_eval = evaluate_candidate(
        target_documents,
        benchmark,
        primary_target_id,
        candidate_record={
            "candidateId": "baseline",
            "parentCandidateId": None,
            "mutationId": None,
            "status": "keep",
        },
        evidence_dataset=evidence_dataset,
    )

    run_root = output_root / experiment["name"]
    run_root.mkdir(parents=True, exist_ok=True)
    learning_promotion_audit_state = _load_learning_promotion_audit_state(run_root)
    experiment["reviewedPolicyRuntimeState"] = _load_reviewed_policy_runtime_state(
        experiment,
        run_root,
    )
    mutation_execution_plan = _prioritized_mutation_plan(
        mutations,
        reviewed_policy_runtime_state=experiment["reviewedPolicyRuntimeState"],
        reviewed_policy_runtime=experiment["reviewedPolicyRuntime"],
    )
    ordered_mutations = [
        mutations[int(entry["catalogIndex"]) - 1] for entry in mutation_execution_plan
    ]
    candidates_root = run_root / "candidates"
    candidates_root.mkdir(parents=True, exist_ok=True)
    checkpoint_path = run_root / "search-checkpoint.json"
    resume_checkpoint_input: Path | None = checkpoint_path if resume else None

    baseline_path = _candidate_output_path(
        candidates_root,
        0,
        "baseline",
        target_documents,
        primary_target_id,
    )
    _write_candidate_documents(baseline_path, target_documents, primary_target_id)
    _write(candidates_root / "iteration-00-baseline-eval.json", _json(baseline_eval))

    candidate_policy = experiment["candidatePolicy"]
    resumed = False
    start_mutation_index = 1

    if resume:
        checkpoint = _load_search_checkpoint(
            checkpoint_path,
            experiment,
            mutations,
            mutation_execution_plan,
            planned_mutation_count,
        )
        targets_by_id = {target["id"]: target for target in targets}
        candidate_records = [
            _restore_checkpoint_candidate_record(payload, targets_by_id)
            for payload in checkpoint["candidateRecords"]
        ]
        by_candidate_id = {record["candidateId"]: record for record in candidate_records}
        deterministic_best_candidate_id = str(checkpoint["deterministicBestCandidateId"])
        best_record = by_candidate_id.get(deterministic_best_candidate_id)
        if best_record is None:
            raise ValueError(
                "Resume checkpoint deterministicBestCandidateId is missing from candidateRecords."
            )
        best_documents = deepcopy(best_record["documents"])
        best_eval = deepcopy(best_record["evaluation"])
        best_candidate_id = best_record["candidateId"]
        best_candidate_path = best_record["path"]
        rows = deepcopy(checkpoint.get("rows") or [])
        kept_candidates = list(checkpoint.get("keptCandidates") or [])
        discarded_candidates = list(checkpoint.get("discardedCandidates") or [])
        frontier_snapshots = deepcopy(checkpoint.get("frontierSnapshots") or [])
        evaluation_iteration = int(checkpoint.get("evaluationIteration") or len(rows))
        start_mutation_index = int(checkpoint.get("nextMutationIndex") or 1)
        resumed = True
    else:
        best_documents = deepcopy(target_documents)
        best_eval = dict(baseline_eval)
        best_candidate_id = "baseline"
        best_candidate_path = baseline_path
        best_record = {
            "iteration": 0,
            "candidateId": "baseline",
            "parentCandidateId": None,
            "description": "Baseline target agent",
            "status": "keep",
            "evaluation": baseline_eval,
            "documents": deepcopy(target_documents),
            "path": baseline_path,
            "searchDepth": 0,
            "mutationId": None,
            "touchedTargets": [],
        }

        rows = [
            {
                "iteration": 0,
                "candidateId": "baseline",
                "parentCandidateId": None,
                "searchDepth": 0,
                "score": baseline_eval["score"],
                "passedChecks": baseline_eval["passedChecks"],
                "totalChecks": baseline_eval["totalChecks"],
                "status": "keep",
                "description": "Baseline target agent",
                "complexity": baseline_eval["complexity"],
            }
        ]
        kept_candidates = ["baseline"]
        discarded_candidates = []
        candidate_records = [best_record]
        frontier_snapshots = [
            {
                "mutationIndex": 0,
                "catalogIndex": 0,
                "planToken": "0:baseline",
                "mutationId": None,
                "evaluatedCandidateIds": ["baseline"],
                "frontierCandidateIds": ["baseline"],
                "bestCandidateId": "baseline",
            }
        ]
        evaluation_iteration = 1

    _refresh_candidate_rankings(
        candidate_records,
        rows,
        mutation_by_id=mutation_by_id,
        experiment=experiment,
        benchmark=benchmark,
        evidence_dataset=evidence_dataset,
        baseline_score=float(baseline_eval["score"]),
    )
    baseline_record = next(
        record for record in candidate_records if record["candidateId"] == "baseline"
    )
    baseline_eval = deepcopy(baseline_record["evaluation"])
    by_candidate_id = {record["candidateId"]: record for record in candidate_records}
    best_record = by_candidate_id[best_candidate_id]
    best_documents = deepcopy(best_record["documents"])
    best_eval = deepcopy(best_record["evaluation"])
    best_candidate_path = best_record["path"]

    frontier_records = (
        _select_frontier_records(candidate_records, candidate_policy["frontierSize"])
        if candidate_policy["searchStrategy"] == "frontier"
        else [best_record]
    )

    for mutation_index, mutation_plan_entry in enumerate(
        mutation_execution_plan[start_mutation_index - 1 : planned_mutation_count],
        start=start_mutation_index,
    ):
        catalog_index = int(mutation_plan_entry["catalogIndex"])
        mutation = ordered_mutations[mutation_index - 1]
        mutation_id = mutation_plan_entry["mutationId"]
        if candidate_policy["searchStrategy"] == "frontier":
            parent_records = _select_frontier_records(
                candidate_records,
                candidate_policy["frontierSize"],
            )
        else:
            parent_records = [best_record]
        branched = len(parent_records) > 1
        mutation_evaluated_candidate_ids: list[str] = []

        for parent_record in parent_records:
            base_candidate_id = mutation_id
            candidate_id = _derived_candidate_id(
                base_candidate_id,
                parent_record["candidateId"],
                branched,
            )
            candidate_documents, changed, touched_targets = apply_mutation(
                parent_record["documents"],
                mutation,
                primary_target_id,
            )
            candidate_path = _candidate_output_path(
                candidates_root,
                evaluation_iteration,
                candidate_id,
                candidate_documents,
                primary_target_id,
            )
            if not changed:
                candidate_eval = deepcopy(parent_record["evaluation"])
            else:
                candidate_eval = evaluate_candidate(
                    candidate_documents,
                    benchmark,
                    primary_target_id,
                    candidate_record={
                        "candidateId": candidate_id,
                        "parentCandidateId": parent_record["candidateId"],
                        "mutationId": mutation_id,
                        "status": "candidate",
                    },
                    evidence_dataset=evidence_dataset,
                )

            candidate_record = {
                "iteration": evaluation_iteration,
                "candidateId": candidate_id,
                "parentCandidateId": parent_record["candidateId"],
                "description": mutation.get("description", "candidate mutation"),
                "status": "candidate",
                "evaluation": candidate_eval,
                "documents": deepcopy(candidate_documents),
                "path": candidate_path,
                "searchDepth": int(parent_record.get("searchDepth", 0)) + 1,
                "mutationId": mutation_id,
                "touchedTargets": touched_targets,
            }
            candidate_records_by_id = {
                record["candidateId"]: record for record in candidate_records
            }
            candidate_records_by_id[candidate_id] = candidate_record
            _annotate_candidate_trajectory_score(
                candidate_record,
                candidate_records_by_id=candidate_records_by_id,
                mutation_by_id=mutation_by_id,
                experiment=experiment,
                benchmark=benchmark,
                evidence_dataset=evidence_dataset,
                baseline_score=float(baseline_eval["score"]),
            )
            candidate_eval = candidate_record["evaluation"]
            if not changed:
                status = "skip"
            else:
                status = (
                    "keep" if _is_better(candidate_eval, parent_record["evaluation"]) else "discard"
                )
            candidate_record["status"] = status

            _write_candidate_documents(candidate_path, candidate_documents, primary_target_id)
            _write(
                candidates_root / f"iteration-{evaluation_iteration:02d}-{candidate_id}-eval.json",
                _json(candidate_eval),
            )

            rows.append(
                {
                    "iteration": evaluation_iteration,
                    "candidateId": candidate_id,
                    "parentCandidateId": parent_record["candidateId"],
                    "searchDepth": int(parent_record.get("searchDepth", 0)) + 1,
                    "score": candidate_eval["score"],
                    "trajectoryScore": _evaluation_trajectory_score(candidate_eval),
                    "passedChecks": candidate_eval["passedChecks"],
                    "totalChecks": candidate_eval["totalChecks"],
                    "status": status,
                    "description": mutation.get("description", "candidate mutation"),
                    "complexity": candidate_eval["complexity"],
                    "touchedTargets": touched_targets,
                }
            )
            candidate_records.append(candidate_record)
            mutation_evaluated_candidate_ids.append(candidate_id)

            if status == "keep":
                if candidate_id not in kept_candidates:
                    kept_candidates.append(candidate_id)
                if changed and _is_better(candidate_eval, best_eval):
                    best_documents = candidate_documents
                    best_eval = candidate_eval
                    best_candidate_id = candidate_id
                    best_candidate_path = candidate_path
                    best_record = candidate_record
            elif status == "discard" and candidate_id not in discarded_candidates:
                discarded_candidates.append(candidate_id)

            evaluation_iteration += 1

        frontier_records = (
            _select_frontier_records(candidate_records, candidate_policy["frontierSize"])
            if candidate_policy["searchStrategy"] == "frontier"
            else [best_record]
        )
        frontier_snapshots.append(
            {
                "mutationIndex": mutation_index,
                "catalogIndex": catalog_index,
                "planToken": mutation_plan_entry["planToken"],
                "mutationId": mutation_id,
                "evaluatedCandidateIds": mutation_evaluated_candidate_ids,
                "frontierCandidateIds": [record["candidateId"] for record in frontier_records],
                "bestCandidateId": best_candidate_id,
            }
        )

    deterministic_best_candidate_id = best_record["candidateId"]

    live_evaluation, selected_record = _execute_live_evaluator(
        experiment,
        candidate_records,
        best_record,
        apply_best or experiment["applyBestCandidate"],
    )
    if selected_record["candidateId"] != best_record["candidateId"]:
        best_record = selected_record
        best_documents = deepcopy(selected_record["documents"])
        best_eval = deepcopy(selected_record["evaluation"])
        best_candidate_id = selected_record["candidateId"]
        best_candidate_path = selected_record["path"]
        if best_candidate_id not in kept_candidates:
            kept_candidates.append(best_candidate_id)
        discarded_candidates = [
            candidate_id
            for candidate_id in discarded_candidates
            if candidate_id != best_candidate_id
        ]

    _refresh_candidate_rankings(
        candidate_records,
        rows,
        mutation_by_id=mutation_by_id,
        experiment=experiment,
        benchmark=benchmark,
        evidence_dataset=evidence_dataset,
        baseline_score=float(baseline_eval["score"]),
        live_evaluation=live_evaluation,
        best_candidate_id=best_candidate_id,
    )
    by_candidate_id = {record["candidateId"]: record for record in candidate_records}
    baseline_record = by_candidate_id["baseline"]
    baseline_eval = deepcopy(baseline_record["evaluation"])
    best_record = by_candidate_id[best_candidate_id]
    best_documents = deepcopy(best_record["documents"])
    best_eval = deepcopy(best_record["evaluation"])
    best_candidate_path = best_record["path"]

    applied_paths: list[str] = []
    if apply_best or experiment["applyBestCandidate"]:
        for target in targets:
            document = best_documents[target["id"]]
            applied_content = render_markdown_document(document["frontmatter"], document["body"])
            _write(target["path"], applied_content)
            applied_paths.append(target["path"].as_posix())

    staged_patch = _staged_patch_metadata(
        target_documents,
        best_documents,
        targets,
        primary_target_id,
        best_candidate_id,
        best_candidate_path,
        experiment["stagedPatchPolicy"],
    )

    checkpoint_payload = _build_search_checkpoint(
        experiment,
        mutations,
        mutation_execution_plan,
        planned_mutation_count,
        candidate_records,
        frontier_records,
        frontier_snapshots,
        rows,
        kept_candidates,
        discarded_candidates,
        evaluation_iteration,
        deterministic_best_candidate_id,
    )
    _write(checkpoint_path, _json(checkpoint_payload))
    checkpoint_artifact = {
        "requestedPath": checkpoint_path.as_posix(),
        "actualPath": checkpoint_path.as_posix(),
        "fallbackUsed": False,
        "warning": None,
        "runSnapshot": None,
    }

    checkpoint_manifest_payload = _build_search_checkpoint_manifest(
        experiment,
        checkpoint_path,
        checkpoint_payload,
        candidate_records,
    )
    checkpoint_manifest_path = run_root / "search-checkpoint-manifest.json"
    _write(checkpoint_manifest_path, _json(checkpoint_manifest_payload))
    checkpoint_manifest_artifact = {
        "requestedPath": checkpoint_manifest_path.as_posix(),
        "actualPath": checkpoint_manifest_path.as_posix(),
        "fallbackUsed": False,
        "warning": None,
        "runSnapshot": None,
    }

    search_ledger = _build_search_ledger(
        experiment,
        candidate_records,
        frontier_snapshots,
        mutation_execution_plan,
        best_candidate_id,
        live_evaluation,
        _winner_explanation(
            candidate_records,
            best_candidate_id=best_candidate_id,
            deterministic_best_candidate_id=deterministic_best_candidate_id,
            live_evaluation=live_evaluation,
        ),
    )
    search_ledger_path = run_root / "search-ledger.json"
    _write(search_ledger_path, _json(search_ledger))
    search_ledger_artifact = {
        "requestedPath": search_ledger_path.as_posix(),
        "actualPath": search_ledger_path.as_posix(),
        "fallbackUsed": False,
        "warning": None,
        "runSnapshot": None,
    }

    benchmark_drafts_path = run_root / "draft-benchmark-fragments.json"
    benchmark_drafts_artifact = {
        "requestedPath": benchmark_drafts_path.as_posix(),
        "actualPath": benchmark_drafts_path.as_posix(),
        "fallbackUsed": False,
        "warning": None,
        "runSnapshot": None,
    }
    mutation_drafts_path = run_root / "draft-mutation-catalog.json"
    mutation_drafts_artifact = {
        "requestedPath": mutation_drafts_path.as_posix(),
        "actualPath": mutation_drafts_path.as_posix(),
        "fallbackUsed": False,
        "warning": None,
        "runSnapshot": None,
    }
    policy_drafts_path = run_root / "draft-policy-catalog.json"
    policy_drafts_artifact = {
        "requestedPath": policy_drafts_path.as_posix(),
        "actualPath": policy_drafts_path.as_posix(),
        "fallbackUsed": False,
        "warning": None,
        "runSnapshot": None,
    }
    guarded_learning_review_path = run_root / "guarded-learning-review.generated.json"
    guarded_learning_review_artifact = {
        "requestedPath": guarded_learning_review_path.as_posix(),
        "actualPath": None,
        "fallbackUsed": False,
        "warning": None,
        "runSnapshot": None,
    }

    results_content = _render_results_tsv(rows)
    if _is_root_docs_artifact(results_path):
        results_artifact = write_docs_artifact(results_path, results_content)
    else:
        _write(results_path, results_content)
        results_artifact = {
            "requestedPath": results_path.as_posix(),
            "actualPath": results_path.as_posix(),
            "fallbackUsed": False,
            "warning": None,
            "runSnapshot": None,
        }

    evidence_content = _json(evidence_dataset)
    if _is_root_docs_artifact(evidence_path):
        evidence_artifact = write_docs_artifact(evidence_path, evidence_content)
    else:
        _write(evidence_path, evidence_content)
        evidence_artifact = {
            "requestedPath": evidence_path.as_posix(),
            "actualPath": evidence_path.as_posix(),
            "fallbackUsed": False,
            "warning": None,
            "runSnapshot": None,
        }

    trace_artifact = {
        "requestedPath": (run_root / "autoagent-trace.json").as_posix(),
        "actualPath": (run_root / "autoagent-trace.json").as_posix(),
        "fallbackUsed": False,
        "warning": None,
        "runSnapshot": None,
    }

    provenance = _provenance_summary(
        experiment_path,
        experiment,
        evidence_dataset,
        evidence_artifact,
        results_artifact,
        resume_checkpoint_input,
        checkpoint_artifact,
        checkpoint_payload["resumeStage"],
        checkpoint_manifest_artifact,
        search_ledger_artifact,
        benchmark_drafts_artifact,
        mutation_drafts_artifact,
        policy_drafts_artifact,
        trace_artifact,
    )

    result = {
        "type": "AutoAgentReport",
        "status": "READY_FOR_QUALITY_GATE",
        "reportStatusMeaning": "artifact_readiness",
        "experiment": {
            "name": experiment["name"],
            "path": experiment_path.as_posix(),
            "description": experiment["description"],
            "directive": experiment["body"],
            "candidatePolicy": experiment["candidatePolicy"],
            "evaluationMode": _serialize_evaluation_mode(experiment["evaluationMode"]),
            "continuousPolicy": _serialize_continuous_policy(experiment["continuousPolicy"]),
            "continuationEligibility": _serialize_continuation_eligibility(
                experiment["continuationEligibility"]
            ),
            "governedTaskLifecycle": _serialize_governed_task_lifecycle(
                experiment["governedTaskLifecycle"]
            ),
            "governedReviewConsensus": _serialize_governed_review_consensus(
                experiment["governedReviewConsensus"]
            ),
            "continuationReadiness": _serialize_continuation_readiness(
                experiment["continuationReadiness"]
            ),
            "reviewedContinuationHandoff": _serialize_reviewed_continuation_handoff(
                experiment["reviewedContinuationHandoff"]
            ),
            "orchestrationContract": _serialize_orchestration_contract(
                experiment["orchestrationContract"]
            ),
            "reviewedDispatchIntent": _serialize_reviewed_dispatch_intent(
                experiment["reviewedDispatchIntent"]
            ),
            "governedApprovalMetadata": _serialize_governed_approval_metadata(
                experiment["governedApprovalMetadata"]
            ),
            "stagedPatchPolicy": _serialize_staged_patch_policy(experiment["stagedPatchPolicy"]),
            "evidencePolicy": _serialize_evidence_policy(experiment["evidencePolicy"]),
            "reviewedPolicyRuntime": _serialize_reviewed_policy_runtime(
                experiment["reviewedPolicyRuntime"]
            ),
            "reviewedPolicyRuntimeState": _serialize_reviewed_policy_runtime_state(
                experiment.get("reviewedPolicyRuntimeState") or {}
            ),
            "stageForReview": experiment["stageForReview"],
        },
        "targetBundle": _serialize_targets(targets),
        "primaryTargetId": primary_target_id,
        "targetAgent": target_agent_path.as_posix(),
        "resume": {
            "requested": resume,
            "resumed": resumed,
            "checkpointStage": checkpoint_payload["resumeStage"],
            "startingMutationIndex": start_mutation_index,
            "completedMutationCount": checkpoint_payload["completedMutationCount"],
            "requestedMutationCount": checkpoint_payload["requestedMutationCount"],
            "totalMutationCount": checkpoint_payload["totalMutationCount"],
            "nextMutationIndex": checkpoint_payload["nextMutationIndex"],
            "hasRemainingMutations": checkpoint_payload["hasRemainingMutations"],
            "inlineCandidateCount": checkpoint_payload["inlineCandidateCount"],
            "snapshotBackedCandidateCount": checkpoint_payload["snapshotBackedCandidateCount"],
            "checkpointPath": checkpoint_artifact["actualPath"],
            "checkpointManifestPath": checkpoint_manifest_artifact["actualPath"],
            "manifestSnapshotCandidateCount": checkpoint_manifest_payload["snapshotCandidateCount"],
            "manifestRequiredFileCount": checkpoint_manifest_payload["requiredFileCount"],
        },
        "candidateSearch": {
            "strategy": candidate_policy["searchStrategy"],
            "frontierSize": candidate_policy["frontierSize"],
            "keepStrategy": candidate_policy["keepStrategy"],
            "rankingSignals": ["benchmark_score", "complexity", "trajectory_score"],
            "mutationExecutionPlan": deepcopy(mutation_execution_plan),
            "maxSearchDepth": max(
                int(record.get("searchDepth", 0)) for record in candidate_records
            ),
            "ledgerNodeCount": len(search_ledger["nodes"]),
            "searchLedgerPath": search_ledger_artifact["actualPath"],
            "bestCandidateLineage": search_ledger["bestCandidateLineage"],
            "finalFrontierCandidateIds": [record["candidateId"] for record in frontier_records],
            "winnerExplanation": deepcopy(search_ledger["winnerExplanation"]),
        },
        "evidenceSummary": evidence_dataset["summary"],
        "liveEvaluation": live_evaluation,
        "stagedPatch": staged_patch,
        "provenance": provenance,
        "baseline": {
            "candidateId": "baseline",
            "score": baseline_eval["score"],
            "trajectoryScore": _evaluation_trajectory_score(baseline_eval),
            "trajectoryScoreBreakdown": deepcopy(
                baseline_eval.get("trajectoryScoreBreakdown") or {}
            ),
            "trajectoryEvidenceContext": deepcopy(
                baseline_eval.get("trajectoryEvidenceContext") or {}
            ),
            "reviewedPolicyContext": deepcopy(baseline_eval.get("reviewedPolicyContext") or {}),
            "passedChecks": baseline_eval["passedChecks"],
            "totalChecks": baseline_eval["totalChecks"],
            "complexity": baseline_eval["complexity"],
        },
        "bestCandidate": {
            "candidateId": best_candidate_id,
            "score": best_eval["score"],
            "trajectoryScore": _evaluation_trajectory_score(best_eval),
            "trajectoryScoreBreakdown": deepcopy(best_eval.get("trajectoryScoreBreakdown") or {}),
            "trajectoryEvidenceContext": deepcopy(best_eval.get("trajectoryEvidenceContext") or {}),
            "reviewedPolicyContext": deepcopy(best_eval.get("reviewedPolicyContext") or {}),
            "passedChecks": best_eval["passedChecks"],
            "totalChecks": best_eval["totalChecks"],
            "complexity": best_eval["complexity"],
            "path": best_candidate_path.as_posix(),
        },
        "keptCandidates": kept_candidates,
        "discardedCandidates": discarded_candidates,
        "iterations": rows,
        "appliedBestVariant": bool(applied_paths),
        "appliedPath": applied_paths[0] if applied_paths else None,
        "appliedPaths": applied_paths,
        "traceSummary": {
            "path": trace_artifact["actualPath"],
            "eventCount": 0,
            "trajectoryCount": 0,
            "episodeCount": 0,
            "evidenceBackedEpisodeCount": 0,
            "bestTrajectoryScore": _evaluation_trajectory_score(best_eval),
            "bestTrajectoryEvidenceMatches": int(
                (best_eval.get("trajectoryEvidenceContext") or {}).get("matchedRecordCount") or 0
            ),
            "winnerExplanation": deepcopy(search_ledger["winnerExplanation"]),
        },
        "learningSummary": {
            "mode": "shadow_only",
            "episodeCount": 0,
            "evidenceBackedEpisodeCount": 0,
            "reasoningPathSignal": {
                "name": REASONING_PATH_EFFICIENCY_SIGNAL_NAME,
                "sourceBackedPathCount": 0,
                "transcriptBackedPathCount": 0,
                "handoffBackedPathCount": 0,
                "bestObservedScore": 0.0,
            },
            "topObservedPaths": [],
            "benchmarkCandidates": [],
            "mutationSeedCandidates": [],
            "policyCandidates": [],
        },
        "learningArtifacts": {
            "mode": "review_only",
            "benchmarkDraftCount": 0,
            "mutationDraftCount": 0,
            "policyDraftCount": 0,
            "benchmarkDraftsPath": benchmark_drafts_artifact["actualPath"],
            "mutationDraftsPath": mutation_drafts_artifact["actualPath"],
            "policyDraftsPath": policy_drafts_artifact["actualPath"],
        },
        "guardedLearningPromotion": {
            "ready": False,
            "status": "blocked",
            "blockedReasons": ["not_evaluated"],
            "mode": "generated_review_manifest",
            "reviewRequired": True,
            "artifactPath": None,
            "minObservedCount": _guarded_learning_min_observed_count(experiment),
            "minPolicyLearningScore": GUARDED_AUTO_PROMOTION_MIN_POLICY_LEARNING_SCORE,
            "acceptedBenchmarkDraftCount": 0,
            "acceptedPolicyDraftCount": 0,
            "deferredBenchmarkDraftCount": 0,
            "deferredPolicyDraftCount": 0,
            "acceptedBenchmarkDraftIds": [],
            "acceptedPolicyDraftIds": [],
            "summary": "Guarded learning promotion has not been evaluated yet.",
            "recommendedAction": (
                "Run the learning summary and approval gates before staging a guarded review "
                "manifest."
            ),
        },
        "learningPromotionAudit": _serialize_learning_promotion_audit_state(
            learning_promotion_audit_state
        ),
        "artifacts": {
            "report": None,
            "results": results_artifact,
            "evidence": evidence_artifact,
            "checkpoint": checkpoint_artifact,
            "checkpointManifest": checkpoint_manifest_artifact,
            "searchLedger": search_ledger_artifact,
            "benchmarkDrafts": benchmark_drafts_artifact,
            "mutationDrafts": mutation_drafts_artifact,
            "policyDrafts": policy_drafts_artifact,
            "guardedLearningReview": guarded_learning_review_artifact,
            "trace": trace_artifact,
            "runRoot": run_root.as_posix(),
        },
    }

    trace_payload = _build_autoagent_trace(
        experiment_path,
        experiment,
        benchmark,
        mutations,
        result,
        candidate_records,
        frontier_snapshots,
        evidence_dataset,
        benchmark_drafts_artifact,
        mutation_drafts_artifact,
        policy_drafts_artifact,
        trace_artifact,
    )
    _write(Path(trace_artifact["actualPath"]), _json(trace_payload))
    result["traceSummary"]["eventCount"] = len(trace_payload["events"])
    result["traceSummary"]["trajectoryCount"] = len(trace_payload["trajectories"])
    result["traceSummary"]["episodeCount"] = len(trace_payload["episodes"])
    result["traceSummary"]["evidenceBackedEpisodeCount"] = int(
        trace_payload["summary"]["evidenceBackedEpisodeCount"]
    )
    result["learningSummary"] = deepcopy(trace_payload["learning"])

    benchmark_drafts_payload = _learning_benchmark_drafts_payload(
        result["learningSummary"],
        experiment=experiment,
        trace_artifact=trace_artifact,
    )
    mutation_drafts_payload = _learning_mutation_drafts_payload(
        result["learningSummary"],
        experiment=experiment,
        trace_artifact=trace_artifact,
    )
    policy_drafts_payload = _learning_policy_drafts_payload(
        result["learningSummary"],
        experiment=experiment,
        trace_artifact=trace_artifact,
    )
    _write(benchmark_drafts_path, _json(benchmark_drafts_payload))
    _write(mutation_drafts_path, _json(mutation_drafts_payload))
    _write(policy_drafts_path, _json(policy_drafts_payload))
    result["learningArtifacts"] = {
        "mode": "review_only",
        "benchmarkDraftCount": int(benchmark_drafts_payload["draftFragmentCount"]),
        "mutationDraftCount": int(mutation_drafts_payload["draftEntryCount"]),
        "policyDraftCount": int(policy_drafts_payload["draftEntryCount"]),
        "benchmarkDraftsPath": benchmark_drafts_artifact["actualPath"],
        "mutationDraftsPath": mutation_drafts_artifact["actualPath"],
        "policyDraftsPath": policy_drafts_artifact["actualPath"],
    }
    guarded_learning_promotion, guarded_learning_review_manifest = _guarded_learning_promotion(
        experiment,
        benchmark_drafts_payload,
        policy_drafts_payload,
        run_root=run_root,
    )
    if guarded_learning_review_manifest is not None:
        _write(guarded_learning_review_path, _json(guarded_learning_review_manifest))
        guarded_learning_review_artifact["actualPath"] = guarded_learning_review_path.as_posix()
        guarded_learning_promotion["artifactPath"] = guarded_learning_review_path.as_posix()
    result["guardedLearningPromotion"] = guarded_learning_promotion
    result["artifacts"]["guardedLearningReview"] = guarded_learning_review_artifact
    result["provenance"]["policy"]["guardedLearningPromotion"] = deepcopy(
        guarded_learning_promotion
    )
    result["provenance"]["artifacts"]["guardedLearningReviewPath"] = (
        guarded_learning_review_artifact["actualPath"]
    )

    report_content = _render_report(result)
    report_artifact = write_docs_artifact(report_path, report_content)
    result["artifacts"]["report"] = report_artifact
    result["provenance"]["artifacts"]["reportPath"] = report_artifact["actualPath"]
    return result


def import_learning_review(
    *,
    experiment_path: Path,
    output_root: Path,
    review_path: Path,
    benchmark_drafts_path: Path | None = None,
    mutation_drafts_path: Path | None = None,
    policy_drafts_path: Path | None = None,
    promoted_benchmark_path: Path | None = None,
    promoted_mutations_path: Path | None = None,
    promoted_policies_path: Path | None = None,
    import_report_path: Path | None = None,
) -> dict[str, Any]:
    experiment = load_experiment(experiment_path)
    run_root = output_root / experiment["name"]

    resolved_benchmark_drafts_path = (
        benchmark_drafts_path or run_root / "draft-benchmark-fragments.json"
    )
    resolved_mutation_drafts_path = mutation_drafts_path or run_root / "draft-mutation-catalog.json"
    resolved_policy_drafts_path = policy_drafts_path or run_root / "draft-policy-catalog.json"
    resolved_promoted_benchmark_path = (
        promoted_benchmark_path or run_root / "reviewed-benchmark.json"
    )
    resolved_promoted_mutations_path = (
        promoted_mutations_path or run_root / "reviewed-mutations.json"
    )
    resolved_promoted_policies_path = promoted_policies_path or run_root / "reviewed-policies.json"
    resolved_import_report_path = import_report_path or run_root / "learning-draft-import.json"
    resolved_promotion_audit_path = run_root / "learning-promotion-audit.json"

    review_manifest = _load_learning_review_manifest(review_path)
    benchmark_drafts_payload = load_json(resolved_benchmark_drafts_path)
    mutation_drafts_payload = load_json(resolved_mutation_drafts_path)
    policy_review_entries = review_manifest.get("policyDrafts") or []
    if policy_review_entries:
        policy_drafts_payload = load_json(resolved_policy_drafts_path)
    else:
        policy_drafts_payload = {"draftEntries": []}
    benchmark_payload = load_benchmark(experiment["benchmarkPath"])
    raw_mutation_payload = load_json(experiment["mutationCatalogPath"])
    base_mutations = load_mutations(experiment["mutationCatalogPath"])
    base_mutations_by_id = {
        str(mutation.get("id")): mutation
        for mutation in base_mutations
        if isinstance(mutation, dict) and mutation.get("id")
    }

    benchmark_drafts = benchmark_drafts_payload.get("draftFragments") or []
    mutation_drafts = mutation_drafts_payload.get("draftEntries") or []
    policy_drafts = policy_drafts_payload.get("draftEntries") or []
    if not isinstance(benchmark_drafts, list):
        raise ValueError("Benchmark draft artifact must contain a 'draftFragments' list.")
    if not isinstance(mutation_drafts, list):
        raise ValueError("Mutation draft artifact must contain a 'draftEntries' list.")
    if not isinstance(policy_drafts, list):
        raise ValueError("Policy draft artifact must contain a 'draftEntries' list.")

    benchmark_drafts_by_id = _index_learning_drafts(
        benchmark_drafts,
        key="draftId",
        context="Benchmark draft artifact",
    )
    mutation_drafts_by_id = _index_learning_drafts(
        mutation_drafts,
        key="draftId",
        context="Mutation draft artifact",
    )
    policy_drafts_by_id = _index_learning_drafts(
        policy_drafts,
        key="draftId",
        context="Policy draft artifact",
    )

    promoted_benchmark = deepcopy(benchmark_payload)
    promoted_benchmark_checks = list(promoted_benchmark.get("checks") or [])
    promoted_benchmark["checks"] = promoted_benchmark_checks
    benchmark_check_ids = {
        str(check.get("id"))
        for check in promoted_benchmark_checks
        if isinstance(check, dict) and check.get("id")
    }
    approved_benchmark_drafts = list(promoted_benchmark.get("approvedLearningDrafts") or [])
    benchmark_review_results: list[dict[str, Any]] = []

    reviewer = review_manifest.get("reviewer")
    reviewed_at = review_manifest.get("reviewedAt")
    benchmark_review_entries = review_manifest.get("benchmarkDrafts") or []
    mutation_review_entries = review_manifest.get("mutationDrafts") or []

    for review_entry in benchmark_review_entries:
        draft_id = str(review_entry["draftId"])
        draft = benchmark_drafts_by_id.get(draft_id)
        if draft is None:
            raise ValueError(
                f"Learning review manifest references unknown benchmark draft '{draft_id}'."
            )
        decision = str(review_entry.get("decision") or "defer")
        review_record = {
            "draftId": draft_id,
            "stagedDecision": review_entry.get("stagedDecision"),
            "decision": decision,
            "reviewerOverride": review_entry.get("stagedDecision") not in (None, decision),
            "decisionRationale": deepcopy(review_entry.get("decisionRationale") or {}),
            "notes": review_entry.get("notes"),
            "sourceSuggestionId": draft.get("sourceSuggestionId"),
        }
        if decision == "accept":
            materialized_checks = _materialize_review_benchmark_checks(
                review_entry,
                draft_entry=draft,
                draft_id=draft_id,
                existing_check_ids=benchmark_check_ids,
            )
            promoted_benchmark_checks.extend(materialized_checks)
            added_check_ids = [str(check["id"]) for check in materialized_checks]
            approved_benchmark_drafts.append(
                {
                    "draftId": draft_id,
                    "sourceSuggestionId": draft.get("sourceSuggestionId"),
                    "reviewer": reviewer,
                    "reviewedAt": reviewed_at,
                    "notes": review_entry.get("notes"),
                    "addedCheckIds": added_check_ids,
                }
            )
            review_record["importStatus"] = "merged_checks"
            review_record["addedCheckIds"] = added_check_ids
        elif decision == "reject":
            review_record["importStatus"] = "rejected"
        else:
            review_record["importStatus"] = "deferred"
        benchmark_review_results.append(review_record)

    promoted_benchmark["approvedLearningDrafts"] = approved_benchmark_drafts

    promoted_mutation_payload = deepcopy(raw_mutation_payload)
    if isinstance(promoted_mutation_payload, list):
        promoted_mutation_payload = {"mutations": promoted_mutation_payload}
    elif not isinstance(promoted_mutation_payload, dict):
        raise ValueError("Mutation catalog must be a JSON object or list.")
    promoted_mutations = list(promoted_mutation_payload.get("mutations") or [])
    promoted_mutation_payload["mutations"] = promoted_mutations
    approved_mutation_drafts = list(promoted_mutation_payload.get("approvedLearningDrafts") or [])
    existing_mutation_ids = {
        str(mutation.get("id"))
        for mutation in promoted_mutations
        if isinstance(mutation, dict) and mutation.get("id")
    }
    mutation_review_results: list[dict[str, Any]] = []

    for review_entry in mutation_review_entries:
        draft_id = str(review_entry["draftId"])
        draft = mutation_drafts_by_id.get(draft_id)
        if draft is None:
            raise ValueError(
                f"Learning review manifest references unknown mutation draft '{draft_id}'."
            )
        decision = str(review_entry.get("decision") or "defer")
        review_record = {
            "draftId": draft_id,
            "stagedDecision": review_entry.get("stagedDecision"),
            "decision": decision,
            "reviewerOverride": review_entry.get("stagedDecision") not in (None, decision),
            "decisionRationale": deepcopy(review_entry.get("decisionRationale") or {}),
            "notes": review_entry.get("notes"),
            "sourceSeedId": draft.get("sourceSeedId"),
            "sourceMutationId": (draft.get("entry") or {}).get("sourceMutationId"),
        }
        if decision == "accept":
            mutation = _materialize_review_mutation(
                review_entry,
                draft,
                base_mutations_by_id=base_mutations_by_id,
                existing_mutation_ids=existing_mutation_ids,
                reviewer=str(reviewer) if reviewer is not None else None,
                reviewed_at=str(reviewed_at) if reviewed_at is not None else None,
            )
            promoted_mutations.append(mutation)
            approved_mutation_drafts.append(
                {
                    "draftId": draft_id,
                    "promotedMutationId": mutation["id"],
                    "sourceSeedId": draft.get("sourceSeedId"),
                    "sourceMutationId": (draft.get("entry") or {}).get("sourceMutationId"),
                    "reviewer": reviewer,
                    "reviewedAt": reviewed_at,
                    "notes": review_entry.get("notes"),
                }
            )
            review_record["importStatus"] = "cloned_mutation"
            review_record["promotedMutationId"] = mutation["id"]
        elif decision == "reject":
            review_record["importStatus"] = "rejected"
        else:
            review_record["importStatus"] = "deferred"
        mutation_review_results.append(review_record)

    promoted_mutation_payload["approvedLearningDrafts"] = approved_mutation_drafts

    promoted_policy_payload: dict[str, Any] | None = None
    promoted_policies_artifact: dict[str, Any] | None = None
    policy_review_results: list[dict[str, Any]] = []
    if policy_review_entries:
        promoted_policy_payload = _load_or_initialize_reviewed_policies_payload(
            resolved_promoted_policies_path,
            experiment=experiment,
            policy_drafts_path=resolved_policy_drafts_path,
        )
        promoted_policies = list(promoted_policy_payload.get("policies") or [])
        promoted_policy_payload["policies"] = promoted_policies
        approved_policy_drafts = list(promoted_policy_payload.get("approvedLearningDrafts") or [])
        promoted_policy_payload["approvedLearningDrafts"] = approved_policy_drafts
        existing_policy_ids = {
            str(policy.get("id"))
            for policy in promoted_policies
            if isinstance(policy, dict) and policy.get("id")
        }

        for review_entry in policy_review_entries:
            draft_id = str(review_entry["draftId"])
            draft = policy_drafts_by_id.get(draft_id)
            if draft is None:
                raise ValueError(
                    f"Learning review manifest references unknown policy draft '{draft_id}'."
                )
            decision = str(review_entry.get("decision") or "defer")
            review_record = {
                "draftId": draft_id,
                "stagedDecision": review_entry.get("stagedDecision"),
                "decision": decision,
                "reviewerOverride": review_entry.get("stagedDecision") not in (None, decision),
                "decisionRationale": deepcopy(review_entry.get("decisionRationale") or {}),
                "notes": review_entry.get("notes"),
                "sourcePolicyId": draft.get("sourcePolicyId"),
            }
            if decision == "accept":
                policy = _materialize_review_policy(
                    review_entry,
                    draft,
                    existing_policy_ids=existing_policy_ids,
                    reviewer=str(reviewer) if reviewer is not None else None,
                    reviewed_at=str(reviewed_at) if reviewed_at is not None else None,
                )
                promoted_policies.append(policy)
                approved_policy_drafts.append(
                    {
                        "draftId": draft_id,
                        "promotedPolicyId": policy["id"],
                        "sourcePolicyId": draft.get("sourcePolicyId"),
                        "reviewer": reviewer,
                        "reviewedAt": reviewed_at,
                        "notes": review_entry.get("notes"),
                    }
                )
                review_record["importStatus"] = "promoted_policy"
                review_record["promotedPolicyId"] = policy["id"]
            elif decision == "reject":
                review_record["importStatus"] = "rejected"
            else:
                review_record["importStatus"] = "deferred"
            policy_review_results.append(review_record)

        promoted_policies_artifact = _write_with_fallback(
            resolved_promoted_policies_path,
            _json(promoted_policy_payload),
        )

    benchmark_artifact = _write_with_fallback(
        resolved_promoted_benchmark_path,
        _json(promoted_benchmark),
    )
    mutation_artifact = _write_with_fallback(
        resolved_promoted_mutations_path,
        _json(promoted_mutation_payload),
    )

    result = {
        "type": "AutoAgentLearningDraftImport",
        "mode": "manual_review_import",
        "experiment": {
            "name": experiment["name"],
            "path": experiment["path"].as_posix(),
            "benchmarkPath": experiment["benchmarkPath"].as_posix(),
            "mutationCatalogPath": experiment["mutationCatalogPath"].as_posix(),
        },
        "review": {
            "path": review_path.as_posix(),
            "reviewer": reviewer,
            "reviewedAt": reviewed_at,
            "summary": review_manifest.get("summary"),
        },
        "sources": {
            "benchmarkDraftsPath": resolved_benchmark_drafts_path.as_posix(),
            "mutationDraftsPath": resolved_mutation_drafts_path.as_posix(),
            "policyDraftsPath": resolved_policy_drafts_path.as_posix()
            if policy_review_entries
            else None,
        },
        "summary": {
            "reviewedBenchmarkDraftCount": len(benchmark_review_results),
            "acceptedBenchmarkDraftCount": sum(
                1 for entry in benchmark_review_results if entry["decision"] == "accept"
            ),
            "importedBenchmarkCheckCount": sum(
                len(entry.get("addedCheckIds") or []) for entry in benchmark_review_results
            ),
            "reviewedMutationDraftCount": len(mutation_review_results),
            "acceptedMutationDraftCount": sum(
                1 for entry in mutation_review_results if entry["decision"] == "accept"
            ),
            "importedMutationCount": sum(
                1 for entry in mutation_review_results if entry.get("promotedMutationId")
            ),
            "reviewedPolicyDraftCount": len(policy_review_results),
            "acceptedPolicyDraftCount": sum(
                1 for entry in policy_review_results if entry["decision"] == "accept"
            ),
            "importedPolicyCount": sum(
                1 for entry in policy_review_results if entry.get("promotedPolicyId")
            ),
        },
        "benchmarkReview": benchmark_review_results,
        "mutationReview": mutation_review_results,
        "policyReview": policy_review_results,
        "artifacts": {
            "promotedBenchmark": benchmark_artifact,
            "promotedMutations": mutation_artifact,
        },
    }
    if promoted_policies_artifact is not None:
        result["artifacts"]["promotedPolicies"] = promoted_policies_artifact

    import_report_artifact = _write_with_fallback(
        resolved_import_report_path,
        _json(result),
    )
    result["artifacts"]["importReport"] = import_report_artifact

    promotion_audit = {
        "type": "AutoAgentLearningPromotionAudit",
        "mode": "manual_review_import",
        "promotionSourceMode": review_manifest.get("mode") or "manual_review",
        "review": deepcopy(result["review"]),
        "experiment": deepcopy(result["experiment"]),
        "sources": deepcopy(result["sources"]),
        "summary": {
            "reviewedBenchmarkDraftCount": len(benchmark_review_results),
            "acceptedBenchmarkDraftCount": sum(
                1 for entry in benchmark_review_results if entry["decision"] == "accept"
            ),
            "rejectedBenchmarkDraftCount": sum(
                1 for entry in benchmark_review_results if entry["decision"] == "reject"
            ),
            "deferredBenchmarkDraftCount": sum(
                1 for entry in benchmark_review_results if entry["decision"] == "defer"
            ),
            "reviewedMutationDraftCount": len(mutation_review_results),
            "acceptedMutationDraftCount": sum(
                1 for entry in mutation_review_results if entry["decision"] == "accept"
            ),
            "rejectedMutationDraftCount": sum(
                1 for entry in mutation_review_results if entry["decision"] == "reject"
            ),
            "deferredMutationDraftCount": sum(
                1 for entry in mutation_review_results if entry["decision"] == "defer"
            ),
            "reviewedPolicyDraftCount": len(policy_review_results),
            "acceptedPolicyDraftCount": sum(
                1 for entry in policy_review_results if entry["decision"] == "accept"
            ),
            "rejectedPolicyDraftCount": sum(
                1 for entry in policy_review_results if entry["decision"] == "reject"
            ),
            "deferredPolicyDraftCount": sum(
                1 for entry in policy_review_results if entry["decision"] == "defer"
            ),
            "importedBenchmarkCheckCount": result["summary"]["importedBenchmarkCheckCount"],
            "importedMutationCount": result["summary"]["importedMutationCount"],
            "importedPolicyCount": result["summary"]["importedPolicyCount"],
        },
        "guardrails": {
            "reviewRequired": True,
            "runtimeEffect": "review_only",
            "autoApplyEnabled": False,
        },
        "decisions": {
            "benchmarkDrafts": deepcopy(benchmark_review_results),
            "mutationDrafts": deepcopy(mutation_review_results),
            "policyDrafts": deepcopy(policy_review_results),
        },
    }
    promotion_audit_artifact = _write_with_fallback(
        resolved_promotion_audit_path,
        _json(promotion_audit),
    )
    result["artifacts"]["promotionAudit"] = promotion_audit_artifact
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a repo-native AutoAgent loop against a custom Copilot agent profile."
    )
    parser.add_argument(
        "--experiment",
        default=(ROOT / "docs" / "agents" / "autoagent-experiment.md").as_posix(),
        help="Path to the AutoAgent experiment markdown file.",
    )
    parser.add_argument(
        "--output-root",
        default=(ROOT / "generated" / "autoagent-runs").as_posix(),
        help="Directory where candidate artifacts should be written.",
    )
    parser.add_argument(
        "--report",
        default=(ROOT / "docs" / "agents" / "autoagent-report.md").as_posix(),
        help="Preferred report path.",
    )
    parser.add_argument(
        "--results",
        default=(ROOT / "docs" / "agents" / "autoagent-results.tsv").as_posix(),
        help="Preferred results ledger path.",
    )
    parser.add_argument(
        "--evidence",
        default=(ROOT / "docs" / "agents" / "autoagent-evidence.json").as_posix(),
        help="Preferred normalized evidence dataset path.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Override the experiment iteration count. Use 0 to honor the experiment file.",
    )
    parser.add_argument(
        "--apply-best",
        action="store_true",
        help="Apply the best candidate back to the target agent profile.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume the run from the checkpoint written under the generated run root.",
    )
    parser.add_argument(
        "--import-learning-review",
        help="Path to a manual review manifest that promotes accepted learning drafts.",
    )
    parser.add_argument(
        "--benchmark-drafts",
        help="Optional path to the generated benchmark draft fragments artifact.",
    )
    parser.add_argument(
        "--mutation-drafts",
        help="Optional path to the generated mutation draft artifact.",
    )
    parser.add_argument(
        "--policy-drafts",
        help="Optional path to the generated policy draft artifact.",
    )
    parser.add_argument(
        "--promoted-benchmark",
        help="Optional output path for the reviewed benchmark artifact.",
    )
    parser.add_argument(
        "--promoted-mutations",
        help="Optional output path for the reviewed mutation artifact.",
    )
    parser.add_argument(
        "--promoted-policies",
        help="Optional output path for the reviewed policy artifact.",
    )
    parser.add_argument(
        "--import-report",
        help="Optional output path for the learning draft import report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.import_learning_review:
        result = import_learning_review(
            experiment_path=Path(args.experiment).resolve(),
            output_root=Path(args.output_root).resolve(),
            review_path=Path(args.import_learning_review).resolve(),
            benchmark_drafts_path=(
                Path(args.benchmark_drafts).resolve() if args.benchmark_drafts else None
            ),
            mutation_drafts_path=(
                Path(args.mutation_drafts).resolve() if args.mutation_drafts else None
            ),
            policy_drafts_path=(Path(args.policy_drafts).resolve() if args.policy_drafts else None),
            promoted_benchmark_path=(
                Path(args.promoted_benchmark).resolve() if args.promoted_benchmark else None
            ),
            promoted_mutations_path=(
                Path(args.promoted_mutations).resolve() if args.promoted_mutations else None
            ),
            promoted_policies_path=(
                Path(args.promoted_policies).resolve() if args.promoted_policies else None
            ),
            import_report_path=(Path(args.import_report).resolve() if args.import_report else None),
        )
    else:
        result = run_autoagent_loop(
            experiment_path=Path(args.experiment).resolve(),
            output_root=Path(args.output_root).resolve(),
            report_path=Path(args.report).resolve(),
            results_path=Path(args.results).resolve(),
            max_iterations=args.max_iterations,
            apply_best=args.apply_best,
            evidence_path=Path(args.evidence).resolve(),
            resume=args.resume,
        )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
