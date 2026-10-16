"""Round10 independent TI manufacturer's minimum 300k / 32V hysteresis gates."""
import unittest
from rev6_round10_ti_factory_uvlo import (
 DATA,A_PIN_SNAPSHOT,R330,resistor_range,vendor_300k_compliance,
 one_resistor_UVLO,OV_factory,old_A_UVLO_factory_OVP_direct_strap_failure,
 raw_short_current,fault_state,report)

class TIManufacturerRound10(unittest.TestCase):
 def test_ti_300k_direct_minimum_is_NOT_nominal_300k_with_tolerance(self):
    a=vendor_300k_compliance({"nominal_ohm":300000.,
             "tolerance":.01,"tcr_per_K":.0001})
    self.assertLess(a["min_R_ohm"],300000)
    self.assertFalse(a["minimum_300k_per_datasheet"])
 def test_reject_earlier_100k_15k_suggestion_even_if_10v_threshold_passes(self):
    r=vendor_300k_compliance({"nominal_ohm":100000.,
               "tolerance":.001,"tcr_per_K":.000025})
    self.assertFalse(r["minimum_300k_per_datasheet"])
    self.assertLess(r["min_R_ohm"],300000)
 def test_330k_real_AEC_1pct_100ppm_at_minus20_plus70_plus85(self):
    r=vendor_300k_compliance(R330)
    self.assertTrue(r["minimum_300k_per_datasheet"])
    self.assertAlmostEqual(r["min_R_ohm"],324720)
    self.assertAlmostEqual(r["max_R_ohm"],335280)
    self.assertTrue(R330["automotive_AEC_Q200"])
 def test_single_R_10v_PIN_v_vs_TI_rising_ref(self):
    a=one_resistor_UVLO()
    self.assertTrue(a["UVLO_high_enough_to_enable_at_10vin_sys"])
    self.assertFalse(a["UVLO_factory_15v_selected"])
    self.assertGreater(a["pin_UVLO_min_max_at_10vin_sys_v"][0],9.94)
    self.assertLess(a["UVLO_trip_in_SYS_voltage_upper_bound_v"],1.28)
    self.assertTrue(a["no_guarantee_whole_board_starts_at_10v"])
 def test_min_reverse_300k_limits_minus60v_ESD_injection_model(self):
    r=vendor_300k_compliance(R330)
    self.assertLess(r["effect_of_negative_60v_max_approx_injection_a"],200e-6)
    self.assertLess(r["resistor_power_at_58v_if_UVLO_grounded_w"],.012)
    self.assertTrue(r["actual_reverse_fault_injection_not_lab_verified"])
 def test_at_10v_VINSYS_drop_can_break_qualified_board_even_when_UVLO_high(self):
    self.assertTrue(one_resistor_UVLO(vin_sys_v=10)["UVLO_high_enough_to_enable_at_10vin_sys"])
    self.assertFalse(one_resistor_UVLO(vin_sys_v=1.1)["UVLO_high_enough_to_enable_at_10vin_sys"])
    # 10V at M8 does not mean 10V at IN_SYS; proof requires actual pads.
 def test_ti_factory_OV_rising_min_max_and_falling_correct_sign(self):
    a=OV_factory()
    self.assertEqual(a["factory_rising_min_max"],(33.2,35.4))
    self.assertEqual(a["factory_falling_min_max"],(32.7,35.))
    self.assertTrue(a["32v_nominal_on_guarantee"])
    self.assertTrue(a["32v_OV_recovery_static_guarantee"])
    self.assertAlmostEqual(a["recovery_margin_v"],.7)
    self.assertTrue(a["36v_shutdown_static_guarantee"])
    self.assertFalse(a["dynamic_58_to_32_pass"])
 def test_ripple_positive_0p8_exceeds_factory_min_falling_32p7(self):
    self.assertFalse(OV_factory(ac_overshoot_v=.8)["32v_OV_recovery_static_guarantee"])
    self.assertTrue(OV_factory(ac_overshoot_v=.5)["32v_OV_recovery_static_guarantee"])
    self.assertFalse(OV_factory(noise_v=.7)["32v_OV_recovery_static_guarantee"])
    self.assertTrue(OV_factory(ac_overshoot_v=.6,extra_drop_from_connector_v=.2)["32v_OV_recovery_static_guarantee"])
 def test_old_A_as_drawn_has_not_implemented_factory_ov(self):
    self.assertEqual(A_PIN_SNAPSHOT["U201_pin8"],"OVP_SENSE")
    self.assertEqual(A_PIN_SNAPSHOT["R201_ohm"],100e3)
    self.assertEqual(A_PIN_SNAPSHOT["R202_ohm"],12e3)
    self.assertFalse(A_PIN_SNAPSHOT["native_approved_OVP8_GND"])
    self.assertEqual(A_PIN_SNAPSHOT["Q201_source"],"VIN_FUSED")
 def test_only_strapping_ovp_to_gnd_causes_10v_UV_failure(self):
    a=old_A_UVLO_factory_OVP_direct_strap_failure()
    self.assertGreater(a["VIN_UVLO_rise_worst_nominal_R_v"],10)
    self.assertFalse(a["ti_reverse_FET_300k_compliant"])
    self.assertTrue(a["factory_OVP_strap_alone_is_NO_GO"])
 def test_PGTH_ground_prevents_fast_recovery_not_normal_ovp_trip_loss(self):
    self.assertTrue(DATA["PGTH_to_GND_if_fast_recovery_unwanted"])
    self.assertGreater(DATA["SHDN_open_v"][0],2)
    self.assertEqual(DATA["SHDN_sinking_requirement_microa"],10)
 def test_MODE_float_latches_overload_not_normal_OVP_same_state(self):
    a=fault_state("normal_OVP_without_other_fault")
    b=fault_state("overcurrent_or_temperature_trip_with_MODE_open")
    self.assertTrue(a["mode_open_does_not_necessarily_latch_OVP"])
    self.assertTrue(a["at_32v_reenable_when_no_OL_latch"])
    self.assertFalse(b["32v_OV_recovery_alone_clears_latch"])
    self.assertTrue(b["latched"])
 def test_RAW_short_and_subILIM_not_automatically_recovered_by_32v(self):
    a=fault_state("RAW_short_at_return_32v")
    self.assertFalse(a["restart_automatically_guaranteed"])
    r=raw_short_current()
    self.assertGreater(r["potential_3x_fast_trip_nominal_a"],8.)
    self.assertAlmostEqual(r["example_raw_load_R32ohm_at_V32V_w"],32)
    self.assertFalse(r["raw_0p5A_selectivity_proven"])
 def test_M8_backup_no_early_warn_and_no_CR1220_SD_guarantee(self):
    m=fault_state("M8_sudden_disconnect")
    self.assertEqual(m["advance_warning_time_ms_guaranteed"],0)
    self.assertTrue(m["critical_data_already_atomically_FRAM_committed_required"])
    self.assertFalse(m["SD_unmount_on_primary_cell_required"])
 def test_both_VOLTS_RATING_and_no_fuse_on_module_are_unreleased(self):
    r=report()
    self.assertEqual(r["manufacturer"]["eFuse_in_operating_max_v"],60)
    self.assertEqual(r["manufacturer"]["eFuse_in_abs_max_v"],67)
    self.assertTrue(all(v is False for v in r["RELEASE_GATES"].values()))
if __name__=="__main__":
 unittest.main()
