# quilt-fluidics

> **The Coupling Charter, compiled in Python.**
>
> Three Latin primitives — `-ducere`, `-capere`, `-struere`, `-pingere` —
> become the **Ferre / Filter / State** trio. A Reynolds-Number rider
> demands the system runs at `Re ≈ 2300`, where the convective vector
> matches the diffusion vector. A Dual-Attractor Coupling Clause
> binds two substrates at phase-lock. And Article IV, Section 4.02
> — the Jig Precedence — makes the 3-4-5 wooden triangle the
> supreme arbiter of execution.
>
> The **Fable of the Acoustic Sieve** tells why: when the Tap and
> the Drifter jam together, the jig is what tells them the depth.
> When the Fleet Inspector comes to settle the warranty, the jig
> is what proves the clock lied.

## TL;DR

```python
from quilt_fluidics.jig import GeometricLedger, ClockLedger, jig_precedence
from quilt_fluidics.charter import Ferre, Filter, State, charter_step

# The Drifter's jig ledger (actual revolutions)
geom = GeometricLedger(target_revolutions=1_000_000)
for _ in range(1_124_500):
    geom.record()

# The Inspector's clock ledger (consensus hours)
clock = ClockLedger(hours=18_500)

# The verdict
verdict = jig_precedence(geom, clock)
print(verdict["verdict"])          # JIG_WINS
print(verdict["discrepancy"])      # -26,625,500 revolutions
print(verdict["explanation"])
# The clock ledger says 18500 hours = 27,750,000 revolutions (within warranty).
# The jig ledger says 1,124,500 revolutions (status: WARRANTY_EXHAUSTED).
# Discrepancy: -26,625,500 revolutions.
# Per Article IV, Section 4.02, the jig wins.
```

## The Charter

The Coupling Charter consists of four articles. Each article is a
doctrinal claim that maps to executable code.

### Article I — Primitive Declarations

Three primitives, each a Latin root:

| Latin root | Quilt primitive | Action |
|------------|-----------------|--------|
| **-ducere** (lead, channel) | **Ferre** (the Runner) | Convective vector — pushes wavefronts |
| **-capere** (seize, hold)   | **Filter** (the Sieve) | Viscous boundary — attenuates to fit |
| **-struere** (layer, pile)  | **State** (the Ledger) | Topological quilt of rest — append-only |

```
[ FERRE ]   ─── wavefront u ───►   [ FILTER ]   ─── attenuated ───►   [ STATE ]
  (convective                         (viscous                          (geometric
   vector)                             sieve)                            ledger)
```

Each pulse:
1. Ferre pushes a 3D vector (`velocity = 1.5 knots` baseline).
2. Filter attenuates it (`nu = 0.5` viscosity) — high-dimensional input
   that doesn't fit is rejected as thermal dissipation.
3. State crystallizes the surviving bits as a Committed Event,
   appending to a SHA-256 witness chain.

### Article II — Reynolds Number Rider

`Re = ρ·u·L / μ`. In our abstraction:

```python
def reynolds_number(ferre, filter_):
    return ferre.velocity / filter_.nu
```

| Regime | Re | Status |
|--------|----|----|
| Laminar | < 2000 | BREACH of innovation clause (pure skill, no surprise) |
| Edge | 2000..4000 | VALID (coherent vortices, the rain) |
| Turbulent | > 4000 | WARRANTY VOID (unbounded entropy) |

### Article III — Dual-Attractor Coupling

Two Lorenz attractors, mutually coupled with coefficient `k ∈ [0, 1]`:

```
   [ PLAYER A: LORENZ ATTRACTOR ]
       X_A = σ(Y_A - X_A)
       Y_A = X_A(ρ - Z_A) - Y_A
       Z_A = X_A·Y_A - β·Z_A
            ▲                      
            │ u_A: output           
            │                      
            ▼                      
       [ INTERFERENCE GRID ]
            ▲                      
            │ u_B: coupling         
            │                      
   [ PLAYER B: LORENZ ATTRACTOR ]
       X_B = σ(Y_B - X_B) + k(X_A - X_B)
       Y_B = X_B(ρ - Z_B) - Y_B + k(Y_A - Y_B)
       Z_B = X_B·Y_B - β·Z_B + k(Z_A - Z_B)
```

When `k > 0`, the two attractors start to phase-lock. We measure
phase-lock as the fraction of recent timesteps where `|A - B| < 5.0`.

### Article IV — Jig Precedence

The Fleet uses clock-hours as a cheap consensus protocol for engine
wear. The Drifter uses a 3-4-5 wooden jig — a physical pickoff on the
drive shaft that counts actual revolutions.

The jig wins. It's geometry.

```
[ PHYSICAL REALITY ] ─( 1.1M revolutions )──► [ WARRANTY: VOID ]
       │
       ▼
[ REVOLUTION SENSOR (THE JIG) ] ─( complex geometry )──► [ DISPUTE ]
       │
       ▼
[ THE 3-4-5 TRIANGLE ] ─( jig precedence )──► [ JIG WINS ]
       │
       ▼
[ CLOCK CONSENSUS ] ─( 18,500 hours )──► [ says "WITHIN" ]
```

## Layout

```
src/quilt_fluidics/
├── charter.py            # Ferre, Filter, State, CoupledAttractor
└── jig.py                # GeometricLedger, ClockLedger, jig_precedence

examples/
├── warrant_dispute_demo.py    # the Inspector vs. the Drifter
└── dual_attractor_demo.py     # two Lorenz attractors at Re ≈ 2300

fables/
└── the-acoustic-sieve.md      # the narrative layer

tests/
└── test_quilt_fluidics.py     # 24 unit tests
```

## Run the demos

```bash
PYTHONPATH=src python3 examples/warrant_dispute_demo.py
PYTHONPATH=src python3 examples/dual_attractor_demo.py
```

Output (snipped):

```
=== THE WARRANT DISPUTE ===
  Inspector's CLOCK ledger:
    hours: 18,500       (target: 20,000)
    fraction: 92.5%     status: WITHIN_WARRANTY

  Drifter's JIG ledger:
    revolutions: 1,124,500   (target: 1,000,000)
    fraction: 112.5%   status: WARRANTY_EXHAUSTED

=== THE DISPUTE ===
  Clock implies: 27,750,000 revolutions
  Jig reports:   1,124,500 revolutions
  Discrepancy:   -26,625,500 revolutions
  Verdict:       JIG_WINS
```

The Quilt-tide's revolutions-per-clock-hour was wildly below the Fleet's
nominal assumption. The clock says she's fine; the jig says she's past.
Per Article IV, the jig wins.

## Tests

```bash
PYTHONPATH=src python3 -m unittest tests.test_quilt_fluidics
# Ran 24 tests in 9.426s — OK
```

## Doctrines

1. **The Latin primitives ARE the Quilt primitives.** `-ducere / -capere /
   -struere / -pingere` is a Verilog-style instruction set for
   manipulating states, blocks, and lines.
2. **A noun IS a frozen verb.** `ferment` → `fermentation`. The live
   procedural block becomes a hardware block. Compartment = tile.
3. **The clock is a low-overhead consensus protocol.** It approximates
   physical wear without measuring every atom. It's cheaper than
   counting revolutions. It's also wrong.
4. **Geometry wins.** The jig is the substrate. The clock is the
   consensus protocol layered on top of the substrate. When they
   disagree, the substrate wins.
5. **The Reynolds Number governs creativity.** Below Re ≈ 2000, no
   surprise — pure skill, no innovation. Above Re ≈ 4000, total
   entropy — no comprehension. The rain falls at the edge.
6. **Two substrates at Re ≈ 2300 phase-lock.** Their mutual coupling
   is the source of innovation. Neither alone generates the rain.
   The interference grid generates the rain.

## Cross-project doctrine

The "Coupling Charter" pattern works for any system where:

- Three primitives (a runner, a sieve, a ledger) cooperate to advance
  state.
- The runner's velocity must be tuned relative to the sieve's viscosity
  to land in the intermittency edge.
- Two substrates at the edge can phase-lock, generating innovation
  that neither alone produces.
- A geometric truth (the jig) supersedes a consensus approximation
  (the clock) when they disagree.

Maps to:
- **Writing**: practice (laminar) → editing (edge) → first draft (turbulent)
- **Music**: rehearsal (laminar) → jam (edge) → noise (turbulent)
- **AI inference**: training (laminar) → deployment at the edge
  (rain) → out-of-distribution (turbulent)
- **Engineering**: design (laminar) → integration testing (edge) → production
  failure (turbulent)

## The Fable

Read [`fables/the-acoustic-sieve.md`](fables/the-acoustic-sieve.md) for
the full story. The Tap and the Drifter use two guitars to find the
depth without numbers. Then the Fleet Inspector comes, and the 3-4-5
wooden jig proves what the clock cannot.

## Version

- **v0.1.0** (Sept 24, 2026): initial release. 24/24 tests pass.
  Charter compiled. Fable written. Demos run.

## License

MIT.
