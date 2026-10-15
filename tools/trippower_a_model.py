#!/usr/bin/env python3
"""TripPower Weg A: reversible analytical screening, never an automotive release.

Run: python3 tools/trippower_a_model.py
     python3 tools/trippower_a_model.py --scenario worst_9v --pretty

Only documented conditional models; unknown manufacturer/PCB limits are null.
No simulated output contains a qualification/pass field.
"""
import argparse
import json
import math
from dataclasses import dataclass, replace, asdict

VIN_PULSE_V = 200.0
PULSE_S = 0.350
R_VS_OHM = (3300.0, 3300.0, 3300.0)
R_TOL = 0.01   # Vishay CRCW25123K30FKEGHP, 1 % at stated measurement conditions
ZENER_NOM_V = 56.0
ZENER_TOL = 0.05  # onsemi 1SMB5943BT3G, at manufacturer test current
Q301_VDS_ABS_MAX_V = 250.0
Q301_VGS_ABS_MAX_V = 20.0
Q302_VDS_ABS_MAX_V = 60.0
VS_OPERATING_MAX_V = 65.0
TVS150_VBR_V = (167.0, 192.5)
TVS33CA_VBR_V = (36.7, 42.2)
CAP_VS_NOMINAL_F = 21e-6  # C302 1uF + C308/C312 10uF; NOT actual Ceff
UNKNOWN_GATES = [
    "Vishay CRCW25123K30FKEGHP: 350ms pulse-load E/P derating at Tmax, repeated pulses",
    "onsemi 1SMB5943BT3G: Vz(I,T), 350ms transient Zth and pulse/repetitive energy",
    "Diodes SMBJ150A-13-F + SMBJ33CA-13-F: common-current series IV(T) and pulse SOA",
    "Vishay SQM10250E_GE3: actual hot switching SOA at VDS(t), ID(t), Tj",
    "C302/C308/C312: certified Ceff(V,T,aging) and leakage",
    "TI LM74930: actual VS input transient current versus VS, EN, CAP and temperature",
    "TI TPS38: CTR/OD behaviour on residual power and RUN_CMD high with VIN=0",
    "Real VIN edge/overshoot, harness inductance, fuse coordination, board thermals",
]

def rvs_pulse(vin=VIN_PULSE_V, vz=ZENER_NOM_V, r_scale=1.0,
              short_index=None, duration=PULSE_S):
    """Fixed-Vz idealised rectangular model. Faults by removing a R branch."""
    rs = [r*r_scale for r in R_VS_OHM]
    if short_index is not None:
        rs[short_index] = 0.0
    total = sum(rs)
    if total <= 0:
        raise ValueError("all resistors short; ideal current undefined")
    i = max(0.0, (vin - vz)/total)
    return {
        "vin_v": vin, "assumed_fixed_vz_v": vz, "r_total_ohm": total,
        "i_ma": i*1000, "resistor_power_w": [i*i*r for r in rs],
        "resistor_energy_j": [i*i*r*duration for r in rs],
        "zener_power_w": i*vz, "zener_energy_j": i*vz*duration,
        "duration_s": duration, "qualified": False
    }

def zener_open(vin=VIN_PULSE_V, initial_vs_v=0.0, ceff_f=CAP_VS_NOMINAL_F):
    """Upper charging tendency: zero loads, open Zener, D302 reverse-biased."""
    if ceff_f <= 0: raise ValueError("ceff must be positive")
    tau = sum(R_VS_OHM)*ceff_f
    final = vin+(initial_vs_v-vin)*math.exp(-PULSE_S/tau)
    def t_cross(level):
        if initial_vs_v >= level: return 0.0
        if level >= vin: return None
        return -tau*math.log((vin-level)/(vin-initial_vs_v))
    return {"initial_vs_v":initial_vs_v,"ceff_uf":ceff_f*1e6,
            "vs_at_350ms_v":final,"time_to_vs_operating_65v_ms":t_cross(65)*1000,
            "time_to_100v_ms":t_cross(100)*1000,
            "model":"OPEN D301, zero load/leak, no internal VS clamp; NOT a prediction",
            "qualified":False}

def illustrative_stack_source(v_open_v, source_r_ohm, assumed_stack_v,
                              duration_s):
    """SENSITIVITY ONLY: fictitious ideal stack voltage, not a TVS I-V curve.

    Never use this as a power or surge qualification of D303/D304.
    """
    if source_r_ohm<=0 or duration_s<0:
        raise ValueError("finite positive source R and nonnegative pulse required")
    i=max(0.0,(v_open_v-assumed_stack_v)/source_r_ohm)
    return {
        "v_open_v":v_open_v, "source_r_ohm":source_r_ohm,
        "assumed_stack_voltage_v_NOT_VENDOR_CURVE":assumed_stack_v,
        "duration_s":duration_s, "i_a_if_assumed_clamp":i,
        "stack_power_w":i*assumed_stack_v,
        "stack_energy_j":i*assumed_stack_v*duration_s,
        "power_split_between_d303_d304_unknown":True,
        "voltage_curve_and_SOA_certified":False,
    }

def pulse_study():
    nominal=rvs_pulse()
    r_min=1-R_TOL
    corners={
      "nominal":nominal,
      "r_min_zener_vz_min_assumed":rvs_pulse(vz=ZENER_NOM_V*(1-ZENER_TOL), r_scale=r_min),
      "r_min_zener_vz_max_assumed":rvs_pulse(vz=ZENER_NOM_V*(1+ZENER_TOL), r_scale=r_min),
      "d301_short_r_min":rvs_pulse(vz=0.0,r_scale=r_min),
      "one_rvs_short_z_min_r_min":rvs_pulse(vz=ZENER_NOM_V*(1-ZENER_TOL),r_scale=r_min,short_index=1),
      "one_rvs_short_d301_short":rvs_pulse(vz=0.0,r_scale=r_min,short_index=1)
    }
    tvs_breakdown_min=sum(x[0] for x in [TVS150_VBR_V,TVS33CA_VBR_V])
    tvs_breakdown_max=sum(x[1] for x in [TVS150_VBR_V,TVS33CA_VBR_V])
    q301_hypothetical_off_i=2.389
    return {
      "scope":"IDEAL_200V_350ms_FIXED_VZ_SCREEN_NOT_ISO_NOT_SOA",
      "topology_from_native_netlist":
         "VIN_FUSED -> Q301.D2; Q301.S3 -> SOURCE_A; "
         "VIN_FUSED -> R313 -> R314 -> R315 -> VS_CLAMP; "
         "D301.K1 VS_CLAMP / A2 GND; D302.K1 VS_CLAMP / A2 SOURCE_A; "
         "D303.K1 VIN_FUSED / A2 TVS_STACK; D304(bidirectional).1 TVS_STACK / .2 GND",
      "fixed_voltage_corner_caveat":
         "56V +/-5% at specified Zener test current is NOT a guaranteed 200V pulse clamp; "
         "no T-dependent full I-V curve or worst-case hot bound is available",
      "pulse_cases":corners,
      "tvs":{
        "d303_d304_series_vbr_at_datasheet_test_current_min_v":tvs_breakdown_min,
        "d303_d304_series_vbr_at_datasheet_test_current_max_v":tvs_breakdown_max,
        "guaranteed_to_clamp_at_200v":False,
        "datasheet_vc_individual_at_DIFFERENT_ipp_v":[243.0,53.3],
        "individual_vc_must_not_be_added_as_guaranteed_stack_clamp":True,
        "series_curve_hot_and_350ms_qualification":None,
        "single_faults":{
           "d303_short":"D304 ~37-42V breakdown alone; uncontrolled energy on input",
           "d304_short":"D303 ~167-192.5V breakdown alone; hot current/SOA unproven",
           "d303_reversed":"Forward polarity on +VIN; D304 alone ~37-42V; wiring/power danger"
        }
      },
      "overshoot_source_impedance_SENSITIVITY_NOT_SPEC": {
        "225v_100us_1ohm_assume220v_stack":illustrative_stack_source(225,1,220,100e-6),
        "250v_100us_5ohm_assume220v_stack":illustrative_stack_source(250,5,220,100e-6),
        "250v_350ms_5ohm_assume220v_stack_NOT_PROJECT_PROFILE":illustrative_stack_source(250,5,220,0.350),
      },
      "q301":{
        "vds_abs_max_v":Q301_VDS_ABS_MAX_V,
        "vgs_abs_max_magnitude_v":Q301_VGS_ABS_MAX_V,
        "ideal_vds_when_off_source_a_0v":VIN_PULSE_V,
        "overshoot_budget_if_source_a_0v_v":Q301_VDS_ABS_MAX_V-VIN_PULSE_V,
        "vds_source_a_0v_with_51v_overshoot_v":VIN_PULSE_V+51.0,
        "example_constant_current_during_turnoff_a":q301_hypothetical_off_i,
        "example_turnoff_energy_at_200v_j_by_duration_us":{
            str(us):VIN_PULSE_V*q301_hypothetical_off_i*us*1e-6 for us in (1,100,1000)
        },
        "hot_linear_SOA_certified":None,
        "EAS_84mJ_must_not_substitute_for_350ms_switching_SOA":True,
      },
      "q302_short_fault":{
        "q302_vds_abs_max_v":Q302_VDS_ABS_MAX_V,
        "q301_stuck_short_source_a_can_reach_200v":True,
        "result":"Q302 60V drain/source exposure depends on output path; unsafe without fault-path proof"
      },
      "d301_open":[zener_open(initial_vs_v=v,ceff_f=c) for v,c in
                    ((0.0,CAP_VS_NOMINAL_F),(56.0,CAP_VS_NOMINAL_F),
                     (0.0,5e-6))],
      "unknown_qualification_gates":UNKNOWN_GATES,
      "fabrication_release":False
    }

@dataclass(frozen=True)
class StartCase:
    vin_v: float = 9.0
    initial_vs_v: float = 0.0
    initial_timer_fraction: float = 0.0
    ceff_uf: float = 21.0  # installed nominal; real Ceff unknown
    r_vs_tolerance_factor: float = 1.0  # 0.99..1.01 at specified R accuracy
    pre_ready_load_ua: float = 35.0  # illustrative, NOT TI max
    enabled_iq_ua: float = 780.0  # TI max measured @ VS=12V/EN=2V; not dynamic max
    additional_pump_ma: float = 2.0  # invented sensitivity parameter, NOT a spec
    pump_interval_ms: float = 2.0  # invented sensitivity parameter, NOT a bound
    ready_on_v: float = 7.51  # P02 REV5 upper preliminary threshold, NOT qualified
    ready_off_v: float = 5.42
    timer_delay_ms: float = 250.0  # placeholder pending TPS38 CTR effective-C data
    source_a_can_rise: bool = True  # optimistic gate/FET/Buck assumption
    diode_drop_v: float = 0.7  # assumed D302 behaviour, not qualified
    duration_s: float = 1.50
    dt_s: float = 0.00010

def vs_static_limit(vin, pre_ua, r=9900.0):
    """Ideal fixed-load asymptotic VS before FET conduction."""
    return max(0.0, vin-r*pre_ua*1e-6)

def simulate_start(s:StartCase):
    if s.ceff_uf<=0 or s.dt_s<=0 or s.timer_delay_ms<=0 or s.r_vs_tolerance_factor<=0:
        raise ValueError("invalid positive time/capacitance")
    if not 0<=s.initial_timer_fraction<=1:
        raise ValueError("timer initial fraction outside [0,1]")
    vs=s.initial_vs_v
    timer=s.initial_timer_fraction*s.timer_delay_ms*1e-3
    phase="precharge"
    cycles=0
    first_en_s=None
    first_source_s=None
    minimum_pump_vs=None
    pump_start=None
    trace=[]
    n=int(s.duration_s/s.dt_s)
    for j in range(n+1):
        t=j*s.dt_s
        if phase=="precharge":
            if vs>=s.ready_on_v: timer+=s.dt_s
            else: timer=0.0
            if timer >= s.timer_delay_ms*1e-3:
                phase="pump"; first_en_s=t if first_en_s is None else first_en_s
                pump_start=t
        elif phase=="pump":
            minimum_pump_vs=vs if minimum_pump_vs is None else min(vs,minimum_pump_vs)
            if vs<=s.ready_off_v:
                phase="precharge"; cycles+=1;timer=0.0
            elif (t-pump_start)*1000>=s.pump_interval_ms:
                if s.source_a_can_rise:
                    phase="source";first_source_s=t
                else:
                    # Gate never succeeds; continued-on IQ remains an unbounded unknown.
                    phase="pump"
        if phase=="pump":
            current=s.enabled_iq_ua*1e-6 + s.additional_pump_ma*1e-3
        elif phase=="source":
            current=s.enabled_iq_ua*1e-6
        else:
            current=s.pre_ready_load_ua*1e-6
        R=sum(R_VS_OHM)*s.r_vs_tolerance_factor
        C=s.ceff_uf*1e-6
        equilibrium=s.vin_v-R*current
        vs=equilibrium+(vs-equilibrium)*math.exp(-s.dt_s/(R*C))
        if phase=="source":
            vs=max(vs,min(s.vin_v,s.vin_v-s.diode_drop_v))  # optimistic D302 feed
        if j%max(1,int(0.025/s.dt_s))==0:
            trace.append([round(t,5),round(vs,4),phase])
    return {
        "parameters":asdict(s),"pre_ready_vs_equilibrium_v":vs_static_limit(
            s.vin_v,s.pre_ready_load_ua, sum(R_VS_OHM)*s.r_vs_tolerance_factor),
        "first_ctrl_en_model_s":first_en_s,
        "first_source_a_model_s":first_source_s,
        "min_pump_vs_model_v":minimum_pump_vs,
        "model_failed_restarts":cycles,
        "end_vs_model_v":vs,
        "trace_25ms_sample":[trace[k] for k in range(0,len(trace),max(1,len(trace)//12))],
        "guaranteed_9v_start":False,
        "unmodelled":["TPS38 real CTR discharge, SENSE1/SENSE2 interaction + RUN_CMD",
                      "LM74930 actual VS I(t) and charge pump current", "CAP_PUMP-VS dynamics",
                      "D302 forward limit, actual FET/source rise/overshoot",
                      "real MLCC Ceff(V,T,age), diode + capacitor leakage at 125C",
                      "ramp/brownout source impedance and 5V/2A plus AUX 1A load"]
    }

def startup_study():
    s=StartCase()
    setups={
      "nominal_assumption_9v":s,
      "9v_high_r_min_start":replace(s,r_vs_tolerance_factor=0.99),
      "9v_high_r_max_start":replace(s,r_vs_tolerance_factor=1.01),
      "9v_unspecified_high_trip_stress_8p539":replace(s,ready_on_v=8.539),
      "9v_preload_155ua_stalls_REV5_trip":replace(s,pre_ready_load_ua=155,
                                                   r_vs_tolerance_factor=1.01),
      "9v_low_ceff_4uf_big_pump":replace(s,ceff_uf=4,additional_pump_ma=8,pump_interval_ms=10),
      "9v_restored_partial_timer":replace(s,initial_vs_v=8.0,initial_timer_fraction=0.75),
      "9v_vin0_run_high_unqualified":replace(s,vin_v=0,initial_vs_v=0,source_a_can_rise=False),
      "12v_nominal_assumptions":replace(s,vin_v=12),
      "30v_nominal_assumptions":replace(s,vin_v=30),
    }
    return {
        "scope":"PARAMETRIC_RC_STATE_SCREEN_NOT_SPICE_NOT_TI_GUARANTEE",
        "cases":{k:simulate_start(v) for k,v in setups.items()},
        "unknown_qualification_gates":UNKNOWN_GATES,
        "fabrication_release":False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scenario",choices=("all","pulse","startup","worst_9v"),default="all")
    p.add_argument("--pretty",action="store_true")
    a=p.parse_args()
    if a.scenario=="pulse": out=pulse_study()
    elif a.scenario=="startup": out=startup_study()
    elif a.scenario=="worst_9v":
        out=simulate_start(replace(StartCase(),ceff_uf=4,additional_pump_ma=8,
                                   pump_interval_ms=10,ready_on_v=7.51,
                                   r_vs_tolerance_factor=1.01))
    else:out={"200v_pulse":pulse_study(),"9v_start":startup_study()}
    print(json.dumps(out,indent=2 if a.pretty else None,sort_keys=True,
                     allow_nan=False))
if __name__=="__main__": main()
