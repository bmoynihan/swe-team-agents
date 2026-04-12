#!/usr/bin/env python
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {".md", ".json", ".py", ".ps1", ".sh", ".txt", ".yaml", ".yml"}
SKILL_PATH_PATTERN = re.compile(r"\.github/skills/[A-Za-z0-9._/-]+/SKILL\.md")
CONTROL_SINGLETONS = {"current-run.json", "CANONICAL_ARTIFACT_POLICY.md"}
REQUIRED_CANONICAL = [
    ROOT / "docs" / "agents" / "state.json",
    ROOT / "docs" / "agents" / "task-spec.md",
    ROOT / "docs" / "agents" / "patch-report.md",
    ROOT / "docs" / "agents" / "test-report.md",
    ROOT / "docs" / "agents" / "review-report.md",
    ROOT / "docs" / "agents" / "release-report.md",
    ROOT / "docs" / "agents" / "research-report.md",
    ROOT / "docs" / "agents" / "docs-report.md",
    ROOT / "docs" / "agents" / "skills-report.md",
    ROOT / "docs" / "agents" / "protocol.md",
    ROOT / "docs" / "agents" / "mcp-config.json",
    ROOT / "docs" / "agents" / "current-run.json",
    ROOT / "docs" / "agents" / "CANONICAL_ARTIFACT_POLICY.md",
]
OPTIONAL_AGENT_ARCH_AUDITOR = {
    "agent": ROOT / ".github" / "agents" / "agent-arch-auditor.agent.md",
    "skill": ROOT / ".github" / "skills" / "agent-arch-auditor" / "SKILL.md",
    "template": ROOT / ".github" / "skills" / "agent-arch-auditor" / "templates" / "agent-architecture-audit-report.template.md",
    "script": ROOT / ".github" / "skills" / "agent-arch-auditor" / "scripts" / "inventory_agent_surface.sh",
    "instruction": ROOT / ".github" / "instructions" / "agent-arch-auditor.instructions.md",
    "report": ROOT / "docs" / "agents" / "agent-architecture-audit-report.md",
}
STATE_AUDIT_REPORT_ENTRY = '"agentArchitectureAuditReport": "docs/agents/agent-architecture-audit-report.md"'
STATE_INTEGRATION_FILES = [
    ROOT / ".github" / "skills" / "team-lead" / "templates" / "state.json.template.json",
    ROOT / ".github" / "skills" / "swe-team-protocol" / "templates" / "state.json.template.json",
    ROOT / "docs" / "agents" / "state.json",
]
TEAM_LEAD_SKILL = ROOT / ".github" / "skills" / "team-lead" / "SKILL.md"
PROTOCOL_SKILL = ROOT / ".github" / "skills" / "swe-team-protocol" / "SKILL.md"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def iter_text_files():
    this_file = Path(__file__).resolve()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.resolve() == this_file:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("docs/agents/runs/"):
            continue
        if "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name.endswith(".agent.md"):
            yield path


def require_text(path: Path, token: str, message: str) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if token not in text:
        fail(f"{message}: {path.relative_to(ROOT).as_posix()}")


def ensure_required_files() -> None:
    missing = [path.relative_to(ROOT).as_posix() for path in REQUIRED_CANONICAL if not path.exists()]
    if missing:
        fail(f"Missing canonical agent artifacts: {', '.join(missing)}")


def ensure_no_pycache() -> None:
    stale = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.rglob("__pycache__") if path.is_dir())
    if stale:
        fail("Remove committed __pycache__ directories: " + ", ".join(stale))


def ensure_optional_agent_arch_auditor() -> None:
    agent_file = OPTIONAL_AGENT_ARCH_AUDITOR["agent"]
    if not agent_file.exists():
        return

    missing = [
        path.relative_to(ROOT).as_posix()
        for path in OPTIONAL_AGENT_ARCH_AUDITOR.values()
        if not path.exists()
    ]
    if missing:
        fail("Optional agent-arch-auditor package is incomplete: " + ", ".join(missing))

    require_text(
        OPTIONAL_AGENT_ARCH_AUDITOR["agent"],
        ".github/skills/agent-arch-auditor/SKILL.md",
        "agent-arch-auditor prompt must load its skill",
    )
    require_text(
        OPTIONAL_AGENT_ARCH_AUDITOR["agent"],
        "docs/agents/agent-architecture-audit-report.md",
        "agent-arch-auditor prompt must reference its report artifact",
    )
    require_text(
        OPTIONAL_AGENT_ARCH_AUDITOR["skill"],
        "templates/agent-architecture-audit-report.template.md",
        "agent-arch-auditor skill must reference its report template",
    )
    require_text(
        OPTIONAL_AGENT_ARCH_AUDITOR["instruction"],
        "docs/agents/agent-architecture-audit-report.md",
        "agent-arch-auditor instruction must target the report artifact",
    )
    require_text(
        TEAM_LEAD_SKILL,
        "agent-arch-auditor",
        "team-lead skill must mention the optional agent-arch-auditor integration",
    )
    require_text(
        PROTOCOL_SKILL,
        "agent-arch-auditor",
        "swe-team-protocol skill must mention the optional agent-arch-auditor integration",
    )
    for path in STATE_INTEGRATION_FILES:
        require_text(
            path,
            STATE_AUDIT_REPORT_ENTRY,
            "state integration is missing the agentArchitectureAuditReport entry",
        )


def ensure_current_run() -> None:
    agents_root = ROOT / "docs" / "agents"
    payload = json.loads((agents_root / "current-run.json").read_text(encoding="utf-8"))
    run_id = payload.get("currentRunId")
    run_path = payload.get("currentRunPath")
    if not run_id or not run_path:
        fail("current-run.json must contain currentRunId and currentRunPath")
    run_root = ROOT / run_path
    if not run_root.exists():
        fail(f"currentRunPath does not exist: {run_path}")
    if not (run_root / "hook-audit").exists():
        fail(f"Missing hook-audit directory: {(run_root / 'hook-audit').relative_to(ROOT).as_posix()}")

    mutable_root_files = [
        path for path in agents_root.iterdir()
        if path.is_file() and path.name not in CONTROL_SINGLETONS
    ]
    missing = []
    for path in mutable_root_files:
        candidate = run_root / path.name
        if not candidate.exists():
            missing.append(candidate.relative_to(ROOT).as_posix())
    if missing:
        fail("Missing run-scoped snapshot artifacts: " + ", ".join(sorted(missing)))


def ensure_custom_agents() -> None:
    agents_dir = ROOT / ".github" / "agents"
    unsupported = sorted(path.relative_to(ROOT).as_posix() for path in agents_dir.glob("*.agent"))
    if unsupported:
        fail(f"Unsupported custom-agent filenames: {', '.join(unsupported)}")
    agent_files = sorted(agents_dir.glob("*.agent.md"))
    if not agent_files:
        fail("No custom agent files found under .github/agents/*.agent.md")
    release_report_owners = []
    for agent_file in agent_files:
        text = agent_file.read_text(encoding="utf-8")
        for skill_path in SKILL_PATH_PATTERN.findall(text):
            if not (ROOT / skill_path).exists():
                fail(
                    f"Referenced skill does not exist: {skill_path} "
                    f"(from {agent_file.relative_to(ROOT).as_posix()})"
                )
        if "docs/agents/release-report.md" in text:
            release_report_owners.append(agent_file.relative_to(ROOT).as_posix())
    if len(release_report_owners) != 1:
        fail("Expected exactly one release-report owner in .github/agents, found: " + ", ".join(release_report_owners))


def ensure_hooks() -> None:
    hooks_dir = ROOT / ".github" / "hooks"
    hook_configs = list(hooks_dir.glob("*.json"))
    if not hook_configs:
        fail("Expected at least one .json hook config under .github/hooks/")
    if (ROOT / ".github" / "scripts" / "hooks").exists():
        fail("Unsupported duplicate hook root found at .github/scripts/hooks/")
    text = (hooks_dir / "hooks.json").read_text(encoding="utf-8")
    if "docs/agents/_hook-audit" in text:
        fail("hooks.json still points at shared singleton hook audit paths")
    if "<current-run>" not in text:
        fail("hooks.json must use the <current-run> placeholder for run-scoped audit paths")


def ensure_setup_workflow() -> None:
    workflow = ROOT / ".github" / "workflows" / "copilot-setup-steps.yml"
    if not workflow.exists():
        fail("Missing .github/workflows/copilot-setup-steps.yml")
    if (ROOT / ".github" / "workflows" / "copilot-setup-steps.md").exists():
        fail("Found unsupported documentation file in .github/workflows/copilot-setup-steps.md")
    text = workflow.read_text(encoding="utf-8")
    jobs_match = re.search(r"(?ms)^jobs:\s*\n(?P<body>(?:^  .*(?:\n|$))*)", text)
    if not jobs_match:
        fail("copilot-setup-steps.yml must define a jobs section")
    jobs = []
    for line in jobs_match.group("body").splitlines():
        match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if match:
            jobs.append(match.group(1))
    if jobs != ["copilot-setup-steps"]:
        fail("copilot-setup-steps.yml must contain exactly one job named copilot-setup-steps")


def ensure_no_unsupported_paths() -> None:
    if (ROOT / ".github" / "docs" / "agents").exists():
        fail("Unsupported duplicate artifact root found at .github/docs/agents/")


def ensure_clean_text() -> None:
    blocked_tokens = [
        ".github/docs/agents",
        "release-engineer",
        "docs/agents/_hook-audit",
        "copilot-setup-steps.md",
        ":contentReference[",
    ]
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in blocked_tokens:
            if token in text:
                fail(f"Found stale token '{token}' in {path.relative_to(ROOT).as_posix()}")
        if len(re.findall(r"^```", text, re.MULTILINE)) % 2 != 0:
            fail(f"Unbalanced fenced code block in {path.relative_to(ROOT).as_posix()}")


def main() -> None:
    ensure_required_files()
    ensure_no_pycache()
    ensure_optional_agent_arch_auditor()
    ensure_current_run()
    ensure_custom_agents()
    ensure_hooks()
    ensure_setup_workflow()
    ensure_no_unsupported_paths()
    ensure_clean_text()
    print("agent-system-consistency: PASS")


if __name__ == "__main__":
    main()
