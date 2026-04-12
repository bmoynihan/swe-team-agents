---
applyTo: ".github/agents/agent-arch-auditor.agent.md,.github/skills/agent-arch-auditor/**/*,docs/agents/agent-architecture-audit-report.md"
---

When editing the Agent Architecture Auditor package:

- Keep the role focused on the Copilot agent substrate: agents, skills, instructions, hooks, setup workflow, artifact ownership, and validator logic.
- Use supported GitHub conventions only.
- Keep findings evidence-first and path-specific.
- Prefer the smallest safe patch plan over broad refactors.
- Preserve least-privilege tool guidance and avoid expanding this role into product implementation.
- Keep the report format stable: short human summary plus exactly one machine-readable JSON object.
- When artifact paths or ownership change, update the skill, prompt, template, state references, and any validator logic together.
