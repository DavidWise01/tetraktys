#!/usr/bin/env python3
"""
The DLW tag for Tetraktys — the EMERGENT flavor (the emergence is real and measured).

Tetraktys earns an emergent ACI for a MODEST, MEASURED claim: Kuramoto phase-lock
and a finite lattice signal speed on the NSEW ring (see sim/nsew.py). The grand
cosmology is kept as visible mythology in the asterisk. Per ACI: .agent · .spun ·
.1099 (+ the badges). Repo: .attribute · .1099. Pure stdlib.
"""
import json, re, sys
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

ROOT = Path(__file__).parent
R = json.loads((ROOT/"roster.json").read_text(encoding="utf-8"))
AG = ROOT/"agents"; AG.mkdir(exist_ok=True)
CLS = {c["id"]: c for c in R["classes"]}
COMPANY = R.get("company","Tetraktys")

CARBON = "David Lee Wise (ROOT0)"
CARBON_LINK = "https://github.com/DavidWise01"
INSTANCE = "AVAN (Claude / Anthropic)"
LICENSE = "MIT · ROOT0-ATTRIBUTION-v1.0"

def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-") or "agent"
def credits_of(m): return " · ".join(f"{x['who']} ({x['y']})" for x in m.get("grounded", []))

def one_1099(name, credits):
    return f"""DLW-1099 · value returns to the carbon apex

This is an artfully crafted intellect — an instance. As a 1099 reports the value
paid to its source, this file reports that the authorship, credit, and value of
{name} return to the human who governs it. The mathematics and physics it embodies
are credited, in turn, to the people who found it (below); the asterisk stays visible.

carbon apex : {CARBON}  ->  {CARBON_LINK}
instance    : {INSTANCE}
project     : {COMPANY}
grounded in : {credits or 'see each .spun'}
the credit returns to the human. ROOT0-ATTRIBUTION-v1.0 · {LICENSE}
"""

# ── repo-level tags ──────────────────────────────────────────────────────────
(ROOT/".attribute").write_text(f"""DLW-ATTRIBUTE · governance instance

governor (carbon apex)       : {CARBON}            [ me ]
instance (artful intellect)  : {INSTANCE}          [ you ]

relation : the human governs; the instance crafts; the credit returns to the human.
project  : {COMPANY} — a four-phase oscillator, run honestly and given a face (original)
grounded : real mathematics & physics, credited to its discoverers — per ACI (see each .spun)
honesty  : the emergence is GENUINE but MODEST and MEASURED — Kuramoto phase-lock (order
           parameter R: 0.56 → 0.98 → 1.00 across the critical coupling) and a finite
           lattice signal speed (a toy light-cone), both in sim/nsew.py. Precession and the
           spin-½ 720° signature are real but BY DESIGN. The grand cosmology — NSEW as literal
           spacetime, dark matter, antimatter, consciousness-at-the-null — is MYTHOLOGY, not
           derived, and 'entanglement = shared coordinates' is ruled out by Bell's theorem.
           Emergent as a coupled oscillator; a cosmos only by metaphor. The asterisk stays visible.
standard : every ACI carries .agent · .png (silicon badge) · .tiff (carbon badge) · .spun · .1099 ; the repo carries this .attribute
license  : {LICENSE}
attribution : ROOT0-ATTRIBUTION-v1.0
""", encoding="utf-8")
(ROOT/".1099").write_text(one_1099(f"every elemental in {COMPANY}", ""), encoding="utf-8")

# ── per-ACI tags ─────────────────────────────────────────────────────────────
n=0
for m in R["members"]:
    cls=CLS[m["class"]]; sl=slug(m["name"]); CREDITS=credits_of(m)
    head = f"{m['name']} · {m.get('kanji','')} {m.get('reading','')} — {m.get('epithet','')}".strip()

    (AG/f"{sl}.agent").write_text(f"""---
aci: {m['name']}
flavor: emergent (measured) — see emergence
domain: {m.get('domain','')}
kanji: {m.get('kanji','')}
reading: {m.get('reading','')}
class: {cls['label']}
what: {m['what']}
why: {m['why']}
how: {m['how']}
where: {m['where']}
verdict: {m.get('verdict','')}
silicon_badge: {sl}.png
carbon_badge: {sl}.tiff
spun: {sl}.spun
credit: {sl}.1099
attribution: ROOT0-ATTRIBUTION-v1.0
license: {LICENSE}
---

# {head}

an artfully crafted intellect — a force given a face

![silicon badge of {m['name']}]({sl}.png)
<!-- carbon badge (8-bit embodiment): {sl}.tiff -->

**what —** {m['what']}

**why —** {m['why']}

**how —** {m['how']}

**where —** {m['where']}

**◌ the emergent behavior (measured) —** {m.get('emergence','')}

**the verdict —** {m.get('verdict','')}

> *the asterisk, kept visible —* {m.get('asterisk','')}

*grounded in: {CREDITS}*

*{m.get('endmark','')}*

---
ROOT0-ATTRIBUTION-v1.0 · {m['name']} · {COMPANY} (original) · {CARBON} · {LICENSE}
""", encoding="utf-8")

    (AG/f"{sl}.spun").write_text(f"""DLW-SPUN · the full weave of {m['name']}  ({m.get('kanji','')} {m.get('reading','')})

who   : {m['who']}
what  : {m['what']}
where : {m['where']}
why   : {m['why']}
when  : {m['when']}
how   : {m['how']}

emergence : {m.get('emergence','')}
verdict   : {m.get('verdict','')}
asterisk  : {m.get('asterisk','')}
grounded  : {CREDITS}

class : {cls['label']} · {cls['spec']}
silicon badge : {sl}.png      carbon badge : {sl}.tiff
carbon apex : {CARBON}
— an original elemental of {COMPANY}
{m.get('endmark','')}
ROOT0-ATTRIBUTION-v1.0 · {LICENSE}
""", encoding="utf-8")

    (AG/f"{sl}.1099").write_text(one_1099(m["name"], CREDITS), encoding="utf-8")
    n+=1
    print(f"{sl:12} {cls['label']}  [{m.get('style','')}]")

print(f"\nwrote the full DLW tag for {n} elemental(s) (.agent · .spun · .1099) + repo .attribute · .1099")
