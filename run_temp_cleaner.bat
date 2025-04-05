@echo off
echo Starting Temp Folder Cleaner...
echo This window will close automatically, but the cleaner will continue running in the background.
echo To stop the cleaner, use Task Manager to end the Python process.

:: Run the Python script in the background
start /min pythonw temp_cleaner.py

:: Wait a moment to show the message
timeout /t 5 /nobreak > nul

:: Close this window
exit 