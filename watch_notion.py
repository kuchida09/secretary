#!/usr/bin/env python3
"""秘書ページの変化を検知するためのダイジェスト（cron の monitor 用）。

出力が前回と同じならエージェントは起きない。変わったときだけ起こす。
決定的な出力にするため、時刻や last_edited_time は入れない。
"""
import json
import os
import pathlib
import time
import urllib.request

REVIEW_DS = "60242da1-b213-4118-ae82-f8782a816cb2"
TASKS_DS = "ef21b283-795e-4fec-8311-2e40c4cb0c57"
MEMO_PAGE = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"
KEY_PATHS = [
    "/home/kuchida09/hermes-data/.hermes/notion_key",
    "/workspace/.hermes/notion_key",
    str(pathlib.Path.home() / ".hermes" / "notion_key"),
]


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


def main():
    key = load_key()
    if not key:
        print("NO_KEY " + str(int(time.time() // 3600)))
        return
    h = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
    lines = []

    for tag, ds in (("R", REVIEW_DS), ("T", TASKS_DS)):
        req = urllib.request.Request(
            f"https://api.notion.com/v1/data_sources/{ds}/query",
            data=b'{"page_size":100}', headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            for row in json.loads(r.read()).get("results", []):
                p = row["properties"]
                name = txt(p.get("件名") or p.get("名前"))
                state = txt(p.get("状態"))
                comment = txt(p.get("コメント"))
                edit = (row.get("last_edited_time") or "")[:16]
                # 名前と状態とコメントと最終更新で、利用者の操作を検知する
                lines.append(f"{tag}|{row['id'][:8]}|{name[:28]}|{state}|{comment[:40]}|{edit}")

    req = urllib.request.Request(
        f"https://api.notion.com/v1/blocks/{MEMO_PAGE}/children?page_size=100", headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        for b in json.loads(r.read()).get("results", []):
            if b.get("type") == "paragraph":
                t = "".join(x.get("plain_text", "") for x in b["paragraph"]["rich_text"])
                if t[:4].isdigit() and "-" in t[:10]:
                    lines.append("M|" + t[:120])

    print("\n".join(sorted(lines)))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # 失敗は1時間ごとに1回だけ起こして気づけるようにする
        print(f"ERROR {type(exc).__name__} {int(time.time() // 3600)}")
