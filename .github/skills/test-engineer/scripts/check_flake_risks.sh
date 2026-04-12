#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

echo "== Static flake risk scan =="
echo "root: $ROOT"
echo

patterns=(
  'sleep\('
  'setTimeout\('
  'Date\.now\('
  'new Date\('
  'time\.Now\('
  'datetime\.now\('
  'Instant\.now\('
  'Math\.random\('
  'random\.random\('
  'rand\.'
  'http://'
  'https://'
  'requests\.get\('
  'fetch\('
  'axios\.'
  'curl '
  'wget '
)

for pattern in "${patterns[@]}"; do
  echo "-- pattern: $pattern"
  grep -RInE "$pattern" "$ROOT" \
    --include='*.js' \
    --include='*.jsx' \
    --include='*.ts' \
    --include='*.tsx' \
    --include='*.py' \
    --include='*.go' \
    --include='*.rs' \
    --include='*.java' \
    --include='*.kt' \
    --include='*.cs' \
    --include='*.rb' 2>/dev/null | head -n 40 || true
  echo
done

echo "Interpretation:"
echo "- Findings are leads, not automatic blockers."
echo "- Prioritize files in changed scope and tests touching acceptance criteria."
echo "- If a risky dependency is intentional, document the control (mock, fake, seed, frozen clock, isolated env)."


