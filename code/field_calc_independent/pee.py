import numpy as np
from scipy.integrate import quad
mu0=4e-7*np.pi
def g(d,l):
    d=max(d,1e-300)
    return l*np.arcsinh(l/d)-np.sqrt(l*l+d*d)+d
def Mtape(y1a,y1b,y2a,y2b,dz,l):
    # (mu0/2pi) * (1/(a1 a2)) * int int g(sqrt((y-y')^2+dz^2)) dy dy'
    a1=y1b-y1a;a2=y2b-y2a
    # u=y'-y ranges [y2a-y1b, y2b-y1a]; weight = overlap length of intervals
    def wt(u): return max(0.0,min(y1b,y2b-u)-max(y1a,y2a-u))
    lo=y2a-y1b;hi=y2b-y1a
    pts=sorted(set([y2a-y1a,y2b-y1b]+([0.0] if lo<0<hi else [])))
    pts=[p for p in pts if lo<p<hi]
    v,_=quad(lambda u: wt(u)*g(np.hypot(u,dz),l),lo,hi,points=pts or None,limit=200,epsabs=0,epsrel=1e-10)
    return mu0/(2*np.pi)*v/(a1*a2)
def loopL(w,h,l,N=30,uniform=False):
    th=np.linspace(0,np.pi,N+1); ye=-w/2*np.cos(th)
    tapes=[(ye[i],ye[i+1],0.0) for i in range(N)]+[(ye[i],ye[i+1],h) for i in range(N)]
    n=2*N; M=np.zeros((n,n))
    for i in range(n):
        for j in range(i,n):
            M[i,j]=M[j,i]=Mtape(tapes[i][0],tapes[i][1],tapes[j][0],tapes[j][1],abs(tapes[i][2]-tapes[j][2]),l)
    if uniform:
        a=np.diff(ye); I=np.concatenate([a/w,-a/w]); return I@M@I
    B=np.zeros((n,2)); B[:N,0]=1; B[N:,1]=1
    A=np.block([[M,-B],[B.T,np.zeros((2,2))]]); b=np.zeros(n+2); b[n]=1; b[n+1]=-1
    s=np.linalg.solve(A,b); return s[n]-s[n+1]
