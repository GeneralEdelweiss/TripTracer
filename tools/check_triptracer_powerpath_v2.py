#!/usr/bin/env python3
"""Verify full low-cost TripTracer power-chain topology in exported KiCad 10 netlist.
Checks schematic connectivity only: no surge, load, thermal or safety approval.
"""
from pathlib import Path
import re
import sys

def check(p):
    text = Path(p).read_text(encoding="utf-8")
    assert "\n\t(nets" in text, "missing native netlist"
    nets = {}
    for part in text.split("\n\t(nets",1)[1].split("\n\t\t(net")[1:]:
        m = re.search(r'\(name "([^"]+)"\)',part)
        if m:
            nets.setdefault(m.group(1).split("/")[-1],set()).update(
                re.findall(r'\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)',part))
    expect = {
        "ACC_PROTECTED_IN": {("R911","1"),("R916","1")},
        "ACC_EN_BIAS": {("R911","2"),("R912","1"),("D911","1")},
        "BUCK_ENABLE": {("D911","2"),("R913","1"),("U911","3"),("U101","2")},
        "GND": {("R912","2"),("R913","2"),("U911","2"),("U912","2"),
                 ("R917","2"),("U301","1"),("U302","1")},
        "HOLD_TIMER_GRANTED_3V3": {("R914","1")},
        "HOLD_LED_ANODE": {("R914","2"),("U911","1")},
        "HV_PROTECTED_AFTER_EFUSE": {("R915","1"),("U101","3")},
        "VIN_HOLD_BIAS": {("R915","2"),("U911","4")},
        "ACC_LED_ANODE": {("R916","2"),("U912","1")},
        "V3V3_SYS": {("U302","2"),("U912","4"),("U201","3"),("R306","1")},
        "ACC_DRIVE_5V": {("U912","3"),("R917","1")},
        "V5_BUCK_RAW": {("U301","3"),("U301","4"),("U301","5")},
        "USB_VBUS_RAW": {("U301","6")},
        "V5_SYS": {("U301","2"),("U301","7"),("U302","3")},
        "USB_ACTIVE_N": {("U301","8"),("R306","2"),("U201","28")},
        "MCU_HOLD_REQ": {("U201","25")},
    }
    for name,req in expect.items():
        actual=nets.get(name,set())
        assert req <= actual, f"{name} missing {sorted(req-actual)}; actual={sorted(actual)}"
    forbidden=[("USB_VBUS_RAW",("U301","2")),("V5_SYS",("U301","6")),
               ("V5_BUCK_RAW",("U301","6")),("BUCK_ENABLE",("U301","8"))]
    for net,node in forbidden:
        assert node not in nets.get(net,set()), f"undesired short: {node} in {net}"
    assert ("R914","1") not in nets["BUCK_ENABLE"], "3V3 hold directly on EN, unsafe on VIN=0"
    print("PASS: 16 ACC, timed HOLD, 5V priority mux, 3V3 core and USB status net connections")

if __name__ == "__main__":
    check(sys.argv[1])
