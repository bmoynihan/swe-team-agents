# Path-Specific Copilot Instructions

This directory adds a small, layered instruction set on top of `.github/copilot-instructions.md` and `AGENTS.md`.

Current files:
- `agent-artifacts.instructions.md`
- `agent-system-authoring.instructions.md`
- `agent-arch-auditor.instructions.md`
- `code-review.instructions.md`
- `hooks-and-setup.instructions.md`
- `python.instructions.md`
- `python-tests.instructions.md`

Notes:
- `code-review.instructions.md` is review-only and uses `excludeAgent: "coding-agent"`.
- `agent-arch-auditor.instructions.md` is the path-specific companion instruction for the new Copilot agent-system auditor role.
- These files are additive with `.github/copilot-instructions.md`.
