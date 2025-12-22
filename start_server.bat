@echo off
REM SUMO-MCP Server Startup Script for Windows
REM 说明：
REM - SUMO 需已安装
REM - 推荐：在系统环境变量中设置 SUMO_HOME，并确保 %SUMO_HOME%\\bin 在 PATH 中
REM - 若未设置 SUMO_HOME，本脚本将仅依赖 PATH 中的 sumo/netgenerate 等二进制

if defined SUMO_HOME (
  set "PATH=%SUMO_HOME%\bin;%PATH%"
) else (
  echo [WARN] SUMO_HOME not set, relying on PATH.
)

where sumo >nul 2>nul
if errorlevel 1 (
  echo [ERROR] SUMO not found. Please install SUMO or set SUMO_HOME and ensure %%SUMO_HOME%%\bin is in PATH.
  exit /b 1
)

python "%~dp0src\server.py"
