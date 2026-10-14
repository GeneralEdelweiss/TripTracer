#!/usr/bin/env python3
"""Verify LMR38020-Q1 power nets from the actual KiCad 10 exported root netlist.
Development guard only; passing is NOT ERC/DRC/thermal/vehicle approval.
"""
import re
import sys
from pathlib import Path

def check(netlist):
    text = Path(netlist).read_text(encoding="utf-8")
    net_section = text.split("\n\t(nets", 1)[1]
    nets = {}
    for block in net_section.split("\n\t\t(net")[1:]:
        name = re.search(r'\(name "([^"]+)"\)', block)
        if name is None:
            continue
        nodes = set(re.findall(
            r'\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block
        ))
        nets.setdefault(name.group(1).split("/")[-1], set()).update(nodes)

    expected = {
        "HV_PROTECTED_AFTER_EFUSE": {("U101", "3"), ("C101", "1"), ("C107", "1")},
        "GND": {("U101", "1"), ("U101", "9"), ("C101", "2"),
                ("C107", "2"), ("R102", "2"), ("R103", "2")},
        "BUCK_ENABLE": {("U101", "2")},
        "RT_400KHZ": {("U101", "4"), ("R103", "1")},
        "FB_5V": {("U101", "5"), ("R101", "2"), ("R102", "1")},
        "BOOT_38020": {("U101", "7"), ("C102", "1")},
        "SW_38020": {("U101", "8"), ("C102", "2"), ("L101", "1")},
        "V5_BUCK_RAW": {("L101", "2"), ("R101", "1"), ("C104", "1"),
                     ("C105", "1"), ("C106", "1")},
    }
    for name, required in expected.items():
        actual = nets.get(name)
        assert actual is not None, f"missing exported net: {name}"
        assert required <= actual, f"{name}: missing {sorted(required - actual)}"
    assert ("U101", "3") not in nets["V5_BUCK_RAW"], "VIN shorted to 5V"
    assert ("U101", "8") not in nets["V5_BUCK_RAW"], "SW bypasses inductor"
    assert ("U101", "7") not in nets["SW_38020"], "BOOT shorted to SW"
    # PG6 is an OPTIONAL open-drain status pin. Per TI LMR38020-Q1 datasheet
    # Table 5-1, it may be left floating if unused. Do not connect/pull it high:
    # with VIN absent and USB powering V3V3, a pullup could give false VIN1-good.
    pg6 = [(name, pins) for name, pins in nets.items() if ("U101", "6") in pins]
    assert "BUCK_PG" not in nets, "Obsolete isolated BUCK_PG label must not return"
    assert all(pins == {("U101", "6")} for _, pins in pg6), (
        f"Optional PG6 incorrectly wired: {pg6}"
    )
    print("PASS: LMR38020-Q1 8 connected native power nets; PG explicitly unused; no VIN/SW/BOOT shorts")
if __name__ == "__main__":
    check(sys.argv[1])
