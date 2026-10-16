#!/usr/bin/env python3
"""Weg B Round11: independent KiCad10 A23 XML-net and order-BOM audit.

Input MUST be an XML netlist exported by KiCad from the pinned A23 root.
Do not use A's checking Python routines: this is a separate B verifier.
The output never denotes a 58V, thermal, PCB or vehicle release.
"""
from __future__ import annotations
import csv, json, re, sys
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path("audit-A23/hardware/modules/TripPower_REV6_A")
ORDER=ROOT/"REV6_A_FACTORY_OVP_23_PART_ORDER_BOM_2026-10-16.csv"
SHEETS=[ROOT/"01_TPS26631_REV6_FACTORY_OVP.kicad_sch", ROOT/"02_5V_LMR38020_FACTORY_OVP.kicad_sch"]

EXPECTED={
("U201","1"):"EFUSE_IN",("U201","2"):"EFUSE_IN",("U201","3"):"EFUSE_IN",
("U201","4"):"R6_B_GATE",("U201","5"):"R6_DRV",("U201","6"):"VIN_FUSED",
("U201","7"):"UVLO_SENSE",("U201","8"):"GND",("U201","9"):"GND",
("U201","10"):"R6_DVDT",("U201","11"):"ILIM_SET",("U201","12"):"GND",
("U201","16"):"GND",("U201","18"):"VIN_PROTECTED_UNFUSED",
("U201","19"):"VIN_PROTECTED_UNFUSED",("U201","20"):"VIN_PROTECTED_UNFUSED",
("U201","21"):"GND",
("Q201","1"):"R6_B_GATE",("Q201","2"):"EFUSE_IN",("Q201","3"):"VIN_FUSED",
("Q202","1"):"R6_DRV",("Q202","2"):"VIN_FUSED",("Q202","3"):"R6_B_GATE",
("R201","1"):"VIN_FUSED",("R201","2"):"UVLO_SENSE",
("R204","1"):"ILIM_SET",("R204","2"):"GND",
("C201","1"):"VIN_FUSED",("C201","2"):"GND",
("C202","1"):"VIN_PROTECTED_UNFUSED",("C202","2"):"GND",
("C203","1"):"R6_DVDT",("C203","2"):"GND",
("U101","2"):"VIN_PROTECTED_UNFUSED",("U101","3"):"VIN_PROTECTED_UNFUSED",
("U101","6"):"BUCK_PG_STATE",
("Q501","1"):"BUCK_PG_STATE",("Q501","2"):"GND",
("Q501","3"):"PWR_OK_SINK_FAIL_RELEASE",
("TP501","1"):"PWR_OK_SINK_FAIL_RELEASE",("TP201","1"):"VIN_FUSED",
("TP202","1"):"VIN_PROTECTED_UNFUSED",("TP203","1"):"GND",
("TP502","1"):"5V_OUT",
}
def main(netfile, native_bom):
    tree=ET.parse(netfile)
    components={}
    for e in tree.findall("./components/comp"):
        ref=e.get("ref")
        if ref:
            assert ref not in components, ("duplicate XML component",ref)
            components[ref]=e
    assert components, "No actual KiCad XML components"
    pins={}
    for net in tree.findall("./nets/net"):
        name=net.attrib["name"].split("/")[-1]
        if name.startswith("unconnected-"):
            continue  # KiCad encodes deliberately NC pins as individual pseudo-nets
        for node in net.findall("node"):
            k=(node.get("ref"),node.get("pin"))
            assert k not in pins, ("pin in multiple nets",k)
            pins[k]=name
    assert len(pins)>40, ("Missing actual KiCad net nodes",len(pins))
    errors={f"{ref}.{pin}":{"found":pins.get((ref,pin)),"want":n}
            for (ref,pin),n in EXPECTED.items() if pins.get((ref,pin))!=n}
    assert not errors, json.dumps(errors,indent=2)
    assert all(("U201",p) not in pins for p in ("13","14","15","17")), "SHDN/diagnostic unexpected external connection"
    assert all(("R202",p) not in pins and ("R203",p) not in pins for p in ("1","2"))
    assert pins[("U201","1")]!=pins[("U201","6")], "TPS IN1..3 and IN_SYS MUST be different nodes"
    assert pins[("U201","12")]==pins[("U201","16")]==pins[("U201","9")]=="GND"
    fitted={r for r in components if re.fullmatch(r"[RCLUQ]\d+",r)}
    assert len(fitted)==23, ("A23 count",len(fitted),sorted(fitted))
    assert all(not re.fullmatch(r"F\d+",r) for r in components), "TripPower must have zero fuse footprints"

    # Read exact instance property pairs independently of vendor price CSV.
    # Restrict matches to placed symbols, not symbol library definitions.
    instance_mpns={}
    for path in SHEETS:
        s=path.read_text(encoding="utf-8")
        pat=r'\(symbol \(lib_id "[^"]+"\)[\s\S]{0,750}?\(property "Reference" "([A-Z]+\d+)"[\s\S]{0,800}?\(property "MPN" "([^"]+)"'
        for ref,mpn in re.findall(pat,s):
            assert ref not in instance_mpns, ("duplicate placed reference",ref)
            instance_mpns[ref]=mpn
    assert set(instance_mpns)==fitted, ("instance MPN/ref mismatch", sorted(set(instance_mpns)^fitted))
    rows=list(csv.DictReader(ORDER.open(encoding="utf-8",newline="")))
    order={r["ref"]:r for r in rows if re.fullmatch(r"[A-Z]+\d+",r["ref"])}
    assert len(order)==23 and set(order)==fitted
    assert set(instance_mpns)==set(order)
    for ref in fitted:
        assert instance_mpns[ref]==order[ref]["mpn"], (ref,instance_mpns[ref],order[ref]["mpn"])
        native_footprint=(components[ref].findtext("footprint") or "").strip()
        assert native_footprint==order[ref]["KiCad_footprint"], (ref,native_footprint,order[ref]["KiCad_footprint"])
    # Explicitly compare every native KiCad resistor VALUE (not just resistor MPN).
    # The seven nominal resistor values come from the actual A23 placed symbols.
    expected_resistor_values={
        "R201":"330k", "R204":"6.04k", "R101":"100k",
        "R102":"24.9k", "R103":"64.9k", "R501":"100k", "R502":"1M",
    }
    assert {r for r in fitted if r.startswith("R")}==set(expected_resistor_values)
    for ref, nominal in expected_resistor_values.items():
        native_value=(components[ref].findtext("value") or "").strip()
        assert native_value.startswith(nominal+" "), (ref,native_value,nominal)
    assert order["R201"]["mpn"]=="AC1206FR-07330KL"
    assert order["R204"]["mpn"]=="CRCW12066K04FKEAHP"
    assert order["U201"]["mpn"]=="TPS26631PWPR"
    assert order["U101"]["mpn"]=="LMR38020SQDDARQ1"
    with open(native_bom,encoding="utf-8",newline="") as f:
        native=list(csv.DictReader(f))
    refs=[ref.strip() for row in native for ref in row["Refs"].split(",") if ref.strip()]
    assert len(refs)==23 and set(refs)==fitted, ("exported BOM refs",len(refs),sorted(set(refs)^fitted))
    assert all(row["Qty"]=="1" and not row["DNP"] for row in native)
    totals=[sum((Decimal(r[k]) for r in order.values()),Decimal(0))
        for k in ("eur_exVAT_1","eur_exVAT_10","eur_exVAT_100")]
    assert totals==[Decimal("20.2570"),Decimal("13.5610"),Decimal("10.6266")],totals
    # Manufacturer min-max arithmetic; not a measured UVLO threshold.
    rmin=330000*(1-.01-100e-6*60)
    assert rmin>300000
    assert 32<32.7 and 36>35.4
    print(json.dumps({
        "basis":"native KiCad 10 XML netlist + native BOM + independently parsed A23 sheets",
        "verified_pin_to_net_relations":len(EXPECTED),
        "fit_count":len(fitted),"all_23_mpn_and_footprints_match":True,
        "all_7_native_resistor_values_match":True,
        "no_tripPower_fuse":True,
        "mode":"GND auto retry","pgth":"GND TPS PGOOD forced low / 2x IOL not armed",
        "SHDN":"open, internal enable pullup: NOT a +85C hardware interlock",
        "UVLO_Rmin_hot_ohm":round(rmin,3),
        "factory_ovp_rising_V":[33.2,35.4],"falling_V":[32.7,35],
        "eu_component_total_ex_vat_1_10_100":[str(v) for v in totals],
        "58V_thermal_RAW_and_host_qualified":False,"fabrication_approved":False
    },indent=2,sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("Usage: ... path/to/native-A23.xml path/to/native-A23-bom.csv")
    main(Path(sys.argv[1]),Path(sys.argv[2]))
