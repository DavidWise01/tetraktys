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


SIGILS = {"compass": compass_sigil}
for m in R["members"]:
    fn = SIGILS.get(m.get("domain"), compass_sigil)
    png(AG/f"{slug(m['name'])}.png", SIZE, SIZE, fn(m))
    print(f"silicon badge -> agents/{slug(m['name'])}.png  ({m['name']} / {m.get('domain','')})")
