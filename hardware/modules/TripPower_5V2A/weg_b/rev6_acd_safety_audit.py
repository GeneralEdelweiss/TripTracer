#!/usr/bin/env python3
"""TripPower B independent REV6 A/C/D static hazard gate, stdlib-only.
Manufacturer source values: TI TPS2663 RevG §6.5/8.3.4,
TPS2660 RevG §7.5; ADI LTC4368 Rev C pp2-4.
No claim of 58V transient, DC arc, thermal, manufacturing or live prototype PASS.

Snapshot A KiCad '01_TPS26631_REV6.kicad_sch':
  source branch design/trippower-a, source KiCad blob SHA
  85ca54d0ed41f714ddccff939b77190649076a70.
  R201=100k/R202=12.4k/R203=4.22k 0.1% 25ppm;
  U201 pin7 UVLO_SENSE, pin8 OVP_SENSE; netlist source
  tools/check_trippower_a_rev6_native_netlist.py on A branch.
Supports --a-schematic FILE to inspect actual independent branch source
locally; CI tests source snapshot constants without claiming native A ERC.
"""
from __future__ import annotations
import argparse
import json
import math
import re

A_SCHEMATIC_BLOB="85ca54d0ed41f714ddccff939b77190649076a70"
TI2663="https://www.ti.com/lit/ds/symlink/tps2663.pdf"
TI2660="https://www.ti.com/lit/ds/symlink/tps2660.pdf"
ADI4368="https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4368.pdf"
FUSE997="https://www.littelfuse.com/de/assetdocs/littelfuse-datasheet-997-mini58v?assetguid=f4bf5724-5a40-4a44-8f08-c52ae959a5ef"
HOLDER="https://www.littelfuse.com/de/products/fuses-overcurrent-protection/fuse-holders-fuse-blocks-accessories/fuse-holders/in-line-fuse-holders/mini-fhm/0fhm0001zxj-red"

def actual_A_values_from_sheet(sheet):
    """Use actual KiCad *placed* component instance reference and nearby value.
    No text-label-only or native netlist continuity claim: netlist independently
    verified by A branch's KiCad-10 CI and pin checker."""
    result={}
    for ref in ("R201","R202","R203"):
        m=re.search(r'\(property "Reference" "'+ref+r'"[^\n]*\)\s*\(property "Value" "([^"]+)"',sheet)
        if not m: raise ValueError("A placed "+ref+" value not found")
        value=m.group(1)
        parsed=re.search(r'([0-9]+(?:\.[0-9]+)?)([kM]?)',value)
        if not parsed:raise ValueError("A placed "+ref+" numeric value not found")
        result[ref]={"raw":value,"ohm":float(parsed.group(1))*{"":1,"k":1e3,"M":1e6}[parsed.group(2)]}
    if "TPS26631PWPR" not in sheet:raise ValueError("Unexpected A controller")
    return result

def A_three_resistor_bounds(r1=100e3,r2=12.4e3,r3=4.22e3,relative=.002125,
                           leak_a=150e-9):
    """Independent resistor R1 above UVLO, R2 UVLO->OVP, R3 OVP->GND.
    At OV pin, leakage through R1+R2 (OV) and R1 (UV).
    For VOV rise use TI 1.176..1.224V, fall TI 1.090..1.150V.
    Independent worst signs assumed; ±relative includes 0.1% + 25ppm/K×45K.
    Does NOT cover PCB leakage, resistor changes beyond stated envelope.
    """
    def corner(v,sgn):
        rr1=r1*(1+sgn*relative)
        rr2=r2*(1+sgn*relative)
        rr3=r3*(1-sgn*relative)
        return v*(1+(rr1+rr2)/rr3)+sgn*leak_a*(2*rr1+rr2)
    rise=(corner(1.176,-1),corner(1.224,1))
    fall=(corner(1.090,-1),corner(1.150,1))
    uv_nom=1.2*(1+r1/(r2+r3))
    # If board's OVP PIN is grounded w/o UVLO divider redesign:
    uv_with_ovp_pin_strapped_ground=1.2*(1+r1/r2)
    return {"rising_v":rise,"falling_v":fall,
            "rising_within_32_to_36":rise[0]>32 and rise[1]<=36,
            "restart_at_exactly_32_guaranteed":fall[0]>32,
            "uvlo_rising_nominal_v":uv_nom,
            "uvlo_if_factory_ovp_strapped_without_UV_redesign_v":uv_with_ovp_pin_strapped_ground,
            "10v_start_possible_without_uv_redesign_after_grounding_ovp":uv_with_ovp_pin_strapped_ground<=10,
            "schematic_external_OVP_as_drawn":True,
            "dynamic_PGOOD_and_58v_restart_test_proven":False}

def TI26631_factory_OVP():
    """TI factory OVP with OVP=GND. Rising 33.2...35.4, falling
    32.7...35.0 V at IN_SYS; re-enable when VIN_SYS FALLS below
    falling threshold. Incorrect historical reviewer reversed inequality."""
    return {"ovp_pin":"GND selects internal fixed OVP", "rising_v":(33.2,35.4),
            "falling_v":(32.7,35.0),"rising_within_32_to_36":True,
            "restart_at_exactly_32_guaranteed":True,
            "NO_FREE_STRAP_SWAP_WITH_UVLO":True,
            "dynamic_overshoot_and_startup_proven":False}

def simple_divider(rtop,rbot,tol, rise,fall, leakage_a):
    """OVLO sense pin: VIN=Vref*(1+Rtop/Rbot)+Ip*Rtop.
    Input leakage sign worst combined with independent R tolerance."""
    if not 0<=tol<1:raise ValueError("tol")
    def bound(v,sgn):
        a=rtop*(1+sgn*tol)
        b=rbot*(1-sgn*tol)
        return v*(1+a/b)+sgn*leakage_a*a
    vr=(bound(rise[0],-1),bound(rise[1],1))
    vf=(bound(fall[0],-1),bound(fall[1],1))
    return {"rising_v":vr,"falling_v":vf,
            "rising_within_32_to_36":vr[0]>32 and vr[1]<=36,
            "restart_at_exactly_32_guaranteed":vf[0]>32}

def C_cases():
    ca=simple_divider(100e3,3.78e3,.001,(1.176,1.224),(1.09,1.15),150e-9)
    cb=simple_divider(100e3,3.74e3,.001,(1.17,1.225),(1.085,1.125),100e-9)
    return {
       "C_TPS26631_SCHOTTKY_ADJUSTABLE":dict(ca,MPN="TPS26631PWPR",
           "series_Schottky_drop_NOT_guaranteed":True,
           "inverting_32v_restart_meaning":"falling min must EXCEED VIN_after_diode",
           "58v_PIN_operating_headroom_v":2.),
       "C_TPS26631_SCHOTTKY_FACTORY":dict(TI26631_factory_OVP(),
           MPN="TPS26631PWPR",requires_UVLO_independent_redesign":True,
           "reverse_diode_max_vf_at_cold_and_recovery_proven":False),
       "C_TPS26600_BARE_ADJUSTABLE":dict(cb,MPN="TPS26600PWPR",
           "58v_PIN_ABS_headroom_v":4.,"integrated_limit_max_a":2.23,
           "reverse_FET_built_in":True,
           "real_INPUT_pads_safe_with_ringing":False)
    }

def D_LTC4368_bounds(relative=.0025,including_three_pin_leakage=True):
    """A genuine 4-resistor ladder (VIN--R4--SHDN--R3--UV--R2--OV--R1--GND).
    OV input leakage affects sum of R above OV; UV affects R4+R3;
    SHDN affects R4. ADI ±10nA UV & OV, ±15nA SHDN at stated conditions.
    Previous D rev6_limits.py modeled only OV leakage; slightly optimistic.
    0.25% is hypothetical *effective* total resistor tolerance+TCR, NOT
    yet a frozen vendor MPN. PCB leakage also excluded.
    """
    a,b,c,d=(475e3,1500e3,121e3,30.2e3)
    if not 0<=relative<1:raise ValueError("relative")
    def bound(v,sgn):
        x=a*(1+sgn*relative);y=b*(1+sgn*relative)
        z=c*(1+sgn*relative);w=d*(1-sgn*relative)
        leak=10e-9*(x+y+z)
        if including_three_pin_leakage:leak+=10e-9*(x+y)+15e-9*x
        return v*(1+(x+y+z)/w)+sgn*leak
    rising=(bound(.4925,-1),bound(.5075,1))
    falling=(bound(.4925-.032,-1),bound(.5075-.020,1))
    return {"rising_v":rising,"falling_v":falling,
            "rising_within_32_to_36":rising[0]>32 and rising[1]<=36,
            "restart_at_exactly_32_guaranteed":falling[0]>32,
            "margin_36v_at_max_rise_v":36-rising[1],
            "margin_32v_above_worst_fall_v":falling[0]-32,
            "all_three_input_leaks_accounted":including_three_pin_leakage,
            "resistor_tolerance_with_TCR_is_ASSUMED_not_MPN_qualified":True,
            "tested_installed_circuit":False}

def thermals():
    """Tj=T_A+theta*(10W*(1/eta-1)) intentionally extreme all losses
    in IC; ignores copper/inductor, not actual buck thermal qualification."""
    samples=[]
    for eta in (.8,.85,.9):
        loss=10*(1/eta-1)
        samples.append({"assumed_eta":eta,"system_regulator_loss_w":loss,
          "naive_all_loss_in_IC_Rtheta45_CperW_TjAt60_C":60+45*loss,
          "actual_60C_2A_PASS":False})
    return samples

def fault_and_fuse():
    """No fuse installed on TripPower. All three share external vehicle BAT
    and ACC line fuses upstream; optional secondary accessible on TripTracer.
    58V fuse must be tested against V_breaker not nominal at M8."""
    return {
       "TripPower_melt_fuse_count":0,
       "TripPower_fuse_holder_count":0,
       "TripPower_one_time_SMD_fuse_count":0,
       "TripPower_PPTC_required":False,
       "TripPower_optional_PPTC_possible_only_if_58v_hot_Ihold_Itrip_proven":True,
       "vehicle_BAT_ACC_FMAIN_NEAR_SOURCE":"REQUIRED",
       "TripTracer_additional_accessible_device_fuse":"OPTIONAL; DOES NOT COVER UPSTREAM WIRE",
       "candidate_Littelfuse_0997004_WXN":{"VDC":58,"interrupt_A_at_58V":1000,
         "temperature_c":(-40,125),"mfr_open_time_at_2xIn_s":(.15,5.0)},
       "candidate_Littelfuse_holder_0FHM0001ZXJ_RED":{"VDC":58,"temperature_max_c":125},
       "fuse_58Vdc_alone_clears_fault_current_below_In":False,
       "DC_breaker_suitability_when_actual_contact_V_beyond_58V":False,
       "cable_protection_guaranteed_without_I2t_full_clear_and_Cu_capacity":False,
       "PPTC_IS_NOT_VEHICLE_FMAIN":True}

def statuses():
    # PASS refers to documented static vendor logic OR a verified structural
    # design fact, NEVER a system-level field qualification.
    rows=[
    ("R6 input 10-32V part rating","PASS","PASS","PASS","All parts nominal VIN cover; assembly operation untested"),
    ("A exact external OVLO rising 32-36","PASS","OFFEN","OFFEN","A actual divider 100k/12.4k/4.22k static; C variants mixed; D conditional 0.25% precision"),
    ("OVP clears at stable 32V after 58V", "FAIL","OFFEN","OFFEN",
     "A actual falling min <32; C TPS26631 fixed PASS only static, C adjustable A and B FAIL; D PASS only if effective 0.25% is proved"),
    ("36V / 400ms survived after static OVP","OFFEN","OFFEN","OFFEN","All need signal delay and temperature transient"),
    ("58V/350ms actual eFuse VIN pin incl ringing","OFFEN","OFFEN","OFFEN",
     "A/C TPS26631 60V operating /67V abs; C TPS26600 only 62V ABS; D VIN 100V ABS but VOUT/SENSE 80V ABS"),
    ("2A buck at +60C", "OFFEN","OFFEN","OFFEN","Actual PCB efficiency, inductor, output MLCC Ceff & heat"),
    ("safe OFF at +85C ambient","FAIL","OFFEN","OFFEN",
     "A 25-piece native prototype has no ambient85C fail-safe sensor or path; C/D no validated circuit"),
    ("RAW 0.5A selectivity hard short","FAIL","OFFEN","OFFEN","A no own 0.5A current limiter; all must size local RAW wire vs main overcurrent"),
    ("Reverse blocking nominal positive/negative", "OFFEN","OFFEN","OFFEN","A ext FET and B_GATE; C TPS26600 integrated; D 2FET. Need true NET and fault injection"),
    ("USB main 5V / vehicle / RTC no backfeed", "OFFEN","OFFEN","OFFEN","TripTracer mainboard integration not complete"),
    ("FRAM-first and PWR_FAIL", "OFFEN","OFFEN","OFFEN","PG state ≠ hold energy, FRAM atomic firmware not measured"),
    ("No F_MAIN/one-time fuse on TripPower", "PASS","PASS","PASS",
     "Product-level required placement, not proof of external fuse coordination"),
    ("External vehicle F_MAIN and cable proven", "OFFEN","OFFEN","OFFEN",
     "Correct VDC + holder at actual fuse arc voltage; BAT & ACC upstream, no sub-I hold guarantee"),
    ("One shorted internal eFuse/FET safely contained","OFFEN","OFFEN","OFFEN",
     "58V to RAW/5V permitted damage ONLY when hot/cable/backfeed demonstrated harmless")
    ]
    return [{"criterion":r[0],"A":r[1],"C":r[2],"D":r[3],"finding":r[4]} for r in rows]

def report(a_sheet=None):
    av=actual_A_values_from_sheet(a_sheet) if a_sheet else None
    a=A_three_resistor_bounds(*[av[k]["ohm"] for k in ("R201","R202","R203")]) if av else A_three_resistor_bounds()
    return {
       "criterion_of_restart":"OVP clears when VIN FALLS BELOW falling threshold. To guarantee restart at stable32V, WORST_MIN_FALLING must EXCEED32V (not max<=32).",
       "A_schematic_source_path":"hardware/modules/TripPower_REV6_A/01_TPS26631_REV6.kicad_sch",
       "A_schematic_blob_sha":A_SCHEMATIC_BLOB,
       "A_placed_R_values_read":av,
       "A_REV6_actual_external_ovp":a,
       "A_TPS26631_FACTORY_OVP":TI26631_factory_OVP(),
       "C_architecture_subcases":C_cases(),
       "D_LTC4368_all_pin_leak_and_0p25pct":D_LTC4368_bounds(),
       "D_LTC4368_1pct_illustration":D_LTC4368_bounds(.01),
       "buck_thermal_sensitivity":thermals(),
       "component_voltage_bounds":{
         "TPS26631_IN_SYS_operating":60,"TPS26631_IN_SYS_abs":67,
         "TPS26600_IN_abs":62,"LTC4368_VIN_oper":60,
         "LTC4368_VIN_abs":100,"LTC4368_SENSE_VOUT_abs":80,
         "LMR38020_VIN_operating":80},
       "fuse_and_BOM_partition":fault_and_fuse(),
       "A_C_D_status_matrix":statuses(),
       "no_go_if_this_release_proposed":True,
       "actual_field_and_thermal_tests_all_open":True,
       "old_REV5_200v_tests_NOT_REV6_required":True
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--a-schematic",help="Optional exact A KiCad sheet captured from named A blob SHA")
    p.add_argument("--output")
    args=p.parse_args()
    data=report(open(args.a_schematic,encoding="utf8").read() if args.a_schematic else None)
    out=json.dumps(data,indent=2,sort_keys=True)
    if args.output:open(args.output,"w",encoding="utf8").write(out+"\n")
    else:print(out)
