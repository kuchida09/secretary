import json, os, urllib.request
KEY = os.environ["NOTION_API_KEY"]
led = {r["番号"]: r for r in json.load(open("/workspace/secretary/ledger.json"))}
row = led["⑨"]
old = row.get("備考") or ""
add = ("2026-10-21(Hermes版・毎日): edat 2026/10/07-10/21の2式(手術映像・術中AI系/基盤モデル系)で新規6件"
       "(術中出血検出の前臨床RCT[S評価]、商用ビジョン転用の器械識別、ambient intelligenceと手術安全、"
       "OCTによる深部神経検出[プレプリント]、外科教育のAI適応学習、AI実装の系統的レビュープロトコル)。連続0件回数0。")
LIMIT = 1950
room = LIMIT - len(add) - 3
trimmed_old = old[-room:] if len(old) > room else old
note = "…" + trimmed_old + "\n" + add

def req(url, payload=None, method="GET"):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03",
                 "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))

props = {"直近検索日": {"date": {"start": "2026-10-21"}},
         "直近発見日": {"date": {"start": "2026-10-21"}},
         "連続0件回数": {"number": 0},
         "備考": {"rich_text": [{"text": {"content": note}}]}}
req(f"https://api.notion.com/v1/pages/{row['id']}", {"properties": props}, "PATCH")
print("OK len", len(note))
