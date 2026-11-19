import json, oa
F = "publication_year:1980-1989,type:article"
strat = oa.sample(F + ",cited_by_count:>49", 100, 11)
rand = oa.sample(F, 100, 12)
rows = []
for grp, lst in (("stratum", strat), ("random", rand)):
    for w in lst:
        cy = oa.cite_years(w["id"].split("/")[-1])
        c = oa.classify(cy)
        rows.append(dict(grp=grp, id=w["id"], cbc=w["cited_by_count"], topic=(w.get("primary_topic") or {}).get("id"), sumcy=sum(cy.values()), **c))
json.dump(rows, open("pilot.json", "w"))
import collections
for g in ("stratum", "random"):
    r = [x for x in rows if x["grp"] == g]
    print(g, "n", len(r), "sleeping", sum(x["sleeping"] for x in r), "awake", sum(x["awake"] for x in r), "notopic", sum(x["topic"] is None for x in r))
    print("  cbc vs cites-sum mismatch>10%:", sum(abs(x["cbc"]-x["sumcy"])>0.1*max(x["cbc"],1) for x in r))
print("calls", oa.STATE)
