# IP Camera Recorder API

[English](#english) | [日本語](#japanese) | [中文](#chinese)

---

<a name="english"></a>
## 🎥 IP Camera Recorder API - Professional RTSP Recording System

A robust and scalable API system for recording and managing IP camera RTSP streams with automatic segment management and web interface.

### ✨ Key Features

- **RTSP Stream Recording**: Support for multiple IP cameras with RTSP protocol
- **Segment-Based Recording**: Automatic file segmentation (default 10 minutes)
- **Web Management Interface**: User-friendly Japanese UI for camera control
- **RESTful API**: Complete API for integration with external systems
- **Automatic Cleanup**: Old recordings auto-deletion after retention period
- **Error Recovery**: Automatic reconnection and error handling
- **Force Split**: Real-time segment splitting for immediate file access
- **Single Camera Mode**: Simplified interface for single camera deployment

### 🚀 Quick Start

#### Prerequisites
- Python 3.7+
- FFmpeg (required for recording)
- Windows/Linux/MacOS

#### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Configure camera in config.yaml
# Start the server
python app.py
```

#### Access Points
- Web Interface: http://localhost:9999
- API Documentation: http://localhost:9999/docs
- Settings: http://localhost:9999/settings

### 📋 Configuration

Edit `config.yaml`:
```yaml
cameras:
  - id: camera_01
    name: "Front Door Camera"
    rtsp_url: "rtsp://username:password@192.168.1.100:554/stream"
    enabled: true

recording:
  output_dir: "recordings"
  segment_duration: 600  # 10 minutes
  retention_days: 7
```

### 🔧 API Endpoints

#### Recording Control
- `POST /api/recording/start` - Start recording
- `POST /api/recording/stop` - Stop recording
- `POST /api/recording/query` - Query recordings by time range

#### Camera Management
- `GET /api/cameras` - List all cameras
- `GET /api/status` - System status

#### Settings
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

### 🏗️ Architecture

```
recoder/
├── app.py                  # Main FastAPI application
├── recorder.py             # FFmpeg recording module
├── recording_manager.py    # Recording management
├── camera_manager.py       # Camera configuration
├── video_processor.py      # Video processing utilities
├── config.yaml            # Configuration file
├── templates/             # Web UI templates
│   ├── index.html        # Japanese interface
│   └── settings.html     # Settings page
└── recordings/           # Video storage (auto-created)
```

### 🛡️ Recent Improvements

#### v1.1.0 (2024-10-10)
- **Force Segment Split**: Automatic segment splitting when querying near real-time
- **Improved Error Handling**: Better FFmpeg error recovery and retry logic
- **Single Camera Mode**: Simplified UI with camera addition disabled
- **Enhanced Stability**: Fixed recording auto-stop issues
- **Better Logging**: Detailed error messages and debugging information

### 📦 Deployment

For production deployment:
1. Use `create_package.bat` to create release package
2. Deploy with systemd (Linux) or Windows Service
3. Configure reverse proxy (nginx/Apache) for HTTPS
4. Set up proper firewall rules

---

<a name="japanese"></a>
## 🎥 IPカメラレコーダーAPI - プロフェッショナルRTSP録画システム

複数のIPカメラのRTSPストリームを録画・管理するための堅牢でスケーラブルなAPIシステム。自動セグメント管理とWebインターフェースを備えています。

### ✨ 主な機能

- **RTSPストリーム録画**: RTSP プロトコル対応の複数IPカメラをサポート
- **セグメントベース録画**: 自動ファイル分割（デフォルト10分）
- **Web管理インターフェース**: 使いやすい日本語UIでカメラ制御
- **RESTful API**: 外部システムとの統合用完全API
- **自動クリーンアップ**: 保存期間後の古い録画を自動削除
- **エラーリカバリー**: 自動再接続とエラー処理
- **強制分割**: リアルタイムセグメント分割で即座にファイルアクセス
- **単一カメラモード**: 単一カメラ展開用の簡略化インターフェース

### 🚀 クイックスタート

#### 前提条件
- Python 3.7以上
- FFmpeg（録画に必要）
- Windows/Linux/MacOS

#### インストール
```bash
# 依存関係のインストール
pip install -r requirements.txt

# config.yamlでカメラを設定
# サーバーを起動
python app.py
```

#### アクセスポイント
- Webインターフェース: http://localhost:9999
- APIドキュメント: http://localhost:9999/docs
- 設定: http://localhost:9999/settings

### 📋 設定

`config.yaml`を編集:
```yaml
cameras:
  - id: camera_01
    name: "玄関カメラ"
    rtsp_url: "rtsp://username:password@192.168.1.100:554/stream"
    enabled: true

recording:
  output_dir: "recordings"
  segment_duration: 600  # 10分
  retention_days: 7
```

### 🛡️ 最新の改善点

#### v1.1.0 (2024-10-10)
- **強制セグメント分割**: リアルタイムに近いクエリ時の自動セグメント分割
- **改善されたエラー処理**: より良いFFmpegエラーリカバリーと再試行ロジック
- **単一カメラモード**: カメラ追加を無効にした簡略化UI
- **安定性の向上**: 録画自動停止問題の修正
- **より良いログ記録**: 詳細なエラーメッセージとデバッグ情報

---

<a name="chinese"></a>
## 🎥 IP摄像机录像API - 专业RTSP录制系统

一个强大且可扩展的API系统，用于录制和管理IP摄像机RTSP流，具有自动分段管理和Web界面。

### ✨ 主要功能

- **RTSP流录制**: 支持多个使用RTSP协议的IP摄像机
- **基于分段的录制**: 自动文件分段（默认10分钟）
- **Web管理界面**: 友好的日语UI用于摄像机控制
- **RESTful API**: 完整的API用于与外部系统集成
- **自动清理**: 保留期后自动删除旧录像
- **错误恢复**: 自动重连和错误处理
- **强制分割**: 实时分段分割以立即访问文件
- **单摄像机模式**: 用于单摄像机部署的简化界面

### 🚀 快速开始

#### 先决条件
- Python 3.7+
- FFmpeg（录制所需）
- Windows/Linux/MacOS

#### 安装
```bash
# 安装依赖
pip install -r requirements.txt

# 在config.yaml中配置摄像机
# 启动服务器
python app.py
```

### 🛡️ 最新改进

#### v1.1.0 (2024-10-10)
- **强制分段分割**: 查询接近实时时自动分段分割
- **改进的错误处理**: 更好的FFmpeg错误恢复和重试逻辑
- **单摄像机模式**: 禁用摄像机添加的简化UI
- **提高稳定性**: 修复录制自动停止问题
- **更好的日志记录**: 详细的错误消息和调试信息