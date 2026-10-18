import json, urllib.request
key = open('/workspace/.hermes/notion_key').read().strip()
H = {"Authorization": "Bearer " + key, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
def get(path):
    req = urllib.request.Request("https://api.notion.com/v1" + path, headers=H)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())
for pid in ["3fde71bc-ecb6-812d-b42d-c1ff89f04a4f"]:
    p = get("/pages/" + pid)
    print(pid)
    print("  created_time:", p.get("created_time"))
    print("  last_edited_time:", p.get("last_edited_time"))
    print("  created_by:", p.get("created_by"))
    print("  last_edited_by:", p.get("last_edited_by"))
    print("  url:", p.get("url"))
