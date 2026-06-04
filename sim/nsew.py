#!/usr/bin/env python3
"""
NSEW — the quaternary cardinal oscillator.

A build of the spec:   1 xwyzn 00 xwyzn 00 xwyzn 00 xwyzn 00 xwyzn 1

  quaternary valence  N S E W   ->  4th roots of unity  -1 +1 +i -i   (2 bits / cell)
  cell  'xwyzn'       ->  a unit quaternion  q = z*1 + x*i + w*j + y*k   (the four axes) + a tick n
  bond  '00'          ->  quaternary coupling between neighbouring cells
  lead  '1' ... '1'   ->  the two unity leads that close the chain into a ring (a discrete torus)

The engine runs and HONESTLY separates what is true BY DESIGN from what is genuinely EMERGENT.
Pure stdlib, deterministic (fixed seed).
"""
import math, random, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

# ───────────────────────── quaternion ─────────────────────────
class Q:
    __slots__ = ("a","b","c","d")          # a*1 + b*i + c*j + d*k
    def __init__(s,a=0.0,b=0.0,c=0.0,d=0.0): s.a,s.b,s.c,s.d=a,b,c,d
    def __mul__(p,q):
        return Q(p.a*q.a-p.b*q.b-p.c*q.c-p.d*q.d,
                 p.a*q.b+p.b*q.a+p.c*q.d-p.d*q.c,
                 p.a*q.c-p.b*q.d+p.c*q.a+p.d*q.b,
                 p.a*q.d+p.b*q.c-p.c*q.b+p.d*q.a)
    def __add__(p,q): return Q(p.a+q.a,p.b+q.b,p.c+q.c,p.d+q.d)
    def __sub__(p,q): return Q(p.a-q.a,p.b-q.b,p.c-q.c,p.d-q.d)
    def scale(p,t):   return Q(p.a*t,p.b*t,p.c*t,p.d*t)
    def dot(p,q):     return p.a*q.a+p.b*q.b+p.c*q.c+p.d*q.d
    def norm(p):      return math.sqrt(max(p.dot(p),0.0))
    def unit(p):
        n=p.norm() or 1.0; return p.scale(1.0/n)
    def __repr__(p):  return f"({p.a:+.2f}{p.b:+.2f}i{p.c:+.2f}j{p.d:+.2f}k)"

def rot(axis, angle):
    """unit quaternion = rotation by `angle` about unit 3-vector `axis`."""
    h=angle/2.0; s=math.sin(h); ax,ay,az=axis
    return Q(math.cos(h), s*ax, s*ay, s*az)

# ───────────────────── NSEW quaternary (the i-plane sub-case) ─────────────────────
# 2 bits -> a cardinal -> a 4th root of unity (k successive 90deg turns of +i)
DIRS  = ["S","E","N","W"]
ROOTS = [Q(1,0,0,0), Q(0,1,0,0), Q(-1,0,0,0), Q(0,-1,0,0)]   # +1 +i -1 -i  (white red black blue)
def nsew(bits): return DIRS[bits & 3], ROOTS[bits & 3]

# ───────────────────────── parse the spec ─────────────────────────
SPEC = "1 xwyzn 00 xwyzn 00 xwyzn 00 xwyzn 00 xwyzn 1"
def parse(spec):
    t=spec.split()
    return {"cells":t.count("xwyzn"), "bonds":t.count("00"), "leads":t.count("1")}

# ───────────────────────── the ring engine ─────────────────────────
def coherence(qs):
    """mean |dot| over adjacent pairs on the ring; |dot| handles the ±q double cover.
       random 4D unit vectors -> ~0.42 ; perfectly phase-locked -> 1.0"""
    N=len(qs); return sum(abs(qs[c].dot(qs[(c+1)%N])) for c in range(N))/N

def step(qs, gs, K):
    """one tick: each cell precesses (left-mult by its natural unit quaternion),
       then is pulled toward its two neighbours through the quaternary bonds."""
    N=len(qs); out=[]
    for c in range(N):
        q = gs[c]*qs[c]                                   # precession (the oscillator)
        if K>0.0:
            nb=(qs[(c-1)%N]+qs[(c+1)%N]).scale(0.5)       # the '00' bonds: neighbour mean
            if q.dot(nb)<0: nb=nb.scale(-1.0)             # align across the double cover
            q = q + (nb-q).scale(K)                       # pull toward neighbours
        out.append(q.unit())
    return out

random.seed(7)
def runit():
    return Q(random.gauss(0,1),random.gauss(0,1),random.gauss(0,1),random.gauss(0,1)).unit()
def naturals(N, base, spread):
    gs=[]
    for _ in range(N):
        v=(random.gauss(0,1),random.gauss(0,1),random.gauss(0,1))
        n=math.sqrt(sum(x*x for x in v)) or 1.0; ax=tuple(x/n for x in v)
        gs.append(rot(ax, base+spread*(random.random()-0.5)))
    return gs

# ═══════════════════════════ the five honest tests ═══════════════════════════
def banner(t): print("\n"+"="*64+"\n"+t+"\n"+"="*64)

def test_precession():
    banner("1 · PRECESSION  — the quaternary turn   [BY DESIGN]")
    q=ROOTS[0]; seq=[]
    for _ in range(5):
        k=0
        for j,r in enumerate(ROOTS):
            if abs(q.dot(r))>0.999 and q.dot(r)>0: k=j
        seq.append(DIRS[k]); q = Q(0,1,0,0)*q          # multiply by +i  (90deg turn)
    print("  start +1(S/white), ×i each tick:", " → ".join(seq))
    print("  period 4 — a compass that turns, not a line that bounces.")
    return seq[:4]==["S","E","N","W"]

def test_spinor():
    banner("2 · SPINOR 720°  — the i,j,k upgrade pays off   [REAL MATH / BY DESIGN]")
    q0=runit(); ax=(0.0,0.0,1.0); M=360; g=rot(ax, 2*math.pi/M)   # M tiny turns = one full 360°
    q=q0
    for _ in range(M):   q=g*q                  # 360°
    d360=q.dot(q0)
    for _ in range(M):   q=g*q                  # 720°
    d720=q.dot(q0)
    print(f"  after 360° rotation:  q·q0 = {d360:+.4f}   (a spinor flips sign → −1)")
    print(f"  after 720° rotation:  q·q0 = {d720:+.4f}   (only now is it home → +1)")
    print("  this is spin-½: the SU(2) double cover. binary ±1 can NEVER show this.")
    return d360 < -0.98 and d720 > 0.98

def test_sync():
    banner("3 · PHASE-LOCK  — the ring synchronizes on the NSEW circle   [GENUINELY EMERGENT]")
    # cells confined to the NSEW plane = phases on the compass circle (Kuramoto on a ring)
    N=5; T=3000; dt=0.05
    def run(K):
        random.seed(7)
        th=[random.uniform(0,2*math.pi) for _ in range(N)]
        om=[0.35+0.50*random.random() for _ in range(N)]      # detuned natural frequencies
        acc=[]
        for t in range(T):
            nu=th[:]
            for c in range(N):
                cpl=math.sin(th[(c-1)%N]-th[c])+math.sin(th[(c+1)%N]-th[c])
                nu[c]=th[c]+dt*(om[c]+(K/2.0)*cpl)
            th=nu
            if t>=T-400:
                sx=sum(math.cos(a) for a in th); sy=sum(math.sin(a) for a in th)
                acc.append(math.hypot(sx,sy)/N)                # Kuramoto order parameter R
        return sum(acc)/len(acc)
    out={}
    for K in (0.0, 0.3, 3.0):
        out[K]=run(K); print(f"  K={K:<4}: order parameter R = {out[K]:.3f}")
    print("  K=0: five detuned dials drift, R stays low. push coupling past the critical")
    print("  threshold and they LOCK (R→1) — collective rhythm no single dial dictates.")
    return out[3.0] > 0.9 and out[0.0] < 0.6

def test_wave():
    banner("4 · SIGNAL SPEED  — a perturbation propagates   [EMERGENT · toy light-cone]")
    N=5; K=0.30; q0=runit()
    qs=[q0 for _ in range(N)]; gs=[Q(1,0,0,0)]*N                  # aligned, no precession
    qs[0]=rot((1.0,0.0,0.0), math.pi*0.9)*qs[0]                  # kick cell 0
    arrive=[0]+[None]*(N-1); t=0
    while None in arrive and t<200:
        t+=1; qs=step(qs,gs,K)
        for c in range(N):
            if arrive[c] is None and (1.0-abs(qs[c].dot(q0)))>0.02:
                arrive[c]=t
    print("  cell      :", "  ".join(f"{c}" for c in range(N)))
    print("  arrives @t :", "  ".join(f"{a}" for a in arrive))
    finite=[a for a in arrive if a]
    speed = (max(finite)/ (N//2)) if finite else 0
    print(f"  disturbance spreads neighbour-by-neighbour at a FINITE speed (~{(N//2)/max(max(finite),1):.3f} cells/tick).")
    print("  a maximum signal speed falls out of local coupling — a toy 'c', not relativity.")
    return all(a is not None for a in arrive) and arrive[1] is not None and arrive[1] <= arrive[2 if N>2 else 1]

def test_rollover():
    banner("5 · n ROLLOVER  — 4096 → 0   [MEASURED · answers 'is it the next Big Bang?']")
    N=5; K=0.08; random.seed(7)
    qs=[runit() for _ in range(N)]; start=list(qs); gs=naturals(N,0.30,0.22)
    for n in range(4096): qs=step(qs,gs,K)
    rec=sum(abs(qs[c].dot(start[c])) for c in range(N))/N
    print(f"  after a full count (n: 0→4095→0), state vs start: |dot| = {rec:.3f}")
    if rec>0.95: print("  → the register RETURNS: rollover is a clean rebirth (periodic cosmos).")
    else:        print("  → the register does NOT return: rollover is just the counter wrapping,")
    print("    the state has moved on. 'Big Bang on rollover' is a design choice, not forced.")
    return True  # informational

if __name__=="__main__":
    print("NSEW quaternary cardinal oscillator")
    print("spec :", SPEC)
    print("parse:", parse(SPEC), "→ a ring of 5 quaternion cells, 4 quaternary bonds, closed by 2 leads")
    r=[test_precession(), test_spinor(), test_sync(), test_wave(), test_rollover()]
    banner("VERDICT")
    labels=["precession (by design)","spinor 720° (real math)","phase-lock (EMERGENT)","signal speed (EMERGENT)","rollover (measured)"]
    for ok,lab in zip(r,labels): print(f"  [{'PASS' if ok else '— '}] {lab}")
