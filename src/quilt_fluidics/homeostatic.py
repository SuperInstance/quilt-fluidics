"""
homeostatic.py — jeviter silence-detector for the Charter.

From https://github.com/SuperInstance/jeviter:
  Don't poll. Rest, and react.

  - No belief, no refusal. The first pull seeds the boundary.
  - Every silence is booked. A silence you cannot audit is
    indistinguishable from a hang.
  - The threshold is alive. Dynamic: mean + k·σ over admitted gains.
  - The ratchet: a world oscillating at any fixed amplitude is silenced
    after exactly one admission — adversarial resonance is impossible.

This module applies homeostatic iteration to the Charter's witness chain:
if the chain is silent (no events for N ticks), emit a REFUSAL row.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class SilenceDetector:
    """Detect when the Charter is silent (stuck).

    Per jeviter: silence is booked, never invisible. A silence you
    cannot audit is indistinguishable from a hang.
    """
    silence_threshold_ticks: int = 5
    last_event_ts: float = 0.0
    silence_receipts: list[dict] = field(default_factory=list)
    n_polls: int = 0
    n_admissions: int = 0
    n_silences: int = 0

    def poll(self, *, state_has_events: bool) -> dict:
        """One poll cycle. Returns a receipt describing the result."""
        self.n_polls += 1
        if state_has_events:
            self.last_event_ts = time.time()
            self.n_admissions += 1
            return {
                "event": "admission",
                "n_polls": self.n_polls,
                "n_admissions": self.n_admissions,
                "n_silences": self.n_silences,
            }
        # Check if we've been silent long enough to emit a refusal.
        if self.last_event_ts == 0.0:
            # No events ever — initialize.
            self.last_event_ts = time.time()
            return {"event": "seed", "n_polls": self.n_polls,
                    "note": "first poll seeds the boundary"}
        elapsed = time.time() - self.last_event_ts
        if elapsed > self.silence_threshold_ticks:
            self.n_silences += 1
            receipt = {
                "event": "silence_refusal",
                "elapsed": elapsed,
                "n_silences": self.n_silences,
                "n_polls": self.n_polls,
                "ts": time.time(),
            }
            receipt["hash"] = hashlib.sha256(
                f"{receipt['ts']}|silence|{self.n_silences}".encode()
            ).hexdigest()[:16]
            self.silence_receipts.append(receipt)
            return receipt
        return {"event": "silence_pending", "elapsed": elapsed,
                "n_polls": self.n_polls}


def homeostatic_step(state, detector: SilenceDetector) -> dict:
    """Run a single homeostatic poll on the Charter state."""
    has_events = bool(state.events)
    return detector.poll(state_has_events=has_events)


def homeostatic_run(state, *, ticks: int = 20,
                    threshold: int = 5) -> dict:
    """Run a series of polls on the Charter state. Book every silence."""
    detector = SilenceDetector(silence_threshold_ticks=threshold)
    receipts = []
    for i in range(ticks):
        r = homeostatic_step(state, detector)
        receipts.append(r)
    return {
        "n_polls": detector.n_polls,
        "n_admissions": detector.n_admissions,
        "n_silences": detector.n_silences,
        "silence_receipts": detector.silence_receipts,
        "receipts": receipts,
    }
