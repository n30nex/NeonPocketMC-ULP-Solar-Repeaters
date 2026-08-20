@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 goto :fail
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto :fail
".venv\Scripts\python.exe" configure_ulp.py
pause
exit /b %errorlevel%
:fail
echo Setup could not start. Install Python 3 from python.org and try again.
pause
exit /b 1
