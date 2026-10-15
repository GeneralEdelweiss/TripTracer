"""Regression/qualification guards. Green means arithmetic correct, not safe PCB."""
import math
import unittest
from round6_safety_backup_gate import (
    manufacturer_register, fuse_decision, tvs_waveform_sensitivity,
    guard_source_pin_screen, versus_normal_minimum, hard_fault_partial_resistor,
    backup_energy, pwr_fail_interface, warning_and_hold_budget,
    backup_fault_states, protection_fmea, report,
)

class Round6HazardRegression(unittest.TestCase):
    def test_real_mersen_mbc_and_10_second_clear_do_not_guarantee_pulse(self):
        maker=manufacturer_register()["MEV55C5"]
        self.assertEqual((maker["DC_rating_v"],maker["DC_minimum_break_a"]), (550,10))
        self.assertEqual(maker["manufacturer_max_clear_at_10a_s"],10)
        self.assertFalse(fuse_decision(10)["clearing_within_350ms_guaranteed"])
        self.assertFalse(fuse_decision(40)["clearing_within_350ms_guaranteed"])
        self.assertFalse(fuse_decision(2.39)["above_minimum_break_current"])
        self.assertTrue(fuse_decision(.05)["hazard_energy_below_fuse_nominal_may_remain"])
    def test_AN1003_conflict_and_thermal_misinterpretation_is_detected(self):
        maker=manufacturer_register()["TLD8S36AH"]
        self.assertEqual((maker["fig_min_Ri_ohm_at_202V_350ms_25C"],
                          maker["table_Ri_ohm_at_202V_350ms_25C"]),(4.5,3.5))
        self.assertTrue(maker["source_discrepancy_unresolved"])
        self.assertFalse(maker["125C_SOA_curve_available"])
    def test_tvs_energy_uses_explicit_waveform_not_unqualified_iso_claim(self):
        exp=tvs_waveform_sensitivity(ri=3.5)
        rect=tvs_waveform_sensitivity(ri=3.5,profile="constant_rectangle")
        self.assertAlmostEqual(exp["source_max_current_a"],(200-61.2)/3.5)
        self.assertLess(exp["illustrative_energy_j"],rect["illustrative_energy_j"])
        self.assertGreater(rect["illustrative_energy_j"],800)
        self.assertFalse(exp["is_real_AN1003_pulse_energy_or_125C_rating"])
        self.assertFalse(exp["valid_max_pad_80v_or_65v_without_ringing_proof"])
        with self.assertRaises(AssertionError):
            tvs_waveform_sensitivity(ri=0)
    def test_guard_src_greater_than_supplied_vin_cannot_qualify_any_start_voltage(self):
        for v in (9.,10.,11.):
            r=guard_source_pin_screen(v)
            self.assertGreater(r["SRC_minus_VIN_v_assumed"],0)
            self.assertFalse(r["AP_absolute_rule_SRC_le_VIN_satisfied_in_scenario"])
            self.assertFalse(r["actual_start_and_AP_chargepump_guaranteed"])
        self.assertAlmostEqual(guard_source_pin_screen(9)["controller_vin_v_assumed"],8.1189)
    def test_9_10_11_only_sensitivity_not_new_requirement(self):
        vals=versus_normal_minimum()
        self.assertEqual([v["vin_v"] for v in vals],[9.,10.,11.])
        self.assertAlmostEqual(vals[0]["RVS_supply_ua_at_VS_8V_and_R_9p9k"],1000000/9900)
        self.assertAlmostEqual(vals[1]["RVS_supply_ua_at_VS_8V_and_R_9p9k"],2000000/9900)
        self.assertAlmostEqual(vals[2]["RVS_supply_ua_at_VS_8V_and_R_9p9k"],3000000/9900)
        self.assertGreater(vals[0]["normal_input_a_assuming_eta_and_RAW1a"],
                           vals[2]["normal_input_a_assuming_eta_and_RAW1a"])
    def test_nonswitching_fuse_cannot_protect_partial_resistor(self):
        f=hard_fault_partial_resistor()
        self.assertAlmostEqual(f["hypothetical_I_a"],200/105)
        self.assertAlmostEqual(f["hypothetical_fault_energy_j"],40000*100*.35/(105**2))
        self.assertTrue(f["fuse_should_not_be_assumed_to_open"])
    def test_backup_fixture_and_cell_remains_unqualified(self):
        b=backup_energy()
        self.assertAlmostEqual(b["load_base_j"],.99)
        self.assertAlmostEqual(b["load_peak_extra_j"],.0396)
        self.assertAlmostEqual(b["source_required_with_eta_and_margin_j"],1.60875)
        self.assertGreater(b["ideal_farad_for_source_voltage_window"],.7)
        self.assertFalse(b["CR1220_already_qualifies_as_shutdown_source"])
        self.assertFalse(b["3s_SD_flush_guaranteed"])
    def test_open_drain_interface_no_false_warning_on_unpowered_controller(self):
        p=pwr_fail_interface()
        self.assertEqual(p["signal_name"],"PWR_FAIL_N")
        self.assertEqual(p["TripPower_output_absent_or_VIN0"],"HIGH-Z or physically disconnected, NOT a warning")
        self.assertEqual(p["PWR_FAIL_VOH_min_at_3v_assuming_leak_target_v"],2.9)
        self.assertAlmostEqual(p["max_asserted_pullup_current_from_backup_ua"],36)
        self.assertLess(p["rise_time_10_to_90_percent_us_RC_ONLY"],50)
        self.assertTrue(p["local_independent_undervoltage_detector_required"])
        self.assertTrue(p["zero_warning_time_possible_on_M8_disconnect"])
    def test_no_SD_flush_time_no_fake_backup_pass_and_return_is_latched(self):
        unknown=warning_and_hold_budget(3)
        self.assertFalse(unknown["pass"])
        self.assertIsNone(unknown["required_hold_s"])
        self.assertTrue(warning_and_hold_budget(3,flush_s=2.8)["pass"])
        self.assertFalse(warning_and_hold_budget(3,flush_s=3.)["pass"])
        cases=backup_fault_states()
        self.assertTrue(any("returns" in f["event"] for f in cases))
        self.assertTrue(any("SD-write peak" in f["event"] for f in cases))
        self.assertTrue(all(f["failure_if_only_TripPower_PWR_FAIL"] for f in cases))
    def test_fault_matrix_comparable_per_architecture_and_no_qualified_winner(self):
        fm=protection_fmea()
        self.assertEqual(len(fm),12)
        self.assertEqual(sorted(f["priority"] for f in fm),list(range(1,13)))
        self.assertEqual(len(set(f["fault"] for f in fm)),12)
        self.assertTrue(any("D TVS TLD8S36AH open"==f["fault"] for f in fm))
        self.assertTrue(any(f["fault"]=="Q401 guard D-S short" for f in fm))
        self.assertTrue(all(f["A_guard"] and f["D_TVS"] for f in fm))
        dec=report()["engineering_decision"]
        self.assertEqual(dec["tentative_fewer_direct_single_FET_short_unprotected_paths"],"A_INDEPENDENT_GUARD")
        for key,v in dec.items():
            if key!="tentative_fewer_direct_single_FET_short_unprotected_paths":
                self.assertFalse(v,key)

if __name__=="__main__":
    unittest.main()
