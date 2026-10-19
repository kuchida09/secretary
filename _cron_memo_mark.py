import json, urllib.request

key = open('/workspace/.hermes/notion_key').read().strip()
H = {'Authorization': 'Bearer ' + key, 'Notion-Version': '2025-09-03',
     'Content-Type': 'application/json'}

MEMO = '3fde71bc-ecb6-81af-8624-ebb86a23bd14'
AFTER = '3fee71bc-ecb6-8105-b8f0-eda5fcd5d953'

body = {
    "after": AFTER,
    "children": [
        {"object": "block", "type": "paragraph",
         "paragraph": {"rich_text": [{"type": "text", "text": {"content": "- 対応: 2026-10-19（Discord で回答）"}}]}}
    ],
}

req = urllib.request.Request(
    'https://api.notion.com/v1/blocks/%s/children' % MEMO,
    data=json.dumps(body).encode(), headers=H, method='PATCH')
r = json.load(urllib.request.urlopen(req))
print('inserted', len(r.get('results', [])))
