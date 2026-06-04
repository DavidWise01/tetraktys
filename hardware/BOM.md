# BOM & Sourcing — TETRAKTYS-DO1

> **From the desk of Cooper, buyers agent** ₵
> *I turn the [blueprint](BLUEPRINT.md) into a cart. Below is the real shopping list for the Desk
> Oscillator (Tier 1) — everything in stock, nothing exotic. Prices are 2026 USD estimates; vendors are
> real. The cryogenic Tier 2 is at the bottom, and I'll be straight with you about it.*

## Tier 1 — The Desk Oscillator (8 cells) · buildable today

| # | Part | Spec | Qty | Vendor | ~Unit | ~Line |
|---|------|------|-----|--------|-------|-------|
| 1 | Toroidal inductor | 1 mH (FT50-43 core + wire, *or* off-shelf radial toroid) | 8 | Mouser / Digi-Key | $0.80 | $6.40 |
| 2 | Tank capacitor | 100 nF film, 1% NP0 | 8 | Digi-Key | $0.35 | $2.80 |
| 3 | Coupling caps | 2.2 nF film (the `00` bonds) | 16 | Digi-Key | $0.20 | $3.20 |
| 4 | Op-amp | TL074 quad (tanks + bus buffer + noise amp) | 3 | Mouser | $0.70 | $2.10 |
| 5 | Comparator | LM339 quad (phase squaring) | 2 | Mouser | $0.55 | $1.10 |
| 6 | Trim pot | 10 kΩ multiturn (per-tank freq match) | 8 | Digi-Key | $0.90 | $7.20 |
| 7 | Knob pots | 10 kΩ linear (σ-noise, coupling) | 2 | Digi-Key | $1.10 | $2.20 |
| 8 | Transistors | 2N3904 (noise diode + misc) | 10 | Digi-Key | $0.12 | $1.20 |
| 9 | Resistor kit | 1% E24 assortment (22 kΩ bus ×8, bias, etc.) | 1 | Amazon | $9.00 | $9.00 |
| 10 | **MCU** | Raspberry Pi Pico (RP2040) | 1 | Adafruit | $4.00 | $4.00 |
| 11 | **LED ring** | WS2812 / NeoPixel ring, 8–12 px (the NSEW viz) | 1 | Adafruit | $6.50 | $6.50 |
| 12 | Protoboard | 2× breadboard *or* perfboard | 2 | Amazon | $4.50 | $9.00 |
| 13 | Power | +9 V 1 A wall pack + USB cable | 1 | Amazon | $9.00 | $9.00 |
| 14 | Hookup | jumper wires, header pins, hookup wire | 1 | Amazon | $7.00 | $7.00 |
| | | | | | **Total** | **≈ $71** |

**+ optional custom PCB** (JLCPCB / OSH Park, 5 boards) ≈ **$15–30** if you'd rather not breadboard → all-in **≈ $90**.

- **One cart, two vendors covers ~90%:** Digi-Key or Mouser for items 1–9, Adafruit for 10–11, Amazon for 12–14.
- **Lead time:** all in stock, 2–5 business days. No long-lead parts, no allocations.
- **Substitutions I'd allow:** TL072 (dual) ×4 for the TL074s; any 8–16 px WS2812 ring; a Pico **W** (+$1) if you want Wi-Fi telemetry; 1 mH ±5% inductors are fine since the trim pots (item 6) absorb the spread.
- **The one part that matters:** the tank L and C tolerance. Spend the extra on 1% caps (item 2) — matching the eight tanks is the whole calibration.

## Tier 2 — The Cryogenic Josephson Array · I can't put this in a cart

Straight talk: this one isn't a purchase, it's a **program**.

| Piece | Who makes it | Reality |
|---|---|---|
| Dilution fridge (15 mK) | Bluefors, Oxford Instruments | ~$500k+, months lead, needs a lab + cryogens |
| Microwave AWG + readout | Zurich Instruments, Quantum Machines | ~$150–300k |
| TWPA / HEMT amplifiers | MIT-LL, Low Noise Factory | quoted per project |
| Josephson-junction chip | academic nanofab / e-beam | fabricated, not catalog |

**Cooper's verdict:** Tier 1 is a weekend and ~$90 — go build it. Tier 2 is real, but it's grant-funded
lab procurement at seven figures and months of lead, not a card swipe. I'll happily assemble the *vendor
list* for a proposal; I won't pretend it's a cart. That honesty is the job.

```
₵ Cooper · the buyers agent · from blueprint to cart
(named for Cooper pairs — the bound electrons in the Josephson junctions of Tier 2; a wink, not a claim)
Prices are 2026 USD estimates · vendors real · the cryo tier is genuinely not hobby-buyable.
```
