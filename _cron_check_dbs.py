import json, urllib.request, os, pathlib

KEY = os.environ.get("NOTION_API_KEY", "").strip()
if not KEY:
    for p in ["/home/kuchida09/hermes-data/.hermes/notion_key", "/workspace/.hermes/notion_key",
              str(pathlib.Path.home() / ".hermes" / "notion_key")]:
        try:
            t = pathlib.Path(p).read_text().strip()
            if t: KEY = t; break
        except Exception: pass
H = {"Authorization": f"Bearer {KEY}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def txt(v):
    if not v: return ""
    t = v.get("type")
    if t in ("title", "rich_text"):
        return "".join(x.get("plain_text", "") for x in v[t])
    if t == "select": return (v.get("select") or {}).get("name") or ""
    if t == "date": return (v.get("date") or {}).get("start") or ""
    return ""

def post(path, payload):
    req = urllib.request.Request("https://api.notion.com/v1" + path,
                                 data=json.dumps(payload).encode(), headers=H, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

REVIEW_DS = "60242da1-b213-4118-ae82-f8782a816cb2"
TASKS_DS = "ef21b283-795e-4fec-8311-2e40c4cb0c57"

print("==== 確認・提案 ====")
for row in post(f"/data_sources/{REVIEW_DS}/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print(" |", txt(p.get("件名")), "|", txt(p.get("状態")), "| コメント:", txt(p.get("コメント"))[:60])

print("==== タスク ====")
for row in post(f"/data_sources/{TASKS_DS}/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print(" |", txt(p.get("名前")), "|", txt(p.get("状態")), "| 完了日:", txt(p.get("完了日")))
