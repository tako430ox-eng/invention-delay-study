"""Rebuild the delay table from Potter's public analysis document.
Usage: python3 -I rebuild_potter_gaps.py inventions_full_analysis.docx out.csv
Input: inventions_full_analysis.docx from github.com/briancpotter/inventiondating (not redistributed here).
For each invention: gap = actual year - estimated year. *_min uses the late end of the
estimated range (most conservative), *_max uses the early end. Rows whose ranges are not
plain years (Flag, antiquity, BC, centuries, ...) are skipped."""
import csv, html, re, sys, zipfile
xml = zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode('utf8')
paras = []
for p in re.findall(r'<w:p[ >].*?</w:p>', xml, flags=re.S):
    t = ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p, flags=re.S))
    paras.append(html.unescape(t).strip())
rows, cur = [], None
for t in paras:
    m = re.match(r'^(\d+)\.\s+(.+)$', t)
    if m and (cur is None or int(m.group(1)) == cur['n'] + 1):
        cur = {'n': int(m.group(1)), 'name': m.group(2).strip()}; rows.append(cur); continue
    if cur is None: continue
    for key, lab in (('year', 'Year actually invented:'), ('plaus', 'Earliest plausible:'), ('straight', 'Earliest straightforward:')):
        if t.startswith(lab) and key not in cur:
            v = t[len(lab):].strip()
            if key == 'year': v = re.match(r'\S+', v).group(0)
            cur[key] = v
def rng(s):
    """Plain years or ranges, with optional BC/AD (e.g. '1700-1750', '400 BC – 200 AD')."""
    parts = re.split(r'\s*[-–]\s*', (s or '').strip())
    if not 1 <= len(parts) <= 2: return None
    vals, eras = [], []
    for x in parts:
        m = re.fullmatch(r'(\d{1,4})\s*(BC|AD|BCE|CE)?', x)
        if not m: return None
        vals.append(int(m.group(1))); eras.append(m.group(2))
    last = eras[-1]
    ys = [(-v if (e or last) in ('BC', 'BCE') else v) for v, e in zip(vals, eras)]
    return ys[0], ys[-1]
out = []
for r in rows:
    try: y = int(r.get('year', ''))
    except ValueError: continue
    a, b = rng(r.get('plaus')), rng(r.get('straight'))
    if not a or not b: continue
    out.append([r['n'], r['name'], y, r['plaus'], r['straight'], y - a[1], y - a[0], y - b[1], y - b[0]])
with open(sys.argv[2], 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['n', 'name', 'year', 'earliest_plausible', 'earliest_straightforward', 'gap_plausible_min', 'gap_plausible_max', 'gap_straight_min', 'gap_straight_max'])
    w.writerows(out)
print(len(rows), 'sections,', len(out), 'rows written')
