@echo off
chcp 65001 >nul
echo 检查端口占用情况...
echo.

REM 检查8080端口
netstat -ano | findstr ":8080"
if errorlevel 1 (
    echo 端口 8080 空闲，可以使用
) else (
    echo 端口 8080 被占用，占用进程:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080"') do (
        echo 进程ID: %%a
        tasklist | findstr "%%a"
    )
)

echo.
pause
