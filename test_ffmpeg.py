"""
FFmpegコマンドをテストするスクリプト
"""

import subprocess
import yaml
import os

# 設定を読み込む
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

camera = config['cameras'][0]
ffmpeg_config = config['ffmpeg']
recording_config = config['recording']

camera_id = camera['id']
rtsp_url = camera['rtsp_url']
ffmpeg_path = ffmpeg_config['path']
segment_duration = recording_config['segment_duration']

# 出力ファイル
output_file = f"test_recording_{camera_id}.mp4"

# FFmpegコマンドを構築
cmd = [
    ffmpeg_path,
    "-rtsp_transport", "tcp",
    "-reconnect", str(ffmpeg_config.get('reconnect', 1)),
    "-reconnect_at_eof", str(ffmpeg_config.get('reconnect_at_eof', 1)),
    "-reconnect_delay_max", str(ffmpeg_config.get('reconnect_delay_max', 5)),
    "-reconnect_streamed", str(ffmpeg_config.get('reconnect_streamed', 1)),
    "-i", rtsp_url,
    "-c:v", "copy",
    "-c:a", "copy",
    "-t", str(segment_duration),
    "-movflags", "+faststart",
    "-y",
    output_file
]

print("=" * 70)
print("FFmpegコマンドテスト")
print("=" * 70)
print(f"カメラID: {camera_id}")
print(f"RTSP URL: {rtsp_url}")
print(f"録画時間: {segment_duration}秒")
print(f"出力ファイル: {output_file}")
print("=" * 70)
print("\nFFmpegコマンド:")
print(" ".join(cmd))
print("=" * 70)
print("\nFFmpegを実行中...")
print("=" * 70)

try:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # リアルタイムでstderrを出力
    import threading

    def print_stderr():
        for line in process.stderr:
            print(f"FFmpeg: {line.rstrip()}")

    stderr_thread = threading.Thread(target=print_stderr, daemon=True)
    stderr_thread.start()

    # プロセスの完了を待つ
    returncode = process.wait()

    print("=" * 70)
    print(f"\nFFmpeg終了コード: {returncode}")

    if returncode == 0:
        print("✅ 録画成功！")
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024 / 1024
            print(f"ファイルサイズ: {size:.2f} MB")
            print(f"ファイルパス: {os.path.abspath(output_file)}")
    else:
        print(f"❌ 録画失敗（エラーコード: {returncode}）")

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
