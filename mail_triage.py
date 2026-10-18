#!/usr/bin/env python3
"""返信が必要なメール／返信待ちのメールを拾う（「下ごしらえ」用）。

出力: JSON
  {"unread_need_reply": [...], "awaiting_reply": [...], "me": "..."}

- unread_need_reply: 未読で、返信が必要そうなもの（広告・自動通知を除く）
- awaiting_reply: 自分が最後に送ったまま、相手から返事が来ていないスレッド
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ME = "kuchida09@gmail.com"
NO_REPLY_HINTS = (
    "no-reply", "noreply", "donotreply", "do-not-reply", "notification",
    "newsletter", "mailer", "bounce", "accounts.google.com", "amazon.co.jp",
    "support@", "info@", "news@", "メルマガ",
)
JST = timezone(timedelta(hours=9))


def token_path():
    for d in (os.environ.get("HERMES_HOME"), str(Path.home() / ".hermes"),
              "/workspace/.hermes", "/home/kuchida09/hermes-data/.hermes"):
        if d and (Path(d) / "google_token.json").exists():
            return Path(d) / "google_token.json"
    sys.exit(json.dumps({"status": "error", "message": "google_token.json が見つかりません。"}, ensure_ascii=False))


def service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    p = token_path()
    creds = Credentials.from_authorized_user_file(str(p))
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        p.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def headers(msg):
    h = {x["name"].lower(): x["value"] for x in msg.get("payload", {}).get("headers", [])}
    return h


def needs_reply(sender, subject):
    s = (sender or "").lower()
    if any(x in s for x in NO_REPLY_HINTS):
        return False
    t = (subject or "").lower()
    if any(x in t for x in ("メルマガ", "ニュースレター", "配信", "自動送信", "unsubscribe")):
        return False
    return True


def main():
    svc = service()
    out = {"me": ME, "unread_need_reply": [], "awaiting_reply": []}

    # 1) 未読で返信が必要そうなもの
    q = "is:unread -category:promotions -category:social newer_than:7d"
    ids = svc.users().messages().list(userId="me", q=q, maxResults=25).execute().get("messages", [])
    for m in ids:
        msg = svc.users().messages().get(userId="me", id=m["id"], format="metadata",
                                        metadataHeaders=["From", "Subject", "Date"]).execute()
        h = headers(msg)
        if not needs_reply(h.get("from", ""), h.get("subject", "")):
            continue
        out["unread_need_reply"].append({
            "id": m["id"], "thread_id": msg.get("threadId"),
            "from": h.get("from", ""), "subject": h.get("subject", ""),
            "date": h.get("date", ""), "snippet": (msg.get("snippet") or "")[:200],
        })

    # 2) 自分が最後に送ったまま返事が来ていないスレッド
    sent = svc.users().messages().list(userId="me", q="in:sent newer_than:21d", maxResults=60).execute().get("messages", [])
    seen = set()
    for m in sent:
        msg = svc.users().messages().get(userId="me", id=m["id"], format="metadata",
                                        metadataHeaders=["From", "To", "Subject", "Date"]).execute()
        tid = msg.get("threadId")
        if tid in seen:
            continue
        seen.add(tid)
        th = svc.users().threads().get(userId="me", id=tid, format="metadata",
                                       metadataHeaders=["From", "To", "Subject", "Date"]).execute()
        msgs = th.get("messages", [])
        if not msgs:
            continue
        last = headers(msgs[-1])
        frm = (last.get("from", "") or "").lower()
        if ME.lower() not in frm:
            continue  # 最後は相手から → 返信待ちではない
        if len(msgs) < 2:
            continue  # 一方的な送信は対象外
        try:
            d = datetime.strptime(last.get("date", ""), "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            d = None
        days = (datetime.now(timezone.utc) - d).days if d else None
        if days is not None and days < 2:
            continue  # 送ったばかりは待たない
        out["awaiting_reply"].append({
            "thread_id": tid, "subject": last.get("subject", ""),
            "to": last.get("to", ""), "sent_date": last.get("date", ""),
            "days_waiting": days, "messages": len(msgs),
        })

    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
