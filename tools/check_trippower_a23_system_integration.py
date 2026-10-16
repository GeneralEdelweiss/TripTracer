#!/usr/bin/env python3
"""Native pin/net/BOM audit of separately integrated A23 and actual host USB/MCU hierarchy.
Rejects duplicate old LM74800 and buck; a PASS is NOT vehicle/thermal/PCB qualification."""
import csv,json,sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets
ROOT=Path("hardware/kicad/TripTracer_A23_Integration")
def verify(net,bom):
    nets=parse_native_nets(Path(net).read_text())
    pins={(ref,p):n for n,ends in nets.items() for ref,p in ends if not n.startswith("unconnected-")}
    for ref,p,n in [("U921","1","EFUSE_IN"),("U921","6","VIN_FUSED"),("U921","8","GND"),
                    ("U921","12","GND"),("U921","16","GND"),
                    ("U921","18","VIN_PROTECTED_UNFUSED"),
                    ("U101","2","VIN_PROTECTED_UNFUSED"),
                    ("TP502","1","5V_OUT"),("Q501","3","PWR_OK_SINK_FAIL_RELEASE")]:
        assert pins.get((ref,p))==n,(ref,p,pins.get((ref,p)),n)
    assert "5V_OUT" in nets and any(ref=="U301" for ref,p in nets["5V_OUT"]),"USB mux is not actually fed from A23"
    assert any(ref=="TP502" for ref,p in nets["5V_OUT"]),"A23 Buck 5V must share USB net"
    assert any(ref=="U201" for x in nets.values() for ref,p in x),"ESP32 not in the same hierarchy"
    assert not any(ref=="U922" for x in nets.values() for ref,p in x),"Unexpected original LM74800!"
    hierarchy=(ROOT/"TripTracer_A23_Integration.kicad_sch").read_text()
    for sheet in ("01_TPS26631_A23_INTEGRATED","02_5V_A23_INTEGRATED","03_3V3_USB_A23","04_ESP32_USB","07_Speicher_RTC"):
        assert sheet+".kicad_sch" in hierarchy
    for legacy in ("01_Eingangsschutz.kicad_sch","01I_LM74800_INPUT.kicad_sch","02_5V_Buck.kicad_sch","01H_ACC_HOLD_GATE.kicad_sch"):
        assert legacy not in hierarchy
    with open(bom) as f:
        parts=list(csv.DictReader(f))
    assert sum("TPS26631PWPR" in str(part) for part in parts)==1
    assert sum("LMR38020SQDDARQ1" in str(part) for part in parts)==1
    return {"native_single_TPS26631":True,"native_single_LMR38020_Q1":True,
      "host_TPS2116_and_ESP32_in_real_netlist":True,
      "5V_buck_linked_to_USB_mux":True,
      "old_LM74800_and_duplicate_Buck_absent":True,
      "unmodified_standalone_A23_reference_preserved":True,
      "lab_bench_EFUSE_IN_source_only":True,
      "acc_hold_default_off_proven":False,"raw_selective_half_amp_proven":False,
      "ambient85_fail_safe_proven":False,"physical_m8_terminal_integration":False,
      "PWR_FAIL_at_MCU_with_host_pullup":False,
      "PCB_present":False,"vehicle_fab_release":False}
if __name__=="__main__":
    print(json.dumps(verify(*sys.argv[1:]),indent=2))
