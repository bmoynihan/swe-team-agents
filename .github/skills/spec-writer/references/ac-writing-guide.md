# Acceptance Criteria Writing Guide (Spec Writer)

## A strong AC is:
- observable (a user/system can tell it happened)
- binary (pass/fail)
- scoped (one PR)
- testable (command/test name included)

## Common anti-patterns (don’t do this)
- “Fix the bug.” (no observable behavior)
- “Improve performance.” (no measurable target or evidence)
- “Refactor X.” (implementation step, not outcome)
- “Add tests.” (not a requirement; tests are evidence for requirements)

## Preferred phrasing patterns
- “When <precondition>, the system <does X> and <returns Y>.”
- “Given <input>, <output> equals <value>.”
- “If <error condition>, return <error type/code/message> and do not <side effect>.”

## Evidence methods
Prefer (in order):
1. deterministic unit/integration tests already in repo
2. targeted commands with stable output
3. log evidence with a unique, stable message


