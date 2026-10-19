import json, urllib.request
key = open('/workspace/.hermes/notion_key').read().strip()
H = {'Authorization': 'Bearer ' + key, 'Notion-Version': '2025-09-03'}
pid = '3fde71bc-ecb6-8153-9856-d628270f7b8b'
r = json.load(urllib.request.urlopen(urllib.request.Request('https://api.notion.com/v1/pages/' + pid, headers=H)))
print('created', r.get('created_time'), 'edited', r.get('last_edited_time'))
print('created_by', r.get('created_by'))
for k, v in r['properties'].items():
    print(k, json.dumps(v, ensure_ascii=False)[:200])
