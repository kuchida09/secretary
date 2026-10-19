import json, urllib.request, urllib.parse, io, zipfile, re

TOK = '/home/pn/.hermes/google_token.json'
d = json.load(open(TOK))
def refresh():
    body = urllib.parse.urlencode({
        'client_id': d['client_id'], 'client_secret': d['client_secret'],
        'refresh_token': d['refresh_token'], 'grant_type': 'refresh_token'}).encode()
    req = urllib.request.Request(d['token_uri'], data=body)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())['access_token']
AT = refresh()

def dl(fid):
    url = f'https://www.googleapis.com/drive/v3/files/{fid}?alt=media'
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + AT})
    return urllib.request.urlopen(req, timeout=60).read()

def docx_text(b):
    z = zipfile.ZipFile(io.BytesIO(b))
    xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    xml = re.sub(r'</w:p>', '\n', xml)
    xml = re.sub(r'<[^>]+>', '', xml)
    return xml

files = {
 '第87回臨床外科学会': '1WOutlyyYMbOVdURXzh75XbIdthvr5z5x',
 '第36回内視鏡外科学会': '1vXmUmrs6B7LmRu3iwkB0VWK0BpJqIQxM',
 '岩手医科大学報_表彰の栄誉_原稿': '1cpPShHSakMx7_yI0dvBpOKTrjz-RkImJ',
}
for name, fid in files.items():
    print('='*20, name, '='*20)
    try:
        print(docx_text(dl(fid))[:3000])
    except Exception as e:
        print('ERR', type(e).__name__, e)
