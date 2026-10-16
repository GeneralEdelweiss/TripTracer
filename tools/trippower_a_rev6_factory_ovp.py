#!/usr/bin/env python3
"""TI TPS2663 Rev G: 23-part fixed-OVP A research, two UVLO wiring variants.

Sources: https://www.ti.com/lit/ds/symlink/tps2663.pdf:
 - §6.1 and §6.3 max ratings: IN_SYS/IN/UVLO 60V recommended, 67V absolute;
   OVP, dVdT, SHDN, MODE and ILIM 5.5V abs.
 - §6.5 factory OVP rise 33.2/34.33/35.4V and fall 32.7/33.89/35V
 - §8.3.3 and §9.4: with external reverse FET minimum 300kohm between IN_SYS and UVLO;
   if external UVLO not needed then UVLO connected to IN_SYS (through >=300k for FET).
 - UVLO comparator rise 1.176..1.224V, fall 1.09..1.15V and leakage +/-150nA.
Model expresses worst resistor tolerance +/-1% and +/-100ppm/K from nominal25C
over -20..+70C, i.e. +/-1.45% envelope. NO manufacturer SPICE
nor physical 58V impulse, thermals, surge, board integrity established.
"""
import json

R_TOP = 330_000.
R_BOT = 56_000.
TOL = .01
TCR_PER_K = .000100
MAX_TDELTA = 45.
LEAK_MAX = 150e-9
R_CORNER = TOL + TCR_PER_K*MAX_TDELTA

def single_uvlo_sense(vin_sys, corner="max_loss"):
    assert 0 <= vin_sys <= 60
    r = R_TOP*(1+R_CORNER if corner=="max_loss" else 1-R_CORNER)
    # Current flowing from IN_SYS toward UVLO within datasheet leakage limits.
    return vin_sys - LEAK_MAX*r

def two_resistor_uvlo_recovery(rising=True,corner="max"):
    s = 1 if corner=="max" else -1 if corner=="min" else 0
    top=R_TOP*(1+s*R_CORNER)
    bottom=R_BOT*(1-s*R_CORNER)
    thr = (1.224 if corner=="max" else 1.176 if corner=="min" else 1.2) if rising else (
        1.15 if corner=="max" else 1.09 if corner=="min" else 1.122)
    leak=s*LEAK_MAX
    return thr*(1+top/bottom)+leak*top

def study():
    factory={"rising_min_v":33.2,"rising_typ_v":34.33,"rising_max_v":35.4,
             "falling_min_v":32.7,"falling_typ_v":33.89,"falling_max_v":35.0,
             "stop_at_36_v_static":35.4<36,
             "32v_stable_on_from_cold_static":33.2>32,
             "32v_return_from_58v_static":32<32.7,
             "return_32v_margin_to_min_falling_v":32.7-32,
             "new_off_32v_margin_to_rising_min_v":33.2-32}
    two={k:two_resistor_uvlo_recovery(rising,corner)
         for rising,edge in ((True,"rising"),(False,"falling"))
         for corner in ("min","typ","max") for k in [edge+"_"+corner+"_v"]}
    return {
       "manufacturer_datasheet":"TI TPS2663 SLVSE94G 2024 §6.5 §8.3.3 §8.3.4 §9.4",
       "min_R_between_IN_SYS_and_UVLO_ohm":300000,
       "R201_one_resistor_MPN":"AC1206FR-07330KL",
       "R201_actual_worst_ohm":[R_TOP*(1-R_CORNER),R_TOP*(1+R_CORNER)],
       "R201_rated_temp_range_C":[-55,155],
       "R201_power_dissipation_upper_at_60v_W":60*60/(R_TOP*(1-R_CORNER)),
       "factory_ovp":factory,
       "single_R_disable_external_UVLO":{
          "guaranteed_10V_UVLO_pin_min_v":single_uvlo_sense(10),
          "guaranteed_4p5V_UVLO_pin_min_v":single_uvlo_sense(4.5),
          "guaranteed_58V_UVLO_pin_min_v":single_uvlo_sense(58),
          "V_UVLO_rising_comp_MAX_v":1.224,
          "internal_UVLO_SELECT_max_v":.240,
          "V_IN_SYS_min_operating_v":4.5,
          "10V_input_voltage_loss_budget_till_min_4p5V_v":10-4.5,
          "10V_total_system_full_load_guaranteed":False,
          "available_10V_drop_includes_Q201_resistance_harness_connectors_and_efuse":True,
          "no_deliberate_brownout_threshold_before_device_min_v":True,
          "conditional_sense_10v_start":single_uvlo_sense(10)>1.224
       },
       "two_resistor_defined_UVLO":{
          "R_TOP":330000,"R_BOTTOM":56000,"R_TOP_to_IN_SYS_GE_300k":True,
          "source_voltage_thresholds":two,
          "10V_input_voltage_loss_budget_to_worst_uvlo_v":10-two["rising_max_v"],
          "10V_uvlo_sense_condition":two["rising_max_v"]<10,
          "not_yet_a_native_KiCad_design":True,
       },
       "pin_wiring":{
          "U201_8_OVP":"GND factory 34.33V rising",
          "U201_7_UVLO":"R201_330k from IN_SYS6 (no external UV threshold)",
          "U201_12_MODE":"GND = auto retry for current/temperature faults, fault behavior bench pending",
          "U201_16_PGTH":"GND = dVdT soft-restart, TPS PGOOD stuck LOW, no 2x IOL pulse, Buck PG separate",
          "U201_13_SHDN":"OPEN = internal enable 2.48..3.3V; must not connect to VIN",
          "U201_15_FLT":"OPEN as no MCU interface, optionally probe via dedicated buffer on host later",
          "U201_17_PGOOD":"OPEN, since host PWR_FAIL uses BUCK PG",
          "U201_10_dVdT":"C203 100nF to GND; pin operating<=4V expected, abs5.5V verify",
          "Q201_reverse":"drain EFUSE_IN, source IN_SYS, gate B_GATE",
          "Q202":"G=DRV, D=B_GATE, S=IN_SYS"
       },
       "58v_pulse_safety":{
          "nominal_vehicle_connector_v":58,
          "max_eFuse_operating_v":60,
          "max_eFuse_abs_v":67,
          "nominal_margin_operating_v":2,
          "dynamic_V_IN_SYS_58v_350ms_VERIFIED":False,
          "supply_ringing_sourceRL_and_load_dump_hot_measurement_MANDATORY":True,
          "32v_recovery_after58v_measured":False,
       },
       "PGTH_GND_forces_TPS_PGOOD_LOW":True,
       "2x_IOL_overload_pulse_available":False,
       "auto_retry_TSD_retry_min_typ_max_ms":[500,648,800],
       "permanent_RAW_short_safe_with_auto_retry_qualified":False,
       "temperature85C_safe_shutdown_realized":False,
       "RAW_0p5A_short_selectively_limited":False,
       "5V2A_plus60C_proven":False,
       "external_vehicle_FMAIN_part_of_module_BOM":False,
       "PCB_created":False,
       "production_release":False
    }

if __name__=="__main__":
    print(json.dumps(study(),indent=2))
