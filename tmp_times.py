import json, urllib.request, pathlib

key = pathlib.Path("/workspace/.hermes/notion_key").read_text(encoding="utf-8").strip()
H = {"Authorization": "Bearer " + key, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}


def post(path, payload):
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=json.dumps(payload).encode(), headers=H, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def get(path):
    req = urllib.request.Request("https://api.notion.com/v1" + path, headers=H)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def txt(v):
    if not v:
        return ""
    t = v.get("type")
    if t in ("title", "rich_text"):
        return "".join(x.get("plain_text", "") for x in v[t])
    if t == "select":
        return (v.get("select") or {}).get("name") or ""
    return ""


rows = []
for row in post("/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 100}).get("results", []):
    rows.append((row.get("created_time"), row.get("last_edited_time"), txt(row["properties"].get("件名")),
                 txt(row["properties"].get("状態"))))
rows.sort()
print("=== REVIEW rows by created_time ===")
for c, e, t, s in rows:
    print(f"created={c}  edited={e}  [{s}] {t}")

print()
print("=== wake_log (numbered) ===")
lines = pathlib.Path("/workspace/secretary/wake_log.txt").read_text(encoding="utf-8").splitlines()
for i, l in enumerate(lines[-40:], start=len(lines) - 40):
    print(i, l)
