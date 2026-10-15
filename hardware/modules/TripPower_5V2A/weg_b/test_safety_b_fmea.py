"""Unittest fault coverage; PASS means correct calculations, not physical safety."""
import unittest
from safety_b_fmea import (EXPECTED, parse_native_netlist, verify_real_pin_map,
                           d301_open, d302_bypass_current_example,
                           q301_turnoff_screen, shunt_zener_pulse, d302_series_resistor_conflict, report)

def native_fixture(swap_d302=False, bypass_r314=False):
    # Artificially structured KiCad-native-shaped .net fixture to validate
    # parser mutation detection; it is NOT a real exported project netlist.
    reversed_map={}
    for component,pins in EXPECTED.items():
        for pin,net in pins.items():
            if swap_d302 and component=="D302":
                net = "SOURCE_A" if pin=="1" else "VS_CLAMP"
            if bypass_r314 and component=="R314" and pin=="1":
                net="VIN_FUSED"
            reversed_map.setdefault(net,[]).append((component,pin))
    lines=["(export (version \"E\")","\t(nets"]
    for code,(name,points) in enumerate(sorted(reversed_map.items()),1):
        lines.append(f'\t\t(net (code "{code}") (name "{name}")')
        for ref,pin in points:
            lines.append(f'\t\t\t(node (ref "{ref}") (pin "{pin}"))')
        lines.append("\t\t)")
    lines.append("\t)")
    lines.append(")")
    return "\n".join(lines)

class IndependentB(unittest.TestCase):
    def test_fixture_native_parser_verifies_requested_pins(self):
        r=verify_real_pin_map(parse_native_netlist(native_fixture()))
        self.assertEqual(r["verified_pin_count"],sum(map(len,EXPECTED.values())))
        self.assertFalse(r["R313_R314_R315_in_path"])
    def test_d302_polarity_mutation_detected(self):
        with self.assertRaises(AssertionError):
            verify_real_pin_map(parse_native_netlist(native_fixture(swap_d302=True)))
    def test_r314_bypass_mutation_detected(self):
        with self.assertRaises(AssertionError):
            verify_real_pin_map(parse_native_netlist(native_fixture(bypass_r314=True)))
    def test_rejects_schematic_text_without_exported_netlist(self):
        with self.assertRaises(ValueError):
            parse_native_netlist('(global_label "SOURCE_A")')
    def test_d301_open_creates_overvoltage_upper_tendency(self):
        z=d301_open()
        self.assertGreater(z["VS_350ms_v"],100)
        self.assertLess(z["cross_65ms"],100)
        self.assertLess(d301_open(vs0=56)["cross_65ms"],20)
        self.assertLess(d301_open(ceff_f=5e-6)["cross_65ms"],25)
    def test_q301_short_allows_unlimited_bypass_path(self):
        r=d302_bypass_current_example(.1)
        self.assertAlmostEqual(r["D301_zener_350ms_j"],1.96,places=5)
        self.assertFalse(r["RVS_9p9kohm_limits_this_path"])
        self.assertTrue(r["main_fuse_may_not_clear"])
        self.assertAlmostEqual(d302_bypass_current_example(1)["D301_zener_350ms_j"],19.6)
    def test_one_d302_series_resistor_cannot_both_run_and_current_limit(self):
        q=d302_series_resistor_conflict()
        self.assertAlmostEqual(q["max_R_for_start_ohms"],384.6153846153846)
        self.assertAlmostEqual(q["min_R_for_200V_fault_ohms"],9553.333333333334)
        self.assertFalse(q["one_resistor_satisfies_both"])

    def test_q301_drain_250v_margin_not_surge_guarantee(self):
        f=q301_turnoff_screen()
        self.assertEqual(f["VDS_ideal_headroom"],50)
        self.assertTrue(f["inductive_overshoot_of_51V_exceeds_absolute_max"])
        self.assertFalse(f["temperature_and_SOA_qualified"])
    def test_nominal_vs_zener_energy_is_not_hot_SOA(self):
        z=shunt_zener_pulse()
        self.assertAlmostEqual(z["i_mA"],14.545454545454545,places=7)
        self.assertAlmostEqual(z["Zener_energy_J"],.2850909090909091,places=7)
        self.assertFalse(z["manufacturer_hot_pulse_pass"])
    def test_missing_release_cannot_be_represented_as_pass(self):
        x=report()
        self.assertEqual(x["netlist"],"NOT_CHECKED_NATIVE_NETLIST")
        self.assertTrue(all(v is False for v in x["RELEASE_GATES"].values()))
        self.assertEqual(x["D303_D304_VBR_min_sum_at_individual_test_current_V"],203.7)

if __name__=="__main__":
    unittest.main()
