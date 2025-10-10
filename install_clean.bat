@echo off
title Install Dependencies
echo ====================================================
echo     Clean Install Dependencies
echo ====================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo Cleaning old dependencies...
if exist libs rmdir /s /q libs
mkdir libs

echo.
echo Installing dependencies from requirements.txt...
echo This will take a few minutes...
echo.

REM Install with pip using requirements.txt
python -m pip install --target libs -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ====================================================
    echo     Installation Failed - Trying Alternative
    echo ====================================================
    echo.

    REM Try installing without target (system-wide)
    python -m pip install -r requirements.txt

    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Installation failed.
        echo.
        echo Try running these commands manually:
        echo   python -m pip install --upgrade pip
        echo   python -m pip install -r requirements.txt
        pause
        exit /b 1
    )

    echo.
    echo Dependencies installed system-wide.
    echo Note: You don't need the libs folder.
) else (
    echo.
    echo ====================================================
    echo     Installation Complete!
    echo ====================================================
    echo Dependencies installed to libs folder.
)

echo.
echo You can now run: start_api.bat
echo.
pause