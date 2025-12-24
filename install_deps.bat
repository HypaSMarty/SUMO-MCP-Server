@echo off
setlocal

REM Windows bootstrap wrapper for install_deps.ps1
REM Usage:
REM   install_deps.bat
REM   install_deps.bat -NoDev
REM   install_deps.bat -IndexUrl https://pypi.tuna.tsinghua.edu.cn/simple

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_deps.ps1" %*

