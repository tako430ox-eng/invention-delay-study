import json, os, sys, threading, oa
from concurrent.futures import ThreadPoolExecutor
F = "publication_year:1980-1989,type:article"
MIN_REMAIN = int(sys.argv[1]) if len(sys.argv) > 1 else 200
def load_or_sample(fn, filt, n, seed):
    if os.path.exists(fn): return json.load(open(fn))
    s = oa.sample(filt, n, seed); json.dump(s, open(fn, "w")); return s
def late(w):  # citations in 2021+ from counts_by_year (free)
    return sum(c["cited_by_count"] for c in w.get("counts_by_year", []) if c["year"] >= 2021)
done = {}
if os.path.exists("rows.jsonl"):
    for l in open("rows.jsonl"):
        r = json.loads(l); done[(r["grp"], r["id"])] = r
lock = threading.Lock()
out = open("rows.jsonl", "a")
def proc(grp, w):
    cy = oa.cite_years(w["id"].split("/")[-1])
    r = dict(grp=grp, id=w["id"], year=w["publication_year"], cbc=w["cited_by_count"],
             topic=(w.get("primary_topic") or {}).get("id"), cy=cy, **oa.classify(cy))
    with lock:
        done[(grp, w["id"])] = r; out.write(json.dumps(r) + "\n"); out.flush()
def low():
    rem = oa.STATE["remaining"]; return rem is not None and int(rem) < MIN_REMAIN
def run(grp, cands, stop):
    todo = [w for w in cands if (grp, w["id"]) not in done]
    with ThreadPoolExecutor(5) as ex:
        i = 0
        while i < len(todo) and not stop() and not low():
            batch = todo[i:i+25]; i += 25
            list(ex.map(lambda w: proc(grp, w), batch))
            print(grp, "processed", i, "credits", oa.STATE, flush=True)
# negatives frame: random 1980s articles with a primary topic
neg_c = [w for w in load_or_sample("cand_neg.json", F, 2600, 202) if w.get("primary_topic")]
nneg = lambda: sum(1 for (g, _), r in done.items() if g == "neg" and r["sleeping"] and not r["awake"])
run("neg", neg_c, lambda: nneg() >= 1500)
# positives frame: 1980s articles with cited_by_count>=50, prefilter: citations through 2020 >= 50 (necessary)
pos_c = load_or_sample("cand_pos_a.json", F + ",cited_by_count:>49", 10000, 101)
if os.path.exists("cand_pos_b.json") or len(sys.argv) > 2:
    ids = {w["id"] for w in pos_c}
    pos_c += [w for w in load_or_sample("cand_pos_b.json", F + ",cited_by_count:>49", 10000, 303) if w["id"] not in ids]
pre = [w for w in pos_c if w.get("primary_topic") and w["cited_by_count"] - late(w) >= 50]
print("pos candidates", len(pos_c), "after prefilter", len(pre), flush=True)
npos = lambda: sum(1 for (g, _), r in done.items() if g == "pos" and r["awake"])
run("pos", pre, lambda: npos() >= 300)
print("FINAL neg", nneg(), "pos", npos(), "pos processed", sum(1 for (g,_) in done if g=="pos"), oa.STATE, flush=True)
