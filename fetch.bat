@echo off
chcp 65001 >nul
echo ========================================
echo   Instagram Tracker - Fetch Avatars
echo ========================================
echo.
echo Fetching avatars and full names from Instagram profiles.
echo This may take a while (2-3 seconds per profile).
echo.

REM Activate virtual environment
call "%~dp0.venv\Scripts\activate.bat"

REM Run fetch command
python "%~dp0main.py" fetch %*

echo.
echo Done! Now run generate.bat to update the dashboard.
pause
