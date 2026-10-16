#!/usr/bin/env python3
"""Weg A isolated thermal switch only: native baseline-to-67F080 netlist diff."""
import json,sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets
def pins(s):
    return {(r,p):n for n,parts in parse_native_nets(s).items()
            for r,p in parts if not n.startswith("unconnected-") and not r.startswith("#")}
def check(original,thermal):
    a,b=pins(original),pins(thermal)
    d={k:(a.get(k),b.get(k)) for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
    expected={
      ("U201","13"):(None,"THERMAL_SHDN"),
      ("T201","1"):(None,"THERMAL_SHDN"),
      ("T201","2"):(None,"GND"),
    }
    assert d==expected, f"expected only 3 thermal pins: {d}"
    assert len({r for r,p in a if r[0] in "UQRLC" and any(c.isdigit() for c in r)})==25
    assert len({r for r,p in b if r[0] in "UQRLCT" and any(c.isdigit() for c in r)})==26
    return {"native_thermal_delta_only_T201_1_2_and_SHDN13":True,
       "baseline_parts":25,"research_parts":26,
       "Sensata_67F080_local_closure_temp_c_range":[75,85],
       "contact_manufacturer_test_low_level_mA_at5v":10,
       "TPS26631_SHDN_pullup_v_ohm":[2.7,1000000],
       "nominal_open_contact_current_microamp":2.7,
       "contact_2p7uA_low_wetting_manufacturer_qualified":False,
       "ambient_vs_local_sensor_85c_verified":False,
       "production_ready":False}
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("Usage: script original.net thermal.net")
    print(json.dumps(check(*[Path(p).read_text() for p in sys.argv[1:]]),indent=2))
