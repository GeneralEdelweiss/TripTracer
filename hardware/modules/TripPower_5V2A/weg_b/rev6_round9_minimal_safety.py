#!/usr/bin/env python3
"""TripPower Weg B: REV6 Round9 minimum protection independent design review.

Pure stdlib and deterministic. This is NOT a Spice simulation, real A KiCad
netlist, temperature field qualification, fuse time/current prediction or release.
Manufacturer: TI TPS2663 Rev G §§6.1, 6.5, 6.6, 8.3.2/8.3.3/8.3.4;
Sensata 6700 series; Bourns MF-LSMF datasheet.
A source snapshot 16.10.2026 branch design/trippower-a:
base 01_TPS26631_REV6.kicad_sch blob 7e8b2dee269628ac0bc993c448dfc34acf336a21.
Thermal/RPTC variants use OTHER 12.4k R202 and must not silently be counted
as equivalent to 12k baseline.
"""
from __future__ import annotations
import json,math

A_SNAPSHOT={
 "source_branch":"design/trippower-a",
 "base_schematic_blob":"7e8b2dee269628ac0bc993c448dfc34acf336a21",
 "source_schematic":"hardware/modules/TripPower_REV6_A/01_TPS26631_REV6.kicad_sch",
 "native_A_CI":"https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38863622329",
 "actual_root_child":"01_TPS26631_REV6.kicad_sch",
 "base_R201_ohm":100000., "base_R202_ohm":12000., "base_R203_ohm":4220.,
 "research_R202_ohm":12400.,
 "pins":{"U201.6":"VIN_FUSED","U201.7":"UVLO_SENSE","U201.8":"OVP_SENSE",
         "U201.13":"UNCONNECTED","U201.16":"UNCONNECTED",
         "R201.1":"VIN_FUSED","R201.2":"UVLO_SENSE",
         "R202.1":"UVLO_SENSE","R202.2":"OVP_SENSE",
         "R203.1":"OVP_SENSE","R203.2":"GND",
         "R204.1":"ILIM_SET","R204.2":"GND",
         "Q201.3":"VIN_FUSED","Q201.2":"EFUSE_IN",
         "U201.18":"VIN_PROTECTED_UNFUSED"},
 "no_factory_OVP_ground_strap_as_drawn":True,
 "no_A_own_PCB_no_DRC":True,
}

TI={
 "part":"TPS26631PWPR",
 "factory_ov_rise_v":(33.2,35.4),
 "factory_ov_fall_v":(32.7,35.0),
 "ov_ref_rise_v":(1.176,1.224),
 "ov_ref_fall_v":(1.090,1.150),
 "uv_ref_rise_v":(1.176,1.224),
 "uv_ref_fall_v":(1.090,1.150),
 "uv_ov_leak_abs_a":150e-9,
 "operating_v":60.,"abs_in_v":67.,
 "ILIM_rk_kohm":6.04,
 "ILIM_typ_a":18/6.04,
 "manufacturer_overload_spread_nominal":.07,
 "pulse_multiple":2,
 "fast_trip_multiple":3,
 "short_circuit_protect_max_a":45,
 "SHDN_ABS_max_v":5.5,
 "SHDN_open_min_max_v":(2.48,3.3),
 "SHDN_t_off_us":(0.8,1.5),
 "OVP_to_FLT_turnoff_us":(8.5,14.),
 "MODE_float":"latched on overcurrent; NOT a global auto-restart promise",
 "PGTH_unconnected":"not a defined fast restart select; use GND for known dV/dt recovery behavior",
 "PG_good_for_SD_warning":False
}
TOL_0P1PCT_25PPM_45K=.001+.000025*45

def a_three_ladder(rtop=100e3,rmid=12e3,rbot=4.22e3,tol=TOL_0P1PCT_25PPM_45K,leak=150e-9):
    """Conservative correlated extremum; actual 3-R TI nodal KCL and UV/OV
    independent signed max leakage. Applies component-wise chosen tolerance
    over -20/+70C, PCB parasitics/age and dynamic still unqualified."""
    def ov(v,hi):
        sg=1 if hi else -1
        a=rtop*(1+sg*tol);b=rmid*(1+sg*tol);c=rbot*(1-sg*tol)
        return v*(1+(a+b)/c)+sg*leak*(2*a+b)
    def uv(v,hi):
        # Full TI 3-R nodal model:
        # VIN=V_UV*(1+Rtop/(Rmid+Rbot))+
        # I_UV*Rtop + I_OV*Rtop*Rbot/(Rmid+Rbot)
        sg=1 if hi else -1
        a=rtop*(1+sg*tol);b=rmid*(1-sg*tol);c=rbot*(1-sg*tol)
        return v*(1+a/(b+c))+sg*leak*a*(1+c/(b+c))
    rising=(ov(1.176,False),ov(1.224,True))
    falling=(ov(1.090,False),ov(1.150,True))
    uv_r=(uv(1.176,False),uv(1.224,True))
    return {"rising_v":rising,"falling_v":falling,"UV_rising_v":uv_r,
            "R_ohm":[rtop,rmid,rbot],
            "32V_OV_trip_guarantee_static":rising[0]>32 and rising[1]<=36,
            "32V_after_OV_restart_guarantee_static":falling[0]>32,
            "UVLO_releases_by_10V_static":uv_r[1]<10}

def factory_with_two_UV_R(rtop=100e3,rbot=15e3,tol=TOL_0P1PCT_25PPM_45K,
                          leak=150e-9,requested_vin=10.,vdrop_to_IN_SYS=0):
    """Proposed circuit ONLY: OVP pin physically GND, UVLO divided independently
    VIN_SYS--Rtop--UVLO--Rbottom--GND. This is NOT drawn in A as of snapshot."""
    rmax=rtop*(1+tol);rmin=rtop*(1-tol)
    botmin=rbot*(1-tol);botmax=rbot*(1+tol)
    umin=1.176*(1+rmin/botmax)-leak*rmin
    umax=1.224*(1+rmax/botmin)+leak*rmax
    highest_pin_v=requested_vin-vdrop_to_IN_SYS
    return {"uv_rising_min_max_v":(umin,umax),
            "OV_factory_rising_min_max_v":TI["factory_ov_rise_v"],
            "OV_factory_falling_min_max_v":TI["factory_ov_fall_v"],
            "start_at_10v_static":highest_pin_v>umax,
            "max_internal_VIN_SYS_drop_at_10v_v":requested_vin-umax,
            "required_actual_OVP_ground_strap":True,
            "requires_new_netlist_check":True,
            "manufacturer_temperature_operating_scope":"-40..+125C guaranteed TPS2663 thresholds, system -20..+70",
            "dynamic_32V_restart_verified":False}

def factory_ripple(steady_connector_v=32.,positive_ringing_at_IN_SYS_v=0,
                   recovery_highest_IN_SYS_v=None,noise_margin_v=0):
    """Two independent limits: falling MIN=32.7 for guaranteed re-enable,
    rising MIN=33.2 for guaranteed no retrip. Does not infer exact spectral
    filter or transient timing. VIN_SYS differs from M8 connector."""
    after=steady_connector_v+positive_ringing_at_IN_SYS_v if recovery_highest_IN_SYS_v is None else recovery_highest_IN_SYS_v
    return {"highest_IN_SYS_v":after,"margin_to_recover_v":32.7-after-noise_margin_v,
            "margin_to_avoid_retrip_v":33.2-after-noise_margin_v,
            "both_static_guarantees":after+noise_margin_v<32.7,
            "real_input_RLC_test":False}

def efuse_raw_hazard(ilim_r_kohm=6.04,rtol=.01,vin=32,raw_normal_a=.5,
                     fault_r_ohm=32,efuse_chopped=False):
    """TI manufacturer's OL nominal±7% and R tolerance *nominal formula*
    are only an estimate, not real PEAK 45A waveform; current protection
    timing 2x Iol <=31ms specified for test conditions; 3x fast-trip,
    I_SCP <=45A short circuit threshold before fast response. No certified
    raw cable/copper rating is known."""
    ilim=18/ilim_r_kohm
    min_a=ilim*(1-.07)/(1+rtol)
    max_a=ilim*(1+.07)/(1-rtol)
    i_r=min(vin/fault_r_ohm,max_a)
    return {"main_OL_nom_a":ilim,"main_OL_estimate_min_max_a":(min_a,max_a),
            "pulse_2xIOL_est_max_a":2*max_a,
            "fast_trip_3xIOL_est_max_a":3*max_a,
            "short_circuit_protect_limit_datasheet_max_a":45.,
            "fault_below_total_OL_a":i_r,
            "fault_resistor_power_w":i_r*i_r*fault_r_ohm,
            "nominal_RAW_0p5A_is_NOT_branch_overcurrent_limit":True,
            "safe_0p5A_connector_cable_from_vendor_data_proven":False,
            "reflected_buck_current_and_auto_retry_unmodelled":True,
            "real_time_thermal_safe":False}

def pptc_candidate():
    """Bourns MF-LSMF075/72X, 2920. Datasheet I_HOLD amp, ambient exact.
    Research variant separately fitted A has different R202 than base."""
    return {"mpn":"MF-LSMF075/72X-2","voltage_max_v":72.,"fault_current_max_a":20.,
         "I_hold_a":{23:0.75,60:0.50,70:0.44,85:0.30},
         "500mA_has_positive_hold_reserve_at60C":False,
         "500mA_continuous_at70C":False,
         "max_45A_efuse_fault_within_PPTC_20A_rating_guaranteed":False,
         "manufacturer_trip_current_and_time_hot_verified":False,
         "no_automatic_eFuse_short_raw_fire_protection_claim":True}

def host_thermal_options():
    """Existing relay documentation is HISTORICAL and on current TripTracer
    01_Eingangsschutz page K101 and 01A were removed from ACTIVE hierarchy!
    Hence sensor-on-coil is *only* a future topology, not fitted."""
    v=5.;r=178.;i=v/r
    return {
      "A_Sensata_67F080_NO_contacts_at80C":"A research fitted +1, SHDN ~2.7uA microcurrent below Sensata 1..20mA low-level contact class",
      "host_Sensata_67L080_NC_contacts_at80C":{
          "relay_coil_proposed_only_5v_a":i,
          "coil_w":v*i,"switch_max_dc_v":48.,
          "current_max_a":.5,
          "contact_inside_ratings_if_5v_coil_and_inductive_energy_qualified":True,
          "not_rated_for_raw_58v_bus_directly":True,
          "thermostat_opens_at_c":(75.,85.),
          "reset_temp_approx_c":55.,
          "hot_sensor_local_case_temperature_not_equal_ambient":True,
          "if_host_relay_welded_or_bypassed_safe_off_verified":False,
          "if_sensor_power_absent_fail_open_safe_when_series_switch":True,
          "if_wire_open_fail_open_safe_when_series_switch":True,
          "if_wire_short_bypasses_contact_safe_off_verified":False,
          "applies_to_CURRENT_TripTracer_active_architecture":False
      },
      "current_mainboard_architecture":"solid state self-hold 01I; 01A relay K101 removed from active 01_Eingangsschutz; historical review is not a real present relay",
      "MCU_software_only_thermal_shdn_is_safety_proof":False,
      "minimal_success_condition":"fail-safe NC thermostat/supervisor in actual always-on hardware RUN path, not just firmware; independent real input disconnect or eFuse SHDN through low-voltage non-backfeeding path after stuck MCU/relay fault",
      "source_relay_document":"docs/POWER_RELAY_DESIGN_REVIEW.md (13 Oct historical)",
      "vehicle_sensor_already_installed_in_current_mainboard_schematic":False
    }

def minimal_function_matrix():
    return [
      ("REV6 10-32V and bounded58V pulse","TPS26631 IC and LMR38020 nominal rated","Keep both","OPEN real VIN pad peaks; 60V TPS recommended, 67V ABS"),
      ("OVP rises >32..≤36, returns at32","TPS26631 factory OVP if tied pin8 GND","Replace drawn 3-res UV+OV ladder with UV-only two-res; net count possible -1, not -3","OPEN A current pin8 still OVP_SENSE; must redesign UV including inrush and ripple"),
      ("UVLO at10V restart","TPS26631 with new dedicated divider","100k/15k candidate (2R), not 100k/12k existing strap","OPEN VIN pad min at10 incl cable dropout, cold start, source R"),
      ("reverse polarity/reverse current","TPS26631 B_GATE+DRV external Q201+Q202","Keep Q201/Q202; not redundant","OPEN hot fault reverse/USB; no Schottky extra"),
      ("input current limiting and short","TPS26631 internal FET + R204","Keep, no additional main eFuse","OPEN transient peak 3x IOL and 45A, sustained partial heat"),
      ("output 5V 2A","LMR38020-Q1 integrated current/thermal","Keep high VIN 80V buck, no second 36V buck","OPEN PCB thermal and Ceff L Isat @60C"),
      ("RAW 0.5A local output","not covered by input eFuse nominal3A","0 additional parts ONLY if downstream all possible fault currents/time/I2t/copper/connector+partial-fault heat pass; else one branch-limiter located near RAW connector on TripTracer, OR vetted 72V PPTC as second best","OPEN dedicated RAW fail hot; candidate75/72 fails .5A at70C"),
      ("ambient+85C OFF","not covered by chip TJ thermal shutdown","Use actual TripTracer-AON independent hardware enable path if possible, zero module component; 67L080 NC low-voltage coil conditional, not current solid-state implementation","OPEN sensor OPEN/SHORT, MCU hang, switch weld, actual device placement thermal gradient, auto reset after cooling"),
      ("PWR_FAIL status","A Buck PG Q501 existing, host fail-HIGH pullup","Retain status, no premature microSD battery","OPEN USB/RTC backfeed, host domain voltage, signal latency"),
      ("SD power loss","FRAM first on TripTracer","No backup supercap/RTC 5V SD guarantee","OPEN atomic SPI / interrupted FAT32 recovery"),
      ("vehicle harness fusing","vehicle BAT/ACC near source","NEVER fitted on module, zero PPTC unless needed","OPEN 58V DC arc, total-clearing, cable I²t and fuse-holder"),
      ("extra 200V FET TVS AP74502 controller","not REV6 requirement","Save all historical HV stages","OPEN EMC/short spikes only if measured")
    ]

def report():
    return {
      "snapshot":A_SNAPSHOT,
      "A_real_base_external_r202_12k":a_three_ladder(),
      "A_thermal_and_RAW_variants_older_r202_12k4":a_three_ladder(rmid=12400),
      "factory_ov_10v_UV_redesign_candidate_100k_15k":factory_with_two_UV_R(),
      "factory_bringup_headroom":factory_ripple(),
      "failure_at32_when_IN_SYS_has_0p8v_overshoot":factory_ripple(positive_ringing_at_IN_SYS_v=.8),
      "TI_manufacturer_boundaries":TI,
      "RAW_main_OL_32V_32ohm_fault":efuse_raw_hazard(),
      "RAW_PPTC":pptc_candidate(),
      "TripTracer_host_thermal":host_thermal_options(),
      "functional_savings":minimal_function_matrix(),
      "release":{x:False for x in ("A_factory_pin8_GND_native_netlist","A_UVLO_10V_full_range",
         "A_32V_dynamic_OV_4edges","RAW_short_subfault_85C","temperature_FAIL_SAFE",
         "58v_PIN_spikes","5V2A_60C","USB_BACKUP_reverse","F_MAIN_cable_DC_arcs",
         "TripTracer_FRAM_SD_recovery","PCB_DRC_or_vehicle_release")}
    }
if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
