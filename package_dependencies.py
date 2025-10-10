"""
便携式Python依赖打包脚本
将所有依赖包安装到本地libs文件夹，实现免安装运行
"""

import subprocess
import sys
import os
from pathlib import Path

def package_dependencies():
    """将所有依赖打包到本地libs文件夹"""

    # 创建libs目录
    libs_dir = Path("libs")
    libs_dir.mkdir(exist_ok=True)

    print("正在安装依赖包到本地libs文件夹...")

    # 使用pip install将包安装到指定目录
    cmd = [
        sys.executable, "-m", "pip", "install",
        "-r", "requirements.txt",
        "--target", str(libs_dir),
        "--upgrade"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 依赖包安装成功！")
            print(f"  包已安装到: {libs_dir.absolute()}")

            # 统计安装的包
            package_count = len(list(libs_dir.glob("*")))
            print(f"  共安装 {package_count} 个包")

            # 创建启动脚本
            create_start_scripts()

        else:
            print("✗ 安装失败:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"✗ 发生错误: {e}")
        return False

    return True

def create_start_scripts():
    """创建Windows启动脚本"""

    # 创建Windows批处理文件
    bat_content = """@echo off
title IP Camera Recorder API
echo ========================================
echo     IP Camera Recorder API Server
echo ========================================
echo.

REM 设置Python路径包含libs目录
set PYTHONPATH=%~dp0libs;%PYTHONPATH%

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查FFmpeg是否安装
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未找到FFmpeg，录像功能将无法使用
    echo 请下载FFmpeg并添加到系统PATH
    echo 下载地址: https://ffmpeg.org/download.html
    echo.
)

echo 正在启动API服务器...
echo 服务地址: http://127.0.0.1:9999
echo 按 Ctrl+C 停止服务
echo.

REM 启动API服务
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 服务启动失败
    pause
)
"""

    with open("start_api.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)

    print("✓ 已创建启动脚本: start_api.bat")

    # 创建便携式启动器（使用内置Python）
    portable_bat = r"""@echo off
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
"""

    with open("start_api_portable.bat", "w", encoding="utf-8") as f:
        f.write(portable_bat)

    print("✓ 已创建便携式启动脚本: start_api_portable.bat")

def create_app_wrapper():
    """修改app.py使其能够使用本地libs"""

    app_wrapper = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IP Camera Recorder API - 便携版启动器
自动加载本地libs目录的依赖包
"""

import sys
import os
from pathlib import Path

# 添加libs目录到Python路径
libs_dir = Path(__file__).parent / "libs"
if libs_dir.exists():
    sys.path.insert(0, str(libs_dir))
    print(f"[INFO] 使用本地依赖包: {libs_dir}")

# 导入并运行原始app
if __name__ == "__main__":
    # 导入原始app模块
    import app

    # app.py中的主函数会自动运行
'''

    # 备份原始app.py
    if Path("app.py").exists() and not Path("app_original.py").exists():
        import shutil
        shutil.copy("app.py", "app_original.py")
        print("✓ 已备份原始app.py为app_original.py")

    # 检查app.py是否已经有libs导入逻辑
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    if "libs_dir = Path" not in content:
        # 在文件开头插入libs导入逻辑
        insert_code = '''# 便携版支持：自动加载本地libs目录
import sys
from pathlib import Path
libs_dir = Path(__file__).parent / "libs"
if libs_dir.exists():
    sys.path.insert(0, str(libs_dir))

'''
        # 找到第一个import语句的位置
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                insert_pos = i
                break

        # 插入代码
        lines.insert(insert_pos, insert_code)
        new_content = '\n'.join(lines)

        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✓ 已更新app.py以支持本地libs")

if __name__ == "__main__":
    print("="*50)
    print("  IP Camera Recorder - 依赖打包工具")
    print("="*50)
    print()

    # 打包依赖
    if package_dependencies():
        create_app_wrapper()
        print()
        print("✅ 打包完成！")
        print()
        print("使用方法:")
        print("1. 双击运行 start_api.bat 启动服务")
        print("2. 或在命令行运行: python app.py")
        print()
        print("打包内容:")
        print("- libs/        : 所有Python依赖包")
        print("- start_api.bat: Windows启动脚本")
        print()
        print("分发时需要包含:")
        print("- 整个recoder文件夹")
        print("- 确保目标机器安装了Python 3.7+")
        print("- 确保目标机器安装了FFmpeg（用于录像）")
    else:
        print()
        print("❌ 打包失败，请检查错误信息")