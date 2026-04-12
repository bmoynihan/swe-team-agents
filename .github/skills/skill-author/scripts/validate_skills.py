#!/usr/bin/env python3
"""
validate_skills.py

Lightweight validation for Agent Skills under .github/skills/**.

Goals:
- No external dependencies (no PyYAML required).
- Catch the most common portability issues:
  - missing frontmatter
  - missing name/description
  - skill directory name != frontmatter name
  - invalid name format (lowercase + hyphens)
  - description too long
  - missing required report JSON block

Exit codes:
- 0: all checks passed (or only warnings)
- 1: at least one error
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

ROOT = Path.cwd()

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
FENCE_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


@dataclass
class Finding:
    level: str  # "ERROR" | "WARN"
    path: Path
    message: str


def extract_frontmatter(md: str) -> Optional[Tuple[str, str]]:
    """
    Return (frontmatter, body) or None if no YAML frontmatter block at top.
    """
    if not md.startswith("---\n"):
        return None
    end = md.find("\n---\n", 4)
    if end == -1:
        return None
    front = md[4:end]
    body = md[end + len("\n---\n") :]
    return front, body


def parse_name(front: str) -> Optional[str]:
    m = re.search(r"^name:\s*(.+?)\s*$", front, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    # strip simple quotes
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    return val.strip()


def parse_description(front: str) -> Optional[str]:
    """
    Supports:
      description: "text"
      description: >
        folded
        text
      description: |
        literal
    """
    m = re.search(r"^description:\s*(.*)\s*$", front, re.MULTILINE)
    if not m:
        return None
    rest = m.group(1).strip()

    # Inline scalar
    if rest and rest not in (">", "|"):
        val = rest
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        return val.strip()

    # Block scalar
    # Capture indented lines following the description line
    lines = front.splitlines()
    # Find the description line index
    desc_idx = None
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            desc_idx = i
            break
    if desc_idx is None:
        return None
    block_lines = []
    for line in lines[desc_idx + 1 :]:
        if not line.startswith("  "):  # block indentation is typically 2 spaces
            break
        block_lines.append(line[2:])

    if rest == "|":
        return "\n".join(block_lines).strip()
    # default folded
    return " ".join([ln.strip() for ln in block_lines]).strip()


def validate_skill_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    md = path.read_text(encoding="utf-8", errors="replace")
    fm = extract_frontmatter(md)
    if fm is None:
        return [
            Finding("ERROR", path, "Missing YAML frontmatter block at top of file (--- ... ---).")
        ]
    front, body = fm

    name = parse_name(front)
    desc = parse_description(front)

    if not name:
        findings.append(Finding("ERROR", path, "Missing required frontmatter key: name"))
    if not desc:
        findings.append(Finding("ERROR", path, "Missing required frontmatter key: description"))

    if name:
        dir_name = path.parent.name
        if dir_name != name:
            findings.append(
                Finding(
                    "ERROR",
                    path,
                    f"Directory name '{dir_name}' must match frontmatter name '{name}'",
                )
            )
        if not NAME_RE.match(name):
            findings.append(
                Finding(
                    "ERROR",
                    path,
                    f"Invalid skill name '{name}'. Must be lowercase, hyphenated, max 64 chars.",
                )
            )
    if desc:
        if len(desc) > 1024:
            findings.append(
                Finding(
                    "ERROR", path, f"Description too long ({len(desc)} chars). Keep <= 1024 chars."
                )
            )
        # heuristic: encourage trigger phrases
        if "Use when" not in desc and "use when" not in desc:
            findings.append(
                Finding(
                    "WARN",
                    path,
                    "Description should usually include 'Use when ...' trigger hints "
                    "for discoverability.",
                )
            )

    # Heuristic body checks (warnings only)
    required_headings = ["## When to use", "## Procedure", "## Failure handling"]
    for h in required_headings:
        if h.lower() not in body.lower():
            findings.append(Finding("WARN", path, f"Recommended section missing: {h}"))

    # Security section: accept several common variants
    if "security" not in body.lower():
        findings.append(
            Finding("WARN", path, "Recommended section missing: Security & privacy notes")
        )

    return findings


def validate_skills_report(report_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not report_path.exists():
        findings.append(
            Finding("WARN", report_path, "Skills report not found. Expected this file to exist.")
        )
        return findings

    md = report_path.read_text(encoding="utf-8", errors="replace")
    matches = FENCE_JSON_RE.findall(md)

    if len(matches) == 0:
        findings.append(
            Finding(
                "ERROR",
                report_path,
                "No fenced ```json { ... } ``` block found "
                "(expected exactly one SkillsReport object).",
            )
        )
        return findings
    if len(matches) > 1:
        findings.append(
            Finding(
                "ERROR", report_path, f"Found {len(matches)} JSON blocks; expected exactly one."
            )
        )
        return findings

    raw = matches[0]
    try:
        obj = json.loads(raw)
    except Exception as e:
        findings.append(Finding("ERROR", report_path, f"SkillsReport JSON is not valid JSON: {e}"))
        return findings

    if obj.get("type") != "SkillsReport":
        findings.append(
            Finding("ERROR", report_path, "SkillsReport JSON must have type='SkillsReport'")
        )
    if obj.get("status") not in ("READY_FOR_QUALITY_GATE", "BLOCKED", "READY_FOR_HUMAN_RELEASE"):
        findings.append(
            Finding(
                "WARN",
                report_path,
                "SkillsReport.status should usually be READY_FOR_QUALITY_GATE or BLOCKED.",
            )
        )

    return findings


def main() -> int:
    findings: list[Finding] = []

    skill_glob = ROOT / ".github" / "skills"
    if not skill_glob.exists():
        print(
            "WARN: .github/skills directory not found in current working directory.",
            file=sys.stderr,
        )
        return 0

    skill_files = sorted(skill_glob.glob("*/SKILL.md"))
    if not skill_files:
        print("WARN: No SKILL.md files found under .github/skills/*/SKILL.md", file=sys.stderr)
        return 0

    for sf in skill_files:
        findings.extend(validate_skill_file(sf))

    
    report_candidates = [
        ROOT / ".github" / "docs" / "agents" / "skills-report.md",
        ROOT / "docs" / "agents" / "skills-report.md",
    ]
    for rp in report_candidates:
        if rp.exists():
            findings.extend(validate_skills_report(rp))
            break
    else:
        findings.append(
            Finding(
                "WARN", report_candidates[0], "No skills-report.md found in expected locations."
            )
        )

    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]

    for f in errors + warns:
        print(f"{f.level}: {f.path.as_posix()}: {f.message}")

    if errors:
        print(f"\nFAILED: {len(errors)} error(s), {len(warns)} warning(s).")
        return 1
    print(f"\nOK: {len(warns)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




