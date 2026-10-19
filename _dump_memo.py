import json, pathlib, urllib.request, os
k = os.environ.get("NOTION_API_KEY","")
if not k:
    for p in ["/workspace/.hermes/notion_key","/home/kuchida09/hermes-data/.hermes/notion_key"]:
        try:
            t=pathlib.Path(p).read_text().strip()
            if t: k=t; break
        except Exception: pass
h={"Authorization":f"Bearer {k}","Notion-Version":"2025-09-03","Content-Type":"application/json"}
def get(path):
    req=urllib.request.Request("https://api.notion.com/v1"+path,headers=h)
    return json.loads(urllib.request.urlopen(req,timeout=30).read())
def plain(b):
    t=b.get("type")
    if t=="paragraph": return "".join(x.get("plain_text","") for x in b["paragraph"]["rich_text"])
    if t=="heading_1": return "H1 "+"".join(x.get("plain_text","") for x in b["heading_1"]["rich_text"])
    if t=="heading_2": return "H2 "+"".join(x.get("plain_text","") for x in b["heading_2"]["rich_text"])
    if t=="heading_3": return "H3 "+"".join(x.get("plain_text","") for x in b["heading_3"]["rich_text"])
    if t=="bulleted_list_item": return "- "+"".join(x.get("plain_text","") for x in b["bulleted_list_item"]["rich_text"])
    return ""
for name,pid in [("MEMO","3fde71bc-ecb6-81af-8624-ebb86a23bd14"),("SIGN","3fde71bc-ecb6-81f8-b7e0-f3408a247d50")]:
    print("=====",name)
    blocks=get(f"/blocks/{pid}/children?page_size=100").get("results",[])
    for b in blocks:
        s=plain(b)
        print(b["id"][:8], b.get("type"), "|", s[:180])
