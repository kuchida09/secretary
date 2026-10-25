"""アプリに出るカードの中身を、書き方の規則で機械的に点検する。

規則の出どころ: records/style/アプリの中身の書き方.md（Claude のフィードバックから）
使い方:
  python3 card_check.py            # 未確認・判断延期のカードを点検
  python3 card_check.py --all      # 取り下げ以外のすべて
  python3 card_check.py --quiet    # 違反が無ければ何も出さない（定期実行用）
"""
import json, re, sys, urllib.request

K = open("/workspace/.hermes/notion_key").read().strip()
H = {"Authorization": "Bearer " + K, "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
PR = "b61639b3-c830-4142-bd15-ebebc99362d5"

BAN = ["適切に", "適切な対応", "検討する", "必要に応じて", "その他", "などなど", "いい感じ"]
JARGON = ["κ", "AUC", "CNN", "PMID", "p値", "95%CI", "交差検証", "感度", "特異度", "ROC"]
ACTION = ["作る", "出す", "送る", "返す", "入れる", "直す", "埋める", "整理", "比較", "確認",
          "実行", "頼む", "断る", "受ける", "押す", "見る", "読む", "決める", "進める", "やる",
          "放置", "そのまま", "様子", "何もしない", "待つ", "保留", "見送", "実施", "連絡", "依頼",
          "提出", "登録", "更新", "削除", "保存", "見直", "止め", "始め", "渡す", "集め", "書き",
          "申し込", "申請", "発注", "任せ", "選ぶ", "決め", "調べ", "確認", "受け取",
          "確かめ", "聞き直", "作り直", "このまま", "見直す", "頼み", "断り", "受け", "依頼"]


def looks_like_action(text):
    """選択肢が『する動詞』で書かれているかをゆるく判定する。"""
    t = text.lstrip("・-* ").strip()
    if any(a in t for a in ACTION):
        return True
    if "する" in t or "します" in t or "します" in t:
        return True
    return t[:1] in "作出送返入直埋整比確実頼断受押見読決進や放様待保見実連依提登更削保書申発選調受確聞"


def api(url, body=None, method="GET"):
    d = json.dumps(body).encode() if body is not None else None
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, data=d, headers=H, method=method), timeout=120).read())


def title_of(x):
    return "".join(s["plain_text"] for s in x["properties"]["件名"]["title"])


def body_of(pid):
    return (api(f"https://api.notion.com/v1/pages/{pid}/markdown").get("markdown") or "").strip()


def line_starting(body, *keys):
    for ln in body.split("\n"):
        s = ln.strip().lstrip("-*・ ").strip()
        for k in keys:
            if s.startswith(k):
                return s
    return ""


def check(title, body):
    """規則に反する点を日本語で列挙する（無ければ空リスト）。"""
    bad = []
    if not body:
        return ["本文が空（『Hermes に本文を作らせる』が要る）"]
    if title in body.split("\n")[0]:
        bad.append("1行目が題名そのもの（題名の繰り返し）")

    youten = line_starting(body, "要点:")
    if not youten:
        bad.append("『要点:』行が無い")
    else:
        v = youten.split(":", 1)[1].strip()
        if len(v) > 42:
            bad.append(f"要点が長い（{len(v)}字。40字以内に）")
        if v.endswith("について") or v.endswith("についてです。"):
            bad.append("要点が『〜について』で終わっている（結論を書く）")
        if v.endswith("です。"):
            bad.append("要点が状態の説明で終わっている（決めてほしいことを書く）")

    if not line_starting(body, "変わること:"):
        bad.append("『変わること:』行が無い")
    elif len(line_starting(body, "変わること:")) > 66:
        bad.append("『変わること』が長い（60字以内に）")

    if not line_starting(body, "動く人:"):
        bad.append("『動く人:』行が無い（誰が動くか）")

    if not line_starting(body, "何の話か"):
        bad.append("『何の話か』の見出しが無い")
    if not line_starting(body, "どう答えるか"):
        bad.append("『どう答えるか』の見出しが無い")
    if "答えるとどうなるか" not in body:
        bad.append("『答えるとどうなるか』の行が無い（押した後の動作）")

    opts = re.findall(r"^\s*([123])[:：]\s*(.+)$", body, re.M)
    if len(opts) != 3:
        bad.append(f"選択肢が3つでない（{len(opts)}個）")
    else:
        if not any("おすすめ" in o[1] for o in opts):
            bad.append("選択肢に『（おすすめ）』が無い")
        for n, o in opts:
            if not looks_like_action(o):
                bad.append(f"選択肢{n}が動詞で始まっていない（何をするか不明）")
            if "（" not in o and "(" not in o:
                bad.append(f"選択肢{n}に『押した後どうなるか』が無い")
        if len({o[1][:14] for o in opts}) < 3:
            bad.append("選択肢の書き出しが似すぎている（違いが見えない）")
    # 専門外の語
    for w in JARGON:
        for ln in body.split("\n"):
            if w in ln and "（" not in ln and "(" not in ln:
                bad.append(f"専門外の語『{w}』に説明が無い")
                break
    for b in BAN:
        if b in body:
            bad.append(f"曖昧な言い方『{b}』")
    # 長すぎる一文
    for ln in body.split("\n"):
        s = ln.strip().lstrip("-*・ ").strip()
        if len(s) > 90 and not s.startswith("http"):
            bad.append(f"一文が長い（{len(s)}字）")
            break
    return bad


def main():
    quiet = "--quiet" in sys.argv
    rows, cursor = [], None
    for _ in range(4):
        b = {"page_size": 100}
        if cursor:
            b["start_cursor"] = cursor
        r = api(f"https://api.notion.com/v1/databases/{PR}/query", b, method="POST")
        rows += r["results"]
        if not r.get("has_more"):
            break
        cursor = r.get("next_cursor")
    ng = []
    for x in rows:
        t = title_of(x)
        st = (x["properties"].get("状態", {}).get("select") or {}).get("name", "")
        if st in ("対応済み", "見送る"):
            continue
        if "--all" not in sys.argv and st not in ("未確認", "判断延期"):
            continue
        if t.startswith("【サンプル】") or t.startswith("【仮想】"):
            continue
        bad = check(t, body_of(x["id"]))
        if bad:
            ng.append((t, bad))
    if quiet and not ng:
        return 0
    print(f"  中身の点検: {len(ng)} 件が規則に不足（未確認・判断延期のうち）")
    for t, bad in ng:
        print(f"   - {t[:52]}")
        for b in bad[:5]:
            print(f"      ・{b}")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
