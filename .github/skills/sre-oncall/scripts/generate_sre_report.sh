#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

OUT="docs/agents/sre-report.md"
mkdir -p "$(dirname "$OUT")"

cp ".github/skills/sre-oncall/templates/sre-report.template.md" "$OUT"

echo "Wrote $OUT"


