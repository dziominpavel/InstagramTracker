@echo off
chcp 65001 >nul
echo ========================================
echo   Instagram Tracker - Generate Dashboard
echo ========================================
echo.

REM Activate virtual environment
call "%~dp0.venv\Scripts\activate.bat"

REM Run generate command
python "%~dp0main.py" generate %*

echo.
echo Done! Open index.html (V2) in your browser.
echo Classic UI: index-v1.html
pause
