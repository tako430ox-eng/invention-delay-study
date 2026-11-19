import numpy as np, sys
sys.path.insert(0, '.')
from fd2d import *
C_LIGHT = 1/np.sqrt(MU0*EPS0)

def hj_z0(u, er):
    # Hammerstad & Jensen 1980, zero thickness
    f = 6 + (2*np.pi - 6)*np.exp(-(30.666/u)**0.7528)
    z01 = 60*np.log(f/u + np.sqrt(1 + (2/u)**2))
    a = 1 + np.log((u**4 + (u/52)**2)/(u**4 + 0.432))/49 + np.log(1 + (u/18.1)**3)/18.7
    b = 0.564*((er - 0.9)/(er + 3))**0.053
    ee = (er + 1)/2 + (er - 1)/2*(1 + 10/u)**(-a*b)
    return z01/np.sqrt(ee)

def microstrip(w, h, er, G=40):
    W = G*h + w
    x = axis([-w/2, w/2, -W/2, W/2], h/40, (-W/2 - 5*h, W/2 + 5*h), dmax=h)
    y = axis([0, h], h/40, (-5*h, 30*h), dmax=2*h)
    p = Problem(x, y)
    p.set_dielectric(0, h, er)
    p.add_strip(0, -W/2, W/2, 0)
    p.add_strip(1, -w/2, w/2, h)
    C, _ = p.solve_energy({1: 1.0}, True)
    C0, _ = p.solve_energy({1: 1.0}, False)
    return 1/(C_LIGHT*np.sqrt(C*C0)), p

h = 1.6e-3
for er in (1.0, 4.3):
    for u in (0.5, 1, 2, 4):
        z, p = microstrip(u*h, h, er)
        zr = hj_z0(u, er)
        print(f"er={er} w/h={u}: FD {z:.2f}  HJ {zr:.2f}  diff {100*(z/zr-1):+.2f}%  grid {p.nx}x{p.ny}")

# wide parallel plates (air): L' vs mu0 h/w
for wh in (10, 100):
    w = wh*h
    x = axis([-w/2, w/2], h/20, (-w/2 - 30*h, w/2 + 30*h), dmax=2*h)
    y = axis([0, h], h/20, (-30*h, 31*h), dmax=2*h)
    p = Problem(x, y); p.add_strip(0, -w/2, w/2, 0); p.add_strip(1, -w/2, w/2, h)
    C0, _ = p.solve_energy({1: 1.0}, False)
    L = MU0*EPS0/C0
    palmer = EPS0*(w/h)*(1 + h/(np.pi*w)*(1 + np.log(2*np.pi*w/h)))
    print(f"plates w/h={wh}: L'/(mu0 h/w)={L/(MU0*h/w):.4f}  C0/palmer={C0/palmer:.4f}")
