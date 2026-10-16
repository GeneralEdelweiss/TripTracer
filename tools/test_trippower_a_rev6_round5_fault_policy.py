#!/usr/bin/env python3
"""Round5 falsifiable independent regressions on real repository source (no hardware PASS)."""
import csv
import unittest
from pathlib import Path
from trippower_a_rev6_round5_fault_policy import study,rtop_corner,uvlo_edges,inductor_ripple

ROOT=Path("hardware/modules/TripPower_REV6_A")
SCHEMA=ROOT/"01_TPS26631_REV6_FACTORY_OVP.kicad_sch"
ORDER=ROOT/"REV6_A_FACTORY_OVP_23_PART_ORDER_BOM_2026-10-16.csv"

class Round5FaultAndTopology(unittest.TestCase):
 def test_factory_ovp_recovery_and_trip_corner(self):
    x=study()
    self.assertGreater(x["OVP_factory_rising_min_max_V"][0],32)
    self.assertLess(x["OVP_factory_rising_min_max_V"][1],36)
    self.assertGreater(x["OVP_factory_falling_min_max_V"][0],32)
    self.assertAlmostEqual(x["OVP_32V_recovery_margin_min_V"],.7)
 def test_vendor_min300k_including_85C(self):
    for t in (-20,70,85):
        low,high=rtop_corner(t)
        self.assertGreaterEqual(low,300000)
        self.assertLess(high,350000)
 def test_a24_is_optional_because_both_programmed_thresholds_below_ten(self):
    for temp in (-20,70,85):
        for bot in (56000,68000):
            rise=uvlo_edges(bot,temp,True)
            fall=uvlo_edges(bot,temp,False)
            self.assertLess(rise[1],10)
            self.assertLess(fall[1],rise[1])
    self.assertFalse(study()["A24_required"])
 def test_pgth_low_is_not_free_2x_current_or_tps_pgood(self):
    x=study()
    self.assertEqual(x["mode"],"MODE12_GND_AUTO_RETRY")
    self.assertFalse(x["tps_2x_IOL_pulse_enabled"])
    self.assertIn("LOW",x["pgth"])
    self.assertEqual(x["retry_TSD_ms_min_typ_max"],[500,648,800])
 def test_latch_has_no_automatic_fault_recovery_without_explicit_reset(self):
    self.assertIn("requires_SHDN_or_UVLO_reset",study()["latch_alternative"])
 def test_hard_short_auto_retry_remains_unqualified(self):
    x=study()
    for k in ("reverse_short_or_repeated_auto_retry_safe_tested","RAW_selective_fault_limit_present",
              "ambient_85C_safe_OFF_present","58V_350ms_at_IC_pads_measured",
              "A23_10V_full_load_verified","host_to_A23_schematic_interface_completed"):
        self.assertFalse(x[k],k)
 def test_buck_15uH_and_3x22uF_is_only_nominal_reference(self):
    self.assertAlmostEqual(study()["buck_fbt_100k_fbb_24k9_nominal_v"],5.016064257,places=5)
    for v in (10,32):
        self.assertLess(inductor_ripple(v)["Ipeak_A_ideal"],2.5)
    self.assertFalse(study()["min_effective_output_C_total_verified"])
 def test_no_historical_ovp_text_left_in_a23_real_sheet(self):
    s=SCHEMA.read_text()
    for obsolete in ("OV <=36 via R201..203","OVP rising 32.223..33.880V",
                     "falling 29.864..31.833V","32V static hysteresis margin0.167V"):
        self.assertNotIn(obsolete,s)
    for must in ("PGTH16=GND disables fast restart","PGOOD HIGH/2x IOL burst",
                 "rising33.2..35.4V/falling32.7..35.0V",
                 "R201=330k UVLO/no external rising divider"):
        self.assertIn(must,s)
 def test_main_and_host_hierarchies_are_separate_with_real_pages(self):
    a=(ROOT/"TripPower_REV6_A_FACTORY_OVP.kicad_sch").read_text()
    host=Path("hardware/kicad/TripTracer_V1.kicad_sch").read_text()
    input_root=Path("hardware/kicad/01_Eingangsschutz.kicad_sch").read_text()
    for name in ("01_TPS26631_REV6_FACTORY_OVP.kicad_sch","02_5V_LMR38020_FACTORY_OVP.kicad_sch"):
        self.assertIn(name,a)
    self.assertIn("01_Eingangsschutz.kicad_sch",host)
    for name in ("01H_ACC_HOLD_GATE.kicad_sch","01I_LM74800_INPUT.kicad_sch"):
        self.assertIn(name,input_root)
    self.assertNotIn("TripPower_REV6_A_FACTORY_OVP.kicad_sch",host)
 def test_native_order_bom_23_and_no_soldered_one_shot_fuse(self):
    rows=list(csv.DictReader(ORDER.open()))
    parts=[r for r in rows if r["ref"]!="SUMMARY_23_FITTED"]
    self.assertEqual(len(parts),23)
    self.assertEqual(len({r["ref"] for r in parts}),23)
    self.assertFalse(any(r["ref"].startswith("F") for r in parts))
    self.assertEqual(next(r["mpn"] for r in parts if r["ref"]=="R201"),"AC1206FR-07330KL")
    self.assertEqual(next(r["mpn"] for r in parts if r["ref"]=="U201"),"TPS26631PWPR")
    for col,total in (("eur_exVAT_1",20.2570),("eur_exVAT_10",13.5610),("eur_exVAT_100",10.6266)):
        self.assertAlmostEqual(sum(float(r[col]) for r in parts),total,places=4)

if __name__=="__main__":
 unittest.main()
