"""Check the TripPower-D model arithmetic, NOT circuit/ISO qualification."""
import math
import unittest
from load_dump_scenarios import scenario, source_voltage, tvs_short, inductive_spike

class ScenarioTest(unittest.TestCase):
    def test_constant_pulse(self):
        s = scenario(3.5, "constant", steps=1000)
        self.assertAlmostEqual(s.i_peak_a, (200-61.2)/3.5, places=6)
        self.assertAlmostEqual(s.energy_j, 61.2*(200-61.2)/3.5*.35, places=6)

    def test_energy_ranking(self):
        for ri in (1,3.5,4.5,6):
            self.assertGreater(scenario(ri,"constant").energy_j,
                               scenario(ri,"linear_to_28").energy_j)
            self.assertGreater(scenario(ri,"linear_to_28").energy_j,
                               scenario(ri,"exp_to_10pct").energy_j)
        self.assertGreater(scenario(3.5,"constant").energy_j,
                           scenario(4.5,"constant").energy_j)

    def test_pulse_ends(self):
        self.assertAlmostEqual(source_voltage(.35,"linear_to_28"),28)
        self.assertAlmostEqual(source_voltage(.35,"exp_to_10pct"),45.2)
        self.assertAlmostEqual(source_voltage(0,"constant"),200)

    def test_short(self):
        s = tvs_short(3.5)
        self.assertAlmostEqual(s["current_a"],200/3.5)
        self.assertAlmostEqual(s["source_i2t_a2s"],(200/3.5)**2*.35)

    def test_inductive_spike(self):
        self.assertAlmostEqual(inductive_spike(1,42.8,10),4.28)
        self.assertAlmostEqual(inductive_spike(.5,42.8,1),21.4)

    def test_rejects_incomplete_models(self):
        with self.assertRaises(ValueError):
            scenario(0,"constant")
        with self.assertRaises(ValueError):
            source_voltage(.1,"unknown")

if __name__ == "__main__":
    unittest.main()
