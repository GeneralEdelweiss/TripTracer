#!/usr/bin/env python3
"""REV6 A procurement lock: 25 populated, native KiCad BOM vs exact MPN + EUR vendor price.
No external fuse, connector, carrier, microcontroller, or unqualified PCB included.
"""
import csv
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

BASE=Path("hardware/modules/TripPower_REV6_A")
SHEETS=[BASE/"01_TPS26631_REV6.kicad_sch",BASE/"02_5V_LMR38020_REV6.kicad_sch"]
SOURCE_BOM=BASE/"REV6_A_25_PART_ORDER_BOM_2026-10-15.csv"

def extract_instances():
    all_parts={}
    pattern=re.compile(
       r'\(symbol \(lib_id "[^"]+"\)[\s\S]{0,750}?\(property "Reference" "([A-Z]+\d+)"[\s\S]{0,800}?\(property "MPN" "([^"]+)"')
    for path in SHEETS:
        s=path.read_text(encoding="utf-8")
        for match in pattern.finditer(s):
            ref,mpn=match.group(1),match.group(2)
            assert ref not in all_parts, f"duplicate {ref}"
            all_parts[ref]=mpn
    assert len(all_parts)==25, f"exact 25 populated instance MPNs required: {sorted(all_parts)}"
    return all_parts

def check(native_bom):
    instances=extract_instances()
    vendor=list(csv.DictReader(SOURCE_BOM.open(encoding="utf-8")))
    vendor=[r for r in vendor if re.fullmatch(r"[A-Z]+\d+",r["ref"])]
    assert len(vendor)==25 and len({r["ref"] for r in vendor})==25, "price list must have precisely 25 unique fitted rows"
    records={r["ref"]:r for r in vendor}
    assert set(records)==set(instances), f"missing={set(instances)-set(records)}, phantom={set(records)-set(instances)}"
    price_totals=[Decimal("0")]*3
    for ref,mpn in instances.items():
        v=records[ref]
        assert v["mpn"]==mpn, f"{ref}: KiCad={mpn}, order CSV={v['mpn']}"
        assert v["KiCad_footprint"] and v["manufacturer"] and v["pricing_status"]
        assert not any(tag in mpn.upper() for tag in ("FUSE","HOLDER","THERMAL_FUSE"))
        for i,q in enumerate(("eur_exVAT_1","eur_exVAT_10","eur_exVAT_100")):
            assert v[q].strip(), f"{ref}: no EU price {q}"
            p=Decimal(v[q])
            assert p>0, f"invalid or zero price {ref}:{q}"
            price_totals[i]+=p
    with open(native_bom,encoding="utf-8",newline="") as f:
        exported=list(csv.DictReader(f))
    native={s.strip() for row in exported for s in row["Refs"].split(",")}
    assert native==set(instances),f"Native schematic BOM mismatch: missing={set(instances)-native}, extra={native-set(instances)}"
    assert len(exported)==25 and all(row["Qty"]=="1" and not row["DNP"] for row in exported)
    expected=[Decimal("20.7630"),Decimal("13.9910"),Decimal("11.0217")]
    assert price_totals==expected,(price_totals,expected)
    return {"populated_tripPower_only":len(instances),"native_KiCad_refs_equal_MPN_rows":True,
      "all_25_real_MPNs_and_supplier_EUR_price_rows_present":True,
      "component_cost_EUR_exVAT_1_10_100":[str(p) for p in price_totals],
      "quoted_but_hot_surge_PCB_UVOV_validation_missing":True,
      "no_vehicle_FMAIN_or_host_carrier_in_BOM":True,
      "released_to_fabrication":False}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Usage: check_trippower_a_rev6_procurement.py native_kicad_bom.csv")
    print(json.dumps(check(Path(sys.argv[1])),indent=2))
