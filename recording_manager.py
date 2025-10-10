"""
录像管理器
负责管理所有摄像机的录像任务
"""

import threading
from typing import Dict, Optional
from datetime import datetime
import logging

from recorder import VideoRecorder
from video_processor import RecordingSession
from camera_manager import CameraManager

logger = logging.getLogger(__name__)


class RecordingManager:
    """录像管理器"""

    def __init__(self, camera_manager: CameraManager, config: dict):
        self.camera_manager = camera_manager
        self.config = config
        self.recorders: Dict[str, VideoRecorder] = {}
        self.lock = threading.RLock()

        # 录像配置
        self.output_dir = config['recording']['output_dir']
        self.segment_duration = config['recording']['segment_duration']
        self.ffmpeg_path = config['ffmpeg']['path']
        self.reconnect_config = {
            'reconnect': config['ffmpeg']['reconnect'],
            'reconnect_at_eof': config['ffmpeg']['reconnect_at_eof'],
            'reconnect_streamed': config['ffmpeg']['reconnect_streamed'],
            'reconnect_delay_max': config['ffmpeg']['reconnect_delay_max'],
        }

    def start_recording(self, camera_id: str):
        """开始录像"""
        with self.lock:
            # 检查摄像机是否存在
            camera = self.camera_manager.get_camera(camera_id)
            if not camera:
                raise ValueError(f"Camera {camera_id} not found")

            if not camera.enabled:
                raise ValueError(f"Camera {camera_id} is disabled")

            # 检查是否已经在录像
            if camera_id in self.recorders and self.recorders[camera_id].is_running:
                logger.warning(f"Camera {camera_id} is already recording")
                return

            # 创建录像器
            recorder = VideoRecorder(
                camera_id=camera_id,
                rtsp_url=camera.rtsp_url,
                output_dir=self.output_dir,
                segment_duration=self.segment_duration,
                ffmpeg_path=self.ffmpeg_path,
                reconnect_config=self.reconnect_config
            )

            # 启动录像
            recorder.start()
            self.recorders[camera_id] = recorder
            camera.is_recording = True
            camera.current_recorder = recorder

            logger.info(f"Started recording for camera {camera_id}")

    def stop_recording(self, camera_id: str) -> dict:
        """
        停止录像并返回录像信息

        Returns:
            包含录像文件信息的字典
        """
        with self.lock:
            # 检查摄像机是否存在
            camera = self.camera_manager.get_camera(camera_id)
            if not camera:
                raise ValueError(f"Camera {camera_id} not found")

            # 检查是否在录像
            if camera_id not in self.recorders:
                logger.warning(f"Camera {camera_id} is not recording")
                return {
                    "camera_id": camera_id,
                    "was_recording": False,
                    "files": []
                }

            recorder = self.recorders[camera_id]

            # 获取录像文件列表（在停止之前）
            recorded_files = recorder.get_recorded_files() if recorder.is_running else []

            if recorder.is_running:
                recorder.stop()

            camera.is_recording = False
            camera.current_recorder = None

            logger.info(f"Stopped recording for camera {camera_id}, {len(recorded_files)} files recorded")

            return {
                "camera_id": camera_id,
                "was_recording": True,
                "files": recorded_files,
                "total_files": len(recorded_files),
                "total_size": sum(f.get('size', 0) for f in recorded_files)
            }

    def is_recording(self, camera_id: str) -> bool:
        """检查摄像机是否正在录像"""
        with self.lock:
            if camera_id in self.recorders:
                return self.recorders[camera_id].is_running
            return False

    def query_recordings(self, camera_id: str, start_time: datetime, end_time: datetime) -> dict:
        """
        查询指定时间段的录像

        Args:
            camera_id: 摄像机ID
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            录像文件信息
        """
        import time

        # 检查摄像机是否存在
        camera = self.camera_manager.get_camera(camera_id)
        if not camera:
            raise ValueError(f"Camera {camera_id} not found")

        # 检查是否需要强制切分当前录像段
        need_force_split = False
        current_time = datetime.now()

        # 如果结束时间接近当前时间（5秒内），且摄像机正在录像，则需要强制切分
        if abs((end_time - current_time).total_seconds()) < 5:
            with self.lock:
                if camera_id in self.recorders and self.recorders[camera_id].is_running:
                    need_force_split = True
                    logger.info(f"Query end time is near current time, will force segment split for camera {camera_id}")

        # 执行强制切分
        if need_force_split:
            with self.lock:
                recorder = self.recorders[camera_id]
                if recorder and recorder.is_running:
                    # 强制结束当前段
                    recorder.force_segment_split()
                    # 等待文件重命名完成
                    time.sleep(2)
                    logger.info(f"Force segment split completed for camera {camera_id}")

        # 获取录像器（可能正在录像，也可能已停止）
        with self.lock:
            if camera_id in self.recorders:
                recorder = self.recorders[camera_id]
            else:
                # 创建一个临时录像器用于查询
                recorder = VideoRecorder(
                    camera_id=camera_id,
                    rtsp_url=camera.rtsp_url,
                    output_dir=self.output_dir,
                    segment_duration=self.segment_duration,
                    ffmpeg_path=self.ffmpeg_path
                )

        # 获取时间段内的录像文件
        video_files = recorder.get_recorded_files(start_time, end_time)

        if not video_files:
            logger.info(f"No recordings found for camera {camera_id} between {start_time} and {end_time}")
            return {
                "camera_id": camera_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "files": []
            }

        # 创建录像会话进行处理
        session = RecordingSession(
            camera_id=camera_id,
            start_time=start_time,
            end_time=end_time,
            video_files=video_files,
            output_dir=self.output_dir,
            ffmpeg_path=self.ffmpeg_path
        )

        # 处理并返回结果
        result = session.get_result()
        logger.info(f"Query result for camera {camera_id}: {len(result['files'])} files found")

        return result

    def stop_all(self):
        """停止所有录像"""
        with self.lock:
            camera_ids = list(self.recorders.keys())

        for camera_id in camera_ids:
            try:
                self.stop_recording(camera_id)
            except Exception as e:
                logger.error(f"Error stopping recording for camera {camera_id}: {e}")

        logger.info("All recordings stopped")

    def get_all_status(self) -> dict:
        """获取所有摄像机的录像状态"""
        cameras = self.camera_manager.list_cameras()
        status = {}

        for camera in cameras:
            status[camera.id] = {
                "name": camera.name,
                "enabled": camera.enabled,
                "is_recording": self.is_recording(camera.id)
            }

        return status
