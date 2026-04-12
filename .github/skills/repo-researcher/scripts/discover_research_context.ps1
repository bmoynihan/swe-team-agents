Param()

# Purpose: Windows/PowerShell version of discover_research_context.sh (best effort)
# Usage:
#   pwsh .github/skills/repo-researcher/scripts/discover_research_context.ps1

$ErrorActionPreference = "Stop"

function Try-Command($cmd) {
  try { Invoke-Expression $cmd } catch { Write-Host "(ignored) $cmd" }
}

$root = (Try-Command "git rev-parse --show-toplevel") | Select-Object -First 1
if (-not $root) { $root = (Get-Location).Path }
Set-Location $root

Write-Host "== Repo Research Context =="
Write-Host "root: $root"
Try-Command "git rev-parse --abbrev-ref HEAD"
Write-Host ""

Write-Host "== Top-level layout =="
Get-ChildItem -Force | Select-Object -First 120 | Format-Table -AutoSize
Write-Host ""

Write-Host "== Likely tech stack signals =="
$signals = @(
  @{ File="package.json"; Label="Node.js" },
  @{ File="pnpm-lock.yaml"; Label="pnpm" },
  @{ File="yarn.lock"; Label="yarn" },
  @{ File="requirements.txt"; Label="Python requirements" },
  @{ File="pyproject.toml"; Label="Python (PEP 517/518)" },
  @{ File="poetry.lock"; Label="Poetry" },
  @{ File="Cargo.toml"; Label="Rust" },
  @{ File="go.mod"; Label="Go" },
  @{ File="pom.xml"; Label="Maven" },
  @{ File="build.gradle"; Label="Gradle" },
  @{ File="Gemfile"; Label="Ruby" },
  @{ File="composer.json"; Label="PHP" },
  @{ File="Makefile"; Label="Make" }
)
foreach ($s in $signals) {
  if (Test-Path $s.File) { Write-Host ("- {0} ({1})" -f $s.Label, $s.File) }
}
Write-Host ""

Write-Host "== Test command hints =="
if (Test-Path "package.json") {
  Write-Host "-- package.json scripts (filtered) --"
  Try-Command "node -e ""const p=require('./package.json'); const s=p.scripts||{}; for (const k of Object.keys(s)) { if (/test|lint|check|ci/i.test(k)) console.log(`${k}: ${s[k]}`); }"""
  Write-Host ""
}
if (Test-Path "pyproject.toml") {
  Write-Host "-- pyproject.toml (first 80 lines) --"
  Get-Content pyproject.toml -TotalCount 80
  Write-Host ""
}

Write-Host "Done."


