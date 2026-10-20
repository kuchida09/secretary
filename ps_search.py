#!/usr/bin/env python3
"""Daily papersearch: PubMed esearch (edat) -> efetch -> dedup vs index.csv -> candidates JSON."""
import csv, json, os, re, sys, time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOOL = "kuchida_papersearch_hermes"
EMAIL = "kuchida09@gmail.com"

INDEX = "/workspace/research/80_AI作業場/knowledge/literature/daily-feed/index.csv"

QUERIES = {
 "①": '(("hepatectomy"[tiab] OR "liver resection"[tiab] OR "hepatic resection"[tiab] OR "liver surgery"[tiab]) AND ("deep learning"[tiab] OR "artificial intelligence"[tiab] OR "computer vision"[tiab] OR segmentation[tiab] OR navigation[tiab] OR "structure recognition"[tiab] OR "anatomical recognition"[tiab]))',
 "③": '((cholecystectomy[tiab] OR "critical view of safety"[tiab] OR "bile duct injury"[tiab] OR "cystic duct"[tiab]) AND ("deep learning"[tiab] OR "artificial intelligence"[tiab] OR "computer vision"[tiab] OR segmentation[tiab] OR "real-time"[tiab] OR "critical view"[tiab] OR "vision language"[tiab] OR "AI"[tiab]))',
 "⑤": '((TAPP[tiab] OR "transabdominal preperitoneal"[tiab] OR "transabdominal pre-peritoneal"[tiab] OR TEP[tiab] OR "totally extraperitoneal"[tiab] OR "inguinal hernia"[tiab] OR "groin hernia"[tiab] OR hernioplasty[tiab] OR eTEP[tiab]) AND ("deep learning"[tiab] OR "artificial intelligence"[tiab] OR "computer vision"[tiab] OR segmentation[tiab] OR "structure recognition"[tiab] OR YOLO[tiab] OR "anatomical landmark"[tiab] OR "nerve"[tiab] OR "vas deferens"[tiab]))',
 "⑨": '((surgery[tiab] OR surgical[tiab] OR intraoperative[tiab] OR "operating room"[tiab]) AND ("artificial intelligence"[tiab] OR "deep learning"[tiab] OR "large language model"[tiab] OR "foundation model"[tiab] OR "computer vision"[tiab] OR "machine learning"[tiab]) AND (autonomous[tiab] OR "phase recognition"[tiab] OR "surgical workflow"[tiab] OR "skill assessment"[tiab] OR "surgical phase"[tiab] OR segmentation[tiab] OR "decision support"[tiab] OR "robotic surgery"[tiab] OR "surgical education"[tiab]))',
}


def http(url, data=None, tries=4):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "lit-collect/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(1.5 * (k + 1))
    raise RuntimeError("http %s %s" % (url[:80], last))


def esearch(term, mindate, maxdate):
    ids, retstart, total = [], 0, None
    while True:
        p = {"db": "pubmed", "term": term, "retmax": 200, "retstart": retstart, "retmode": "json",
             "tool": TOOL, "email": EMAIL, "datetype": "edat", "mindate": mindate, "maxdate": maxdate}
        j = json.loads(http(E + "esearch.fcgi?" + urllib.parse.urlencode(p)))
        r = j["esearchresult"]
        total = int(r["count"])
        ids += r["idlist"]
        retstart += 200
        time.sleep(0.4)
        if retstart >= total or not r["idlist"]:
            break
    return total, ids


def text_of(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def parse(pa):
    mc = pa.find("MedlineCitation")
    pmid = text_of(mc.find("PMID"))
    art = mc.find("Article")
    title = text_of(art.find("ArticleTitle"))
    ab = art.find("Abstract")
    abs_parts = []
    if ab is not None:
        for t in ab.findall("AbstractText"):
            lab = t.get("Label")
            abs_parts.append((lab + ": " if lab else "") + text_of(t))
    abstract = "\n".join(abs_parts)
    d = art.find("Journal/JournalIssue/PubDate")
    year = text_of(d.find("Year")) if d is not None else ""
    if not year and d is not None:
        m = re.search(r"(19|20)\d\d", text_of(d.find("MedlineDate")))
        year = m.group(0) if m else ""
    journal = text_of(art.find("Journal/ISOAbbreviation")) or text_of(art.find("Journal/Title"))
    doi = ""
    for a in pa.findall("PubmedData/ArticleIdList/ArticleId"):
        if a.get("IdType") == "doi":
            doi = text_of(a)
    aus = []
    for au in art.findall("AuthorList/Author"):
        ln, fn = text_of(au.find("LastName")), text_of(au.find("ForeName"))
        if ln:
            aus.append((ln + " " + fn).strip())
    first = aus[0] if aus else ""
    ptypes = [text_of(x) for x in art.findall("PublicationTypeList/PublicationType")]
    return dict(pmid=pmid, title=title, abstract=abstract, year=year, journal=journal,
                doi=doi, first_author=first, authors=aus, pubtypes=ptypes)


def efetch(pmids):
    out = []
    for i in range(0, len(pmids), 100):
        chunk = pmids[i:i + 100]
        data = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(chunk), "retmode": "xml", "tool": TOOL}).encode()
        root = ET.fromstring(http(E + "efetch.fcgi", data=data))
        for pa in root.findall("PubmedArticle"):
            try:
                out.append(parse(pa))
            except Exception as e:
                print("parse fail", e, file=sys.stderr)
        time.sleep(0.4)
    return out


def load_have():
    pm, doi, ti = set(), set(), set()
    with open(INDEX, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("pmid"):
                pm.add(r["pmid"].strip())
            if r.get("doi"):
                doi.add(r["doi"].strip().lower())
            if r.get("title"):
                ti.add(re.sub(r"[^a-z0-9]", "", r["title"].lower()))
    return pm, doi, ti


def main():
    mindate, maxdate = sys.argv[1], sys.argv[2]
    only = sys.argv[3:] if len(sys.argv) > 3 else list(QUERIES)
    have_pm, have_doi, have_ti = load_have()
    result = {}
    for t in only:
        total, ids = esearch(QUERIES[t], mindate, maxdate)
        new = [p for p in ids if p not in have_pm]
        recs = efetch(new) if new else []
        # second-pass dedup by doi/title
        cands = []
        for r in recs:
            if r["doi"] and r["doi"].lower() in have_doi:
                continue
            key = re.sub(r"[^a-z0-9]", "", r["title"].lower())
            if key in have_ti:
                continue
            cands.append(r)
        result[t] = dict(total=total, n_ids=len(ids), n_new=len(cands), cands=cands)
        print("=== %s: total=%d ids=%d new=%d ===" % (t, total, len(ids), len(cands)))
        for c in cands:
            print("- %s | %s | %s | %s" % (c["pmid"], c["year"], c["journal"], c["title"][:110]))
    with open("/workspace/secretary/ps_candidates.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
