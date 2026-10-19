import json, os, pathlib, urllib.request

k = os.environ.get("NOTION_API_KEY", "")
if not k:
    for p in ["/workspace/.hermes/notion_key", "/home/kuchida09/hermes-data/.hermes/notion_key"]:
        try:
            t = pathlib.Path(p).read_text().strip()
            if t:
                k = t
                break
        except Exception:
            pass
h = {"Authorization": "Bearer " + k, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}


def api(path, body=None, method="GET"):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=data, headers=h, method=method)
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
    if t == "status":
        return (v.get("status") or {}).get("name") or ""
    if t == "date":
        return (v.get("date") or {}).get("start") or ""
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
        for kk in p:
            val = txt(p[kk])
            if val:
                out.append(kk + "=" + repr(val[:300]))
        print(r["id"], "|", " ; ".join(out))

print("=== MEMO PAGE BLOCKS ===")
d = api("/blocks/3fde71bc-ecb6-81af-8624-ebb86a23bd14/children?page_size=100")
for b in d.get("results", []):
    ty = b["type"]
    rt = b.get(ty, {}).get("rich_text", [])
    s = "".join(x.get("plain_text", "") for x in rt)
    if s.strip():
        print(b["id"], "|", ty, "|", repr(s))
