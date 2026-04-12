$ErrorActionPreference = "Stop"

$pythonBin = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "python" }
& $pythonBin "$PSScriptRoot/full_test.py"
exit $LASTEXITCODE
