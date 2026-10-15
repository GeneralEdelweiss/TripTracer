#!/usr/bin/env python3
"""TripPower Weg B: reproducible threshold, dynamic counterexample and BOM gates.

Run: python3 hardware/modules/TripPower_5V2A/weg_b/verify_b_feasibility.py
Run tests: python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_b -p 'test_*.py' -v

Manufacturer-defined bounds are kept separate from *scenario assumptions*.
This is NOT SPICE/ISO compliance and deliberately never issues a release.
Only Python standard library is needed.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Specs:
    vnormal_min: float = 9.0
    vnormal_max: float = 30.0
    vdumptest: float = 200.0
    dumptest_seconds: float = 0.350
    tpsm_operating_max: float = 36.0
    tpsm_absolute_max: float = 40.0
    vth_min: float = 0.792  # TPS3760 0.8V adjustable OV: TI table 6.5
    vth_nom: float = 0.800
    vth_max: float = 0.808
    hys_nom: float = 0.020  # TPS3760 E012, 2% relative to positive threshold
    hys_accuracy: float = 0.015  # +/-1.5% of *hysteresis amount*, not of threshold
    isense_max_a: float = 100e-9
    resistor_tolerance: float = 0.01
    rtop_ohms: float = 2 * 470000.0
    rbottom_ohms: float = 23200.0
    t_sense_max_us: float = 17.0  # only for 20% overdrive/1V/us/10pF, NOT universal
    t_startup_delay_ms: float = 2.0  # max, valid supply
    supervisor_por_controlled_min_v: float = 1.4
    supervisor_vdd_min: float = 2.7
    tpsm_junction_max_c: float = 150.0
    target_ambient_max_c: float = 125.0
    output_watts: float = 10.0


SPECS = Specs()


def trip_voltage(vthreshold, rtop, rbottom, sense_current):
    """Input trip at specified sense current (positive into SENSE).
    KCL: (vin-vsense)/rtop = vsense/rbottom + sense_current
    => vin = vsense*(1+rtop/rbottom)+sense_current*rtop.
    Current +/- uses conservative envelope (sign not guaranteed from TI).
    """
    return vthreshold * (1.0 + rtop / rbottom) + sense_current * rtop


def threshold_envelope(specs=SPECS):
    tol = specs.resistor_tolerance
    top_lo, top_hi = specs.rtop_ohms * (1-tol), specs.rtop_ohms * (1+tol)
    bot_lo, bot_hi = specs.rbottom_ohms * (1-tol), specs.rbottom_ohms * (1+tol)
    j = specs.isense_max_a
    up = {
        "min_v": trip_voltage(specs.vth_min, top_lo, bot_hi, -j),
        "typ_v": trip_voltage(specs.vth_nom, specs.rtop_ohms, specs.rbottom_ohms, 0),
        "max_v": trip_voltage(specs.vth_max, top_hi, bot_lo, +j),
    }
    down = {
        "min_v": trip_voltage(specs.vth_min * (1-specs.hys_nom*(1+specs.hys_accuracy)), top_lo, bot_hi, -j),
        "typ_v": trip_voltage(specs.vth_nom * (1-specs.hys_nom), specs.rtop_ohms, specs.rbottom_ohms, 0),
        "max_v": trip_voltage(specs.vth_max * (1-specs.hys_nom*(1-specs.hys_accuracy)), top_hi, bot_lo, +j),
    }
    return {"rising": up, "falling": down,
            "static_restart_30_possible_by_thresholds": down["min_v"] > 30.0,
            "static_on_30_by_thresholds": up["min_v"] > 30.0,
            "static_below_36_without_overshoot": up["max_v"] < 36.0}


def pad_after_step(vinitial, vsource, rpath_ohm, ceff_f, time_us):
    """One-pole *assumed* still-conducting series path. It is a counterexample,
    not a manufacturer-predicted waveform: no stray L, no TVS, no source clamp.
    """
    assert rpath_ohm > 0 and ceff_f > 0 and time_us >= 0
    return vsource + (vinitial-vsource)*math.exp(-(time_us*1e-6)/(rpath_ohm*ceff_f))


def time_to_pad_volt_us(vinitial, vsource, vtarget, rpath_ohm, ceff_f):
    assert vinitial < vtarget < vsource and rpath_ohm > 0 and ceff_f > 0
    return -1e6*rpath_ohm*ceff_f*math.log((vsource-vtarget)/(vsource-vinitial))


def pad_ramp_upper_bound(trip_max_v, slew_v_per_us, sense_delay_us,
                         downstream_turnoff_us, overshoot_v=0):
    """Illustrative bound IF assumptions are true; unknown gate turnoff is NOT
    specified by the supervisor tCTS or the LM74930 OV deglitch figure.
    """
    assert slew_v_per_us >= 0 and downstream_turnoff_us >= 0
    return trip_max_v + slew_v_per_us*(sense_delay_us+downstream_turnoff_us)+overshoot_v


def permitted_slew_v_per_us(trip_max, limit, assumed_delay_us, overshoot=0):
    assert assumed_delay_us > 0
    return (limit-trip_max-overshoot)/assumed_delay_us


def min_efficiency_for_thermal(theta_k_per_w, spec=SPECS):
    """At 5V x 2A, P-loss <= (TJmax - Tamb)/theta. If theta is not
    evidenced for board layout, output is only a sensitivity curve."""
    loss_allow = (spec.tpsm_junction_max_c-spec.target_ambient_max_c)/theta_k_per_w
    return spec.output_watts/(spec.output_watts + loss_allow)


def placement_counts(simplified_hf_bypass=True, new_interlock=0,
                     new_pad_protection=0):
    """Shared 45 AUTO/46 RUN placements are unchanged from REV5. New OV
    needs U+3R+VDD-C=5, assuming direct tie of OD to existing EN.
    Added interlock / clamp parts are explicit integers, NOT silently zero
    in a proposed qualified solution."""
    old_buck = 12
    new_buck = 6 if simplified_hf_bypass else 5  # 1 module+5 or 4 capacitors
    ov_add = 5
    d = new_buck + ov_add + new_interlock + new_pad_protection-old_buck
    return {"A_auto": 57, "A_run": 58, "B_auto": 57+d,
            "B_run": 58+d, "delta_placements": d, "new_buck": new_buck,
            "added_ov": ov_add, "interlock_unpriced": new_interlock,
            "pad_protection_unpriced": new_pad_protection}


# Source snapshots: Mouser DE LMR38020; DigiKey DE TPSM and TPS3760,
# all EUR/excl VAT, shipping, soldering; NEVER a complete system quote.
CORE_EUR = {
    "1": {"lmr38020": 3.92, "tpsm33620": 2.100, "tps3760": 2.330},
    "10": {"lmr38020": 2.98, "tpsm33620": 1.987, "tps3760": 1.731},
    "100": {"lmr38020": 2.49, "tpsm33620": 1.882, "tps3760": 1.418},
}


def core_ic_costs():
    return {qty: {"A_regulator_eur": vals["lmr38020"],
                  "B_regulator_plus_ov_eur": round(vals["tpsm33620"]+vals["tps3760"], 3),
                  "B_minus_A_eur": round(vals["tpsm33620"]+vals["tps3760"]-vals["lmr38020"], 3),
                  "note": "Only IC price delta; R/L/C, assembly, PCB, safeguards and logistics excluded"}
            for qty, vals in CORE_EUR.items()}


def state_matrix():
    """Target fail-safe requirements, NOT achieved wiring. POR-undervoltage
    assertion is controlled only above 1.4V at specified VDD slew.
    """
    return [
        {"state": "VIN=0, RUN=HIGH", "required": "OFF / no backfeed", "proven": False,
         "blocker": "TPS3760 VDD below VPOR can produce unspecified OD; RUN injection unresolved"},
        {"state": "cold start 9V", "required": "OFF until VS_READY, RUN/AUTO, OV ready", "proven": False,
         "blocker": "Inherited VS 9V bootstrap and tSD 2ms interlock unverified"},
        {"state": "30V steady", "required": "ON 5V/2A", "proven": False,
         "blocker": "Static OVP permits ON but 9/30 system/thermals unproven"},
        {"state": "200V / 350ms", "required": "Q301 OFF; TPSM VIN<=36 running and <40 always", "proven": False,
         "blocker": "No bounded VIN rise, EN gate fall, Ldi/dt, local clamp or hot SOA"},
        {"state": "return to 30V", "required": "automatic restart after OV and VS_READY", "proven": False,
         "blocker": "Static falling threshold passes, dynamic recovery and residual states unknown"},
        {"state": "supervisor supply below VPOR", "required": "Q301 OFF", "proven": False,
         "blocker": "Output undefined below 1.4V; extra hardware POR interlock required"},
    ]


def report():
    specs = SPECS
    trip = threshold_envelope()
    example = {
        "assumptions_not_guarantees": {
            "prestep_v": 30.0, "vehicle_step_v": 200.0, "source_plus_path_resistance_ohm": 0.1,
            "assumed_capacitance_uF": 4.7,
            "sense_time_us": 17.0, "assumed_gate_fall_us": 7.0,
            "input_loop_inductance_nH": 100.0, "switching_current_step_a": 2.0,
            "current_step_time_ns": 100.0
        },
        "time_to_36_v_us": time_to_pad_volt_us(30,200,36,0.1,4.7e-6),
        "time_to_40_v_us": time_to_pad_volt_us(30,200,40,0.1,4.7e-6),
        "pad_at_17us_v": pad_after_step(30,200,0.1,4.7e-6,17),
        "pad_at_24us_v": pad_after_step(30,200,0.1,4.7e-6,24),
        "inductive_overshoot_example_v": (100e-9*2)/(100e-9),  # 100 nH, 2A /100ns
        "illustrative_ramp_1ms_plus_2v_v": pad_ramp_upper_bound(trip["rising"]["max_v"], 0.170, 17, 7, 2.0),
        "illustrative_ramp_10ms_plus_2v_v": pad_ramp_upper_bound(trip["rising"]["max_v"], 0.017, 17, 7, 2.0),
        "max_slew_to_stay_36_at_24us_no_overshoot_v_per_us":
            permitted_slew_v_per_us(trip["rising"]["max_v"],36,24),
    }
    return {"classification": "NO_GO_AS_SIMPLE_REV5_BUCK_SWAP",
            "manufacturer_limitations": {
                "sense_detect_17us": "only specified at 20pct overdrive, 1V/us slew and test load",
                "HGATE_7us": "TI LM74930 OV deglitch, NOT EN-to-Q301-off maximum",
                "supervisor_startup_ms": 2.0,
                "supervisor_below_1p4v": "OD output UNDEFINED; fail-off not proven",
                "TPSM_vin_operating_max_v": 36, "TPSM_vin_absolute_max_v": 40,
            },
            "thresholds_v": trip, "dynamic_conducting_path_counterexample": example,
            "thermal_min_efficiency_vs_theta": {
                "22K_per_W_EVM_illustrative": min_efficiency_for_thermal(22),
                "35K_per_W_layout_hypothesis": min_efficiency_for_thermal(35),
            }, "placement_count": {
                "ti_typical_with_hf_input_cap": placement_counts(True),
                "ti_marketing_four_caps_lower_bound": placement_counts(False),
                "two_additional_interlock_and_one_clamp_hypothesis": placement_counts(True,2,1),
            }, "core_cost_eur_ex_vat": core_ic_costs(), "logic_cases": state_matrix(),
            "pass_gates": {
                "static_threshold_only": all([trip["static_restart_30_possible_by_thresholds"],
                         trip["static_on_30_by_thresholds"], trip["static_below_36_without_overshoot"]]),
                "VIN_PAD_WORST_CASE_PROVEN": False,
                "9V_START_PROVEN": False, "30V_RESTART_SYSTEM_PROVEN": False,
                "200V_350ms_SOA_PROVEN": False, "FAIL_OFF_PROVEN": False,
                "125C_2A_THERMAL_PROVEN": False, "PCB_ERC_DRC_PROVEN": False
            }}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
