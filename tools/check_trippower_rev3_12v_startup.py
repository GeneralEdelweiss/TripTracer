#!/usr/bin/env python3
"""REV3 R330=715k candidate: 9V/12V VS precharge comparison with RESET delay.

Illustrative RC/hysteresis sensitivity only. NO dynamic VS pump input-current
upper bound, full-temp BJT guarantee, transient SPICE, bench or 202V release.
"""
import json, math
from itertools import product
from pathlib import Path

base=Path("hardware/modules/TripPower_5V2A")
sch=(base/"03_VS_READY_TPS3760.kicad_sch").read_text(encoding="utf-8")
protect=(base/"01_Protection_LM74930.kicad_sch").read_text(encoding="utf-8")
assert '(property "Value" "715k 1% VS-SENSE REV3 12V START EXP"' in sch
assert '(property "MPN" "CRCW1206715KFKEA"' in sch
assert '(property "Reference" "C311"' in sch and '330nF 100V X7R AEC-Q200 CTR REV4' in sch and 'C1206C334K1RACAUTO' in sch
assert '(property "Reference" "C308"' in protect and '(property "Reference" "C312"' in protect
assert protect.count('10uF 100V VS STARTUP RESERVOIR X7R REV4')==2
assert protect.count('KAF55CR72A106KV')==2
assert '3.3k 2512 PULSE CANDIDATE' in protect
RVS=9900.0
RTOP=715e3
R_BOTTOM=100e3
R_FB=R_PULL=R_Q304=1e6

def rise(a,b,c,threshold=.8,hyst=.016,vol=.0,sense_bias=0.):
    return (threshold+hyst)*(1+a/b+a/c)-(a/c)*vol+a*sense_bias

def fall(a,b,c,d,e,threshold=.8,vbe=.7,sense_bias=0.,reset_leak=0.):
    A=threshold*(1+a/b+a/c)+a*sense_bias
    denom=(1+a/c)/d+1/c+1/e
    reset=(A/d+threshold/c+vbe/e-reset_leak)/denom
    return A-(a/c)*reset

bounds=[]
for corner in product((.99,1.01), repeat=5):
    a,b,c,d,e=(x*y for x,y in zip((RTOP,R_BOTTOM,R_FB,R_PULL,R_Q304),corner))
    for vth,h,vl,vbe,ibias,ileak in product(
        (.792,.808),(.016*.985,.016*1.015),(0,.3),(.55,.95),
        (-100e-9,100e-9),(-300e-9,300e-9)
    ):
        bounds.append((rise(a,b,c,vth,h,vl,ibias),
                       fall(a,b,c,d,e,vth,vbe,ibias,ileak)))
on_nom=rise(RTOP,R_BOTTOM,R_FB)
off_nom=fall(RTOP,R_BOTTOM,R_FB,R_PULL,R_Q304)
on_min=min(x[0] for x in bounds)
on_max=max(x[0] for x in bounds)
off_min=min(x[1] for x in bounds)
off_max=max(x[1] for x in bounds)
assert 7.22<on_nom<7.25 and 5.42<off_nom<5.46
assert 6.7<on_min<6.8 and 7.49<on_max<7.53
assert 5.1<off_min<5.2 and 5.72<off_max<5.77
assert off_min>4., "Do not model nominal supervisor-off below LM74930 VS operating minimum"
assert on_min>6., "Do not model initial charge-pump release below TI VS>=6V CAP-source-current condition"

# Illustrative pre-start budget drawn from REV2 proof gate, not certified
# at any temperature. Model constant-current load, nominal 21uF VS
# (C302 1uF + C308/C312 10uF each), nominal 0.420s TPS3760 CTR delay.
# No controller charge-pump activity here.
OFF_UA=34.6
C_VS=21e-6
TDELAY=.420
# TPS3760-Q1 Rev.B §7.3.4.1 Eq.1–3 / §6.5: RCTR 877k/1M/1147k.
# Conditional ceramic 330nF capacitor envelope: initial +/-10% multiplied by
# X7R-temperature +/-15%. C311 MPN is now fixed, but an exact Ceff/aging
# guarantee still requires vendor-specific bias and insulation data; these extremes
# ARE NOT guaranteed for the actual build. DC-bias, aging and leakage excluded.
C_CTR_NOM=330e-9
CTR_R_MIN=877e3
CTR_R_TYP=1e6
CTR_R_MAX=1147e3
C_CTR_ASSUMED_MIN=C_CTR_NOM*.90*.85
C_CTR_ASSUMED_MAX=C_CTR_NOM*1.10*1.15
TCTR_CONDITIONAL_MIN=-math.log(.31)*CTR_R_MIN*C_CTR_ASSUMED_MIN
TCTR_TYP=-math.log(.28)*CTR_R_TYP*C_CTR_NOM
TCTR_CONDITIONAL_MAX=-math.log(.25)*CTR_R_MAX*C_CTR_ASSUMED_MAX
assert .25<TCTR_CONDITIONAL_MIN<.27
assert .419<TCTR_TYP<.422
assert .66<TCTR_CONDITIONAL_MAX<.67
def vs_after_reset_delay(vin,threshold,delay_s):
    v_eq=vin-RVS*OFF_UA*1e-6
    return v_eq-(v_eq-threshold)*math.exp(-delay_s/(RVS*C_VS))
VS9_AFTER_CONDITIONAL_EARLIEST_RELEASE=vs_after_reset_delay(
    9.,on_max,TCTR_CONDITIONAL_MIN)
assert 8.2<VS9_AFTER_CONDITIONAL_EARLIEST_RELEASE<8.4
# This is *not* a bound on real start: OFF_UA, C_VS and upper READY voltage
# aren't guaranteed, nor is pump I(VS,t), and RESET could reassert.
VS_EFFECTIVE_CORNER_HYP=12e-6   # arbitrary sensitivity, NOT a guaranteed ceramic Ceff
VS_PUMP_TOLERABLE_AVERAGE_I_A_IF_NO_RVS_REPLENISH=(
    (VS9_AFTER_CONDITIONAL_EARLIEST_RELEASE-6.)*VS_EFFECTIVE_CORNER_HYP/0.003031)
assert .008<VS_PUMP_TOLERABLE_AVERAGE_I_A_IF_NO_RVS_REPLENISH<.010
VIRTUAL_OLD_ON=8.221
VIRTUAL_OLD_ON_HIGH=8.539
VIRTUAL_OLD_OFF=5.998
def precharge(vin, vready):
    v_eq=vin-RVS*OFF_UA*1e-6
    tau=RVS*C_VS
    if vready>=v_eq:
        return {"crossing_ms":None,"release_vs_v":None}
    crossing=-tau*math.log(1-vready/v_eq)
    after=v_eq-(v_eq-vready)*math.exp(-TDELAY/tau)
    return {"crossing_ms":round(crossing*1e3,1),"release_vs_v":round(after,3)}

matrix=[]
for vin in (9.0,12.0,13.8,24.0,30.0):
    new=precharge(vin,on_nom)
    old=precharge(vin,VIRTUAL_OLD_ON)
    matrix.append({"vin_fused_v":vin,
       "RVS_feed_at_model_upper_rising_threshold_ua":round((vin-on_max)/RVS*1e6,1),
       "old_RVS_feed_at_model_upper_rising_threshold_ua":round((vin-VIRTUAL_OLD_ON_HIGH)/RVS*1e6,1),
       "REV3_on_nom":new,"REV2_comparison_nom":old,
       "guaranteed_first_start":False})
assert matrix[0]["RVS_feed_at_model_upper_rising_threshold_ua"]>140
assert matrix[0]["RVS_feed_at_model_upper_rising_threshold_ua"]<160
assert 8.4<matrix[0]["REV3_on_nom"]["release_vs_v"]<8.6
assert matrix[0]["REV2_comparison_nom"]["release_vs_v"]>8.5

print(json.dumps({
 "experiment":"REV4 R330715K VS_READY with 330nF 100V automotive CTR RESET delay",
 "evidence":"RC and TI/Vbe hypothetical tolerance scenarios only; no SPICE nor bench",
 "old_REV2_nominal_vs_threshold_v":{"on":VIRTUAL_OLD_ON,"off":VIRTUAL_OLD_OFF},
 "new_REV3_nominal_vs_threshold_v":{"on":round(on_nom,3),"off":round(off_nom,3)},
 "new_REV3_non_guaranteed_vs_threshold_scenario_v":{"on_min":round(on_min,3),
     "on_max":round(on_max,3),"off_min":round(off_min,3),"off_max":round(off_max,3)},
 "assumptions":{"constant_OFF_VS_consumption_ua":OFF_UA,"Ceff_vs_nominal_uF":21.,
     "Ceff_pump_corner_hyp_uF":VS_EFFECTIVE_CORNER_HYP*1e6,
     "TPS3760_reset_delay_TYP_ms":TDELAY*1e3,
     "TI_min_CAP_current_VS_ge_6V_NOT_VS_SUPPLY_CURRENT":True},
 "matrix":matrix,
 "reset_C311_TPS3760_timing_conditional_not_yet_guaranteed":{
    "RCTR_kohm_min_typ_max":[877,1000,1147],
    "assumed_C311_nom_nF":330,
    "assumed_initial_cap_tolerance_pct":10,
    "assumed_X7R_temp_delta_pct":15,
    "delay_ms_min_typ_max_under_these_assumptions":[
        round(TCTR_CONDITIONAL_MIN*1e3,1),
        round(TCTR_TYP*1e3,1),
        round(TCTR_CONDITIONAL_MAX*1e3,1)],
    "VS9_at_delay_end_for_upper_model_ready_threshold_and_34p6uA_model_V":round(VS9_AFTER_CONDITIONAL_EARLIEST_RELEASE,3),
    "VS9_to_6V_12uF_3p031ms_average_draw_limit_mA_model_ONLY":round(VS_PUMP_TOLERABLE_AVERAGE_I_A_IF_NO_RVS_REPLENISH*1e3,2),
    "NOT_GUARANTEED":"C311 330nF MPN fixed but DC bias/aging/leak unverified; two C308/C312 ceramic Ceff/leak unverified, hypothetical 34.6uA OFF total, REV3 trip temp/BJT, dynamic VS current, partial-discharge restart"
 },
 "failure_modes_unchanged":["Actual CAP pump I(VS,t) unknown, C308/C312 and C311 T/age/leak not qualified",
    "Reset delay at cold and hot is not necessarily nominal 420ms",
    "PNP/NPN 20uA-gain and 125C leakage are not supplier guaranteed",
    "202V/350ms MOSFET SOA, F_MAIN and PCB thermal not released"],
 "result":"MODEL_PASS__FUNCTIONAL_AND_VEHICLE_RELEASE_BLOCKED"
},indent=2,ensure_ascii=False))
