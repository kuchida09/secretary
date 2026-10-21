import json, os, urllib.request
KEY = os.environ["NOTION_API_KEY"]
DS = "8f49d8fb-3ffd-4e76-ac63-6ce14337e2ad"
def call(url, payload=None, method="GET"):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03",
                 "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))
d = call(f"https://api.notion.com/v1/data_sources/{DS}/query", {"page_size": 2}, "POST")
for r in d["results"]:
    for k, v in r["properties"].items():
        print(k, "=", json.dumps(v, ensure_ascii=False)[:300])
    print("---")
