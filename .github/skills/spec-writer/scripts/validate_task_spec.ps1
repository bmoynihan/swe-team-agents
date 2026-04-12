param(
  [string]$Path = "docs/agents/task-spec.md"
)

$required = @(
  "Summary",
  "Context",
  "Goals",
  "Non-goals",
  "Acceptance Criteria",
  "Validation Plan",
  "Risks & Mitigations",
  "Rollback Plan",
  "Open Questions",
  "Traceability Matrix"
)

if (-not (Test-Path $Path)) {
  Write-Error "File not found: $Path"
  exit 2
}

$content = Get-Content -Raw -Path $Path

$missing = @()
foreach ($h in $required) {
  if ($content -notmatch ("(?m)^##\s+" + [regex]::Escape($h) + "\s*$")) {
    $missing += $h
  }
}

if ($content -notmatch "\bAC1\b") {
  Write-Warning "Could not find 'AC1' in $Path (did you forget to fill Acceptance Criteria?)"
}

if ($missing.Count -gt 0) {
  Write-Error ("Missing headings: " + ($missing -join ", "))
  exit 1
}

Write-Host "OK: required headings present in $Path"


