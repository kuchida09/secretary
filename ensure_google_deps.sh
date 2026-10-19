#!/bin/sh
# 端末の箱は毎回作り直されるので、Google の道具とトークンを毎回そろえる。
#  - Google のライブラリ: 永続する /workspace/.venv に入れる
#  - トークン: 永続する /workspace/.hermes/google_token.json を $HOME/.hermes に戻す
# 使い方: PY=$(sh /workspace/secretary/ensure_google_deps.sh)  → その python で道具を実行
set -e
V=/workspace/.venv
if [ ! -x "$V/bin/python" ]; then
  python3 -m venv "$V" >/dev/null 2>&1
fi
if ! "$V/bin/python" -c "import googleapiclient" 2>/dev/null; then
  "$V/bin/pip" install -q --disable-pip-version-check google-api-python-client google-auth-oauthlib google-auth-httplib2
fi
mkdir -p "$HOME/.hermes"
for f in google_token.json google_client_secret.json; do
  if [ ! -f "$HOME/.hermes/$f" ] && [ -f "/workspace/.hermes/$f" ]; then
    cp "/workspace/.hermes/$f" "$HOME/.hermes/$f"
  fi
done
echo "$V/bin/python"
