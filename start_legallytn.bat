@echo off
title Start LegallyTN and RAG Servers
echo Starting all required servers...

:: Step 1 - Start FastAPI Server
echo Starting FastAPI server...
start cmd /k "cd /d RAG && venv\Scripts\activate && python -m app.main"

:: Step 2 - Start Node.js Backend Server
echo Starting Node.js backend server...
start cmd /k "cd /d LegallyTN\server && node server.js"

:: Step 3 - Start React Frontend Server
echo Starting frontend server...
start cmd /k "cd /d LegallyTN\client && npm start"

echo All servers are starting up. Keep the opened terminal windows running.
pause
