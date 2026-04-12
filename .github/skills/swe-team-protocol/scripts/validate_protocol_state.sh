#!/usr/bin/env bash
set -euo pipefail

ROOT="docs/agents"
CURRENT_RUN_FILE="$ROOT/current-run.json"

fail() { echo "ERROR: $1" >&2; exit 1; }

for required in state.json task-spec.md patch-report.md test-report.md review-report.md release-report.md protocol.md; do
  [[ -f "$ROOT/$required" ]] || fail "Missing $ROOT/$required"
done

node -e "const fs=require('fs');const obj=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));for(const key of ['schemaVersion','protocol','phase','task','decisions','delegations','failures','next_action']){if(!(key in obj)) throw new Error('Missing required key: '+key);}console.log('OK: state.json has required keys');" "$ROOT/state.json"

if [[ -f "$CURRENT_RUN_FILE" ]]; then
  node -e "const fs=require('fs');const p=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));if(!p.currentRunPath) throw new Error('currentRunPath missing');for(const f of ['state.json','task-spec.md','patch-report.md','test-report.md','review-report.md','release-report.md','protocol.md']){if(!fs.existsSync(p.currentRunPath + '/' + f)) throw new Error('Missing run-scoped artifact: ' + p.currentRunPath + '/' + f);}console.log('OK: current run snapshot exists');" "$CURRENT_RUN_FILE"
fi

echo "OK: task artifacts look sane under $ROOT"


