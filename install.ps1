$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$Root;$env:PYTHONPATH" } else { $Root }

$Python = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { $null }
if (-not $Python) {
    Write-Error "P172_PYTHON_NOT_FOUND: install Python 3.11 or use a verified offline bundle containing it"
    exit 2
}

if ($Python -eq "py") {
    & py -3.11 "$Root\hhs-bootstrap.py" install @args
} else {
    & $Python "$Root\hhs-bootstrap.py" install @args
}
exit $LASTEXITCODE
