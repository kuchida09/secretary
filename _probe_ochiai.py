import pathlib, json, collections

och_dir = pathlib.Path("/workspace/research/80_AI作業場/knowledge/literature/daily-feed/ochiai")
req = ["pmid","what","compared_to_prior","key_technique","target","verification_method",
       "technical_metrics","clinical_metrics","discussion_limitations","summary_ja",
       "study_design","source","generated_date"]
files = sorted(och_dir.glob("*.json"))
print("files", len(files))
miss_summary = []
miss_design = []
miss_any = []
parse_bad = []
for p in files:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        parse_bad.append(p.name); continue
    if not str(d.get("summary_ja", "")).strip(): miss_summary.append(p.name)
    if not str(d.get("study_design", "")).strip(): miss_design.append(p.name)
    m = [k for k in req if k not in d]
    if m: miss_any.append((p.name, m))
print("missing summary_ja", len(miss_summary))
print("missing study_design", len(miss_design))
print("missing any key", len(miss_any))
print("parse_bad", len(parse_bad))
if miss_any[:5]:
    for s in miss_any[:5]: print("  ex", s)
# distribution of missing key sets
c = collections.Counter(tuple(sorted(m)) for _, m in miss_any)
for k, v in c.most_common(5):
    print("  set", k, "x", v)
