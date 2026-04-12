#!/usr/bin/env pwsh
#requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

<#
preToolUse hook policy enforcer (PowerShell).
- Input JSON includes toolName and toolArgs (toolArgs is a JSON string) per GitHub hook docs. 
- To deny, output a single-line JSON object with permissionDecision=deny. 
- Keep logs minimal and redact sensitive data. 
#>

$inputJson = [Console]::In.ReadToEnd()

$HOOK_EVENT = $env:HOOK_EVENT      ?? "preToolUse"
$HOOK_POLICY_MODE = $env:HOOK_POLICY_MODE ?? "enforce"  # enforce | audit
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

# --- helpers ---------------------------------------------------------------

function Ensure-DirAndFile {
  param(
    [Parameter(Mandatory = $true)][string]$Dir,
    [Parameter(Mandatory = $true)][string]$File
  )
  try { New-Item -ItemType Directory -Path $Dir -Force | Out-Null } catch {}
  try {
    if (-not (Test-Path -LiteralPath $File)) { New-Item -ItemType File -Path $File -Force | Out-Null }
  }
  catch {}
}

function Get-Sha256Hex {
  param([Parameter(Mandatory = $true)][string]$Text)
  try {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha.ComputeHash($bytes)
    ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""
  }
  catch {
    # fallback: length only (avoid failing hook)
    return "$($Text.Length)"
  }
}

function Redact-Preview {
  param([Parameter(Mandatory = $true)][string]$Text)

  $s = $Text -replace "(`r|`n)", " "
  # redact common key=value patterns
  $s = $s -replace "(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|key)=\S+", '$1=[REDACTED]'
  # redact Authorization headers / Bearer tokens
  $s = $s -replace "(?i)\bAuthorization:\s*\S+", "Authorization: [REDACTED]"
  $s = $s -replace "(?i)\bBearer\s+\S+", "Bearer [REDACTED]"

  if ($s.Length -gt 160) { $s = $s.Substring(0, 160) + "…" }
  return $s
}

function Append-AuditJsonl {
  param(
    [Parameter(Mandatory = $true)][string]$Decision,
    [Parameter(Mandatory = $true)][string]$Reason,
    [Parameter(Mandatory = $true)][string]$ToolName,
    [Parameter(Mandatory = $true)][string]$Command
  )

  $preview = Redact-Preview -Text $Command
  $hash = Get-Sha256Hex -Text $Command
  $tsMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()

  $evt = @{
    ts             = $tsMs
    event          = $HOOK_EVENT
    decision       = $Decision
    reason         = $Reason
    toolName       = $ToolName
    commandHash    = $hash
    commandPreview = $preview
    policyMode     = $HOOK_POLICY_MODE
  }

  try {
    ($evt | ConvertTo-Json -Compress) | Add-Content -LiteralPath $HOOK_AUDIT_LOG -Encoding UTF8
  }
  catch {
    # do not fail hook if logging fails
  }
}

function Try-ParseJson {
  param([string]$Json)
  if ([string]::IsNullOrWhiteSpace($Json)) { return $null }
  try { return ($Json | ConvertFrom-Json -ErrorAction Stop) } catch { return $null }
}

# --- init ------------------------------------------------------------------

Ensure-DirAndFile -Dir $HOOK_AUDIT_DIR -File $HOOK_AUDIT_LOG

$toolName = ""
$toolCommand = ""

$root = Try-ParseJson -Json $inputJson
if ($null -ne $root) {
  $toolName = ($root.toolName ?? $root.tool ?? "")
  $toolArgsRaw = ($root.toolArgs ?? $root.args ?? $null)

  $toolArgsObj = $null
  if ($toolArgsRaw -is [string]) {
    $toolArgsObj = Try-ParseJson -Json $toolArgsRaw
    if ($null -eq $toolArgsObj) {
      # fallback: treat as raw string
      $toolArgsObj = @{ raw = $toolArgsRaw }
    }
  }
  elseif ($null -ne $toolArgsRaw) {
    $toolArgsObj = $toolArgsRaw
  }

  if ($null -ne $toolArgsObj) {
    $toolCommand = ($toolArgsObj.command ?? $toolArgsObj.cmd ?? "")
  }
}

# Only enforce deny policy for bash commands (same as bash version).
if ($toolName -ne "bash" -or [string]::IsNullOrWhiteSpace($toolCommand)) {
  exit 0
}

$cmd = $toolCommand
$cmdLc = $cmd.ToLowerInvariant()

function Get-DenyReason {
  param([Parameter(Mandatory = $true)][string]$C)

  # 1) Obvious destructive rm -rf on dangerous targets
  if ($C -match "(^|[\s;&|])rm\s+-rf\s+(/|~/?|(\.\./)+|\.($|\s)|\.git\b|\$pwd\b|\$\{pwd\}|\$\(\s*pwd\s*\)|\*)") {
    return "Denied: destructive rm -rf target"
  }
  if ($C -match "(^|[\s;&|])sudo\s+rm\s+-rf\s+(/|~/?|(\.\./)+|\.($|\s)|\.git\b|\$pwd\b|\$\{pwd\}|\$\(\s*pwd\s*\)|\*)") {
    return "Denied: destructive rm -rf target"
  }
  if ($C -match "\b(mkfs(\.[a-z0-9]+)?|fdisk|parted)\b") {
    return "Denied: disk formatting command"
  }

  # 2) Full environment dumps (block only "dump all", not printenv VAR)
  if ($C -match "(^|[\s;&|])env(\s*$|\s*[|>])") {
    return "Denied: full environment dump"
  }
  if ($C -match "(^|[\s;&|])printenv(\s*$|\s*[|>])") {
    return "Denied: full environment dump"
  }

  # 3) Credential harvesting
  if ($C -match "\bcat\s+~\/\.ssh\/(id_rsa|id_ed25519|config)\b") {
    return "Denied: reading SSH private key material"
  }
  if ($C -match "\bcat\s+~\/\.aws\/credentials\b") {
    return "Denied: reading AWS credentials file"
  }
  if ($C -match "\bcat\s+~\/\.config\/gcloud\/application_default_credentials\.json\b") {
    return "Denied: reading cloud credentials file"
  }
  if ($C -match "\bcat\s+(\.env(\.|$)|\.npmrc(\.|$)|\.pypirc(\.|$))") {
    return "Denied: reading local secrets/config file"
  }
  if ($C -match "\bcat\s+\/etc\/(shadow|sudoers)\b") {
    return "Denied: reading sensitive system file"
  }

  # 4) Obvious exfil patterns
  if ($C -match "\bcurl\b.*(--upload-file\b|-t\s+\S+|--data-binary\s+@|@\S+)") {
    return "Denied: potential file upload/exfil via curl"
  }
  if ($C -match "\bwget\b.*(--post-file\b|--body-file\b|--method=put)") {
    return "Denied: potential file upload/exfil via wget"
  }
  if ($C -match "\b(nc|ncat|netcat|socat)\b") {
    return "Denied: raw socket exfiltration tooling"
  }
  if ($C -match "\b(tar|zip)\b.*\b(curl|wget)\b") {
    return "Denied: archive + network transfer pattern"
  }

  return $null
}

$denyReason = Get-DenyReason -C $cmdLc

if ($null -ne $denyReason) {
  Append-AuditJsonl -Decision "deny" -Reason $denyReason -ToolName $toolName -Command $cmd

  if ($HOOK_POLICY_MODE -eq "audit") {
    # Audit-only mode: allow execution (no output).
    exit 0
  }

  # Deny decision must be single-line JSON; Compress is recommended by GitHub docs. 
  $resp = @{
    permissionDecision       = "deny"
    permissionDecisionReason = $denyReason
  }
  ($resp | ConvertTo-Json -Compress)
  exit 0
}

# Allow by default (no output)
exit 0




