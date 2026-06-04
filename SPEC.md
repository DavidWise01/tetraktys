# Tetraktys — the spec

A precise, runnable reading of the notation:

```
1   xwyzn   00   xwyzn   00   xwyzn   00   xwyzn   00   xwyzn   1
↑     ↑      ↑                                                   ↑
lead  cell   bond (quaternary, 2-bit = NSEW)            lead → closes the ring (a torus)
```

→ **a ring of 5 quaternion cells, 4 quaternary bonds, closed by two unity leads.**

## The algebra

**NSEW = the 4th roots of unity.** Two bits per cell, four cardinal valences:

| dir | colour | bits | root | meaning in the lore* |
|-----|--------|------|------|----------------------|
| **N** | black | `10` | −1 | contraction / "time-in" |
| **S** | white | `00` | +1 | expansion / "time-out" |
| **E** | red   | `01` | +i | radiate / "distance" |
| **W** | blue  | `11` | −i | cohere / "structure" |

Multiply by `i` and the compass turns 90°: `S → E → N → W → S`. It **precesses** (period 4) instead of bouncing along a line. That is the whole upgrade from binary ±1.

**The cell `xwyzn` = a quaternion.** The four axes `x w y z` are the four quaternion
components `(1, i, j, k)`; `q = z·1 + x·i + w·j + y·k`. Unit quaternions are **SU(2)** — the
group where physical **spin** lives. `n` is the tick that counts the register. NSEW is the
`i`-plane sub-case of the quaternion (the compass circle).

**The bonds `00`** couple neighbouring cells; the two **`1` leads** close the chain into a ring
(a discrete torus). Each tick: every cell precesses (left-multiply by its natural unit
quaternion), then is pulled toward its neighbours through the bonds.

\* the "meaning" column is the model's *mythology* — see the seam below.

## What the engine measures  (`python sim/nsew.py`)

| # | test | result | status |
|---|------|--------|--------|
| 1 | **Precession** | `S → E → N → W → S`, period 4 | **by design** |
| 2 | **Spinor 720°** | `q·q₀ = −1.000` at 360°, `+1.000` at 720° (SU(2) double cover) | **real math, by design** |
| 3 | **Phase-lock** | order parameter **R: 0.56 (K=0) → 0.98 (K=0.3) → 1.00 (K=3.0)** | **genuinely emergent** |
| 4 | **Signal speed** | kick → neighbours at t=2, far side at t=9 (finite, symmetric, *slows*) | **genuinely emergent** |
| 5 | **n rollover** | after 0→4095→0, state vs start `|dot| = 0.37` → does **not** return | **measured** |

**Emergent (3, 4):** synchronization and a finite signal speed are collective — not put into any
single cell. **By design (1, 2):** the turn and the spinor sign-flip are properties of the
algebra. **Measured (5):** rollover is just the counter wrapping; "Big Bang on rollover" is a
*design choice*, not forced.

## The seam (kept visible)

- **Real & measured:** quaternion algebra (SU(2)/spin), Kuramoto phase-lock, a finite lattice signal speed.
- **Serious speculation it rhymes with:** "spacetime from a discrete substrate" (causal sets, tensor networks); the single external lead ≈ **ER=EPR** (entanglement as a wormhole).
- **Mythology (not derived):** that NSEW *is* space/time/distance, dark matter = N-S-only,
  antimatter = blue-dominant, the matter-asymmetry, consciousness-at-the-null. And the simple
  "entanglement = shared coordinates with opposite n" picture is **ruled out by Bell's theorem.**

> Emergent as a coupled oscillator; a cosmos only by metaphor. The asterisk stays visible.
