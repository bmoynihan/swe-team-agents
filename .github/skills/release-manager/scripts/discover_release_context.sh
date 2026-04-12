#!/usr/bin/env bash
set -euo pipefail

# Discover release context (version + last tag + change summary) without external network calls.
# Safe to run inside Copilot Agent environments.
#
# Usage:
#   bash .github/skills/release-manager/scripts/discover_release_context.sh
#
# Optional env vars:
#   RANGE_FROM_TAG=1   # default: 1; if 0, don't compute commit range
#   SHOW_DIFFSTAT=0    # default: 0; if 1, show diffstat since last tag (can be noisy)

RANGE_FROM_TAG="${RANGE_FROM_TAG:-1}"
SHOW_DIFFSTAT="${SHOW_DIFFSTAT:-0}"

root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${root}" ]]; then
  echo "Not a git repository (git rev-parse failed)."
  exit 1
fi
cd "$root"

echo "== Repo =="
echo "root: $root"
echo "branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "<unknown>")"
echo "head:   $(git rev-parse HEAD 2>/dev/null || echo "<unknown>")"
echo

last_tag="$(git describe --tags --abbrev=0 2>/dev/null || true)"
if [[ -n "$last_tag" ]]; then
  echo "== Last tag =="
  echo "$last_tag"
else
  echo "== Last tag =="
  echo "<none found>"
fi
echo

detect_version_file() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  echo "$f"
  return 0
}

extract_version() {
  local f="$1"
  case "$f" in
    package.json)
      python - <<'PY' 2>/dev/null || true
import json
from pathlib import Path
p=Path("package.json")
try:
  print(json.loads(p.read_text(encoding="utf-8"))["version"])
except Exception:
  pass
PY
      ;;
    pyproject.toml)
      # naive parse (works for most PEP 621 projects)
      python - <<'PY' 2>/dev/null || true
import re
from pathlib import Path
t=Path("pyproject.toml").read_text(encoding="utf-8", errors="ignore")
m=re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']\s*$', t)
print(m.group(1) if m else "")
PY
      ;;
    Cargo.toml)
      python - <<'PY' 2>/dev/null || true
import re
from pathlib import Path
t=Path("Cargo.toml").read_text(encoding="utf-8", errors="ignore")
# first version under [package]
pkg = re.search(r'(?ms)^\[package\].*?^\s*version\s*=\s*["\']([^"\']+)["\']', t)
print(pkg.group(1) if pkg else "")
PY
      ;;
    VERSION|version.txt)
      head -n 1 "$f" 2>/dev/null | tr -d '[:space:]' || true
      ;;
    *)
      ;;
  esac
}

echo "== Detected version (best effort) =="
version_files=()
for candidate in package.json pyproject.toml Cargo.toml VERSION version.txt; do
  if detect_version_file "$candidate" >/dev/null; then
    version_files+=("$candidate")
  fi
done

if [[ ${#version_files[@]} -eq 0 ]]; then
  echo "<no standard version file found>"
else
  for vf in "${version_files[@]}"; do
    v="$(extract_version "$vf" | head -n 1 | tr -d '\r' || true)"
    if [[ -n "$v" ]]; then
      echo "$vf: $v"
    else
      echo "$vf: <found but could not parse>"
    fi
  done
fi
echo

if [[ "$RANGE_FROM_TAG" == "1" && -n "$last_tag" ]]; then
  range="${last_tag}..HEAD"
  echo "== Commits since $last_tag =="
  git --no-pager log --oneline --no-decorate "$range" 2>/dev/null || true
  echo
  if [[ "$SHOW_DIFFSTAT" == "1" ]]; then
    echo "== Diffstat since $last_tag =="
    git --no-pager diff --stat "$range" 2>/dev/null || true
    echo
  fi
else
  echo "== Recent commits =="
  git --no-pager log -n 20 --oneline --no-decorate 2>/dev/null || true
  echo
fi

# Optional: list merged PRs via gh if available and authenticated.
if command -v gh >/dev/null 2>&1; then
  echo "== GitHub PRs (best effort via gh) =="
  if gh auth status >/dev/null 2>&1; then
    # If we have a last tag, we can often use the compare view.
    # Not all repos use tags consistently, so keep this best-effort.
    gh pr list --state merged --limit 20 --json number,title,author,mergedAt 2>/dev/null \
      | python - <<'PY' 2>/dev/null || true
import json,sys
data=json.load(sys.stdin)
for pr in data:
  print(f"#{pr.get('number')}: {pr.get('title')} (@{(pr.get('author') or {}).get('login','?')}) {pr.get('mergedAt','')}")
PY
  else
    echo "<gh installed but not authenticated>"
  fi
  echo
fi


