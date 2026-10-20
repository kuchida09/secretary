#!/usr/bin/env python3
"""Fetch OA fulltext for the newly added papers and update index.csv oa_status/fulltext_path."""
import csv, os, subprocess, sys

BASE = "/workspace/research/80_AI作業場"
FT = BASE + "/knowledge/literature/daily-feed/fulltext"
INDEX = BASE + "/knowledge/literature/daily-feed/index.csv"
SCRIPT = BASE + "/ops/literature/fetch_fulltext.py"

TARGETS = [
    ("42844276", "10.1038/s41467-026-77498-w"),
    ("42881307", "10.1007/s00464-026-13321-3"),
    ("42879739", "10.1177/15533506261498412"),
    ("42855513", "10.1007/s00464-026-13404-1"),
    ("42857507", "10.3389/fonc.2026.1947280"),
    ("42849513", "10.1097/SLA.0000000000007229"),
    ("42869423", "10.1177/00031348261496616"),
]

results = {}
for pmid, doi in TARGETS:
    out = subprocess.run([sys.executable, SCRIPT, doi, FT, pmid], capture_output=True, text=True, timeout=180)
    line = (out.stdout or "").strip().split("\n")[-1] if out.stdout else "error\t\t"
    parts = line.split("\t")
    status = parts[0]
    path = parts[1] if len(parts) > 1 else ""
    results[pmid] = (status, path)
    print(pmid, status, path)

# update index.csv (only oa_status/fulltext_path of these pmids)
with open(INDEX, encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f)
    fields = rd.fieldnames
    rows = list(rd)
for r in rows:
    if r["pmid"] in results:
        st, p = results[r["pmid"]]
        r["oa_status"] = st
        if p:
            r["fulltext_path"] = p
with open(INDEX, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print("updated index.csv for", len(results), "pmids")
