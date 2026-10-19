#!/usr/bin/env python3
import json, urllib.request, pathlib, time
KEY_PATHS = ["/workspace/.hermes/notion_key", "/home/kuchida09/hermes-data/.hermes/notion_key"]
key = ""
for p in KEY_PATHS:
    try:
        t = pathlib.Path(p).read_text(encoding="utf-8").strip()
        if t:
            key = t; break
    except Exception:
        pass

def api(path, body=None, method="POST"):
    req = urllib.request.Request("https://api.notion.com/v1/" + path,
        data=json.dumps(body).encode() if body else None, method=method,
        headers={"Authorization": "Bearer " + key, "Notion-Version": "2025-09-03", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))

def txt(rt):
    return "".join(t.get("plain_text", "") for t in rt) if rt else ""

print("=== REVIEW DB ===")
r = api("data_sources/60242da1-b213-4118-ae82-f8782a816cb2/query", {"page_size": 50})
for pg in r["results"]:
    p = pg["properties"]
    print("|".join([
        pg["id"],
        txt(p.get("件名", {}).get("title", [])),
        "状態=" + ((p.get("状態", {}).get("select") or {}).get("name", "")),
        "コメント=" + txt(p.get("コメント", {}).get("rich_text", [])),
        "対応=" + txt(p.get("Hermes の対応", {}).get("rich_text", [])),
    ]))

print("=== MEMO PAGE BLOCKS ===")
r = api("blocks/3fde71bc-ecb6-81af-8624-ebb86a23bd14/children?page_size=100", method="GET")
for b in r["results"]:
    t = b["type"]
    if t in ("paragraph", "bulleted_list_item", "numbered_list_item", "heading_1", "heading_2", "heading_3", "callout", "to_do", "quote"):
        print(b["id"], t, "|", txt(b[t].get("rich_text", [])))

print("=== TASKS (not done) ===")
r = api("data_sources/ef21b283-795e-4fec-8311-2e40c4cb0c57/query", {"page_size": 100})
for pg in r["results"]:
    p = pg["properties"]
    st = (p.get("状態", {}).get("select") or {}).get("name", "")
    print("|".join([txt(p.get("名前", {}).get("title", [])), "状態=" + st, "完了日=" + ((p.get("完了日", {}).get("date") or {}) or {}).get("start", "")]))
