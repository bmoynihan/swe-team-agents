#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# sessionStart hook: initialize audit dir/log and write a session-start marker.
# Keep this script deterministic and fast. Hooks run synchronously.

INPUT="$(cat || true)" # stdin may contain JSON; we do not rely on it here.

HOOK_EVENT="${HOOK_EVENT:-sessionStart}"
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

ts_ms="$(date +%s%3N 2>/dev/null || printf '%s000' "$(date +%s 2>/dev/null || echo 0)")"

have_cmd() { command -v "$1" >/dev/null 2>&1; }

jq_status="missing"
python_status="missing"
bash_status="present"

if have_cmd jq; then jq_status="present"; fi
if [[ -n "$PYTHON_BIN" ]]; then python_status="present"; fi

hooks_dir_status="missing"
scripts_hooks_status="missing"
agent_docs_status="missing"

[[ -d ".github/hooks" ]] && hooks_dir_status="present"
[[ -d "scripts/hooks" ]] && scripts_hooks_status="present"
[[ -d "docs/agents" ]] && agent_docs_status="present"

copilot_instr_status="missing"
[[ -f ".github/copilot-instructions.md" ]] && copilot_instr_status="present"

append_jsonl() {
  local payload_json="$1"
  printf '%s\n' "$payload_json" >>"$HOOK_AUDIT_DIR/session.jsonl" 2>/dev/null || true
  printf '%s\n' "$payload_json" >>"$HOOK_AUDIT_LOG" 2>/dev/null || true
}

payload=""
if [[ -n "$PYTHON_BIN" ]]; then
  payload="$(
    TS_MS="$ts_ms" \
    HOOK_EVENT="$HOOK_EVENT" \
    JQ_STATUS="$jq_status" \
    PY_STATUS="$python_status" \
    BASH_STATUS="$bash_status" \
    HOOKS_DIR="$hooks_dir_status" \
    SCRIPTS_HOOKS="$scripts_hooks_status" \
    AGENT_DOCS="$agent_docs_status" \
    COPILOT_INSTR="$copilot_instr_status" \
    "$PYTHON_BIN" - <<'PY' 2>/dev/null || true
import json, os

evt = {
    "ts": int(os.environ.get("TS_MS", "0")),
    "event": os.environ.get("HOOK_EVENT", "sessionStart"),
    "readiness": {
        "jq": os.environ.get("JQ_STATUS", "missing"),
        "python": os.environ.get("PY_STATUS", "missing"),
        "bash": os.environ.get("BASH_STATUS", "present"),
        "dirs": {
            ".github/hooks": os.environ.get("HOOKS_DIR", "missing"),
            "scripts/hooks": os.environ.get("SCRIPTS_HOOKS", "missing"),
            "docs/agents": os.environ.get("AGENT_DOCS", "missing"),
        },
        "files": {
            ".github/copilot-instructions.md": os.environ.get("COPILOT_INSTR", "missing"),
        },
    },
}

print(json.dumps(evt, separators=(",", ":")), end="")
PY
  )"
elif [[ -n "$NODE_BIN" ]]; then
  payload="$(
    TS_MS="$ts_ms" \
    HOOK_EVENT="$HOOK_EVENT" \
    JQ_STATUS="$jq_status" \
    PY_STATUS="$python_status" \
    BASH_STATUS="$bash_status" \
    HOOKS_DIR="$hooks_dir_status" \
    SCRIPTS_HOOKS="$scripts_hooks_status" \
    AGENT_DOCS="$agent_docs_status" \
    COPILOT_INSTR="$copilot_instr_status" \
    "$NODE_BIN" - <<'NODE' 2>/dev/null || true
const evt = {
  ts: Number(process.env.TS_MS || "0"),
  event: process.env.HOOK_EVENT || "sessionStart",
  readiness: {
    jq: process.env.JQ_STATUS || "missing",
    python: process.env.PY_STATUS || "missing",
    bash: process.env.BASH_STATUS || "present",
    dirs: {
      ".github/hooks": process.env.HOOKS_DIR || "missing",
      "scripts/hooks": process.env.SCRIPTS_HOOKS || "missing",
      "docs/agents": process.env.AGENT_DOCS || "missing"
    },
    files: {
      ".github/copilot-instructions.md": process.env.COPILOT_INSTR || "missing"
    }
  }
};

process.stdout.write(JSON.stringify(evt));
NODE
  )"
else
  payload="$(printf '{"ts":%s,"event":"%s","readiness":{"jq":"%s","python":"%s","bash":"%s","dirs":{".github/hooks":"%s","scripts/hooks":"%s","docs/agents":"%s"},"files":{".github/copilot-instructions.md":"%s"}}}' \
    "$ts_ms" "$HOOK_EVENT" "$jq_status" "$python_status" "$bash_status" \
    "$hooks_dir_status" "$scripts_hooks_status" "$agent_docs_status" "$copilot_instr_status")"
fi

if [[ -n "$payload" ]]; then
  append_jsonl "$payload"
fi

exit 0
