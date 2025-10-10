@echo off
title IP Camera Recorder - Build Portable
color 0A

echo ====================================================
echo      IP Camera Recorder - Portable Builder
echo ====================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo [1/4] Cleaning old files...
if exist libs rmdir /s /q libs 2>nul
mkdir libs

echo [2/4] Installing dependencies...
echo.

REM Install dependencies one by one
echo   - Installing FastAPI...
python -m pip install --target libs --upgrade --no-cache-dir fastapi==0.104.1 -q

echo   - Installing Uvicorn...
python -m pip install --target libs --upgrade --no-cache-dir "uvicorn[standard]==0.24.0" -q

echo   - Installing Jinja2...
python -m pip install --target libs --upgrade --no-cache-dir jinja2==3.1.2 -q

echo   - Installing Python-Multipart...
python -m pip install --target libs --upgrade --no-cache-dir python-multipart==0.0.6 -q

echo   - Installing PyYAML...
python -m pip install --target libs --upgrade --no-cache-dir pyyaml==6.0.1 -q

echo   - Installing Python-Dateutil...
python -m pip install --target libs --upgrade --no-cache-dir python-dateutil==2.8.2 -q

echo.
echo [3/4] Updating startup files...

REM Check if app.py needs update
findstr /C:"libs_dir = Path" app.py >nul
if %errorlevel% neq 0 (
    REM Backup original file
    if not exist app_original.py copy app.py app_original.py >nul

    REM Create temp file with libs support
    (
        echo # Portable version support: auto-load local libs
        echo import sys
        echo from pathlib import Path
        echo libs_dir = Path^(__file__^).parent / "libs"
        echo if libs_dir.exists^(^):
        echo     sys.path.insert^(0, str^(libs_dir^)^)
        echo.
        type app.py
    ) > app_temp.py
    move /y app_temp.py app.py >nul
    echo   - Updated app.py
) else (
    echo   - app.py already has libs support
)

echo.
echo [4/4] Creating startup script...

REM Create startup script
(
echo @echo off
echo title IP Camera Recorder API
echo echo ========================================
echo echo     IP Camera Recorder API Server
echo echo ========================================
echo echo.
echo.
echo REM Set Python path to include libs directory
echo set PYTHONPATH=%%~dp0libs;%%PYTHONPATH%%
echo.
echo REM Check Python
echo python --version ^>nul 2^>^&1
echo if %%errorlevel%% neq 0 ^(
echo     echo [ERROR] Python not found. Please install Python 3.7+
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
) > start_api.bat

echo   - Created start_api.bat
echo.

REM Count installed packages
for /f %%i in ('dir /b libs ^| find /c /v ""') do set package_count=%%i

echo ====================================================
echo              BUILD COMPLETE!
echo ====================================================
echo.
echo Installed %package_count% packages to libs directory
echo Run start_api.bat to start the service
echo Configuration file: config.yaml
echo.
pause