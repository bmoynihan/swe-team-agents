Param(
  [string]$OutDir = ".github/skills/security-engineer/out",
  [string]$OutJson = ".github/skills/security-engineer/out/security-evidence.json"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$now = (Get-Date).ToUniversalTime().ToString("o")
$repo = Split-Path -Leaf (Get-Location)

$evidence = [ordered]@{
  generatedAt = $now
  repo        = $repo
  checks      = @()
  notes       = @()
}

function Add-Check([string]$Name, [string]$Result, [string]$Evidence) {
  $evidence.checks += [ordered]@{ name=$Name; result=$Result; evidence=$Evidence }
}

# Secrets heuristic scan (limited to a small file set)
$patterns = @(
  "BEGIN (RSA|EC|OPENSSH) PRIVATE KEY",
  "AKIA[0-9A-Z]{16}",
  "ghp_[0-9A-Za-z]{36}",
  "github_pat_[0-9A-Za-z_]{82,}"
)

$files = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Length -lt 500000 } |
  Select-Object -First 200

$hits = @()
foreach ($f in $files) {
  foreach ($p in $patterns) {
    if (Select-String -Path $f.FullName -Pattern $p -Quiet) {
      $hits += "$($f.FullName): /$p/"
    }
  }
}

if ($hits.Count -gt 0) {
  Add-Check "secrets_hygiene" "fail" ("Potential secret-like patterns found (review manually): " + ($hits -join "; "))
} else {
  Add-Check "secrets_hygiene" "pass" "No secret-like patterns detected via heuristic scan."
}

$evidence | ConvertTo-Json -Depth 6 | Out-File -FilePath $OutJson -Encoding utf8
Write-Host "Wrote evidence to: $OutJson"


