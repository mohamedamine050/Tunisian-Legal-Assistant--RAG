@echo off
title Start LegallyTN Project
echo Starting LegallyTN project...

:: Step 1 - Start PostgreSQL (if not running)
echo Checking PostgreSQL status...
net start postgresql 2>nul || echo PostgreSQL is already running.

:: Step 2 - Start Backend Server
echo Starting the backend server...
cd server
start cmd /k "node server.js"
cd ..

:: Step 3 - Start Frontend React App
echo Starting the frontend React app...
cd client
start cmd /k "npm start"
cd ..

echo LegallyTN project is running.
pause
