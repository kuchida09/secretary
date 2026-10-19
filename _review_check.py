import json, os, urllib.request

KEY = os.environ["NOTION_API_KEY"]
H = {"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def api(path, body=None, method="GET"):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=data, headers=H, method=method)
    return json.load(urllib.request.urlopen(req))

def txt(v):
    ty = v.get("type")
    if ty == "title": return "".join(x["plain_text"] for x in v["title"])
    if ty == "rich_text": return "".join(x["plain_text"] for x in v["rich_text"])
    if ty == "select": return (v["select"] or {}).get("name")
    if ty == "date": return json.dumps(v["date"])
    if ty == "relation": return ",".join(x["id"] for x in v["relation"])
    if ty == "checkbox": return str(v["checkbox"])
    return ""

print("=== REVIEW DS ===")
d = api("/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 50}, "POST")
for r in d.get("results", []):
    p = r["properties"]
    print("--- " + r["id"])
    for k in p:
        print("   " + k + " = " + repr(txt(p[k])))

print("")
print("=== TASKS DS ===")
d = api("/data_sources/ef21b283-795e-4fec-8311-2e40c4cb0c57/query", {"page_size": 100}, "POST")
for r in d.get("results", []):
    p = r["properties"]
    name = ""
    for k in p:
        if p[k].get("type") == "title":
            name = txt(p[k])
    print(r["id"][:8] + " | " + name + " | " + txt(p.get("状態", {})) + " | " + txt(p.get("完了日", {})) + " | " + txt(p.get("期限", {})))
