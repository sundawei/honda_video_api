@echo off
title 打包依赖
echo ========================================
echo     简化版依赖打包工具
echo ========================================
echo.

REM 创建libs目录
if not exist libs mkdir libs

echo 正在安装依赖包到libs目录...
echo.

REM 使用pip安装依赖到libs目录
python -m pip install --target libs --upgrade fastapi==0.104.1
python -m pip install --target libs --upgrade uvicorn[standard]==0.24.0
python -m pip install --target libs --upgrade jinja2==3.1.2
python -m pip install --target libs --upgrade python-multipart==0.0.6
python -m pip install --target libs --upgrade pyyaml==6.0.1
python -m pip install --target libs --upgrade python-dateutil==2.8.2

echo.
echo 打包完成！
echo.
echo 提示：
echo - 依赖已安装到 libs 文件夹
echo - 使用 start_api.bat 启动服务
echo.
pause