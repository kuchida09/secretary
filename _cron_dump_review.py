import json, os, urllib.request

KEY = os.environ.get("NOTION_API_KEY", "")
print("keylen", len(KEY))
H = {"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}


def api(path, body=None, method="GET"):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=data, headers=H, method=method)
    return json.load(urllib.request.urlopen(req))


def txt(v):
    t = v.get("type")
    if t == "title":
        return "".join(x["plain_text"] for x in v["title"])
    if t == "rich_text":
        return "".join(x["plain_text"] for x in v["rich_text"])
    if t == "select":
        return (v["select"] or {}).get("name", "")
    if t == "date":
        return json.dumps(v["date"])
    if t == "relation":
        return ",".join(x["id"] for x in v["relation"])
    return ""


for name, ds in [("REVIEW", "60242da1-b213-4118-ae82-f8782a816cb2"),
                 ("QA", "8d58d65b-8d15-4012-866a-772ee3942500"),
                 ("REPORT", "a54924f2-1ca7-44f5-b5d1-47576d368aff"),
                 ("TASKS", "ef21b283-795e-4fec-8311-2e40c4cb0c57")]:
    print("=== " + name + " ===")
    d = api("/data_sources/" + ds + "/query", {"page_size": 100}, "POST")
    for r in d.get("results", []):
        p = r["properties"]
        out = []
        for k in p:
            val = txt(p[k])
            if val:
                out.append(k + "=" + repr(val))
        print(r["id"], "|", " ; ".join(out))

# memo page children
print("=== MEMO PAGE BLOCKS ===")
d = api("/blocks/3fde71bc-ecb6-81af-8624-ebb86a23bd14/children?page_size=100")
for b in d.get("results", []):
    ty = b["type"]
    rt = b.get(ty, {}).get("rich_text", [])
    s = "".join(x.get("plain_text", "") for x in rt)
    if s.strip():
        print(b["id"], "|", ty, "|", repr(s))
