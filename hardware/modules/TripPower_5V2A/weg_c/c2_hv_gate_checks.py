#!/usr/bin/env python3
"""Weg C2-HV quantitative safety screening, no physical ISO/surge clearance.

Pure stdlib.  Execute python3 -m unittest -v c2_hv_gate_checks
               python3 c2_hv_gate_checks.py

Model: VIN positive rectangular or linear ramp; AP OVLO resistor/leakage bounded,
idealized propagation-delay sensitivity. No parasitic inductance or measured waveform.
"""
import itertools
import math
import unittest

SURGE_V = 200.0                 # user, NOT 202V
SURGE_DURATION_S = 0.350
BUCK_LM70840_VIN_OPER_MAX_V = 80.0
BUCK_LM70840_VIN_ABS_MAX_V = 87.5
EFUSE_TPS26631_OPER_MAX_V = 60.0
EFUSE_TPS26631_ABS_MAX_V = 67.0
OVLO_RTOP_NOM = 1e6
OVLO_RBOTTOM_NOM = 35e3
R_TOL = .01
OVLO_REF_RISING_MAX = 1.333  # Diodes AP74502HQ
OVLO_REF_FALLING_MIN = 1.063
OVLO_I_LEAKAGE_MAX_ABS = 110e-9 # Diodes OVLO input leakage bounded for sensitivity
FET_RDS_125C_MAX = .214       # Vishay SQM35N30-97 @ VGS=10V, 125C
FET_RDS_175C_MAX = .285       # Vishay @ VGS=10V, 175C
EFUSE_RON_125C_MAX = .053     # TPS26631 whole temperature rating
FET_COUNT = 2
OUTPUT_W = 10.0
RAW_A = 1.0


def ovlo_trip_input_v(reference_v, rtop_ohm, rbottom_ohm, sink_a=0.0):
    """Node current balance I_top=I_bottom+I_sink:
       Vin=(Vref*(Rtop+Rbottom)+I_sink*Rtop).
       Signed leakage values swept conservatively, independent across Vref cases.
    """
    return reference_v*(rtop_ohm+rbottom_ohm)/rbottom_ohm + sink_a*rtop_ohm


def worst_ovlo_limits():
    rtop=(OVLO_RTOP_NOM*(1-R_TOL), OVLO_RTOP_NOM*(1+R_TOL))
    rbot=(OVLO_RBOTTOM_NOM*(1-R_TOL), OVLO_RBOTTOM_NOM*(1+R_TOL))
    lk=(-OVLO_I_LEAKAGE_MAX_ABS,OVLO_I_LEAKAGE_MAX_ABS)
    rise=max(ovlo_trip_input_v(OVLO_REF_RISING_MAX, rt, rb, i)
             for rt, rb, i in itertools.product(rtop,rbot,lk))
    fall_min=min(ovlo_trip_input_v(OVLO_REF_FALLING_MIN,rt,rb,i)
                 for rt, rb, i in itertools.product(rtop,rbot,lk))
    return fall_min,rise


def linear_ramp_v(rise_time_us, turnoff_delay_us, input_before_v=30.0):
    """Stress envelope at switch output *if* fully conducting until delay.
       Does not include capacitance, L, ringing, Miller nor AP charge-pump dynamics.
    """
    _,worst_rise=worst_ovlo_limits()
    ramp=(SURGE_V-input_before_v)/rise_time_us
    return min(SURGE_V,worst_rise+ramp*turnoff_delay_us)


def max_allowable_gate_off_us(rise_time_us, limit_v):
    """No inductive overshoot margin; *not* an acceptable real design limit."""
    _,worst_rise=worst_ovlo_limits()
    return (limit_v-worst_rise)/(SURGE_V-30.0)*rise_time_us


def self_consistent_path_i(vin=9.,eta=.90,fet_rds=FET_RDS_125C_MAX, efuse_ron=EFUSE_RON_125C_MAX, raw_a=RAW_A):
    """Solve I=RAW+10W/(eta*(VIN-I*(2*Rds+ReFuse))).
       Reject unrealistic quadratic roots. Output limited to positive VIN net.
    """
    R=FET_COUNT*fet_rds+efuse_ron
    # f(I) = (I-raw)*eta*(vin-I*R)-10
    # note two roots; use physical low-current root
    a=R
    b=-(vin+raw_a*R)
    c=raw_a*vin+OUTPUT_W/eta
    disc=b*b-4*a*c
    if disc<=0:
        return None
    i=(-b-math.sqrt(disc))/(2*a)
    vin_buck=vin-i*R
    if vin_buck<=0: return None
    return i,vin_buck,FET_COUNT*i*i*fet_rds,i*i*efuse_ron


def buck_thermal(eta,theta_ja, ambient_c=125.):
    """Pout/eta-Pout = total system buck loss; conservative if all counted in IC.
       Output inductor dissipates separately; measured IC P might differ.
    """
    loss=OUTPUT_W*(1/eta-1)
    return ambient_c+theta_ja*loss,loss


def needed_efficiency(theta_ja, ambient_c=125., max_junc=150.):
    pmax=(max_junc-ambient_c)/theta_ja
    return OUTPUT_W/(OUTPUT_W+pmax)


def zener_supply_rectangular(standoff=60.,r_ohm=10200.,v=200., t=.350):
    """Ideal 60V clamp approximation: not a real SMCJ56A Vclamp guarantee."""
    iz=(v-standoff)/r_ohm
    return {"i_A":iz,"R_W":(v-standoff)*iz,"R_J":(v-standoff)*iz*t,
            "Z_W":standoff*iz,"Z_J":standoff*iz*t,
            "R_shortZ_W":v*v/r_ohm,"R_shortZ_J":v*v/r_ohm*t}


def tvs_absorption_rectangular(source_ohm,clamp_v=60.,surge_v=200.,duration_s=.350):
    # Upper envelope if ideal rectangular voltage, neglect source decay.
    peak_i=max((surge_v-clamp_v)/source_ohm,0.)
    return peak_i, clamp_v*peak_i,clamp_v*peak_i*duration_s


def cap_pulse_energy(cap_f,cap_to_v=200.):
    return 0.5*cap_f*cap_to_v**2


class GateTests(unittest.TestCase):
    def test_exact_spec(self):
        self.assertEqual(SURGE_V,200.)
        self.assertEqual(SURGE_DURATION_S,.350)

    def test_falling_trip_30v_with_1_percent_resistors_and_leakage(self):
        fall,rise=worst_ovlo_limits()
        self.assertGreater(fall,30.)
        self.assertGreater(rise,39.)
        self.assertLess(rise,41.)

    def test_10us_1us_ramp_close_to_efuse_limit(self):
        self.assertGreater(linear_ramp_v(10,1),57.)
        self.assertLess(linear_ramp_v(10,1),EFUSE_TPS26631_OPER_MAX_V)
        self.assertGreater(linear_ramp_v(10,2),EFUSE_TPS26631_ABS_MAX_V)

    def test_critical_fet_short_bypasses_switch_ovlo(self):
        # Common-source Q1 D-S short -> body diode Q2 to output, 200V
        # This is independent of comparator state. 1.5V max body diode drop.
        v_protected_min=SURGE_V-1.5
        self.assertGreater(v_protected_min, EFUSE_TPS26631_ABS_MAX_V)
        self.assertGreater(v_protected_min, BUCK_LM70840_VIN_ABS_MAX_V)

    def test_9v_full_load_thermal_self_consistency(self):
        i,vinbuck,pfet,pef=self_consistent_path_i()
        self.assertGreater(i,2.3)
        self.assertLess(vinbuck,8)
        self.assertGreater(pfet,2.4)
        self.assertGreater(pef,.28)

    def test_buck_thermal_evm_vs_non_evm(self):
        tej,pl=buck_thermal(.90,18.6)
        tboard,_=buck_thermal(.90,33.5)
        self.assertGreater(tej,145)
        self.assertGreater(tboard,150)
        self.assertGreater(needed_efficiency(33.5),.93)

    def test_short_zener_pulse_increases_feed_energy(self):
        d=zener_supply_rectangular()
        self.assertGreater(d["R_shortZ_J"],d["R_J"])
        self.assertGreater(d["R_shortZ_J"],1.3)

    def test_hv_tvs_energy_not_a_small_signal_zener(self):
        i,p,e=tvs_absorption_rectangular(1)
        self.assertEqual(i,140.)
        self.assertEqual(p,8400.)
        self.assertEqual(e,2940.)

    def test_single_high_voltage_cap_fails_with_stored_energy(self):
        self.assertAlmostEqual(cap_pulse_energy(220e-6,200),4.4)

    def test_no_fuse_3a_trigger_from_normal_load(self):
        i,*_=self_consistent_path_i()
        self.assertLess(i,3.0) # 3A F_MAIN cannot be relied on at I<rated.


def main():
    fall,rise=worst_ovlo_limits()
    print(f"UNQUALIFIED C2-HV STUDY; 200V/{SURGE_DURATION_S*1000:.0f}ms")
    print(f"30V restart margin fall-min={fall:.3f}V, rise-max={rise:.3f}V")
    for us in (10,100,1000):
        for off in (1.,2.,3.):
            print(f"30-200V / {us}us rise; assumed {off}us gate off -> {linear_ramp_v(us,off):.2f}V before opening (idealized)")
    print("Max effective off delays @10us ramp: for 60V = %.3fus, 67V=%.3fus" %
          (max_allowable_gate_off_us(10,60),max_allowable_gate_off_us(10,67)))
    print("125C/9V, 5V/2A + RAW1A, eta90%%: I, Vbuck, PFET2, PeFuse=",self_consistent_path_i())
    for theta in (18.6,33.5):
        print(f"Buck PCB assumed theta={theta}K/W: min efficiency to hold 150C = {needed_efficiency(theta)*100:.2f}%")
        for eta in (.85,.90,.94):
            print(f" eta {eta:.2f}: Tj-proxy {buck_thermal(eta,theta)[0]:.1f}C")
    for ri in (1.,8.):
        print(f"200V rectangular 350ms ideal 60V TVS Ri={ri}ohm -> {tvs_absorption_rectangular(ri)}")
    print("HV input FET D-S SHORT, ZENER OPEN/SHORT, RAW fault and ISO pulse shapes remain NO-GO.")

if __name__=="__main__":
    main()
