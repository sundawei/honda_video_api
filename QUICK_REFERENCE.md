# クイックリファレンス - IPカメラ録画システム

## Python録画API - よく使うコマンド

### サービス起動
```bash
# 通常起動
cd /mnt/d/wch/recoder
python recorder.py

# バックグラウンド起動
nohup python recorder.py > recorder.log 2>&1 &
```

### 録画制御（コマンドライン）
```bash
# 録画開始
curl -X POST http://127.0.0.1:9999/api/start/camera_01 \
  -H "Content-Type: application/json" \
  -d '{"rtsp_url":"rtsp://192.168.1.100:554/stream"}'

# 録画停止
curl -X POST http://127.0.0.1:9999/api/stop/camera_01

# ステータス確認
curl http://127.0.0.1:9999/api/status/camera_01
```

### 録画検索
```bash
# 時間範囲で検索
curl "http://127.0.0.1:9999/api/recordings/query?camera_id=camera_01&start_time=2024-12-03T10:00:00&end_time=2024-12-03T11:00:00"

# 全カメラの録画リスト
curl http://127.0.0.1:9999/api/recordings/list
```

### Web UI アクセス
```
http://127.0.0.1:9999
```

### 設定変更
```yaml
# config.yaml を編集
recording:
  segment_duration: 60  # セグメント長（秒）
  retention_days: 30    # 保持期間（日）
server:
  port: 9999           # ポート番号
```

### トラブルシューティング
```bash
# ログ確認
tail -f recorder.log

# プロセス確認
ps aux | grep recorder.py

# ポート確認
netstat -an | grep 9999

# FFmpegテスト
ffmpeg -rtsp_transport tcp -i rtsp://camera_url -t 10 test.mp4
```

---

## C# Recording Manager - よく使う操作

### アプリケーション起動
1. RecordingManager.exe をダブルクリック
2. または管理者として実行（推奨）

### 基本操作

#### 監視開始/停止
```
メインウィンドウ → [監視開始] ボタン
または
Ctrl + S (開始/停止トグル)
```

#### フォルダ追加
```
1. 設定 → 監視フォルダ → [追加]
2. フォルダパスとカメラIDを入力
3. [保存]
```

#### 録画検索
```
1. メニュー → 検索 (Ctrl + F)
2. 条件入力:
   - 日付範囲
   - カメラID
   - タグ
3. [検索]
```

### 設定ファイル場所

#### アプリケーション設定
```
%APPDATA%\RecordingManager\settings.json
```

#### 録画データベース
```
%APPDATA%\RecordingManager\recordings.json
```

#### ログファイル
```
%APPDATA%\RecordingManager\logs\recorder_YYYYMMDD.log
```

### コマンドラインオプション
```cmd
# 自動開始モード
RecordingManager.exe /autostart

# 最小化起動
RecordingManager.exe /minimize

# 設定ファイル指定
RecordingManager.exe /config:"C:\custom\settings.json"
```

### データベース操作

#### 録画情報エクスポート
```
メニュー → ファイル → エクスポート → JSON/CSV
```

#### 録画情報インポート
```
メニュー → ファイル → インポート → ファイル選択
```

#### データクリア
```
メニュー → ツール → データクリア (要確認)
```

---

## システム連携 - よくある操作

### 初期セットアップ
```bash
# 1. Python API起動
cd /mnt/d/wch/recoder
python recorder.py

# 2. 録画開始（ブラウザまたはcurl）
# http://127.0.0.1:9999 にアクセス

# 3. C# Manager起動
# RecordingManager.exe 実行

# 4. 監視フォルダ設定
# 設定画面でフォルダとカメラIDマッピング
```

### 日常運用

#### 朝の確認作業
1. Python APIステータス確認
2. C# Manager監視状態確認
3. ディスク容量確認
4. エラーログ確認

#### 録画ファイル整理
```bash
# 古いファイル削除（30日以前）
find /mnt/d/RecordingArchive -type f -mtime +30 -delete

# ディスク使用量確認
du -sh /mnt/d/RecordingArchive/*
```

### エラー対処

#### Python API再起動
```bash
# プロセス終了
pkill -f recorder.py
# または
ps aux | grep recorder.py
kill [PID]

# 再起動
python recorder.py
```

#### C# Manager再起動
```
1. タスクマネージャー起動 (Ctrl+Shift+Esc)
2. RecordingManager.exe を終了
3. RecordingManager.exe を再起動
```

#### API接続テスト
```cmd
# Windows コマンドプロンプト
curl http://127.0.0.1:9999/api/status
ping 127.0.0.1 -n 4
```

---

## 緊急時の対処

### 録画が停止した場合
1. FFmpegプロセス確認
2. RTSPストリーム接続確認
3. ディスク容量確認
4. Python API再起動

### ファイルコピーが失敗した場合
1. ターゲットディレクトリのアクセス権確認
2. ディスク容量確認
3. ネットワークドライブ接続確認
4. C# Manager再起動

### システム全体が停止した場合
1. 両アプリケーション強制終了
2. システム再起動
3. Python API起動
4. C# Manager起動
5. ログ確認

---

## パフォーマンスチューニング

### Python API
```yaml
# config.yaml
recording:
  segment_duration: 300  # 長いセグメント（5分）
  buffer_size: 8192      # バッファサイズ増加
ffmpeg:
  threads: 4             # スレッド数調整
```

### C# Manager
```json
// settings.json
{
  "PollInterval": 5000,     // ポーリング間隔を長く
  "MaxConcurrentCopies": 2, // 同時コピー数を制限
  "LogLevel": "Warning"    // ログレベルを下げる
}
```

---

## ショートカットキー

### Python Web UI
- F5: ページ更新
- Ctrl+R: 録画リスト更新

### C# Manager
- Ctrl+S: 監視開始/停止
- Ctrl+F: 検索ダイアログ
- Ctrl+O: 設定ダイアログ
- Ctrl+L: ログ表示切替
- F5: リスト更新
- Alt+F4: アプリケーション終了

---

## チェックリスト

### 日次チェック
- [ ] Python APIの稼働状態
- [ ] 録画ファイル生成確認
- [ ] C# Managerの監視状態
- [ ] エラーログ確認
- [ ] ディスク容量（80%未満）

### 週次チェック
- [ ] 古い録画ファイル削除
- [ ] ログファイルローテーション
- [ ] バックアップ実行
- [ ] パフォーマンス確認

### 月次チェック
- [ ] 設定ファイルバックアップ
- [ ] システムアップデート確認
- [ ] ディスク断片化解消
- [ ] 統計レポート作成

---
更新日: 2024-12-03