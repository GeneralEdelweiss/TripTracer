#!/usr/bin/env python3
"""TripPower 80-V Weg A: supplier MPN/landpattern locks and transparent limits.

PASS never denotes guaranteed 9-V start, hot 2-A output, 200-V load dump,
PCB DRC, F_MAIN I2t or automotive/production approval.
"""
from pathlib import Path
import math, json, re

base=Path("hardware/modules/TripPower_5V2A")
design=json.loads((base/"REV5_DESIGN_BASELINE.json").read_text(encoding="utf-8"))
assert design["target"]["VIN_at_connector_v"] == [9,30]
assert design["target"]["separate_unsuppressed_load_dump_target"]=={"v":200,"duration_s":0.35}
assert design["authorization"]["branch_a_80v_only"] is True
assert design["authorization"]["automotive_released"] is False
assert design["authorization"]["manufacturing_released"] is False

buck=(base/"02_5V_LMR38020.kicad_sch").read_text(encoding="utf-8")
front=(base/"01_Protection_LM74930.kicad_sch").read_text(encoding="utf-8")
assert buck.count('(property "Reference" "L101"') == 1
assert front.count('(property "Reference" "C306"') == 1
for f,ref,v,mpn,fp in [
 (buck,"L101","15uH Bourns SRP7050TA-150M AEC-Q200","SRP7050TA-150M","Tripmaster:L_BOURNS_SRP7050TA_150M"),
 (front,"C306","47uF 63V Panasonic ZC AEC-Q200","EEHZC1J470P","Capacitor_SMD:CP_Elec_8x10.5")]:
 p=f.index('(property "Reference" "'+ref+'"')
 span=f[p:f.index("(instances",p)]
 assert '(property "Value" "'+v+'"' in span
 assert '(property "MPN" "'+mpn+'"' in span
 assert '(property "Footprint" "'+fp+'"' in span

foot=(base/"Tripmaster.pretty/L_BOURNS_SRP7050TA_150M.kicad_mod").read_text(encoding="utf-8")
assert '(footprint "L_BOURNS_SRP7050TA_150M"' in foot
assert foot.count('(pad "')==2, "two physical power pads only"
for pnum,x in [(1,"-2.725"),(2,"2.725")]:
 assert f'(pad "{pnum}" smd rect (at {x} 0) (size 2.95 3.50)' in foot
# Manufacturer recommended pad outer span 8.4 mm, inter-pad gap 2.5 mm.
assert abs((2*2.725+2.95)-8.4)<1e-8
assert abs((2*2.725-2.95)-2.5)<1e-8
assert all(buck.count(f'(property "Reference" "C{n}"')==1 for n in [104,105,106]), "3x22uF TI reference bank retained"

# LMR38020-Q1 high-side ILIMIT min 2.6A, 400k nominal with 320k min.
# Inductor +-20% nameplate at 25C, DC-bias/hot drop not vendor-guaranteed.
def ripple(vin,l_uh,f_khz):
 return (vin-5)*(5/vin)/(l_uh*1e-6*f_khz*1e3)
peak_ripple_9 = ripple(9,12,320)
peak_ripple_30 = ripple(30,12,320)
peak_i_30 = 2+peak_ripple_30/2
min_hs_limit=2.6
assert peak_i_30<min_hs_limit, "nominal +/-20% L and -20% fsw limit has no arithmetic margin"
# This is only 57 mA margin BEFORE effective inductance loss at hot/bias;
# if effective L drops further 20%, current limit headroom is negative.
peak_i_30_biased = 2+ripple(30,9.6,320)/2

rvs=3*3300
v_pulse=200
v_zener_typ=56
i=(v_pulse-v_zener_typ)/rvs
per_r_W=i*i*3300
per_r_J=per_r_W*.350
zener_W=v_zener_typ*i
zener_J=zener_W*.350
# CRCW2512-HP rated P70=1.5W, max film temp 155C (per Vishay).
rated_cont_125=1.5*(155-125)/(155-70)
# THIS DOES NOT PASS OR FAIL 350ms pulse capability.
vready_high_scenario=7.510
i_rvs_at_9=(9-vready_high_scenario)/rvs

result={
 "result":"PASS_80V_BRANCH_A_SOURCE_AND_ARITHMETIC_ONLY__FATIGUE_AND_HOT_TESTS_BLOCKED",
 "configuration":"LMR38020SQDDARQ1 + SRP7050TA-150M 15uH AEC-Q200 + Panasonic EEHZC1J470P",
 "source_locked_footprint_2pad":True,
 "f_main_external_still_required":True,
 "output_2a_possible_not_thermally_certified":True,
 "inductor_min_nameplate_uh":12,
 "inductor_ripple_pp_a_30v_320khz_12uh":round(peak_ripple_30,4),
 "buck_2a_30v_peak_a_with_12uh":round(peak_i_30,4),
 "buck_hs_current_limit_min_a":min_hs_limit,
 "margin_to_hs_limit_a_at_12uh_nameplate_min":round(min_hs_limit-peak_i_30,4),
 "hypothetical_30v_peak_a_if_extra_inductance_drops_20percent":round(peak_i_30_biased,4),
 "risk_L_bias_temp_can_exceed_min_hs_current_limit":peak_i_30_biased>=min_hs_limit,
 "rvs_200v_350ms_typ_vz_per_resistor_w":round(per_r_W,4),
 "rvs_200v_350ms_typ_vz_per_resistor_j":round(per_r_J,4),
 "crcw2512hp_derated_continuous_at_125c_w_NOT_PULSE_APPROVAL":round(rated_cont_125,4),
 "zener_200v_350ms_typ_power_w":round(zener_W,4),
 "zener_200v_350ms_typ_energy_j":round(zener_J,4),
 "rvs_9v_vs7p510_static_feed_uA":round(1e6*i_rvs_at_9,1),
 "manufacturer_proof_gates":["9V dynamic VS/CAP current and Ceff with slow/ramped VIN","9V/30V 2A buck current limit after L hot-bias","200V Q301 hot SOA/overshoot; 56V Zener and 3x2512 pulse curve @125C","C306 63V transient max pad voltage, leakage/hot life and polarity","new L101 landpattern stencil and 2-pad EDA model; KiCad native ERC/Netlist; PCB DRC and 3D model still missing","external F_MAIN cable/PCB I2t"],
 "manufacturing_released":False,
 "automotive_released":False
}
print(json.dumps(result,indent=2,ensure_ascii=False))
