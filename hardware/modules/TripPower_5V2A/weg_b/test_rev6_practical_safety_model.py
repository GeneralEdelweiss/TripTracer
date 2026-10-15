"""Round7: manufacturer-sourced 58V fuse facts and REV6-only safety gates.

Passing unittest confirms assertions, not physical qualification.
"""
import unittest
from rev6_practical_safety_model import (
    REV6,FUSES,FUSE_FAMILY_MANUFACTURER,load_sensitivity,fuse_guard,
    fuse_opening_at_exact_maker_multipliers,harness_ringing,
    source_installation_check,ov_corner_gates,failed_silicon_power,
    fram_journal_model,report, fmea, matrix
)

class Rev6PracticalSafety(unittest.TestCase):
    def test_supersedes_old_9v_200v_125c_revision(self):
        self.assertEqual(REV6["normal_v"],(10.,32.))
        self.assertEqual(REV6["clamped_load_dump"],(58.,.350))
        self.assertEqual(REV6["ov_survival_test"],(36.,.400))
        self.assertEqual(REV6["5v_2a_ambient_range_c"],(-20.,60.))
        self.assertEqual(REV6["ambient_range_c"],(-20.,70.))
        self.assertEqual(REV6["safe_off_up_to_ambient_c"],85.)
        self.assertEqual(REV6["optional_not_required"],(90.,.005))
    def test_5v2a_raw0p5_10v_combined_load_only_assumption(self):
        self.assertAlmostEqual(load_sensitivity(10)["main_input_a_hypothetical"],1.75)
        self.assertAlmostEqual(load_sensitivity(10)["5v_buck_heat_w_hypothetical"],2.5)
        self.assertAlmostEqual(load_sensitivity(32)["main_input_a_hypothetical"],.890625)
        self.assertTrue(load_sensitivity(10)["not_a_verified_joint_output_rating"])
    def test_58v_fuse_has_actual_maker_voltage_and_break_rating(self):
        m=FUSE_FAMILY_MANUFACTURER
        self.assertEqual(m["rating_dc_v"],58)
        self.assertEqual(m["interrupt_at_58v_dc_a"],1000)
        self.assertEqual(m["environment_c"],(-40.,125.))
        self.assertFalse(m["holder_plus_fuse_rated_for_ringing_beyond_58v"])
        self.assertEqual(FUSES["4A"].mpn,"0997004.WXN")
        self.assertEqual(FUSES["5A"].mpn,"0997005.WXN")
        self.assertAlmostEqual(FUSES["4A"].distributor_eur_net_1_10_100[0],.88)
    def test_manufacturer_fuse_hot_derating_at_exact_60_and_80C(self):
        table=fuse_guard(58.,30.,60.,1.75)
        self.assertEqual([r["mfr_typical_derated_current_a_at_exact_temperature"] for r in table],[2.2,2.9,3.7])
        self.assertTrue(all(r["carrying_load_below_tabulated_current"] for r in table))
        tab80=fuse_guard(58.,30.,80.,1.75)
        self.assertEqual([r["mfr_typical_derated_current_a_at_exact_temperature"] for r in tab80],[2,2.7,3.4])
        self.assertIsNone(fuse_guard(58.,30.,70.)[0]["mfr_typical_derated_current_a_at_exact_temperature"])
    def test_actual_datasheet_opening_times_not_magical_350ms(self):
        rows=fuse_opening_at_exact_maker_multipliers(FUSES["5A"])
        self.assertEqual(rows[1]["amps_at_exact_multiplier"],10)
        self.assertEqual(rows[1]["manufacturer_opening_time_s_max"],5)
        self.assertFalse(rows[1]["will_certainly_open_within_350ms"])
        self.assertTrue(rows[3]["will_certainly_open_within_350ms"])
        self.assertFalse(rows[3]["applies_to_OTHER_fault_current"])
    def test_58v_nominal_upstream_does_not_guarantee_58v_local(self):
        a=harness_ringing()
        self.assertAlmostEqual(a["induced_voltage_v_hypothetical"],20.)
        self.assertAlmostEqual(a["local_connector_peak_v_hypothetical"],78.)
        self.assertFalse(a["58V_fuse_system_rating_ok_under_this_scenario"])
        self.assertEqual(a["65V_VS_normal_operating_margin_v"],-13)
        self.assertFalse(a["manufacturer_clamp_test_proven"])
        with self.assertRaises(ValueError):harness_ringing(dt=0)
    def test_fuse_must_not_interrupt_more_voltage_than_its_rating(self):
        r=fuse_guard(58.1,10,60)[0]
        self.assertFalse(r["meets_DC_voltage_rating_in_this_scenario"])
        self.assertFalse(r["fuse_total_dc_arc_clearing_time_proven_for_fault"])
        self.assertTrue(fuse_guard(58.,2,60)[0]["fault_below_nominal_a_does_not_require_fuse_to_open"])
    def test_nonqualified_installation_had_nominal_clamp_but_uncontrolled_ringing(self):
        a=source_installation_check(78.,negative_min_v=-5.,fuse_break_v=78.,
                                    measured_generator_impedance_ohm=2.,
                                    measured_harness_inductance_h=1e-6,pulse_duration_s=.35)
        self.assertTrue(a["all_profile_parameters_recorded"])
        self.assertFalse(a["release_possible_on_complete_input_evidence"])
        no_r=source_installation_check(58.)
        self.assertFalse(no_r["release_possible_on_complete_input_evidence"])
        self.assertFalse(no_r["actual_installed_vehicle_pass"])
    def test_ov_threshold_must_work_at_32_and_off_by_36(self):
        a=ov_corner_gates(32.2,35.6,31.8,30.5)
        self.assertTrue(a["all_nominal_DC_corners_consistent"])
        self.assertFalse(a["trip_thermally_or_dynamically_proven"])
        self.assertFalse(ov_corner_gates(32.0,35.0,31.8)["normal_32v_on_possible"])
        self.assertFalse(ov_corner_gates(33,36.01,31.8)["shutdown_by_36v"])
        self.assertFalse(ov_corner_gates(33,35,32.2)["restart_at_stable_32v"])
    def test_below_fuse_short_can_be_thermal_hazard_even_at_32v(self):
        a=failed_silicon_power()
        self.assertLess(a["fault_a"],1.)
        self.assertGreater(a["local_350ms_energy_j"],10)
        self.assertFalse(a["5a_fuse_must_open"])
        b=failed_silicon_power(32.,seconds=10.)
        self.assertGreater(b["local_power_w"],9.)
        self.assertGreater(b["local_350ms_energy_j"],90.)
    def test_fram_recovery_not_full_FAT32_cleanliness(self):
        a=fram_journal_model(100,1,bank_a_valid=True,bank_b_valid=False)
        self.assertEqual(a["loss_window_upper_bound_ms_ONLY_if_atomic_protocol_works"],101)
        self.assertTrue(a["one_corrupt_slot_can_be_recovered"])
        self.assertFalse(a["full_filesystem_repair_guaranteed"])
        self.assertFalse(fram_journal_model(100,1,bank_a_valid=False,bank_b_valid=False)["at_least_one_valid_slot"])
    def test_priority_matrix_no_fake_release(self):
        self.assertGreaterEqual(len(fmea()),14)
        self.assertGreaterEqual(len(matrix()),12)
        self.assertTrue(all(x[0] in ("P0","P1","P2") for x in fmea()))
        self.assertEqual({z[0] for z in fmea()},{"P0","P1","P2"})
        self.assertTrue(all(not v for v in report()["RELEASE_GATES"].values()))
if __name__=="__main__":
    unittest.main()
