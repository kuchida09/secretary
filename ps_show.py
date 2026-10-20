#!/usr/bin/env python3
import json, sys
d = json.load(open("/workspace/secretary/ps_candidates.json", encoding="utf-8"))
want = set(sys.argv[1:])
for t, v in d.items():
    for c in v["cands"]:
        if c["pmid"] in want:
            print("### %s [%s] %s" % (c["pmid"], t, c["title"]))
            print("journal:", c["journal"], "| year:", c["year"], "| doi:", c["doi"], "| first:", c["first_author"])
            print("authors:", ", ".join(c["authors"][:6]))
            print("pubtypes:", c["pubtypes"])
            print("abstract:", c["abstract"][:2600])
            print()
