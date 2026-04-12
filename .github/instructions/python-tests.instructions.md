---
applyTo: "tests/**/*.py"
---

When writing or updating Python tests in this repository:

## Use the repository's testing style
- Use `pytest`.
- Keep tests small, explicit, and deterministic.
- Prefer direct assertions over overly abstract helper layers.
- Name tests for observable behavior, not implementation details.

## Cover the right risks
- Test success paths and at least one failure or edge path when behavior changes.
- Mock or isolate external processes, network calls, time, and filesystem effects when needed.
- Use `tmp_path`, fixtures, and parametrization when they make the test clearer.
- Keep each test focused on one behavior.

## Protect agent-system reliability
- For CI and validator changes, add or update tests for path conventions, artifact ownership, and failure conditions.
- Do not rely on ambient files outside the test fixture or repository.
- Keep tests runnable with the project's existing `pytest` setup and without extra services.
