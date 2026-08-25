@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [Minecraft World Translator] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo python was not found. Install Python 3.11+ from https://www.python.org/downloads/windows/
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
python -m pip install -q -r requirements.txt
python webui_server.py --host 127.0.0.1 --port 8765 --open-browser
if errorlevel 1 pause
