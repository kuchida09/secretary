import sys
sys.path.insert(0, "/workspace/secretary")
from notion_ds import req
j = req("/data_sources/d2346174-f4b7-43fa-aa46-8637406e8cdf")
print("ledger db:", j.get("parent", {}))
print("url:", j.get("url"))
