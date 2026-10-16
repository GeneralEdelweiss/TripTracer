#!/usr/bin/env python3
"""REV6 A no-false-release tests for actual IC thresholds, thermal & price scope."""
import unittest
from trippower_a_rev6_limits import study,voltage_threshold,load_sensitivity,ld_max_envelope
from trippower_a_rev6_ringing import step_peak,hypothetical_resistor_tradeoff
class REV6Limits(unittest.TestCase):
 def test_32v_normal_stays_below_min_trip(self):
    self.assertGreater(voltage_threshold("ovp","min"),32)
 def test_factory_OVP_hysteresis_prevents_32v_restart(self):
    self.assertEqual(study()["10_32_logic"]["fixed_OVP_falling_min_typ_max_v"],[32.7,33.89,35.0])
    self.assertFalse(study()["10_32_logic"]["fixed_OVP_guarantees_32v_restart"])
 def test_factory_UVLO_fails_10v_start(self):
    self.assertFalse(study()["10_32_logic"]["factory_UVLO_guarantees_10v_start"])
 def test_adjustable_ovp_stronger_32v_margins(self):
    self.assertGreater(voltage_threshold("ovp","min")-32,.16)
    self.assertGreater(32-voltage_threshold("ovp_falling","max"),.16)
 def test_32v_restart_after_OVP_falling_with_precision_resistors(self):
    self.assertLess(voltage_threshold("ovp_falling","max"),32)
    self.assertGreater(32-voltage_threshold("ovp_falling","max"),0.05)
 def test_wide_tolerance_historical_chain_does_not_prove_32v_restart(self):
    r1,r2,r3=402000,49900,16500
    scale=.01+.0001*45
    worst=1.15*(1+(r1+r2)*(1+scale)/(r3*(1-scale)))+150e-9*(2*r1+r2)*(1+scale)
    self.assertGreater(worst,32)
 def test_ovp_rise_min_fall_max_and_10v_uvlo_are_separate(self):
    self.assertGreater(voltage_threshold("ovp","min"),32)
    self.assertLess(voltage_threshold("ovp","max"),36)
    self.assertGreater(voltage_threshold("ovp","min"),voltage_threshold("ovp_falling","max"))
    self.assertLess(voltage_threshold("uvlo","max"),10)
 def test_36v_is_above_max_trip(self):
    self.assertLess(voltage_threshold("ovp","max"),36)
 def test_10v_uv_start_limit(self):
    self.assertLess(voltage_threshold("uvlo","max"),10)
 def test_58v_abs_margin_9v_only_before_ringing(self):
    x=ld_max_envelope()
    self.assertTrue(x["input_within_eFuse_operating_limit"])
    self.assertEqual(x["TPS26631_IN_SYS_ABS_MAX_V"]-58,9)
    self.assertFalse(ld_max_envelope(58,9.1)["input_within_eFuse_absolute_rating"])
 def test_output_can_be_off_at58v_and_buck_unprotected_internal_fault(self):
    x=ld_max_envelope()
    self.assertIsNone(x["buck_VIN_if_OVP_actually_opens_v"])
    self.assertEqual(x["buck_VIN_if_eFuse_internal_FET_SHORT_v"],58)
 def test_10v_full_load_with_half_A_RAW(self):
    x=load_sensitivity(10)
    self.assertAlmostEqual(x["input_a_assuming_eta"],1.75)
    self.assertLess(x["input_a_assuming_eta"],x["efuse_ol_limit_low_corner_typ_formula_a"])
 def test_max_voltage_32_with_RAW(self):
    x=load_sensitivity(32)
    self.assertLess(x["input_a_assuming_eta"],1)
 def test_normal_25_components_and_missing_85c_trigger(self):
    s=study()
    self.assertFalse(s["integrated_efuse"]["temperature_fault_off_by85c_has_specific_sensor"])
    self.assertFalse(s["fabrication_release"])
 def test_58v_source_can_ring_above_67v_absolute_at_efuse(self):
    c=step_peak()
    self.assertGreater(c["ideal_1st_peak_at_pin_v"],67)
    self.assertTrue(c["TPS26631_67v_absolute_violation_in_example"])
    self.assertFalse(c["real_vehicle_spectrum_or_lab_proof"])
 def test_series_resistor_solution_has_real_10v_thermal_cost(self):
    c=hypothetical_resistor_tradeoff(1.)
    self.assertAlmostEqual(c["power_dissipation_W"],3.0625,places=4)
    self.assertFalse(c["safe_part_selected"])
 def test_legacy_requirements_not_authority(self):
    s=study()
    self.assertIn("REV6",s["authority"])
    self.assertNotIn("200V",s["authority"])
if __name__=="__main__":unittest.main()
