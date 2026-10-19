import json, pathlib, urllib.request, os
k = os.environ.get("NOTION_API_KEY", "")
if not k:
    for p in ["/workspace/.hermes/notion_key", "/home/kuchida09/hermes-data/.hermes/notion_key"]:
        try:
            t = pathlib.Path(p).read_text().strip()
            if t:
                k = t; break
        except Exception:
            pass
h = {"Authorization": f"Bearer {k}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
def post(path, payload):
    req = urllib.request.Request("https://api.notion.com/v1"+path, data=json.dumps(payload).encode(), headers=h, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())
def txt(v):
    if not v: return ""
    t=v.get("type")
    if t=="title": return "".join(x.get("plain_text","") for x in v["title"])
    if t=="rich_text": return "".join(x.get("plain_text","") for x in v["rich_text"])
    if t=="select": return (v.get("select") or {}).get("name") or ""
    if t=="date": return (v.get("date") or {}).get("start") or ""
    return ""
print("=== QA (8d58d65b) ===")
for row in post("/data_sources/8d58d65b-8d15-4012-866a-772ee3942500/query", {"page_size":100}).get("results",[]):
    p=row["properties"]
    print(row["id"], "|", txt(p.get("質問")), "|", txt(p.get("状態")), "|回答:", txt(p.get("回答")))
print("=== REPORT (a54924f2) ===")
for row in post("/data_sources/a54924f2-1ca7-44f5-b5d1-47576d368aff/query", {"page_size":50}).get("results",[]):
    p=row["properties"]
    print(row["id"], "|", txt(p.get("件名")), "|", txt(p.get("状態")), "|修正:", txt(p.get("修正メモ")))
