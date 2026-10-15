"""TripPower B Round5: numerical regression and deliberate rejection of unsafe claims.

PASS = screen behaves as authored; no supplier certification, SOA or ISO PASS.
"""
import unittest
from fault_energy_fuse_gate import (
    FUSES, PULSE_V, PULSE_S, qualification, i2t_350ms_constant,
    i2t_catalog_screen, normal_input_current, zener_branch,
    fault_resistive, prospective_short, external_cable_screen,
    fuse_no_action_counterexample, report, fmea,
)

class FuseAndEnergyGate(unittest.TestCase):
    def test_generic_32v_automotive_fuse_not_200v_dc_breaker(self):
        p=qualification(FUSES["AUTO_BLADE_32V_COMPARISON_ONLY"],prospective_short_a=40)
        self.assertFalse(p["DC_voltage_rating_sufficient"])
        self.assertFalse(p["complete_selectivity_time_energy_and_holder_proven"])
    def test_proposed_500vdc_fuse_needs_real_dc_opening_time_and_holder(self):
        w=FUSES["WEIDMULLER_1460620000"]
        q=qualification(w,prospective_short_a=40)
        self.assertTrue(q["DC_voltage_rating_sufficient"])
        self.assertTrue(q["DC_interrupt_capacity_sufficient_if_prospective_given"])
        self.assertFalse(q["complete_selectivity_time_energy_and_holder_proven"])
        self.assertFalse(q["safe_125C_carry_proven"])
        self.assertFalse(q["holder_200VDC_qualified"])
    def test_genuine_mersen_automotive_fuse_still_does_not_guarantee_350ms(self):
        m=FUSES["MERSEN_MEV55C5"]
        self.assertTrue(m.supported_operating_to_125c)
        self.assertEqual(m.dc_v_rating,550)
        self.assertEqual(m.interrupt_dc_a,20000)
        self.assertEqual(m.min_dc_break_current_a,10.)
        self.assertEqual(m.manufacturer_max_clear_at_min_break_s,10.)
        self.assertTrue(qualification(m,prospective_short_a=40)["fuse_clearing_range_includes_this_current"])
        self.assertFalse(qualification(m,prospective_short_a=2.6)["fuse_clearing_range_includes_this_current"])
        self.assertFalse(qualification(m,prospective_short_a=40)["complete_selectivity_time_energy_and_holder_proven"])

    def test_weidmuller_manufacturer_temperature_spec_fails_target(self):
        w=FUSES["WEIDMULLER_1460620000"]
        self.assertEqual(w.manufacturer_ambient_range_c,(-5.,40.))
        self.assertFalse(w.supported_operating_to_125c)

    def test_eaton_catalog_i2t_not_a_predicted_350ms_trip(self):
        e=FUSES["EATON_FWC-4A10F"]
        case=i2t_catalog_screen(e,20)
        self.assertAlmostEqual(case["integral_a2s"],140.)
        self.assertAlmostEqual(case["prearc_catalog_a2s"],5.2)
        self.assertAlmostEqual(case["clearing_catalog_a2s"],32.)
        self.assertFalse(case["eligible_to_claim_fuse_cleared"])
        self.assertAlmostEqual(i2t_350ms_constant(1),.35)
    def test_9v_operation_requires_fuse_temperature_margin(self):
        z=normal_input_current(efficiency=.8)
        self.assertAlmostEqual(z["main_input_a"],2.388888888888889)
        self.assertFalse(z["fuse_125c_carry_guaranteed"])
        self.assertGreater(normal_input_current(efficiency=.75)["main_input_a"],2.4)
    def test_q301_short_zener_path_low_source_resistance(self):
        a=zener_branch(5)
        self.assertAlmostEqual(a["current_a"],28.66,places=6)
        self.assertAlmostEqual(a["zener_energy_j"],561.736,places=4)
        self.assertFalse(a["real_zener_fails_or_hot_SOA_proven"])
        self.assertFalse(a["external_fuse_will_clear"])
    def test_series_resistive_fault_below_fuse_nominal_but_zener_dissipation_large(self):
        v=zener_branch(5,50)
        self.assertAlmostEqual(v["current_a"],2.6054545454545455)
        self.assertAlmostEqual(v["zener_energy_j"],51.066909090909085)
        f=fuse_no_action_counterexample(v["current_a"],FUSES["WEIDMULLER_1460620000"],v["zener_energy_j"])
        self.assertTrue(f["current_not_above_nominal"])
        self.assertFalse(f["guaranteed_350ms_protection_by_FMAIN"])
    def test_low_current_destructive_silicon_resistance_is_not_a_short_circuit(self):
        x=fault_resistive(5,100)
        self.assertAlmostEqual(x["current_a"],1.9047619047619047)
        self.assertAlmostEqual(x["fault_energy_j"],126.98412698412697)
        self.assertFalse(x["fuse_clearing_guaranteed"])
        y=fault_resistive(5,500)
        self.assertLess(y["current_a"],.5)
        self.assertGreater(y["fault_energy_j"],25.)
    def test_DC_short_capacity_not_same_as_short_cable_thermal_guarantee(self):
        weid=FUSES["WEIDMULLER_1460620000"]
        a=external_cable_screen(weid,5,.1)
        self.assertEqual(a["prospective_or_assumed_a"],40.)
        self.assertTrue(a["fuse_dc_voltage_ok"])
        self.assertTrue(a["fuse_interrupt_a_ok"])
        self.assertAlmostEqual(a["wire_joule_energy_if_uncleared_j"],56.)
        self.assertFalse(a["fuse_total_clearing_vs_copper_damage_proven"])
        high=external_cable_screen(weid,.5,.1)
        self.assertEqual(high["prospective_or_assumed_a"],400.)
    def test_no_unearned_safety_release_and_fmea_is_prioritized(self):
        out=report()
        for k,v in out["qualification_decision"].items():
            if k in ("200VDC_interrupting_candidate_identified","possibility_of_safe_sacrificial_fault_containment"):
                self.assertTrue(v)
            else: self.assertFalse(v,k)
        ranks=[v["rank"] for v in fmea()]
        self.assertEqual(ranks,sorted(ranks))
        self.assertEqual(len(ranks),len(set(ranks)))
        self.assertEqual(fmea()[-1]["class_"],"CONDITIONALLY_ACCEPTABLE_TOTAL_LOSS")

if __name__=="__main__":
    unittest.main()
