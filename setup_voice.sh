#!/usr/bin/env bash
# Hermes の音声通話（Discord）の下ごしらえと診断 v2
# 使い方: WSL のターミナルで  bash /home/kuchida09/hermes-data/secretary/setup_voice.sh
#
# 2026-10-27 修正（v2）:
#   v1 は /usr/bin/python3 を見てしまい、本体の環境を測れていなかった。
#   本体の venv（~/.hermes/hermes-agent/.venv）を先に探し、そこへ入れる。
set -u
log(){ echo; echo "=== $* ==="; }

log "1/7 Hermes の確認"
if ! command -v hermes >/dev/null 2>&1; then
  echo "hermes が見つかりません。PATH を確認してください（中断）"; exit 1
fi
hermes --version
INST="$HOME/.hermes/hermes-agent"

log "2/7 Hermes 本体の Python を特定する"
HERMES_PY=""
for c in "$INST/.venv/bin/python" "$INST/venv/bin/python" "$INST/.venv/bin/python3"; do
  if [ -x "$c" ]; then HERMES_PY="$c"; break; fi
done
if [ -z "$HERMES_PY" ]; then
  HB=$(command -v hermes)
  CAND=$(head -1 "$HB" 2>/dev/null | sed 's/^#!//' | tr -d '\r')
  case "$CAND" in *python*) [ -x "$CAND" ] && HERMES_PY="$CAND" ;; esac
fi
[ -z "$HERMES_PY" ] && HERMES_PY=$(command -v python3)
echo "hermes の本体: $INST"
echo "python       : $HERMES_PY"
"$HERMES_PY" -V 2>&1

diag(){
  "$HERMES_PY" - <<'PY'
import importlib
for m in ("discord", "nacl", "davey", "faster_whisper"):
    try:
        mod = importlib.import_module(m)
        print("OK ", m, getattr(mod, "__version__", ""))
    except Exception as e:
        print("NG ", m, type(e).__name__, e)
PY
}

log "3/7 いまの状態（本体の環境で確認）"
diag

log "4/7 通話用ライブラリ（Discord の暗号化 DAVE 対応に必要）"
if command -v uv >/dev/null 2>&1; then
  uv pip install --python "$HERMES_PY" -U "discord.py[voice]>=2.7.1" || echo "uv での更新に失敗（続行）"
fi
"$HERMES_PY" -m pip install -U "discord.py[voice]>=2.7.1" 2>/dev/null || echo "pip での更新に失敗（続行）"

log "5/7 ローカル音声認識と日本語の設定"
if command -v uv >/dev/null 2>&1; then
  uv pip install --python "$HERMES_PY" -U faster-whisper || echo "uv での導入に失敗（続行）"
fi
"$HERMES_PY" -m pip install -U faster-whisper 2>/dev/null || true
"$HERMES_PY" -c "import pm; pm.sync_venv(['stt-whisper'], explicit=True)" 2>/dev/null || true
hermes config set stt.enabled true
hermes config set stt.provider local --force
hermes config set stt.local.model small
hermes config set stt.language ja --force
hermes config set stt.local.language ja
hermes config set tts.provider edge

log "6/7 もう一度確認"
diag
hermes config get stt 2>&1 | head -14

log "7/7 完了"
cat <<'EOS'
次にやること:
1) Discord のテキスト欄で  /restart
2) ボイスチャンネル「一般」に入る → /voice join → 入ってすぐ「ヘルメス、聞こえる？」とはっきり話す
3) 聞き取れていれば #システム に文字起こしが出ます（echo_transcripts が有効）。それが出れば成功の証拠です。

まだダメなときは、上の「3/7」「6/7」と、次の出力を貼ってください:
  tail -n 60 ~/.hermes/logs/gateway.log

音が鳴らない・読み上げが変なとき:
  sudo apt install -y libopus0 ffmpeg
EOS
