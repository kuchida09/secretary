import json, os, pathlib, urllib.request, time
KEY = os.environ.get("NOTION_API_KEY","").strip()
if not KEY:
    for p in ["/home/kuchida09/hermes-data/.hermes/notion_key","/workspace/.hermes/notion_key",str(pathlib.Path.home()/".hermes"/"notion_key")]:
        try:
            t=pathlib.Path(p).read_text().strip()
            if t: KEY=t; break
        except Exception: pass
H={"Authorization":"Bearer "+KEY,"Notion-Version":"2025-09-03","Content-Type":"application/json"}
DS="60242da1-b213-4118-ae82-f8782a816cb2"

items=[
 ("#8 落合まとめ205件に要約・研究デザインが欠けているのを揃える",
  "落合まとめ632件のうち205件（2026-09-29作成の初期バッチ）に summary_ja と study_design が無い。索引の抄録から生成して追記する。【推測】約30〜60万トークン（安いモデルで数ドル）"),
 ("#9 Google ドライブへの書き戻しが失敗している（I: が見えない）",
  "2026-10-18 23:45 の書き戻しが「Google ドライブ（I:）が見えません」で失敗。以降の変更がドライブに反映されていない可能性。Windows 側で I: を確認・再接続して1回手動実行。トークン0・無料"),
 ("#10 索引の書誌欠け（DOI 42件・第一著者 8件）を埋める",
  "index.csv 4,006件のうち DOI が空42件・第一著者（略記）が空8件。PubMed から再取得して空欄だけ埋める（既存値は触らない）。トークン0・無料"),
]

def post(path,payload):
    req=urllib.request.Request("https://api.notion.com/v1"+path,data=json.dumps(payload).encode(),headers=H,method="POST")
    return json.loads(urllib.request.urlopen(req,timeout=30).read())

created=[]
for title,comment in items:
    payload={"parent":{"type":"data_source_id","data_source_id":DS},
             "properties":{"件名":{"title":[{"text":{"content":title}}]},
                           "状態":{"select":{"name":"未確認"}},
                           "種類":{"select":{"name":"提案"}},
                           "コメント":{"rich_text":[{"text":{"content":comment}}]}}}
    r=post("/pages",payload)
    print("created",r["id"],title[:20])
    created.append(r["id"])
    time.sleep(0.5)

# read back
for pid in created:
    req=urllib.request.Request("https://api.notion.com/v1/pages/"+pid,headers=H)
    d=json.loads(urllib.request.urlopen(req,timeout=30).read())
    p=d["properties"]
    def tx(v):
        t=v["type"]
        if t=="title": return "".join(x["plain_text"] for x in v["title"])
        if t=="rich_text": return "".join(x["plain_text"] for x in v["rich_text"])
        if t=="select": return (v["select"] or {}).get("name","")
        return ""
    print("VERIFY", tx(p["状態"]), "|", tx(p["種類"]), "|", tx(p["件名"])[:30])
