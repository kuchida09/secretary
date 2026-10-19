import json, urllib.request, pathlib

key = pathlib.Path('/workspace/.hermes/notion_key').read_text().strip()
h = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}


def get(p):
    r = urllib.request.Request("https://api.notion.com/v1" + p, headers=h)
    return json.loads(urllib.request.urlopen(r, timeout=30).read())


def post(p, pl):
    r = urllib.request.Request("https://api.notion.com/v1" + p, data=json.dumps(pl).encode(), headers=h, method="POST")
    return json.loads(urllib.request.urlopen(r, timeout=30).read())


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
    if t == "status":
        return (v.get("status") or {}).get("name") or ""
    return ""


print("=== review ===")
for row in post("/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print(row["id"], "|", txt(p.get("件名")), "|S:", txt(p.get("状態")), "|C:", repr(txt(p.get("コメント"))), "|H:", repr(txt(p.get("Hermes の対応"))))

print("=== tasks ===")
for row in post("/data_sources/ef21b283-795e-4fec-8311-2e40c4cb0c57/query", {"page_size": 100}).get("results", []):
    p = row["properties"]
    print(row["id"], "|", txt(p.get("名前")), "|S:", txt(p.get("状態")), "|done:", txt(p.get("完了日")), "|due:", txt(p.get("期限")))

print("=== memo blocks ===")
for b in get("/blocks/3fde71bc-ecb6-81af-8624-ebb86a23bd14/children?page_size=100").get("results", []):
    if b.get("type") == "paragraph":
        t = "".join(x.get("plain_text", "") for x in b["paragraph"]["rich_text"])
        print(b["id"], "|", t)

print("=== sign blocks ===")
for b in get("/blocks/3fde71bc-ecb6-81f8-b7e0-f3408a247d50/children?page_size=100").get("results", []):
    if b.get("type") == "paragraph":
        t = "".join(x.get("plain_text", "") for x in b["paragraph"]["rich_text"])
        print(b["id"], "|", t)
