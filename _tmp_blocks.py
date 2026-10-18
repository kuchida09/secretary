import json, os, urllib.request

KEY = os.environ["NOTION_API_KEY"]
H = {"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=H, method=method)
    return json.load(urllib.request.urlopen(r))

def children(pid):
    out = []
    cur = None
    while True:
        url = "https://api.notion.com/v1/blocks/%s/children?page_size=100" % pid
        if cur: url += "&start_cursor=" + cur
        d = req("GET", url)
        out += d["results"]
        if not d.get("has_more"): break
        cur = d["next_cursor"]
    return out

def flat(b):
    t = b["type"]
    v = b.get(t, {})
    rt = v.get("rich_text") or []
    s = "".join(x.get("plain_text","") for x in rt)
    return t, s

for name, pid in [("改善メモ", "3fde71bc-ecb6-81af-8624-ebb86a23bd14"),
                  ("確認サイン", "3fde71bc-ecb6-81f8-b7e0-f3408a247d50")]:
    print("=====", name, "=====")
    for b in children(pid):
        t, s = flat(b)
        print(b["id"], "|", t, "|", repr(s))
