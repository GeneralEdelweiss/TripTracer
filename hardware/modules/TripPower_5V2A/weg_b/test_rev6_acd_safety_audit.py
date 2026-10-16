"""Independent REV6 A/C/D regression, NOT a physical release or A-native ERC."""
import unittest
from rev6_acd_safety_audit import (
    actual_A_values_from_sheet,A_three_resistor_bounds,TI26631_factory_OVP,
    C_cases,D_LTC4368_bounds,thermals,fault_and_fuse,statuses,report)

class CrossBranch(unittest.TestCase):
    def test_real_A_placed_Rs_parse_by_reference(self):
        fragment='''(symbol (property "Reference" "R201" (at 1 1 0))
(property "Value" "100k 0.1pct UV_TOP" (at 1 2 0)))
(symbol (property "Reference" "R202" (at 1 1 0))
(property "Value" "12.4k 0.1pct" (at 1 2 0)))
(symbol (property "Reference" "R203" (at 1 1 0))
(property "Value" "4.22k 0.1pct" (at 1 2 0)))
TPS26631PWPR'''
        x=actual_A_values_from_sheet(fragment)
        self.assertEqual([x[i]["ohm"] for i in ("R201","R202","R203")],
                         [100000.,12400.,4220.])
        self.assertEqual(report(fragment)["A_placed_R_values_read"]["R201"]["ohm"],100000.)
        with self.assertRaises(ValueError):
            actual_A_values_from_sheet(fragment.replace("R203","R399"))
    def test_A_as_drawn_rising_pass_but_recovery_at_32_fails(self):
        x=A_three_resistor_bounds()
        self.assertAlmostEqual(x["rising_v"][0],32.33421,places=4)
        self.assertAlmostEqual(x["rising_v"][1],33.99611,places=4)
        self.assertAlmostEqual(x["falling_v"][0],29.96731,places=4)
        self.assertAlmostEqual(x["falling_v"][1],31.94272,places=4)
        self.assertTrue(x["rising_within_32_to_36"])
        self.assertFalse(x["restart_at_exactly_32_guaranteed"])
        self.assertFalse(x["dynamic_PGOOD_and_58v_restart_test_proven"])
    def test_factory_TPS26631_32v_recovery_requires_BOTH_OVP_and_UV_redesign(self):
        f=TI26631_factory_OVP()
        self.assertEqual(f["rising_v"],(33.2,35.4))
        self.assertEqual(f["falling_v"],(32.7,35.0))
        self.assertTrue(f["restart_at_exactly_32_guaranteed"])
        a=A_three_resistor_bounds()
        self.assertAlmostEqual(a["uvlo_rising_nominal_v"],8.4200,delta=.2)
        # Simple strap pin8 to GND would make UVLO path only 12.4k:
        self.assertGreater(a["uvlo_if_factory_ovp_strapped_without_UV_redesign_v"],10.8)
        self.assertFalse(a["10v_start_possible_without_uv_redesign_after_grounding_ovp"])
    def test_C_26631_adjustable_static_fails_32v_restart(self):
        a=C_cases()["C_TPS26631_SCHOTTKY_ADJUSTABLE"]
        self.assertTrue(a["rising_within_32_to_36"])
        self.assertFalse(a["restart_at_exactly_32_guaranteed"])
        self.assertLess(a["falling_v"][0],30)
        self.assertTrue(a["series_Schottky_drop_NOT_guaranteed"])
        self.assertTrue(C_cases()["C_TPS26631_SCHOTTKY_FACTORY"]["restart_at_exactly_32_guaranteed"])
    def test_C_26600_adjustable_fails_restart_and_pin_abs_margin_only4v(self):
        b=C_cases()["C_TPS26600_BARE_ADJUSTABLE"]
        self.assertTrue(b["rising_within_32_to_36"])
        self.assertFalse(b["restart_at_exactly_32_guaranteed"])
        self.assertAlmostEqual(b["falling_v"][0],30.0277,places=3)
        self.assertEqual(b["58v_PIN_ABS_headroom_v"],4)
        self.assertEqual(b["integrated_limit_max_a"],2.23)
        self.assertFalse(b["real_INPUT_pads_safe_with_ringing"])
    def test_D_0p25pct_all_pin_leaks_is_statically_but_NARROWLY_possible(self):
        d=D_LTC4368_bounds()
        self.assertAlmostEqual(d["rising_v"][1],35.954525,places=4)
        self.assertAlmostEqual(d["falling_v"][0],32.213910,places=4)
        self.assertTrue(d["rising_within_32_to_36"])
        self.assertTrue(d["restart_at_exactly_32_guaranteed"])
        self.assertGreater(d["margin_36v_at_max_rise_v"],0)
        self.assertLess(d["margin_36v_at_max_rise_v"],.05)
        self.assertTrue(d["resistor_tolerance_with_TCR_is_ASSUMED_not_MPN_qualified"])
        self.assertFalse(d["tested_installed_circuit"])
    def test_D_1pct_fails_both_corners_and_is_worse_with_extra_pin_leak(self):
        d=D_LTC4368_bounds(.01)
        self.assertGreater(d["rising_v"][1],36.)
        self.assertLess(d["falling_v"][0],32.)
        self.assertFalse(d["rising_within_32_to_36"])
        self.assertFalse(d["restart_at_exactly_32_guaranteed"])
        new=D_LTC4368_bounds(.0025,True)
        old=D_LTC4368_bounds(.0025,False)
        self.assertGreater(new["rising_v"][1],old["rising_v"][1])
        self.assertLess(new["falling_v"][0],old["falling_v"][0])
    def test_zero_one_time_fuses_on_module_and_harness_is_external(self):
        f=fault_and_fuse()
        for x in ("TripPower_melt_fuse_count","TripPower_fuse_holder_count",
                  "TripPower_one_time_SMD_fuse_count"):self.assertEqual(f[x],0)
        self.assertFalse(f["TripPower_PPTC_required"])
        self.assertEqual(f["vehicle_BAT_ACC_FMAIN_NEAR_SOURCE"],"REQUIRED")
        self.assertFalse(f["DC_breaker_suitability_when_actual_contact_V_beyond_58V"])
        self.assertFalse(f["cable_protection_guaranteed_without_I2t_full_clear_and_Cu_capacity"])
    def test_heat_efficiency_and_thermal_off_not_qualified(self):
        t=thermals()
        self.assertEqual(len(t),3)
        self.assertGreater(t[0]["naive_all_loss_in_IC_Rtheta45_CperW_TjAt60_C"],150)
        self.assertTrue(all(not x["actual_60C_2A_PASS"] for x in t))
    def test_pass_fail_offen_are_risk_not_automotive_certification(self):
        rows=statuses()
        self.assertGreaterEqual(len(rows),12)
        self.assertTrue(all(x["A"] in ("PASS","FAIL","OFFEN") and
                            x["C"] in ("PASS","FAIL","OFFEN") and
                            x["D"] in ("PASS","FAIL","OFFEN") for x in rows))
        x=next(x for x in rows if "OVP clears" in x["criterion"])
        self.assertEqual(x["A"],"FAIL")
        self.assertTrue(report()["no_go_if_this_release_proposed"])
        self.assertTrue(report()["actual_field_and_thermal_tests_all_open"])

if __name__=="__main__":
    unittest.main()
