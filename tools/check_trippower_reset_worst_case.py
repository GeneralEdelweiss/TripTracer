#!/usr/bin/env python3
"""Current PNP/NPN TripPower reset interface -40..125C sensitivity.
No simulation, guaranteed transistor min beta, 125C off leakage, or ISO release.
"""
from itertools import product
from pathlib import Path
import json
root=Path("hardware/modules/TripPower_5V2A")
s=(root/"03_VS_READY_TPS3760.kicad_sch").read_text()
p=(root/"01_Protection_LM74930.kicad_sch").read_text()
for r in ("U302","Q303","Q304","Q305","R330","R331","R332","R333","R339"):
 assert f'(property "Reference" "{r}"' in s,r
assert "PMBTA92-Q" in s and "PMBTA42-Q" in s and "RUN_SINK_C" in s
assert "68k PNP OUTPUT CURRENT LIMIT" in p and "22k EN PULLDOWN" in p
R330,R331,R332,R333,R339=715e3,100e3,1e6,1e6,1e6
def on(a,b,c,t,h,vol,ibias):
 return (t+h)*(1+a/b+a/c)-(a/c)*vol+a*ibias
def off(a,b,c,d,e,t,vbe,ibias,resetleak):
 A=t*(1+a/b+a/c)+a*ibias
 denom=(1+a/c)/d+1/c+1/e
 reset=(A/d+t/c+vbe/e-resetleak)/denom
 return A-(a/c)*reset,reset
nom_on=on(R330,R331,R332,.8,.016,0,0)
nom_off,nom_reset=off(R330,R331,R332,R333,R339,.8,.7,0,0)
corners=[]
for factors in product((.99,1.01),repeat=5):
 a,b,c,d,e=[x*y for x,y in zip((R330,R331,R332,R333,R339),factors)]
 for vth,h,vl,vbe,ibias,ileak in product((.792,.808),(.016*.985,.016*1.015),(0,.3),(.55,.95),(-100e-9,100e-9),(-300e-9,300e-9)):
  corners.append((on(a,b,c,vth,h,vl,ibias),off(a,b,c,d,e,vth,vbe,ibias,ileak)[0]))
on_min,on_max=min(x[0] for x in corners),max(x[0] for x in corners)
off_min,off_max=min(x[1] for x in corners),max(x[1] for x in corners)
assert 7.1<nom_on<7.4 and 5.3<nom_off<5.6  # RESET=0V nominal rise 8.22V, RESET=0.3V model ~7.97V
assert on_min<nom_on<on_max and off_min<nom_off<off_max
max_leak_uA=(.41/(22000*1.01)-.2e-6)*1e6
PNP_power_max=65**2/(4*68000)
R318_power_max=65**2/68000
pnp_125W=(150-125)/500
assert 0<PNP_power_max<pnp_125W and 18<max_leak_uA<19
assert 0.06<R318_power_max<0.07
# REV3 experimental R330 715k reduces upper model READY threshold;
# this also starts C308 from lower voltage, so do not infer pump success.
# OFF precharge assumes LM74930 off 5uA, TPS3760 2.6uA,
# Panasonic 10uA, UV divider 9uA, reset pullup 8uA;
# 125C hot reverse leak and supply pump DO NOT have a bound.
vpre9=9-9900*(5+2.6+10+9+8)*1e-6
print(json.dumps({
 "status":"NEW_VS_ONLY_PNP_TOPOLOGY; HOT_125C_AND_9V_STARTUP_NOT_YET_QUALIFIED",
 "temp_cases_c":[-40,25,85,125],
 "references":["https://assets.nexperia.com/documents/data-sheet/PMBTA42-Q.pdf",
 "https://assets.nexperia.com/documents/data-sheet/PMBTA92-Q.pdf",
 "https://www.diodes.com/datasheet/download/BAS116.pdf",
 "https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf",
 "https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf"],
 "schmitt_sensitivity_not_guaranteed":{
 "on_nom_v":round(nom_on,3),"off_nom_v":round(nom_off,3),
 "on_range_v":[round(on_min,3),round(on_max,3)],
 "off_range_v":[round(off_min,3),round(off_max,3)],
 "reset_high_under_NPN_base_loading_at_VS6_model_v":round(nom_reset,3),
 "note":"VBE .55-.95V is a hypothetical scenario, not manufacturer-certified temperature bounds"},
 "off_125C":{
 "LM74930_EN_max_off_v":.41,"PNP_collector_current_limit_required_uA":round(max_leak_uA,2),
 "Nexperia_PM_BTA92_125C_collector_leak_max_uA":"NOT_SPECIFIED at this bias - fails formal release"},
 "on":{
 "LM74930_EN_min_on_v":1.05,
 "vs8_ideal_pnp_enable_v":round(8*22/(68+22),3),
 "Nexperia_min_beta_at_2_to_20uA_125C":"NOT_SPECIFIED - cannot promise drive"},
 "thermal":{
 "PNP_MAX_VS65_RESISTOR_FEED_W":round(PNP_power_max,4),
 "PNP_ALLOWED_125C_FR4_REFERENCE_W":round(pnp_125W,4),
 "R318_65V_BOUND_W":round(R318_power_max,4)},
 "vin_9v_off_voltage_model_v":round(vpre9,3),
 "VIN9_START_GUARANTEED":False,
 "RESET_TO_EN_INTERFACE_TOPOLOGY_FIXED":True,
 "AUTO_RUN_BACKFEED_BLOCKED_BY_D305":"A1 to READY_NPN emitter, K3 to RUN_NPN collector; needs 125C leakage and pin orientation validation",
 "full_automotive_vehicle_release":False,
 "blockers":["125C PNP off leakage unspecified","NPN and PNP minimum beta at 2-20uA, -40..125C unspecified",
 "RESET Sense thresholds vary with Q304 base loading and leakage",
 "9V inrush and 200V/350ms Q301 SOA/F_MAIN not tested"]
},indent=2,ensure_ascii=False))
