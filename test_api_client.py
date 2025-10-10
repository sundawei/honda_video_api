#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IP Camera Recorder API 测试工具
用于测试API是否正常工作
"""

import requests
import json
from datetime import datetime, timedelta
import time

# API基础地址
BASE_URL = "http://127.0.0.1:9999"

def test_health():
    """测试健康检查"""
    print("📡 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("   请确认服务已启动: start_api.bat")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_cameras():
    """获取摄像机列表"""
    print("\n📹 获取摄像机列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/cameras")
        if response.status_code == 200:
            cameras = response.json()
            print(f"✅ 找到 {len(cameras)} 个摄像机:")
            for cam in cameras:
                status = "✓启用" if cam['enabled'] else "✗禁用"
                recording = "🔴录制中" if cam.get('is_recording') else "⚪未录制"
                print(f"   [{status}] {cam['id']}: {cam['name']} {recording}")
            return cameras
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []

def test_recording(camera_id):
    """测试录像功能"""
    print(f"\n🎬 测试录像功能 (摄像机: {camera_id})...")

    # 开始录像
    print("  1. 开始录像...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/recording/start",
            json={"camera_id": camera_id}
        )
        if response.status_code == 200:
            print("  ✅ 录像已开始")
        else:
            print(f"  ❌ 开始失败: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

    # 等待一段时间
    print("  2. 录制10秒测试视频...")
    for i in range(10, 0, -1):
        print(f"     {i}...", end="\r")
        time.sleep(1)
    print("     完成!    ")

    # 查询录像
    print("  3. 查询录像...")
    start_time = datetime.now() - timedelta(seconds=20)
    end_time = datetime.now()

    try:
        response = requests.post(
            f"{BASE_URL}/api/recording/query",
            json={
                "camera_id": camera_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        )
        if response.status_code == 200:
            result = response.json()
            files = result.get('files', [])
            if files:
                print(f"  ✅ 找到 {len(files)} 个录像文件:")
                for f in files:
                    size_mb = f.get('size', 0) / 1024 / 1024
                    print(f"     - {f.get('filename')} ({size_mb:.2f} MB)")
            else:
                print("  ⚠️ 未找到录像文件（可能还在处理中）")
        else:
            print(f"  ❌ 查询失败: {response.text}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")

    # 停止录像
    print("  4. 停止录像...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/recording/stop",
            json={"camera_id": camera_id}
        )
        if response.status_code == 200:
            result = response.json()
            print("  ✅ 录像已停止")
            if result.get('files'):
                print(f"     共录制 {result.get('total_files', 0)} 个文件")
        else:
            print(f"  ❌ 停止失败: {response.text}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")

    return True

def main():
    """主测试流程"""
    print("="*50)
    print("   IP Camera Recorder API 测试工具")
    print("="*50)

    # 1. 健康检查
    if not test_health():
        print("\n⚠️ API服务未启动，请先运行 start_api.bat")
        return

    # 2. 获取摄像机
    cameras = test_cameras()
    if not cameras:
        print("\n⚠️ 没有配置摄像机，请编辑 config.yaml")
        return

    # 找到启用的摄像机
    enabled_cameras = [c for c in cameras if c['enabled']]
    if not enabled_cameras:
        print("\n⚠️ 没有启用的摄像机")
        return

    # 3. 询问是否测试录像
    print("\n" + "="*50)
    test_cam = enabled_cameras[0]
    choice = input(f"是否测试录像功能？将使用摄像机 [{test_cam['id']}] (Y/N): ")

    if choice.upper() == 'Y':
        test_recording(test_cam['id'])

    print("\n" + "="*50)
    print("✅ 测试完成！")
    print("\n提示:")
    print("- API文档: http://127.0.0.1:9999/docs")
    print("- 录像文件: recordings/")
    print("- 日志文件: logs/app.log")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

    input("\n按回车键退出...")