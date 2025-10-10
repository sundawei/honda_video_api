@echo off
title Create Release Package
echo ====================================================
echo        Creating Release Package
echo ====================================================
echo.

set VERSION=1.0.0
set PACKAGE_NAME=IPCameraRecorder_v%VERSION%
set PACKAGE_DIR=release\%PACKAGE_NAME%

echo Cleaning old release...
if exist release rmdir /s /q release

echo Creating package directory...
mkdir %PACKAGE_DIR%

echo Copying files...

REM Copy Python files
copy app.py %PACKAGE_DIR%\ >nul
copy recorder.py %PACKAGE_DIR%\ >nul
copy recording_manager.py %PACKAGE_DIR%\ >nul
copy camera_manager.py %PACKAGE_DIR%\ >nul
copy video_processor.py %PACKAGE_DIR%\ >nul

REM Copy configuration and documentation
copy config.yaml %PACKAGE_DIR%\ >nul
copy requirements.txt %PACKAGE_DIR%\ >nul
copy start_simple.bat %PACKAGE_DIR%\ >nul
copy README_DEPLOY.md %PACKAGE_DIR%\ >nul

REM Copy directories
xcopy /s /e /i /q static %PACKAGE_DIR%\static >nul
xcopy /s /e /i /q templates %PACKAGE_DIR%\templates >nul

REM Create empty directories
mkdir %PACKAGE_DIR%\recordings
mkdir %PACKAGE_DIR%\logs

REM Create installation script
(
echo @echo off
echo title Install Dependencies
echo echo ====================================
echo echo     Installing Dependencies
echo echo ====================================
echo echo.
echo echo This will install required Python packages.
echo echo.
echo pip install -r requirements.txt
echo echo.
echo if %%errorlevel%% equ 0 ^(
echo     echo Installation complete!
echo     echo You can now run: start_simple.bat
echo ^) else ^(
echo     echo Installation failed. Please check the error above.
echo ^)
echo pause
) > %PACKAGE_DIR%\install.bat

echo.
echo ====================================================
echo           Package Created Successfully!
echo ====================================================
echo.
echo Location: %PACKAGE_DIR%
echo.
echo Package Contents:
dir /b %PACKAGE_DIR%
echo.

set /p ZIP=Create ZIP file? (Y/N):
if /i "%ZIP%"=="Y" (
    echo Creating ZIP file...
    powershell Compress-Archive -Path "%PACKAGE_DIR%" -DestinationPath "release\%PACKAGE_NAME%.zip"
    echo ZIP file created: release\%PACKAGE_NAME%.zip
)

echo.
echo Deployment Instructions:
echo ------------------------
echo 1. Extract the package on target machine
echo 2. Install Python 3.7+ and FFmpeg
echo 3. Run: install.bat
echo 4. Run: start_simple.bat
echo.
pause