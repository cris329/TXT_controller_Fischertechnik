@echo off
cd /d "%~dp0\.."
if not exist "scripts\wifi_host.txt" (
  echo Primero corre: python scripts\wait_wifi_and_switch.py
  pause
  exit /b 1
)
set /p TXT_HOST=<scripts\wifi_host.txt
echo Usando TXT_HOST=%TXT_HOST%
python pc\app.py
