import json, os, urllib.request

KEY = os.environ["NOTION_API_KEY"]
H = {"Authorization": f"Bearer {KEY}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=H, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def get(url):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def rt(prop):
    if not prop: return ""
    arr = prop.get("rich_text") or prop.get("title") or []
    return "".join(t.get("plain_text","") for t in arr)

def sel(prop):
    if not prop: return ""
    s = prop.get("select")
    return s.get("name") if s else ""

# tasks
tasks = post("https://api.notion.com/v1/data_sources/ef21b283-795e-4fec-8311-2e40c4cb0c57/query", {"page_size": 100})
print("=== TASKS ===")
for row in tasks["results"]:
    p = row["properties"]
    name = rt(p.get("名前") or p.get("Name"))
    st = sel(p.get("状態") or p.get("Status"))
    due = (p.get("期限") or {}).get("date")
    due = due.get("start") if due else ""
    done = (p.get("完了日") or {}).get("date")
    done = done.get("start") if done else ""
    print(f"{row['id']} | {name} | {st} | due={due} | done={done}")

# review
rev = post("https://api.notion.com/v1/data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 100})
print("=== REVIEW ===")
for row in rev["results"]:
    p = row["properties"]
    subj = rt(p.get("件名") or p.get("Name"))
    st = sel(p.get("状態") or p.get("Status"))
    cm = rt(p.get("コメント"))
    resp = rt(p.get("Hermes の対応"))
    print(f"{row['id']} | {subj} | state={st} | comment={cm!r} | resp={resp!r}")
