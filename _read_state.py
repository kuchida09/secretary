import json, pathlib, urllib.request

def load_key():
    for p in ["/home/kuchida09/hermes-data/.hermes/notion_key", "/workspace/.hermes/notion_key",
              str(pathlib.Path.home() / ".hermes" / "notion_key")]:
        try:
            t = pathlib.Path(p).read_text().strip()
            if t:
                return t
        except Exception:
            pass
    return ""

k = load_key()
h = {"Authorization": f"Bearer {k}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def get(path):
    req = urllib.request.Request("https://api.notion.com/v1" + path, headers=h)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def post(path, payload):
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=json.dumps(payload).encode(),
                                 headers=h, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

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

print("KEY len", len(k))
print("=== REVIEW ===")
for row in post("/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print(row["id"], "|", txt(p.get("件名")), "|", txt(p.get("状態")), "|cmt:", txt(p.get("コメント")),
          "|con:", txt(p.get("Hermes の対応")))
print("=== TASKS ===")
for row in post("/data_sources/ef21b283-795e-4fec-8311-2e40c4cb0c57/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print(row["id"], "|", txt(p.get("名前")), "|", txt(p.get("状態")), "|due:", txt(p.get("期限")),
          "|done:", txt(p.get("完了日")))
print("=== MEMO BLOCKS ===")
for b in get("/blocks/3fde71bc-ecb6-81af-8624-ebb86a23bd14/children?page_size=100").get("results", []):
    ty = b.get("type")
    rt = b.get(ty, {}).get("rich_text", []) if isinstance(b.get(ty), dict) else []
    print(b["id"], "|", ty, "|", "".join(x.get("plain_text", "") for x in rt))
print("=== SIGN BLOCKS ===")
for b in get("/blocks/3fde71bc-ecb6-81f8-b7e0-f3408a247d50/children?page_size=100").get("results", []):
    ty = b.get("type")
    rt = b.get(ty, {}).get("rich_text", []) if isinstance(b.get(ty), dict) else []
    print(b["id"], "|", ty, "|", "".join(x.get("plain_text", "") for x in rt))
