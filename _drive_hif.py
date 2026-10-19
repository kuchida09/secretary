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
    if params: url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + AT})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

queries = {
 'HIF': "name contains 'HIF' and trashed=false",
 'HIF-PHI': "name contains 'PHI' and trashed=false",
 'CNI': "name contains 'CNI' and trashed=false",
 '肝移植': "name contains '肝移植' and trashed=false",
 '腎機能': "name contains '腎' and trashed=false",
 'calcin': "fullText contains 'HIF-PHI' and trashed=false",
}
for label, q in queries.items():
    print('==== ' + label)
    try:
        r = api('files', {'q': q, 'fields': 'files(id,name,mimeType)', 'pageSize': 30})
        for f in r.get('files', []):
            print(' ', f['mimeType'].split('.')[-1], f['name'])
    except Exception as e:
        print(' ERR', type(e).__name__, e)
