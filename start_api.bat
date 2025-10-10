@echo off
title IP Camera Recorder API
echo ========================================
echo     IP Camera Recorder API Server
echo ========================================
echo.

REM Set Python path to include libs directory
set PYTHONPATH=%~dp0libs;%PYTHONPATH%

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo Starting API server...
echo Service URL: http://127.0.0.1:9999
echo Press Ctrl+C to stop
echo.

python app.py

if %errorlevel% neq 0 pause
