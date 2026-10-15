#!/usr/bin/env python3
"""Engineering startup screening for separate TripPower LM74930 + LMR38020.
Analytical envelope ONLY. No simulation, vendor-qualified bootstrap, or
guaranteed power-up. Do NOT change 202V VS feed resistor without surge review.
"""
import json
from pathlib import Path

base=Path("hardware/modules/TripPower_5V2A")
d=json.loads((base/"lm74930_design_v1.json").read_text(encoding="utf-8"))
sch=(base/"01_Protection_LM74930.kicad_sch").read_text(encoding="utf-8"))
buck=(base/"02_5V_LMR38020.kicad_sch").read_text(encoding="utf-8"))
refs=("R313","R314","R315","D302","C302","C303","R316","R318","R319","Q301","Q302","U301")
for ref in refs:
    assert f'(property "Reference" "{ref}"' in sch, ref
assert sch.count('(property "MPN" "CRCW25123K30FKEGHP"') == 3
assert '(property "Value" "470nF 100V X7R AEC-Q200"' in sch
assert '(property "MPN" "C1206C474K1RECAUTO7210"' in sch
assert "LMR38020" in buck
assert "VIN_PROTECTED_UNFUSED" in sch and "VIN_FUSED" in sch
assert d["load_dump_design_target_v"] == 202
assert d["nominal_input_range_v"] == [9,30] or d["nominal_input_range_v"] == {"min":9,"max":30}

rv_total=3*3300.0
i_q_typ=665e-6      # TI table, measured at VS=12V, not vs4V/startup
i_q_max=780e-6      # TI table, measured at VS=12V, not vs4V/startup
vs_operating_min=4.0
vs_por_rise_max=2.9
cp_uvlo_rise_typ=6.6
cp_uvlo_rise_max=7.9
cp_source_typ=2.7e-3  # CAP source, NOT necessarily VS supply draw
cp_source_min=1.3e-3  # spec at VS>=6V CAP-V(A)=7V, not at VS4V
c_cap=470e-9
c_vs_nom=1e-6
tdrv_typ=175e-6+c_cap*cp_uvlo_rise_typ/cp_source_typ
tdrv_sensitivity=175e-6+c_cap*cp_uvlo_rise_max/cp_source_min
# Base static IQ current is NOT the pump charge current. The actual VS
# voltage before Q301 conducts cannot be computed by VIN-R*IQ independently
# of VS; these are illustrative evaluations only.
rtop=d["assumptions"]["UV_Rtop_ohm"]
rbot=d["assumptions"]["UV_Rbottom_ohm"]
rhot=rtop*1.01
rlow=rbot*0.99
req_top=d["assumptions"]["UV_threshold_rising_nom_v"]
assert req_top==0.6
uv_max_trip=0.63
pin_leak_max=200e-9
uv_worst_frac=rlow/(rhot+rlow)
uv_worst_requiv=(rhot*rlow)/(rhot+rlow)
uv_worst_input_trip=(uv_max_trip+pin_leak_max*uv_worst_requiv)/uv_worst_frac
i_full_by_v=lambda v: 10/(v*0.8)+1.0
vin_points=(9.0,12.0,13.8,24.0,30.0)
matrix=[]
for v in vin_points:
    i_avail=max(0.0,(v-vs_operating_min)/rv_total)
    vq_typ=v-rv_total*i_q_typ
    vq_max=v-rv_total*i_q_max
    uv_pin=v*rbot/(rtop+rbot)
    uv_pin_worst=v*uv_worst_frac-pin_leak_max*uv_worst_requiv
    matrix.append({
        "vin_v":v,
        "max_vs_feed_ma_at_vs_4v":round(i_avail*1000,3),
        "vs_v_if_665ua_held_constant_not_startup_prediction":round(vq_typ,2),
        "vs_v_if_780ua_held_constant_not_startup_prediction":round(vq_max,2),
        "uvlo_pin_nominal_v_without_leakage":round(uv_pin,3),
        "uvlo_pin_pessimistic_1pct_r_and_200na_leak_v":round(uv_pin_worst,3),
        "uvlo_rising_max_0p63v_pessimistic_threshold_pass":uv_pin_worst>uv_max_trip,
        "total_9to30v_load_5v2a_plus_raw1a_input_a_at_assumed_80pct_efficiency":round(i_full_by_v(v),3),
        "first_start_guaranteed":False,
    })
assert abs(uv_worst_input_trip-8.349)<0.02
assert matrix[0]["max_vs_feed_ma_at_vs_4v"] < i_q_typ*1000
assert matrix[1]["max_vs_feed_ma_at_vs_4v"] < 1.0
assert matrix[-1]["uvlo_rising_max_0p63v_pessimistic_threshold_pass"] is True
assert abs(tdrv_typ-1.323888888888889e-3)<1e-7
r_cable_contact_limit_at_9v=(9.0-uv_worst_input_trip)/i_full_by_v(9.0)
assert 0.25 < r_cable_contact_limit_at_9v < 0.29
# Surge power: a 1k RVS cannot substitute 9.9k without renewed thermal/Zener tests.
surge_zener_v=56.0
surge_vin=202.0
hypothetical_1k_i=(surge_vin-surge_zener_v)/1000
hypothetical_1k_r_w=hypothetical_1k_i**2*1000
hypothetical_1k_z_w=hypothetical_1k_i*surge_zener_v
report={
 "analysis":"9_TO_30V_VS_FEED_PRESTART_CURRENT_ENVELOPE_ONLY__Q303_INTERLOCK_NOT_SIMULATED",
 "status":"BLOCKED_NOT_GUARANTEED: 9V AND_12V_CONTROLLER_VS_PRECHARGE/CHARGE_PUMP; NO_SPICE_OR_LAB",
 "normal_input_range_v":[9,30],
 "current_VS_feed_total_ohm":rv_total,
 "supply_pin_required_operating_min_v":vs_operating_min,
 "supply_por_rising_max_v":vs_por_rise_max,
 "TI_spec_IQ_at_12v_VS_typ_ua":665,
 "TI_spec_IQ_at_12v_VS_max_ua":780,
 "VS_charge_pump_CAP_output_typ_ma_not_equal_to_VS_input_draw":2.7,
 "VS_charge_pump_CAP_min_ma_spec_at_VS_ge_6v_not_valid_at_4v":1.3,
 "C302_nominal_VS_uF_not_effective":c_vs_nom*1e6,
 "C303_CAP_nominal_nf":c_cap*1e9,
 "TI_C303_1p324ms_typ_startup_driver_delay_not_guaranteed":round(tdrv_typ*1000,3),
 "hypothetical_pump_min_7p9v_gate_threshold_sensitivity_ms_not_guaranteed":round(tdrv_sensitivity*1000,3),
 "UVLO_nominal_turnon_v":round(req_top*(rtop+rbot)/rbot,2),
 "UVLO_conservative_1pct_resistor_200na_leak_0p63v_trip_v":round(uv_worst_input_trip,2),
 "if_9v_measured_at_vehicle_not_module_max_total_series_resistance_before_UVLO_at_5v2a_raw1a_80pct_eta_ohm_idealized":round(r_cable_contact_limit_at_9v,3),
 "conditional_static_values_assume_full_Ti_12v_IQ_at_low_VS_and_are_not_simulation":matrix,
 "simplistic_1kVS_at202V_56Vzener_350ms":{
     "series_R_peak_W":round(hypothetical_1k_r_w,2),
     "series_R_rectangular_J":round(hypothetical_1k_r_w*0.35,2),
     "zener_peak_W":round(hypothetical_1k_z_w,2),
     "zener_rectangular_J":round(hypothetical_1k_z_w*0.35,2)
 },
 "why_A_to_VS_D302_does_not_prove_cold_start":"Q301 (VIN_FUSED drain / SOURCE_A source) is off until gate drive starts; D302 forward from SOURCE_A to VS supplies only after SOURCE_A rises, not an independently available first-start bypass",
 "risk_and_differences":[
   "TI 665/780uA IQ tested at VS12V; actual IQ at VS4, pump source current vs supply current and VS capacitor dynamics unspecified",
   "TI direct charge-pump 1.3mA-min data valid at VS>=6V; do not treat as VS input draw",
   "C302 1uF nominal 100V may lose effective C due to DC bias/temperature, particularly when charged near 56V during surge",
   "HISTORICAL early EN issue now addressed topologically by U302 RESET-controlled Q303 series gate; actual R318=22k (upstream), R316=5.6k downstream and C309 DNP; current hot-off remains unqualified",
   "At 9V UVLO divider worst about 8.35V rising based on R1pct and max positive leakage, leaving limited source sag headroom. If 9V is measured before M8 cable+F_MAIN+connector, the approx 2.389A full-load current can drop 0.65V across ~0.27ohm, causing UVLO. Module VIN must be specified.",
   "Buck LMR38020 is rated from 4.2V startup but its 4ms typical soft-start and raw auxiliary startup must be evaluated together with 3.61A nominal LM74930 OCP",
   "202V 350ms pulse and external F_MAIN remain unqualified"
 ],
 "mitigation_candidates_unapproved":[
   "Maintain 9.9k pulse-rated VS resistor path with A-to-VS diode, prove startup across cold/hot and VIN 9V before change",
   "If startup fails, engineer precharge/delayed EN and adequately derated C302 energy, and verify 202V/350ms; no design committed yet",
   "For deterministic first-start consider current-limited HV supply/alternative rated high-voltage regulator with fault/current/standby analysis",
   "Do not bridge 9.9k with a permanent diode or simply switch to 1k: 202V 350ms Zener/R/IC protection gets compromised"
 ],
 "CI_success_meaning":"arithmetic+crossfile consistency only. This report intentionally returns process success even when startup remains BLOCKED"
}
print(json.dumps(report,ensure_ascii=False,indent=2))
