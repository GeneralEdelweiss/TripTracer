#!/usr/bin/env python3
"""Read-only TripPower TPS3760 RESET → Q303 gated LM74930 EN screening.
Success means topology and *stated arithmetic* match KiCad, NOT guaranteed
hot off voltage, 9V startup, ISO 16750-2, F_MAIN or automotive qualification.
"""
import json
from pathlib import Path
base=Path("hardware/modules/TripPower_5V2A")
p=(base/"01_Protection_LM74930.kicad_sch").read_text("utf-8")
s=(base/"03_VS_READY_TPS3760.kicad_sch").read_text("utf-8")
lib=(base/"TripPower_Sym.kicad_sym").read_text("utf-8")
d=json.loads((base/"lm74930_design_v1.json").read_text("utf-8"))
assert d["nominal_input_range_v"]==[9,30]
for ref,part in (
("Q303","BVSS123LT1G"),("D306","BAS70-02V-HG3-08"),
("D307","SZMMSZ5240BT1G"),("D308","BAS70-02V-HG3-08"),
("R334","470k 1%"),("R335","1M 1%")):
  assert f'(property "Reference" "{ref}"' in s,ref
  assert part in s,part
assert "(symbol \"EN_PASS_NMOS_GSD\"" in lib
assert '(property "Reference" "R318"' in p and "22k VS TO AUTO_REQ" in p
assert '(property "Reference" "R316"' in p and "5.6k EN PULLDOWN" in p
assert '(global_label "EN_REQUEST_RAW"' in p
assert '(global_label "EN_REQUEST_RAW"' in s
assert '(at 405.13 350.52 0) (unit 1) (in_bom yes) (on_board yes) (dnp yes)' in p
# Conservative comparator specs are guaranteed for stated datasheet tests:
ven_rise_max=1.05
ven_fall_min=.41
r_auto=22e3
r_out=5.6e3
r_run=4.7e3
min_vs_ready_candidate=8
run_nominal=3.3
d305_assumed_vf=.8
auto_en_resistive_limit=min_vs_ready_candidate*r_out/(r_auto+r_out)
run_en_resistive_limit=(run_nominal-d305_assumed_vf)*r_out/(r_run+r_out)
leak_bvss_max_125a=60e-6  # TJ 125C at VDS100V VGS0, not at schottky Vf gate
leak_out_model=leak_bvss_max_125a*r_out
r_top_gate=470e3
r_btm_gate=1e6
gate_ideal_8v=8*r_btm_gate/(r_top_gate+r_btm_gate)
gate_8v_3ua_zener_leak_sensitivity=(8/r_top_gate-3e-6)/(1/r_top_gate+1/r_btm_gate)
# Q303 dissipates from R318 while VS high; source follower, no measured drain current
p30_inrush_sensitivity=(30-7)**2/r_auto
p56_surge_sensitivity=(56-7)**2/r_auto
assert auto_en_resistive_limit>ven_rise_max
assert run_en_resistive_limit>ven_rise_max
assert leak_out_model+0.2e-6*r_out < ven_fall_min  # only if VGS remains <=0!
assert p56_surge_sensitivity>0.1 and p30_inrush_sensitivity<0.03
assert 5.4 <gate_ideal_8v <5.5 and gate_8v_3ua_zener_leak_sensitivity>4.0
print(json.dumps({
 "check":"TPS3760_RESET_INTERLOCK_KICAD_TOPOLOGY_AND_ARITHMETIC",
 "pass":True,
 "release":False,
 "gating":"Q303 N-FET drain EN_REQUEST_RAW source CTRL_EN; RESET LOW clamps gate D306 and EN D308",
 "AUTO_then_Q303":"VS via R31822k R3190R to EN_REQUEST_RAW; R316 5.6k CTRL_EN to ground",
 "RUN_then_Q303":"RUN_CMD via R3174.7k D305 to EN_REQUEST_RAW; no direct RUN-to-CTRL_EN net",
 "C309":"DNP; CTR C311 produces adjustable reset release delay",
 "bounds":{
   "LM74930_VENR_max_v":ven_rise_max,
   "LM74930_VENF_min_v":ven_fall_min,
   "VS_8V_AUTO_ohmic_ideal_EN_v":round(auto_en_resistive_limit,3),
   "3p3V_RUN_assumed_D305Vf_0p8V_ohmic_EN_v":round(run_en_resistive_limit,3),
   "onsemi_Q303_IDSS_125C_100V_60ua_hypothetical_off_EN_v":round(leak_out_model,3),
   "Q303_GATE_8V_no_zener_leak_v":round(gate_ideal_8v,3),
   "Q303_GATE_8V_with_hyp_3ua_zener_leak_v":round(gate_8v_3ua_zener_leak_sensitivity,3),
   "Q303_30V_source7V_hyp_continuous_W":round(p30_inrush_sensitivity,3),
   "Q303_56V_source7V_hyp_350ms_W":round(p56_surge_sensitivity,3),
 },
 "blocked":[
  "Cold and hot VGS variation and MOSFET source-follower min EN; gate Zener 10V breakdown specified at high test current, only tens of uA in actual circuit",
  "Q303 hot 125C IDSS guaranteed only at VGS0 and VDS100V, D306 clamp gate may be +Vf, D308 Vf/leak at 125C not qualified",
  "Q303 transient thermal at 56V VS 350ms may exceed thermal derated DC; P56 model is 109mW",
  "U302 RESET VDD below VPOR1.4V undefined, input EN must remain LOW on first bootstrap",
  "9V startup and protection 202V 350ms Q301 SOA, external F_MAIN not approved",
  "R334/R335 & upstream series resistors component MPNs and mechanical DRC not selected",
 ],},indent=2,ensure_ascii=False))
