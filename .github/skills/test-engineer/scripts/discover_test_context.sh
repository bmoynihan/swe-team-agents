#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

echo "== Test context discovery =="
echo "root: $ROOT"
echo

echo "-- Candidate task artifacts --"
for path in \
  "$ROOT/docs/agents/task-spec.md" \
  "$ROOT/docs/agents/patch-report.md" \
  "$ROOT/docs/agents/test-report.md"
do
  if [[ -f "$path" ]]; then
    printf "FOUND  %s\n" "$path"
  else
    printf "MISS   %s\n" "$path"
  fi
done
echo

echo "-- Likely package / build files --"
find "$ROOT" -maxdepth 3 \( \
  -name package.json -o \
  -name pnpm-lock.yaml -o \
  -name yarn.lock -o \
  -name pyproject.toml -o \
  -name requirements.txt -o \
  -name requirements-dev.txt -o \
  -name poetry.lock -o \
  -name Pipfile -o \
  -name Cargo.toml -o \
  -name go.mod -o \
  -name pom.xml -o \
  -name build.gradle -o \
  -name build.gradle.kts -o \
  -name "*.csproj" \
\) -print 2>/dev/null | sed 's#^\./##' | sort || true
echo

echo "-- Likely test framework markers --"
grep -RInE \
  'pytest|unittest|jest|vitest|mocha|ava|playwright|cypress|rspec|minitest|go test|cargo test|JUnit|xUnit|NUnit' \
  "$ROOT" \
  --include='package.json' \
  --include='pyproject.toml' \
  --include='requirements*.txt' \
  --include='Cargo.toml' \
  --include='go.mod' \
  --include='pom.xml' \
  --include='build.gradle*' \
  --include='*.csproj' 2>/dev/null | head -n 80 || true
echo

echo "-- Likely test directories/files --"
find "$ROOT" -maxdepth 4 \( \
  -type d \( -iname test -o -iname tests -o -iname __tests__ -o -iname spec -o -iname specs \) -o \
  -type f \( -iname '*test*' -o -iname '*spec*' \) \
\) -print 2>/dev/null | sed 's#^\./##' | sort | head -n 200 || true
echo

echo "-- Existing CI / setup helpers --"
find "$ROOT" -maxdepth 4 \( \
  -path '*/.github/workflows/*' -o \
  -path '*/.github/scripts/ci/*' -o \
  -path '*/scripts/ci/*' \
\) -print 2>/dev/null | sed 's#^\./##' | sort || true
echo

echo "-- Changed files (if git available) --"
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$ROOT" status --short || true
  echo
  git -C "$ROOT" diff --name-only HEAD 2>/dev/null || true
else
  echo "git metadata unavailable"
fi
echo

echo "-- Suggested next steps --"
echo "1. Open the task spec and extract AC1..ACn."
echo "2. Find nearest existing tests for changed modules."
echo "3. Choose the smallest deterministic layer that proves each AC."
echo "4. Record key commands with record_test_run.sh."


