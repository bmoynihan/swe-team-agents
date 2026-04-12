#!/usr/bin/env python3
"""Validate the SREReport JSON block inside a markdown report.

Rules:
- markdown contains exactly one fenced code block with JSON (```json ... ```)
- JSON is a single object with required keys
- status is READY_FOR_QUALITY_GATE or BLOCKED

This script is intentionally dependency-free.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List

RE_BLOCK = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)

REQUIRED_TOP_LEVEL: List[str] = [
    "type",
    "status",
    "goal",
    "runbookEntries",
    "goldenSignalAlerts",
    "useMethodChecks",
    "incidentScenarios",
    "dependenciesAndBlastRadius",
    "knownIssues",
    "followUps",
    "notesToTeamLead",
]

ALLOWED_STATUS = {"READY_FOR_QUALITY_GATE", "BLOCKED"}


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: validate_sre_report.py <path-to-sre-report.md>")

    path = sys.argv[1]
    try:
        text = open(path, "r", encoding="utf-8").read()
    except FileNotFoundError:
        fail(f"File not found: {path}")

    blocks = RE_BLOCK.findall(text)
    if len(blocks) != 1:
        fail(f"Expected exactly 1 ```json``` block, found {len(blocks)}")

    raw = blocks[0]
    try:
        data: Dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON: {e}")

    if not isinstance(data, dict):
        fail("Top-level JSON must be an object")

    missing = [k for k in REQUIRED_TOP_LEVEL if k not in data]
    if missing:
        fail(f"Missing required keys: {', '.join(missing)}")

    if data.get("type") != "SREReport":
        fail("type must be 'SREReport'")

    status = data.get("status")
    if status not in ALLOWED_STATUS:
        fail(f"status must be one of {sorted(ALLOWED_STATUS)}")

    # Basic structural checks (lightweight; avoid being overly prescriptive)
    for list_key in [
        "runbookEntries",
        "goldenSignalAlerts",
        "useMethodChecks",
        "incidentScenarios",
        "dependenciesAndBlastRadius",
        "knownIssues",
        "followUps",
        "notesToTeamLead",
    ]:
        if not isinstance(data.get(list_key), list):
            fail(f"{list_key} must be a list")

    print("OK: SREReport JSON block validated")


if __name__ == "__main__":
    main()


