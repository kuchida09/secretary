import json, urllib.request, urllib.parse, time

TOK = '/home/pn/.hermes/google_token.json'
d = json.load(open(TOK))

def refresh():
    body = urllib.parse.urlencode({
        'client_id': d['client_id'],
        'client_secret': d['client_secret'],
        'refresh_token': d['refresh_token'],
        'grant_type': 'refresh_token',
    }).encode()
    req = urllib.request.Request(d['token_uri'], data=body)
    r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return r['access_token']

AT = refresh()

def api(path, params=None):
    url = 'https://www.googleapis.com/drive/v3/' + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + AT})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

# find folder 20_学会・発表
res = api('files', {'q': "name contains '学会' and mimeType='application/vnd.google-apps.folder' and trashed=false", 'fields': 'files(id,name,parents)', 'pageSize': 50})
print('FOLDERS 学会:')
for f in res.get('files', []):
    print(' ', f['id'], f['name'])

res2 = api('files', {'q': "name contains '発表' and mimeType='application/vnd.google-apps.folder' and trashed=false", 'fields': 'files(id,name)', 'pageSize': 50})
print('FOLDERS 発表:')
for f in res2.get('files', []):
    print(' ', f['id'], f['name'])

res3 = api('files', {'q': "name contains '表彰' and trashed=false", 'fields': 'files(id,name,mimeType)', 'pageSize': 50})
print('FILES 表彰:')
for f in res3.get('files', []):
    print(' ', f['id'], f['name'], f['mimeType'])

res4 = api('files', {'q': "name contains '受賞' and trashed=false", 'fields': 'files(id,name,mimeType)', 'pageSize': 50})
print('FILES 受賞:')
for f in res4.get('files', []):
    print(' ', f['id'], f['name'], f['mimeType'])
