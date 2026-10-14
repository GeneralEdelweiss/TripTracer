#!/usr/bin/env python3
"""Validate the *standalone KiCad 10 exported netlist* of TripPower_5V2A.
This does not certify surge, thermal, FET SOA, solderability or automotive use.
"""
from pathlib import Path
import re,sys,json
content=Path(sys.argv[1]).read_text(encoding="utf-8")
assert "(nets" in content, "missing KiCad native schematic nets"
nets={}
for chunk in re.split(r'\n\s*\(net ',content.split("(nets",1)[1])[1:]:
    m=re.search(r'\(name "([^"]+)"\)',chunk)
    if not m: continue
    key=m.group(1).split("/")[-1]
    nets.setdefault(key,set()).update(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)',chunk))
print("DIAG native report start",repr(content[:250]))
print("DIAG KiCad net names",sorted(nets.keys())[:80])
print("DIAG U301 refs",[(net,sorted([node for node in nodes if node[0]=="U301"])) for net,nodes in nets.items() if any(node[0]=="U301" for node in nodes)][:32])
mapping={
 "U301": {"1":"Q2_GATE","2":"SOURCE_A","4":"UV_DIV","5":"OV_DIV","6":"CTRL_EN",
  "7":"VS_CLAMP","9":"TMR_NODE","10":"IMON_MON","11":"ILIM",
  "12":"FAULT_OC_N","13":"GND","14":"HGATE","15":"SOURCE_A","16":"GND",
  "18":"ISCP","19":"VIN_PROTECTED_MAIN","20":"CS_PLUS","22":"VS_CLAMP",
  "23":"CAP_PUMP","24":"C_NODE"},
 "Q301":{"1":"Q1_GATE","2":"VIN_FUSED","3":"SOURCE_A"},
 "Q302":{"1":"SOURCE_A","2":"SOURCE_A","3":"SOURCE_A","4":"Q2_GATE","5":"C_NODE"},
 "R301":{"1":"C_NODE","2":"VIN_PROTECTED_MAIN"},
 "R302":{"1":"C_NODE","2":"CS_PLUS"},
 "R303":{"1":"C_NODE","2":"ISCP"},
 "F302":{"1":"VIN_PROTECTED_MAIN","2":"VIN_PROTECTED"},
 "J301":{"1":"VIN_FUSED","2":"RUN_CMD","3":"GND"},
 "J302":{"1":"VIN_PROTECTED","2":"5V_OUT","3":"GND"},
 "U101":{"2":"VIN_PROTECTED_MAIN","3":"VIN_PROTECTED_MAIN"}
}
for ref,pins in mapping.items():
  for pin,desired in pins.items():
    found=[k for k,v in nets.items() if (ref,pin) in v]
    assert found==[desired],f"{ref}.{pin}: expected {desired}, found {found}"
for k in ("VIN_FUSED","VIN_PROTECTED_MAIN","VIN_PROTECTED","5V_OUT"):
    assert k in nets, f"missing power domain {k}"
for a,b in [("VIN_FUSED","VIN_PROTECTED_MAIN"),("VIN_PROTECTED_MAIN","VIN_PROTECTED"),
            ("VIN_PROTECTED","5V_OUT"),("VIN_FUSED","5V_OUT")]:
    assert nets[a].isdisjoint(nets[b]),f"shorted or aliased {a} {b}"
assert ("U301","25") not in nets.get("GND",set()),"RTN thermal pad must FLOAT"
assert ("U301","3") not in nets.get("VIN_FUSED",set()),"SW must NC in direct UV divider prototype"
# All power branches have a real device in their path; no refactoring to
# a global-label-only shortcut that defeats short-circuit protection.
assert ("Q302","5") in nets["C_NODE"] and ("R301","1") in nets["C_NODE"]
assert ("U101","3") in nets["VIN_PROTECTED_MAIN"]
assert ("J302","1") not in nets["VIN_PROTECTED_MAIN"]
assert ("F302","2") in nets["VIN_PROTECTED"]
print(json.dumps({"pass":True,"native_export":sys.argv[1],
"nodes_checked":sum(len(x) for x in mapping.values()),
"message":"Two external output paths and 24+RTN LM74930 wiring; NOT safety/PCB approval"},indent=2))
