#!/usr/bin/env python3
"""秘書ページの「利用者の操作」を検知する（cron の monitor 用）。

監視する（利用者が触るものだけ）:
- ✅ 確認サインの最新「読了:」行
- 確認・提案の 状態 と コメント
- タスクの 状態（完了にした等）
- 改善メモの依頼行（`YYYY-MM-DD HH:MM 端末から:`）

前回と同じなら `NOCHANGE` とだけ出力 → AI は起きない（消費ゼロ）。
変わったときは、変わった項目と現在の状態を出力 → AI が起きて Discord に報告する。
"""
import json
import os
import pathlib
import time
import urllib.request

def jst_now():
    """日本時間の time.struct_time（実行環境が UTC でも正しく動くように）。"""
    return time.gmtime(time.time() + 9 * 3600)


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
    if t == "date":
        return (v.get("date") or {}).get("start") or ""
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


def snapshot(h):
    snap = {}
    signs = [t for t in [("".join(x.get("plain_text", "") for x in b["paragraph"]["rich_text"]).strip())
                         for b in get(h, f"/blocks/{SIGN_PAGE}/children?page_size=100").get("results", [])
                         if b.get("type") == "paragraph"] if t.startswith("読了:")]
    snap["sign"] = signs[-1] if signs else ""
    for row in post(h, f"/data_sources/{REVIEW_DS}/query", {"page_size": 100}).get("results", []):
        p = row["properties"]
        snap["r:" + row["id"]] = "|".join([txt(p.get("件名")), txt(p.get("状態")), txt(p.get("コメント"))])
    for row in post(h, f"/data_sources/{TASKS_DS}/query", {"page_size": 100}).get("results", []):
        p = row["properties"]
        snap["t:" + row["id"]] = "|".join([txt(p.get("名前")), txt(p.get("状態")), txt(p.get("完了日"))])
    reqs = [t for t in [("".join(x.get("plain_text", "") for x in b["paragraph"]["rich_text"]).strip())
                        for b in get(h, f"/blocks/{MEMO_PAGE}/children?page_size=100").get("results", [])
                        if b.get("type") == "paragraph"] if t[:4].isdigit()]
    snap["memo"] = "||".join(reqs)
    return snap


def main():
    key = load_key()
    if not key:
        print("NO_KEY " + str(int(time.time() // 3600)))
        return
    h = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

    now = snapshot(h)
    sp = state_path()
    old = {}
    try:
        old = json.loads(sp.read_text(encoding="utf-8"))
    except Exception:
        pass

    if old == now:
        print("NOCHANGE")
        return

    # 費用と夜間の歯止め（読了サイン＝利用者の明示操作は例外）
    is_sign = bool(now.get("sign")) and now.get("sign") != old.get("sign")
    nowj = jst_now()
    today = time.strftime("%Y-%m-%d", nowj)
    try:
        logp = pathlib.Path(__file__).resolve().parent / "wake_log.txt"
        wakes_today = sum(1 for ln in logp.read_text(encoding="utf-8").splitlines() if ln.startswith(today)) if logp.exists() else 0
    except Exception:
        wakes_today = 0
    night = nowj.tm_hour >= 23 or nowj.tm_hour < 7
    if not is_sign and (night or wakes_today >= 60):
        print("NOCHANGE")  # 朝まで／上限まで待つ（変化は消さずに持ち越す）
        return

    try:
        sp.write_text(json.dumps(now, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    print("CHANGED")
    try:
        logp = pathlib.Path(__file__).resolve().parent / "wake_log.txt"
        with logp.open("a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M", jst_now()) + " " +
                     ("sign" if now.get("sign") != old.get("sign") else "change") + "\n")
        lines = logp.read_text(encoding="utf-8").splitlines()[-2000:]
        logp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception:
        pass
    if now.get("sign") and now.get("sign") != old.get("sign"):
        print("読了サイン: " + now["sign"])
    for k in sorted(set(now) | set(old)):
        if k in ("sign", "memo"):
            continue
        if now.get(k) != old.get(k):
            label = "提案" if k.startswith("r:") else "タスク"
            print(f"{label}|{k[2:]}|{(old.get(k) or '（新規）')} → {now.get(k)}")
    if now.get("memo") != old.get("memo"):
        new_reqs = [r for r in now.get("memo", "").split("||") if r and r not in (old.get("memo") or "")]
        for r in new_reqs:
            print("メモ|" + r[:160])
    print("--- いまの状態 ---")
    for k, v in sorted(now.items()):
        if k.startswith("r:"):
            parts = v.split("|", 2)
            if len(parts) >= 2 and parts[1] not in ("対応済み", "見送る"):
                print("提案|" + v[:120])
        elif k.startswith("t:"):
            parts = v.split("|", 2)
            if len(parts) >= 2 and parts[1] != "完了":
                print("タスク|" + v[:120])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # 失敗は1時間に1回だけ起こす
        print(f"ERROR {type(exc).__name__} {int(time.time() // 3600)}")
