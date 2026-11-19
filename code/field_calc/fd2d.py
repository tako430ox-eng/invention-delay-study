"""2D quasi-static field solver (finite volume on a graded tensor grid).
Conductors are zero-thickness strips at fixed potential. Outer box: Neumann.
Capacitance from field energy: C = sum G*(dphi)^2 for unit excitation."""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

EPS0 = 8.8541878128e-12
MU0 = 4e-7 * np.pi

def axis(features, dmin, extent, growth=1.15, dmax=None):
    """Graded 1D grid: fine (dmin) near each feature coordinate, growing geometrically away."""
    lo, hi = extent
    dmax = dmax or (hi - lo) / 20
    pts = set()
    for f in features:
        for sgn in (-1, 1):
            x, d = f, dmin
            while lo <= x <= hi:
                pts.add(round(x, 12))
                x += sgn * d
                d = min(d * growth, dmax)
    pts.add(lo); pts.add(hi)
    for f in features:
        pts.add(f)
    a = np.array(sorted(pts))
    # merge points closer than dmin/4
    keep = [a[0]]
    for v in a[1:]:
        if v - keep[-1] > dmin / 4:
            keep.append(v)
    return np.array(keep)

class Problem:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.nx, self.ny = len(x), len(y)
        self.epsr = np.ones((self.nx - 1, self.ny - 1))  # per element
        self.cond = -np.ones((self.nx, self.ny), dtype=int)  # conductor id per node

    def set_dielectric(self, y0, y1, er):
        yc = 0.5 * (self.y[:-1] + self.y[1:])
        m = (yc > y0) & (yc < y1)
        self.epsr[:, m] = er

    def add_strip(self, cid, x0, x1, y0):
        j = int(np.argmin(abs(self.y - y0)))
        assert abs(self.y[j] - y0) < 1e-12 * max(1, abs(y0)) + 1e-15, (y0, self.y[j])
        i = (self.x >= x0 - 1e-12) & (self.x <= x1 + 1e-12)
        self.cond[i, j] = cid

    def _links(self, epsr):
        dx, dy = np.diff(self.x), np.diff(self.y)
        nx, ny = self.nx, self.ny
        # x-links between (i,j)-(i+1,j): element rows j-1 and j
        Gx = np.zeros((nx - 1, ny))
        Gx[:, 1:] += epsr * dy[None, :] / 2
        Gx[:, :-1] += epsr * dy[None, :] / 2
        Gx /= dx[:, None]
        Gy = np.zeros((nx, ny - 1))
        Gy[1:, :] += epsr * dx[:, None] / 2
        Gy[:-1, :] += epsr * dx[:, None] / 2
        Gy /= dy[None, :]
        return Gx, Gy

    def solve_energy(self, volts, dielectric=True):
        """volts: dict cid->V. Returns C-like energy sum (F/m) = sum G dphi^2 * eps0."""
        epsr = self.epsr if dielectric else np.ones_like(self.epsr)
        Gx, Gy = self._links(epsr)
        nx, ny = self.nx, self.ny
        N = nx * ny
        idx = np.arange(N).reshape(nx, ny)
        rows, cols, vals = [], [], []
        def add(a, b, g):
            rows.extend([a, b, a, b]); cols.extend([a, b, b, a]); vals.extend([g, g, -g, -g])
        a = idx[:-1, :].ravel(); b = idx[1:, :].ravel(); g = Gx.ravel()
        A = sp.coo_matrix((np.concatenate([g, g, -g, -g]),
                           (np.concatenate([a, b, a, b]), np.concatenate([a, b, b, a]))), shape=(N, N))
        a = idx[:, :-1].ravel(); b = idx[:, 1:].ravel(); g = Gy.ravel()
        A = A + sp.coo_matrix((np.concatenate([g, g, -g, -g]),
                           (np.concatenate([a, b, a, b]), np.concatenate([a, b, b, a]))), shape=(N, N))
        A = A.tocsr()
        c = self.cond.ravel()
        fixed = c >= 0
        phi = np.zeros(N)
        for cid, v in volts.items():
            phi[c == cid] = v
        free = ~fixed
        Aff = A[free][:, free]
        rhs = -A[free][:, fixed] @ phi[fixed]
        phi[free] = spla.spsolve(Aff.tocsc(), rhs)
        P = phi.reshape(nx, ny)
        E = (Gx * np.diff(P, axis=0) ** 2).sum() + (Gy * np.diff(P, axis=1) ** 2).sum()
        return EPS0 * E, P

    def cap_matrix(self, cids, dielectric=True):
        n = len(cids)
        C = np.zeros((n, n))
        self_e = {}
        for k, ck in enumerate(cids):
            volts = {c: 0.0 for c in cids}; volts[ck] = 1.0
            e, _ = self.solve_energy(volts, dielectric)
            C[k, k] = e
        for k in range(n):
            for l in range(k + 1, n):
                volts = {c: 0.0 for c in cids}; volts[cids[k]] = 1.0; volts[cids[l]] = 1.0
                e, _ = self.solve_energy(volts, dielectric)
                C[k, l] = C[l, k] = (e - C[k, k] - C[l, l]) / 2  # Maxwell (negative)
        return C
