@echo off
title IP Camera Recorder API
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

REM Clean and reinstall if there are issues
echo Checking dependencies...

REM Test if pydantic works
python -c "import sys; sys.path.insert(0, 'libs'); from pydantic_core import _pydantic_core" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Dependencies missing or corrupted. Installing...
    echo This may take a few minutes on first run...
    echo.

    REM Remove old libs completely
    if exist libs (
        echo Removing old dependencies...
        rmdir /s /q libs
    )

    REM Create new libs directory
    mkdir libs

    REM Install using pip with all dependencies resolved
    echo Installing all dependencies...
    python -m pip install --target libs fastapi==0.104.1 uvicorn[standard]==0.24.0 jinja2==3.1.2 python-multipart==0.0.6 pyyaml==6.0.1 python-dateutil==2.8.2

    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Installation failed. Trying alternative method...
        echo.

        REM Alternative: Install to user site-packages and run from there
        echo Installing to user packages...
        python -m pip install --user fastapi==0.104.1 uvicorn[standard]==0.24.0 jinja2==3.1.2 python-multipart==0.0.6 pyyaml==6.0.1 python-dateutil==2.8.2

        if %errorlevel% neq 0 (
            echo.
            echo [ERROR] Installation failed completely.
            echo.
            echo Please install manually:
            echo   pip install fastapi uvicorn[standard] jinja2 python-multipart pyyaml python-dateutil
            echo.
            pause
            exit /b 1
        )

        echo.
        echo Dependencies installed to user packages.
        echo Starting server without local libs...
        echo.
        goto :start_without_libs
    )

    echo.
    echo Dependencies installed successfully!
    echo.
)

REM Update app.py to use libs
findstr /C:"libs_dir = Path" app.py >nul
if %errorlevel% neq 0 (
    echo Configuring app.py...

    REM Backup original
    if not exist app_original.py copy app.py app_original.py >nul

    REM Create new app.py with libs support
    (
        echo # Auto-load local libs directory
        echo import sys
        echo from pathlib import Path
        echo libs_dir = Path^(__file__^).parent / "libs"
        echo if libs_dir.exists^(^):
        echo     sys.path.insert^(0, str^(libs_dir^)^)
        echo.
        type app_original.py
    ) > app.py
)

:start_with_libs
REM Set Python path
set PYTHONPATH=%~dp0libs;%PYTHONPATH%

echo.
echo ====================================================
echo Starting API Server...
echo ====================================================
echo Service URL: http://127.0.0.1:9999
echo API Docs:    http://127.0.0.1:9999/docs
echo Press Ctrl+C to stop
echo.

python app.py
goto :end

:start_without_libs
echo.
echo ====================================================
echo Starting API Server (using system packages)...
echo ====================================================
echo Service URL: http://127.0.0.1:9999
echo API Docs:    http://127.0.0.1:9999/docs
echo Press Ctrl+C to stop
echo.

REM Run without modifying app.py
python app_original.py 2>nul
if %errorlevel% neq 0 python app.py

:end
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server failed to start.
    pause
)