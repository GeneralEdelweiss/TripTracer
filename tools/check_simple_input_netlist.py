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
    for pin in ("4","5","6"):
        assert ("D902",pin) in out and ("D902",pin) not in gnd, ("TVS5800 IN",pin,out)
    for pin in ("1","2","3"):
        assert ("D902",pin) in gnd and ("D902",pin) not in out, ("TVS5800 GND",pin,gnd)
    assert 'TVS5800VEBR' in data and 'D_TVS5800_VEB0006A' in data
    assert 'S5MC-13-F 5A 1000V' in data and 'D_S5MC_SMC' in data
    assert ("U101","3") in out, ("buck VIN must be protected",out)
    assert not (("D901","1") in bat or ("D901","2") in out), "reversed or shorted diode"
    print("PASS: S5MC anode2 BAT+, cathode1 VIN; TVS5800 all six IN/GND pads; U101 VIN connected. No surge rating implied.")

if __name__ == "__main__":
    check(sys.argv[1])
