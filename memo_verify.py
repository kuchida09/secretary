import json, os, re, time, urllib.request

KEY = os.environ.get("NOTION_API_KEY")
HDR = {"Authorization": "Bearer " + (KEY or ""), "Notion-Version": "2025-09-03"}
MEMO = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"

def get(url):
    r = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(r) as resp:
        return json.load(resp)

d = get("https://api.notion.com/v1/blocks/%s/children?page_size=100" % MEMO)
all_lines = []
for b in d["results"]:
    if b.get("type") == "paragraph":
        t = "".join(x.get("plain_text", "") for x in b["paragraph"]["rich_text"]).strip()
        if t:
            all_lines.append(t)

pending = []
for i, ln in enumerate(all_lines):
    if re.match(r"^\d{4}-\d{2}-\d{2}", ln):
        handled = False
        for j in range(i + 1, len(all_lines)):
            if re.match(r"^\d{4}-\d{2}-\d{2}", all_lines[j]):
                break
            if all_lines[j].lstrip("-").strip().startswith("対応:"):
                handled = True
                break
        if not handled:
            pending.append(ln)
print("PENDING count:", len(pending))
for p in pending:
    print(" -", p[:110])
