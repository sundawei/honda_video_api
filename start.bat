@echo off
chcp 65001 >nul
echo ================================
echo IP Camera Recorder 启动脚本
echo ================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查FFmpeg
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo 警告: 未找到FFmpeg，请确保已安装并添加到PATH
    echo 或在config.yaml中配置FFmpeg路径
    echo.
    pause
)

echo 正在启动服务器...
echo 访问地址: http://127.0.0.1:9999
echo 按 Ctrl+C 停止服务器
echo.

python app.py

pause
