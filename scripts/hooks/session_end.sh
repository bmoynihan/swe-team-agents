#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# sessionEnd hook: append a session-end marker and write a compact audit summary.
# Keep deterministic and fast; avoid network and avoid logging secrets.

INPUT="$(cat || true)" # stdin may contain JSON; not required here.

HOOK_EVENT="${HOOK_EVENT:-sessionEnd}"
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
SUMMARY_JSON="${HOOK_AUDIT_DIR}/session-summary.json"

mkdir -p "$HOOK_AUDIT_DIR" 2>/dev/null || true
touch "$HOOK_AUDIT_LOG" 2>/dev/null || true

ts_ms="$(date +%s%3N 2>/dev/null || printf '%s000' "$(date +%s 2>/dev/null || echo 0)")"

write_summary_python() {
  HOOK_AUDIT_LOG="$HOOK_AUDIT_LOG" SUMMARY_JSON="$SUMMARY_JSON" TS_MS="$ts_ms" "$PYTHON_BIN" - <<'PY'
import json
import os
from collections import Counter

audit_path = os.environ["HOOK_AUDIT_LOG"]
summary_path = os.environ["SUMMARY_JSON"]
ts = int(os.environ.get("TS_MS", "0"))

total = 0
by_event = Counter()
by_tool = Counter()
denies = 0
errors = 0
first_ts = None
last_ts = None

def safe_load(line: str):
    try:
        return json.loads(line)
    except Exception:
        return None

try:
    with open(audit_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = safe_load(line)
            if not isinstance(obj, dict):
                continue
            total += 1
            evt = str(obj.get("event") or "unknown")
            by_event[evt] += 1

            tool = obj.get("toolName")
            if tool:
                by_tool[str(tool)] += 1

            if obj.get("decision") == "deny":
                denies += 1

            status = obj.get("status")
            if status == "error" or evt == "errorOccurred":
                errors += 1

            tsv = obj.get("ts")
            if isinstance(tsv, int):
                if first_ts is None or tsv < first_ts:
                    first_ts = tsv
                if last_ts is None or tsv > last_ts:
                    last_ts = tsv
except FileNotFoundError:
    pass

summary = {
    "ts": ts,
    "event": "sessionEnd",
    "audit": {
        "path": audit_path,
        "totalEvents": total,
        "denies": denies,
        "errors": errors,
        "firstTs": first_ts,
        "lastTs": last_ts,
        "byEvent": dict(by_event),
        "topTools": [{"tool": name, "count": count} for name, count in by_tool.most_common(10)],
    },
}

os.makedirs(os.path.dirname(summary_path), exist_ok=True)
with open(summary_path, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2)
    fh.write("\n")

marker = {
    "ts": ts,
    "event": "sessionEnd",
    "summaryPath": summary_path,
    "totalEvents": total,
    "denies": denies,
    "errors": errors,
}
with open(audit_path, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(marker, separators=(",", ":")) + "\n")
PY
}

write_summary_node() {
  HOOK_AUDIT_LOG="$HOOK_AUDIT_LOG" SUMMARY_JSON="$SUMMARY_JSON" TS_MS="$ts_ms" "$NODE_BIN" - <<'NODE'
const fs = require("fs");
const path = require("path");

const auditPath = process.env.HOOK_AUDIT_LOG;
const summaryPath = process.env.SUMMARY_JSON;
const ts = Number(process.env.TS_MS || "0");

let total = 0;
let denies = 0;
let errors = 0;
let firstTs = null;
let lastTs = null;
const byEvent = {};
const byTool = {};

try {
  const lines = fs.readFileSync(auditPath, "utf8").split(/\r?\n/);
  for (const line of lines) {
    if (!line.trim()) continue;
    let obj;
    try {
      obj = JSON.parse(line);
    } catch {
      continue;
    }
    if (!obj || typeof obj !== "object") continue;
    total += 1;
    const evt = String(obj.event || "unknown");
    byEvent[evt] = (byEvent[evt] || 0) + 1;
    if (obj.toolName) {
      const tool = String(obj.toolName);
      byTool[tool] = (byTool[tool] || 0) + 1;
    }
    if (obj.decision === "deny") denies += 1;
    if (obj.status === "error" || evt === "errorOccurred") errors += 1;
    if (Number.isInteger(obj.ts)) {
      if (firstTs === null || obj.ts < firstTs) firstTs = obj.ts;
      if (lastTs === null || obj.ts > lastTs) lastTs = obj.ts;
    }
  }
} catch {}

const topTools = Object.entries(byTool)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 10)
  .map(([tool, count]) => ({ tool, count }));

const summary = {
  ts,
  event: "sessionEnd",
  audit: {
    path: auditPath,
    totalEvents: total,
    denies,
    errors,
    firstTs,
    lastTs,
    byEvent,
    topTools
  }
};

fs.mkdirSync(path.dirname(summaryPath), { recursive: true });
fs.writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`, "utf8");

const marker = {
  ts,
  event: "sessionEnd",
  summaryPath,
  totalEvents: total,
  denies,
  errors
};
fs.appendFileSync(auditPath, `${JSON.stringify(marker)}\n`, "utf8");
NODE
}

write_summary_fallback() {
  local total denies errors
  total="$(wc -l <"$HOOK_AUDIT_LOG" 2>/dev/null || echo 0)"
  denies="$(grep -c '"decision":"deny"' "$HOOK_AUDIT_LOG" 2>/dev/null || echo 0)"
  errors="$(grep -c '"status":"error"' "$HOOK_AUDIT_LOG" 2>/dev/null || echo 0)"

  cat >"$SUMMARY_JSON" <<EOF
{
  "ts": ${ts_ms},
  "event": "sessionEnd",
  "audit": {
    "path": "${HOOK_AUDIT_LOG}",
    "totalEvents": ${total},
    "denies": ${denies},
    "errors": ${errors},
    "note": "fallback summary"
  }
}
EOF

  printf '{"ts":%s,"event":"sessionEnd","summaryPath":"%s","totalEvents":%s,"denies":%s,"errors":%s}\n' \
    "$ts_ms" "$SUMMARY_JSON" "$total" "$denies" "$errors" >>"$HOOK_AUDIT_LOG" 2>/dev/null || true
}

if [[ -n "$PYTHON_BIN" ]]; then
  if ! write_summary_python >/dev/null 2>&1; then
    if [[ -n "$NODE_BIN" ]]; then
      write_summary_node >/dev/null 2>&1 || write_summary_fallback >/dev/null 2>&1 || true
    else
      write_summary_fallback >/dev/null 2>&1 || true
    fi
  fi
elif [[ -n "$NODE_BIN" ]]; then
  write_summary_node >/dev/null 2>&1 || write_summary_fallback >/dev/null 2>&1 || true
else
  write_summary_fallback >/dev/null 2>&1 || true
fi

exit 0
