@echo off
title Fix App.py
echo Fixing app.py to use system packages...

REM Check if app_original.py exists
if exist app_original.py (
    echo Restoring original app.py...
    copy /y app_original.py app.py >nul
    echo Done! Original app.py restored.
) else (
    echo Removing libs import from app.py...

    REM Create a temporary file without the libs import
    findstr /v "libs_dir = Path" app.py > app_temp.py
    findstr /v "sys.path.insert" app_temp.py > app_temp2.py
    findstr /v "from pathlib import Path" app_temp2.py > app_temp3.py
    findstr /v "# Auto-load local libs" app_temp3.py > app_temp4.py
    findstr /v "# Portable version support" app_temp4.py > app_temp5.py
    findstr /v "if libs_dir.exists" app_temp5.py > app_clean.py

    REM Backup current app.py
    copy app.py app_with_libs.py >nul

    REM Replace with clean version
    copy /y app_clean.py app.py >nul

    REM Clean up temp files
    del app_temp*.py app_clean.py 2>nul

    echo Done! Cleaned app.py
)

echo.
echo Now delete or rename the libs folder:
echo   rmdir /s /q libs
echo Or rename it:
echo   rename libs libs_old
echo.
echo Then run: python app.py
echo.
pause