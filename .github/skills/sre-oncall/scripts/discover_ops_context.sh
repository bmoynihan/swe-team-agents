#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "== SRE Oncall: repository context =="

echo "\n-- Candidate runbook locations --"
for d in docs/runbooks docs/ops docs/oncall .github/docs/runbooks .github/docs/ops; do
  if [ -d "$d" ]; then
    echo "FOUND: $d"
  fi
done

echo "\n-- Agent artifacts present --"
for f in docs/agents/task-spec.md docs/agents/patch-report.md docs/agents/test-report.md docs/agents/observability-report.md; do
  if [ -f "$f" ]; then
    echo "FOUND: $f"
  else
    echo "MISSING: $f"
  fi
done

echo "\n-- Recent change hints (best-effort) --"
if [ -f docs/agents/patch-report.md ]; then
  echo "Patch report excerpt:" 
  sed -n '1,160p' docs/agents/patch-report.md || true
else
  echo "No patch report found."
fi

echo "\n-- Quick telemetry hints (best-effort grep) --"
# Heuristic-only: keep it fast and safe.
grep -RIn --exclude-dir=.git --exclude='*.lock' --exclude='*.min.*' \
  -e "prometheus" -e "otel" -e "opentelemetry" -e "metrics" -e "trace" -e "logging" \
  . 2>/dev/null | head -n 50 || true


