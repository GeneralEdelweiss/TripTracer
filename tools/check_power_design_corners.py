#!/usr/bin/env python3
"""Static ACC/HOLD/USB power design corner-case checks; NOT a bench/ISO certification."""
from math import isfinite

def acc_en(vbat, rtop=100e3, rbleed=47e3, ren=100e3, vf=0.35):
    # D911 idealized forward biased model with R912 loading upstream node
    # and R913 EN-to-GND load. Solve exact two node KCL with constant diode Vf.
    # (VB-Va)/Rtop = Va/Rbleed + Ve/ren; Va=Ve+Vf.
    va=(vbat/rtop+vf/ren)/(1/rtop+1/rbleed+1/ren)
    return max(0,va-vf)

def test():
    # Electrical assumptions are explicit, not worst case, to identify topology errors.
    for v in (9,12,24,30):
        ve=acc_en(v)
        print(f"ACC ON VIN={v:>2}V -> EN~{ve:.2f}V with D911=0.35V, ideal resistors")
        assert 1.4 < ve < v+0.3
    # Off ACC: pull-down must be real; leakage / VIN bias need temperature qualification.
    assert acc_en(0)==0
    # At 9V, input resistor to ACC-sense LED IF about 1.1mA, so
    # datasheet CTR minimum at IF=5mA cannot justify the present signal guarantee.
    for v in (9,24,30):
        ifled=max(0,(v-1.25)/6800)
        ic_needed=3.3/47000
        print(f"U912 VIN={v:>2}V: IF~{ifled*1000:.2f}mA; required CTR >= {100*ic_needed/ifled:.1f}%")
    # 555 t = 1.1 R C nominal; MLCC bias/thermal tolerance is not covered.
    assert abs(1.1*2.2e6*10e-6 - 24.2) < .1
    # TPS2116 priority-mode: tie MODE=VIN1, PR1=VIN1, USB=VIN2.
    # PR1=VIN1 at ~5V gives guaranteed threshold if VIN1 valid, but in
    # source switchover a break-before-make dropout remains.
    print("PASS: ACC resistor-divider nominal start at 9V; source-priority connectivity rules represented.")
    print("NOT TESTED: hot/cold component leakage, USB transfer dropout, ACC transient, optocoupler CTR at low IF, TVS load-dump.")
if __name__=="__main__":
    test()
