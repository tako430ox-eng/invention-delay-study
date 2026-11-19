from mom import *
h=1.6e-3
def Lp2d(w,h,N=300):
    C=C_free([(0,w,0),(0,w,h)],N=N); return mu0*e0/C
print("Task1 2D:")
res={}
for w in [0.25e-3,25e-3]:
    L=Lp2d(w,h); res[w]=L
    print(f" w={w*1e3}mm L'={L*1e9:.3f} nH/m -> x3w ={L*3*w*1e12:.3f} pH  (parallel-plate mu0 h/w*len={mu0*h/w*3*w*1e12:.2f} pH)")
print(" ratio 2D (0.25/25):", res[0.25e-3]*0.75e-3/(res[25e-3]*75e-3))
print("Task2:")
W=10e-3
# infinite ground: strip over plane via images = strip and its image at 2h, C_inf = 2*C_free(pair at 2h)
Cinf=2*C_free([(0,W,0),(0,W,2*h)],N=300); Linf=mu0*e0/Cinf
for e in [1e-3,2e-3,6.35e-3,20e-3,50e-3,200e-3]:
    C=C_free([(0,W,h),(0,W+2*e,0)],N=300)
    print(f" e={e*1e3}mm L'={mu0*e0/C*1e9:.3f} nH/m ratio={mu0*e0/C/Linf:.4f}")
print(" Linf=",Linf*1e9,"nH/m; parallel plate",mu0*h/W*1e9)
