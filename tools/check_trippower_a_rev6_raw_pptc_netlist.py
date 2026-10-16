#!/usr/bin/env python3
"""Only optional resettable 72V PPTC on RAW branch; pin-exact KiCad differential."""
import json,sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets
def pins(s):
    return {(r,p):n for n,parts in parse_native_nets(s).items()
            for r,p in parts if not n.startswith("unconnected-") and not r.startswith("#")}
def verify(a,b):
    p,q=pins(a),pins(b)
    delta={k:(p.get(k),q.get(k)) for k in p.keys()|q.keys() if p.get(k)!=q.get(k)}
    expected={
       ("TP202","1"):("VIN_PROTECTED_UNFUSED","RAW_AUX_AFTER_PPTC_0P5A"),
       ("F201","1"):(None,"VIN_PROTECTED_UNFUSED"),
       ("F201","2"):(None,"RAW_AUX_AFTER_PPTC_0P5A"),
    }
    assert delta==expected, json.dumps(delta,indent=2)
    count=lambda x:len({r for r,pin in x if r[0] in "UQRLCF" and any(ch.isdigit() for ch in r)})
    assert count(p)==25,(count(p),sorted(set(r for r,n in p)))
    assert count(q)==26,(count(q),sorted(set(r for r,n in q)))
    return {"PPTC_ONLY_RAW_BRANCH_NATIVE_NETLIST_VALID":True,
      "raw_branch_after_PPTC_node":"RAW_AUX_AFTER_PPTC_0P5A",
      "shared_main5V_buck_fed_before_PPTC":True,
      "adds_only_one_populated_2920_pptc":True,
      "neither_fuse_holder_nor_one_shot_fuse":True,
      "Bourns_MF_LSMF075_72X_hold_A_60C":0.5,
      "Bourns_MF_LSMF075_72X_hold_A_70C":0.44,
      "hot_fault_time_copper_and_20A_fault_rating_verified":False,
      "RAW_0p5A_at70C_guaranteed":False,
      "release":False}
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: ... baseline.net pptc.net")
    print(json.dumps(verify(*[Path(x).read_text() for x in sys.argv[1:]]),indent=2))
