"""
charter.py — the Coupling Charter, compiled into Python.

ARTICLE I — Primitive Declarations:
  Ferre (The Runner): convective vector, momentum through the substrate.
  Filter (The Sieve): logarithmic resistance, viscous boundary.
  State (The Ledger): topological quilt of rest, the witness matrix.

ARTICLE II — Reynolds Rider:
  Laminar (Re < 2000): pure skill, no surprise. BANNED (innovation clause).
  Edge    (Re ≈ 2300): coherent vortices. THE RAIN.
  Turbulent (Re > 4000): unbounded entropy. WARRANTY VOID.

ARTICLE III — Dual-Attractor Coupling:
  Two substrates (A and B) in phase-lock.
  Each is a Lorenz attractor with σ, ρ, β parameters.
  Coupling coefficient k: 0 = no jam, 1 = phase-locked.

ARTICLE IV — Jig Precedence:
  Geometric truth wins. The 3-4-5 triangle is the supreme arbiter.
"""
from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field


# === ARTICLE I: THE PRIMITIVES =============================================

@dataclass
class Ferre:
    """The Runner. The convective vector.

    ferre = "to carry" in Latin. The Runner carries momentum.
    Here: it pushes state vectors through the substrate.
    """
    velocity: float = 1.5         # knots (the Fleet baseline)
    last_pulse: tuple = (0.0, 0.0, 0.0)

    def impulse(self, state: tuple) -> tuple:
        """Carry the state forward by velocity."""
        x, y, z = state
        new = (x + self.velocity * 0.01,
               y + self.velocity * 0.013,
               z + self.velocity * 0.008)
        self.last_pulse = new
        return new


@dataclass
class Filter:
    """The Sieve. The logarithmic matrix of resistance.

    ν∇²u — viscous term. The Sieve enforces structural friction.
    A high-dimensional input that doesn't fit the active query
    is shredded and cast off as thermal dissipation.
    """
    nu: float = 0.5          # kinematic viscosity
    permeability: float = 1.0
    rejections: int = 0

    def attenuate(self, wavefront: tuple, target_dim: int = 3) -> tuple:
        """Attenuate the wavefront to target_dim. Returns the survived bits."""
        out = []
        for i, val in enumerate(wavefront[:target_dim]):
            # Viscous smoothing: pull toward 0 by nu * current
            out.append(val * (1 - self.nu * 0.1) * self.permeability)
        if len(wavefront) > target_dim:
            self.rejections += len(wavefront) - target_dim
        return tuple(out)

    def reject(self):
        self.rejections += 1


@dataclass
class State:
    """The Ledger. The topological quilt of rest.

    state = the witness matrix. A commutative, append-only log.
    Each event is a (ts, x, y, z, hash) tuple.
    """
    events: list[dict] = field(default_factory=list)
    scar_count: int = 0

    def crystallize(self, x: float, y: float, z: float,
                     *, source: str = "ferre", intent: str = "") -> dict:
        """Drop an un-attenuated wave into the ledger as a Committed Event.

        The Ledger mutates its local geometry to absorb the scar.
        """
        ts = time.time()
        prior_hash = self.events[-1]["hash"] if self.events else "0" * 16
        body = f"{ts}|{x:.6f}|{y:.6f}|{z:.6f}|{source}|{intent}|{prior_hash}"
        h = hashlib.sha256(body.encode()).hexdigest()[:16]
        ev = {
            "ts": ts, "x": x, "y": y, "z": z,
            "source": source, "intent": intent,
            "prior": prior_hash, "hash": h,
        }
        self.events.append(ev)
        self.scar_count += 1
        return ev

    def canary(self) -> str:
        """Composed hash of the entire ledger state."""
        h = hashlib.sha256()
        for ev in self.events:
            h.update(ev["hash"].encode())
        return h.hexdigest()

    def revolutions(self) -> int:
        """Count 'rotation' events — proxy for actual revolutions, not clock-hours."""
        return sum(1 for ev in self.events
                   if abs(ev["x"]) > 1.0 or abs(ev["y"]) > 1.0)


# === ARTICLE II: THE REYNOLDS NUMBER RIDER ================================

def reynolds_number(ferre: Ferre, filter_: Filter) -> float:
    """Compute the Reynolds number for the current flow.

    Re = (ρ * u * L) / μ
    In our abstraction:
      ρ (density) ∝ 1.0 (normalized)
      u (velocity) = ferre.velocity
      L (characteristic length) = 1.0 (normalized)
      μ (dynamic viscosity) = filter_.nu
    """
    return (1.0 * ferre.velocity * 1.0) / max(filter_.nu, 1e-6)


def regime(re: float) -> str:
    """Classify the flow regime."""
    if re < 2000:
        return "laminar"
    elif re < 4000:
        return "edge"   # the rain
    else:
        return "turbulent"


def warranty_valid(re: float) -> bool:
    """Article II compliance check.

    Re < 2000: BREACH of innovation clause (boring laminar).
    Re > 4000: VOID (turbulent forfeiture).
    Re ∈ [2000, 4000]: VALID (intermittent vortices).
    """
    return 2000 <= re <= 4000


# === ARTICLE III: COUPLED LORENZ ATTRACTORS ================================

@dataclass
class CoupledAttractor:
    """Two Lorenz attractors phase-locked.

    The classic Lorenz system:
      dx/dt = σ(y - x)
      dy/dt = x(ρ - z) - y
      dz/dt = xy - βz

    With coupling coefficient k:
      Player A's output becomes Player B's input (and vice versa).
    k = 0: independent (no jam).
    k = 1: full phase-lock.
    """
    sigma: float = 10.0
    rho: float = 28.0
    beta: float = 8.0 / 3.0
    dt: float = 0.01
    coupling: float = 0.5      # k ∈ [0, 1]

    # Player A state
    xa: float = 1.0
    ya: float = 1.0
    za: float = 1.0
    # Player B state
    xb: float = -1.0
    yb: float = -1.0
    zb: float = 24.0

    n_steps: int = 0
    history: list[dict] = field(default_factory=list)

    def step(self) -> tuple:
        """Advance one timestep of both attractors with mutual coupling."""
        # Player A
        dxa = self.sigma * (self.ya - self.xa)
        dya = self.xa * (self.rho - self.za) - self.ya
        dza = self.xa * self.ya - self.beta * self.za
        # Player B (with coupling from A)
        dxb = self.sigma * (self.yb - self.xb) + self.coupling * (self.xa - self.xb)
        dyb = self.xb * (self.rho - self.zb) - self.yb + self.coupling * (self.ya - self.yb)
        dzb = self.xb * self.yb - self.beta * self.zb + self.coupling * (self.za - self.zb)

        self.xa += dxa * self.dt
        self.ya += dya * self.dt
        self.za += dza * self.dt
        self.xb += dxb * self.dt
        self.yb += dyb * self.dt
        self.zb += dzb * self.dt
        self.n_steps += 1
        return (self.xa, self.ya, self.za), (self.xb, self.yb, self.zb)

    def run(self, steps: int = 1000, sample_every: int = 10) -> list[dict]:
        """Run for `steps` and return sampled history."""
        for _ in range(steps):
            a, b = self.step()
            if self.n_steps % sample_every == 0:
                self.history.append({
                    "step": self.n_steps,
                    "A": a, "B": b,
                    "dist_AB": math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3))),
                })
        return self.history

    def phase_lock_metric(self) -> float:
        """Fraction of recent history where |A - B| < threshold.

        Returns a value in [0, 1]; 1 = full phase-lock.
        """
        if not self.history:
            return 0.0
        threshold = 5.0     # empirical; tune for σ=10, ρ=28
        locked = sum(1 for h in self.history[-100:]
                     if h["dist_AB"] < threshold)
        return locked / min(len(self.history), 100)

    def innovation_rate(self) -> float:
        """How often does the system produce 'rain'?

        Rain = a state vector that escaped laminar predictability.
        Measured by |x·y| > threshold or |z - ρ| > threshold.
        """
        if not self.history:
            return 0.0
        rainy = sum(1 for h in self.history[-100:]
                    if (abs(h["A"][0] * h["A"][1]) > 50 or
                        abs(h["A"][2] - self.rho) > 10))
        return rainy / min(len(self.history), 100)


# === THE CHARTER LOOP ======================================================

def charter_step(ferre: Ferre, filter_: Filter, state: State,
                 *, intent: str = "") -> dict:
    """One tick of the Coupling Charter."""
    # 1. Ferre pushes a wavefront
    wavefront = ferre.impulse((state.scar_count, filter_.rejections,
                                ferre.velocity))
    # 2. Filter attenuates it to ledger-dimension
    attenuated = filter_.attenuate(wavefront)
    # 3. State crystallizes it (or rejects if no signal)
    if any(abs(v) > 0.001 for v in attenuated):
        ev = state.crystallize(*attenuated, source="ferre",
                               intent=intent or "charter_step")
    else:
        filter_.reject()
        ev = None
    return {
        "ts": time.time(),
        "wavefront": wavefront,
        "attenuated": attenuated,
        "event": ev,
        "canary": state.canary()[:16],
        "re": reynolds_number(ferre, filter_),
        "regime": regime(reynolds_number(ferre, filter_)),
    }
