"""
摄像机管理模块
负责摄像机的添加、删除、配置管理
"""

import threading
import yaml
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Camera:
    """摄像机类"""

    def __init__(self, camera_id: str, name: str, rtsp_url: str, enabled: bool = True):
        self.id = camera_id
        self.name = name
        self.rtsp_url = rtsp_url
        self.enabled = enabled
        self.is_recording = False
        self.current_recorder = None
        self.created_at = datetime.now()

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "rtsp_url": self.rtsp_url,
            "enabled": self.enabled,
            "is_recording": self.is_recording,
            "created_at": self.created_at.isoformat()
        }


class CameraManager:
    """摄像机管理器"""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.cameras: Dict[str, Camera] = {}
        self.lock = threading.RLock()
        self.load_cameras()

    def load_cameras(self):
        """从配置文件加载摄像机"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            cameras_config = config.get('cameras', [])
            with self.lock:
                for cam_cfg in cameras_config:
                    camera = Camera(
                        camera_id=cam_cfg['id'],
                        name=cam_cfg['name'],
                        rtsp_url=cam_cfg['rtsp_url'],
                        enabled=cam_cfg.get('enabled', True)
                    )
                    self.cameras[camera.id] = camera

            logger.info(f"Loaded {len(self.cameras)} cameras from config")

        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found")
        except Exception as e:
            logger.error(f"Error loading cameras: {e}")

    def save_cameras(self):
        """保存摄像机配置到文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            cameras_list = []
            with self.lock:
                for camera in self.cameras.values():
                    cameras_list.append({
                        'id': camera.id,
                        'name': camera.name,
                        'rtsp_url': camera.rtsp_url,
                        'enabled': camera.enabled
                    })

            config['cameras'] = cameras_list

            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"Saved {len(cameras_list)} cameras to config")

        except Exception as e:
            logger.error(f"Error saving cameras: {e}")
            raise

    def add_camera(self, camera_id: str, name: str, rtsp_url: str, enabled: bool = True) -> Camera:
        """添加摄像机"""
        with self.lock:
            if camera_id in self.cameras:
                raise ValueError(f"Camera with ID {camera_id} already exists")

            camera = Camera(camera_id, name, rtsp_url, enabled)
            self.cameras[camera_id] = camera

        self.save_cameras()
        logger.info(f"Added camera: {camera_id} - {name}")
        return camera

    def remove_camera(self, camera_id: str) -> bool:
        """删除摄像机"""
        with self.lock:
            if camera_id not in self.cameras:
                return False

            camera = self.cameras[camera_id]
            if camera.is_recording:
                raise ValueError(f"Camera {camera_id} is currently recording. Stop recording first.")

            del self.cameras[camera_id]

        self.save_cameras()
        logger.info(f"Removed camera: {camera_id}")
        return True

    def get_camera(self, camera_id: str) -> Optional[Camera]:
        """获取摄像机"""
        with self.lock:
            return self.cameras.get(camera_id)

    def update_camera(self, camera_id: str, name: Optional[str] = None,
                     rtsp_url: Optional[str] = None, enabled: Optional[bool] = None) -> Camera:
        """更新摄像机信息"""
        with self.lock:
            camera = self.cameras.get(camera_id)
            if not camera:
                raise ValueError(f"Camera {camera_id} not found")

            if name is not None:
                camera.name = name
            if rtsp_url is not None:
                camera.rtsp_url = rtsp_url
            if enabled is not None:
                camera.enabled = enabled

        self.save_cameras()
        logger.info(f"Updated camera: {camera_id}")
        return camera

    def list_cameras(self) -> List[Camera]:
        """列出所有摄像机"""
        with self.lock:
            return list(self.cameras.values())

    def get_enabled_cameras(self) -> List[Camera]:
        """获取所有启用的摄像机"""
        with self.lock:
            return [cam for cam in self.cameras.values() if cam.enabled]
