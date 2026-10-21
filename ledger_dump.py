import json, os, urllib.request

KEY = os.environ["NOTION_API_KEY"]
DS = "d2346174-f4b7-43fa-aa46-8637406e8cdf"

def query(payload):
    req = urllib.request.Request(
        f"https://api.notion.com/v1/data_sources/{DS}/query",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + KEY,
                 "Notion-Version": "2025-09-03",
                 "Content-Type": "application/json"},
        method="POST")
    return json.load(urllib.request.urlopen(req))

res, cursor = [], None
while True:
    p = {"page_size": 100}
    if cursor:
        p["start_cursor"] = cursor
    d = query(p)
    res += d["results"]
    if not d.get("has_more"):
        break
    cursor = d["next_cursor"]

def flat(v):
    t = v["type"]
    if t == "title":
        return "".join(x["plain_text"] for x in v["title"])
    if t == "rich_text":
        return "".join(x["plain_text"] for x in v["rich_text"])
    if t == "select":
        return (v["select"] or {}).get("name")
    if t == "number":
        return v["number"]
    if t == "date":
        return (v["date"] or {}).get("start")
    if t == "formula":
        f = v["formula"]
        return f.get(f["type"]) if f["type"] in f else f["type"]
    return None

out = []
for r in res:
    row = {"id": r["id"]}
    for k, v in r["properties"].items():
        row[k] = flat(v)
    out.append(row)

json.dump(out, open("/workspace/secretary/ledger.json", "w"), ensure_ascii=False, indent=1)
for row in out:
    print(json.dumps(row, ensure_ascii=False))
