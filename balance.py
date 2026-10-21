#!/usr/bin/env python3
"""OpenRouter の残高（デポジット）を取ってきて、Notion に書き、少なければ知らせる。

- 鍵は環境変数 OPENROUTER_API_KEY（画面にも記録にも出さない）
- 1時間ごとに呼ばれる想定（呼び出し側で間隔を制御する）
- 少ないときだけ標準出力に1行出す（cron がそれを Discord に流す）

使い方:
  python3 balance.py            # 取得して Notion を更新（少なければ1行出す）
  python3 balance.py --force    # 前回から1時間たっていなくても実行
  python3 balance.py --show     # 取ってきた値だけ出す（Notion は触らない）
"""
import json
import os
import pathlib
import sys
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
STATE = HERE / "balance_state.json"
CONF = HERE / "balance_config.json"
NOTION_PAGE_TITLE = "💴 残高・使用量"
NOTION_PARENT = "3fce71bc-ecb6-8015-a491-ce32d4832219"   # 秘書ページ
DEFAULT_THRESHOLD = 1000        # 円。これを下回ったら知らせる


def load_conf():
    try:
        return json.loads(CONF.read_text(encoding="utf-8"))
    except Exception:
        return {}


def fetch_credits(key):
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/credits",
        headers={"Authorization": "Bearer " + key},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode("utf-8"))
    data = d.get("data", d)
    credits = float(data.get("total_credits", 0) or 0)
    usage = float(data.get("total_usage", 0) or 0)
    return credits, usage


def notion(key, method, url, body=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={
            "Authorization": "Bearer " + key,
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def find_or_create_page(nkey):
    out = notion(nkey, "POST", "https://api.notion.com/v1/search",
                 {"query": NOTION_PAGE_TITLE, "page_size": 5})
    for r in out.get("results", []):
        if r.get("object") == "page":
            for v in (r.get("properties") or {}).values():
                if v.get("type") == "title" and v.get("title"):
                    if "".join(x["plain_text"] for x in v["title"]).strip() == NOTION_PAGE_TITLE:
                        return r["id"]
    page = notion(nkey, "POST", "https://api.notion.com/v1/pages", {
        "parent": {"type": "page_id", "page_id": NOTION_PARENT},
        "properties": {"title": [{"text": {"content": NOTION_PAGE_TITLE}}]},
    })
    return page["id"]


def main():
    force = "--force" in sys.argv
    show = "--show" in sys.argv
    conf = load_conf()
    threshold = float(conf.get("threshold_jpy", DEFAULT_THRESHOLD))
    rate = float(conf.get("usd_jpy", 158.44))

    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        print("OPENROUTER_API_KEY が未設定です（残高を取得できません）", file=sys.stderr)
        return 2

    try:
        credits, usage = fetch_credits(key)
    except Exception as exc:
        print(f"残高を取得できませんでした（{type(exc).__name__}）", file=sys.stderr)
        return 1

    balance_usd = credits - usage
    balance_jpy = balance_usd * rate

    prev = {}
    try:
        prev = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        prev = {}
    last_ts = float(prev.get("ts", 0) or 0)
    if not (force or show) and time.time() - last_ts < 3300:   # 55分
        return 0

    delta_usd = None
    if prev.get("balance_usd") is not None:
        delta_usd = balance_usd - float(prev["balance_usd"])
    line = f"残高 ${balance_usd:,.2f}（約{balance_jpy:,.0f}円）／使用済み ${usage:,.2f}"
    if delta_usd is not None:
        line += f"／前回から {'+' if delta_usd >= 0 else '-'}${abs(delta_usd):,.2f}"

    if show:
        print(line)
        return 0

    # Notion のページを更新（アプリが読む）
    nkey = os.environ.get("NOTION_API_KEY", "")
    if nkey:
        try:
            pid = find_or_create_page(nkey)
            md = (f"# 残高・使用量（{time.strftime('%Y-%m-%d %H:%M')} UTC）\n\n"
                  f"- 残高: ${balance_usd:,.2f}（約 **{balance_jpy:,.0f}円**）\n"
                  f"- 使った累計: ${usage:,.2f}（クレジット ${credits:,.2f}）\n"
                  + (f"- 前回から: {'+' if delta_usd>=0 else '-'}${abs(delta_usd):,.2f}\n" if delta_usd is not None else "")
                  + f"\n（1時間ごとに自動更新。しきい値 {threshold:,.0f}円）")
            notion(nkey, "PATCH", f"https://api.notion.com/v1/pages/{pid}/markdown",
                   {"type": "replace_content", "replace_content": {"content": md}})
        except Exception as exc:
            print(f"Notion の更新に失敗（{type(exc).__name__}）", file=sys.stderr)

    STATE.write_text(json.dumps({"ts": time.time(), "balance_usd": balance_usd,
                                 "credits": credits, "usage": usage}), encoding="utf-8")

    if balance_jpy < threshold:
        print(f"⚠️ OpenRouter の残高が少なくなっています: 約{balance_jpy:,.0f}円（しきい値 {threshold:,.0f}円）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
