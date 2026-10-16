#!/usr/bin/env python3
"""REV6 A threshold and voltage-envelope acceptance arithmetic, NOT physical qualification.

Vendor: TI TPS2663 RevG p6 (OV/UV 1.176..1.224V, leak +-150nA,
Ilimit R=k/I eq8, 60V operating, 67V ABS), TI LMR38020-Q1 80V operating
85V absolute. Divider nodal KCL accounts for independent UV and OV leak.
Resistors Yageo RT1206 BRD 0.1% +/-25ppm/K vendor rated; independent corner model.
"""
import json
R1,R2,R3=100000.0,12400.0,4220.0
RSTOL=.001
TCR=.000025
LEAK=150e-9
def voltage_threshold(kind,corner):
    """Independent resistor anti-correlated corners, -20..+70C for free air."""
    if corner=="typ":
        r1,r2,r3=R1,R2,R3
        v=1.122 if kind=="ovp_falling" else 1.2;iuv=iov=0.
    else:
        tdelta=45.
        scale=RSTOL+TCR*tdelta
        if kind in ("ovp","ovp_falling"):
            s=1 if corner=="max" else -1
            r1,r2,r3=R1*(1+s*scale),R2*(1+s*scale),R3*(1-s*scale)
        elif kind=="uvlo":
            s=1 if corner=="max" else -1
            r1,r2,r3=R1*(1+s*scale),R2*(1-s*scale),R3*(1-s*scale)
        else:raise ValueError(kind)
        v=(1.15 if corner=="max" else 1.09) if kind=="ovp_falling" else (1.224 if corner=="max" else 1.176)
        iuv=iov=LEAK*(1 if corner=="max" else -1)
    if kind in ("ovp","ovp_falling"):
        return v*(1+(r1+r2)/r3)+iov*(r1+r2)+iuv*r1
    if kind=="uvlo":
        return v*(1+r1/(r2+r3))+iov*r1*r3/(r2+r3)+iuv*r1
    raise ValueError(kind)
def ld_max_envelope(installed_peak=58.,wire_inductive_overshoot=0.):
    v=installed_peak+wire_inductive_overshoot
    return {"conditioned_input_at_connector_v":installed_peak,
      "additional_local_ringing_assumed_v":wire_inductive_overshoot,
      "TPS26631_IN_SYS_MAX_OPERATING_V":60.0,
      "TPS26631_IN_SYS_ABS_MAX_V":67.0,
      "LMR38020_buck_VIN_MAX_OPERATING_V":80.,
      "LMR38020_buck_VIN_ABS_MAX_V":85.,
      "input_to_eFuse_PIN_max_assuming_no_connector_other_pulse_v":v,
      "input_within_eFuse_operating_limit":v<=60.,
      "input_within_eFuse_absolute_rating":v<67.,
      "buck_VIN_if_OVP_actually_opens_v":None,
      "buck_VIN_if_eFuse_internal_FET_SHORT_v":v,
      "data_proves_eFuse_58V_350ms_and65C":False}
def load_sensitivity(vin,eta=.8,raw=.5):
    if not 10<=vin<=32 or not 0<eta<=1:raise ValueError()
    current=10/(vin*eta)+raw
    nominal_ol=18/6040*1000
    return {"vin":vin,"input_a_assuming_eta":current,
      "efuse_ILIM_6p04k_typ_a":nominal_ol,
      "datasheet_IOL_accuracy_nominal_plusminus_percent":7.,
      "efuse_ol_limit_low_corner_typ_formula_a":nominal_ol*.93/1.01,
      "efuse_ol_limit_high_corner_typ_formula_a":nominal_ol*1.07/.99,
      "TPS26631_has_2x_transient_pulse_limit":True,
      "100V_Q201_RDS_on_hot_max_OHM":None,
      "efuse_RDS_typ_25C_ohm":.031,
      "efuse_IC_losses_at_nominal_rds_W":current**2*.031,
      "plus_Q201_hot_loss_W":None}
def study():
    return {
      "authority":"TRIPPOWER REV6 2026-10-15, not REV5",
      "new_two_sheet_project":"hardware/modules/TripPower_REV6_A/TripPower_REV6_A.kicad_sch",
      "range_10_32":{k:{c:voltage_threshold(k,c) for c in ("min","typ","max")} for k in ("uvlo","ovp","ovp_falling")},
      "R1_100k_R2_12p4k_R3_4p22k_MPN":["RT1206BRD07100KL","RT1206BRD0712K4L","RT1206BRD074K22L"],
      "10_32_logic":{
        "ovp_does_not_trip_at_32_on_resistor_vendor_sensitivity":voltage_threshold("ovp","min")>32,
        "ovp_trips_by_36_on_resistor_vendor_sensitivity":voltage_threshold("ovp","max")<36,
        "ovp_restart_at32_no_overshoot_sensitivity":voltage_threshold("ovp_falling","max")<32,
        "ovp_32V_recovery_pin_margin_v":32-voltage_threshold("ovp_falling","max"),
        "restart_requires_stable_effective_IN_SYS_at_most32_no_positive_transients":True,
        "uvlo_releases_before_10_on_sensitivity":voltage_threshold("uvlo","max")<10,
        "overshoot_and_restart_TIMING_verified":False,
      },
      "load_a":[load_sensitivity(x) for x in (10,12,24,32)],
      "input":[ld_max_envelope(),ld_max_envelope(58,2),ld_max_envelope(58,9.1)],
      "integrated_efuse":{
        "MPN":"TPS26631PWPR","input_operating_v":[4.5,60],
        "input_abs_max_v":67,"catalog_rating_not_automotive_Q1":True,
        "reverse_blocking":"SQM100N10-10_GE3 reverse FET with BSS138LT1G B_GATE pull-down",
        "current_limit_resistor":"R204 6.04k 1%; TI eq8: 18 / Iol A -> kiloohms",
        "OVP_behavior":"AUTO_RETRY after voltage returns; MODE floating latch faults; need actual reset validation",
        "temperature_fault_off_by85c_has_specific_sensor":False,
        "ambient_60C_5V_2A_thermally_proven":False,
        "single_FET_short_eFuse_internal_failure_guaranteed_harmless":False,
        "FMAIN_and_RAW_cable_0p5A_verified":False,
        "USB_fuse_is_outside_TripPower_and_backfeed_proven":False},
      "data_policy":"FRAM-FIRST prior commits; no guaranteed SD close at hard M8 failure",
      "PWR_FAIL":"Q501/R501/R502 derived from buck PG6; LOW main healthy; OPEN fail-high; not guaranteed advance notice",
      "fabrication_release":False,
    }
if __name__=="__main__":print(json.dumps(study(),indent=2))
