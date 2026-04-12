#!/usr/bin/env pwsh
#requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

<#
postToolUse / errorOccurred hook audit logger (PowerShell).
- Hook input arrives as JSON on stdin. We append JSONL to HOOK_AUDIT_LOG.
- Hook stdout output is ignored for postToolUse; do not emit decisions here.
Docs: ([docs.github.com](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/use-hooks?utm_source=chatgpt.com))
#>

$inputJson = [Console]::In.ReadToEnd()

$HOOK_EVENT     = $env:HOOK_EVENT     ?? "postToolUse"   # postToolUse | errorOccurred
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

function Try-ParseJson {
  param([string]$Json)
  if ([string]::IsNullOrWhiteSpace($Json)) { return $null }
  try { return ($Json | ConvertFrom-Json -ErrorAction Stop) } catch { return $null }
}

function Get-Sha256Hex {
  param([Parameter(Mandatory=$true)][string]$Text)
  try {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha.ComputeHash($bytes)
    ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""
  } catch {
    return "$($Text.Length)"
  }
}

function Redact-Preview {
  param([Parameter(Mandatory=$true)][string]$Text)
  $s = $Text -replace "(`r|`n)", " "
  $s = $s -replace "(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|key)=\S+", '$1=[REDACTED]'
  $s = $s -replace "(?i)\bAuthorization:\s*\S+", "Authorization: [REDACTED]"
  $s = $s -replace "(?i)\bBearer\s+\S+", "Bearer [REDACTED]"
  if ($s.Length -gt 160) { $s = $s.Substring(0,160) + "…" }
  return $s
}

Ensure-DirAndFile -Dir $HOOK_AUDIT_DIR -File $HOOK_AUDIT_LOG

$toolName = ""
$toolCommand = ""
$status = "unknown"
$errorMessage = ""
$resultPreview = ""

$root = Try-ParseJson -Json $inputJson
if ($null -ne $root) {
  $toolName = ($root.toolName ?? $root.tool ?? "")
  $toolArgsRaw = ($root.toolArgs ?? $root.args ?? $null)

  $toolArgsObj = $null
  if ($toolArgsRaw -is [string]) {
    $toolArgsObj = Try-ParseJson -Json $toolArgsRaw
    if ($null -eq $toolArgsObj) { $toolArgsObj = @{ raw = $toolArgsRaw } }
  } elseif ($null -ne $toolArgsRaw) {
    $toolArgsObj = $toolArgsRaw
  }

  if ($null -ne $toolArgsObj) {
    $toolCommand = ($toolArgsObj.command ?? $toolArgsObj.cmd ?? "")
  }

  # output/result keys vary; keep a small preview only
  $resultPreview = ($root.toolResult ?? $root.toolOutput ?? $root.output ?? $root.result ?? "")
  $errorMessage  = ($root.error ?? $root.errorMessage ?? $root.message ?? "")

  if (-not [string]::IsNullOrWhiteSpace($errorMessage)) {
    $status = "error"
  } elseif (-not [string]::IsNullOrWhiteSpace([string]$resultPreview) -or ($root.success -eq $true)) {
    $status = "success"
  }
}

$cmdPreview = Redact-Preview -Text ([string]$toolCommand)
$cmdHash    = Get-Sha256Hex -Text ([string]$toolCommand)

$resPreview = Redact-Preview -Text ([string]$resultPreview)
$errPreview = Redact-Preview -Text ([string]$errorMessage)

$tsMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()

$evt = @{
  ts = $tsMs
  event = $HOOK_EVENT
  toolName = [string]$toolName
  status = $status
  commandHash = $cmdHash
  commandPreview = $cmdPreview
  resultPreview = $resPreview
  errorPreview = $errPreview
}

try {
  ($evt | ConvertTo-Json -Compress) | Add-Content -LiteralPath $HOOK_AUDIT_LOG -Encoding UTF8
} catch {
  # Never fail the hook on logging issues.
}

# No stdout output needed (ignored by postToolUse anyway).
exit 0




