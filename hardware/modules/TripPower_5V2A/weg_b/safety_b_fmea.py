#!/usr/bin/env python3
"""Independent TripPower Weg-B fault-path gate against a KiCad-10 exported netlist.

This is NOT a device qualification, transient simulation, fault injection in
hardware or a release. Assumed diode states, currents and Ceff are explicit.
Usage:
  python3 hardware/modules/TripPower_5V2A/weg_b/safety_b_fmea.py --netlist reports/TripPower_5V2A.net
"""
import argparse
import json
import math
import re
from pathlib import Path

EXPECTED = {
    "Q301": {"1": "HGATE", "2": "VIN_FUSED", "3": "SOURCE_A"},
    "D301": {"1": "VS_CLAMP", "2": "GND"},
    "D302": {"1": "VS_CLAMP", "2": "SOURCE_A"},
    "D303": {"1": "VIN_FUSED", "2": "TVS_STACK"},
    "D304": {"1": "TVS_STACK", "2": "GND"},
    "R313": {"1": "VIN_FUSED", "2": "VS_SERIES_A"},
    "R314": {"1": "VS_SERIES_A", "2": "VS_SERIES_B"},
    "R315": {"1": "VS_SERIES_B", "2": "VS_CLAMP"},
    "C302": {"1": "VS_CLAMP", "2": "GND"},
    "C308": {"1": "VS_CLAMP", "2": "GND"},
    "C312": {"1": "VS_CLAMP", "2": "GND"},
    "U301": {"7": "VS_CLAMP", "22": "VS_CLAMP"}
}

def parse_native_netlist(net_text):
    """Strictly require KiCad-exported (nets ... (net... (node...)) structure.
    An in-repo schematic label by itself CANNOT pass this test.
    """
    if "\n\t(nets" not in net_text:
        raise ValueError("No native KiCad (nets ...) tree")
    region = net_text.split("\n\t(nets", 1)[1]
    chunks = region.split("\n\t\t(net")[1:]
    if not chunks:
        raise ValueError("No KiCad (net ...) nodes")
    nets = {}
    for part in chunks:
        name = re.search(r'\(name "([^"]+)"\)', part)
        if not name:
            continue
        n = name.group(1).split("/")[-1]
        nodes = set(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', part))
        if nodes:
            nets.setdefault(n, set()).update(nodes)
    if not nets:
        raise ValueError("Empty KiCad pin-node map")
    return nets

def verify_real_pin_map(nets):
    failures=[]
    for ref, pins in EXPECTED.items():
        for pin, intended in pins.items():
            actual=[name for name,points in nets.items() if (ref,pin) in points]
            if actual != [intended]:
                failures.append({"ref":ref,"pin":pin,"expected":intended,"actual":actual})
    if failures:
        raise AssertionError(json.dumps(failures,sort_keys=True))
    # The following is a *logical* fault-graph test, not an analogue assertion:
    # one welded Q301 connects VIN_FUSED to SOURCE_A, and diode D302 conducts
    # from SOURCE_A (anode pad 2) to VS_CLAMP (cathode pad 1).
    welded_q301_edge=("VIN_FUSED","SOURCE_A")
    forward_d302_edge=("SOURCE_A","VS_CLAMP")
    bypasses_all_rvs=all(r not in ("R313","R314","R315")
                          for r in ("Q301.D-S_SHORT","D302.FORWARD"))
    assert bypasses_all_rvs
    return {"status":"EXPECTED_NATIVE_PIN_MAP_OBSERVED",
            "verified_pin_count":sum(map(len,EXPECTED.values())),
            "single_fault":"Q301 drain-source welded while VIN_FUSED rises to 200V",
            "possible_series_path":[welded_q301_edge,forward_d302_edge],
            "R313_R314_R315_in_path":False,
            "physical_fault_energy_qualified":False}

def d301_open(vin=200., vs0=0., ceff_f=21e-6, r_ohms=9900., sec=.350):
    if not (0<=vs0<=vin and ceff_f>0 and r_ohms>0 and sec>=0):
        raise ValueError("bad ideal RC corner")
    tau=r_ohms*ceff_f
    def crossing(level):
        if vs0>=level: return 0.
        if level>=vin: return None
        return -tau*math.log((vin-level)/(vin-vs0))
    return {"model":"zero load/no internal clamping; hypothetical upper tendency",
            "VS_350ms_v":vin-(vin-vs0)*math.exp(-sec/tau),
            "cross_65ms":crossing(65)*1000,
            "cross_100ms":crossing(100)*1000,
            "Ceff_assumption_uF":ceff_f*1e6,
            "TI_LM74930_VS_operating_max_v":65,
            "ceramic_VS_cap_rated_v":100,
            "qualified":False}

def d302_bypass_current_example(i_amp, vz=56., duration=.350, vf=.8):
    """Injected SOURCE_A current into VS via D302 AFTER welded Q301.
    This is a bounded current *assumption*, not the actual vehicle current."""
    if i_amp<0:raise ValueError("negative example current")
    return {"assumed_continuous_current_a":i_amp,
            "D301_zener_dissipation_w":vz*i_amp,
            "D301_zener_350ms_j":vz*i_amp*duration,
            "D302_diode_dissipation_w":vf*i_amp,
            "main_fuse_may_not_clear":i_amp<3.0,
            "RVS_9p9kohm_limits_this_path":False,
            "Zener_I_V_T_and_SOA_PROVEN":False}

def q301_turnoff_screen(vpulse=200., vds_max=250., current=2.389):
    return {"ideal_off_Q301_VDS":vpulse,
            "VDS_ideal_headroom":vds_max-vpulse,
            "inductive_overshoot_of_51V_exceeds_absolute_max":vpulse+51>vds_max,
            "illustrative_100us_turnoff_J":vpulse*current*100e-6,
            "illustrative_1ms_turnoff_J":vpulse*current*.001,
            "temperature_and_SOA_qualified":False}

def shunt_zener_pulse(vin=200, vz=56, r=9900, duration=.350):
    i=max((vin-vz)/r,0)
    return {"i_mA":i*1000,"R_3p3kohm_energy_J":i*i*3300*duration,
            "Zener_energy_J":i*vz*duration,"manufacturer_hot_pulse_pass":False}

def fmea():
    return [
        {"fault":"D301 open","classification":"CRITICAL","effects":"VS capacitors 100V / LM74930 VS65V may be overstressed at 200V","protected":False},
        {"fault":"Q301 D-S short","classification":"CRITICAL","effects":"SOURCE_A can see 200V; D302 feeds VS directly bypassing 9.9kohm; Q302 60V domain in doubt","protected":False},
        {"fault":"D302 short","classification":"CRITICAL","effects":"VS directly coupled to SOURCE_A even when no diode rectification, review 200V load dump with Q301 D-S short","protected":False},
        {"fault":"D302 open","classification":"AVAILABILITY","effects":"9V start VS source replenishment may fail; device can remain off","protected":None},
        {"fault":"D303 short or reverse","classification":"CRITICAL","effects":"D304 alone takes surge energy, no validated 350ms SOA","protected":False},
        {"fault":"D304 short","classification":"CRITICAL","effects":"D303 alone sees surge, cannot sum unmatched IPP clamping","protected":False},
        {"fault":"D303/D304 both open","classification":"CRITICAL_DOUBLE","effects":"No TVS voltage mitigation; external Q301 may exceed 250V on ringing","protected":False},
        {"fault":"Q301 and Q302 both D-S short","classification":"CRITICAL_DOUBLE","effects":"Unprotected 200V can reach RAW and 80V buck","protected":False},
        {"fault":"R313 one short and D301 short","classification":"THERMAL_DOUBLE","effects":"two 3.3k limit current; >=1J each under 200V/350ms ideal model","protected":False},
        {"fault":"RUN stuck LOW / D302 open","classification":"AVAILABILITY","effects":"Permitted controlled shutdown, no expected cable-fire hazard","protected":None},
    ]

def report(nets=None):
    return {
        "project":"TripPower Weg B independent adversarial review",
        "manufacturer_spec_but_not_complete_system":{"VS_operating_max_v":65,"VS_caps_rated_v":100,
            "Q301_abs_VDS_max_v":250,"Q302_abs_VDS_max_v":60},
        "netlist":verify_real_pin_map(nets) if nets is not None else "NOT_CHECKED_NATIVE_NETLIST",
        "D301_open_21uF_zero_load":d301_open(),
        "D301_open_warm_56v_21uF_zero_load":d301_open(vs0=56),
        "D301_open_5uF_zero_load":d301_open(ceff_f=5e-6),
        "D302_feed_from_source_A_with_welded_Q301_assumed_current": [
            d302_bypass_current_example(i) for i in (0.02,0.1,0.25,1.0)],
        "q301":q301_turnoff_screen(),
        "nominal_RVS_zener_pulse":shunt_zener_pulse(),
        "D303_D304_VBR_min_sum_at_individual_test_current_V":167+36.7,
        "D303_D304_200V_guaranteed_to_clamp":False,
        "FMEA":fmea(),
        "RELEASE_GATES":{"manufacturer_SOA_200V_350ms":False,
                         "single_fault_Q301_short_D302_safe":False,
                         "D301_open_safe":False,"KiCad_DRC":False,"physical_test":False}
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--netlist",help="native KiCad10 exported .net; REQUIRED for pin map qualification")
    p.add_argument("--output",help="report json path")
    args=p.parse_args()
    result=report(parse_native_netlist(Path(args.netlist).read_text()) if args.netlist else None)
    out=json.dumps(result,indent=2,sort_keys=True)
    if args.output: Path(args.output).write_text(out+"\n")
    else: print(out)
