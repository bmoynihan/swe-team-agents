#!/usr/bin/env bash
set -euo pipefail

# Minimal smoke test for the Repo Researcher skill assets.
# Usage:
#   bash .github/skills/repo-researcher/scripts/research_smoke_test.sh

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "== Repo Researcher skill smoke test =="

required=(
  ".github/skills/repo-researcher/SKILL.md"
  ".github/skills/repo-researcher/templates/research-report.template.md"
  ".github/skills/repo-researcher/templates/research-request.template.json"
  ".github/skills/repo-researcher/templates/research-report.schema.json"
  ".github/skills/repo-researcher/scripts/discover_research_context.sh"
)

missing=0
for f in "${required[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING: $f"
    missing=1
  else
    echo "OK: $f"
  fi
done

if [[ $missing -ne 0 ]]; then
  echo "FAIL: missing required files"
  exit 1
fi

echo "PASS"


