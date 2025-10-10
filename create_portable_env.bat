@echo off
title Create Portable Python Environment
echo ====================================================
echo     Creating Portable Python Environment
echo ====================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if exist venv rmdir /s /q venv
python -m venv venv

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies in virtual environment...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [4/4] Creating portable starter script...
(
echo @echo off
echo title IP Camera Recorder API - Portable
echo echo ========================================
echo echo     IP Camera Recorder API Server
echo echo ========================================
echo echo.
echo.
echo REM Activate virtual environment
echo call venv\Scripts\activate.bat
echo.
echo REM Check if activation succeeded
echo if "%%VIRTUAL_ENV%%"=="" ^(
echo     echo [ERROR] Failed to activate virtual environment
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo Starting API server...
echo echo Service URL: http://127.0.0.1:9999
echo echo Press Ctrl+C to stop
echo echo.
echo.
echo python app.py
echo.
echo if %%errorlevel%% neq 0 pause
echo deactivate
) > start_api_portable.bat

echo.
echo ====================================================
echo           SETUP COMPLETE!
echo ====================================================
echo.
echo Virtual environment created successfully!
echo.
echo To run on any machine:
echo 1. Copy the entire folder including 'venv' directory
echo 2. Run: start_api_portable.bat
echo.
echo Note: Both source and target machines should have
echo       similar Python versions for best compatibility.
echo.
pause