#!/usr/bin/env python3
"""Weg A proof: native KiCad 10 netlist of *alternate* protection sheet.

Usage: python3 tools/check_trippower_a_d301_prototype.py BASE.net PROTOTYPE.net
Neither pass nor ERC qualifies Zener thermals, VS absolute pin voltage or FET SOA.
"""
import json
import re
import sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets, EXPECTED

PART="hardware/modules/TripPower_5V2A/"
ALT=PART+"01_Protection_LM74930_D301_BACKUP_PROTOTYPE.kicad_sch"
BASE=PART+"01_Protection_LM74930.kicad_sch"

def check(base_text, prototype_text, original_sch, alternate_sch):
    original=parse_native_nets(base_text)
    alternate=parse_native_nets(prototype_text)
    assert not any(ref=="D306" for n in original.values() for ref,pin in n), \
        "Original baseline polluted with D306"
    for ref,pins in EXPECTED.items():
        for pin,net in pins.items():
            assert (ref,pin) in original.get(net,set()),f"baseline {ref}.{pin}->{net} changed"
            assert (ref,pin) in alternate.get(net,set()),f"alternate {ref}.{pin}->{net} changed"
    for pin,net in (("1","VS_CLAMP"),("2","GND")):
        actual=[n for n,nodes in alternate.items() if ("D306",pin) in nodes]
        assert actual==[net],f"incorrect D306 {pin} {actual} expected {net}"
    assert 'Cathode pad1, anode pad2' in alternate_sch
    assert '(property "Reference" "D306"' not in original_sch
    pos=alternate_sch.index('(property "Reference" "D306"')
    region=alternate_sch[pos:pos+1100]
    assert '(property "MPN" "ACZRC5370B-G"' in region
    assert '(property "Footprint" "Diode_SMD:D_SMC"' in region
    assert '(property "Value" "ACZRC5370B-G 56V 5W AEC-Q101 BACKUP"' in region
    assert 'ACZRC5370B-G' in prototype_text, "Native export must contain D306 actual MPN/value"
    assert 'D301' in prototype_text
    all_base=set((n,r,p) for n,nodes in original.items() for r,p in nodes)
    all_alt=set((n,r,p) for n,nodes in alternate.items() for r,p in nodes)
    difference=all_alt-all_base
    assert difference=={("VS_CLAMP","D306","1"),("GND","D306","2")},f"unexpected extra nodes {difference}"
    assert not (all_base-all_alt),f"baseline nets unexpectedly missing {all_base-all_alt}"
    return {
      "native_kicad10_netlist_candidate_delta_pass":True,
      "baseline_unchanged":True,
      "sole_added_electrical_component":"D306 ACZRC5370B-G",
      "d306_pins":{"1":"VS_CLAMP (K)","2":"GND (A)"},
      "d306_footprint":"Diode_SMD:D_SMC",
      "additional_auto_run_placements":1,
      "prototype_fabrication_qualified":False
    }

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: ... BASE.net ALTERNATE.net")
    a=Path(BASE).read_text(encoding="utf-8")
    b=Path(ALT).read_text(encoding="utf-8")
    v=check(Path(sys.argv[1]).read_text(encoding="utf-8"),
            Path(sys.argv[2]).read_text(encoding="utf-8"),a,b)
    print(json.dumps(v,indent=2))
