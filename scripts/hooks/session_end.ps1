#!/usr/bin/env pwsh
#requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

<#
sessionEnd hook (PowerShell):
- Append a sessionEnd marker to HOOK_AUDIT_LOG
- Generate a compact summary JSON at $HOOK_AUDIT_DIR/session-summary.json
- Keep deterministic and fast; avoid network.
#>

$null = [Console]::In.ReadToEnd() # stdin may contain JSON; not required here.

$HOOK_EVENT     = $env:HOOK_EVENT     ?? "sessionEnd"
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

function Try-ParseJsonLine {
  param([string]$Line)
  if ([string]::IsNullOrWhiteSpace($Line)) { return $null }
  try { return ($Line | ConvertFrom-Json -ErrorAction Stop) } catch { return $null }
}

Ensure-DirAndFile -Dir $HOOK_AUDIT_DIR -File $HOOK_AUDIT_LOG

$summaryPath = Join-Path $HOOK_AUDIT_DIR "session-summary.json"

# Summary counters
[int]$total = 0
[int]$denies = 0
[int]$errors = 0
$byEvent = @{}
$byTool  = @{}
[int64]$firstTs = 0
[int64]$lastTs = 0
$haveFirst = $false

try {
  Get-Content -LiteralPath $HOOK_AUDIT_LOG -ErrorAction Stop | ForEach-Object {
    $obj = Try-ParseJsonLine -Line $_
    if ($null -eq $obj) { return }

    $total++

    $evt = [string]($obj.event ?? "unknown")
    if (-not $byEvent.ContainsKey($evt)) { $byEvent[$evt] = 0 }
    $byEvent[$evt]++

    $tool = $obj.toolName
    if ($null -ne $tool -and -not [string]::IsNullOrWhiteSpace([string]$tool)) {
      $toolKey = [string]$tool
      if (-not $byTool.ContainsKey($toolKey)) { $byTool[$toolKey] = 0 }
      $byTool[$toolKey]++
    }

    if ([string]$obj.decision -eq "deny") { $denies++ }

    $status = [string]($obj.status ?? "")
    if ($status -eq "error" -or $evt -eq "errorOccurred") { $errors++ }

    $ts = $obj.ts
    if ($ts -is [long] -or $ts -is [int]) {
      $tsVal = [int64]$ts
      if (-not $haveFirst) {
        $firstTs = $tsVal
        $lastTs = $tsVal
        $haveFirst = $true
      } else {
        if ($tsVal -lt $firstTs) { $firstTs = $tsVal }
        if ($tsVal -gt $lastTs)  { $lastTs = $tsVal }
      }
    }
  }
} catch {
  # If audit log is missing/unreadable, still write an end marker and a minimal summary.
}

# Top tools (top 10)
$topTools = @()
try {
  $topTools = $byTool.GetEnumerator() |
    Sort-Object -Property Value -Descending |
    Select-Object -First 10 |
    ForEach-Object { @{ tool = $_.Key; count = $_.Value } }
} catch {}

$tsMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()

$summary = @{
  ts    = $tsMs
  event = "sessionEnd"
  audit = @{
    path        = $HOOK_AUDIT_LOG
    totalEvents = $total
    denies      = $denies
    errors      = $errors
    firstTs     = if ($haveFirst) { $firstTs } else { $null }
    lastTs      = if ($haveFirst) { $lastTs } else { $null }
    byEvent     = $byEvent
    topTools    = $topTools
  }
}

# Write summary file (pretty JSON for humans)
try {
  ($summary | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $summaryPath -Encoding UTF8
} catch {
  # don't fail hook
}

# Append a compact marker line to the main audit log for correlation
$marker = @{
  ts          = $tsMs
  event       = $HOOK_EVENT
  summaryPath = $summaryPath
  totalEvents = $total
  denies      = $denies
  errors      = $errors
}

try {
  ($marker | ConvertTo-Json -Compress) | Add-Content -LiteralPath $HOOK_AUDIT_LOG -Encoding UTF8
} catch {}

exit 0




