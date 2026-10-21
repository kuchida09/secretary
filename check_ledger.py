import json
led = {r["番号"]: r for r in json.load(open("/workspace/secretary/ledger.json"))}
for no in ["①", "③", "⑤", "⑨"]:
    r = led[no]
    print(no, r["現在の頻度"], r["ステータス"], r["直近検索日"], r.get("直近発見日"), r["連続0件回数"], len(r.get("備考") or ""))
