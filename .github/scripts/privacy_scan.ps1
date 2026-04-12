Param(
  [string]$Root = "."
)

Write-Host "== Privacy Scan (lightweight) =="
Write-Host "Root: $Root`n"

function Scan([string]$Pattern, [string]$Label) {
  Write-Host "-- $Label"
  Get-ChildItem -Path $Root -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\.git\\|\\node_modules\\|\\dist\\|\\build\\' } |
    Select-String -Pattern $Pattern -SimpleMatch -ErrorAction SilentlyContinue |
    ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
  Write-Host ""
}

Scan "logger" "Logging calls (logger)"
Scan "console.log" "Logging calls (console.log)"
Scan "telemetry" "Telemetry"
Scan "analytics" "Analytics"
Scan "Authorization" "Auth headers"
Scan "Bearer" "Bearer tokens"
Scan "cookie" "Cookies"
Scan "api_key" "API keys"
Scan "token" "Tokens"
Scan "jwt" "JWT"
Scan "email" "PII indicators"
Scan "phone" "PII indicators"
Scan "address" "PII indicators"
Scan "ssn" "PII indicators"
Scan "ip" "Identifiers"
Scan "device_id" "Identifiers"
Scan "session_id" "Identifiers"
Scan "user_id" "Identifiers"
Scan "retention" "Retention clues"
Scan "redis" "Persistence clues"
Scan "s3" "Persistence clues"
Scan "database" "Persistence clues"

Write-Host "== End scan =="

