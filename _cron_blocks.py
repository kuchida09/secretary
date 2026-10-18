import json, urllib.request

key = open('/workspace/.hermes/notion_key').read().strip()
H = {"Authorization": "Bearer " + key, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
MEMO_PAGE = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"
SIGN_PAGE = "3fde71bc-ecb6-81f8-b7e0-f3408a247d50"


def get(path):
    req = urllib.request.Request("https://api.notion.com/v1" + path, headers=H)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def btext(b):
    t = b.get("type")
    if not t:
        return ""
    arr = b[t].get("rich_text", [])
    return "".join(x.get("plain_text", "") for x in arr)


for name, pid in [("MEMO", MEMO_PAGE), ("SIGN", SIGN_PAGE)]:
    print("##########", name, pid)
    r = get("/blocks/" + pid + "/children?page_size=100")
    for b in r["results"]:
        print(b["id"], "|", b["type"], "|", repr(btext(b)))
