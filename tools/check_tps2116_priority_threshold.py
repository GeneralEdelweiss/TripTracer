#!/usr/bin/env python3
"""TPS2116 manufacturer-limit PR1 threshold, with -40..105C VREF and pin leakage.

TI TPS2116 Rev A: VREF=0.92..1.08V (-40..105 C), IPR1<=0.1uA.
These are component limits, not an end-to-end brownout/ISO guarantee.
"""
from pathlib import Path

SCHEMATIC = Path(__file__).resolve().parents[1]/"hardware/kicad/03_3V3_USB.kicad_sch"
TOP, BOTTOM = 100_000.0, 30_100.0

def threshold(vref, top, bottom, leakage):
    # KCL PR1: (VIN-VPR1)/top = VPR1/bottom + I_leak.
    return vref*(1+top/bottom) + leakage*top

def run():
    s=SCHEMATIC.read_text()
    for p in ('(property "Reference" "R308"', '(property "Reference" "R309"',
              '(property "Value" "100k 1% PR1_TOP"',
              '(property "Value" "30.1k 1% PR1_BOTTOM"',
              '(global_label "MUX_PRI1_SENSE"'):
        assert p in s, f"missing PR1 divider feature: {p}"
    minimum=threshold(.92, TOP*.99, BOTTOM*1.01, -.1e-6)
    nominal=threshold(1.0,TOP,BOTTOM,0)
    maximum=threshold(1.08, TOP*1.01, BOTTOM*.99, .1e-6)
    print(f"PR1 vehicle rail switch threshold: min={minimum:.3f}V, typical={nominal:.3f}V, max={maximum:.3f}V")
    assert 3.8 < minimum < 4.1
    assert 4.2 < nominal < 4.4
    assert 4.6 < maximum < 4.8
    assert maximum < 4.9, "Nominal 5V vehicle rail may never be selected"
    print(f"VIN1=5.00V PR1 nominal={5*BOTTOM/(TOP+BOTTOM):.3f}V vs TI worst VREF=1.08V")
    print(f"Divider current at VIN1=5V ~{5/(TOP+BOTTOM)*1e6:.1f}uA, only when buck is on.")
    print("PASS: TI VREF/temp/leakage resistor-corner budget; native netlist pin4 routing test separately required")
    print("OPEN: buck tolerance/ripple, real USB switchover dynamics, system 3V3 brownout under load")
if __name__=="__main__":
    run()
