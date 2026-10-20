#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/workspace/secretary")
from notion_ds import req, query_all

DS = "8f49d8fb-3ffd-4e76-ac63-6ce14337e2ad"

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "schema"
    if cmd == "schema":
        j = req("/data_sources/%s" % DS)
        print(json.dumps(j, ensure_ascii=False, indent=1)[:4000])
    elif cmd == "sample":
        j = query_all(DS, {"page_size": 2})
        print(json.dumps(j["results"], ensure_ascii=False, indent=1)[:4000])
