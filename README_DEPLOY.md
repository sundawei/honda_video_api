# IP Camera Recorder API - Deployment Guide

## Quick Start

### 1. System Requirements
- Python 3.7 or higher
- FFmpeg (for video recording)
- Windows/Linux/MacOS

### 2. Installation Steps

#### Step 1: Install Python
Download and install Python from: https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

#### Step 2: Install FFmpeg
Download FFmpeg from: https://ffmpeg.org/download.html
- Extract and add to system PATH

#### Step 3: Install Dependencies
Open Command Prompt/Terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Cameras
Edit `config.yaml` to add your camera information:
```yaml
cameras:
  - id: camera_01
    name: "Camera 1"
    rtsp_url: "rtsp://username:password@ip:port/stream"
    enabled: true
```

#### Step 5: Start the Server
Double-click `start_simple.bat` or run:
```bash
python app.py
```

## API Access
- Web Interface: http://127.0.0.1:9999
- API Documentation: http://127.0.0.1:9999/docs
- Health Check: http://127.0.0.1:9999/api/health

## Project Structure
```
recoder/
├── app.py                  # Main application
├── recorder.py             # Recording module
├── recording_manager.py    # Recording management
├── camera_manager.py       # Camera management
├── video_processor.py      # Video processing
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── start_simple.bat       # Windows startup script
├── recordings/            # Video storage (auto-created)
├── logs/                  # Log files (auto-created)
├── static/                # Static files
└── templates/             # HTML templates
```

## API Endpoints

### Recording Control
- `POST /api/recording/start` - Start recording
- `POST /api/recording/stop` - Stop recording
- `POST /api/recording/query` - Query recordings

### Camera Management
- `GET /api/cameras` - List all cameras
- `GET /api/status` - System status

## Troubleshooting

### Python not found
- Make sure Python is installed and added to PATH
- Try running `python --version` in command prompt

### Module not found error
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try upgrading pip: `python -m pip install --upgrade pip`

### FFmpeg not found
- Download FFmpeg and add to PATH
- Recording won't work without FFmpeg

### Port already in use
- Change port in app.py (last line)
- Default port is 9999

## Notes
- Recordings are saved in `recordings/` directory
- Logs are saved in `logs/` directory
- Default recording segment duration is 600 seconds (10 minutes)
- Recordings are automatically deleted after 7 days (configurable)