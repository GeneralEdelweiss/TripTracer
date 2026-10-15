#!/usr/bin/env python3
"""Validate the *standalone KiCad 10 exported netlist* of TripPower_5V2A.
This does not certify surge, thermal, FET SOA, solderability or automotive use.
"""
from pathlib import Path
import re,sys,json
content=Path(sys.argv[1]).read_text(encoding="utf-8")
assert "(nets" in content, "missing KiCad native schematic nets"
nets={}
for chunk in content.split("\n\t(nets",1)[1].split("\n\t\t(net")[1:]:
    m=re.search(r'\(name "([^"]+)"\)',chunk)
    if not m: continue
    key=m.group(1).split("/")[-1]
    nets.setdefault(key,set()).update(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)',chunk))
mapping={
 "U301": {"1":"Q2_GATE","2":"SOURCE_A","4":"UV_DIV","5":"OV_DIV","6":"CTRL_EN",
  "7":"VS_CLAMP","9":"TMR_NODE","10":"IMON_MON","11":"ILIM",
  "12":"FAULT_OC_N","13":"GND","14":"HGATE","15":"SOURCE_A","16":"GND",
  "18":"ISCP","19":"VIN_PROTECTED_UNFUSED","20":"CS_PLUS","22":"VS_CLAMP",
  "23":"CAP_PUMP","24":"C_NODE"},
 "Q301":{"1":"HGATE","2":"VIN_FUSED","3":"SOURCE_A"},
 "R320":{"1":"HGATE","2":"DV_DT_RC_NODE"},
 "C307":{"1":"DV_DT_RC_NODE","2":"GND"},
 "C303":{"1":"CAP_PUMP","2":"VS_CLAMP"},
 "Q302":{"1":"SOURCE_A","2":"SOURCE_A","3":"SOURCE_A","4":"Q2_GATE","5":"C_NODE"},
 "R301":{"1":"C_NODE","2":"VIN_PROTECTED_UNFUSED"},
 "R302":{"1":"C_NODE","2":"CS_PLUS"},
 "R303":{"1":"C_NODE","2":"ISCP"},
 "J301":{"1":"VIN_FUSED","2":"RUN_CMD","3":"GND"},
 "J302":{"1":"VIN_PROTECTED_UNFUSED","2":"5V_OUT","3":"GND"},
 "R317":{"1":"RUN_CMD","2":"RUN_ISOLATED_AFTER_R"},
 "D305":{"1":"CTRL_EN","2":"RUN_ISOLATED_AFTER_R"},
 "U101":{"2":"VIN_PROTECTED_UNFUSED","3":"VIN_PROTECTED_UNFUSED"}
}
for ref,pins in mapping.items():
  for pin,desired in pins.items():
    found=[k for k,v in nets.items() if (ref,pin) in v]
    assert found==[desired],f"{ref}.{pin}: expected {desired}, found {found}"
for k in ("VIN_FUSED","VIN_PROTECTED_UNFUSED","VIN_PROTECTED_UNFUSED","5V_OUT"):
    assert k in nets, f"missing power domain {k}"
for a,b in [("VIN_FUSED","VIN_PROTECTED_UNFUSED"),
            ("VIN_PROTECTED_UNFUSED","5V_OUT"),("VIN_FUSED","5V_OUT")]:
    assert nets[a].isdisjoint(nets[b]),f"shorted or aliased {a} {b}"
assert ("U301","25") not in nets.get("GND",set()),"RTN thermal pad must FLOAT"
assert ("U301","3") not in nets.get("VIN_FUSED",set()),"SW must NC in direct UV divider prototype"
# All power branches have a real device in their path; no refactoring to
# a global-label-only shortcut that defeats the LM74930 shared electronic circuit breaker.
assert ("Q301","1") in nets["HGATE"] and ("U301","14") in nets["HGATE"], "HGATE must drive Q301 gate directly"
assert ("R320","2") in nets["DV_DT_RC_NODE"] and ("C307","1") in nets["DV_DT_RC_NODE"], "Rg/CdVdT must be series branch to GND"
assert ("Q301","1") not in nets["DV_DT_RC_NODE"], "Do not put R320 100ohm in HGATE series gate path"
assert ("Q302","5") in nets["C_NODE"] and ("R301","1") in nets["C_NODE"]
assert ("U101","3") in nets["VIN_PROTECTED_UNFUSED"]
assert ("J302","1") in nets["VIN_PROTECTED_UNFUSED"],"Output is intentionally UNFUSED on module"
assert ("R301","2") in nets["VIN_PROTECTED_UNFUSED"],"Output must remain behind common LM74930 shunt"
assert not any(ref=="F302" for nodes in nets.values() for ref,pin in nodes),"Fuse moved to consuming mainboard, not module"
print(json.dumps({"pass":True,"native_export":sys.argv[1],
"nodes_checked":sum(len(x) for x in mapping.values()),
"message":"Protected but unfused aux output shared with buck behind LM74930 shunt; external fuse ON TRIPTRACER mandatory; NOT safety/PCB approval"},indent=2))
