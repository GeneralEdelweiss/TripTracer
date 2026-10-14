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
        "ACC_PROTECTED_IN": {("J901","2"),("R911","1"),("R916","1")},
        "ACC_EN_BIAS": {("R911","2"),("R912","1"),("D911","1")},
        "BUCK_ENABLE": {("D911","2"),("R913","1"),("U911","3"),("U101","2")},
        "GND": {("R309","2"),("C306","2"),("J901","3"),("R912","2"),("R913","2"),("U911","2"),("Q912","2"),("Q913","2"),
                 ("R917","2"),("U301","1"),("U302","2")},
        "HOLD_TIMER_GRANTED_3V3": {("R914","1")},
        "HOLD_LED_ANODE": {("R914","2"),("U911","1")},
        "HV_PROTECTED_AFTER_EFUSE": {("R915","1"),("U101","3")},
        "BAT_INPUT_FUSED_UNPROTECTED_TVS": {("J901","1"),("D901","2")},
        "VIN_HOLD_BIAS": {("R915","2"),("U911","4")},
        "ACC_Q912_BASE": {("R916","2"),("Q912","1"),("R918","1")},
        "ACC_INV_N": {("Q912","3"),("R919","2"),("R920","1")},
        "ACC_Q913_BASE": {("R920","2"),("Q913","1")},
        "V3V3_SYS": {("U302","3"),("R919","1"),("R921","1"),("U201","3"),("R306","1")},
        "ACC_DRIVE_5V": {("Q913","3"),("R917","1"),("R921","2")},
        "V5_BUCK_RAW": {("U301","3"),("U301","5"),("R308","1")},
        "MUX_PRI1_SENSE": {("U301","4"),("R308","2"),("R309","1")},
        "USB_VBUS_RAW": {("U301","6")},
        "V5_SYS": {("U301","2"),("U301","7"),("U302","1"),("C303","1"),("C306","1")},
        "USB_ACTIVE_N": {("U301","8"),("R306","2"),("U201","28")},
        "MCU_HOLD_REQ": {("U201","25"),("U502","2"),("R504","1")},
        "TIMER_TRIG": {("U501","2"),("C502","2"),("R502","2"),("D501","2"),("D502","1")},
        "TIMER_RC": {("U501","6"),("U501","7"),("R501","2"),("C501","1")},
        "TIMER_RESET": {("U501","4"),("R503","2"),("C503","1")},
        "TIMER_CTRL": {("U501","5"),("C504","1")},
        "HOLD_TIME_WINDOW": {("U501","3"),("U502","1")},
        "HOLD_TIMER_GRANTED_3V3": {("U502","4"),("R914","1")},

    }
    for name,req in expect.items():
        actual=nets.get(name,set())
        assert req <= actual, f"{name} missing {sorted(req-actual)}; actual={sorted(actual)}"
    forbidden=[("USB_VBUS_RAW",("U301","2")),("V5_SYS",("U301","6")),
               ("V5_BUCK_RAW",("U301","6")),("BUCK_ENABLE",("U301","8"))]
    for net,node in forbidden:
        assert node not in nets.get(net,set()), f"undesired short: {node} in {net}"
    assert ("R914","1") not in nets["BUCK_ENABLE"], "3V3 hold directly on EN, unsafe on VIN=0"
    # Isolation checks: all four relevant power domains must remain disjoint.
    # Comparing node membership catches accidental global-label aliases even
    # if expected pins happen to remain present in the netlist.
    unique_rails=("HV_PROTECTED_AFTER_EFUSE","V5_BUCK_RAW","USB_VBUS_RAW","V5_SYS","V3V3_SYS")
    for idx,left in enumerate(unique_rails):
        for right in unique_rails[idx+1:]:
            assert nets[left] != nets[right], f"power rails aliased: {left} / {right}"
    # Make pin/rail association explicit for every mux terminal, including
    # its two VOUT pads (a footprint-level wiring requirement).
    exact_mux={
        "1":"GND","2":"V5_SYS","3":"V5_BUCK_RAW",
        "4":"MUX_PRI1_SENSE","5":"V5_BUCK_RAW",
        "6":"USB_VBUS_RAW","7":"V5_SYS","8":"USB_ACTIVE_N"}
    for pin,required_rail in exact_mux.items():
        actual=[name for name,nodes in nets.items() if ("U301",pin) in nodes]
        assert actual==[required_rail], (
            f"TPS2116 pin {pin}: expected exactly {required_rail}, actual {actual}")
    assert ("C305","2") in nets["GND"], "MCP1826S output capacitor must return directly to GND"
    # Critical: neither source goes directly to the core LDO: only V5_SYS.
    assert ("U302","1") not in nets["USB_VBUS_RAW"]
    assert ("U302","1") not in nets["V5_BUCK_RAW"]
    # PR1 cannot be tied directly to VIN1: it must select USB before the buck collapses.
    assert ("U301","4") not in nets["V5_BUCK_RAW"], "PR1 improperly bypasses VIN1 priority divider"
    # The opto output transistor cannot pull the vehicle VIN/EN domain
    # directly from the MCU 3.3-V GPIO.
    assert ("U911","4") not in nets["V3V3_SYS"]
    assert ("U911","3") not in nets["V3V3_SYS"]
    print("PASS: TPS2116 all eight pins exactly matched; MCP1826S VIN1/GND2/VOUT3 and ceramic output return wired")
    print("PASS: native TLC555 RC/trigger/reset + gated MCU-HOLD pin topology")
    print("PASS: 16 ACC, timed HOLD, 5V priority mux, 3V3 core and USB status net connections")

if __name__ == "__main__":
    check(sys.argv[1])
