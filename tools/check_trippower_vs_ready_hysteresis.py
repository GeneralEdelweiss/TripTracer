#!/usr/bin/env python3
"""VS_READY 8V rise/6V fall and 250ms delay predesign sensitivity.

All outputs explicitly preliminary: NO guarantee at any VIN, no asserted
physical CAP pump VS draw bound; 200V/350ms and RUN path unchanged.
"""
import json,math
from pathlib import Path
base=Path("hardware/modules/TripPower_5V2A")
s=(base/"01_Protection_LM74930.kicad_sch").read_text(encoding="utf-8")
d=json.loads((base/"lm74930_design_v1.json").read_text(encoding="utf-8"))
for ref in ("C302","C303","C308","C309","R313","R314","R315","R316","R318","R319","D305"):
    assert f'(property "Reference" "{ref}"' in s
assert d["nominal_input_range_v"] == [9,30]
VREADY_ON=8.;VREADY_OFF=6.;DELAY=0.25
RVS=9900.;R_AUTO=200000.
Iq_off=5e-6;Icap_leak=10e-6; Isuper_max=2.6e-6; Isense=0.1e-6
Istatic=Iq_off+Icap_leak+Isuper_max+Isense
Cnom=11e-6;Ccorner=8.5e-6
req=1/(1/RVS+1/R_AUTO)
tau=req*Cnom
time_pump=(470e-9*7.9/1.3e-3)+175e-6  # sensitivity ONLY, 175us typ
out=[]
for vin in [9,10,12,13.8,24,30]:
    equilibrium=(vin-RVS*Istatic)/(1+RVS/R_AUTO)
    crossover=None if equilibrium<=VREADY_ON else -tau*math.log(1-VREADY_ON/equilibrium)
    release=None if crossover is None else equilibrium-(equilibrium-VREADY_ON)*math.exp(-DELAY/tau)
    feed=(vin-release)/RVS if release is not None else None
    # I_extra is UNSPECIFIED theoretical supply draw, deliberately free param
    traces=[]
    for iex in [2e-3,5e-3,8e-3]:
        worst_assumed=release - max(0,iex+0.780e-3-feed)*time_pump/Ccorner if release else None
        traces.append({"hypothetical_extra_VS_draw_mA":iex*1e3,
                       "VS_min_model_v":round(worst_assumed,3) if worst_assumed is not None else None,
                       "stays_above_6v_under_model_ONLY": worst_assumed>=VREADY_OFF if worst_assumed else False})
    out.append({"VIN_v":vin, "OFF_VS_estimate_v":round(equilibrium,3),
        "VS_8v_crossing_ms":round(crossover*1e3,1) if crossover else None,
        "vs_at_250ms_post_ready_delay_v":round(release,3) if release else None,
        "pulse_supply_current_input_approx_not_max_mA":round(feed*1e3,3) if feed else None,
        "hypothetical_pump_cases":traces,
        "guaranteed_start":False})
assert out[0]["OFF_VS_estimate_v"]>8
assert out[0]["OFF_VS_estimate_v"]<8.5
assert out[0]["hypothetical_pump_cases"][0]["stays_above_6v_under_model_ONLY"]
assert not out[0]["hypothetical_pump_cases"][2]["stays_above_6v_under_model_ONLY"]
print(json.dumps({
"status":"HISTORICAL_PRE_IMPLEMENTATION_VS_READY_TARGETS_ONLY__REAL_Q303_CIRCUIT_NOT_MODELED",
"targets":{"VS_ready_on_nominal_v":VREADY_ON,"VS_ready_off_nominal_v":VREADY_OFF,
           "hysteresis_nominal_v":VREADY_ON-VREADY_OFF,"stable_ready_delay_nominal_ms":DELAY*1000},
"notes":["HISTORICAL 8V/6V preliminary sensitivity; current KiCad has U302 R330-R333 feedback and Q303 gated AUTO/RUN, not modeled here",
         "RUN_CMD must be AND-gated by VS_READY independent of RUN high",
         "LM74930 VS pump input transient upper bound not established by TI CAP output current",
         "C308/C302 Ceff not manufacturer guaranteed in intended temp and VS clamp",
         "Product supervisor exact 8/6 variant unavailable; TPS3760A012DYYRQ1 0.8V/2percent requires added feedback",
         "No mechanical, 200V SOA, fuse, automotive or manufacturing release"],
"model":{"off_currents_uA":[5,10,2.6,0.1],
         "VS_C_nominal_uF":11,"VS_C_corner_hypothetical_uF":8.5,
         "RC_tau_nominal_ms":round(tau*1e3,1),
         "CAP_charge_interval_hypothetical_ms":round(time_pump*1e3,3)},
"VIN_cases":out},indent=2,ensure_ascii=False))
