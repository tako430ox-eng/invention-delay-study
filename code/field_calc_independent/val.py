from mom import *
def HJ(u,er):
    a=1+np.log((u**4+(u/52)**2)/(u**4+0.432))/49+np.log(1+(u/18.1)**3)/18.7
    b=0.564*((er-0.9)/(er+3))**0.053
    ee=(er+1)/2+(er-1)/2*(1+10/u)**(-a*b)
    f=6+(2*np.pi-6)*np.exp(-(30.666/u)**0.7528)
    Z01=60*np.log(f/u+np.sqrt(1+4/u**2))
    return Z01/np.sqrt(ee),ee
h=1e-3
for u in [0.1,0.25,0.5,1,2,4,10]:
  for er in [1,4.3]:
    C=C_slab([0],[u*h],h,er)[0,0]; C0=C_slab([0],[u*h],h,1)[0,0]
    Z=1/(c0*np.sqrt(C*C0)); Zh,eh=HJ(u,er)
    print(f"u={u} er={er} Z_MoM={Z:.3f} Z_HJ={Zh:.3f} err={(Z/Zh-1)*100:+.3f}% eeff {C/C0:.4f} vs {eh:.4f}")
# convergence
for N in [50,100,200,400]: print(N,1/(c0*C_slab([0],[1e-3],1e-3,1,N=N)[0,0]))
