# Agent Arch Auditor Package

This package contains the new `agent-arch-auditor` specialist role and the minimal integration files needed to use it in this repository's manager-led Copilot agent system.

Included contents:
- custom agent prompt under `.github/agents/`
- skill, template, and helper script under `.github/skills/agent-arch-auditor/`
- companion path-specific instruction under `.github/instructions/`
- report artifact under `docs/agents/`
- state and protocol integration touchpoints for Team Lead and SWE Team Protocol
- validator support in `scripts/ci/check_agent_system.py`
- a small integration test under `tests/`

Intent:
- audit GitHub Copilot Agent Mode architecture
- detect unsupported GitHub conventions, duplicate canonical artifacts, role overlaps, stale paths, tool-scope issues, and nondeterministic run behavior
- produce a structured `AgentArchitectureAuditReport`
