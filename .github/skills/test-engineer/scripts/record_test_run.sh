#!/usr/bin/env bash
set -euo pipefail

LABEL=""
OUTPUT=""
WORKDIR="."
TIMEOUT_SECS=""

usage() {
  cat <<'EOF'
Usage:
  record_test_run.sh --label NAME --output path/to/result.json [--workdir DIR] [--timeout SECONDS] -- <command> [args...]

Example:
  bash .github/skills/test-engineer/scripts/record_test_run.sh \
    --label fast-subset \
    --output .artifacts/test-runs/fast-subset.json \
    -- npm test -- tests/foo.test.ts
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label)
      LABEL="$2"; shift 2 ;;
    --output)
      OUTPUT="$2"; shift 2 ;;
    --workdir)
      WORKDIR="$2"; shift 2 ;;
    --timeout)
      TIMEOUT_SECS="$2"; shift 2 ;;
    --)
      shift
      break ;;
    -h|--help)
      usage
      exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2 ;;
  esac
done

if [[ -z "${LABEL}" || -z "${OUTPUT}" || $# -eq 0 ]]; then
  usage >&2
  exit 2
fi

mkdir -p "$(dirname "$OUTPUT")"

TMP_STDOUT="$(mktemp)"
TMP_STDERR="$(mktemp)"
TMP_EXIT="$(mktemp)"

START_EPOCH="$(date +%s)"

set +e
if [[ -n "$TIMEOUT_SECS" ]]; then
  (
    cd "$WORKDIR"
    timeout "$TIMEOUT_SECS" "$@" >"$TMP_STDOUT" 2>"$TMP_STDERR"
    echo $? >"$TMP_EXIT"
  )
else
  (
    cd "$WORKDIR"
    "$@" >"$TMP_STDOUT" 2>"$TMP_STDERR"
    echo $? >"$TMP_EXIT"
  )
fi
WRAPPER_EXIT=$?
set -e

END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

COMMAND_STR=""
for arg in "$@"; do
  if [[ -z "$COMMAND_STR" ]]; then
    COMMAND_STR="$arg"
  else
    COMMAND_STR="$COMMAND_STR $(printf '%q' "$arg")"
  fi
done

EXIT_CODE="$(cat "$TMP_EXIT" 2>/dev/null || echo "$WRAPPER_EXIT")"
RESULT="fail"
if [[ "$EXIT_CODE" == "0" ]]; then
  RESULT="pass"
fi

python3 - "$LABEL" "$OUTPUT" "$WORKDIR" "$DURATION" "$EXIT_CODE" "$RESULT" "$COMMAND_STR" "$TMP_STDOUT" "$TMP_STDERR" <<'PY'
import json, pathlib, sys

label, output, workdir, duration, exit_code, result, command_str, stdout_path, stderr_path = sys.argv[1:11]
stdout_text = pathlib.Path(stdout_path).read_text(errors="replace")
stderr_text = pathlib.Path(stderr_path).read_text(errors="replace")

payload = {
    "label": label,
    "command": command_str,
    "workdir": workdir,
    "duration_seconds": int(duration),
    "exit_code": int(exit_code),
    "result": result,
    "stdout_tail": stdout_text[-4000:],
    "stderr_tail": stderr_text[-4000:],
}
path = pathlib.Path(output)
path.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps(payload, indent=2))
PY

rm -f "$TMP_STDOUT" "$TMP_STDERR" "$TMP_EXIT"


