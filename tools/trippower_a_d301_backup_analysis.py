#!/usr/bin/env python3
"""TripPower Weg A: manufacturer-constrained D301 open/parallel D306 screening.

This is a qualification GATE, NOT a thermal/ISO compliance certificate.
All numerical assumptions, especially fixed Zener voltage, are labelled.
"""
import json
from trippower_a_model import rvs_pulse, zener_open, R_HOT125_MIN_SCALE

V_IN = 200.0
T = 0.350
R_HOT_MIN = 3*3300*R_HOT125_MIN_SCALE
TJ_MAX = 150.0
# onsemi 1SMB59xx manufacturer datasheet Rev10 page1: 3W at TL=75C,
# 40mW/°C above 75C, junction-to-lead 25 K/W; 550mW on reference
# PCB @TA=25C with 4.4mW/°C above 25C.
ONSEMI_PD_TL75 = 3.0
ONSEMI_DERATE_PER_C = 0.040
ONSEMI_PCB_TA25 = 0.550
ONSEMI_PCB_DERATE_PER_C = 0.0044
COMCHIP_PMAX_CATALOG = 5.0  # @ vendor-specified, NON-125C reference!
COMCHIP_T125_ALLOWED_W = None # No application-validated package/PCB temp bound.
MISSING=["Comchip ACZRC5370B-G worst-case Vz(I,T) up to +125C and pulse!",
         "D306 0.35s transient Zth(T), PCB-specific lead temperature and junction T",
         "D301/D306 individual current sharing and repetitive surge thermal history",
         "D306 reverse leakage at VIN=9V, -40..+125C; 500nA is at 42.6V test point",
         "D301+D306 simultaneous fault/common-cause connector, solder, heat",
         "Actual LM74930 VS/EN/CAP response when D301 is disconnected",
         "100V MLCC Ceff(V,T) and voltage surge before D306 takes conduction",
         "F_MAIN coordination for low-current Zener failures"]

def allowable_onsemi_at_tlead(tlead):
    return max(0,ONSEMI_PD_TL75-ONSEMI_DERATE_PER_C*max(0,tlead-75))

def allowable_onsemi_reference_board_at_ambient(ta):
    return max(0,ONSEMI_PCB_TA25-ONSEMI_PCB_DERATE_PER_C*max(0,ta-25))

def fault_study():
    open_nom=zener_open(initial_vs_v=0,ceff_f=21e-6)
    open_recharged=zener_open(initial_vs_v=56,ceff_f=21e-6)
    isolated={}
    for voltage in (53.2,56.0,58.8,65.0):
        c=rvs_pulse(vz=voltage,r_scale=R_HOT125_MIN_SCALE)
        isolated[str(voltage)]={"ASSUMED_FIXED_ZENER_V":voltage,
            "I_RVS_mA":c["i_ma"],
            "individual_full_pulse_zener_power_W":c["zener_power_w"],
            "individual_full_pulse_zener_energy_J":c["zener_energy_j"],
            "R313_315_energy_each_J":c["resistor_energy_j"][0],
            "D306_5W_at_125C_package_proven":False,
            "onsemi_3W_at_fixed_Tlead125_margin_W":
                allowable_onsemi_at_tlead(125)-c["zener_power_w"]
        }
    p_65=isolated["65.0"]["individual_full_pulse_zener_power_W"]
    return {
        "scope":"MANUFACTURER_CORNER_AND_TOPOLOGY_ONLY_NOT_SURGE_QUALIFICATION",
        "input":{"VIN_V":200,"pulse_ms":350,"R_nom_ohm":9900,
                 "R_min_with_1pct_and_100ppm_per_K_to125C_ohm":R_HOT_MIN,
                 "D301_MPN":"1SMB5943BT3G",
                 "D306_candidate_MPN":"ACZRC5370B-G",
                 "D306_package":"DO-214AB / SMC",
                 "D306_AEC_Q101":True},
        "unprotected_d301_open":{"21uf_vs0":open_nom,
                                 "21uf_precharged56v":open_recharged,
                                 "caps_C302_C308_C312_absolute_rated_V":100,
                                 "LM74930_VS_operating_max_V":65,
                                 "TPS38_VDD_operating_max_V":65,
                                 "OTHER_PINS_AND_INTERNAL_CLAMPS":"UNKNOWN"},
        "D301_open_D306_healthy_fixed_Vz_cases":isolated,
        "Zener_hot_case_manufacturer_limits":{
            "onsemi_3W_at_lead75_C":ONSEMI_PD_TL75,
            "onsemi_lead_derating_W_per_C":ONSEMI_DERATE_PER_C,
            "onsemi_max_W_if_lead_exactly125C":allowable_onsemi_at_tlead(125),
            "onsemi_reference_FR4_max_W_at_ambient125C":
                allowable_onsemi_reference_board_at_ambient(125),
            "onsemi_3W_56v_max_Tlead_C_if_65V_fixed_assumed":
                75+(ONSEMI_PD_TL75-p_65)/ONSEMI_DERATE_PER_C,
            "comchip_ACZRC5370B_G_catalog_W_NOT_125C":COMCHIP_PMAX_CATALOG,
            "comchip_ACZRC5370B_G_W_at125C_on_our_pcb":COMCHIP_T125_ALLOWED_W,
        },
        "9v_start_delta":{
            "supply_R_ohm_unchanged":True,
            "extra_zener_capacitance_F":"UNKNOWN",
            "additional_D306_500nA_reverse_leak_test_point_V":42.6,
            "additional_D306_9V_125C_reverse_leak_max_A":None,
            "hypothetical_500nA_effect_on_VS_v":9900*500e-9,
            "TPS38_delay_C311_effect":"no intentional change, must revalidate",
            "9v_guaranteed":False,
        },
        "fmea": {
            "D301_open_D306_healthy":"D306 alternative structural limiting path; hot and Vz(I,T) unqualified",
            "D306_open_D301_healthy":"same baseline D301 clamp retained; hot qualification unproven",
            "D301_and_D306_open":"VS exposed to source via 9.9k; fails risk screen",
            "D306_short":"VS collapses, controlled OFF presumed but resistor pulse and F_MAIN proof required",
            "D301_short":"VS collapses, unchanged previous short-fault issue",
            "D306_leakage_hot":"9V first-start margin may worsen, unspecified"
        },
        "gate_status":"NO_FAB_NO_125C_PULSE_PROOF_NO_9V_RESTART_GUARANTEE",
        "known_missing":MISSING
    }
if __name__=="__main__":
    print(json.dumps(fault_study(),indent=2,sort_keys=True,allow_nan=False))
