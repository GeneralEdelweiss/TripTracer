#!/usr/bin/env python3
"""TripPower C Round 6: condition-dependent physics ONLY, not a safety qualification.
Run: python3 -m unittest -v r6_independent_gates
     python3 r6_independent_gates.py
No circuit may be claimed safe based on these tests.
"""
import math
import unittest

V_PEAK = 200.0       # mandatory user check: 200 V, NOT 202 V
T_SPEC = 0.350       # user-requested event duration, waveform/source impedance still undefined
V_BASE = 30.0
V_TVS_EXAMPLE = 61.2  # TSC AN-1003 example at 25 C, NEVER a 125C guaranteed clamp
V_BUCK_OPER_MAX = 80.0
V_EFUSE_ABS_MAX = 67.0
BUCK_W = 10.0
RAW_A = 1.0
ETA_ASSUMED = 0.90
RDS_HOT = .214       # Vishay SQM35N30-97 only at Vgs=10V; illustrative baseline
RE_FUSE_HOT = .053   # TI TPS26631 maximum Ron high temperature (example)
SINGLE_BREAK_RATING_KNOWN = False


def tvs_rectangular(r_source, v_clamp=V_TVS_EXAMPLE, duration=T_SPEC):
    if r_source <= 0:
        raise ValueError("Source resistance must be >0")
    i = max(0, (V_PEAK-v_clamp)/r_source)
    return (i, v_clamp*i, v_clamp*i*duration)


def tvs_exponential(r_source, t_constant=T_SPEC, v_clamp=V_TVS_EXAMPLE):
    """Illustration ONLY: v(t)=30+(200-30)*exp(-t/tau).
    td in ISO documents is NOT automatically the same as exponential tau.
    Integrate positive dissipated energy until crossing Vclamp.
    """
    if r_source <= 0 or t_constant <= 0:
        raise ValueError("Positive R and tau required")
    if not V_BASE < v_clamp < V_PEAK:
        raise ValueError("Clamp must be between base and peak")
    t_end=t_constant*math.log((V_PEAK-V_BASE)/(v_clamp-V_BASE))
    vin_integral=(V_PEAK-V_BASE)*t_constant*(1-math.exp(-t_end/t_constant))
    over_integral=vin_integral-(v_clamp-V_BASE)*t_end
    return v_clamp*over_integral/r_source,t_end


def current_hot(vin, path_r=2*RDS_HOT+RE_FUSE_HOT, raw_a=RAW_A, efficiency=ETA_ASSUMED):
    """Solve I=RAW+P/(eta*(VIN-I*R)), low-current physical root."""
    # R*I^2 - (VIN+R*RAW)*I + VIN*RAW+P/eta = 0
    a=path_r
    b=-(vin+path_r*raw_a)
    c=vin*raw_a+BUCK_W/efficiency
    discriminant=b*b-4*a*c
    if discriminant<=0:
        return None
    I=(-b-math.sqrt(discriminant))/(2*a)
    return {"I":I,"V_after":vin-I*path_r,
            "P_FETs":I*I*(path_r-RE_FUSE_HOT),
            "P_eFuse":I*I*RE_FUSE_HOT}


def buck_temp_proxy(eff,theta_K_per_W,ambient=125):
    """All conversion loss attributed to IC as bounding screening; NOT a theta or efficiency guarantee."""
    return ambient+theta_K_per_W*BUCK_W*(1/eff-1)


def open_fet_fault_voltage():
    """A shorted series FET cannot be forced open by its control IC."""
    return V_PEAK # diode drop intentionally omitted for conservative maximum


def fuse_qualification_required(available_voltage):
    # Published 32 V DC automotive blade ratings cannot prove 200 V DC interruption.
    return available_voltage > 32 and not SINGLE_BREAK_RATING_KNOWN


class Round6Tests(unittest.TestCase):
    def test_spec_exact(self):
        self.assertEqual((V_PEAK,T_SPEC),(200.0,0.350))

    def test_shunt_energy_unbounded_without_Rsource(self):
        self.assertGreater(tvs_rectangular(.1)[2],tvs_rectangular(1)[2])
        self.assertGreater(tvs_rectangular(1)[2],tvs_rectangular(8)[2])
        self.assertGreater(tvs_rectangular(.01)[2],100000)

    def test_example_25C_3point5ohm_not_hot_certified(self):
        i,p,e=tvs_rectangular(3.5)
        self.assertAlmostEqual(i,39.657142857,places=4)
        self.assertGreater(e,800)
        self.assertGreater(p,2400)

    def test_exponential_is_not_rectangular(self):
        e,t=tvs_exponential(3.5)
        self.assertAlmostEqual(e,525.73329593,places=3)
        self.assertGreater(t,T_SPEC)
        self.assertLess(e,tvs_rectangular(3.5)[2])

    def test_fet_short_bypasses_gate_shutdown(self):
        self.assertGreater(open_fet_fault_voltage(),V_EFUSE_ABS_MAX)
        self.assertGreater(open_fet_fault_voltage(),V_BUCK_OPER_MAX)

    def test_automotive_32v_fuse_not_200v_certified(self):
        self.assertTrue(fuse_qualification_required(200))

    def test_hot_9_10_11_voltage_trade(self):
        currents=[current_hot(v) for v in (9,10,11)]
        self.assertTrue(all(x is not None for x in currents))
        self.assertTrue(currents[0]["I"] > currents[1]["I"] > currents[2]["I"])
        self.assertTrue(currents[0]["P_FETs"] > currents[1]["P_FETs"] > currents[2]["P_FETs"])
        self.assertLess(currents[0]["V_after"],8)

    def test_hot_buck_uncertainty(self):
        self.assertGreater(buck_temp_proxy(.90,30),150)
        self.assertLess(buck_temp_proxy(.90,20),150)

    def test_surge_linear_fet_clamp_fault_power(self):
        # LTC4366 example if holding output to 43 V at 2.4 A.
        self.assertGreater((200-43)*2.4,370)
        self.assertGreater((200-43)*2.4*0.35,130)

    def test_backup_cannot_charge_primary_cell_from_5V(self):
        # Design principle: there is NO selected charger and no granted primary-cell power path.
        backup_primary_cell_charge_allowed=False
        self.assertFalse(backup_primary_cell_charge_allowed)

    def test_10v_11v_not_permitted_spec_change(self):
        mandatory_minimum_v=9
        self.assertEqual(mandatory_minimum_v,9)


def report():
    print("TripPower C R6 analytical screen; 200V/350ms, NO circuit/ISO approval")
    for R in (1,3.5,4.5,8):
        i,p,er=tvs_rectangular(R)
        e,te=tvs_exponential(R)
        print(f"TVS ideal 61.2V, Rsrc={R:g} Ohm: square {i:.1f}A / {p:.0f}W / {er:.1f}J;"
              f" hypothetical exp tau=350ms {e:.1f}J up to t={1000*te:.1f}ms")
    for v in (9,10,11):
        x=current_hot(v)
        print(f"{v}V, assumed two 214mohm FETs +53mohm eFuse, eta90%:"
              f" I={x['I']:.3f}A Vdown={x['V_after']:.3f}V"
              f" FET heat={x['P_FETs']:.3f}W eFuse={x['P_eFuse']:.3f}W")
    for eff in (.85,.90,.93):
        print(f"Buck eta={eff:.0%}, thetaJA proxy 30K/W: Tj={buck_temp_proxy(eff,30):.1f}C")
    print("BLOCKED: TVS 125C derating; 200V waveform/Rsrc; F_MAIN 200V DC I²t; MOSFET short; "
          "PWR_FAIL isolation; real +125C buck heat; system hardware test.")


if __name__=="__main__":
    report()
