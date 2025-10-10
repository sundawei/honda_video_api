"""
快速测试API是否正常工作
"""
import requests
import time

API_BASE = "http://127.0.0.1:9999/api"

print("测试API连接...")

# 等待服务器启动
time.sleep(1)

try:
    # 测试健康检查
    print("\n1. 测试健康检查...")
    response = requests.get(f"{API_BASE}/health", timeout=5)
    print(f"   状态: {response.status_code}")
    print(f"   响应: {response.json()}")

    # 测试系统状态
    print("\n2. 测试系统状态...")
    response = requests.get(f"{API_BASE}/status", timeout=5)
    print(f"   状态: {response.status_code}")
    print(f"   响应: {response.json()}")

    # 测试摄像机列表
    print("\n3. 测试摄像机列表...")
    response = requests.get(f"{API_BASE}/cameras", timeout=5)
    print(f"   状态: {response.status_code}")
    print(f"   响应: {response.json()}")

    print("\n✅ 所有测试通过！服务器运行正常。")
    print("请访问: http://127.0.0.1:9999")

except requests.exceptions.ConnectionError:
    print("\n❌ 无法连接到服务器")
    print("请确保运行了: python app.py")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
