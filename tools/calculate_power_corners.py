"""Transparent design scenarios, not guaranteed circuit limits or release tests."""
import itertools
import json


def divider_corners(top, bottom, threshold_range, leakage=0.2e-6, tolerance=0.01):
    return sorted((v*(rt+rb)/rb+i*rt) for v,rt,rb,i in itertools.product(
        threshold_range, [top*(1-tolerance),top*(1+tolerance)],
        [bottom*(1-tolerance),bottom*(1+tolerance)],[-leakage,leakage]))


def calculate():
    power=10.0
    current=[{'vin_V':v,'assumed_efficiency':eta,'input_current_A':power/(v*eta)}
             for v in [6,9,12,24,30] for eta in [0.8,0.85,0.9]]
    shunts=[]
    for r in [0.002,0.005,0.01,0.02]:
        shunts.append({'shunt_ohm':r,'ocp_3A_RLIM_ohm':12*50/(3*r),
                       'scp_default_typ_A':0.02/r,
                       'scp_default_low_high_A':[0.0174/(r*1.01),0.022/(r*0.99)],
                       'startup_scp_low_high_A':[0.0165/(r*1.01),0.024/(r*0.99)],
                       'shunt_power_at_3A_W':9*r,'drop_at_3A_V':3*r})
    # These include threshold/1% resistor/input-leakage corners, not transient behavior.
    uv=divider_corners(100e3,12.4e3,[0.533,0.573])
    uv_on=divider_corners(100e3,12.4e3,[0.585,0.63])
    ov_reference=divider_corners(100e3,1.65e3,[0.585,0.63])
    ov_candidate=divider_corners(100e3,1.58e3,[0.585,0.63])
    ov_30V=divider_corners(100e3,1.8e3,[0.585,0.63])
    return {'status':'design scenarios only; no lab/ISO or circuit release',
            'power_assumption_W':power,'input_current_scenarios':current,
            'shunt_tradeoffs':shunts,
            'uv_candidate_fall_V':[min(uv),max(uv)],
            'uv_candidate_rise_V':[min(uv_on),max(uv_on)],
            'ov_TI_reference_100k_1k65_rise_V':[min(ov_reference),max(ov_reference)],
            'ov_candidate_100k_1k58_rise_V':[min(ov_candidate),max(ov_candidate)],
            'current_continuous_input_range_V':[9,30],
            'motor_start_input_target_V':6,
            'ov_30V_candidate_100k_1k8_rise_V':[min(ov_30V),max(ov_30V)],
            'vs_clamp_at_200V_scenario':{'zener_V':60,'series_R_ohm':10000,
                'series_R_peak_power_W':(200-60)**2/10000,
                'zener_peak_power_W':60*(200-60)/10000,
                'constant_350ms_energy_upper_scenario_J':(200-60)**2/10000*0.35},
            'open':['No guaranteed efficiency or complete load budget',
                    'OCP model needs independent gain/offset characterization; nominal RLIM is not a guaranteed current limit',
                    'RISCP cannot increase fixed LV_SCP startup threshold',
                    'VS supply/startup with 10k resistor at 6V needs validation',
                    'MOSFET SOA, pulse resistor ratings, zener tolerances, ADC protection and ACC/HOLD still pending']}


if __name__=='__main__':
    print(json.dumps(calculate(),indent=2))
