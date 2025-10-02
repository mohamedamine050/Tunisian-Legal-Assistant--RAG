@echo off
title LegallyTN Project Setup
echo Starting LegallyTN project setup...
setlocal enabledelayedexpansion

:: Step 1 - Install frontend dependencies
echo Installing frontend dependencies...
cd client
call npm install
cd ..

:: Step 2 - Install backend dependencies
echo Installing backend dependencies...
cd server
call npm install
cd ..

:: Step 3 - Set database variables
set DB_NAME=legallytn_db
set DB_USER=legallytn_user
set DB_PASSWORD=legallytn_secure

echo Setting up PostgreSQL database...

:: Step 4 - Create PostgreSQL Database & User (without password prompt)
(
echo CREATE DATABASE %DB_NAME%;
echo CREATE USER %DB_USER% WITH SUPERUSER;
echo GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;
) | psql -U postgres -d postgres --no-password

:: Step 5 - Create Tables
(
echo CREATE TABLE IF NOT EXISTS users (
echo    id SERIAL PRIMARY KEY,
echo    first_name VARCHAR(255) NOT NULL,
echo    last_name VARCHAR(255) NOT NULL,
echo    email VARCHAR(255) UNIQUE NOT NULL,
echo    password TEXT NOT NULL,
echo    phone_number VARCHAR(20),
echo    user_type VARCHAR(50),
echo    bar_number VARCHAR(50),
echo    created_at TIMESTAMP DEFAULT NOW()
echo );

echo CREATE TABLE IF NOT EXISTS conversations (
echo    id SERIAL PRIMARY KEY,
echo    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
echo    title VARCHAR(255) NOT NULL,
echo    created_at TIMESTAMP DEFAULT NOW()
echo );

echo CREATE TABLE IF NOT EXISTS messages (
echo    id SERIAL PRIMARY KEY,
echo    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
echo    sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
echo    message_type VARCHAR(50) DEFAULT 'text',
echo    message_content TEXT NOT NULL,
echo    sent_at TIMESTAMP DEFAULT NOW()
echo );
) | psql -U postgres -d %DB_NAME% --no-password

echo LegallyTN setup completed successfully.
pause
