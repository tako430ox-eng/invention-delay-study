import numpy as np, sys
sys.path.insert(0, '.')
from fd2d import *
def next_coeff(w, h, s_center, er=4.3):
    xs = [-s_center/2 - w/2, -s_center/2 + w/2, s_center/2 - w/2, s_center/2 + w/2]
    G = 40*h + 2*s_center
    d = min(w, h)/30
    x = axis(xs + [-G/2, G/2], d, (-G/2 - 5*h, G/2 + 5*h), dmax=h)
    y = axis([0, h], d, (-5*h, 30*h), dmax=2*h)
    p = Problem(x, y); p.set_dielectric(0, h, er)
    p.add_strip(0, -G/2, G/2, 0); p.add_strip(1, xs[0], xs[1], h); p.add_strip(2, xs[2], xs[3], h)
    C = p.cap_matrix([1, 2], True); C0 = p.cap_matrix([1, 2], False)
    L = MU0*EPS0*np.linalg.inv(C0)
    return 0.25*(L[0, 1]/L[0, 0] + (-C[0, 1])/C[0, 0])
w = 0.2e-3
print("center spacing 3W:")
for hw in (0.25, 0.5, 1, 2):
    k = next_coeff(w, hw*w, 3*w)
    print(f" h/w={hw}: Kb={k:.4f} ({20*np.log10(k):.1f} dB)")
print("center spacing 3h (edge gap ~3h-w) for comparison:")
for hw in (0.25, 0.5, 1, 2):
    h = hw*w; s = max(3*h, 1.5*w)
    k = next_coeff(w, h, s)
    print(f" h/w={hw}: s={s/w:.2f}W Kb={k:.4f} ({20*np.log10(k):.1f} dB)")
