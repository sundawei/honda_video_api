# IP Camera Recorder API - 使用说明

## 📦 快速部署

### 系统要求
- Windows 7/10/11
- Python 3.7 或更高版本
- FFmpeg（必需）

### 部署步骤

1. **解压文件**
   将压缩包解压到任意目录

2. **安装前置软件**
   - Python: https://www.python.org/downloads/
   - FFmpeg: https://ffmpeg.org/download.html

3. **配置摄像机**
   编辑 `config.yaml` 文件：
   ```yaml
   cameras:
     - id: camera_01
       name: "前门摄像机"
       rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream"
       enabled: true
   ```

4. **启动服务**
   双击运行 `start_api.bat`

5. **访问API**
   - API文档: http://127.0.0.1:9999/docs
   - 健康检查: http://127.0.0.1:9999/api/health

## 📁 目录结构

```
IPCameraRecorder/
├── libs/           # Python依赖包（已包含，无需安装）
├── recordings/     # 录像文件存储
├── logs/          # 日志文件
├── config.yaml    # 配置文件
└── start_api.bat  # 启动脚本
```

## 🔧 常见问题

### 1. 提示找不到Python
- 确认已安装Python 3.7+
- 确认Python已添加到系统PATH

### 2. 提示找不到FFmpeg
- 下载FFmpeg并解压
- 将FFmpeg的bin目录添加到系统PATH

### 3. 录像无法开始
- 检查RTSP地址是否正确
- 检查网络连接
- 查看logs/app.log日志文件

### 4. 端口被占用
- 修改app.py最后一行的端口号

## 📝 API接口说明

### 开始录像
```
POST /api/recording/start
{"camera_id": "camera_01"}
```

### 停止录像
```
POST /api/recording/stop
{"camera_id": "camera_01"}
```

### 查询录像
```
POST /api/recording/query
{
  "camera_id": "camera_01",
  "start_time": "2024-01-01T00:00:00",
  "end_time": "2024-01-01T23:59:59"
}
```

## 💡 提示

- 录像文件默认保存7天，可在config.yaml中修改
- 每个录像段默认10分钟，可调整segment_duration参数
- 支持多个摄像机同时录像

## 📞 技术支持

如遇问题，请检查：
- logs/app.log - 应用日志
- 控制台输出信息

---
版本: v1.0.0