#!/usr/bin/env bash
set -euo pipefail

ROOT="docs/agents"
PROTOCOL_TEMPLATES=".github/skills/swe-team-protocol/templates"
IMPLEMENTER_TEMPLATES=".github/skills/implementer/templates"
TEST_TEMPLATES=".github/skills/test-engineer/templates"
RELEASE_TEMPLATES=".github/skills/release-manager/templates"
CURRENT_RUN_FILE="$ROOT/current-run.json"

mkdir -p "$ROOT"

install_if_missing() {
  local src="$1"
  local dst="$2"
  if [[ ! -f "$dst" ]]; then
    cp "$src" "$dst"
  fi
}

install_if_missing "$PROTOCOL_TEMPLATES/state.json.template.json" "$ROOT/state.json"
install_if_missing "$PROTOCOL_TEMPLATES/task-spec.template.md" "$ROOT/task-spec.md"
install_if_missing "$IMPLEMENTER_TEMPLATES/patch-report.template.md" "$ROOT/patch-report.md"
install_if_missing "$TEST_TEMPLATES/test-report.template.md" "$ROOT/test-report.md"
install_if_missing "$PROTOCOL_TEMPLATES/review-report.template.md" "$ROOT/review-report.md"
install_if_missing "$RELEASE_TEMPLATES/release-report.template.md" "$ROOT/release-report.md"
install_if_missing "$PROTOCOL_TEMPLATES/protocol.template.md" "$ROOT/protocol.md"

if [[ -f "$CURRENT_RUN_FILE" ]]; then
  RUN_ROOT="$(node -e "const fs=require('fs');const p=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));process.stdout.write(p.currentRunPath||'');" "$CURRENT_RUN_FILE")"
  if [[ -n "$RUN_ROOT" ]]; then
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
  fi
fi

echo "Bootstrapped task artifacts under $ROOT"
