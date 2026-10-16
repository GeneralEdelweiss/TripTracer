"""Arithmetic and passive-network tests, NOT TI manufacturer PSpice or hardware tests."""
import unittest
from dataclasses import replace
from tps26631_ti_eq14_passive_step import InputCase,ti_inductive_spike,required_cap_uf,step_peak,sweep

class Ti58VEvidence(unittest.TestCase):
    def test_eq14(self):
        self.assertAlmostEqual(ti_inductive_spike(58,1.75,.8,.5),58+1.75*(.8/.5)**.5)
        self.assertAlmostEqual(required_cap_uf(58,60,1.75,.8),.6125)
    def test_boundary_protects_no_monotone_claim(self):
        self.assertGreater(required_cap_uf(58,60,3,5),required_cap_uf(58,67,3,5))
    def test_fast_edge(self):
        self.assertTrue(step_peak(InputCase(rise_us=.2))['reaches_TI_67V_abs'])
    def test_slow_edge_smaller(self):
        self.assertLess(step_peak(InputCase(rise_us=20))['pin_peak_V'],
                        step_peak(InputCase(rise_us=.2))['pin_peak_V'])
    def test_onboard_boundary_fast_m8(self):
        a=step_peak(InputCase(l_uh=.05,c_uf=.5,r_ohm=.08,rise_us=1.))
        self.assertLess(a['pin_peak_V'],67.)
        b=step_peak(InputCase(l_uh=.05,c_uf=.5,r_ohm=.08,rise_us=.2))
        self.assertGreater(b['pin_peak_V'],67.)
    def test_passive_model_independent_of_load(self):
        p=InputCase()
        self.assertEqual(step_peak(p)['pin_peak_V'],step_peak(replace(p,current_a=0))['pin_peak_V'])
    def test_sweep_size(self):
        self.assertEqual(len(sweep()),6*4*3*4)
    def test_truthful_output(self):
        self.assertEqual(step_peak(InputCase())['model'],'PASSIVE_RLC_SOURCE_EDGE_ONLY_TI_MACRO_NOT_USED')
    def test_validation(self):
        with self.assertRaises(ValueError):step_peak(InputCase(c_uf=0))
        with self.assertRaises(ValueError):required_cap_uf(58,58,3,1)
if __name__=="__main__":
    unittest.main()
