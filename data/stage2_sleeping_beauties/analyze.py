import json, math, numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
rows = {}
for l in open("rows.jsonl"):
    r = json.loads(l); rows[(r["grp"], r["id"])] = r
T = json.load(open("topics.json"))
pos = [r for (g,_), r in rows.items() if g == "pos" and r["awake"] and r["topic"]]
neg = [r for (g,_), r in rows.items() if g == "neg" and r["sleeping"] and not r["awake"] and r["topic"]]
neg = neg[:1500]
data = pos + neg
y = np.array([1]*len(pos) + [0]*len(neg))
c96 = np.array([r["c9600"] for r in data], float)
a = np.array([T["p8690"].get(r["topic"], 0) for r in data], float)
b = np.array([T["p9600"].get(r["topic"], 0) for r in data], float)
grow = np.log((b + 1) / (a + 1))
rng = np.random.default_rng(0)
randscore = rng.random(len(y))
X = np.c_[np.log1p(c96), grow]
def cvauc(X, seed):
    p = cross_val_predict(LogisticRegression(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=seed), method="predict_proba")[:, 1]
    return roc_auc_score(y, p), p
comb, pcomb = cvauc(X, 0)
combs = [cvauc(X, s)[0] for s in range(10)]
res = dict(n_pos=len(pos), n_neg=len(neg),
    auc_random=roc_auc_score(y, randscore), auc_B=roc_auc_score(y, c96), auc_growth=roc_auc_score(y, grow),
    auc_comb=comb, auc_comb_10seeds_mean=float(np.mean(combs)), auc_comb_10seeds_range=[float(min(combs)), float(max(combs))])
# bootstrap CIs
bs = {"B": [], "growth": [], "comb_minus_B": []}
for i in range(2000):
    ip = rng.choice(np.where(y==1)[0], len(pos)); ineg = rng.choice(np.where(y==0)[0], len(neg))
    idx = np.r_[ip, ineg]; yy = y[idx]
    bs["B"].append(roc_auc_score(yy, c96[idx])); bs["growth"].append(roc_auc_score(yy, grow[idx]))
    bs["comb_minus_B"].append(roc_auc_score(yy, pcomb[idx]) - bs["B"][-1])
res["ci95"] = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in bs.items()}
# descriptive
res["desc"] = dict(
    c96_mean_pos=float(c96[y==1].mean()), c96_mean_neg=float(c96[y==0].mean()),
    c96_zero_pos=float((c96[y==1]==0).mean()), c96_zero_neg=float((c96[y==0]==0).mean()),
    growth_median_pos=float(np.median(np.exp(grow[y==1]))), growth_median_neg=float(np.median(np.exp(grow[y==0]))),
    upto2000_mean_pos=float(np.mean([r["upto2000"] for r in pos])), upto2000_mean_neg=float(np.mean([r["upto2000"] for r in neg])),
    year_mean_pos=float(np.mean([r["year"] for r in pos])), year_mean_neg=float(np.mean([r["year"] for r in neg])))
# exploratory (not pre-registered): control for total-pre-2000 & publication year
lr = LogisticRegression().fit(X, y); res["coef_logc96_growth"] = lr.coef_[0].tolist()
res["topic_missing_in_counts"] = int(sum(1 for r in data if r["topic"] not in T["p8690"]))
g = res["auc_growth"]; d = res["auc_comb"] - res["auc_B"]
res["verdict"] = "支持" if (g >= 0.60 and d >= 0.03) else ("不支持" if g <= 0.55 else "未決")
print(json.dumps(res, indent=1, ensure_ascii=False))
json.dump(res, open("result.json", "w"), ensure_ascii=False, indent=1)
# --- prevalence and precision (uses frame sizes; descriptive, not pre-registered) ---
N_ALL, N_STRAT = 11374842, 821951
cands = json.load(open("cand_pos_a.json"))
import os
if os.path.exists("cand_pos_b.json"):
    ids = {w["id"] for w in cands}; cands += [w for w in json.load(open("cand_pos_b.json")) if w["id"] not in ids]
late = lambda w: sum(c["cited_by_count"] for c in w.get("counts_by_year", []) if c["year"] >= 2021)
p_pass = np.mean([bool(w.get("primary_topic")) and w["cited_by_count"] - late(w) >= 50 for w in cands])
proc_pos = [r for (g,_), r in rows.items() if g == "pos"]
r_pos = np.mean([r["awake"] for r in proc_pos])
p_awake = N_STRAT / N_ALL * p_pass * r_pos            # P(awake & has topic) among 1980s articles
negc = json.load(open("cand_neg.json")); p_topic = np.mean([bool(w.get("primary_topic")) for w in negc])
proc_neg = [r for (g,_), r in rows.items() if g == "neg"]
p_sleep_t = np.mean([r["sleeping"] for r in proc_neg])
pi = p_awake / (p_topic * p_sleep_t)
res["prevalence"] = dict(p_stratum=N_STRAT/N_ALL, p_prefilter_pass=float(p_pass), awake_rate_in_processed=float(r_pos),
    n_pos_processed=len(proc_pos), p_awake_among_articles=float(p_awake), p_sleeping_given_topic=float(p_sleep_t),
    pi_awake_given_sleeping=float(pi), random_frame_awake=f"{sum(r['awake'] for r in proc_neg)}/{len(proc_neg)}")
def prec_at(score, frac):
    # threshold at the score quantile that flags `frac` of the sleeping population
    thr_scores = np.r_[score[y==1], score[y==0]]
    best = None
    for t in np.unique(score):
        tpr = np.mean(score[y==1] >= t); fpr = np.mean(score[y==0] >= t)
        flagged = pi*tpr + (1-pi)*fpr
        if best is None or abs(flagged - frac) < abs(best[0] - frac): best = (flagged, tpr, fpr)
    flagged, tpr, fpr = best
    return dict(flagged_share=float(flagged), recall=float(tpr), precision=float(pi*tpr/flagged), lift=float(tpr/flagged))
res["precision"] = {name: {f"top{int(f*100)}pct": prec_at(s, f) for f in (0.01, 0.05, 0.10)}
                    for name, s in (("B", c96), ("growth", grow), ("comb", pcomb))}
print(json.dumps({k: res[k] for k in ("prevalence", "precision")}, indent=1))
json.dump(res, open("result.json", "w"), ensure_ascii=False, indent=1)
