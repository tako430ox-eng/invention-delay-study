"""3D check including end effects: loop inductance of two stacked thin strips
(length l, width w, separation h), uniform current (low-frequency) via filament partial inductances."""
import numpy as np
MU0 = 4e-7*np.pi
def M_fil(l, d):
    a = l/d
    return MU0*l/(2*np.pi)*(np.log(a + np.sqrt(1 + a*a)) - np.sqrt(1 + 1/(a*a)) + 1/a)
def loop_L(l, w, h, N=60):
    xs = (np.arange(N) + 0.5)*w/N
    dx = xs[:, None] - xs[None, :]
    d_self = np.where(dx == 0, 0.2235*w/N, np.abs(dx))   # GMD of thin tape segment
    Lp = M_fil(l, d_self).mean()
    d_mut = np.sqrt(dx**2 + h*h)
    Mp = M_fil(l, d_mut).mean()
    return 2*(Lp - Mp)
if __name__ == '__main__':
    h = 1.6e-3
    print("check: long wide plates vs mu0 h l/w ->", loop_L(1.0, 0.16, h, 200)/(MU0*h*1.0/0.16))
    for w_mm in (0.25, 0.5, 1, 2, 5, 10, 25):
        w = w_mm*1e-3
        print(w_mm, "L(3:1) nH =", round(loop_L(3*w, w, h)*1e9, 3))
