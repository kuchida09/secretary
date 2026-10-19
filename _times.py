import json, os, pathlib, urllib.request

KEY = os.environ.get("NOTION_API_KEY", "").strip()
H = {"Authorization": f"Bearer {KEY}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}


def get(path):
    req = urllib.request.Request("https://api.notion.com/v1" + path, headers=H)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


ids = [
    ("task_award", "3fee71bc-ecb6-8112-9300-f4e716319661"),
    ("task_pub", "3fee71bc-ecb6-8191-a2c1-ed348cf48066"),
    ("task_talkyear", "3fee71bc-ecb6-8154-86da-e44583062677"),
    ("task_talklist", "3fee71bc-ecb6-816e-b131-deaeda19ffbc"),
    ("qa_pub", "3fee71bc-ecb6-8138-a0ea-e047a204aab8"),
    ("qa_award", "3fee71bc-ecb6-819c-9e8b-edbe70c2d07e"),
    ("qa_talk", "3fee71bc-ecb6-813d-aad8-e3d5e9e9789b"),
    ("qa_list", "3fee71bc-ecb6-81ac-a25c-f222a2f0cb77"),
    ("qa_howto", "3fee71bc-ecb6-81f6-9603-c060e982b957"),
    ("qa_docs", "3fee71bc-ecb6-81f7-9b3f-df645412912d"),
]
for name, i in ids:
    p = get(f"/pages/{i}")
    print(name, "created:", p.get("created_time"), "edited:", p.get("last_edited_time"))
