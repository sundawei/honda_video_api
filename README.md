# IP Camera Recorder

一个功能强大的IP摄像机录像管理系统，支持多摄像机同时录像、时间段录像提取、自动清理等功能。

## 主要特性

- **多摄像机支持**: 支持同时管理和录制多个IP摄像机
- **高效录制**: 使用FFmpeg直接拷贝编码，不重新编码，节省CPU资源
- **分段录像**: 自动按时间分段录制，便于管理和查找
- **时间段提取**: 支持根据开始和结束时间提取特定时间段的录像
- **Web界面**: 提供友好的Web界面进行摄像机管理和控制
- **RESTful API**: 完整的HTTP API接口，方便集成
- **自动清理**: 自动删除超过保留期限的旧录像
- **完善日志**: 详细的日志记录，便于调试和问题排查
- **循环录像**: 支持连续录像模式

## 系统要求

### 软件要求
- Python 3.8+
- FFmpeg (需要安装并配置到系统PATH，或在配置文件中指定路径)
- Windows 10/11 (推荐) 或 Linux

### 硬件要求
- CPU: 双核及以上
- 内存: 4GB+
- 硬盘: 根据录像需求，建议至少100GB可用空间

## 安装步骤

### 1. 安装FFmpeg

#### Windows:
1. 从 [FFmpeg官网](https://ffmpeg.org/download.html) 下载Windows版本
2. 解压到某个目录，例如 `C:\ffmpeg`
3. 将 `C:\ffmpeg\bin` 添加到系统环境变量PATH中
4. 或在 `config.yaml` 中设置FFmpeg路径：
   ```yaml
   ffmpeg:
     path: "C:/ffmpeg/bin/ffmpeg.exe"
   ```

#### Linux:
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

## 配置

编辑 `config.yaml` 文件进行配置：

```yaml
# 服务器配置
server:
  host: "0.0.0.0"  # 监听地址
  port: 8000       # 监听端口

# 录像配置
recording:
  output_dir: "recordings"  # 录像保存目录
  segment_duration: 600     # 每个视频文件的时长（秒），默认10分钟
  retention_days: 7         # 保留录像天数
  enable_auto_delete: true  # 是否启用自动删除旧录像

# FFmpeg配置
ffmpeg:
  path: "ffmpeg"  # Windows下可设置为绝对路径

# 日志配置
logging:
  level: "INFO"  # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 运行

### 启动服务器

```bash
python app.py
```

服务器启动后，访问 http://localhost:8000 进入Web管理界面。

## 使用方法

### 1. Web界面管理

访问 http://localhost:8000 可以：
- 添加/删除摄像机
- 开始/停止录像
- 查看系统状态
- 管理摄像机配置

### 2. API接口

#### 摄像机管理

**列出所有摄像机**
```bash
GET /api/cameras
```

**添加摄像机**
```bash
POST /api/cameras
Content-Type: application/json

{
    "id": "camera_01",
    "name": "前门摄像头",
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
    "enabled": true
}
```

**删除摄像机**
```bash
DELETE /api/cameras/{camera_id}
```

#### 录像控制

**开始录像**
```bash
POST /api/recording/start
Content-Type: application/json

{
    "camera_id": "camera_01"
}
```

**停止录像**
```bash
POST /api/recording/stop
Content-Type: application/json

{
    "camera_id": "camera_01"
}
```

**查询时间段录像**
```bash
POST /api/recording/query
Content-Type: application/json

{
    "camera_id": "camera_01",
    "start_time": "2025-10-09T08:00:00",
    "end_time": "2025-10-09T10:00:00"
}
```

响应示例：
```json
{
    "success": true,
    "result": {
        "camera_id": "camera_01",
        "start_time": "2025-10-09T08:00:00",
        "end_time": "2025-10-09T10:00:00",
        "files": [
            {
                "path": "D:\\recordings\\sessions\\camera_01_20251009_080000\\clip_000_camera_01_20251009_075500.mp4",
                "filename": "clip_000_camera_01_20251009_075500.mp4",
                "size": 15728640
            }
        ]
    }
}
```

#### 系统状态

**获取系统状态**
```bash
GET /api/status
```

**健康检查**
```bash
GET /api/health
```

## 使用示例

### Python调用示例

```python
import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"

# 1. 添加摄像机
response = requests.post(f"{API_BASE}/cameras", json={
    "id": "camera_01",
    "name": "前门摄像头",
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
    "enabled": True
})
print(response.json())

# 2. 开始录像
response = requests.post(f"{API_BASE}/recording/start", json={
    "camera_id": "camera_01"
})
print(response.json())

# 3. 等待一段时间...
import time
time.sleep(600)  # 录像10分钟

# 4. 停止录像
response = requests.post(f"{API_BASE}/recording/stop", json={
    "camera_id": "camera_01"
})
print(response.json())

# 5. 查询录像
end_time = datetime.now()
start_time = end_time - timedelta(minutes=15)

response = requests.post(f"{API_BASE}/recording/query", json={
    "camera_id": "camera_01",
    "start_time": start_time.isoformat(),
    "end_time": end_time.isoformat()
})

result = response.json()
print(f"找到 {len(result['result']['files'])} 个录像文件")
for file in result['result']['files']:
    print(f"文件: {file['path']}, 大小: {file['size']/1024/1024:.2f}MB")
```

## 目录结构

```
ipcam_recorder/
├── app.py                  # 主应用入口
├── camera_manager.py       # 摄像机管理模块
├── recorder.py             # FFmpeg录像模块
├── recording_manager.py    # 录像管理器
├── video_processor.py      # 视频处理模块
├── config.yaml            # 配置文件
├── requirements.txt       # Python依赖
├── README.md             # 说明文档
├── api/
│   ├── __init__.py
│   └── routes.py         # API路由
├── templates/
│   └── index.html        # Web界面
├── logs/                 # 日志目录
└── recordings/           # 录像目录
    ├── camera_01/        # 各摄像机录像
    └── sessions/         # 提取的录像片段
```

## 录像文件命名规则

- 原始录像: `{camera_id}_{YYYYMMDD}_{HHMMSS}.mp4`
- 提取片段: `clip_{序号}_{原始文件名}.mp4`

示例：
- `camera_01_20251009_080000.mp4` - 2025年10月9日8点开始的录像
- `clip_000_camera_01_20251009_080000.mp4` - 从该录像提取的片段

## 故障排查

### 1. FFmpeg未找到
**错误**: `FileNotFoundError: ffmpeg not found`

**解决方案**:
- 确保FFmpeg已正确安装
- 检查FFmpeg是否在系统PATH中
- 在config.yaml中设置FFmpeg的绝对路径

### 2. 无法连接RTSP流
**错误**: FFmpeg连接超时或失败

**解决方案**:
- 检查RTSP URL是否正确
- 确认摄像机IP地址、端口、用户名、密码
- 检查网络连接
- 尝试使用VLC等工具测试RTSP流

### 3. 录像文件过大
**解决方案**:
- 减小 `segment_duration` 参数（在config.yaml中）
- 检查摄像机的码率设置

### 4. 磁盘空间不足
**解决方案**:
- 减小 `retention_days` 参数
- 手动清理旧录像
- 增加磁盘空间

## 性能优化建议

1. **硬盘**: 使用专用硬盘存储录像，避免系统盘空间不足
2. **网络**: 确保稳定的局域网连接，千兆网络为佳
3. **分段时长**: 根据需求调整，太小会产生过多文件，太大不便于管理
4. **并发录像**: 根据系统性能，合理控制同时录像的摄像机数量

## 常见问题

**Q: 支持哪些视频编码格式？**

A: 支持摄像机输出的所有格式（H.264、H.265等），本系统不重新编码，直接拷贝流。

**Q: 可以远程访问吗？**

A: 可以，修改config.yaml中的host为0.0.0.0，并确保防火墙允许相应端口。建议使用VPN或反向代理以保证安全。

**Q: 如何备份录像？**

A: 录像文件保存在recordings目录下，可以直接复制备份。也可以通过API查询获取文件路径后进行备份。

**Q: 系统崩溃后录像会丢失吗？**

A: 已录制的分段文件不会丢失，只有当前正在录制的分段可能不完整。建议设置较小的segment_duration以减少损失。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 作者

Claude Code Assistant

## 更新日志

### v1.0.0 (2025-10-09)
- 初始版本发布
- 支持多摄像机录像
- Web管理界面
- RESTful API
- 自动清理功能
- 时间段录像提取
