#!/usr/bin/env python3
"""Current TripPower VS-only EN PNP/NPN interlock; arithmetic check, no vehicle release."""
import json
from pathlib import Path
root=Path("hardware/modules/TripPower_5V2A")
p=(root/"01_Protection_LM74930.kicad_sch").read_text()
s=(root/"03_VS_READY_TPS3760.kicad_sch").read_text()
l=(root/"TripPower_Sym.kicad_sym").read_text()
for ref,value in [("Q303","PMBTA92-Q"),("Q304","PMBTA42-Q"),("Q305","PMBTA42-Q"),("R336","47k"),("R337","220k"),("R339","1M"),("R340","1M"),("R341","100k")]:
 assert f'(property "Reference" "{ref}"' in s and value in s,ref
assert '(symbol "PNP_B1_E2_C3"' in l and '(symbol "NPN_B1_E2_C3"' in l
assert "68k PNP OUTPUT CURRENT LIMIT" in p and "22k EN PULLDOWN" in p
assert "825k 1% VS-SENSE" in s and "1M 1% RESET FEEDBACK" in s
assert "BAS116Q_A1_K3_NC2" in p and "RUN_SINK_C" in p
assert '(at 405.13 350.52 0) (unit 1) (in_bom yes) (on_board yes) (dnp yes)' in p
vout=8*22/(68+22)
ib_pnp=max(0,(8-.7)/220e3-.7/47e3)
ib_ready=max(0,(8-.7)/(1e6+1e6)-.7/1e6)
pmax=65**2/(4*68e3)
rmax=65**2/68e3
offlimit=(.41/22e3-.2e-6)*1e6
assert vout>1.05 and ib_pnp>0 and ib_ready>0
assert pmax<.016 and .06<rmax<.07 and offlimit>18
print(json.dumps({"stage":"NEW_VS_ONLY_ENABLE_SWITCH_ARITHMETIC","pass":True,
 "vehicle_release":False,
 "vs_supply":"Q303 PNP emitter to VS, collector through R318 68k to CTRL_EN",
 "interlock":"Q304 RESET-high NPN in series with Q305 RUN-high NPN; R319 0R bypasses RUN in AUTO",
 "usb_backfeed":"D305 BAS116Q SOT23 K3/A1/NC2 reverse-blocks RUN_BASE Q305 collector feed",
 "math":{"VS8_ideal_EN_v":round(vout,3),"PNP_8V_base_drive_uA":round(ib_pnp*1e6,2),
 "READY_NPN_8V_base_drive_uA":round(ib_ready*1e6,2),
 "NPN_min_gain_needed_nominal":round(ib_pnp/ib_ready,1),
 "PNP_upper_power_w_at_VS65_resistoronly":round(pmax,4),
 "R318_upper_power_w_at_VS65":round(rmax,4),
 "PNP_125C_max_allowed_leak_uA_at_EN":round(offlimit,2)},
 "blockers":["No min hFE at 20uA and cold/hot; cannot guarantee RUN/AUTO on",
 "No max 125C PNP collector leakage; cannot guarantee EN<0.41V",
 "R332 hysteresis influenced by RESET base load, R330825k/R3321M is provisional",
 "202V SOA, F_MAIN, 9V charge pump, prototype thermal/DRC remain blocked"]},indent=2))
