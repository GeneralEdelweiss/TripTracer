#!/usr/bin/env python3
"""TripTracer power-mux switchover and MCP1826S 3V3 dropout/thermal design gate.

This checks datasheet arithmetic. PASS means hazards were detected,
NOT that the supply passed thermal or automotive qualification.
TPS2116: https://www.ti.com/lit/ds/symlink/tps2116.pdf
MCP1826S: https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP1826-MCP1826S-1000-mA,-Low-Voltage,-Low-Quiescent-Current-LDO-Regulator-20002057C.pdf
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMATIC=(ROOT/"hardware/kicad/03_3V3_USB.kicad_sch").read_text()

def c_required(current, microseconds, max_droop):
    return current*microseconds/max_droop  # numeric value is in microfarads

def main():
    assert '"MCP1826S-3302E/DB"' in SCHEMATIC
    assert '"NCV1117ST33T3G"' not in SCHEMATIC
    assert '"R307"' not in SCHEMATIC
    assert '"22uF 10V MUX_OUT_HOLDUP"' in SCHEMATIC
    # TPS2116 PR1: VREF 0.92..1.08, 1% resistors, 0.1uA PR1 leakage.
    v_switch_min = .92*(1+(100e3*.99)/(30.1e3*1.01)) - .1e-6*(100e3*.99)
    i3v3=.4
    # TPS2116 on-resistance at 105C up to 74mohm (datasheet).
    v_rail_min = v_switch_min - i3v3*.074
    # MCP1826S max drop 0.4V at 1A, fixed 3.3V with standard 2% tolerance.
    v_needed=3.3*1.02 + .4
    margin=v_rail_min-v_needed
    print(f"Power mux PR1 minimum transition approx {v_switch_min:.3f}V")
    print(f"At {i3v3:.1f}A and 74mOhm TPS2116: V5_SYS at limit ~{v_rail_min:.3f}V; MCP1826S target input >= {v_needed:.3f}V; margin ~{margin:.3f}V")
    assert margin>0, "Selected LDO still cannot guarantee regulation before VIN1 switchover"
    print("PASS: static worst-limit dropout compatibility (not dynamics, load transients or capacitor derating)")
    for micros in (8,20,100):
        req=c_required(i3v3,micros,.3)
        print(f"TPS2116 gap {micros:3d}us at 0.4A: >= {req:.1f}uF effective for 0.3V droop; current schematic 44uF nominal.")
    assert c_required(.4,8,.3)<44
    # Datasheet MCP1826S SOT-223 reference 4-layer JEDEC thetaJA=62K/W.
    ambient=85.0
    rise_watts=(5.0-3.3)*i3v3
    theta_reference=62.0
    tj=ambient+rise_watts*theta_reference
    allowed=(125-ambient)/(theta_reference*(5.0-3.3))
    print(f"MCP1826S SOT223 JEDEC 4-layer: thetaJA={theta_reference:.0f}K/W; I={i3v3:.1f}A; Tj~{tj:.1f}C @ Ta85C, above 125C continuous rating.")
    print(f"At Ta85C nominal V5=5V, reference 4-layer maximum I3V3~{allowed:.3f}A for Tj<=125C.")
    assert tj>125, "4-layer thermal risk detection expected at 0.4A"
    print("PASS: identifies thermal BLOCKER. 2-layer PCB or small copper may be worse.")
    print("REMAINING: choose DDPAK/thermal-safe 3.3V regulator or verified current limit, calculate worst-case load and bench temperature.")
    print("NOT PROVEN: actual source switchover/reset behavior, USB source budget, TVS 350ms load-dump.")
if __name__=="__main__":
    main()
