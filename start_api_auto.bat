@echo off
title IP Camera Recorder API - Auto Setup
echo ====================================================
echo     IP Camera Recorder API - Auto Setup
echo ====================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if libs directory exists and has content
set LIBS_EXISTS=0
if exist libs (
    for /f %%i in ('dir /b libs 2^>nul ^| find /c /v ""') do (
        if %%i gtr 0 set LIBS_EXISTS=1
    )
)

REM Check if we can import fastapi from libs
if %LIBS_EXISTS%==1 (
    echo Testing existing dependencies...
    python -c "import sys; sys.path.insert(0, 'libs'); import fastapi" 2>nul
    if %errorlevel% neq 0 (
        echo [WARNING] Dependencies exist but are incompatible with this system.
        set LIBS_EXISTS=0
    ) else (
        echo [OK] Using existing dependencies.
    )
)

REM If libs don't exist or are incompatible, install them
if %LIBS_EXISTS%==0 (
    echo.
    echo Dependencies not found or incompatible.
    echo Installing dependencies for this machine...
    echo This is a one-time process and may take a few minutes...
    echo.

    REM Create libs directory
    if not exist libs mkdir libs

    REM Install dependencies
    echo Installing FastAPI...
    python -m pip install --target libs --upgrade fastapi==0.104.1
    if %errorlevel% neq 0 goto :install_error

    echo Installing Uvicorn...
    python -m pip install --target libs --upgrade "uvicorn[standard]==0.24.0"
    if %errorlevel% neq 0 goto :install_error

    echo Installing other dependencies...
    python -m pip install --target libs --upgrade jinja2==3.1.2 python-multipart==0.0.6 pyyaml==6.0.1 python-dateutil==2.8.2
    if %errorlevel% neq 0 goto :install_error

    echo.
    echo Dependencies installed successfully!
    echo.
)

REM Update app.py to use libs if needed
findstr /C:"libs_dir = Path" app.py >nul
if %errorlevel% neq 0 (
    echo Updating app.py to use local dependencies...

    REM Backup original
    if not exist app_original.py copy app.py app_original.py >nul

    REM Create temp file with libs support
    (
        echo # Auto-load local libs directory
        echo import sys
        echo from pathlib import Path
        echo libs_dir = Path^(__file__^).parent / "libs"
        echo if libs_dir.exists^(^):
        echo     sys.path.insert^(0, str^(libs_dir^)^)
        echo.
        type app.py
    ) > app_temp.py
    move /y app_temp.py app.py >nul
)

REM Set Python path
set PYTHONPATH=%~dp0libs;%PYTHONPATH%

REM Start the API server
echo.
echo ====================================================
echo Starting API Server...
echo ====================================================
echo.
echo Service URL: http://127.0.0.1:9999
echo API Docs:    http://127.0.0.1:9999/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server failed to start.
    echo Check the error messages above.
    pause
)
goto :end

:install_error
echo.
echo [ERROR] Failed to install dependencies.
echo.
echo Possible solutions:
echo 1. Check your internet connection
echo 2. Try running: python -m pip install --upgrade pip
echo 3. Install dependencies manually:
echo    python -m pip install fastapi uvicorn jinja2 python-multipart pyyaml python-dateutil
echo.
pause

:end