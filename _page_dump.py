import json, os, urllib.request

KEY = os.environ["NOTION_API_KEY"]
H = {"Authorization": f"Bearer {KEY}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def get(url):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def blocktext(b):
    t = b.get("type")
    payload = b.get(t, {})
    arr = payload.get("rich_text", [])
    return "".join(x.get("plain_text","") for x in arr)

for label, pid in [("IMPROVE", "3fde71bc-ecb6-81af-8624-ebb86a23bd14"),
                   ("SIGN", "3fde71bc-ecb6-81f8-b7e0-f3408a247d50")]:
    print(f"=== {label} ({pid}) ===")
    data = get(f"https://api.notion.com/v1/blocks/{pid}/children?page_size=100")
    for b in data["results"]:
        print(f"{b['id']} | {b['type']} | {blocktext(b)!r}")
