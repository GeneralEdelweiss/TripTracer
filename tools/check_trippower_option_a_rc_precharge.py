#!/usr/bin/env python3
"""TripPower option A: conditional capacitor/EN RC transient sensitivity screen.

NOT SPICE, NOT LM74930 silicon behavior and NOT a pass of 9-V start.
The unvalidated current draw of the LM74930 during CAP pump activity can
make the actual 9-V behavior differ strongly from this rectangular envelope.
"""
import json
from pathlib import Path

BASE=Path("hardware/modules/TripPower_5V2A")
sch=(BASE/"01_Protection_LM74930.kicad_sch").read_text(encoding="utf-8")
d=json.loads((BASE/"lm74930_design_v1.json").read_text(encoding="utf-8"))
for ref, part in (("C308","EEE-TG2A100P"),("C309","12105C106K4T2A"),
                  ("R313","CRCW25123K30FKEGHP"),("C303","C1206C474K1RECAUTO7210")):
    assert f'(property "Reference" "{ref}"' in sch, f"missing {ref}"
    assert part in sch, f"missing manufacturer MPN {part}"
assert "0R POPULATE FOR ALWAYS_ON" in sch
assert "VIN_PROTECTED_UNFUSED" in sch
assert "10uF 100V VS STARTUP RESERVOIR WIP" in sch
assert "10uF 50V EN DELAY WIP" in sch
assert '(at 405.13 350.52 0) (unit 1) (in_bom yes) (on_board yes) (dnp yes)' in sch, "Historical RC C309 must stay DNP in current RESET design"
assert d["load_dump_design_target_v"] == 202

RVS=3*3300.0
R_AUTO_TOP=100000.
R_EN_DOWN=100000.
IQ_OFF_MAX=5.e-6  # TI test EN=0; not a measured full PCB off draw
LEAK_RESERVOIR_MAX=10.e-6  # 10uF/100V Panasonic catalogue max at RATED V
IQ_ON_SENSITIVITY=780.e-6 # TI 12-V operating IQ(max), NOT startup bound
CAP_F=470.e-9
CAP_UVLO_MAX=7.9
PUMP_CAP_OUT_I_MIN=1.3e-3 # vs>=6 V / special TI test, not input draw
DRIVER_DELAY_MODEL_S=175.e-6 # TI typical fixed time, not guaranteed
EN_ON_WORST=1.05
EN_OFF_HYP=0.70
TIME_STEP_S=20.e-6

def screen(vin_v, cvs_uf, cen_uf, pump_input_extra_ma):
    # Algebraic two-node RC forward Euler with V(EN) approx 0 current.
    # Once EN on, rectangular IQ plus assumed extra charge-pump INPUT draw;
    # actual pump input current/efficiency and input behavior are unknown.
    # Q301 / D302 ideal instantaneous source support AFTER CAP UVLO.
    cvs=cvs_uf*1e-6
    cen=cen_uf*1e-6
    vs=en=vcap=0.
    t_en=t_turn=None
    initial_vs=minimum_vs=0.
    fail=None
    pump_gate_ready=None
    max_s=1.5
    for idx in range(int(max_s/TIME_STEP_S)):
        t=idx*TIME_STEP_S
        enabled=en>=EN_ON_WORST
        if enabled and t_en is None:
            t_en=t
            initial_vs=vs
            minimum_vs=vs
        i_top=(vs-en)/R_AUTO_TOP
        i_series=(vin_v-vs)/RVS
        i_on=IQ_ON_SENSITIVITY+pump_input_extra_ma*1e-3
        i_controller=IQ_OFF_MAX if t_en is None else i_on
        dvdt_vs=(i_series-i_top-i_controller-LEAK_RESERVOIR_MAX)/cvs
        dvdt_en=(i_top-en/R_EN_DOWN)/cen
        vs=max(0.,vs+dvdt_vs*TIME_STEP_S)
        en=max(0.,en+dvdt_en*TIME_STEP_S)
        if t_en is not None and t_turn is None:
            minimum_vs=min(minimum_vs,vs)
            if vs<6.0 and fail is None:
                fail="VS_BELOW_6V_DURING_PUMP__TI_1P3MA_SPEC_NOT_APPLICABLE"
            if en<EN_OFF_HYP and fail is None:
                fail="EN_FALLING_DURING_CAP_CHARGE__TRANSIENT_NOT_SOLVED"
            # Accumulate CAP charge only while the external EN-request is on.
            # This is a simplified *CAP output* charging rate and ignores
            # variations in VCAP, temperature, efficiency and A voltage.
            if pump_gate_ready is None:
                vcap+=PUMP_CAP_OUT_I_MIN*TIME_STEP_S/CAP_F
                if vcap>=CAP_UVLO_MAX:
                    pump_gate_ready=t
            elif t>=pump_gate_ready+DRIVER_DELAY_MODEL_S:
                t_turn=t
                break
    return {
       "vin_v":vin_v,
       "CVS_effective_assumed_uF":cvs_uf,
       "CEN_effective_assumed_uF":cen_uf,
       "VS_pump_INPUT_extra_assumed_mA":pump_input_extra_ma,
       "EN_1p05V_crossing_ms":round(t_en*1000,2) if t_en is not None else None,
       "VS_at_EN_trigger_v":round(initial_vs,2) if t_en is not None else None,
       "minimum_VS_before_HGATE_ready_v":round(minimum_vs,2) if t_en is not None else None,
       "simplified_HGATE_ready_ms":round(t_turn*1000,2) if t_turn else None,
       "stress_case_model_condition":fail or "VS_6V_CONDITION_MODEL_ONLY__SILICON_START_UNPROVEN",
       "actual_start_validated":False,
    }

scenarios=[
    ("nominal_sensitivity",11.0,10.0,2.0), # C308 10uF + C302 nominal 1uF
    ("optimistic_pump_high_draw_sensitivity",11.0,10.0,5.0),
    ("component_bias_tolerance_corner_high_draw",8.5,6.0,5.0),
]
rows=[]
for name,cvs,cen,pump in scenarios:
    for vin in (9.0,12.0,13.8,24.0,30.0):
        item=screen(vin,cvs,cen,pump)
        item["scenario"]=name
        rows.append(item)

nominal9=next(i for i in rows if i["scenario"]=="nominal_sensitivity" and i["vin_v"]==9)
corner9=next(i for i in rows if i["scenario"]=="component_bias_tolerance_corner_high_draw" and i["vin_v"]==9)
assert 7.3<nominal9["VS_at_EN_trigger_v"]<7.7,nominal9
assert 6.6<nominal9["minimum_VS_before_HGATE_ready_v"]<7.0,nominal9
assert corner9["minimum_VS_before_HGATE_ready_v"]<6.0,corner9
assert len(rows)==15
print(json.dumps({
 "stage":"HISTORICAL_RC_PRE_SUPERVISOR_NOT_AS_BUILT_C309_DNP__NOT_SILICON_BOOT_APPROVAL",
 "source":"TI LM74930-Q1 SNOSDF6; P200 transient qualification remains OPEN",
 "schema_rc_components":"HISTORICAL_PRE_Q303_MODEL_ONLY: R318 100k -> R316 100k and C309 10uF; ACTUAL KiCad uses R318 22k, R316 5.6k, C309 DNP and Q303 VS_READY interlock",
 "additional_reservoir":"C308 10uF/100V Panasonic SMD in parallel with C302 1uF/100V VS->GND",
 "critical_limits":[
    "TI EN_LOW disables pump; cannot precharge CAP while EN low",
    "EN delay only applies to fitted R319 auto mode; D305/RUN_CMD bypasses it",
    "C309 50V is on EN not VS, hypothetical EN max about 28V when VS at 56V",
    "C308 physical can mounting/ESR/cold leakage and C309 MLCC effective capacitance unverified",
    "10uF/100V Panasonic EEE-TG2A100P availability depends on distributor; DigiKey Germany snapshot not guaranteed",
    "When CAP pump starts, 665/780uA 12V test IQ NOT a guaranteed pump input draw; extra current in matrix is only sensitivity parameter",
    "No capacitor model as of yet proves 9V startup; model shows 6V VS violation in pessimistic assumed corner",
    "C309 is DNP in actual Q303 interlock; historical 10uF EN capacitor quick-restart model is no longer present",
    "VS 9.9k resistor remains required for 202V/350ms surge; no reduction",
    "Only after verified gate-on can D302 SOURCE_A->VS supply actual controller current",
    "Historical R318/R316 100k divider has been eliminated by the Q303 series gate; do not use its quiescent current prediction for current circuit",
    "Active RUN_CMD 3.3/5V bypasses this delay on D305; controlled mode must use separate VS-qualified enable gate"
 ],
 "model_assumptions":{"i_off_uA":IQ_OFF_MAX*1e6,
                      "C308_leak_max_uA_at_RATED_100V":LEAK_RESERVOIR_MAX*1e6,
                      "i_enabled_current_uA_nonstartup_bound":IQ_ON_SENSITIVITY*1e6,
                      "CAP_charge_source_mA_min_TI_test_conditions":PUMP_CAP_OUT_I_MIN*1000,
                      "CAP_UVLO_rising_max_v":CAP_UVLO_MAX,
                      "driver_additional_175us_TYP_model_only":True,
                      "NO_component_derating_guarantee":True},
 "scenarios":rows
},ensure_ascii=False,indent=2))
