"""
IP Camera Recorder 主应用
"""

import os
import sys
import yaml
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import threading
import time
from datetime import datetime, timedelta

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

from camera_manager import CameraManager
from recording_manager import RecordingManager
from api.routes import router as api_router

# ===== 全局变量 =====
camera_manager = None
recording_manager = None
config = None


def setup_logging(log_config: dict):
    """设置日志系统"""
    log_dir = Path(log_config['file']).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_config['level']))

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_config['level']))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        log_config['file'],
        maxBytes=log_config['max_bytes'],
        backupCount=log_config['backup_count'],
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_config['level']))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def load_config(config_file: str = "config.yaml") -> dict:
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file {config_file} not found, using defaults")
        # 返回默认配置
        return {
            'server': {'host': '0.0.0.0', 'port': 8000},
            'recording': {
                'output_dir': 'recordings',
                'segment_duration': 600,
                'retention_days': 7,
                'enable_auto_delete': True
            },
            'ffmpeg': {
                'path': 'ffmpeg',
                'reconnect': 1,
                'reconnect_at_eof': 1,
                'reconnect_streamed': 1,
                'reconnect_delay_max': 5
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/recorder.log',
                'max_bytes': 10485760,
                'backup_count': 5
            },
            'cameras': []
        }


def cleanup_old_recordings(output_dir: str, retention_days: int):
    """清理旧录像文件"""
    logger = logging.getLogger(__name__)
    cutoff_time = datetime.now() - timedelta(days=retention_days)

    try:
        recordings_path = Path(output_dir)
        if not recordings_path.exists():
            return

        deleted_count = 0
        deleted_size = 0

        # 遍历所有摄像机目录
        for camera_dir in recordings_path.iterdir():
            if not camera_dir.is_dir():
                continue

            # 检查视频文件
            for video_file in camera_dir.glob("*.mp4"):
                try:
                    file_mtime = datetime.fromtimestamp(video_file.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        file_size = video_file.stat().st_size
                        video_file.unlink()
                        deleted_count += 1
                        deleted_size += file_size
                        logger.info(f"Deleted old recording: {video_file}")
                except Exception as e:
                    logger.error(f"Error deleting file {video_file}: {e}")

        # 清理sessions目录
        sessions_dir = recordings_path / "sessions"
        if sessions_dir.exists():
            for session_dir in sessions_dir.iterdir():
                if not session_dir.is_dir():
                    continue

                try:
                    dir_mtime = datetime.fromtimestamp(session_dir.stat().st_mtime)
                    if dir_mtime < cutoff_time:
                        # 删除目录下所有文件
                        for file in session_dir.glob("*"):
                            file.unlink()
                        session_dir.rmdir()
                        logger.info(f"Deleted old session directory: {session_dir}")
                except Exception as e:
                    logger.error(f"Error deleting session directory {session_dir}: {e}")

        if deleted_count > 0:
            logger.info(f"Cleanup completed: deleted {deleted_count} files, freed {deleted_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        logger.error(f"Error in cleanup_old_recordings: {e}")


def auto_cleanup_thread(output_dir: str, retention_days: int, check_interval: int = 3600):
    """自动清理线程"""
    logger = logging.getLogger(__name__)
    logger.info(f"Auto cleanup thread started: retention_days={retention_days}, check_interval={check_interval}s")

    while True:
        try:
            cleanup_old_recordings(output_dir, retention_days)
        except Exception as e:
            logger.error(f"Error in auto cleanup thread: {e}")

        time.sleep(check_interval)


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    global camera_manager, recording_manager, config

    # 加载配置
    config = load_config()

    # 设置日志
    logger = setup_logging(config['logging'])
    logger.info("Starting IP Camera Recorder...")

    # 创建必要的目录
    Path(config['recording']['output_dir']).mkdir(parents=True, exist_ok=True)
    Path("static").mkdir(parents=True, exist_ok=True)
    Path("templates").mkdir(parents=True, exist_ok=True)

    # 初始化管理器
    camera_manager = CameraManager(config_file="config.yaml")
    recording_manager = RecordingManager(camera_manager, config)

    # Lifespan事件管理器
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # 将管理器存储到app.state，使路由可以访问
        app.state.camera_manager = camera_manager
        app.state.recording_manager = recording_manager

        # 启动时执行
        logger.info("Application started")

        # 启动自动清理线程
        cleanup_thread = None
        if config['recording']['enable_auto_delete']:
            cleanup_thread = threading.Thread(
                target=auto_cleanup_thread,
                args=(
                    config['recording']['output_dir'],
                    config['recording']['retention_days']
                ),
                daemon=True
            )
            cleanup_thread.start()
            logger.info("Auto cleanup thread started")

        # 自动开始录像（如果有已配置的相机）
        cameras = camera_manager.list_cameras()
        started_count = 0
        for camera in cameras:
            if camera.enabled:
                try:
                    recording_manager.start_recording(camera.id)
                    started_count += 1
                    logger.info(f"Auto-started recording for camera: {camera.id} ({camera.name})")
                except Exception as e:
                    logger.error(f"Failed to auto-start recording for camera {camera.id}: {e}")

        if started_count > 0:
            logger.info(f"Auto-started recording for {started_count} camera(s)")
        else:
            logger.info("No cameras configured or enabled for auto-start")

        yield

        # 关闭时执行
        logger.info("Shutting down application...")
        recording_manager.stop_all()
        logger.info("Application stopped")

    # 创建FastAPI应用
    app = FastAPI(
        title="IP Camera Recorder API",
        description="IP摄像机录像系统API",
        version="1.0.0",
        lifespan=lifespan
    )

    # 注册API路由
    app.include_router(api_router, prefix="/api")

    # 静态文件
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # 模板
    templates = Jinja2Templates(directory="templates")

    # 主页路由
    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """主页"""
        return templates.TemplateResponse("index.html", {"request": request})

    # 设置页面路由
    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(request: Request):
        """设置页面"""
        return templates.TemplateResponse("settings.html", {"request": request})

    return app


def main():
    """主函数"""
    global config

    app = create_app()

    # 启动服务器
    uvicorn.run(
        app,
        host=config['server']['host'],
        port=config['server']['port'],
        log_config=None  # 使用我们自己的日志配置
    )


if __name__ == "__main__":
    main()
