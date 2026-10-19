import json, urllib.request, os

KEY = os.environ["NOTION_API_KEY"]
H = {"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def get(url):
    req = urllib.request.Request(url, headers=H)
    return json.load(urllib.request.urlopen(req))

def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=H, method="POST")
    return json.load(urllib.request.urlopen(req))

def rt(p, k):
    v = p.get(k, {})
    t = v.get("type")
    if t == "select": return (v["select"] or {}).get("name")
    if t == "title": return "".join(x["plain_text"] for x in v["title"])
    if t == "rich_text": return "".join(x["plain_text"] for x in v["rich_text"])
    if t == "date": return (v["date"] or {}).get("start")
    if t == "multi_select": return [x["name"] for x in v["multi_select"]]
    return None

def dump_children(pid, depth=0, limit=100):
    d = get(f"https://api.notion.com/v1/blocks/{pid}/children?page_size={limit}")
    out = []
    for b in d["results"]:
        t = b["type"]
        block = b[t]
        text = "".join(x["plain_text"] for x in block.get("rich_text", []))
        out.append((b["id"], t, text))
        if b.get("has_children"):
            for cid, ct, ct2 in dump_children(b["id"], depth+1, limit):
                out.append((cid, "  " + ct, "    " + ct2))
    return out

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "props":
        d = post("https://api.notion.com/v1/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 100})
        for row in d["results"]:
            p = row["properties"]
            print(row["id"])
            print("  件名:", rt(p, "件名") or rt(p, "名前"))
            print("  状態:", rt(p, "状態"), "| 種類:", rt(p, "種類"), "| コメント:", repr(rt(p, "コメント")))
            print("  対応:", repr(rt(p, "Hermes の対応")), "| edited:", row.get("last_edited_time"))
        print("has_more", d.get("has_more"))
    elif sys.argv[1] == "children":
        for cid, t, text in dump_children(sys.argv[2]):
            print(cid, t, "|", text[:300])
    elif sys.argv[1] == "page":
        for pid in sys.argv[2:]:
            d = get(f"https://api.notion.com/v1/pages/{pid}")
            print(pid, "| created:", d.get("created_time"), d.get("created_by"), "| edited_by:", d.get("last_edited_by"))
            for cid, t, text in dump_children(pid):
                print("   ", t, "|", text[:400])
    elif sys.argv[1] == "tasks":
        d = post("https://api.notion.com/v1/data_sources/ef21b283-795e-4fec-8311-2e40c4cb0c57/query", {"page_size": 100})
        for row in d["results"]:
            p = row["properties"]
            print(row["id"], "|", rt(p, "名前") or rt(p, "件名"), "|", rt(p, "状態"), "|", rt(p, "期限"), "|", rt(p, "完了日"))
        print("has_more", d.get("has_more"))
