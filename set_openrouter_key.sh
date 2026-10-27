#!/usr/bin/env bash
# OpenRouter の鍵を、残高チェック（secretary/balance.py）が読める場所に置く。
#
# 使い方（パソコンのターミナルで1回だけ）:
#   bash /home/kuchida09/hermes-data/secretary/set_openrouter_key.sh
#   鍵を自分で入れる場合（鍵が自動で見つからなかったとき）:
#   bash /home/kuchida09/hermes-data/secretary/set_openrouter_key.sh sk-or-（ここに鍵）
#
# 鍵の内容は画面に出しません。置いた場所だけ知らせます。
set -u

DEST="${OPENROUTER_KEY_DEST:-/home/kuchida09/hermes-data/.hermes/openrouter_key}"
key="${1:-}"

find_key() {
  # 1) すでに環境変数にある
  if [ -n "${OPENROUTER_API_KEY:-}" ]; then printf '%s' "$OPENROUTER_API_KEY"; return 0; fi
  # 2) Hermes の .env に入っている
  for f in "${HERMES_HOME:-$HOME/.hermes}/.env" "$HOME/.hermes/.env"; do
    [ -f "$f" ] || continue
    v=$(grep -E '^[[:space:]]*(export[[:space:]]+)?OPENROUTER_API_KEY[[:space:]]*=' "$f" 2>/dev/null | tail -1 \
        | sed -E 's/^[^=]*=//; s/^[[:space:]]*//; s/^["'"'"']//; s/["'"'"'][[:space:]]*$//')
    if [ -n "$v" ]; then printf '%s' "$v"; return 0; fi
  done
  # 3) auth.json / config.yaml に sk-or- で始まる鍵がある
  for f in "${HERMES_HOME:-$HOME/.hermes}/auth.json" "$HOME/.hermes/auth.json" \
           "${HERMES_HOME:-$HOME/.hermes}/config.yaml" "$HOME/.hermes/config.yaml"; do
    [ -f "$f" ] || continue
    v=$(grep -oE 'sk-or-[A-Za-z0-9._-]+' "$f" 2>/dev/null | head -1)
    if [ -n "$v" ]; then printf '%s' "$v"; return 0; fi
  done
  return 1
}

if [ -z "$key" ]; then
  key=$(find_key) || true
fi

if [ -z "$key" ]; then
  echo "鍵が見つかりませんでした。次のどちらかをお願いします。"
  echo "  A) https://openrouter.ai/settings/keys で鍵を新しく作り、下を実行する"
  echo "     bash $0 sk-or-（ここに鍵）"
  echo "  B) 鍵のありかを Discord で教える（「鍵はここにある」）"
  exit 1
fi

mkdir -p "$(dirname "$DEST")" 2>/dev/null || true
umask 077
printf '%s\n' "$key" > "$DEST" || { echo "書けませんでした: $DEST"; exit 1; }
chmod 600 "$DEST" 2>/dev/null || true
echo "OK: 鍵を $DEST に置きました（鍵の内容は表示していません）。"
echo "このあと、1時間ごとの残高更新が自動で戻ります。アプリを開き直して確認してください。"
