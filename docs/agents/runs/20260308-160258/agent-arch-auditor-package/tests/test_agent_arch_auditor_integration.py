from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_agent_arch_auditor_role_files_exist() -> None:
    required = [
        ROOT / ".github" / "agents" / "agent-arch-auditor.agent.md",
        ROOT / ".github" / "skills" / "agent-arch-auditor" / "SKILL.md",
        ROOT / ".github" / "skills" / "agent-arch-auditor" / "templates" / "agent-architecture-audit-report.template.md",
        ROOT / ".github" / "skills" / "agent-arch-auditor" / "scripts" / "inventory_agent_surface.sh",
        ROOT / ".github" / "instructions" / "agent-arch-auditor.instructions.md",
        ROOT / "docs" / "agents" / "agent-architecture-audit-report.md",
    ]

    missing = [path.as_posix() for path in required if not path.exists()]
    assert not missing, f"missing agent-arch-auditor package files: {missing}"


def test_validator_knows_agent_arch_auditor_optional_integration() -> None:
    text = (ROOT / "scripts" / "ci" / "check_agent_system.py").read_text(encoding="utf-8")

    assert "ensure_optional_agent_arch_auditor" in text
    assert ".github/agents/agent-arch-auditor.agent.md" in text
    assert ".github/instructions/agent-arch-auditor.instructions.md" in text
    assert '"agentArchitectureAuditReport": "docs/agents/agent-architecture-audit-report.md"' in text
