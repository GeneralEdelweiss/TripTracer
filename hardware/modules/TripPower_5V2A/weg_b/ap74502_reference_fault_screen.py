#!/usr/bin/env python3
"""Independent AP74502HQ + TPS1HTC30A automotive reference screen.

Datasource: Diodes AP74502Q/AP74502HQ DS47093 Rev2-2 Oct2025 pp4,15-16,
TI TPS1HTC30-Q1 SLVSGL4A May2026, distributor snapshots Oct2026.
Checks static tolerances and explicit illustrative fault/energy scenarios.
NOT electrical simulation, ISO proof, hot-SOA or fab release.
Run: python3 hardware/modules/TripPower_5V2A/weg_b/ap74502_reference_fault_screen.py
"""
import json, math

VIN_NORMAL_MIN=9.
VIN_NORMAL_MAX=30.
VIN_DUMP=200.
DUMP_DURATION=0.35

def trip(threshold, top, bottom, i_pin=0.):
    """Physical sense KCL: V_bat=V_trip(1+Rtop/Rbottom)+I_pin*Rtop."""
    return threshold*(1+top/bottom)+i_pin*top

def ov_corners():
    top=100000.; bottom=3500.; t=.01; leakage=110e-9
    min_top,max_top=top*(1-t),top*(1+t)
    min_bot,max_bot=bottom*(1-t),bottom*(1+t)
    return {
        "rising_v":{"min":trip(1.165,min_top,max_bot,-leakage),
                    "typ":trip(1.25,top,bottom),
                    "max":trip(1.333,max_top,min_bot,+leakage)},
        "falling_v":{"min":trip(1.063,min_top,max_bot,-leakage),
                     "typ":trip(1.143,top,bottom),
                     "max":trip(1.222,max_top,min_bot,+leakage)},
        "input_on_at_30_by_static_threshold_only":trip(1.165,min_top,max_bot,-leakage)>30,
        "restarts_at_30_by_static_threshold_only":trip(1.063,min_top,max_bot,-leakage)>30,
        "VOUT_SAFE_DURING_200V_TRANSIENT":False,
        "FET_GATE_OFF_TIMING_VERIFIED":False,
    }

def supply_60v_zener(vin=200.,z=60.,r=10000.,seconds=.35):
    """Manufacturer static assumed clamp; actual 350ms hot SOA unknown."""
    i=max((vin-z)/r,0.)
    return {"input_v":vin,"clamp_assumption_v":z,"r_ohm":r,
            "i_ideal_a":i,"resistor_power_w":i*i*r,
            "resistor_energy_j":i*i*r*seconds,
            "zener_power_w":i*z,"zener_energy_j":i*z*seconds,
            "thermal_pulse_certified":False}

def zener_open(c=1e-6,r=10000.,v_source=200.,initial=0.,seconds=.35):
    if not 0<=initial<=v_source or c<=0 or r<=0: raise ValueError("invalid RC")
    tau=r*c
    def t_to(level):
        if level<=initial:return 0.
        if level>=v_source:return None
        return -tau*math.log((v_source-level)/(v_source-initial))
    return {"model":"unclamped ideal 1uF VIN decoupling, zero load",
            "vin_pin_at_350ms_v":v_source+(initial-v_source)*math.exp(-seconds/tau),
            "seconds_to_75v":t_to(75.),"seconds_to_80v":t_to(80.),
            "device_80v_abs_max_guaranteed":False}

def zener_short(v=200.,r=10000.,seconds=.35):
    i=v/r
    return {"assumed_vin_pin_v":0.,"r_ohm":r,"resistor_w":v*i,
            "resistor_energy_j":v*i*seconds,"F_MAIN_clear_20mA_guaranteed":False}

def resistor_ov_200v(r_top=100000.,r_bottom=3500.,seconds=.35):
    i=200./(r_top+r_bottom)
    return {"OV_pin_ideal_v":i*r_bottom,
            "OV_top_R_power_w":i*i*r_top,
            "OV_top_R_energy_j":i*i*r_top*seconds,
            "split_two_equal_R_power_w_each":i*i*r_top/2.,
            "split_two_equal_R_energy_j_each":i*i*r_top/2.*seconds,
            "actual_1206_125C_350ms_pulse_proven":False}

def output_current_screen(eta=.8, vbat=9., raw_a=1.,r_highside_typ=.03,
                          r_highside_max=.055):
    i=10./eta/vbat+raw_a
    return {"assumed_efficiency":eta,"buck_5v_output_w":10,
            "normal_9v_input_a":i,
            "tps1htc30_typ_conduction_w":i*i*r_highside_typ,
            "tps1htc30_max_r_conduction_w":i*i*r_highside_max,
            "setpoint_assumption_a":4.0,
            "current_limit_at_plus_minus20pct_a":[3.2,4.8],
            "hot_125c_thermal_and_current_limit_proven":False}

def core_cost_eur():
    """EUR net/unit: source MPN URL and quantity 1,10,100, EXCLUDES other BOM."""
    source={
       "AP74502HQTA8-7":{
          "url":"https://eu.mouser.com/en/ProductDetail/Diodes-Incorporated/AP74502HQTA8-7",
          "eur":[.636,.450,.352],
          "quantity_available_snapshot":505},
       "TPS1HTC30AQPWPRQ1":{
          "url":"https://www.mouser.de/de/ProductDetail/Texas-Instruments/TPS1HTC30AQPWPRQ1",
          "eur":[4.39,3.35,2.80],
          "quantity_available_snapshot":50},
       "LM74930QRGERQ1":{
          "url":"https://www.digikey.de/en/products/detail/texas-instruments/LM74930QRGERQ1/22147207",
          "eur":[4.42,3.369,2.8175],
          "quantity_available_snapshot":"UNVERIFIED_ON_CURRENT_DAY"},
       "LMR38020SQDDARQ1":{
          "url":"https://www.digikey.de/de/products/detail/texas-instruments/LMR38020SQDDARQ1/18177286",
          "eur":[3.91,2.965,2.4703],
          "quantity_available_snapshot":"UNVERIFIED_ON_CURRENT_DAY"},
    }
    rows=[]
    for i,qty in enumerate((1,10,100)):
        a=source["LM74930QRGERQ1"]["eur"][i]+source["LMR38020SQDDARQ1"]["eur"][i]
        b=sum(source[p]["eur"][i] for p in
              ("AP74502HQTA8-7","TPS1HTC30AQPWPRQ1","LMR38020SQDDARQ1"))
        rows.append({"quantity":qty,"A_two_IC_eur_net":round(a,4),
                     "B_three_IC_eur_net":round(b,4),
                     "B_minus_A_IC_only_eur":round(b-a,4),
                     "missing_B_extra_HV_MOSFET_and_full_passives":True})
    return {"sources":source,"price_rows":rows,
            "complete_1_10_100_eur_qualifiable":False,
            "quotes_are_NOT_shipping_vat_assembly_or_entire_BOM":True}

def fault_matrix():
    return [
      {"fault":"external Q1 D-S welded","legacy_REV5":"SOURCE_A via D302 may backfeed VS",
       "AP74502_alternative":"Other independently rated high-voltage series FET MAY interrupt 200V, if gate off and body diode reverse",
       "guaranteed":False},
      {"fault":"AP supply zener Dz OPEN","legacy_REV5":"D301 OPEN overcharges VS",
       "AP74502_alternative":"After R1, VIN IC pin can rise to 200V; only 80V ABS -> dangerous",
       "guaranteed":False},
      {"fault":"AP supply zener Dz SHORT","legacy_REV5":"D301 SHORT pulse burden RVS resistors",
       "AP74502_alternative":"10k R1 carries 20mA at 200V, 4W / 1.4J; F_MAIN cannot be relied on",
       "guaranteed":False},
      {"fault":"single external HV FET short + OVP","legacy_REV5":"Q301 short -> D302 bypass + Q302 60V exposed",
       "AP74502_alternative":"One remaining >=200V FET provides possible redundant off",
       "guaranteed":False},
      {"fault":"both external FET D-S SHORT","legacy_REV5":"High voltage may propagate",
       "AP74502_alternative":"High voltage can reach TPS1HTC30 (60V), LMR38020 (80V), RAW",
       "guaranteed":False},
      {"fault":"AP74502 fail to assert GATE OFF","legacy_REV5":"LM74930 output danger",
       "AP74502_alternative":"200V at input can propagate even with good FETs",
       "guaranteed":False},
    ]

def evidence():
    ov=ov_corners()
    return {
      "stage":"INDEPENDENT_REFERENCE_FEASIBILITY_STOP_NOT_FAB",
      "targets":{"operation_v":[9,30],"output_5v_a":2,"raw_aux_a":1,
                 "dump_v":200,"dump_seconds":.35,"ambient_c":[-40,125]},
      "manufacturer_AP74502HQ":{"VIN_operating_v":[4,75],"VIN_ABS_MAX_v":80,
                                "operating_IQ_max_uA":84,
                                "minimum_startup_v_max_spec_v":3.9,
                                "standby_IQ_max_uA":1.5,
                                "does_not_integrate_current_limit":True},
      "ov_static":ov,
      "AP_frontend_R1_zener":supply_60v_zener(),
      "AP_zener_open":zener_open(),
      "AP_zener_open_initial_60":zener_open(initial=60.),
      "AP_zener_short":zener_short(),
      "AP_ov_sense_200v_resistor":resistor_ov_200v(),
      "9v_input_load_hypothesis":output_current_screen(),
      "costs":core_cost_eur(),
      "fault_matrix":fault_matrix(),
      "potentially_better_than_legacy_fault_isolation_without_D302":True,
      "proven_fully_safe_architecture":False,
      "200v_350ms_vendor_fet_SOA_verified":False,
      "dZ_open_fault_safe":False,
      "qualified_9v_start":False,
      "qualified_30v_restart":False,
      "qualified_Tj_125_2A_plus_RAW":False,
      "real_connected_KiCad":False
    }

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
