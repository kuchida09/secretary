#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/workspace/secretary")
from notion_ds import req

DB = "73030fec-90a9-4b83-8a6a-a0b97564d97a"

rows = json.load(open("/workspace/secretary/ps_rows.json", encoding="utf-8"))
meta = {
    "42844276": ("Nature Communications", "2026", "Guo Haiman", "10.1038/s41467-026-77498-w", "③"),
    "42881307": ("Surgical Endoscopy", "2026", "Haynes Nathanael", "10.1007/s00464-026-13321-3", "⑨"),
    "42879739": ("Surgical Innovation", "2026", "McCarrick Cathleen A", "10.1177/15533506261498412", "⑨"),
    "42855513": ("Surgical Endoscopy", "2026", "Farzadmanesh Mohammad Javad", "10.1007/s00464-026-13404-1", "⑨"),
    "42857507": ("Frontiers in Oncology", "2026", "Cheang Waiian", "10.3389/fonc.2026.1947280", "⑨"),
    "42849513": ("Annals of Surgery", "2026", "Gandhewar Rishikesh", "10.1097/SLA.0000000000007229", "⑨"),
    "42869423": ("The American Surgeon", "2026", "Lies Isaac H", "10.1177/00031348261496616", "⑨"),
}
titles = {
    "42844276": "A multitask framework for automated multi-frame right upper quadrant ultrasound interpretation and clinical decision support.",
    "42881307": "Proprietary platform artificial intelligence-based segmentation of surgical videos facilitates review and rating of operative recordings.",
    "42879739": "Surgeon-Derived Design Insights Regarding Real-Time Artificial Intelligence Decision Support for Endoscopic Cancer Surgery.",
    "42855513": "Deep learning-based semantic segmentation of abdominal wall layers during direct optical trocar insertion: toward AI-assisted surgical access.",
    "42857507": "Artificial intelligence in the surgical management for colorectal cancer: current applications and future directions.",
    "42849513": "Surgical Artificial Intelligence Innovation Trends and Regulatory Insights: A Systematic Analysis of Food and Drug Administration-Approved Devices.",
    "42869423": "Artificial Intelligence Across the Surgical Research Workflow: A Stage-Specific Framework for Benefits, Failure Modes, and Oversight.",
}
qtext = {"③": "③胆嚢摘出のCVS自動認識AI・胆管損傷予防AI(edat 直近2週間)",
         "⑨": "⑨外科一般×AI(edat 直近2週間)"}

for r in rows:
    p = r["pmid"]
    j, y, au, doi, tp = meta[p]
    props = {
        "タイトル": {"title": [{"text": {"content": titles[p]}}]},
        "ステータス": {"select": {"name": "未読"}},
        "関連プロジェクト": {"multi_select": [{"name": "外科AI全般"}]},
        "誌名": {"rich_text": [{"text": {"content": j}}]},
        "著者": {"rich_text": [{"text": {"content": au}}]},
        "検索クエリ": {"rich_text": [{"text": {"content": qtext[tp]}}]},
        "URL": {"url": "https://pubmed.ncbi.nlm.nih.gov/%s/" % p},
        "PMID/DOI": {"rich_text": [{"text": {"content": "PMID: %s / DOI: %s" % (p, doi)}}]},
        "要約": {"rich_text": [{"text": {"content": r["summary_ja"]}}]},
    }
    res = req("/pages", "POST", {"parent": {"database_id": DB}, "properties": props})
    if "_error" in res:
        print("ERROR", p, res)
    else:
        print("OK", p, res["id"])
