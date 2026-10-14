#!/usr/bin/env python3
"""Bounded ACC/HOLD DC resistor checks after the LM74800/LMR38020 EN separation.

NOT a SPICE/transient/hot leakage/automotive qualification. At 9V the LM74800
charge pump draws dynamic current; VS bootstrap via D924 and capacitors must
be measured. Values below are stress assumptions, NOT guaranteed device limits.
"""
from itertools import product
from pathlib import Path
import json
import re

P=Path("hardware/kicad/01H_ACC_HOLD_GATE.kicad_sch").read_text("utf-8")
BUCK=Path("hardware/kicad/02_5V_Buck.kicad_sch").read_text("utf-8")
REFS={
    "R912":("100k 1% E-B OFF","RC1206FR-07100KL"),
    "R923":("100k 1% 0.66W ACC surge","ERJP08F1003V"),
    "R924":("100k 1% NPN base OFF","RC1206FR-07100KL"),
    "R916":("100k 1% 0.66W ACC sense surge","ERJP08F1003V"),
    "R922":("100k 1% BASE LIMIT","RC1206FR-07100KL"),
    "R911":("33k 1% LM748 EN TOP","RC1206FR-0733KL"),
    "R913":("47k 1% LM748 EN OFF","RC1206FR-0747KL"),
}
for ref,(value,mpn) in REFS.items():
    i=P.index('(property "Reference" "'+ref+'"')
    chunk=P[i:i+650]
    assert '(property "Value" "'+value+'"' in chunk, ref
    assert '(property "MPN" "'+mpn+'"' in chunk, ref

assert '(global_label "BUCK_ENABLE" (shape bidirectional) (at 109.22 96.52 0)' not in BUCK
assert '(global_label "HV_PROTECTED_AFTER_EFUSE" (shape bidirectional) (at 109.22 96.52 0)' in BUCK

# 100k base-drive path, 100k E-B turnoff, 33k/47k LM748 EN divider.
rPNP=100000.; rOFF=100000.; rTOP=33000.; rBOT=47000.
# Raw ACC 200V impulse: 100k R923 <=0.40W steady-equivalent; 350ms <=0.14J.
assert 200**2/100000 < .66
assert (200**2/100000)*.350 < .15
assert rTOP+rBOT==80000.
results=[]
for acc,vs in product((9.,12.,24.,30.),(3.5,4.,6.,9.,24.,30.,56.)):
    # 1V VBE, 0.3V Q914 VCE, 0.5V Q915 saturated drop and
    # 1uA EN input/opto leakage are conservative illustrative assumptions.
    npn_ib=(acc-1)/(100000*1.01)-1/(100000*.99)
    npn_sink=max(0,(vs-1.3)/(rPNP*.99))
    pnp_ib=max(0,(vs-1.3)/(rPNP*1.01)-1/(rOFF*.99))
    en_divider=(vs-.5)*(rBOT*.99)/(rTOP*1.01+rBOT*.99)
    en=en_divider-1e-6/(1/(rTOP*1.01)+1/(rBOT*.99))
    pnp_load=max(0,(vs-.5)/(rTOP*.99+rBOT*.99))
    assert npn_ib>0 and npn_sink/npn_ib<10,(acc,vs,"NPN")
    assert pnp_ib>0 and pnp_load/pnp_ib<10,(acc,vs,"PNP")
    assert 1.267<en<vs,(acc,vs,"LM748 EN nominal threshold",en)
    results.append({"acc":acc,"vs":vs,"lm748_en":round(en,3)})

# VIN-pin hazard is separately guarded by the root native KiCad netlist:
# LM74800 can be ON while Q921 disconnects the buck VIN; its ENABLE MUST NOT
# also reach the LMR38020 EN pin because LMR's EN_absmax is VIN+0.3V.
# At 100C MMBT5401 collector leakage spec 50uA (at VCB=-120V)
# plus opto 1uA can develop ~2.4V on 47k: FULL HOT OFF GUARANTEE NOT PROVEN.
worst_hot_off_v=(50e-6+1e-6)*47000
print(json.dumps({
 "status":"DC CORNER CHECK ONLY; transient/hot OFF not qualified",
 "corners":len(results),
 "min_lm748_enable_v":min(x["lm748_en"] for x in results),
 "buck_enable":"directly tied to its own downstream protected VIN",
 "9V_startup":"UNVERIFIED: VS charge pump + R921=10k + D924 / 4.4uF CVS must be tested",
 "off_leakage_risk_v_at_47k":round(worst_hot_off_v,3),
 "blocked":[
   "hot Q915 leakage and fail-OFF needs measured or datasheet-qualified margin",
   "VS startup transient/charge pump including 9V and -40 to 125C",
   "ACC chatter/HOLD transition and USB-only isolation",
   "ISO 16750-2 load-dump/current limit/short circuit"
 ]},indent=2))
