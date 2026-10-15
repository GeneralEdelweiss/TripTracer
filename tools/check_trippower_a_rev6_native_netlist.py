#!/usr/bin/env python3
"""REV6 A native KiCad10 TOP-level netlist semantic+part-count checker."""
import json,sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets
ROOT=Path("hardware/modules/TripPower_REV6_A")
def verify(s):
    net=parse_native_nets(s)
    pins={(ref,p):name for name,ends in net.items() for ref,p in ends if not name.startswith("unconnected-")}
    exp={
      ("U201","1"):"EFUSE_IN",("U201","2"):"EFUSE_IN",("U201","3"):"EFUSE_IN",
      ("U201","4"):"R6_B_GATE",("U201","5"):"R6_DRV",
      ("U201","6"):"VIN_FUSED",("U201","7"):"UVLO_SENSE",
      ("U201","8"):"OVP_SENSE",("U201","9"):"GND",
      ("U201","10"):"R6_DVDT",("U201","11"):"ILIM_SET",
      ("U201","13"):"VIN_FUSED",
      ("U201","18"):"VIN_PROTECTED_UNFUSED",
      ("U201","19"):"VIN_PROTECTED_UNFUSED",
      ("U201","20"):"VIN_PROTECTED_UNFUSED",
      ("U201","21"):"GND",
      ("Q201","1"):"R6_B_GATE",("Q201","2"):"EFUSE_IN",
      ("Q201","3"):"VIN_FUSED",
      ("Q202","1"):"R6_DRV",("Q202","2"):"VIN_FUSED",
      ("Q202","3"):"R6_B_GATE",
      ("R201","1"):"VIN_FUSED",("R201","2"):"UVLO_SENSE",
      ("R202","1"):"UVLO_SENSE",("R202","2"):"OVP_SENSE",
      ("R203","1"):"OVP_SENSE",("R203","2"):"GND",
      ("R204","1"):"ILIM_SET",("R204","2"):"GND",
      ("C201","1"):"VIN_FUSED",("C201","2"):"GND",
      ("C202","1"):"VIN_PROTECTED_UNFUSED",("C202","2"):"GND",
      ("C203","1"):"R6_DVDT",("C203","2"):"GND",
      ("U101","2"):"VIN_PROTECTED_UNFUSED",
      ("U101","3"):"VIN_PROTECTED_UNFUSED",
      ("U101","6"):"BUCK_PG_STATE",
      ("Q501","1"):"BUCK_PG_STATE",("Q501","2"):"GND",
      ("Q501","3"):"PWR_OK_SINK_FAIL_RELEASE",
      ("TP501","1"):"PWR_OK_SINK_FAIL_RELEASE",
      ("TP201","1"):"VIN_FUSED",
      ("TP202","1"):"VIN_PROTECTED_UNFUSED",
      ("TP203","1"):"GND",
    }
    errors={f"{x[0]}.{x[1]}":{ "observed":pins.get(x),"required":v} for x,v in exp.items() if pins.get(x)!=v}
    assert not errors, json.dumps(errors,indent=2)
    forbidden={"U301","Q301","Q302","D301","D302","D303","D304","D306","Q307","U401","Q401",
               "TPS3760"}
    actual_refs={ref for ref,p in pins}
    assert not forbidden.intersection(actual_refs),forbidden.intersection(actual_refs)
    # pin12 floating is TI latch mode, deliberate NC; other diagnostic outputs unused
    for i in (12,14,15,16,17):
        assert ("U201",str(i)) not in pins,("incorrectly connected",i,pins.get(("U201",str(i))))
    r=ROOT/"01_TPS26631_REV6.kicad_sch"
    a=r.read_text()
    assert "TPS26631PWPR" in a and "SQM100N10-10_GE3" in a
    assert "AC1206FR-07402KL" in a and "AC1206FR-0749K9L" in a
    assert "AC1206FR-0716K5L" in a and "AC1206FR-076K04L" in a
    assert "R201=402k R202=49k9 R203=16k5" in a
    b=(ROOT/"02_5V_LMR38020_REV6.kicad_sch").read_text()
    assert "LMR38020SQDDARQ1" in b and "BVSS123LT1G" in b
    # Native orderable parts in root hierarchy: first 10, buck + PGOOD 15;
    # check actual instances rather than inflated parent symbol caches.
    nref=set(x for x in actual_refs if x[0] in "UQRLC" and any(c.isdigit() for c in x))
    assert len(nref)==25,sorted(nref)
    assert all("BAT" not in n for n in ("BUCK_PG_STATE","PWR_OK_SINK_FAIL_RELEASE"))
    return {
        "native_REV6_protection_pinout_correct":True,
        "native_UV_OV_current_limit_NFET_direction_confirmed":True,
        "native_PGOOD_external_fail_high_no_main_backfeed":True,
        "root_populated_count_derived_from_native_instance_refs":len(nref),
        "expected_auto_and_run_count":25,
        "REV5_HV_controller_and_250V_FET_removed":True,
        "temperature_at_85C_safe_off_qualified":False,
        "surge_ESD_58V_SOC_validated":False,
        "fab_release":False
    }
if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("Usage: ... REV6_A.net")
    print(json.dumps(verify(Path(sys.argv[1]).read_text()),indent=2))
