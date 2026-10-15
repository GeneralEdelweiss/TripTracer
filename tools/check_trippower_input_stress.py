#!/usr/bin/env python3
"""TripPower LM74930 input-stage STRESS SCREEN, NOT a component qualification.

Reproducible bounding arithmetic from the current design JSON and KiCad schematic.
PASS here only means the arithmetic and component references are internally consistent.
Datasheet/supplier pulse curves, SOA, thermal PCB design and actual measurements remain gates.
"""
import json
from pathlib import Path

BASE = Path("hardware/modules/TripPower_5V2A")
d = json.loads((BASE / "lm74930_design_v1.json").read_text(encoding="utf-8"))
sch = (BASE / "01_Protection_LM74930.kicad_sch").read_text(encoding="utf-8")
parts = {"R313": "3.3k", "R314": "3.3k", "R315": "3.3k",
         "Q301": "SQM10250E_GE3", "Q302": "BUK7Y4R8-60EX",
         "D301": "1SMB5943BT3G", "U301": "LM74930QRGERQ1"}
for ref, token in parts.items():
    assert f'(property "Reference" "{ref}"' in sch, f"missing {ref}"
    assert token in sch, f"candidate changed ({ref}); reassess input stress"
assert '(property "Reference" "F302"' not in sch, "separate aux fuse reintroduced"
assert "VIN_PROTECTED_UNFUSED" in sch
assert sch.count('(property "MPN" "CRCW25123K30FKEGHP"') == 3, "must have R313-R315 vendor MPN"
assert d["controller"] == "LM74930QRGERQ1"
assert d["load_dump_design_target_v"] == 202

VIN, DURATION = 202.0, 0.350  # Conservative rectangular PEAK stress, NOT actual ISO waveform.
R_EACH, N = 3300.0, 3
def vs_case(zener_voltage, multiplier=1.0):
    each = R_EACH * multiplier
    total = each * N
    i = max(0.0, (VIN - zener_voltage) / total)
    return {"zener_v": zener_voltage, "each_resistor_ohms": round(each, 3),
            "chain_current_ma": round(i * 1000, 3),
            "each_resistor_voltage_v": round(i * each, 3),
            "each_resistor_peak_w": round(i*i*each, 3),
            "each_resistor_rectangular_j": round(i*i*each*DURATION, 3),
            "zener_peak_w": round(i*zener_voltage, 3)}
vs = {
    "zener_56v_nominal": vs_case(56),
    "zener_53p2v_illustrative_minus_5pct_and_r_minus_1pct": vs_case(53.2, 0.99),
    "zener_hard_short_single_fault_r_minus_1pct": vs_case(0, 0.99),
}
assert 0.23 < vs["zener_56v_nominal"]["each_resistor_rectangular_j"] < 0.27
assert vs["zener_hard_short_single_fault_r_minus_1pct"]["each_resistor_rectangular_j"] > 0.45
# OV/UV top sections see ~99 V each at 202 V, NOT the whole 202 V.
ov_top = d["assumptions"]["OV_Rtop_ohm"]
uv_top = d["assumptions"]["UV_Rtop_ohm"]
ov_bot = d["assumptions"]["OV_Rbottom_ohm"]
uv_bot = d["assumptions"]["UV_Rbottom_ohm"]
divider = {
    "ov_each_750k_v_at_202v_nom": round(VIN*(ov_top/2)/(ov_top+ov_bot), 2),
    "uv_each_750k_v_at_202v_nom": round(VIN*(uv_top/2)/(uv_top+uv_bot), 2),
    "ov_each_750k_peak_w_at_202v": round((VIN/(ov_top+ov_bot))**2*(ov_top/2), 5),
}
assert 95 < divider["ov_each_750k_v_at_202v_nom"] < 105

# Vishay SQM10250E_GE3 250V AEC-Q101, specified maxima at VGS=10V.
# Hot RDS values are measured in short-pulse datasheet conditions, not 350ms SOA.
i9 = 10/(9*0.80) + d["aux_output"]["max_current_design_target_a"]
rds_max = {"25C":0.0300,"125C":0.0650,"175C":0.0868}
p = {k:i9*i9*v for k,v in rds_max.items()}
rth_reference = 40.0  # K/W; Vishay 1 inch square 2oz FR4 PCB only!
ta = 85.0
thermal = {
    "q301_mpn": "SQM10250E_GE3",
    "input_current_a_at_9v_5v2a_80pct_plus_aux1a":round(i9,3),
    "rds_max_ohms_vgs10":rds_max,
    "conduction_losses_w":{k:round(v,3) for k,v in p.items()},
    "predecessor_25c_loss_w":round(i9*i9*0.165,3),
    "rthja_example_special_2oz_board_k_per_w":rth_reference,
    "tj_c_85ambient_at_hot175c_max_rds_and_reference_board":round(ta+p["175C"]*rth_reference,1),
    "rthja_limit_for_125c_tj_at_85c_k_per_w":round((125-ta)/p["175C"],1),
    "qg_max_nC":75,
    "idss_max_uA_at_250v_175c":600
}
assert 0.48 < p["175C"] < 0.51
assert 0.16 < p["25C"] < 0.18
assert thermal["tj_c_85ambient_at_hot175c_max_rds_and_reference_board"] < 110
# Rough startup sensitivity ONLY: 0.65 mA typical Iq is not an accurate
# charge-pump transient model; the A->VS diode must be retained and tested.
vs9_hypothetical = 9 - 0.00065 * N * R_EACH
# TI SNOSDF6 Figure 7-2 / Eq. 2: R320 should be in series with C307 to
# GND, not placed in the HGATE-to-Q301-gate path. These are NOMINAL
# startup-slew estimates, not predicted or guaranteed physical inrush currents.
# COUT includes C306=47uF + 2x4.7uF buck input MLCC + 0.1uF HF.
# C307 X7R bias/temp derating, other parasitics, source 9V startup and Buck
# input nonconstant current mean real inrush must be measured.
out_cap_f = 47e-6 + 2*4.7e-6 + 0.1e-6
dvdt_nominal_f = 10e-9
gate_source_current_a = {"min":39e-6, "typ":55e-6, "max":75e-6}
inrush = {k:out_cap_f*i/dvdt_nominal_f for k,i in gate_source_current_a.items()}
# Charge-pump decoupler check: TI 10x sum of two MOSFET Ciss. Ciss max at
# Vishay 4.05nF and Nexperia 5.52nF (rated conditions differ).
cap_min_est_f = 10*(4050e-12+5520e-12)
cap_placed_f = 470e-9  # KEMET C1206C474K1RECAUTO7210 selected design candidate
x7r_tolerance_factor = 0.90
x7r_temperature_factor = 0.85  # X7R maximum deviation; not a DC-bias model
cap_after_tol_and_temp_f = cap_placed_f*x7r_tolerance_factor*x7r_temperature_factor
required_dc_bias_retention_fraction_no_aging = cap_min_est_f/cap_after_tol_and_temp_f
ti_initial_driver_delay_s_old = 175e-6 + 100e-9*6.6/2.7e-3
ti_initial_driver_delay_s_new = 175e-6 + cap_placed_f*6.6/2.7e-3
ti_initial_driver_delay_s_new_1p3mA_illustrative = 175e-6 + cap_placed_f*6.6/1.3e-3
assert 0.30<inrush["typ"]<0.32
assert cap_placed_f > cap_min_est_f
assert cap_after_tol_and_temp_f > cap_min_est_f
assert 0.26 < required_dc_bias_retention_fraction_no_aging < 0.27
assert 1.32e-3 < ti_initial_driver_delay_s_new < 1.33e-3
assert d["components"][[i["ref"] for i in d["components"]].index("C_CAP")]["mpn"] == "C1206C474K1RECAUTO7210"
assert '(property "MPN" "C1206C474K1RECAUTO7210"' in sch
assert '(property "Value" "470nF 100V X7R AEC-Q200"' in sch
# Simplistic Q/I lower-bound-like ratios, not switching-time predictions:
q301_qg_max_c = 75e-9
hg_sink_min_a = 128e-3
q_over_i_us = q301_qg_max_c/hg_sink_min_a*1e6
# 10nF high-side gate-to-GND CdVdt (not gate-to-source!) can charge to
# substantial absolute voltage; real HGATE sink current is not constant.
cap_charge_sensitivity_us = {str(v):round((q301_qg_max_c + dvdt_nominal_f*v)/hg_sink_min_a*1e6,2)
                             for v in (40,100,200)}
gate_screen = {
    "output_cap_total_nominal_uF":round(out_cap_f*1e6,2),
    "CdVdt_C307_nominal_nF":10,
    "Rg_R320_ohms":100,
    "nominal_startup_inrush_a_by_source_driver_current":{k:round(v,3) for k,v in inrush.items()},
    "scope":"TI simplified dV/dt formula ONLY; not total startup input current nor max",
    "Q301_Qg_max_nC_test_VDS125V_ID10A":75,
    "HGATE_min_sink_mA":128,
    "Qg_over_min_sink_us_not_guaranteed":round(q_over_i_us,3),
    "with_external_gate_to_GND_C_charge_sensitivity_us_not_switching_time":cap_charge_sensitivity_us,
    "Q301_Ciss_max_pF":4050,
    "Q302_Ciss_max_pF":5520,
    "CAP_10x_Ciss_required_nominal_min_nF":round(cap_min_est_f*1e9,1),
    "C303_CAP_installed_nominal_nF":round(cap_placed_f*1e9,1),
    "C303_at_minus10pct_nF":round(cap_placed_f*0.90*1e9,1),
    "C303_after_minus10pct_and_X7R_minus15pct_nF_excluding_bias_aging":round(cap_after_tol_and_temp_f*1e9,2),
    "C303_min_DCbias_retention_after_tolerance_temperature_no_aging_pct":round(required_dc_bias_retention_fraction_no_aging*100,2),
    "C303_typical_TI_initial_driver_delay_ms_old":round(ti_initial_driver_delay_s_old*1e3,3),
    "C303_typical_TI_initial_driver_delay_ms_new":round(ti_initial_driver_delay_s_new*1e3,3),
    "C303_illustrative_1p3mA_TI_initial_driver_delay_ms":round(ti_initial_driver_delay_s_new_1p3mA_illustrative*1e3,3),
    "C303_effective_value_and_DC_bias_GATE":"CANDIDATE; require KEMET K-SIM 14.1V temperature aging Ceff and 9V dynamic chargepump validation; no fabricated effective-cap claim",
}
assert '(property "Reference" "C307"' in sch and 'C1206C103JARECAUTO' in sch
assert '(property "Value" "100R dVdt-C SERIES (TI)"' in sch
assert '"Q1_GATE"' not in sch, "must no longer connect via 100ohm resistor"

result = {
    "scope": "ANALYTICAL_SAFETY_SCREEN_VISHAY_3P3K_CANDIDATE_NO_HARDWARE_OR_PULSE_PART_QUALIFICATION",
    "kinetic_model": "202V held as rectangular peak for 350ms, deliberately harsher than an ISO load-dump waveform; ignores wiring/source impedance and dynamic clamping",
    "vs_feed": vs,
    "hg_overvoltage_gate_derived_screen":gate_screen,
    "ov_uv_top_dividers": divider,
    "q301_thermal_screen": thermal,
    "vs_9v_at_hypothetical_0p65ma_typical_iq_v_no_boost": round(vs9_hypothetical, 2),
    "status": "BLOCKED: NO_RVS_MPN_PULSE_CURVE; Q301_SOA_GATE_CHARGE_PCB_THERMAL_HOT_LEAKAGE; 9V_DYNAMIC_START; ZENER_TVS_PULSE",
    "next_proofs": [
        "C307 effective 250V 10nF vs gate absolute HV excursions, transient 202V case and board tracking",
        "C303 KEMET 470nF 100V X7R AEC-Q200: obtain vendor K-SIM effective C under 14.1V, full temperature, aging; confirm >95.7nF; verify 9V startup",
        "R320+CdVdt C307 nominal startup inrush and HGATE dynamic off/SOA lab validation",
        "manufacturer 350ms pulse power and voltage curves for three actual VS resistor MPNs at max temperature, including repeated pulses",
        "Q301 real gate VGS, RDS(T), board RthJA and switching/inrush/202V SOA; choose replacement if needed",
        "D301 zener clamp tolerance and surge power versus temperature; Q302 voltage/gate stress; RAW OV/UV divider pulse and leakage",
        "SPICE/bench 9V enable, A->VS boost and chargepump under 5V/2A plus extra raw 1A load",
        "main fuse coordination and both-output interconnect current/I2t including FET-short single fault"
    ]
}
print(json.dumps(result, indent=2, ensure_ascii=False))
