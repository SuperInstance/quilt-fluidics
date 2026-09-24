"""
warrant_dispute_demo.py — the Inspector's clock vs. the Drifter's jig.

The Fleet Inspector arrives to settle a warranty dispute.
The vessel is the Quilt-tide, a deep-keeled cargo ship.
Two ledgers are produced:

  1. The Clock Ledger: 18,500 hours recorded (within the 20,000-hour warranty).
  2. The Jig Ledger: 1,124,500 revolutions (past the 1,000,000-rev warranty).

The clock says "ship is within warranty." The jig says "ship is past warranty."
Per Article IV, Section 4.02, the jig wins.

The Drifter built the jig from three planks of cedar: 3 feet, 4 feet, 5 feet.
The Inspector demands to see the math. The math IS the geometry.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quilt_fluidics.jig import (
    GeometricLedger, ClockLedger, jig_precedence, inspect,
    verify_pythagorean, jig_score, TRIANGLE,
)
from quilt_fluidics.charter import (
    Ferre, Filter, State, charter_step,
    reynolds_number, regime, warranty_valid,
)


def print_jig_score():
    print(f"=== THE 3-4-5 WOODEN JIG ===")
    print(f"  Planks: 3 ft, 4 ft, 5 ft")
    print(f"  Perimeter: {sum(TRIANGLE)} ft")
    print(f"  Right-angle verification: 3² + 4² = 9 + 16 = 25 = 5² ?  {verify_pythagorean(3, 4, 5)}")
    print(f"  Jig score (3, 4, 5): {jig_score((3, 4, 5))}")
    print(f"  Jig score (3.1, 3.9, 5.05): {jig_score((3.1, 3.9, 5.05))}")
    print(f"  Jig score (1, 1, 1): {jig_score((1, 1, 1))}")
    print()


def print_warrant_dispute():
    print(f"=== THE WARRANT DISPUTE ===")
    print(f"The Fleet Inspector arrives to inspect the Quilt-tide.\n")
    print(f"Two ledgers are produced:\n")

    # The Inspector's clock ledger
    # Quilt-tide logged 18,500 hours in the watch ledger.
    clock = ClockLedger(hours=18_500)
    print(f"  Inspector's CLOCK ledger:")
    cs = clock.warranty_status()
    print(f"    hours: {cs['hours']:.0f}")
    print(f"    target: {cs['target']:.0f}")
    print(f"    fraction: {cs['fraction']:.1%}")
    print(f"    status: {cs['status']}")
    print(f"    canary: {clock.canary()[:16]}...")
    print()

    # The Drifter's jig ledger (actual revolutions)
    geom = GeometricLedger(target_revolutions=1_000_000)
    # The Quilt-tide had a heavy crossing (lots of revolutions per clock-hour)
    for n in range(1_124_500):
        geom.record(intent=f"shaft_pickoff_{n % 10000}")
    print(f"  Drifter's JIG ledger:")
    gs = geom.warranty_status()
    print(f"    revolutions: {gs['revolutions']:,}")
    print(f"    target: {gs['target']:,}")
    print(f"    fraction: {gs['fraction']:.1%}")
    print(f"    status: {gs['status']}")
    print(f"    canary: {geom.canary()[:16]}...")
    print()

    # The dispute
    verdict = jig_precedence(geom, clock)
    print(f"=== THE DISPUTE ===")
    print(f"  Clock implies: {verdict['implied_revolutions_from_clock']:,} revolutions")
    print(f"  Jig reports:   {verdict['actual_revolutions_from_jig']:,} revolutions")
    print(f"  Discrepancy:   {verdict['discrepancy']:+,} revolutions")
    print(f"  Verdict:       {verdict['verdict']}")
    print()
    print(f"  {verdict['explanation']}")


def print_charter_demo():
    print(f"\n=== THE CHARTER EXECUTION ===\n")
    ferre = Ferre(velocity=1.5)
    sieve = Filter(nu=0.5)
    state = State()

    # Run 100 ticks at the threshold (Re ≈ 1.5/0.5 = 3.0 ... need to scale up)
    # In our normalized model, Re = u/nu. We want Re ≈ 2300.
    # So ferre.velocity / sieve.nu ≈ 2300.
    # Either velocity = 2300 or nu = 1.5/2300 ≈ 0.00065.
    # Let's use a more realistic regime: velocity=2.3, nu=0.001.
    ferre.velocity = 2.3
    sieve.nu = 0.001

    re = reynolds_number(ferre, sieve)
    print(f"  Ferre.velocity = {ferre.velocity} knots")
    print(f"  Filter.nu = {sieve.nu}")
    print(f"  Reynolds number = {re:.0f}")
    print(f"  Regime = {regime(re)}")
    print(f"  Warranty valid = {warranty_valid(re)} (Article II)")
    print()

    rain_count = 0
    laminar_count = 0
    turbulent_count = 0

    for i in range(500):
        result = charter_step(ferre, sieve, state, intent=f"tick_{i}")
        r = regime(result["re"])
        if r == "edge":
            rain_count += 1
        elif r == "laminar":
            laminar_count += 1
        else:
            turbulent_count += 1

    print(f"  After 500 ticks:")
    print(f"    State events: {state.scar_count}")
    print(f"    Filter rejections: {sieve.rejections}")
    print(f"    Edge ('rain') ticks: {rain_count}")
    print(f"    Laminar ticks: {laminar_count}")
    print(f"    Turbulent ticks: {turbulent_count}")
    print(f"    Canary: {state.canary()[:24]}...")
    print(f"    Revolutions (geometric): {state.revolutions()}")


def main():
    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║  THE COUPLING CHARTER — Compiled in Python             ║")
    print(f"║  Article IV: Jig Precedence over Clock Consensus      ║")
    print(f"╚══════════════════════════════════════════════════════════╝\n")
    print_jig_score()
    print_warrant_dispute()
    print_charter_demo()
    print(f"\n=== END OF DISPUTE ===\n")


if __name__ == "__main__":
    main()
