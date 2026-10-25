# Claude に渡す封筒（TASK.md の型）

使い方: この型をコピーして各項目を埋め、ファイルとして渡す。口頭の長文をそのまま渡さない。
呼び方の例:

```
export CLAUDE_CODE_OAUTH_TOKEN="$(cat /workspace/.hermes/claude_oauth_token)"
/workspace/tools/bin/claude-task \
  --dir /workspace/secretary \
  --prompt-file /workspace/secretary/_task_<名前>.md \
  --allow "Read,Edit,Write" --turns 10 --budget 1.00
```

- 本体: `/workspace/tools/claude/node_modules/.bin/claude`（`/workspace/tools/bin/claude-task` が安全設定つきで包む）
- 認証は定額のトークン（`CLAUDE_CODE_OAUTH_TOKEN`）。`ANTHROPIC_API_KEY` は必ず外す（残っていると従量課金に切り替わる）
- 子には会話が渡らない。ここに書いていないことは存在しない

---

目的:

成果物（絶対パス）:

合格条件（機械で確かめられる形で。例: 「この JSON が読める」「見出しが5つ」「構文検査が通る」）:

触ってよい範囲:

触ってはいけない範囲:

渡す事実（確認済みのものだけ。ここに無いものは「要確認」と書く）:

禁止: サブエージェントを起こさない／コミットしない／外部に送らない／事実や出典を作らない

上限: --max-turns 10 / --max-budget-usd 1.00

道具: --allowedTools "Read,Grep,Glob"（編集させるなら "Read,Grep,Glob,Write,Edit"。Bash は足さない）

検証（こちらでやる）: 差分を読む → 構文検査 → `python3 /workspace/secretary/check.py`。子の「できました」は採らない。
