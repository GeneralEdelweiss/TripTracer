"""Regression tests for a deliberate NO-GO, not a simulation approval."""
import unittest

from verify_b_feasibility import (
    SPECS, threshold_envelope, pad_after_step, time_to_pad_volt_us,
    pad_ramp_upper_bound, permitted_slew_v_per_us, min_efficiency_for_thermal,
    placement_counts, core_ic_costs, report,
)


class BFeasibilityRegression(unittest.TestCase):
    def test_threshold_reproducibility(self):
        v = threshold_envelope()
        self.assertAlmostEqual(v["rising"]["typ_v"], 33.213793103448275, places=6)
        self.assertAlmostEqual(v["rising"]["min_v"], 32.15315645612837, places=6)
        self.assertAlmostEqual(v["rising"]["max_v"], 34.30224337861373, places=6)
        self.assertAlmostEqual(v["falling"]["min_v"], 31.49855826206896, places=6)
        self.assertAlmostEqual(v["falling"]["max_v"], 33.628359502055034, places=6)
        self.assertTrue(v["static_restart_30_possible_by_thresholds"])
        self.assertTrue(v["static_on_30_by_thresholds"])

    def test_dynamic_load_dump_counterexample_can_exceed_absolute_maximum(self):
        # Scenario, not a claim about a specific ISO generator.
        self.assertLess(time_to_pad_volt_us(30, 200, 36, 0.1, 4.7e-6), 0.017)
        self.assertLess(time_to_pad_volt_us(30, 200, 40, 0.1, 4.7e-6), 0.030)
        self.assertGreater(pad_after_step(30,200,0.1,4.7e-6,17), 199.0)
        self.assertGreater(pad_after_step(30,200,0.1,4.7e-6,24), SPECS.tpsm_absolute_max)

    def test_slew_and_ring_pulse(self):
        v = threshold_envelope()["rising"]["max_v"]
        self.assertAlmostEqual(pad_ramp_upper_bound(v,.017,17,7,2),36.71024337861373,places=7)
        self.assertAlmostEqual(pad_ramp_upper_bound(v,.170,17,7,2),40.38224337861373,places=7)
        self.assertLess(permitted_slew_v_per_us(v,36,24), .071)

    def test_thermal_headroom_sensitivity_only(self):
        self.assertAlmostEqual(min_efficiency_for_thermal(22), .8979591836734694, places=6)
        self.assertAlmostEqual(min_efficiency_for_thermal(35), .9333333333333333, places=6)

    def test_actual_placement_counts_include_added_ov(self):
        typ = placement_counts(True)
        minimum = placement_counts(False)
        self.assertEqual((typ["B_auto"], typ["B_run"]), (56,57))
        self.assertEqual((minimum["B_auto"], minimum["B_run"]), (55,56))
        self.assertEqual(placement_counts(True,2,1)["B_auto"],59)
        self.assertEqual(typ["delta_placements"], -1)

    def test_ic_only_1_10_100_eur_costs(self):
        costs=core_ic_costs()
        self.assertAlmostEqual(costs["1"]["B_minus_A_eur"],.510)
        self.assertAlmostEqual(costs["10"]["B_minus_A_eur"],.738)
        self.assertAlmostEqual(costs["100"]["B_minus_A_eur"],.810)

    def test_no_unearned_release(self):
        data=report()
        self.assertEqual(data["classification"],"NO_GO_AS_SIMPLE_REV5_BUCK_SWAP")
        self.assertTrue(data["pass_gates"]["static_threshold_only"])
        for key,value in data["pass_gates"].items():
            if key != "static_threshold_only":
                self.assertFalse(value,key)
        self.assertEqual(len(data["logic_cases"]),6)
        self.assertTrue(all(not s["proven"] for s in data["logic_cases"]))


if __name__ == "__main__":
    unittest.main()
