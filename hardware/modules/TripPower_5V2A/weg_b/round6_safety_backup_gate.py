#!/usr/bin/env python3
"""TripPower Weg B Round 6: independent A-guard vs D-TVS + backup model.

Python stdlib only. All thermal/source/fault paths are conditional screen models,
NOT 200V/350ms at 125C qualification. No unconditional fuse-clear promises.
Run: python3 hardware/modules/TripPower_5V2A/weg_b/round6_safety_backup_gate.py
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json
import math

REV5_NORMAL_MIN_V=9.0
REV5_NORMAL_MAX_V=30.0
DUMP_V=200.0
DUMP_S=0.350
TVS_VC_AT_25C_TEST_V=61.2   # AN-1003 Table 1 202V/350ms, Ri=3.5Ω; NOT hot or 200V guarantee
TVS_AN1003_RI_FIGURE_OHM=4.5
TVS_AN1003_RI_TABLE_OHM=3.5
FUSE_MEV55C5_MIN_BREAK_A=10.0
FUSE_MEV55C5_MAX_CLEAR_AT_MBC_S=10.0
FUSE_MEV55C5_DC_RATED_V=550.0
FUSE_MEV55C5_125C_RANGE_PROVEN=True
AP_ABS_SRC_MUST_NOT_EXCEED_VIN=True
BASE_AUTO_PLACEMENTS=57
BASE_RUN_PLACEMENTS=58
A_GUARD_INCREMENT=12

# Clear distinction between maker-specified values, screen assumptions and unknowns.
def manufacturer_register():
    return {
        "TLD8S36AH":{
            "AN1003":"https://services.taiwansemi.com/storage/resources/application-note-17/AN-1003_Automotive%20circuit%20protection%20of%20load%20dump%20TVS_A1901.pdf",
            "fig_min_Ri_ohm_at_202V_350ms_25C":TVS_AN1003_RI_FIGURE_OHM,
            "table_Ri_ohm_at_202V_350ms_25C":TVS_AN1003_RI_TABLE_OHM,
            "table_Ipp_a":42.8,
            "table_Vclamp_v":TVS_VC_AT_25C_TEST_V,
            "source_discrepancy_unresolved":True,"125C_SOA_curve_available":False,
            "local_80V_buck_and_65V_controller_safe_at_125C":False},
        "AP74502HQTA8-7":{
            "datasheet":"https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf",
            "SRC_le_VIN_for_VIN_gt0_ABS":AP_ABS_SRC_MUST_NOT_EXCEED_VIN,
            "VIN_abs_max_v":80.0,
            "turnoff_1us_max_only_12v_4p7nF_specified_fixture":True,
            "125C_200V_independent_controller_and_hot_FET_SOA_proven":False},
        "MEV55C5":{
            "datasheet":"https://de.mersen.com/sites/default/files/medias/PIM/files/DS-EVpack-fuse-MEV55C-MEV50A-500VDC-max-L-R-less-than-2-5ms-5-800A-EN.pdf",
            "DC_rating_v":FUSE_MEV55C5_DC_RATED_V,
            "continuous_rating_a":5.0,"operating_temperature_c":[-40,125],
            "DC_minimum_break_a":FUSE_MEV55C5_MIN_BREAK_A,
            "manufacturer_max_clear_at_10a_s":FUSE_MEV55C5_MAX_CLEAR_AT_MBC_S,
            "DC_break_cap_a_at_550v_L_over_R_le_1ms":20000,
            "350ms_guaranteed_clearing_at_10a":False,
            "fuse_holder_and_harness_qualified":False}
    }

def fuse_decision(fault_current_a:float):
    assert fault_current_a>=0
    return {
        "fault_a":fault_current_a,
        "can_guarantee_break_at_200v_when_I_lt_10A":False,
        "above_minimum_break_current":fault_current_a>=FUSE_MEV55C5_MIN_BREAK_A,
        "at_10a_mfr_max_clearing_s":FUSE_MEV55C5_MAX_CLEAR_AT_MBC_S,
        "clearing_within_350ms_guaranteed":False,
        "hazard_energy_below_fuse_nominal_may_remain":fault_current_a<=5,
        "need_mfr_time_current_full_clearing_curve_and_L_over_R":True,
        "no_generic_I2t_to_trip_time_extrapolation":True
    }

def tvs_waveform_sensitivity(vpeak=200.0, vbase=24.0, duration=0.35,
                             ri=3.5, vc=TVS_VC_AT_25C_TEST_V,
                             profile="exponential_to_10percent", points=3500):
    """Illustrative fixed clamp Vc = single 25C example, not actual dynamic I-V.
    Exponential: Vopen(t)=Vbase+(Vpeak-Vbase) exp(-ln(10)*t/duration).
    Td=350ms convention here is SCENARIO ONLY, not certified ISO test waveform.
    Integrate Ptv=Vc*max((Vopen-Vc)/Ri,0). NO fuse clearing or TVS failure modeled.
    """
    assert points>=2 and vpeak>=vbase>=0 and ri>0 and duration>0 and vc>0
    assert profile in ("exponential_to_10percent","constant_rectangle")
    def open_v(t):
        if profile=="constant_rectangle":return vpeak
        return vbase+(vpeak-vbase)*math.exp(-math.log(10)*t/duration)
    dt=duration/points
    peak_i=max((vpeak-vc)/ri,0)
    energy=0.0
    charge=0.0
    for k in range(points):
        t=(k+.5)*dt
        i=max((open_v(t)-vc)/ri,0)
        energy+=vc*i*dt
        charge+=i*dt
    return {"mode":profile,"assumed_vpeak_v":vpeak,"assumed_base_v":vbase,
            "assumed_ri_ohm":ri,"assumed_fixed_clamp_v":vc,
            "source_max_current_a":peak_i,
            "source_initial_tvs_power_w":peak_i*vc,
            "illustrative_energy_j":energy,"illustrative_charge_c":charge,
            "is_real_AN1003_pulse_energy_or_125C_rating":False,
            "is_safe_on_TVS_open":False,"is_safe_on_TVS_short_without_DC_fuse_qualification":False,
            "valid_max_pad_80v_or_65v_without_ringing_proof":False}

def guard_source_pin_screen(vbat:float, bootstrap_r_ohm=9900.0,
                            controller_i_assumed_ua=89.0,
                            total_vehicle_load_a:float|None=None,
                            fet_r_on_ohm=0.065, eta=0.8):
    """AP SRC<=VIN absolute condition. Example uses AP 84uA + EN 5uA
    values at vendor's 12V test, NOT guaranteed at startup or load.
    A 65mΩ FET is at vendor stated gate/ID/temp conditions, not any gate.
    """
    if total_vehicle_load_a is None:
        total_vehicle_load_a=10/(vbat*eta)+1.
    controller_vin=vbat-bootstrap_r_ohm*controller_i_assumed_ua*1e-6
    source_node=vbat-fet_r_on_ohm*total_vehicle_load_a
    return {"vehicle_v":vbat,"controller_vin_v_assumed":controller_vin,
        "guard_source_v_assumed":source_node,
        "SRC_minus_VIN_v_assumed":source_node-controller_vin,
        "AP_absolute_rule_SRC_le_VIN_satisfied_in_scenario":source_node<=controller_vin,
        "controller_current_assumed_ua":controller_i_assumed_ua,
        "vendor_12v_QA_does_NOT_bound_9v_start":True,
        "actual_start_and_AP_chargepump_guaranteed":False,
        "9v_10v_11v_comparison_NOT_requirement_change":True}

def versus_normal_minimum(vlist=(9.0,10.0,11.0),eta=.8):
    return [{
        "vin_v":v,
        "normal_input_a_assuming_eta_and_RAW1a":10/(v*eta)+1,
        "RVS_supply_ua_at_VS_8V_and_R_9p9k":(v-8)/9900*1e6,
        "guard":guard_source_pin_screen(v,eta=eta)
    } for v in vlist]

def hard_fault_partial_resistor(vsource=200.0,source_r=5.0,damaged_r=100.0,duration=0.35):
    assert source_r>0 and damaged_r>0 and duration>0
    i=vsource/(source_r+damaged_r)
    return {"hypothetical_I_a":i,"hypothetical_fault_energy_j":i*i*damaged_r*duration,
        "integrated_current_square_a2s_if_constant":i*i*duration,
        "fuse_should_not_be_assumed_to_open":True,
        "no_manufacturer_thermal_failure_mode_proven":True}

def backup_energy(steady_i_a=.1,vcrit_v=3.3,seconds=3.0,
                  extra_peak_i_a=.2, peak_count=3,peak_s=.02,
                  transfer_eta=.8,margin=1.25,
                  source_high_v=3.6,source_low_v=2.9):
    """Pure EXAMPLE, not a chosen CR1220 or measured ESP32/SD profile.
    Assume 100mA base, three additional 200mA bursts lasting 20ms.
    The ~3s figure is provisional from backup specification.
    """
    assert seconds>0 and steady_i_a>=0 and extra_peak_i_a>=0
    assert 0<transfer_eta<=1 and margin>=1 and source_high_v>source_low_v>0
    base_j=vcrit_v*steady_i_a*seconds
    burst_j=vcrit_v*extra_peak_i_a*peak_s*peak_count
    source_j=(base_j+burst_j)*margin/transfer_eta
    cap_f=2*source_j/(source_high_v**2-source_low_v**2)
    return {
        "fixture_only_not_measured":True,"measured_SD_peak_needed":True,
        "load_base_j":base_j,"load_peak_extra_j":burst_j,
        "source_required_with_eta_and_margin_j":source_j,
        "ideal_farad_for_source_voltage_window":cap_f,
        "farad_not_a_qualified_circuit_capacitance":True,
        "CR1220_already_qualifies_as_shutdown_source":False,
        "3s_SD_flush_guaranteed":False,
        "backup_domain_must_not_drive_5v2a_MAIN":True}

def pwr_fail_interface():
    """Electrical *design target* for future hardware, not characterized MPN."""
    vpu_min=3.0
    vpu_max=3.6
    rp=100000.0
    ileak=1e-6
    cline_max=200e-12
    return {
        "signal_name":"PWR_FAIL",
        "asserted":1,"healthy":0,
        "high_on_unpowered_TripPower":True,
        "logic":"High = lost or unhealthy TripPower, Low = validated Power-Good",
        "output_style":"TripPower open-drain N-FET SINKS while Power Good; RELEASES on failed/absent supply; never push-pull or pull-up",
        "TripTracer_pullup_domain":"V_BK_3V3 (LOCAL, independently backed up)",
        "pullup_resistor_ohm_target":rp,
        "backup_pullup_voltage_range_v":[vpu_min,vpu_max],
        "TripPower_output_absent_or_VIN0":"HIGH-Z, TripTracer pull-up asserts FAIL HIGH; no advance warning",
        "TripPower_max_OFF_leak_a_TARGET":ileak,
        "PWR_FAIL_VOH_min_at_3v_assuming_leak_target_v":vpu_min-ileak*rp,
        "max_normal_healthy_sink_current_ua":vpu_max/rp*1e6,
        "VOL_max_v_TARGET":0.3,
        "receiver_capacitance_max_F_TARGET":cline_max,
        "rise_time_10_to_90_percent_us_RC_ONLY":math.log(9)*rp*cline_max*1e6,
        "main_trip_detector_release_latency_max_us_TARGET":100,
        "local_rail_detector_assert_latency_max_us_TARGET":100,
        "local_backup_switch_time_max_us_TARGET":100,
        "local_VMAIN_valid_threshold":"SELECT only after min critical rail + dV/dt+latency margin; not a signed 4.7V guarantee",
        "local_independent_undervoltage_detector_required":True,
        "local_supervisor_MUST_be_separate_irq_or_logic_no_parallel_OD":True,
        "can_be_read_with_tripPower_unpowered":True,
        "proof_from_actual_PIN_3p3_leakage_and_MCU_VIH_required":True,
        "return_stable_filter_ms_TARGET":500,
        "during_SAVE_IN_PROGRESS":"Latch SAVE transaction; ignore restore for remount until transaction committed and verified",
        "PWR_FAIL_stuck_LOW_failure":"Independently locally monitored VMAIN supervisor REQUIRED",
        "PWR_FAIL_stuck_HIGH_failure":"Spurious shutdown, safe only if firmware refuses unnecessary backup consumption",
        "single_fault_200V_to_signal_coupling_blocked_PROVEN":False,
        "OFF_and_RAW_ISOLATION":"No backfeed into VIN/BAT/ACC/USB/RAW, physical interface unpowered leakage measure",
        "zero_warning_time_possible_on_M8_disconnect":True,
        "signal_by_itself_can_guarantee_data_preservation":False}

def warning_and_hold_budget(hold_s,detect_us=100,switch_us=100,
                            fw_irq_us=1000,flush_s=None,margin_s=.1):
    """Never invent SD flush bound. Concrete numerical gate requires measured time."""
    if hold_s<=0 or detect_us<0 or switch_us<0 or fw_irq_us<0:raise ValueError
    fixed=(detect_us+switch_us+fw_irq_us)*1e-6+margin_s
    return {"independent_local_hold_s":hold_s,
        "detect_switch_irq_plus_margin_s":fixed,
        "measured_flush_s":flush_s,
        "required_hold_s":fixed+flush_s if flush_s is not None else None,
        "pass":hold_s>=fixed+flush_s if flush_s is not None else False,
        "cannot_pass_without_measured_SD_flush":flush_s is None}

def backup_fault_states():
    return [
        {"event":"M8/BAT+ torn away, ACC HIGH","notice":"0 warning ahead guaranteed",
         "action":"local supervisor + immediate isolated backup switch; stop new writes",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"D-TVS SHORT / F_MAIN opens","notice":"5V may collapse faster than TripPower driver can assert",
         "action":"local backup supervisor and high-Z USB/BAT/RAW isolation",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"A-guard trips at 200V / Q401 fault","notice":"local 5V may vanish before PWR_FAIL_N",
         "action":"TripTracer self-detect; backup minimal rails",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"PWR_FAIL transistor stuck LOW (false GOOD)","notice":"TripPower FAIL high release absent",
         "action":"local UV independent check detects loss",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"PWR_FAIL stuck HIGH (false FAIL)","notice":"false failure IRQ / backup stress possible",
         "action":"software sanity checks + local VMAIN; avoid battery drain; no continuous high-power backup",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"backup cell missing/dead/high ESR","notice":"IRQ may work but SD brownouts",
         "action":"atomic FRAM intent marker then watchdog recovery; never claim clean SD",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"SD-write peak voltage sag","notice":"RTC-only cell cannot establish current support",
         "action":"validate SD peak/ESR/capacitance over temperature/age",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"vehicle supply returns mid flush","notice":"signal may deassert before SAVE finished",
         "action":"retain SAVE latch; stable power >=500ms as TARGET, remount only after verified commit",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"rapid OV/UV flapping / repeated restart","notice":"multiple PWR_FAIL edges",
         "action":"debounce + state latch + no double-mount + anti-backfeed",
         "failure_if_only_TripPower_PWR_FAIL":True},
        {"event":"VIN=0, RUN_CMD HIGH, USB attached","notice":"indirect backfeeding may mask vehicle loss",
         "action":"distinct vehicle presence and USB power indications; separate backup 3V3 rail",
         "failure_if_only_TripPower_PWR_FAIL":True},
    ]

FAULT_NAMES=[
    "Q301 D-S short", "Q401 guard D-S short",
    "AP74502 guard supply D401 zener open","AP74502 guard supply D401 zener short",
    "D TVS TLD8S36AH open","D TVS TLD8S36AH short",
    "controller gate stuck ON","controller gate stuck OFF",
    "F_MAIN does not open","fault current under 5A",
    "both HV FETs short","normal 200V 350ms +125C"
]

def protection_fmea():
    # Labels: mitigated means only *topological* extra barrier, not safe hardware.
    # Danger applies when sustained heat, output backfeed or cable destruction is unproven.
    return [
      {"priority":1,"fault":"Q301 D-S short",
       "A_guard":"Guard Q401 upstream and reverse body diode potentially isolates when OV controller works; D302/U301 path downstream then not live",
       "D_TVS":"If healthy, input may be clamped; TVS OPEN means full 200V and unqualified U301/Q302 path",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":True,"D_topological_barrier":False},
      {"priority":2,"fault":"Q401 guard D-S short",
       "A_guard":"Q301 OVP remains if Q301 and LM74930 work; 200V bypasses guard",
       "D_TVS":"Not part of D minimal shunt arrangement",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":True,"D_topological_barrier":None},
      {"priority":3,"fault":"AP74502 guard supply D401 zener open",
       "A_guard":"AP VIN pin >80V potential after 200V from 9.9k; unknown gate fail state, other Q301 may protect",
       "D_TVS":"No new guard zener; inherited D301 open remains",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":False,"D_topological_barrier":None},
      {"priority":4,"fault":"AP74502 guard supply D401 zener short",
       "A_guard":"Supply collapses and 9.9k R pulse heating; don't equate OFF with safe hot resistor",
       "D_TVS":"No new guard zener; inherited D301 short remains",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":False,"D_topological_barrier":None},
      {"priority":5,"fault":"D TVS TLD8S36AH open",
       "A_guard":"No added TVS; original D303/304 stack and guarded OV but not hot/SOA proven",
       "D_TVS":"Whole 200V may reach low-voltage circuitry; safe sacrifice unproven",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":True,"D_topological_barrier":False},
      {"priority":6,"fault":"D TVS TLD8S36AH short",
       "A_guard":"Not part of A guard unless also fitted",
       "D_TVS":"Strong sustained DC shunt; F_MAIN must open in 200VDC source window incl arc, I2t, cable and holder",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":None,"D_topological_barrier":False},
      {"priority":7,"fault":"controller gate stuck ON",
       "A_guard":"AP Q401 forced ON: LM74930/Q301 independent OVP may disconnect; common-mode EN and D401 faults still unsafe",
       "D_TVS":"TVS is passive, no gate output; inherited LM74930 stuck ON still fault source",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":True,"D_topological_barrier":False},
      {"priority":8,"fault":"controller gate stuck OFF",
       "A_guard":"Safe shutdown if no heating/no reverse feeding; backup may need immediate activation",
       "D_TVS":"No gate in TVS; inherited controller OFF disables supply",
       "category":"CONDITIONALLY_ACCEPTABLE_TOTAL_LOSS","A_topological_barrier":True,"D_topological_barrier":None},
      {"priority":9,"fault":"F_MAIN does not open",
       "A_guard":"Independent FET cutoff can limit downstream energy when healthy, but D401/R-series/TVS remain on unswitched input",
       "D_TVS":"TVS short or leaky shunt can be sustained externally indefinitely; no independent cutoff",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":True,"D_topological_barrier":False},
      {"priority":10,"fault":"fault current under 5A",
       "A_guard":"A successful HV cutoff can isolate 50mA...3A downstream leakage but front-end zener unchanged",
       "D_TVS":"F_MAIN does not automatically clear; low-current thermal failure at 200V can persist",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":True,"D_topological_barrier":False},
      {"priority":11,"fault":"both HV FETs short",
       "A_guard":"Single-fault-independent scheme defeated; F_MAIN/limited safe failure still mandatory",
       "D_TVS":"Only one shunt protection, no series isolation",
       "category":"HAZARDOUS_DOUBLE","A_topological_barrier":False,"D_topological_barrier":False},
      {"priority":12,"fault":"normal 200V 350ms +125C",
       "A_guard":"Two FET hot SOA/VDS and controller-supply zeners + dynamic cutoff unproven",
       "D_TVS":"AN-1003 25C only, Ri 3.5/4.5 discrepancy, 125C and pad voltage unknown",
       "category":"HAZARDOUS_UNPROVEN","A_topological_barrier":False,"D_topological_barrier":False},
    ]

def report():
    return {
      "source_of_truth":"Review Round6 + POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md",
      "no_fabrication_release":True,
      "vendor_register":manufacturer_register(),
      "fuse_cases":[fuse_decision(x) for x in (.05,2.39,5,9.99,10,40)],
      "TVS_model_assumptions":[tvs_waveform_sensitivity(ri=ri,profile=mode)
                              for ri in (3.5,4.5)
                              for mode in ("exponential_to_10percent","constant_rectangle")],
      "normal_vin_sensitivity":versus_normal_minimum(),
      "guard_9_10_11_v_SRC_constraint":[guard_source_pin_screen(v) for v in (9,10,11)],
      "subfuse_fault_screen":hard_fault_partial_resistor(),
      "backup_energy_fixture":backup_energy(),
      "pwr_fail_proposed_interface":pwr_fail_interface(),
      "hold_budget_no_measured_flush":warning_and_hold_budget(3.),
      "backup_faults":backup_fault_states(),
      "prioritized_comparable_fmea":protection_fmea(),
      "engineering_decision":{
         "tentative_fewer_direct_single_FET_short_unprotected_paths":"A_INDEPENDENT_GUARD",
         "demonstrated_fewer_dangerous_fault_modes_at_125C":False,
         "AP_SRC_VIN_absolute_and_D401_fault_closed":False,
         "TLD_125C_350ms_SOA_and_AN1003_Ri_resolved":False,
         "FMAIN_200VDC_full_time_current_and_holder_proven":False,
         "backup_cell_SD_flush_qualified":False,
         "PWR_FAIL_PIN_physical_ERC_and_hot_leak_proven":False,
         "any_hardware_release":False
       }
    }

if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
