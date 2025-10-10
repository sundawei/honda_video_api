"""
视频处理模块
负责视频片段的提取、裁剪、合并等操作
"""

import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """视频处理器类"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def extract_time_range(self, input_file: str, output_file: str,
                          start_offset: float = 0, duration: float = None) -> bool:
        """
        从视频中提取指定时间段

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            start_offset: 开始时间偏移（秒）
            duration: 持续时间（秒），如果为None则提取到文件末尾

        Returns:
            是否成功
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", input_file,
                "-ss", str(start_offset),
            ]

            if duration is not None:
                cmd.extend(["-t", str(duration)])

            cmd.extend([
                "-c:v", "copy",
                "-c:a", "copy",
                "-y",  # 覆盖输出文件
                output_file
            ])

            logger.info(f"Extracting video: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            if result.returncode == 0:
                logger.info(f"Successfully extracted video to {output_file}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error extracting video: {e}")
            return False

    def concat_videos(self, input_files: List[str], output_file: str) -> bool:
        """
        合并多个视频文件

        Args:
            input_files: 输入文件列表
            output_file: 输出文件路径

        Returns:
            是否成功
        """
        if not input_files:
            logger.warning("No input files to concatenate")
            return False

        try:
            # 创建临时文件列表
            concat_list_file = output_file + ".concat.txt"
            with open(concat_list_file, 'w', encoding='utf-8') as f:
                for file_path in input_files:
                    # 需要转义文件路径
                    escaped_path = file_path.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")

            cmd = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_file,
                "-c:v", "copy",
                "-c:a", "copy",
                "-y",
                output_file
            ]

            logger.info(f"Concatenating {len(input_files)} videos to {output_file}")

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # 删除临时文件
            try:
                os.remove(concat_list_file)
            except:
                pass

            if result.returncode == 0:
                logger.info(f"Successfully concatenated videos to {output_file}")
                return True
            else:
                logger.error(f"FFmpeg concat error: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error concatenating videos: {e}")
            return False

    def get_video_duration(self, video_file: str) -> float:
        """
        获取视频时长

        Args:
            video_file: 视频文件路径

        Returns:
            视频时长（秒）
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_file,
                "-f", "null",
                "-"
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # 从stderr中解析时长
            for line in result.stderr.split('\n'):
                if 'Duration:' in line:
                    # Duration: 00:10:00.00, start: 0.000000, bitrate: ...
                    duration_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = duration_str.split(':')
                    total_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                    return total_seconds

            logger.warning(f"Could not parse duration for {video_file}")
            return 0

        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return 0


class RecordingSession:
    """录像会话类，用于处理开始-结束时间段内的录像提取"""

    def __init__(self, camera_id: str, start_time: datetime, end_time: datetime,
                 video_files: List[dict], output_dir: str, ffmpeg_path: str = "ffmpeg"):
        """
        初始化录像会话

        Args:
            camera_id: 摄像机ID
            start_time: 开始时间
            end_time: 结束时间
            video_files: 视频文件列表（从recorder获取）
            output_dir: 输出目录
            ffmpeg_path: FFmpeg路径
        """
        self.camera_id = camera_id
        self.start_time = start_time
        self.end_time = end_time
        self.video_files = video_files
        self.output_dir = output_dir
        self.processor = VideoProcessor(ffmpeg_path)

        # 创建会话输出目录
        self.session_dir = os.path.join(
            output_dir,
            f"sessions/{camera_id}_{start_time.strftime('%Y%m%d_%H%M%S')}"
        )
        Path(self.session_dir).mkdir(parents=True, exist_ok=True)

    def process(self) -> List[str]:
        """
        处理录像会话，提取并返回所有相关的录像片段

        Returns:
            处理后的视频文件路径列表
        """
        processed_files = []

        try:
            for idx, file_info in enumerate(self.video_files):
                file_path = file_info['path']
                file_start_time = datetime.fromisoformat(file_info['start_time'])

                # 估算文件结束时间（使用下一个文件的开始时间，或当前时间）
                if idx + 1 < len(self.video_files):
                    file_end_time = datetime.fromisoformat(self.video_files[idx + 1]['start_time'])
                else:
                    # 最后一个文件，使用实际视频时长
                    duration = self.processor.get_video_duration(file_path)
                    file_end_time = file_start_time + timedelta(seconds=duration)

                # 检查文件是否与时间段有交集
                if file_end_time < self.start_time or file_start_time > self.end_time:
                    continue

                # 计算需要提取的时间段
                extract_start = max(0, (self.start_time - file_start_time).total_seconds())
                extract_end = (self.end_time - file_start_time).total_seconds()
                extract_duration = extract_end - extract_start

                # 如果需要提取的是整个文件
                if extract_start == 0 and extract_end >= (file_end_time - file_start_time).total_seconds():
                    logger.info(f"Using entire file: {file_path}")
                    processed_files.append(file_path)
                else:
                    # 需要裁剪
                    output_filename = f"clip_{idx:03d}_{os.path.basename(file_path)}"
                    output_path = os.path.join(self.session_dir, output_filename)

                    logger.info(f"Extracting clip from {file_path}: start={extract_start}s, duration={extract_duration}s")

                    if self.processor.extract_time_range(
                        file_path, output_path,
                        start_offset=extract_start,
                        duration=extract_duration
                    ):
                        processed_files.append(output_path)
                    else:
                        logger.error(f"Failed to extract clip from {file_path}")

            logger.info(f"Processed {len(processed_files)} video clips for session")

        except Exception as e:
            logger.error(f"Error processing recording session: {e}")

        return processed_files

    def get_result(self) -> dict:
        """
        获取处理结果

        Returns:
            包含所有处理后视频文件信息的字典
        """
        processed_files = self.process()

        result = {
            "camera_id": self.camera_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "files": []
        }

        for file_path in processed_files:
            if os.path.exists(file_path):
                file_stat = Path(file_path).stat()
                result["files"].append({
                    "path": str(Path(file_path).absolute()),
                    "filename": os.path.basename(file_path),
                    "size": file_stat.st_size
                })

        return result
