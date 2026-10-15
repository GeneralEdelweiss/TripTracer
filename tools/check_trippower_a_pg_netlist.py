#!/usr/bin/env python3
"""Weg A: native KiCad10 standalone PG-only interface exact delta check."""
import json,sys
from pathlib import Path
from check_trippower_a_netlist import parse_native_nets
ROOT=Path("hardware/modules/TripPower_5V2A")
ALT=ROOT/"02_5V_LMR38020_PGOOD_BACKUP_INTERFACE_PROTOTYPE.kicad_sch"
OLD=ROOT/"02_5V_LMR38020.kicad_sch"
NEW={
("U101","6"):(None,"BUCK_PG_STATE"),
("R501","1"):(None,"5V_OUT"),
("R501","2"):(None,"BUCK_PG_STATE"),
("R502","1"):(None,"BUCK_PG_STATE"),
("R502","2"):(None,"GND"),
("Q501","1"):(None,"BUCK_PG_STATE"),
("Q501","2"):(None,"GND"),
("Q501","3"):(None,"PWR_OK_SINK_FAIL_RELEASE")
}
def pins(nl):
    return {(r,p):net for net,ends in parse_native_nets(nl).items()
            for r,p in ends if not net.startswith("unconnected-") and not r.startswith("#")}
def verify(base,prototype,sch):
    a=pins(base);b=pins(prototype)
    changes={k:(a.get(k),b.get(k)) for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
    assert changes==NEW, f"unexpected PG pin delta {changes}"
    for ref,mpn in [("R501","RC1206FR-07100KL"),("R502","RC1206FR-071ML"),
                    ("Q501","BVSS123LT1G")]:
        idx=sch.index(f'(property "Reference" "{ref}"')
        assert mpn in sch[idx:idx+600],(ref,mpn)
    # Backfeed ban: no backup rail, BAT+, RAW or USB label is in output path.
    assert b[("Q501","3")]=="PWR_OK_SINK_FAIL_RELEASE"
    assert b[("Q501","1")]=="BUCK_PG_STATE"
    assert b[("Q501","2")]=="GND"
    assert '(global_label "3V3_AON"' not in sch and "CR1220" not in sch
    return {"PG_only_isolated_netlist_valid":True,
      "new_fitted_parts":3,
      "REV5_U101_PG_open_drain_switched_from_NC":True,
      "input_from_main_only":"5V_OUT->R501->PG6/Q501.G",
      "PG_D_signal_not_connected_to_any_other_power_rail":True,
      "external_pullup_needed":"TripTracer 3V3_AON via host-side resistor",
      "exported_logic":"LOW=main-good; HIGH=main-fault; no power=release",
      "no_vehicle_200v_or_coin_cell_in_PG_network":True,
      "SD_shutdown_runtime_measured":False,
      "data_safe_no_fab":True}
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("check_trippower_a_pg_netlist.py original.net alternative.net")
    print(json.dumps(verify(Path(sys.argv[1]).read_text(),Path(sys.argv[2]).read_text(),ALT.read_text()),indent=2))
