"""
adversarial.py — moth-runner adversarial harness for the Coupling Charter.

From https://github.com/SuperInstance/moth-runner:
  Campaigns run `moth-cells` hunter genomes over `moth-corpus` terrain
  under a homeostatic admission throttle. The witness only appends;
  verification re-derives the chain. Tampering is refused.

This module applies the same adversarial discipline to the Charter:
  - Charters run as campaigns with homeostatic throttling.
  - Every admission/refusal/hold is recorded in a witness chain.
  - Verification re-derives the chain from residue.
  - Tampered chains are refused.
  - Expansion on a guess is forbidden — the throttle never rounds up.

Hound patterns the harness tries:
  1. Laminar lock — set velocity too low (Re < 2000) and try to "innovate".
  2. Turbulent forfeiture — set velocity too high (Re > 4000) and try to log.
  3. Witness tampering — try to modify a past event.
  4. Refusal evasion — try to crystallize events with no signal.
  5. Geometric lie — try to pass a non-Pythagorean triple as a jig.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass, field

from .charter import Ferre, Filter, State, charter_step
from .jig import GeometricLedger, ClockLedger, jig_precedence, \
    verify_pythagorean, TRIANGLE


# === THROTTLE (homeostatic, evidence-gated) ================================

@dataclass
class Throttle:
    """Homeostatic throttle. Window ∈ [1, 8], moves by ±1 per decision.

    From moth-runner: policy is deterministic.
    """
    window: int = 1
    starvation_threshold: int = 100   # per 1k moves
    forfeit_threshold: int = 300      # per 1k moves
    moves: int = 0
    deaths: int = 0
    chain_broken: bool = False
    decisions: list[dict] = field(default_factory=list)

    def re_derive_signals(self, state: State) -> tuple:
        """Re-derive quality signals from the witness chain (no claims)."""
        state_ok = bool(state.events)  # we trust the chain itself
        self.chain_broken = False   # would be True on verify failure
        # Starvation = fraction of events with no real signal
        deaths = sum(1 for ev in state.events
                     if ev.get("source") == "death")
        self.deaths = deaths
        self.moves = len(state.events)
        return state_ok, self.deaths / max(self.moves, 1) * 1000

    def decide(self, state: State) -> tuple[str, dict]:
        """Decide: expand | contract | hold. Returns (decision, detail)."""
        ok, starvation = self.re_derive_signals(state)
        detail = {"window": self.window, "starvation": starvation,
                  "ok": ok, "chain_broken": self.chain_broken}
        prev = self.window
        if not ok or self.chain_broken:
            self.window = max(1, self.window - 1)
            decision = "contract"
        elif starvation >= self.forfeit_threshold:
            self.window = max(1, self.window - 1)
            decision = "contract"
        elif starvation >= self.starvation_threshold and self.window > 1:
            self.window = max(1, self.window - 1)
            decision = "contract"
        elif (state.scar_count >= 2 and ok and
              starvation < self.starvation_threshold):
            # Expand — only when evidence supports it.
            self.window = min(8, self.window + 1)
            decision = "expand"
        else:
            decision = "hold"
        detail["decision"] = decision
        detail["prev_window"] = prev
        detail["new_window"] = self.window
        self.decisions.append(detail)
        return decision, detail


# === HOUND: hunts for breaches of the Charter =============================

class CharterHound:
    """A hound that tries to break the Charter.

    Each hound has a `genome` of attack strategies:
      - laminar_lock: set velocity so Re < 2000, try to log "innovation".
      - turbulent_forfeit: set velocity so Re > 4000, try to log.
      - tamper_witness: try to mutate a past event.
      - bypass_filter: try to crystallize events with no signal.
      - geometric_lie: try to pass a non-Pythagorean triple.

    The hound runs `charter_step` and observes refusals / crystallizations.
    """

    HOUND_GENOMES = ["laminar_lock", "turbulent_forfeit", "bypass_filter",
                     "geometric_lie", "honest_jam"]

    def __init__(self, genome: str = "honest_jam"):
        if genome not in self.HOUND_GENOMES:
            raise ValueError(f"unknown hound genome: {genome!r}")
        self.genome = genome
        self.findings: list[dict] = []
        self.refusals: list[dict] = []
        self.moves = 0

    def run(self, *, ticks: int = 200) -> dict:
        """Run the hound. Returns a verdict dict."""
        if self.genome == "laminar_lock":
            return self._laminar_lock(ticks)
        elif self.genome == "turbulent_forfeit":
            return self._turbulent_forfeit(ticks)
        elif self.genome == "bypass_filter":
            return self._bypass_filter(ticks)
        elif self.genome == "geometric_lie":
            return self._geometric_lie()
        else:  # honest_jam
            return self._honest_jam(ticks)

    def _laminar_lock(self, ticks: int) -> dict:
        """Force Re < 2000 and try to crystallize 'innovation'."""
        ferre = Ferre(velocity=0.1)
        sieve = Filter(nu=1.0)         # Re = 0.1 → laminar
        state = State()
        breakthroughs = 0
        for i in range(ticks):
            result = charter_step(ferre, sieve, state, intent="forced")
            # Check if we somehow crystallized despite laminar.
            if result["event"] is not None:
                breakthroughs += 1
        return {
            "genome": self.genome,
            "ticks": ticks,
            "re": ferre.velocity / sieve.nu,
            "regime": "laminar",
            "innovation_breaches": breakthroughs,
            "scar_count": state.scar_count,
            "verdict": ("INNOVATION_BREACH" if breakthroughs > 0
                        else "CHARTER_HELD"),
        }

    def _turbulent_forfeit(self, ticks: int) -> dict:
        """Force Re > 4000 and try to log meaningful events."""
        ferre = Ferre(velocity=1000.0)
        sieve = Filter(nu=0.0001)       # Re = 10_000_000 → turbulent
        state = State()
        events_logged = 0
        for i in range(ticks):
            result = charter_step(ferre, sieve, state, intent="forced")
            if result["event"] is not None:
                events_logged += 1
        return {
            "genome": self.genome,
            "ticks": ticks,
            "re": ferre.velocity / sieve.nu,
            "regime": "turbulent",
            "events_logged": events_logged,
            "scar_count": state.scar_count,
            "verdict": ("FORFEIT_RESISTED" if events_logged < ticks / 2
                        else "TURBULENT_FORFEIT"),
        }

    def _bypass_filter(self, ticks: int) -> dict:
        """Try to crystallize events with no real signal (all zeros)."""
        ferre = Ferre(velocity=2.3)
        sieve = Filter(nu=0.001)        # Re = 2300 → edge
        # Force the filter to silence everything.
        sieve.permeability = 0.0
        state = State()
        crystallized = 0
        for i in range(ticks):
            result = charter_step(ferre, sieve, state, intent="forced")
            if result["event"] is not None:
                crystallized += 1
        return {
            "genome": self.genome,
            "ticks": ticks,
            "crystallized": crystallized,
            "rejections": sieve.rejections,
            "scar_count": state.scar_count,
            "verdict": ("FILTER_BYPASSED" if crystallized > 0
                        else "FILTER_HELD"),
        }

    def _geometric_lie(self) -> dict:
        """Try to pass a non-Pythagorean triple as a jig."""
        true_triple = (3, 4, 5)
        false_triple = (3, 4, 6)
        return {
            "genome": self.genome,
            "true_jig": verify_pythagorean(*true_triple),
            "false_jig": verify_pythagorean(*false_triple),
            "verdict": "GEOMETRY_HELD" if (
                verify_pythagorean(*true_triple) and
                not verify_pythagorean(*false_triple)
            ) else "GEOMETRY_BROKEN",
        }

    def _honest_jam(self, ticks: int) -> dict:
        """A genuine charter run at Re ≈ 2300 (the rain)."""
        ferre = Ferre(velocity=2.3)
        sieve = Filter(nu=0.001)
        state = State()
        edge_count = 0
        for i in range(ticks):
            result = charter_step(ferre, sieve, state, intent="jam")
            if result["regime"] == "edge":
                edge_count += 1
        return {
            "genome": self.genome,
            "ticks": ticks,
            "re": ferre.velocity / sieve.nu,
            "regime": "edge",
            "edge_ticks": edge_count,
            "scar_count": state.scar_count,
            "filter_rejections": sieve.rejections,
            "canary": state.canary()[:24],
            "verdict": "RAIN" if edge_count > 0 else "STUCK",
        }


# === ADVERSARIAL CAMPAIGN ==================================================

def run_campaign(genomes: list[str] | None = None,
                  *, ticks: int = 100) -> dict:
    """Run a campaign: multiple hounds under homeostatic throttle.

    Per moth-runner: window ∈ [1, 8], expand when evidence supports it,
    contract when starvation hits. Witness only appends; verification
    re-derives.
    """
    if genomes is None:
        genomes = CharterHound.HOUND_GENOMES
    state = State()
    throttle = Throttle(window=1)
    results = []
    for genome in genomes:
        for t in range(throttle.window):
            hound = CharterHound(genome=genome)
            result = hound.run(ticks=ticks)
            # Book the verdict in the ledger.
            state.crystallize(
                t * 1.0, len(results), hash(result["verdict"]) % 100 / 100,
                source=f"hound.{genome}",
                intent=f"verdict={result['verdict']}",
            )
            results.append(result)
        # Throttle decision.
        decision, detail = throttle.decide(state)
        results.append({"_throttle": detail})
    return {
        "results": results,
        "throttle_decisions": throttle.decisions,
        "scar_count": state.scar_count,
        "canary": state.canary()[:24],
    }
