import json, os, urllib.request
KEY = os.environ["NOTION_API_KEY"]
created = json.load(open("/workspace/secretary/notion_created.json"))
def get(url):
    r = urllib.request.Request(url, headers={"Authorization": "Bearer " + KEY,
        "Notion-Version": "2025-09-03"})
    return json.load(urllib.request.urlopen(r))
for pmid, pid, url in created:
    p = get(f"https://api.notion.com/v1/pages/{pid}")
    pr = p["properties"]
    t = pr["タイトル"]["title"][0]["plain_text"][:60]
    q = pr["検索クエリ"]["rich_text"][0]["plain_text"] if pr["検索クエリ"]["rich_text"] else ""
    st = (pr["ステータス"]["select"] or {}).get("name")
    print(pmid, "|", st, "|", q, "|", t)
