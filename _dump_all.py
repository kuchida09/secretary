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
    if t == "date":
        return (v.get("date") or {}).get("start") or ""
    return ""


print("########## QA DB (確認事項) ##########")
for row in post("/data_sources/8d58d65b-8d15-4012-866a-772ee3942500/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print("=== QA", row["id"], "| url:", row.get("url"))
    for k, v in p.items():
        val = txt(v)
        if val:
            print("   ", k, "=", repr(val))

print()
print("########## REPORT DB (レポート) ##########")
for row in post("/data_sources/a54924f2-1ca7-44f5-b5d1-47576d368aff/query", {"page_size": 50}).get("results", []):
    p = row["properties"]
    print("=== REP", row["id"], "| url:", row.get("url"))
    for k, v in p.items():
        val = txt(v)
        if val:
            print("   ", k, "=", repr(val))

print()
print("########## MEMO PAGE ##########")
for b in get("/blocks/3fde71bc-ecb6-81af-8624-ebb86a23bd14/children?page_size=100").get("results", []):
    ty = b.get("type")
    t = "".join(x.get("plain_text", "") for x in b.get(ty, {}).get("rich_text", [])) if ty in ("paragraph", "heading_1", "heading_2", "heading_3") else ""
    print(b["id"], "|", ty, "|", t[:300])

print()
print("########## SIGN PAGE ##########")
for b in get("/blocks/3fde71bc-ecb6-81f8-b7e0-f3408a247d50/children?page_size=100").get("results", []):
    ty = b.get("type")
    t = "".join(x.get("plain_text", "") for x in b.get(ty, {}).get("rich_text", [])) if ty in ("paragraph", "heading_1", "heading_2", "heading_3") else ""
    print(b["id"], "|", ty, "|", t[:300])
