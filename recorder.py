"""
FFmpeg录像模块
负责使用FFmpeg进行RTSP流录制，支持分段录像
"""

import subprocess
import threading
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class VideoRecorder:
    """视频录像器类"""

    def __init__(self, camera_id: str, rtsp_url: str, output_dir: str,
                 segment_duration: int = 600, ffmpeg_path: str = "ffmpeg",
                 reconnect_config: dict = None):
        """
        初始化录像器

        Args:
            camera_id: 摄像机ID
            rtsp_url: RTSP流地址
            output_dir: 输出目录
            segment_duration: 分段时长（秒）
            ffmpeg_path: FFmpeg可执行文件路径
            reconnect_config: 重连配置
        """
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.output_dir = output_dir
        self.segment_duration = segment_duration
        self.ffmpeg_path = ffmpeg_path
        self.reconnect_config = reconnect_config or {}

        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.segments: List[dict] = []  # 存储已录制的分段信息
        self.lock = threading.Lock()
        self._force_split = False  # 强制切分标志

        # 创建摄像机专属目录
        self.camera_output_dir = os.path.join(output_dir, camera_id)
        Path(self.camera_output_dir).mkdir(parents=True, exist_ok=True)

    def _get_output_filename(self, start_time: datetime) -> str:
        """
        生成输出文件名（临时文件名，录制完成后会重命名）

        Args:
            start_time: 录制开始时间
        """
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.camera_output_dir, f"{self.camera_id}_{timestamp}_recording.mp4")

    def _get_final_filename(self, start_time: datetime, end_time: datetime) -> str:
        """
        生成最终文件名（包含开始和结束时间）
        格式: camera_id_YYYYMMDD_HHMMSS_to_YYYYMMDD_HHMMSS.mp4

        Args:
            start_time: 录制开始时间
            end_time: 录制结束时间
        """
        start_str = start_time.strftime("%Y%m%d_%H%M%S")
        end_str = end_time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.camera_output_dir, f"{self.camera_id}_{start_str}_to_{end_str}.mp4")

    def _build_ffmpeg_command(self, output_file: str) -> List[str]:
        """构建FFmpeg命令"""
        cmd = [
            self.ffmpeg_path,
            # RTSP传输协议设置
            "-rtsp_transport", "tcp",  # 使用TCP传输，更稳定
            # 超时设置（对于RTSP使用-timeout，单位：微秒）
            "-timeout", "10000000",  # RTSP超时10秒（增加到10秒以容忍网络波动）
            # 分析持续时间，设置更长以确保正确检测流格式
            "-analyzeduration", "10000000",  # 10秒
            "-probesize", "10000000",  # 10MB探测大小
            # 输入源
            "-i", self.rtsp_url,
            # 编码参数
            "-c:v", "copy",    # 视频流复制
            "-c:a", "copy",    # 音频流复制
            "-t", str(self.segment_duration),  # 录制时长（秒）
            # 错误处理
            "-err_detect", "ignore_err",  # 忽略一些非致命错误
            "-max_error_rate", "0.5",  # 容忍50%的错误率
            # MP4优化
            "-movflags", "+faststart+frag_keyframe+empty_moov",  # 更好的流媒体兼容性
            "-y",  # 覆盖已存在的文件
            output_file
        ]

        return cmd

    def start(self):
        """开始录像"""
        if self.is_running:
            logger.warning(f"Recorder for camera {self.camera_id} is already running")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()
        logger.info(f"Started recording for camera {self.camera_id}")

    def _record_loop(self):
        """录像循环（在独立线程中运行）"""
        consecutive_errors = 0
        max_errors = 10  # 增加到10次，给更多重试机会
        retry_delay = 10  # 秒
        error_reset_threshold = 60  # 降低到60秒，让错误计数更容易重置
        last_success_time = None  # 记录最后成功时间
        total_success_duration = 0  # 累计成功时长

        while self.is_running:
            try:
                # 记录开始时间
                start_time = datetime.now()

                # 为每个分段生成临时文件名
                temp_file = self._get_output_filename(start_time)
                cmd = self._build_ffmpeg_command(temp_file)

                logger.info(f"Starting new segment for camera {self.camera_id}: {temp_file}")
                logger.debug(f"FFmpeg command: {' '.join(cmd)}")

                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )

                # 等待FFmpeg进程完成并获取输出
                stdout, stderr = self.process.communicate()
                returncode = self.process.returncode

                # 记录结束时间
                end_time = datetime.now()
                segment_duration = (end_time - start_time).total_seconds()

                # SIGTERM通常返回255或-15，但文件可能是完整的
                # 检查文件是否存在且有效，而不只是依赖返回码
                # 或者是强制切分的情况
                if returncode == 0 or self._force_split or (os.path.exists(temp_file) and os.path.getsize(temp_file) > 1024):
                    # 录制成功或文件有效

                    # 如果是强制切分，记录一下并重置标志
                    if self._force_split:
                        if returncode != 0:
                            logger.info(f"Force split with return code {returncode}, but file is valid")
                        self._force_split = False

                    # 累计成功时长
                    if last_success_time:
                        time_since_last_success = (start_time - last_success_time).total_seconds()
                        # 如果距离上次成功不超过30秒，认为是连续成功
                        if time_since_last_success <= 30:
                            total_success_duration += segment_duration
                        else:
                            total_success_duration = segment_duration
                    else:
                        total_success_duration = segment_duration

                    last_success_time = end_time

                    # 如果累计成功录制超过阈值，重置错误计数
                    if total_success_duration > error_reset_threshold:
                        if consecutive_errors > 0:
                            logger.info(f"Cumulative successful recording for {total_success_duration:.1f}s, resetting error count from {consecutive_errors} to 0")
                        consecutive_errors = 0
                        total_success_duration = 0  # 重置累计时长

                    # 检查临时文件是否生成
                    if os.path.exists(temp_file):
                        file_size = os.path.getsize(temp_file)

                        # 只有文件大小大于1KB才认为是有效文件
                        if file_size > 1024:
                            # 重命名为最终文件名（包含开始和结束时间）
                            final_file = self._get_final_filename(start_time, end_time)
                            try:
                                os.rename(temp_file, final_file)
                                logger.info(f"Segment completed successfully for camera {self.camera_id}: {os.path.basename(final_file)}")
                                logger.info(f"File size: {file_size / 1024 / 1024:.2f} MB, Duration: {segment_duration:.1f}s")
                            except Exception as rename_error:
                                logger.error(f"Failed to rename {temp_file} to {final_file}: {rename_error}")
                                # 如果重命名失败，至少文件还在
                        else:
                            logger.warning(f"Segment file too small ({file_size} bytes), likely incomplete: {temp_file}")
                            try:
                                os.remove(temp_file)
                                logger.info(f"Removed incomplete file: {temp_file}")
                            except:
                                pass
                    else:
                        logger.warning(f"Temporary file not found: {temp_file}")

                    # 如果仍在运行，继续下一个分段
                    if not self.is_running:
                        break
                else:
                    # 录制失败
                    # 注意：强制切分的情况已经在上面的if条件中处理了

                    consecutive_errors += 1
                    logger.error(f"FFmpeg exited with code {returncode} for camera {self.camera_id}")
                    logger.error(f"Error count: {consecutive_errors}/{max_errors}")

                    # 记录完整的stderr输出（分行记录以便阅读）
                    if stderr:
                        stderr_lines = stderr.strip().split('\n')
                        # 只记录最后30行以获取更多错误信息
                        logger.error(f"=== FFmpeg stderr output for camera {self.camera_id} ===")
                        for line in stderr_lines[-30:]:
                            logger.error(f"FFmpeg: {line}")
                        logger.error(f"=== End of FFmpeg stderr ===")

                    if consecutive_errors >= max_errors:
                        logger.error(f"Too many consecutive errors ({consecutive_errors}) for camera {self.camera_id}, stopping recording!")
                        self.is_running = False
                        break

                    if self.is_running:
                        # 根据错误次数调整重试延迟
                        adjusted_delay = min(retry_delay * (1 + consecutive_errors // 3), 60)
                        logger.warning(f"Retrying in {adjusted_delay}s... (error {consecutive_errors}/{max_errors})")
                        time.sleep(adjusted_delay)

            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in recording loop for camera {self.camera_id}: {e}")

                if consecutive_errors >= max_errors:
                    logger.error(f"Too many consecutive errors, stopping...")
                    self.is_running = False
                    break

                if self.is_running:
                    time.sleep(retry_delay)

        logger.info(f"Recording stopped for camera {self.camera_id}")

    def stop(self):
        """停止录像"""
        if not self.is_running:
            logger.warning(f"Recorder for camera {self.camera_id} is not running")
            return

        logger.info(f"Stopping recording for camera {self.camera_id}")
        self.is_running = False

        if self.process:
            try:
                # 发送SIGTERM信号优雅地关闭FFmpeg
                self.process.terminate()
                # 等待最多10秒
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"FFmpeg for camera {self.camera_id} did not terminate, killing...")
                self.process.kill()
            except Exception as e:
                logger.error(f"Error stopping FFmpeg for camera {self.camera_id}: {e}")

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=15)

        logger.info(f"Recorder stopped for camera {self.camera_id}")

    def force_segment_split(self):
        """
        强制结束当前录像段并立即开始新段
        用于查询时需要获取完整时间段的录像
        """
        if not self.is_running:
            logger.warning(f"Recorder for camera {self.camera_id} is not running")
            return False

        logger.info(f"Force segment split for camera {self.camera_id}")

        # 临时设置标志，让录像循环知道这是强制切分
        self._force_split = True

        if self.process:
            try:
                # 发送SIGTERM信号结束当前段
                self.process.terminate()
                # 等待较短时间，因为我们要立即重启
                self.process.wait(timeout=5)
                logger.info(f"Current segment terminated for camera {self.camera_id}, will start new segment")
                return True
            except subprocess.TimeoutExpired:
                logger.warning(f"FFmpeg did not terminate quickly, killing...")
                self.process.kill()
                return True
            except Exception as e:
                logger.error(f"Error during force segment split: {e}")
                return False

        return False

    def get_recorded_files(self, start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> List[dict]:
        """
        获取指定时间段内的录像文件

        Args:
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            录像文件列表，包含文件路径和时间信息
        """
        files = []

        try:
            for file_path in Path(self.camera_output_dir).glob(f"{self.camera_id}_*.mp4"):
                # 跳过正在录制的临时文件
                if file_path.stem.endswith('_recording'):
                    continue

                filename = file_path.stem
                file_start_time = None
                file_end_time = None

                try:
                    # 新格式: camera_id_YYYYMMDD_HHMMSS_to_YYYYMMDD_HHMMSS
                    if '_to_' in filename:
                        parts = filename.split('_to_')
                        if len(parts) == 2:
                            # 提取开始时间部分
                            start_parts = parts[0].split('_')
                            if len(start_parts) >= 3:
                                date_str = start_parts[-2]
                                time_str = start_parts[-1]
                                file_start_time = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")

                            # 提取结束时间部分
                            end_parts = parts[1].split('_')
                            if len(end_parts) >= 2:
                                date_str = end_parts[0]
                                time_str = end_parts[1]
                                file_end_time = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")

                    # 旧格式: camera_id_YYYYMMDD_HHMMSS（向后兼容）
                    else:
                        parts = filename.split('_')
                        if len(parts) >= 3:
                            date_str = parts[-2]
                            time_str = parts[-1]
                            file_start_time = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                            # 旧格式没有结束时间，估算为开始时间+分段时长
                            file_end_time = file_start_time + timedelta(seconds=self.segment_duration)

                    if file_start_time:
                        # 过滤时间范围
                        if start_time and file_end_time and file_end_time < start_time:
                            continue
                        if end_time and file_start_time > end_time:
                            continue

                        file_info = {
                            "path": str(file_path.absolute()),
                            "filename": file_path.name,
                            "start_time": file_start_time.isoformat(),
                            "end_time": file_end_time.isoformat() if file_end_time else None,
                            "duration": (file_end_time - file_start_time).total_seconds() if file_end_time else None,
                            "size": file_path.stat().st_size,
                            "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                        }
                        files.append(file_info)

                except ValueError as e:
                    logger.warning(f"Could not parse time from filename {filename}: {e}")

        except Exception as e:
            logger.error(f"Error getting recorded files for camera {self.camera_id}: {e}")

        # 按开始时间排序
        files.sort(key=lambda x: x['start_time'])
        return files
