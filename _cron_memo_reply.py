import json, urllib.request, urllib.parse, os, pathlib

KEY = os.environ.get("NOTION_API_KEY", "").strip()
if not KEY:
    for p in ["/home/kuchida09/hermes-data/.hermes/notion_key", "/workspace/.hermes/notion_key",
              str(pathlib.Path.home() / ".hermes" / "notion_key")]:
        try:
            t = pathlib.Path(p).read_text().strip()
            if t: KEY = t; break
        except Exception: pass
H = {"Authorization": f"Bearer {KEY}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
MEMO = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"

def patch(path, payload):
    req = urllib.request.Request("https://api.notion.com/v1" + path,
                                 data=json.dumps(payload).encode(), headers=H, method="PATCH")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

targets = [
    ("3fee71bc-ecb6-8198-9249-d6426c5a98f6", "受賞歴"),
    ("3fee71bc-ecb6-8142-96b9-e6bda8d5a813", "記録に無い学会発表"),
    ("3fee71bc-ecb6-811c-9f2b-c8ea4fd2c5bd", "コメント機能"),
    ("3fee71bc-ecb6-819d-901a-daae46518b3c", "hifの論文"),
]
for bid, label in targets:
    payload = {
        "after": bid,
        "children": [{"object": "block", "type": "paragraph",
                      "paragraph": {"rich_text": [{"type": "text", "text": {"content": "- 対応: 2026-10-19（Discord で回答）"}}]}}],
    }
    try:
        r = patch(f"/blocks/{MEMO}/children", payload)
        print("OK", label, "->", r["results"][0]["id"])
    except Exception as e:
        print("ERR", label, type(e).__name__, getattr(e, 'read', lambda: b'')()[:200])
