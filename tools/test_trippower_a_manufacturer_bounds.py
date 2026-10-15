#!/usr/bin/env python3
"""Vendor timing equation regression — C311 Ceff is intentionally unknown."""
import unittest
from trippower_a_start_manufacturer_bounds import tctr_bound_ms, manufacturer_bounds, static_9v_budget

class ManufacturerBoundTests(unittest.TestCase):
    def test_vendor_tps38_ctr_nominal_420ms(self):
        self.assertAlmostEqual(tctr_bound_ms(0.33,"typ"),420.0819,places=2)

    def test_resistor_and_ctr_cap_tolerances_expand_delay(self):
        self.assertLess(tctr_bound_ms(0.33,"min"),tctr_bound_ms(0.33,"typ"))
        self.assertLess(tctr_bound_ms(0.33,"typ"),tctr_bound_ms(0.33,"max"))
        self.assertLess(tctr_bound_ms(0.126225,"min"),tctr_bound_ms(0.33,"min"))
        self.assertIsNone(tctr_bound_ms(None,"min"))

    def test_d306_9v_hot_leak_no_manufacturer_bound(self):
        a=manufacturer_bounds()
        self.assertIsNone(a["D306_comchip"]["IR_max_ua_at_VS9v_and125C"])
        self.assertIsNone(a["ti_LM74930"]["actual_charge_pump_additional_VS_draw_max_9v_ua"])
        self.assertIsNone(a["ti_TPS38"]["CTR_Ceff_min_and_max_at_bias_temp_aging_uf"])
        self.assertTrue(a["cannot_claim_GUARANTEED_9v"])

    def test_9v_budget_at_1percent_and_hot_tcr(self):
        base=static_9v_budget(7.51,rv_factor=1.0)
        hot=static_9v_budget(7.51,rv_factor=1.0201)
        self.assertAlmostEqual(base["max_total_precharge_current_for_9v_trip_ua"],150.50505,places=3)
        self.assertLess(hot["max_total_precharge_current_for_9v_trip_ua"],
                        base["max_total_precharge_current_for_9v_trip_ua"])

if __name__=="__main__":unittest.main()
