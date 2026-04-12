#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Copilot hooks pass JSON on stdin. For preToolUse we can deny by emitting a single-line JSON object.

INPUT="$(cat || true)"

HOOK_EVENT="${HOOK_EVENT:-preToolUse}"
HOOK_POLICY_MODE="${HOOK_POLICY_MODE:-enforce}" # enforce | audit
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
  if ((${#s} > 140)); then
    s="${s:0:140}…"
  fi
  printf '%s' "$s"
}

append_audit() {
  local decision="$1"
  local reason="$2"
  local tool="$3"
  local cmd="$4"
  local preview hash

  preview="$(redact_preview "$cmd")"
  hash="$(printf '%s' "$cmd" | sha256)"

  if [[ -n "$PYTHON_BIN" ]]; then
    HOOK_EVENT="$HOOK_EVENT" HOOK_POLICY_MODE="$HOOK_POLICY_MODE" "$PYTHON_BIN" -c 'import json, os, sys, time
evt = {
    "ts": int(time.time() * 1000),
    "event": os.environ.get("HOOK_EVENT", "preToolUse"),
    "decision": sys.argv[1],
    "reason": sys.argv[2],
    "toolName": sys.argv[3],
    "commandHash": sys.argv[4],
    "commandPreview": sys.argv[5],
    "policyMode": os.environ.get("HOOK_POLICY_MODE", "enforce"),
}
sys.stdout.write(json.dumps(evt, separators=(",", ":")) + "\n")' \
      "$decision" "$reason" "$tool" "$hash" "$preview" >>"$HOOK_AUDIT_LOG" 2>/dev/null || true
  elif [[ -n "$NODE_BIN" ]]; then
    HOOK_EVENT="$HOOK_EVENT" HOOK_POLICY_MODE="$HOOK_POLICY_MODE" "$NODE_BIN" -e 'const evt = {
      ts: Date.now(),
      event: process.env.HOOK_EVENT || "preToolUse",
      decision: process.argv[1] || "",
      reason: process.argv[2] || "",
      toolName: process.argv[3] || "",
      commandHash: process.argv[4] || "",
      commandPreview: process.argv[5] || "",
      policyMode: process.env.HOOK_POLICY_MODE || "enforce"
    };
    process.stdout.write(JSON.stringify(evt) + "\n");' \
      "$decision" "$reason" "$tool" "$hash" "$preview" >>"$HOOK_AUDIT_LOG" 2>/dev/null || true
  else
    printf '{"ts":%s,"event":"%s","decision":"%s","reason":"%s","toolName":"%s","commandHash":"%s","commandPreview":"%s","policyMode":"%s"}\n' \
      "$(date +%s000 2>/dev/null || echo 0)" \
      "$HOOK_EVENT" "$decision" "$reason" "$tool" "$hash" "$preview" "$HOOK_POLICY_MODE" \
      >>"$HOOK_AUDIT_LOG" 2>/dev/null || true
  fi
}

TOOL_NAME=""
TOOL_COMMAND=""

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
print("TOOL_NAME=" + shlex.quote("" if tool is None else str(tool)))
print("TOOL_COMMAND=" + shlex.quote("" if cmd is None else str(cmd)))' 2>/dev/null || true
  )"
elif command -v jq >/dev/null 2>&1 && [[ -n "${INPUT// /}" ]]; then
  TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.toolName // .tool // ""' 2>/dev/null || echo "")"
  TOOL_COMMAND="$(printf '%s' "$INPUT" | jq -r '
    .toolArgs // .args // "" |
    (if type=="string" then (try (fromjson) catch {}) else . end) |
    (.command // .cmd // "")
  ' 2>/dev/null || echo "")"
fi

if [[ "$TOOL_NAME" != "bash" || -z "${TOOL_COMMAND:-}" ]]; then
  exit 0
fi

cmd="${TOOL_COMMAND}"
cmd_lc="${cmd,,}" 2>/dev/null || cmd_lc="$cmd"

get_deny_reason() {
  local c="$1"

  if [[ "$c" =~ (^|[[:space:];|&])sudo[[:space:]]+rm[[:space:]]+-rf[[:space:]]+(/|~/?|(\.\./)+|\.[[:space:]]|\.git\b|\$PWD\b|\$\{PWD\}|\$\([[:space:]]*pwd[[:space:]]*\)|\*) ]]; then
    echo "Denied: destructive rm -rf target"
    return 0
  fi
  if [[ "$c" =~ (^|[[:space:];|&])rm[[:space:]]+-rf[[:space:]]+(/|~/?|(\.\./)+|\.[[:space:]]|\.git\b|\$PWD\b|\$\{PWD\}|\$\([[:space:]]*pwd[[:space:]]*\)|\*) ]]; then
    echo "Denied: destructive rm -rf target"
    return 0
  fi
  if [[ "$c" =~ \b(mkfs\.[a-z0-9]+|mkfs|fdisk|parted)\b ]]; then
    echo "Denied: disk formatting command"
    return 0
  fi

  if [[ "$c" =~ (^|[[:space:];|&])env([[:space:]]*$|[[:space:]]*[|>]) ]]; then
    echo "Denied: full environment dump"
    return 0
  fi
  if [[ "$c" =~ (^|[[:space:];|&])printenv([[:space:]]*$|[[:space:]]*[|>]) ]]; then
    echo "Denied: full environment dump"
    return 0
  fi

  if [[ "$c" =~ \bcat[[:space:]]+~\/\.ssh\/(id_rsa|id_ed25519|config)\b ]]; then
    echo "Denied: reading SSH private key material"
    return 0
  fi
  if [[ "$c" =~ \bcat[[:space:]]+~\/\.aws\/credentials\b ]]; then
    echo "Denied: reading AWS credentials file"
    return 0
  fi
  if [[ "$c" =~ \bcat[[:space:]]+~\/\.config\/gcloud\/application_default_credentials\.json\b ]]; then
    echo "Denied: reading cloud credentials file"
    return 0
  fi
  if [[ "$c" =~ \bcat[[:space:]]+(\.env(\.|$)|\.npmrc(\.|$)|\.pypirc(\.|$)) ]]; then
    echo "Denied: reading local secrets/config file"
    return 0
  fi
  if [[ "$c" =~ \bcat[[:space:]]+\/etc\/(shadow|sudoers)\b ]]; then
    echo "Denied: reading sensitive system file"
    return 0
  fi

  if [[ "$c" =~ \bcurl\b.*(--upload-file\b|-T[[:space:]]+[^[:space:]]+|--data-binary[[:space:]]+@|@[[:alnum:]_./-]+) ]]; then
    echo "Denied: potential file upload/exfil via curl"
    return 0
  fi
  if [[ "$c" =~ \bwget\b.*(--post-file\b|--body-file\b|--method=PUT) ]]; then
    echo "Denied: potential file upload/exfil via wget"
    return 0
  fi
  if [[ "$c" =~ \b(nc|ncat|netcat|socat)\b ]]; then
    echo "Denied: raw socket exfiltration tooling"
    return 0
  fi
  if [[ "$c" =~ \b(tar|zip)\b.*\b(curl|wget)\b ]]; then
    echo "Denied: archive + network transfer pattern"
    return 0
  fi

  return 1
}

deny_reason=""
if deny_reason="$(get_deny_reason "$cmd_lc" 2>/dev/null)"; then
  :
else
  deny_reason=""
fi

if [[ -n "$deny_reason" ]]; then
  append_audit "deny" "$deny_reason" "$TOOL_NAME" "$cmd"

  if [[ "$HOOK_POLICY_MODE" == "audit" ]]; then
    exit 0
  fi

  printf '{"permissionDecision":"deny","permissionDecisionReason":"%s"}\n' \
    "$(printf '%s' "$deny_reason" | tr -d '\n' | sed 's/"/'"'"'/g')"
  exit 0
fi

exit 0
