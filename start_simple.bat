@echo off
title IP Camera Recorder API
echo ========================================
echo     IP Camera Recorder API Server
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found. Recording will not work.
    echo Download from: https://ffmpeg.org/download.html
    echo.
)

echo Starting API server...
echo Service URL: http://127.0.0.1:9999
echo API Docs:    http://127.0.0.1:9999/docs
echo.
echo Press Ctrl+C to stop
echo.

python app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start. Please check:
    echo 1. Have you installed dependencies?
    echo    Run: pip install -r requirements.txt
    echo 2. Check the error message above
    pause
)