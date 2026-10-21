import json, os, urllib.request
KEY = os.environ["NOTION_API_KEY"]
DS = "8f49d8fb-3ffd-4e76-ac63-6ce14337e2ad"

def call(url, payload=None, method="GET"):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03",
                 "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))

d = call(f"https://api.notion.com/v1/data_sources/{DS}")
print("title:", d.get("title"))
for name, p in d["properties"].items():
    extra = ""
    if p["type"] == "select":
        extra = [o["name"] for o in p["select"]["options"]]
    elif p["type"] == "status":
        extra = [o["name"] for o in p["status"]["options"]]
    print(p["type"], "|", name, "|", extra)
print("database_parent:", d.get("parent"))
print("db_id:", d.get("database_id"), d.get("id"))
