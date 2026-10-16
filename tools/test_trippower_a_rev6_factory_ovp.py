#!/usr/bin/env python3
"""Independent fixed-OVP/reverse-FET/UVLO truth-table tests, TI TPS2663 RevG."""
import unittest
from trippower_a_rev6_factory_ovp import study,single_uvlo_sense,two_resistor_uvlo_recovery

class FactoryOVP(unittest.TestCase):
 def test_vendor_rise_above_32_and_off_before36(self):
    x=study()["factory_ovp"]
    self.assertGreater(x["rising_min_v"],32)
    self.assertLess(x["rising_max_v"],36)
 def test_vendor_falling_above32_means_recovery_below_threshold(self):
    x=study()["factory_ovp"]
    self.assertTrue(x["32v_return_from_58v_static"])
    self.assertAlmostEqual(x["return_32v_margin_to_min_falling_v"],0.7)
 def test_older_round3_assertion_was_wrong(self):
    self.assertGreater(study()["factory_ovp"]["falling_min_v"],32)
 def test_fixed_ovp_pin8_must_be_at_0v(self):
    self.assertEqual(study()["pin_wiring"]["U201_8_OVP"],"GND factory 34.33V rising")
 def test_factory_uvlo_15v_is_not_used(self):
    x=study()["single_R_disable_external_UVLO"]
    self.assertTrue(x["conditional_sense_10v_start"])
    self.assertGreater(x["guaranteed_10V_UVLO_pin_min_v"],1.224)
 def test_min300k_upline_reverse_fet(self):
    self.assertGreaterEqual(study()["R201_actual_worst_ohm"][0],300000)
 def test_330k_uvlo_min_at_10v(self):
    self.assertGreater(single_uvlo_sense(10),9.94)
 def test_330k_uvlo_min_at_58v(self):
    self.assertLess(single_uvlo_sense(58),60)
    self.assertGreater(single_uvlo_sense(58),57.94)
 def test_two_resistor_uvlo_330k_56k_is_10v_compatible(self):
    self.assertLess(two_resistor_uvlo_recovery(True,"max"),8.71)
    self.assertGreater(two_resistor_uvlo_recovery(True,"min"),7.8)
    self.assertGreater(10-two_resistor_uvlo_recovery(True,"max"),1.2)
 def test_two_resistor_uvlo_hysteresis(self):
    self.assertLess(two_resistor_uvlo_recovery(False,"max"),two_resistor_uvlo_recovery(True,"max"))
 def test_mode_pgth_known_states(self):
    p=study()["pin_wiring"]
    self.assertTrue(p["U201_12_MODE"].startswith("GND"))
    self.assertTrue(p["U201_16_PGTH"].startswith("GND"))
    self.assertTrue(p["U201_13_SHDN"].startswith("OPEN"))
 def test_58v_physical_pad_safety_stays_open(self):
    self.assertFalse(study()["58v_pulse_safety"]["dynamic_V_IN_SYS_58v_350ms_VERIFIED"])
 def test_85c_raw_thermals_stay_open(self):
    x=study()
    self.assertFalse(x["temperature85C_safe_shutdown_realized"])
    self.assertFalse(x["RAW_0p5A_short_selectively_limited"])
    self.assertFalse(x["5V2A_plus60C_proven"])
 def test_10v_power_not_guaranteed_by_uvlo_only(self):
    self.assertFalse(study()["single_R_disable_external_UVLO"]["10V_total_system_full_load_guaranteed"])
 def test_external_fuse_stays_outside_tripPower_BOM(self):
    self.assertFalse(study()["external_vehicle_FMAIN_part_of_module_BOM"])
    self.assertFalse(study()["production_release"])
if __name__=="__main__":unittest.main()
