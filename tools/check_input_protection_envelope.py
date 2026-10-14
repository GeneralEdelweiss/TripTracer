#!/usr/bin/env python3
"""Source-bound input envelope and symbol/land-pattern checks; NOT ISO or hardware approval."""
import json
import math
import re
from pathlib import Path
from check_kicad_custom_pinouts import block

ROOT = Path(__file__).resolve().parents[1] / "hardware" / "kicad"

def check():
    lib = (ROOT / "TripTracer_V1.kicad_sym").read_text(encoding="utf-8")
    sch = (ROOT / "01G_SIMPLE_INPUT.kicad_sch").read_text(encoding="utf-8")
    expected = {
        "TVS5800_VEB": sorted([("GND",str(n)) for n in (1,2,3)] +
                              [("IN",str(n)) for n in (4,5,6)]),
        "S5MC_SMC": [("A","2"),("K","1")],
    }
    for name, pins in expected.items():
        for text, full in ((lib,name),(sch,"TripTracer_V1:"+name)):
            sym = block(text, '(symbol "'+full+'"')
            actual = re.findall(r'\(pin passive line.*?\(name "([^"]+)".*?\(number "([^"]+)"',sym,re.S)
            assert sorted(actual) == pins, (full,actual)
    land = {
        "D_TVS5800_VEB0006A": {1:(-.75,-.5,.5,.2),2:(-.75,0,.5,.2),3:(-.75,.5,.5,.2),
                              4:(.75,.5,.5,.2),5:(.75,0,.5,.2),6:(.75,-.5,.5,.2)},
        "D_S5MC_SMC": {1:(-3.45,0,2.5,3.3),2:(3.45,0,2.5,3.3)},
    }
    for name, pads in land.items():
        text=(ROOT / "Tripmaster.pretty" / (name+".kicad_mod")).read_text(encoding="utf-8")
        actual={}
        for n,x,y,w,h in re.findall(r'\(pad "(\d+)" smd roundrect \(at ([\d.-]+) ([\d.-]+)\) \(size ([\d.-]+) ([\d.-]+)\)',text):
            assert int(n) not in actual, (name,"duplicate pad",n)
            actual[int(n)]=tuple(map(float,(x,y,w,h)))
        assert actual.keys() == pads.keys(), (name,actual)
        for n, values in pads.items():
            assert all(math.isclose(a,b,abs_tol=1e-6) for a,b in zip(actual[n],values)), (name,n,actual[n])
    buck=(ROOT/"02_5V_Buck.kicad_sch").read_text(encoding="utf-8")
    assert "4.7uF 100V X7R" in buck and "100nF 100V X7R HF" in buck
    # Table6.6 leakage maxima, NOT typical figures. TestB scope is Vbus<=58V.
    rows=[]
    for temp,leak in ((27,300e-9),(85,1200e-9),(105,2400e-9)):
        power=58*leak
        rows.append(dict(temperature_C=temp,max_leak_A=leak,power_W=power,energy_350ms_J=power*.350))
    # Single specified short-pulse point, initially unbiased and at27C.
    clamp_margin=80-75
    assert clamp_margin == 5 and 600+80 < 1000
    # Counterexample: a TVS below the central clamp can deactivate that clamp.
    # Ideal40V local clamp is an explanatory bound, NOT a TVS V-I simulation.
    current=(174-40-.8)/(1+.1)
    bus=40+.8+.1*current
    assert bus < 58
    result=dict(
        status="PASS source-bound design and pad checks; no hardware or ISO qualification",
        test_B_scope="terminal BAT never exceeds58V; no58V-Thevenin source assumption",
        clamp_20A_8_20us_27C_initially_0V_margin_to_80V_V=clamp_margin,
        tvs_leakage_cases=rows,
        negative_pulse_static_rectifier_margin_V=1000-(600+80),
        old_ideal40V_clamp_counterexample=dict(generator_V=174,Ri_ohm=1,line_R_ohm=.1,
            current_A=current,bus_V=bus,central58V_clamp="inactive"),
        qualification_gates=["terminal waveform/tolerance and bias-dependent overshoot",
            "hot/cold clamp at actual ISO7637 waveforms;25A8/20us is not350ms",
            "S5MC reverse recovery, forward pulse and inrush; BAT/ACC external fuse coordination",
            "PCB parasitics and component/trace temperatures at10W load",
            "TVS5800 procurement: TI/DigiKey currently no confirmed stock",
            "TestA202V/350ms remains unmet; this clamp cannot absorb that event"])
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    check()
