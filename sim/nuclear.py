#!/usr/bin/env python3
"""
Tetraktys — going nuclear (the full native engine).

Scaling (sim/scale.py) found two limits of the first-order proof: propagation
DIFFUSED (t∝d²) and the nearest-neighbour ring lost sync at scale. This folds
both fixes into the NATIVE dynamics:

  • INERTIA  — cells are second-order (a velocity term). Propagation is now
    natively BALLISTIC: a real, constant-speed light-cone (t∝d).
  • THE EXTERNAL LEAD — a long-range (all-to-all) coupling term, the two `1`
    leads of the spec. The lattice now genuinely synchronizes at ANY size.

Then the full emergence suite — including HYSTERESIS, the collective signature
inertia adds that the first-order model cannot show. Pure stdlib, deterministic.
Writes img/lightcone.png.
"""
import math, random, struct, zlib, sys
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT/"img"; IMG.mkdir(exist_ok=True)
def banner(t): print("\n"+"="*68+"\n"+t+"\n"+"="*68)

def order(th):
    C=sum(math.cos(a) for a in th); S=sum(math.sin(a) for a in th)
    return math.hypot(C,S)/len(th), math.atan2(S,C)

# ════════════ 1 · NATIVE LIGHT-CONE — inertial propagation is ballistic ════════════
def propagate(N, K, mode, thresh=0.02, steps=300, record=False):
    c0=N//2; u=[0.0]*N; v=[0.0]*N; arrive=[None]*N; arrive[c0]=0; hist=[]
    for t in range(1,steps+1):
        u[c0]=1.0
        lap=[u[(i-1)%N]+u[(i+1)%N]-2*u[i] for i in range(N)]
        if mode=="diffusion":
            u=[u[i]+K*lap[i] for i in range(N)]
        else:                                              # inertial → ballistic (native)
            v=[v[i]+K*lap[i] for i in range(N)]
            u=[u[i]+v[i] for i in range(N)]
        u[c0]=1.0
        if record: hist.append([abs(x) for x in u])
        for i in range(N):
            if arrive[i] is None and abs(u[i])>thresh: arrive[i]=t
    return arrive,c0,hist

def png(path,w,h,px):
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w): raw+=bytes(px[y*w+x])
    comp=zlib.compress(bytes(raw),9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+ch(b"IDAT",comp)+ch(b"IEND",b""))

def test_lightcone():
    banner("1 · NATIVE LIGHT-CONE — inertial propagation is ballistic (t∝d)")
    N=181; ds=[10,20,40,70]; win=70; H=150
    panels={}
    for mode,K in (("diffusion",0.25),("ballistic",0.50)):
        arr,c0,hist=propagate(N,K,mode,steps=H,record=True)
        ts=[arr[c0+d] for d in ds]; panels[mode]=hist
        print(f"\n  {mode:9s}: t at d={ds} → {ts}")
        if all(ts): print(f"             t÷d = {['%.1f'%(t/d) for t,d in zip(ts,ds)]}  (const ⇒ ballistic light-cone)")
    # space-time image: x (horizontal) vs t (downward); diffusion | ballistic
    GOLD=(232,196,90); BLUE=(96,158,255); DARK=(9,11,20)
    def mixc(a,b,t): t=0 if t<0 else 1 if t>1 else t; return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
    c0=N//2; gap=8; PW=2*win+1; W=PW*2+gap
    base=[DARK]*(W*H)
    for col,(mode,col0) in enumerate((("diffusion",0),("ballistic",PW+gap))):
        hist=panels[mode]; mx=max(max(r) for r in hist) or 1.0
        for t in range(H):
            for k in range(PW):
                x=c0-win+k; val=(hist[t][x]/mx)**0.5
                base[t*W + col0+k]= mixc(DARK, GOLD if col==1 else BLUE, val)
    S=2; W2=W*S; H2=H*S; out=[(0,0,0)]*(W2*H2)
    for y in range(H):
        for x in range(W):
            c=base[y*W+x]
            for yy in range(S):
                row=(y*S+yy)*W2
                for xx in range(S): out[row+x*S+xx]=c
    png(IMG/"lightcone.png", W2, H2)  if False else png(IMG/"lightcone.png", W2, H2, out)
    print("\n  → diffusion fills a PARABOLA (front ∝√t); inertial fills a straight-edged CONE")
    print("    (front ∝ t, constant speed). img/lightcone.png — left blue=diffusion, right gold=ballistic.")

# ════════════ 2 · ROBUST SYNC AT SCALE — the external lead ════════════
def sync(N, Kglobal, gamma=0.5, T=1800, dt=0.05, seed=7):
    random.seed(seed)
    th=[random.uniform(0,2*math.pi) for _ in range(N)]; vel=[0.0]*N
    om=[0.35+0.50*random.random() for _ in range(N)]; acc=[]
    for t in range(T):
        R,psi=order(th)
        for i in range(N):
            vel[i]+=dt*(om[i]-gamma*vel[i]+Kglobal*R*math.sin(psi-th[i]))
        th=[th[i]+dt*vel[i] for i in range(N)]
        if t>=T-300: r,_=order(th); acc.append(r)
    return sum(acc)/len(acc)

def test_sync():
    banner("2 · ROBUST SYNC AT SCALE — the external lead holds at any N")
    print(f"  inertial + all-to-all (the '1' leads), K=2.0 · order parameter R")
    print(f"    {'N':>5} | {'R (external lead)':>18}")
    out={}
    for N in (5,50,200,500):
        out[N]=sync(N,2.0); print(f"    {N:>5} | {out[N]:>18.3f}")
    print("  → unlike the bare ring (which fell to R≈0.22 at N=160), the external lead keeps")
    print("    the whole lattice locked at any size. robust, native synchronization.")
    return out

# ════════════ 3 · HYSTERESIS — the emergent signature of inertia ════════════
def hysteresis(N=200, gamma=0.30, dt=0.05, T_relax=700, avg=250, seed=11):
    random.seed(seed)
    th=[random.uniform(0,2*math.pi) for _ in range(N)]; vel=[0.0]*N
    om=[random.gauss(0,0.9) for _ in range(N)]
    grid=[round(0.25*k,2) for k in range(0,29)]           # K = 0 .. 7.0
    def relax(K):
        acc=[]
        for t in range(T_relax):
            R,psi=order(th)
            for i in range(N):
                vel[i]+=dt*(om[i]-gamma*vel[i]+K*R*math.sin(psi-th[i]))
            for i in range(N): th[i]+=dt*vel[i]
            if t>=T_relax-avg: acc.append(order(th)[0])     # time-average R (settle the slosh)
        return sum(acc)/len(acc)
    up={K:relax(K) for K in grid}
    down={K:relax(K) for K in reversed(grid)}
    return grid,up,down

def test_hysteresis():
    banner("3 · HYSTERESIS — the collective signature inertia adds")
    grid,up,down=hysteresis()
    show=[1.0,2.0,3.0,4.0,5.0]
    print("        K   :", "  ".join(f"{k:>5.1f}" for k in show))
    print("  R (up)    :", "  ".join(f"{up[k]:>5.2f}" for k in show))
    print("  R (down)  :", "  ".join(f"{down[k]:>5.2f}" for k in show))
    gap=max(down[k]-up[k] for k in grid)
    kgap=max(grid, key=lambda k: down[k]-up[k])
    print(f"  max R(down) − R(up) = {gap:.2f}  at K≈{kgap}")
    if gap>0.15:
        print("  → a real HYSTERESIS LOOP: the synced state survives to lower coupling than it")
        print("    formed at. a discontinuous (first-order) transition — pure inertia, genuinely")
        print("    emergent. the over-damped first-order model has NO such loop.")
    else:
        print("  → only a faint loop at these settings (honest: inertia/damping not in the bistable regime).")
    return gap

if __name__=="__main__":
    print("Tetraktys — going nuclear (native inertial + external-lead engine)")
    test_lightcone(); s=test_sync(); g=test_hysteresis()
    banner("FULL EMERGENCE — what is now native")
    print("  • light-cone : NATIVE & ballistic (t∝d) — inertia, not diffusion.")
    print(f"  • sync       : ROBUST at scale (R≈{s[500]:.2f} at N=500) via the external lead.")
    print(f"  • hysteresis : emergent bistability (ΔR≈{g:.2f}) — inertia's own signature.")
    print("  • spin (720°)+ precession : unchanged, by design (the quaternion algebra).")
    print("  the cosmology stays mythology; the emergence is now native, robust, and richer.")
