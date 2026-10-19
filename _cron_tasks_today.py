import json, urllib.request, datetime

key = open('/workspace/.hermes/notion_key').read().strip()
ds = json.load(open('/workspace/records/notion_ids.json'))['tasks_ds']
utcnow = datetime.datetime.utcnow()
jst = utcnow + datetime.timedelta(hours=9)
today = jst.strftime('%Y-%m-%d')

body = {"page_size": 100}
req = urllib.request.Request(
    f"https://api.notion.com/v1/data_sources/{ds}/query",
    data=json.dumps(body).encode(),
    headers={"Authorization": f"Bearer {key}",
             "Notion-Version": "2025-09-03",
             "Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req))

def val(pr, n):
    x = pr.get(n, {})
    t = x.get('type')
    if t == 'title': return ''.join(i['plain_text'] for i in x['title'])
    if t == 'rich_text': return ''.join(i['plain_text'] for i in x['rich_text'])
    if t == 'select': return (x['select'] or {}).get('name')
    if t == 'date': return (x['date'] or {}).get('start')
    if t == 'status': return (x['status'] or {}).get('name')
    return None

rows = []
for p in r['results']:
    pr = p['properties']
    name = val(pr, '名前') or ''
    if '【サンプル】' in name:
        continue
    st = val(pr, '状態')
    due = val(pr, '期限')
    rows.append({'name': name, 'state': st, 'due': due, 'area': val(pr, '領域'),
                 'prio': val(pr, '優先度'), 'waiting': val(pr, '待ち相手'),
                 'proj': val(pr, 'プロジェクト')})

over, today_due, soon, waiting = [], [], [], []
for t in rows:
    if not t['due']:
        continue
    d = t['due'][:10]
    if t['state'] == '完了':
        continue
    if d < today:
        over.append(t)
    elif d == today:
        today_due.append(t)
    elif d <= (jst + datetime.timedelta(days=3)).strftime('%Y-%m-%d'):
        soon.append(t)

print('today_jst', today)
print('total_open', len([t for t in rows if t['state'] != '完了']))
print('OVERDUE', json.dumps(over, ensure_ascii=False))
print('TODAY', json.dumps(today_due, ensure_ascii=False))
print('SOON3', json.dumps(soon, ensure_ascii=False))
