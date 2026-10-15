#!/usr/bin/env python3
"""Safety regressions: AP No-Go, manufacturer TLD Test A vs hot, PG backfeed."""
import unittest
from trippower_a_round6_powerfail_architecture import ap_screen,tld_screen,backup_pg,costs,current_scenario,all_studies

class R6PowerLossArchitectureRegression(unittest.TestCase):
    def test_ap_src_exceeds_vin_normal_9_10_11_30v_for_typ_case(self):
        s=ap_screen()
        for v in (9,10,11,30):
            c=s["scenarios"][str(v)]["typ62uA_25C_Rds30mOhm_illustrative"]
            self.assertGreater(c["ap_src_v_ASSUMED"],c["ap_vin_v_ASSUMED"])
            self.assertTrue(c["scenario_exceeds_SRC_le_VIN_absolute_rating"])
            self.assertLess(c["max_ap_vin_feed_current_to_avoid_SRC_over_VIN_a"],62e-6)
        self.assertEqual(s["decision"],"NO_GO_AS_DRAWN_NO_GUARANTEED_SRC_VIN_ENVELOPE")

    def test_abs_limit_not_a_pseudo_typical_voltage(self):
        s=ap_screen()
        self.assertIsNone(s["vendor_IQ_at_9V_dynamic_max_a"])
        self.assertIsNone(s["vendor_IQ_at_12V_min_a"])
        self.assertFalse(s["vendor_guaranteed_9V_start_with_9p9k_feed"])
        with self.assertRaises(ValueError):current_scenario(9,-1)

    def test_feasible_low_IQ_scenario_does_not_prove_guarantee(self):
        s=ap_screen()["scenarios"]["9"]
        a=s["lowIQ1uA_example"]
        self.assertFalse(a["scenario_exceeds_SRC_le_VIN_absolute_rating"])
        self.assertFalse(a["static_state_guaranteed"])

    def test_TLD_Ri_disagreement_vendor_clamp_25c_only(self):
        t=tld_screen()
        self.assertEqual(t["graph_Ri_202v350ms_25c_ohm"],4.5)
        self.assertEqual(t["text_Ri_202v350ms_25c_ohm"],3.5)
        self.assertAlmostEqual(t["ideal_I_at_202V_3p5ohm_assuming_Vc61p2_a"],40.2285714,places=5)
        self.assertIsNone(t["guaranteed_max_Vc_at125c_v"])
        self.assertIsNone(t["guaranteed_min_Ri_at125c_ohm"])
        self.assertFalse(t["can_replace_HV_guard_and_LM74930_at125c"])

    def test_measured_61v_is_not_a_60v_rating_certificate(self):
        t=tld_screen()
        self.assertLess(t["margin_to60V_absolute_Q302_rating_if_across_FET_v"],0)
        self.assertLess(t["margin_to65V_LM74930_VS_operating_at25c_measured_v"],4)
        self.assertTrue(t["hypothetical_full_350ms_rectangular_energy_NOT_PULSE_SOA"])

    def test_pgood_failure_logic_and_backup_isolation(self):
        x=backup_pg()
        self.assertIn("3V3",x["interface"])
        self.assertEqual(x["exported_logic_low"],"5V healthy/PG released, NMOS ON")
        self.assertTrue(x["gpio_high_no_backfeed_requires_hot_leakage_and_gate_pin_proof"])
        self.assertIsNone(x["verified_IRQ_leadtime_before_3v3_brownout_ms"])
        self.assertFalse(x["backup_power_integral_and_SD_shutdown_success_proven"])

    def test_pgood_warning_can_be_late_without_external_hold(self):
        x=backup_pg()
        self.assertLess(x["normal_5v_2A_ideal_holdtime_66uF_to4p6_ms"],.014)
        self.assertGreater(x["manufacturer_glitch_filter_fall_min_us"],35)

    def test_total_positions_and_unpriced_BOM_cannot_be_faked(self):
        x=costs()
        c=x["nominal_populated_board_counts"]
        self.assertEqual(c["AP_guard_AUTO"],69)
        self.assertEqual(c["PWR_GOOD_buffer_prototype_plus_REV5_AUTO"],60)
        self.assertEqual(c["TVS_plus_REV5_and_PG_OPTION_AUTO"],61)
        self.assertTrue(x["no_credible_complete_57_58_or_69_70_unit_price_yet"])

    def test_no_survival_release(self):
        a=all_studies()
        self.assertEqual(a["requirements"],[9,30,200,.35,-40,125])
        self.assertFalse(a["fabrication_release"])
        self.assertEqual(a["decisions"]["old_AP_guard"],"NO_GO")

if __name__=="__main__":unittest.main()
