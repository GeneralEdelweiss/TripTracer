import unittest
from rev6_limits import ov_bounds, sense_trip, inductive_term,buck_input_current

class Rev6Limits(unittest.TestCase):
    def test_precision_divider_passes_static(self):
        b=ov_bounds(.0025)
        self.assertLess(b.ov_rising_max,36)
        self.assertGreater(b.ov_falling_min,32)
        self.assertGreater(b.ov_rising_min,32)
    def test_one_percent_divider_fails(self):
        b=ov_bounds(.01)
        self.assertTrue(b.ov_rising_max>36 or b.ov_falling_min<=32)
    def test_sense_limits(self):
        mi,ty,ma=sense_trip()
        self.assertAlmostEqual(ty,10/3)
        self.assertAlmostEqual(mi,8/3)
        self.assertAlmostEqual(ma,4)
    def test_current(self):
        self.assertAlmostEqual(buck_input_current(),1.75)
    def test_ring_sensitivity(self):
        self.assertAlmostEqual(inductive_term(.5,2,1),1.)
        self.assertAlmostEqual(inductive_term(1,5,.1),50.)
if __name__=="__main__":unittest.main()
