#!/usr/bin/env python3
"""Regression gates for TripPower Weg A conditional engineering model.
Run: python3 -m unittest discover -s tools -p 'test_trippower_a_*.py' -v
"""
import math
import unittest
from dataclasses import replace
from trippower_a_model import (
    StartCase, pulse_study, rvs_pulse, simulate_start, startup_study,
    vs_static_limit, zener_open, UNKNOWN_GATES
)

class TestSurgeBounds(unittest.TestCase):
    def test_nominal_vs_chain_power(self):
        c=rvs_pulse()
        self.assertAlmostEqual(c["i_ma"],14.5454545454,places=5)
        for x in c["resistor_energy_j"]:
            self.assertAlmostEqual(x,0.24436363636,places=6)
        self.assertAlmostEqual(c["zener_energy_j"],0.285090909,places=6)
        self.assertFalse(c["qualified"])

    def test_resistor_and_zener_corner_envelopes(self):
        data=pulse_study()["pulse_cases"]
        self.assertGreater(
            data["r_min_zener_vz_min_assumed"]["resistor_energy_j"][0],
            data["nominal"]["resistor_energy_j"][0])
        self.assertGreater(
            data["r_min_zener_vz_max_assumed"]["zener_energy_j"],
            data["nominal"]["zener_energy_j"])
        self.assertAlmostEqual(data["d301_short_r_min"]["resistor_energy_j"][0],
                               0.47614189,places=6)
        self.assertAlmostEqual(
            max(data["one_rvs_short_z_min_r_min"]["resistor_energy_j"]),
            0.57717968,places=6)

    def test_hot_surge_limit_is_explicitly_unknown(self):
        p=pulse_study()
        self.assertIsNone(p["q301"]["hot_linear_SOA_certified"])
        self.assertIsNone(p["tvs"]["series_curve_hot_and_350ms_qualification"])
        self.assertFalse(p["fabrication_release"])
        self.assertGreater(len(UNKNOWN_GATES),6)

    def test_tvs_not_assumed_as_200v_clamp(self):
        tvs=pulse_study()["tvs"]
        self.assertAlmostEqual(tvs["d303_d304_series_vbr_at_datasheet_test_current_min_v"],203.7)
        self.assertAlmostEqual(tvs["d303_d304_series_vbr_at_datasheet_test_current_max_v"],234.7)
        self.assertFalse(tvs["guaranteed_to_clamp_at_200v"])
        self.assertTrue(tvs["individual_vc_must_not_be_added_as_guaranteed_stack_clamp"])

    def test_q301_51v_overshoot_exceeds_absolute_limit(self):
        q=pulse_study()["q301"]
        self.assertEqual(q["overshoot_budget_if_source_a_0v_v"],50)
        self.assertGreater(q["vds_source_a_0v_with_51v_overshoot_v"],
                           q["vds_abs_max_v"])

    def test_zener_open_charges_above_vs_operating(self):
        c=zener_open(initial_vs_v=0,ceff_f=21e-6)
        self.assertGreater(c["vs_at_350ms_v"],100)
        self.assertLess(c["time_to_vs_operating_65v_ms"],350)
        charged=zener_open(initial_vs_v=56,ceff_f=21e-6)
        self.assertLess(charged["time_to_vs_operating_65v_ms"],20)
        self.assertGreater(charged["vs_at_350ms_v"],c["vs_at_350ms_v"])

    def test_rvs_short_escalates_energy(self):
        n=rvs_pulse()
        one=rvs_pulse(vz=0.0,short_index=1,r_scale=0.99)
        self.assertGreater(max(one["resistor_energy_j"]),4*n["resistor_energy_j"][0])
        with self.assertRaises(ValueError):
            zener_open(ceff_f=0)

class TestStartState(unittest.TestCase):
    def test_static_9v_precharge_corner(self):
        self.assertAlmostEqual(vs_static_limit(9,35),8.6535)
        self.assertLess(vs_static_limit(9,75),8.539)
        self.assertLess((9-8.539)/9900*1e6,47)
        self.assertGreater((9-8.539)/9900*1e6,46)

    def test_nominal_model_may_release_but_not_guaranteed(self):
        s=simulate_start(StartCase())
        self.assertIsNotNone(s["first_ctrl_en_model_s"])
        self.assertFalse(s["guaranteed_9v_start"])
        self.assertTrue(len(s["unmodelled"])>3)

    def test_75ua_does_not_reach_8p539(self):
        bad=simulate_start(replace(StartCase(),pre_ready_load_ua=75,ready_on_v=8.539))
        self.assertIsNone(bad["first_ctrl_en_model_s"])
        self.assertIsNone(bad["first_source_a_model_s"])

    def test_small_ceff_pump_droop_can_cause_retry(self):
        s=simulate_start(replace(StartCase(),ceff_uf=4,additional_pump_ma=8,
                                 pump_interval_ms=10,ready_on_v=7.51))
        self.assertGreaterEqual(s["model_failed_restarts"],1)
        self.assertIsNone(s["first_source_a_model_s"])

    def test_residual_vs_and_timer_are_not_ignored(self):
        cold=simulate_start(StartCase())
        resumed=simulate_start(replace(StartCase(),initial_vs_v=8.0,
                                        initial_timer_fraction=0.75))
        self.assertLess(resumed["first_ctrl_en_model_s"],cold["first_ctrl_en_model_s"])

    def test_vin0_run_high_does_not_create_source_via_model(self):
        s=simulate_start(replace(StartCase(),vin_v=0,source_a_can_rise=False))
        self.assertIsNone(s["first_source_a_model_s"])
        self.assertIsNone(s["first_ctrl_en_model_s"])
        self.assertFalse(s["guaranteed_9v_start"])

    def test_no_invalid_units_or_model_defaults(self):
        with self.assertRaises(ValueError):
            simulate_start(replace(StartCase(),ceff_uf=0))
        with self.assertRaises(ValueError):
            simulate_start(replace(StartCase(),initial_timer_fraction=1.01))
        self.assertFalse(startup_study()["fabrication_release"])

if __name__=="__main__":
    unittest.main()
