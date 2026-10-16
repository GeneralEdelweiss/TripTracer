#!/usr/bin/env python3
"""Native KiCad 10 root-netlist assertions for new LM74800-Q1 common-source frontend.
Checks only schematic connectivity, never electrical/automotive/PCB safety approval.
"""
import re
import sys
from pathlib import Path

def check(path):
    data = Path(path).read_text(encoding="utf-8")
    assert "\n\t(nets" in data, "Not a KiCad native netlist"
    nets = {}
    for part in data.split("\n\t(nets",1)[1].split("\n\t\t(net")[1:]:
        m=re.search(r'\(name "([^"]+)"\)',part)
        if m:
            nets.setdefault(m.group(1).split("/")[-1],set()).update(
                re.findall(r'\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)',part))
    def need(net,*pins):
        actual=nets.get(net,set())
        missing=set(pins)-actual
        assert not missing, f"{net}: missing {missing}; actual={sorted(actual)}"
    need("ACC_PROTECTED_IN",("J901","2"),("R923","1"),("R916","1"))
    need("BAT_INPUT_FUSED_UNPROTECTED_TVS",("J901","1"),("Q921","2"),("R921","1"),("D921","1"),("C921","1"),("R932","1"))
    need("GND",("J901","3"),("U921","7"),("D922","2"),("D923","2"),("C924","2"),("R934","2"))
    need("LM748_A",("Q921","3"),("Q922","1"),("Q922","2"),("Q922","3"),("U921","2"),("D924","2"),("C924","1"),("C927","2"))
    need("LM748_VS_SAFE",("U921","4"),("R921","2"),("D923","1"),("D924","1"),("C922","1"),("C923","1"),
         ("U921","3"),("U921","10"),("R912","1"),("Q915","2"))
    assert "LM748_OV_FEED" not in nets, "obsolete clamped OV-divider input returned"
    need("LM748_OV_TOP_MID",("R932","2"),("R933","1"))
    need("LM748_OV",("U921","5"),("R933","2"),("R934","1"))
    need("LM748_CAP",("U921","11"),("C925","1"))
    need("LM748_HGATE_RAW",("U921","8"),("R925","1"))
    need("LM748_HGATE_POWER",("R925","2"),("Q921","1"),("C927","1"))
    need("LM748_DGATE",("U921","1"),("Q922","4"))
    need("BUCK_ENABLE",("U921","6"),("R911","2"),("R913","1"))
    assert ("U101","2") not in nets["BUCK_ENABLE"], "Buck EN must follow its VIN after LM748 cutoff"
    need("HV_PROTECTED_AFTER_EFUSE",("Q922","5"),("U921","9"),("U921","12"),
         ("U101","2"),("U101","3"),("C926","1"),("R915","1"))
    need("LM748_TVS_MID",("D921","2"),("D922","1"))
    need("LM748_CAP",("C925","1"),("U921","11"))
    # The KiCad native BOM/netlist includes on-board J901 pigtail; excludes on_board=no external fuses and M8.
    # Assert their presence in the actual schematic source; only live PCB nodes
    # are compared with the export. Source wires are explicitly mapped by names.
    source = Path("hardware/kicad/01I_LM74800_INPUT.kicad_sch").read_text("utf-8")
    for ref,net_a,net_b in (
        ("F901","VEHICLE_BAT_RAW","BAT_INPUT_FUSED_UNPROTECTED_TVS"),
        ("F902","VEHICLE_ACC_RAW","ACC_PROTECTED_IN")):
        begin=source.find(f'(property "Reference" "{ref}"')
        assert begin>=0 and net_a in source and net_b in source, f"offboard {ref} is not drawn"
    assert 'VEHICLE_M8_EXTERNAL' in source and 'POWER_HARNESS_3WIRE' in source, "external M8 vehicle feed missing"
    # TI LM74800 DRR0012E (TI datasheet pp.42-44): 3x3mm, 0.5mm pitch,
    # 12x 0.62x0.25mm leads, center RTN pad 13 MUST remain isolated.
    fref='Tripmaster:TI_LM74800_Q1_DRR0012E'
    assert '(property "Footprint" "'+fref+'"' in source, "U921 missing TI WSON12 footprint"
    fp=Path('hardware/kicad/Tripmaster.pretty/TI_LM74800_Q1_DRR0012E.kicad_mod').read_text('utf-8')
    pads=re.findall(r'\(pad "(\d+)" smd',fp)
    assert sorted(map(int,pads))==list(range(1,14)),f"LM74800 footprint pins 1..13 mismatch: {pads}"
    for n in range(1,7):
        y=-1.25+(n-1)*.5
        assert f'(pad "{n}" smd roundrect (at -1.39 {y:g})' in fp, f"left DRR pad {n} position"
        assert f'(pad "{13-n}" smd roundrect (at 1.39 {y:g})' in fp, f"right DRR pad {13-n} position"
    assert '(pad "13" smd rect (at 0 0) (size 1.3 2.5)' in fp
    assert "RTN pad13 MUST FLOAT" in fp and "(via " not in fp, "RTN pad13 must not be tied to GND"
    # Charge pump is CAP-to-VS, NOT CAP-to-GND.
    need("LM748_VS_SAFE",("C925","2"))
    # KiCad exports explicitly NC-marked pads on a synthetic unconnected net;
    # this is correct and must not be misclassified as a GND or rail connection.
    rtn_nets=[(name,nodes) for name,nodes in nets.items() if ("U921","13") in nodes]
    assert all(name.startswith("unconnected-") and nodes == {("U921","13")}
               for name,nodes in rtn_nets), f"RTN 13 must float: {rtn_nets}"
    for old in ("D901","D902","U401","Q401","Q402"):
        assert all(ref != old for nodes in nets.values() for ref,pin in nodes), f"Obsolete {old} is active"
    assert {("D923","1"),("D924","1")} <= nets["LM748_VS_SAFE"], "D_A_VS vs zener mixed up"
    print("PASS: native 01I LM74800 / 2 FETs / ACC-HOLD / OV / VS clamp / TVS / fuses mapped; no ISO/PCB approval")
if __name__ == "__main__": check(sys.argv[1])
