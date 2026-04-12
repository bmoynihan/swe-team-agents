#!/usr/bin/env bash
set -euo pipefail

FILE="${1:-docs/agents/task-spec.md}"

required_headings=(
  "Summary"
  "Context"
  "Goals"
  "Non-goals"
  "Acceptance Criteria"
  "Validation Plan"
  "Risks & Mitigations"
  "Rollback Plan"
  "Open Questions"
  "Traceability Matrix"
)

missing=0

if [ ! -f "$FILE" ]; then
  echo "ERROR: file not found: $FILE" >&2
  exit 2
fi

for h in "${required_headings[@]}"; do
  if ! grep -qE "^##[[:space:]]+$h[[:space:]]*$" "$FILE"; then
    echo "Missing heading: ## $h" >&2
    missing=1
  fi
done

# lightweight AC sanity check
if ! grep -qE "\bAC1\b" "$FILE"; then
  echo "WARN: could not find 'AC1' in $FILE (did you forget to fill Acceptance Criteria?)" >&2
fi

if [ "$missing" -ne 0 ]; then
  echo "FAIL: required headings missing." >&2
  exit 1
fi

echo "OK: required headings present in $FILE"


