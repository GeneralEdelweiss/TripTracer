#!/usr/bin/env python3
"""TripPower A Round5: two holistic safety architectures, labelled vendor bounds.

A: F_MAIN destructive-safe only IF independently proven I2t/arc/pcb; is NOT
guaranteed because VIN=200 can be delivered to high-Z exposed pins.
B: separate AP74502HQ+one HV N-FET OFF in blocking orientation before Q301;
vendor single-FET load-switch + 200V/10k/Zener references, not qualified
for our FET/Qg/PCB/hot and not proven with single zener-open.
"""
import json
import math

VIN_NORMAL_MIN=9.
VIN_NORMAL_MAX=30.
LD_V=200.
LD_T=0.350
MAIN_LOAD_A=10/(9*0.8)+1 # 2.389A assumed 80% buck, RAW1A
FUSE_MPN="A6Y3-1"  # Mersen 500VDC/3A. Holder I2t not yet qualified
FUSE_A=3.
FUSE_VDC=500.
AP_MPN="AP74502HQTA8-7"
FET_MPN="SQM10250E_GE3"
R_HV_NOM=3*3300.
C_HV_NOM=1e-6
AP_IQ_MAX_12V_A=84e-6  # datasheet test at VIN12, EN3.3; NOT 9V guarantee
AP_IEN_MAX_12V_A=5e-6  # same test conditions
R_TOL_125_MIN=.99*.99 # worst -1% and -100ppm/K from 25->125
R_TOL_125_MAX=1.01*1.01
OV_TOP_NOM=3*100000.
OV_BOTTOM_NOM=10000.
OV_THRESH_RISE=(1.165,1.333)
OV_THRESH_FALL=(1.063,1.222)
IOV_ABS_A=110e-9 # max specified OV pin input leakage, sign conservatively +/-.

def fuse_high_impedance(counterexample_current_a=.050,voltage=LD_V,duration=LD_T):
    """No datasheet curve is implied; I<<3A will not guarantee a 0.35s opening."""
    return {
     "candidate_mpn":FUSE_MPN,"manufacturer":"Mersen",
     "rated_current_a":FUSE_A,"dc_interrupt_rating_v":FUSE_VDC,
     "hot_fault_current_assumed_a":counterexample_current_a,
     "device_voltage_v":voltage,"duration_s":duration,
     "current_below_nominal_fuse_rating":counterexample_current_a<FUSE_A,
     "energy_possible_in_failed_device_j":voltage*counterexample_current_a*duration,
     "manufacturer_clearing_time_at_fault_a_and125c_s":None,
     "manufacturer_total_clearing_i2t_at200vdc":None,
     "holder_500vdc_and_vehicle_wiring_qualified":False,
     "fuse_guarantees_harmless_q301short":False
    }

def fuse_short_sensitivity(source_resistance_ohm,short_voltage=0.0):
    assert source_resistance_ohm>0
    i=max(0,(LD_V-short_voltage)/source_resistance_ohm)
    return {"source_r_ohm_assumed":source_resistance_ohm,"fault_a_if_constant":i,
            "source_energy_delivered_j_if_350ms":LD_V*i*LD_T,
            "fuse_trip_curve_not_supplied":True,
            "fuse_200vdc_clearing_qualified":False}

def ap_ov_thresholds():
    min_r=OV_TOP_NOM*R_TOL_125_MIN
    max_r=OV_TOP_NOM*R_TOL_125_MAX
    min_b=OV_BOTTOM_NOM*R_TOL_125_MIN
    max_b=OV_BOTTOM_NOM*R_TOL_125_MAX
    # KCL for OVLO: VIN = Vthreshold * (1 + Rt/Rb) + IOV*Rt.
    def boundary(ref,rt,rb,leak):
        return ref*(1+rt/rb)+leak*rt
    return {
     "OV_divider_top_3x_100k_mpn":"AC1206FR-07100KL",
     "OV_divider_bottom_10k_mpn":"AC1206FR-0710KL",
     "rise_min_v":boundary(OV_THRESH_RISE[0],min_r,max_b,-IOV_ABS_A),
     "rise_max_v":boundary(OV_THRESH_RISE[1],max_r,min_b,IOV_ABS_A),
     "fall_min_v":boundary(OV_THRESH_FALL[0],min_r,max_b,-IOV_ABS_A),
     "fall_max_v":boundary(OV_THRESH_FALL[1],max_r,min_b,IOV_ABS_A),
     "OVLO_at30v_nominal_v":VIN_NORMAL_MAX*OV_BOTTOM_NOM/(OV_TOP_NOM+OV_BOTTOM_NOM),
     "OVLO_at200v_nominal_v":LD_V*OV_BOTTOM_NOM/(OV_TOP_NOM+OV_BOTTOM_NOM),
     "top_each_peak_w_at200v_equal_resistors":(LD_V/(OV_TOP_NOM+OV_BOTTOM_NOM))**2*100000,
     "top_each_350ms_j":(LD_V/(OV_TOP_NOM+OV_BOTTOM_NOM))**2*100000*LD_T,
     "30v_return_below_worst_possible_falling_threshold":boundary(
       OV_THRESH_FALL[0],min_r,max_b,-IOV_ABS_A)>30,
     "pulse_and_hot_resistor_derating_proven":False,
     "AP_OV_falling_rising_bound_applies_at_manufacturer_tests_ONLY":True
    }

def ap_feed():
    vz=56.
    i=(LD_V-vz)/(R_HV_NOM*R_TOL_125_MIN)
    one_r=3300*R_TOL_125_MIN
    # AP datasheet 84uA+EN max5uA (@VIN12). At VIN=9 unknown startup maxima.
    ap_i=AP_IQ_MAX_12V_A+AP_IEN_MAX_12V_A
    ap_nom_dc_pin_9v=9-R_HV_NOM*ap_i
    vs9_source_ideal=9-MAIN_LOAD_A*0.030 # use MOSFET 30mOhm RDS max @25C
    return {
     "hv_precharge_resistors":["R401 CRCW25123K30FKEGHP","R402 same","R403 same"],
     "zener":"D401 1SMB5943BT3G 56V",
     "ap_supply_CVIN":"C401 C1210C105K1RACAUTO 1uF nominal, Ceff unknown",
     "ap_VCAP":"C402 C1206C224K1RACAUTO 220nF nominal, Ceff unknown",
     "200v_56v_fixed_clamp_current_a":i,
     "pulse_power_each_resistor_w":i*i*one_r,
     "pulse_energy_each_resistor_j":i*i*one_r*LD_T,
     "pulse_zener_power_w":vz*i,
     "pulse_zener_energy_j":vz*i*LD_T,
     "zener_350ms_at125c_qualified":False,
     "D401_open_C1_nominal_time_to80v_ms":-R_HV_NOM*C_HV_NOM*math.log((LD_V-80)/LD_V)*1000,
     "VIN_9v_if_84plus5ua_held_constant_v_SENSITIVITY":ap_nom_dc_pin_9v,
     "SRC_9v_if_2p389a_and30mohm_held_constant_v_SENSITIVITY":vs9_source_ideal,
     "SRC_above_VIN_possible_vs_AP_abs_SRC_LE_VIN":vs9_source_ideal>ap_nom_dc_pin_9v,
     "vendor_absolute_limit_VSRC_le_VVIN_when_VVIN_positive":True,
     "vendor_reference_has_10k_feed_but_real_9v_SRC_vs_VIN_pin_needs_confirmation":True,
     "ap_9v_current_max_for_full_chargepump":None,
     "9v_first_start_qualified":False,
     "30v_restart_static_possible":True
    }

def compare():
    return {
      "required":{"VIN_normal":[9,30],"regulated_output":"5V/2A","RAW_design_a":1,
         "load_dump":[200,.350],"ambient_c":[-40,125]},
      "A_external_main_fuse":{
        "candidate":FUSE_MPN, "rated_dc_v":500,
        "recommended_role":"wiring and hard-short containment pending real source and I2t",
        "example_high_impedance":fuse_high_impedance(),
        "constant_source_sensitivity":[fuse_short_sensitivity(r) for r in (1,5,8,20,50)],
        "single_fault_hazard_energy_proven_bounded":False,
        "incremental_PCB_parts":0, "external_fuse_and_holder_added_to_main_triptracer":True,
        "decision":"NOT_SUFFICIENT_ALONE__HARD_SHORT_WIRING_AUXILIARY_ONLY"
      },
      "B_independent_HV_cutoff":{
        "architecture":"VIN_FUSED -> Q401.D, Q401.S -> VIN_A_GUARD_OUT -> Q301.D -> SOURCE_A; independent U401+R401-407+D401+C401/C402",
        "controller_MPN":AP_MPN,"independent_FET_MPN":FET_MPN,
        "D401_clamp_is_a_separate_possible_single_point_failure":True,
        "AP_fet_short_then_Q301_healthy_still_protected_by_LM74930":True,
        "Q301_short_then_AP_healthy_and_OV_OFF_forward_body_diode_blocks":True,
        "AP_single_fet_reference_datasheet_page":2,
        "200V_series_reference_datasheet_page":15,
        "OV_LO_corners":ap_ov_thresholds(),"AP_9v_200v_supply":ap_feed(),
        "components_new":12,
        "total_placements_auto":69, "total_placements_run":70,
        "previous_Q307_R342_D306_not_used":True,
        "hot_FET_on_and_switching_SOA_qualified":False,
        "gate_off_max_1us_ap_test_Cgate4p7nF_VIN12_NOT_design":True,
        "body_diode_single_fet_WORST_CASE_verified_in_native_netlist":False,
        "FET_250v_margin_above200v_before_ringing":50,
        "PNP_ECV_vin0_usb_RUN_backfeed_proven":False,
        "chip_source_vs_supply_absolute_max_unresolved":True,
        "part_stock_AP_Mouser_505_as_seen_snapshot":True,
        "decision":"PREFERRED_ISOLATED_KICAD_PROTOTYPE__NOT_DESIGN_FREEZE"
      },
      "system_release":False,
      "blocking_gates":[
         "200V-source shape / R / L / rise time / repeated pulses / F_MAIN holder DC interrupt and I2t",
         "AP74502 VIN 10k feed SRC>VIN possible at 9-30V; reconcile manufacturer's absolute SRC/VIN table with page15 reference",
         "AP 200V OVP gate timing with actual 250V 50nC MOSFET Q401 (1us @4.7nF not Qg-specific)",
         "Q401 hot +125C conducting loss, turnoff SOA and 50V VDS overshoot budget",
         "D401 shunt open fault causes its AP supply to cross 80V in ideal 5ms",
         "D401 transient 350ms pulse / resistor hot board thermal, and 56V-Zener VZmax",
         "Main REV5 VS start, EN, Ceff, 5V/2A and RAW1A at −40..125C",
         "PCB footprint TSOT-23-8 landpattern and full native PCB DRC not yet available"
      ]
    }
if __name__=="__main__":
    print(json.dumps(compare(),indent=2,sort_keys=True,allow_nan=False))
