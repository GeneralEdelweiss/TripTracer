#!/usr/bin/env python3
"""KiCad10 native netlist differential: D302 current-limiter prototype.

Run with native hierarchy netlists from copy-substituted module.
Topology PASS means only the enumerated ref/pin nets changed. No HV approval.
"""
import json
import sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets
ROOT=Path("hardware/modules/TripPower_5V2A")
PROTO=ROOT/"01_Protection_LM74930_Q301SHORT_CURRENTLIMIT_PROTOTYPE.kicad_sch"

def nodes(nets):
    return {(r,p):n for n,pairs in nets.items() for r,p in pairs}

def verify(reference,alternate,sch):
    a=nodes(parse_native_nets(reference))
    b=nodes(parse_native_nets(alternate))
    expected={
      ("D302","1"):("VS_CLAMP","VS_BOOST_IN"),
      ("Q307","1"):(None,"VS_CLAMP"),
      ("Q307","2"):(None,"VS_BOOST_IN"),
      ("Q307","3"):(None,"VS_BOOST_RS"),
      ("R342","1"):(None,"VS_BOOST_RS"),
      ("R342","2"):(None,"VS_CLAMP")
    }
    delta={k:(a.get(k),b.get(k)) for k in set(a)|set(b) if a.get(k)!=b.get(k)}
    assert delta==expected,f"native netlist mutation mismatch: {delta} expected {expected}"
    for k,v in {("D302","2"):"SOURCE_A",("Q301","2"):"VIN_FUSED",("Q301","3"):"SOURCE_A",
                ("D301","1"):"VS_CLAMP",("D306","1"):"VS_CLAMP",
                ("U301","2"):"SOURCE_A",("U301","22"):"VS_CLAMP",
                ("U302","1"):"VS_CLAMP"}.items():
        assert b.get(k)==v,f"existing component {k} moved: {b.get(k)} expected {v}"
    assert '(property "Reference" "Q307"' in sch and "BSP135H6327XTSA1" in sch
    assert '(property "Reference" "R342"' in sch and "RC1206FR-071K5L" in sch
    assert '(property "Footprint" "Package_TO_SOT_SMD:SOT-223-3_TabPin2"' in sch
    return {"native_10_pin_delta_pass":True, "changed_nodes":{f"{k[0]}.{k[1]}":list(v) for k,v in delta.items()},
            "Q301_DS_SHORT_EXPOSES_U301_A_AT_200V":True,
            "D302_backfeed_has_current_limiting_branch":True,
            "FET_Q307_current_hot_SOA_qualified":False,"full_safety_qualified":False}

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: checker.py D306_REF.net Q307_PROTOTYPE.net")
    result=verify(Path(sys.argv[1]).read_text(),Path(sys.argv[2]).read_text(),PROTO.read_text())
    print(json.dumps(result,indent=2))
