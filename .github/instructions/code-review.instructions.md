---
applyTo: "**"
excludeAgent: "coding-agent"
---

When performing Copilot code review in this repository:

## Prioritize only high-signal findings
- Focus on correctness, security, GitHub compatibility, determinism, and maintainability risks.
- Prefer fewer, stronger findings over many low-value comments.
- Do not comment on purely stylistic issues unless they hide a real defect or future maintenance risk.

## Review this repository with its agent-system architecture in mind
- Treat `docs/agents/` as the only live shared artifact root.
- Flag duplicate mutable roots, competing canonical artifacts, path drift, or role ownership conflicts.
- For agent-system changes, verify supported GitHub conventions for `.github/agents/*.agent.md`, `.github/instructions/**/*.instructions.md`, `.github/hooks/*.json`, and `.github/workflows/copilot-setup-steps.yml`.
- Flag stale placeholders, obsolete role names, broken schema examples, and unbalanced fenced code blocks when they can confuse models or break automation.

## Hooks and workflow review expectations
- Verify run-scoped hook audit paths and consistency between hook JSON, Bash scripts, and PowerShell scripts.
- Check for least-privilege workflow permissions, explicit timeouts, and safe triggers.
- Flag secret logging, environment dumping, or unsafe exfiltration patterns immediately.

## Python and validation review expectations
- Prefer deterministic tests and validators that avoid network access.
- Check repo-wide scanners for false positives, self-matching rules, and correct exclusions for run snapshots and caches.
- Expect targeted tests or validation evidence when CI, hooks, or agent contracts change.

## Comment behavior
- Surface the highest-severity issues first.
- Make each finding specific and actionable.
- Avoid asking for changes that GitHub Copilot code review does not control, such as comment formatting or merge policy behavior.
