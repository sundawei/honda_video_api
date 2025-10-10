"""
セグメント録画モニター
録画ディレクトリを監視して、セグメントファイルの作成状況をリアルタイムで表示
"""

import os
import time
from pathlib import Path
from datetime import datetime

def format_size(bytes_size):
    """ファイルサイズを人間が読みやすい形式に変換"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def get_file_age(filepath):
    """ファイルの経過時間を取得（秒）"""
    return time.time() - os.path.getmtime(filepath)

def monitor_recordings(recording_dir="recordings", camera_id="camera_01", interval=5):
    """
    録画ディレクトリを監視してセグメントファイルの作成を追跡

    Args:
        recording_dir: 録画ディレクトリのパス
        camera_id: 監視するカメラID
        interval: チェック間隔（秒）
    """
    camera_dir = os.path.join(recording_dir, camera_id)

    print("=" * 70)
    print("📹 セグメント録画モニター")
    print("=" * 70)
    print(f"監視ディレクトリ: {camera_dir}")
    print(f"チェック間隔: {interval}秒")
    print("=" * 70)
    print()

    if not os.path.exists(camera_dir):
        print(f"❌ エラー: ディレクトリが存在しません: {camera_dir}")
        return

    seen_files = {}
    file_count = 0

    try:
        while True:
            current_files = {}

            # MP4ファイルを検索
            for filepath in Path(camera_dir).glob("*.mp4"):
                filename = filepath.name
                file_size = filepath.stat().st_size
                file_age = get_file_age(str(filepath))
                current_files[filename] = {
                    'size': file_size,
                    'age': file_age,
                    'path': str(filepath)
                }

            # 新しいファイルをチェック
            new_files = set(current_files.keys()) - set(seen_files.keys())
            if new_files:
                for filename in sorted(new_files):
                    file_count += 1
                    info = current_files[filename]
                    print(f"\n✅ 新しいセグメント検出 (#{file_count})")
                    print(f"   ファイル名: {filename}")
                    print(f"   サイズ: {format_size(info['size'])}")
                    print(f"   作成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # ファイルサイズの変化をチェック（録画中のファイル）
            for filename in current_files:
                if filename in seen_files:
                    old_size = seen_files[filename]['size']
                    new_size = current_files[filename]['size']

                    # サイズが変化している = 録画中
                    if new_size != old_size:
                        age = current_files[filename]['age']
                        print(f"\r⏺️  録画中: {filename} | サイズ: {format_size(new_size)} | 経過: {age:.1f}秒", end='', flush=True)

            # 完成したファイルをチェック（サイズが変化しなくなったファイル）
            for filename in seen_files:
                if filename in current_files:
                    old_size = seen_files[filename]['size']
                    new_size = current_files[filename]['size']

                    # 前回チェック時もサイズが同じ = 完成
                    if old_size == new_size and seen_files[filename].get('was_growing', True):
                        print(f"\n✔️  セグメント完成: {filename} | 最終サイズ: {format_size(new_size)}")
                        current_files[filename]['was_growing'] = False

            seen_files = current_files
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("📊 監視終了")
        print("=" * 70)
        print(f"検出されたセグメント数: {file_count}")
        if current_files:
            total_size = sum(f['size'] for f in current_files.values())
            print(f"総ファイルサイズ: {format_size(total_size)}")
            print(f"総ファイル数: {len(current_files)}")
        print("=" * 70)

if __name__ == "__main__":
    import sys

    # コマンドライン引数からカメラIDを取得
    camera_id = sys.argv[1] if len(sys.argv) > 1 else "camera_01"

    monitor_recordings(camera_id=camera_id, interval=3)
