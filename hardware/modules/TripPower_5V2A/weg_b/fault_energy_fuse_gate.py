#!/usr/bin/env python3
"""TripPower Weg B: 200V/350ms single-fault F_MAIN / thermal-energy screen.

No manufacturer's I²t is transformed into an invented guaranteed opening time.
No claimed ISO waveforms, hot SOA, contact arc extinction or safety release.

Run:
  python3 hardware/modules/TripPower_5V2A/weg_b/fault_energy_fuse_gate.py
  python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_b -p 'test_fault_energy_fuse_gate.py' -v

Sources (read exact provenance for voltage/current/conditional I²t):
- Eaton FWC-4A10F manufacturer official sku page, DC >=500V, aR, 4A,
  5.2 A²s pre-arc, 32 A²s clearing as CATALOG INDICES (not a time guarantee);
  conservative use of lower 500VDC despite conflicting Eaton regional listings.
- Weidmuller GZ 5.0A/F, 1460620000: DigiKey de 5A 500V AC/DC,
  50kA listing; manufacturer's original DC interrupt proof pending.
- Littelfuse MINI series rated 32VDC (not 200VDC!).
- TI LM74930-Q1: A to GND recommended <=65V, absolute <=70V.
- Vishay SQM10250E: VDS 250V, SOA at 25C only, not 350ms/125C.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json
import math

PULSE_V=200.0
PULSE_S=.350
TZ=56.0
VF_HYP=.7
SYSTEM_AMBIENT_C=125.0

@dataclass(frozen=True)
class Fuse:
    mpn:str
    rated_a:float
    dc_v_rating:float
    interrupt_dc_a:float | None
    i2t_prearc_catalog_a2s:float | None
    i2t_clearing_catalog_a2s:float | None
    origin:str
    availability:str
    prices_eur_net_1_10_100:tuple[float,float,float] | None
    supported_operating_to_125c:bool | None
    holder_200vdc_qualified:bool
    full_fault_current_range_dc_qualified:bool
    notes:str
    min_dc_break_current_a:float | None = None
    manufacturer_max_clear_at_min_break_s:float | None = None
    manufacturer_ambient_range_c:tuple[float,float] | None = None

FUSES={
 "AUTO_BLADE_32V_COMPARISON_ONLY":Fuse(
     mpn="Littelfuse MINI family: 32VDC (no exact 5A BOM freeze)",
     rated_a=5,dc_v_rating=32,interrupt_dc_a=None,
     i2t_prearc_catalog_a2s=None,i2t_clearing_catalog_a2s=None,
     origin="https://www.littelfuse.com/products/fuses-overcurrent-protection/fuses/automotive-fuses/blade-fuses-shunt",
     availability="family exists; NOT FIT FOR 200V DC breaking",
     prices_eur_net_1_10_100=None,supported_operating_to_125c=None,
     holder_200vdc_qualified=False,full_fault_current_range_dc_qualified=False,
     notes="32VDC is insufficient for interrupting 200VDC even if 5A continuous is acceptable."),
 "WEIDMULLER_1460620000":Fuse(
     mpn="Weidmuller GZ 5.0A/F 1460620000",
     rated_a=5,dc_v_rating=500,interrupt_dc_a=50000,
     i2t_prearc_catalog_a2s=None,i2t_clearing_catalog_a2s=None,
     origin="https://www.digikey.de/de/products/detail/weidm%C3%BCller/1460620000/22132585",
     availability="20 pcs distributor snapshot 2026-10-15; 6.3x32 cartridge",
     prices_eur_net_1_10_100=(3.08,2.361,1.8065),
     supported_operating_to_125c=False,holder_200vdc_qualified=False,
     full_fault_current_range_dc_qualified=False,
     notes="Weidmueller manufacturer specifies -5..40C AMBIENT; fails TripPower -40..125C mounting. DC clearing curves and fuse holder also absent.",
     manufacturer_ambient_range_c=(-5.,40.)),
 "EATON_FWC-4A10F":Fuse(
     mpn="Eaton Bussmann FWC-4A10F",
     rated_a=4,dc_v_rating=500,interrupt_dc_a=10000,
     i2t_prearc_catalog_a2s=5.2,i2t_clearing_catalog_a2s=32.0,
     origin="https://www.eaton.com/us/en-us/skuPage.FWC-4A10F.html",
     availability="manufacturer active 10x38; distributor stock/price unconfirmed",
     prices_eur_net_1_10_100=None,supported_operating_to_125c=None,
     holder_200vdc_qualified=False,full_fault_current_range_dc_qualified=False,
     notes="Eaton regions disagree 500/700 DC vs generic 600 V; use only conservative 500VDC; aR partial-range semiconductor protection; catalog 5.2/32 I2t NOT a 350ms guarantee."),
 "MERSEN_MEV55C5":Fuse(
     mpn="Mersen MEV55C5 (ferrule clip)",
     rated_a=5,dc_v_rating=550,interrupt_dc_a=20000,
     i2t_prearc_catalog_a2s=None,i2t_clearing_catalog_a2s=None,
     origin="https://www.mersen.com/en/products/evpack-fuse-mev55-550-vdc-max-l-r-less-or-equal-1ms-5-50a/mev55c5",
     availability="Manufacturer MPN current. EU secondary distributor shows ~EUR46.24/1 with RFQ, authorized stock NOT independently confirmed",
     prices_eur_net_1_10_100=None,supported_operating_to_125c=True,
     holder_200vdc_qualified=False, full_fault_current_range_dc_qualified=False,
     notes="ISO8820-8 automotive family, -40..125C, 550VDC, 20kA L/R<=1ms; DC min breaking current 10A and MAX clearance time at 10A of 10s, so cannot GUARANTEE 350ms cut; ferrule needs 200VDC-appropriate accessible holder. Do NOT silently use -P 10ms table anomaly.",
     min_dc_break_current_a=10.,
     manufacturer_max_clear_at_min_break_s=10.0,
     manufacturer_ambient_range_c=(-40.,125.))
}

def normal_input_current(vin=9., efficiency=.80, raw_input_a=1., vout=5.,iout=2.):
    assert vin>0 and 0<efficiency<=1 and raw_input_a>=0
    return {"vin_v":vin,"efficiency_assumed":efficiency,
            "raw_input_a_assumed":raw_input_a,
            "main_input_a":vout*iout/(vin*efficiency)+raw_input_a,
            "fuse_125c_carry_guaranteed":False}

def qualification(fuse:Fuse, source_open_v=200., prospective_short_a=None):
    voltage_ok=fuse.dc_v_rating>=source_open_v
    current_cap_ok=(prospective_short_a is not None and
                    fuse.interrupt_dc_a is not None and
                    prospective_short_a<=fuse.interrupt_dc_a)
    return {"MPN":fuse.mpn,"DC_voltage_rating_sufficient":voltage_ok,
        "DC_interrupt_capacity_sufficient_if_prospective_given":current_cap_ok,
        "complete_selectivity_time_energy_and_holder_proven":False,
        "safe_125C_carry_proven":fuse.supported_operating_to_125c is True,
        "fuse_clearing_range_includes_this_current": (
            prospective_short_a is not None and
            fuse.min_dc_break_current_a is not None and
            prospective_short_a >= fuse.min_dc_break_current_a and
            (fuse.interrupt_dc_a is None or prospective_short_a<=fuse.interrupt_dc_a)
        ),
        "supplier_min_dc_break_current_a":fuse.min_dc_break_current_a,
        "supplier_max_clear_at_min_break_s":fuse.manufacturer_max_clear_at_min_break_s,
        "full_overload_range_DC_qualified":fuse.full_fault_current_range_dc_qualified,
        "holder_200VDC_qualified":fuse.holder_200vdc_qualified}

def i2t_350ms_constant(i_a,seconds=PULSE_S):
    assert i_a>=0 and seconds>=0
    return i_a*i_a*seconds

def i2t_catalog_screen(fuse:Fuse, amps, seconds=PULSE_S):
    """NEVER estimate actual t_open from one prearc/clearing I2t value:
    those indices are measured at specific test currents and voltage, not a
    complete DC time-current and arcing curve over 0.35 sec.
    """
    exposure=i2t_350ms_constant(amps,seconds)
    return {"fault_current_a":amps,"duration_s":seconds,
            "integral_a2s":exposure,
            "prearc_catalog_a2s":fuse.i2t_prearc_catalog_a2s,
            "clearing_catalog_a2s":fuse.i2t_clearing_catalog_a2s,
            "eligible_to_claim_fuse_cleared":False,
            "reason":"Need vendor DC time-current min/max+arc clearing curves for real I, V, temp, source L; I2t indices not opening time."}

def zener_branch(source_r_ohms,fault_r_ohms=0.,
                 source_v=PULSE_V,z_v=TZ,diode_v=VF_HYP,duration=PULSE_S):
    """Illustrative Q301 D-S welded, SOURCE_A -> D302 forward -> D301 56V.
    Includes external source resistance + optional resistive damaged IC path.
    Fixed Zener V is deliberately NOT a physical device model.
    """
    assert source_r_ohms>0 and fault_r_ohms>=0 and duration>=0
    i=max(0.,(source_v-z_v-diode_v)/(source_r_ohms+fault_r_ohms))
    return {"source_r_ohm":source_r_ohms,"fault_r_ohm":fault_r_ohms,
            "assumed_ideal_zener_v":z_v,"assumed_ideal_diode_v":diode_v,
            "current_a":i, "i2t_a2s":i2t_350ms_constant(i,duration),
            "zener_energy_j":i*z_v*duration,
            "d302_diode_energy_j":i*diode_v*duration,
            "source_resistor_energy_j":i*i*source_r_ohms*duration,
            "fault_resistor_energy_j":i*i*fault_r_ohms*duration,
            "assumes_current_persists_full_duration":True,
            "real_zener_fails_or_hot_SOA_proven":False,
            "external_fuse_will_clear":False}

def fault_resistive(source_r_ohms,fault_r_ohms,source_v=PULSE_V,duration=PULSE_S):
    """Single degraded silicon/PCB path modeled as positive resistive load.
    No Zener clamp needed: faulty IC alone can absorb significant energy.
    """
    assert source_r_ohms>0 and fault_r_ohms>0 and duration>=0
    i=source_v/(source_r_ohms+fault_r_ohms)
    return {"source_r_ohm":source_r_ohms,"fault_r_ohm":fault_r_ohms,
            "current_a":i,"fault_power_w":i*i*fault_r_ohms,
            "fault_energy_j":i*i*fault_r_ohms*duration,
            "i2t_a2s":i2t_350ms_constant(i,duration),
            "temperature_safety_established":False,
            "fuse_clearing_guaranteed":False}

def prospective_short(source_r_ohms, v=PULSE_V):
    assert source_r_ohms>0
    return v/source_r_ohms

def direct_pin_rating_exposure(source_a_v=200.,q302_drain_v=0.,
                               q301_extra_overshoot_v=0.):
    """Manufacturer absolute specs, conditional potentials, not real waveforms:
    U301 LM74930 A pin +70V abs; Q302 60V VDS abs; Q301 250V VDS abs.
    MOSFET source=200 does NOT imply VDS=200 unless drain potential is known.
    """
    q302_vds=abs(source_a_v-q302_drain_v)
    vds_q301_off=source_a_v+q301_extra_overshoot_v
    return {
      "hypothetical_SOURCE_A_v":source_a_v,
      "LM74930_A_to_GND_abs_max_v":70.,
      "LM74930_A_over_abs_by_v":max(0.,source_a_v-70.),
      "Q302_VDS_abs_max_v":60.,
      "Q302_drain_assumption_v":q302_drain_v,
      "Q302_conditional_VDS_v":q302_vds,
      "Q302_rating_exceeded_in_this_corner":q302_vds>60,
      "Q301_VDS_abs_max_v":250.,
      "Q301_normal_OFF_conditional_vds_v":vds_q301_off,
      "Q301_51v_overshoot_exceeds_250v":200.+51.>250.,
      "Vishay_hot_switching_SOA_350ms_proven":False,
      "TVS_D303_D304_max_200v_clamp_proven":False,
      "manufacturer_A_to_GND_spec":"https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf",
      "BAV21WQ_average_forward_current_rating_a":.4,
      "BAV21WQ_200V_VR_is_REVERSE_not_forward_limit":True
    }

def fuse_no_action_counterexample(amps,fuse:Fuse,energy_j):
    """Below In, the fuse is not required to interrupt; do not infer it will
    have melted. Even above In a 350ms time-to-clear is manufacturer dependent.
    """
    return {"fault_a":amps,"fuse_rating_a":fuse.rated_a,
            "current_not_above_nominal":amps<=fuse.rated_a,
            "energy_still_dissipated_j_without_clearing":energy_j,
            "guaranteed_350ms_protection_by_FMAIN":False}

def external_cable_screen(fuse:Fuse,rs,wire_R,amps=None,seconds=PULSE_S):
    """Copper I2t is NOT declared safe without cable cross section, insulation,
    harness bundling, initial temperature, terminals and melt/current curves.
    """
    i=prospective_short(rs) if amps is None else amps
    return {"prospective_or_assumed_a":i,"source_ohm":rs,
            "wire_ohm":wire_R,"wire_joule_energy_if_uncleared_j":i*i*wire_R*seconds,
            "wire_i2t_a2s":i2t_350ms_constant(i,seconds),
            "fuse_dc_voltage_ok":fuse.dc_v_rating>=PULSE_V,
            "fuse_interrupt_a_ok":fuse.interrupt_dc_a is not None and i<=fuse.interrupt_dc_a,
            "holder_high_voltage_hot_rating_known":False,
            "cable_insulation_thermal_capacity_known":False,
            "fuse_total_clearing_vs_copper_damage_proven":False}

def fmea():
    # Severity is potential harm, NOT assertion that fire will happen.
    return [
        dict(rank=1,id="B5-01",failure="A: Q301 drain-source short; 200V SOURCE_A -> U301.A/CS/Q302.S",
             class_="POTENTIALLY_DANGEROUS_SINGLE",
             hazard="A pin 70V ABS and Q302 60V VDS are overstressed; uncertain IC short modes -> local heat/RAW/PCB energy",
             mitigation="Measure real 200V prospective source and fault IV; fail-open/containment + DC-rated F_MAIN; otherwise independent disconnect",
             evidence="Physical pin topology and TI/Vishay rated maxima; actual device failure mode unknown"),
        dict(rank=2,id="B5-02",failure="B/C: input-side common-source FET drain-source welded",
             class_="POTENTIALLY_DANGEROUS_SINGLE",
             hazard="Output-side body diode can conduct input -> 60/80V downstream at 200V; no redundant positive blocking",
             mitigation="Fault-inject with current-limited generator; assess safe-sacrifice energy/fuse vs independent positive block",
             evidence="Directed diode network; thermal output failure unspecified"),
        dict(rank=3,id="B5-03",failure="A: Q301 short feeds D302 -> D301 VS, bypass R313-R315",
             class_="POTENTIALLY_DANGEROUS_SINGLE",
             hazard="Unbounded through-diode transient current at VS clamp, F_MAIN may see less than nominal",
             mitigation="Separately current-limit SOURCE_A->VS without compromising 9V start; or remove feed with proven startup method",
             evidence="Native-protection net topology; illustrative current-energies only"),
        dict(rank=4,id="B5-04",failure="A: D301 open",
             class_="POTENTIALLY_DANGEROUS_SINGLE",
             hazard="Unclamped VS 65V IC and 100V capacitors overvoltage from RVS, low fault current will not clear ampere fuse",
             mitigation="Qualified limited-energy supply + proven nonigniting failure or truly independent clamp",
             evidence="RC upper-tendency; no proven internal peak limit"),
        dict(rank=5,id="B5-05",failure="A/B: TVS stack fails short (or shunt short)",
             class_="POTENTIALLY_DANGEROUS_SINGLE",
             hazard="High 200V prospective current in TVS and cable; DC arc/thermal threat if F_MAIN not HV DC suitable",
             mitigation="Coordinate true DC breaker with available short current and cable I2t; pulse test",
             evidence="DC voltage and interrupt rating are distinct from 32V fuse nameplate"),
        dict(rank=6,id="B5-06",failure="A: Q301 short plus D301 open",
             class_="POTENTIALLY_DANGEROUS_DOUBLE",
             hazard="D302 supplies VS with no shunt; destruction probable; energy unknown",
             mitigation="Common cause and realistic conditional probability; safe destructive-fault containment",
             evidence="Two faults, no assumed manufacturer safe-open"),
        dict(rank=7,id="B5-07",failure="B/C: two common-source MOSFET D-S short",
             class_="POTENTIALLY_DANGEROUS_DOUBLE",
             hazard="No electronic series cutoff, multiple unprotected ICs potentially at 200V",
             mitigation="F_MAIN fault-envelope or truly independent HV disconnect",
             evidence="Directed-graph state"),
        dict(rank=8,id="B5-08",failure="F_MAIN has only 32/58V DC breaking rating",
             class_="POTENTIALLY_DANGEROUS_SYSTEMATIC",
             hazard="May sustain DC arc at 200V after element melts",
             mitigation="Specify F_MAIN with >=200V DC interruption and matched approved holder; check 125C",
             evidence="Littelfuse voltage rating; breaking capacity not interchangeable"),
        dict(rank=9,id="B5-09",failure="A: MOSFET turnoff with Q301 intact",
             class_="POTENTIALLY_DANGEROUS_NORMAL_TRANSIENT",
             hazard="200V plus 50V overshoot exceeds 250V VDS; hot SOA not shown",
             mitigation="Source waveform including L and measured VDS, E, hot SOA",
             evidence="Vishay 250V absolute, 25C SOA curves cannot certify hot 350ms"),
        dict(rank=10,id="B5-10",failure="D302 open or RUN_EN remains low",
             class_="ACCEPTABLE_AVAILABILITY",
             hazard="No 5V/RAW, safe reset/no vehicle feedback if actually off",
             mitigation="Prove fail-off/no backfeed and no overheating; permit device loss",
             evidence="No required operation after severe component failure"),
        dict(rank=11,id="B5-11",failure="Buck destructively fails open without current-path",
             class_="CONDITIONALLY_ACCEPTABLE_TOTAL_LOSS",
             hazard="Lost power/data, no cable fire provided verified nonconducting/hot state",
             mitigation="Fault injection must prove PCB temperatures, smoke/flame, no 200V output or backfeed",
             evidence="Safe-open not guaranteed by IC voltage absolute maximum"),
    ]

def report():
    weid=FUSES["WEIDMULLER_1460620000"]
    eaton=FUSES["EATON_FWC-4A10F"]
    mersen=FUSES["MERSEN_MEV55C5"]
    cases=[
        zener_branch(5,0),
        zener_branch(20,0),
        zener_branch(5,50),
        zener_branch(5,150),
        fault_resistive(5,100),
        fault_resistive(5,500),
    ]
    return {
        "project":"TripPower B Round 5 adversarial hazard-energy and F_MAIN qualification",
        "scope":"Hypothetical rectangular source 200V/350ms; not an ISO generator",
        "fuse_catalog":{k:asdict(v) for k,v in FUSES.items()},
        "fuse_candidate_gate":{k:qualification(v,prospective_short_a=prospective_short(5))
                               for k,v in FUSES.items()},
        "normal_9V_5V2A_RAW1A_sensitivity":[normal_input_current(efficiency=eta)
                                             for eta in (.75,.80,.90)],
        "hypothetical_energy_cases":cases,
        "faulted_direct_pin_ratings":direct_pin_rating_exposure(),
        "conditional_Q302_drains_at_200v_SOURCE_A":[direct_pin_rating_exposure(q302_drain_v=v) for v in (0.,30.,200.)],
        "EATON_fast_short_i2t_example_not_opening_time":[
            i2t_catalog_screen(eaton,i) for i in (2.,4.,10.,20.,40.)],
        "mersen_10A_min_break_10s_max_versus_350ms":{
          "min_dc_break_a":mersen.min_dc_break_current_a,
          "manufacturer_max_clear_at_min_break_seconds":mersen.manufacturer_max_clear_at_min_break_s,
          "requested_pulse_seconds":PULSE_S,
          "fuse_must_clear_by_350ms":False,
          "sub_10A_200VDC_break_guarantee":False,
          "manufacturer_pdf_url":"https://de.mersen.com/sites/default/files/medias/PIM/files/DS-EVpack-fuse-MEV55C-MEV50A-500VDC-max-L-R-less-than-2-5ms-5-800A-EN.pdf",
          "anomalous_MEV55C5_P_10ms_pdf_table_requires_mersen_clarification":True
        },
        "below_fuse_rating_even_if_zener_energy_high":
            fuse_no_action_counterexample(cases[2]["current_a"],weid,cases[2]["zener_energy_j"]),
        "fuse_and_harness_sensitivity":[external_cable_screen(weid,rs=.5,wire_R=.1),
                                        external_cable_screen(weid,rs=5,wire_R=.1)],
        "priority_FMEA":fmea(),
        "qualification_decision":{
            "200V_350ms_FMAIN_ONLY_PROVEN":False,
            "200VDC_interrupting_candidate_identified":True,
            "DC_min_max_time_current_curve_and_125C_available":False,
            "downstream_cable_copper_harness_I2t_qualified":False,
            "post_failed_IC_sustained_or_arcing_energy_qualified":False,
            "Q301_short_safe_module_failure_proven":False,
            "B_common_source_input_FET_short_safe_module_failure_proven":False,
            "need_second_HV_disconnect_proven_inevitable":False,
            "possibility_of_safe_sacrificial_fault_containment":True,
            "hardware_vehicle_or_fabrication_release":False
        }}
if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
