Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Guardrail: singular path drift should never reappear in active agent config.
$targets = @('.github', 'scripts')
$files = @()
foreach ($root in $targets) {
    if (Test-Path $root) {
        $files += Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue
    }
}
if (Test-Path 'AGENTS.md') { $files += Get-Item 'AGENTS.md' }
if (Test-Path '.github/copilot-instructions.md') { $files += Get-Item '.github/copilot-instructions.md' }

$exclude = @(
    [IO.Path]::GetFullPath('.github/instructions/agent-artifacts.instructions.md'),
    [IO.Path]::GetFullPath('.github/tests/agent-path-policy.test.ps1'),
    [IO.Path]::GetFullPath('scripts/ci/check_agent_paths.py'),
    [IO.Path]::GetFullPath('scripts/ci/check_agent_paths.sh')
)
$files = $files | Where-Object { $exclude -notcontains $_.FullName }

$pathMatches = $files | Select-String -Pattern 'docs/agent/' -SimpleMatch -ErrorAction SilentlyContinue
if ($pathMatches) {
    $pathMatches | ForEach-Object { Write-Output ("{0}:{1}: {2}" -f $_.Path, $_.LineNumber, $_.Line.Trim()) }
    throw 'Found forbidden path token docs/agent/'
}

Write-Output 'agent-path-policy: PASS'


