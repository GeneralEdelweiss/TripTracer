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
parts = {"R313": "3.32k", "R314": "3.32k", "R315": "3.32k",
         "Q301": "STD17NF25", "Q302": "BUK7Y4R8-60EX",
         "D301": "1SMB5943BT3G", "U301": "LM74930QRGERQ1"}
for ref, token in parts.items():
    assert f'(property "Reference" "{ref}"' in sch, f"missing {ref}"
    assert token in sch, f"candidate changed ({ref}); reassess input stress"
assert '(property "Reference" "F302"' not in sch, "separate aux fuse reintroduced"
assert "VIN_PROTECTED_UNFUSED" in sch
assert d["controller"] == "LM74930QRGERQ1"
assert d["load_dump_design_target_v"] == 202

VIN, DURATION = 202.0, 0.350  # Conservative rectangular PEAK stress, NOT actual ISO waveform.
R_EACH, N = 3320.0, 3
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

# Full-load thermal screen for Q301. ST RthJA=50 K/W requires 1 inch^2 FR-4,
# 2 oz copper, and cannot be used as a guaranteed 35-um compact PCB value.
i9 = 10/(9*0.80) + d["aux_output"]["max_current_design_target_a"]
rds25_max = 0.165  # STD17NF25 max only at VGS=10V; not hot maximum.
p25 = i9**2 * rds25_max
ta = 85.0
rth_example = 50.0
temp_25_rds = ta + p25*rth_example
hot_factor = 1.5 # Sensitivity factor ONLY; NOT an ST guaranteed multiplier.
temp_hot_example = ta + p25*hot_factor*rth_example
thermal = {
    "input_current_9v_full_load_a_80pct_eff": round(i9,3),
    "std17nf25_rds25_max_at_vgs10_ohms": rds25_max,
    "p_w_using_rds25_max": round(p25, 3),
    "rthja_k_per_w_st_special_large_2oz_test_board": rth_example,
    "tj_c_85ambient_rds25_and_special_board_illustrative": round(temp_25_rds,1),
    "tj_c_85ambient_1p5x_rds_sensitivity_special_board": round(temp_hot_example,1),
    "rds_multiplier_1p5_is_assumed_not_guaranteed": True
}
assert 0.9 < p25 < 1.0
assert thermal["tj_c_85ambient_1p5x_rds_sensitivity_special_board"] > 150

# Rough startup sensitivity ONLY: 0.65 mA typical Iq is not an accurate
# charge-pump transient model; the A->VS diode must be retained and tested.
vs9_hypothetical = 9 - 0.00065 * N * R_EACH
result = {
    "scope": "ANALYTICAL_SAFETY_SCREEN_NO_HARDWARE_OR_PULSE_PART_QUALIFICATION",
    "kinetic_model": "202V held as rectangular peak for 350ms, deliberately harsher than an ISO load-dump waveform; ignores wiring/source impedance and dynamic clamping",
    "vs_feed": vs,
    "ov_uv_top_dividers": divider,
    "q301_thermal_screen": thermal,
    "vs_9v_at_hypothetical_0p65ma_typical_iq_v_no_boost": round(vs9_hypothetical, 2),
    "status": "BLOCKED: NO_RVS_MPN_PULSE_CURVE; Q301_HOT_RDS_PCB_THERMAL_AND_SOA; 9V_DYNAMIC_START; ZENER_TVS_PULSE",
    "next_proofs": [
        "manufacturer 350ms pulse power and voltage curves for three actual VS resistor MPNs at max temperature, including repeated pulses",
        "Q301 real gate VGS, RDS(T), board RthJA and switching/inrush/202V SOA; choose replacement if needed",
        "D301 zener clamp tolerance and surge power versus temperature; Q302 voltage/gate stress; RAW OV/UV divider pulse and leakage",
        "SPICE/bench 9V enable, A->VS boost and chargepump under 5V/2A plus extra raw 1A load",
        "main fuse coordination and both-output interconnect current/I2t including FET-short single fault"
    ]
}
print(json.dumps(result, indent=2, ensure_ascii=False))
