#!/usr/bin/env python3
"""TripPower A: separate published TI parameter bounds from unknown Ceff/I(t).

Manufacturer sources: TPS38-Q1 SNVSBI8E §7.5 and §8.3.4.1;
LM74930-Q1 SNOSDF6 §6.5 (12V test), onsemi/Comchip 56V clamp.
Not a SPICE model or device-start guarantee.
"""
import json, math

R_VS=[3300,3300,3300] # nominal ±1%, TCR ±100ppm/K tracked separately
VIN9=9.0
# TI TPS38 CTR1/MR internal resistor manufacturer min/typ/max kOhm
TPS38_RCTR_KOHM=(877.0,1000.0,1147.0)
TPS38_CCTR_INSTALLED_UF=0.330
# TI datasheet eq 1-3, see Rev E page22
TPS38_TRIP_TIMING_FACTORS=(0.31,0.28,0.25)
# Typical and max for LM74930 supply only with VIN=12, EN=2V
LM74930_SHDN_MAX_UA=5.0 # VVS12, VIN=12 per table; not startup
LM74930_ON_IQ_MAX_UA=780.0 # @VS12, EN=2V; NOT 9V dynamic/pump
TPS38_IQ_MAX_UA=2.6 # actual VDD conditions from TI datasheet
D306_IR_TEST_MAX_UA=0.5 # @ VR42.6V, manufacturer test point only
# C311 includes ±10% X7R temperature 15%, but actual bias & aging unknown.
def tctr_bound_ms(ceff_uf,side):
    """TI Eq1..3 capacitor contribution only; noncapacitor startup/CTR extra separate."""
    if ceff_uf is None:return None
    if ceff_uf<0:raise ValueError("negative Ceff")
    i={"min":0,"typ":1,"max":2}[side]
    return -math.log(TPS38_TRIP_TIMING_FACTORS[i])*TPS38_RCTR_KOHM[i]*ceff_uf

def static_9v_budget(trip_v,known_current_ua=0.,rv_factor=1.0):
    r=sum(R_VS)*rv_factor
    budget_ua=(VIN9-trip_v)*1e6/r
    return {"trip_v":trip_v,"r_effective_ohm":r,
            "max_total_precharge_current_for_9v_trip_ua":budget_ua,
            "included_current_ua":known_current_ua,
            "remaining_current_allowance_ua":budget_ua-known_current_ua,
            "total_startup_current_guaranteed_under_allowance":False}

def manufacturer_bounds():
    # trip_v from existing REV5 P02 on/off analysis (not a full new max):
    rise_v_rev5_model_upper=7.51
    # Only values for which manufacturer has certified corners given as bounds.
    caps=[None,0.05,0.1,0.126225,0.33,0.396]
    return {
      "analysis":"TI_SUPERVISOR_CTR_MANUFACTURER_EQUATION_AND_VS_STATIC_BUDGET",
      "ti_TPS38":{
         "rctr_internal_kohm_manufacturer_min_typ_max":TPS38_RCTR_KOHM,
         "CTR1_C311_nominal_uf":TPS38_CCTR_INSTALLED_UF,
         "CTR_Ceff_min_and_max_at_bias_temp_aging_uf":None,
         "ctr_t_no_cap_min_typ_max_ms_including_por":[None,None,None],
         "startup_delay_no_cap_max_ms_from_TI":2.0,
         "delay_capacitor_formula_components_ms":[
            {"ceff_uf":c,"minimum_cap_component_ms":tctr_bound_ms(c,"min"),
             "typical_cap_component_ms":tctr_bound_ms(c,"typ"),
             "maximum_cap_component_ms":tctr_bound_ms(c,"max")} for c in caps],
         "nominal_420ms_result_is_conditional_on_330nF_actual":True,
         "residual_CTR_discharge_rule_from_TI":
              "Fault duration greater than 5 percent of delay needed for full-discharge assurance in vendor application text; re-test rapid brownout.",
         "reset_remaining_at_partial_charge_on_brownout_ms":None,
      },
      "ti_LM74930":{
        "VS_operating_min_max_v":[4.0,65.0],
        "shutdown_current_max_ua_12v_test_condition":LM74930_SHDN_MAX_UA,
        "on_current_max_ua_12v_test_condition":LM74930_ON_IQ_MAX_UA,
        "actual_pre_enable_VS_draw_max_9v_and125C_ua":None,
        "actual_charge_pump_additional_VS_draw_max_9v_ua":None,
        "VS_Ceff_1_plus_10_plus_10uF_min_real_uf":None,
        "source_a_recovery_time_before_D302_replenishes_VS_max_ms":None,
      },
      "D306_comchip":{
        "MPN":"ACZRC5370B-G",
        "IR_max_ua_at_42p6v_test":D306_IR_TEST_MAX_UA,
        "IR_max_ua_at_VS9v_and125C":None,
        "9v_start_requires_extra_leakage_test":True,
      },
      "static_threshold_budgets":[
           static_9v_budget(rise_v_rev5_model_upper, rv_factor=x)
           for x in (0.99,1.0,1.01,1.0201)],
      "cannot_claim_GUARANTEED_9v":True,
    }
if __name__=="__main__":
    print(json.dumps(manufacturer_bounds(),indent=2,sort_keys=True))
