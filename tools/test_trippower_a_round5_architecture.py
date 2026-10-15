#!/usr/bin/env python3
"""Reproducible manufacturer-threshold vs hypothetical-fault regressions."""
import unittest
from trippower_a_architecture_decision import compare, ap_ov_thresholds, ap_feed, fuse_high_impedance

class Round5SafetyArchitectureTests(unittest.TestCase):
    def test_genuine_500vdc_fuse_not_auto_closing_hiz_fault(self):
        a=fuse_high_impedance()
        self.assertEqual(a["rated_current_a"],3)
        self.assertEqual(a["dc_interrupt_rating_v"],500)
        self.assertLess(a["hot_fault_current_assumed_a"],a["rated_current_a"])
        self.assertAlmostEqual(a["energy_possible_in_failed_device_j"],3.5)
        self.assertIsNone(a["manufacturer_clearing_time_at_fault_a_and125c_s"])
        self.assertFalse(a["fuse_guarantees_harmless_q301short"])

    def test_ap_ov_corners_tcr_leak_and_30v_recovery(self):
        c=ap_ov_thresholds()
        self.assertGreater(c["rise_min_v"],30)
        self.assertLess(c["rise_max_v"],65)
        self.assertGreater(c["fall_min_v"],30)
        self.assertTrue(c["30v_return_below_worst_possible_falling_threshold"])
        self.assertAlmostEqual(c["OVLO_at30v_nominal_v"],30/31)
        self.assertAlmostEqual(c["OVLO_at200v_nominal_v"],200/31)

    def test_ov_three_resistors_share_high_voltage_pulse(self):
        c=ap_ov_thresholds()
        self.assertLess(c["top_each_peak_w_at200v_equal_resistors"],.05)
        self.assertLess(c["top_each_350ms_j"],.02)
        self.assertFalse(c["pulse_and_hot_resistor_derating_proven"])

    def test_ap_feed_matches_56v_350ms_but_not_zener_hot_qualified(self):
        v=ap_feed()
        self.assertGreater(v["pulse_energy_each_resistor_j"],.24)
        self.assertLess(v["pulse_energy_each_resistor_j"],.27)
        self.assertGreater(v["pulse_zener_energy_j"],.285)
        self.assertFalse(v["zener_350ms_at125c_qualified"])
        self.assertLess(v["D401_open_C1_nominal_time_to80v_ms"],6)

    def test_9v_abs_src_pin_violation_critical_must_report(self):
        s=ap_feed()
        self.assertTrue(s["SRC_above_VIN_possible_vs_AP_abs_SRC_LE_VIN"])
        self.assertTrue(s["vendor_absolute_limit_VSRC_le_VVIN_when_VVIN_positive"])
        self.assertFalse(s["9v_first_start_qualified"])
        self.assertIsNone(s["ap_9v_current_max_for_full_chargepump"])

    def test_single_fet_mutual_series_off_not_body_diode_guarantee(self):
        s=compare()["B_independent_HV_cutoff"]
        self.assertTrue(s["Q301_short_then_AP_healthy_and_OV_OFF_forward_body_diode_blocks"])
        self.assertTrue(s["AP_fet_short_then_Q301_healthy_still_protected_by_LM74930"])
        self.assertEqual(s["components_new"],12)
        self.assertEqual(s["total_placements_auto"],69)
        self.assertEqual(s["total_placements_run"],70)
        self.assertFalse(s["hot_FET_on_and_switching_SOA_qualified"])
        self.assertFalse(s["body_diode_single_fet_WORST_CASE_verified_in_native_netlist"])

    def test_safe_shutdown_not_qualified(self):
        c=compare()
        self.assertFalse(c["system_release"])
        self.assertEqual(c["A_external_main_fuse"]["decision"],
                         "NOT_SUFFICIENT_ALONE__HARD_SHORT_WIRING_AUXILIARY_ONLY")
        self.assertGreater(len(c["blocking_gates"]),5)

if __name__=="__main__": unittest.main()
