import json, urllib.request

key = open('/workspace/.hermes/notion_key').read().strip()
H = {'Authorization': 'Bearer ' + key, 'Notion-Version': '2025-09-03'}

PAGES = {
    'MEMO': '3fde71bc-ecb6-81af-8624-ebb86a23bd14',
    'SIGN': '3fde71bc-ecb6-81f8-b7e0-f3408a247d50',
}

for name, pid in PAGES.items():
    print('=====', name, pid)
    url = 'https://api.notion.com/v1/blocks/%s/children?page_size=100' % pid
    r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H)))
    for b in r['results']:
        t = b['type']
        rt = b[t].get('rich_text', []) if isinstance(b[t], dict) else []
        txt = ''.join(x.get('plain_text', '') for x in rt)
        print(b['id'], t, '|', txt)
