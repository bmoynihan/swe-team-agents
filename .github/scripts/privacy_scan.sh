#!/usr/bin/env bash
set -euo pipefail

# Lightweight privacy scan:
# - looks for log/telemetry calls + risky fields
# - prints findings to stdout (does not write files)

ROOT="${1:-.}"

echo "== Privacy Scan (lightweight) =="
echo "Root: $ROOT"
echo

have_rg=0
command -v rg >/dev/null 2>&1 && have_rg=1

scan() {
  local pattern="$1"
  local label="$2"
  echo "-- $label"
  if [[ $have_rg -eq 1 ]]; then
    rg -n --hidden --no-ignore-vcs "$pattern" "$ROOT" \
      -g'!.git/**' -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/build/**' || true
  else
    grep -RIn --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
      -e "$pattern" "$ROOT" || true
  fi
  echo
}

scan '\b(logger|logging|getLogger|console\.log|print)\b' "Logging calls"
scan '\b(telemetry|analytics|track|capture|event|metrics|prometheus)\b' "Telemetry/analytics"
scan '\b(Authorization|Bearer|cookie|set-cookie|x-api-key|api[_-]?key|token|jwt|secret)\b' "Secrets/auth headers"
scan '\b(email|e-mail|phone|address|dob|birth|ssn|passport|credit|card|iban)\b' "PII indicators"
scan '\b(ip(_address)?|device(_id)?|session(_id)?|user(_id)?|customer(_id)?)\b' "Identifiers (high-cardinality risk)"
scan '\b(INSERT|UPDATE|DELETE|SELECT|database|db\.|redis|s3|bucket|persist|retention)\b' "Persistence/retention clues"

echo "== End scan =="

