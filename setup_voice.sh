#!/usr/bin/env bash
# Hermes 音声セットアップ（Discord通話＝運転中の会話用）
# 使い方: WSL のターミナルで  bash /home/kuchida09/hermes-data/secretary/setup_voice.sh
set -u
log(){ echo; echo "=== $* ==="; }

log "1/6 Hermes の確認"
if ! command -v hermes >/dev/null 2>&1; then
  echo "hermes が見つかりません。PATH を確認してください（中断）"; exit 1
fi
hermes --version

log "2/6 依存の導入（Discord音声・DAVE暗号化・ローカル音声認識）"
if [ -d "$HOME/.hermes/hermes-agent" ]; then
  ( cd "$HOME/.hermes/hermes-agent" && uv pip install -e ".[messaging,voice]" ) || echo "messaging/voice の導入に失敗"
else
  echo "hermes-agent のソースが見つからないのでスキップ（インストーラ版の可能性）"
fi
python3 -c "import pm; pm.sync_venv(['stt-whisper'], explicit=True)" 2>/dev/null \
  || pip install -U faster-whisper || echo "faster-whisper の導入に失敗"

log "3/6 設定（聞き取り=ローカルWhisper / 読み上げ=無料のEdge TTS）"
hermes config set stt.enabled true
hermes config set stt.provider local
hermes config set stt.local.model small
hermes config set tts.provider edge

log "4/6 リアルタイム音声プラグイン hermes-talk"
hermes plugins install TheSmokeDev/hermes-talk --enable || echo "プラグイン導入に失敗（後で再実行可）"
pip install "hermes-talk[audio]" 2>/dev/null || echo "hermes-talk の音声依存に失敗（後で再実行可）"

log "5/6 動作確認"
hermes talk doctor 2>&1 | head -40

log "6/6 完了"
cat <<'EOS'
次: Discord のテキスト欄で  /restart  を打って反映してください。
そのあと ボイスチャンネル「一般」に入り、テキスト欄で  /voice join  を試します。

音が出ない／聞こえないときは、WSL で次を1回だけ:
  sudo apt update && sudo apt install -y libopus0 ffmpeg
EOS
