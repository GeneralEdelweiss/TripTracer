import unittest
from rev6_round8_compare import PARTS,vin_current,ring_volts,margins,conduction_w,semiconductors_eur

class Rev6Round8(unittest.TestCase):
 def test_current_10V(self):
    self.assertAlmostEqual(vin_current(),1.75)
 def test_thermal_conduction_typical_only(self):
    self.assertAlmostEqual(conduction_w(1.75,.15),.459375)
    self.assertAlmostEqual(conduction_w(1.75,.031),.0949375)
 def test_pin_headroom_at_58V(self):
    self.assertEqual([margins(58,p)[1] for p in PARTS],[9,4,42])
 def test_ringing_scenarios(self):
    self.assertAlmostEqual(ring_volts(.5,2,1),1)
    self.assertAlmostEqual(ring_volts(1,2,.5),4)
    self.assertAlmostEqual(ring_volts(1,5,.1),50)
    self.assertLessEqual(margins(62,PARTS[1])[1],0)
    self.assertLess(margins(108,PARTS[2])[1],0)
 def test_frontend_costs(self):
    self.assertAlmostEqual(semiconductors_eur([3.87,3.78,.292]),7.942)
    self.assertAlmostEqual(semiconductors_eur([7.57,2.93,2.93]),13.43)
 def test_input_validation(self):
    with self.assertRaises(ValueError): vin_current(vin=0)
    with self.assertRaises(ValueError): ring_volts(1,2,0)

if __name__=="__main__":unittest.main()
