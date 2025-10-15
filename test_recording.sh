#!/bin/bash
# ====================================
# IP Camera Recording Test Script (Linux/Mac)
# ====================================

echo "========================================"
echo "IP Camera Recording Test"
echo "========================================"
echo

# 设置变量
RTSP_URL="rtsp://admin:Admin1234@192.168.31.14:554/main"
OUTPUT_FILE="test_output_$(date +%Y%m%d_%H%M%S).mp4"
LOG_FILE="ffmpeg_test_log_$(date +%Y%m%d_%H%M%S).txt"
DURATION=60

echo "RTSP URL: $RTSP_URL"
echo "Output File: $OUTPUT_FILE"
echo "Log File: $LOG_FILE"
echo "Duration: $DURATION seconds"
echo
echo "========================================"

# 检查FFmpeg是否存在
echo "Step 1: Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "[ERROR] FFmpeg not found! Please install FFmpeg first."
    echo "Install on Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "Install on CentOS/RHEL: sudo yum install ffmpeg"
    echo "Install on Mac: brew install ffmpeg"
    exit 1
fi
echo "[OK] FFmpeg is installed"
ffmpeg -version | head -n 1
echo

# 测试RTSP连接
echo "Step 2: Testing RTSP connection..."
echo "Testing connection to camera..."
if ffmpeg -rtsp_transport tcp -i "$RTSP_URL" -t 1 -f null - &> /dev/null; then
    echo "[OK] RTSP connection test passed"
else
    echo "[WARNING] RTSP connection test failed"
    echo "This might be normal - continuing with recording test..."
fi
echo

# 开始录制测试
echo "Step 3: Starting recording test ($DURATION seconds)..."
echo "This will take $DURATION seconds. Please wait..."
echo "All output will be saved to: $LOG_FILE"
echo

ffmpeg -v verbose \
  -rtsp_transport tcp \
  -timeout 10000000 \
  -analyzeduration 10000000 \
  -probesize 10000000 \
  -i "$RTSP_URL" \
  -c:v copy \
  -c:a copy \
  -t $DURATION \
  -err_detect ignore_err \
  -max_error_rate 0.5 \
  -movflags +faststart+frag_keyframe+empty_moov \
  -y \
  "$OUTPUT_FILE" 2>&1 | tee "$LOG_FILE"

# 检查结果
echo
echo "========================================"
echo "Test Complete!"
echo "========================================"

if [ -f "$OUTPUT_FILE" ]; then
    echo "[OK] Output file created: $OUTPUT_FILE"
    FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
    echo "File size: $FILE_SIZE bytes"

    if [ "$FILE_SIZE" -lt 1024 ]; then
        echo "[WARNING] File size is very small - recording may have failed"
    else
        echo "[OK] File size looks reasonable"
    fi

    # 尝试获取视频信息
    if command -v ffprobe &> /dev/null; then
        echo
        echo "Video information:"
        ffprobe "$OUTPUT_FILE" 2>&1 | grep -E "Duration|Stream|Video|Audio"
    fi
else
    echo "[ERROR] Output file was not created!"
fi

echo
echo "Log file saved to: $LOG_FILE"
echo
echo "Please check:"
echo "1. Video file: $OUTPUT_FILE"
echo "2. Log file: $LOG_FILE"
echo

# 显示日志文件的最后几行
echo "Last 20 lines of log:"
echo "========================================"
tail -n 20 "$LOG_FILE"
echo "========================================"
echo
echo "To view full log: cat $LOG_FILE"
echo "To play video: ffplay $OUTPUT_FILE"
echo
