#!/usr/bin/env python3
"""Data-sheet-conditioned TPS2116 transfer and NCV1117 thermal budgets.

TPS2116 rev A section 6.6: tSW (VINx=5V, RL=10ohm, CL=10uF)
is a TYPICAL test point (~8us), NOT a worst-case guarantee.
No claim of successful SD writes or production qualification.
Source: https://www.ti.com/lit/ds/symlink/tps2116.pdf
"""
def c_required(load_a, duration_us, droop_v):
    return 1e6 * load_a * duration_us * 1e-6 / droop_v

def main():
    load=0.4
    print("TPS2116 5V tSW datasheet typical test: ~8us, RL=10ohm, CL=10uF")
    for t in (8,20,100,1000):
        req=c_required(load,t,0.3)
        actual_droop=load*t*1e-6/22e-6
        print(f"0.4A, {t}us: >= {req:.1f}uF effective for 0.3V droop; nominal C303=22uF gives {actual_droop:.3f}V")
    assert abs(c_required(.4,8,.3)-10.6666666667)<.01
    assert c_required(.4,100,.3)>133
    # 22uF capacitor DC derating unknown; evaluate usable cap separately.
    for eff in (10,22,44):
        print(f"effective V5_SYS {eff}uF: ~{eff*.3/.4:.1f}us supported at 0.4A /0.3V droop")
    for i in (0.2,0.3,0.4,0.5):
        dissipated=(5-3.3)*i
        thermal=(125-85)/dissipated
        print(f"NCV1117 {i:.1f}A: Pd={dissipated:.3f}W; for Tamb85C, Tj<=125C needs thetaJA <= {thermal:.1f}K/W")
    print("PASS: representative calculations. tSW 8us is typical ONLY; no guaranteed max given here.")
    print("OPEN: measured transition while both sources present, USB current limit, MLCC derating, LDO junction temperature.")
if __name__=="__main__":
    main()
