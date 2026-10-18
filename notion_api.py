import json, os, urllib.request

KEY = os.environ.get("NOTION_API_KEY")
HDR = {"Authorization": "Bearer " + (KEY or ""), "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=HDR, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:800]}

def prop(p, k):
    v = p.get(k, {})
    ty = v.get("type")
    if ty == "title":
        return "".join(x["plain_text"] for x in v["title"])
    if ty == "rich_text":
        return "".join(x["plain_text"] for x in v["rich_text"])
    if ty == "select":
        return (v["select"] or {}).get("name")
    if ty == "date":
        return (v["date"] or {}).get("start")
    if ty == "multi_select":
        return [x["name"] for x in v["multi_select"]]
    if ty == "checkbox":
        return v["checkbox"]
    return str(v.get(ty))

def query_all(ds):
    out, cur = [], None
    while True:
        body = {"page_size": 100}
        if cur:
            body["start_cursor"] = cur
        d = req("POST", "https://api.notion.com/v1/data_sources/%s/query" % ds, body)
        if "results" not in d:
            print("QUERY ERROR", ds, d)
            break
        out += d["results"]
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "review":
        rows = query_all("60242da1-b213-4118-ae82-f8782a816cb2")
        print("REVIEW count", len(rows))
        for r in rows:
            p = r["properties"]
            print("---", r["id"])
            print("  name:", prop(p, "件名"))
            print("  status:", prop(p, "状態"), "| kind:", prop(p, "種類"), "| due:", prop(p, "期限"))
            print("  comment:", repr(prop(p, "コメント")))
            print("  hermes:", repr(prop(p, "Hermes の対応")))
    elif sys.argv[1] == "tasks":
        rows = query_all("ef21b283-795e-4fec-8311-2e40c4cb0c57")
        print("TASKS count", len(rows))
        for r in rows:
            p = r["properties"]
            print("---", r["id"])
            print("  name:", prop(p, "名前"), "| status:", prop(p, "状態"), "| due:", prop(p, "期限"), "| done:", prop(p, "完了日"))
    elif sys.argv[1] == "blocks":
        d = req("GET", "https://api.notion.com/v1/blocks/%s/children?page_size=100" % sys.argv[2])
        print(json.dumps(d, ensure_ascii=False, indent=1)[:8000])
    elif sys.argv[1] == "search":
        d = req("POST", "https://api.notion.com/v1/search", {"query": sys.argv[2] if len(sys.argv) > 2 else ""})
        for r in d.get("results", []):
            ttl = ""
            if r.get("object") == "page":
                tt = r.get("properties", {}).get("title", {})
                if tt and tt.get("type") == "title":
                    ttl = "".join(x["plain_text"] for x in tt["title"])
            else:
                ttl = "".join(x["plain_text"] for x in r.get("title", []))
            print(r["object"], r["id"], repr(ttl))
