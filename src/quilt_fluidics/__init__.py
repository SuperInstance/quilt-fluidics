"""quilt-fluidics — the Coupling Charter, compiled.

ARTICLE I — Primitives:  Ferre (Runner) / Filter (Sieve) / State (Ledger).
ARTICLE II — Reynolds Rider:  laminar / edge / turbulent regimes.
ARTICLE II-bis — Reynolds-as-Knob:  per-layer Re via LayeredCharter.
ARTICLE III — Coupling:  two Lorenz attractors phase-locked at k ∈ [0,1].
ARTICLE IV — Jig:  geometric truth (a²+b²=c²) supersedes clock consensus.
"""
from .charter import (
    Ferre, Filter, State,
    reynolds_number, regime, warranty_valid,
    CoupledAttractor,
    charter_step,
    LayeredCharter,
)
from .jig import (
    TRIANGLE, verify_pythagorean, jig_score, inspect,
    GeometricLedger, ClockLedger, jig_precedence,
)
from .adversarial import (
    Throttle, CharterHound, run_campaign,
)
from .homeostatic import SilenceDetector, homeostatic_step, homeostatic_run


__version__ = "0.3.0"


__all__ = [
    # Article I
    "Ferre", "Filter", "State",
    # Article II
    "reynolds_number", "regime", "warranty_valid",
    # Article II-bis (Fold integration)
    "LayeredCharter",
    # Article III
    "CoupledAttractor",
    # Article IV + charter loop
    "charter_step",
    # Jig
    "TRIANGLE", "verify_pythagorean", "jig_score", "inspect",
    "GeometricLedger", "ClockLedger", "jig_precedence",
    # Adversarial (moth-runner integration)
    "Throttle", "CharterHound",
    "run_campaign",
    # Homeostatic (jeviter integration)
    "SilenceDetector", "homeostatic_step", "homeostatic_run",
]
