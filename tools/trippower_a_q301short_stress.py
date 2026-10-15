#!/usr/bin/env python3
"""Q301 D-S SHORT forcing SOURCE_A=200V; honest load/thermal/9V sensitivity.

TI reference §8.2.2 presumes Q301 not welded. This is an adversarial failure
screen, NOT a certified current limit, SOA analysis or 9V startup guarantee.
Infineon BSP135 600V AEC-Q101; depletion VGS(th) -1..-2.1V at the
manufacturer's specified ID, not a guaranteed 350ms current bound.
"""
import json
from math import inf

PULSE=0.350
VIN=200.0
VS=56.0
VF=0.7  # illustrative, BAV21 not tested at fault stress
R342=1500.0 # RC1206FR-071K5L 1 %, before temperature coefficients
VDS_Q307_MAX=600.0
BSP135_IDSS_MIN=0.020  # @VGS0 and vendor test
BSP135_VGSTH_ABS_MAX=2.1
BSP135_RDS0_MAX=60.0  # manufacturer datasheet at defined points
BSP135_PTOT_25C_BOARD=1.8
BSP135_TJ_MAX=150.0
CEFF=21e-6 # NOT worst-case certified

def direct(rsrc, v=VIN, vs=VS, vf=VF):
    assert rsrc>0
    i=max(0,(v-vs-vf)/rsrc)
    return {"source_resistance_ohm_hypothetical":rsrc,"ideal_fault_current_a":i,
            "D302_thermal_J_if_350ms_no_interrupt":vf*i*PULSE,
            "D301_or_D306_thermal_J_if_350ms_no_interrupt":vs*i*PULSE,
            "DIODES_ZENER_AND_MAIN_FUSE_ARE_NOT_SIZED_FOR_THIS":True,
            "current_is_NOT_a_real_fuse_coordination_prediction":True}

def limited(current_ma=1.4, r=R342,vs=VS,vin=VIN,vf=VF):
    i=current_ma/1000
    resistor_v=i*r
    fet_vds=max(0,vin-vs-vf-resistor_v)
    return {"assumed_current_mA_NOT_GUARANTEED":current_ma,
            "BSP135_drain_to_source_v":fet_vds,
            "BSP135_power_W":fet_vds*i,
            "BSP135_pulse_energy_J":fet_vds*i*PULSE,
            "R342_power_W":i*i*r,"R342_energy_J":i*i*r*PULSE,
            "D302_energy_J":vf*i*PULSE,
            "D301_OR_D306_energy_J_if_SINGLE_SHUNT":vs*i*PULSE,
            "BSP135_BUDGET_BELOW_600V_WITHOUT_OVERSHOOT_V":VDS_Q307_MAX-fet_vds,
            "source_current_limit_proven_over_temperature":False,
            "hot_SOA_proven":False}

def study():
    # This VGS(th)/R relation is heuristic only; at threshold the vendor
    # specifies a small ID. It is NOT a guaranteed Imax bound at 200V/125C.
    ithreshold_ma=BSP135_VGSTH_ABS_MAX/(R342*.99)*1e3
    # Headroom from 9V at VS8 depends on actual D302 VF, RDS0 and
    # source resistance; an intentionally optimistic simple ohmic comparison.
    headroom_9v_ma=max(0,(9-8-VF)/(R342+BSP135_RDS0_MAX))*1e3
    vs_precharge_irvs_ma=(9-8)/9900*1e3
    return {
      "fault":"Q301_DRAIN_SOURCE_SHORT_AT_200V_FOR_350MS",
      "scope":"THEORETICAL_FAULT_AND_VENDOR_TOPOLOGY_SCREEN_ONLY",
      "published_bounds":{
        "BSP135_MPN":"BSP135H6327XTSA1","AEC_Q101":True,
        "VDS_absolute_max_V":600,"VGS_abs_V":20,
        "BSP135_VGSth_min_typ_max_V":[-2.1,-1.4,-1.0],
        "BSP135_Idss_min_Vgs0_mA":20.0,
        "BSP135_1p8W_rating_at25C_board_not125C_qual":True,
        "BSP135_hot_SOA_350ms":None,
        "D302_BAV21WQ_reverse_max_V":200,
        "D301_D306_zener_hot_energy_allowable_J":None,
        "U301_source_A_absolute_max_v":None,
        "Q302_Buk7Y4R8_60EX_VDS_abs_max_V":60,
        "module_main_fuse_I2t_interrupt_resistance":None,
      },
      "no_limiter_hypothetical_source_impedance":[direct(r) for r in (0.1,1.0,5.0,10.0,50.0)],
      "with_Q307_BSP135_and_R342_1p5k":{
        "Infineon_reference":"AN Applications for depletion MOSFETs: I-V depletion with gate tied to downstream end of source resistor; at high VDS saturation current affected by VGS and IDSS",
        "threshold_divided_by_R_heuristic_mA_NOT_MAX":ithreshold_ma,
        "pulsed_assumed_current_scenarios":[limited(x) for x in (.5,1.4,3.0,5.0,10.0)],
        "BSP135_125C_allowable_350ms_energy_J":None,
        "BSP135_Vgs_threshold_not_guaranteed_current_limit":True,
        "saturated_vs_linear_9v_behaviour_not_vendor_bound":True
      },
      "9v_start":{
        "vin_V":9.0,"vs_assumed_V":8.0,"D302_vf_assumed_V":VF,
        "R342_ohm":R342,
        "optimistic_max_backfeed_mA_using_Rds0_max":headroom_9v_ma,
        "RVS_feed_mA_at_vs8":vs_precharge_irvs_ma,
        "sum_sensitivity_mA":headroom_9v_ma+vs_precharge_irvs_ma,
        "LM74930_active_Iq_12V_test_max_mA":0.780,
        "cannot_prove_boost_current_at9v":True,"guaranteed_9v_start":False,
      },
      "unsolved_Q301_short_transmission":{
         "U301_A_connected_to_SOURCE_A_and_exposed_to200":True,
         "Q302_source_pins_connected_to_SOURCE_A_200":True,
         "Q302_60V_MOSFET_not_qualified_at200":True,
         "U301_U302_VS_pins_may_be_clamped_but_cannot_save_direct_A":True,
         "even_perfect_Q307_does_not_make_Q301_short_safe":True,
         "required_full_fix":"second independent 200V-rated SERIES-OFF device UPSTREAM of Q301 or equivalent harness-rated disconnect, with fail-off at 200V, 9V startup, short fault I2t/SOA, and output protection"
      },
      "D306_decision":{
        "D306_only_redundant_against_D301_open_if_FEED_is_current_limited":True,
        "D306_without_current_limiter_not_safe_for_Q301_short":True,
        "D306_hot_350ms_rating":None,
        "D306_hot_9v_leakage":None,
        "D306_production_decision":"DO_NOT_POPULATE_REV5_YET",
      },
      "overall_result":"REJECT_FULL_SINGLE_FAULT_QUALIFICATION__ISOLATED_RESEARCH_PROTOTYPE_ONLY"
    }
if __name__=="__main__":
    print(json.dumps(study(),indent=2,sort_keys=True))
