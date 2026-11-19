import json, oa
res = {}
for lab, yr in (("p8690", "1986-1990"), ("p9600", "1996-2000")):
    cur = "*"; d = {}
    while cur:
        r = oa.get("/works", {"filter": f"publication_year:{yr},type:article", "group_by": "primary_topic.id", "per_page": 200, "cursor": cur})
        for g in r["group_by"]: d[g["key"]] = g["count"]
        cur = r["meta"].get("next_cursor")
        if not r["group_by"]: break
    res[lab] = d
    print(lab, len(d), sum(d.values()))
json.dump(res, open("topics.json", "w")); print(oa.STATE)
