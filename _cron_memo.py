import json, urllib.request, urllib.error

key = open('/workspace/.hermes/notion_key').read().strip()
H = {"Authorization": "Bearer " + key, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
MEMO_PAGE = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"
AFTER = "3fde71bc-ecb6-8197-88ad-e8e76ccfd2e8"


def patch(path, payload):
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=json.dumps(payload).encode(), headers=H, method="PATCH")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode())
        raise


payload = {
    "children": [{
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "- 対応: 2026-10-18（Discord で回答）"}}]},
    }],
    "after": AFTER,
}
r = patch("/blocks/" + MEMO_PAGE + "/children", payload)
print("inserted:", r["results"][0]["id"])
