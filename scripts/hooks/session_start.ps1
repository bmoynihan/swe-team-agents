#!/usr/bin/env pwsh
#requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

<#
sessionStart hook (PowerShell):
- Create audit dir/log and write a compact readiness marker.
- Keep deterministic and fast; hooks run synchronously. ([docs.github.com](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-hooks?utm_source=chatgpt.com))
#>

$null = [Console]::In.ReadToEnd() # stdin may contain JSON; we don't rely on it here.

$HOOK_EVENT     = $env:HOOK_EVENT     ?? "sessionStart"
$HOOK_CURRENT_RUN_FILE = $env:HOOK_CURRENT_RUN_FILE ?? "docs/agents/current-run.json"

function Resolve-RunScopedPath {
  param([Parameter(Mandatory=$true)][string]$RawPath)
  if (-not $RawPath.Contains("<current-run>")) { return $RawPath }
  $runId = "current"
  if (Test-Path -LiteralPath $HOOK_CURRENT_RUN_FILE) {
    try {
      $payload = Get-Content -Raw -LiteralPath $HOOK_CURRENT_RUN_FILE | ConvertFrom-Json -ErrorAction Stop
      if ($payload.currentRunId) { $runId = [string]$payload.currentRunId }
    } catch {}
  }
  return $RawPath.Replace("<current-run>", $runId)
}

$HOOK_AUDIT_DIR = Resolve-RunScopedPath ($env:HOOK_AUDIT_DIR ?? "docs/agents/runs/<current-run>/hook-audit")
$HOOK_AUDIT_LOG = Resolve-RunScopedPath ($env:HOOK_AUDIT_LOG ?? "docs/agents/runs/<current-run>/hook-audit/tool-audit.jsonl")

function Ensure-DirAndFile {
  param(
    [Parameter(Mandatory=$true)][string]$Dir,
    [Parameter(Mandatory=$true)][string]$File
  )
  try { New-Item -ItemType Directory -Path $Dir -Force | Out-Null } catch {}
  try {
    if (-not (Test-Path -LiteralPath $File)) { New-Item -ItemType File -Path $File -Force | Out-Null }
  } catch {}
}

Ensure-DirAndFile -Dir $HOOK_AUDIT_DIR -File $HOOK_AUDIT_LOG

function Cmd-Present([string]$name) {
  try { return [bool](Get-Command $name -ErrorAction Stop) } catch { return $false }
}

# Lightweight readiness checks (do not fail hook).
$jqStatus     = if (Cmd-Present "jq") { "present" } else { "missing" }
$pythonStatus = if (Cmd-Present "python3" -or Cmd-Present "python") { "present" } else { "missing" }
$bashStatus   = if (Cmd-Present "bash") { "present" } else { "missing" }

$hooksDirStatus        = if (Test-Path -LiteralPath ".github/hooks") { "present" } else { "missing" }
$scriptsHooksDirStatus = if (Test-Path -LiteralPath "scripts/hooks") { "present" } else { "missing" }
$agentDocsDirStatus    = if (Test-Path -LiteralPath "docs/agents") { "present" } else { "missing" }
$copilotInstrStatus    = if (Test-Path -LiteralPath ".github/copilot-instructions.md") { "present" } else { "missing" }

$tsMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()

$evt = @{
  ts    = $tsMs
  event = $HOOK_EVENT
  readiness = @{
    jq     = $jqStatus
    python = $pythonStatus
    bash   = $bashStatus
    dirs = @{
      ".github/hooks" = $hooksDirStatus
      "scripts/hooks" = $scriptsHooksDirStatus
      "docs/agents"    = $agentDocsDirStatus
    }
    files = @{
      ".github/copilot-instructions.md" = $copilotInstrStatus
    }
  }
}

# Append to a session marker file and to the main audit log for correlation.
$sessionJsonl = Join-Path $HOOK_AUDIT_DIR "session.jsonl"

try {
  ($evt | ConvertTo-Json -Compress) | Add-Content -LiteralPath $sessionJsonl -Encoding UTF8
} catch {}
try {
  ($evt | ConvertTo-Json -Compress) | Add-Content -LiteralPath $HOOK_AUDIT_LOG -Encoding UTF8
} catch {}

# No stdout output needed.
exit 0




