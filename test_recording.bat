@echo off
REM ====================================
REM IP Camera Recording Test Script (Windows)
REM ====================================

echo ========================================
echo IP Camera Recording Test
echo ========================================
echo.

REM 设置变量
set RTSP_URL=rtsp://admin:Admin1234@192.168.31.14:554/main
set OUTPUT_FILE=test_output_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.mp4
set OUTPUT_FILE=%OUTPUT_FILE: =0%
set LOG_FILE=ffmpeg_test_log_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set LOG_FILE=%LOG_FILE: =0%
set DURATION=60

echo RTSP URL: %RTSP_URL%
echo Output File: %OUTPUT_FILE%
echo Log File: %LOG_FILE%
echo Duration: %DURATION% seconds
echo.
echo ========================================

REM 检查FFmpeg是否存在
echo Step 1: Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] FFmpeg not found! Please install FFmpeg first.
    echo Download from: https://ffmpeg.org/download.html
    pause
    exit /b 1
)
echo [OK] FFmpeg is installed
echo.

REM 测试RTSP连接
echo Step 2: Testing RTSP connection...
echo Testing connection to camera...
ffmpeg -rtsp_transport tcp -i %RTSP_URL% -t 1 -f null - > nul 2>&1
if errorlevel 1 (
    echo [WARNING] RTSP connection test failed
    echo This might be normal - continuing with recording test...
) else (
    echo [OK] RTSP connection test passed
)
echo.

REM 开始录制测试
echo Step 3: Starting recording test (%DURATION% seconds)...
echo This will take %DURATION% seconds. Please wait...
echo All output will be saved to: %LOG_FILE%
echo.

ffmpeg -v verbose -rtsp_transport tcp -timeout 10000000 -analyzeduration 10000000 -probesize 10000000 -i %RTSP_URL% -c:v copy -c:a copy -t %DURATION% -err_detect ignore_err -max_error_rate 0.5 -movflags +faststart+frag_keyframe+empty_moov -y %OUTPUT_FILE% > %LOG_FILE% 2>&1

REM 检查结果
echo.
echo ========================================
echo Test Complete!
echo ========================================

if exist %OUTPUT_FILE% (
    echo [OK] Output file created: %OUTPUT_FILE%
    for %%A in (%OUTPUT_FILE%) do (
        echo File size: %%~zA bytes
        if %%~zA LSS 1024 (
            echo [WARNING] File size is very small - recording may have failed
        ) else (
            echo [OK] File size looks reasonable
        )
    )
) else (
    echo [ERROR] Output file was not created!
)

echo.
echo Log file saved to: %LOG_FILE%
echo.
echo Please check:
echo 1. Video file: %OUTPUT_FILE%
echo 2. Log file: %LOG_FILE%
echo.

REM 显示日志文件的最后几行
echo Last 20 lines of log:
echo ========================================
powershell -Command "Get-Content '%LOG_FILE%' -Tail 20"
echo ========================================

pause
