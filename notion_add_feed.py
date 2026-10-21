import json, os, urllib.request
KEY = os.environ["NOTION_API_KEY"]
DS = "8f49d8fb-3ffd-4e76-ac63-6ce14337e2ad"
IDX = "/workspace/research/80_AI作業場/knowledge/literature/daily-feed/index.csv"
import csv

rows = {}
with open(IDX, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["date_added"] == "2026-10-21":
            rows[r["pmid"]] = r

PROJ = {"42845713": ["外科AI全般", "eTEP/NVB"]}

def req(url, payload=None, method="GET"):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03",
                 "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))

created = []
for pmid, r in rows.items():
    props = {
        "タイトル": {"title": [{"text": {"content": r["title"]}}]},
        "ステータス": {"select": {"name": "未読"}},
        "関連プロジェクト": {"multi_select": [{"name": n} for n in PROJ.get(pmid, ["外科AI全般"])]},
        "誌名": {"rich_text": [{"text": {"content": r["journal"]}}]},
        "検索クエリ": {"rich_text": [{"text": {"content": "⑨外科一般×AI(edat 直近2週間)"}}]},
        "URL": {"url": r["url"]},
        "要約": {"rich_text": [{"text": {"content": r["summary_ja"]}}]},
        "PMID/DOI": {"rich_text": [{"text": {"content": f"PMID: {pmid} / DOI: {r['doi'] or 'なし'}"}}]},
        "著者": {"rich_text": [{"text": {"content": r["first_author"] + " ほか"}}]},
    }
    body = {"parent": {"database_id": "73030fec-90a9-4b83-8a6a-a0b97564d97a"},
            "properties": props}
    try:
        p = req("https://api.notion.com/v1/pages", body, "POST")
        created.append((pmid, p["id"], p["url"]))
        print("OK", pmid, p["id"])
    except urllib.error.HTTPError as e:
        print("ERR", pmid, e.read().decode()[:400])

json.dump(created, open("/workspace/secretary/notion_created.json", "w"))
