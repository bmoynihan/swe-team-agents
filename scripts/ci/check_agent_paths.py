#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

FORBIDDEN_TOKEN = "docs/agent/"
TEXT_SUFFIXES = {".json", ".md", ".ps1", ".py", ".sh", ".yaml", ".yml"}
EXCLUDED_RELATIVE_PATHS = {
    ".github/instructions/agent-artifacts.instructions.md",
    ".github/tests/agent-path-policy.test.ps1",
    "scripts/ci/check_agent_paths.py",
    "scripts/ci/check_agent_paths.sh",
}


def iter_candidate_files(root: Path):
    for rel_dir in (".github", "scripts"):
        directory = root / rel_dir
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts:
                continue
            rel_path = path.relative_to(root).as_posix()
            if rel_path in EXCLUDED_RELATIVE_PATHS:
                continue
            if path.suffix.lower() in TEXT_SUFFIXES or path.name.endswith(".agent.md"):
                yield path

    agents_file = root / "AGENTS.md"
    if agents_file.exists():
        yield agents_file


def find_matches(root: Path) -> list[str]:
    matches: list[str] = []
    for path in iter_candidate_files(root):
        rel_path = path.relative_to(root).as_posix()
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            if FORBIDDEN_TOKEN in line:
                matches.append(f"{rel_path}:{line_number}:{line.strip()}")
    return matches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[2], type=Path)
    args = parser.parse_args()

    root = args.root.resolve()

    print("== check_agent_paths ==")
    matches = find_matches(root)
    if matches:
        for match in matches:
            print(match)
        print("ERROR: found forbidden path token docs/agent/")
        raise SystemExit(1)

    print("== check_agent_paths: PASS ==")


if __name__ == "__main__":
    main()
