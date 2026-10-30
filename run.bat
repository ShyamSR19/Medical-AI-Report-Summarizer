@echo off
cd /d "%~dp0"
echo ===================================================
echo   Starting ClarityMed Navigator (Flask Server)
echo ===================================================
echo.
echo 1. Opening your browser to http://127.0.0.1:5000 ...
start "" "http://127.0.0.1:5000"
echo.
echo 2. Launching server... (Do not close this window!)
echo.
.\venv\Scripts\python.exe app.py
if errorlevel 1 (
    echo.
    echo Trying fallback launcher...
    py app.py
)
pause
