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
result = {
    "scope": "ANALYTICAL_SAFETY_SCREEN_VISHAY_3P3K_CANDIDATE_NO_HARDWARE_OR_PULSE_PART_QUALIFICATION",
    "kinetic_model": "202V held as rectangular peak for 350ms, deliberately harsher than an ISO load-dump waveform; ignores wiring/source impedance and dynamic clamping",
    "vs_feed": vs,
    "ov_uv_top_dividers": divider,
    "q301_thermal_screen": thermal,
    "vs_9v_at_hypothetical_0p65ma_typical_iq_v_no_boost": round(vs9_hypothetical, 2),
    "status": "BLOCKED: NO_RVS_MPN_PULSE_CURVE; Q301_SOA_GATE_CHARGE_PCB_THERMAL_HOT_LEAKAGE; 9V_DYNAMIC_START; ZENER_TVS_PULSE",
    "next_proofs": [
        "manufacturer 350ms pulse power and voltage curves for three actual VS resistor MPNs at max temperature, including repeated pulses",
        "Q301 real gate VGS, RDS(T), board RthJA and switching/inrush/202V SOA; choose replacement if needed",
        "D301 zener clamp tolerance and surge power versus temperature; Q302 voltage/gate stress; RAW OV/UV divider pulse and leakage",
        "SPICE/bench 9V enable, A->VS boost and chargepump under 5V/2A plus extra raw 1A load",
        "main fuse coordination and both-output interconnect current/I2t including FET-short single fault"
    ]
}
print(json.dumps(result, indent=2, ensure_ascii=False))
