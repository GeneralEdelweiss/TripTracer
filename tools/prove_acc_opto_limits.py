#!/usr/bin/env python3
"""Manufacturer-limit proof for U912 ACC sense. A FAIL verdict is a successful diagnostic test.

Source: Wuerth 140356145000 datasheet rev 001.004, 2023-08-22, p.2:
CTR min 50% only at IF=5mA,VCE=5V,TA=25C.
VF max 1.4V at IF=10mA, IF absolute max 60mA, input power max 100mW.
Do not interpolate a guaranteed CTR outside stated test conditions.
"""
from pathlib import Path
import re

SCHEMATIC = Path(__file__).resolve().parents[1]/"hardware/kicad/01H_ACC_HOLD_GATE.kicad_sch"

def verify():
    s=SCHEMATIC.read_text()
    assert '"R916"' in s and '"6.8k ACC LED"' in s, "R916 changed; recompute proof"
    assert '"R917"' in s and '"47k ACC SENSE BLEED"' in s, "R917 changed; recompute proof"
    rled, rload=6800,47000
    vf_for_min_approx=1.4
    for v in (9,12,24,30):
        if_approx=(v-vf_for_min_approx)/rled
        required_if=0.005
        available_ic_50pct=if_approx*0.5  # hypothetical, NOT a guarantee
        load_ih=2.31/rload
        print(f"VIN={v}V: IF indicative {if_approx*1000:.2f}mA; "
              f"hypothetical 50% CTR Ic {available_ic_50pct*1000:.3f}mA; "
              f"R917 source threshold {load_ih*1000:.3f}mA")
    if_9=(9-1.4)/rled
    if_30=(30-1.4)/rled
    assert if_9 < 0.005 and if_30 < 0.005
    r_at_9=(9-1.4)/0.005
    power_r_at_30=(30-1.4)**2/r_at_9
    led_p_at_30=1.4*(30-1.4)/r_at_9
    print(f"To reach IF>=5mA at VIN=9V (ideal Vf=1.4V): R916<={r_at_9:.0f}ohm; "
          f"at 30V resistor dissipates {power_r_at_30:.3f}W, "
          f"LED indicative {led_p_at_30*1000:.1f}mW.")
    assert power_r_at_30>0.5
    print("VERDICT: NOT PROVEN across 9-30V / -40..85C: "
          "minimum CTR not specified for actual 1.1mA IF or hot/cold. "
          "Single resistor change alone is NOT a qualified repair.")
    print("PASS: regression correctly detects missing manufacturer guarantee; "
          "this is NOT an ACC hardware pass.")

if __name__=="__main__":
    verify()
