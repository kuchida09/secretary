#!/usr/bin/env python3
"""スキル一覧を出す（LLMを使わない）。

使い方:
  python3 /workspace/secretary/skills_catalog.py          … Discord に貼れる短い形（既定）
  python3 /workspace/secretary/skills_catalog.py --full   … 説明つきの長い形

利用者が「スキル名」と言ったら、この出力をそのまま貼る（LLMで作り直さない）。
中身は skills_catalog.json を直せば変わる。
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "skills_catalog.json"


def short(text, limit=46):
    t = (text or "").replace("\n", " ")
    for cut in ("。", "／", "、"):          # 最初の区切りまでで切る
        if cut in t[:limit]:
            t = t.split(cut)[0]
            break
    return t[:limit]


def main():
    full = "--full" in sys.argv
    try:
        d = json.loads(DATA.read_text(encoding="utf-8"))
    except Exception as exc:
        print("スキル一覧を読めませんでした（skills_catalog.json）:", type(exc).__name__)
        return 1
    print(f"【スキル一覧】（{d.get('updated','')} 更新）")
    print(f"モデル: {d.get('model','')}")
    for g in d.get("groups", []):
        print()
        print("■ " + g.get("title", ""))
        for it in g.get("items", []):
            if full:
                print(f"・{it.get('name','')}")
                print(f"    何をする: {it.get('what','')}")
                print(f"    呼び方: {it.get('how','')}")
                print(f"    費用: {it.get('cost','')}")
                print(f"    置き場所: {it.get('where','')}")
            else:
                name = it.get("name", "")
                what = short(it.get("what", ""))
                how = it.get("how", "")
                cost = it.get("cost", "")
                line = f"・{name} — {what}"
                if how and how != "-":
                    line += f"／呼び方: {how}"
                if cost and cost != "-":
                    line += f"／費用: {cost}"
                print(line)
    if not full:
        print()
        print("（詳しくは `--full`。追加・修正は skills_catalog.json）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
