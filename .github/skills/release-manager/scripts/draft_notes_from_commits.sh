#!/usr/bin/env bash
set -euo pipefail

# Draft a categorized release note outline from git commit subjects.
# This is intentionally conservative: it does NOT claim breaking changes.
#
# Usage:
#   bash .github/skills/release-manager/scripts/draft_notes_from_commits.sh [<from_ref>] [<to_ref>]
# Examples:
#   bash .../draft_notes_from_commits.sh v1.2.3 HEAD
#   bash .../draft_notes_from_commits.sh <sha> <sha>
#
# Output: Markdown snippet you can paste into docs/agents/release-report.md

from_ref="${1:-}"
to_ref="${2:-HEAD}"

if [[ -z "${from_ref}" ]]; then
  from_ref="$(git describe --tags --abbrev=0 2>/dev/null || true)"
fi

if [[ -z "${from_ref}" ]]; then
  echo "No from_ref provided and no tags found. Provide an explicit range."
  exit 1
fi

range="${from_ref}..${to_ref}"

tmp="$(mktemp)"
git --no-pager log --format='%s' "$range" > "$tmp"

echo "## Draft release notes (from commit subjects: $range)"
echo
echo "### Highlights"
echo "- <fill: 1–3 user-facing bullets>"
echo
echo "### Features"
grep -Ei '^(feat|feature)(\(.+\))?: ' "$tmp" | sed 's/^/- /' || true
echo
echo "### Fixes"
grep -Ei '^fix(\(.+\))?: ' "$tmp" | sed 's/^/- /' || true
echo
echo "### Docs"
grep -Ei '^docs(\(.+\))?: ' "$tmp" | sed 's/^/- /' || true
echo
echo "### Chore / Maintenance"
grep -Ei '^(chore|refactor|perf|build|ci|test)(\(.+\))?: ' "$tmp" | sed 's/^/- /' || true
echo
echo "> NOTE: This outline is heuristic. Validate against Task Spec + diffs before publishing."
rm -f "$tmp"


