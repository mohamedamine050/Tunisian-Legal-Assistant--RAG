@echo off
title Start RAG System

REM Change directory to the script's location
cd /d "%~dp0"

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Start FastAPI server and wait for it to finish
echo Starting FastAPI server...
start "FastAPI Server" cmd /k "call venv\Scripts\activate.bat && python -m app.main"

REM Wait for the server to be ready
echo Waiting for FastAPI to start...
:loop
timeout /t 2 /nobreak >nul

REM Check if the server is running on port 8000
curl -s http://127.0.0.1:8000 >nul
if %ERRORLEVEL% neq 0 (
    echo Server is not ready yet...
    goto loop
)

REM Open Swagger UI in default web browser after server is up
echo FastAPI is now running. Opening Swagger UI...
start http://127.0.0.1:8000/docs

exit
