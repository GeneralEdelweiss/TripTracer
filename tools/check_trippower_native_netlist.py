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
 "C308":{"1":"VS_CLAMP","2":"GND"},
 "C309":{"1":"CTRL_EN","2":"GND"},
 "Q303":{"1":"EN_GATE_DRIVE","2":"CTRL_EN","3":"EN_REQUEST_RAW"},
 "R334":{"1":"VS_CLAMP","2":"EN_GATE_DRIVE"},
 "R335":{"1":"EN_GATE_DRIVE","2":"GND"},
 "D306":{"1":"VS_READY_RESET_OD_PRELIM","2":"EN_GATE_DRIVE"},
 "D307":{"1":"EN_GATE_DRIVE","2":"GND"},
 "D308":{"1":"VS_READY_RESET_OD_PRELIM","2":"CTRL_EN"},
 "U302":{"1":"VS_CLAMP","3":"VS_SENSE","6":"VS_READY_RESET_OD_PRELIM","8":"GND","9":"CTR_READY","13":"GND"},
 "R330":{"1":"VS_CLAMP","2":"VS_SENSE"},
 "R331":{"1":"VS_SENSE","2":"GND"},
 "R332":{"1":"VS_READY_RESET_OD_PRELIM","2":"VS_SENSE"},
 "R333":{"1":"VS_CLAMP","2":"VS_READY_RESET_OD_PRELIM"},
 "C310":{"1":"VS_CLAMP","2":"GND"},
 "C311":{"1":"CTR_READY","2":"GND"},
 "Q302":{"1":"SOURCE_A","2":"SOURCE_A","3":"SOURCE_A","4":"Q2_GATE","5":"C_NODE"},
 "R301":{"1":"C_NODE","2":"VIN_PROTECTED_UNFUSED"},
 "R302":{"1":"C_NODE","2":"CS_PLUS"},
 "R303":{"1":"C_NODE","2":"ISCP"},
 "J301":{"1":"VIN_FUSED","2":"RUN_CMD","3":"GND"},
 "J302":{"1":"VIN_PROTECTED_UNFUSED","2":"5V_OUT","3":"GND"},
 "R316":{"1":"CTRL_EN","2":"GND"},
 "R318":{"1":"VS_CLAMP","2":"AUTO_EN_LINK"},
 "R319":{"1":"AUTO_EN_LINK","2":"EN_REQUEST_RAW"},
 "R317":{"1":"RUN_CMD","2":"RUN_ISOLATED_AFTER_R"},
 "D305":{"1":"EN_REQUEST_RAW","2":"RUN_ISOLATED_AFTER_R"},
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
assert ("C308","1") in nets["VS_CLAMP"] and ("C309","1") in nets["CTRL_EN"], "VS reservoir / EN delay topology required"
assert ("U302","6") in nets["VS_READY_RESET_OD_PRELIM"] and ("U302","6") not in nets["CTRL_EN"], "RESET must not directly link to EN; isolation via D306 and D308"
assert ("Q303","2") in nets["CTRL_EN"] and ("Q303","3") in nets["EN_REQUEST_RAW"], "EN must pass through Q303 source follower only"
assert ("D305","1") in nets["EN_REQUEST_RAW"] and ("R319","2") in nets["EN_REQUEST_RAW"], "both RUN and AUTO must connect before Q303 pass FET"
assert ("R316","1") in nets["CTRL_EN"] and ("D308","2") in nets["CTRL_EN"], "low-EN pull-down and failsafe diode required"
assert ("D306","1") in nets["VS_READY_RESET_OD_PRELIM"] and ("D306","2") in nets["EN_GATE_DRIVE"], "RESET must clamp Q303 gate when low"
assert ("R334","1") in nets["VS_CLAMP"] and ("D307","2") in nets["GND"], "gate reference and 10V zener to GND must remain"
assert ("C309","1") in nets["CTRL_EN"], "C309 DNP footprint left physically not fitted to prevent EN-off latency"
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
