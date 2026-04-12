#!/usr/bin/env pwsh
#requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Say($msg) { Write-Host $msg }
function Die($msg) { Write-Error "ERROR: $msg"; exit 1 }

function Cmd-Present([string]$name) {
  try { return [bool](Get-Command $name -ErrorAction Stop) } catch { return $false }
}

# Repo root = two levels up from scripts/hooks/
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

# Temp audit dir so we don't pollute committed artifacts
$tmpBase = [System.IO.Path]::GetTempPath()
$tmpAuditDir = Join-Path $tmpBase ("copilot-hooks-audit-" + [System.Guid]::NewGuid().ToString("n"))
$tmpAuditLog = Join-Path $tmpAuditDir "tool-audit.jsonl"

try { New-Item -ItemType Directory -Path $tmpAuditDir -Force | Out-Null } catch { Die "Failed to create temp dir" }

$env:HOOK_AUDIT_DIR = $tmpAuditDir
$env:HOOK_AUDIT_LOG = $tmpAuditLog

Say "== Copilot Hooks Smoke Test (PowerShell) =="
Say "Repo root: $root"
Say "Audit dir: $tmpAuditDir"
Say ""

# [1/5] Validate hooks.json
$hooksJson = ".github/hooks/hooks.json"
if (-not (Test-Path -LiteralPath $hooksJson)) { Die "Missing $hooksJson" }

Say "[1/5] Validate $hooksJson"
if (Cmd-Present "jq") {
  $jq = (Get-Command jq).Source
  & $jq "." $hooksJson | Out-Null
  Say "  ✓ JSON valid (jq)"
} else {
  try {
    $null = Get-Content -LiteralPath $hooksJson -Raw | ConvertFrom-Json -ErrorAction Stop
    Say "  ✓ JSON valid (ConvertFrom-Json)"
  } catch {
    Die "hooks.json is not valid JSON"
  }
}
Say ""

# [2/5] sessionStart
Say "[2/5] Run session_start.ps1"
$sessionStart = "scripts/hooks/session_start.ps1"
if (-not (Test-Path -LiteralPath $sessionStart)) { Die "Missing $sessionStart" }

$env:HOOK_EVENT = "sessionStart"
'{}' | & $sessionStart | Out-Null

if (-not (Test-Path -LiteralPath $tmpAuditLog)) { Die "Audit log not created by session_start" }
Say "  ✓ session_start wrote audit log"
Say ""

# [3/5] Deny fixture
Say "[3/5] Run pretool_denylist.ps1 deny fixture"
$pretool = "scripts/hooks/pretool_denylist.ps1"
if (-not (Test-Path -LiteralPath $pretool)) { Die "Missing $pretool" }

$env:HOOK_EVENT = "preToolUse"
$env:HOOK_POLICY_MODE = "enforce"

$denyInput = '{"toolName":"bash","toolArgs":"{\"command\":\"rm -rf /\"}"}'
$denyOut = ($denyInput | & $pretool)

if ([string]::IsNullOrWhiteSpace($denyOut)) { Die "Expected deny JSON output, got empty output" }

try {
  $denyObj = $denyOut | ConvertFrom-Json -ErrorAction Stop
  if ($denyObj.permissionDecision -ne "deny") { Die "Expected permissionDecision=deny" }
  Say "  ✓ deny decision emitted"
  Say "  output: $denyOut"
} catch {
  Die "Deny output not valid JSON: $denyOut"
}
Say ""

# [4/5] postToolUse audit append fixture
Say "[4/5] Run audit_log.ps1 postToolUse fixture"
$audit = "scripts/hooks/audit_log.ps1"
if (-not (Test-Path -LiteralPath $audit)) { Die "Missing $audit" }

$env:HOOK_EVENT = "postToolUse"

$postInput = '{"toolName":"bash","toolArgs":"{\"command\":\"echo hello\"}","toolResult":"hello"}'
$postInput | & $audit | Out-Null

# Confirm audit log has lines
$lines = 0
try { $lines = (Get-Content -LiteralPath $tmpAuditLog -ErrorAction Stop).Count } catch { Die "Could not read audit log" }
if ($lines -lt 2) { Die "Expected audit log to have >=2 lines, got $lines" }

Say "  ✓ audit_log appended event (lines=$lines)"
Say ""

# [5/5] sessionEnd summary
Say "[5/5] Run session_end.ps1 and verify summary"
$sessionEnd = "scripts/hooks/session_end.ps1"
if (-not (Test-Path -LiteralPath $sessionEnd)) { Die "Missing $sessionEnd" }

$env:HOOK_EVENT = "sessionEnd"
'{}' | & $sessionEnd | Out-Null

$summaryPath = Join-Path $tmpAuditDir "session-summary.json"
if (-not (Test-Path -LiteralPath $summaryPath)) { Die "Expected summary at $summaryPath" }

try {
  $summaryObj = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json -ErrorAction Stop
  if ($summaryObj.event -ne "sessionEnd") { Die "Summary missing event=sessionEnd" }
  if ($summaryObj.audit.totalEvents -lt 1) { Die "Summary totalEvents < 1" }
  Say "  ✓ session summary valid"
} catch {
  Die "Summary JSON invalid"
}

Say ""
Say "== SUCCESS =="
Say "Audit log sample (last 3 lines):"
try {
  Get-Content -LiteralPath $tmpAuditLog -Tail 3 | ForEach-Object { Say $_ }
} catch {
  Say "(could not read tail)"
}

# Cleanup
try { Remove-Item -LiteralPath $tmpAuditDir -Recurse -Force -ErrorAction SilentlyContinue } catch {}
exit 0

