#!/usr/bin/env python3
"""Q301 failed-short regression: faults must not be mistaken for safety PASS."""
import unittest
from trippower_a_q301short_stress import direct,limited,study

class Q301ShortTests(unittest.TestCase):
    def test_direct_d302_is_not_RVS_limited(self):
        x=direct(1.0)
        self.assertGreater(x["ideal_fault_current_a"],100)
        self.assertGreater(x["D301_or_D306_thermal_J_if_350ms_no_interrupt"],1000)
        self.assertTrue(x["DIODES_ZENER_AND_MAIN_FUSE_ARE_NOT_SIZED_FOR_THIS"])

    def test_source_impedance_raises_fault_energy_when_lower(self):
        self.assertGreater(direct(1)["D301_or_D306_thermal_J_if_350ms_no_interrupt"],
                           direct(10)["D301_or_D306_thermal_J_if_350ms_no_interrupt"])

    def test_assumed_depletion_currents_do_not_constitute_max(self):
        r=study()["with_Q307_BSP135_and_R342_1p5k"]
        self.assertGreater(r["threshold_divided_by_R_heuristic_mA_NOT_MAX"],1)
        self.assertLess(r["threshold_divided_by_R_heuristic_mA_NOT_MAX"],1.5)
        self.assertTrue(r["BSP135_Vgs_threshold_not_guaranteed_current_limit"])
        self.assertIsNone(r["BSP135_125C_allowable_350ms_energy_J"])

    def test_5ma_could_make_mosfet_hot_stress(self):
        a=limited(1.4)
        b=limited(5)
        self.assertLess(a["BSP135_pulse_energy_J"],b["BSP135_pulse_energy_J"])
        self.assertGreater(b["BSP135_power_W"],0.6)
        self.assertFalse(b["hot_SOA_proven"])

    def test_at_9v_not_enough_guaranteed_backfeed(self):
        x=study()["9v_start"]
        self.assertLess(x["sum_sensitivity_mA"],x["LM74930_active_Iq_12V_test_max_mA"])
        self.assertFalse(x["guaranteed_9v_start"])

    def test_secondary_65v_domain_is_not_whole_fault_fix(self):
        x=study()["unsolved_Q301_short_transmission"]
        self.assertTrue(x["U301_A_connected_to_SOURCE_A_and_exposed_to200"])
        self.assertTrue(x["Q302_60V_MOSFET_not_qualified_at200"])
        self.assertTrue(x["even_perfect_Q307_does_not_make_Q301_short_safe"])

    def test_d306_not_production_released(self):
        x=study()["D306_decision"]
        self.assertIsNone(x["D306_hot_350ms_rating"])
        self.assertEqual(x["D306_production_decision"],"DO_NOT_POPULATE_REV5_YET")

if __name__=="__main__":unittest.main()
