@echo off
title Shikshalay AI Educator Server
echo ===================================================
echo Starting Shikshalay AI Educator Backend...
echo ===================================================

cd /d %~dp0

if not exist venv\Scripts\python.exe (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please run: python -m venv venv and pip install -r requirements.txt
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Uvicorn on http://localhost:8000 ...
echo Press Ctrl+C in this window to stop the server.
echo.

venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
pause
