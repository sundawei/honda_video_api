"""
全API接口测试脚本
测试所有的REST API端点
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
BASE_URL = "http://127.0.0.1:9999/api"

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(method, endpoint, response, request_data=None):
    """打印API调用结果"""
    print(f"\n【{method}】 {endpoint}")
    if request_data:
        print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    print(f"状态码: {response.status_code}")
    try:
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except:
        print(f"响应 (非JSON): {response.text[:200]}")
        return None

def test_get_cameras():
    """测试1: 获取相机列表"""
    print_section("测试1: GET /api/cameras - 获取相机列表")
    response = requests.get(f"{BASE_URL}/cameras")
    return print_result("GET", "/api/cameras", response)

def test_get_status():
    """测试2: 获取录制状态"""
    print_section("测试2: GET /api/status - 获取所有相机录制状态")
    response = requests.get(f"{BASE_URL}/status")
    return print_result("GET", "/api/status", response)

def test_get_recordings(camera_id):
    """测试3: 获取录像文件列表"""
    print_section(f"测试3: GET /api/recordings/{camera_id} - 获取录像文件列表")
    response = requests.get(f"{BASE_URL}/recordings/{camera_id}")
    return print_result("GET", f"/api/recordings/{camera_id}", response)

def test_stop_recording(camera_id):
    """测试4: 停止录制"""
    print_section(f"测试4: POST /api/recording/stop - 停止录制")
    data = {"camera_id": camera_id}
    response = requests.post(f"{BASE_URL}/recording/stop", json=data)
    return print_result("POST", "/api/recording/stop", response, data)

def test_start_recording(camera_id):
    """测试5: 开始录制"""
    print_section(f"测试5: POST /api/recording/start - 开始录制")
    data = {"camera_id": camera_id}
    response = requests.post(f"{BASE_URL}/recording/start", json=data)
    return print_result("POST", "/api/recording/start", response, data)

def test_add_camera():
    """测试6: 添加新相机"""
    print_section("测试6: POST /api/cameras - 添加新相机")
    data = {
        "id": "test_camera_02",
        "name": "测试相机02",
        "rtsp_url": "rtsp://admin:Admin1234@192.168.1.100:554/stream",
        "enabled": False
    }
    response = requests.post(f"{BASE_URL}/cameras", json=data)
    return print_result("POST", "/api/cameras", response, data)

def test_delete_camera(camera_id):
    """测试7: 删除相机"""
    print_section(f"测试7: DELETE /api/cameras/{camera_id} - 删除相机")
    response = requests.delete(f"{BASE_URL}/cameras/{camera_id}")
    return print_result("DELETE", f"/api/cameras/{camera_id}", response)

def test_get_settings():
    """测试8: 获取系统设置"""
    print_section("测试8: GET /api/settings - 获取系统设置")
    response = requests.get(f"{BASE_URL}/settings")
    return print_result("GET", "/api/settings", response)

def test_update_settings():
    """测试9: 更新系统设置"""
    print_section("测试9: POST /api/settings - 更新系统设置")
    data = {
        "recording": {
            "segment_duration": 120,  # 改为120秒
            "output_dir": "recordings",
            "enable_auto_delete": True,
            "retention_days": 14  # 改为14天
        },
        "ffmpeg": {
            "path": "ffmpeg"
        }
    }
    response = requests.post(f"{BASE_URL}/settings", json=data)
    result = print_result("POST", "/api/settings", response, data)

    # 恢复原设置
    if result and result.get("success"):
        print("\n⚠️  注意: 设置已更改，现在恢复原设置...")
        restore_data = {
            "recording": {
                "segment_duration": 60,
                "output_dir": "recordings",
                "enable_auto_delete": True,
                "retention_days": 7
            },
            "ffmpeg": {
                "path": "ffmpeg"
            }
        }
        restore_response = requests.post(f"{BASE_URL}/settings", json=restore_data)
        print("✅ 已恢复原设置")

    return result

def main():
    """主测试流程"""
    print("=" * 70)
    print("  IP相机录像系统 - API接口完整测试")
    print("  测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    try:
        # 测试1: 获取相机列表
        cameras_result = test_get_cameras()
        if not cameras_result or not cameras_result.get("success"):
            print("\n❌ 无法获取相机列表，测试终止")
            return

        cameras = cameras_result.get("cameras", [])
        if not cameras:
            print("\n⚠️  系统中没有相机，部分测试将跳过")
            main_camera_id = None
        else:
            main_camera_id = cameras[0]["id"]
            print(f"\n✅ 找到 {len(cameras)} 个相机，使用 {main_camera_id} 进行测试")

        # 测试2: 获取录制状态
        test_get_status()

        # 测试3: 获取录像文件列表（如果有相机）
        if main_camera_id:
            recordings_result = test_get_recordings(main_camera_id)
            if recordings_result and recordings_result.get("success"):
                files = recordings_result.get("files", [])
                print(f"\n📹 找到 {len(files)} 个录像文件")
                if files:
                    print(f"   最新文件: {files[-1].get('filename', 'N/A')}")

        # 测试8: 获取系统设置（放在前面，避免影响录制测试）
        test_get_settings()

        # 测试9: 更新系统设置
        test_update_settings()

        # 测试4-5: 停止和开始录制（如果有相机且正在录制）
        if main_camera_id:
            status_result = requests.get(f"{BASE_URL}/status").json()
            if status_result.get("success"):
                camera_status = status_result.get("cameras", {}).get(main_camera_id, {})
                is_recording = camera_status.get("is_recording", False)

                if is_recording:
                    print(f"\n📹 相机 {main_camera_id} 正在录制，测试停止录制...")
                    stop_result = test_stop_recording(main_camera_id)

                    if stop_result and stop_result.get("success"):
                        files = stop_result.get("files", [])
                        print(f"\n✅ 停止成功，返回了 {len(files)} 个录像文件")
                        if files:
                            total_size = sum(f.get("size", 0) for f in files)
                            print(f"   总大小: {total_size / 1024 / 1024:.2f} MB")

                    # 等待2秒
                    print("\n⏱️  等待2秒后重新开始录制...")
                    time.sleep(2)

                    # 重新开始录制
                    test_start_recording(main_camera_id)
                else:
                    print(f"\n📹 相机 {main_camera_id} 未在录制，直接测试开始录制...")
                    test_start_recording(main_camera_id)

                    print("\n⏱️  等待2秒后测试停止录制...")
                    time.sleep(2)
                    test_stop_recording(main_camera_id)

                    print("\n⏱️  重新开始录制...")
                    time.sleep(1)
                    test_start_recording(main_camera_id)

        # 测试6: 添加新相机
        add_result = test_add_camera()
        new_camera_id = None
        if add_result and add_result.get("success"):
            new_camera_id = "test_camera_02"
            print(f"\n✅ 成功添加测试相机: {new_camera_id}")

        # 测试7: 删除相机（删除刚才添加的测试相机）
        if new_camera_id:
            print("\n⏱️  等待1秒后删除测试相机...")
            time.sleep(1)
            delete_result = test_delete_camera(new_camera_id)
            if delete_result and delete_result.get("success"):
                print(f"\n✅ 成功删除测试相机: {new_camera_id}")

        # 最终状态检查
        print_section("测试完成 - 最终状态检查")
        final_cameras = test_get_cameras()
        final_status = test_get_status()

        print("\n" + "=" * 70)
        print("  ✅ 所有API测试完成！")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("   请确认服务器正在运行: python app.py")
        print("   服务地址: http://127.0.0.1:9999")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
