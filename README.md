# 秘書アプリ（口田さんの個人秘書）

スマホ用の1枚ページ（PWA）。GitHub Pages で公開している。

- `index.html` … アプリ本体（ビルド不要。直したら push で反映）
- `privacy.html` … プライバシー表記
- `reports/` … レポート本文（HTML をそのままアプリに差し込む）
- `watch_notion.py` … Notion の変化を見張る（変化が無ければ AI は起きない）
- `mail_triage.py` … メールの下ごしらえ（未読で返信が必要そう／返事待ちを JSON で返す）
- `check.py` … 検査の1コマンド。`python3 check.py` で11項目を機械的に判定（NG があれば終了コード1）
- `ensure_google_deps.sh` … 実行環境を作り直したときに Google の道具をそろえ直す

状態ファイル（`watch_notion_state.json`・`watch_notion_lastwake`・`wake_log.txt`）は端末に置くだけで、
このリポジトリには入れない（`.gitignore`）。

## 直したときの手順

1. `python3 check.py` … NG が無いことを確かめる
2. `git push` … GitHub Pages に反映（数十秒かかる）
3. 公開URLを `?v=2` のようなクエリ付きで開き直して、キャッシュを避けて確認する
