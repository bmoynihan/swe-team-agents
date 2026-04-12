#!/usr/bin/env bash
set -euo pipefail

ROOT="docs/agents"
CURRENT_RUN_FILE="$ROOT/current-run.json"

if [[ ! -f "$CURRENT_RUN_FILE" ]]; then
  echo "No current-run.json found; nothing to sync."
  exit 0
fi

RUN_ROOT="$(node -e "const fs=require('fs');const p=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));process.stdout.write(p.currentRunPath||'');" "$CURRENT_RUN_FILE")"
if [[ -z "$RUN_ROOT" ]]; then
  echo "current-run.json does not contain currentRunPath"
  exit 1
fi

mkdir -p "$RUN_ROOT" "$RUN_ROOT/hook-audit"

for src in "$ROOT"/*; do
  [[ -f "$src" ]] || continue
  name="$(basename "$src")"
  case "$name" in
    current-run.json|CANONICAL_ARTIFACT_POLICY.md)
      continue
      ;;
  esac
  cp "$src" "$RUN_ROOT/$name"
done

echo "Synced mutable working set from $ROOT -> $RUN_ROOT"
