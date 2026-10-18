import json, os, time, urllib.request

KEY = os.environ.get("NOTION_API_KEY")
HDR = {"Authorization": "Bearer " + (KEY or ""), "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
MEMO = "3fde71bc-ecb6-81af-8624-ebb86a23bd14"

def req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=HDR, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:500]}

ITEMS = [
 ("3fde71bc-ecb6-8104-bba9-f726994add7b",
  "- 対応: 2026-10-18 原因は OAuth 同意画面の公開ステータスが「テスト」のままのため、機微なスコープの refresh token が7日で失効していたこと。Google Auth Platform →「対象」→「アプリを公開」に切り替えれば審査は不要で7日制限が消える。切替後は一度だけ再認可して新しいトークンを取り直す必要あり。Discord で報告済み。"),
 ("3fde71bc-ecb6-81ce-8f0e-e2c230138614",
  "- 対応: 2026-10-18 上と同じ内容（ボタンの反応が見えず二重に送信された分として処理）。"),
 ("3fde71bc-ecb6-81b0-b2ce-f4309a693527",
  "- 対応: 2026-10-18 アプリを直した: (1)「調べてもらう」を押すと「依頼済み ✓」に変わり、ページを読み直して送信できたことを確認してから結果を表示するようにした (2) 対応済みのメモは一覧に出さない（既に反映済み）。git push 済み。"),
 ("3fde71bc-ecb6-8160-bedb-f8caed94f4df",
  "- 対応: 2026-10-18 dots は OpenAI の常時稼働エージェント（モデルは GPT-6 Astra、専用のクラウドPC とブラウザを持ち、指示がなくても自発的に調べる。2026-09-29 発表、Pro・Business のプレミアム席・Enterprise 向け）。いまの秘書との違い（常時稼働の実体・自発的な調査・アプリ外への通知）を Discord で報告済み。"),
 ("3fde71bc-ecb6-81b6-932d-f3777179a8dc",
  "- 対応: 2026-10-18 Notion の連携のコメント機能は、notion.so/my-integrations の該当コネクション → 構成（Capabilities）で「Read comments」「Insert comments」をオンにする（初期はオフ）。ページ側は ••• →「接続」でそのコネクションを共有しておく。オンにする操作は利用者の管理画面でのみ可能。Discord で報告済み。"),
 ("3fde71bc-ecb6-8142-a383-d1d15c32adf4",
  "- 対応: 2026-10-18「この案で進める」等を押した後に出ていた長い説明文を削除した（上部の短い表示だけに）。git push 済み。"),
]

for bid, text in ITEMS:
    r = req("PATCH", "https://api.notion.com/v1/blocks/%s/children" % MEMO,
            {"children": [{"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}}],
             "after": bid})
    print(bid, "->", "OK" if r.get("object") == "list" else r)
    time.sleep(0.5)
