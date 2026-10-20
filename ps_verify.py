#!/usr/bin/env python3
import csv, sys
sys.path.insert(0, "/workspace/secretary")
from notion_ds import req, query_all, flat

DS = "8f49d8fb-3ffd-4e76-ac63-6ce14337e2ad"
pmids = ["42844276","42881307","42879739","42855513","42857507","42849513","42869423"]

found = {}
cur = None
while True:
    b = {"page_size": 100}
    if cur:
        b["start_cursor"] = cur
    j = req("/data_sources/%s/query" % DS, "POST", b)
    for r in j["results"]:
        p = r["properties"]
        key = flat(p.get("PMID/DOI", {}))
        for pm in pmids:
            if pm in key:
                found[pm] = (r["id"], flat(p["タイトル"]))
    if not j.get("has_more"):
        break
    cur = j["next_cursor"]

print("found in Notion:", len(found))
for pm in pmids:
    print(pm, "OK" if pm in found else "MISSING")

# update index notion_synced
INDEX = "/workspace/research/80_AI作業場/knowledge/literature/daily-feed/index.csv"
with open(INDEX, encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f); fields = rd.fieldnames; rows = list(rd)
n = 0
for r in rows:
    if r["pmid"] in found:
        r["notion_synced"] = "Y"; n += 1
with open(INDEX, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
print("notion_synced set for", n)
