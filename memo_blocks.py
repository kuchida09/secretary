import json, os, urllib.request, sys

KEY = os.environ.get("NOTION_API_KEY")
HDR = {"Authorization": "Bearer " + (KEY or ""), "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
MEMO = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"

def req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=HDR, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:800]}

d = req("GET", "https://api.notion.com/v1/blocks/%s/children?page_size=100" % MEMO)
for b in d.get("results", []):
    t = b.get("type")
    rt = (b.get(t) or {}).get("rich_text", []) if t in ("paragraph",) else []
    txt = "".join(x.get("plain_text", "") for x in rt)
    print(b["id"], "|", t, "|", txt[:160])
print("has_more", d.get("has_more"))
