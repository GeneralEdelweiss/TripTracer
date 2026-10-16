"""Round9 independent review: confirm vendor min/max and no false zero-part release."""
import csv
import unittest
from pathlib import Path
from rev6_round9_minimal_safety import (
 A_SNAPSHOT,TI,a_three_ladder,factory_with_two_UV_R,factory_ripple,
 efuse_raw_hazard,pptc_candidate,host_thermal_options,
 minimal_function_matrix,report)

class Round9MinimalSafety(unittest.TestCase):
 def test_actual_A_base_12k_not_older_12k4_variants(self):
    self.assertEqual(A_SNAPSHOT["base_R202_ohm"],12000)
    self.assertEqual(A_SNAPSHOT["research_R202_ohm"],12400)
    self.assertEqual(A_SNAPSHOT["pins"]["U201.8"],"OVP_SENSE")
    self.assertEqual(A_SNAPSHOT["pins"]["R202.2"],"OVP_SENSE")
    self.assertEqual(A_SNAPSHOT["pins"]["U201.7"],"UVLO_SENSE")
    self.assertEqual(A_SNAPSHOT["pins"]["Q201.3"],"VIN_FUSED")
 def test_A_actual_base_restarts_not_at32_after_OV(self):
    a=a_three_ladder()
    self.assertGreater(a["rising_v"][0],32)
    self.assertLess(a["rising_v"][1],36)
    self.assertLess(a["falling_v"][1],32)
    self.assertFalse(a["32V_after_OV_restart_guarantee_static"])
    b=a_three_ladder(rmid=12400)
    self.assertGreater(b["falling_v"][1],a["falling_v"][1])
    self.assertFalse(b["32V_after_OV_restart_guarantee_static"])
 def test_TI_factory_two_edges_and_original_trip_logic(self):
    self.assertEqual(TI["factory_ov_rise_v"],(33.2,35.4))
    self.assertEqual(TI["factory_ov_fall_v"],(32.7,35.0))
    self.assertGreater(TI["factory_ov_fall_v"][0],32.)
    self.assertLess(TI["factory_ov_rise_v"][1],36.)
    self.assertEqual(TI["OVP_to_FLT_turnoff_us"],(8.5,14.))
    self.assertFalse(TI["PG_good_for_SD_warning"])
 def test_factory_independent_UV_100k_15k_candidate_10v(self):
    x=factory_with_two_UV_R()
    self.assertGreater(x["uv_rising_min_max_v"][0],8.9)
    self.assertLess(x["uv_rising_min_max_v"][1],9.5)
    self.assertGreater(x["max_internal_VIN_SYS_drop_at_10v_v"],.5)
    self.assertTrue(x["start_at_10v_static"])
    self.assertTrue(x["requires_new_netlist_check"])
    self.assertFalse(x["dynamic_32V_restart_verified"])
 def test_factory_10v_start_cannot_ignore_input_drop(self):
    assert factory_with_two_UV_R(vdrop_to_IN_SYS=.4)["start_at_10v_static"]
    self.assertFalse(factory_with_two_UV_R(vdrop_to_IN_SYS=.8)["start_at_10v_static"])
 def test_factory_32v_restart_requires_ripple_below_fall_min(self):
    self.assertTrue(factory_ripple()["both_static_guarantees"])
    self.assertTrue(factory_ripple(positive_ringing_at_IN_SYS_v=.4)["both_static_guarantees"])
    self.assertFalse(factory_ripple(positive_ringing_at_IN_SYS_v=.8)["both_static_guarantees"])
    self.assertFalse(factory_ripple(positive_ringing_at_IN_SYS_v=.6,
                                    noise_margin_v=.2)["both_static_guarantees"])
 def test_factory_not_current_A_net_and_wont_delete_3_resistors_automatically(self):
    self.assertTrue(A_SNAPSHOT["no_factory_OVP_ground_strap_as_drawn"])
    self.assertEqual(A_SNAPSHOT["pins"]["U201.8"],"OVP_SENSE")
    self.assertEqual(len(a_three_ladder()["R_ohm"]),3)
    self.assertTrue(factory_with_two_UV_R()["required_actual_OVP_ground_strap"])
 def test_TI_current_OL_not_RAW_0p5_short_protector(self):
    a=efuse_raw_hazard()
    self.assertGreater(a["main_OL_nom_a"],2.9)
    self.assertGreater(a["main_OL_estimate_min_max_a"][1],3.1)
    self.assertGreater(a["pulse_2xIOL_est_max_a"],6)
    self.assertGreater(a["fast_trip_3xIOL_est_max_a"],9)
    self.assertEqual(a["short_circuit_protect_limit_datasheet_max_a"],45)
    self.assertTrue(a["nominal_RAW_0p5A_is_NOT_branch_overcurrent_limit"])
 def test_under_main_ILIM_can_make_32W_external_partial_fault(self):
    a=efuse_raw_hazard(vin=32,fault_r_ohm=32)
    self.assertAlmostEqual(a["fault_below_total_OL_a"],1.,places=3)
    self.assertAlmostEqual(a["fault_resistor_power_w"],32.,places=3)
    self.assertFalse(a["safe_0p5A_connector_cable_from_vendor_data_proven"])
 def test_raw_pptc_0p5a_no_hold_margin_at60_70(self):
    a=pptc_candidate()
    self.assertEqual(a["voltage_max_v"],72)
    self.assertEqual(a["I_hold_a"][60],.5)
    self.assertEqual(a["I_hold_a"][70],.44)
    self.assertFalse(a["500mA_has_positive_hold_reserve_at60C"])
    self.assertFalse(a["500mA_continuous_at70C"])
 def test_72v_pptc_20a_rating_below_efuse_short_limit(self):
    p=pptc_candidate()
    self.assertLess(p["fault_current_max_a"],TI["short_circuit_protect_max_a"])
    self.assertFalse(p["max_45A_efuse_fault_within_PPTC_20A_rating_guaranteed"])
 def test_no_assumed_relay_in_current_active_TripTracer(self):
    h=host_thermal_options()
    self.assertFalse(h["vehicle_sensor_already_installed_in_current_mainboard_schematic"])
    self.assertIn("removed",h["current_mainboard_architecture"])
    self.assertFalse(h["MCU_software_only_thermal_shdn_is_safety_proof"])
 def test_NC_coil_option_conditions_and_welded_fail(self):
    h=host_thermal_options()["host_Sensata_67L080_NC_contacts_at80C"]
    self.assertAlmostEqual(h["relay_coil_proposed_only_5v_a"],5/178)
    self.assertLess(h["relay_coil_proposed_only_5v_a"],.5)
    self.assertTrue(h["not_rated_for_raw_58v_bus_directly"])
    self.assertFalse(h["if_host_relay_welded_or_bypassed_safe_off_verified"])
    self.assertFalse(h["if_wire_short_bypasses_contact_safe_off_verified"])
 def test_electrical_fail_safe_requires_hw_independent_of_MCU(self):
    h=host_thermal_options()
    self.assertIn("hardware",h["minimal_success_condition"])
    self.assertIn("SHDN",h["minimal_success_condition"])
 def test_proposed_savings_have_all_releases_open(self):
    m=minimal_function_matrix()
    self.assertGreaterEqual(len(m),12)
    for x in report()["release"].values():self.assertFalse(x)
    self.assertIn("UV-only two-res",m[1][2])
 def test_research_variants_not_masquerading_as_base(self):
    r=report()
    self.assertEqual(r["A_real_base_external_r202_12k"]["R_ohm"][1],12000)
    self.assertEqual(r["A_thermal_and_RAW_variants_older_r202_12k4"]["R_ohm"][1],12400)
    self.assertFalse(r["factory_ov_10v_UV_redesign_candidate_100k_15k"]["dynamic_32V_restart_verified"])

if __name__=="__main__":
 unittest.main()
