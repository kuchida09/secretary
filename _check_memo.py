import json, pathlib, urllib.request

def load_key():
    for p in ["/home/kuchida09/hermes-data/.hermes/notion_key", "/workspace/.hermes/notion_key",
              str(pathlib.Path.home() / ".hermes" / "notion_key")]:
        try:
            t = pathlib.Path(p).read_text().strip()
            if t:
                return t
        except Exception:
            pass
    return ""

k = load_key()
h = {"Authorization": f"Bearer {k}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def get(path):
    req = urllib.request.Request("https://api.notion.com/v1" + path, headers=h)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

blocks = get("/blocks/3fde71bc-ecb6-81af-8624-ebb86a23bd14/children?page_size=100").get("results", [])
texts = []
for b in blocks:
    ty = b.get("type")
    rt = b.get(ty, {}).get("rich_text", []) if isinstance(b.get(ty), dict) else []
    texts.append((b["id"], "".join(x.get("plain_text", "") for x in rt)))

print("total blocks:", len(texts))
unhandled = []
for i, (bid, t) in enumerate(texts):
    if "端末から:" in t:
        nxt = texts[i + 1][1] if i + 1 < len(texts) else ""
        handled = nxt.startswith("- 対応:")
        print(("OK  " if handled else "MISS"), bid, t[:60].replace("\n", " / "))
        if not handled:
            unhandled.append((bid, t))
print("UNHANDLED:", len(unhandled))
for u in unhandled:
    print(" ->", u[0], repr(u[1][:200]))
