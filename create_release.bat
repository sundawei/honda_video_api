@echo off
title 创建发布包
echo ========================================
echo     IP Camera Recorder - 创建发布包
echo ========================================
echo.

REM 设置发布包名称和版本
set VERSION=1.0.0
set RELEASE_NAME=IPCameraRecorder_v%VERSION%
set RELEASE_DIR=release\%RELEASE_NAME%

REM 创建发布目录
echo [1/5] 创建发布目录...
if exist release rmdir /s /q release
mkdir %RELEASE_DIR%

REM 复制核心文件
echo [2/5] 复制核心文件...
copy app.py %RELEASE_DIR%\
copy app_original.py %RELEASE_DIR%\ 2>nul
copy recorder.py %RELEASE_DIR%\
copy recording_manager.py %RELEASE_DIR%\
copy camera_manager.py %RELEASE_DIR%\
copy video_processor.py %RELEASE_DIR%\
copy config.yaml %RELEASE_DIR%\
copy requirements.txt %RELEASE_DIR%\
copy start_api.bat %RELEASE_DIR%\
copy start_api_portable.bat %RELEASE_DIR%\
copy "部署说明.md" %RELEASE_DIR%\

REM 复制目录
echo [3/5] 复制依赖和资源...
xcopy /s /e /i /q libs %RELEASE_DIR%\libs
xcopy /s /e /i /q static %RELEASE_DIR%\static
xcopy /s /e /i /q templates %RELEASE_DIR%\templates

REM 创建必要的空目录
echo [4/5] 创建必要目录...
mkdir %RELEASE_DIR%\recordings
mkdir %RELEASE_DIR%\logs

REM 创建README文件
echo [5/5] 创建README...
echo # IP Camera Recorder API v%VERSION% > %RELEASE_DIR%\README.txt
echo. >> %RELEASE_DIR%\README.txt
echo 快速启动: >> %RELEASE_DIR%\README.txt
echo 1. 确保已安装Python 3.7+ 和 FFmpeg >> %RELEASE_DIR%\README.txt
echo 2. 双击运行 start_api.bat >> %RELEASE_DIR%\README.txt
echo. >> %RELEASE_DIR%\README.txt
echo 详细说明请查看: 部署说明.md >> %RELEASE_DIR%\README.txt

echo.
echo ✅ 发布包创建成功！
echo 📁 位置: %RELEASE_DIR%
echo.

REM 询问是否压缩
set /p COMPRESS="是否创建ZIP压缩包？(Y/N): "
if /i "%COMPRESS%"=="Y" (
    echo.
    echo 正在创建压缩包...

    REM 使用PowerShell压缩
    powershell -Command "Compress-Archive -Path '%RELEASE_DIR%' -DestinationPath 'release\%RELEASE_NAME%.zip' -Force"

    if exist "release\%RELEASE_NAME%.zip" (
        echo ✅ 压缩包创建成功: release\%RELEASE_NAME%.zip

        REM 显示文件大小
        for %%A in ("release\%RELEASE_NAME%.zip") do echo 📦 文件大小: %%~zA bytes
    ) else (
        echo ❌ 压缩包创建失败
    )
)

echo.
pause