@echo off
title IP Camera Recorder API (Portable)
echo ========================================
echo   IP Camera Recorder API (便携版)
echo ========================================
echo.

REM 设置当前目录为工作目录
cd /d "%~dp0"

REM 添加libs到Python路径
set PYTHONPATH=%~dp0libs;%PYTHONPATH%

REM 使用系统Python或指定Python路径
set PYTHON_EXE=python

REM 如果有便携式Python，使用它
if exist "python_portable\python.exe" (
    set PYTHON_EXE=python_portable\python.exe
    echo 使用便携式Python
)

echo 正在启动API服务器...
echo 服务地址: http://127.0.0.1:9999
echo 按 Ctrl+C 停止服务
echo.

"%PYTHON_EXE%" app.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 服务启动失败
    echo 可能原因:
    echo 1. Python未安装或版本过低（需要3.7+）
    echo 2. 依赖包未正确安装
    pause
)
