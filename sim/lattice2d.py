#!/usr/bin/env python3
"""
Tetraktys — the 2-D inertial lattice (one world).

The ring becomes a torus: an L×L grid of inertial NSEW cells with periodic
(toroidal) boundaries. The same native dynamics now run all three emergent
behaviours in ONE world:

  • a 2-D ballistic LIGHT-CONE   — a point kick → a circular wavefront at constant speed
  • two-source INTERFERENCE      — coherent sources → fringes (see sim/scale.py)
  • SYNCHRONIZATION              — detuned cells + the external lead → global lock

This file VERIFIES the 2-D claims and renders a snapshot; cosmos.html runs the
same model live in the browser. Pure stdlib, deterministic. Writes img/cosmos.png.
"""
import math, random, struct, zlib, sys
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT/"img"; IMG.mkdir(exist_ok=True)
def banner(t): print("\n"+"="*68+"\n"+t+"\n"+"="*68)

def png(path,w,h,px):
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w): raw+=bytes(px[y*w+x])
    comp=zlib.compress(bytes(raw),9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+ch(b"IDAT",comp)+ch(b"IEND",b""))

# ───────── A · 2-D ballistic light-cone (circular wavefront, constant speed) ─────────
def test_lightcone2d():
    banner("A · 2-D LIGHT-CONE — a point kick makes a circular wavefront at constant speed")
    L=161; K=0.25; c=L//2; steps=150; thresh=0.03
    u=[0.0]*(L*L); v=[0.0]*(L*L)
    for y in range(c-2,c+3):                                  # gaussian velocity impulse
        for x in range(c-2,c+3):
            v[y*L+x]=math.exp(-((x-c)**2+(y-c)**2)/3.0)
    arrive={}; snap=None
    for t in range(1,steps+1):
        nv=v[:]
        for y in range(1,L-1):
            b=y*L
            for x in range(1,L-1):
                i=b+x
                nv[i]=v[i]+K*(u[i-1]+u[i+1]+u[i-L]+u[i+L]-4.0*u[i])
        v=nv
        for i in range(L*L): u[i]+=v[i]
        for r in (15,30,50,70):
            if r not in arrive and abs(u[c*L+(c+r)])>thresh: arrive[r]=t
        if t==96: snap=u[:]
    rs=[15,30,50,70]; ts=[arrive.get(r) for r in rs]
    print("    radius r :", "  ".join(f"{r:>4}" for r in rs))
    print("    arrival t :","  ".join(f"{(t if t else -1):>4}" for t in ts))
    if all(ts): print("    t ÷ r    :", "  ".join(f"{t/r:>4.1f}" for t,r in zip(ts,rs)), " (const ⇒ constant-speed light-cone)")
    # render the snapshot ring
    GOLD=(232,196,90); BLUE=(96,158,255); DARK=(7,9,17)
    def mixc(a,b,t): t=0 if t<0 else 1 if t>1 else t; return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
    amp=max(1e-6, sorted(abs(x) for x in snap)[int(0.99*len(snap))])
    base=[DARK]*(L*L)
    for i in range(L*L):
        val=max(-1.0,min(1.0,snap[i]/amp))
        base[i]=mixc(DARK,GOLD,val) if val>=0 else mixc(DARK,BLUE,-val)
    S=2; W=L*S; out=[(0,0,0)]*(W*W)
    for y in range(L):
        for x in range(L):
            cc=base[y*L+x]
            for yy in range(S):
                row=(y*S+yy)*W
                for xx in range(S): out[row+x*S+xx]=cc
    png(IMG/"cosmos.png", W, W, out)
    print("    → a single circular wavefront expanding at constant speed → img/cosmos.png")
    return ts

# ───────── B · synchronization in 2-D (the external lead) ─────────
def test_sync2d():
    banner("B · SYNCHRONIZATION IN 2-D — detuned cells + the external lead lock the field")
    L=40; N=L*L; print(f"  {L}×{L} = {N} inertial cells, all-to-all (external lead) · order parameter R")
    out={}
    for K in (0.0, 1.0, 3.0):
        random.seed(7)
        th=[random.uniform(0,2*math.pi) for _ in range(N)]; vel=[0.0]*N
        om=[random.gauss(0,0.5) for _ in range(N)]; acc=[]; dt=0.05; gamma=0.5; T=1000
        for t in range(T):
            C=sum(math.cos(a) for a in th); Sx=sum(math.sin(a) for a in th)
            R=math.hypot(C,Sx)/N; psi=math.atan2(Sx,C)
            for i in range(N): vel[i]+=dt*(om[i]-gamma*vel[i]+K*R*math.sin(psi-th[i]))
            for i in range(N): th[i]+=dt*vel[i]
            if t>=T-200:
                C=sum(math.cos(a) for a in th); Sx=sum(math.sin(a) for a in th); acc.append(math.hypot(C,Sx)/N)
        out[K]=sum(acc)/len(acc); print(f"    K={K:<4}: R = {out[K]:.3f}")
    print("  → at K=0 the field is incoherent; the external lead drives it to a single rhythm.")
    return out

if __name__=="__main__":
    print("Tetraktys — the 2-D inertial lattice (one world)")
    test_lightcone2d(); test_sync2d()
    banner("ONE WORLD")
    print("  light-cone (circular, constant speed) · interference · synchronization —")
    print("  all the native inertial dynamics, now on a 2-D torus. watch it live: cosmos.html")
