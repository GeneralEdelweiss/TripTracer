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
    assert '"MCP1826S-3302E/EB"' in SCHEMATIC
    assert '"Package_TO_SOT_SMD:TO-263-3_TabPin2"' in SCHEMATIC
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
    # Datasheet MCP1826S 3-lead DDPAK θJA=31.4K/W on JEDEC 4-layer reference.
    ambient=85.0
    loss=(5.0-3.3)*i3v3
    theta_reference=31.4
    tj=ambient+loss*theta_reference
    allowed=(125-ambient)/(theta_reference*(5.0-3.3))
    print(f"MCP1826S DDPAK JEDEC 4-layer thetaJA={theta_reference:.1f}K/W; 0.4A and 85C ambient -> Tj~{tj:.1f}C")
    print(f"At 85C, maximum I3V3 for Tj<=125C and nominal 5V ~{allowed:.3f}A on that reference PCB.")
    assert tj<125, "DDPAK at 0.4A failed nominal reference-board thermal check"
    # Reference-board condition, not an actual future 2-layer PCB/copper promise.
    s223=ambient+loss*62
    assert s223>125 and tj<125, "DDPAK must meaningfully improve on original SOT223 design"
    print(f"PASS: DDPAK reference estimate reduces Tj versus SOT-223 ~{s223:.1f}C; actual copper/layout still to prove.")
    print("REMAINING: choose DDPAK/thermal-safe 3.3V regulator or verified current limit, calculate worst-case load and bench temperature.")
    print("NOT PROVEN: actual source switchover/reset behavior, USB source budget, TVS 350ms load-dump.")
if __name__=="__main__":
    main()
