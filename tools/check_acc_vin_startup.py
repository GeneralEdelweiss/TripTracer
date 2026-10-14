#!/usr/bin/env python3
"""DC design envelope only. BJT temperature/dynamic bounds remain bench gates."""
from itertools import product
import json
from pathlib import Path
def check():
    sch=Path("hardware/kicad/01H_ACC_HOLD_GATE.kicad_sch").read_text(encoding="utf-8")
    for value in ("33k 1% VIN LIMIT","10k 1% EN OFF","33k 1% HOLD VIN",
                  "10k 1% 0.5W ACC","4.7k 1%","10k 1% 0.5W","2.2k 1% E-B OFF"):
        assert value in sch, "requalify envelope after value change: "+value
    rows=[]
    # Explicit engineering stress assumptions, NOT guaranteed device limits:
    # VBE<=1V, NPN VCE<=0.3V, PNP VCE<=0.5V, opto VCE<=1V,
    # EN sink leakage<=20uA; forced beta target<=10. No model of transient charge.
    for acc,vin in product((9.,12.,24.,30.),(8.2,11.2,23.2,29.2)):
        ib_n=(acc-1)/(10000*1.01)-1/(4700*.99)
        ic_n=(vin-1-.3)/(10000*.99)
        ib_p=(vin-1-.3)/(10000*1.01)-1/(2200*.99)
        assert ib_n>0 and ib_p>0
        assert ic_n/ib_n<10, (acc,vin,"insufficient NPN drive")
        en=(vin-.5)*(10000*.99)/(33000*1.01+10000*.99)-20e-6/(1/(33000*1.01)+1/(10000*.99))
        hold=(vin-1)*(10000*.99)/(33000*1.01+10000*.99)-20e-6/(1/(33000*1.01)+1/(10000*.99))
        assert min(en,hold)>1.4, (acc,vin,en,hold)
        assert en<vin and hold<vin
        assert en/(10000*.99)<10*ib_p, "insufficient PNP drive"
        rows.append(dict(acc=acc,vin=vin,start_en_min=en,hold_en_min=hold,forced_beta_n=ic_n/ib_n))
    # At VIN=0 both EN energy sources are absent. ACC is on a separate NPN base;
    # no linear ACC divider into EN exists. Exact topology is checked from native netlist.
    # Example leakage envelope: 50uA PNP + 1uA opto dark current into 10k pull-down.
    off_en=51e-6*10000*1.01
    assert off_en<.95
    assert (30-1)**2/(10000*.99)<.5 # R923/R922 0.5W required, derating still apply
    print(json.dumps({"status":"PASS analytical DC envelope only; NOT temperature or transient qualification",
        "corners":len(rows),"min_start_en":min(r["start_en_min"] for r in rows),
        "min_hold_en":min(r["hold_en_min"] for r in rows),"off_en_assuming_51uA":off_en,
        "vin_zero_acc_live":"no passive ACC-to-EN path, confirmed separately by native netlist",
        "unverified":["-40..125C gain/leakage","ACC-off transfer timing","VIN collapse capacitive injection",
                      "reverse inputs and ISO pulses","real USB reverse current"]},indent=2))
if __name__=="__main__": check()
