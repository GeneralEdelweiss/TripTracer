#!/usr/bin/env python3
"""Documented, strict safety-evidence gate for current TripPower REV2.
Script success means calculations/data limitations are correctly preserved,
NOT that 9-30V operation or 202V safety is proven. No fabricated SPICE.
"""
import json
from pathlib import Path
base=Path("hardware/modules/TripPower_5V2A")
sch=(base/"03_VS_READY_TPS3760.kicad_sch").read_text()
prot=(base/"01_Protection_LM74930.kicad_sch").read_text()
for ref,mpn in (("Q303","PMBTA92-Q"),("Q304","PMBTA42-Q"),("Q305","PMBTA42-Q")):
 assert f'(property "Reference" "{ref}"' in sch and mpn in sch,ref
assert "825k 1% VS-SENSE" in sch and "1M 1% RESET FEEDBACK" in sch
assert "68k PNP OUTPUT CURRENT LIMIT" in prot and "22k EN PULLDOWN" in prot
assert "BAS116Q_A1_K3_NC2" in prot
# Specified by TI, complete -40..125C:
EN_OFF_MAX=0.41
EN_ON_MIN=1.05
EN_INPUT_LEAK_MAX=0.2e-6
# Nexperia ICBO max of PMBTA92-Q at 25C with emitter OPEN is not
# a max ICEO at 125C with emitter connected & base biased through R336.
PMBTA92_125C_MAX_ICEO_A=None
# Nexperia hFE(min) tested at IC=1mA, VCE10V, TA25C; no guaranteed
# min hFE at required IC tens of uA and TA -40 or 125C.
PMBTA92_MIN_HFE_AT_50UA_ALL_TEMP=None
PMBTA42_MIN_HFE_AT_20UA_ALL_TEMP=None
RVS=9900.0
R_OUT=68000.0
R_GND=22000.0
R_GND_MAX=R_GND*1.01
R_READY=825e3
R_SENSE=100e3
R_FB=1e6
# Last measured in repo's previous Rev2 script after RESET loading,
# not the earlier unloaded nominal 7.974 V. 1% resistors + TI
# reference and illustrative Q304 Vbe .55-.95V/sense bias, not a
# qualified bound when transistor temperature/leakage is unknown.
REV2_RISE_NOM=8.221
REV2_RISE_MODELED_MAX=8.539
# Vehicle VIN=9 at TripPower connector, VS leakage budget evaluated at
# upper threshold. Additional dynamic I(VS,t) not guaranteed by data.
VIN_MIN=9.0
I_VS_TOTAL_AT_ON=(VIN_MIN-REV2_RISE_MODELED_MAX)/RVS
assumed_off_current_components_ua={"LM74930_shutdown":5.0,
  "TPS3760_supply":2.6,"C308_leakage_scenario":10.0,
  "sense_divider_scenario":9.0,"reset_and_bias_scenario":8.0}
I_MODEL_SUM=sum(assumed_off_current_components_ua.values())*1e-6
UNBOUNDED_ADDITIONAL_LEAK_MARGIN_A=I_VS_TOTAL_AT_ON-I_MODEL_SUM
# OFF - actual 125C requirement from ENF min and EN pin leak:
Q303_125C_MAX_COLLECTOR_LEAK_ALLOWED_A=EN_OFF_MAX/R_GND_MAX-EN_INPUT_LEAK_MAX
# ON - min collector current to lift LM74930 EN past guaranteed high:
I_PNP_MIN_COLLECTOR_ON_A=EN_ON_MIN/R_GND
I_PNP_BASE_NOMINAL_A=max(0,(8.0-0.7)/220e3-0.7/47e3)
I_READY_NPN_BASE_NOM_A=max(0,(8.0-0.7)/(1e6+1e6)-0.7/1e6)
PNP_MIN_BETA_REQUIRED_SENSITIVITY=I_PNP_MIN_COLLECTOR_ON_A/I_PNP_BASE_NOMINAL_A
READY_NPN_MIN_BETA_REQUIRED_SENSITIVITY=I_PNP_BASE_NOMINAL_A/I_READY_NPN_BASE_NOM_A
C_VS_EFFECTIVE_ASSUMED_F=8.5e-6
# Rectangular hypothesized dynamic pump VS input draw, only sensitivity:
C_VS_DELTA_AT_3MS_5MA=5e-3*.003/C_VS_EFFECTIVE_ASSUMED_F
C_VS_DELTA_AT_3MS_8MA=8e-3*.003/C_VS_EFFECTIVE_ASSUMED_F
# Both scenarios intentionally exclude dynamic replenishment and IQ;
# no actual guaranteed charge pump input draw or all-temp Ceff.
assert 0<UNBOUNDED_ADDITIONAL_LEAK_MARGIN_A<15e-6
assert 18e-6<Q303_125C_MAX_COLLECTOR_LEAK_ALLOWED_A<19e-6
assert 45e-6<I_PNP_MIN_COLLECTOR_ON_A<50e-6
assert 2<PNP_MIN_BETA_REQUIRED_SENSITIVITY<3
assert 5<READY_NPN_MIN_BETA_REQUIRED_SENSITIVITY<7
assert C_VS_DELTA_AT_3MS_8MA>2.8
# No acceptance without guaranteed 125C I_CEO, min hFE at actual
# current and temps, min actual Ceff and maximal dynamic I_VS(t).
guaranteed_off=(PMBTA92_125C_MAX_ICEO_A is not None and
 PMBTA92_125C_MAX_ICEO_A<Q303_125C_MAX_COLLECTOR_LEAK_ALLOWED_A)
guaranteed_on=(PMBTA92_MIN_HFE_AT_50UA_ALL_TEMP is not None and
 PMBTA42_MIN_HFE_AT_20UA_ALL_TEMP is not None)
assert not guaranteed_off and not guaranteed_on
print(json.dumps({
 "gate":"TripPower_REV2_2026-10-15_full_temperature_and_9V_boot",
 "result":"BLOCKED_INSUFFICIENT_MANUFACTURER_GUARANTEES",
 "datasheet_documented":"Nexperia PMBTA92-Q & PMBTA42-Q only give min hFE at IC>=1mA/25C; PMBTA92 ICBO at25C emitter-open is not ICEO at125C; TI LM74930 charge pump CAP source current is NOT 9V VS input supply current",
 "pins":"Q303/Q304/Q305 B1/E2/C3, D305 BAS116Q A1/K3/NC2, all pin-mapping covered by native KiCad CI",
 "safe_off_requirement":{"LM74930_EN_FALL_MIN_V":EN_OFF_MAX,
 "R316_max_ohm":R_GND_MAX,
 "Q303_collector_leak_125C_must_be_below_uA":round(Q303_125C_MAX_COLLECTOR_LEAK_ALLOWED_A*1e6,2),
 "Q303_manufacturer_guaranteed_125C_current":"NOT_AVAILABLE",
 "guaranteed":guaranteed_off},
 "safe_on_requirement":{"LM74930_EN_RISE_MAX_V":EN_ON_MIN,
 "Q303_collector_current_required_at_EN_1p05_uA":round(I_PNP_MIN_COLLECTOR_ON_A*1e6,2),
 "Q303_nominal_8V_base_drive_uA":round(I_PNP_BASE_NOMINAL_A*1e6,2),
 "Q304_nominal_8V_base_drive_uA":round(I_READY_NPN_BASE_NOM_A*1e6,2),
 "required_PNP_min_gain_nominal":round(PNP_MIN_BETA_REQUIRED_SENSITIVITY,2),
 "required_READY_NPN_min_gain_nominal":round(READY_NPN_MIN_BETA_REQUIRED_SENSITIVITY,2),
 "manufacturer_guaranteed_gain_under_actual_temperature_and_current":"NOT_AVAILABLE",
 "guaranteed":guaranteed_on},
 "nine_volt_cold_boot":{"VIN_at_module_V":VIN_MIN,
 "current_REV2_model_upper_rising_threshold_V":REV2_RISE_MODELED_MAX,
 "R313_to_R315_ohms":RVS,
 "maximum_available_VS_precharge_feed_at_threshold_uA":round(I_VS_TOTAL_AT_ON*1e6,2),
 "illustrative_OFF_current_ua":assumed_off_current_components_ua,
 "remaining_UNBOUNDED_leakage_and_model_error_budget_uA":round(UNBOUNDED_ADDITIONAL_LEAK_MARGIN_A*1e6,2),
 "Ceff_assumed_uF":8.5,
 "hypothetical_3ms_5mA_VS_drop_V":round(C_VS_DELTA_AT_3MS_5MA,3),
 "hypothetical_3ms_8mA_VS_drop_V":round(C_VS_DELTA_AT_3MS_8MA,3),
 "actual_guaranteed_dynamic_VS_input_current":"NOT_SPECIFIED",
 "start_guaranteed":False},
 "safety": {"9_to_30V_start_certified":False,
 "202V_350ms_load_dump_SOA_proven":False,
 "external_F_MAIN_fault_coordination_proven":False,
 "automotive_manufacturing_release":False},
 "required_next_evidence":["Manufacturer guaranteed all-temp min hFE and max leakage at 10-100uA, or change active circuit",
 "Actual VS startup current envelope versus 9V/temperature and C302/C308 Ceff/ESR",
 "Measure -40,25,85,125C; 9,10,12,13.8,24,30V; AUTO/RUN VIN0; all loads and full transient validation"]
 },indent=2,ensure_ascii=False))
