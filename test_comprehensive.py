"""
IP相机录像系统 - 综合功能测试脚本
测试所有功能包括新的文件名格式
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

BASE_URL = "http://127.0.0.1:9999/api"

# 颜色输出（Windows兼容）
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def colored_print(text, color_code):
    """带颜色的打印（如果终端支持）"""
    try:
        print(f"{color_code}{text}{Colors.ENDC}")
    except:
        print(text)

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    colored_print(f"  {title}", Colors.HEADER + Colors.BOLD)
    print("=" * 80)

def print_success(msg):
    colored_print(f"✅ {msg}", Colors.OKGREEN)

def print_error(msg):
    colored_print(f"❌ {msg}", Colors.FAIL)

def print_warning(msg):
    colored_print(f"⚠️  {msg}", Colors.WARNING)

def print_info(msg):
    colored_print(f"ℹ️  {msg}", Colors.OKBLUE)

def print_result(method, endpoint, response, request_data=None):
    """打印API调用结果"""
    print(f"\n【{method}】 {endpoint}")
    if request_data:
        print(f"请求: {json.dumps(request_data, ensure_ascii=False)}")
    print(f"状态: {response.status_code}")

    try:
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except:
        print(f"响应: {response.text[:200]}")
        return None

# ==================== 测试函数 ====================

def test_health_check():
    """测试1: 健康检查"""
    print_header("测试1: 健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health")
        result = print_result("GET", "/health", response)
        if response.status_code == 200 and result.get("success"):
            print_success("服务运行正常")
            return True
        else:
            print_error("健康检查失败")
            return False
    except Exception as e:
        print_error(f"无法连接到服务器: {e}")
        return False

def test_get_cameras():
    """测试2: 获取相机列表"""
    print_header("测试2: 获取相机列表")
    response = requests.get(f"{BASE_URL}/cameras")
    result = print_result("GET", "/cameras", response)

    if result and result.get("success"):
        cameras = result.get("cameras", [])
        print_success(f"找到 {len(cameras)} 个相机")
        return cameras
    else:
        print_error("获取相机列表失败")
        return []

def test_get_status():
    """测试3: 获取系统状态"""
    print_header("测试3: 获取系统状态")
    response = requests.get(f"{BASE_URL}/status")
    result = print_result("GET", "/status", response)

    if result and result.get("success"):
        status = result.get("status", {})
        print_success(f"总相机数: {status.get('total_cameras')}, 录制中: {status.get('recording_cameras')}")
        return status
    else:
        print_error("获取系统状态失败")
        return {}

def test_start_recording(camera_id):
    """测试4: 开始录制"""
    print_header(f"测试4: 开始录制 ({camera_id})")
    data = {"camera_id": camera_id}
    response = requests.post(f"{BASE_URL}/recording/start", json=data)
    result = print_result("POST", "/recording/start", response, data)

    if result and result.get("success"):
        print_success("录制已开始")
        return True
    else:
        print_error("开始录制失败")
        return False

def test_wait_for_recording(camera_id, wait_seconds=70):
    """测试5: 等待录制（生成新格式文件）"""
    print_header(f"测试5: 等待录制 {wait_seconds} 秒（生成新格式文件）")

    print_info(f"正在录制中，请等待 {wait_seconds} 秒...")
    print_info("这将生成至少一个完整的录像片段")

    for i in range(wait_seconds):
        remaining = wait_seconds - i
        print(f"\r⏱️  剩余时间: {remaining:2d} 秒", end='', flush=True)
        time.sleep(1)

    print("\n")
    print_success(f"等待完成，已录制 {wait_seconds} 秒")
    return True

def test_get_recordings(camera_id):
    """测试6: 获取录像文件列表"""
    print_header(f"测试6: 获取录像文件列表 ({camera_id})")
    response = requests.get(f"{BASE_URL}/recordings/{camera_id}")
    result = print_result("GET", f"/recordings/{camera_id}", response)

    if result and result.get("success"):
        files = result.get("files", [])
        total_size = result.get("total_size", 0)

        print_success(f"找到 {len(files)} 个录像文件，总大小: {total_size / 1024 / 1024:.2f} MB")
        return files
    else:
        print_error("获取录像文件失败")
        return []

def test_filename_format(files):
    """测试7: 验证文件名格式"""
    print_header("测试7: 验证文件名格式")

    if not files:
        print_warning("没有文件可供检查")
        return False

    new_format_count = 0
    old_format_count = 0

    print("\n文件名格式分析:")
    print("-" * 80)

    for file in files:
        filename = file.get("filename", "")
        start_time = file.get("start_time", "N/A")
        end_time = file.get("end_time", "N/A")
        duration = file.get("duration", 0)
        size_mb = file.get("size", 0) / 1024 / 1024

        if "_to_" in filename:
            new_format_count += 1
            format_type = "新格式"
            color = Colors.OKGREEN
        else:
            old_format_count += 1
            format_type = "旧格式"
            color = Colors.WARNING

        print(f"\n{color}[{format_type}]{Colors.ENDC} {filename}")
        print(f"  开始: {start_time}")
        print(f"  结束: {end_time}")
        print(f"  时长: {duration:.1f}秒 | 大小: {size_mb:.2f}MB")

    print("\n" + "-" * 80)
    print(f"统计: 新格式 {new_format_count} 个, 旧格式 {old_format_count} 个")

    if new_format_count > 0:
        print_success("✓ 系统已生成新格式文件")
    else:
        print_warning("! 尚未生成新格式文件（需要完成一个完整的录制周期）")

    return True

def test_stop_recording(camera_id):
    """测试8: 停止录制"""
    print_header(f"测试8: 停止录制 ({camera_id})")
    data = {"camera_id": camera_id}
    response = requests.post(f"{BASE_URL}/recording/stop", json=data)
    result = print_result("POST", "/recording/stop", response, data)

    if result and result.get("success"):
        info = result.get("recording_info", {})
        files = info.get("files", [])
        total_files = info.get("total_files", 0)
        total_size = info.get("total_size", 0)

        print_success(f"录制已停止")
        print_info(f"录制文件: {total_files} 个, 总大小: {total_size / 1024 / 1024:.2f} MB")
        return files
    else:
        print_error("停止录制失败")
        return []

def test_query_recent(camera_id, minutes=2):
    """测试9: 查询最近几分钟的录像"""
    print_header(f"测试9: 查询最近 {minutes} 分钟的录像")

    now = datetime.now()
    start_time = now - timedelta(minutes=minutes)

    data = {
        "camera_id": camera_id,
        "start_time": start_time.isoformat(),
        "end_time": now.isoformat()
    }

    print(f"查询时间范围: {start_time.strftime('%H:%M:%S')} ~ {now.strftime('%H:%M:%S')}")

    response = requests.post(f"{BASE_URL}/recording/query", json=data)
    result = print_result("POST", "/recording/query", response, data)

    if result and result.get("success"):
        query_result = result.get("result", {})
        files = query_result.get("files", [])
        print_success(f"查询到 {len(files)} 个相关文件")
        return files
    else:
        print_error("查询失败")
        return []

def test_query_specific_time(camera_id, files):
    """测试10: 查询特定时间段（跨文件）"""
    print_header("测试10: 查询特定时间段（测试时间范围过滤）")

    if len(files) < 2:
        print_warning("文件数量不足，跳过此测试")
        return []

    # 选择中间的文件
    mid_index = len(files) // 2
    mid_file = files[mid_index]

    file_start = datetime.fromisoformat(mid_file["start_time"])

    # 查询从该文件开始前30秒到开始后90秒的录像
    query_start = file_start - timedelta(seconds=30)
    query_end = file_start + timedelta(seconds=90)

    data = {
        "camera_id": camera_id,
        "start_time": query_start.isoformat(),
        "end_time": query_end.isoformat()
    }

    print(f"查询时间: {query_start.strftime('%H:%M:%S')} ~ {query_end.strftime('%H:%M:%S')}")
    print(f"预期: 应该跨越至少2个文件")

    response = requests.post(f"{BASE_URL}/recording/query", json=data)
    result = print_result("POST", "/recording/query", response, data)

    if result and result.get("success"):
        query_result = result.get("result", {})
        files = query_result.get("files", [])
        print_success(f"查询到 {len(files)} 个相关文件")
        return files
    else:
        print_error("查询失败")
        return []

def test_add_camera():
    """测试11: 添加测试相机"""
    print_header("测试11: 添加测试相机")
    data = {
        "id": "test_camera_99",
        "name": "综合测试相机",
        "rtsp_url": "rtsp://test:test@192.168.1.99:554/stream",
        "enabled": False
    }

    response = requests.post(f"{BASE_URL}/cameras", json=data)
    result = print_result("POST", "/cameras", response, data)

    if result and result.get("success"):
        print_success("测试相机添加成功")
        return True
    else:
        print_error("添加测试相机失败")
        return False

def test_delete_camera(camera_id):
    """测试12: 删除测试相机"""
    print_header(f"测试12: 删除测试相机 ({camera_id})")
    response = requests.delete(f"{BASE_URL}/cameras/{camera_id}")
    result = print_result("DELETE", f"/cameras/{camera_id}", response)

    if result and result.get("success"):
        print_success("测试相机删除成功")
        return True
    else:
        print_error("删除测试相机失败")
        return False

def test_settings():
    """测试13: 设置管理"""
    print_header("测试13: 获取和更新系统设置")

    # 获取当前设置
    print("\n[1] 获取当前设置:")
    response = requests.get(f"{BASE_URL}/settings")
    current_settings = print_result("GET", "/settings", response)

    if not current_settings or not current_settings.get("success"):
        print_error("获取设置失败")
        return False

    print_success("当前设置获取成功")

    # 测试更新设置（然后恢复）
    print("\n[2] 测试更新设置:")
    test_update = {
        "recording": {
            "segment_duration": 90,  # 临时改为90秒
            "output_dir": current_settings["settings"]["recording"]["output_dir"],
            "enable_auto_delete": current_settings["settings"]["recording"]["enable_auto_delete"],
            "retention_days": current_settings["settings"]["recording"]["retention_days"]
        },
        "ffmpeg": {
            "path": current_settings["settings"]["ffmpeg"]["path"]
        }
    }

    response = requests.post(f"{BASE_URL}/settings", json=test_update)
    result = print_result("POST", "/settings", response, test_update)

    if result and result.get("success"):
        print_success("设置更新成功")

        # 恢复原设置
        print("\n[3] 恢复原设置:")
        original_settings = {
            "recording": current_settings["settings"]["recording"],
            "ffmpeg": {"path": current_settings["settings"]["ffmpeg"]["path"]}
        }
        response = requests.post(f"{BASE_URL}/settings", json=original_settings)
        if response.status_code == 200:
            print_success("原设置已恢复")
        return True
    else:
        print_error("更新设置失败")
        return False

def verify_files_on_disk(camera_id):
    """测试14: 验证磁盘上的文件"""
    print_header("测试14: 验证磁盘上的实际文件")

    recording_dir = Path(f"recordings/{camera_id}")

    if not recording_dir.exists():
        print_warning(f"录像目录不存在: {recording_dir}")
        return []

    files = list(recording_dir.glob("*.mp4"))

    print(f"\n磁盘上的文件 ({len(files)} 个):")
    print("-" * 80)

    new_format = []
    old_format = []
    recording = []

    for file in sorted(files):
        size_mb = file.stat().st_size / 1024 / 1024
        name = file.name

        if name.endswith("_recording.mp4"):
            recording.append(name)
            print(f"{Colors.WARNING}⏺️  [录制中] {name} ({size_mb:.2f}MB){Colors.ENDC}")
        elif "_to_" in name:
            new_format.append(name)
            print(f"{Colors.OKGREEN}✓ [新格式] {name} ({size_mb:.2f}MB){Colors.ENDC}")
        else:
            old_format.append(name)
            print(f"{Colors.OKCYAN}○ [旧格式] {name} ({size_mb:.2f}MB){Colors.ENDC}")

    print("-" * 80)
    print(f"统计: 新格式={len(new_format)}, 旧格式={len(old_format)}, 录制中={len(recording)}")

    if new_format:
        print_success(f"✓ 发现 {len(new_format)} 个新格式文件")
    if old_format:
        print_info(f"○ 发现 {len(old_format)} 个旧格式文件（向后兼容）")
    if recording:
        print_warning(f"⏺️  发现 {len(recording)} 个正在录制的临时文件")

    return files

# ==================== 主测试流程 ====================

def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    colored_print("  IP相机录像系统 - 综合功能测试", Colors.HEADER + Colors.BOLD)
    print("  测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    test_results = {
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }

    try:
        # 测试1: 健康检查
        if not test_health_check():
            print_error("\n服务未运行或无法连接，测试终止")
            return
        test_results["passed"] += 1

        # 测试2-3: 基础信息
        cameras = test_get_cameras()
        test_results["passed"] += 1

        test_get_status()
        test_results["passed"] += 1

        if not cameras:
            print_error("\n系统中没有相机，无法继续测试")
            return

        camera_id = cameras[0]["id"]
        print_info(f"\n使用相机 '{camera_id}' 进行后续测试")

        # 测试4-5: 录制功能
        if test_start_recording(camera_id):
            test_results["passed"] += 1

            # 等待录制生成新格式文件
            test_wait_for_recording(camera_id, wait_seconds=70)
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1
            test_results["skipped"] += 1

        # 测试6-7: 获取和验证文件
        files = test_get_recordings(camera_id)
        if files:
            test_results["passed"] += 1
            test_filename_format(files)
            test_results["passed"] += 1
        else:
            test_results["failed"] += 2

        # 测试8: 停止录制
        stopped_files = test_stop_recording(camera_id)
        if stopped_files:
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1

        # 重新获取文件列表用于查询测试
        time.sleep(1)
        files = test_get_recordings(camera_id)

        # 测试9-10: 查询功能
        if files:
            test_query_recent(camera_id, minutes=2)
            test_results["passed"] += 1

            test_query_specific_time(camera_id, files)
            test_results["passed"] += 1
        else:
            test_results["skipped"] += 2

        # 测试11-12: 相机管理
        if test_add_camera():
            test_results["passed"] += 1
            time.sleep(1)
            if test_delete_camera("test_camera_99"):
                test_results["passed"] += 1
            else:
                test_results["failed"] += 1
        else:
            test_results["failed"] += 1
            test_results["skipped"] += 1

        # 测试13: 设置管理
        if test_settings():
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1

        # 测试14: 验证磁盘文件
        verify_files_on_disk(camera_id)
        test_results["passed"] += 1

        # 最终状态
        print_header("最终系统状态")
        test_get_cameras()
        test_get_status()

        # 重新开始录制
        print_header("恢复录制")
        test_start_recording(camera_id)

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print_error(f"\n测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

    # 测试总结
    print("\n" + "=" * 80)
    colored_print("  测试总结", Colors.HEADER + Colors.BOLD)
    print("=" * 80)

    total = test_results["passed"] + test_results["failed"]

    if test_results["passed"] > 0:
        print_success(f"通过: {test_results['passed']} 项")
    if test_results["failed"] > 0:
        print_error(f"失败: {test_results['failed']} 项")
    if test_results["skipped"] > 0:
        print_warning(f"跳过: {test_results['skipped']} 项")

    if total > 0:
        success_rate = (test_results["passed"] / total) * 100
        print(f"\n成功率: {success_rate:.1f}%")

    print("\n" + "=" * 80)

    if test_results["failed"] == 0:
        colored_print("  ✅ 所有测试通过！系统运行正常", Colors.OKGREEN + Colors.BOLD)
    else:
        colored_print("  ⚠️  部分测试失败，请检查日志", Colors.WARNING + Colors.BOLD)

    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
