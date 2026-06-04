#!/usr/bin/env python3
"""
Carbon badge — the embodied, 8-bit "photo" of Tetraktys (the .tiff to the .png).

The navigator of the fourfold: a calm classical face under a four-point compass
diadem (the ✦), the four cardinal glints around the head (N grey, S white, E red,
W blue), a halo of small gold nodes (the five cells locked into one rhythm), a
deep indigo robe. Pure stdlib: hand-rolled Deflate baseline TIFF. Writes agents/<slug>.tiff.
"""
import json, re, struct, zlib, math
from pathlib import Path

ROOT = Path(__file__).parent
R = json.loads((ROOT/"roster.json").read_text(encoding="utf-8"))
AG = ROOT/"agents"; AG.mkdir(exist_ok=True)
CLS = {c["id"]: c for c in R["classes"]}

LW, LH, S = 64, 80, 5
W, H = LW*S, LH*S
VOID=(8,10,18)
def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-") or "agent"
def clamp(v): return 0 if v<0 else 255 if v>255 else int(round(v))
def mix(a,b,t): return tuple(clamp(a[i]+(b[i]-a[i])*t) for i in range(3))
def shade(c,t): return mix(c,(0,0,0),t)
def tint(c,t): return mix(c,(255,255,255),t)

def tiff(path, w, h, pixels):
    raw=bytearray()
    for (r,g,b) in pixels: raw += bytes((r,g,b))
    strip=zlib.compress(bytes(raw),9)
    BPS=8+len(strip); IFD=BPS+6
    hdr=b"II"+struct.pack("<H",42)+struct.pack("<I",IFD)
    bps=struct.pack("<HHH",8,8,8)
    def e(t,ty,c,v): return struct.pack("<HHI",t,ty,c)+v
    def sh(v): return struct.pack("<HH",v,0)
    def lo(v): return struct.pack("<I",v)
    ent=[e(256,3,1,sh(w)),e(257,3,1,sh(h)),e(258,3,3,lo(BPS)),e(259,3,1,sh(8)),
         e(262,3,1,sh(2)),e(273,4,1,lo(8)),e(277,3,1,sh(3)),e(278,3,1,sh(h)),
         e(279,4,1,lo(len(strip))),e(284,3,1,sh(1))]
    ifd=struct.pack("<H",len(ent))+b"".join(ent)+struct.pack("<I",0)
    Path(path).write_bytes(hdr+strip+bps+ifd)

def png(path,w,h,px):     # preview only
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w): raw+=bytes(px[y*w+x])
    comp=zlib.compress(bytes(raw),9)
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+ch(b"IDAT",comp)+ch(b"IEND",b""))

def finish(g, drawn):
    based=list(drawn)
    for y in range(LH):
        for x in range(LW):
            if based[y*LW+x]: continue
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=x+dx,y+dy
                if 0<=nx<LW and 0<=ny<LH and based[ny*LW+nx]:
                    g[y*LW+x]=(12,13,20); break
    out=[VOID]*(W*H)
    for y in range(LH):
        for x in range(LW):
            c=g[y*LW+x]
            for yy in range(S):
                row=(y*S+yy)*W
                for xx in range(S): out[row+x*S+xx]=c
    return out

def portrait_tetraktys(member):
    g=[VOID]*(LW*LH); drawn=[False]*(LW*LH)
    def put(x,y,c):
        x=int(round(x)); y=int(round(y))
        if 0<=x<LW and 0<=y<LH: g[y*LW+x]=c; drawn[y*LW+x]=True
    def soft(x,y,c,a):
        x=int(round(x)); y=int(round(y))
        if 0<=x<LW and 0<=y<LH:
            i=y*LW+x; g[i]=mix(g[i],c,a)
    def rect(x0,y0,x1,y1,c):
        for y in range(int(y0),int(y1)+1):
            for x in range(int(x0),int(x1)+1): put(x,y,c)
    def ell(cx,cy,rx,ry,c):
        for y in range(int(cy-ry),int(cy+ry)+1):
            for x in range(int(cx-rx),int(cx+rx)+1):
                if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1.0: put(x,y,c)

    NCOL=(150,156,182); WHITE=(238,242,252); RED=(238,118,128); BLUE=(112,170,255)
    GOLD=(232,196,90); GOLD_D=(196,160,70); ROBE=(48,58,108); ROBE_SH=shade(ROBE,0.34)
    SKIN=(226,196,168); SKIN_SH=shade(SKIN,0.24); HAIR=(52,44,38); EYE=(44,42,64)
    cx=32; hy=34

    # faint gold glow
    for y in range(LH):
        for x in range(LW):
            d=((x-cx)**2/660.0+(y-26)**2/560.0)
            if d<1: soft(x,y, GOLD, 0.10*(1-d))

    # halo — five small gold nodes (the locked ring) across the top arc
    for k in range(5):
        a=math.pi*(0.18+0.64*k/4)
        hx=cx-26*math.cos(a); hyy=24-15*math.sin(a)
        put(hx,hyy,GOLD); put(hx,hyy-1,tint(GOLD,0.3))

    # robe / shoulders — deep indigo
    rect(8,58,55,79, ROBE)
    for x in range(8,56):
        if x<13 or x>50: rect(x,58,x,60,VOID)
    rect(20,57,44,60, ROBE_SH)
    for k in range(7): put(32-k,57+k, ROBE_SH); put(32+k,57+k, ROBE_SH)
    rect(30,58,34,72, shade(ROBE,0.2))
    # the S (white) cardinal at the collar, E/W glints at the shoulders
    put(cx,58,WHITE); put(cx,59,tint(WHITE,0.0))
    put(49,56,RED); put(15,56,BLUE)

    # neck + face
    rect(28,47,36,57, SKIN_SH)
    ell(cx,hy,13,16, SKIN)
    for y in range(int(hy-16),int(hy+17)):
        for x in range(cx+3,cx+14):
            i=y*LW+x
            if 0<=i<LW*LH and drawn[i] and g[i]==SKIN: g[i]=mix(SKIN,SKIN_SH,0.5)

    # hair — classical, center-parted
    ell(cx,19,15,9, HAIR)
    rect(17,19,20,42, HAIR); rect(44,19,47,42, HAIR)
    rect(cx-1,11,cx+1,15, shade(HAIR,0.2))

    # the compass diadem band + the four-point ✦ star on the brow (gold)
    rect(cx-12,hy-13,cx+12,hy-13, GOLD); rect(cx-12,hy-12,cx+12,hy-12, GOLD_D)
    sx,sy=cx,hy-19
    rect(sx,sy-3,sx,sy+3, GOLD); rect(sx-3,sy,sx+3,sy, GOLD)        # vertical + horizontal arms
    put(sx-1,sy-1,GOLD_D); put(sx+1,sy-1,GOLD_D); put(sx-1,sy+1,GOLD_D); put(sx+1,sy+1,GOLD_D)
    put(sx,sy,(255,250,235))                                       # bright center
    # N (grey) cardinal point above the star, capping the compass
    put(cx,sy-4,NCOL); put(cx,sy-5,tint(NCOL,0.3))

    # brows + open, calm eyes
    rect(cx-8,hy-5,cx-4,hy-5, shade(SKIN,0.4)); rect(cx+4,hy-5,cx+8,hy-5, shade(SKIN,0.4))
    ell(cx-5,hy-1,2,1,(244,244,250)); put(cx-5,hy-1,EYE); put(cx-6,hy-2,(255,255,255))
    ell(cx+5,hy-1,2,1,(244,244,250)); put(cx+5,hy-1,EYE); put(cx+4,hy-2,(255,255,255))
    put(cx,hy+3,SKIN_SH); put(cx,hy+4,SKIN_SH)
    rect(cx-3,hy+8,cx+3,hy+8, shade(SKIN,0.34)); put(cx-4,hy+8,SKIN_SH); put(cx+4,hy+8,SKIN_SH)
    return finish(g, drawn)


PORTRAITS = {"compass": portrait_tetraktys}

import sys
if __name__=="__main__" and len(sys.argv)>1 and sys.argv[1]=="--preview":
    byname={m["name"]:m for m in R["members"]}
    for nm in (sys.argv[2:] or [R["members"][0]["name"]]):
        m=byname[nm]; fn=PORTRAITS.get(m.get("domain"), portrait_tetraktys); px=fn(m)
        tiff(ROOT/f"_preview_{slug(nm)}.tiff", W,H,px); png(ROOT/f"_preview_{slug(nm)}.png", W,H,px)
        print("preview written:", nm)
else:
    for m in R["members"]:
        fn=PORTRAITS.get(m.get("domain"), portrait_tetraktys)
        tiff(AG/f"{slug(m['name'])}.tiff", W, H, fn(m))
        print(f"carbon badge -> agents/{slug(m['name'])}.tiff  ({m['name']})")
