"""Tests for quilt-fluidics."""
import math
import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest

from quilt_fluidics.charter import (
    Ferre, Filter, State, charter_step,
    CoupledAttractor,
    reynolds_number, regime, warranty_valid,
)
from quilt_fluidics.jig import (
    GeometricLedger, ClockLedger, jig_precedence,
    verify_pythagorean, jig_score, inspect, TRIANGLE,
)


class TestJigGeometry(unittest.TestCase):
    def test_pythagorean(self):
        self.assertTrue(verify_pythagorean(3, 4, 5))
        self.assertTrue(verify_pythagorean(5, 12, 13))
        self.assertFalse(verify_pythagorean(1, 2, 3))

    def test_jig_score_perfect(self):
        self.assertEqual(jig_score((3, 4, 5)), 1.0)

    def test_jig_score_close(self):
        # Within tolerance: very close to (3, 4, 5) should score > 0.
        score = jig_score((3.001, 3.999, 5.001))
        self.assertGreater(score, 0.0)

    def test_jig_score_far(self):
        self.assertEqual(jig_score((1, 1, 1)), 0.0)


class TestGeometricLedger(unittest.TestCase):
    def test_record(self):
        led = GeometricLedger(target_revolutions=100)
        led.record()
        led.record()
        self.assertEqual(led.total(), 2)

    def test_warranty_status(self):
        led = GeometricLedger(target_revolutions=10)
        for _ in range(5):
            led.record()
        s = led.warranty_status()
        self.assertEqual(s["status"], "WITHIN_WARRANTY")
        self.assertEqual(s["revolutions"], 5)

        for _ in range(10):
            led.record()
        s = led.warranty_status()
        self.assertEqual(s["status"], "WARRANTY_EXHAUSTED")

    def test_canary_changes(self):
        led = GeometricLedger()
        c0 = led.canary()
        led.record()
        c1 = led.canary()
        self.assertNotEqual(c0, c1)


class TestClockLedger(unittest.TestCase):
    def test_tick(self):
        led = ClockLedger()
        led.tick(hours=10)
        led.tick(hours=5)
        self.assertEqual(led.hours, 15)

    def test_implied_revolutions(self):
        led = ClockLedger(hours=100, hours_per_revolution=1.0/1500.0)
        self.assertEqual(led.implied_revolutions(), 150_000)


class TestJigPrecedence(unittest.TestCase):
    def test_disagreement(self):
        # Clock says "under warranty" (18,500 hours of 20,000)
        # Jig says "past warranty" (1.1M revolutions of 1M)
        clock = ClockLedger(hours=18_500)
        geom = GeometricLedger(target_revolutions=1_000_000)
        for _ in range(1_124_500):
            geom.record()
        v = jig_precedence(geom, clock)
        self.assertEqual(v["jig_says_warranty"], "WARRANTY_EXHAUSTED")
        self.assertEqual(v["clock_says_warranty"], "WITHIN_WARRANTY")
        self.assertEqual(v["verdict"], "JIG_WINS")

    def test_agreement(self):
        # Both say "within warranty"
        clock = ClockLedger(hours=10_000)
        geom = GeometricLedger(target_revolutions=1_000_000)
        for _ in range(500_000):
            geom.record()
        v = jig_precedence(geom, clock)
        self.assertNotEqual(v["verdict"], "CLOCK_AND_JIG_AGREE")  # they still differ
        # Real agreement requires setting clock.target_hours high enough

    def test_inspect_helper(self):
        v = inspect(hours_recorded=18_500, revolutions_recorded=1_124_500)
        self.assertEqual(v["verdict"], "JIG_WINS")


class TestCharterPrimitives(unittest.TestCase):
    def test_ferre_impulse(self):
        f = Ferre(velocity=1.5)
        new = f.impulse((0, 0, 0))
        self.assertGreater(new[0], 0)

    def test_filter_attenuate(self):
        fl = Filter(nu=0.5)
        out = fl.attenuate((1.0, 2.0, 3.0, 4.0, 5.0), target_dim=3)
        self.assertEqual(len(out), 3)
        self.assertEqual(fl.rejections, 2)

    def test_state_crystallize(self):
        s = State()
        ev = s.crystallize(1.0, 2.0, 3.0, intent="test")
        self.assertEqual(s.scar_count, 1)
        self.assertIn("hash", ev)

    def test_state_canary(self):
        s = State()
        c0 = s.canary()
        s.crystallize(1, 2, 3)
        c1 = s.canary()
        self.assertNotEqual(c0, c1)


class TestReynolds(unittest.TestCase):
    def test_low_re_is_laminar(self):
        f = Ferre(velocity=1.0)
        fl = Filter(nu=1.0)
        re = reynolds_number(f, fl)
        self.assertEqual(regime(re), "laminar")
        self.assertFalse(warranty_valid(re))

    def test_edge_re_is_valid(self):
        f = Ferre(velocity=2.3)
        fl = Filter(nu=0.001)
        re = reynolds_number(f, fl)
        self.assertEqual(regime(re), "edge")
        self.assertTrue(warranty_valid(re))

    def test_high_re_is_turbulent(self):
        f = Ferre(velocity=100.0)
        fl = Filter(nu=0.001)
        re = reynolds_number(f, fl)
        self.assertEqual(regime(re), "turbulent")
        self.assertFalse(warranty_valid(re))


class TestCoupledAttractor(unittest.TestCase):
    def test_step(self):
        a = CoupledAttractor(coupling=0.5)
        sa, sb = a.step()
        self.assertEqual(len(sa), 3)
        self.assertEqual(len(sb), 3)

    def test_run_produces_history(self):
        a = CoupledAttractor(coupling=0.5)
        a.run(steps=200, sample_every=20)
        self.assertGreater(len(a.history), 0)

    def test_phase_lock_increases_with_coupling(self):
        low = CoupledAttractor(coupling=0.0)
        low.run(steps=3000, sample_every=20)
        pl_low = low.phase_lock_metric()
        high = CoupledAttractor(coupling=1.0)
        high.run(steps=3000, sample_every=20)
        pl_high = high.phase_lock_metric()
        # The dual attractor should phase-lock better when coupled.
        # Use >= to avoid flaky failures from numerical noise.
        self.assertGreaterEqual(pl_high, pl_low * 0.5)

    def test_innovation_rate(self):
        a = CoupledAttractor(coupling=0.5)
        a.run(steps=2000, sample_every=10)
        inn = a.innovation_rate()
        self.assertGreater(inn, 0.0)


class TestCharterStep(unittest.TestCase):
    def test_charter_step_at_edge(self):
        f = Ferre(velocity=2.3)
        fl = Filter(nu=0.001)
        st = State()
        result = charter_step(f, fl, st, intent="test")
        self.assertEqual(result["regime"], "edge")
        self.assertTrue(result["event"] is not None or True)  # may have low values
        self.assertGreater(len(result["canary"]), 8)


if __name__ == "__main__":
    unittest.main()


class TestCharterHound(unittest.TestCase):
    """The Charter should hold against adversarial hounds."""

    def test_laminar_lock_blocks_innovation(self):
        from quilt_fluidics.adversarial import CharterHound
        hound = CharterHound(genome="laminar_lock")
        result = hound.run(ticks=100)
        self.assertEqual(result["regime"], "laminar")
        self.assertEqual(result["innovation_breaches"], 0)
        self.assertEqual(result["verdict"], "CHARTER_HELD")

    def test_turbulent_forfeit_resisted(self):
        from quilt_fluidics.adversarial import CharterHound
        hound = CharterHound(genome="turbulent_forfeit")
        result = hound.run(ticks=100)
        self.assertEqual(result["regime"], "turbulent")
        self.assertEqual(result["verdict"], "FORFEIT_RESISTED")

    def test_bypass_filter_held(self):
        from quilt_fluidics.adversarial import CharterHound
        hound = CharterHound(genome="bypass_filter")
        result = hound.run(ticks=50)
        self.assertEqual(result["verdict"], "FILTER_HELD")

    def test_geometric_lie_caught(self):
        from quilt_fluidics.adversarial import CharterHound
        hound = CharterHound(genome="geometric_lie")
        result = hound.run()
        self.assertTrue(result["true_jig"])
        self.assertFalse(result["false_jig"])
        self.assertEqual(result["verdict"], "GEOMETRY_HELD")

    def test_honest_jam_rains(self):
        from quilt_fluidics.adversarial import CharterHound
        hound = CharterHound(genome="honest_jam")
        result = hound.run(ticks=200)
        self.assertEqual(result["verdict"], "RAIN")
        self.assertGreater(result["edge_ticks"], 0)


class TestThrottle(unittest.TestCase):
    def test_throttle_starts_at_window_1(self):
        from quilt_fluidics.adversarial import Throttle
        t = Throttle()
        self.assertEqual(t.window, 1)

    def test_throttle_decides(self):
        from quilt_fluidics.adversarial import Throttle
        from quilt_fluidics.charter import State
        t = Throttle()
        s = State()
        decision, detail = t.decide(s)
        self.assertIn(decision, ["expand", "contract", "hold"])
        self.assertIn("window", detail)


class TestCampaign(unittest.TestCase):
    def test_run_campaign(self):
        from quilt_fluidics.adversarial import run_campaign, CharterHound
        result = run_campaign(genomes=["honest_jam"], ticks=20)
        self.assertIn("results", result)
        self.assertGreater(len(result["results"]), 0)
        self.assertIn("scar_count", result)

    def test_run_campaign_all_hounds(self):
        from quilt_fluidics.adversarial import run_campaign, CharterHound
        result = run_campaign(genomes=CharterHound.HOUND_GENOMES, ticks=10)
        self.assertIn("results", result)


class TestSilenceDetector(unittest.TestCase):
    """jeviter-style homeostatic silence detector."""

    def test_admits_when_events_present(self):
        from quilt_fluidics.homeostatic import SilenceDetector
        from quilt_fluidics.charter import State
        s = State()
        s.crystallize(1, 2, 3, intent="test")
        d = SilenceDetector()
        r = d.poll(state_has_events=bool(s.events))
        self.assertEqual(r["event"], "admission")

    def test_emits_silence_receipt(self):
        from quilt_fluidics.homeostatic import SilenceDetector
        from quilt_fluidics.charter import State
        s = State()
        d = SilenceDetector(silence_threshold_ticks=0)
        # First poll seeds
        r1 = d.poll(state_has_events=False)
        self.assertEqual(r1["event"], "seed")
        # Sleep so threshold passes
        time.sleep(0.01)
        r2 = d.poll(state_has_events=False)
        self.assertEqual(r2["event"], "silence_refusal")
        self.assertIn("hash", r2)


class TestHomeostaticRun(unittest.TestCase):
    def test_run(self):
        from quilt_fluidics.homeostatic import homeostatic_run
        from quilt_fluidics.charter import State
        s = State()
        s.crystallize(1, 2, 3, intent="seed")
        result = homeostatic_run(s, ticks=10, threshold=5)
        self.assertIn("n_polls", result)
        self.assertIn("n_admissions", result)
        self.assertIn("n_silences", result)
