#!/usr/bin/env python3
"""TripPower C Round10: independent A23/A24 TPS26631 vendor calculation ONLY.

TI TPS2663 Rev G §8.3.3, §8.3.4, §9.4:
- factory OVP enabled by OVP=GND, rising 33.2..35.4, falling 32.7..35.0.
- if UVLO not needed tie UVLO to IN_SYS, BUT when reverse protection present
  at least 300k resistor BETWEEN IN_SYS and UVLO.
- if explicit undervoltage cutoff desired a 330k top resistor may feed UVLO,
  68k lower resistor from UVLO to GND, with trip Vref at 1.176..1.224 rising.

This model shows comparator margins. It does not model actual reverse MOSFET,
brown-out/start current, PCB parasitics, eFuse local 58V/60V absolute, or
temperature/RAW safety; KiCad/ERC and physical tests MUST be done by Weg A.
"""
import unittest
from itertools import product

R_TOL=0.01    # ±1 percent vendor resistor
TCR=100e-6    # vendor ±100ppm/K
DELTAT=60     # bounding 25..-20/+85 => 60K (conservative)
IUVLO=150e-9  # TI UVLO input signed leakage +/-150nA
RTOP=330000.
RBOT=68000.
OVP_RISE=(33.2,35.4)
OVP_FALL=(32.7,35.0)
UV_RISE=(1.176,1.224)
UV_FALL=(1.09,1.15)
UVLO_SELECT_MIN=0.18 # factory select when UVLO near 0V, not our case
EFUSE_IN_OPER_MIN=4.5
EFUSE_IN_OPER_MAX=60.
UVLO_IN_OPER_MAX=60.
UVLO_ABS_MAX=67.

def resistor_bounds(r):
    fmin=(1-R_TOL)*(1-TCR*DELTAT)
    fmax=(1+R_TOL)*(1+TCR*DELTAT)
    return r*fmin,r*fmax

def one_res_pin_min_at_vin(vin_sys):
    # signed pin leakage worst case through 330k towards IN_SYS
    return vin_sys-IUVLO*resistor_bounds(RTOP)[1]

def one_res_pin_max_at_vin(vin_sys):
    return vin_sys+IUVLO*resistor_bounds(RTOP)[1]

def two_res_threshold_bounds(references):
    vals=[]
    for rt,rb,iref,vref in product(resistor_bounds(RTOP),resistor_bounds(RBOT),(-IUVLO,IUVLO),references):
        # At trip: VIN_sys=Vref*(1+Rt/Rb)+ I_input*Rt
        vals.append(vref*(1+rt/rb)+iref*rt)
    return min(vals),max(vals)

def one_res_minimum_complies():
    return resistor_bounds(RTOP)[0]>=300000.

def one_res_off_leakage_current():
    # Series connection to high-impedance sense node; no standing divider current
    return IUVLO

def two_res_off_divider_current_at24():
    return 24/(RTOP+RBOT)

def max_reverse_uvlo_series_current(vsys_reverse=-60.,vsense_clamp=-.3):
    # crude worst external injection through min resistor; no internal diode model
    return (vsense_clamp-vsys_reverse)/resistor_bounds(RTOP)[0]

class TPS26631Qualify(unittest.TestCase):
    def test_vendor_factory_ovp_full_window(self):
        self.assertGreater(OVP_RISE[0],32)
        self.assertLess(OVP_RISE[1],36)
        self.assertGreater(OVP_FALL[0],32) # correct direction on OV recovery!
        self.assertLess(32,OVP_FALL[0])
    def test_reject_inverted_old_c_rule(self):
        self.assertFalse(OVP_FALL[1]<=32)
    def test_nominal_300k_1pct_is_below_TI_min_at_tolerance(self):
        self.assertLess(300000*(1-R_TOL),300000)
    def test_330k_1pct_100ppm_remains_above_300k(self):
        self.assertTrue(one_res_minimum_complies())
    def test_one_res_at_10v_is_far_above_uvlo_comparator_min(self):
        self.assertGreater(one_res_pin_min_at_vin(10), UV_RISE[1])
    def test_one_res_58v_pin_stress_depends_on_vin_sys_actual(self):
        self.assertLess(one_res_pin_max_at_vin(58),UVLO_IN_OPER_MAX)
        self.assertLess(EFUSE_IN_OPER_MAX-58,3) # ONLY 2V, no pad-margin proof
    def test_330k_reverse_input_clamp_current_is_small_model(self):
        self.assertLess(max_reverse_uvlo_series_current(),0.0002)
    def test_two_res_68k_uv_rising_below_10v(self):
        m,M=two_res_threshold_bounds(UV_RISE)
        self.assertGreater(m,EFUSE_IN_OPER_MIN)
        self.assertLess(M,10)
    def test_two_res_uv_falling_hysteresis(self):
        r0,r1=two_res_threshold_bounds(UV_RISE)
        f0,f1=two_res_threshold_bounds(UV_FALL)
        self.assertLess(f1,r1)  # Each correlated device corner has rising>falling; independent envelopes may overlap
    def test_battery_off_divider_cost(self):
        self.assertLess(two_res_off_divider_current_at24(),0.0001)
        self.assertLess(one_res_off_leakage_current(),two_res_off_divider_current_at24())
    def test_ovp_abs_58v_scope_remains_blocked(self):
        self.assertLess(EFUSE_IN_OPER_MAX-58,3)
        self.assertLess(UVLO_ABS_MAX-58,10)
    def test_no_board_fuse_or_native_design_new(self):
        native_kicad_design_new=False
        populated_tripPower_fuse_parts=0
        self.assertFalse(native_kicad_design_new)
        self.assertEqual(populated_tripPower_fuse_parts,0)

if __name__ == '__main__':
    print('Manufacturer OVP rising',OVP_RISE,'falling',OVP_FALL,'32V restart: PASS comparator threshold only')
    print('1R 330k Ohm min/max across 1% + TCR:',resistor_bounds(RTOP))
    print('1R UVLO sense at 10V min:',one_res_pin_min_at_vin(10))
    print('1R UVLO at 58V max:',one_res_pin_max_at_vin(58),'- limit 60V recommended and 67V absolute')
    print('2R 330k/68k UV rising min/max:',two_res_threshold_bounds(UV_RISE))
    print('2R UV falling min/max:',two_res_threshold_bounds(UV_FALL))
    print('2R 24V divider current:',two_res_off_divider_current_at24(),'A')
    print('Reverse -60V via >300k min R approx:',max_reverse_uvlo_series_current(),'A')
    print('ALL FULL-LOAD, 85C, RAW, 58V PAD/PCB, GND SHDN AND KIcad native gates OPEN.')
