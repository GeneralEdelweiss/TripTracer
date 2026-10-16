#!/usr/bin/env python3
"""REV6 Round10: independent TI TPS26631 factory OVP + reverse-FET UVLO gates.

Strict original datasheet SLVSE94G Rev G, §§6.3/6.5/6.6/8.3.2–8.4/9.4,
TI E2E UVLO/reverse ESD. Snapshot of current A round3 schematic
blob c9d93ca009739f1186ca39477473f57c87ceb5ca, parent HEAD
854a2c797bcf2e5cbff8f6449e8d8d7c60fd9b9b.

Checks here are static numerical screens. Native independent A KiCad-10
check is a separate CI step; neither is a physical 58V/85C certification.
"""
import json
from dataclasses import dataclass,asdict

DATA={
 "manufacturer":"https://www.ti.com/lit/ds/symlink/tps2663.pdf",
 "rev":"SLVSE94G 2024-06",
 "min_R_IN_SYS_to_UVLO_ohm_reverse_FET":300000.,
 "UVLO_rising_pin_v":(1.176,1.224),
 "UVLO_falling_pin_v":(1.090,1.150),
 "UVLO_input_leak_abs_a":150e-9,
 "UVLO_factory_select_pin_max_v":.240,
 "UVLO_pin_operating_max_v":60.,
 "internal_supply_input_oper_min_v":4.5,
 "factory_OVP_rising_v":(33.2,35.4),
 "factory_OVP_falling_v":(32.7,35.),
 "OVP_to_FLT_off_us_at_20mV_overdrive":(8.5,14.),
 "mode_float":"Overcurrent/thermal fault latches, SHDN or UVLO or VIN cycle required",
 "PGTH_to_GND_if_fast_recovery_unwanted":True,
 "PGTH_ground_tps_PGOOD_forced_low":True,
 "TI_2x_pulse_overcurrent_enabled_ONLY_after_PGOOD_high":True,
 "PGTH_ground_removes_poststartup_2x_IOL_pulse_mode":True,
 "PGTH_ground_short_circuit_peak_STILL_NEEDS_TEST":True,
 "SHDN_open_v":(2.48,3.3),
 "SHDN_sinking_requirement_microa":10.,
 "eFuse_in_operating_max_v":60.,
 "eFuse_in_abs_max_v":67.,
}
A_PIN_SNAPSHOT={
 "ref":"design/trippower-a",
 "head":"854a2c797bcf2e5cbff8f6449e8d8d7c60fd9b9b",
 "schematic_path":"hardware/modules/TripPower_REV6_A/01_TPS26631_REV6.kicad_sch",
 "blob":"c9d93ca009739f1186ca39477473f57c87ceb5ca",
 "mpn_R201":"RT1206BRD07100KL",
 "mpn_R202":"ERA-8AEB123V",
 "mpn_R203":"RT1206BRD074K22L",
 "R201_ohm":100000.,"R202_ohm":12000.,"R203_ohm":4220.,
 "U201_pin6":"VIN_FUSED",
 "U201_pin7":"UVLO_SENSE",
 "U201_pin8":"OVP_SENSE",
 "U201_pin12":"unconnected MODE",
 "U201_pin13":"unconnected SHDN",
 "U201_pin16":"unconnected PGTH",
 "R201":"VIN_FUSED→UVLO_SENSE",
 "R202":"UVLO_SENSE→OVP_SENSE",
 "R203":"OVP_SENSE→GND",
 "Q201_source":"VIN_FUSED",
 "Q201_drain":"EFUSE_IN",
 "Q202":"DRV/B_GATE/IN_SYS",
 "native_approved_OVP8_GND":False
}
# proposed real catalog automotive MPN, ±1% / ±100 ppm/K / 0.25W / 1206
R330={"mpn":"Yageo AC1206FR-07330KL",
      "source":"https://www.digikey.com/en/products/detail/yageo/AC1206FR-07330KL/5897466",
      "nominal_ohm":330000.,"tolerance":.01,"tcr_per_K":100e-6,
      "watts":.25,"automotive_AEC_Q200":True}

def resistor_range(r,at_c,room_c=25.):
    # temperature worst-case tolerance accumulated conservatively
    e=r["tolerance"]+abs(at_c-room_c)*r["tcr_per_K"]
    return (r["nominal_ohm"]*(1-e),r["nominal_ohm"]*(1+e))

def vendor_300k_compliance(r,temps=(-20.,25.,70.,85.)):
    bounds=[resistor_range(r,t) for t in temps]
    return {"temp_range_c":temps,
            "min_R_ohm":min(x[0] for x in bounds),
            "max_R_ohm":max(x[1] for x in bounds),
            "minimum_300k_per_datasheet":min(x[0] for x in bounds)>=300000.,
            "effect_of_negative_60v_max_approx_injection_a":60/min(x[0] for x in bounds),
            "resistor_power_at_58v_if_UVLO_grounded_w":58**2/min(x[0] for x in bounds),
            "actual_reverse_fault_injection_not_lab_verified":True}

def one_resistor_UVLO(r=R330,vin_sys_v=10.,hot_c=70.,cold_c=-20.):
    """IN_SYS6 -- R330 -- UVLO7; NO resistor to GND. UVLO pin 0..60V
    operating range. No programmed 9..10V trip required by REV6; default
    device internal supply UVLO 4.5V min governs startup.
    Does not simulate injected ESD diode current in reverse connection.
    """
    rmin=min(resistor_range(r,hot_c)[0],resistor_range(r,cold_c)[0])
    rmax=max(resistor_range(r,hot_c)[1],resistor_range(r,cold_c)[1])
    uv_pin_min=vin_sys_v-DATA["UVLO_input_leak_abs_a"]*rmax
    uv_pin_max=vin_sys_v+DATA["UVLO_input_leak_abs_a"]*rmax
    # VIN falls below UV threshold only around 1.2V, but cannot claim
    # functional running operation below 4.5V recommended input.
    uv_trip_highest=DATA["UVLO_rising_pin_v"][1]+DATA["UVLO_input_leak_abs_a"]*rmax
    return {"vendor":vendor_300k_compliance(r),
       "pin_UVLO_min_max_at_10vin_sys_v":(uv_pin_min,uv_pin_max),
       "UVLO_high_enough_to_enable_at_10vin_sys":uv_pin_min>DATA["UVLO_rising_pin_v"][1],
       "UVLO_factory_15v_selected":uv_pin_min<DATA["UVLO_factory_select_pin_max_v"],
       "UVLO_trip_in_SYS_voltage_upper_bound_v":uv_trip_highest,
       "remainder_margin_to_start_v":vin_sys_v-uv_trip_highest,
       "no_guarantee_whole_board_starts_at_10v":True}

def OV_factory(steady_sys_v=32.,ac_overshoot_v=0.,noise_v=0.,
               extra_drop_from_connector_v=0.):
    pin=steady_sys_v-extra_drop_from_connector_v+ac_overshoot_v
    minfall,maxfall=DATA["factory_OVP_falling_v"]
    minrise,maxrise=DATA["factory_OVP_rising_v"]
    return {"V_IN_SYS_highest_on_recovery":pin,
            "factory_rising_min_max":(minrise,maxrise),
            "factory_falling_min_max":(minfall,maxfall),
            "32v_nominal_on_guarantee":pin+noise_v<minrise,
            "32v_OV_recovery_static_guarantee":pin+noise_v<minfall,
            "recovery_margin_v":minfall-pin-noise_v,
            "36v_shutdown_static_guarantee":maxrise<=36.,
            "recovery_after_latched_overcurrent_fault_guarantee":False,
            "dynamic_58_to_32_pass":False}

def old_A_UVLO_factory_OVP_direct_strap_failure(r201=100e3,r202=12e3):
    """If one connects OVP GND while leaving 3-res chain/pad positions
    floating or shorted, UVLO network is NOT a 300k from IN_SYS."""
    vin_uv=DATA["UVLO_rising_pin_v"][1]*(1+r201/r202)
    return {"VIN_UVLO_rise_worst_nominal_R_v":vin_uv,
            "R_IN_SYS_to_UVLO_ohm":r201,
            "ti_reverse_FET_300k_compliant":False,
            "factory_OVP_strap_alone_is_NO_GO":True}

def raw_short_current():
    ilim=18/6.04
    return {"A_R204_6p04k_nominal_total_overload_a":ilim,
            "potential_2x_pulse_nominal_a":2*ilim,
            "potential_3x_fast_trip_nominal_a":3*ilim,
            "I_SCP_quoted_max_a":45.,
            "example_raw_load_R32ohm_at_V32V_a":1.,
            "example_raw_load_R32ohm_at_V32V_w":32.,
            "F_MAIN_guaranteed_clear_on_raw_1A":False,
            "raw_0p5A_selectivity_proven":False}

def fault_state(case):
    """No claim of device-level functional safety; differentiates OVP,
    held MODE fault, UVLO and SHDN reset, isolated SD journal."""
    return {
      "normal_OVP_without_other_fault":{
       "mode_open_does_not_necessarily_latch_OVP":True,
       "at_32v_reenable_when_no_OL_latch":True,
       "must_account_IN_SYS_pin_ripple_and_dvdt":True},
      "overcurrent_or_temperature_trip_with_MODE_open":{
       "latched":True,"32v_OV_recovery_alone_clears_latch":False,
       "reset_options":"SHDN low-to-high OR UVLO low-to-high OR IN_SYS power cycle",
       "safe_RAW_reattempt_with_short_still_present":False},
      "RAW_short_at_return_32v":{
       "if_starting_with_short":"current limited & then latch per TI, energy/temperature tests OPEN",
       "restart_automatically_guaranteed":False},
      "M8_sudden_disconnect":{
       "advance_warning_time_ms_guaranteed":0,
       "critical_data_already_atomically_FRAM_committed_required":True,
       "SD_unmount_on_primary_cell_required":False}
    }[case]

def report():
    nominal300={"nominal_ohm":300000.,"tolerance":.01,
                "tcr_per_K":100e-6}
    old100={"nominal_ohm":100000.,"tolerance":.001,
                "tcr_per_K":25e-6}
    return {"manufacturer":DATA,"latest_A_actual":A_PIN_SNAPSHOT,
      "nominal_300k_1pct_REJECT":vendor_300k_compliance(nominal300),
      "old_A_100k_REJECT":vendor_300k_compliance(old100),
      "recommended_330k_automotive":dict(R330,**one_resistor_UVLO()),
      "factory_OVP_32V":OV_factory(),
      "factory_OVP_32V_plus_0p8_ripple":OV_factory(ac_overshoot_v=.8),
      "old_A_factory_OVP_strap_NO_GO":old_A_UVLO_factory_OVP_direct_strap_failure(),
      "raw_short":raw_short_current(),
      "recovery_states":{i:fault_state(i) for i in (
          "normal_OVP_without_other_fault",
          "overcurrent_or_temperature_trip_with_MODE_open",
          "RAW_short_at_return_32v","M8_sudden_disconnect")},
      "RELEASE_GATES":{k:False for k in (
        "A_actual_1R_factory_OVP_native_schematic",
        "A_factory_OVP_32V_post58V_oscilloscope",
        "A_start_10V_5V2A_Ta60C",
        "A_PIN58V_350ms_with_harness_RLC",
        "RAW_0p5A_hot_short_cable",
        "85C_temperature_sensor_host_hw_fail_safe",
        "USB_M8_RTC_reverse_current",
        "external_fuse_total_clearing",
        "FRAM_atomic_and_SD_recovery",
        "FAB_OR_VEHICLE_RELEASE")}}
if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
