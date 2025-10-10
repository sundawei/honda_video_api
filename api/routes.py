"""
API路由定义
提供所有HTTP接口
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# 辅助函数：从请求中获取管理器
def get_camera_manager(request: Request):
    """从app.state获取camera_manager"""
    return request.app.state.camera_manager


def get_recording_manager(request: Request):
    """从app.state获取recording_manager"""
    return request.app.state.recording_manager


# ===== 数据模型 =====

class CameraCreate(BaseModel):
    """创建摄像机请求"""
    id: str
    name: str
    rtsp_url: str
    enabled: bool = True


class CameraUpdate(BaseModel):
    """更新摄像机请求"""
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    enabled: Optional[bool] = None


class RecordingStartRequest(BaseModel):
    """开始录像请求"""
    camera_id: str


class RecordingStopRequest(BaseModel):
    """停止录像请求"""
    camera_id: str


class RecordingQueryRequest(BaseModel):
    """查询录像请求"""
    camera_id: str
    start_time: str  # ISO格式时间字符串
    end_time: str    # ISO格式时间字符串


# ===== 摄像机管理接口 =====

@router.get("/cameras")
async def list_cameras(request: Request):
    """列出所有摄像机"""
    camera_manager = get_camera_manager(request)

    cameras = camera_manager.list_cameras()
    return {
        "success": True,
        "cameras": [cam.to_dict() for cam in cameras]
    }


@router.post("/cameras")
async def add_camera(camera: CameraCreate, request: Request):
    """添加摄像机"""
    camera_manager = get_camera_manager(request)

    try:
        new_camera = camera_manager.add_camera(
            camera_id=camera.id,
            name=camera.name,
            rtsp_url=camera.rtsp_url,
            enabled=camera.enabled
        )
        return {
            "success": True,
            "message": f"Camera {camera.id} added successfully",
            "camera": new_camera.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding camera: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cameras/{camera_id}")
async def get_camera(camera_id: str, request: Request):
    """获取摄像机信息"""
    camera_manager = get_camera_manager(request)

    camera = camera_manager.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

    return {
        "success": True,
        "camera": camera.to_dict()
    }


@router.put("/cameras/{camera_id}")
async def update_camera(camera_id: str, camera: CameraUpdate, request: Request):
    """更新摄像机信息"""
    camera_manager = get_camera_manager(request)

    try:
        updated_camera = camera_manager.update_camera(
            camera_id=camera_id,
            name=camera.name,
            rtsp_url=camera.rtsp_url,
            enabled=camera.enabled
        )
        return {
            "success": True,
            "message": f"Camera {camera_id} updated successfully",
            "camera": updated_camera.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating camera: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cameras/{camera_id}")
async def delete_camera(camera_id: str, request: Request):
    """删除摄像机"""
    camera_manager = get_camera_manager(request)

    try:
        success = camera_manager.remove_camera(camera_id)
        if success:
            return {
                "success": True,
                "message": f"Camera {camera_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting camera: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 录像控制接口 =====

@router.post("/recording/start")
async def start_recording(data: RecordingStartRequest, request: Request):
    """开始录像"""
    recording_manager = get_recording_manager(request)

    try:
        recording_manager.start_recording(data.camera_id)
        return {
            "success": True,
            "message": f"Recording started for camera {data.camera_id}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting recording: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recording/stop")
async def stop_recording(data: RecordingStopRequest, request: Request):
    """停止录像并返回录像信息"""
    recording_manager = get_recording_manager(request)

    try:
        result = recording_manager.stop_recording(data.camera_id)
        return {
            "success": True,
            "message": f"Recording stopped for camera {data.camera_id}",
            "recording_info": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error stopping recording: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recordings/{camera_id}")
async def get_recordings(
    camera_id: str,
    request: Request,
    start_time: Optional[str] = Query(None, description="开始时间(ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间(ISO格式)")
):
    """获取指定相机的录像文件列表"""
    camera_manager = get_camera_manager(request)
    recording_manager = get_recording_manager(request)

    # 检查相机是否存在
    camera = camera_manager.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

    try:
        # 解析时间参数
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None

        # 获取录像器
        recorder = recording_manager.recorders.get(camera_id)
        if not recorder:
            # 如果录像器不存在，返回空列表
            return {
                "success": True,
                "camera_id": camera_id,
                "files": [],
                "total_files": 0,
                "total_size": 0
            }

        # 获取录像文件
        files = recorder.get_recorded_files(start_time=start_dt, end_time=end_dt)
        total_size = sum(f.get("size", 0) for f in files)

        return {
            "success": True,
            "camera_id": camera_id,
            "files": files,
            "total_files": len(files),
            "total_size": total_size
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting recordings for {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recording/query")
async def query_recordings(data: RecordingQueryRequest, request: Request):
    """查询指定时间段的录像"""
    recording_manager = get_recording_manager(request)

    try:
        # 解析时间
        start_time = datetime.fromisoformat(data.start_time)
        end_time = datetime.fromisoformat(data.end_time)

        result = recording_manager.query_recordings(
            camera_id=data.camera_id,
            start_time=start_time,
            end_time=end_time
        )

        return {
            "success": True,
            "result": result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error querying recordings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recording/status/{camera_id}")
async def get_recording_status(camera_id: str, request: Request):
    """获取摄像机录像状态"""
    camera_manager = get_camera_manager(request)
    recording_manager = get_recording_manager(request)

    camera = camera_manager.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

    is_recording = recording_manager.is_recording(camera_id)

    return {
        "success": True,
        "camera_id": camera_id,
        "is_recording": is_recording,
        "camera_enabled": camera.enabled
    }


# ===== 系统状态接口 =====

@router.get("/status")
async def get_system_status(request: Request):
    """获取系统状态"""
    camera_manager = get_camera_manager(request)
    recording_manager = get_recording_manager(request)

    cameras = camera_manager.list_cameras()
    recording_count = sum(1 for cam in cameras if recording_manager.is_recording(cam.id))

    return {
        "success": True,
        "status": {
            "total_cameras": len(cameras),
            "enabled_cameras": len(camera_manager.get_enabled_cameras()),
            "recording_cameras": recording_count
        }
    }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "status": "healthy"
    }


# ===== 配置管理接口 =====

@router.get("/settings")
async def get_settings():
    """获取系统设置"""
    import yaml
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return {
            "success": True,
            "settings": {
                "recording": config.get('recording', {}),
                "ffmpeg": config.get('ffmpeg', {}),
                "server": config.get('server', {})
            }
        }
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings")
async def update_settings(settings: dict):
    """更新系统设置"""
    import yaml
    try:
        # 读取现有配置
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 更新配置
        if 'recording' in settings:
            config['recording'].update(settings['recording'])

        if 'ffmpeg' in settings:
            config['ffmpeg'].update(settings['ffmpeg'])

        # 保存配置
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        logger.info("Settings updated successfully")

        return {
            "success": True,
            "message": "Settings updated successfully. Please restart the server for changes to take effect."
        }
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
