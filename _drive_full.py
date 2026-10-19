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
    out, tok = [], None
    while True:
        p = {'q': f"'{fid}' in parents and trashed=false",
             'fields': 'nextPageToken,files(id,name,mimeType)', 'pageSize': 200, 'orderBy': 'name'}
        if tok: p['pageToken'] = tok
        r = api('files', p)
        out += r.get('files', [])
        tok = r.get('nextPageToken')
        if not tok: break
    return out

FOLDER = 'application/vnd.google-apps.folder'
out = []
def walk(fid, path, depth=0, maxdepth=4):
    if depth > maxdepth: return
    for f in children(fid):
        if f['mimeType'] == FOLDER:
            out.append(('D', path + '/' + f['name'], f['id']))
            walk(f['id'], path + '/' + f['name'], depth+1, maxdepth)
        else:
            out.append(('F', path + '/' + f['name'], f['id']))

roots = {
 '20_学会・発表': '14Xe4NmmUwSLJ9A0doyZkXNw7RRmp9Q9F',
 '学会発表(1)': '1JKnZdIOPmUEhBMyUshpmPmZ84DGPTs_o',
 '学会発表2': '1JUIo5-5PBmFOc_xaJE7TyurNS__Nju6V',
 '学会発表_抄録a': '1x6QuX2rD1O-1Sbv5bRyPDIbkRxJlA7UZ',
 '学会発表_抄録b': '1_4a4MOP9kJMiC5uGdH5KsFDMklhgJBIj',
 '臨床外科学会': '1-A9de0XlVKv-0QzpMFER-X0tVQhBmeZ0',
 '07_発表_a': '1WoEiJo4W-UE82YEdOvhbinE4ErWnNQZh',
 '07_発表_b': '1MzUmPbL-edBnUcss9uaaNi5FU0d_y5so',
 '学会発表_c': '12heyikUT7gqTanFBJHYC3AgOtvtf81F-',
 '学会発表_d': '1RxwfnDNfRbUH39av3WjWtYGWNBIlqbrD',
 '学会発表_e': '1B9TWLE5wCYXjl6Uu4GhpvTfC13M_DWrc',
 '学会発表_f': '1ro1_jupPTeiD1kRGibapHib-FAmSPsxU',
 '学会発表_g': '1yjQxA1Mg2TzZDDWihhNwbOcWZkE92ahF',
}
for name, fid in roots.items():
    out.append(('ROOT', name, fid))
    walk(fid, name, 0, 3)

with open('/workspace/secretary/_drive_presentations.txt', 'w', encoding='utf-8') as fh:
    for t, p, i in out:
        fh.write(f"{t}\t{p}\n")
print('total lines', len(out))
