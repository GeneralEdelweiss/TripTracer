#!/usr/bin/env python3
"""Weg C 16-Oct-2026: repeatable TPS26600 vs TPS26631 manufacturer gate checks.

Manufacturer source: TI SLVSDG2G (TPS2660) pages 6,7,38; TI SLVSE94G
(TPS2663) pages 5,6,7. These are screening calculations, NOT safety testing.
"""
from dataclasses import dataclass
from itertools import product
from math import sqrt
import unittest

@dataclass(frozen=True)
class Candidate:
    name: str
    V_abs: float
    V_oper: float
    ovp_min: float
    ovp_max: float
    ovp_falling_max: float
    leak_max_amp: float
    fwd_diode: bool
    r_top_ohm: float
    r_bot_ohm: float

C00 = Candidate("TPS26600",62.,60.,1.170,1.225,1.125,100e-9,False,100000.,3740.)
C31 = Candidate("TPS26631",67.,60.,1.176,1.224,1.150,150e-9,True,100000.,3780.)

def worst_ovp(c:Candidate, tolerance=.001):
    """Return rising min/max, falling min/max, in IC VIN domain.

    Nodal relation Vsource=Vref*(1+Rtop/Rbottom)+I_OVP*Rtop.
    Independent extreme R-tolerance and signed leakage; 0.1% required.
    """
    tops=(c.r_top_ohm*(1-tolerance),c.r_top_ohm*(1+tolerance))
    bottoms=(c.r_bot_ohm*(1-tolerance),c.r_bot_ohm*(1+tolerance))
    leak=(-c.leak_max_amp,c.leak_max_amp)
    rise=[ref*(1+t/b)+i*t for ref,t,b,i in product(
        (c.ovp_min,c.ovp_max), tops,bottoms,leak)]
    fall_min=[c.ovp_falling_max*(1+t/b)+i*t for t,b,i in product(tops,bottoms,leak)]
    return min(rise),max(rise),min(fall_min),max(fall_min)

def worst_eFuse_input_v(v_connector=58., series_diode_drop=0., current_a=2.35,
                       effective_cap_uF=1., input_inductance_uH=1.):
    """TI TPS2660 DS 11.1: Vs=Vin+I sqrt(Lin/Cin).  Undamped energy
    approximation in micro-units. NOT exact under rectangular load-dump,
    harmonics or nonlinear cap energy / FET dynamics.
    """
    return v_connector-series_diode_drop+current_a*sqrt(input_inductance_uH/effective_cap_uF)

def permitted_inductance_uH(c:Candidate, cap_eff_uF=1., I_a=2.35, target="absolute"):
    ceiling=c.V_abs if target=="absolute" else c.V_oper
    margin=ceiling-58.
    return (margin/I_a)**2*cap_eff_uF

def approx_hot_current(v=10., out_w=10., raw_a=.5, eta=.85, r_on=.25):
    """Solve I = RAW + Pout / [eta*(Vin - I*Ron)] for integrated TPS26600.
    Ron .25ohm maximum specified across -40..125C, not measured at 60C.
    No startup current included.
    """
    b=v+raw_a*r_on
    discr=b*b-4*r_on*(v*raw_a+out_w/eta)
    if discr<0:return None
    I=(b-sqrt(discr))/(2*r_on)
    return I,v-I*r_on,I*I*r_on

def die_temp_at_60(loss_w,thermal_resistance=38.6):
    """TI TPS26600 PWP16 JEDEC thetaJA 38.6 K/W, not a PCB temperature guarantee."""
    return 60.+thermal_resistance*loss_w

class Tests(unittest.TestCase):
    def test_specs_exact(self):
        self.assertEqual((C00.V_oper,C00.V_abs,C31.V_abs),(60.,62.,67.))
    def test_c00_divider_precision_0p1pct_still_fails_32v_restart(self):
        rmin,rmax,_fmin,fmax=worst_ovp(C00)
        self.assertGreater(rmin,32.)
        self.assertLess(rmax,36.)
        self.assertLess(fmax,32.) # CORRECTION: this is an automatic FAIL for 32V re-enable, not PASS
    def test_c31_divider_precision_0p1pct_still_fails_32v_restart(self):
        rmin,rmax,_fmin,fmax=worst_ovp(C31)
        self.assertGreater(rmin,32.)
        self.assertLess(rmax,36.)
        self.assertGreater(fmax,31.5) # MIN falling may be far lower; cannot infer restart
        self.assertLess(fmax,32.)
    def test_1percent_tolerance_c00_does_not_guarantee_32vin_operating(self):
        self.assertLess(worst_ovp(C00,tolerance=.01)[0],32.)
    def test_1percent_tolerance_c31_does_not_guarantee_32vin_recovery(self):
        self.assertGreater(worst_ovp(C31,tolerance=.01)[3],32.)
    def test_c31_schottky_recovery_is_not_guaranteed_at_32v(self):
        max_falling=worst_ovp(C31)[3]
        max_allowable_recovery_diode_vf=32.-max_falling
        self.assertLess(max_allowable_recovery_diode_vf,0.352)
        self.assertGreater(max_allowable_recovery_diode_vf,0.35)
    def test_c00_operating_margin_even_tighter_than_abs(self):
        self.assertAlmostEqual(permitted_inductance_uH(C00,1,2.35,"absolute"),(4/2.35)**2)
        self.assertAlmostEqual(permitted_inductance_uH(C00,1,2.35,"operating"),(2/2.35)**2)
    def test_c00_transient_model_can_exceed_62abs(self):
        self.assertGreater(worst_eFuse_input_v(current_a=2.35,
                              effective_cap_uF=.47,input_inductance_uH=2),62.)
    def test_c31_larger_abs_envelope_but_same_60v_operating(self):
        self.assertGreater(C31.V_abs,C00.V_abs)
        self.assertEqual(C31.V_oper,C00.V_oper)
    def test_c00_hot_losses_not_replacing_pcb_thermals(self):
        I,vout,p=approx_hot_current()
        self.assertGreater(I,1.6)
        self.assertLess(I,2.0)
        self.assertLess(die_temp_at_60(p),110.)
    def test_2p35_short_fault_not_half_amps_raw_limit(self):
        self.assertGreater(2.35/.5,4.)
    def test_factory_tps2660_trips_under_32v_in_worst_case(self):
        self.assertLess(31.,32.) # TI factory OVP rising min31 V; external divider essential.
    def test_factory_tps26631_falling_above_32v(self):
        self.assertGreater(32.7,32.) # TI falling min 32.7V; manual divider essential.

if __name__ == "__main__":
    for dev in (C00,C31):
        print(dev.name,"OVP 0.1% (rise min/max; fall min/max) IC domain=",worst_ovp(dev))
        print(dev.name,"OVP 1.0% (rise min/max; fall min/max) IC domain=",worst_ovp(dev,.01))
        print(dev.name,"Lmax(abs) @58V,2.35A, Ceff=1uF:",round(permitted_inductance_uH(dev),3),"uH")
        print(dev.name,"Lmax(oper) @58V,2.35A, Ceff=1uF:",round(permitted_inductance_uH(dev,target="operating"),3),"uH")
    print("TPS26600 stress 58V, 2.35A, 2uH, Ceff.47uF =>",
          round(worst_eFuse_input_v(effective_cap_uF=.47,input_inductance_uH=2.),2),"V at pad")
    print("TPS26600 full nominal 10W plus 0.5A RAW, eta85%, Ron max 250mohm:",
          approx_hot_current(),"TJ proxy 60C",die_temp_at_60(approx_hot_current()[2]))
    print("This script proves NEITHER 58V-pad-max NOR a release-qualified REV6 design.")
