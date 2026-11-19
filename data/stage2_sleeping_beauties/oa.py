import os, time, json, requests
KEY = os.environ["OPENALEX_API_KEY"]
BASE = "https://api.openalex.org"
S = requests.Session()
STATE = {"credits": 0, "calls": 0, "remaining": None}
def get(path, params):
    p = dict(params); p["api_key"] = KEY
    for a in range(6):
        try:
            r = S.get(BASE + path, params=p, timeout=60)
        except requests.RequestException as e:
            time.sleep(2 ** a); continue
        if r.status_code == 200:
            STATE["calls"] += 1
            STATE["credits"] += int(r.headers.get("x-ratelimit-credits-used", "0") or 0)
            STATE["remaining"] = r.headers.get("x-ratelimit-remaining")
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** a + 1); continue
        raise RuntimeError(f"HTTP {r.status_code} on {path}: {r.text[:200]}")
    raise RuntimeError("retries exhausted on " + path)
SEL = "id,publication_year,cited_by_count,counts_by_year,primary_topic,type"
def sample(filt, n, seed):
    out = []
    page = 1
    while len(out) < n:
        d = get("/works", {"filter": filt, "sample": n, "seed": seed, "per_page": 200, "page": page, "select": SEL})
        if not d["results"]: break
        out += d["results"]; page += 1
    return out[:n]
def cite_years(wid):
    d = get("/works", {"filter": f"cites:{wid}", "group_by": "publication_year"})
    return {int(g["key"]): g["count"] for g in d["group_by"] if g["key"].isdigit()}
def classify(cy):
    upto2000 = sum(v for y, v in cy.items() if y <= 2000)
    w0120 = sum(v for y, v in cy.items() if 2001 <= y <= 2020)
    c9600 = sum(v for y, v in cy.items() if 1996 <= y <= 2000)
    sleeping = upto2000 <= 10
    return dict(upto2000=upto2000, w0120=w0120, c9600=c9600, sleeping=sleeping, awake=sleeping and w0120 >= 50)
