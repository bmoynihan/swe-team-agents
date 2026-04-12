#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

say() { printf '%s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

# Use a temp audit dir so smoke tests don't pollute repo artifacts.
TMP_AUDIT_DIR="${TMPDIR:-/tmp}/copilot-hooks-audit-$$"
TMP_AUDIT_LOG="${TMP_AUDIT_DIR}/tool-audit.jsonl"

cleanup() {
  rm -rf "$TMP_AUDIT_DIR" >/dev/null 2>&1 || true
}
trap cleanup EXIT

mkdir -p "$TMP_AUDIT_DIR"

export HOOK_AUDIT_DIR="$TMP_AUDIT_DIR"
export HOOK_AUDIT_LOG="$TMP_AUDIT_LOG"

say "== Copilot Hooks Smoke Test =="
say "Audit dir: $HOOK_AUDIT_DIR"
say

# 1) Validate hooks.json if present
HOOKS_JSON=".github/hooks/hooks.json"
if [[ -f "$HOOKS_JSON" ]]; then
  say "[1/5] Validate $HOOKS_JSON"
  if have jq; then
    jq . "$HOOKS_JSON" >/dev/null || die "hooks.json is not valid JSON"
    say "  ✓ JSON valid (jq)"
  else
    say "  ! jq not found; skipping JSON validation (install jq for stronger checks)"
  fi
else
  die "Missing $HOOKS_JSON"
fi
say

# 2) sessionStart
say "[2/5] Run session_start.sh"
[[ -x "scripts/hooks/session_start.sh" ]] || die "scripts/hooks/session_start.sh missing or not executable"
echo '{}' | HOOK_EVENT="sessionStart" scripts/hooks/session_start.sh >/dev/null
[[ -f "$TMP_AUDIT_LOG" ]] || die "audit log not created by session_start"
say "  ✓ session_start wrote audit log"
say

# 3) Deny fixture (preToolUse)
say "[3/5] Run pretool_denylist.sh deny fixture"
[[ -x "scripts/hooks/pretool_denylist.sh" ]] || die "scripts/hooks/pretool_denylist.sh missing or not executable"

DENY_INPUT='{"toolName":"bash","toolArgs":"{\"command\":\"rm -rf /\"}"}'
DENY_OUT="$(printf '%s' "$DENY_INPUT" | HOOK_EVENT="preToolUse" HOOK_POLICY_MODE="enforce" scripts/hooks/pretool_denylist.sh || true)"

if [[ -z "${DENY_OUT// /}" ]]; then
  die "Expected deny JSON output, got empty output"
fi

if have jq; then
  echo "$DENY_OUT" | jq -e '.permissionDecision=="deny"' >/dev/null || die "Deny output is not a valid deny decision"
else
  echo "$DENY_OUT" | grep -q '"permissionDecision":"deny"' || die "Deny output did not contain deny decision"
fi

say "  ✓ deny decision emitted"
say "  output: $DENY_OUT"
say

# 4) postToolUse audit append fixture
say "[4/5] Run audit_log.sh postToolUse fixture"
[[ -x "scripts/hooks/audit_log.sh" ]] || die "scripts/hooks/audit_log.sh missing or not executable"

POST_INPUT='{"toolName":"bash","toolArgs":"{\"command\":\"echo hello\"}","toolResult":"hello"}'
printf '%s' "$POST_INPUT" | HOOK_EVENT="postToolUse" scripts/hooks/audit_log.sh >/dev/null

# Confirm log line exists
LINES="$(wc -l <"$TMP_AUDIT_LOG" 2>/dev/null || echo 0)"
[[ "$LINES" -ge 2 ]] || die "Expected audit log to have >=2 lines, got $LINES"

say "  ✓ audit_log appended event (lines=$LINES)"
say

# 5) sessionEnd summary
say "[5/5] Run session_end.sh and verify summary"
[[ -x "scripts/hooks/session_end.sh" ]] || die "scripts/hooks/session_end.sh missing or not executable"

echo '{}' | HOOK_EVENT="sessionEnd" scripts/hooks/session_end.sh >/dev/null

SUMMARY_JSON="${TMP_AUDIT_DIR}/session-summary.json"
[[ -f "$SUMMARY_JSON" ]] || die "Expected summary at $SUMMARY_JSON"

if have jq; then
  jq -e '.event=="sessionEnd" and .audit.totalEvents>=1' "$SUMMARY_JSON" >/dev/null \
    || die "Summary JSON missing expected fields"
  say "  ✓ session summary valid (jq)"
else
  grep -q '"event": "sessionEnd"' "$SUMMARY_JSON" || die "Summary JSON did not include sessionEnd"
  say "  ✓ session summary created (no jq)"
fi

say
say "== SUCCESS =="
say "Audit log sample (last 3 lines):"
tail -n 3 "$TMP_AUDIT_LOG" || true

