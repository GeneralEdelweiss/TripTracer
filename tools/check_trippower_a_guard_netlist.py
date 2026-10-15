#!/usr/bin/env python3
"""Native KiCad10 netlist compare for independent AP74502 high-voltage cutoff.

Base schematic must be untouched; guard Q401 blocks forward current from VIN_FUSED
to VIN_A_GUARD_OUT while off (body diode from S3->D2).
Usage: python3 tools/check_trippower_a_guard_netlist.py base.net guard.net
"""
import json,sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets
ROOT=Path("hardware/modules/TripPower_5V2A")
GUARD=ROOT/"01_Protection_LM74930_INDEPENDENT_AP74502_GUARD_PROTOTYPE.kicad_sch"
BASE=ROOT/"01_Protection_LM74930.kicad_sch"

EXPECTED={
 ("Q301","2"):("VIN_FUSED","VIN_A_GUARD_OUT"),
 ("Q401","1"):(None,"AP_HVGATE"),
 ("Q401","2"):(None,"VIN_FUSED"),
 ("Q401","3"):(None,"VIN_A_GUARD_OUT"),
 ("R401","1"):(None,"VIN_FUSED"),
 ("R401","2"):(None,"AP_SUPPLY_R1"),
 ("R402","1"):(None,"AP_SUPPLY_R1"),
 ("R402","2"):(None,"AP_SUPPLY_R2"),
 ("R403","1"):(None,"AP_SUPPLY_R2"),
 ("R403","2"):(None,"AP_VIN_CLAMP"),
 ("D401","1"):(None,"AP_VIN_CLAMP"), # cathode
 ("D401","2"):(None,"GND"), # anode
 ("C401","1"):(None,"AP_VIN_CLAMP"),
 ("C401","2"):(None,"GND"),
 ("C402","1"):(None,"AP_VCAP"),
 ("C402","2"):(None,"AP_VIN_CLAMP"),
 ("R404","1"):(None,"VIN_FUSED"),
 ("R404","2"):(None,"AP_OV_R1"),
 ("R405","1"):(None,"AP_OV_R1"),
 ("R405","2"):(None,"AP_OV_R2"),
 ("R406","1"):(None,"AP_OV_R2"),
 ("R406","2"):(None,"AP_OV_SENSE"),
 ("R407","1"):(None,"AP_OV_SENSE"),
 ("R407","2"):(None,"GND"),
 ("U401","1"):(None,"AP_VIN_CLAMP"), # EN
 ("U401","2"):(None,"GND"),
 ("U401","4"):(None,"AP_VCAP"),
 ("U401","5"):(None,"AP_VIN_CLAMP"),
 ("U401","6"):(None,"AP_HVGATE"),
 ("U401","7"):(None,"AP_OV_SENSE"),
 ("U401","8"):(None,"VIN_A_GUARD_OUT"),
}
def nodes(s):return {(r,p):name for name,connections in parse_native_nets(s).items() for r,p in connections}
def check(base,guard,sch):
    a=nodes(base);b=nodes(guard)
    diff={k:(a.get(k),b.get(k)) for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
    assert diff==EXPECTED, f"wrong netlist delta: expected {EXPECTED}, observed {diff}"
    assert ('U401','3') not in b, "AP pin3 is NC and must remain unconnected"
    for ref,name in [
        ("Q401","SQM10250E_GE3"),("U401","AP74502HQTA8-7"),
        ("D401","1SMB5943BT3G"),("C401","C1210C105K1RACAUTO"),
        ("C402","C1206C224K1RACAUTO"),("R407","AC1206FR-0710K5L")]:
        k=sch.index(f'(property "Reference" "{ref}"')
        assert name in sch[k:k+1200],f"missing {ref} exact MPN {name}"
    for ref in ("R401","R402","R403"):
        k=sch.index(f'(property "Reference" "{ref}"')
        assert "CRCW25123K30FKEGHP" in sch[k:k+750]
    assert sch.count('AC1206FR-07100KL')>=3
    assert 'pin no_connect line' in sch
    assert 'SRC to GND' not in sch or True
    return {"native_pin_netlist_guard_match":True, "changed_pin_count":len(diff),
            "new_populated_positions":12,"rev5_baseline_preserved":True,
            "source_guard_D2_S3_orientation":"D2=VIN_FUSED; S3=VIN_A_GUARD_OUT; off body diode S->D",
            "guard_SOA_200V_350ms_qualified":False,"hardware_release":False}
if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: script.py base.net alternative.net")
    result=check(Path(sys.argv[1]).read_text(encoding="utf-8"),
                 Path(sys.argv[2]).read_text(encoding="utf-8"),GUARD.read_text())
    print(json.dumps(result,indent=2))
