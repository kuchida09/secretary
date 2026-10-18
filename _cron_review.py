import json, urllib.request

key = open('/workspace/.hermes/notion_key').read().strip()
H = {"Authorization": "Bearer " + key, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}


def post(path, payload):
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=json.dumps(payload).encode(), headers=H, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def get(path):
    req = urllib.request.Request("https://api.notion.com/v1" + path, headers=H)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def txt(v):
    if not v:
        return ""
    t = v.get("type")
    if t == "title":
        return "".join(x["plain_text"] for x in v["title"])
    if t == "rich_text":
        return "".join(x["plain_text"] for x in v["rich_text"])
    if t == "select":
        return (v.get("select") or {}).get("name") or ""
    if t == "date":
        return (v.get("date") or {}).get("start") or ""
    return ""


print("########## REVIEW DB ##########")
r = post("/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 50})
for p in r["results"]:
    pr = p["properties"]
    print("=== PAGE", p["id"], "| url:", p.get("url"))
    for k, v in pr.items():
        val = txt(v)
        if val:
            print("   ", k, "=", repr(val))

print()
print("########## TASKS DB ##########")
r = post("/data_sources/ef21b283-795e-4fec-8311-2e40c4cb0c57/query", {"page_size": 100})
for p in r["results"]:
    pr = p["properties"]
    print("=== TASK", p["id"])
    for k, v in pr.items():
        val = txt(v)
        if val:
            print("   ", k, "=", repr(val))
