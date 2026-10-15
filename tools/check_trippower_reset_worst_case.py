#!/usr/bin/env python3
"""RESET / Q303 vs TI/onsemi/Vishay published limits, -40..125C.
No analog circuit simulation or automotive sign-off; unknown parameters are
explicit UNPROVEN and a passing script must NEVER signal functional approval.

Sources (manufacturer):
https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf
https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf
https://www.onsemi.com/pdf/datasheet/bss123lt1-d.pdf
https://www.vishay.com/docs/85652/bas70-02v.pdf
"""
from pathlib import Path
from itertools import product
import json
BASE=Path("hardware/modules/TripPower_5V2A")
s=(BASE/"03_VS_READY_TPS3760.kicad_sch").read_text(encoding="utf-8")
p=(BASE/"01_Protection_LM74930.kicad_sch").read_text(encoding="utf-8")
lib=(BASE/"TripPower_Sym.kicad_sym").read_text(encoding="utf-8")
assert 'TripPower_Sym:BAS70_02V_A1_K2' in s
assert '(symbol "BAS70_02V_A1_K2"' in lib
assert '(pin passive line (at -10.16 0 0) (length 5.08) (name "K"' in lib
for pos,mpn in [("U302","TPS3760A012DYYRQ1"),("Q303","BVSS123LT1G"),
   ("D306","BAS70-02V-HG3-08"),("D307","SZMMSZ5240BT1G"),
   ("D308","BAS70-02V-HG3-08")]:
    assert f'(property "Reference" "{pos}"' in s and mpn in s,pos
assert '(at 405.13 350.52 0) (unit 1) (in_bom yes) (on_board yes) (dnp yes)' in p
assert "5.6k EN PULLDOWN" in p and "22k VS TO AUTO_REQ" in p

R330=845e3; R331=100e3; R332=1.91e6; R333=1e6
R334=470e3;R335=1e6;R318=22e3;R316=5.6e3;RVS=9900.
TI_EN_FALL_MIN_V=.41
TI_EN_RISE_MAX_V=1.05
ON_Q303_IDSS_MAX_25_UA=15.
ON_Q303_IDSS_MAX_125_UA=60.
ON_Q303_IDSS_TEST_VGS=0.0
VISHAY_BAS70_IR_MAX_25_NA=100
VISHAY_BAS70_IR_TEST_VR=50
VISHAY_BAS70_IR_TEST_PULSE_US=300
VISHAY_BAS70_VF_MAX_25_1MA_V=.410
TI_U302_VOL_MAX_5MA_V=.3

def switch_thresholds(resistors, vth, hys, reset_low, i_sense):
    a,b,c,d=resistors
    # RESET asserted: KCL into SENSE, R332 to RESET low level
    rising=(vth+hys)*(1+a/b+a/c)-(a/c)*reset_low+a*i_sense
    # RESET deasserted/open drain: VRESET pulled up by R333 to VS
    conductance_to_VS=1/a+1/(c+d)
    falling=vth*(1+1/(b*conductance_to_VS))+i_sense/conductance_to_VS
    return rising, falling

nom_on,nom_off=switch_thresholds([R330,R331,R332,R333],.8,.016,0,0)
corner=[]
for ss in product([.99,1.01],repeat=4):
    r=[v*f for v,f in zip([R330,R331,R332,R333],ss)]
    for vth,hh,vol,isense in product([.792,.808],[.016*.985,.016*1.015],[0,.3],[-100e-9,100e-9]):
        corner.append(switch_thresholds(r,vth,hh,vol,isense))
von_min=min(t[0] for t in corner)
von_max=max(t[0] for t in corner)
voff_min=min(t[1] for t in corner)
voff_max=max(t[1] for t in corner)
assert 7.63<von_min<7.64 and 8.38<von_max<8.40
assert 5.80<voff_min<5.83 and 6.26<voff_max<6.28
assert abs(nom_on-8.0722052356)<1e-6
assert abs(nom_off-6.0387749667)<1e-6

off_current_ta_25=ON_Q303_IDSS_MAX_25_UA*1e-6*R316
off_current_ta_125=ON_Q303_IDSS_MAX_125_UA*1e-6*R316
comparator_leak=200e-9*R316
assert abs(off_current_ta_125-.336)<1e-5
assert off_current_ta_125+comparator_leak<TI_EN_FALL_MIN_V
# CRITICAL: above test uses VGS=0 exactly, current schematic VGS is
# approx VF(Schottky) + VOL(reset) - V(CTRL_EN), NOT specified as 0!
assert not (TI_U302_VOL_MAX_5MA_V + VISHAY_BAS70_VF_MAX_25_1MA_V < TI_EN_FALL_MIN_V)
# Vishay VF max @25C, 1mA, <300us: 0.3+0.410=0.710V.
D308_testcondition_clamp_v=TI_U302_VOL_MAX_5MA_V+VISHAY_BAS70_VF_MAX_25_1MA_V
assert D308_testcondition_clamp_v>.41
# Schottky reverse leakage at 125C is NOT manufacturer bounded.
# 100nA is 25C PULSED at 50V; using as 125C max would be invalid.
Vgate_nom8=8*R335/(R334+R335)
gate_minus_3ua_zener_testpoint= (8/R334-3e-6)/(1/R334+1/R335)
gate_no_zener_at_56=56*R335/(R334+R335)
gate_no_zener_at_65=65*R335/(R334+R335)
assert gate_no_zener_at_56>20 and gate_no_zener_at_65>20
# Gate clamp is only tested at the zener's IZ(T) many mA, NOT
# for 30-110uA from R334. Datasheet does not certify Vg<20V here.
# Q303 power is NOT (VS-EN)^2/R318: that is resistor heat, not FET heat.
r318_p56_if_source7=(56-7)**2/R318
q303_p_upper_56=56**2/(4*R318)  # conservative simple resistor-fed path
q303_p_upper_65=65**2/(4*R318)
q303_pd_dc_allowed_ta125=.225-.0018*(125-25)
assert abs(r318_p56_if_source7-.109136363636)<1e-9
assert q303_p_upper_56<q303_pd_dc_allowed_ta125<q303_p_upper_65
# For this bound, presume no significant independent RUN injection.
# Q303 source follower VGS and dynamic profile determine actual PD.
# R318 worst absolute resistor dissipation when Vdrain~0 is VS^2/R318.
r318_abs56=56**2/R318
r318_abs65=65**2/R318
# Simplified VS precharge envelope: assumes C308 leakage at rated 100V
# can be treated as 10uA at 9V, omits several unspecified hot currents.
i_const=(5+10+2.6)*1e-6
g=1/(R330+R331)+1/R333+1/R334
i_offset=-.3/R333-.7/R334
vs_9_est=(9-RVS*(i_const+i_offset))/(1+RVS*g)
assert 8.45<vs_9_est<8.52
assert 0<vs_9_est-von_max<.2

thermal=[]
for t,idss in [(-40,None),(25,15.),(85,None),(125,60.)]:
    thermal.append({
      "temperature_C":t,
      "Q303_IDSS_max_uA_at_VGS_0_and_VDS_100V_only":idss,
      "R316_EN_ohmic_upper_if_VGS_exactly_0V_v":round(idss*1e-6*R316,4) if idss is not None else None,
      "BAS70_reverse_max_at_this_temp":"100nA at 50V only for pulsed <=300us" if t==25 else "NOT_SPECIFIED",
      "D308_forward_max_under_actual_50uA_2mA_DC_and_temperature":"NOT_SPECIFIED",
      "EN_LOW_below_0p41V_guaranteed_with_current_network":False,
      "EN_HIGH_above_1p05V_guaranteed_with_current_network":False,
    })
data={
"result":"BLOCKED__CURRENT_RESET_Q303_GATE_FAILS_FORMAL_WORST_CASE_SIGNOFF",
"silicon_temperature_envelope_C":[-40,25,85,125],
"datasheet_sources":[
 "https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf",
 "https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf",
 "https://www.onsemi.com/pdf/datasheet/bss123lt1-d.pdf",
 "https://www.vishay.com/docs/85652/bas70-02v.pdf"],
"physical_pin_correction":"BAS70-02V SOD523 manufacturer A1 K2; native KiCad D306,D308 use dedicated TripPower_Sym:BAS70_02V_A1_K2; native netlist check required",
"thresholds_at_1pct_resistors_TPS3760_internal_0p792_to_0p808V_2pct_hysteresis_1p5pct_Vol_0_to_0p3_I_SENSE_plusminus100nA":{
 "nominal_rising_v":round(nom_on,3),"nominal_falling_v":round(nom_off,3),
 "rising_ideal_network_range_v":[round(von_min,3),round(von_max,3)],
 "falling_ideal_network_range_v":[round(voff_min,3),round(voff_max,3)],
 "qualification":"ILLUSTRATIVE_BOUNDED_BEFORE_RESET_LEAK_AND_SCHOTTKY_REVERSE_AND_THERMAL_RESISTOR_DRIFT",
},
"off":{
 "max_allowable_LM74930_EN_low_v":TI_EN_FALL_MIN_V,
 "Q303_IDSS_125C_60uA_into_5p6k_ideal_v":round(off_current_ta_125,3),
 "including_EN_input_0p2uA_ideal_v":round(off_current_ta_125+comparator_leak,3),
 "assumption_VGS_0V_NOT_MET":"RESET LOW can put Q303 G up to RESET VOL + BAS70 VF: positive VGS vs low source; IDSS max does not apply",
 "TI_U302_RESET_VOL_5mA_max_v":TI_U302_VOL_MAX_5MA_V,
 "BAS70_VF_max_25C_1mA_300us_v":VISHAY_BAS70_VF_MAX_25_1MA_V,
 "D308_possible_clamp_at_datasheet_test_current_vol_plus_vf_v":round(D308_testcondition_clamp_v,3),
 "result":"FAIL_TO_PROVE_EN_BELOW_0p41V_ALL_TEMPERATURES_AND_INPUTS"
},
"ready_high":{
 "BVSS123_max_RDS_6ohm_SPEC_AT_VGS10V_ID100mA_25C_NOT_AT_CIRCUIT_GATE_BIAS":True,
 "auto_8v_resistive_EN_ideal_v":round(8*R316/(R318+R316),3),
 "Q303_GATE_8V_zero_zener_current_nom_v":round(Vgate_nom8,3),
 "Q303_GATE_8V_with_hypothetical_3uA_Zener_leak_v":round(gate_minus_3ua_zener_testpoint,3),
 "source_follower_9V_cold_guaranteed_on":"NO__NO_MIN_ID_OR_MAX_RDS_AT_VGS3p0_TO_4p5V_ACROSS_COLD_HOT"
},
"gate":{
 "BVSS123_continuous_abs_max_VGS_v":20,
 "gate_if_no_zener_at_VS56_v":round(gate_no_zener_at_56,3),
 "gate_if_no_zener_at_VS65_v":round(gate_no_zener_at_65,3),
 "D307_zener_10V_test_conditions":"MANUFACTURER_IZT_AT_MILLIAMPS__DOES_NOT_GUARANTEE_10V_AT_100uA",
 "Gate_max_rating_proved":"NO__PER_COMPONENT_LOW_CURRENT_VZ_GUARANTEE_MISSING"
},
"reset_leak":{
 "BAS70_25C_reverse_50V_max_nA":VISHAY_BAS70_IR_MAX_25_NA,
 "BAS70_125C_reverse_limit":"NOT_SPECIFIED",
 "BAS70_DC_reverse_limit":"NOT_SPECIFIED_ONLY_LT_300US_PULSES_IN_DATASHEET",
 "R333_reset_pullup_current_at_56V_0V_reset_uA":round(56/R333*1e6,3),
 "RESULT":"HOT_SCHOTTKY_LEAK_CAN_DISTURB_1M_PULLUP_AND_1p91M_HYSTERESIS_NO_HOT_BOUND"
},
"thermal":{
 "Q303_rated_225mW_25C_derate_1p8mW_per_C_continuous_allowed_125C_mW":round(q303_pd_dc_allowed_ta125*1000,1),
 "Q303_model_simple_R318_resistorfed_max_56V_mW":round(q303_p_upper_56*1000,1),
 "Q303_model_simple_R318_resistorfed_max_65V_mW":round(q303_p_upper_65*1000,1),
 "R318_loss_at_56V_EN7V_mW_NOT_Q303":round(r318_p56_if_source7*1e3,2),
 "R318_absolute_model_max_56V_mW":round(r318_abs56*1000,2),
 "R318_absolute_model_max_65V_mW":round(r318_abs65*1000,2),
 "limitations":"Assumes only passive R318 feed; source/RUN 5V and switching transient, pulse Zth, hot R318 rating undefined; use physics circuit-aware no blind 109mW in FET"
},
"9v_precharge":{
 "VS_off_limit_illustrative_v":round(vs_9_est,3),
 "margin_over_pessimistic_ideal_VS_READY_on_v":round(vs_9_est-von_max,3),
 "status":"UNQUALIFIED__HOT_LEAK_9V_GATE_RESET_DERATING_MORE_THAN_FEW_TENTHS_CAN_PREVENT_START"
},
"thermal_matrix":thermal,
"open_gates":[
 "MANDATORY: different low-leakage high-temperature, fail-safe logic to guarantee EN <0.41V when U302 RESET asserted (incl VDD<1.4V)",
 "MANDATORY: adequate gate VGS clamp at actual 20-140uA across temperature and source follower minimum VGS/EN thresholds",
 "MANDATORY: switch RESET-feedback and inhibit diodes to max-125C leakage specified candidates before 8/6 thresholds release",
 "MANDATORY: 9V startup with VIN ramp full load and 202V/350ms resistor+Q303 transient stress in native PCB",
 "D306/D308 K2 A1 vendor polarity now reflected in library, but future footprint visual verification still required"
],
"success_meaning":"Native calculation consistency only. Result is deliberately BLOCKED and never means ISO/board release."}
print(json.dumps(data,ensure_ascii=False,indent=2))
