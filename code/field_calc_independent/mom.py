import numpy as np
e0=8.8541878128e-12; mu0=4e-7*np.pi; c0=1/np.sqrt(mu0*e0)
def F(t,a):  # antiderivative of ln(t^2+a^2)
    t=np.asarray(t,float); a=np.abs(a)
    with np.errstate(divide='ignore',invalid='ignore'):
        lt=np.where(t**2+a**2>0, t*np.log(t**2+a**2+1e-300), 0.0)
        at=np.where(a>0, 2*a*np.arctan2(t,a+0*t), 0.0)
    return lt-2*t+at
def Iln(x0,xl,xr,a): return F(xr-x0,a)-F(xl-x0,a)
def mesh(xc,w,y,N):
    th=np.linspace(0,np.pi,N+1); xe=xc-w/2*np.cos(th)
    return xe[:-1],xe[1:],np.full(N,y)
# free-space strips (no ground), kernel -1/(2pi e0) ln r = -1/(4pi e0) ln r^2
def C_free(strips,N=200):
    segs=[mesh(*s,N) for s in strips]
    xl=np.concatenate([s[0] for s in segs]); xr=np.concatenate([s[1] for s in segs]); y=np.concatenate([s[2] for s in segs])
    idx=np.concatenate([[i]*N for i in range(len(strips))]); xm=(xl+xr)/2
    P=-1/(4*np.pi*e0)*Iln(xm[:,None],xl[None,:],xr[None,:],y[:,None]-y[None,:])/(xr-xl)[None,:]
    # two conductors V=+1/2,-1/2 plus unknown offset c, neutrality
    n=len(xm); A=np.zeros((n+1,n+1)); A[:n,:n]=P; A[:n,n]=-1; A[n,:n]=1
    b=np.zeros(n+1); b[:n]=np.where(idx==0,0.5,-0.5)
    s=np.linalg.solve(A,b); Q=s[:n][idx==0].sum()
    return Q  # per 1 V
# strips on grounded slab interface (height h), image series
def C_slab(xcs,ws,h,er,N=200,nt=400):
    K=(er-1)/(er+1)
    segs=[mesh(xc,w,h,N) for xc,w in zip(xcs,ws)]
    xl=np.concatenate([s[0] for s in segs]); xr=np.concatenate([s[1] for s in segs])
    xm=(xl+xr)/2; M=len(xcs); idx=np.repeat(np.arange(M),N)
    P=np.zeros((len(xm),len(xm)))
    for n in range(nt):
        c=(-K)**n
        if abs(c)<1e-16 and n>0: break
        P+=c*(Iln(xm[:,None],xl[None,:],xr[None,:],2*(n+1)*h)-Iln(xm[:,None],xl[None,:],xr[None,:],2*n*h))
    P/=2*np.pi*e0*(er+1); P/=(xr-xl)[None,:]
    Pi=np.linalg.inv(P); C=np.zeros((M,M))
    for j in range(M):
        v=(idx==j).astype(float); q=Pi@v
        for i in range(M): C[i,j]=q[idx==i].sum()
    return C
