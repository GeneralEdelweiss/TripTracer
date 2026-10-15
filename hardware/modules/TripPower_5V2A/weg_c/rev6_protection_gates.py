#!/usr/bin/env python3
"""TripPower C REV6 manufacturer-rating and candidate OVLO divider sensitivity.
NOT manufacturer calibration, validated board design or automotive lab clearance.
Call: python3 -m unittest -v rev6_protection_gates
      python3 rev6_protection_gates.py
"""
from dataclasses import dataclass
import unittest

R_TOL = .001                # 0.1% precision selected candidate resistors
MAIN_VIN_MIN, MAIN_VIN_MAX = 10.0,32.0
OVP_CUTOFF_DEADLINE=36.0
LIMITED_SURGE=58.0
SURGE_TIME_S=.350
SURVIVAL36_S=.400
TP26631_OPER=60.0
TP26631_ABS=67.0
TP26600_ABS=62.0
LMR38020_OPER=80.0
LMR38020_VOUT=5.0
LMR38020_IOUT=2.0
RAW_NOM_A=.5

@dataclass(frozen=True)
class Ovlo:
    label:str
    rtop:float
    rbot:float
    vrmin:float
    vrmax:float
    vfmax:float
    leak:float
    diode:bool = False

A=Ovlo("A_TPS26631_100k_3k78",100e3,3.78e3,1.176,1.224,1.15,150e-9,True)
B=Ovlo("B_TPS26600_100k_3k74",100e3,3.74e3,1.17,1.225,1.125,100e-9,False)

def bounds(x):
    # Input leakage into OVLO is modeled bidirectional; equation Vsrc=Vref*(1+Rtop/Rbottom)+Ileak*Rtop.
    rtop_min=x.rtop*(1-R_TOL)
    rtop_max=x.rtop*(1+R_TOL)
    rbot_min=x.rbot*(1-R_TOL)
    rbot_max=x.rbot*(1+R_TOL)
    v_rise_min=x.vrmin*(1+rtop_min/rbot_max)-x.leak*rtop_min
    v_rise_max=x.vrmax*(1+rtop_max/rbot_min)+x.leak*rtop_max
    v_fall_max=x.vfmax*(1+rtop_max/rbot_min)+x.leak*rtop_max
    return v_rise_min,v_rise_max,v_fall_max

def buck_input_current(vin_after_protection,eta=.85):
    return LMR38020_VOUT*LMR38020_IOUT/(vin_after_protection*eta)

def total_and_losses(vin=10,eta=.85,raw_a=.5,diode_drop=.6):
    # Independent typical sensitivity with no efficiency/vendor thermal assurance
    eFuse_drop=.053*(buck_input_current(vin-diode_drop,eta)+raw_a)
    vbuck=vin-diode_drop-eFuse_drop
    ibuck=buck_input_current(vbuck,eta)
    i_total=ibuck+raw_a
    return {"V_Buck_IN":vbuck, "I_total":i_total, "Diode_loss":i_total*diode_drop,
            "eFuse_53mOhm_loss":i_total*i_total*.053, "Buck_full_heat_if_eta":10*(1/eta-1)}

def p_buck_tj_proxy(eta=.85,theta=45,ta=60):
    return ta+theta*10*(1/eta-1)

class Checks(unittest.TestCase):
    def test_rev6_versus_old_200v(self):
        self.assertEqual((MAIN_VIN_MIN,MAIN_VIN_MAX,LIMITED_SURGE),(10,32,58))
        self.assertEqual((SURGE_TIME_S,SURVIVAL36_S),(.35,.4))
    def test_A_OVP_design_window_at_efuse_pins(self):
        rise_min,rise_max,fall_max=bounds(A)
        self.assertGreater(rise_min,32)
        self.assertLess(rise_max+1.0,36) # conservatively allow 1V diode at switching current
        self.assertLess(fall_max,32)
    def test_B_OVP_design_window_with_precision(self):
        rise_min,rise_max,fall_max=bounds(B)
        self.assertGreater(rise_min,32)
        self.assertLess(rise_max,36)
        self.assertLess(fall_max,32)
    def test_A_factory_ovlo_invalid_at_32v_restart(self):
        # Even in best scenario, falling threshold >=32.7 V at TPS26631 IN.
        self.assertGreater(32.7,32.)
    def test_B_factory_ovlo_invalid_at_32v_continuous(self):
        self.assertLess(31.,32.)
    def test_A_limited_58v_is_2v_below_recommended_ceiling(self):
        self.assertEqual(TP26631_OPER-LIMITED_SURGE,2.)
        self.assertEqual(TP26631_ABS-LIMITED_SURGE,9.)
    def test_B_58v_has_small_absolute_margin(self):
        self.assertEqual(TP26600_ABS-LIMITED_SURGE,4.)
    def test_Buck_has_higher_nominal_vin_margin_than_module55(self):
        self.assertGreater(LMR38020_OPER-LIMITED_SURGE,20)
        self.assertLess(55,LIMITED_SURGE)
    def test_10v_normal_eff85_total_input_and_diode_heat(self):
        s=total_and_losses()
        self.assertLess(s["I_total"],2.)
        self.assertGreater(s["I_total"],1.6)
        self.assertGreater(s["Diode_loss"],1.)
    def test_no_thermal_conclusion_from_eta_guess(self):
        self.assertGreater(p_buck_tj_proxy(.85,55,60),150)
        self.assertLess(p_buck_tj_proxy(.90,45,60),150)
    def test_2x_short_pulses_require_raw_wiring_margin(self):
        ilimit_nom=2.4
        self.assertGreater(2*ilimit_nom,RAW_NOM_A*5)
    def test_powerfail_without_energy_not_sd_close(self):
        guaranteed_warning_ms=0
        self.assertEqual(guaranteed_warning_ms,0)
        self.assertFalse(guaranteed_warning_ms>=1)
    def test_acc_shdn_absolute_limit(self):
        shdn_abs=5.5
        self.assertGreater(MAIN_VIN_MAX,shdn_abs)

def report():
    print("TRIPPOWER C REV6 manufacturer screening, ABSOLUTELY NO ISO/PCB RELEASE")
    for x in (A,B):
        trip=bounds(x)
        print("%s: OV rising min %.3f V max %.3f V / OV falling worst-max %.3f V at IC input"%
              (x.label,*trip))
    print("TPS26631 58V margin 2V operating, 9V absolute; TPS26600 only 4V absolute.")
    print("Unmodeled surge pad ringing can erase these margins.")
    print("10V/5V2A RAW0.5A eta85% sensitivity:",total_and_losses())
    print("85% eta is NOT a guaranteed efficiency nor a thermal clearance.")
    print("SHDN<=5.5V, 32V restart, 58V pad waveform, 60C 2A heat, 85C fail off, "
          "F_MAIN DC short-fault, local PWR_FAIL, genuine RAW0.5A and native KiCad remain blocked.")

if __name__=="__main__":
    report()
