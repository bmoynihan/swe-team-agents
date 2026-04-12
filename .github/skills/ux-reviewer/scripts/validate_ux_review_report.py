#!/usr/bin/env python3
"""
Validate a UX review markdown artifact.

Rules enforced:
- file exists
- contains exactly one fenced code block
- fenced block parses as JSON
- required UXReviewReport keys exist
- enum-like values are within allowed sets where checked
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL = {
    "type",
    "status",
    "goal",
    "scope",
    "specAlignment",
    "heuristicsReview",
    "accessibilityReview",
    "contentReview",
    "statesReview",
    "designSystemConsistency",
    "blockers",
    "nonBlockingFindings",
    "evidence",
    "readyForQualityGate",
}

STATUS_VALUES = {"PASS", "FAIL"}
GENERIC_VERDICTS = {"pass", "fail", "partial", "not_applicable", "not_checked"}
CHECK_VERDICTS = {"pass", "fail", "not_checked"}
FORM_VERDICTS = {"pass", "fail", "not_applicable", "not_checked"}
STATE_VERDICTS = {"pass", "fail", "not_applicable", "not_checked"}
DESIGN_VERDICTS = {"pass", "fail", "not_checked"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_markdown(path: Path) -> str:
    if not path.exists():
        fail(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_code_blocks(markdown: str) -> list[str]:
    pattern = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL)
    return pattern.findall(markdown)


def ensure_summary_before_json(markdown: str) -> None:
    first_fence = markdown.find("```")
    if first_fence == -1:
        fail("No fenced code block found.")
    summary = markdown[:first_fence].strip()
    if not summary:
        fail("Expected a human summary before the JSON block.")
    summary_lines = [line for line in summary.splitlines() if line.strip()]
    if len(summary_lines) > 12:
        fail(f"Human summary exceeds 12 non-empty lines ({len(summary_lines)} found).")


def ensure_required_keys(report: dict) -> None:
    missing = REQUIRED_TOP_LEVEL - set(report.keys())
    if missing:
        fail(f"Missing required top-level keys: {sorted(missing)}")


def ensure_status(report: dict) -> None:
    if report["type"] != "UXReviewReport":
        fail("type must be UXReviewReport")
    if report["status"] not in STATUS_VALUES:
        fail(f"status must be one of {sorted(STATUS_VALUES)}")


def ensure_scope(report: dict) -> None:
    scope = report["scope"]
    if not isinstance(scope, dict):
        fail("scope must be an object")
    for key in ("summary", "pathsReviewed", "userJourneys"):
        if key not in scope:
            fail(f"scope missing key: {key}")


def ensure_collections(report: dict) -> None:
    collection_keys = [
        "specAlignment",
        "heuristicsReview",
        "contentReview",
        "statesReview",
        "blockers",
        "nonBlockingFindings",
        "evidence",
    ]
    for key in collection_keys:
        if not isinstance(report[key], list):
            fail(f"{key} must be a list")


def ensure_spec_alignment(report: dict) -> None:
    for idx, item in enumerate(report["specAlignment"], start=1):
        if not isinstance(item, dict):
            fail(f"specAlignment[{idx}] must be an object")
        for key in ("acceptanceCriterion", "verdict", "evidence"):
            if key not in item:
                fail(f"specAlignment[{idx}] missing key: {key}")
        if item["verdict"] not in GENERIC_VERDICTS:
            fail(f"specAlignment[{idx}].verdict invalid: {item['verdict']}")


def ensure_heuristics(report: dict) -> None:
    for idx, item in enumerate(report["heuristicsReview"], start=1):
        if not isinstance(item, dict):
            fail(f"heuristicsReview[{idx}] must be an object")
        for key in ("heuristic", "verdict", "evidence", "notes"):
            if key not in item:
                fail(f"heuristicsReview[{idx}] missing key: {key}")
        if item["verdict"] not in {"pass", "fail", "not_applicable"}:
            fail(f"heuristicsReview[{idx}].verdict invalid: {item['verdict']}")


def ensure_accessibility(report: dict) -> None:
    acc = report["accessibilityReview"]
    if not isinstance(acc, dict):
        fail("accessibilityReview must be an object")
    expected_keys = {
        "wcagTarget",
        "keyboard",
        "focus",
        "semantics",
        "formsAndErrors",
        "contrast",
        "targetSize",
        "statusMessages",
    }
    missing = expected_keys - set(acc.keys())
    if missing:
        fail(f"accessibilityReview missing keys: {sorted(missing)}")

    for key in ("keyboard", "focus", "semantics", "contrast"):
        node = acc[key]
        if node["verdict"] not in CHECK_VERDICTS:
            fail(f"accessibilityReview.{key}.verdict invalid: {node['verdict']}")
    for key in ("formsAndErrors", "targetSize", "statusMessages"):
        node = acc[key]
        if node["verdict"] not in FORM_VERDICTS:
            fail(f"accessibilityReview.{key}.verdict invalid: {node['verdict']}")


def ensure_content(report: dict) -> None:
    for idx, item in enumerate(report["contentReview"], start=1):
        if not isinstance(item, dict):
            fail(f"contentReview[{idx}] must be an object")
        for key in ("area", "verdict", "evidence"):
            if key not in item:
                fail(f"contentReview[{idx}] missing key: {key}")
        if item["verdict"] not in {"pass", "fail", "not_applicable"}:
            fail(f"contentReview[{idx}].verdict invalid: {item['verdict']}")


def ensure_states(report: dict) -> None:
    for idx, item in enumerate(report["statesReview"], start=1):
        if not isinstance(item, dict):
            fail(f"statesReview[{idx}] must be an object")
        for key in ("state", "verdict", "notes"):
            if key not in item:
                fail(f"statesReview[{idx}] missing key: {key}")
        if item["verdict"] not in STATE_VERDICTS:
            fail(f"statesReview[{idx}].verdict invalid: {item['verdict']}")


def ensure_design_system(report: dict) -> None:
    ds = report["designSystemConsistency"]
    if not isinstance(ds, dict):
        fail("designSystemConsistency must be an object")
    for key in ("verdict", "evidence"):
        if key not in ds:
            fail(f"designSystemConsistency missing key: {key}")
    if ds["verdict"] not in DESIGN_VERDICTS:
        fail(f"designSystemConsistency.verdict invalid: {ds['verdict']}")


def ensure_evidence(report: dict) -> None:
    for idx, item in enumerate(report["evidence"], start=1):
        if not isinstance(item, dict):
            fail(f"evidence[{idx}] must be an object")
        for key in ("commandOrCheck", "result", "notes"):
            if key not in item:
                fail(f"evidence[{idx}] missing key: {key}")
        if item["result"] not in {"pass", "fail", "not_run"}:
            fail(f"evidence[{idx}].result invalid: {item['result']}")


def ensure_boolean(report: dict) -> None:
    if not isinstance(report["readyForQualityGate"], bool):
        fail("readyForQualityGate must be a boolean")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: {Path(argv[0]).name} <ux-review-report.md>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    markdown = load_markdown(path)
    ensure_summary_before_json(markdown)

    blocks = extract_code_blocks(markdown)
    if len(blocks) != 1:
        fail(f"Expected exactly one fenced code block, found {len(blocks)}")

    try:
        report = json.loads(blocks[0])
    except json.JSONDecodeError as exc:
        fail(f"JSON parse error: {exc}")

    if not isinstance(report, dict):
        fail("Top-level JSON must be an object")

    ensure_required_keys(report)
    ensure_status(report)
    ensure_scope(report)
    ensure_collections(report)
    ensure_spec_alignment(report)
    ensure_heuristics(report)
    ensure_accessibility(report)
    ensure_content(report)
    ensure_states(report)
    ensure_design_system(report)
    ensure_evidence(report)
    ensure_boolean(report)

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


