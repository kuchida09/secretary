import json, os, urllib.request

KEY = os.environ["NOTION_API_KEY"]
H = {"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def api(path, body=None, method="GET"):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=data, headers=H, method=method)
    return json.load(urllib.request.urlopen(req))

def txt(rt):
    return "".join(x.get("plain_text", "") for x in rt)

for pid, label in [("3fde71bc-ecb6-81af-8624-ebb86a23bd14", "IMPROVE MEMO"),
                   ("3fde71bc-ecb6-81f8-b7e0-f3408a247d50", "READ SIGN")]:
    print("===== " + label + " (" + pid + ") =====")
    d = api("/blocks/" + pid + "/children?page_size=100")
    for b in d.get("results", []):
        t = b.get("type")
        rt = b.get(t, {}).get("rich_text", []) if isinstance(b.get(t), dict) else []
        print(b["id"] + " [" + t + "] " + repr(txt(rt)))
    print("has_more:", d.get("has_more"))
    print("")
