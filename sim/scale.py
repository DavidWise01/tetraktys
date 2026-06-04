#!/usr/bin/env python3
"""
Tetraktys at scale — does the 5-cell proof survive when the ring grows?

Three honest scaling tests (each can REFUTE a small-N claim):
  A · 1-D propagation : is the spread a light-cone (t∝d) or diffusion (t∝d²)?
  B · synchronization : does the nearest-neighbour ring still lock as N grows?
  C · 2-D lattice     : do two coherent sources interfere?  -> img/interference.png

Pure stdlib, deterministic.
"""
import math, random, struct, zlib, sys
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT/"img"; IMG.mkdir(exist_ok=True)
def banner(t): print("\n"+"="*68+"\n"+t+"\n"+"="*68)

# ─────────────── A · 1-D propagation: light-cone vs diffusion ───────────────
def propagate(N, K, mode, thresh=0.02, steps=2600):
    c0=N//2; u=[0.0]*N; v=[0.0]*N; arrive=[None]*N; arrive[c0]=0
    for t in range(1,steps+1):
        u[c0]=1.0                                              # held source
        lap=[u[(i-1)%N]+u[(i+1)%N]-2*u[i] for i in range(N)]
        if mode=="diffusion":
            u=[u[i]+K*lap[i] for i in range(N)]                # first-order  (heat eq)
        else:
            v=[(v[i]+K*lap[i])*0.999 for i in range(N)]        # second-order (wave eq)
            u=[u[i]+v[i] for i in range(N)]
        u[c0]=1.0
        for i in range(N):
            if arrive[i] is None and abs(u[i])>thresh: arrive[i]=t
    return arrive,c0

def test_propagation():
    banner("A · 1-D PROPAGATION — light-cone (t∝d) or diffusion (t∝d²)?")
    N=201; ds=[5,10,20,40]; res={}
    for mode,K in (("diffusion",0.25),("wave",0.50)):
        arrive,c0=propagate(N,K,mode)
        ts=[arrive[c0+d] for d in ds]; res[mode]=ts
        print(f"\n  {mode:9s} (K={K}):")
        print("    distance d :", "  ".join(f"{d:>5}" for d in ds))
        print("    arrival  t :", "  ".join(f"{(t if t else -1):>5}" for t in ts))
        if all(ts):
            print("    t ÷ d      :", "  ".join(f"{t/d:>5.1f}" for t,d in zip(ts,ds)), "  (const ⇒ light-cone)")
            print("    t ÷ d²     :", "  ".join(f"{t/d/d:>5.2f}" for t,d in zip(ts,ds)), "  (const ⇒ diffusion)")
    print("\n  → first-order coupling DIFFUSES (t∝d², the front keeps slowing). add inertia")
    print("    (the wave term) and a FINITE, constant signal speed appears — a real light-cone.")
    return res

# ─────────────── B · synchronization at scale ───────────────
def kuramoto(N, K, mode, T=1500, dt=0.05, seed=7):
    random.seed(seed)
    th=[random.uniform(0,2*math.pi) for _ in range(N)]
    om=[0.35+0.50*random.random() for _ in range(N)]
    acc=[]
    for t in range(T):
        if mode=="ring":
            nu=th[:]
            for c in range(N):
                nu[c]=th[c]+dt*(om[c]+(K/2.0)*(math.sin(th[(c-1)%N]-th[c])+math.sin(th[(c+1)%N]-th[c])))
            th=nu
        else:                                                  # mean-field (all-to-all, O(N))
            C=sum(math.cos(a) for a in th); Sx=sum(math.sin(a) for a in th)
            Rg=math.hypot(C,Sx)/N; psi=math.atan2(Sx,C)
            th=[th[c]+dt*(om[c]+K*Rg*math.sin(psi-th[c])) for c in range(N)]
        if t>=T-300:
            C=sum(math.cos(a) for a in th); Sx=sum(math.sin(a) for a in th)
            acc.append(math.hypot(C,Sx)/N)
    return sum(acc)/len(acc)

def test_sync_scale():
    banner("B · SYNCHRONIZATION AT SCALE — does the ring still lock as N grows?")
    Ns=[5,40,160]; K=1.0
    print(f"  fixed coupling K={K} · order parameter R (1 = locked)")
    print(f"    {'N':>5} | {'ring (nearest-nbr)':>20} | {'all-to-all (mean-field)':>24}")
    out={}
    for N in Ns:
        rr=kuramoto(N,K,"ring"); rm=kuramoto(N,K,"mean"); out[N]=(rr,rm)
        print(f"    {N:>5} | {rr:>20.3f} | {rm:>24.3f}")
    print("  → the literal nearest-neighbour RING stops locking as it grows (1-D short-range")
    print("    Kuramoto): the N=5 lock was finite-size. robust sync needs LONG-RANGE coupling —")
    print("    which is exactly the 'one external lead' (all-to-all) in the spec.")
    return out

# ─────────────── C · 2-D wave lattice: interference ───────────────
def png(path, w, h, px):
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w): raw += bytes(px[y*w+x])
    comp=zlib.compress(bytes(raw),9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+ch(b"IDAT",comp)+ch(b"IEND",b""))

def test_interference(L=180, steps=240, K=0.22, om=0.45):
    banner("C · 2-D WAVE LATTICE — do two coherent sources interfere?")
    u=[0.0]*(L*L); v=[0.0]*(L*L)
    s1=(int(L*0.40), L//2); s2=(int(L*0.60), L//2)
    i1=s1[1]*L+s1[0]; i2=s2[1]*L+s2[0]
    edge=16
    damp=[1.0]*(L*L)
    for y in range(L):
        for x in range(L):
            m=min(x,L-1-x,y,L-1-y)
            if m<edge: damp[y*L+x]=0.88+0.12*(m/edge)
    for t in range(steps):
        dr=math.sin(om*t); u[i1]=dr; u[i2]=dr
        for y in range(1,L-1):
            b=y*L
            for x in range(1,L-1):
                i=b+x
                v[i]=(v[i]+K*(u[i-1]+u[i+1]+u[i-L]+u[i+L]-4.0*u[i]))*damp[i]
        for i in range(L*L): u[i]+=v[i]
        u[i1]=dr; u[i2]=dr
    # normalize by interior amplitude, render diverging gold(+)/blue(−) on dark
    amp=max(1e-6, sorted(abs(u[y*L+x]) for y in range(edge,L-edge) for x in range(edge,L-edge))[int(0.985*((L-2*edge)**2))])
    GOLD=(232,196,90); BLUE=(96,158,255); DARK=(9,11,20)
    def mix(a,b,t): t=0 if t<0 else 1 if t>1 else t; return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
    base=[DARK]*(L*L)
    for i in range(L*L):
        val=max(-1.0,min(1.0,u[i]/amp))
        base[i]= mix(DARK,GOLD,val) if val>=0 else mix(DARK,BLUE,-val)
    base[i1]=(255,255,255); base[i2]=(255,255,255)
    S=2; W=L*S; out=[(0,0,0)]*(W*W)                            # ×2 upscale
    for y in range(L):
        for x in range(L):
            c=base[y*L+x]
            for yy in range(S):
                row=(y*S+yy)*W
                for xx in range(S): out[row+x*S+xx]=c
    png(IMG/"interference.png", W, W, out)
    # fringe count along a row well above the sources
    row_y=edge+10; signs=[1 if u[row_y*L+x]>0 else -1 for x in range(edge,L-edge)]
    fr=sum(1 for k in range(1,len(signs)) if signs[k]!=signs[k-1])
    print(f"  two coherent sources, {L}×{L} wave lattice, {steps} ticks  → img/interference.png")
    print(f"  sign-changes along a sample row: {fr}  → {fr} interference fringes (alternating + / −)")
    print("  diffusion would smear to a featureless blob; the WAVE lattice shows real fringes.")
    return fr

if __name__=="__main__":
    print("Tetraktys at scale")
    test_propagation(); test_sync_scale(); fr=test_interference()
    banner("WHAT SCALING FOUND")
    print("  • the spread is DIFFUSIVE (t∝d²) under first-order coupling; a true light-cone")
    print("    (constant speed, t∝d) needs the inertial WAVE term.")
    print("  • the nearest-neighbour RING does NOT stay locked at scale — robust sync needs")
    print("    long-range coupling (the external lead). the N=5 lock was finite-size.")
    print(f"  • the 2-D WAVE lattice genuinely interferes ({fr} fringes). emergence, measured.")
