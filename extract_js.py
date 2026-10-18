import re
h = open('index.html', encoding='utf-8').read()
m = re.search(r'<script>(.*)</script>', h, re.S)
open('/tmp/app.js', 'w', encoding='utf-8').write(m.group(1))
print('extracted', len(m.group(1)))
