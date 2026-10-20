#!/usr/bin/env python3
"""Notion data source / page helpers (curl-free, stdlib)."""
import os, sys, json, urllib.request, urllib.error

KEY = os.environ.get("NOTION_API_KEY", "")
VER = "2025-09-03"
BASE = "https://api.notion.com/v1"


def req(path, method="GET", body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", "Bearer " + KEY)
    r.add_header("Notion-Version", VER)
    r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "body": e.read().decode()[:800]}


def query_all(ds_id, body=None):
    out, cur = [], None
    while True:
        b = dict(body or {})
        if cur:
            b["start_cursor"] = cur
        j = req("/data_sources/%s/query" % ds_id, "POST", b)
        if "_error" in j:
            return j
        out += j.get("results", [])
        if not j.get("has_more"):
            break
        cur = j.get("next_cursor")
    return {"results": out}


def flat(prop):
    t = prop.get("type")
    v = prop.get(t)
    if t == "title":
        return "".join(x["plain_text"] for x in v)
    if t == "rich_text":
        return "".join(x["plain_text"] for x in v)
    if t == "select":
        return v["name"] if v else ""
    if t == "multi_select":
        return ",".join(x["name"] for x in v)
    if t == "number":
        return v
    if t == "date":
        return v["start"] if v else ""
    if t == "url":
        return v or ""
    if t == "checkbox":
        return v
    if t == "formula":
        return v.get("string") or v.get("number") or ""
    return ""


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "ledger":
        j = query_all("d2346174-f4b7-43fa-aa46-8637406e8cdf", {"page_size": 100})
        if "_error" in j:
            print(json.dumps(j, ensure_ascii=False)); sys.exit(1)
        for r in j["results"]:
            p = {k: flat(v) for k, v in r["properties"].items()}
            p["_id"] = r["id"]
            print(json.dumps(p, ensure_ascii=False))
    elif cmd == "page":
        j = req("/pages/%s/markdown" % sys.argv[2])
        print(json.dumps(j, ensure_ascii=False)[:2000] if isinstance(j, dict) and "_error" in j else (j.get("markdown", "") if isinstance(j, dict) else str(j)))
    elif cmd == "raw":
        j = query_all(sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else None)
        print(json.dumps(j, ensure_ascii=False)[:3000])
