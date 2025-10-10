@echo off
title Install Dependencies for IP Camera Recorder
echo ====================================================
echo     Installing Dependencies for Current Machine
echo ====================================================
echo.
echo This script will install all required dependencies
echo for the current machine to ensure compatibility.
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo [1/3] Cleaning old dependencies...
if exist libs rmdir /s /q libs 2>nul
mkdir libs

echo.
echo [2/3] Installing dependencies for this machine...
echo This may take a few minutes...
echo.

REM Install all dependencies with --platform and --python-version for current system
python -m pip install --target libs --upgrade --no-deps fastapi==0.104.1
python -m pip install --target libs --upgrade --no-deps uvicorn==0.24.0
python -m pip install --target libs --upgrade --no-deps pydantic==2.5.0
python -m pip install --target libs --upgrade --no-deps pydantic-core==2.14.0
python -m pip install --target libs --upgrade --no-deps typing-extensions
python -m pip install --target libs --upgrade --no-deps starlette
python -m pip install --target libs --upgrade --no-deps anyio
python -m pip install --target libs --upgrade --no-deps sniffio
python -m pip install --target libs --upgrade --no-deps idna
python -m pip install --target libs --upgrade --no-deps click
python -m pip install --target libs --upgrade --no-deps h11
python -m pip install --target libs --upgrade --no-deps httptools
python -m pip install --target libs --upgrade --no-deps python-dotenv
python -m pip install --target libs --upgrade --no-deps watchfiles
python -m pip install --target libs --upgrade --no-deps websockets
python -m pip install --target libs --upgrade --no-deps jinja2==3.1.2
python -m pip install --target libs --upgrade --no-deps MarkupSafe
python -m pip install --target libs --upgrade --no-deps python-multipart==0.0.6
python -m pip install --target libs --upgrade --no-deps pyyaml==6.0.1
python -m pip install --target libs --upgrade --no-deps python-dateutil==2.8.2
python -m pip install --target libs --upgrade --no-deps six
python -m pip install --target libs --upgrade --no-deps certifi
python -m pip install --target libs --upgrade --no-deps annotated-types
python -m pip install --target libs --upgrade --no-deps uvloop

echo.
echo [3/3] Installing full dependency tree...
python -m pip install --target libs --upgrade -r requirements.txt

echo.
echo ====================================================
echo           INSTALLATION COMPLETE!
echo ====================================================
echo.
echo Dependencies have been installed for this machine.
echo You can now run: start_api.bat
echo.
pause