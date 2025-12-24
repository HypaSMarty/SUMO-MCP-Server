# SUMO-MCP dependency bootstrap (Windows PowerShell)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\install_deps.ps1
#   powershell -ExecutionPolicy Bypass -File .\install_deps.ps1 -NoDev
#   powershell -ExecutionPolicy Bypass -File .\install_deps.ps1 -IndexUrl https://pypi.tuna.tsinghua.edu.cn/simple
#
# What it does:
#   - Creates .venv (if missing)
#   - Upgrades pip
#   - Installs this project in editable mode (default: with dev extras)

param(
    [switch]$NoDev,
    [string]$IndexUrl = "",
    [string]$ExtraIndexUrl = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Python {
    param(
        [string[]]$PythonCmd,
        [string[]]$Args
    )

    if ($PythonCmd.Length -eq 1) {
        return & $PythonCmd[0] @Args
    }

    $prefix = $PythonCmd[1..($PythonCmd.Length - 1)]
    return & $PythonCmd[0] @prefix @Args
}

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

# Resolve a base Python (prefer `python`, fallback to the Windows launcher `py -3`).
$PythonCmd = @()
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $PythonCmd = @($python.Path)
} else {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if (-not $py) {
        throw "Python not found. Install Python 3.10+ and ensure `python` or `py` is available in PATH."
    }
    $PythonCmd = @($py.Path, "-3")
}

# Verify Python version (>= 3.10).
$versionText = (Invoke-Python $PythonCmd @("-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")).Trim()
$parts = $versionText.Split(".")
if ($parts.Length -lt 2) {
    throw "Could not detect Python version from: $versionText"
}
$major = [int]$parts[0]
$minor = [int]$parts[1]
if (($major -lt 3) -or (($major -eq 3) -and ($minor -lt 10))) {
    throw "Python 3.10+ required. Found: $versionText"
}

$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating virtual environment: $VenvDir"
    Invoke-Python $PythonCmd @("-m", "venv", $VenvDir) | Out-Null
    if (-not (Test-Path $VenvPython)) {
        throw "Failed to create venv. Expected: $VenvPython"
    }
} else {
    Write-Host "Using existing virtual environment: $VenvDir"
}

$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
if ($IndexUrl) {
    $env:PIP_INDEX_URL = $IndexUrl
}
if ($ExtraIndexUrl) {
    $env:PIP_EXTRA_INDEX_URL = $ExtraIndexUrl
}

Write-Host "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip setuptools wheel

$spec = if ($NoDev) { "." } else { ".[dev]" }
Write-Host "Installing project: $spec"
& $VenvPython -m pip install -e $spec

Write-Host ""
Write-Host "Done."
Write-Host "Activate venv: .\\.venv\\Scripts\\activate"
Write-Host "Start server:  .\\.venv\\Scripts\\python.exe src\\server.py"
Write-Host "Or use:        .\\start_server.ps1"
