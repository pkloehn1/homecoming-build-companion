Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    $usePyLauncher = $false
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            throw "python.exe or py.exe not found on PATH."
        }
        $usePyLauncher = $true
    }

    Push-Location $repoRoot
    try {
        if ($usePyLauncher) {
            & $pythonCmd.Source -3 -m tools.dev.bootstrap_venv @args
        } else {
            & $pythonCmd.Source -m tools.dev.bootstrap_venv @args
        }
        if ($LASTEXITCODE -ne 0) {
            throw "bootstrap_venv failed with exit code $LASTEXITCODE."
        }
    } finally {
        Pop-Location
    }
} catch {
    Write-Error "[FAIL] $($_.Exception.Message)"
    exit 1
}
