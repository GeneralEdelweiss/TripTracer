#!/usr/bin/env python3
"""TripTracer power switching and NCV1117 thermal capacity budgets.
Conservative engineering bounds, NOT qualification or measured performance.
"""
from math import inf

def cap_needed(i_amp, gap_seconds, allowable_droop):
    return i_amp*gap_seconds/allowable_droop

def main():
    # Representative envelope only; TPS2116 manufacturer tSW max must be
    # selected from exact variant, VIN difference and worst-case datasheet.
    for i in (0.2,0.4,0.7):
        for gap_us in (100,1000):
            c=cap_needed(i,gap_us*1e-6,0.3)
            print(f"mux transition: I={i:.1f} A, break={gap_us}us, 0.30V droop -> >= {c*1e6:.0f}uF effective")
    for i in (0.2,0.3,0.4,0.5):
        p=(5.0-3.3)*i
        for ambient in (60,85):
            theta_allowed=(125-ambient)/p
            print(f"NCV1117: I3V3={i:.1f}A, P={p:.3f}W, Tamb={ambient}C, "
                  f"thetaJA needed <= {theta_allowed:.1f}K/W for Tj<=125C")
    c_nom=22e-6
    max_100us=c_nom*.3/100e-6
    print(f"22uF nominal could support at most {max_100us:.3f}A for 100us/0.3V, "
          "and real MLCC DC bias reduces this.")
    assert c_nom < cap_needed(.4,100e-6,.3)
    print("PASS: correctly flags that 22uF is insufficient at 0.4A / 100us / 0.3V droop.")
    print("NOT PROVEN: actual TPS2116 transition time, 3V3 LDO thermals, effective MLCC capacitance.")
if __name__=="__main__":
    main()
