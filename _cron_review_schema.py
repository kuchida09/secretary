import json, os, pathlib, urllib.request
KEY = os.environ.get("NOTION_API_KEY","").strip()
if not KEY:
    for p in ["/home/kuchida09/hermes-data/.hermes/notion_key","/workspace/.hermes/notion_key",str(pathlib.Path.home()/".hermes"/"notion_key")]:
        try:
            t=pathlib.Path(p).read_text().strip()
            if t: KEY=t; break
        except Exception: pass
H={"Authorization":"Bearer "+KEY,"Notion-Version":"2025-09-03","Content-Type":"application/json"}
req=urllib.request.Request("https://api.notion.com/v1/data_sources/60242da1-b213-4118-ae82-f8782a816cb2",headers=H)
d=json.loads(urllib.request.urlopen(req,timeout=30).read())
for name,pr in d["properties"].items():
    print(name,"|",pr["type"],"|",[o["name"] for o in (pr.get(pr["type"],{}) or {}).get("options",[])] if pr["type"]=="select" else "")
