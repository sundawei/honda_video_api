"""
API测试脚本
用于测试系统功能
"""

import requests
import time
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"


def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    response = requests.get(f"{API_BASE}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_system_status():
    """测试系统状态"""
    print("\n=== 测试系统状态 ===")
    response = requests.get(f"{API_BASE}/status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_list_cameras():
    """测试列出摄像机"""
    print("\n=== 测试列出摄像机 ===")
    response = requests.get(f"{API_BASE}/cameras")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"摄像机数量: {len(data.get('cameras', []))}")
    for camera in data.get('cameras', []):
        print(f"  - {camera['id']}: {camera['name']} (录像中: {camera['is_recording']})")


def test_add_camera(camera_id, name, rtsp_url):
    """测试添加摄像机"""
    print(f"\n=== 测试添加摄像机 {camera_id} ===")
    response = requests.post(f"{API_BASE}/cameras", json={
        "id": camera_id,
        "name": name,
        "rtsp_url": rtsp_url,
        "enabled": True
    })
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def test_start_recording(camera_id):
    """测试开始录像"""
    print(f"\n=== 测试开始录像 {camera_id} ===")
    response = requests.post(f"{API_BASE}/recording/start", json={
        "camera_id": camera_id
    })
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def test_recording_status(camera_id):
    """测试录像状态"""
    print(f"\n=== 测试录像状态 {camera_id} ===")
    response = requests.get(f"{API_BASE}/recording/status/{camera_id}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_stop_recording(camera_id):
    """测试停止录像"""
    print(f"\n=== 测试停止录像 {camera_id} ===")
    response = requests.post(f"{API_BASE}/recording/stop", json={
        "camera_id": camera_id
    })
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200


def test_query_recordings(camera_id, start_time, end_time):
    """测试查询录像"""
    print(f"\n=== 测试查询录像 {camera_id} ===")
    print(f"时间范围: {start_time} 到 {end_time}")
    response = requests.post(f"{API_BASE}/recording/query", json={
        "camera_id": camera_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    })
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data.get('success'):
        result = data.get('result', {})
        files = result.get('files', [])
        print(f"找到 {len(files)} 个文件")
        for file_info in files:
            print(f"  - {file_info['filename']}: {file_info['size']/1024/1024:.2f}MB")
            print(f"    路径: {file_info['path']}")
    else:
        print(f"查询失败: {data}")


def test_delete_camera(camera_id):
    """测试删除摄像机"""
    print(f"\n=== 测试删除摄像机 {camera_id} ===")
    response = requests.delete(f"{API_BASE}/cameras/{camera_id}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def run_full_test():
    """运行完整测试流程"""
    print("=" * 60)
    print("开始API完整测试")
    print("=" * 60)

    # 1. 健康检查
    test_health()

    # 2. 系统状态
    test_system_status()

    # 3. 列出摄像机
    test_list_cameras()

    # 4. 添加测试摄像机（注意：需要修改为实际的RTSP地址进行测试）
    test_camera_id = "test_camera_01"
    test_rtsp_url = "rtsp://admin:password@192.168.1.100:554/stream1"  # 修改为实际地址

    print("\n注意：测试将使用模拟的RTSP地址，实际测试请修改test_rtsp_url变量")

    # 如果要跳过需要实际摄像机的测试，取消下面的return
    # return

    if test_add_camera(test_camera_id, "测试摄像机", test_rtsp_url):

        # 5. 查看添加后的摄像机列表
        test_list_cameras()

        # 6. 开始录像
        if test_start_recording(test_camera_id):

            # 7. 检查录像状态
            test_recording_status(test_camera_id)

            # 8. 等待一段时间（让它录像）
            print("\n等待30秒以进行录像...")
            time.sleep(30)

            # 9. 停止录像
            test_stop_recording(test_camera_id)

            # 10. 查询录像
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=5)
            test_query_recordings(test_camera_id, start_time, end_time)

        # 11. 删除测试摄像机
        test_delete_camera(test_camera_id)

        # 12. 最终状态
        test_list_cameras()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 运行完整测试
    run_full_test()

    # 或者单独运行某个测试
    # test_health()
    # test_system_status()
    # test_list_cameras()
