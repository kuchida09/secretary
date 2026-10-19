import json, urllib.request, urllib.parse

TOK = '/home/pn/.hermes/google_token.json'
d = json.load(open(TOK))
def refresh():
    body = urllib.parse.urlencode({
        'client_id': d['client_id'], 'client_secret': d['client_secret'],
        'refresh_token': d['refresh_token'], 'grant_type': 'refresh_token'}).encode()
    req = urllib.request.Request(d['token_uri'], data=body)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())['access_token']
AT = refresh()

def api(path, params=None):
    url = 'https://www.googleapis.com/drive/v3/' + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + AT})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def children(fid):
    out = []
    tok = None
    while True:
        p = {'q': f"'{fid}' in parents and trashed=false",
             'fields': 'nextPageToken,files(id,name,mimeType,modifiedTime)',
             'pageSize': 200, 'orderBy': 'name'}
        if tok: p['pageToken'] = tok
        r = api('files', p)
        out += r.get('files', [])
        tok = r.get('nextPageToken')
        if not tok: break
    return out

roots = {
 '20_学会・発表': '14Xe4NmmUwSLJ9A0doyZkXNw7RRmp9Q9F',
}
def walk(fid, name, depth=0, maxdepth=3):
    if depth > maxdepth: return
    for f in children(fid):
        tag = '[D]' if f['mimeType'] == 'application/vnd.google-apps.folder' else '   '
        print('  '*depth + tag, f['name'], '' if tag=='[D]' else '('+f['mimeType'].split('.')[-1]+')')
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            walk(f['id'], f['name'], depth+1, maxdepth)

for name, fid in roots.items():
    print('#'*10, name)
    walk(fid, name, 0, 3)
