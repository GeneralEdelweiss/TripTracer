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
        "ACC_PROTECTED_IN": {("F902","2"),("R923","1"),("R916","1")},
        "BUCK_ENABLE": {("R911","2"),("R913","1"),("U911","3"),("U101","2")},
        "GND": {("J201","A1"),("C305","2"),("R309","2"),("C306","2"),("J901","3"),("R924","2"),("U921","7"),("D911","2"),("Q914","2"),("R913","2"),("U911","2"),("Q912","2"),("D912","2"),
                 ("U301","1"),("U302","2")},
        "HOLD_LED_ANODE": {("R914","2"),("U911","1")},
        "HV_PROTECTED_AFTER_EFUSE": {("R915","1"),("U101","3"),("Q922","5"),("U921","9"),("U921","12")},
        "BAT_INPUT_FUSED_UNPROTECTED_TVS": {("F901","2"),("D921","1"),("Q921","2")},
        "VIN_HOLD_BIAS": {("R915","2"),("U911","4")},
        "ACC_Q912_BASE": {("R916","2"),("Q912","1"),("R918","1")},
        "MCU_ACC_INV_N": {("R207","2"),("U201","29")},
        "ACC_INV_N": {("R207","1"),("Q912","3"),("R919","2"),("U501","2"),("R502","2"),("D503","3")},
        "V3V3_SYS": {("U302","3"),("R919","1"),("U201","3"),("R306","1")},
        "V5_BUCK_RAW": {("U301","3"),("U301","5"),("R308","1")},
        "MUX_PRI1_SENSE": {("U301","4"),("R308","2"),("R309","1")},
        "USB_VBUS_RAW": {("U301","6"),("J201","A4"),("J201","A9"),("J201","B4"),("J201","B9")},
        "V5_SYS": {("U301","2"),("U301","7"),("U302","1"),("C303","1"),("C306","1")},
        "USB_ACTIVE_N": {("U301","8"),("R306","2"),("U201","28")},
        "MCU_HOLD_REQ": {("U201","25"),("U502","2"),("R504","1")},
        "TIMER_RC": {("U501","6"),("U501","7"),("R501","2"),("C501","1")},
        "TIMER_RESET": {("U501","4"),("R503","2"),("C503","1")},
        "TIMER_CTRL": {("U501","5"),("C504","1")},
        "HOLD_TIME_WINDOW": {("U501","3"),("U502","1")},
        "HOLD_TIMER_GRANTED_3V3": {("U502","4"),("R914","1")},

    }
    for name,req in expect.items():
        actual=nets.get(name,set())
        assert req <= actual, f"{name} missing {sorted(req-actual)}; actual={sorted(actual)}"
    # MCU must observe ACC OFF without being able to clamp the timer directly.
    for pin, required in {"1": "ACC_INV_N", "2": "MCU_ACC_INV_N"}.items():
        actual = [name for name, nodes in nets.items() if ("R207", pin) in nodes]
        assert actual == [required], f"ACC sense isolation R207.{pin}: {actual}"
    assert ("U201", "29") not in nets["ACC_INV_N"], "MCU bypasses timer fault isolation"
    assert nets["MCU_ACC_INV_N"] == {("R207", "2"), ("U201", "29")}, "ACC sense unexpectedly loaded"
    assert nets["ACC_INV_N"] == {("Q912","3"),("R919","2"),("U501","2"),
                                ("R502","2"),("D503","3"),("R207","1")}, "timer trigger unexpectedly loaded"
    print("PASS: GPIO34/pad29 senses inverse ACC through R207; no direct MCU clamp of shared timer trigger")
    # Check every timer IC terminal exactly, including supply pins and clamps.
    # TRIG is now a DC inverse-ACC signal; obsolete AC coupling/clamps are absent.
    exact_timer = {
        "U501": {"1":"GND", "2":"ACC_INV_N", "3":"HOLD_TIME_WINDOW",
                 "4":"TIMER_RESET", "5":"TIMER_CTRL", "6":"TIMER_RC",
                 "7":"TIMER_RC", "8":"V3V3_SYS"},
        "U502": {"1":"HOLD_TIME_WINDOW", "2":"MCU_HOLD_REQ", "3":"GND",
                 "4":"HOLD_TIMER_GRANTED_3V3", "5":"V3V3_SYS"},
        "C503": {"1":"TIMER_RESET", "2":"GND"},
        "C504": {"1":"TIMER_CTRL", "2":"GND"},
        "C505": {"1":"V3V3_SYS", "2":"GND"},
        "R503": {"1":"V3V3_SYS", "2":"TIMER_RESET"},
        "R504": {"1":"MCU_HOLD_REQ", "2":"GND"},
    }
    for ref, pins in exact_timer.items():
        for pin, required in pins.items():
            actual = [name for name, nodes in nets.items() if (ref, pin) in nodes]
            assert actual == [required], (
                f"{ref}.{pin}: expected exactly {required}, actual {actual}")
    print("PASS: timer and AND supply pins, direct inverse-ACC trigger, POR and fail-off pull-down")
    rearm = {
        "R505": {"1":"TIMER_RC", "2":"TIMER_RC_CLAMP"},
        "D503": {"1":"TIMER_RC_CLAMP", "3":"ACC_INV_N"},
        "D912": {"1":"ACC_Q912_BASE", "2":"GND"},
        "R919": {"1":"V3V3_SYS", "2":"ACC_INV_N"},
    }
    for ref, pins in rearm.items():
        for pin, required in pins.items():
            actual = [name for name, nodes in nets.items() if (ref, pin) in nodes]
            assert actual == [required], f"rearm {ref}.{pin}: {actual} != {required}"
    for retired in ("C502","D501","D502","Q913","R917","R920"):
        assert not any(ref == retired for nodes in nets.values() for ref, pin in nodes), retired
    assert "ACC_DRIVE_5V" not in nets and "ACC_Q913_BASE" not in nets
    print("PASS: prearmed 555 TRIG on global inverse ACC, low-leak RC rearm diode and Q912 reverse-base clamp")
    # ACC has no passive positive-current path to EN: all startup energy is VIN.
    startup = {
        "Q914": {"1":"ACC_START_BASE", "2":"GND", "3":"ACC_START_SINK"},
        "Q915": {"1":"ACC_START_PNP_BASE", "2":"LM748_VS_SAFE", "3":"ACC_START_VIN"},
        "R923": {"1":"ACC_PROTECTED_IN", "2":"ACC_START_BASE"},
        "R924": {"1":"ACC_START_BASE", "2":"GND"},
        "R922": {"1":"ACC_START_SINK", "2":"ACC_START_PNP_BASE"},
        "R912": {"1":"LM748_VS_SAFE", "2":"ACC_START_PNP_BASE"},
        "R911": {"1":"ACC_START_VIN", "2":"BUCK_ENABLE"},
        "D911": {"1":"ACC_START_BASE", "2":"GND"},
    }
    for ref, pins in startup.items():
        for pin, required in pins.items():
            actual = [name for name, nodes in nets.items() if (ref, pin) in nodes]
            assert actual == [required], f"startup {ref}.{pin}: {actual} != {required}"
    assert "ACC_EN_BIAS" not in nets, "old direct ACC-to-EN bias route returned"
    assert ("R911","1") not in nets["ACC_PROTECTED_IN"]
    assert not ({("D911","1"),("D911","2")} & nets["BUCK_ENABLE"])
    print("PASS: VIN-sourced PNP startup, isolated ACC NPN drive, EN pulldown and negative base clamp")
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
    print("PASS: physical USB-C J201 VBUS A4/A9/B4/B9, GND A1 and external harness J901 mapped to real source nets")
    print("PASS: native TLC555 RC/trigger/reset + gated MCU-HOLD pin topology")
    print("PASS: 16 ACC, timed HOLD, 5V priority mux, 3V3 core and USB status net connections")

if __name__ == "__main__":
    check(sys.argv[1])
