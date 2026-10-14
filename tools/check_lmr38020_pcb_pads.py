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
expect={"1":"GND","2":"BUCK_ENABLE","3":"HV_PROTECTED_AFTER_EFUSE","4":"RT_400KHZ",
        "5":"FB_5V","6":None,"7":"BOOT_38020","8":"SW_38020","9":"GND"}
assert '(footprint "Tripmaster:TI_LMR38020Q1_DDA_EP"' in u
assert '(property "Value" "LMR38020SQDDARQ1"' in u
assert '(property "Footprint" "Tripmaster:TI_LMR38020Q1_DDA_EP"' in sch
assert pads(u)==expect,f"Physical IC pin-to-net mismatch {pads(u)}"
assert pads(l) == {"1":"SW_38020","2":"V5_BUCK_RAW"}
assert '15uH FCH0650-150M Isat5.5A PROVISIONAL' in sch
assert '(footprint "Tripmaster:L_Bourns_SRP6030VA_100M"' in l
print(json.dumps({"pass":True,"pads":pads(u),"connected_inductor_pads":pads(l),
 "blocked":"L101 geometric land pattern is for 10uH Bourns, schematic selects 15uH FCH",
 "fabrication_release":False,"vehicle_release":False},indent=2))
