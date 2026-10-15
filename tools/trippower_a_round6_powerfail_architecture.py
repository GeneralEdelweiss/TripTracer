#!/usr/bin/env python3
"""TripPower A R6: falsifiable source-voltage, TVS and backup-PG gates.

Everything tagged SENSITIVITY is NOT a certified manufacturer's max.
No unknown value is silently treated as 0 or 'PASS'.
Sources: Diodes DS47093 Rev2 p3-4/15, TSC AN-1003 p3, TI SNVSBS6B
§6.5/7.3.12, repo REV5, 2026-10-15 Power Loss requirements.
"""
from __future__ import annotations
import json
import math

AP_RFEED=9900.
AP_I_TYP=62e-6  # manufacturer typical with VIN=12, EN=3.3V only
AP_I_MAX=84e-6  # manufacturer max in same test; NOT startup bound
AP_I_EN_MAX=5e-6  # preliminary prior A assumption, sensitivity only
FET_RON=0.030 # manufacturer RDS max @25C and 10V gate, NOT cold crank
FET_RON_HOT=0.065 # manufacturer @125C, VGS=10V, other test condition
VIN_NORMAL=(9.,10.,11.,30.)
TVS_VCLAMP_25C_MEASURED=61.2
TVS_SRC_202V=202.
TVS_R_GRAPH_202V=4.5
TVS_R_TEXT=3.5

def current_scenario(vin, iq, eta=0.8, rds=FET_RON, raw_a=1.):
    if not(0<eta<=1) or vin<=0 or iq<0 or rds<0:raise ValueError("physical inputs")
    ib=10/(vin*eta)+raw_a
    apvin=vin-iq*AP_RFEED
    src=vin-ib*rds
    diff=src-apvin
    return dict(vin_v=vin,controller_current_a_assumed=iq,
        buck_efficiency_ASSUMED=eta,raw_load_a_ASSUMED=raw_a,
        fet_rds_ohm_ASSUMED=rds,
        total_current_a_ASSUMED=ib,
        ap_vin_v_ASSUMED=apvin,ap_src_v_ASSUMED=src,
        abs_SRC_le_VIN_margin_v=-diff,
        scenario_exceeds_SRC_le_VIN_absolute_rating=diff>0,
        max_ap_vin_feed_current_to_avoid_SRC_over_VIN_a=ib*rds/AP_RFEED,
        static_state_guaranteed=False)

def ap_screen():
    return dict(mpn="AP74502HQTA8-7",
        manufacturer_requirement="VIN>0: SRC maximum VIN (absolute ratings)",
        reference_Diodes_200V="Fig. page15 R1=10k, Dz=60V, output selector VIN for OV clamp; not a guarantee for proposed one-FET guard",
        actual_prototype_mpn_and_net="R401..403=9.9k feed VIN; U401 pin8 SRC at Q401 source / VIN_A_GUARD_OUT",
        vendor_IQ_at_12V_min_a=None,
        vendor_IQ_at_9V_dynamic_max_a=None,
        vendor_VIN_and_SRC_differential_allowance_v=0.,
        vendor_guaranteed_9V_start_with_9p9k_feed=False,
        scenarios={
          str(int(v)):{
            "typ62uA_25C_Rds30mOhm_illustrative":current_scenario(v,AP_I_TYP),
            "max84uA_datasheet12V_illustrative":current_scenario(v,AP_I_MAX),
            "lowIQ1uA_example":current_scenario(v,1e-6),
            "Rds65mOhm_Tj125C_test_requires_Vgs10V":current_scenario(v,AP_I_TYP,rds=FET_RON_HOT)
          } for v in VIN_NORMAL
        },
        off_state_worry="when AP feed near 56V but source remains >56V during step, SRC≤VIN absolute violated despite Q401 switching; inspect 200V off/power-down transients",
        gate_condition="VCAP-VIN<=15V and GATE-SRC 0..15V; gate forcing while SRC>VIN not qualified",
        decision="NO_GO_AS_DRAWN_NO_GUARANTEED_SRC_VIN_ENVELOPE")

def tld_screen():
    i=(TVS_SRC_202V-TVS_VCLAMP_25C_MEASURED)/TVS_R_TEXT
    # Alternative constant-voltage 200V rectangular calculation is NOT actual
    # 350ms ISO exponential/half-sine impulse waveform.
    return dict(mpn="TLD8S36AH",manufacturer="Taiwan Semiconductor",
        manufacturer_note="AN-1003 page3 Figure5 ~4.5Ohm at202V/350ms, prose/Table1 claim3.5Ohm; internal disagreement",
        graph_Ri_202v350ms_25c_ohm=4.5,
        text_Ri_202v350ms_25c_ohm=3.5,
        measured_Vc_25c_v=61.2,measured_Ippm_25c_a=42.8,
        stated_Pppm_w=2619.36,
        ideal_I_at_202V_3p5ohm_assuming_Vc61p2_a=i,
        ideal_I_at_200V_3p5ohm_assuming_Vc61p2_a=(200-61.2)/3.5,
        hypothetical_full_350ms_rectangular_energy_at_I_measured_j=
            61.2*42.8*.35,
        hypothetical_full_350ms_rectangular_energy_NOT_PULSE_SOA=True,
        stated_test_temperature_c=25,
        rated_junction_temperature_range_C=[-55,175],
        datasheet_VC_MAX_10_over_1000us_at_114A_V=58.1,
        ten_over_1000us_limit_does_not_apply_to_350ms=True,
        guaranteed_max_Vc_at125c_v=None,guaranteed_min_Ri_at125c_ohm=None,
        fit_for_60V_Q302_differential_vds_proven=False,
        margin_to65V_LM74930_VS_operating_at25c_measured_v=65-61.2,
        margin_to80V_buck_operating_at25c_measured_v=80-61.2,
        margin_to60V_absolute_Q302_rating_if_across_FET_v=60-61.2,
        needs_polarity_and_open_short_FMEA=True,
        shorted_tvs_fuse_200vdc_fault_clearing_guaranteed=False,
        can_replace_HV_guard_and_LM74930_at125c=False)

def backup_pg():
    return {
      "manufacturer":"TI LMR38020SQDDARQ1",
      "pin":"U101 PG6 open drain, original currently NC",
      "manufacturer_threshold_falling_percent_feedback_min_typ_max":[90,92,94],
      "manufacturer_glitch_filter_fall_min_us":40,
      "manufacturer_glitch_filter_fall_max_us":None,
      "PG_valid_min_buck_input_v":2.,
      "pg_assert_low_when_EN_disabled_if_input_at_least2V":True,
      "interface":"PG pullup R501 100k to 5V_OUT; buffered automotive NMOS Q501 gate=PG, source GND, drain=PWR_OK_SINK_FAIL_RELEASE; R502 gate pulldown1M; pull up on TripTracer only to local always-on 3V3 via current-limiting RHOST and DO NOT attach to BAT/ACC/RAW/5V",
      "exported_logic_low":"5V healthy/PG released, NMOS ON",
      "exported_logic_high":"5V not-good or no 5V, NMOS OFF, HOST pullup HIGH => power fail",
      "detection_voltage_at5v_falling_feedback_corners_v":[5*x/100 for x in (90,92,94)],
      "delta_from5v_nominal_to_detection_v":[5*(1-x/100) for x in (90,92,94)],
      "normal_5v_2A_output_energy_66uF_from5v_to4p6_j":.5*66e-6*(25-4.6**2),
      "normal_5v_2A_ideal_holdtime_66uF_to4p6_ms":.5*66e-6*(25-4.6**2)/10*1000,
      "backup_branch":"TripTracer owner: switched battery/backup rail to MCU/FRAM/SD only, never main 5V 2A; cell charge disabled",
      "gpio_high_no_backfeed_requires_hot_leakage_and_gate_pin_proof":True,
      "verified_IRQ_leadtime_before_3v3_brownout_ms":None,
      "PG_output_low_unpowered_5v_0v_valid":None,
      "backup_power_integral_and_SD_shutdown_success_proven":False,
      "recovery_auto_RUN_and_USB_only_no_backfeed_proven":False,
    }

def costs():
    return {
      "pricing_basis":"EUR vendor snapshot, single units only if sourced; historical supplier VAT basis may differ; not a basket or qualified full BOM",
      "nominal_populated_board_counts":{
        "REV5_AUTO":57,"REV5_RUN":58,
        "AP_guard_AUTO":69,"AP_guard_RUN":70,
        "TVS_plus_unmodified_REV5_AUTO":58,"TVS_plus_unmodified_REV5_RUN":59,
        "PWR_GOOD_buffer_prototype_plus_REV5_AUTO":60,
        "PWR_GOOD_buffer_prototype_plus_REV5_RUN":61,
        "AP_guard_and_PG_optional_AUTO":72,
        "AP_guard_and_PG_optional_RUN":73,
        "TVS_plus_REV5_and_PG_OPTION_AUTO":61,
        "TVS_plus_REV5_and_PG_OPTION_RUN":62
      },
      "price_eur_1_known":{
        "AP74502HQ":.636,
        "SQM10250E_Q401":3.85,
        "TI_LMR38020_SQ":3.92,
        "TI_LM74930":5.39,
        "TLD8S36AH_REICHELT_GROSS":1.85,
        "TLD8S36AH_REICHELT_NET":1.55,
        "Q501_BVSS123_DIGIKEY_NET":.38,
        "R501_100k_MOUSER_NET":.086,
        "R502_1Meg_MOUSER_NET":.086,
        "R407_10k":.10,
      },
      "subtotals_not_whole_bom":{
        "AP_addition_U_Q_only_eur":.636+3.85,
        "REV5_two_main_IC_only_eur":3.92+5.39,
        "TLD8S36AH_price_including_VAT_REICHELT_GROSS":1.85,
        "TLD8S36AH_price_excluding_VAT_REICHELT_NET":1.55,
        "PG_three_extra_parts_MOUSER_DIGIKEY_NET_1":.38+.086+.086,
        "PG_three_extra_parts_MOUSER_DIGIKEY_NET_10":.23+.022+.022,
        "PG_three_extra_parts_MOUSER_DIGIKEY_NET_100":.1451+.015+.015,
        "PG_plus_host_Rpull_EXTRA_1":.38+3*.086,
      },
      "missing_price_positions_rev5":True,
      "no_credible_complete_57_58_or_69_70_unit_price_yet":True,
      "do_not_add_gross_tld_reichelt_to_net_mouser":True,
      "full_supplier_quote_required_before_buy":True
    }

def all_studies():
    return {"AP_guard":ap_screen(),"TLD8S36AH":tld_screen(),
            "PWR_GOOD_interface":backup_pg(),"BOM_and_cost_gate":costs(),
            "requirements":[9,30,200,.35,-40,125],
            "fabrication_release":False,
            "decisions":{"old_AP_guard":"NO_GO",
                         "TVS_only_200v_125c":"NO_GO_AS_PROVEN_REPLACEMENT",
                         "PG_interface":"isolated prototype for backup signal only"}}
if __name__=="__main__":print(json.dumps(all_studies(),indent=2,sort_keys=True))
