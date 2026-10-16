#!/usr/bin/env python3
"""Pin-exact native KiCad10 comparison of legacy 25 vs factory-OVP 23 circuit."""
import json,sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets

def pinmap(s):
    return {(ref,pin):net for net,items in parse_native_nets(s).items()
            for ref,pin in items if not net.startswith("unconnected-") and not ref.startswith("#")}

def compare(before,after):
    a,b=pinmap(before),pinmap(after)
    differences={k:(a.get(k),b.get(k)) for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
    expected={
       ("U201","8"):("OVP_SENSE","GND"),
       ("U201","12"):(None,"GND"),
       ("U201","16"):(None,"GND"),
       ("R202","1"):("UVLO_SENSE",None),
       ("R202","2"):("OVP_SENSE",None),
       ("R203","1"):("OVP_SENSE",None),
       ("R203","2"):("GND",None),
    }
    assert differences==expected, json.dumps({"observed":{str(k):v for k,v in differences.items()},
                                              "expected":{str(k):v for k,v in expected.items()}},indent=2)
    partcount=lambda p:len({ref for ref,pin in p if ref[0] in "UQRLCD" and any(z.isdigit() for z in ref)})
    assert partcount(a)==25
    assert partcount(b)==23
    assert a[("U201","7")]==b[("U201","7")]=="UVLO_SENSE"
    assert a[("U201","6")]==b[("U201","6")]=="VIN_FUSED"
    assert all(a[k]==b[k] for k in [("Q201","1"),("Q201","2"),("Q201","3"),
        ("Q202","1"),("Q202","2"),("Q202","3"),("U101","2"),("U101","3"),
        ("Q501","1"),("Q501","2"),("Q501","3"),("TP501","1"),("TP502","1")])
    return {"native_differential_exactly_seven_changed_pin_connections":True,
            "baseline_25_factory_23_fitted":True,
            "reverse_FET_Q201_Q202_untouched":True,
            "buck_and_PGOOD_untouched":True,
            "OVP8_and_MODE12_and_PGTH16_grounded":True,
            "only_two_fitted_UV_OV_R_removed":True,
            "85C_temp_and_RAW_remain_unqualified":True,
            "factory_58V_pulse_including_ringing_pass":False,
            "fabrication_release":False}
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("Usage: factory_delta.py old25.net new23.net")
    print(json.dumps(compare(*(Path(p).read_text(encoding="utf-8") for p in sys.argv[1:])),indent=2))
