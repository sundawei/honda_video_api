"""
查找可用端口
"""
import socket

def is_port_available(port):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False

# 测试一系列端口
ports_to_check = [8000, 8080, 8888, 9000, 9999, 5000, 5555, 7000, 7777, 3000]

print("查找可用端口...\n")
available_ports = []

for port in ports_to_check:
    if is_port_available(port):
        print(f"✓ 端口 {port} 可用")
        available_ports.append(port)
    else:
        print(f"✗ 端口 {port} 被占用")

if available_ports:
    print(f"\n推荐使用端口: {available_ports[0]}")
    print(f"\n请修改 config.yaml 中的端口为: {available_ports[0]}")
else:
    print("\n所有常用端口都被占用")
    # 尝试找一个10000以上的端口
    for port in range(10000, 10100):
        if is_port_available(port):
            print(f"找到可用端口: {port}")
            break
