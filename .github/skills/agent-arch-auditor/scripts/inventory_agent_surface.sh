#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

count_files() {
  local path="$1"
  if [[ -d "$ROOT/$path" ]]; then
    find "$ROOT/$path" -type f | wc -l | tr -d ' '
  else
    echo 0
  fi
}

workflow_count=0
if [[ -f "$ROOT/.github/workflows/copilot-setup-steps.yml" ]]; then
  workflow_count=1
fi

artifact_count=0
if [[ -d "$ROOT/docs/agents" ]]; then
  artifact_count="$(find "$ROOT/docs/agents" -maxdepth 1 -type f | wc -l | tr -d ' ')"
fi

cat <<EOF
{
  "agentFiles": $(count_files ".github/agents"),
  "skillFiles": $(count_files ".github/skills"),
  "instructionFiles": $(count_files ".github/instructions"),
  "hookFiles": $(count_files ".github/hooks"),
  "workflowFiles": ${workflow_count},
  "artifactFiles": ${artifact_count}
}
EOF
