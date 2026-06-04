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


# ── shared helpers for the court portraits (64×80 logical) ──
def cput(g,d,x,y,c):
    x=int(round(x)); y=int(round(y))
    if 0<=x<LW and 0<=y<LH: g[y*LW+x]=c; d[y*LW+x]=True
def csoft(g,x,y,c,a):
    x=int(round(x)); y=int(round(y))
    if 0<=x<LW and 0<=y<LH: i=y*LW+x; g[i]=mix(g[i],c,a)
def crect(g,d,x0,y0,x1,y1,c):
    for y in range(int(y0),int(y1)+1):
        for x in range(int(x0),int(x1)+1): cput(g,d,x,y,c)
def cell(g,d,cx,cy,rx,ry,c):
    for y in range(int(cy-ry),int(cy+ry)+1):
        for x in range(int(cx-rx),int(cx+rx)+1):
            if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1.0: cput(g,d,x,y,c)
def cline(g,d,x0,y0,x1,y1,c):
    n=int(max(abs(x1-x0),abs(y1-y0)))+1
    for k in range(n+1): cput(g,d,x0+(x1-x0)*k/n, y0+(y1-y0)*k/n, c)
def glow(g,cx,cy,col,amp,sx,sy):
    for y in range(LH):
        for x in range(LW):
            dd=((x-cx)**2/sx+(y-cy)**2/sy)
            if dd<1: csoft(g,x,y,col,amp*(1-dd))

def portrait_knight(m):   # White Knight — a silver great-helm, plume, an order cross
    g=[VOID]*(LW*LH); d=[False]*(LW*LH)
    SIL=(188,198,218); SIL_D=shade(SIL,0.3); STEEL=(118,132,164); W=(238,242,252); GD=(232,196,90); DK=(26,28,40)
    cx=32; glow(g,cx,26,W,0.08,640,560)
    crect(g,d,9,58,54,79, SIL)
    for x in range(9,55):
        if x<14 or x>49: crect(g,d,x,58,x,60,VOID)
    crect(g,d,20,57,44,60, SIL_D)
    for k in range(7): cput(g,d,32-k,57+k, SIL_D); cput(g,d,32+k,57+k, SIL_D)
    crect(g,d,31,64,33,73, GD); crect(g,d,28,67,36,69, GD)        # order cross
    crect(g,d,28,49,36,57, STEEL)                                  # neck
    crect(g,d,cx-12,24,cx+12,46, SIL); cell(g,d,cx,25,13,11, SIL)  # great helm
    crect(g,d,cx-11,31,cx+11,33, DK)                               # visor slit
    crect(g,d,cx,24,cx,46, SIL_D)
    for yy in (28,38,43): cput(g,d,cx-9,yy, STEEL); cput(g,d,cx+9,yy, STEEL)
    for yy in (38,40,42): cput(g,d,cx+5,yy, DK); cput(g,d,cx+7,yy,DK)
    for k in range(7): cput(g,d,cx, 23-k, W); cput(g,d,cx-1,21-k,SIL); cput(g,d,cx+1,22-k,SIL)  # plume
    return finish(g, d)

def portrait_queen(m):    # Dark Queen — pale face, a tall dark 5-point crown, violet robe
    g=[VOID]*(LW*LH); d=[False]*(LW*LH)
    VI=(150,136,190); VD=(74,62,108); ROBE=(52,44,78); ROBE_S=shade(ROBE,0.34); SK=(214,202,220); SK_S=shade(SK,0.22); HAIR=(30,26,44); JW=(212,192,255); GD=(232,196,90); MO=(150,92,112)
    cx=32; hy=37; glow(g,cx,28,VI,0.12,680,560)
    crect(g,d,8,58,55,79, ROBE)
    for x in range(8,56):
        if x<13 or x>50: crect(g,d,x,58,x,60,VOID)
    crect(g,d,20,57,44,60, ROBE_S)
    for k in range(8): cput(g,d,32-k,57+k, ROBE_S); cput(g,d,32+k,57+k, ROBE_S)
    for x in range(20,45): cput(g,d,x, 56-abs(x-32)//3, VD)       # high collar
    crect(g,d,28,49,36,57, SK_S); cell(g,d,cx,hy,12,15, SK)       # neck + pale face
    cell(g,d,cx,23,15,9, HAIR); crect(g,d,18,23,21,45,HAIR); crect(g,d,43,23,46,45,HAIR)
    crect(g,d,cx-8,hy-4,cx-4,hy-4, shade(SK,0.4)); crect(g,d,cx+4,hy-4,cx+8,hy-4, shade(SK,0.4))
    cell(g,d,cx-5,hy-1,2,1,(40,36,60)); cell(g,d,cx+5,hy-1,2,1,(40,36,60))
    cput(g,d,cx,hy+3,SK_S); crect(g,d,cx-3,hy+8,cx+3,hy+8, MO)    # severe mouth
    by=hy-13; crect(g,d,cx-11,by,cx+11,by, VD)                    # crown band
    for p,h in zip((-1.0,-0.5,0,0.5,1.0),(4,6,9,6,4)):
        bx=int(cx+p*11)
        for hh in range(h): cput(g,d,bx, by-1-hh, VI)
        cput(g,d,bx, by-1-h, JW); cput(g,d,bx, by-2-h, GD)
    return finish(g,d)

def portrait_jester(m):   # Red Court Jester — a grin, a three-point belled cap, motley collar
    g=[VOID]*(LW*LH); d=[False]*(LW*LH)
    RD=(228,96,110); CR=(184,64,84); GD=(232,196,90); SK=(226,196,168); SK_S=shade(SK,0.22); WT=(255,250,235); EYE=(40,30,34)
    cx=32; hy=39; glow(g,cx,30,RD,0.10,700,600)
    crect(g,d,8,61,55,79, CR)
    for x in range(8,56):
        if x<13 or x>50: crect(g,d,x,61,x,63,VOID)
    for x in range(10,54,4): cput(g,d,x,60,RD); cput(g,d,x+2,60,GD)   # motley zigzag + bells
    crect(g,d,28,52,36,61, SK_S); cell(g,d,cx,hy,12,14, SK)           # neck + face
    cell(g,d,cx-5,hy-2,2,2,WT); cput(g,d,cx-5,hy-2,EYE)
    cell(g,d,cx+5,hy-2,2,2,WT); cput(g,d,cx+5,hy-2,EYE)
    for t in range(11): cput(g,d, cx-7+t*1.4, hy+4+2.6*math.sin(t/10*math.pi), CR)   # grin (corners up)
    cput(g,d,cx-7,hy+3, RD); cput(g,d,cx+7,hy+3, RD)                  # rosy cheeks
    by=hy-12; crect(g,d,cx-12,by,cx+12,by, RD)                        # cap band
    for tx,ty in ((-14,-7),(0,-13),(14,-7)):
        cline(g,d, cx+tx//2, by-1, cx+tx, by+ty, RD); cell(g,d,cx+tx,by+ty,2,2, GD)  # point + bell
    return finish(g,d)

def portrait_wizard(m):   # Blue Wizard — long beard, a starred pointed hat, blue robe
    g=[VOID]*(LW*LH); d=[False]*(LW*LH)
    BD=(48,74,140); BL=(96,150,230); SK=(224,198,172); SK_S=shade(SK,0.2); BR=(216,224,238); BR_S=(166,178,204); GD=(232,196,90); WT=(245,250,255); EYE=(40,42,64)
    cx=32; hy=35; glow(g,cx,30,BL,0.11,680,620)
    crect(g,d,9,60,54,79, BD)
    for x in range(9,55):
        if x<14 or x>49: crect(g,d,x,60,x,62,VOID)
    crect(g,d,28,41,36,47, SK_S); cell(g,d,cx,38,11,10, SK)           # neck + face
    cell(g,d,cx-5,hy+2,2,1,WT); cput(g,d,cx-5,hy+2,EYE)
    cell(g,d,cx+5,hy+2,2,1,WT); cput(g,d,cx+5,hy+2,EYE)
    crect(g,d,cx-7,hy,cx-3,hy, BR_S); crect(g,d,cx+3,hy,cx+7,hy, BR_S)   # bushy brows
    cput(g,d,cx,hy+4,SK_S)
    for y in range(46,73):                                           # the long beard
        w=max(2, 11-(y-46)//2); crect(g,d,cx-w,y,cx+w,y, BR if y%2==0 else BR_S)
    tipx,tipy=cx,5; blx,bly=cx-15,30; brx=cx+15; yy=tipy             # pointed hat
    while yy<=bly:
        t=(yy-tipy)/(bly-tipy); xl=tipx+(blx-tipx)*t; xr=tipx+(brx-tipx)*t
        crect(g,d,xl,yy,xr,yy, BD); yy+=1
    cline(g,d,tipx,tipy,blx,bly,BL); cline(g,d,tipx,tipy,brx,bly,BL); crect(g,d,blx-3,30,brx+3,31, BL)
    for sx,sy in ((cx,15),(cx+5,23),(cx-6,25)):
        cput(g,d,sx,sy,GD); cput(g,d,sx-1,sy,GD); cput(g,d,sx+1,sy,GD); cput(g,d,sx,sy-1,GD); cput(g,d,sx,sy+1,GD)
    return finish(g,d)

PORTRAITS = {"compass": portrait_tetraktys, "knight": portrait_knight, "queen": portrait_queen, "jester": portrait_jester, "wizard": portrait_wizard}

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
