#!/usr/bin/env python3
"""Native KiCad 10 netlist guard for experimental low-cost automotive input."""
import re
import sys
from pathlib import Path

def check(path):
    data = Path(path).read_text(encoding="utf-8")
    assert '\n\t(nets' in data, "missing netlist nets section"
    nets = {}
    for block in data.split('\n\t(nets',1)[1].split('\n\t\t(net')[1:]:
        m = re.search(r'\(name "([^"]+)"\)', block)
        if m:
            nets.setdefault(m.group(1).split("/")[-1],set()).update(
                re.findall(r'\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)',block))
    bat = nets.get("BAT_INPUT_FUSED_UNPROTECTED_TVS",set())
    out = nets.get("HV_PROTECTED_AFTER_EFUSE",set())
    gnd = nets.get("GND",set())
    assert ("D901","2") in bat, ("BAT+ missing diode anode",bat)
    assert ("D901","1") in out, ("output missing diode cathode",out)
    assert ("D902","1") in out, ("TVS cathode must be on protected 5V buck VIN",out)
    assert ("D902","2") in gnd, ("TVS anode must be grounded",gnd)
    assert ("U101","3") in out, ("buck VIN must be protected",out)
    assert not (("D901","1") in bat or ("D901","2") in out), "reversed or shorted diode"
    assert ("D902","1") not in gnd, "TVS shorted"
    print("PASS: low-cost diode anode BAT+, cathode VIN, TVS reverse-biased; U101 VIN connected. No surge rating implied.")

if __name__ == "__main__":
    check(sys.argv[1])
