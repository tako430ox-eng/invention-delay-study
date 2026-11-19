from mom import *
def kb(w,h,er=4.3,N=200):
    C=C_slab([0,3*w],[w,w],h,er,N=N); C0=C_slab([0,3*w],[w,w],h,1,N=N)
    L=mu0*e0*np.linalg.inv(C0)
    kc=-C[0,1]/C[0,0]; kl=L[0,1]/L[0,0]
    Ze=np.sqrt((L[0,0]+L[0,1])/(C[0,0]+C[0,1])); Zo=np.sqrt((L[0,0]-L[0,1])/(C[0,0]-C[0,1]))
    return 0.25*(kc+kl),kl,kc,Ze,Zo
for N in [100,200,400]:
    print(N,[kb(1e-3,r*1e-3,N=N)[0] for r in [0.25,2]])
r=[]
for w,h in [(1e-3,0.25e-3),(1e-3,2e-3),(0.25e-3,1.6e-3)]:
    K,kl,kc,Ze,Zo=kb(w,h,N=400); r.append(K)
    print(f"w={w*1e3} h={h*1e3} h/w={h/w}: Kb={K:.5f} Lm/Ls={kl:.5f} Cm/Cs={kc:.5f} Zeven={Ze:.2f} Zodd={Zo:.2f}")
print("ratio Kb(h/w=2)/Kb(0.25)=",r[1]/r[0])
