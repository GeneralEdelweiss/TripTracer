#!/usr/bin/env python3
"""Prearmed TLC555 topology model. Not SPICE, lab or a timer tolerance guarantee."""
import json, math, re
from itertools import product
from pathlib import Path

def advance(v, target, resistance, capacitance, dt):
    return target+(v-target)*math.exp(-dt/(resistance*capacitance))

def simulate(acc_fn, hold_fn, usb_only=False):
    vdd=3.3; r=1e6; c=22e-6; clamp=.7; rd=10e3
    vc=0.; out=False; history=[]
    for n in range(45001):
        now=n*.002; acc=acc_fn(now)
        # After 10 ms POR, TI Table 6-1: TRIG LOW sets output independent of THRES.
        if now<.010: out=False
        elif acc: out=True
        elif vc>=2*vdd/3: out=False
        if acc:
            target=(vdd/r+clamp/rd)/(1/r+1/rd)
            vc=advance(vc,target,1/(1/r+1/rd),c,.002)
        elif out: vc=advance(vc,vdd,r,c,.002)
        else: vc=0. # simplified internal DISCH action, not a device timing model
        history.append((now,out and hold_fn(now),vc))
    return history

def at(hist,t):
    return hist[round(t/.002)][1]

def check():
    sch=Path("hardware/kicad/01C_HOLD_TIMER.kicad_sch").read_text(encoding="utf-8")
    for value in ("1M 1% - OFF DEADLINE","22uF 25V X7R 1210 DERATE","10k 1% RC discharge limit"):
        assert value in sch, "recalculate timer after component value change: "+value
    assert 'Reference" "C502"' not in sch
    normal=simulate(lambda t:t<3,lambda t:t>=.5)
    assert all(at(normal,t) for t in (2.9,2.998,3.,3.002,3.01,4.)), "HOLD edge gap"
    assert not at(normal,60), "stuck MCU request bypasses deadline"
    early=simulate(lambda t:t<3,lambda t:.5<=t<4)
    assert at(early,3.5) and not at(early,4.), "MCU cannot release early"
    returned=simulate(lambda t:t<3 or 5<=t<7,lambda t:t>=.5)
    assert all(at(returned,t) for t in (4,5,6,7,7.1,10))
    assert not at(returned,70), "ACC return never times out after second off"
    usb=simulate(lambda t:False,lambda t:True)
    assert not any(row[1] for row in usb), "USB-only requests false HOLD"
    # DC/leakage/threshold sensitivity. 3.3V behavior is not fully bounded by TI's
    # 5V/15V tables; fractions and C-effective range are explicit stress assumptions.
    windows=[]
    for vdd,r,c,vc,frac,leak in product(
            (3.,3.3,3.6),(.99e6,1.01e6),(10e-6,26.4e-6),
            (.5,1.3),(.54,.78),(-80e-9,500e-9)):
        final=vdd-r*leak; threshold=frac*vdd
        assert vc<threshold<final, "RC never reaches threshold under declared envelope"
        windows.append(r*c*math.log((final-vc)/(final-threshold)))
    # Q912 additionally sinks the limited RC reset current and both pull-ups.
    ib=(9-1)/(100e3*1.01)-1/(100e3*.99)
    ic=(3.6-.3)/(10e3*.99)+3.6/(22e3*.99)+3.6/(100e3*.99)
    # Conservative forced gain target 10. VBE/VCE are stress assumptions.
    assert ic/ib<10, ("Q912 drive margin",ic/ib)
    # TRIG high recovers to VDD without the retired second inverter load.
    high_drop=(80e-9+5e-9)/(1/22e3+1/100e3)
    assert high_drop<.01
    result={"status":"PASS topology/state and declared analog sensitivity models only",
        "scenarios":["continuous HOLD at ACC off","early MCU release","stuck-high MCU deadline",
                     "ACC return and second off","USB-only stays unarmed"],
        "sensitivity_corners":len(windows),
        "modeled_min_seconds":min(windows),"modeled_max_seconds":max(windows),
        "nominal_seconds":1e6*22e-6*math.log((3.3-.7)/(3.3-2.2)),
        "q912_forced_gain_target":ic/ib,
        "open_gates":["3.3V full-temperature TLC555 thresholds/leakage",
            "C501 effective capacitance/insulation resistance","clamp drop over temperature",
            "short ACC chatter and waveform bench tests","sensor stuck-low or shorted RC can defeat timer",
            "opto/MCU timing during initialization","no whole-vehicle qualification"]}
    print(json.dumps(result,indent=2))
if __name__=="__main__": check()
