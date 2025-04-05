@echo off
echo Starting Coresky Automation Bots
echo ===============================

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if the script exists
if not exist multiprocessing_browser.py (
    echo Error: multiprocessing_browser.py not found
    pause
    exit /b 1
)

:: Check if required packages are installed
echo Checking dependencies...
pip install selenium psutil > nul 2>&1

:: Run the script
echo Starting automation bots...
echo Press Ctrl+C to stop all bots.
echo.

:: Uncomment and modify the line below to run a specific number of instances
:: python multiprocessing_browser.py --instances=20

:: Or use auto-detection (recommended)
python multiprocessing_browser.py

pause 