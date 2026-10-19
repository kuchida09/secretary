#!/usr/bin/env python3
"""Google ドライブへの書き戻しを、Windows の I: に依存せず Drive API で行う。

- 対象: research/80_AI作業場 の決められたフォルダ（I: 版の 08_writeback_to_drive.ps1 と同じ範囲）
- 追加と更新だけ（ドライブ側のファイルは消さない）
- ドライブ側の方が新しいファイルは上書きしない
- 結果は /workspace/writeback.log に 1 行で残す
使い方: python3 writeback_via_api.py            # 実行
        python3 writeback_via_api.py --dry       # 何をするかだけ表示
"""
import json
import mimetypes
import os
import pathlib
import sys
import time
import urllib.parse
import urllib.request
import uuid

TOK = "/workspace/.hermes/google_token.json"
LOCAL = pathlib.Path("/workspace/research/80_AI作業場")
DRIVE_ROOT = "1bCq9Zo5y_-e46L585MmfII6wikjYAGgO"  # マイドライブ/80_AI作業場
DIRS = ["knowledge/literature", "knowledge/academia", "knowledge/_maintenance",
        "knowledge/topics", "ops/literature", "ops/routines", "ops/morning", "outbox"]
LOG = pathlib.Path("/workspace/writeback.log")
SKIP = {"__pycache__", ".git", ".DS_Store"}
DRY = "--dry" in sys.argv

_tok = json.load(open(TOK))


def refresh():
    d = _tok
    body = urllib.parse.urlencode({"client_id": d["client_id"], "client_secret": d["client_secret"],
                                   "refresh_token": d["refresh_token"], "grant_type": "refresh_token"}).encode()
    req = urllib.request.Request(d["token_uri"], data=body)
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read())
    d["token"] = j["access_token"]
    d["expiry"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + j.get("expires_in", 3600)))
    json.dump(d, open(TOK, "w"), ensure_ascii=False)


def api(url, method="GET", body=None, raw=None, ctype="application/json", retry=True):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": "Bearer " + _tok["token"], "Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            b = r.read()
            return json.loads(b) if b else {}
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            refresh()
            return api(url, method, body, raw, ctype, retry=False)
        raise


def jst():
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 9 * 3600))


def log(msg):
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{jst()} {msg}\n")


def list_children(fid):
    out = []
    tok = None
    while True:
        p = {"q": f"'{fid}' in parents and trashed=false",
             "fields": "nextPageToken,files(id,name,mimeType,modifiedTime,md5Checksum)",
             "pageSize": "1000"}
        if tok:
            p["pageToken"] = tok
        r = api("https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(p))
        out += r.get("files", [])
        tok = r.get("nextPageToken")
        if not tok:
            return out


def ensure_folder(parent_id, name, cache):
    key = (parent_id, name)
    if key in cache:
        return cache[key]
    q = f"'{parent_id}' in parents and name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    r = api("https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode({"q": q, "fields": "files(id)"}))
    if r.get("files"):
        fid = r["files"][0]["id"]
    elif DRY:
        fid = "DRY"
    else:
        fid = api("https://www.googleapis.com/drive/v3/files", "POST",
                  {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]})["id"]
    cache[key] = fid
    return fid


def upload(parent_id, name, path, existing_id):
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    if DRY:
        return "dry"
    boundary = "b" + uuid.uuid4().hex
    meta = {"name": name}
    if existing_id:
        meta["parents"] = [parent_id]
    body = b""
    body += ("--" + boundary + "\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n" +
             json.dumps(meta) + "\r\n").encode()
    body += ("--" + boundary + "\r\nContent-Type: " + ctype + "\r\n\r\n").encode()
    body += path.read_bytes() + b"\r\n"
    body += ("--" + boundary + "--").encode()
    if existing_id:
        url = f"https://www.googleapis.com/upload/drive/v3/files/{existing_id}?uploadType=multipart"
        return api(url, "PATCH", raw=body, ctype="multipart/related; boundary=" + boundary)
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    return api(url, "POST", raw=body, ctype="multipart/related; boundary=" + boundary)


def main():
    # ドライブ側の目録を作る（対象フォルダ配下だけ）
    folder_cache = {}
    files_map = {}   # (parent_id, name) -> {id, modifiedTime}

    def walk_drive(fid, rel):
        for c in list_children(fid):
            if c["mimeType"] == "application/vnd.google-apps.folder":
                walk_drive(c["id"], rel + "/" + c["name"])
            else:
                files_map[(rel, c["name"])] = c

    for d in DIRS:
        parts = d.split("/")
        fid = DRIVE_ROOT
        for p in parts:
            fid = ensure_folder(fid, p, folder_cache)
        if fid == "DRY":
            continue
        walk_drive(fid, d)

    copied = 0
    failed = 0
    for d in DIRS:
        base = LOCAL / d
        if not base.exists():
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x not in SKIP]
            rel = pathlib.Path(root).relative_to(LOCAL).as_posix()
            for fn in files:
                if fn in SKIP:
                    continue
                lp = pathlib.Path(root) / fn
                try:
                    lm = lp.stat().st_mtime
                except Exception:
                    continue
                key = (rel, fn)
                drv = files_map.get(key)
                if drv:
                    dt = drv.get("modifiedTime", "")
                    try:
                        dtm = time.mktime(time.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S"))
                    except Exception:
                        dtm = 0
                    if lm <= dtm + 1:
                        continue  # ドライブの方が新しい → 触らない
                try:
                    fid = DRIVE_ROOT
                    for p in rel.split("/"):
                        fid = ensure_folder(fid, p, folder_cache)
                    last = None
                    for attempt in range(5):
                        try:
                            upload(fid, fn, lp, drv["id"] if drv else None)
                            last = None
                            break
                        except urllib.error.HTTPError as e:
                            last = e
                            if e.code in (403, 429, 500, 503):
                                time.sleep(2 * (attempt + 1))
                                continue
                            raise
                    if last is not None:
                        raise last
                    copied += 1
                    time.sleep(0.12)
                except Exception as exc:
                    failed += 1
                    print("FAIL", key, type(exc).__name__, str(exc)[:120])
    msg = f"失敗: {failed} 件" if failed else f"成功: 更新 {copied} 件（Drive API 経由）"
    print(msg)
    if not DRY:
        log(msg)


if __name__ == "__main__":
    main()
