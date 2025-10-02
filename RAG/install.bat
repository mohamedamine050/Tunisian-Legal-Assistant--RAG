@echo off
title Setup and Launch Script

REM Change directory to the folder where this batch file resides
cd /d "%~dp0"

REM Step 1: Create virtual environment and install dependencies
echo Creating virtual environment and installing dependencies...
python setup_venv.py
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment or install dependencies.
    pause
    exit /b 1
)

REM Step 2: Run the MongoDB fill script
echo Running MongoDB fill script...
python mangodb_fill.py
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to execute mangodb_fill.py.
    pause
    exit /b 1
)

REM Step 3: Start FastAPI server in a new command prompt window using relative paths
echo Starting FastAPI server...
start "FastAPI Server" cmd /k "cd /d \"%~dp0api\" && call \"%~dp0venv\Scripts\activate\" && python -m app.main"

pause
