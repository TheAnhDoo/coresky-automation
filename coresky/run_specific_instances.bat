@echo off
:: Get the number of instances as a parameter or use default
set INSTANCES=%1
if "%INSTANCES%"=="" set INSTANCES=8

echo Starting Coresky Automation with %INSTANCES% browser instances
echo ===========================================================

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

:: Run the script with specified number of instances
echo Starting automation with %INSTANCES% bots...
echo Press Ctrl+C to stop all bots.
echo.

python multiprocessing_browser.py --instances=%INSTANCES%

pause 