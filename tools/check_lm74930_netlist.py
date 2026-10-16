"""Check REAL KiCad-exported electrical nets of LM74930/Q401/Q402/R405.

Run: python3 tools/check_lm74930_netlist.py reports/TripTracer.net
Fails closed on a wrong device pin, swapped current-sense connection, or
open gate. This verifies connectivity only; NO electrical/thermal/ISO approval.
"""
import sys
from pathlib import Path
from check_kicad_hierarchy import parse, children


def fields(item, name):
    return children(item, name)


def checks(net_file):
    root = parse(net_file)
    if root[0] != "export":
        raise ValueError(f"Unexpected netlist root {root[0]}")
    nets = fields(root, "nets")
    if len(nets) != 1:
        raise ValueError("missing KiCad nets")
    by_pin = {}
    for n in fields(nets[0], "net"):
        name = fields(n, "name")
        for item in fields(n, "node"):
            r, p = fields(item, "ref"), fields(item, "pin")
            if not r or not p:
                raise ValueError(f"Bad netlist node {item}")
            key = (str(r[0][1]), str(p[0][1]))
            if key in by_pin:
                raise AssertionError(f"Pin duplicated among nets: {key}")
            by_pin[key] = str(name[0][1]) if name else str(n)

    # Same-net assertions are valid regardless of generated global-label name.
    same = (
        (("Q401", "1"), ("R407", "2"), "HGATE series to load switch"),
        (("R407", "1"), ("U401", "14"), "HGATE output"),
        (("Q401", "3"), ("Q402", "3"), "FET common sources"),
        (("Q401", "3"), ("U401", "2"), "A sense node"),
        (("Q401", "3"), ("U401", "15"), "OUT sense node"),
        (("Q402", "1"), ("U401", "1"), "ideal diode DGATE"),
        (("Q402", "2"), ("U401", "24"), "ideal diode cathode C"),
        (("Q402", "2"), ("R405", "1"), "pre-shunt high-current node"),
        (("Q402", "2"), ("R406", "1"), "CS+ Kelvin series input"),
        (("R406", "2"), ("U401", "20"), "CS+ device pin"),
        (("R405", "2"), ("U401", "19"), "CS- device pin"),
        (("C401", "1"), ("U401", "22"), "VS bypass supply"),
        (("C401", "2"), ("U401", "13"), "GND bypass"),
        (("C402", "1"), ("U401", "23"), "CAP charge-pump supply"),
        (("C402", "2"), ("U401", "22"), "CAP charge-pump return VS"),
        (("U401", "7"), ("U401", "22"), "MODE high reverse block"),
    )
    for a, b, reason in same:
        if a not in by_pin or b not in by_pin or by_pin[a] != by_pin[b]:
            raise AssertionError(f"{reason}: {a} -> {by_pin.get(a)} != {b} -> {by_pin.get(b)}")

    # Never short source/drain or bypass protection shunt.
    different = (
        (("Q401", "2"), ("Q401", "3")),
        (("Q402", "2"), ("Q402", "3")),
        (("R405", "1"), ("R405", "2")),
        (("R406", "1"), ("R406", "2")),
        (("R407", "1"), ("R407", "2")),
        (("C401", "1"), ("C401", "2")),
        (("C402", "1"), ("C402", "2")),
    )
    for a, b in different:
        if by_pin[a] == by_pin[b]:
            raise AssertionError(f"SHORT across {a}/{b}")
    assert ("Q401", "2") in by_pin, "unconnected BAT input"
    print("PASS: 16 LM74930 controller/FET/shunt connection assertions and 7 no-short checks")
    print("NOT TESTED: MOSFET SOA, TVS, VS clamp, EN/ACC startup, OCP/OV/UV circuit, full ERC/DRC")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: check_lm74930_netlist.py <TripTracer.net>")
    checks(Path(sys.argv[1]))
