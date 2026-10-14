#!/usr/bin/env python3
"""ACC U912 retirement regression, two-transistor nominal drive calculations.
NOT a manufacturer hot/cold or hardware test: flags unqualified cases explicitly.
"""
from pathlib import Path

s=(Path(__file__).resolve().parents[1]/"hardware/kicad/01H_ACC_HOLD_GATE.kicad_sch").read_text()
assert '(property "Reference" "U912"' not in s, "old low-current CTR-dependent optocoupler still active"
assert all(f'(property "Reference" "{ref}"' in s for ref in
           ("Q912","Q913","R916","R917","R918","R919","R920","R921"))
assert '"100k ACC NPN base feed"' in s
for vin in (9,12,24,30):
    # Vbe=.7V nominal, ideal resistor (not a guaranteed temperature bound).
    ib1=max(0,(vin-0.7)/100e3-0.7/100e3)
    ic1=(3.3-.2)/22e3
    if vin>=9:
        assert ib1 > ic1/10
    print(f"ACC={vin}V: Q912 IB={ib1*1e6:.1f}uA, IC required={ic1*1e6:.1f}uA, forced-beta<={ic1/ib1:.2f}")
# Q913 holds output low when ACC absent, giving falling edge.
ib2=(3.3-.7)/(22e3+22e3)
ic2=3.3/10e3
print(f"ACC OFF: Q913 nominal IB={ib2*1e6:.1f}uA, IC~{ic2*1e6:.1f}uA, forced-beta~{ic2/ib2:.1f}")
assert ib2>ic2/10
print("PASS: obsolete U912 removed; nominal two-NPN current drive sufficient under assumed VBE/hFE.")
print("NOT PROVEN: worst-case hFE, VBE/leakage at -40..85C, input clamps, GPIO timer, ECU electrical testing.")
