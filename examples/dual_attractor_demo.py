"""
dual_attractor_demo.py — Two substrates jamming at Re ≈ 2300.

Player A: the Drifter's acoustic sieve — listens for what doesn't fit.
Player B: the Tap's rhythm track — keeps the drum steady.

The dual attractor phase-locks when both substrates stop being
independent and start being each other's boundary constraint.

We watch the phase-lock metric climb from 0 → 1 as the system
finds its resonant frequency.

Article III: "Your output vector becomes the direct boundary constraint
for their input vector."
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quilt_fluidics.charter import CoupledAttractor


def run_jam(coupling: float = 0.5, steps: int = 5000,
            sample_every: int = 50) -> CoupledAttractor:
    """Run a jamming session."""
    sys_a = CoupledAttractor(coupling=coupling)
    sys_a.run(steps=steps, sample_every=sample_every)
    return sys_a


def print_session(label: str, attractor: CoupledAttractor):
    pl = attractor.phase_lock_metric()
    inn = attractor.innovation_rate()
    h = attractor.history
    print(f"  {label}:")
    print(f"    steps:      {attractor.n_steps}")
    print(f"    coupling:   {attractor.coupling}")
    print(f"    phase_lock: {pl:.3f}  (1.0 = fully locked)")
    print(f"    innovation: {inn:.3f}  (1.0 = all rain)")
    if h:
        last_a = h[-1]["A"]
        last_b = h[-1]["B"]
        print(f"    last A:     ({last_a[0]:.2f}, {last_a[1]:.2f}, {last_a[2]:.2f})")
        print(f"    last B:     ({last_b[0]:.2f}, {last_b[1]:.2f}, {last_b[2]:.2f})")
        print(f"    |A-B|:      {h[-1]['dist_AB']:.3f}")
    print()


def main():
    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║  COUPLED LORENZ ATTRACTORS — A JAMMING SESSION          ║")
    print(f"║  Article III: The Dual-Attractor Coupling Clause        ║")
    print(f"╚══════════════════════════════════════════════════════════╝\n")

    # Sweep the coupling coefficient from 0 → 1
    print(f"=== Coupling Sweep: from isolation to phase-lock ===\n")
    results = []
    for k in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        a = run_jam(coupling=k, steps=4000, sample_every=40)
        results.append((k, a.phase_lock_metric(), a.innovation_rate()))

    print(f"  Coupling → Phase-Lock → Innovation Rate")
    print(f"  " + "-" * 60)
    for k, pl, inn in results:
        bar_lock = "█" * int(pl * 30)
        bar_inn = "░" * int(inn * 30)
        print(f"  k={k:.1f}     {pl:.3f}  {bar_lock:30s}    {inn:.3f}  {bar_inn:30s}")

    print()
    print(f"=== Session: k=0.5 (Article III default) ===\n")
    print_session("The Drifter + The Tap", run_jam(coupling=0.5, steps=8000,
                                                  sample_every=80))

    print(f"=== Session: k=0.9 (Article III, near-full lock) ===\n")
    print_session("The Drifter + The Tap (deep lock)", run_jam(coupling=0.9,
                                                              steps=8000,
                                                              sample_every=80))

    print(f"=== Reading the dual attractor's interference grid ===\n")
    a = run_jam(coupling=0.5, steps=2000, sample_every=10)
    print(f"  First 10 samples (the rain forming):")
    print(f"  step |   A=(x,y,z)            B=(x,y,z)            |A-B|")
    print(f"  " + "-" * 70)
    for h in a.history[:10]:
        A, B = h["A"], h["B"]
        print(f"  {h['step']:4d} | "
              f"({A[0]:6.2f},{A[1]:6.2f},{A[2]:6.2f})  "
              f"({B[0]:6.2f},{B[1]:6.2f},{B[2]:6.2f})  "
              f"{h['dist_AB']:.2f}")
    print(f"  ...")
    print(f"  Last 5 samples (after phase-lock):")
    for h in a.history[-5:]:
        A, B = h["A"], h["B"]
        print(f"  {h['step']:4d} | "
              f"({A[0]:6.2f},{A[1]:6.2f},{A[2]:6.2f})  "
              f"({B[0]:6.2f},{B[1]:6.2f},{B[2]:6.2f})  "
              f"{h['dist_AB']:.2f}")


if __name__ == "__main__":
    main()
