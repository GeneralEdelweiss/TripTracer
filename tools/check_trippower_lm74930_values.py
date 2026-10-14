#!/usr/bin/env python3
"""Read-only arithmetic + pin-plan checks for preliminary TripPower LM74930-Q1.
No electrical simulation, native KiCad ERC, physical safety or vehicle sign-off.
Source: TI SNOSDF6 (2023) equations 14-18, sections 7.3.4-7.3.6, 8.2.2.
"""
import json
from pathlib import Path
d=json.loads(Path("hardware/modules/TripPower_5V2A/lm74930_design_v1.json").read_text("utf-8"))
a=d["assumptions"]
r=a["R_sense_ohm"]
rs=a["R_set_ohm"]
ri=a["R_ilim_ohm"]
ris=a["R_iscp_ohm"]
ct=a["C_tmr_f"]
assert d["controller"]=="LM74930QRGERQ1"
assert d["load_dump_design_target_v"]==202
assert set(str(i) for i in range(1,25)) | {"EP"}=={p[0] for p in d["pin_plan"]}
assert "FLOAT" in dict((p[0],p[2]) for p in d["pin_plan"])["EP"]
assert "GND" in dict((p[0],p[2]) for p in d["pin_plan"])["16"]
assert len(d["components"])==len(set(p["ref"] for p in d["components"]))
assert d["aux_output"]["status"].startswith("PRELIMINARY")
# TI Eq.15 nominal ILIM = 12*RSET/(RILIM*RSENSE); comparator tolerance 1.08..1.32V / 1.22V typ.
ilim_nom=12*rs/(ri*r)
ilim_low=ilim_nom*(1.08/1.22)*(.99/(1.01**2))
ilim_high=ilim_nom*(1.32/1.22)*(1.01/(.99**2))
# TI Eq.14 SCP threshold at 20mV + RISCP*I(ISCP); worst data sheet 17.4..22mV, 9.5..12uA
scp_nom=(.020+ris*11e-6)/r
scp_low=(.0174+ris*.99*9.5e-6)/(r*1.01)
scp_high=(.022+ris*1.01*12e-6)/(r*.99)
assert 3.5<ilim_nom<3.8
assert 3.0<ilim_low<3.3
assert 3.9<ilim_high<4.1
assert scp_low>ilim_high, "nominal OCP and fast SCP tolerance ranges overlap"
assert 4.8<scp_nom<5.3
# 9V, simultaneous load under an explicit conservative 80% efficiency assumption
ibuck_85=10/(9*.85)
ibuck_80=10/(9*.8)
i_total=ibuck_80+d["aux_output"]["max_current_design_target_a"]
assert i_total<ilim_low, "steady 9V load can already trip breaker"
# TI Eq 16: TCB approx 1.2CTMR/82.3uA (100k TMR latch resistor affects charging; measured time required)
tcb_nom=1.2*ct/(82.3e-6)
tcb_range=[1.2*ct*.9/(97e-6),1.2*ct*1.1/(65e-6)]
assert .0004<tcb_range[0]<tcb_range[1]<.0011
# TI equations 12,13 and max 200nA OV/UVLO leakage. VIN threshold offset = I_leak*Rtop.
def trip_bounds(vnom,vmin,vmax,rt,rb):
    return {
        "nom": vnom*(1+rt/rb),
        "min": vmin*(1+(rt*.99)/(rb*1.01))-200e-9*rt*.99,
        "max": vmax*(1+(rt*1.01)/(rb*.99))+200e-9*rt*1.01
    }
ov=trip_bounds(.6,.585,.63,a["OV_Rtop_ohm"],a["OV_Rbottom_ohm"])
uv=trip_bounds(.6,.585,.63,a["UV_Rtop_ohm"],a["UV_Rbottom_ohm"])
uv_falling=.55*(1+a["UV_Rtop_ohm"]/a["UV_Rbottom_ohm"])
assert 30<ov["min"]<ov["nom"]<ov["max"]<45
assert uv["max"]<9, "UVLO fails nominal 9V startup under static 1%+leakage stress"
assert 6<uv_falling<8
divider_30=30/(a["OV_Rtop_ohm"]+a["OV_Rbottom_ohm"])+30/(a["UV_Rtop_ohm"]+a["UV_Rbottom_ohm"])
assert divider_30<40e-6
# At 202V, VS clamp nominal ~56V with 3 x 3.32k in series; energy for rectangular worst-case 350ms.
rvs=3*3320
pvs=(202-56)**2/rvs
evs=pvs*.350
pz=56*(202-56)/rvs
assert .7<evs<.8
# Full load combined high VDS 250V candidate FET Rds at 25C max 165mohm
q_hv_worst_25c=(i_total**2)*.165
assert q_hv_worst_25c<1.1
summary={
 "status":"PASS: ARITHMETIC_AND_PINPLAN_ONLY_NOT_SCHEMATIC_OR_THERMAL_APPROVAL",
 "nominal_ocp_a":round(ilim_nom,3),
 "ocp_1pct_comparator_bounds_a":[round(ilim_low,3),round(ilim_high,3)],
 "nominal_fast_scp_a":round(scp_nom,3),
 "fast_scp_1pct_comparator_bounds_a":[round(scp_low,3),round(scp_high,3)],
 "nominal_tmr_ms_no_latch_resistor":round(tcb_nom*1000,3),
 "tmr_component_ic_range_ms_no_latch_resistor":[round(x*1000,3) for x in tcb_range],
 "input_a_at_9v_5v2a_80pct_efficiency":round(ibuck_80,3),
 "combined_9v_input_a_80pct_eff_plus_aux_1a":round(i_total,3),
 "ov_cutoff_nominal_and_leakage_bounds_v":{k:round(v,3) for k,v in ov.items()},
 "uv_start_nominal_and_leakage_bounds_v":{k:round(v,3) for k,v in uv.items()},
 "uv_falling_nominal_v":round(uv_falling,3),
 "passive_dividers_30v_uA":round(divider_30*1e6,2),
 "VS_202v_350ms_series_resistor_total_w_j":[round(pvs,3),round(evs,3)],
 "VS_202v_350ms_each_three_resistor_j":round(evs/3,3),
 "VS_zener_202v_w":round(pz,3),
 "HV_250V_FET_25c_max_rds_w_at_9v_full_combined_load":round(q_hv_worst_25c,3),
 "unverified":["202V thermal/surge and MOSFET SOA","9V dynamic startup/EN","VIN_PROTECTED branch current cut-off, shunt Kelvin, cold hot tolerance",
 "external fuse coordination","full current-sense offset, EMI, layout and real ERC/DRC","supplier MPNs and startup inrush","TMR timing with latch resistor"]
}
print(json.dumps(summary,indent=2,ensure_ascii=False))
