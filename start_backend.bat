@echo off
REM Meta-Learning System Startup Script
REM This script helps you start the entire system quickly

echo.
echo ============================================================
echo     META-LEARNING AI SYSTEM - STARTUP SCRIPT
echo ============================================================
echo.

echo [1/3] Checking Python environment...
IF NOT EXIST venv (
    echo ERROR: Virtual environment not found!
    echo Please create it first: python -m venv venv
    pause
    exit /b 1
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/3] Starting Python Backend (Port 8000)...
echo.
echo ============================================================
echo Backend is starting at http://localhost:8000
echo Watch for Transformer model loading and Supabase connection
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

uvicorn app:app --reload
