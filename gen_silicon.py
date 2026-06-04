#!/usr/bin/env python3
"""
Silicon badge — the abstract, computed essence of Tetraktys.

The NSEW compass: four cardinal valences (N grey, S white, E red, W blue) on the
unit circle of the 4th roots of unity, a precession arrow turning it (×i = 90°),
and the inner ring of five coupled cells locked into one rhythm (gold, aligned).
Deterministic, pure-stdlib PNG. Writes agents/<slug>.png.
"""
import json, re, zlib, struct, math
from pathlib import Path

ROOT = Path(__file__).parent
R = json.loads((ROOT/"roster.json").read_text(encoding="utf-8"))
AG = ROOT/"agents"; AG.mkdir(exist_ok=True)
CLS = {c["id"]: c for c in R["classes"]}

SIZE  = 360
VOID  = (8, 10, 18)
NCOL  = (122, 128, 152)   # N · black cardinal, drawn as cool silver so it reads
WHITE = (238, 242, 252)   # S · white
RED   = (240, 110, 120)   # E · red
BLUE  = (108, 168, 255)   # W · blue
GOLD  = (232, 196, 90)    # the emergent locked rhythm
INK   = (120, 140, 210)

def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-") or "agent"
def clamp(v): return 0 if v<0 else 255 if v>255 else int(round(v))
def mix(a,b,t): return tuple(clamp(a[i]+(b[i]-a[i])*t) for i in range(3))

def png(path, w, h, px):
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w): raw += bytes(px[y*w+x])
    comp=zlib.compress(bytes(raw),9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"
        + ch(b"IHDR", struct.pack(">IIBBBBB", w,h,8,2,0,0,0))
        + ch(b"IDAT", comp) + ch(b"IEND", b""))

def compass_sigil(member):
    px=[VOID]*(SIZE*SIZE); cx=cy=SIZE/2.0
    for y in range(SIZE):
        for x in range(SIZE):
            d=math.hypot(x-cx,y-cy)/(SIZE*0.5); glow=max(0.0,1.0-d*1.12)
            c=mix(VOID, mix(GOLD,INK,0.5), 0.11*glow**2)
            c=mix(c, VOID, min(0.55,(d-0.72)*1.7) if d>0.72 else 0.0)
            px[y*SIZE+x]=c
    def plot(x,y,c,a=1.0):
        xi,yi=int(round(x)),int(round(y))
        if 0<=xi<SIZE and 0<=yi<SIZE:
            i=yi*SIZE+xi; px[i]=mix(px[i],c,a)
    def disk(x,y,r,c,a=1.0):
        for yy in range(int(y-r),int(y+r)+1):
            for xx in range(int(x-r),int(x+r)+1):
                if (xx-x)**2+(yy-y)**2<=r*r: plot(xx,yy,c,a)
    def ring(r,c,a,th=1):
        steps=int(2*math.pi*r)+8
        for k in range(steps):
            t=k/steps*2*math.pi; disk(cx+r*math.cos(t),cy+r*math.sin(t),th/2.0,c,a)
    def line(x0,y0,x1,y1,c,a,th=1):
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        for k in range(n+1):
            t=k/n; x=x0+(x1-x0)*t; y=y0+(y1-y0)*t
            disk(x,y,th/2.0,c,a) if th>1 else plot(x,y,c,a)
    def arc(r,a0,a1,c,a,th=2):
        n=int(abs(a1-a0)*r)+6
        for k in range(n+1):
            t=a0+(a1-a0)*k/n; disk(cx+r*math.cos(t),cy+r*math.sin(t),th/2.0,c,a)

    Rc=SIZE*0.37
    ring(Rc, mix(INK,WHITE,0.10), 0.5, th=2)             # the 4th-roots unit circle

    # precession arrow — a CCW arc just outside the circle, with a head (×i turns it)
    arc(Rc+14, -math.pi*0.30, math.pi*0.62, GOLD, 0.8, th=2)
    hx,hy=cx+(Rc+14)*math.cos(math.pi*0.62), cy+(Rc+14)*math.sin(math.pi*0.62)
    line(hx,hy, hx-9, hy-2, GOLD, 0.85, th=2); line(hx,hy, hx-2, hy-10, GOLD, 0.85, th=2)

    # the four cardinals: N top, S bottom, E right, W left
    cards=[("N",cx,cy-Rc,NCOL),("S",cx,cy+Rc,WHITE),("E",cx+Rc,cy,RED),("W",cx-Rc,cy,BLUE)]
    for nm,x,y,c in cards:
        line(cx,cy,x,y, mix(c,VOID,0.55), 0.16)           # faint spoke
        disk(x,y, 13, c, 0.16)
        if nm=="N":                                       # black cardinal → dark core, bright rim
            disk(x,y,8, (26,28,40), 0.95); ring_pts=[(x+8*math.cos(t),y+8*math.sin(t)) for t in [i*math.pi/8 for i in range(16)]]
            for (rx,ry) in ring_pts: plot(rx,ry, NCOL, 0.9)
        else:
            disk(x,y, 7, c, 0.95); disk(x,y, 3, mix(c,(255,255,255),0.5), 0.95)

    # the inner ring of five coupled cells, locked into one rhythm (all arrows aligned, gold)
    r2=SIZE*0.165
    nodes=[]
    for k in range(5):
        a=k*(2*math.pi/5) - math.pi/2
        nodes.append((cx+r2*math.cos(a), cy+r2*math.sin(a)))
    for k in range(5):                                    # the quaternary bonds (links)
        x0,y0=nodes[k]; x1,y1=nodes[(k+1)%5]
        line(x0,y0,x1,y1, mix(GOLD,VOID,0.35), 0.28)
    for (x,y) in nodes:                                   # cells + aligned dials (phase-locked)
        disk(x,y, 7, mix(GOLD,VOID,0.1), 0.18); disk(x,y, 4.2, GOLD, 0.95)
        line(x,y, x+9, y-9, GOLD, 0.9, th=2)              # every dial points the same way → locked
        disk(x+9,y-9, 2.2, mix(GOLD,WHITE,0.5), 0.95)

    disk(cx,cy, 11, mix(INK,VOID,0.3), 0.5); disk(cx,cy, 3, (255,255,255), 0.9)   # the pivot / 0,0,0,0
    return px


# ── shared helpers for the court sigils ──
def _plot(px,x,y,c,a=1.0):
    xi,yi=int(round(x)),int(round(y))
    if 0<=xi<SIZE and 0<=yi<SIZE:
        i=yi*SIZE+xi; px[i]=mix(px[i],c,a)
def _disk(px,x,y,r,c,a=1.0):
    for yy in range(int(y-r),int(y+r)+1):
        for xx in range(int(x-r),int(x+r)+1):
            if (xx-x)**2+(yy-y)**2<=r*r: _plot(px,xx,yy,c,a)
def _line(px,x0,y0,x1,y1,c,a,th=1):
    n=int(max(abs(x1-x0),abs(y1-y0)))+1
    for k in range(n+1):
        t=k/n; x=x0+(x1-x0)*t; y=y0+(y1-y0)*t
        _disk(px,x,y,th/2.0,c,a) if th>1 else _plot(px,x,y,c,a)
def _ring(px,r,c,a,th=1):
    cx=cy=SIZE/2.0; steps=int(2*math.pi*r)+8
    for k in range(steps):
        t=k/steps*2*math.pi; _disk(px,cx+r*math.cos(t),cy+r*math.sin(t),th/2.0,c,a)
def _bg(base, glow_col, glow=0.11):
    cx=cy=SIZE/2.0; px=[base]*(SIZE*SIZE)
    for y in range(SIZE):
        for x in range(SIZE):
            d=math.hypot(x-cx,y-cy)/(SIZE*0.5); g=max(0.0,1.0-d*1.12)
            c=mix(base, glow_col, glow*g**2)
            c=mix(c, base, min(0.55,(d-0.72)*1.7) if d>0.72 else 0.0)
            px[y*SIZE+x]=c
    return px

def knight_sigil(m):   # White Knight — S, +1: a silver sword, expansion rays (order & expansion)
    V=(9,10,16); W=(238,242,252); SIL=(176,188,214); ST=(120,134,166); GD=(232,196,90)
    px=_bg(V,W,0.10); cx=cy=SIZE/2.0
    for k in range(28):
        a=k*(2*math.pi/28); r0=SIZE*0.17; r1=SIZE*(0.30+0.15*((k%3)/2))
        _line(px, cx+r0*math.cos(a),cy+r0*math.sin(a), cx+r1*math.cos(a),cy+r1*math.sin(a), W, 0.10, th=1)
    tipY=cy-SIZE*0.34; guardY=cy+SIZE*0.07; gripEnd=cy+SIZE*0.24; pomY=cy+SIZE*0.27
    _line(px, cx, tipY, cx, gripEnd, SIL, 0.96, th=7)
    _line(px, cx, tipY+6, cx, guardY, W, 0.85, th=2)
    _line(px, cx-SIZE*0.13, guardY, cx+SIZE*0.13, guardY, ST, 0.96, th=6)
    _disk(px, cx, pomY, 10, GD, 0.95); _disk(px, cx, pomY, 5, W, 0.95)
    _line(px, cx, tipY-SIZE*0.05, cx, tipY-SIZE*0.012, GD, 0.9, th=3)
    _line(px, cx-SIZE*0.028, tipY-SIZE*0.034, cx+SIZE*0.028, tipY-SIZE*0.034, GD, 0.9, th=3)
    _disk(px, cx, cy, 3, W, 0.9)
    return px

def queen_sigil(m):    # Dark Queen — N, −1: a dark crown, contraction rings (the inward pull)
    V=(12,10,18); VI=(154,140,192); VD=(86,72,124); DK=(26,20,38); JW=(206,186,255); GD=(232,196,90)
    px=_bg(V,VI,0.12); cx=cy=SIZE/2.0
    for fr in (0.46,0.38,0.30,0.23): _ring(px, SIZE*fr, mix(VI,V,0.55), 0.14, th=1)
    for k in range(24):
        a=k*(2*math.pi/24)
        _line(px, cx+SIZE*0.46*math.cos(a),cy+SIZE*0.46*math.sin(a), cx+SIZE*0.40*math.cos(a),cy+SIZE*0.40*math.sin(a), mix(VI,V,0.3),0.16,th=1)
    by=cy+SIZE*0.10; halfw=SIZE*0.16
    _line(px, cx-halfw, by, cx+halfw, by, VD, 0.96, th=8)
    for p,h in zip((-1.0,-0.5,0.0,0.5,1.0),(0.14,0.20,0.27,0.20,0.14)):
        bx=cx+p*halfw; ty=by-SIZE*h
        _line(px, bx, by, bx, ty, VI, 0.9, th=3); _disk(px, bx, ty, 6, GD, 0.95); _disk(px, bx, ty, 3, JW, 0.95)
    _disk(px, cx, cy+SIZE*0.02, 15, DK, 0.45); _disk(px, cx, cy+SIZE*0.02, 6, JW, 0.45); _disk(px, cx, cy+SIZE*0.02, 3, (245,240,255), 0.9)
    return px

def jester_sigil(m):   # Red Court Jester — E, +i: a three-point cap with bells, a motion trail
    V=(14,8,10); RD=(240,110,120); CR=(200,70,90); GD=(232,196,90); CY=(95,208,230); WT=(255,250,235)
    px=_bg(V,RD,0.12); cx=cy=SIZE/2.0
    for k in range(18):
        a=-k*0.17+0.6; r=SIZE*(0.42-0.006*k)
        _disk(px, cx+r*math.cos(a), cy+r*math.sin(a), 1.6+2.0*(1-k/18), RD, 0.42*(1-k/18))
    for k in range(6):
        a=k*(2*math.pi/6)+0.3; _disk(px, cx+SIZE*0.35*math.cos(a), cy+SIZE*0.35*math.sin(a), 2.4, GD if k%2 else CY, 0.55)
    by=cy+SIZE*0.05
    _line(px, cx-SIZE*0.16, by, cx+SIZE*0.16, by, CR, 0.95, th=7)
    for (tx,ty),bx in zip(((-0.30,-0.10),(0.0,-0.34),(0.30,-0.10)),(-0.13,0.0,0.13)):
        x0=cx+bx*SIZE; x1=cx+tx*SIZE; y1=by+ty*SIZE
        mx=(x0+x1)/2 + tx*SIZE*0.05; my=(by+y1)/2 - SIZE*0.03
        _line(px, x0,by, mx,my, RD, 0.9, th=5); _line(px, mx,my, x1,y1, RD,0.9,th=4)
        _disk(px, x1,y1, 7, GD, 0.95); _disk(px, x1,y1, 3, WT,0.95)
    for t in range(9):
        _disk(px, cx-18+t*4.5, by+19+3*math.sin((t-4)*0.5), 1.5, RD, 0.6)
    _disk(px, cx, cy, 3, GD, 0.8)
    return px

def wizard_sigil(m):   # Blue Wizard — W, −i: a starred pointed hat, coherence rings & a focal orb
    V=(6,9,16); BL=(108,168,255); BD=(56,86,150); ORB=(160,205,255); ST=(232,210,140); WT=(235,244,255)
    px=_bg(V,BL,0.12); cx=cy=SIZE/2.0
    for i,fr in enumerate((0.46,0.37,0.29,0.22,0.16)): _ring(px, SIZE*fr, mix(BL,V,0.5-i*0.07), 0.10+0.04*i, th=1)
    tipx,tipy=cx, cy-SIZE*0.36; blx,bly=cx-SIZE*0.19, cy+SIZE*0.06; brx=cx+SIZE*0.19
    yy=int(tipy)
    while yy<=int(bly):
        t=(yy-tipy)/(bly-tipy); xl=tipx+(blx-tipx)*t; xr=tipx+(brx-tipx)*t
        _line(px, xl, yy, xr, yy, BD, 0.92, th=1); yy+=1
    _line(px, tipx,tipy, blx,bly, BL,0.9,th=2); _line(px, tipx,tipy, brx,bly, BL,0.9,th=2)
    _line(px, blx-SIZE*0.04, bly, brx+SIZE*0.04, bly, mix(BL,WT,0.2), 0.95, th=5)
    for (sx,sy) in ((cx-SIZE*0.02, cy-SIZE*0.16),(cx+SIZE*0.055, cy-SIZE*0.04),(cx-SIZE*0.06, cy-SIZE*0.015)):
        for dx,dy in ((0,-5),(0,5),(-5,0),(5,0)): _line(px, sx,sy, sx+dx, sy+dy, ST, 0.9, th=2)
        _disk(px,sx,sy,1.5, WT,0.9)
    _disk(px, cx, cy+SIZE*0.20, 13, mix(ORB,V,0.4), 0.4); _disk(px, cx, cy+SIZE*0.20, 8, ORB, 0.9); _disk(px, cx, cy+SIZE*0.20, 3, WT, 0.95)
    return px

def buyer_sigil(m):    # Cooper — a Cooper pair (two bonded dots) inside a ring of sourced BOM coins
    V=(6,16,15); TEAL=(134,208,192); CY=(95,208,230); GD=(232,196,90); WT=(235,250,248); LK=(120,200,210)
    px=_bg(V,TEAL,0.11); cx=cy=SIZE/2.0
    R=SIZE*0.34
    _ring(px, R, mix(TEAL,V,0.4), 0.18, th=1)                      # the cart loop / BOM ring
    for k in range(10):
        a=k*(2*math.pi/10)-math.pi/2; x=cx+R*math.cos(a); y=cy+R*math.sin(a)
        _disk(px,x,y,7,GD,0.9); _disk(px,x,y,3.5, mix(GD,WT,0.4),0.9)   # a line-item coin
        if k%2==0:                                                  # checkmark = sourced
            _line(px, x-3,y, x-1,y+3, V, 0.8, th=2); _line(px, x-1,y+3, x+4,y-3, V, 0.8, th=2)
    dx=SIZE*0.07
    _disk(px, cx-dx, cy, 16, mix(CY,V,0.5), 0.22); _disk(px, cx+dx, cy, 16, mix(CY,V,0.5), 0.22)   # pair halo
    _line(px, cx-dx, cy, cx+dx, cy, LK, 0.9, th=3)                 # the bond
    _disk(px, cx-dx, cy, 9, CY, 0.95); _disk(px, cx-dx, cy, 4, WT, 0.95)
    _disk(px, cx+dx, cy, 9, CY, 0.95); _disk(px, cx+dx, cy, 4, WT, 0.95)
    _line(px, cx-SIZE*0.18, cy, cx-dx-10, cy, mix(LK,V,0.4), 0.5, th=1)   # zero-resistance leads
    _line(px, cx+dx+10, cy, cx+SIZE*0.18, cy, mix(LK,V,0.4), 0.5, th=1)
    return px

SIGILS = {"compass": compass_sigil, "knight": knight_sigil, "queen": queen_sigil, "jester": jester_sigil, "wizard": wizard_sigil, "buyer": buyer_sigil}
for m in R["members"]:
    fn = SIGILS.get(m.get("domain"), compass_sigil)
    png(AG/f"{slug(m['name'])}.png", SIZE, SIZE, fn(m))
    print(f"silicon badge -> agents/{slug(m['name'])}.png  ({m['name']} / {m.get('domain','')})")
