#!/usr/bin/env python3
"""読了サイン方式の差分検知（cron の monitor 用）。

- 5分/1分ごとに「✅ 確認サイン」ページを見る。
- 新しい `読了: ...` の行が増えていれば、その行と現在の状態を出力する → AI が起きる。
- 増えていなければ `NOCHANGE` とだけ出力 → AI は起きない（消費ゼロ）。

途中で編集している間に判断してしまう事故を防ぐため、**判断の合図は「読了」行だけ**。
"""
import json
import os
import pathlib
import time
import urllib.request

REVIEW_DS = "60242da1-b213-4118-ae82-f8782a816cb2"
TASKS_DS = "ef21b283-795e-4fec-8311-2e40c4cb0c57"
MEMO_PAGE = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"
SIGN_PAGE = "3fde71bc-ecb6-81f8-b7e0-f3408a247d50"
KEY_PATHS = [
    "/home/kuchida09/hermes-data/.hermes/notion_key",
    "/workspace/.hermes/notion_key",
    str(pathlib.Path.home() / ".hermes" / "notion_key"),
]


def state_path():
    try:
        p = pathlib.Path(__file__).resolve().parent / "watch_notion_state.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    except Exception:
        return pathlib.Path("/tmp/watch_notion_state.json")


def load_key():
    v = os.environ.get("NOTION_API_KEY", "").strip()
    if v:
        return v
    for p in KEY_PATHS:
        try:
            t = pathlib.Path(p).read_text(encoding="utf-8").strip()
            if t:
                return t
        except Exception:
            continue
    return ""


def txt(v):
    if not v:
        return ""
    t = v.get("type")
    if t == "title":
        return "".join(x.get("plain_text", "") for x in v["title"])
    if t == "rich_text":
        return "".join(x.get("plain_text", "") for x in v["rich_text"])
    if t == "select":
        return (v.get("select") or {}).get("name") or ""
    return ""


def get(h, path):
    req = urllib.request.Request("https://api.notion.com/v1" + path, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def post(h, path, payload):
    req = urllib.request.Request("https://api.notion.com/v1" + path,
                                 data=json.dumps(payload).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def para_texts(blocks):
    out = []
    for b in blocks:
        if b.get("type") == "paragraph":
            out.append("".join(x.get("plain_text", "") for x in b["paragraph"]["rich_text"]).strip())
    return out


def main():
    key = load_key()
    if not key:
        print("NO_KEY " + str(int(time.time() // 3600)))
        return
    h = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

    signs = [t for t in para_texts(get(h, f"/blocks/{SIGN_PAGE}/children?page_size=100").get("results", []))
             if t.startswith("読了:")]
    latest = signs[-1] if signs else ""

    sp = state_path()
    seen = ""
    try:
        seen = json.loads(sp.read_text(encoding="utf-8")).get("sign", "")
    except Exception:
        pass

    if not latest or latest == seen:
        print("NOCHANGE")
        return

    try:
        sp.write_text(json.dumps({"sign": latest, "at": time.strftime("%Y-%m-%d %H:%M")}), encoding="utf-8")
    except Exception:
        pass

    print("SIGN " + latest)
    print("--- いまの状態 ---")
    for tag, ds in (("提案", REVIEW_DS), ("タスク", TASKS_DS)):
        rows = post(h, f"/data_sources/{ds}/query", {"page_size": 100}).get("results", [])
        for row in rows:
            p = row["properties"]
            name = txt(p.get("件名") or p.get("名前"))
            state = txt(p.get("状態"))
            comment = txt(p.get("コメント"))
            if tag == "提案" and state in ("対応済み", "見送る") and not comment:
                continue
            if tag == "タスク" and state == "完了":
                continue
            print(f"{tag}|{name[:34]}|{state}|{comment[:60]}")
    memos = [t for t in para_texts(get(h, f"/blocks/{MEMO_PAGE}/children?page_size=100").get("results", []))
             if t[:4].isdigit()]
    for m in memos[-5:]:
        print("メモ|" + m[:120])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # 失敗は1時間に1回だけ起こす
        print(f"ERROR {type(exc).__name__} {int(time.time() // 3600)}")
