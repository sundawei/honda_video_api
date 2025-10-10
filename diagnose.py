"""
录像问题诊断脚本
"""
import os
import subprocess
from pathlib import Path

print("=" * 60)
print("IP Camera Recorder 诊断工具")
print("=" * 60)

# 1. 检查FFmpeg
print("\n1. 检查FFmpeg...")
try:
    result = subprocess.run(
        ["ffmpeg", "-version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        first_line = result.stdout.split('\n')[0]
        print(f"   ✓ FFmpeg已安装: {first_line}")
    else:
        print(f"   ✗ FFmpeg检查失败")
except FileNotFoundError:
    print("   ✗ FFmpeg未找到，请安装FFmpeg")
except Exception as e:
    print(f"   ✗ 错误: {e}")

# 2. 检查录像目录
print("\n2. 检查录像目录...")
recordings_dir = Path("recordings")
if recordings_dir.exists():
    print(f"   ✓ 录像目录存在: {recordings_dir.absolute()}")

    # 列出所有摄像机目录
    camera_dirs = [d for d in recordings_dir.iterdir() if d.is_dir() and d.name != "sessions"]
    print(f"   摄像机数量: {len(camera_dirs)}")

    for camera_dir in camera_dirs:
        print(f"\n   📁 摄像机: {camera_dir.name}")
        video_files = list(camera_dir.glob("*.mp4"))
        print(f"      录像文件数: {len(video_files)}")

        if video_files:
            print(f"      最新文件:")
            latest_file = max(video_files, key=lambda p: p.stat().st_mtime)
            file_size = latest_file.stat().st_size

            print(f"        - 文件名: {latest_file.name}")
            print(f"        - 大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
            print(f"        - 路径: {latest_file.absolute()}")

            # 3. 检查视频文件完整性
            print(f"\n   3. 检查视频文件完整性...")
            try:
                result = subprocess.run(
                    ["ffmpeg", "-v", "error", "-i", str(latest_file), "-f", "null", "-"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and not result.stderr:
                    print(f"      ✓ 视频文件完整，无错误")
                else:
                    print(f"      ⚠ 视频文件可能有问题:")
                    if result.stderr:
                        print(f"        {result.stderr[:200]}")
            except Exception as e:
                print(f"      ✗ 检查失败: {e}")

            # 4. 获取视频信息
            print(f"\n   4. 获取视频信息...")
            try:
                result = subprocess.run(
                    ["ffmpeg", "-i", str(latest_file)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # FFmpeg的信息在stderr中
                stderr = result.stderr

                # 提取关键信息
                for line in stderr.split('\n'):
                    if 'Duration:' in line:
                        print(f"      {line.strip()}")
                    elif 'Stream #0:0' in line or 'Stream #0:1' in line:
                        print(f"      {line.strip()}")

            except Exception as e:
                print(f"      ✗ 获取信息失败: {e}")

            # 5. 测试文件是否可播放
            print(f"\n   5. 测试文件可读性...")
            try:
                result = subprocess.run(
                    ["ffmpeg", "-i", str(latest_file), "-t", "1", "-f", "null", "-"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"      ✓ 文件可以正常读取和解码")
                else:
                    print(f"      ⚠ 文件读取有问题")

            except Exception as e:
                print(f"      ✗ 测试失败: {e}")
        else:
            print(f"      ⚠ 没有找到录像文件")
            print(f"      建议: 启动录像后等待至少1分钟")

else:
    print(f"   ✗ 录像目录不存在: {recordings_dir.absolute()}")

# 6. 检查日志
print("\n6. 检查日志...")
log_file = Path("logs/recorder.log")
if log_file.exists():
    print(f"   ✓ 日志文件存在")
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 显示最后20行错误或警告
    errors = [line for line in lines[-100:] if 'ERROR' in line or 'WARNING' in line]
    if errors:
        print(f"   最近的错误/警告 (最多显示5条):")
        for line in errors[-5:]:
            print(f"      {line.strip()}")
    else:
        print(f"   ✓ 没有发现错误或警告")
else:
    print(f"   ⚠ 日志文件不存在")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
print("\n如果发现问题，请提供以上信息以便进一步诊断。")
