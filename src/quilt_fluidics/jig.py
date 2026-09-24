"""
jig.py — the 3-4-5 wooden jig and the geometric ledger.

ARTICLE IV, Section 4.02: Jig Precedence.

"The sound of the drum off the tap of reality remains the supreme arbiter of execution."

The jig is the geometric truth — a 3-4-5 right triangle. It measures
revolutions (kinematic cycles) directly, not via clock-hours. The
Inspector uses clock-hours (the cheap consensus protocol); the Drifter
uses the jig (the geometric substrate).

This module lets you:
  - Build a geometric ledger from actual revolutions.
  - Build a clock-based ledger from hour counts.
  - Compare them and surface the discrepancy.
  - Decide which one wins under Article IV.
"""
from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field


# The Fleet's canonical 3-4-5 triangle (units in feet).
TRIANGLE = (3.0, 4.0, 5.0)
TRIANGLE_PERIMETER = sum(TRIANGLE)
TRIANGLE_AREA = (3.0 * 4.0) / 2.0


def verify_pythagorean(a: float, b: float, c: float, *, tol: float = 1e-6) -> bool:
    """The jig's only contract: a² + b² = c²."""
    return abs(a * a + b * b - c * c) < tol


def jig_score(observed: tuple, reference: tuple = TRIANGLE,
              *, tol: float = 0.1) -> float:
    """How well does the observed triple match the canonical 3-4-5?

    Returns 1.0 if it's a perfect 3-4-5 (within tolerance); 0.0 if it's
    totally unlike. Smooth gradient in between.
    """
    # Normalize so the largest value is 1.0
    obs_max = max(observed)
    ref_max = max(reference)
    obs_n = tuple(v * ref_max / obs_max for v in observed)
    # Distance from the reference
    dist = math.sqrt(sum((obs_n[i] - reference[i]) ** 2 for i in range(3)))
    return max(0.0, 1.0 - dist / tol)


@dataclass
class GeometricLedger:
    """The Drifter's ledger: actual revolutions (geometric truth).

    A revolution = one full rotation of a vessel's drive shaft,
    counted by a physical pickoff on the shaft (the jig's tap).
    """
    revolutions: list[dict] = field(default_factory=list)
    target_revolutions: int = 1_000_000  # 1M revolutions = warranty baseline

    def record(self, *, source: str = "jig_tap", intent: str = "") -> dict:
        rev = {
            "n": len(self.revolutions) + 1,
            "ts": time.time(),
            "source": source,
            "intent": intent,
            "hash": hashlib.sha256(
                f"{len(self.revolutions)+1}|{source}|{intent}|{time.time()}".encode()
            ).hexdigest()[:16],
        }
        self.revolutions.append(rev)
        return rev

    def total(self) -> int:
        return len(self.revolutions)

    def canary(self) -> str:
        h = hashlib.sha256()
        for rev in self.revolutions:
            h.update(rev["hash"].encode())
        return h.hexdigest()

    def warranty_status(self) -> dict:
        total = self.total()
        return {
            "revolutions": total,
            "target": self.target_revolutions,
            "fraction": total / self.target_revolutions,
            "warranty_remaining": max(0, self.target_revolutions - total),
            "status": "WITHIN_WARRANTY" if total < self.target_revolutions
                      else "WARRANTY_EXHAUSTED",
        }


@dataclass
class ClockLedger:
    """The Inspector's ledger: clock-hours (consensus truth).

    A clock-hour is what the wall clock said. Cheap, but lossy:
    two engines running the same clock-hours can have wildly
    different revolution counts.
    """
    hours: float = 0.0
    hours_per_revolution: float = 1.0 / 1500.0   # nominal, but variable!
    target_hours: float = 20_000.0                # Fleet warranty baseline
    records: list[dict] = field(default_factory=list)

    def tick(self, hours: float = 1.0) -> dict:
        self.hours += hours
        rec = {
            "ts": time.time(),
            "hours": self.hours,
            "hash": hashlib.sha256(
                f"{self.hours}|{time.time()}".encode()
            ).hexdigest()[:16],
        }
        self.records.append(rec)
        return rec

    def canary(self) -> str:
        h = hashlib.sha256()
        for r in self.records:
            h.update(r["hash"].encode())
        return h.hexdigest()

    def warranty_status(self) -> dict:
        return {
            "hours": self.hours,
            "target": self.target_hours,
            "fraction": self.hours / self.target_hours,
            "warranty_remaining": max(0, self.target_hours - self.hours),
            "status": "WITHIN_WARRANTY" if self.hours < self.target_hours
                      else "WARRANTY_EXHAUSTED",
        }

    def implied_revolutions(self) -> int:
        return int(self.hours / self.hours_per_revolution)


# === ARTICLE IV: THE JIG PRECEDENCE =======================================

def jig_precedence(geom: GeometricLedger, clock: ClockLedger) -> dict:
    """Apply Article IV: Jig wins over clock when they disagree.

    The discrepancy arises because clock-hours and revolutions are
    not the same metric. A vessel running in heavy seas makes more
    revolutions per clock-hour than one in calm water.
    """
    g_status = geom.warranty_status()
    c_status = clock.warranty_status()
    implied = clock.implied_revolutions()
    actual = geom.total()
    discrepancy = actual - implied
    return {
        "geometric": g_status,
        "clock": c_status,
        "implied_revolutions_from_clock": implied,
        "actual_revolutions_from_jig": actual,
        "discrepancy": discrepancy,
        "jig_says_warranty": g_status["status"],
        "clock_says_warranty": c_status["status"],
        "verdict": (
            "JIG_WINS" if discrepancy != 0 else "CLOCK_AND_JIG_AGREE"
        ),
        "explanation": (
            f"The clock ledger says {clock.hours:.0f} hours = "
            f"{implied:,} revolutions (within warranty: {c_status['status']}). "
            f"The jig ledger says {actual:,} revolutions "
            f"(status: {g_status['status']}). "
            f"Discrepancy: {discrepancy:+,} revolutions. "
            f"Per Article IV, Section 4.02, the jig wins."
        ),
    }


# === THE FLEET INSPECTION ================================================

def inspect(*, hours_recorded: float, revolutions_recorded: int,
            target_hours: float = 20_000,
            target_revolutions: int = 1_000_000) -> dict:
    """A single-shot inspection. Returns the verdict and the discrepancy."""
    clock = ClockLedger(hours=hours_recorded, target_hours=target_hours)
    geom = GeometricLedger(target_revolutions=target_revolutions)
    # Pre-populate from inputs.
    for _ in range(revolutions_recorded):
        geom.record(intent="shaft_pickoff")
    return jig_precedence(geom, clock)
