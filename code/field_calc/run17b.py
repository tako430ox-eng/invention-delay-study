import numpy as np, sys
sys.path.insert(0, '.')
from fd2d import *
mm = 1e-3
def Lp_over_ground(x0, x1, gx0, gx1, h):
    feats = [x0, x1, gx0, gx1]
    d = min(x1 - x0, h)/30
    x = axis(feats, d, (gx0 - 40*h - 10*mm, gx1 + 40*h + 10*mm), dmax=2*h)
    y = axis([0, h], d, (-40*h, 41*h), dmax=2*h)
    p = Problem(x, y); p.add_strip(0, gx0, gx1, 0); p.add_strip(1, x0, x1, h)
    C0, _ = p.solve_energy({1: 1.0}, False)
    return MU0*EPS0/C0
es = [0, 0.5, 1, 1.5, 2, 3, 4, 6.35, 10, 15, 25]
for h_mm in (1.6, 0.2):
    h = h_mm*mm
    print(f"== h={h_mm} mm")
    # Model A: 10 mm wide conductor (device-sized current) over ground of width 10+2e
    ref = Lp_over_ground(-5*mm, 5*mm, -5*mm - 40*mm, 5*mm + 40*mm, h)
    print(" A: e(mm) ratio L'(e)/L'(inf):", [(e, round(Lp_over_ground(-5*mm, 5*mm, -5*mm - e*mm, 5*mm + e*mm, h)/ref, 3)) for e in es])
    # Model B: 0.25 mm trace at the device edge; ground under device (10 mm) + e beyond trace edge
    tw = 0.25*mm
    refB = Lp_over_ground(5*mm, 5*mm + tw, -5*mm, 5*mm + tw + 40*mm, h)
    print(" B: e(mm) ratio:", [(e, round(Lp_over_ground(5*mm, 5*mm + tw, -5*mm, 5*mm + tw + e*mm, h)/refB, 3)) for e in es])
