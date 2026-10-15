"""Checks numerical source-example calculations and explicit NOT-QUALIFIED gates.
Only manufacturer DC spec + circuit assumption assertions, NOT an ISO test.
"""
import unittest
from ap74502_reference_fault_screen import (
    ov_corners, supply_60v_zener, zener_open, zener_short,
    resistor_ov_200v, core_cost_eur, fault_matrix, output_current_screen,
    evidence,
)

class APReferenceSafetyGates(unittest.TestCase):
    def test_ov_30v_rising_and_restart_dc_thresholds(self):
        x=ov_corners()
        self.assertAlmostEqual(x["rising_v"]["min"],33.78070123055163,places=6)
        self.assertAlmostEqual(x["rising_v"]["max"],40.19923265512266,places=6)
        self.assertAlmostEqual(x["falling_v"]["min"],30.82212414427157,places=6)
        self.assertTrue(x["restarts_at_30_by_static_threshold_only"])
        self.assertFalse(x["VOUT_SAFE_DURING_200V_TRANSIENT"])
    def test_dz_reference_peak_energy_is_not_qualified(self):
        x=supply_60v_zener()
        self.assertAlmostEqual(x["i_ideal_a"],.014)
        self.assertAlmostEqual(x["resistor_power_w"],1.96)
        self.assertAlmostEqual(x["resistor_energy_j"],.686)
        self.assertAlmostEqual(x["zener_energy_j"],.294)
        self.assertFalse(x["thermal_pulse_certified"])
    def test_dz_open_exceeds_controller_absolute_max_well_before_350ms(self):
        x=zener_open()
        self.assertAlmostEqual(x["seconds_to_80v"],.005108256237659907,places=7)
        self.assertGreater(x["vin_pin_at_350ms_v"],199.)
        self.assertLess(zener_open(initial=60.)["seconds_to_80v"],.002)
        self.assertFalse(x["device_80v_abs_max_guaranteed"])
    def test_dz_short_leaves_hot_resistor_pulse_without_fuse_guarantee(self):
        x=zener_short()
        self.assertAlmostEqual(x["resistor_w"],4.)
        self.assertAlmostEqual(x["resistor_energy_j"],1.4)
        self.assertFalse(x["F_MAIN_clear_20mA_guaranteed"])
    def test_ov_top_resistor_200v_pulse_must_be_rated(self):
        x=resistor_ov_200v()
        self.assertGreater(x["OV_top_R_power_w"],.35)
        self.assertGreater(x["OV_top_R_energy_j"],.13)
        self.assertFalse(x["actual_1206_125C_350ms_pulse_proven"])
    def test_9v_2a_buck_plus_1a_raw_current(self):
        x=output_current_screen()
        self.assertAlmostEqual(x["normal_9v_input_a"],2.388888888888889,places=5)
        self.assertGreater(x["tps1htc30_max_r_conduction_w"],.31)
    def test_three_ICs_not_cheaper_before_extra_MOSFET(self):
        x=core_cost_eur()
        self.assertEqual([d["quantity"] for d in x["price_rows"]],[1,10,100])
        self.assertAlmostEqual(x["price_rows"][0]["B_minus_A_IC_only_eur"],.606)
        self.assertAlmostEqual(x["price_rows"][1]["B_minus_A_IC_only_eur"],.431)
        self.assertAlmostEqual(x["price_rows"][2]["B_minus_A_IC_only_eur"],.3345)
        self.assertFalse(x["complete_1_10_100_eur_qualifiable"])
    def test_all_faults_are_unqualified_not_false_passes(self):
        self.assertTrue(all(not fault["guaranteed"] for fault in fault_matrix()))
        x=evidence()
        for k in ("proven_fully_safe_architecture","200v_350ms_vendor_fet_SOA_verified",
                  "dZ_open_fault_safe","qualified_9v_start","qualified_30v_restart",
                  "qualified_Tj_125_2A_plus_RAW","real_connected_KiCad"):
            self.assertFalse(x[k],k)

if __name__=="__main__":
    unittest.main()
