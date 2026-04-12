$ErrorActionPreference="Stop"

Write-Host "== Repo Researcher skill smoke test =="

$required = @(
  ".github/skills/repo-researcher/SKILL.md",
  ".github/skills/repo-researcher/templates/research-report.template.md",
  ".github/skills/repo-researcher/templates/research-request.template.json",
  ".github/skills/repo-researcher/templates/research-report.schema.json",
  ".github/skills/repo-researcher/scripts/discover_research_context.ps1"
)

$missing = $false
foreach ($f in $required) {
  if (-not (Test-Path $f)) {
    Write-Host "MISSING: $f"
    $missing = $true
  } else {
    Write-Host "OK: $f"
  }
}

if ($missing) { throw "FAIL: missing required files" }

Write-Host "PASS"


