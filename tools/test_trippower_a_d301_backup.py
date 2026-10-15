#!/usr/bin/env python3
"""Regression of published derating arithmetic and conservative D301-open gate."""
import unittest
from trippower_a_d301_backup_analysis import (
    fault_study, allowable_onsemi_at_tlead,
    allowable_onsemi_reference_board_at_ambient)

class D301RedundancyTests(unittest.TestCase):
    def test_3w_is_conditional_on_lead_not_ambient(self):
        self.assertAlmostEqual(allowable_onsemi_at_tlead(125),1.0,places=6)
        self.assertAlmostEqual(allowable_onsemi_reference_board_at_ambient(125),
                               0.110,places=6)

    def test_full_load_at_200v_not_half_in_parallel(self):
        s=fault_study()
        p=s["D301_open_D306_healthy_fixed_Vz_cases"]["56.0"]
        self.assertGreater(p["individual_full_pulse_zener_power_W"],0.8)
        self.assertGreater(p["individual_full_pulse_zener_energy_J"],0.28)
        self.assertFalse(p["D306_5W_at_125C_package_proven"])

    def test_operating_max_corner_needs_hot_lead_and_vz_proof(self):
        s=fault_study()
        p=s["D301_open_D306_healthy_fixed_Vz_cases"]["65.0"]
        self.assertGreater(p["individual_full_pulse_zener_power_W"],0.9)
        hot=s["Zener_hot_case_manufacturer_limits"]
        self.assertLess(hot["onsemi_3W_56v_max_Tlead_C_if_65V_fixed_assumed"],128)
        self.assertIsNone(hot["comchip_ACZRC5370B_G_W_at125C_on_our_pcb"])

    def test_fmea_either_single_open_has_other_branch(self):
        s=fault_study()
        f=s["fmea"]
        self.assertIn("D306",f["D301_open_D306_healthy"])
        self.assertIn("D301",f["D306_open_D301_healthy"])
        self.assertIn("fails risk",f["D301_and_D306_open"])

    def test_9v_leak_not_silently_specified(self):
        s=fault_study()["9v_start_delta"]
        self.assertAlmostEqual(s["hypothetical_500nA_effect_on_VS_v"],0.00495)
        self.assertIsNone(s["additional_D306_9V_125C_reverse_leak_max_A"])
        self.assertFalse(s["9v_guaranteed"])
        self.assertTrue(s["supply_R_ohm_unchanged"])

if __name__=="__main__":unittest.main()
