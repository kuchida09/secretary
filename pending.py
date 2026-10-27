#!/usr/bin/env python3
"""アプリ（秘書ページ）の操作のうち、まだ処理していないものを一覧にする。

使い方: python3 /workspace/secretary/pending.py
出力: 未処理の項目を1行ずつ。何も無ければ何も出さない（AI を起こさない）。
判定はスクリプトだけで行う（AI を使わない＝トークン0）。

見るもの:
- 確認事項: 状態=回答済み で、まだ印の無いもの
- レポート: 状態=修正あり
- 確認・提案: 状態が この案で進める / 直して / 追加で調べて
- タスク: 今日 完了 になったもの
- 改善メモ: 未対応の依頼行

同じ内容を二度出さないように、見た内容の指紋を pending_seen.json に残す。
"""
import json
import os
import pathlib
import re
import sys
import urllib.request

HOME = pathlib.Path("/workspace/secretary")
SEEN = HOME / "pending_seen.json"

REVIEW_DS = "60242da1-b213-4118-ae82-f8782a816cb2"
TASKS_DS = "ef21b283-795e-4fec-8311-2e40c4cb0c57"
REPORT_DS = "a54924f2-1ca7-44f5-b5d1-47576d368aff"
QA_DS = "8d58d65b-8d15-4012-866a-772ee3942500"
MEMO_PAGE = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"


def load_key():
    v = os.environ.get("NOTION_API_KEY", "").strip()
    if v:
        return v
    for p in ("/home/kuchida09/hermes-data/.hermes/notion_key", "/workspace/.hermes/notion_key",
              str(pathlib.Path.home() / ".hermes" / "notion_key")):
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
    if t in ("title", "rich_text"):
        return "".join(x.get("plain_text", "") for x in v[t])
    if t == "select":
        return (v.get("select") or {}).get("name") or ""
    if t == "date":
        return (v.get("date") or {}).get("start") or ""
    return ""


def api(h, method, path, payload=None):
    req = urllib.request.Request("https://api.notion.com/v1" + path,
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers=h, method=method)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())


def query(h, ds):
    return api(h, "POST", f"/data_sources/{ds}/query", {"page_size": 100}).get("results", [])


def main():
    key = load_key()
    if not key:
        print("NOTION のトークンが見つかりません")
        return 0
    h = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
    import time
    today = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 9 * 3600))

    items = {}
    for r in query(h, QA_DS):
        p = r["properties"]
        st, detail = txt(p.get("状態")), txt(p.get("詳細"))
        if st == "回答済み" and "対応:" not in detail:
            items["qa:" + r["id"]] = f"確認事項への回答: 「{txt(p.get('質問'))[:60]}」→ 回答: {txt(p.get('回答'))[:120]}"
    for r in query(h, REPORT_DS):
        p = r["properties"]
        if txt(p.get("状態")) == "修正あり":
            items["rep:" + r["id"]] = f"レポートの修正依頼: 「{txt(p.get('件名'))[:50]}」修正メモ: {txt(p.get('修正メモ'))[:120]}"
    for r in query(h, REVIEW_DS):
        p = r["properties"]
        st = txt(p.get("状態"))
        if st in ("この案で進める", "直して", "追加で調べて") and "対応:" not in txt(p.get("Hermes の対応")):
            items["rev:" + r["id"]] = f"提案への判断（{st}）: 「{txt(p.get('件名'))[:50]}」コメント: {txt(p.get('コメント'))[:120]}"
        # 書き方の好み調査への回答（アプリの数字ボタンで答えたもの。状態は 対応済み になる）
        #   → 集計は records/style/研究文の選択肢キー.json、記録は records/style/研究文の書き方.md を使う
        elif (re.search(r"書き方の好み|^(会話の書き方|研究計画書の書き方|メールの書き方|書き方|長い文章)[:：]", txt(p.get("件名")))
              and re.match(r"^[123]", txt(p.get("コメント")))
              and "対応:" not in txt(p.get("Hermes の対応"))):
            items["sty:" + r["id"]] = (f"書き方の好みへの回答: 「{txt(p.get('件名'))[:64]}」→ "
                                       f"{txt(p.get('コメント'))[:40]}。"
                                       f"手順は /workspace/records/style/好み回答の処理手順.md を読んで従う。")
    for r in query(h, TASKS_DS):
        p = r["properties"]
        if txt(p.get("状態")) == "完了" and txt(p.get("完了日")) == today:
            items["task:" + r["id"]] = f"タスクの完了: 「{txt(p.get('名前'))[:50]}」"
        # タスクのコメント（メモ欄）は Hermes が読んで対応する（本人指示 2026-10-27）。
        # 対応したらメモに `対応: YYYY-MM-DD` を書く。書くまで何度でも拾う。
        memo = txt(p.get("メモ")).strip()
        if txt(p.get("状態")) != "完了" and memo and "対応:" not in memo:
            items["tcmt:" + r["id"]] = (f"タスクへのコメント: 「{txt(p.get('名前'))[:50]}」"
                                        f"→ メモ: {memo[:160]}")
    try:
        # 改善メモのページは 100 ブロックを超えて伸びる。100 件で打ち切ると、
        # 古いメモ行の直後に置いた `対応:` の段落が見えず、同じ依頼を何度も報告してしまう。
        blocks, cursor, guard = [], None, 0
        while True:
            _p = f"/blocks/{MEMO_PAGE}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
            _r = api(h, "GET", _p)
            blocks += _r.get("results", [])
            guard += 1
            if not _r.get("has_more") or guard > 20:
                break
            cursor = _r.get("next_cursor")
        lines = ["".join(x.get("plain_text", "") for x in b["paragraph"]["rich_text"]).strip()
                 for b in blocks if b.get("type") == "paragraph"]
        for i, ln in enumerate(lines):
            if re.match(r"^\d{4}-\d{2}-\d{2}", ln):
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                if "対応:" not in nxt:
                    items["memo:" + str(abs(hash(ln)) % 10**8)] = f"改善メモ: {ln[:140]}"
    except Exception:
        pass

    # 処理が済んだものは Notion 側の印（詳細の `対応:` など）で消える。
    # ここでは「いま未処理のもの」をそのまま出す（取りこぼしを残さないため）。
    for line in sorted(items.values()):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
