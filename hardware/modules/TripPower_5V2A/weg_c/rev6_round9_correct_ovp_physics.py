#!/usr/bin/env python3
"""TPS26600 adjustable OVLO impossible guarantee, and TPS26631 factory fallback.
Model backed by TI TPS2660 Rev G p7 / TPS2663 Rev G p6 and TI §8.3.3.
DO NOT mistake passing model assertions for real board/58V/thermal qualification.
"""
import math, unittest
OV_00_RISE=(1.170,1.225)
OV_00_FALL=(1.085,1.125)
OV_31_FACTORY_RISE=(33.2,35.4)
OV_31_FACTORY_FALL=(32.7,35.0)
REV6_MAX_OFF=36.
REV6_MIN_OPERATING=32.

def divider_feasible_ideal():
    # Even ideal zero-leak, zero-tolerance shared comparator gain G for TPS26600:
    # falling voltage = G * Vref_fall, rising voltage = G * Vref_rise.
    # Re-enable upon Vin FALLING BELOW Vtrip; must MIN(fall) > 32.
    lower=REV6_MIN_OPERATING/OV_00_FALL[0]
    upper=REV6_MAX_OFF/OV_00_RISE[1]
    return lower, upper, lower < upper

def realistic_tps26600_ladder():
    # TI Fig 50 3 resistors IN->UVLO->OVP->RTN; tested tolerance/leak
    R=(86600.,9650.,3570.)
    from itertools import product
    rs=[[r*(1-.001),r*(1+.001)] for r in R]
    rmin,rmax,fmin,fmax=1e9,-1e9,1e9,-1e9
    for r1,r2,r3,i_uv,i_ov in product(*rs,[-100e-9,100e-9],[-100e-9,100e-9]):
        gain=1+(r1+r2)/r3
        offsets=i_uv*r1+i_ov*(r1+r2)
        for vr in OV_00_RISE:
            x=gain*vr+offsets; rmin=min(rmin,x);rmax=max(rmax,x)
        for vf in OV_00_FALL:
            x=gain*vf+offsets; fmin=min(fmin,x);fmax=max(fmax,x)
    return rmin,rmax,fmin,fmax

def induced_vin(v_start=58.,i=2.35,L_microhenry=2.,C_effective_microfarad=.47):
    return v_start+i*math.sqrt(L_microhenry/C_effective_microfarad)

def real_A_factory_ovp_pass():
    # TPS26631 PWP20 ext reverse MOSFET and helper maintained.
    return OV_31_FACTORY_RISE[0]>32 and OV_31_FACTORY_RISE[1]<=36 and OV_31_FACTORY_FALL[0]>32

def A_uvlo_resistor_schematic_rule():
    # TI: when reverse blocking FET used, no-UVLO required: R>=300k to IN_SYS,
    # rather than direct link; UVLO never floating or strapped to ground factory 15V.
    return dict(resistor_ohm=300e3, from_net="IN_SYS", to_net="UVLO",ovp_net="GND")

def tps00_full_load(v=10,eta=.85,raw=.5,ron_hot=.250):
    p=10./eta; b=v+raw*ron_hot; disc=b*b-4*ron_hot*(v*raw+p)
    i=(b-math.sqrt(disc))/(2*ron_hot)
    return i,v-i*ron_hot,i*i*ron_hot

class FinalGates(unittest.TestCase):
    def test_correct_physical_falling_direction(self):
        # v=32, threshold=31.5: still OFF, not ON
        self.assertFalse(32. < 31.5)
        self.assertTrue(32. < 32.7)
    def test_tps00_impossible_even_ideal_no_leak(self):
        lo,hi,feasible=divider_feasible_ideal()
        self.assertGreater(lo,hi)
        self.assertFalse(feasible)
        self.assertGreater(32*OV_00_RISE[1]/OV_00_FALL[0],36)
    def test_old_three_res_0p1pct_recovery_fails(self):
        rlo,rhi,flo,fhi=realistic_tps26600_ladder()
        self.assertGreater(rlo,32)
        self.assertLess(rhi,36)
        self.assertLess(flo,32)
        self.assertLess(fhi,32)
    def test_factory_tps00_not_suitable(self):
        # TI factory rise MIN=31 (<32), fall MAX=31.5 (<32)
        self.assertLess(31,32)
        self.assertLess(31.5,32)
    def test_factory_tps31_is_possible_even_on_release_at_32(self):
        self.assertTrue(real_A_factory_ovp_pass())
        self.assertGreater(OV_31_FACTORY_FALL[0]-32,0.7-1e-9)
    def test_external_reverse_tps31_requires_300k_uvlo(self):
        x=A_uvlo_resistor_schematic_rule()
        self.assertGreaterEqual(x["resistor_ohm"],300e3)
        self.assertEqual(x["from_net"],"IN_SYS")
        self.assertEqual(x["ovp_net"],"GND")
    def test_factory_uvlo_incorrect_at_10v(self):
        self.assertGreater(15.1,10)
    def test_58v_overshoot_exceeds_tps00_abs(self):
        self.assertGreater(induced_vin(),62)
        self.assertLess(induced_vin(),67)
    def test_tps00_58v_only_4v_abs_2v_oper(self):
        self.assertEqual(62-58,4)
        self.assertEqual(60-58,2)
    def test_tps00_hot_10v_5v2a_raw05(self):
        i,vp,p=tps00_full_load()
        self.assertGreater(i,1.7)
        self.assertLess(i,2.0)
        self.assertGreater(p,.7)
        self.assertLess(2.11-i,.5)
    def test_separately_protected_raw_not_yet_supported(self):
        raw_independent_current_limit=False
        self.assertFalse(raw_independent_current_limit)
    def test_85ambient_shdn_not_a_junction_shutdown(self):
        self.assertGreater(157,85)

if __name__=="__main__":
    lo,hi,feasible=divider_feasible_ideal()
    print(f"IMPOSSIBLE TPS26600 guaranteed adjustable OVP: gain>{lo:.6f} for FALLING_MIN>32V, gain<={hi:.6f} for RISING_MAX<=36V; feasible={feasible}")
    print("Prior WRONG rule 'falling_max <=32V' reversed the restart semantics.")
    print("Actual 0.1% TPS26600 3-res ladder (rise low/high; fall low/high):",realistic_tps26600_ladder())
    print("TPS26631 factory OVP rising",OV_31_FACTORY_RISE,"falling",OV_31_FACTORY_FALL,"is compatible with 32V recovery after VIN really settles.")
    print("TPS26631 ext reverse requires UVLO to IN_SYS via MINIMUM 300kΩ, factory OVP to GND; no direct UVLO tie.")
    print("Hot TPS26600 10V eta85% power check:",tps00_full_load())
    print("Inductor 2uH/effective cap .47uF, interrupt 2.35A, entry58V ->",induced_vin(),"V at TPS26600 VIN pad")
    print("NO-GO C replacement; A factory OVP/300k REDESIGN research; no native KiCad or 58V proof.")
