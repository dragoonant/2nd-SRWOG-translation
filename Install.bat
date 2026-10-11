@echo off
rem Double-click to run. See README.md for details.
setlocal
cd /d "%~dp0"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo Python 3.10 or newer is needed.
  echo Get it from https://www.python.org/downloads/ and tick "Add python.exe to PATH" in the installer.
  start "" https://www.python.org/downloads/
  pause
  exit /b 1
)
%PY% install.py %*
pause
