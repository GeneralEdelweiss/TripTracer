"""No-vendor-SPICE A23 three-node M8 boundary regression checks."""
from dataclasses import replace
import unittest

from tps26631_a23_after_m8_linear_nodes import Params, source, load, simulate

class A23LocalNetwork(unittest.TestCase):
    def test_m8_boundary_never_exceeds_58(self):
        p=Params()
        self.assertEqual(source(p.rise_s,p),58)
        self.assertEqual(source(p.rise_s+p.plateau_s,p),58)
        self.assertAlmostEqual(source(p.rise_s+p.plateau_s+p.fall_s,p),32)

    def test_a23_fixed_rise_nominal_sensitivity(self):
        x=simulate(Params())
        self.assertAlmostEqual(x['peaks']['pre_tps_in_v'],59.98721,delta=0.03)
        self.assertLess(x['peaks']['post_in_sys_v'],x['peaks']['pre_tps_in_v'])
        self.assertFalse(x['over_recommended_60_v'])

    def test_fast_edge_can_exceed_absolute_max_in_model(self):
        x=simulate(replace(Params(),rise_s=0.2e-6))
        self.assertGreater(x['peaks']['pre_tps_in_v'],67)
        self.assertTrue(x['at_or_over_absmax_67_v'])

    def test_changed_line_resistance_damps_fast_edge_not_a_part_suggestion(self):
        base=simulate(replace(Params(),rise_s=0.2e-6))
        higher=simulate(replace(Params(),rise_s=0.2e-6,r_after_m8_ohm=0.35))
        self.assertLess(higher['peaks']['pre_tps_in_v'],base['peaks']['pre_tps_in_v'])

    def test_input_short_hypothesis_does_not_claim_ovp_isolation(self):
        x=simulate(replace(Params(),mode='fet_short',load_a=1.75))
        self.assertGreater(x['peaks']['abs_line_current_a'],0)

    def test_trip_hypothesis_has_explicit_assumed_delay(self):
        p=replace(Params(),mode='assumed_trip',load_a=3.0)
        self.assertEqual(load(0,p),3.0)
        self.assertEqual(load(100e-6,p),0)
        self.assertIn('NOT vendor',simulate(p)['method'])

    def test_bad_units_rejected(self):
        with self.assertRaises(ValueError):
            simulate(replace(Params(),c201_eff_f=0))

if __name__=='__main__':
    unittest.main()
