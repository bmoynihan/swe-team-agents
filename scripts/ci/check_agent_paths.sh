#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Fail fast if singular artifact path drift reappears.
# Keep the search scoped to active configuration/script/instruction paths.

echo "== check_agent_paths =="

if command -v rg >/dev/null 2>&1; then
  if rg -n --glob '.github/**' --glob 'scripts/**' --glob 'AGENTS.md' --glob '.github/copilot-instructions.md' --glob '!scripts/ci/check_agent_paths.sh' --glob '!scripts/ci/check_agent_paths.py' --glob '!.github/tests/agent-path-policy.test.ps1' --glob '!.github/instructions/agent-artifacts.instructions.md' 'docs/agent/' .; then
    echo "ERROR: found forbidden path token docs/agent/"
    exit 1
  fi
else
  if grep -RIn --include='*.md' --include='*.json' --include='*.yml' --include='*.yaml' --include='*.sh' --include='*.ps1' --include='*.py' --exclude='check_agent_paths.sh' --exclude='check_agent_paths.py' --exclude='agent-path-policy.test.ps1' --exclude='agent-artifacts.instructions.md' 'docs/agent/' .github scripts AGENTS.md; then
    echo "ERROR: found forbidden path token docs/agent/"
    exit 1
  fi
fi

echo "== check_agent_paths: PASS =="


