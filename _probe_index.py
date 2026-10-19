import csv, os, pathlib, collections, json

BASE = "/workspace/research/80_AI作業場/knowledge/literature"
idx = os.path.join(BASE, "daily-feed", "index.csv")
rows = []
with open(idx, encoding="utf-8") as f:
    r = csv.DictReader(f)
    cols = r.fieldnames
    for row in r:
        rows.append(row)
print("rows", len(rows))
print("cols", len(cols))

def blank(v):
    return v is None or not str(v).strip()

no_pmid = [r for r in rows if blank(r.get("pmid"))]
no_doi = [r for r in rows if blank(r.get("doi"))]
no_title = [r for r in rows if blank(r.get("title"))]
no_author = [r for r in rows if blank(r.get("first_author"))]
no_year = [r for r in rows if blank(r.get("year"))]
print("no_pmid", len(no_pmid))
print("no_doi", len(no_doi))
print("no_title", len(no_title))
print("no_first_author", len(no_author))
print("no_year", len(no_year))

pmids = [r["pmid"] for r in rows if not blank(r.get("pmid"))]
dups = [k for k, v in collections.Counter(pmids).items() if v > 1]
print("dup_pmid", len(dups))
for d in dups[:5]:
    print("  dup", d, "x", collections.Counter(pmids)[d])

# ochiai coverage
och_dir = os.path.join(BASE, "daily-feed", "ochiai")
have = set(p.name[:-5] for p in pathlib.Path(och_dir).glob("*.json"))
print("ochiai files", len(have))
missing = [p for p in pmids if p not in have]
print("ochiai missing vs pmid rows", len(missing))

# key consistency in ochiai json
import itertools
req = ["pmid","what","compared_to_prior","key_technique","target","verification_method",
       "technical_metrics","clinical_metrics","discussion_limitations","summary_ja",
       "study_design","source","generated_date"]
bad = 0
sample_bad = []
for p in itertools.islice(pathlib.Path(och_dir).glob("*.json"), 50):
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        bad += 1; sample_bad.append((p.name, "parse")); continue
    miss = [k for k in req if k not in d]
    if miss:
        bad += 1
        if len(sample_bad) < 5: sample_bad.append((p.name, miss))
print("ochiai_bad_keys(sample50)", bad)
for s in sample_bad: print("   ", s)
