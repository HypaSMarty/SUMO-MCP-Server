# SUMO-MCP Server Startup Script for PowerShell
# 说明：
# - SUMO 需已安装
# - 推荐：在系统环境变量中设置 SUMO_HOME，并确保 $env:SUMO_HOME\bin 在 PATH 中
# - 若未设置 SUMO_HOME，本脚本将仅依赖 PATH 中的 sumo/netgenerate 等二进制

if ($env:SUMO_HOME) {
    $env:PATH = "$env:SUMO_HOME\bin;$env:PATH"
} else {
    Write-Host "[WARN] SUMO_HOME not set, relying on PATH."
}

$sumoCmd = Get-Command sumo -ErrorAction SilentlyContinue
if (-not $sumoCmd) {
    if (-not $env:SUMO_HOME) {
        Write-Error "SUMO not found. Please install SUMO or set SUMO_HOME."
    } else {
        Write-Error "sumo not found in PATH after applying SUMO_HOME=$env:SUMO_HOME (expected $env:SUMO_HOME\\bin)."
    }
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\src\server.py"
