import json, os, urllib.request

KEY = os.environ["NOTION_API_KEY"]
led = {r["番号"]: r for r in json.load(open("/workspace/secretary/ledger.json"))}

UPD = {
 "①": {"直近検索日": "2026-10-21", "連続0件回数": 2,
   "備考追記": "2026-10-21(Hermes版・毎日): edat 2026/10/07-10/21で①解剖学的構造認識AIの新規0件(候補はHCCのprecision surgical oncologyレビュー1件のみで非該当)。連続0件回数2。"},
 "③": {"直近検索日": "2026-10-21", "連続0件回数": 1,
   "備考追記": "2026-10-21(Hermes版・毎日): edat 2026/10/07-10/21でCVS・胆管損傷予防AIの新規0件。連続0件回数1。"},
 "⑤": {"直近検索日": "2026-10-21", "連続0件回数": 3, "現在の頻度": "週次", "ステータス": "週次縮小",
   "備考追記": "2026-10-21(Hermes版・毎日): edat 2026/10/07-10/21で新規0件(ヘルニア×AI該当1件は既存収載)。競合著者ウォッチ: Marcelo FJ[Author]はHernIA論文(40527303)のみで新著なし、Mita K[Author]の新規ヒット4件はいずれも2014-2021年の非AI論文(鼠径ヘルニア後出血・mesh plug等)で新著なし、SatoはeTEP/NVB文脈0件。連続0件回数3に達したため毎日→週次・週次縮小へ。"},
 "⑨": {"直近検索日": "2026-10-21", "直近発見日": "2026-10-21", "連続0件回数": 0,
   "備考追記": "2026-10-21(Hermes版・毎日): edat 2026/10/07-10/21の2式(手術映像・術中AI系/基盤モデル系)で新規6件(術中出血検出の前臨床RCT[S評価]、商用ビジョン転用の器械識別、ambient intelligenceと手術安全、OCTによる深部神経検出[プレプリント]、外科教育のAI適応学習、AI実装の系統的レビュープロトコル)。連続0件回数0。"},
}

def req(url, payload=None, method="GET"):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": "Bearer " + KEY, "Notion-Version": "2025-09-03",
                 "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))

for no, u in UPD.items():
    row = led[no]
    props = {"直近検索日": {"date": {"start": u["直近検索日"]}},
             "連続0件回数": {"number": u["連続0件回数"]}}
    if u.get("直近発見日"):
        props["直近発見日"] = {"date": {"start": u["直近発見日"]}}
    if u.get("現在の頻度"):
        props["現在の頻度"] = {"select": {"name": u["現在の頻度"]}}
    if u.get("ステータス"):
        props["ステータス"] = {"select": {"name": u["ステータス"]}}
    note = (row.get("備考") or "") + "\n" + u["備考追記"]
    props["備考"] = {"rich_text": [{"text": {"content": note}}]}
    try:
        req(f"https://api.notion.com/v1/pages/{row['id']}", {"properties": props}, "PATCH")
        print("OK", no)
    except urllib.error.HTTPError as e:
        print("ERR", no, e.read().decode()[:400])
