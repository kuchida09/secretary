#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/workspace/secretary")
from notion_ds import req
import re

TODAY = "2026-10-20"

# page_id -> dict of updates
UPD = {
 "3dee71bc-ecb6-81a3-88fa-c425a025f11d": {  # ①
    "直近検索日": TODAY, "連続0件回数": 1,
    "note": "2026-10-20(Hermes版・毎日): edat 2026/10/06-10/20(直近2週間)で①解剖学的構造認識AIに該当する新規0件(候補はHCC precision oncologyレビュー、CRLM予後予測MLモデルで①非該当)。3ヶ月(2026/07/01〜)まで遡及したが解剖構造認識AIの新規なし。連続0件回数1。"},
 "3dee71bc-ecb6-8194-957b-eef7fd699502": {  # ③
    "直近検索日": TODAY, "直近発見日": TODAY, "連続0件回数": 0,
    "note": "2026-10-20(Hermes版・毎日): edat 2026/10/06-10/20で新規1件(RUQ超音波のマルチタスクVLM、16所見分類+レポート生成+胆嚢摘出術要否予測、Nat Commun)。ICG関連の非AI研究2件は不採用。連続0件回数0。"},
 "3dee71bc-ecb6-81c5-a13a-d657713bdbd2": {  # ⑤
    "直近検索日": TODAY, "連続0件回数": 2,
    "note": "2026-10-20(Hermes版・毎日): edat 2026/10/06-10/20で新規0件(該当は神経ブロック研究と症例報告のみ、AIなし)。競合著者ウォッチ(Marcelo FJ/Mita K/Sato)は新著なし。連続0件回数2。"},
 "3dee71bc-ecb6-81a4-9d46-f4a7b6f324fe": {  # ⑨
    "直近検索日": TODAY, "直近発見日": TODAY, "連続0件回数": 0,
    "note": "2026-10-20(Hermes版・毎日): edat 2026/10/06-10/20で新規6件(手術動画auto-segmentation、CLASSICA-ORリアルタイムAI意思決定支援の質的研究、トロッカー挿入時の腹壁層セグメンテーション[DeepLabV3+]、大腸癌外科AIレビュー、FDA認可外科AI機器の体系解析、外科研究ワークフローAIフレームワーク)。連続0件回数0。"},
}


def txt(prop):
    v = prop.get("rich_text") or []
    return "".join(x["plain_text"] for x in v)


for pid, u in UPD.items():
    page = req("/pages/%s" % pid)
    if "_error" in page:
        print("ERR get", pid, page); continue
    props = page["properties"]
    old = txt(props.get("備考", {}))
    newnote = (old + "\n" + u["note"]) if old else u["note"]
    body = {"properties": {
        "直近検索日": {"date": {"start": u["直近検索日"]}},
        "連続0件回数": {"number": u["連続0件回数"]},
        "備考": {"rich_text": [{"text": {"content": newnote[-1900:]}}]},
    }}
    if "直近発見日" in u:
        body["properties"]["直近発見日"] = {"date": {"start": u["直近発見日"]}}
    r = req("/pages/%s" % pid, "PATCH", body)
    print(pid, "OK" if "_error" not in r else r)
