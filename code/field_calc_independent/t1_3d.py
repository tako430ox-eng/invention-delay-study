from pee import *
h=1.6e-3
L2={0.25e-3:1298.249e-9,25e-3:72.0745e-9}
for w in [0.25e-3,25e-3]:
    for N in [10,20,40]:
        L=loopL(w,h,3*w,N)
        print(f"w={w*1e3} N={N} L3D={L*1e12:.3f} pH  2D*len={L2[w]*3*w*1e12:.3f}")
    print(" uniform current N=40:",loopL(w,h,3*w,40,True)*1e12)
# validation: long-length limit approaches 2D per unit length
w=1e-3
for l in [10e-3,100e-3,1.0]:
    L=loopL(w,h,l,20); print("w=1mm l=",l, "L/l=",L/l*1e9,"nH/m")
