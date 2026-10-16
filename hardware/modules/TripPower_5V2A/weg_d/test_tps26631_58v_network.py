"""Network sensitivity regression only; not TI macro validation or bench evidence."""
import unittest
from dataclasses import replace
from tps26631_58v_network import P, src, gate, simulate, matrix

class TripPower58V(unittest.TestCase):
    def test_source_profile_and_350ms_hold(self):
        p=P()
        self.assertAlmostEqual(src(0.,p),32.)
        self.assertAlmostEqual(src(p.t0+p.edge+.200,p),58.)
        self.assertAlmostEqual(src(p.t0+p.edge+p.hold+p.edge,p),32.)
    def test_10V_start_dynamic(self):
        r=simulate(P(mode="start",v0=0,v1=10))
        self.assertLess(r["peak"]["TPS_IN_SYS_V"]["max"],20)
        self.assertGreater(r["peak"]["LMR_VIN_V"]["max"],7)
    def test_36V_ramp(self):
        r=simulate(P(v1=36.,hold=.0004))
        self.assertGreater(r["peak"]["TPS_IN_SYS_V"]["max"],34.)
    def test_58V_nominal_bounded_assumption(self):
        r=simulate(P())
        self.assertFalse(r["sys_ge67"])
        self.assertGreater(r["peak"]["TPS_IN_SYS_V"]["max"],58.)
    def test_58V_high_l_low_ceff_crosses_67_scenario(self):
        # Existence proof in this approximate network, NOT a predicted real truck.
        p=P(cable_l=5e-6,c_sys=.1e-6,off_delay=14e-6,buck_w=5,raw_a=0)
        r=simulate(p)
        self.assertTrue(r["sys_ge67"])
    def test_input_fet_short_not_same_as_internal_short(self):
        a=simulate(P(reverse_short=True))
        b=simulate(P(efuse_short=True))
        self.assertGreater(a["peak"]["TPS_IN_SYS_V"]["max"],57)
        self.assertGreater(b["peak"]["LMR_VIN_V"]["max"],45)
    def test_32V_recovery_gate_not_guaranteed(self):
        p=P()
        self.assertFalse(simulate(p)["restart_at_32_possible"])
        self.assertEqual(gate(p.t0+p.edge+p.hold+p.edge+.001,p),0)
    def test_enumerate_faults_and_cases(self):
        r=simulate(P(v0=32,v1=32,short_at=.15e-3))
        self.assertTrue(r["peak"]["TPS_IN_SYS_V"]["max"]>0)
        u=simulate(P(mode="unplug",v0=32,v1=0,edge=1e-6))
        self.assertTrue(u["peak"]["LMR_VIN_V"]["max"]>0)
    def test_matrix_has_all_axes(self):
        x=matrix()
        self.assertEqual(len(x),4*3*3*2*2)
        self.assertTrue(any(z["exceeds60"] for z in x))
        self.assertTrue(any(not z["exceeds60"] for z in x))

if __name__=="__main__":
    unittest.main()
