#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Hook input arrives as JSON on stdin. We append a JSONL record.
# postToolUse output is ignored by Copilot; we only write to HOOK_AUDIT_LOG.

INPUT="$(cat || true)"

HOOK_EVENT="${HOOK_EVENT:-postToolUse}" # postToolUse | errorOccurred
HOOK_CURRENT_RUN_FILE="${HOOK_CURRENT_RUN_FILE:-docs/agents/current-run.json}"
PYTHON_BIN="$(command -v python3 || command -v python || true)"
NODE_BIN="$(command -v node || true)"

read_current_run_id() {
  local run_id=""

  if [[ -f "$HOOK_CURRENT_RUN_FILE" ]]; then
    if [[ -n "$NODE_BIN" ]]; then
      run_id="$("$NODE_BIN" -e 'const fs=require("fs"); try { const payload=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); if (payload && payload.currentRunId) process.stdout.write(String(payload.currentRunId)); } catch {}' "$HOOK_CURRENT_RUN_FILE" 2>/dev/null || true)"
    elif [[ -n "$PYTHON_BIN" ]]; then
      run_id="$("$PYTHON_BIN" -c 'import json, sys;
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        payload = json.load(fh)
    value = payload.get("currentRunId", "")
    if value:
        print(value, end="")
except Exception:
    pass' "$HOOK_CURRENT_RUN_FILE" 2>/dev/null || true)"
    elif command -v jq >/dev/null 2>&1; then
      run_id="$(jq -r '.currentRunId // empty' "$HOOK_CURRENT_RUN_FILE" 2>/dev/null || true)"
    fi
  fi

  if [[ -z "$run_id" ]]; then
    run_id="current"
  fi

  printf '%s' "$run_id"
}

resolve_run_scoped_path() {
  local raw_path="$1"
  if [[ "$raw_path" == *"<current-run>"* ]]; then
    local run_id
    run_id="$(read_current_run_id)"
    printf '%s' "${raw_path//<current-run>/$run_id}"
    return
  fi
  printf '%s' "$raw_path"
}

HOOK_AUDIT_DIR="$(resolve_run_scoped_path "${HOOK_AUDIT_DIR:-docs/agents/runs/<current-run>/hook-audit}")"
HOOK_AUDIT_LOG="$(resolve_run_scoped_path "${HOOK_AUDIT_LOG:-docs/agents/runs/<current-run>/hook-audit/tool-audit.jsonl}")"

mkdir -p "$HOOK_AUDIT_DIR" 2>/dev/null || true
touch "$HOOK_AUDIT_LOG" 2>/dev/null || true

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 | awk '{print $1}'
  else
    cat | wc -c | tr -d ' '
  fi
}

redact_preview() {
  local s="$1"
  s="${s//$'\n'/ }"
  s="${s//$'\r'/ }"
  s="$(printf '%s' "$s" | sed -E \
    -e 's/([Pp]assword|[Pp]asswd|[Pp]wd|[Tt]oken|[Ss]ecret|[Aa]pi[_-]?[Kk]ey|[Kk]ey)=([^[:space:]]+)/\1=[REDACTED]/g' \
    -e 's/(Authorization:)[^[:space:]]+/\1 [REDACTED]/g' \
    -e 's/(Bearer)[[:space:]]+[^[:space:]]+/\1 [REDACTED]/g')"
  if ((${#s} > 160)); then
    s="${s:0:160}…"
  fi
  printf '%s' "$s"
}

TOOL_NAME=""
TOOL_COMMAND=""
TOOL_STATUS="unknown"
ERROR_MESSAGE=""
RESULT_PREVIEW=""

if [[ -n "$PYTHON_BIN" && -n "${INPUT// /}" ]]; then
  eval "$(
    HOOK_INPUT="$INPUT" "$PYTHON_BIN" -c 'import json, os, shlex
raw = os.environ.get("HOOK_INPUT", "")
try:
    data = json.loads(raw) if raw.strip() else {}
except Exception:
    data = {}
tool = data.get("toolName") or data.get("tool") or ""
args = data.get("toolArgs") or data.get("args") or {}
if isinstance(args, str):
    try:
        args = json.loads(args)
    except Exception:
        args = {"raw": args}
cmd = args.get("command") if isinstance(args, dict) else ""
if not cmd and isinstance(args, dict):
    cmd = args.get("cmd") or ""
out = data.get("toolResult") or data.get("toolOutput") or data.get("output") or data.get("result") or ""
err = data.get("error") or data.get("errorMessage") or data.get("message") or ""
status = "unknown"
if err:
    status = "error"
elif out != "" or data.get("success") is True:
    status = "success"
def emit(name, value):
    print(f"{name}=" + shlex.quote("" if value is None else str(value)))
emit("TOOL_NAME", tool)
emit("TOOL_COMMAND", cmd)
emit("TOOL_STATUS", status)
emit("ERROR_MESSAGE", err)
emit("RESULT_PREVIEW", out)' 2>/dev/null || true
  )"
elif command -v jq >/dev/null 2>&1 && [[ -n "${INPUT// /}" ]]; then
  TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.toolName // .tool // ""' 2>/dev/null || echo "")"
  TOOL_COMMAND="$(printf '%s' "$INPUT" | jq -r '
    .toolArgs // .args // "" |
    (if type=="string" then (try (fromjson) catch {}) else . end) |
    (.command // .cmd // "")
  ' 2>/dev/null || echo "")"
  ERROR_MESSAGE="$(printf '%s' "$INPUT" | jq -r '.error // .errorMessage // .message // ""' 2>/dev/null || echo "")"
  RESULT_PREVIEW="$(printf '%s' "$INPUT" | jq -r '.toolResult // .toolOutput // .output // .result // ""' 2>/dev/null || echo "")"
  if [[ -n "$ERROR_MESSAGE" ]]; then
    TOOL_STATUS="error"
  elif [[ -n "$RESULT_PREVIEW" ]]; then
    TOOL_STATUS="success"
  fi
fi

cmd_preview="$(redact_preview "$TOOL_COMMAND")"
cmd_hash="$(printf '%s' "$TOOL_COMMAND" | sha256)"
res_preview="$(redact_preview "$RESULT_PREVIEW")"
err_preview="$(redact_preview "$ERROR_MESSAGE")"
ts_ms="$(date +%s%3N 2>/dev/null || printf '%s000' "$(date +%s 2>/dev/null || echo 0)")"

append_jsonl() {
  if [[ -n "$PYTHON_BIN" ]]; then
    HOOK_EVENT="$HOOK_EVENT" "$PYTHON_BIN" -c 'import json, os, sys
evt = {
    "ts": int(sys.argv[1]),
    "event": os.environ.get("HOOK_EVENT", "postToolUse"),
    "toolName": sys.argv[2],
    "status": sys.argv[3],
    "commandHash": sys.argv[4],
    "commandPreview": sys.argv[5],
    "resultPreview": sys.argv[6],
    "errorPreview": sys.argv[7],
}
sys.stdout.write(json.dumps(evt, separators=(",", ":")) + "\n")' \
      "$ts_ms" "${TOOL_NAME:-}" "${TOOL_STATUS:-unknown}" "$cmd_hash" "$cmd_preview" "$res_preview" "$err_preview" \
      >>"$HOOK_AUDIT_LOG" 2>/dev/null || true
  elif [[ -n "$NODE_BIN" ]]; then
    HOOK_EVENT="$HOOK_EVENT" "$NODE_BIN" -e 'const evt = {
      ts: Number(process.argv[1] || "0"),
      event: process.env.HOOK_EVENT || "postToolUse",
      toolName: process.argv[2] || "",
      status: process.argv[3] || "unknown",
      commandHash: process.argv[4] || "",
      commandPreview: process.argv[5] || "",
      resultPreview: process.argv[6] || "",
      errorPreview: process.argv[7] || ""
    };
    process.stdout.write(JSON.stringify(evt) + "\n");' \
      "$ts_ms" "${TOOL_NAME:-}" "${TOOL_STATUS:-unknown}" "$cmd_hash" "$cmd_preview" "$res_preview" "$err_preview" \
      >>"$HOOK_AUDIT_LOG" 2>/dev/null || true
  else
    printf '{"ts":%s,"event":"%s","toolName":"%s","status":"%s","commandHash":"%s","commandPreview":"%s","resultPreview":"%s","errorPreview":"%s"}\n' \
      "$ts_ms" "$HOOK_EVENT" "${TOOL_NAME:-}" "${TOOL_STATUS:-unknown}" "$cmd_hash" "$cmd_preview" "$res_preview" "$err_preview" \
      >>"$HOOK_AUDIT_LOG" 2>/dev/null || true
  fi
}

append_jsonl

exit 0
