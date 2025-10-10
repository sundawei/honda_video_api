"""
测试 POST /api/recording/query 接口
查询指定时间段的录像
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:9999/api"

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_query_recordings(camera_id, start_time, end_time):
    """测试查询录像接口"""
    print_section(f"测试 POST /api/recording/query")

    data = {
        "camera_id": camera_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }

    print(f"\n请求参数:")
    print(f"  相机ID: {camera_id}")
    print(f"  开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  查询时长: {(end_time - start_time).total_seconds() / 60:.1f} 分钟")

    try:
        response = requests.post(f"{BASE_URL}/recording/query", json=data)
        print(f"\n状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

            if result.get("success"):
                query_result = result.get("result", {})
                files = query_result.get("files", [])

                print("\n" + "-" * 70)
                print(f"✅ 查询成功！")
                print(f"找到 {len(files)} 个相关录像文件")

                if files:
                    total_size = sum(f.get("size", 0) for f in files)
                    print(f"总大小: {total_size / 1024 / 1024:.2f} MB")

                    print("\n文件列表:")
                    for i, file_info in enumerate(files, 1):
                        filename = file_info.get("filename", "unknown")
                        size = file_info.get("size", 0) / 1024 / 1024
                        start = file_info.get("start_time", "unknown")
                        print(f"  {i}. {filename}")
                        print(f"     大小: {size:.2f} MB | 开始时间: {start}")
                else:
                    print("⚠️  指定时间段内没有录像")
                print("-" * 70)

            return result
        else:
            print(f"❌ 请求失败: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主测试流程"""
    print("=" * 70)
    print("  查询录像接口测试 (POST /api/recording/query)")
    print("  测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    try:
        # 获取相机列表
        print("\n正在获取相机列表...")
        response = requests.get(f"{BASE_URL}/cameras")
        if response.status_code != 200:
            print("❌ 无法获取相机列表")
            return

        cameras_data = response.json()
        cameras = cameras_data.get("cameras", [])

        if not cameras:
            print("❌ 系统中没有相机")
            return

        camera_id = cameras[0]["id"]
        print(f"✅ 使用相机: {camera_id}")

        # 获取现有录像文件以确定时间范围
        print(f"\n正在获取相机 {camera_id} 的录像文件...")
        response = requests.get(f"{BASE_URL}/recordings/{camera_id}")

        if response.status_code != 200:
            print("❌ 无法获取录像文件列表")
            return

        recordings_data = response.json()
        files = recordings_data.get("files", [])

        if not files:
            print("❌ 没有找到录像文件，无法进行query测试")
            print("建议：先录制几分钟后再测试query接口")
            return

        print(f"✅ 找到 {len(files)} 个录像文件")

        # 显示文件时间范围
        first_file = files[0]
        last_file = files[-1]
        first_time = datetime.fromisoformat(first_file["start_time"])
        last_time = datetime.fromisoformat(last_file["start_time"])

        print(f"\n录像时间范围:")
        print(f"  最早: {first_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  最晚: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 测试场景1: 查询最近2分钟的录像
        print_section("测试场景1: 查询最近2分钟的录像")
        now = datetime.now()
        start_time_1 = now - timedelta(minutes=2)
        end_time_1 = now
        test_query_recordings(camera_id, start_time_1, end_time_1)

        # 测试场景2: 查询最近5分钟的录像
        print_section("测试场景2: 查询最近5分钟的录像")
        start_time_2 = now - timedelta(minutes=5)
        end_time_2 = now
        test_query_recordings(camera_id, start_time_2, end_time_2)

        # 测试场景3: 查询所有录像（从最早文件到现在）
        print_section("测试场景3: 查询所有录像")
        test_query_recordings(camera_id, first_time, now)

        # 测试场景4: 查询特定时间段（如果有多个文件）
        if len(files) >= 3:
            print_section("测试场景4: 查询中间时间段的录像")
            mid_file = files[len(files) // 2]
            mid_time = datetime.fromisoformat(mid_file["start_time"])
            start_time_4 = mid_time - timedelta(seconds=30)
            end_time_4 = mid_time + timedelta(seconds=90)
            test_query_recordings(camera_id, start_time_4, end_time_4)

        # 测试场景5: 查询不存在的时间段
        print_section("测试场景5: 查询未来时间（应该返回空）")
        future_start = now + timedelta(hours=1)
        future_end = now + timedelta(hours=2)
        test_query_recordings(camera_id, future_start, future_end)

        print("\n" + "=" * 70)
        print("  ✅ Query接口测试完成！")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("   请确认服务器正在运行: python app.py")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
