#!/usr/bin/env python3
"""Check placed PCB power IC pin nets. Does not prove routed PCB or automotive readiness."""
import json
import re
from pathlib import Path
base=Path(__file__).resolve().parents[1]/"hardware"/"kicad"
pcb=(base/"TripTracer_V1.kicad_pcb").read_text(encoding="utf-8")
sch=(base/"02_5V_Buck.kicad_sch").read_text(encoding="utf-8")
def block(text,at):
    depth=0
    quoted=False
    escaped=False
    for idx in range(at,len(text)):
        c=text[idx]
        if quoted:
            if escaped: escaped=False
            elif c=="\\": escaped=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c=='(': depth+=1
        elif c==')':
            depth-=1
            if depth==0:return text[at:idx+1]
    raise AssertionError("Malformed s-expression")
def foot(ref):
    idx=pcb.index('(property "Reference" "'+ref+'"')
    return block(pcb,pcb.rfind("(footprint ",0,idx))
def pads(fp):
    result={}
    for m in re.finditer(r'\(pad "(\d+)" smd ',fp):
        piece=block(fp,m.start())
        nm=re.search(r'\(net "([^"]+)"\)',piece)
        assert m.group(1) not in result
        result[m.group(1)]=nm.group(1) if nm else None
    return result
u=foot("U101")
l=foot("L101")
expect={"1":"GND","2":"HV_PROTECTED_AFTER_EFUSE","3":"HV_PROTECTED_AFTER_EFUSE","4":"RT_400KHZ",
        "5":"FB_5V","6":None,"7":"BOOT_38020","8":"SW_38020","9":"GND"}
assert '(footprint "Tripmaster:TI_LMR38020Q1_DDA_EP"' in u
assert '(property "Value" "LMR38020SQDDARQ1"' in u
assert '(property "Footprint" "Tripmaster:TI_LMR38020Q1_DDA_EP"' in sch
assert pads(u)==expect,f"Physical IC pin-to-net mismatch {pads(u)}"
assert pads(l) == {"1":"SW_38020","2":"V5_BUCK_RAW"}
assert '15uH FCH0650-150M Isat5.5A' in sch
assert '(footprint "Tripmaster:L_FANGCHENG_FCH0650_150M"' in l

for ref, expected in {
    "C101":{"1":"HV_PROTECTED_AFTER_EFUSE","2":"GND"},
    "C102":{"1":"BOOT_38020","2":"SW_38020"},
    "C104":{"1":"V5_BUCK_RAW","2":"GND"},
    "C105":{"1":"V5_BUCK_RAW","2":"GND"},
    "C106":{"1":"V5_BUCK_RAW","2":"GND"},
    "C107":{"1":"HV_PROTECTED_AFTER_EFUSE","2":"GND"},
    "C108":{"1":"HV_PROTECTED_AFTER_EFUSE","2":"GND"},
    "R101":{"1":"V5_BUCK_RAW","2":"FB_5V"},
    "R102":{"1":"FB_5V","2":"GND"},
    "R103":{"1":"RT_400KHZ","2":"GND"}
}.items():
    actual = pads(foot(ref))
    assert actual == expected, f"{ref}: PCB pad nets {actual}, want {expected}"
assert '(property "Reference" "C103"' not in pcb, "Retired 1uF VCC capacitor still on PCB"
assert '(property "Reference" "C108"' in sch
land = (base/"Tripmaster.pretty"/"L_FANGCHENG_FCH0650_150M.kicad_mod").read_text(encoding="utf-8")
assert "NOT VERIFIED" in land, "Prototype FCH land-pattern misleadingly released"

print(json.dumps({"pass":True,"pads":pads(u),"connected_inductor_pads":pads(l),
 "blocked":"FCH pad geometry unverified with manufacturer drawing; PCB unrouted and NOT released",
 "fabrication_release":False,"vehicle_release":False},indent=2))
