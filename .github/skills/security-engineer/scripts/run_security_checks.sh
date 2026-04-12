#!/usr/bin/env bash
set -euo pipefail

# Lightweight, heuristic security evidence collector.
# - No network access required.
# - No new tools installed.
# - Produces JSON evidence you can paste/summarize into docs/agents/security-report.md

OUT_DIR="${OUT_DIR:-.github/skills/security-engineer/out}"
mkdir -p "$OUT_DIR"
OUT_JSON="${OUT_JSON:-$OUT_DIR/security-evidence.json}"

now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

note_not_run() {
  local name="$1"
  local why="$2"
  jq --arg n "$name" --arg w "$why" '.checks += [{"name":$n,"result":"not_run","evidence":$w}]' "$OUT_JSON" > "$OUT_JSON.tmp" && mv "$OUT_JSON.tmp" "$OUT_JSON"
}

add_check() {
  local name="$1"
  local result="$2"
  local evidence="$3"
  jq --arg n "$name" --arg r "$result" --arg e "$evidence" '.checks += [{"name":$n,"result":$r,"evidence":$e}]' "$OUT_JSON" > "$OUT_JSON.tmp" && mv "$OUT_JSON.tmp" "$OUT_JSON"
}

init_json() {
  cat > "$OUT_JSON" <<EOF
{
  "generatedAt": "$(now_iso)",
  "repo": "$(basename "$(pwd)")",
  "git": {"enabled": false, "baseRef": null, "headRef": null, "changedFiles": []},
  "checks": [],
  "notes": []
}
EOF
}

git_enabled=false
base_ref="${BASE_REF:-}"
head_ref="${HEAD_REF:-}"

detect_git() {
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git_enabled=true
    jq '.git.enabled = true' "$OUT_JSON" > "$OUT_JSON.tmp" && mv "$OUT_JSON.tmp" "$OUT_JSON"

    # pick a reasonable base ref
    if [[ -z "$base_ref" ]]; then
      if git show-ref --verify --quiet refs/remotes/origin/main; then base_ref="origin/main"
      elif git show-ref --verify --quiet refs/remotes/origin/master; then base_ref="origin/master"
      else base_ref="HEAD~1"
      fi
    fi
    if [[ -z "$head_ref" ]]; then head_ref="HEAD"; fi

    jq --arg b "$base_ref" --arg h "$head_ref" '.git.baseRef=$b | .git.headRef=$h' "$OUT_JSON" > "$OUT_JSON.tmp" && mv "$OUT_JSON.tmp" "$OUT_JSON"

    # changed files list (best-effort)
    changed="$(git diff --name-only "$base_ref" "$head_ref" 2>/dev/null || true)"
    if [[ -n "$changed" ]]; then
      jq --argjson files "$(printf '%s\n' "$changed" | jq -R -s -c 'split("\n")[:-1]')" '.git.changedFiles=$files' "$OUT_JSON" > "$OUT_JSON.tmp" && mv "$OUT_JSON.tmp" "$OUT_JSON"
    fi
  fi
}

# --- Check 1: Secrets hygiene (heuristic) ---
check_secrets() {
  local patterns=(
    "BEGIN (RSA|EC|OPENSSH) PRIVATE KEY"
    "AKIA[0-9A-Z]{16}"                 # AWS access key id pattern
    "AIza[0-9A-Za-z\-_]{35}"           # Google API key pattern
    "xox[baprs]-[0-9A-Za-z-]{10,48}"   # Slack token patterns
    "ghp_[0-9A-Za-z]{36}"              # GitHub classic PAT
    "github_pat_[0-9A-Za-z_]{82,}"     # GitHub fine-grained PAT
    "-----BEGIN PGP PRIVATE KEY BLOCK-----"
  )

  local files=()
  if [[ "$git_enabled" == true ]]; then
    mapfile -t files < <(jq -r '.git.changedFiles[]' "$OUT_JSON" 2>/dev/null || true)
  fi
  if [[ ${#files[@]} -eq 0 ]]; then
    # fallback: quick scan of tracked text files (limited)
    mapfile -t files < <(git ls-files 2>/dev/null | head -n 200 || true)
  fi

  local hits=()
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    # skip obvious binaries
    if file "$f" | grep -qiE 'image|archive|executable|binary|compressed'; then
      continue
    fi
    for p in "${patterns[@]}"; do
      if grep -nE -- "$p" "$f" >/dev/null 2>&1; then
        hits+=("$f: pattern=/$p/")
      fi
    done
  done

  if [[ ${#hits[@]} -gt 0 ]]; then
    add_check "secrets_hygiene" "fail" "Potential secret-like patterns found (review manually): $(printf '%s; ' "${hits[@]}")"
  else
    add_check "secrets_hygiene" "pass" "No secret-like patterns detected via heuristic grep."
  fi
}

# --- Check 2: GitHub Actions permissions & pinning (heuristic) ---
check_actions_security() {
  if [[ ! -d ".github/workflows" ]]; then
    add_check "actions_security" "not_applicable" "No .github/workflows directory found."
    return
  fi

  local workflow_files
  workflow_files="$(ls -1 .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null || true)"
  if [[ -z "$workflow_files" ]]; then
    add_check "actions_security" "not_applicable" "No workflow YAML files found."
    return
  fi

  local missing_permissions=0
  local uses_unpinned=0

  while IFS= read -r wf; do
    # basic heuristic: a workflow declaring `permissions:` somewhere is better than none.
    if ! grep -qE '^[[:space:]]*permissions[[:space:]]*:' "$wf"; then
      missing_permissions=$((missing_permissions+1))
    fi
    # action pinning heuristic: `uses: owner/repo@<40-hex-sha>` considered pinned
    while IFS= read -r line; do
      if [[ "$line" =~ uses:[[:space:]]*[^@]+@([^\ ]+) ]]; then
        ref="${BASH_REMATCH[1]}"
        if [[ ! "$ref" =~ ^[0-9a-fA-F]{40}$ ]]; then
          uses_unpinned=$((uses_unpinned+1))
        fi
      fi
    done < <(grep -nE '^[[:space:]]*uses:' "$wf" || true)
  done <<< "$workflow_files"

  local evidence="workflows_missing_permissions=$missing_permissions; actions_uses_not_pinned_to_sha=$uses_unpinned"
  if [[ "$missing_permissions" -gt 0 || "$uses_unpinned" -gt 0 ]]; then
    add_check "actions_security" "fail" "$evidence"
  else
    add_check "actions_security" "pass" "$evidence"
  fi
}

# --- Check 3: Dependency manifest delta (best-effort) ---
check_dependency_files() {
  local dep_files=(
    "package.json" "package-lock.json" "pnpm-lock.yaml" "yarn.lock"
    "requirements.txt" "requirements-dev.txt" "pyproject.toml" "poetry.lock" "Pipfile.lock"
    "Cargo.toml" "Cargo.lock" "go.mod" "go.sum"
    "pom.xml" "build.gradle" "build.gradle.kts"
  )

  local changed_deps=()
  if [[ "$git_enabled" == true ]]; then
    for f in "${dep_files[@]}"; do
      if git diff --name-only "$base_ref" "$head_ref" -- "$f" >/dev/null 2>&1; then
        if git diff --name-only "$base_ref" "$head_ref" -- "$f" | grep -q .; then
          changed_deps+=("$f")
        fi
      fi
    done
  fi

  if [[ ${#changed_deps[@]} -gt 0 ]]; then
    add_check "dependency_files_changed" "pass" "Dependency-related files changed: $(printf '%s ' "${changed_deps[@]}")"
  else
    add_check "dependency_files_changed" "pass" "No common dependency manifest/lockfile changes detected (heuristic)."
  fi
}

main() {
  command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required."; exit 1; }

  init_json
  detect_git

  check_secrets
  check_actions_security
  check_dependency_files

  echo "Wrote evidence to: $OUT_JSON"
}

main "$@"


