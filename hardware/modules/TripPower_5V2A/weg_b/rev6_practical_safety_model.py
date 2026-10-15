#!/usr/bin/env python3
"""TripPower B independent REV6 safety screens: stdlib-only reproducible.

All manufacturer figures explicitly attributed; illustrative waveforms, source
R/L and damaged-silicon paths are NOT manufacturer limits, ISO certification,
fuse clearing predictions or pass/fail of an actual PCB. Requirements source:
docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json
import math

REV6 = {
    "normal_v": (10.,32.),
    "undervoltage_reset_allowed_below_v": 10.,
    "ov_off_lower_open_v": 32.,
    "ov_off_upper_inclusive_v": 36.,
    "ov_survival_test":(36.,.400),
    "clamped_load_dump":(58.,.350),
    "optional_not_required":(90.,.005),
    "ambient_range_c":(-20.,70.),
    "5v_2a_ambient_range_c":(-20.,60.),
    "safe_off_up_to_ambient_c":85.,
    "raw_target_a":.5,
    "BAT_OFF_max_a":.001,
    "BAT_OFF_target_a":.0005,
}

@dataclass(frozen=True)
class Mini58:
    mpn:str
    nominal_a:float
    maker_derated_a_at_60c:float
    maker_derated_a_at_80c:float
    maker_typ_prearcing_i2t_a2s:float
    distributor_eur_net_1_10_100:tuple[float,float,float]
    source:str
    stock_status:str

FUSES={
    "3A":Mini58("0997003.WXN",3.,2.2,2.0,9.4,(.91,.695,.5323),
        "https://www.digikey.de/de/products/detail/littelfuse-inc/0997003-WXN/701055",
        "Distributor shows stock; snapshot date 2026-10-15, changes"),
    "4A":Mini58("0997004.WXN",4.,2.9,2.7,17.,(.88,.673,.5153),
        "https://www.digikey.de/de/products/detail/littelfuse-inc/0997004-WXN/701056",
        "Distributor shows stock; snapshot date 2026-10-15, changes"),
    "5A":Mini58("0997005.WXN",5.,3.7,3.4,25.,(.89,.678,.5191),
        "https://www.digikey.de/de/products/detail/littelfuse-inc/0997005-WXN/701057",
        "Distributor shows stock; snapshot date 2026-10-15, changes")
}
FUSE_FAMILY_MANUFACTURER={
    "maker_datasheet":"https://www.littelfuse.com/de/assetdocs/littelfuse-datasheet-997-mini58v?assetguid=f4bf5724-5a40-4a44-8f08-c52ae959a5ef",
    "rating_dc_v":58.,
    "interrupt_at_58v_dc_a":1000.,
    "environment_c":(-40.,125.),
    "rating_is_NOT_absolute_module_peak_proof":True,
    "opening_time_exact_multipliers":{
        "135pct_s":(.75,600.),
        "200pct_s":(.15,5.),
        "350pct_s":(.08,.5),
        "600pct_s":(.03,.1)
    },
    "holder_mpn":"0FHM0001ZXJ-RED",
    "holder_rating_dc_v":58.,
    "holder_maker_url":"https://www.littelfuse.com/de/products/fuses-overcurrent-protection/fuse-holders-fuse-blocks-accessories/fuse-holders/in-line-fuse-holders/mini-fhm/0fhm0001zxj-red",
    "fuse_typical_i2t_only_no_per_case_opening_prediction":True,
    "holder_plus_fuse_rated_for_ringing_beyond_58v":False
}

def load_sensitivity(vin,efficiency=.8,raw_a=.5,vout=5.,iout=2.):
    if not (vin>0 and 0<efficiency<=1 and raw_a>=0 and vout>0 and iout>=0):
        raise ValueError("invalid load case")
    main=vout*iout/(vin*efficiency)+raw_a
    return {"vin_v":vin,"eta_assumed":efficiency,
            "raw_input_equivalent_a_assumed":raw_a,
            "main_input_a_hypothetical":main,
            "5v_buck_heat_w_hypothetical":vout*iout*(1/efficiency-1),
            "not_a_verified_joint_output_rating":True}

def fuse_guard(voltage_at_fuse_open_v, prospective_fault_a, ambient_c=60.,
               assumed_input_a=1.75):
    """Manufacturer 58V rating is for DC circuit breaking. No interpolation of
    maker opening times or fuse derate above/between 60 and 80C.
    """
    if voltage_at_fuse_open_v<0 or prospective_fault_a<0:raise ValueError
    results=[]
    for fuse in FUSES.values():
        allowed=fuse.maker_derated_a_at_60c if ambient_c==60 else (
            fuse.maker_derated_a_at_80c if ambient_c==80 else None)
        results.append({
          "mpn":fuse.mpn,"rating_dc_v":58,
          "meets_DC_voltage_rating_in_this_scenario":voltage_at_fuse_open_v<=58,
          "within_mfr_interrupt_capacity_1000A":prospective_fault_a<=1000,
          "mfr_typical_derated_current_a_at_exact_temperature":allowed,
          "carrying_load_below_tabulated_current": (
              assumed_input_a<=allowed if allowed is not None else None),
          "fault_below_nominal_a_does_not_require_fuse_to_open":
              prospective_fault_a<=fuse.nominal_a,
          "fuse_total_dc_arc_clearing_time_proven_for_fault":False,
          "wire_and_holder_short_time_safe_proven":False
        })
    return results

def fuse_opening_at_exact_maker_multipliers(fuse:Mini58):
    return [{"amps_at_exact_multiplier":fuse.nominal_a*x,
             "manufacturer_opening_time_s_min":span[0],
             "manufacturer_opening_time_s_max":span[1],
             "will_certainly_open_within_350ms":span[1]<=.350,
             "applies_to_OTHER_fault_current":False}
            for x,span in ((1.35,(.75,600.)),(2.,(.15,5.)),
                           (3.5,(.08,.5)),(6.,(.03,.1)))]

def harness_ringing(v_clamp_central=58.,l_h=1e-6,delta_i=20.,dt=1e-6):
    """Scenario V_L=L*di/dt, assumes transient adds same sign at connector.
    Actual line impedances, suppression topology, measurement are essential.
    """
    if dt<=0 or l_h<0:raise ValueError
    v_extra=l_h*delta_i/dt
    local_peak=v_clamp_central+v_extra
    return {"central_nominal_clamp_v":v_clamp_central,
        "harness_inductance_assumed_h":l_h,"current_change_assumed_a":delta_i,
        "change_time_assumed_s":dt,
        "induced_voltage_v_hypothetical":v_extra,
        "local_connector_peak_v_hypothetical":local_peak,
        "58V_fuse_system_rating_ok_under_this_scenario":local_peak<=58.,
        "65V_VS_normal_operating_margin_v":65.-local_peak,
        "70V_LM74930_abs_max_margin_v":70.-local_peak,
        "80V_buck_operating_margin_v":80.-local_peak,
        "manufacturer_clamp_test_proven":False}

def source_installation_check(positive_connector_max_v,
                             negative_min_v=None,fuse_break_v=None,
                             measured_generator_impedance_ohm=None,
                             measured_harness_inductance_h=None,
                             pulse_duration_s=None):
    known=all(x is not None for x in
              (negative_min_v, fuse_break_v, measured_generator_impedance_ohm,
               measured_harness_inductance_h, pulse_duration_s))
    pulse_ok=pulse_duration_s is not None and pulse_duration_s<=.350
    v_ok=positive_connector_max_v<=58.
    fuse_ok=fuse_break_v is not None and fuse_break_v<=58.
    return {"all_profile_parameters_recorded":known,
        "max_connector_voltage_within_REV6":v_ok,
        "duration_within_REV6":pulse_ok,
        "58V_fuse_voltage_gate":fuse_ok,
        "release_possible_on_complete_input_evidence": bool(known and pulse_ok and v_ok and fuse_ok),
        "also_requires_source_repetition_temp_and_negative_transients":True,
        "actual_installed_vehicle_pass":False}

def ov_corner_gates(rising_min,rising_max,falling_max,falling_min=0.):
    """A candidate or measured response includes tolerances/hot/cold and ramp.
    Formal required rising_min >32 and rising_max<=36; falling_max<=32
    to be able to resume at 32V after trip.
    """
    return {
       "normal_32v_on_possible":rising_min>32.,
       "shutdown_by_36v":rising_max<=36.,
       "restart_at_stable_32v":falling_max<=32.,
       "positive_hysteresis":falling_max<rising_min,
       "trip_thermally_or_dynamically_proven":False,
       "all_nominal_DC_corners_consistent": bool(
           rising_min>32 and rising_max<=36 and falling_max<=32 and
           falling_max<rising_min and falling_min<=falling_max)
    }

def failed_silicon_power(v_source=58.,r_supply=5.,r_fault=100.,seconds=.350):
    """Hypothetical damaged device as resistive path; not a semiconductor
    failure prediction. This is why rated F_MAIN alone is not full safety."""
    if min(v_source,r_supply,r_fault,seconds)<=0:raise ValueError
    i=v_source/(r_supply+r_fault)
    return {"fault_a":i,"local_power_w":i*i*r_fault,
        "local_350ms_energy_j":i*i*r_fault*seconds,
        "5a_fuse_must_open":False,
        "still_dangerous_if_fault_persists_continuously":True,
        "thermal_SOAwire_proven":False}

def fram_journal_model(interval_ms,update_duration_ms,
                       crc_ok=True,bank_a_valid=True,bank_b_valid=True):
    """Two-slot independent-validity model, NOT MCU/FRAM driver code."""
    if interval_ms<=0 or update_duration_ms<0:raise ValueError
    return {
       "loss_window_upper_bound_ms_ONLY_if_atomic_protocol_works": interval_ms+update_duration_ms,
       "required_algorithm":"A/B slots with sequence, validity/CRC; payload written before final commit marker",
       "at_least_one_valid_slot":bool(bank_a_valid or bank_b_valid),
       "powerloss_not_guaranteed_safe_without_actual_write_order_test":True,
       "one_corrupt_slot_can_be_recovered":bool(bank_a_valid != bank_b_valid and crc_ok),
       "full_filesystem_repair_guaranteed":False
    }

def fmea():
    return [
      ("P0","R6-01","58V upstream limiter declared without Vconnector,Rsrc,L proof",
       "200V-like installation or local >58V pad / 58V DC fuse arcing",
       "Reject vehicle or install qualified external suppressor; capture full connector waveform"),
      ("P0","R6-02","TVS OPEN / central suppressor OPEN",
       "Unbounded vehicle load-dump enters 65/80V domains",
       "Detect/label incompatible vehicle; safe-sacrifice physical test"),
      ("P0","R6-03","TVS SHORT / reverse wiring / local hard-short",
       "F_MAIN DC arc, harness and connector thermal damage",
       "58VDC min fuse+holder only if verified Vbreaker<=58; select DC time-current versus actual source"),
      ("P0","R6-04","Protecting MOSFET drain-source welded",
       "OV shutdown cannot isolate; RAW may see >36V; below-fuse current may heat IC",
       "Test 58V normal and external pin/cable energy; independent RAW current limit if needed"),
      ("P0","R6-05","F_MAIN does not open under sub-rated leakage",
       "Thermally destructive local 10..30W fault with <1A current",
       "Measured I(t), local T, PCB/enclosure materials & sustained 32V voltage fault test"),
      ("P0","R6-06","OV cutoff rising >36 or false hysteresis",
       "5V/RAW at overvoltage while 36/400ms commanded off",
       "Sweep temperature/tolerance/dVdt 32..36 with PIN oscilloscope, shutdown by36"),
      ("P0","R6-07","ACC permanently live when main VIN drops or GND breaks",
       "Underspecified off/current/backfeed through GPIO USB RAW",
       "Separate BAT ACC current-limited; GND-open USB VIN0 RUN HIGH tests"),
      ("P0","R6-08","RAW 0.5A load hard-short / 58V power FET short",
       "Harness connector wire overheating not covered by main fuse",
       "Protect RAW branch current/thermal; check off leakage and thermal at 70/85C"),
      ("P0","R6-09","Buck 2A at 10V 60C and loss of cooling",
       "Regulator overheats while still below manufacturer Tj absolute",
       "Measure hot Tj estimate from solder point with actual copper/airflow; thermal shutdown 70..85C"),
      ("P0","R6-10","USB VBUS with battery absent or controller failed",
       "Backfeed BAT ACC RAW and damaged primary RTC cell",
       "Measure microamp/currents and maxima on USB VIN0/wrong GND"),
      ("P0","R6-11","FRAM torn between data and commit-marker writes",
       "Unrecognized distance/session loss; invalid state on restart",
       "Power cycle at every instruction phase and verify older CRC slot stays valid"),
      ("P0","R6-12","SD sudden 5V loss during FAT32 metadata write",
       "Interrupted file/file system, false valid log or unrecoverable SD",
       "Journal recovery tests across all write phases; report lost records"),
      ("P1","R6-13","Normal ACC OFF BAT still connected: HOLD timeout or MCU hang",
       "File unfinished or permanent BAT drain",
       "Bound relay hold and watchdog recovery; data-loss availability distinct from heat"),
      ("P1","R6-14","PWR_FAIL stuck LOW / local UV sensor fails",
       "No forewarning and optional backup unavailable",
       "FRAM-first remains safe without signal; SD flush only with independent hold-up tested"),
      ("P1","R6-15","Backup cell reversed shorted aged / hot",
       "Unsafe battery current, accidental primary-cell charging",
       "RTC current/reverse-voltage/aging across declared temperature; independent from main"),
      ("P1","R6-16","Stable 10V recovery / 32V return flickers",
       "Repeated boot/mount and corruption",
       "UV+OV filtering, margin, FRAM journal and stable restart tests"),
      ("P2","R6-17","Demand 90V/5ms despite optional status",
       "Unneeded parts/heat/cost in V1",
       "Track separately only on management authorization"),
    ]

def matrix():
    return [
      ("10V, 32V DC, −20/+25/+60C","5V 2A steady, nominal RAW <=0.5A only after load coexistence proof","measure 5V regulation, TPCB/Tj, Iin/RAW; no thermal limits invented"),
      ("VIN<10V, −20/+25/+70C","safe reset/brownout; no bogus FRAM commit","10→0→10 ramps, 8/9/9.99V; verify stable recovery"),
      ("32+→36V OV sweep and return","cutoff trip >32 to <=36 (hot/cold/full load), restart at stable32","measure earliest/latest rising/falling trips with ramp rates/hysteresis"),
      ("36V/400ms, 10..32V recovery","shutdown allowed, no permanent dangerous damage, recover","oscilloscope max VIN pad, 5V RAW behavior, 5 pulses preliminary TEST count TBD"),
      ("58V/350ms in QUALIFIED clamped 24V source","shutdown allowed, no fire/arc and safe outputs, recover","define actual V(t), Rsource, Lwire, dV/dt, local ring, repetition/temps"),
      ("−20..+70C with 70..85C overheat","2A only mandatory <=60C; derate/off 60..70; safe off by85C","probe heat sink, PCB hotspot, system trips incl sensor fail"),
      ("F_MAIN BAT, ACC separate, 3/4/5A study","fuse meets actual Vfault peak and 1000A conditional rating, cable/holder hot","verify DC interruption and manufacturer 60C derating + inrush; ACC own fuse"),
      ("RAW 0.5A & hard short","no harness/board overheating and downstream safe","0/0.5A, hard short and reverse feed with VIN10/32/58 and USB"),
      ("USB only; VIN=0 RUN HIGH / GND open","no vehicle/RTC/raw backfeed; Boot/USB works within policy","USB VBUS 5V, injected faults, open power grounds"),
      ("BAT-off at 12/24V at -20/25/70C","I_BAT_OFF <1mA, aim <0.5mA","measure true OFF incl ACC sense, divider and PWR_FAIL pull-up"),
      ("ACC OFF BAT+ present","orderly SD flush/unmount and bounded HOLD deadline","filesystem consistency and timeout under SD full/removal/hung MCU"),
      ("Abrupt M8/BAT/GND disconnect","atomic committed FRAM data recover; SD closure NOT guaranteed","cut at every FRAM/SD write phase and log recoverable damage"),
      ("Optional independent emergency supply","no promise until measured T_SD and storage energy/ESR","battery empty/cold/hot, SD write peaks, supply return/flapping, primary never charge"),
      ("Wrong installation unclamped 24V generator","NONCONFORMING use: refuse or require qualified external load-dump guard","document and test installed vehicle Vpeak including cable overshoot"),
    ]

def report():
    return {"source":"REV6 requirement; all numbers in tests are hypotheses unless manufacturer-backed",
      "REV6":REV6,"manufacturer_58v_fuses":{"series":FUSE_FAMILY_MANUFACTURER,
        "MPN":{key:asdict(v) for key,v in FUSES.items()}},
      "normal_load_sensitivity":[load_sensitivity(v) for v in (10.,12.,24.,32.)],
      "5a_fuse_at_60c":fuse_guard(58.,30.,60.,1.75),
      "fuse_times_4a_exact_current_multipliers_only":fuse_opening_at_exact_maker_multipliers(FUSES["4A"]),
      "harness_1uH_20A_per_1us_example":harness_ringing(),
      "installed_rated_fuse_false_pass_example":source_installation_check(78.,fuse_break_v=78.,negative_min_v=-5.,measured_generator_impedance_ohm=2.,measured_harness_inductance_h=1e-6,pulse_duration_s=.35),
      "OV_candidate_example":ov_corner_gates(32.2,35.6,31.8,30.5),
      "silicon_58v_100ohm_fail":failed_silicon_power(),
      "silicon_32v_100ohm_fail_continuous_hazard":failed_silicon_power(32.,seconds=10.),
      "FRAM_commit_example":fram_journal_model(100,1),
      "FMEA_priority":fmea(),"test_matrix":matrix(),
      "RELEASE_GATES":{
         "vehicle_maximum_V_R_L_waveform_measured":False,
         "installed_58V_fuse_and_holder_vs_peak_and_cable_coordinated":False,
         "OVP_32_36_at_temp_and_dynamics":False,
         "RAW_overcurrent_thermal_and_USB_reverse_proven":False,
         "buck_10V_2A_60c_and_safe_off_85c_proven":False,
         "FRAM_atomic_injection_and_SD_recovery_proven":False,
         "actual_circuit_revised_for_REV6_and_KiCad_ERC_DRC":False,
         "hardware_fabrication_and_vehicle_release":False}}
if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
