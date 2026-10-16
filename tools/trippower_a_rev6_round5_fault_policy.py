#!/usr/bin/env python3
"""Round5 independent static vendor-corner / A23 fault-policy audit, NOT physical validation.

Primary documents:
TI TPS2663 SLVSE94G Rev G (2024), 6.5, 6.6, 8.3.1, 8.3.2.1,
8.3.7.1.2, 8.3.12, Table 8-1, 9.4.
TI LMR38020-Q1 SNVSBS6B Rev B (2024), 8.2 Table 8-1.
"""
import json

R_TOP=330000
TOL=.01
TCR=.0001
I_LEAK=.000000150

def tolerance(temp_c):
    return TOL+TCR*abs(temp_c-25)

def rtop_corner(temp_c):
    e=tolerance(temp_c)
    return R_TOP*(1-e),R_TOP*(1+e)

def uvlo_edges(bottom, temp_c, rising=True):
    """Independent worst opposing resistor TCR/tolerance, +/-150 nA sink/source."""
    lo,hi=rtop_corner(temp_c)
    botlo,bothi=bottom*(1-tolerance(temp_c)),bottom*(1+tolerance(temp_c))
    vmin,vmax=(1.176,1.224) if rising else (1.09,1.15)
    return (vmin*(1+lo/bothi)-I_LEAK*lo,
            vmax*(1+hi/botlo)+I_LEAK*hi)

def inductor_ripple(vin,vout=5, l_h=15e-6, fs=400000, iout=2):
    ripple=(vin-vout)*vout/(vin*l_h*fs)
    return {"ripple_A_pkpk":ripple,"Ipeak_A_ideal":iout+ripple/2}

def study():
    return {
        "status":"ENGINEERING_ONLY_NO_FAB",
        "mode":"MODE12_GND_AUTO_RETRY",
        "latch_alternative":"MODE12_OPEN_requires_SHDN_or_UVLO_reset_or_IN_SYS_power_cycle",
        "retry_TSD_ms_min_typ_max":[500,648,800],
        "pgth":"PGTH16_GND_RESTART_DVDT_TPS_PGOOD_STAYS_LOW",
        "tps_2x_IOL_pulse_enabled":False,
        "tps_IOL_nominal_A":3.0,
        "tps_IOL_is_not_RAW_branch_0p5A_limit":True,
        "tps_junction_TSD_typ_C":165,
        "ambient_85C_safe_OFF_present":False,
        "reverse_short_or_repeated_auto_retry_safe_tested":False,
        "OVP_factory_rising_min_max_V":[33.2,35.4],
        "OVP_factory_falling_min_max_V":[32.7,35.0],
        "OVP_32V_recovery_margin_min_V":.7,
        "uvlo_one_r_Rmin_Rmax_85C_ohm":rtop_corner(85),
        "uvlo_one_r_Rmin_Rmax_minus20C_ohm":rtop_corner(-20),
        "A24_56k_rise_minus20C_V":uvlo_edges(56000,-20,True),
        "A24_68k_rise_minus20C_V":uvlo_edges(68000,-20,True),
        "A24_56k_rise_85C_V":uvlo_edges(56000,85,True),
        "A24_68k_rise_85C_V":uvlo_edges(68000,85,True),
        "A24_required":False,
        "A23_10V_full_load_verified":False,
        "buck_ripple_10V":inductor_ripple(10),
        "buck_ripple_32V":inductor_ripple(32),
        "buck_fbt_100k_fbb_24k9_nominal_v":1*(1+100000/24900),
        "min_effective_output_C_total_verified":False,
        "host_to_A23_schematic_interface_completed":False,
        "RAW_selective_fault_limit_present":False,
        "58V_350ms_at_IC_pads_measured":False,
        "PCB_present":False
    }

if __name__=="__main__":
    print(json.dumps(study(),indent=2))
