@echo off
title Create Release Package
color 0B

echo ====================================================
echo        IP Camera Recorder - Create Release
echo ====================================================
echo.

REM Set version and directory
set VERSION=1.0.0
set RELEASE_NAME=IPCameraRecorder_v%VERSION%
set RELEASE_DIR=release\%RELEASE_NAME%

echo Version: %VERSION%
echo.

REM Build portable version first
echo [1/6] Building portable version...
call build_portable.bat
if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [2/6] Creating release directory...
if exist release rmdir /s /q release
mkdir %RELEASE_DIR%

echo [3/6] Copying program files...
REM Core Python files
copy app.py %RELEASE_DIR%\ >nul
copy recorder.py %RELEASE_DIR%\ >nul
copy recording_manager.py %RELEASE_DIR%\ >nul
copy camera_manager.py %RELEASE_DIR%\ >nul
copy video_processor.py %RELEASE_DIR%\ >nul
copy config.yaml %RELEASE_DIR%\ >nul

REM Documentation and scripts
copy start_api.bat %RELEASE_DIR%\ >nul
copy requirements.txt %RELEASE_DIR%\ >nul
if exist test_api_client.py copy test_api_client.py %RELEASE_DIR%\ >nul

echo [4/6] Copying dependencies and resources...
REM Copy libs directory
xcopy /s /e /i /q libs %RELEASE_DIR%\libs >nul

REM Copy static resources
if exist static xcopy /s /e /i /q static %RELEASE_DIR%\static >nul
if exist templates xcopy /s /e /i /q templates %RELEASE_DIR%\templates >nul

echo [5/6] Creating necessary directories...
mkdir %RELEASE_DIR%\recordings 2>nul
mkdir %RELEASE_DIR%\logs 2>nul

echo [6/6] Creating README file...
(
echo IP Camera Recorder API v%VERSION%
echo ====================================
echo.
echo Quick Start:
echo ------------
echo 1. Make sure Python 3.7+ and FFmpeg are installed
echo 2. Edit config.yaml to configure camera information
echo 3. Double-click start_api.bat to run
echo.
echo Directory Structure:
echo --------------------
echo - libs/        : Python dependencies [included]
echo - recordings/  : Video file storage
echo - logs/        : Log files
echo - config.yaml  : Configuration file
echo.
echo API URL:
echo --------
echo http://127.0.0.1:9999
echo.
echo For detailed instructions, please check the documentation.
) > %RELEASE_DIR%\README.txt

echo.
echo ====================================================
echo           RELEASE PACKAGE CREATED!
echo ====================================================
echo.
echo Location: %RELEASE_DIR%
echo.

REM Ask if want to compress
set /p COMPRESS=Create ZIP archive? (Y/N):
if /i "%COMPRESS%"=="Y" (
    echo.
    echo Creating ZIP archive...

    REM Check for 7z
    where 7z >nul 2>&1
    if %errorlevel% equ 0 (
        7z a -tzip "release\%RELEASE_NAME%.zip" "%RELEASE_DIR%\*" -r >nul
        echo Created archive with 7-Zip
    ) else (
        REM Use PowerShell to compress
        powershell -NoProfile -Command "Compress-Archive -Path '%RELEASE_DIR%' -DestinationPath 'release\%RELEASE_NAME%.zip' -Force"
        echo Created archive with PowerShell
    )

    if exist "release\%RELEASE_NAME%.zip" (
        for %%F in ("release\%RELEASE_NAME%.zip") do (
            set /a size=%%~zF/1024/1024
        )
        echo File: release\%RELEASE_NAME%.zip
        echo Size: Approx !size! MB
    )
)

echo.
echo Release contents:
echo -----------------
dir /b %RELEASE_DIR%
echo.
pause