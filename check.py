#!/usr/bin/env python3
"""秘書のしくみの「検査の1コマンド」。

使い方:  python3 /workspace/secretary/check.py
出力:  OK / NG / 注意 の一覧。NG が1つでもあれば終了コード 1。

考え方（ハーネス設計の「柵」）: 書いたものを、機械的に検証する。
判定は誰が実行しても同じ結果になるように、スクリプトだけで行う（AI を使わない）。
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.request

HOME = pathlib.Path("/workspace/secretary")
APP_URL = "https://kuchida09.github.io/secretary/"
REQUIRED_PARTS = ['id="tok"', "function load", "function mdToHtml", "function blocksToHtml", 'txt(p["場所"])']
SECRET_PAT = re.compile(r"(ntn_[A-Za-z0-9]{20,}|secret_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_\-]{20,}|Bearer\s+[A-Za-z0-9._\-]{20,})")
PATIENT_PAT = re.compile(r"(患者氏名|患者ID|カルテ番号|診療録番号|マイナンバー)")
SKIP_DIRS = {".git", "__pycache__", "node_modules"}

results = []  # (状態, 名前, 補足)


def add(state, name, detail=""):
    results.append((state, name, detail))


def tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=HOME, capture_output=True, text=True).stdout.split()
    return [HOME / f for f in out]


def check_python_syntax():
    bad = []
    for p in sorted(HOME.glob("*.py")):
        r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(p.name)
    add("NG" if bad else "OK", "Python の構文", "、".join(bad))


def check_bash_syntax():
    bad = []
    for p in sorted(HOME.glob("*.sh")):
        r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(p.name)
    add("NG" if bad else "OK", "シェルの構文", "、".join(bad))


def check_monitor_runs():
    env = dict(os.environ, WATCH_DRY="1")  # 検査は「見るだけ」。状態を書き換えない
    r = subprocess.run([sys.executable, str(HOME / "watch_notion.py")], capture_output=True, text=True, cwd=HOME, env=env)
    first = (r.stdout or r.stderr).strip().split("\n")[0][:120]
    ok = r.returncode == 0 and (first == "" or first.startswith("✅"))
    add("OK" if ok else "NG", "監視スクリプトが動く", first)


def check_app_js():
    html = (HOME / "index.html").read_text(encoding="utf-8")
    m = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)
    if not m:
        add("NG", "アプリの JavaScript の構文", "script が見つからない")
        return
    tmp = pathlib.Path("/tmp/_check_app.js")
    tmp.write_text("\n".join(m), encoding="utf-8")
    r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, text=True)
    add("OK" if r.returncode == 0 else "NG", "アプリの JavaScript の構文", (r.stderr or "").strip().split("\n")[0][:160])


def check_app_parts():
    html = (HOME / "index.html").read_text(encoding="utf-8")
    missing = [p for p in REQUIRED_PARTS if p not in html]
    add("NG" if missing else "OK", "アプリの必須部品", ("欠け: " + "、".join(missing)) if missing else "")


def check_no_secrets():
    hits = []
    for p in tracked_files():
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for line in t.split("\n"):
            if SECRET_PAT.search(line) and "placeholder" not in line and "ntn_ または" not in line:
                hits.append(p.name)
                break
    add("NG" if hits else "OK", "公開リポジトリに秘密情報が無い", "、".join(sorted(set(hits))))


def check_no_patient_info():
    hits = []
    for p in tracked_files():
        if p.name == "check.py":  # 検査の検索語そのものが引っかかるので除く
            continue
        if p.suffix.lower() not in (".md", ".txt", ".html", ".py", ".json", ".csv"):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if PATIENT_PAT.search(t):
            hits.append(p.name)
    add("NG" if hits else "OK", "患者情報らしき記述が無い", "、".join(sorted(set(hits))))


def notion_key():
    v = os.environ.get("NOTION_API_KEY", "").strip()
    if v:
        return v
    for p in ("/home/kuchida09/hermes-data/.hermes/notion_key", "/workspace/.hermes/notion_key",
              str(pathlib.Path.home() / ".hermes" / "notion_key")):
        try:
            t = pathlib.Path(p).read_text(encoding="utf-8").strip()
            if t:
                return t
        except Exception:
            continue
    return ""


def check_notion():
    key = notion_key()
    if not key:
        add("NG", "Notion に接続できる", "トークンが見つからない")
        return
    h = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
    ds = {
        "確認・提案": "60242da1-b213-4118-ae82-f8782a816cb2",
        "タスク": "ef21b283-795e-4fec-8311-2e40c4cb0c57",
        "レポート": "a54924f2-1ca7-44f5-b5d1-47576d368aff",
        "確認事項": "8d58d65b-8d15-4012-866a-772ee3942500",
    }
    bad, report_paths = [], []
    for name, d in ds.items():
        try:
            req = urllib.request.Request(f"https://api.notion.com/v1/data_sources/{d}/query",
                                         data=json.dumps({"page_size": 100}).encode(), headers=h, method="POST")
            rows = json.loads(urllib.request.urlopen(req, timeout=30).read()).get("results", [])
            if name == "レポート":
                for r in rows:
                    loc = "".join(x.get("plain_text", "") for x in r["properties"].get("場所", {}).get("rich_text", [])).strip()
                    if loc.endswith((".html", ".md")):
                        report_paths.append(loc)
        except Exception as exc:
            bad.append(f"{name}({type(exc).__name__})")
    add("NG" if bad else "OK", "Notion に接続できる", "、".join(bad))

    # レポート本文は Notion 側に置く運用（場所に Notion のURLを入れる）。ローカルの .html/.md を
    # 指している場合だけ実在を確かめる。どちらの場合も項目を必ず1つ出す（検査の数を保つ）。
    missing = [loc for loc in report_paths if not (HOME / loc.lstrip("/")).exists()]
    if not report_paths:
        add("OK", "レポート本文のファイルが実在する", "ローカルに置いた本文は無し（Notion側に置く運用）")
    else:
        add("NG" if missing else "OK", "レポート本文のファイルが実在する",
            "欠け: " + "、".join(missing) if missing else f"{len(report_paths)} 件すべて実在")


def check_report_summary():
    """レポート本文の先頭に「要点」があるか（#67・2026-10-24 承認）。

    Notion 側に置いた本文の、直近3件だけを見る。先頭5ブロックに
    要点にあたる見出し・文が無ければ「注意」を出す（NG にはしない＝止めない）。
    """
    key = notion_key()
    if not key:
        add("注意", "レポート本文の先頭に要点がある", "トークンが見つからない")
        return
    h = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
    try:
        req = urllib.request.Request(
            "https://api.notion.com/v1/data_sources/a54924f2-1ca7-44f5-b5d1-47576d368aff/query",
            data=json.dumps({"page_size": 20,
                             "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}]}).encode(),
            headers=h, method="POST")
        rows = json.loads(urllib.request.urlopen(req, timeout=30).read()).get("results", [])
    except Exception as exc:
        add("注意", "レポート本文の先頭に要点がある", type(exc).__name__)
        return

    keywords = ("要点", "まとめ", "ひとこと", "3行", "結論", "要約")
    checked, missing = 0, []
    for r in rows:
        loc = "".join(x.get("plain_text", "") for x in r["properties"].get("場所", {}).get("rich_text", [])).strip()
        m = re.search(r"([0-9a-f]{32})", loc)
        if not m:
            continue
        checked += 1
        if checked > 3:
            break
        try:
            breq = urllib.request.Request(f"https://api.notion.com/v1/blocks/{m.group(1)}/children?page_size=8",
                                          headers=h)
            blocks = json.loads(urllib.request.urlopen(breq, timeout=30).read()).get("results", [])
        except Exception:
            continue
        head = []
        for b in blocks:
            t = b.get("type")
            if t in ("paragraph", "heading_1", "heading_2", "heading_3"):
                head.append("".join(x.get("plain_text", "") for x in b[t]["rich_text"]))
        if not any(k in " ".join(head[:5]) for k in keywords):
            title = "".join(x.get("plain_text", "") for x in r["properties"].get("件名", {}).get("title", []))
            missing.append(title[:24] or "（無題）")
    if not checked:
        add("OK", "レポート本文の先頭に要点がある", "Notion 側の本文は無し")
    else:
        add("注意" if missing else "OK", "レポート本文の先頭に要点がある",
            ("先頭に要点が無い: " + "、".join(missing)) if missing else f"直近{checked}件は要点あり")


def check_published():
    try:
        with urllib.request.urlopen(APP_URL, timeout=30) as r:
            live = r.read()
        add("OK", "公開アプリが生きている", f"{len(live)} バイト")
    except Exception as exc:
        add("NG", "公開アプリが生きている", type(exc).__name__)
        return
    local = (HOME / "index.html").read_bytes()
    if len(live) != len(local):
        add("注意", "公開版と手元が同じ", f"公開 {len(live)} / 手元 {len(local)} バイト（push 忘れの可能性）")
    else:
        add("OK", "公開版と手元が同じ", f"{len(local)} バイト")


def check_card_content():
    """アプリに出るカードの中身が、書き方の規則を満たしているか（card_check.py）。"""
    r = subprocess.run([sys.executable, "card_check.py", "--quiet"], cwd=HOME,
                       capture_output=True, text=True)
    out = (r.stdout or "").strip()
    if r.returncode == 0 and not out:
        add("OK", "カードの中身が規則を満たす", "未確認・判断延期のカードはすべて合格")
    else:
        first = "／".join(out.splitlines()[1:4])[:180]
        add("注意", "カードの中身に不足", first or "card_check.py の出力を確認")


def main():
    os.chdir(HOME)
    check_python_syntax()
    check_bash_syntax()
    check_monitor_runs()
    check_app_js()
    check_app_parts()
    check_no_secrets()
    check_no_patient_info()
    check_notion()
    check_report_summary()
    check_published()
    check_card_content()

    ng = [r for r in results if r[0] == "NG"]
    for state, name, detail in results:
        mark = {"OK": "OK  ", "NG": "NG  ", "注意": "注意"}[state]
        print(f"{mark} {name}" + (f" — {detail}" if detail else ""))
    print(f"--- NG {len(ng)} 件 / 全 {len(results)} 件 ---")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
