#!/usr/bin/env python3
"""Vehicle harness / 9V constant-power envelope. Assumptions, not hardware approval."""
import json
import math
import re
from itertools import product
from pathlib import Path
from check_kicad_custom_pinouts import block

ROOT=Path(__file__).resolve().parents[1]
KICAD=ROOT/"hardware"/"kicad"

def solve_input(source_v, drop_v, loop_ohm, output_w, efficiency=.8, bias_a=.010):
    """Stable high-voltage solution of I=Pbuck/(eta*VIN)+Ibias."""
    a=source_v-drop_v-loop_ohm*bias_a
    if loop_ohm == 0:
        return a, output_w/(efficiency*a)+bias_a
    disc=a*a-4*loop_ohm*output_w/efficiency
    if disc < 0:
        raise ValueError("constant-power collapse")
    vin=(a+math.sqrt(disc))/2
    return vin, output_w/(efficiency*vin)+bias_a

def en_min(vin, top=24900, source_drop=1.0):
    rt=top*1.01
    rb=10000*.99
    return (vin-source_drop)*rb/(rt+rb)-20e-6/(1/rt+1/rb)

def source_fuse_check():
    sch=(KICAD/"01G_SIMPLE_INPUT.kicad_sch").read_text(encoding="utf-8")
    labels={}
    for m in re.finditer(r'\(global_label "',sch):
        b=block(sch[m.start():], '(global_label "')
        name=re.search(r'^\(global_label "([^"]+)"',b).group(1)
        xy=tuple(map(float,re.search(r'\(at ([\d.-]+) ([\d.-]+) ',b).groups()))
        labels.setdefault(xy,set()).add(name)
    graph={}
    for m in re.finditer(r'\(wire \(pts',sch):
        b=block(sch[m.start():], '(wire (pts')
        pts=[tuple(map(float,p)) for p in re.findall(r'\(xy ([\d.-]+) ([\d.-]+)\)',b)]
        if len(pts)==2:
            graph.setdefault(pts[0],set()).add(pts[1])
            graph.setdefault(pts[1],set()).add(pts[0])
    def names_at(start):
        todo=[start]; seen=set(); result=set()
        while todo:
            p=todo.pop()
            if p in seen: continue
            seen.add(p); result.update(labels.get(p,set())); todo.extend(graph.get(p,set())-seen)
        return result
    expected={"F901":("0997003.WXN 3A 58V EXTERN","VEHICLE_BAT_RAW","BAT_INPUT_FUSED_UNPROTECTED_TVS"),
              "F902":("0997002.WXN 2A 58V EXTERN","VEHICLE_ACC_RAW","ACC_PROTECTED_IN")}
    seen=set()
    for m in re.finditer(re.escape('(symbol (lib_id "TripTracer_V1:OFFBOARD_FUSE"'),sch):
        b=block(sch[m.start():], '(symbol (lib_id')
        ref=re.search(r'\(property "Reference" "([^"]+)"',b).group(1)
        value,src,dst=expected[ref]
        assert '(on_board no)' in b and '(property "Footprint" ""' in b
        assert '(property "Value" "'+value+'"' in b
        x,y,angle=map(float,re.search(r'\(at ([\d.-]+) ([\d.-]+) ([\d.-]+)\)',b).groups())
        assert angle==0
        assert names_at((round(x-7.62,2),y))=={src}, (ref,"source")
        assert names_at((round(x+7.62,2),y))=={dst}, (ref,"output")
        seen.add(ref)
    assert seen==set(expected)
    return sorted(seen)

def check():
    h=(KICAD/"01H_ACC_HOLD_GATE.kicad_sch").read_text(encoding="utf-8")
    for value in ("24.9k 1% VIN LIMIT","24.9k 1% HOLD VIN","154R 1% HOLD LED"):
        assert value in h, "requalify after value change: "+value
    source_refs=source_fuse_check()
    rows=[]
    for source,drop,loop,power,eta in product((9.,12.,24.,30.),(.7,1.15,1.5),(0.,.175,.350),(0.,2.5,5.,10.),(.8,.9)):
        vin,current=solve_input(source,drop,loop,power,eta)
        rows.append(dict(source_V=source,diode_drop_V=drop,loop_ohm=loop,load_W=power,efficiency=eta,
                         vin_V=vin,current_A=current,diode_W=drop*current,harness_W=current*current*loop,
                         hold_en_min_V=en_min(vin)))
    worst_i=max(rows,key=lambda r:r["current_A"])
    worst_en=min(rows,key=lambda r:r["hold_en_min_V"])
    assert worst_i["current_A"] < 2.1 # typical3A fuse interpolation at70C, NOT guaranteed current rating
    assert worst_en["hold_en_min_V"] > 1.4
    old_en=en_min(worst_en["vin_V"],30100)
    assert old_en < 1.4, "harness regression no longer demonstrates original defect"
    # TI VOH>=2.3V at3V/24mA. VF<=1.5V is a declared opto allowance,
    # not a guaranteed full-temperature maximum. LED-short current stays below24mA.
    led_min=(2.3-1.5)/(154*1.01)
    led_max=3.6/(154*.99)
    assert led_min>=.005 and led_max<.024
    led_r_short_w=3.6**2/(154*.99)
    assert led_r_short_w<.25
    wire_loop_70=.0175*(2*2)/.5*(1+.00393*(70-20))
    # Illustrative adiabatic Cu calculation; not an insulation/ampacity certificate.
    area=.5e-6; rho=1.75e-8; alpha=.00393
    wire_i2t=area**2*8960*385/(rho*alpha)*math.log((1+alpha*(105-20))/(1+alpha*(70-20)))
    fuse_points={}
    for name,rating in (("BAT_3A",3),("ACC_2A",2)):
        fuse_points[name]={str(mult):dict(current_A=rating*mult,max_s=seconds,
              i2t_A2s=(rating*mult)**2*seconds) for mult,seconds in ((2,5),(3.5,.5),(6,.1))}
        assert max(x["i2t_A2s"] for x in fuse_points[name].values())<wire_i2t
    thermal=[]
    for theta in (20.,30.,45.,60.):
        for drop in (1.15,1.5):
            current=(125-70)/(theta*drop)
            vin=9-drop-current*.35
            output=max(0.,.8*vin*max(0,current-.010))
            thermal.append(dict(assumed_theta_JA_K_W=theta,assumed_Vf_V=drop,
                thermal_only_5V_ceiling_A=output/5,system_ceiling_A=min(2.,output/5),design_Tj_C=125,ambient_C=70))
    max_pd=max(r["diode_W"] for r in rows)
    report=dict(status="PASS electrical engineering envelope and external-fuse source graph; no vehicle release",
      cases=len(rows),worst_current=worst_i,worst_hold=worst_en,previous_30k1_hold_V=old_en,
      LED=dict(min_A_assuming_Vf_le_1p5=led_min,max_A_even_LED_short=led_max,
        series_resistor_short_W=led_r_short_w,CTR_temperature_current_transfer="not guaranteed by this model"),
      harness=dict(copper_mm2=.5,max_oneway_m=2,assumed_total_loop_budget_ohm=.350,
        calculated_wire_loop_70C_ohm=wire_loop_70,remaining_fuse_contacts_budget_ohm=.350-wire_loop_70,
        required_verified_wire_ampacity_A_at70C=5,source_checked_offboard_refs=source_refs),
      fuse_points=fuse_points,wire_illustrative_70_to105C_adiabatic_i2t_A2s=wire_i2t,
      diode_thermal=dict(max_model_dissipation_W=max_pd,required_theta_JA_for_125C_at70C_K_W=(125-70)/max_pd,
          theta_JT_datasheet_typ_K_W=10,theta_JA_actual="unknown",derating_sensitivities=thermal),
      open_gates=["TVS5800 supplier/MOQ remains blocked; no unqualified conventional substitute fitted",
        "opto cold/hot Vf and CTR plus actual AND loaded output voltage",
        "measured S5MC terminal/junction heat and real efficiency at9V/full load",
        "fuse70C derating is typical; outside70C installation needs review",
        "above600% fuse current, get maximum total clearing I2t or measure; typ I2t is not a bound",
        "holder, M8, crimps, PCB traces and cable insulation fault qualification",
        "actual terminal amplitude<=58V and prospective current<=1kA before fuse58V/1kA credit",
        "TestA202V and vehicle transient/short-circuit tests remain unmet"])
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    check()
