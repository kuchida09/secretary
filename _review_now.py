import json, os, pathlib, urllib.request

KEY = os.environ.get("NOTION_API_KEY", "").strip()
if not KEY:
    for p in ["/workspace/.hermes/notion_key", "/home/kuchida09/hermes-data/.hermes/notion_key",
              str(pathlib.Path.home() / ".hermes" / "notion_key")]:
        try:
            t = pathlib.Path(p).read_text(encoding="utf-8").strip()
            if t:
                KEY = t
                break
        except Exception:
            pass
H = {"Authorization": f"Bearer {KEY}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}


def post(path, payload):
    req = urllib.request.Request("https://api.notion.com/v1" + path, data=json.dumps(payload).encode(), headers=H, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def txt(v):
    if not v:
        return ""
    t = v.get("type")
    if t in ("title", "rich_text"):
        return "".join(x.get("plain_text", "") for x in v[t])
    if t == "select":
        return (v.get("select") or {}).get("name") or ""
    if t == "status":
        return (v.get("status") or {}).get("name") or ""
    if t == "date":
        return (v.get("date") or {}).get("start") or ""
    return ""


print("########## REVIEW DB (確認・提案) ##########")
for row in post("/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print("=== ", row["id"], "| url:", row.get("url"))
    for k, v in p.items():
        val = txt(v)
        if val:
            print("   ", k, "=", repr(val[:400]))

print()
print("########## TASKS DB ##########")
for row in post("/data_sources/ef21b283-795e-4fec-8311-2e40c4cb0c57/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print("=== ", row["id"], "| url:", row.get("url"))
    for k, v in p.items():
        val = txt(v)
        if val:
            print("   ", k, "=", repr(val[:300]))
