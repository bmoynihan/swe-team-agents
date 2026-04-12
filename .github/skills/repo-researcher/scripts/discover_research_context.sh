#!/usr/bin/env bash
set -euo pipefail

# Purpose: Provide a fast "research context" snapshot to help the Repo Researcher
# find entry points, test commands, configs, and likely hot paths.
#
# Usage:
#   bash .github/skills/repo-researcher/scripts/discover_research_context.sh
#
# This script is read-only: it does not modify files.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "== Repo Research Context =="
echo "root: $ROOT"
echo "git branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'n/a')"
echo

echo "== Top-level layout =="
ls -la | sed -n '1,120p'
echo

echo "== Likely tech stack signals =="
declare -a SIGNALS=(
  "package.json:Node.js"
  "pnpm-lock.yaml:pnpm"
  "yarn.lock:yarn"
  "requirements.txt:Python requirements"
  "pyproject.toml:Python (PEP 517/518)"
  "poetry.lock:Poetry"
  "Pipfile:Pipenv"
  "Cargo.toml:Rust"
  "go.mod:Go"
  "pom.xml:Maven"
  "build.gradle:Gradle"
  "Gemfile:Ruby"
  "composer.json:PHP"
  "Makefile:Make"
)
for entry in "${SIGNALS[@]}"; do
  file="${entry%%:*}"
  label="${entry#*:}"
  if [[ -f "$file" ]]; then
    echo "- $label ($file)"
  fi
done
echo

echo "== Test command hints =="
if [[ -f package.json ]]; then
  echo "-- package.json scripts (filtered) --"
  node -e 'const p=require("./package.json"); const s=p.scripts||{}; for (const k of Object.keys(s)) { if (/test|lint|check|ci/i.test(k)) console.log(`${k}: ${s[k]}`); }' 2>/dev/null || true
  echo
fi

if [[ -f pyproject.toml ]]; then
  echo "-- pyproject.toml tool hints (first 80 lines) --"
  sed -n '1,80p' pyproject.toml || true
  echo
fi

if [[ -f Makefile ]]; then
  echo "-- Makefile targets (first 120 lines) --"
  sed -n '1,120p' Makefile || true
  echo
fi

echo "== Common entry points (best effort) =="
rg -n --hidden --no-ignore-vcs -S \
  'main\(|if __name__ == "__main__"|app\.listen\(|createServer\(|FastAPI\(|Flask\(|Express\(|click\.command|typer\.Typer|cobra\.Command' \
  -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/build/**' \
  2>/dev/null | head -n 80 || true
echo

echo "== Nearest tests (sample) =="
rg -n --hidden --no-ignore-vcs -S \
  'describe\(|it\(|test\(|pytest|unittest|jest|vitest|mocha|go test|cargo test' \
  -g'**/*test*.*' -g'**/*spec*.*' \
  -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/build/**' \
  2>/dev/null | head -n 80 || true
echo

echo "== Config + flags (sample) =="
rg -n --hidden --no-ignore-vcs -S \
  'FEATURE_|FLAG_|ENABLE_|DISABLE_|ENV_|CONFIG_|settings\.|config\.|dotenv' \
  -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/build/**' \
  2>/dev/null | head -n 80 || true

echo
echo "Done. Tip: rerun with a focused search term, e.g.:"
echo "  rg -n -S '<error string or API path>'"


