#!/usr/bin/env python3
"""Proof against KiCad 10 *exported* TripPower netlist (not labels alone).

Required: kicad-cli sch export netlist -o /tmp/TripPower_5V2A.net \
 hardware/modules/TripPower_5V2A/TripPower_5V2A.kicad_sch
          python3 tools/check_trippower_a_netlist.py /tmp/TripPower_5V2A.net
"""
import json
import re
import sys
from pathlib import Path

def parse_native_nets(content):
    # KiCad S-expr netlist, same compatible form used by existing REV5 checker.
    if "(nets" not in content:
        raise AssertionError("missing actual KiCad nets; labels alone are insufficient")
    nets={}
    for chunk in content.split("\n\t(nets",1)[1].split("\n\t\t(net")[1:]:
        m=re.search(r'\(name "([^"]+)"\)',chunk)
        if not m:continue
        net=m.group(1).split("/")[-1]
        nets.setdefault(net,set()).update(
            re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)',chunk))
    if not nets:
        raise AssertionError("no nodes read from native KiCad netlist")
    return nets

EXPECTED={
    "Q301": {"1":"HGATE","2":"VIN_FUSED","3":"SOURCE_A"},
    "D301": {"1":"VS_CLAMP","2":"GND"},  # K1/A2
    "D302": {"1":"VS_CLAMP","2":"SOURCE_A"},  # K1/A2
    "D303": {"1":"VIN_FUSED","2":"TVS_STACK"},  # K1/A2, reverse in positive dump
    "D304": {"1":"TVS_STACK","2":"GND"},  # bidirectional SMBJ33CA
    "R313": {"1":"VIN_FUSED","2":"VS_SERIES_A"},
    "R314": {"1":"VS_SERIES_A","2":"VS_SERIES_B"},
    "R315": {"1":"VS_SERIES_B","2":"VS_CLAMP"},
    "C302": {"1":"VS_CLAMP","2":"GND"},
    "C308": {"1":"VS_CLAMP","2":"GND"},
    "C312": {"1":"VS_CLAMP","2":"GND"},
    "U301": {"7":"VS_CLAMP","14":"HGATE","22":"VS_CLAMP",
             "19":"VIN_PROTECTED_UNFUSED"},
}
def verify(nets,sch):
    for ref,pins in EXPECTED.items():
        for pin,want in pins.items():
            actual=[name for name, nodes in nets.items() if (ref,pin) in nodes]
            assert actual==[want],f"{ref}.{pin}: expected {want}, got {actual}"
    # Confirm source symbol mapping and real fitted MPN/diode types.
    assert 'Cathode pad1, anode pad2' in sch, "diode K/A pin definition changed"
    for ref,mpn in (("Q301","SQM10250E_GE3"),("D301","1SMB5943BT3G"),
                    ("D302","BAV21WQ-7-F"),("D303","SMBJ150A-13-F"),
                    ("D304","SMBJ33CA-13-F")):
        assert f'(property "Reference" "{ref}"' in sch, f"missing {ref}"
        assert mpn in sch, f"missing {mpn}"
    for ref in ("R313","R314","R315"):
        assert f'(property "Reference" "{ref}"' in sch
    assert sch.count('(property "MPN" "CRCW25123K30FKEGHP"')==3
    assert nets["VIN_FUSED"].isdisjoint(nets["VS_CLAMP"])
    assert nets["VIN_FUSED"].isdisjoint(nets["TVS_STACK"])
    assert nets["SOURCE_A"].isdisjoint(nets["VS_CLAMP"])
    return {"native_netlist_topology_pass":True,"verified_pins":sum(map(len,EXPECTED.values())),
            "diode_orientation":"D301 K=VS/A=GND; D302 K=VS/A=SOURCE_A; "
                                "D303 K=VIN/A=TVS_STACK; D304 bidirectional",
            "hardware_surge_safety_qualified":False}

def main():
    if len(sys.argv)!=2:raise SystemExit("Usage: check_trippower_a_netlist.py PATH_TO_NATIVE_NETLIST")
    nets=parse_native_nets(Path(sys.argv[1]).read_text(encoding="utf-8"))
    sch=Path("hardware/modules/TripPower_5V2A/01_Protection_LM74930.kicad_sch").read_text(encoding="utf-8")
    print(json.dumps(verify(nets,sch),indent=2))
if __name__=="__main__":main()
