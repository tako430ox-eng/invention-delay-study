import numpy as np, sys, json
sys.path.insert(0, '.')
from fd2d import *
out = {}
mm = 1e-3

# ---- Test 1: 3:1 rule, power trace stacked over ground trace (same width), air (L only)
def stacked_Lp(w, h):
    x = axis([-w/2, w/2], min(w, h)/30, (-w/2 - 40*h, w/2 + 40*h), dmax=2*h)
    y = axis([0, h], min(w, h)/30, (-40*h, 41*h), dmax=2*h)
    p = Problem(x, y); p.add_strip(0, -w/2, w/2, 0); p.add_strip(1, -w/2, w/2, h)
    C0, _ = p.solve_energy({1: 1.0}, False)
    return MU0*EPS0/C0
h = 1.6*mm
t1 = []
for w_mm in (0.25, 0.5, 1, 2, 5, 10, 25):
    w = w_mm*mm
    Lp = stacked_Lp(w, h)
    t1.append(dict(w_mm=w_mm, Lp_nH_per_mm=Lp*1e9*1e-3, L_total_at_3to1_nH=Lp*3*w*1e9,
                   bound_3mu0h_nH=3*MU0*h*1e9))
    print(t1[-1])
out['test1_h1.6'] = t1
# equal-inductance comparison: length of a narrow trace with same L as 25 mm wide 3:1
Lref = t1[-1]['L_total_at_3to1_nH']
for r in t1[:3]:
    ell = Lref/r['Lp_nH_per_mm']
    print(f"w={r['w_mm']} mm trace reaches {Lref:.2f} nH at length {ell:.1f} mm = ratio {ell/r['w_mm']:.0f}:1")
    r['len_for_same_L_as_25mm_3to1_mm'] = ell
