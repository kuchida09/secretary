import json, os, urllib.request

KEY = os.environ["NOTION_API_KEY"]
H = {"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=H, method=method)
    return json.load(urllib.request.urlopen(r))

def txt(v):
    if not v: return ""
    t = v.get("type")
    if t == "title": return "".join(x["plain_text"] for x in v["title"])
    if t == "rich_text": return "".join(x["plain_text"] for x in v["rich_text"])
    if t == "select": return (v["select"] or {}).get("name","")
    if t == "date": return (v["date"] or {}).get("start","")
    return ""

print("=== REVIEW DB ===")
d = req("POST", "https://api.notion.com/v1/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 100})
for r in d.get("results", []):
    p = r["properties"]
    print(r["id"], "|", txt(p.get("件名")), "|状態:", txt(p.get("状態")), "|コメント:", repr(txt(p.get("コメント"))), "|対応:", repr(txt(p.get("Hermes の対応"))))

print("=== SEARCH ===")
s = req("POST", "https://api.notion.com/v1/search", {"query": ""})
for r in s.get("results", []):
    if r.get("object") == "page":
        p = r.get("properties", {})
        title = ""
        for k, v in p.items():
            if v.get("type") == "title":
                title = "".join(x["plain_text"] for x in v["title"])
        print("PAGE", r["id"], "|", title, "| parent:", r.get("parent"))
    else:
        print(r.get("object"), r["id"], "|", "".join(x.get("plain_text","") for x in (r.get("title") or [])))
