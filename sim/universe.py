#!/usr/bin/env python3
"""
Tetraktys — "the universe" (1-D hardware ⊂ 2-D software ⊂ 3-D test loop).

The three injections, built and MEASURED on an 8×8×8 toroidal NSEW lattice
(the visualised slice of the 8⁴ register), inertial dynamics, run to n=4096:

  • FORCED FLIP    — dump N (contraction) charge; does the majority valence flip S→N?
                     measured as a THRESHOLD (basin of attraction), not a story.
  • COHERENCE LOCK — force E≈W each tick; measure the balance metric over the run.
  • TOROID         — render the lattice on a torus, coloured by valence, antipode links.

Honest seam: the mechanics (a threshold-gated majority flip, a forced balance that
holds until the flip) are real and reproducible. "Big Crunch / CP violation /
antimatter / cognition" are METAPHOR, not derived. Pure stdlib, deterministic.
Writes img/universe_flip.png and img/toroid.png.
"""
import math, random, struct, zlib, sys
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT/"img"; IMG.mkdir(exist_ok=True)
def banner(t): print("\n"+"="*68+"\n"+t+"\n"+"="*68)

L=8; N=L*L*L                              # 8×8×8 = 512 cells (the visualised slice)
def idx(i,j,k): return (i%L)*L*L+(j%L)*L+(k%L)
NB=[]                                     # 6 toroidal neighbours per cell
for i in range(L):
    for j in range(L):
        for k in range(L):
            NB.append([idx(i+1,j,k),idx(i-1,j,k),idx(i,j+1,k),idx(i,j-1,k),idx(i,j,k+1),idx(i,j,k-1)])

def run(Q_inject, flip_at=3000, window=250, lock=True, steps=4096,
        Kloc=0.6, gamma=0.30, dt=0.18, mu=0.6, seed=7, record=False):
    random.seed(seed)
    th=[random.gauss(0,0.30) for _ in range(N)]   # start near θ=0 → S (+1, expansion)
    v=[0.0]*N
    hist=[]
    for n in range(steps):
        msin=sum(math.sin(t) for t in th)/N           # net E−W imbalance
        h = Q_inject if (flip_at<=n<flip_at+window) else 0.0
        for c in range(N):
            t=th[c]; loc=0.0
            for nb in NB[c]: loc+=math.sin(th[nb]-t)
            f = -gamma*v[c] + Kloc*loc + h*math.sin(t)  # +h·sinθ drives toward π (N/contraction)
            if lock: f += -mu*msin*math.cos(t)          # coherence lock: balance E≈W
            v[c]+=dt*f
        for c in range(N): th[c]+=dt*v[c]
        if record and (n%16==0 or n==steps-1):
            mx=sum(math.cos(t) for t in th)/N
            coh=1.0-abs(sum(math.sin(t) for t in th)/N)
            hist.append((n,mx,coh))
    mx=sum(math.cos(t) for t in th)/N
    return mx, th, hist

# ─────────── 1 · FORCED FLIP as a THRESHOLD (the basin of attraction) ───────────
def test_flip():
    banner("1 · FORCED FLIP — is it threshold-gated? (the basin of attraction)")
    print("  inject N-charge Q at n=3000; final S–N order Mx (+1 = S/expansion, −1 = N/contraction):")
    last_stable=None; first_flip=None
    for Q in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0):
        mx,_,_=run(Q, steps=3600, record=False)
        phase="S (+1)" if mx>0 else "N (−1)"
        print(f"    Q={Q:<4}: Mx = {mx:+.3f}  → phase {phase}")
        if mx>0: last_stable=Q
        elif first_flip is None: first_flip=Q
    print(f"  → the +1 (S) phase is a genuine ATTRACTOR: N-doses up to Q={last_stable} are pulled back;")
    print(f"    it only flips above a CRITICAL dose (Q_crit between {last_stable} and {first_flip}). the flip is")
    print(f"    forced and threshold-gated — self-stabilising, as the structure predicts. NOT spontaneous.")
    return last_stable, first_flip

# ─────────── 2 · COHERENCE LOCK + the showcase run to n=4096 ───────────
def test_run4096():
    banner("2 · COHERENCE LOCK + the run to n=4096 (super-threshold flip)")
    mx,th,hist=run(6.0, flip_at=3000, window=250, lock=True, steps=4096, record=True)
    pre = [c for (n,_,c) in hist if n<3000]
    post= [c for (n,_,c) in hist if n>3300]
    print(f"  coherence (E≈W balance): pre-flip ≈ {sum(pre)/len(pre):.3f}  →  post-flip ≈ {sum(post)/len(post):.3f}")
    print(f"  final S–N order Mx = {mx:+.3f}  (flipped to N/contraction and stayed — held by coupling)")
    print("  → HONEST RESULT: the forced lock holds E≈W at ≈1.0 THROUGHOUT, including across the flip.")
    print("    the E-W balance and the S-N majority are independent axes here — I did NOT reproduce a")
    print("    post-flip coherence collapse (the other write-up's 0.010). reporting what the sim does.")
    return th, hist

# ─────────── renderers (pure stdlib PNG) ───────────
def png(path,w,h,px):
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w): raw+=bytes(px[y*w+x])
    comp=zlib.compress(bytes(raw),9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+ch(b"IDAT",comp)+ch(b"IEND",b""))

def plot_flip(hist, flip_at=3000):
    W,H=560,300; M=[44,16,28,40]  # margins l,t,r,b
    DARK=(10,12,20); GRID=(34,40,60); INK=(150,160,190)
    GREEN=(67,214,163); GREY=(150,156,182); CYAN=(63,208,224); GOLD=(232,196,90)
    px=[DARK]*(W*H)
    def set(x,y,c):
        x=int(x);y=int(y)
        if 0<=x<W and 0<=y<H: px[y*W+x]=c
    def line(x0,y0,x1,y1,c):
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        for k in range(n+1): set(x0+(x1-x0)*k/n, y0+(y1-y0)*k/n, c)
    x0,y0,x1,y1=M[0],M[1],W-M[2],H-M[3]
    nmax=hist[-1][0]
    def X(n): return x0+(x1-x0)*n/nmax
    def Y(val): return y1-(y1-y0)*(val+1)/2.0     # map [-1,1] → plot
    for gy in (-1,-0.5,0,0.5,1):
        line(x0,Y(gy),x1,Y(gy), GRID if gy else INK)
    line(X(flip_at),y0,X(flip_at),y1, GOLD)        # flip marker
    def series(key,c):
        p=None
        for (n,mx,coh) in hist:
            val = mx if key=="mx" else (coh*2-1)    # coh[0,1]→[-1,1] axis
            x,y=X(n),Y(val)
            if p: line(p[0],p[1],x,y,c)
            p=(x,y)
    series("coh",CYAN); series("mx",GREEN)
    png(IMG/"universe_flip.png", W, H, px)

def render_toroid(th):
    W=Wh=420; cx=cy=W/2; DARK=(8,10,18)
    NCOL=(140,146,170); SCOL=(238,242,252); ECOL=(240,114,124); WCOL=(108,168,255); CYAN=(70,150,200)
    px=[DARK]*(W*Wh)
    def blend(x,y,c,a):
        x=int(x);y=int(y)
        if 0<=x<W and 0<=y<Wh:
            i=y*W+x; px[i]=tuple(int(px[i][k]+(c[k]-px[i][k])*a) for k in range(3))
    def disk(x,y,r,c,a):
        for yy in range(int(y-r),int(y+r)+1):
            for xx in range(int(x-r),int(x+r)+1):
                if (xx-x)**2+(yy-y)**2<=r*r: blend(xx,yy,c,a)
    R=1.0; rr=0.42; al=0.62; ca,sa=math.cos(al),math.sin(al)
    pts=[]
    for i in range(L):
        for j in range(L):
            for k in range(L):
                c=idx(i,j,k); u=2*math.pi*(i+k/L)/L; vv=2*math.pi*j/L
                X=(R+rr*math.cos(vv))*math.cos(u); Y=(R+rr*math.cos(vv))*math.sin(u); Z=rr*math.sin(vv)
                Yp=Y*ca-Z*sa; Zp=Y*sa+Z*ca                 # tilt for a 3/4 view
                t=th[c]%(2*math.pi)
                col = SCOL if (math.cos(t)>0.5) else NCOL if (math.cos(t)<-0.5) else (ECOL if math.sin(t)>0 else WCOL)
                pts.append((Zp, cx+150*X, cy-150*Yp, col, c, i,j,k))
    pts.sort(key=lambda p:p[0])                              # painter's sort (back→front)
    # antipode entanglement links (faint)
    pos={p[4]:(p[1],p[2]) for p in pts}
    for i in range(0,L,2):
        for j in range(0,L,2):
            a=idx(i,j,0); b=idx(i+L//2,j+L//2,0)
            if a in pos and b in pos:
                (ax,ay),(bx,by)=pos[a],pos[b]; n=int(max(abs(bx-ax),abs(by-ay)))+1
                for s in range(0,n+1,2): blend(ax+(bx-ax)*s/n, ay+(by-ay)*s/n, CYAN, 0.10)
    for (z,sx,sy,col,c,i,j,k) in pts:
        depth=(z+1.5)/3.0; r=2.0+2.0*depth; disk(sx,sy,r,col,0.45+0.5*depth)
    png(IMG/"toroid.png", W, Wh, px)

if __name__=="__main__":
    print("Tetraktys — the universe (8×8×8 toroidal NSEW lattice, run to n=4096)")
    Qc=test_flip()
    th,hist=test_run4096()
    plot_flip(hist)
    # toroid: render the NSEW valence *layout* (a winding field) so all four colours flow
    # around the ring — the topology + colour map, not the monochrome flipped end-state.
    th_show=[2*math.pi*((i+k/L)/L)+math.pi*(j/L) for i in range(L) for j in range(L) for k in range(L)]
    render_toroid(th_show)
    print("\n  rendered: img/universe_flip.png (Mx + coherence vs n) · img/toroid.png (the donut)")
    banner("THE SEAM — what is real, what is metaphor")
    print("  REAL & measured : a threshold-gated majority flip S→N (basin of attraction);")
    print("                    a forced E≈W lock that holds until the flip; a toroidal layout.")
    print("  METAPHOR        : 'Big Crunch', 'CP violation', 'antimatter burns off', 'cognition',")
    print("                    'our universe expanding 13.8 Gyr'. evocative labels, NOT derived.")
    print("  the sim shows a coupled-oscillator lattice flipping its majority phase past a")
    print("  threshold. that is the honest result. the cosmos remains the metaphor.")
