#!/usr/bin/env python3
"""REV6 A coil and 5-V/2-A buck conservative ripple screen, not board thermal approval."""
import json,math

def coil_corner(vin,load=2.,vout=5.,freq=400_000.,l_nom=15e-6,l_tolerance=.20,dcr_max=.092):
    if not (vin>vout and load>0 and l_nom>0 and freq>0):raise ValueError("invalid buck scenario")
    l_min=l_nom*(1-l_tolerance)
    ripple=vout*(vin-vout)/(vin*freq*l_min)
    return {"vin_v":vin,"out_v":vout,"load_a":load,
        "L_SRP7050TA_MPN":"SRP7050TA-150M","L_nominal_uH":l_nom*1e6,
        "L_min_uH_at_nominal_tolerance_only":l_min*1e6,
        "switching_frequency_assumed_Hz":freq,
        "inductor_ripple_pp_A":ripple,
        "inductor_peak_A":load+ripple/2,
        "inductor_rms_A":math.sqrt(load**2+ripple**2/12),
        "inductor_dc_loss_at_92mohm_W":dcr_max*(load**2+ripple**2/12),
        "manufacturer_Irms_limit_25C_A":3.5,
        "manufacturer_Isat_typ_A":6.,
        "thermal_and_magnetic_loss_at_plus60C_PROVEN":False}
def study():
    return {"rated_COTs_vendor":"Bourns SRP7050TA-150M 15uH AEC-Q200",
       "10V_2A":coil_corner(10),"32V_2A":coil_corner(32),
       "expected_thermal_note":"Irms/Isat ratings not equivalent to guaranteed +60C winding temperature; PCB copper, AC loss, DC bias and passives need lab measurements",
       "buck_LMR38020_Q1_5V2A_plus60C_PROVEN":False,
       "layout_available":False,
       "fuse_on_tripPower":False,
       "release":False}
if __name__=="__main__":print(json.dumps(study(),indent=2))
